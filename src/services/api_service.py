from requests import get, post


class APIService:
    def __init__(self):
        self.client_id = '278b5ce854d54d088d5c740a768dc46e'
        self.client_secret = 'b17bff721823449586b80a86ef6d5c26'
        self.redirect_uri = 'http://google.com/callback/'
        self.headers = {
            'Authorization': 'Bearer {token}'.format(token=self.update_token())
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


    # -------------------- USER RELATED FUNCTIONS ---------------------------

    def get_user_name(self, user_id: str):
        return user_id

    def get_user_playlists(self, user_id: str):
        response = get(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=self.headers)
        playlists = response.json()
        playlists_ids = []

        for i, playlist in enumerate(playlists['items']):
            playlists_ids.append(playlist['id'])
        return playlists_ids

    def get_user_playlists_info(self, user_id: str):
        response = get(f'https://api.spotify.com/v1/users/{user_id}/playlists', headers=self.headers)
        playlists = response.json()

        for i, playlist in enumerate(playlists['items']):
            print(f'{i + 1} - {playlist["name"]}')
            print(f'\tNumber of tracks: {playlist["tracks"]["total"]}')

    # --------------------- PLAYLIST RELATED FUNCTIONS -------------------------

    def get_playlist_name(self, pl_id: str):
        return pl_id

    def get_playlist_duration(self, pl_id: str):
        response = get(f'https://api.spotify.com/v1/playlists/{pl_id}/tracks', headers=self.headers)
        songs = response.json()
        duration = 0
        for i, song in enumerate(songs['items']):
            song = song["track"]
            duration += song["duration_ms"]
        print(
            f'\tDuration: {duration // 1000 // 60 // 60}h:{duration // 1000 // 60 % 60}m')

    def get_playlist_songs(self, pl_id: str):
        response = get(f'https://api.spotify.com/v1/playlists/{pl_id}/tracks', headers=self.headers)
        songs = response.json()
        songs_ids = []
        for i, song in enumerate(songs['items']):
            song = song["track"]
            songs_ids.append(song)
        return songs_ids

    def get_playlist_songs_info(self, pl_id: str):
        response = get(f'https://api.spotify.com/v1/playlists/{pl_id}/tracks', headers=self.headers)
        songs = response.json()
        for i, song in enumerate(songs['items']):
            song = song["track"]
            print(
                f'{i + 1} - {song["name"]} - {song["album"]["artists"][0]["name"]}')
            print(f'\tUrl: {song["external_urls"]}')
            print(
                f'\tDuration: {song["duration_ms"] // 1000 // 60}:{song["duration_ms"] // 1000 % 60}')
