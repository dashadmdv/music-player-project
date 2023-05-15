from entities.user import *
from entities.playlist import *
from services.api_service import *
from services.storage_service import *
from controllers.playback import *
from threading import Thread


# TO BE DONE: PLAYLIST&SONG DIALOGUE, SEARCH ITEMS DIALOGUE + REFACTORING


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
                    input('Choose a folder to open(1 - search, 2 - my library, 3 - settings), 0 - exit the app: '))
            except ValueError:
                continue
            if nav_choice == 1:
                search_query = input('What do you want to listen? ')
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

            if nav_choice == 3:
                pass
            if nav_choice == 0:
                print('Goodbye then!')
                break
            if nav_choice == 2:
                if not self.user:
                    print("Authorize if you want to access your library :) You can do it in the SETTINGS folder!")
                    continue
                while True:
                    try:
                        show_choice = int(
                            input('Choose what you want to open(whole library - 1, only your playlists - 2), ' +
                                  'back to navigation - 0: '))
                    except ValueError:
                        continue
                    if show_choice == 1:
                        self.api_serv.get_user_library_info()
                        library = self.api_serv.get_user_library()
                    elif show_choice == 2:
                        self.user.get_user_playlists_info()
                    else:
                        break

                    while True:
                        try:
                            choice = int(input('Select playlist(by index), go back - 0: '))
                        except ValueError:
                            continue

                        if choice == 0:
                            break
                        if show_choice == 1:
                            if choice > len(library):
                                continue
                            playlist = Playlist(id=str(library[choice - 1]))
                        else:
                            if choice > len(self.user.playlists):
                                continue
                            playlist = Playlist(id=str(self.user.playlists[choice - 1]))

                        # I play 3rd last song automatically - playlist & song dialogue will be done later
                        thread = Thread(target=self.pl.play, args=(playlist.songs[-3], playlist.songs), daemon=True)
                        thread.start()

                        self.playback_dialogue()
            else:
                continue

    def auth_dialogue(self):
        if not self.api_serv.refresh_token:
            while True:
                try:
                    auth_choice = int(input('Hello! You are not authorized :( Do you want to sign in? yes - 1, no - 0'))
                    break
                except ValueError:
                    print('Type something correct please!')
                    continue
            if auth_choice == 1:
                print('You will now be redirected to the browser. ' +
                      'Please ACCEPT PERMISSIONS AND THEN COPY THE LINK YOU WILL GET IN THE BROWSER AND PASTE IT HERE')
                self.api_serv.auth_agent()
                code = input('The URL: ')
                self.api_serv.authentication(code)
            elif auth_choice == 0:
                print('If you are not authorized, you will not have access to your library then. You can sign in ' +
                      'in the SETTINGS folder when you need to!')
        else:
            print(f'Hello, {self.api_serv.get_user_name(self.api_serv.get_current_user())}!')
            self.user = User(self.api_serv.get_current_user())

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
                song = self.pl.queue.cur_song
                if song[1][:8] == 'https://':
                    print('Track: ', self.api_serv.get_song_title(song[0]), ' - ',
                          self.api_serv.get_song_artist(song[0]))
                else:
                    artist = self.stor_serv.get_song_artist(song[1])
                    print('Track: ', song[0] + (f' - {artist}' if artist else ''))
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
