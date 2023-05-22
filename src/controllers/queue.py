from src.services.storage_service import *
from src.services.api_service import *
from multipledispatch import dispatch
from random import shuffle

api_serv = APIService()
stor_serv = StorageService()


class Queue(object):
    def __init__(self):
        self.previous_songs = []
        self.first_order_ids = []
        self.song_ids = []
        self.whole_playlist = []
        self.cur_song = ''
        self.cur_playlist = ''
        self.shuffle_mode = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Queue, cls).__new__(cls)
        return cls.instance

    @dispatch(tuple)
    def add(self, song: tuple):
        self.first_order_ids.append((song[0], song[1]))

    @dispatch(tuple, list)
    def add(self, song: tuple, playlist: list):
        if playlist:
            start_index = playlist.index(song)
            songs_to_add = (playlist[start_index + 1:])
            self.song_ids.extend(songs_to_add)
            self.previous_songs.extend((playlist[:start_index]))
        self.cur_song = song
        if not self.shuffle_mode:
            self.whole_playlist = playlist

    @dispatch(str, list)
    def add(self, song: str, playlist: list):
        song = (song, api_serv.get_song_url(song))
        playlist = [(item, api_serv.get_song_url(item)) for item in playlist]
        self.add(song, playlist)

    def update(self, song: tuple, last_song: bool = False):
        song_queue_count = self.previous_songs.count(self.cur_song) + self.first_order_ids.count(self.cur_song) + \
                           self.song_ids.count(self.cur_song) + 1
        song_playlist_count = self.whole_playlist.count(self.cur_song)
        if self.first_order_ids and song == self.first_order_ids[0]:
            if not (song_queue_count > song_playlist_count):
                self.previous_songs.append(self.cur_song)
            self.cur_song = self.first_order_ids.pop(0)
        elif self.previous_songs and song == self.previous_songs[-1]:
            if not (song_queue_count > song_playlist_count):
                self.song_ids.insert(0, self.cur_song)
            self.cur_song = self.previous_songs.pop()
        elif self.song_ids and song == self.song_ids[0]:
            if not last_song:
                if not (song_queue_count > song_playlist_count):
                    self.previous_songs.append(self.cur_song)
            self.cur_song = self.song_ids.pop(0)
        elif song is self.cur_song:
            pass
        else:
            self.reload(song, [song])

    def reload(self, song: tuple, playlist: list):
        self.clear()
        self.add(song, playlist)

    def clear(self):
        self.song_ids.clear()
        self.previous_songs.clear()

    def previous(self):
        if not self.previous_songs:
            return self.cur_song
        else:
            return self.previous_songs[-1]

    def next(self):
        if not self.first_order_ids:
            if self.is_empty():
                if self.previous_songs:
                    song_queue_count = self.previous_songs.count(self.cur_song) + self.first_order_ids.count(
                        self.cur_song) + \
                                       self.song_ids.count(self.cur_song) + 1
                    song_playlist_count = self.whole_playlist.count(self.cur_song)
                    if not (song_queue_count > song_playlist_count):
                        self.previous_songs.append(self.cur_song)
                    self.song_ids = self.previous_songs.copy()
                    self.previous_songs.clear()
                else:
                    return self.cur_song
            return self.song_ids[0]
        else:
            return self.first_order_ids[0]

    def is_empty(self):
        available = False
        for item in self.first_order_ids:
            available = available or bool(item[1])
        for item in self.song_ids:
            available = available or bool(item[1])
        return (not self.first_order_ids and not self.song_ids) or not available

    def shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            shuffled_playlist = self.whole_playlist.copy()
            shuffle(shuffled_playlist)
            if self.cur_song in self.whole_playlist:
                cur_song = self.cur_song
            else:
                cur_song = self.song_ids[0]
            del shuffled_playlist[shuffled_playlist.index(cur_song)]
            shuffled_playlist.insert(0, cur_song)
            self.song_ids.clear()
            self.previous_songs.clear()
            self.add(cur_song, shuffled_playlist)
        else:
            if self.cur_song in self.whole_playlist:
                cur_song = self.cur_song
            else:
                cur_song = self.song_ids[0]
            self.song_ids.clear()
            self.previous_songs.clear()
            self.add(cur_song, self.whole_playlist)
