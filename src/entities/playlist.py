from src.services.api_service import APIService

api_serv = APIService()


class Playlist:
    def __init__(self, id, album=False):
        self.id = id
        self.album = album
        if not album:
            self.name = api_serv.get_playlist_name(self.id)
            self.size = api_serv.get_playlist_size(self.id)
            self.songs = api_serv.get_playlist_songs(self.id, self.size)
            self.duration = api_serv.get_playlist_duration(self.id, self.size)
        else:
            self.name = api_serv.get_album_name(self.id)
            self.size = api_serv.get_album_size(self.id)
            self.songs = api_serv.get_album_songs(self.id, self.size)
            self.duration = api_serv.get_album_duration(self.id, self.size)

    def is_unavailable(self):
        available = False
        for item in self.songs:
            available = available or bool(item[1])
        return not available

    def check_if_self_owned(self):
        return api_serv.check_if_self_owned(self.id)

    def check_if_followed(self):
        return api_serv.check_if_followed(self.id, self.album)

    def add_song(self, song_id: str, position: int = 0):
        return api_serv.add_song_to_playlist(self.id, song_id, position)

    def delete_song(self, song_id: str):
        return api_serv.delete_song_from_playlist(self.id, song_id)

    def follow(self):
        if not self.album:
            api_serv.follow_playlist(self.id)
        else:
            api_serv.follow_album(self.id)

    def unfollow(self):
        if not self.album:
            api_serv.unfollow_playlist(self.id)
        else:
            api_serv.unfollow_album(self.id)

    def get_playlist_info(self):
        if not self.album:
            return api_serv.get_playlist_info(self.id)
        else:
            return api_serv.get_album_info(self.id)

    def get_playlist_songs_info(self):
        if not self.album:
            return api_serv.get_playlist_songs_info(self.id, self.size)
        else:
            return api_serv.get_album_songs_info(self.id, self.size)

    def add_to_another_playlist(self, dest_id: str):
        api_serv.add_playlist_to_playlist(self.songs, dest_id)
