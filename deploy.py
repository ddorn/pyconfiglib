import os

import click

TYPES = ['major', 'minor', 'patch']

def get_version():
    with open('version') as f:
        return f.read()

def save_version(major, minor, patch):
    with open('version', 'w') as f:
        f.write('%d.%d.%d' % (major, minor, patch))

def run(cmd):
    click.secho(cmd, fg='yellow')
    os.system(cmd)

@click.command()
@click.argument('type', type=click.Choice(TYPES))
@click.argument('message', nargs=-1)
def main(type, message):
    """Deploy a project easily and change the version number at the same time."""

    version = get_version()
    version = list(map(int, version.split('.')))
    importance = TYPES.index(type)
    # we increase major/minor/path as chosen
    version[importance] += 1
    # en reset the ones after
    for i in range(importance + 1, 3):
        version[i] = 0

    save_version(*version)
    version = get_version()

    message = message and ' '.join(message) or 'Release of version %s' % version

    run('git commit -a -m "changing version number"'.format(message=message))
    run('git push origin')
    run('git tag v{version} -a -m "{message}"'.format(version=version,
                                                      message=message))
    run('git push origin --tags')

    click.secho('Version changed to ' + version, fg='green')

if __name__ == '__main__':
    main()
