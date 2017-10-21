import glob
import os

from setuptools import setup

VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'configlib', 'version')


def get_version():
    with open(VERSION_FILE) as f:
        return f.read()


def save_version(major, minor, patch):
    version = '%d.%d.%d' % (major, minor, patch)
    with open(VERSION_FILE, 'w') as f:
        f.write(version)

    with open('readme.md') as f:
        readme = f.readlines()

    readme[0] = '[![Build Status](https://travis-ci.org/ddorn/configlib.svg?branch=v%s)](https://travis-ci.org/ddorn/configlib)\n' % version

    with open('readme.md', 'w') as f:
        f.writelines(readme)

if __name__ == '__main__':

    try:
        with open('readme.rst') as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = 'Configuration for python made easy'

    import manconfig
    config = manconfig.Config()
    print(config.package_data)
    
    setup(
        name='pyconfiglib',
        version=get_version(),
        packages=config.packages,
        url='https://github.com/ddorn/configlib',
        license='MIT',
        author='Diego Dorn',
        author_email='diego.dorn@free.fr',
        description='Configuration for python made easy',
        long_description=long_description,
        install_requires=config.dependancies,
        package_data=config.package_data,
        data_files=[(dir, list({file for patern in pats for file in glob.glob(patern)})) for (dir, pats) in config.data_files]
    )
