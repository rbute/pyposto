import importlib.util
import os
from os import makedirs
from os.path import join as pjoin

import click
import yaml
from pip._internal import main as pipmain

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


def _setup_project(ctx):
    project_home = os.path.abspath('.') if not '_project_root_' in ctx else ctx['_project_root_']
    build_recipe_file = os.path.join(project_home, 'build_recipe.yml') if not '_build_recipe_' in ctx else ctx[
        '_build_recipe_']
    if os.path.exists(build_recipe_file):
        ctx['project_data'] = yaml.load(open(build_recipe_file, 'r'), yaml.Loader)
    else:
        raise FileNotFoundError('build_recipe.yaml doesn\'t exist')
    build_local_override = os.path.join(project_home, 'build_override.yml') if not '_build_local_override_' in ctx else \
        ctx['_build_local_override_']
    if os.path.exists(build_local_override):
        ctx['_build_override_'] = yaml.load(open(build_local_override, 'r'), yaml.Loader)


@click.group(name='pyposto')
@click.option(
    '--home-dir',
    type=click.STRING,
    help='Define Home directory',
    default=HOME_DIR,
    envvar='PYPOSTO_HOME',
    required=False,
    expose_value=True
)
@click.pass_context
def step(ctx, home_dir):
    ctx.ensure_object(dict)
    ctx.obj['pyposto_dirs'] = posto_dirs(home_dir)
    _setup_project(ctx.obj)
    build_plugin = ctx.obj['project_data']['builder_plugin']
    plugin_spec = importlib.util.find_spec(build_plugin)
    if not plugin_spec:
        pipmain(['install', build_plugin])


@step.command()
@click.pass_context
def setup(ctx):
    ctx.ensure_object(dict)
    click.secho('Inside setup', color='red')


if __name__ == '__main__':
    step()
