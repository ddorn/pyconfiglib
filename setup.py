import glob
import json

from setuptools import setup

if __name__ == '__main__':

    try:
        with open('readme.rst') as f:
            long_description = f.read()
    except FileNotFoundError:
        long_description = 'Configuration for python made easy'

    with open('.manconfig') as f:
        config = json.load(f)

    setup(
        name='pyconfiglib',
        version=config['version'],
        packages=config['packages'],
        url='https://github.com/ddorn/configlib',
        license='MIT',
        author='Diego Dorn',
        author_email='diego.dorn@free.fr',
        description='Configuration for python made easy',
        long_description=long_description,
        install_requires=config['dependancies'],
        package_data=config['package_data'],
        data_files=[(dir, list({file for patern in pats for file in glob.glob(patern)})) for (dir, pats) in config['data_files']]
    )
