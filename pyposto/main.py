from os import makedirs
from os.path import join as pjoin

import click

HOME_DIR = click.get_app_dir('pyposto', force_posix=True, roaming=False)


def _mkdirs_util(dirmap: dict):
    for k, v in dirmap.items():
        makedirs(v, mode=0o770, exist_ok=True)


def posto_dirs(pyposto_home):
    dirs = {
        'dirs': {
            'pyposto_home': pyposto_home,
            'cache': pjoin(pyposto_home, 'cache'),
            'raw': pjoin(pyposto_home, 'cache', 'raw'),
            'yield': pjoin(pyposto_home, 'yield'),
            'tools': pjoin(pyposto_home, 'tools'),
        }
    }
    _mkdirs_util(dirs['dirs'])
    return dirs


@click.group(name='pyposto')
@click.option(
    '--home-dir',
    type=click.STRING,
    help='Define Home directory',
    default=HOME_DIR,
    show_default=True,
    envvar='PYPOSTO_HOME',
    required=False
)
def step(home_dir=None):
    pass


@step.command()
def setup(home_dir):
    home_dir(home_dir)


if __name__ == '__main__':
    step()
