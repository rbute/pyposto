import os.path
import platform
import re
import subprocess
import tarfile
import urllib.parse as uparse

import wget
import yaml
from pyunpack import Archive

import pyposto.decorators as ppd

get_url_file_name = lambda name: name[name.rfind('/') + 1:]
extract_all = lambda archive, destination: Archive(archive).extractall(destination)
config_default = {
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
    'name': 'test-library',
    'org': '',
    'platform': 'terminal',
    'repo': '',
    'version': '0.0.1',
}


def dl_raw(url: str, folder: str = None):
    p_url: uparse.ParseResult = uparse.urlparse(url)
    file_name: str = get_url_file_name(p_url.path)
    file_name = os.path.join(folder, file_name)
    if not os.path.exists(file_name):
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
        'local': os.path.join(user_home, '.pyposto', 'cache', '.local'),
        'certs': os.path.join(user_home, '.pyposto', 'certs'),
        'venv': os.path.join(user_home, '.pyposto', 'venv'),
        'tools': os.path.join(user_home, '.pyposto', 'tools'),
    }
    for k, v in conf['pyposto_dirs'].items():
        os.makedirs(v, mode=0o770, exist_ok=True)


def setup_project(conf):
    project_home = os.path.abspath('.') if not '_project_root_' in conf else conf['_project_root_']

    build_recipe_file = os.path.join(project_home, 'build_recipe.yml') if not '_build_recipe_' in conf else conf[
        '_build_recipe_']
    if os.path.exists(build_recipe_file):
        conf['project_data'] = yaml.load(open(build_recipe_file, 'r'), yaml.Loader)
    else:
        raise FileNotFoundError('build_recipe.yaml doesn\'t exist')
    build_local_override = os.path.join(project_home, 'build_override.yml') if not '_build_local_override_' in conf else \
        conf['_build_local_override_']
    if os.path.exists(build_local_override):
        conf['_build_override_'] = yaml.load(open(build_local_override, 'r'), yaml.Loader)

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
    build_dir = config['project_dirs']['build']
    header_files_dir = config['project_dirs']['include']
    bin_files = club_files(
        [(tuple(path.replace(bin_files_dir, '').split('/'))[1:], file) for path, dirs, files in os.walk(bin_files_dir)
         for file in files if file.find('.c') >= 0])
    libs_files = club_files(
        [(tuple(path.replace(libs_files_dir, '').split('/'))[1:], file) for path, dirs, files in os.walk(libs_files_dir)
         for file in files if file.find('.c') >= 0])
    base_command: list = ['gcc', '-shared', '-Wall', f'-I{header_files_dir}']
    shared_objects: list = []
    for lib, files in libs_files.items():
        in_files: list = [os.path.abspath(os.path.join(libs_files_dir, *lib, file)) for file in files]
        so_name: str = f'lib{lib[-1]}.so'
        so_path: str = os.path.join(build_dir, so_name)
        shared_objects.append(lib[-1])
        final_command = base_command + in_files + ['-o', so_path]
        subprocess.call(final_command)
    bins: list = []
    bin_base_command: list = ['gcc', f'-L{build_dir}'] + [f'-l{obj}' for obj in shared_objects]
    for fol, files in bin_files.items():
        for file in files:
            out_bin: str = file.replace('.c', '')
            out_bin_path: str = os.path.join(build_dir, out_bin)
            in_file = os.path.abspath(os.path.join(bin_files_dir, *fol, file))
            bins.append(out_bin)
            subprocess.call(bin_base_command + [in_file, '-o', out_bin_path])


def club_files(lib_files):
    files: dict = {}
    for lib, file in lib_files:
        if lib in files:
            files[lib].append(file)
        else:
            files[lib] = [file]
    return files


def pack_artefacts(config):
    name: str = config['name']
    platform_name: str = config['platform']
    version: str = config['version']
    extension: str = 'tar'
    build_dir: str = config['project_dirs']['build']
    local_cache_dir: str = config['pyposto_dirs']['local']
    artefact_name: str = f"{name}-{platform_name}-{version}.{extension}"
    cache_path: str = os.path.join(local_cache_dir, platform_name, name, version)
    output_filename = os.path.join(cache_path, artefact_name)
    os.makedirs(cache_path, mode=0o770, exist_ok=True)
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(build_dir, arcname='')


@ppd.config(config_default)
@ppd.do(os_config_homogenizer)
@ppd.do(setup_home)
@ppd.do(setup_project)
@ppd.do(setup_compiler_tool)
@ppd.do(compile_project)
def compile_c_app(conf):
    pass


@ppd.config(config_default)
@ppd.do(os_config_homogenizer)
@ppd.do(setup_home)
@ppd.do(setup_project)
@ppd.do(setup_compiler_tool)
@ppd.do(pack_artefacts)
def cache_local(conf):
    pass


if __name__ == '__main__':
    cache_local()
    # compile_c_app()
