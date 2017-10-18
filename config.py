#!/usr/bin/env python3

import configlib
import conftypes

class Config(configlib.Config):
    __config_path__ = 'config.json'

    orange = (255, 127, 31)
    __orange_type__ = conftypes.color
    __orange_hint__ = "The most beautiful orange"

    age = 3

    name = 'Archibald'
    __name_hint__ = 'Your name'

    documents = '.'
    __documents_type__ = conftypes.path
    __documents_hint__ = "The path to your documents folder"

    bald = True
    __bald_hint__ = "Are you bald ?"

if __name__ == '__main__':
    configlib.update_config(Config)
