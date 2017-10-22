import configlib
import os


class Config(configlib.Config):
    __config_path__ = os.path.join(os.path.dirname(__file__), 'manconfig.json')

    libname = ''
    github_username = ''
    fullname = ''
    email = ''
    pypi_username = ''

    package_data = dict()
    __package_data_type__ = configlib.Python(dict)

    data_files = []
    __data_files_type__ = configlib.Python(list)

    packages = []
    __packages_type__ = configlib.Python(list)

    dependancies = []
    __dependancies_type__ = configlib.Python(list)
