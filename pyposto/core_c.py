import os.path

import yaml


class CProjectDescription(object):
    def __init__(self, project_location: str, libraries: list, headers: list, c_files: list,
                 artefacts: list):
        self.project_location: str = project_location
        self.libraries: list = libraries
        self.headers: list = headers
        self.c_files: list = c_files
        self.artefacts: list = artefacts
        self._prepend_path: bool = False
        self._poject_meta_data: dict = self._populate_meta_data(self)

    @staticmethod
    def _populate_meta_data(obj):
        project_yaml = os.path.join(obj.project_location, 'posto.yml')
        project_meta = os.path.join(obj.project_location, 'posto.meta')
        project_desc = None
        if os.path.exists(project_yaml):
            project_desc = project_yaml
        elif os.path.exists(project_meta):
            project_desc = project_meta
        else:
            raise FileNotFoundError('Project description missing')
        return yaml.load(open(project_desc, 'r'), yaml.Loader)


if __name__ == '__main__':
    CProjectDescription('', [], [], [], [])
