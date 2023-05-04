from src.services.api_service import APIService

api_serv = APIService()


class APISong:
    def __init__(self, id):
        self.id = id
        self.title = api_serv.get_song_title(self.id)
        self.artist = api_serv.get_song_artist(self.id)
        self.album_id = api_serv.get_song_album(self.id)
        self.duration = api_serv.get_song_duration(self.id)
        self.cover = api_serv.get_song_cover(self.id)
        self.date = api_serv.get_song_date(self.id)
        self.preview_url = api_serv.get_song_url(self.id)
        self.genre = []

    def get_song_info(self):
        return api_serv.get_song_info(self.id)
