import vlc
from src.controllers.queue import Queue


class Playback(object):
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.paused = False
        self.queue = Queue()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Playback, cls).__new__(cls)
        return cls.instance

    def play(self, song: tuple, playlist: list = []):
        if not song[1]:
            self.next()
        else:
            if self.queue.is_empty() and not playlist:
                self.queue.update(song)
            elif self.queue.is_empty() and playlist:
                self.queue.reload(song, playlist)
            else:
                self.queue.reload(song, playlist)
            media = vlc.Media(song[1])
            self.player.set_media(media)
            self.player.play()

    def pause(self):
        self.paused = not self.paused
        self.player.set_pause(int(self.paused))

    def stop(self):
        self.paused = False
        self.player.stop()

    def previous(self):
        prev = self.queue.previous()
        self.queue.update(prev)
        if not prev[1]:
            self.previous()
        else:
            self.stop()
            media = vlc.Media(prev[1])
            self.player.set_media(media)
            self.player.play()

    def next(self):
        last_song = self.queue.is_empty()
        next = self.queue.next()
        self.queue.update(next, last_song)
        if not next[1]:
            self.next()
        else:
            self.stop()
            media = vlc.Media(next[1])
            self.player.set_media(media)
            self.player.play()
