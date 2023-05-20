from src.entities.api_song import APISong
from src.entities.storage_song import StorageSong
from src.services.api_service import APIService


class SongFactory:
    @staticmethod
    def create_song(song_template: str or tuple):
        if type(song_template) is str:
            api_serv = APIService()
            song_template = (song_template, api_serv.get_song_url(song_template))
        if type(song_template) is tuple:
            if song_template[1][:8] == 'https://':
                return APISong(song_template[0])
            elif song_template:
                return StorageSong(song_template)
            elif not song_template:
                return StorageSong(song_template[0])