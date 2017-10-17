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

import json

import click

from prompting import prompt_file
import conftypes

try:
    import pygments
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments = "You can install pygments with `pip install pygments` and have the output colored !"
    JsonLexer = None  # type: type
    TerminalFormatter = None  # type: type


def is_config_field(attr: str):
    """Every string which doesn't start and end with '--' is considered to be a valid configuration field."""
    return not (attr.startswith('__') and attr.endswith('__'))


def represent_path(field: str):
    """A path field starts or and its name with path and an underscore"""
    return field.lower().startswith('path_') or field.lower().endswith('_path')


def get_field_type(config: 'Config', field: str):
    """Get the type given by __field_type__ or str if not defined."""
    return getattr(config, '__{field}_type__'.format(field=field), conftypes.ConfigType())



def get_field_hint(config, field):
    """Get the hint given by __field_hint__ or the field name if not defined."""
    return getattr(config, '__{field}_hint__'.format(field=field), field)


def warn_for_field_type(config, field):
    click.echo('The field ', nl=False)
    click.secho(field, nl=False, fg='yellow')
    click.echo(' is a ', nl=False)
    click.secho(type(config[field]).__name__, nl=False, fg='red')
    click.echo(' but should be ', nl=False)
    click.secho(get_field_type(config, field).__name__, nl=False, fg='green')
    click.echo('.')


class Config(object):

    __config_path__ = 'config.json'

    def __init__(self, raise_on_fail=True):
        self.__load__(raise_on_fail)

    def __init_subclass__(cls, **kwargs):
        # we want to set the type for the implicit ones
        for field in list(cls.__dict__):
            if not is_config_field(field):
                continue

            field_type_name = '__{field}_type__'.format(field=field)
            if not hasattr(cls, field_type_name):
                setattr(cls, field_type_name, type(getattr(cls, field)))

    def __iter__(self):
        """Iterate over the fields"""
        keys = sorted(type(self).__dict__)
        for key in keys:
            if is_config_field(key):
                yield key

    def __load__(self, raise_on_fail=True):
        try:
            with open(self.__config_path__) as f:
                file = f.read()

        except FileNotFoundError:
            file = '{}'

        conf = json.loads(file)  # type: dict

        # we update only the fields in the conf #NoPolution
        for field in self:
            # so we set the field to the field if there is one in the conf (.get)
            new_value = conf.get(field, getattr(self, field))
            supposed_type = get_field_type(self, field)
            if isinstance(supposed_type, conftypes.ConfigType):
                if conftypes.isgood(new_value, supposed_type):
                    pass
                else:
                    new_value = supposed_type.load(new_value)
            if not conftypes.isgood(new_value, supposed_type):
                import inspect
                click.echo("The field {} is a {} but should be {}.".format(field, type(new_value).__name__,
                                                                                     supposed_type.__name__), end=' ')
                click.echo("You can run `python {}` to update the configuration".format(inspect.getfile(self.__class__)))
                if raise_on_fail:
                    raise TypeError

            setattr(self, field, new_value)

    def __save__(self):

        attr_dict = {}
        for attr in self:
            if is_config_field(attr):
                supposed_type = get_field_type(self, attr)
                if isinstance(supposed_type, conftypes.ConfigType):
                    attr_dict[attr] = supposed_type.save(self[attr])
                else:
                    attr_dict[attr] = self[attr]

        jsonstr = json.dumps(attr_dict, indent=4, sort_keys=True)
        with open(self.__config_path__, 'w') as f:
            f.write(jsonstr)

    def __len__(self):
        # we can't do len(list(self)) because list uses len when it can, causing recurtion of the death
        return sum(1 for _ in self)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __print_list__(self):
        click.echo("The following fields are available: ")
        for i, field in enumerate(list(self)):
            click.echo(" - {:-3} ".format(i + 1), nl=0)
            click.echo(field + ' (', nl=0)
            click.secho(get_field_type(self, field).__name__, fg='yellow', nl=0)
            click.echo(')')
        click.echo()

    def __show__(self):
        try:
            with open(self.__config_path__, 'r') as f:
                file = f.read()
        except FileNotFoundError:
            click.echo("You don't have any configuration.")
            return

        file = json.dumps(json.loads(file), indent=4, sort_keys=True)

        if isinstance(pygments, str):
            click.secho(pygments, fg='yellow')
        else:
            file = pygments.highlight(file, JsonLexer(), TerminalFormatter())

        click.echo()
        click.echo(file)

    def __update__(self, dct):
        for field, value in dct.items():
            supposed_type = get_field_type(self, field)
            if conftypes.isgood(value, supposed_type):
                self[field] = value
            else:
                warn_for_field_type(self, field)

def prompt_update_all(config):

    click.echo()
    click.echo('Welcome !')
    click.echo('Press enter to keep the defaults or enter a new value to update the configuration.')
    click.echo('Press Ctrl+C at any time to quit and save')
    click.echo()

    for i, field in enumerate(list(config)):

        type_ = getattr(config, '__' + field + '_type__', type(config[field]))
        hint = getattr(config, '__' + field + '_hint__', field) + ' ({})'.format(type_.__name__)

        if represent_path(field) or type_ is conftypes.path:
            config[field] = prompt_file(hint, default=config[field])
        else:
            # ask untill we have the right type
            while True:
                value = click.prompt(hint, default=config[field], type=type_)

                supposed_type = get_field_type(config, field)
                if conftypes.isgood(value, supposed_type):
                    config[field] = value
                    break

                warn_for_field_type(config, field)


def update_config(config: type(Config)):
    config = config(raise_on_fail=False)  # type: Config

    def print_list(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return param

        config.__print_list__()

        ctx.exit()

    def show_conf(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return param

        config.__show__()

        ctx.exit()

    # all option must be eager and start with only one dash, so it doesn't conflic with any possible field
    @click.command()
    @click.option('-l', '-list', is_eager=True, is_flag=True, expose_value=False, callback=print_list,
                            help='List the availaible configuration fields.')
    @click.option('-s', '-show', is_eager=True, is_flag=True, expose_value=False, callback=show_conf,
                            help='View the configuration.')
    def command(**kwargs):
        """
        I manage your configuration.

        If you call me with no argument, you will be able to set each field
        in an interactive prompt. I can show your configuration with -s,
        list the available field with -l and set them by --name-of-field=whatever.
        """

        try:
            # save directly what is passed if something was passed
            kwargs = {field: value for (field, value) in kwargs.items() if value is not None}

            if kwargs:
                config.__update__(kwargs)
            else:
                # or update all
                prompt_update_all(config)
        except click.exceptions.Abort:
            pass
        finally:
            config.__save__()
            click.echo('\nSaved !')

    # update the arguments with all fields
    for i, field in enumerate(list(config)):
        command = click.option('--{}'.format(field), '-{}'.format(i + 1), type=get_field_type(config, field),
                                         help=get_field_hint(config, field))(command)

    command()
