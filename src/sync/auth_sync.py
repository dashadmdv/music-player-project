from json import dump, load
from pathlib import Path


class AuthSynchronization:
    def __init__(self, user=None, token=None):
        self.user_name = user
        self.refresh_token = token

    def save_token(self):
        filename = f'{self.user_name}.json'
        auth_info = [self.user_name, self.refresh_token]
        with open(filename, 'w') as f:
            dump(auth_info, f)

    def load_token(self):
        if not self.user_name:
            path = Path(".")
            extension = ".json"
            filename = next(path.glob(f"*{extension}"))
        else:
            filename = f'{self.user_name}.json'
        try:
            with open(filename, 'r') as f:
                auth_info = load(f)
                self.user_name = auth_info[0]
                self.refresh_token = auth_info[1]
            return self.refresh_token
        except FileNotFoundError:
            return None
