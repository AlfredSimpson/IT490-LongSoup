import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Your Spotify API credentials
SPOTIFY_CLIENT_ID="0333477c29da440c828ede4dc2eb6747"
SPOTIFY_CLIENT_SECRET="512ee493749c4959af01f8c32f3cd7d5" 

# Create a Spotify client with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Get song recommendations based on seed tracks
def get_recommendations(seed_tracks, limit=10):
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=limit)
    return recommendations['tracks']

# Provide a list of seed tracks (track IDs)
seed_tracks = [
    'spotify:track:1bHnRc60O1N0l3PbHjaKyK',
    'spotify:track:2VOomzT6VavJOGBeySqaMc',
]

# Get song recommendations and print their names and artists
recommendedTracks = get_recommendations(seed_tracks, limit=10)
for track in recommendedTracks:
    trackName = track['name']
    artists = ", ".join([artist['name'] for artist in track['artists']])
    print(f"{trackName} by {artists}")