import requests
from requests.auth import HTTPBasicAuth
import os
import dotenv
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

sp_oauth = SpotifyOAuth(
    "your_client_id",
    "your_client_secret",
    "your_redirect_uri",
    scope=["playlist-modify-public"]
)

token_info = sp_oauth.get_access_token(requests.args['code'])
access_token = token_info['access_token']

def create_playlist(user_id, access_token, playlist_name, public=True):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

    # Playlist data
    data = {
        "name": playlist_name,
        "public": public
    }

    # headers for auth
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # post request
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful 
    if response.status_code == 201:
        print("Playlist has been created.")
    else:
        print(f"Error, unable to create playlist: {response.status_code}, {response.text}")

# Test
user_id = "jtekson"
access_token = "BQCYQC2fnugsOr7uxOflQKIvo52B9cvcabPIKHs-Bp-79KIxooToLEk5H4itxwD9re090-XhyCevwqjvW_RKqT46hCM7vd_FiBOgO3snji478JJ8Oeg"
playlist_name = "test playlist"

create_playlist(user_id, access_token, playlist_name)
