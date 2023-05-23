from requests import get, post, put, delete
from math import ceil
from webbrowser import open_new_tab
from src.services.storage_service import StorageService
from json import dumps
from dashadmdv_music_player_sync.auth_sync import AuthSynchronization
from src.utils.check_connection import connect


class APIService:
    def __init__(self, user_id=None):
        self.client_id = '278b5ce854d54d088d5c740a768dc46e'
        self.client_secret = 'b17bff721823449586b80a86ef6d5c26'
        self.redirect_uri = 'https://google.com/callback/'
        self.base_uri = 'https://api.spotify.com/v1'
        self.auth_sync = AuthSynchronization(user=user_id)
        self.refresh_token = self.auth_sync.load_token()
        if not self.refresh_token:
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=self.update_token())
            }
        else:
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=self.refresh_user_token())
            }
        self.scope = 'user-library-read user-read-private user-read-email user-library-modify ' + \
                     'playlist-modify-public playlist-read-private playlist-modify-private'

    # --------------------- AUTHORIZATION RELATED FUNCTIONS -------------------------

    def auth_agent(self):
        if connect():
            auth_url = f'https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code' + \
                       f'&redirect_uri={self.redirect_uri}&scope={self.scope.replace(" ", "+")}&state=34fFs29kd09'
            open_new_tab(auth_url)

    def authentication(self, code_url: str):
        if connect():
            substring = 'https://google.com/callback/?code='
            index1 = code_url.find(substring) - 1
            index2 = code_url.find('&state=34fFs29kd09')
            auth_code = code_url[index1 + len(substring) + 1: index2]
            auth_url = 'https://accounts.spotify.com/api/token'
            auth_response = post(auth_url, {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
            })
            auth_response_data = auth_response.json()
            self.refresh_token = auth_response_data['refresh_token']
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=auth_response_data['access_token'])
            }
            self.auth_sync.__init__(self.get_current_user(), self.refresh_token)
            self.auth_sync.save_token()

    def update_token(self):
        if connect():
            auth_url = 'https://accounts.spotify.com/api/token'
            auth_response = post(auth_url, {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            })
            auth_response_data = auth_response.json()
            access_token = auth_response_data['access_token']
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=access_token)
            }
            return access_token
        else:
            return None

    def refresh_user_token(self):
        if connect():
            if not self.auth_sync.load_token():
                return self.update_token()
            auth_url = 'https://accounts.spotify.com/api/token'
            auth_response = post(auth_url, {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': self.refresh_token,
            })
            auth_response_data = auth_response.json()
            access_token = auth_response_data['access_token']
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=access_token)
            }
            return access_token
        else:
            return None

    # -------------------- USER RELATED FUNCTIONS ---------------------------

    def get_current_user(self):
        if connect():
            if self.auth_sync.load_token():
                self.refresh_user_token()
            response = get(f'{self.base_uri}/me', headers=self.headers)
            user = response.json()
            return user['id']
        else:
            return None

    def get_user_name(self, user_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/users/{user_id}', headers=self.headers)
            user_name = response.json()
            return user_name['display_name']
        else:
            return None

    def get_user_playlists(self, user_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/users/{user_id}/playlists?limit=50', headers=self.headers)
            playlists = response.json()
            playlists_ids = []

            for i, playlist in enumerate(playlists['items']):
                if playlist['owner']['id'] == user_id:
                    playlists_ids.append(playlist['id'])
            return playlists_ids
        else:
            return []

    def get_user_playlists_info(self, user_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/users/{user_id}/playlists?limit=50', headers=self.headers)
            playlists = response.json()
            count = 0
            for i, playlist in enumerate(playlists['items']):
                if playlist['owner']['id'] == user_id:
                    count = count + 1
                    print(f'{count} - {playlist["name"]}')
                    print(f'Number of tracks: {playlist["tracks"]["total"]}')

    def get_user_library(self):
        if connect():
            self.refresh_user_token()
            response = get(f'{self.base_uri}/me/playlists?limit=50', headers=self.headers)
            playlists = response.json()
            playlists_ids = []

            for i, playlist in enumerate(playlists['items']):
                playlists_ids.append(playlist['id'])
            playlists_ids.append('favs')

            response = get(f'{self.base_uri}/me/albums?limit=50', headers=self.headers)
            albums = response.json()
            for i, album in enumerate(albums['items']):
                playlists_ids.append(album['album']['id'])

            return playlists_ids
        else:
            return []

    def get_user_library_info(self):
        if connect():
            self.refresh_user_token()
            response = get(f'{self.base_uri}/me/playlists?limit=50', headers=self.headers)
            playlists = response.json()
            for i, playlist in enumerate(playlists['items']):
                print(f'{i + 1} - {playlist["name"]}')
                print(f'Number of tracks: {playlist["tracks"]["total"]}')
            favs = self.get_favourite_songs()
            print(f'{len(playlists["items"]) + 1} - Favourite tracks')
            print(f'Number of tracks: {len(favs)}')
            response = get(f'{self.base_uri}/me/albums?limit=50', headers=self.headers)
            albums = response.json()
            for i, album in enumerate(albums['items']):
                print(f'{len(playlists["items"]) + 1 + i + 1} - {album["album"]["name"]}')
                print(f'Number of tracks: {album["album"]["total_tracks"]}')

    def get_favourite_songs(self):
        if connect():
            self.refresh_user_token()
            stor_serv = StorageService()
            request_url = f'{self.base_uri}/me/tracks'
            songs_ids = []
            while True:
                response = get(request_url, headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    if song:
                        if song['is_local']:
                            songs_ids.append((song['name'], stor_serv.get_song_path(song['name'])))
                        else:
                            songs_ids.append((song['id'], song['preview_url']))
                request_url = songs['next']
                if not request_url:
                    break
            return songs_ids
        else:
            return []

    def get_favourite_songs_info(self):
        if connect():
            self.refresh_user_token()
            request_url = f'{self.base_uri}/me/tracks'
            while True:
                response = get(request_url, headers=self.headers)
                songs = response.json()
                j = 0
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    print(
                        f'{j + 1} - {song["name"]} - {song["artists"][0]["name"]}')
                    seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                    print(
                        f'Duration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')
                    j = j + 1
                request_url = songs['next']
                if not request_url:
                    break

    def create_playlist(self, user_id: str, name: str, public: bool = True, description: str = ''):
        if connect():
            self.refresh_user_token()
            response = post(f'{self.base_uri}/users/{user_id}/playlists',
                            dumps({"name": name, "public": public, "description": description}),
                            headers=self.headers)
            playlist = response.json()
            return playlist['id']
        else:
            return None

    def delete_playlist(self, pl_id: str):
        if connect():
            self.refresh_user_token()
            delete(f'{self.base_uri}/playlists/{pl_id}/followers', headers=self.headers)

    def follow_playlist(self, pl_id: str):
        if connect():
            self.refresh_user_token()
            put(f'{self.base_uri}/playlists/{pl_id}/followers', headers=self.headers)

    def unfollow_playlist(self, pl_id: str):
        if connect():
            self.refresh_user_token()
            delete(f'{self.base_uri}/playlists/{pl_id}/followers', headers=self.headers)

    def follow_album(self, album_id):
        if connect():
            self.refresh_user_token()
            put(f'{self.base_uri}/me/albums', dumps({"ids": [album_id]}), headers=self.headers)

    def unfollow_album(self, album_id):
        if connect():
            self.refresh_user_token()
            delete(f'{self.base_uri}/me/albums', data=dumps({"ids": [album_id]}), headers=self.headers)

    def check_if_followed(self, id, album=False):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            if not album:
                response = get(f'{self.base_uri}/playlists/{id}/followers/contains?ids={self.get_current_user()}',
                               headers=self.headers)
                check = response.json()
                if check == [False] or check == [True]:
                    return check[0]
                else:
                    return False
            else:
                response = get(f'{self.base_uri}/me/albums/contains?ids={id}', headers=self.headers)
                check = response.json()
                if check == [False] or check == [True]:
                    return check[0]
                else:
                    return False
        else:
            return False

    # --------------------- PLAYLIST/ALBUM RELATED FUNCTIONS -------------------------

    def get_playlist_name(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            return playlist["name"]
        else:
            return None

    def get_album_name(self, album_id):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/albums/{album_id}', headers=self.headers)
            album = response.json()
            return album["name"]
        else:
            return None

    def get_playlist_publicity(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            return playlist["public"]
        else:
            return None

    def get_playlist_size(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            return playlist["tracks"]["total"]
        else:
            return None

    def get_album_size(self, album_id):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/albums/{album_id}', headers=self.headers)
            album = response.json()
            return album["total_tracks"]
        else:
            return None

    def get_playlist_snapshot(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            return playlist["snapshot_id"]
        else:
            return None

    def get_playlist_duration(self, pl_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            if not length:
                length = self.get_playlist_size(pl_id)
            duration = 0
            for j in range(ceil(length / 100)):
                response = get(f'{self.base_uri}/playlists/{pl_id}/tracks?offset={j * 100}', headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    if song:
                        duration += song["duration_ms"]
            return duration
        else:
            return 0

    def get_album_duration(self, album_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            if not length:
                length = self.get_album_size(album_id)
            duration = 0
            for j in range(ceil(length / 50)):
                response = get(f'{self.base_uri}/albums/{album_id}/tracks?limit=50&offset={j * 100}',
                               headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    if song:
                        duration += song["duration_ms"]
            return duration
        else:
            return 0

    def get_fav_duration(self):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            request_url = f'{self.base_uri}/me/tracks'
            duration = 0
            while True:
                response = get(request_url, headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    if song:
                        duration += song["duration_ms"]
                request_url = songs['next']
                if not request_url:
                    break
            return duration
        else:
            return 0

    def get_playlist_info(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            print(f'Name: {playlist["name"]}')
            print(f'Description: {playlist["description"]}')
            print(f'Number of tracks: {playlist["tracks"]["total"]}')
            if self.check_if_self_owned(pl_id):
                print(f'Publicity: ' + ('public' if self.get_playlist_publicity(pl_id) else 'private'))
            print(f'Cover: {playlist["images"][0]["url"] if playlist["images"] else ""}')
            duration = self.get_playlist_duration(playlist['id'])
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'Duration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_album_info(self, album_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/albums/{album_id}', headers=self.headers)
            album = response.json()
            print(f'Name: {album["name"]}')
            artists = []
            for i, artist in enumerate(album['artists']):
                artists.append(artist['name'])
            artists = ', '.join(artists)
            print(f'Artist: {artists}')
            print(f'Number of tracks: {album["total_tracks"]}')
            print('Release date: ' + album['release_date'])
            print(f'Cover: {album["images"][0]["url"]}')
            duration = self.get_album_duration(album['id'])
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'Duration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_favorites_playlist_info(self):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            favs = self.get_favourite_songs()
            print(f'Name: Favourite tracks')
            print(f'Number of tracks: {len(favs)}')
            duration = self.get_fav_duration()
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'Duration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_playlist_songs(self, pl_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            stor_serv = StorageService()
            songs_ids = []
            if not length:
                length = self.get_playlist_size(pl_id)
            for j in range(ceil(length / 100)):
                response = get(f'{self.base_uri}/playlists/{pl_id}/tracks?offset={j * 100}', headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    if song:
                        if song['is_local']:
                            songs_ids.append((song['name'], stor_serv.get_song_path(song['name'])))
                        else:
                            songs_ids.append((song['id'], song['preview_url']))
            return songs_ids
        else:
            return []

    def get_playlist_songs_info(self, pl_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            if not length:
                length = self.get_playlist_size(pl_id)
            if length == 0:
                print('Playlist is empty!')
            else:
                for j in range(ceil(length / 100)):
                    response = get(f'{self.base_uri}/playlists/{pl_id}/tracks?offset={j * 100}', headers=self.headers)
                    songs = response.json()
                    for i, song in enumerate(songs['items']):
                        song = song["track"]
                        print(
                            f'{i + 1 + j * 100} - {song["name"]} - {song["artists"][0]["name"]}')
                        seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                        print(
                            f'Duration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')

    def get_album_songs(self, album_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            songs_ids = []
            if not length:
                length = self.get_album_size(album_id)
            else:
                for j in range(ceil(length / 50)):
                    response = get(f'{self.base_uri}/albums/{album_id}/tracks?limit=50&offset={j * 50}',
                                   headers=self.headers)
                    songs = response.json()
                    for i, song in enumerate(songs['items']):
                        songs_ids.append((song['id'], song['preview_url']))
            return songs_ids
        else:
            return []

    def get_album_songs_info(self, album_id: str, length: int = None):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            songs_ids = []
            if not length:
                length = self.get_album_size(album_id)
            else:
                for j in range(ceil(length / 50)):
                    response = get(f'{self.base_uri}/albums/{album_id}/tracks?limit=50&offset={j * 50}',
                                   headers=self.headers)
                    songs = response.json()
                    for i, song in enumerate(songs['items']):
                        print(
                            f'{i + 1 + j * 50} - {song["name"]} - {song["artists"][0]["name"]}')
                        seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                        print(
                            f'Duration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')
                        songs_ids.append((song['id'], song['preview_url']))
            return songs_ids
        else:
            return []

    def check_if_self_owned(self, pl_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            try:
                return playlist['owner']['id'] == self.get_current_user()
            except:
                return False
        else:
            return False

    def add_song_to_playlist(self, pl_id: str, song_id: str, position: int = 0):
        if connect():
            self.refresh_user_token()
            position = self.get_playlist_size(pl_id)
            post(f'{self.base_uri}/playlists/{pl_id}/tracks',
                 dumps({"uris": [f"spotify:track:{song_id}"], "position": position}),
                 headers=self.headers)

    def delete_song_from_playlist(self, pl_id: str, song_id: str):
        if connect():
            self.refresh_user_token()
            snapshot = self.get_playlist_snapshot(pl_id)
            delete(f'{self.base_uri}/playlists/{pl_id}/tracks',
                   data=dumps({"tracks": [{"uri": f"spotify:track:{song_id}"}], "snapshot_id": snapshot}),
                   headers=self.headers)

    def update_playlist_info(self, pl_id: str, name: str = None, public: bool = None, description: str = None):
        if connect():
            self.refresh_user_token()
            response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
            playlist = response.json()
            if not name:
                name = playlist["name"]
            if not description:
                description = playlist["description"]
            if public is None:
                public = playlist["public"]
            put(f'{self.base_uri}/playlists/{pl_id}',
                dumps({"name": name, "public": public, "description": description}),
                headers=self.headers)

    # --------------------- SONG RELATED FUNCTIONS -------------------------

    def get_song(self, song_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
            song = response.json()
            try:
                if song['error']:
                    return dict(is_local=True)
            except KeyError:
                artists = []
                for i, artist in enumerate(song['artists']):
                    artists.append(artist['name'])
                artists = ', '.join(artists)
                return dict(title=song['name'], album_id=song['album']['id'], artist=artists,
                            duration=song['duration_ms'], cover=song['album']['images'][0]['url'],
                            date=song['album']['release_date'], source=song['preview_url'], is_local=song['is_local'])
        else:
            return None

    def get_song_url(self, song_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
            song = response.json()
            return song['preview_url']
        else:
            return None

    def get_song_info(self, song_id: str):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            song = self.get_song(song_id)
            print(song['title'] + ' - ' + song['artist'])
            seconds = str(song["duration"] // 1000 % 60 + 100)
            print(
                f'Duration: {song["duration"] // 1000 // 60}:{seconds[1:]}')
            print('Album: ' + self.get_album_name(song['album_id']))
            print('Release date: ' + song['date'])
            print('Cover: ' + song['cover'])

    def add_song_to_favourites(self, song_id: str):
        if connect():
            self.refresh_user_token()
            put(f'{self.base_uri}/me/tracks', dumps({"ids": [song_id]}), headers=self.headers)

    def delete_song_from_favourites(self, song_id: str):
        if connect():
            self.refresh_user_token()
            delete(f'{self.base_uri}/me/tracks', data=dumps({"ids": [song_id]}), headers=self.headers)

    # --------------------- SEARCH RELATED FUNCTIONS -------------------------

    def search(self, query: str, search_type: str = 'track'):
        if connect():
            if not self.refresh_token:
                self.refresh_user_token()
            response = get(f'{self.base_uri}/search', params={'q': query, 'type': search_type}, headers=self.headers)
            search_results = response.json()
            search_items = []
            for i, item in enumerate(search_results[search_type + 's']['items']):
                search_items.append(item['id'])
                if search_type == 'track':
                    print(
                        f'{i + 1} - {item["name"]} - {item["artists"][0]["name"]}')
                    seconds = str(item["duration_ms"] // 1000 % 60 + 100)
                    print(
                        f'Duration: {item["duration_ms"] // 1000 // 60}:{seconds[1:]}')
                elif search_type == 'playlist':
                    print(f'{i + 1} - {item["name"]}')
                    print(f'Number of tracks: {item["tracks"]["total"]}')
                elif search_type == 'album':
                    print(f'{i + 1} - {item["name"]}')
                    print(f'Number of tracks: {item["total_tracks"]}')
            return search_items
        else:
            return []
