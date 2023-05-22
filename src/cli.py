from entities.user import *
from entities.playlist import *
from services.api_service import *
from services.storage_service import *
from controllers.playback import *
from utils.song_factory import *
from threading import Thread
from src.sync.auth_sync import AuthSynchronization
from src.sync.path_settings import PathSettings
from utils.path_dialogue import *


class CLIDialogue:
    def __init__(self):
        self.api_serv = APIService()
        self.stor_serv = StorageService()
        self.user = None
        self.pl = Playback()

    def run(self):
        self.auth_dialogue()

        while True:
            try:
                nav_choice = int(
                    input('Choose a folder to open(1 - search, 2 - my library, 3 - settings), ' +
                          ('9 - open player, ' if self.pl.check_if_was_playing() else '') + '0 - exit the app: '))
            except ValueError:
                continue
            if nav_choice == 0:
                try:
                    exit_choice = int(input('Are you sure you want to exit app? 0 - yes, 1 - no: '))
                    if exit_choice == 0:
                        print('Goodbye then!')
                        break
                    elif exit_choice == 1:
                        continue
                except ValueError:
                    continue
            elif nav_choice == 1:
                self.search_dialogue()
            elif nav_choice == 2:
                self.library_dialogue()
            elif nav_choice == 3:
                self.settings_dialogue()
            elif nav_choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()
            else:
                continue

    def auth_dialogue(self, simplified=False):
        if not self.api_serv.refresh_token:
            while True:
                try:
                    if not simplified:
                        auth_choice = int(
                            input('Hello! You are not authorized :( Do you want to sign in? yes - 1, no - 0: '))
                    else:
                        auth_choice = 1
                    break
                except ValueError:
                    print('Type something correct please!')
                    continue
            if auth_choice == 1:
                print('You will now be redirected to the browser. ' +
                      'Please ACCEPT PERMISSIONS AND THEN COPY THE LINK YOU WILL GET IN THE BROWSER AND PASTE IT HERE')
                self.api_serv.auth_agent()
                while True:
                    code = input('The URL: ')
                    if code and code[:34] == 'https://google.com/callback/?code=':
                        self.api_serv.authentication(code)
                        self.auth_dialogue()
                        break
                    else:
                        print('Wrong URL')
                        continue
            elif auth_choice == 0:
                print('If you are not authorized, you will not have access to your library then. You can sign in ' +
                      'in the SETTINGS folder when you need to!')
        else:
            print(f'Hello, {self.api_serv.get_user_name(self.api_serv.get_current_user())}!')
            self.user = User(self.api_serv.get_current_user())

    def search_dialogue(self):
        while True:
            search_query = input('What do you want to listen? ')
            if not search_query:
                print('Input something!')
                continue
            break
        try:
            search_type = int(input('What are you looking for? 1 - track, 2 - album, 3 - playlist: '))
        except ValueError:
            search_type = 1
        if search_type == 1:
            search_type = 'track'
        elif search_type == 2:
            search_type = 'album'
        elif search_type == 3:
            search_type = 'playlist'
        search_items = self.api_serv.search(search_query, search_type)

        if search_type == 'track':
            while True:
                try:
                    song_choice = int(input('Select song(by index), go back - 0: '))
                except ValueError:
                    continue
                if song_choice == 0:
                    break
                elif song_choice > 20:
                    print("Try again!")
                    continue
                self.song_dialogue(search_items[song_choice - 1], playlist=[])
                break
        elif search_type == 'playlist' or search_type == 'album':
            while True:
                try:
                    choice = int(input(f'Select {search_type}(by index), go back - 0: '))
                except ValueError:
                    continue
                if choice == 0:
                    break
                elif choice > 20:
                    print("Try again!")
                    continue
                playlist = Playlist(id=str(search_items[choice - 1]), album=(search_type == 'album'))
                self.playlist_dialogue(playlist)
                break

    def library_dialogue(self):
        while True:
            try:
                prompt = 'Choose what you want to open(whole library - 1, only my playlists - 2, local songs - 3), or' \
                         ' create new playlist - 4, ' + (
                             '9 - open player, ' if self.pl.check_if_was_playing() else '') + \
                         'back to navigation - 0: '
                if not self.user:
                    print('You don\'t have full Spotify library access because you are not authorized :( ' +
                          'If you want full access you can log in in the SETTINGS folder!')
                    prompt = 'Choose what you want to do: open local songs - 3, ' + \
                             ('9 - open player, ' if self.pl.check_if_was_playing() else '') + \
                             'back to navigation - 0: '
                show_choice = int(input(prompt))
            except ValueError:
                continue
            if show_choice == 0:
                break
            elif show_choice == 1:
                if not self.user:
                    print("Authorize if you want to access your library :) You can do it in the SETTINGS folder!")
                    continue
                self.api_serv.get_user_library_info()
                library = self.api_serv.get_user_library()
            elif show_choice == 2:
                self.user.get_user_playlists_info()
            elif show_choice == 3:
                playlist = self.stor_serv.get_songs()
                while True:
                    try:
                        song_choice = int(input('Select song(by index), go back - 0: '))
                    except ValueError:
                        continue
                    if song_choice == 0:
                        break
                    elif len(playlist) == 0:
                        print('Playlist is empty!')
                        break
                    elif song_choice > len(playlist):
                        print("There is no such song in the playlist! Try again!")
                        continue

                    self.song_dialogue(playlist[song_choice - 1], playlist)
                    break
                continue
            elif show_choice == 4:
                name = input('Input new playlist name: ')
                description = input('Input new playlist description: ')
                public = None

                while True:
                    try:
                        public_choice = int(input('Do you want playlist to be private - 0 or public - 1: '))
                        if public_choice != 0 and public_choice != 1:
                            continue
                        else:
                            public = bool(public_choice)
                            break
                    except ValueError:
                        continue

                self.api_serv.create_playlist(user_id=self.user.id, name=name, public=public, description=description)
                self.user.update_playlists()
                continue
            elif show_choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()
                continue
            else:
                continue

            while True:
                try:
                    choice = int(input('Select playlist(by index), go back - 0: '))
                except ValueError:
                    continue

                playlist = None
                if choice == 0:
                    break
                if show_choice == 1:
                    if choice > len(library):
                        continue
                    if library[choice - 1] != 'favs':
                        playlist = Playlist(id=str(library[choice - 1]), album=((choice - 1) > library.index('favs')))
                else:
                    if choice > len(self.user.playlists):
                        continue
                    playlist = Playlist(id=str(self.user.playlists[choice - 1]))

                if not playlist:
                    self.fav_songs_dialogue(self.api_serv.get_favourite_songs())
                else:
                    self.playlist_dialogue(playlist)
                break

    def playlist_dialogue(self, playlist: Playlist):
        while True:
            try:
                owned = playlist.check_if_self_owned()
                followed = self.api_serv.check_if_followed(playlist.id, playlist.album)
                if (not followed) and (not owned):
                    following = '6 - add to the library, '
                elif followed and not owned:
                    following = '6 - delete from the library, '
                else:
                    following = ''
                extended_interactions = '4 - change info, 5 - delete playlist, ' if (self.user and owned) else ""
                choice = int(input('What do you want to do with the playlist?\n1 - show short info, 2 - open songs, '
                                   '3 - play, ' + f'{extended_interactions} ' + (following if self.user else '') +
                                   ('9 - open player, ' if self.pl.check_if_was_playing() else '') + 'go back - 0: '))
            except ValueError:
                continue

            if choice == 0:
                break
            elif choice == 1:
                playlist.get_playlist_info()
            elif choice == 2:
                playlist.get_playlist_songs_info()
                while True:
                    try:
                        song_choice = int(input('Select song(by index), go back - 0: '))
                    except ValueError:
                        continue
                    if song_choice == 0:
                        break
                    elif playlist.size == 0:
                        print('Playlist is empty!')
                        break
                    elif song_choice > playlist.size:
                        print("There is no such song in the playlist! Try again!")
                        continue

                    self.song_dialogue(playlist.songs[song_choice - 1], playlist)
                    break
            elif choice == 3:
                if not playlist.is_unavailable():
                    thread = Thread(target=self.pl.play, args=(playlist.songs[0], playlist.songs),
                                    daemon=True)
                    thread.start()
                    self.playback_dialogue()
                else:
                    print('It seems like this playlist is unavailable for listening! Sorry :(')
            elif choice == 4:
                new_name = None
                new_description = None
                new_public = None
                while True:
                    try:
                        name_choice = int(input('Do you want to change name? 0 - yes, 1 - no: '))
                        if name_choice == 0:
                            new_name = input('Input new playlist name: ')
                            break
                        elif name_choice == 1:
                            break
                    except ValueError:
                        continue

                while True:
                    try:
                        description_choice = int(input('Do you want to change description? 0 - yes, 1 - no: '))
                        if description_choice == 0:
                            new_description = input('Input new playlist description: ')
                            break
                        elif description_choice == 1:
                            break
                    except ValueError:
                        continue

                while True:
                    try:
                        publicity = self.api_serv.get_playlist_publicity(playlist.id)
                        public_choice = int(input('Do you want to change playlist publicity? Current publicity: ' +
                                                  ('public' if publicity else 'private') + '. 0 - yes, 1 - no: '))
                        if public_choice == 0:
                            new_public = not publicity
                            break
                        elif public_choice == 1:
                            break
                        else:
                            continue
                    except ValueError:
                        continue

                self.api_serv.update_playlist_info(playlist.id, name=new_name, public=new_public,
                                                   description=new_description)
            elif choice == 5:
                while True:
                    try:
                        del_choice = int(input('Are you sure you want to delete playlist? 0 - yes, 1 - no: '))
                        if del_choice == 0:
                            self.api_serv.delete_playlist(playlist.id)
                            self.user.update_playlists()
                            print('You can restore deleted playlist for 90 days here: ' +
                                  'https://www.spotify.com/us/account/recover-playlists/')
                            break
                        elif del_choice == 1:
                            break
                    except ValueError:
                        continue
                break
            elif choice == 6:
                if not followed and not owned:
                    playlist.follow()
                elif followed and not owned:
                    playlist.unfollow()
            elif choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()

    def fav_songs_dialogue(self, playlist: list):
        while True:
            try:
                choice = int(input('What do you want to do with the playlist?\n1 - show short info, 2 - open songs, '
                                   '3 - play, ' + ('9 - open player, ' if self.pl.check_if_was_playing() else '') +
                                   'go back - 0: '))
            except ValueError:
                continue

            if choice == 0:
                break
            elif choice == 1:
                self.api_serv.get_favorites_playlist_info()
            elif choice == 2:
                self.api_serv.get_favourite_songs_info()
                while True:
                    try:
                        song_choice = int(input('Select song(by index), go back - 0: '))
                    except ValueError:
                        continue
                    if song_choice == 0:
                        break
                    elif song_choice > len(playlist):
                        print("There is no such song in the playlist! Try again!")
                        continue

                    self.song_dialogue(playlist[song_choice - 1], playlist)
                    break
            elif choice == 3:
                thread = Thread(target=self.pl.play, args=(playlist[0], playlist),
                                daemon=True)
                thread.start()
                self.playback_dialogue()
            elif choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()

    def song_dialogue(self, song, playlist):
        song = SongFactory.create_song(song)
        while True:
            prompt = \
                'What do you want to do with the song?\n1 - show info, 2 - play, ' + \
                ('3 - add to playlist, 4 - like, ' if type(song) != StorageSong and self.user else '') + \
                '5 - add to queue, ' + ('9 - open player, ' if self.pl.check_if_was_playing() else '') + 'go back - 0: '
            try:
                choice = int(input(prompt))
            except ValueError:
                continue

            if choice == 0:
                break
            elif choice == 1:
                song.get_song_info()
            elif choice == 2:
                if playlist:
                    if type(playlist) == Playlist and not playlist.is_unavailable():
                        thread = Thread(target=self.pl.play, args=((song.id, song.source), playlist.songs), daemon=True)
                    elif type(playlist) == list:
                        available = False
                        for item in playlist:
                            available = available or bool(item[1])
                        if available:
                            thread = Thread(target=self.pl.play, args=((song.id, song.source), playlist), daemon=True)
                    else:
                        print('It seems like this playlist is unavailable for listening! Sorry :(')
                        continue
                else:
                    thread = Thread(target=self.pl.play, args=((song.id, song.source), []),
                                    daemon=True)
                if thread:
                    thread.start()
                    self.playback_dialogue()
                else:
                    print('Something went wrong :(')
            elif choice == 3:
                while True:
                    try:
                        self.user.get_user_playlists_info()
                        pl_choice = int(input('Select playlist to add song to(by index), go back - 0: '))
                    except ValueError:
                        continue
                    self.api_serv.add_song_to_playlist(self.user.playlists[pl_choice - 1], song.id)
                    break
            elif choice == 4:
                if type(song) == StorageSong:
                    print('Cannot like local tracks! Sorry :(')
                else:
                    favourites = self.api_serv.get_favourite_songs()
                    if (song.id, song.source) in favourites:
                        self.api_serv.delete_song_from_favourites(song.id)
                    else:
                        self.api_serv.add_song_to_favourites(song.id)
            elif choice == 5:
                self.pl.queue.add((song.id, song.source))
            elif choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()

    def playback_dialogue(self):
        while True:
            try:
                choice = int(input(
                    '1 - previous, 2 - pause/unpause, 3 - next, 4 - rewind track, 5 - state, ' +
                    '6 - change repeat mode, 7 - turn on/off shuffle, 8 - stop, 0 - go back: '))
            except ValueError:
                choice = 9
            if choice == 1:
                thread = Thread(target=self.pl.previous, daemon=True)
                thread.start()
            if choice == 2:
                self.pl.pause()
            if choice == 3:
                thread = Thread(target=self.pl.next, daemon=True)
                thread.start()
            if choice == 4:
                secs = input(
                    'Write seconds and + to go forth, - to go back, nothing to jump to that second: ')
                if secs[-1].isdigit():
                    try:
                        self.pl.set_time(int(secs))
                    except ValueError:
                        continue
                else:
                    try:
                        self.pl.set_time(int(secs[:-1]), secs[-1])
                    except ValueError:
                        continue
            if choice == 5:
                song = SongFactory.create_song(self.pl.queue.cur_song)
                artist = song.artist
                print('Track: ', song.title + (f' - {artist}' if artist else ''))
                seconds = str(self.pl.player.get_time() // 1000 % 60 + 100)
                print(f'Time: {self.pl.player.get_time() // 1000 // 60}:{seconds[1:]}')
                print('Player state: ', self.pl.player.get_state())
                repeat_modes = ['no repeat', 'repeat track', 'repeat playlist']
                print('Repeat mode: ' + repeat_modes[self.pl.repeat_mode] + f'({self.pl.repeat_mode})')
                print('Shuffle mode: ' + ('on' if self.pl.queue.shuffle_mode else 'off'))
            if choice == 6:
                try:
                    mode = int(input(
                        "Enter repeat mode: 0 - no repeat, 1 - repeat track, 2 - repeat playlist: "))
                except ValueError:
                    mode = 3
                self.pl.change_repeat_mode(mode)
            if choice == 7:
                self.pl.shuffle()
            if choice == 8:
                self.pl.stop()
            if choice == 0:
                break

    def settings_dialogue(self):
        while True:
            try:
                nav_choice = int(
                    input('Choose option(1 - log in, 2 - log out, 3 - choose folders to show local songs from), ' +
                          ('9 - open player, ' if self.pl.check_if_was_playing() else '') + '0 - go back: '))
            except ValueError:
                continue
            if nav_choice == 0:
                break
            elif nav_choice == 1:
                if self.user:
                    print('You are authorized! If you want to log in as a different user you should LOG OUT first')
                    continue
                else:
                    self.auth_dialogue(simplified=True)
            elif nav_choice == 2:
                if not self.user:
                    print("You can't log out because you have not logged in yet :)")
                    continue
                else:
                    try:
                        exit_choice = int(input('Are you sure you want to log out? 0 - yes, 1 - no: '))
                        if exit_choice == 0:
                            auth_sync = AuthSynchronization(self.user.id)
                            auth_sync.delete_token()
                            self.user = None
                            self.api_serv.__init__()
                            break
                        elif exit_choice == 1:
                            continue
                    except ValueError:
                        continue

            elif nav_choice == 3:
                path_sync = PathSettings()
                paths = path_sync.load_paths() or []

                print('Your current chosen folders: ' + ('None' if not paths else ''))
                if paths:
                    for i, item in enumerate(paths):
                        print(f'{i+1} - {item}')
                try:
                    path_choice = int(input('Do you want to add - 1 or delete - 2 source directories? go back - 0: '))
                    if path_choice == 0:
                        continue
                    elif path_choice == 1:
                        new_path = select_path()
                        if new_path:
                            set_paths = set(paths)
                            set_paths.add(new_path)
                            paths = list(set_paths)
                            path_sync.save_paths(paths)
                    elif path_choice == 2:
                        while True:
                            try:
                                path_del_choice = int(input('Select directory(by index) to delete, go back - 0: '))
                            except ValueError:
                                continue
                            if path_del_choice == 0:
                                break
                            elif path_del_choice > len(paths):
                                print("Try again!")
                                continue
                            paths.pop(path_del_choice-1)
                            path_sync.save_paths(paths)
                            break
                except ValueError:
                    continue

            elif nav_choice == 9 and self.pl.check_if_was_playing():
                self.playback_dialogue()
            else:
                continue
