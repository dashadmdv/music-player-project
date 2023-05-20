from src.services.api_service import APIService

api_serv = APIService()


class APISong:
    def __init__(self, id):
        template = api_serv.get_song(id)
        self.id = id
        self.title = template['title']
        self.artist = template['artist']
        self.album_id = template['album_id']
        self.duration = template['duration']
        self.cover = template['cover']
        self.date = template['date']
        self.source = template['source']

    def get_song_info(self):
        return api_serv.get_song_info(self.id)
