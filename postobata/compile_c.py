import os.path
import platform
import re
import urllib.parse as uparse

import wget
from pyunpack import Archive

import pyposto.decorators as ppd

get_url_file_name = lambda name: name[name.rfind('/') + 1:]
extract_all = lambda archive, destination: Archive(archive).extractall(destination)


def dl_raw(url: str, folder: str = None):
    p_url: uparse.ParseResult = uparse.urlparse(url)
    file_name: str = get_url_file_name(p_url.path)
    if folder:
        file_name = os.path.join(folder, file_name)
        wget.download(url, out=file_name)


def setup_compiler_tool(conf):
    file_name: str = get_url_file_name(conf['compiler_bin_url'])
    file_name_path: str = os.path.join(conf['pyposto_dirs']['raw'], file_name)
    if not os.path.exists(file_name_path):
        dl_raw(conf['compiler_bin_url'], conf['pyposto_dirs']['raw'])
        extract_all(file_name_path, conf['pyposto_dirs']['tools'])
    conf['pyposto_dirs']['compiler_path'] = \
        os.path.join(conf['pyposto_dirs']['tools'], re.sub(
            '(.tar)|(.gz)|(.xz)|(.zip)|(.z)|(.7z)|(.bz)|(.bz2)'
            , '', file_name))
    conf['compiler'] = os.path.join(conf['pyposto_dirs']['compiler_path'], 'bin', 'clang')


def os_config_homogenizer(conf):
    os_conf: dict = {}
    if platform.system():
        conf.update(conf['_os_overrides_'][platform.system()])
    conf.pop('_os_overrides_')


def setup_home(conf):
    user_home = os.path.expanduser('~')
    conf['pyposto_dirs'] = {
        'root': os.path.join(user_home, '.pyposto'),
        'cache': os.path.join(user_home, '.pyposto', 'cache'),
        'raw': os.path.join(user_home, '.pyposto', 'cache', '.raw'),
        'certs': os.path.join(user_home, '.pyposto', 'certs'),
        'venv': os.path.join(user_home, '.pyposto', 'venv'),
        'tools': os.path.join(user_home, '.pyposto', 'tools'),
    }
    for k, v in conf['pyposto_dirs'].items():
        os.makedirs(v, mode=0o770, exist_ok=True)


def setup_project(conf):
    project_home = os.path.abspath('.') if not '_project_root_' in conf else conf['_project_root_']
    conf['project_dirs'] = {
        'root': os.path.join(project_home),
        'cache': os.path.join(project_home, '.pyposto', 'cache'),
        'build': os.path.join(project_home, '.pyposto', 'build'),
        'temp': os.path.join(project_home, '.pyposto', 'temp'),
        'src': os.path.join(project_home, 'src'),
        'include': os.path.join(project_home, 'include'),
        'tests': os.path.join(project_home, 'tests'),
        'libs': os.path.join(project_home, 'libs'),
        'bins': os.path.join(project_home, 'bins'),
        'pkg': os.path.join(project_home, 'pkg'),
        'man': os.path.join(project_home, 'man'),
        'docs': os.path.join(project_home, 'docs'),
    }
    for k, v in conf['project_dirs'].items():
        os.makedirs(v, mode=0o770, exist_ok=True)


def compile_project(config):
    bin_files_dir = config['project_dirs']['bins']
    libs_files_dir = config['project_dirs']['libs']
    header_files_dir = config['project_dirs']['include']


@ppd.config({
    '_os_overrides_': {
        'Linux': {
            'compiler_bin_url': 'https://github.com/llvm/llvm-project/releases/download/llvmorg-10.0.0/clang+llvm-10.0.0-amd64-unknown-freebsd11.tar.xz'
        },
        'Darwin': {
            'compiler_bin_url': ''
        },
        'Windows': {
            'compiler_bin_url': ''
        }
    },
    '_required_fields_': '',
    'artefact_type': '',
    'compiler_bin_url': '',
    'libs': '',
    'name': '',
    'org': '',
    'platform':
        'terminal',
    'repo': '',
    'version': '',
})
@ppd.do(os_config_homogenizer)
@ppd.do(setup_home)
@ppd.do(setup_project)
@ppd.do(setup_compiler_tool)
@ppd.do(compile_project)
def compile_c_app(conf):
    pass


if __name__ == '__main__':
    compile_c_app()
