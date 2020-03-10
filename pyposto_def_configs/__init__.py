import copy

common_cofig: dict = {
    'repo': '',
    'org': '',
    'name': '',
    'version': '',
    'libs': '',
    'platform': 'terminal',
    'artefact_type': '',
    'compiler_bin_url': '',
    '_required_fields_': '',
    '_os_overrides_': {
        'win': {
            'compiler_bin_url': '',
        },
        'macos': {
            'compiler_bin_url': '',
        },
        'linux': {
            'compiler_bin_url': '',
        }
    }
}

terminal_app_c: dict = copy.deepcopy(common_cofig)
terminal_app_c.update({
    'artifact_type': 'executable',
})

terminal_app_cpp: dict = copy.deepcopy(common_cofig)
terminal_app_c.update({
    'artifact_type': 'executable',
})

shared_lib_c: dict = copy.deepcopy(common_cofig)
shared_lib_c.update({
    'artifact_type': 'lib',
})

shared_lib_cpp: dict = copy.deepcopy(common_cofig)
shared_lib_cpp.update({
    'artifact_type': 'lib',
})

static_lib_c: dict = copy.deepcopy(common_cofig)
static_lib_c.update({
    'artifact_type': 'static',
})

static_lib_cpp: dict = copy.deepcopy(common_cofig)
static_lib_cpp.update({
    'artifact_type': 'static',
})

standalone_app_c: dict = copy.deepcopy(common_cofig)
standalone_app_c.update({
    'artifact_type': 'standalone',
})

standalone_app_cpp: dict = copy.deepcopy(common_cofig)
standalone_app_cpp.update({
    'artifact_type': 'standalone',
})

desktop_app_c: dict = copy.deepcopy(common_cofig)
desktop_app_c.update({
    'artifact_type': 'desktop_app',
})

desktop_app_cpp: dict = copy.deepcopy(common_cofig)
desktop_app_cpp.update({
    'artifact_type': 'desktop_app',
})

__all__ = [
    'terminal_app_c',
    'terminal_app_cpp',
    'shared_lib_c',
    'shared_lib_cpp',
    'static_lib_c',
    'static_lib_cpp',
    'standalone_app_c',
    'standalone_app_cpp',
    'desktop_app_c',
    'desktop_app_cpp',
]
