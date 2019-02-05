"""
Utility to manage a configuration fileand provide an easy way to modify it.

To use the configlib in your project, just create a file name `conf.py` awith the following code

    import configlib

    class Config(configlib.Config):
        __config_path__ = 'my/path/to/the/config/file.json

        # you can define all class attributes as you want
        # as long as they don't start and end with a bouble underscore
        foot_size = 52

        bald  = True
        # you can specify the type of the field. It will be auto detected if you don't
        __bald_type__ = bool
        # you can also provide hint to enhance user experience
        __bald_hint__ = "Are you bald ?"

        # and you can not define any function (except super methods)
        name = "Archibald"

        # if a name starts with 'path_' or ends with '_path' there will be autocompletion
        # when the user wants to update it
        path_to_install = ''
        # OR you can just tell the type
        __path_to_install_type__ = configlib.path

        All basic types will be preserved even after save and loading them
        favourite_color = (230, 120, 32)

    if __name__ == '__main__':
        # with that the user will be able to easily edit the config by running `python config.py`
        configlib.update_config(Config)

    Then in your main code you can get the config with

    import config
    myconfig = config.Config()


Made with love by ddorn (https://github.com/ddorn/)
"""

import inspect
import json
import logging
import os
from itertools import cycle
from typing import Tuple

import click

from .prompting import prompt_file
from . import conftypes

LOGGER = logging.getLogger("configlib")

try:
    import pygments
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments = "You can install pygments with `pip install pygments` and have the output colored !"
    JsonLexer = None  # type: type
    TerminalFormatter = None  # type: type
    LOGGER.warning('Pygment not installed')

TYPE_TO_CLICK_TYPE = {
    int: click.INT,
    float: click.FLOAT,
    str: click.STRING,
    bool: click.BOOL
}


# ✓
def is_config_field(attr: str):
    """Every string which doesn't start and end with '__' is considered to be a valid usable configuration field."""
    return not (attr.startswith('_') or attr.endswith('_'))


# ✓
def prompt_update_all(config: 'Config'):
    """Prompt each field of the configuration to the user."""

    click.echo()
    click.echo('Welcome !')
    click.echo('Press enter to keep the defaults or enter a new value to update the configuration.')
    click.echo('Press Ctrl+C at any time to quit and save')
    click.echo()

    for field in config:

        type_ = config.__type__(field)
        hint = config.__hint__(field) + ' ({})'.format(type_.__name__)

        if isinstance(type_, conftypes.SubConfigType):
            continue

        # we prompt the paths through prompt_file and not click
        if type_ is conftypes.path:
            config[field] = prompt_file(hint, default=config[field])
            continue

        if isinstance(type_, conftypes.ConfigType):
            # config[field] is always real data, but we want to show something that is the closest
            # possible to what the user needs to enter
            # thus, we show what we would store in the json
            default = type_.save(config[field])
        else:
            default = config[field]

        # a too long hint is awful
        if len(str(default)) > 14:
            default = str(default)[:10] + '...'

        # ask untill we have the right type
        value = click.prompt(hint, default=default, type=type_)

        # click doesnt convert() the default if nothing is entered, so it wont be valid
        # however we don't care because default means that we don't have to update
        if value == default:
            LOGGER.debug('same value and default, skipping set. %r == %r', value, default)
            continue

        config[field] = value


class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.__instance__ = None

    def __call__(cls, *args, **kw):
        if cls.__instance__ is None:
            cls.__instance__ = super(Singleton, cls).__call__(*args, **kw)
        return cls.__instance__


