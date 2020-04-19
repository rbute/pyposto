import importlib.util
import os
from os import makedirs
from os.path import join as pjoin

import click
import pkg_resources
import yaml
from pip._internal import main as pipmain
from reentry import manager

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


class PostoMainCommand(click.Group):

    def list_commands(self, ctx):
        all_commands: list = sorted(self.commands)
        try:
            if os.path.exists('build_recipe.yml'):
                build_plugin = yaml.load(open('build_recipe.yml', 'r'), yaml.SafeLoader)['builder_plugin']
                all_commands = all_commands + list(
                    pkg_resources.get_entry_map(build_plugin).get('pyposto_plugins', {}).keys())
        except Exception:
            pass

        return all_commands

    def get_command(self, ctx, cmd_name):
        cmd = click.Group.get_command(self, ctx, cmd_name)
        if cmd:
            return cmd
        else:
            try:
                ctx.obj = {}
                ctx.obj['pyposto_dirs'] = posto_dirs(ctx.params['home_dir'])
                _setup_project(ctx.obj)
                build_plugin = ctx.obj['project_data']['builder_plugin']
                plugin_spec = importlib.util.find_spec(build_plugin)
                if not plugin_spec:
                    pipmain(['install', build_plugin])
                manager.scan()
                # TODO: Right now build plugin name is just a string, it is supposed to break here
                entry_point = pkg_resources.get_entry_map(build_plugin).get('pyposto_plugins', {}).get(cmd_name)
                # TODO: Create command from entrypoint
                loaded_command = None if not entry_point else entry_point.load()
                return loaded_command
            except:
                return None


# @click.group(name='pyposto')
@click.command(cls=PostoMainCommand)
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
    ctx.obj = {}
    ctx.obj['pyposto_dirs'] = posto_dirs(home_dir)
    _setup_project(ctx.obj)
    build_plugin = ctx.obj['project_data']['builder_plugin']
    plugin_spec = importlib.util.find_spec(build_plugin)
    if not plugin_spec:
        pipmain(['install', build_plugin])
    manager.scan()


@step.command()
@click.pass_obj
def setup(obj):
    click.secho('Inside setup', color='red')


if __name__ == '__main__':
    step()
