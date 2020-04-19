import importlib.util
import os
import urllib.parse as uparse
from os import makedirs
from os.path import join as pjoin

import click
import wget
import yaml
from pip._internal import main as pipmain
from pkg_resources import iter_entry_points
from pyunpack import Archive
from reentry import manager

HOME_DIR = click.get_app_dir('pyposto', force_posix=True, roaming=False)
BUILD_FILE_NAME = os.getenv('BUILD_RECIPE', 'build_recipe.yml')
BUILD_FILE_PATH = pjoin('.', os.getenv('BUILD_RECIPE', 'build_recipe.yml'))
PLUGIN_ENTRYPOINT_GROUP = 'pypopsto'


class utils(object):
    @classmethod
    def get_url_file_name(cls, name: str):
        return name[name.rfind('/') + 1:]

    @classmethod
    def extract_all(cls, archive, destination):
        Archive(archive).extractall(destination)

    @classmethod
    def download(cls, url: str, folder: str = '.', file_name=None):
        p_url: uparse.ParseResult = uparse.urlparse(url)
        if not file_name:
            file_name: str = cls.get_url_file_name(p_url.path)
            file_name = os.path.join(folder, file_name)
        if not os.path.exists(file_name):
            wget.download(url, out=file_name)
        return file_name

    @classmethod
    async def download_async(cls, url: str, folder: str = '.', file_name=None):
        p_url: uparse.ParseResult = uparse.urlparse(url)
        if not file_name:
            file_name: str = cls.get_url_file_name(p_url.path)
            file_name = os.path.join(folder, file_name)
        if not os.path.exists(file_name):
            wget.download(url, out=file_name)
        return file_name


class starter(object):
    @classmethod
    def _mkdirs_util(cls, dirmap: dict):
        for k, v in dirmap.items():
            makedirs(v, mode=0o770, exist_ok=True)

    @classmethod
    def _posto_dirs(cls, pyposto_home):
        dirs: dict = {
            'pyposto_home': pyposto_home,
            'cache': pjoin(pyposto_home, 'cache'),
            'raw': pjoin(pyposto_home, 'cache', 'raw'),
            'yield': pjoin(pyposto_home, 'yield'),
            'tools': pjoin(pyposto_home, 'tools'),
        }
        cls._mkdirs_util(dirs)
        return dirs

    @classmethod
    def _setup_project(cls, obj):
        project_home = os.path.abspath('.') if not '_project_root_' in obj else obj['_project_root_']
        build_recipe_file = os.path.join(project_home, 'build_recipe.yml') if not '_build_recipe_' in obj else obj[
            '_build_recipe_']
        if os.path.exists(build_recipe_file):
            obj['project_data'] = yaml.load(open(build_recipe_file, 'r'), yaml.Loader)
        else:
            raise FileNotFoundError('build_recipe.yml doesn\'t exist')
        build_local_override = \
            os.path.join(project_home, 'build_override.yml') if not '_build_local_override_' in obj else obj[
                '_build_local_override_']
        if os.path.exists(build_local_override):
            obj['_build_override_'] = yaml.load(open(build_local_override, 'r'), yaml.Loader)

    @classmethod
    def _get_plugin_entrypoints(cls, pkg):
        return {
            a.name: a.load() for a in list(iter_entry_points(PLUGIN_ENTRYPOINT_GROUP))
        }

    @classmethod
    def create_context(cls):
        build_file_path = pjoin('.', BUILD_FILE_NAME)
        build_plugin = None
        try:
            if os.path.exists(build_file_path):
                build_plugin = yaml.load(build_file_path, yaml.SafeLoader)['builder_plugin']
        except Exception:
            pass
        if build_plugin and not importlib.util.find_spec(build_plugin):
            pipmain(['install', build_plugin])
        return {
            'context_settings': {
                'obj': {
                    'name': 'rakesh',
                    'pyposto_dirs': cls._posto_dirs(HOME_DIR),
                }
            },
            # 'commands': cls._get_plugin_entrypoints(''),
            'chain': True,
        }


@click.group(**starter.create_context())
@click.option(
    '--home-dir',
    type=click.STRING,
    help='Define Home directory',
    default=HOME_DIR,
    envvar='PYPOSTO_HOME',
    required=False,
    expose_value=True
)
@click.pass_obj
def step(obj, home_dir):
    if not obj:
        obj = {}
    obj['pyposto_dirs'] = starter._posto_dirs(home_dir)
    starter._setup_project(obj)
    build_plugin = obj['project_data']['builder_plugin']
    plugin_spec = importlib.util.find_spec(build_plugin)
    if not plugin_spec:
        pipmain(['install', build_plugin])
    manager.scan()


if __name__ == '__main__':
    # starter.create_context()
    step()
