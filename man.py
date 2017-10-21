import os
import subprocess

import click

from setup import get_version, save_version
import manconfig

TYPES = ['major', 'minor', 'patch']
TEST = False
CONFIG = manconfig.Config()


def run(cmd, test=False):
    click.secho('$ ', fg='green', nl=0)
    click.secho(cmd, fg='yellow')
    if not test:
        result = subprocess.Popen(cmd)
        text = result.communicate()[0]
        return result.returncode
    return 0


@click.group()
@click.option('--test', is_flag=True)
@click.version_option(get_version())
def man(test):
    global TEST
    TEST = test


@man.command()
@click.argument('importance', type=click.Choice(TYPES))
@click.argument('message', nargs=-1)
@click.option('--test', is_flag=True)
def release(importance, message, test):
    """Deploy a project: update version, add tag, and push."""

    global TEST
    TEST = TEST or test

    # read and parsing the version
    version = get_version()
    click.secho('Current version: %s' % version, fg='green')
    version = list(map(int, version.split('.')))
    last_version = version[:]

    def revert_version():
        save_version(*last_version)
        click.secho('Version reverted to %s' % get_version(), fg='yellow')

    importance = TYPES.index(importance)
    # we increase major/minor/path as chosen
    version[importance] += 1
    # en reset the ones after
    for i in range(importance + 1, 3):
        version[i] = 0

    # save the version
    save_version(*version)

    # uninstall the previous version because the test imports it :/
    run('pip uninstall pyconfiglib --yes')

    # make sure it passes the tests
    if run('pytest') != 0:
        click.secho("The tests doesn't pass.", fg='red')
        revert_version()
        return

    # make sure I can install it
    if run('py setup.py install --user clean --all') != 0:
        click.secho('Failed to install the updated library.', fg='red')
        revert_version()
        return

    version = get_version()

    # default message if nothing was provided
    message = ' '.join(message) if message else 'Release of version %s' % version

    # we need to commit and push the change of the version number before everything
    # if we don't, travis will not have the right version and will fail to deploy

    run('git commit -a -m "changing version number"'.format(message=message), test)
    run('git push origin', test)

    if click.confirm('Are you sure you want to create a new release ?'):
        # creating a realase with the new version
        run('git tag v{version} -a -m "{message}"'.format(version=version,
                                                          message=message), test)
        run('git push origin --tags', test)

        click.secho('Version changed to ' + version, fg='green')
    else:
        revert_version()
        return

    if test:
        # We do not want to increase the version number at each test
        revert_version()


@man.group()
def add():
    pass


@add.command(name='dep')
@click.argument('lib')
def add_dep(lib):
    import importlib
    modul = importlib.import_module(lib)
    print(f'{lib}=={modul.__version__}')


@add.command('file')
@click.argument('filename')
def add_file(filename):
    filename = os.path.relpath(filename, os.path.dirname(__file__))
    directory = os.path.dirname(filename)

    print(f'dir: {directory}')
    print(f'file: {filename}')

    data_files = CONFIG.data_files
    for i, (direc, files) in enumerate(data_files):
        if direc == directory:
            if filename not in files:
                files.append(filename)
            break
    else:
        data_files.append((directory, [filename]))

    CONFIG.__save__()

@add.command('pkg-data')
@click.argument('filename')
def add_pkg_data(filename):
    pass


if __name__ == '__main__':
    man()
