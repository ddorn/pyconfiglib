import configlib

class Config(configlib.Config):
    name = 'pyconfiglib'


if __name__ == '__main__':
    configlib.update_config(Config)
