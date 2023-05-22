from json import dump, load
from os import getcwd, walk, remove, path as Path


class AuthSynchronization:
    def __init__(self, user=None, token=None):
        self.user_name = user
        self.refresh_token = token

    def save_token(self):
        filename = Path.dirname(getcwd()) + rf'\sync_info\users\{self.user_name}.json'
        auth_info = [self.user_name, self.refresh_token]
        with open(filename, 'w') as f:
            dump(auth_info, f)

    def load_token(self):
        filename = ''
        if not self.user_name:
            path = Path.dirname(getcwd()) + r"\sync_info\users"
            for root, dirs, files in walk(path):
                for file in files:
                    if file.endswith('.json'):
                        filename = Path.dirname(getcwd()) + rf'\sync_info\users\{file}'
        else:
            filename = Path.dirname(getcwd()) + rf'\sync_info\users\{self.user_name}.json'
        try:
            with open(filename, 'r') as f:
                auth_info = load(f)
                self.user_name = auth_info[0]
                self.refresh_token = auth_info[1]
            return self.refresh_token
        except FileNotFoundError:
            return None

    def delete_token(self):
        filename = ''
        if not self.user_name:
            path = Path.dirname(getcwd()) + r"\sync_info\users"
            for root, dirs, files in walk(path):
                for file in files:
                    if file.endswith('.json'):
                        filename = Path.dirname(getcwd()) + rf'\sync_info\users\{file}'
        else:
            filename = Path.dirname(getcwd()) + rf'\sync_info\users\{self.user_name}.json'
        try:
            if Path.isfile(filename):
                remove(filename)
        except FileNotFoundError:
            pass
