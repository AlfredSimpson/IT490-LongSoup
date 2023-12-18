import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Set up your Spotify API credentials
SPOTIPY_CLIENT_ID = '10c241e9a6b944928d20497ef814ef7d'
SPOTIPY_CLIENT_SECRET = 'b1cb224681ee4f8ea9d3f54ea1a3966a'
SPOTIPY_REDIRECT_URI = 'https://njiticc.com'

# Set up the scope for playlist modification
SCOPE = 'playlist-modify-public playlist-modify-private'

# Create a Spotify OAuth object
sp_oauth = SpotifyOAuth(
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE
)

# Get user authorization
token_info = sp_oauth.get_access_token()
token = token_info['access_token']

# Create a Spotify object
sp = spotipy.Spotify(auth=token)

def create_playlist(user_id, playlist_name):
    # Create a new playlist
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name)
    return playlist['id']

def add_tracks_to_playlist(playlist_id, track_uris):
    # Add tracks to the playlist
    sp.playlist_add_items(playlist_id, track_uris)

if __name__ == '__main__':
    # Replace 'your_spotify_username' with your Spotify username
    spotify_username = 'jtekson'
    
    # Replace 'Your Playlist Name' with the desired playlist name
    playlist_name = 'test playlist'

    # Replace 'track_uri_1', 'track_uri_2', etc. with the URIs of the tracks you want to add
    track_uris = ['1G391cbiT3v3Cywg8T7DM1', '1Ic9pKxGSJGM0LKeqf6lGe']

    # Create the playlist
    playlist_id = create_playlist(spotify_username, playlist_name)

    # Add tracks to the playlist
    add_tracks_to_playlist(playlist_id, track_uris)

    print(f"Playlist '{playlist_name}' created and tracks added successfully!")

