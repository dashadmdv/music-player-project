import vlc
from time import sleep
from src.utils.custom_thread import CustomThread
from multipledispatch import dispatch
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

    @dispatch(tuple, list)
    def play(self, song: tuple, playlist: list = []):
        if not song[1] and not playlist and not self.queue.previous_songs:
            self.next()
        else:
            if self.queue.is_empty() and not playlist:
                self.queue.update(song)
            elif self.queue.is_empty() and playlist:
                self.queue.reload(song, playlist)
            else:
                self.queue.reload(song, playlist)
            # the 2nd check is for the case when the first ever song
            # we want to play doesn't have a source to play it from
            if not song[1]:
                self.next()
            self.play(song[1])

    @dispatch(str)
    def play(self, source: str):
        self.stop()
        media = vlc.Media(source)
        self.player.set_media(media)
        self.player.play()
        thread2 = CustomThread(target=self.check_if_ended, args=self.player)
        thread2.start()
        thread2.join()
        ended = thread2.value
        if ended:
            self.next()

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
            self.play(prev[1])

    def next(self):
        last_song = self.queue.is_empty()
        next = self.queue.next()
        self.queue.update(next, last_song)
        if not next[1]:
            self.next()
        else:
            self.play(next[1])

    def set_time(self, seconds: int, operator: str = '='):
        cur_time = self.player.get_time()
        if operator == '+':
            self.player.set_time(cur_time + seconds * 1000)
        elif operator == '-':
            self.player.set_time(cur_time - seconds * 1000)
        elif operator == '=':
            self.player.set_time(seconds * 1000)

    def check_if_ended(self, player: vlc.MediaPlayer):
        while player.get_state() != vlc.State.Playing:
            sleep(0.001)
        while player.get_state() != vlc.State.Ended:
            sleep(0.001)
        if player.get_state() == vlc.State.Ended:
            return True
        return False
