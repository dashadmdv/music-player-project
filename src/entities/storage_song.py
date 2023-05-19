from src.services.storage_service import StorageService

stor_serv = StorageService()


# the reason why the title is the main property instead of path
# is that Spotify API does not give you access to local file's path
# instead it can only give you the song's title, which is file's metadata
class StorageSong:
    def __init__(self, title: str or tuple):
        if type(title) is tuple:
            self.title = title[0]
            self.id = self.title
            self.source = title[1]
        else:
            self.title = title
            self.id = self.title
            self.source = stor_serv.get_song_path(self.title)
        self.artist = stor_serv.get_song_artist(self.source)
        self.album = stor_serv.get_song_album(self.source)
        self.duration = stor_serv.get_song_duration(self.source)
        self.cover = stor_serv.get_song_cover(self.source)
        self.date = stor_serv.get_song_date(self.source)

    def get_song_info(self):
        return stor_serv.get_song_info(self.title)
