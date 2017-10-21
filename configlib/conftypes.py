import json

import click

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import configlib


def is_valid(instance, type_):
    if isinstance(type_, ConfigType):
        return type_.is_valid(instance)
    return isinstance(instance, type_)


class ConfigType(click.ParamType):
    name = 'any'

    def __repr__(self):
        return '<ConfigType %s>' % self.name

    def convert(self, value, param=None, ctx=None):
        try:
            return self.load(value)
        except (IndexError, ValueError):
            self.fail('%s is not a %s' % (value, self.name), param, ctx)

    def load(self, value: str):
        """
        Convert the string representation to the real data.
        Raise anything if not correct format.
        """
        return value

    def is_valid(self, value):
        """Validate a real data."""
        return True

    def save(self, value):
        """Converts the real data back into a json valid data"""
        return value

    @property
    def __name__(self):
        return self.name


class SubConfigType(ConfigType):
    name = 'SubConfig'

    def __init__(self, sub_config_class):
        self.sub_config_class = sub_config_class  # type: type(configlib.SubConfig)

    def load(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError('Not a valid json')

        if isinstance(value, dict):
            return self.sub_config_class(value)

        raise ValueError

    def save(self, value: 'configlib.SubConfig'):
        return value.__get_json_dict__()

    def is_valid(self, value):
        return isinstance(value, self.sub_config_class)


class _ColorType(ConfigType):
    name = 'color'

    def load(self, value):
        if len(value) not in (4, 7) or value[0] != '#':
            raise ValueError

        size = len(value) // 3
        factor = 1 if size == 2 else 16
        r, g, b = [value[1 + size * i: 1 + size * (i + 1)] for i in range(3)]
        return [int(c, 16) * factor for c in (r, g, b)]

    def is_valid(self, value):
        return isinstance(value, (tuple, list)) and \
               len(value) == 3 and \
               all(isinstance(c, int) and
                   0 <= c < 256
                   for c in value)

    def save(self, value):
        return '#{:02x}{:02x}{:02x}'.format(*value)


class _PathType(ConfigType):
    name = 'path'

    def is_valid(self, value):
        return isinstance(value, str)


class Python(ConfigType):
    """
    Represent a real python type that is converted from a string with eval().

    :note: It can be maliciously used to inject code
    """
    name = 'dict'

    def __init__(self, type_: type):
        """
        Represent a real python type that is converted from a string with eval().

        :param type type_: The corresponding python type like dict, list or tuple...
        """

        self.type = type_
        self.name = type_.__name__

    def is_valid(self, value):
        return isinstance(value, self.type)

    def save(self, value):
        return value

    def load(self, value: str):
        if isinstance(value, str):
            try:
                value = eval(value)
            except:
                pass
        else:
            # convert gently between similar types, for instance
            # From tuples to lists, because tuples are stored as list in json...
            try:
                value = self.type(value)
            except:
                pass

        if not isinstance(value, self.type):
            raise ValueError('Does not evaluate to a %s' % self.type.__name__)

        return value


color = _ColorType()

path = _PathType()
