import os

from setuptools import setup

VERSION_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'configlib', 'version')


def get_version():
    with open(VERSION_FILE) as f:
        return f.read()


def save_version(major, minor, patch):
    with open(VERSION_FILE, 'w') as f:
        f.write('%d.%d.%d' % (major, minor, patch))


if __name__ == '__main__':

    try:
        with open('readme.rst') as f:
            long_description = f.read()
    except:
        long_description = 'Configuration for python made easy'

    setup(
        name='pyconfiglib',
        version=get_version(),
        packages=['configlib'],
        url='https://github.com/ddorn/configlib',
        license='MIT',
        author='Diego Dorn',
        author_email='diego.dorn@free.fr',
        description='Configuration for python made easy',
        long_description=long_description,
        install_requires=['click==6.*', 'pygments>=2.2'],
        package_data={
            'configlib': ['version']
        }
    )
