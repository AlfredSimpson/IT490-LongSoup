import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('JTCLIENT_ID')
client_secret = os.getenv('JTCLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_TEST_URI')

print("Client ID:", client_id)
print("Client Secret:", client_secret)
print("Redirect URI:", redirect_uri)

sp_oauth = SpotifyOAuth(
    client_id, client_secret, redirect_uri
)

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])
