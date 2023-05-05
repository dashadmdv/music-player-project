import vlc


class Playback(object):
    def __init__(self):
        self.player = vlc.MediaPlayer()
        self.paused = False

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Playback, cls).__new__(cls)
        return cls.instance

    def play(self, source: str):
        media = vlc.Media(source)
        self.player.set_media(media)
        self.player.play()

    def pause(self):
        self.paused = not self.paused
        self.player.set_pause(int(self.paused))

    def stop(self):
        self.paused = False
        self.player.stop()
