import vlc
from time import sleep
from src.utils.custom_thread import CustomThread
from src.controllers.queue import Queue


class Playback(object):
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.queue = Queue()
        self.paused = False
        self.repeat_mode = 2  # 0 - no repeat, 1 - track repeat, 2 - playlist repeat

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Playback, cls).__new__(cls)
        return cls.instance

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
            self.start_play(song[1])

    def start_play(self, source: str, no_repeat: bool = False):
        media = vlc.Media(source)
        self.player.set_media(media)
        self.player.play()
        thread2 = CustomThread(target=self.check_if_ended, args=self.player)
        if no_repeat:
            self.set_time(0)
            self.pause()
        thread2.start()
        thread2.join()
        ended = thread2.value
        if ended and self.repeat_mode == 0 or self.repeat_mode == 2:
            self.next()
        elif ended and self.repeat_mode == 1:
            self.start_play(self.queue.cur_song[1])

    def pause(self):
        self.paused = not self.paused
        self.player.set_pause(int(self.paused))

    def stop(self):
        self.paused = True
        self.player.stop()

    def previous(self):
        prev = self.queue.previous()
        self.queue.update(prev)
        if not prev[1]:
            self.previous()
        else:
            self.start_play(prev[1])

    def next(self):
        last_song = self.queue.is_empty()
        next = self.queue.next()
        self.queue.update(next, last_song)
        if not next[1]:
            self.next()
        elif last_song and self.repeat_mode == 0:
            self.start_play(next[1], True)
        else:
            if self.repeat_mode == 1:
                self.change_repeat_mode(2)
            self.start_play(next[1])

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

    def check_if_was_playing(self):
        return self.player.get_state() == vlc.State.Paused \
                or self.player.get_state() == vlc.State.Playing \
                or self.player.get_state() == vlc.State.Opening

    def change_repeat_mode(self, mode: int):
        if mode not in [0, 1, 2]:
            pass
        else:
            self.repeat_mode = mode

    def shuffle(self):
        self.queue.shuffle()