class BaseConfig(object):
    # the path where the configuration is stored. The directory must exist
    __config_path__ = 'config.json'
    __version__ = 1
    __xor_key__ = b''

    # ✓
    def __init__(self, strict=False):
        self.__load__(strict)

    # ✓
    def __init_subclass__(cls, **kwargs):

        # this is called every times a subclass of Config is made.
        # Here we add all the missing types so the type of the default can not change
        # when there is not __field_type__.

        for field in list(cls.__dict__):
            if not is_config_field(field):
                continue

            field_type_name = '__{field}_type__'.format(field=field)

            # if it is an implicit type
            if not hasattr(cls, field_type_name):
                # we add the type of the default
                default = getattr(cls, field)
                if isinstance(default, SubConfig):
                    setattr(cls, field_type_name, conftypes.SubConfigType(type(default)))
                else:
                    setattr(cls, field_type_name, type(default))
                    LOGGER.debug('In %s the field %s has now type %s because the default is %r', cls, field,
                                  type(default), default)

    def __str__(self):
        return json.dumps(self.__get_json_dict__(), indent=4, sort_keys=True)

    def __repr__(self):
        return json.dumps(self.__get_json_dict__(), sort_keys=True)
    # ✓
    def __iter__(self):
        """Iterate over the fields, sorted."""

        # the fields are all class attributes,
        # so they are accessible from everywhere
        keys = sorted(type(self).__dict__)
        for key in keys:
            if is_config_field(key) and not callable(self[key]):
                yield key

    def __contains__(self, item: str):
        # if there is a dot in item, it is a field of a subconfig
        if '.' in item:
            item, _, sub_item = item.partition('.')
            if hasattr(self, item) and isinstance(self[item], SubConfig):
                return sub_item in self[item]
            else:
                return False
        return is_config_field(item) and hasattr(self, item)

    def __load__(self, strict=False):
        mode = 'rb' if self.__xor_key__ else 'r'

        try:
            with open(self.__config_path__, mode) as f:
                file = f.read()
            LOGGER.info('Read %d chars from %s', len(file), self.__config_path__)
        except FileNotFoundError:
            # if no config was ever created, it's time to make one
            file = '{}'
            LOGGER.info('Config file not found, creating empty one')
        else:
            if self.__xor_key__:
                file = self.__decrypt__(file).decode()

        conf = json.loads(file)  # type: dict

        if conf.get("__version__", self.__version__) != self.__version__:
            logging.info("Config version mismatch (saved: %s, current: %s). Restoring default config.",
                         conf["__version__"], self.__version__)
            conf = {}

        self.__update__(conf, strict)

    # ✓
    def __save__(self):
        """Save the config to __config_path__ in a json format."""

        if self.__xor_key__:
            jsonstr = json.dumps(self.__get_json_dict__()).encode()
            jsonstr = self.__crypt__(jsonstr)
        else:
            jsonstr = json.dumps(self.__get_json_dict__(), indent=4, sort_keys=True)

        LOGGER.info('saving %d chars at %s', len(jsonstr), self.__config_path__)

        mode = 'wb' if self.__xor_key__ else 'w'
        with open(self.__config_path__, mode) as f:
            f.write(jsonstr)

    def __get_json_dict__(self):
        json_dict = {}
        for attr in self:
            # we want to save only the fields
            if is_config_field(attr):

                supposed_type = self.__type__(attr)
                # but we may need to convert the to something json knows
                # if the type is a custom type
                if isinstance(supposed_type, conftypes.ConfigType):
                    json_dict[attr] = supposed_type.save(self[attr])
                else:
                    json_dict[attr] = self[attr]

        json_dict["__version__"] = self.__version__

        return json_dict

    def __crypt__(self, byte_text):
        if self.__xor_key__:
            key = self.__xor_key__[:2] + b'...' + self.__xor_key__[-2:]
            logging.debug("Encryption of the config with the key %s", key)
            byte_text = ''.join(chr(c ^ k) for c, k in zip(byte_text, cycle(self.__xor_key__))).encode()
        return byte_text

    __decrypt__ = __crypt__

    # ✓
    def __len__(self):
        # we can't do len(list(self)) because list uses len when it can, causing recursion of the death
        return sum(1 for _ in self)

    # ✓
    def __setitem__(self, field, value):
        """
        Sets a field to a given value if it is a correct type.

        :param field: needs to be an existing field
        :raise ValueError: when the value is not valid.
        """

        if not is_config_field(field):
            # normal setter for normal fields
            object.__setattr__(self, field, value)
            return

        if callable(value):
            logging.warning('Cannot set a field to a callable object: trying to set %s to %s' % (field, value))
            raise ValueError('Cannot set a field to a callable object: trying to set %s to %s' % (field, value))

        # if there is a dot in the name, we want to set an field of a subconfig
        if '.' in field:
            field, _, subfield = field.partition('.')
            LOGGER.debug('setting subitem %s in %s', subfield, field)
            self[field][subfield] = value
            return

        supposed_type = self.__type__(field)

        LOGGER.debug('SETITEM %s to %r supposed type: %s', field, value, supposed_type)

        if conftypes.is_valid(value, supposed_type):
            # everything is correct, we assign is directly
            object.__setattr__(self, field, value)
            LOGGER.debug('valid')


        elif isinstance(supposed_type, conftypes.ConfigType):
            # we may need to convert it
            LOGGER.debug('try to convert the value through ConfigType')
            try:
                value = supposed_type.load(value)
                object.__setattr__(self, field, value)
            except Exception:
                LOGGER.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
                raise ValueError('fail loading %r of type %s but supposed %s' % (value, type(value), supposed_type))

        elif supposed_type in TYPE_TO_CLICK_TYPE:
            try:
                LOGGER.debug('try to convert the value throught click.ParamType')
                value = TYPE_TO_CLICK_TYPE[supposed_type](value)
                object.__setattr__(self, field, value)
            except Exception:
                LOGGER.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
                raise ValueError('fail loading %s of type %s but supposed %s' % (value, type(value), supposed_type))
        else:
            # it is just not good
            LOGGER.warning('fail loading %r of type %s but supposed %s', value, type(value), supposed_type)
            raise ValueError('fail loading %s of type %s but supposed %s' % (value, type(value), supposed_type))

    __setattr__ = __setitem__

    # ✓
    def __getitem__(self, item: str):
        # proxy to getattribute to have be symetrical to __setitem__
        if '.' in item:
            item, _, sub = item.partition('.')
            return self[item][sub]
        return self.__getattribute__(item)

    # ✓
    def __enter__(self):
        """The context manager pattern ensures that the config will be saved."""
        return self

    # ✓
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__save__()

    # ✓
    def __print_list__(self, prefix=''):
        """Print all the availaible fields with their order and type."""

        if not prefix:
            click.echo("The following fields are available: ")

        # we list the fields
        for field in self:
            if isinstance(self[field], SubConfig):
                continue

            # we print the supposed type
            type_ = click.style(self.__type__(field).__name__, fg='yellow')
            text = '{field} ({type})  '.format(field=field, type=type_)

            if self.__hint__(field) != field:
                # 51 and not 42 because of the size of the ansii escape sequence
                click.echo('{pre} - {text:.<51}  {hint}'.format(pre=prefix, text=text, hint=self.__hint__(field)))
            else:
                click.echo('{pre} - {text}'.format(pre=prefix, text=text))

        # and then the subconfigs
        for field in self:
            if not isinstance(self[field], SubConfig):
                continue

            if self.__hint__(field) != field:
                click.echo('{pre} - {field:.<42}  {hint}'.format(pre=prefix, field=field + ':  ', hint=self.__hint__(field)))
            else:
                click.echo('{pre} - {field}:'.format(pre=prefix, field=field))
            self[field].__print_list__(prefix + '    ')

    # ✓
    def __show__(self):
        """Print the json that stores the data with colors."""

        try:
            with open(self.__config_path__, 'r', encoding='utf-8') as f:
                file = f.read()
        except FileNotFoundError:
            click.echo("You don't have any configuration.")
            return

        file = json.dumps(json.loads(file), indent=4, sort_keys=True)

        # I've set pygments to an help str when there is an import error
        if isinstance(pygments, str):
            click.secho(pygments, fg='yellow')
        else:
            # add ansii coloring
            file = pygments.highlight(file, JsonLexer(), TerminalFormatter())

        click.echo()
        click.echo(file)

    # ✓
    def __update__(self, dct, strict=False):
        """
        Update all the fields with the key/values in the dict.

        When the type is wrong, a warning is printed and the field is not updated.
        Return the success of setting ALL fields of the dict.
        """

        one_field_is_with_a_bad_type = False

        for field, value in dct.items():

            # we update only the fields in the conf so if someone added fields in the json,
            # they won't interfere with the already defined attributes...
            # For instance, we don't want to override __load__.

            if field not in self:
                LOGGER.debug('field %s is not in the config', field)
                continue

            try:
                self[field] = value
            except ValueError:
                LOGGER.debug('failed to set %s to %r but we ignore it', field, value)
                one_field_is_with_a_bad_type = True
                self.__warn__(value, field)

                if strict:
                    raise

        if one_field_is_with_a_bad_type:
            click.echo("You can run `python {}` to update the configuration".format(
                os.path.relpath(inspect.getfile(self.__class__))))

        return one_field_is_with_a_bad_type

    # ✓
    def __warn__(self, value, field):
        """Show a colored message to say that the field is not of the right type."""

        click.echo('The field ', nl=False)
        click.secho(field, nl=False, fg='yellow')
        click.echo(' is a ', nl=False)
        click.secho(type(value).__name__, nl=False, fg='red')
        click.echo(' but should be ', nl=False)
        click.secho(self.__type__(field).__name__, nl=False, fg='green')
        click.echo('.')

    # ✓
    def __type__(self, field: str):
        """Get the type given by __field_type__"""
        if '.' in field:
            subconfigs, _, field = field.rpartition('.')
            return self['{subconfigs}.__{field}_type__'.format(subconfigs=subconfigs,
                                                               field=field)]
        return self['__{field}_type__'.format(field=field)]

    # ✓
    def __hint__(self, field):
        """Get the hint given by __field_hint__ or the field name if not defined."""
        return getattr(self, '__{field}_hint__'.format(field=field), field)

    def __reset__(self):
        try:
            os.remove(self.__config_path__)
        except FileNotFoundError:
            pass
        self.__class__()  # we create a new instance to load it from nowhere
        for field in self:
            if isinstance(self[field], SubConfig):
                self[field] = self[field].__class__()


