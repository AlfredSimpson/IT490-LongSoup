import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id='10c241e9a6b944928d20497ef814ef7d',
        client_secret='b1cb224681ee4f8ea9d3f54ea1a3966a',
        redirect_uri='https://njiticc.com/', 
        scope='user-top-read',  # Request the user's top artists and tracks
    )
)
def get_user_top_tracks(sp, limit=10):
    results = sp.current_user_top_tracks(limit=limit, time_range='medium_term')
    return results

user_top_tracks = get_user_top_tracks(sp)
print(json.dumps(user_top_tracks, indent=4))

