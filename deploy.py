import os

import click
from setup import get_version, save_version
import subprocess

TYPES = ['major', 'minor', 'patch']


def run(cmd, test=False):
    click.secho(cmd, fg='yellow')
    if not test:
        result = subprocess.Popen(cmd)
        text = result.communicate()[0]
        return result.returncode
    return 0


@click.command()
@click.argument('type', type=click.Choice(TYPES))
@click.argument('message', nargs=-1)
@click.option('--test', '--preview', is_flag=True)
@click.version_option(get_version())
def main(type, message, test):
    """Deploy a project easily and change the version number at the same time."""

    # read and parsing the version
    version = get_version()
    click.secho('Current version: %s' % version, fg='green')
    version = list(map(int, version.split('.')))
    last_version = version[:]
    def revert_version():
        save_version(*last_version)
        click.secho('Version reverted to %s' % get_version(), fg='yellow')

    importance = TYPES.index(type)
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
        click.secho("The test doesn't pass.", fg='red')
        revert_version()
        return

    # make sur I can install it
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

    if test:
        revert_version()


if __name__ == '__main__':
    main()
