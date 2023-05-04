import eyed3
import os

eyed3.log.setLevel("ERROR")


class StorageService:
    def __init__(self, paths=[r"C:\Users\user\Music", r"C:\Users\user\Downloads"]):
        self.paths = paths

    def get_song_path(self, title: str):
        for path in self.paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.mp3'):
                        cur_path = root + '\\' + str(file)
                        cur_title = StorageService.get_song_title(cur_path)
                        if title == cur_title:
                            return cur_path

    @staticmethod
    def get_song_title(path: str):
        audio = eyed3.load(path)
        try:
            return audio.tag.title
        except:
            return ''

    @staticmethod
    def get_song_artist(path: str):
        audio = eyed3.load(path)
        try:
            return audio.tag.artist
        except:
            return ''

    @staticmethod
    def get_song_album(path: str):
        audio = eyed3.load(path)
        try:
            return audio.tag.album
        except:
            return ''

    @staticmethod
    def get_song_duration(path: str):
        audio = eyed3.load(path)
        try:
            return audio.info.time_secs
        except:
            return 0

    @staticmethod
    def get_song_cover(path: str):
        audio = eyed3.load(path)
        try:
            return audio.tag.image_urls
        except:
            return ''

    @staticmethod
    def get_song_date(path: str):
        audio = eyed3.load(path)
        try:
            return audio.tag.date
        except:
            return ''

    def get_song_info(self, title: str):
        path = self.get_song_path(title)
        print(StorageService.get_song_title(path) + ' - ' + StorageService.get_song_artist(path))
        duration = StorageService.get_song_duration(path)
        seconds = str(int(duration % 60 + 100))
        print(f'Duration: {int(duration // 60)}:{seconds[1:]}')
        print('Album: ' + StorageService.get_song_album(path))
        print('Release date: ' + StorageService.get_song_date(path))
        print('Cover: ' + StorageService.get_song_cover(path))
        print('Path: ' + path)
