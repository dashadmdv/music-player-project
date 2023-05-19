from requests import get, post, put, delete
from math import ceil
from webbrowser import open_new_tab
from src.services.storage_service import StorageService
from json import dumps
from src.sync.auth_sync import AuthSynchronization


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
        auth_url = f'https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code' + \
                   f'&redirect_uri={self.redirect_uri}&scope={self.scope.replace(" ", "+")}&state=34fFs29kd09'
        open_new_tab(auth_url)

    def authentication(self, code_url: str):
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
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        })
        auth_response_data = auth_response.json()
        access_token = auth_response_data['access_token']
        return access_token

    def refresh_user_token(self):
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

    # -------------------- USER RELATED FUNCTIONS ---------------------------

    def get_current_user(self):
        response = get(f'{self.base_uri}/me', headers=self.headers)
        user = response.json()
        return user['id']

    def get_user_name(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}', headers=self.headers)
        user_name = response.json()
        return user_name['display_name']

    def get_user_playlists(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}/playlists?limit=50', headers=self.headers)
        playlists = response.json()
        playlists_ids = []

        for i, playlist in enumerate(playlists['items']):
            if playlist['owner']['id'] == user_id:
                playlists_ids.append(playlist['id'])
        return playlists_ids

    def get_user_playlists_info(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}/playlists?limit=50', headers=self.headers)
        playlists = response.json()
        count = 0
        for i, playlist in enumerate(playlists['items']):
            if playlist['owner']['id'] == user_id:
                count = count + 1
                print(f'{count} - {playlist["name"]}')
                print(f'Number of tracks: {playlist["tracks"]["total"]}')
                duration = self.get_playlist_duration(playlist['id'])
                minutes = str(duration // 1000 // 60 % 60 + 100)
                print(
                    f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_user_library(self):
        response = get(f'{self.base_uri}/me/playlists?limit=50', headers=self.headers)
        playlists = response.json()
        playlists_ids = []

        for i, playlist in enumerate(playlists['items']):
            playlists_ids.append(playlist['id'])
        return playlists_ids

    def get_user_library_info(self):
        response = get(f'{self.base_uri}/me/playlists?limit=50', headers=self.headers)
        playlists = response.json()
        for i, playlist in enumerate(playlists['items']):
            print(f'{i + 1} - {playlist["name"]}')
            print(f'Number of tracks: {playlist["tracks"]["total"]}')
            duration = self.get_playlist_duration(playlist['id'])
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_favourite_songs(self):
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

    def get_favourite_songs_info(self):
        request_url = f'{self.base_uri}/me/tracks'
        while True:
            response = get(request_url, headers=self.headers)
            songs = response.json()
            j = 0
            for i, song in enumerate(songs['items']):
                song = song["track"]
                print(
                    f'{j + 1} - {song["name"]} - {song["artists"][0]["name"]}')
                print(f'\tUrl: {song["external_urls"]}')
                seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                print(
                    f'\tDuration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')
                j = j + 1
            request_url = songs['next']
            if not request_url:
                break

    def create_playlist(self, user_id: str, name: str, public: bool = True, description: str = ''):
        self.refresh_user_token()
        response = post(f'{self.base_uri}/users/{user_id}/playlists',
                        dumps({"name": name, "public": public, "description": description}),
                        headers=self.headers)
        playlist = response.json()
        return playlist['id']

    def delete_playlist(self, pl_id: str):
        self.refresh_user_token()
        delete(f'{self.base_uri}/playlists/{pl_id}/followers', headers=self.headers)

    # --------------------- PLAYLIST/ALBUM RELATED FUNCTIONS -------------------------

    def get_playlist_name(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["name"]

    def get_album_name(self, album_id):
        response = get(f'{self.base_uri}/albums/{album_id}', headers=self.headers)
        album = response.json()
        return album["name"]

    def get_playlist_description(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["description"]

    def get_playlist_publicity(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["public"]

    def get_playlist_size(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["tracks"]["total"]

    def get_album_size(self, album_id):
        response = get(f'{self.base_uri}/albums/{album_id}', headers=self.headers)
        album = response.json()
        return album["total_tracks"]

    def get_playlist_snapshot(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["snapshot_id"]

    def get_playlist_duration(self, pl_id: str, length: int = None):
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

    def get_album_duration(self, album_id: str, length: int = None):
        if not length:
            length = self.get_album_size(album_id)
        duration = 0
        for j in range(ceil(length / 100)):
            response = get(f'{self.base_uri}/albums/{album_id}/tracks?offset={j * 100}', headers=self.headers)
            songs = response.json()
            for i, song in enumerate(songs['items']):
                if song:
                    duration += song["duration_ms"]
        return duration

    def get_playlist_songs(self, pl_id: str, length: int = None):
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

    def get_playlist_songs_info(self, pl_id: str, length: int = None):
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
                    print(f'\tUrl: {song["external_urls"]}')
                    seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                    print(
                        f'\tDuration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')

    def get_album_songs_info(self, album_id: str, length: int = None):
        songs_ids = []
        if not length:
            length = self.get_album_size(album_id)
        else:
            for j in range(ceil(length / 100)):
                response = get(f'{self.base_uri}/albums/{album_id}/tracks?offset={j * 100}', headers=self.headers)
                songs = response.json()
                for i, song in enumerate(songs['items']):
                    song = song["track"]
                    print(
                        f'{i + 1 + j * 100} - {song["name"]} - {song["artists"][0]["name"]}')
                    seconds = str(song["duration_ms"] // 1000 % 60 + 100)
                    print(
                        f'\tDuration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')
                    songs_ids.append((song['id'], song['preview_url']))
        return songs_ids

    def check_if_self_owned(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        try:
            if playlist['owner']['id'] == self.get_current_user():
                return True
            else:
                return False
        except:
            return False

    def add_song_to_playlist(self, pl_id: str, song_id: str, position: int = 0):
        self.refresh_user_token()
        print(post(f'{self.base_uri}/playlists/{pl_id}/tracks',
             dumps({"uris": [f"spotify:track:{song_id}"], "position": position}),
             headers=self.headers))

    def delete_song_from_playlist(self, pl_id: str, song_id: str):
        self.refresh_user_token()
        snapshot = self.get_playlist_snapshot(pl_id)
        delete(f'{self.base_uri}/playlists/{pl_id}/tracks',
               data=dumps({"tracks": [{"uri": f"spotify:track:{song_id}"}], "snapshot_id": snapshot}),
               headers=self.headers)

    def update_playlist_info(self, pl_id: str, name: str = None, public: bool = None, description: str = None):
        self.refresh_user_token()
        if not name:
            name = self.get_playlist_name(pl_id)
        if not description:
            description = self.get_playlist_description(pl_id)
        if public is None:
            public = self.get_playlist_publicity(pl_id)
        put(f'{self.base_uri}/playlists/{pl_id}',
            dumps({"name": name, "public": public, "description": description}),
            headers=self.headers)

    # --------------------- SONG RELATED FUNCTIONS -------------------------

    def get_song_title(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['name']

    def get_song_artist(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        artists = []
        for i, artist in enumerate(song['artists']):
            artists.append(artist['name'])
        return ', '.join(artists)

    def get_song_album(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['album']['id']

    def get_song_duration(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['duration_ms']

    def get_song_cover(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['album']['images'][0]['url']

    def get_song_date(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['album']['release_date']

    def get_song_url(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['preview_url']

    def get_song_uri(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        return song['uri']

    def get_song_info(self, song_id: str):
        response = get(f'{self.base_uri}/tracks/{song_id}', headers=self.headers)
        song = response.json()
        print(song['name'] + ' - ' + self.get_song_artist(song_id))
        seconds = str(song["duration_ms"] // 1000 % 60 + 100)
        print(
            f'Duration: {song["duration_ms"] // 1000 // 60}:{seconds[1:]}')
        print('Album: ' + song['album']['name'])
        print('Release date: ' + song['album']['release_date'])
        print('Cover: ' + song['album']['images'][0]['url'])
        print('Link: ' + str(song['preview_url']))

    def add_song_to_favourites(self, song_id: str):
        put(f'{self.base_uri}/me/tracks', dumps({"ids": [song_id]}), headers=self.headers)

    def delete_song_from_favourites(self, song_id: str):
        delete(f'{self.base_uri}/me/tracks', data=dumps({"ids": [song_id]}), headers=self.headers)

    # --------------------- SEARCH RELATED FUNCTIONS -------------------------

    def search(self, query: str, search_type: str = 'track'):
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
                    f'\tDuration: {item["duration_ms"] // 1000 // 60}:{seconds[1:]}')
            elif search_type == 'playlist':
                print(f'{i + 1} - {item["name"]}')
                print(f'Number of tracks: {item["tracks"]["total"]}')
                duration = self.get_playlist_duration(item['id'])
                minutes = str(duration // 1000 // 60 % 60 + 100)
                print(
                    f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')
            elif search_type == 'album':
                print(f'{i + 1} - {item["name"]}')
                print(f'Number of tracks: {item["total_tracks"]}')
                duration = self.get_album_duration(item['id'])
                minutes = str(duration // 1000 // 60 % 60 + 100)
                print(
                    f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')
        return search_items
