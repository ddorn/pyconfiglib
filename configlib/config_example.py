#!/usr/bin/env python3

import configlib
from configlib import conftypes


class WallColors(configlib.SubConfig):
    east = (255, 0, 0)
    __east_type__ = conftypes.color
    __east_hint__ = 'The color of the eastern wall, where the sun rises.'

    west = (0, 255, 0)
    __west_type__ = conftypes.color
    __west_hint__ = 'The color of the western wall, where the cow boys.'

    nord = (0, 0, 255)
    __nord_type__ = conftypes.color
    __nord_hint__ = 'The color of the northern wall, where the snow falls.'

    south = (0, 0, 0)
    __south_type__ = conftypes.color
    __south_hint__ = 'The color of the southern wall, where the ice creams.'


class Colors(configlib.SubConfig):
    """The colors of your favorite text editor"""

    light = (255, 255, 255)
    __light_type__ = conftypes.color
    __light_hint__ = 'The color of your lights'

    walls = WallColors()
    __walls_hint__ = 'The colors of the walls of your secret place'

    castle = WallColors()
    __castle_hint__ = 'The colors of the walls of your castle'


class Config(configlib.Config):
    __config_path__ = 'assets/config.json'
    __version__ = 1

    age = 3

    name = 'Archibald'
    __name_hint__ = 'Your name'

    documents = '.'
    __documents_type__ = conftypes.path
    __documents_hint__ = "The path to your documents folder"

    bald = True
    __bald_hint__ = "Are you bald ?"

    colors = Colors()
    __colors_hint__ = 'The colors around you.'

    def get_fancy_name(self):
        if self.bald:
            return self.name + " the Bald"
        else:
            return self.name + " the Hirsute"


if __name__ == '__main__':
    configlib.update_config(Config)
