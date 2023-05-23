from json import dump, load
from os import getcwd, path


class PathSettings:
    def __init__(self, paths=[]):
        self.paths = paths

    def save_paths(self, new_paths=None):
        filename = path.dirname(getcwd()) + rf'\sync_info\settings\paths.json'
        if not new_paths:
            path_info = self.paths
        else:
            path_info = new_paths
        with open(filename, 'w') as f:
            dump(path_info, f)

    def load_paths(self):
        filename = path.dirname(getcwd()) + rf'\sync_info\settings\paths.json'
        try:
            with open(filename, 'r') as f:
                path_info = load(f)
                self.paths = path_info
            return self.paths
        except FileNotFoundError:
            return None
