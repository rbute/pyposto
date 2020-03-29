import os.path
import platform
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
    file_name = os.path.join(conf['pyposto_dirs']['raw'], get_url_file_name(conf['compiler_bin_url']))
    if not os.path.exists(file_name):
        dl_raw(conf['compiler_bin_url'], conf['pyposto_dirs']['raw'])
        extract_all(file_name, conf['pyposto_dirs']['tools'])



def os_config_homogenizer(conf):
    os_conf: dict = {}
    if platform.system():
        conf.update(conf['_os_overrides_'][platform.system()])
    conf.pop('_os_overrides_')


def setup_home2(conf):
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
@ppd.do(setup_home2)
@ppd.do(setup_compiler_tool)
def compile_c_app(conf):
    print('Example compilation step')


if __name__ == '__main__':
    compile_c_app()
