import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# Your Spotify API credentials
SPOTIFY_CLIENT_ID="0333477c29da440c828ede4dc2eb6747"
SPOTIFY_CLIENT_SECRET="512ee493749c4959af01f8c32f3cd7d5"

# Create a Spotify client with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_ID, scope='user-library-read user-read-playback-state'))

def get_current_track():
    playback = sp.current_playback()
    if playback is not None:
        trackName = playback.get('item', {}).get('name')
        artists = ", ".join([artist['name'] for artist in playback.get('item', {}).get('artists', [])])
        return f"Now playing: {trackName} by {artists}"
    return "No track currently playing."

previous_track = None

while True:
    track = get_current_track()
    if track != previous_track:
        print(track)
        previous_track = track
    time.sleep(5) 