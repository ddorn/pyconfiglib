#!/usr/bin/env python3

import configlib
import conftypes


class Colors(configlib.SubConfig):
    """The colors of your favorite text editor"""

    text = (64, 128, 128)
    __text_type__ = conftypes.color

    background = (255, 255, 255)
    __background_type__ = conftypes.color


class Config(configlib.Config):
    __config_path__ = 'config.json'

    age = 3

    name = 'Archibald'
    __name_hint__ = 'Your name'

    documents = '.'
    __documents_type__ = conftypes.path
    __documents_hint__ = "The path to your documents folder"

    bald = True
    __bald_hint__ = "Are you bald ?"

    colors = Colors()

if __name__ == '__main__':
    configlib.update_config(Config)
