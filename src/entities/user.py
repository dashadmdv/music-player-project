from src.services.api_service import APIService

api_serv = APIService()


class User:
    def __init__(self, id):
        self.id = id
        self.name = api_serv.get_user_name()
        self.token = api_serv.update_token()
        self.playlists = api_serv.get_user_playlists(self.id)
        self.preferences = []

    def get_user_playlists_info(self):
        return api_serv.get_user_playlists_info(self.id)
