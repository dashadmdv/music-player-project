from src.services.storage_service import StorageService

stor_serv = StorageService()


# the reason why the title is the main property instead of path
# is that Spotify API does not give you access to local file's path
# instead it can only give you the song's title, which is file's metadata
class StorageSong:
    def __init__(self, title):
        self.title = title
        self.path = stor_serv.get_song_path(title)
        self.artist = stor_serv.get_song_artist(self.path)
        self.album = stor_serv.get_song_album(self.path)
        self.duration = stor_serv.get_song_duration(self.path)
        self.cover = stor_serv.get_song_cover(self.path)
        self.date = stor_serv.get_song_date(self.path)

    def get_song_info(self):
        return stor_serv.get_song_info(self.title)
