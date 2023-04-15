from src.services.api_service import APIService

api_serv = APIService()


class Playlist:
    def __init__(self, id):
        self.id = id
        self.name = api_serv.get_playlist_name(self.id)
        self.songs = api_serv.get_playlist_songs(self.id)
        self.duration = api_serv.get_playlist_duration(self.id)

    def get_playlist_info(self):
        return api_serv.get_playlist_songs_info(self.id)
