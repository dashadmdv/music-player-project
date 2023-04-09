from requests import get, post


class APIService:
    def __init__(self):
        self.client_id = '278b5ce854d54d088d5c740a768dc46e'
        self.client_secret = 'b17bff721823449586b80a86ef6d5c26'
        self.redirect_uri = 'http://google.com/callback/'
        self.headers = None

    def update_token(self):
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

    def get_user_name(self):
        return 0

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
            print(f'{i} - {playlist["name"]}')
            print(f'\tNumber of tracks: {playlist["tracks"]["total"]}')
