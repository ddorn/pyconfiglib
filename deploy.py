import os

import click
from setup import get_version, save_version

TYPES = ['major', 'minor', 'patch']


def run(cmd):
    click.secho(cmd, fg='yellow')
    os.system(cmd)


@click.command()
@click.argument('type', type=click.Choice(TYPES))
@click.argument('message', nargs=-1)
def main(type, message):
    """Deploy a project easily and change the version number at the same time."""

    # read and parsing the version
    version = get_version()
    version = list(map(int, version.split('.')))

    importance = TYPES.index(type)
    # we increase major/minor/path as chosen
    version[importance] += 1
    # en reset the ones after
    for i in range(importance + 1, 3):
        version[i] = 0

    # save the version
    save_version(*version)
    version = get_version()

    # default message if nothing was provided
    message = ' '.join(message) if message else 'Release of version %s' % version

    # we need to commit and push the change of the version number before everything
    # if we don't, travis will not have the right version and will fail to deploy
    run('git commit -a -m "changing version number"'.format(message=message))
    run('git push origin')
    # creating a realase with the new version
    run('git tag v{version} -a -m "{message}"'.format(version=version,
                                                      message=message))
    run('git push origin --tags')

    click.secho('Version changed to ' + version, fg='green')


if __name__ == '__main__':
    main()
