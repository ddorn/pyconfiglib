import configlib

class Config(configlib.Config):

    __config_path__ = 'manconfig.json'

    package_data = {}
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)


if __name__ == '__main__':
    c = Config()
    configlib.update_config(Config)
