from setuptools import setup

from configlib.__deploy import get_version

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