class Config(BaseConfig, metaclass=Singleton):
    # We make the config singletons because everybody wants to have the same config everywhere in his code
    # but not the subconfig, as we can have more than one of each in each Config
    pass


class SubConfig(BaseConfig):
    # noinspection PyMissingConstructor
    def __init__(self, dct=None):
        dct = dct or {}

        self.__update__(dct)


def update_config(configclass: type(Config)):
    """Command line function to update and the a config."""

    # we build the real click command inside the function, because it needs to be done
    # dynamically, depending on the config.

    # we ignore the type errors, keeping the the defaults if needed
    # everything will be updated anyway
    config = configclass()  # type: Config

    def print_list(ctx, param, value):
        # they do like that in the doc (http://click.pocoo.org/6/options/#callbacks-and-eager-options)
        # so I do the same... but I don't now why.
        # the only goal is to call __print_list__()
        if not value or ctx.resilient_parsing:
            return param

        config.__print_list__()

        ctx.exit()

    def show_conf(ctx, param, value):
        # see print_list
        if not value or ctx.resilient_parsing:
            return param

        config.__show__()

        ctx.exit()

    def reset(ctx, param, value):
        # see print_list
        if not value or ctx.resilient_parsing:
            return param

        click.confirm('Are you sure you want to reset ALL fields to the defaults ? This action is not reversible.', abort=True)

        # that doesn't exist
        configclass.__config_path__, config_path = '', configclass.__config_path__
        # So the file won't be opened and only the default will be loaded.
        config = configclass()
        # Thus we can save the defaults
        # To the right place again
        configclass.__config_path__ = config_path
        config.__save__()

        ctx.exit()

    def clean(ctx, param, value):
        # see print_list
        if not value or ctx.resilient_parsing:
            return param

        config.__save__()
        click.echo('Cleaned !')

        ctx.exit()

    @click.command(context_settings={'ignore_unknown_options': True})
    @click.option('-c', '--clean', is_eager=True, is_flag=True, expose_value=False, callback=clean,
                  help='Clean the file where the configutation is stored.')
    @click.option('-l', '--list', is_eager=True, is_flag=True, expose_value=False, callback=print_list,
                  help='List the availaible configuration fields.')
    @click.option('--reset', is_flag=True, is_eager=True, expose_value=False, callback=reset,
                  help='Reset all the fields to their default value.')
    @click.option('-s', '--show', is_eager=True, is_flag=True, expose_value=False, callback=show_conf,
                  help='View the configuration.')
    @click.argument('fields-to-set', nargs=-1, type=click.UNPROCESSED)
    def command(fields_to_set: 'Tuple[str]'):
        """
        I manage your configuration.

        If you call me with no argument, you will be able to set each field
        in an interactive prompt. I can show your configuration with -s,
        list the available field with -l and set them by --name-of-field=whatever.
        """

        # with a context manager, the config is always saved at the end
        with config:

            if len(fields_to_set) == 1 and '=' not in fields_to_set[0]:
                # we want to update a part of the config
                sub = fields_to_set[0]
                if sub in config:
                    if isinstance(config[sub], SubConfig):
                        # the part is a subconfig
                        prompt_update_all(config[sub])
                    else:
                        # TODO: dynamic prompt for one field
                        raise click.BadParameter('%s is not a SubConfig of the configuration')

                else:
                    raise click.BadParameter('%s is not a field of the configuration')

            elif fields_to_set:
                dct = {}
                for field in fields_to_set:
                    field, _, value = field.partition('=')
                    dct[field] = value
                # save directly what is passed if something was passed whitout the interactive prompt
                config.__update__(dct)
            else:
                # or update all
                prompt_update_all(config)

    # this is the real function for the CLI
    LOGGER.debug('start command')
    command()
    LOGGER.debug('end command')


__all__ = ['Config', 'SubConfig', 'update_config']
