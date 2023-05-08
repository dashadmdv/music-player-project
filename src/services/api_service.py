from requests import get, post
from math import ceil
from webbrowser import open_new_tab
from src.services.storage_service import StorageService
from multipledispatch import dispatch


class APIService:
    def __init__(self):
        self.client_id = '278b5ce854d54d088d5c740a768dc46e'
        self.client_secret = 'b17bff721823449586b80a86ef6d5c26'
        self.redirect_uri = 'https://google.com/callback/'
        self.base_uri = 'https://api.spotify.com/v1'
        self.refresh_token = None
        if not self.refresh_token:
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=self.update_token())
            }
        else:
            self.headers = {
                'Authorization': 'Bearer {token}'.format(token=self.refresh_user_token())
            }
        self.scope = 'user-library-read user-read-private user-read-email ' + \
                     'playlist-modify-public playlist-read-private playlist-modify-private'

    def auth_agent(self):
        auth_url = f'https://accounts.spotify.com/authorize?client_id={self.client_id}&response_type=code' + \
                   f'&redirect_uri={self.redirect_uri}&scope={self.scope.replace(" ", "+")}&state=34fFs29kd09'
        open_new_tab(auth_url)

    def authorization(self, code_url: str):
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
            'Authorization': 'Bearer {token}'.format(token=self.refresh_user_token())
        }

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
        return access_token

    # -------------------- USER RELATED FUNCTIONS ---------------------------

    def get_user_name(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}', headers=self.headers)
        user_name = response.json()
        return user_name['display_name']

    def get_user_playlists(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}/playlists', headers=self.headers)
        playlists = response.json()
        playlists_ids = []

        for i, playlist in enumerate(playlists['items']):
            playlists_ids.append(playlist['id'])
        return playlists_ids

    def get_user_playlists_info(self, user_id: str):
        response = get(f'{self.base_uri}/users/{user_id}/playlists', headers=self.headers)
        playlists = response.json()

        for i, playlist in enumerate(playlists['items']):
            print(f'{i + 1} - {playlist["name"]}')
            print(f'Number of tracks: {playlist["tracks"]["total"]}')
            duration = self.get_playlist_duration(playlist['id'])
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    def get_user_library(self):
        response = get(f'{self.base_uri}/me/playlists', headers=self.headers)
        playlists = response.json()
        playlists_ids = []

        for i, playlist in enumerate(playlists['items']):
            playlists_ids.append(playlist['id'])
        return playlists_ids

    def get_user_library_info(self):
        response = get(f'{self.base_uri}/me/playlists', headers=self.headers)
        playlists = response.json()
        for i, playlist in enumerate(playlists['items']):
            print(f'{i + 1} - {playlist["name"]}')
            print(f'Number of tracks: {playlist["tracks"]["total"]}')
            duration = self.get_playlist_duration(playlist['id'])
            minutes = str(duration // 1000 // 60 % 60 + 100)
            print(
                f'\tDuration: {duration // 1000 // 60 // 60}h:{minutes[1:]}m')

    # --------------------- PLAYLIST RELATED FUNCTIONS -------------------------

    def get_playlist_name(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()
        return playlist["name"]

    def get_playlist_size(self, pl_id: str):
        response = get(f'{self.base_uri}/playlists/{pl_id}', headers=self.headers)
        playlist = response.json()

        return playlist["tracks"]["total"]

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

    def get_playlist_songs(self, pl_id: str, length: int):
        stor_serv = StorageService()
        songs_ids = []
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

    def get_playlist_songs_info(self, pl_id: str, length: int):
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
        print('Link: ' + str(self.get_song_url(song_id)))
