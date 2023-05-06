from src.services.storage_service import *
from src.services.api_service import *
from multipledispatch import dispatch

api_serv = APIService()
stor_serv = StorageService()


class Queue(object):
    def __init__(self):
        self.previous_songs = []
        self.first_order_ids = []
        self.song_ids = []
        self.cur_song = ''
        self.cur_playlist = ''

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Queue, cls).__new__(cls)
        return cls.instance

    @dispatch(tuple)
    def add(self, song: str or tuple):
        self.first_order_ids.append((song[0], stor_serv.get_song_path(song[0])))

    @dispatch(tuple, list)
    def add(self, song: tuple, playlist: list):
        start_index = playlist.index(song)
        songs_to_add = (playlist[start_index+1:])
        self.song_ids.extend(songs_to_add)
        self.previous_songs.extend((playlist[:start_index]))
        self.cur_song = song

    def update(self, song: tuple):
        if song in self.previous_songs:
            self.song_ids.insert(0, self.cur_song)
            self.cur_song = self.previous_songs.pop()
        elif song in self.song_ids:
            self.previous_songs.append(self.cur_song)
            self.cur_song = self.song_ids.pop(0)
        elif song in self.first_order_ids:
            self.previous_songs.append(self.cur_song)
            self.cur_song = self.first_order_ids.pop(0)
        else:
            self.reload(song, [])

    def reload(self, song: tuple, playlist: list):
        self.clear()
        self.add(song, playlist)

    def clear(self):
        self.first_order_ids.clear()
        self.song_ids.clear()
        self.previous_songs.clear()

    def previous(self):
        if not self.previous_songs:
            return self.cur_song
        else:
            self.cur_song = self.previous_songs[-1]
            return self.previous_songs[-1]

    def next(self):
        if not self.first_order_ids:
            if self.is_empty():
                self.song_ids = self.previous_songs.copy()
                self.previous_songs.clear()
            self.cur_song = self.song_ids[0]
            return self.song_ids[0]
        else:
            self.cur_song = self.first_order_ids[0]
            return self.first_order_ids[0]

    def is_empty(self):
        return not self.first_order_ids and not self.song_ids