import click


def is_valid(instance, type_):
    if isinstance(type_, ConfigType):
        return type_.is_valid(instance)
    return isinstance(instance, type_)


class ConfigType(click.ParamType):

    def convert(self, value, param, ctx):
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


class _ColorType(ConfigType):
    name = 'color'

    def load(self, value):
        if len(value) not in (4, 7) or value[0] != '#':
            raise ValueError

        size = len(value) // 3
        factor = 1 if size == 2 else 16
        r, g, b = [value[1 + size*i: 1 + size*(i+1)] for i in range(3)]
        return [int(c, 16) * factor for c in (r, g, b)]

    def is_valid(self, value):
        return isinstance(value, (tuple, list)) and \
               len(value) == 3 and \
               all(isinstance(c, int) and
                   0 <= c < 256
                   for c in value)

    def save(self, value):
        return '#{}{}{}'.format(hex(value[0])[2:],
                                hex(value[1])[2:],
                                hex(value[2])[2:])


class _PathType(ConfigType):

    name = 'path'

    def is_valid(self, value):
        return isinstance(value, str)


color = _ColorType()

path = _PathType()
