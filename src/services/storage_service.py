import eyed3
import os
from dashadmdv_music_player_sync.path_settings import PathSettings

eyed3.log.setLevel("ERROR")


class StorageService:
    def __init__(self, paths=[]):
        self.path_sync = PathSettings()
        self.paths = self.path_sync.load_paths()

    def get_song_path(self, title: str):
        if self.paths:
            for path in self.paths:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(".mp3") or file.endswith(".m4a"):
                            cur_path = root + "\\" + str(file)
                            cur_title = StorageService.get_song_title(cur_path)
                            if (
                                title == cur_title
                                or title == str(file)[:-4]
                                or str(file)[:-4].count(title)
                            ):
                                return cur_path
        else:
            return ""

    @staticmethod
    def get_song_title(path: str):
        try:
            audio = eyed3.load(path)
            return audio.tag.title or ""
        except:
            return ""

    @staticmethod
    def get_song_artist(path: str):
        try:
            audio = eyed3.load(path)
            return audio.tag.artist or ""
        except:
            return ""

    @staticmethod
    def get_song_album(path: str):
        try:
            audio = eyed3.load(path)
            return audio.tag.album or ""
        except:
            return ""

    @staticmethod
    def get_song_duration(path: str):
        try:
            audio = eyed3.load(path)
            return audio.info.time_secs
        except:
            return 0

    @staticmethod
    def get_song_cover(path: str):
        try:
            audio = eyed3.load(path)
            return audio.tag.image_urls or ""
        except:
            return ""

    @staticmethod
    def get_song_date(path: str):
        try:
            audio = eyed3.load(path)
            return audio.tag.date or ""
        except:
            return ""

    def get_song_info(self, title: str):
        path = self.get_song_path(title)
        name = (
            StorageService.get_song_title(path)
            + " - "
            + StorageService.get_song_artist(path)
        )
        if name == " - ":
            print(title)
        else:
            print(name)
        duration = StorageService.get_song_duration(path)
        seconds = str(int(duration % 60 + 100))
        print(f"Duration: {int(duration // 60)}:{seconds[1:]}")
        print("Album: " + StorageService.get_song_album(path))
        print("Release date: " + StorageService.get_song_date(path))
        print("Cover: " + StorageService.get_song_cover(path))
        print("Path: " + path)

    def get_songs(self):
        if self.paths:
            local_songs = []
            for path in self.paths:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(".mp3") or file.endswith(".m4a"):
                            cur_path = root + "\\" + str(file)
                            cur_title = StorageService.get_song_title(cur_path)
                            local_songs.append((cur_title, cur_path))
                            name = (
                                cur_title
                                + " - "
                                + StorageService.get_song_artist(cur_path)
                            )
                            if name == " - ":
                                print(f"{len(local_songs)} - {str(file)[:-4]}")
                            else:
                                print(f"{len(local_songs)} - {name}")
                            duration = StorageService.get_song_duration(cur_path)
                            seconds = str(int(duration % 60 + 100))
                            print(f"Duration: {int(duration // 60)}:{seconds[1:]}")
            return local_songs
        else:
            print(
                "You didn't specify directories to get music from! You can do it in the SETTINGS folder"
            )
            return []
