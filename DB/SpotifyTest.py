import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import json
# from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="0333477c29da440c828ede4dc2eb6747",
                                                            client_secret="512ee493749c4959af01f8c32f3cd7d5"))

tracks ="2tBomeCTCXl3fq0g0jterX"


track_data = sp.track(tracks)

artist_ids = []

for artist in track_data["artists"]:
    artist_ids.append(artist["id"])

artists_data = sp.artists(artist_ids)

genres = []

for artist in artists_data["artists"]:
    genres += artist["genres"]

genres = set(genres) # removes duplicates

print(artist)
print(genres)

# result_artist = json.dumps(artist)
# result_genre = json.dumps(genres)

# song_artist = json.loads(result_artist)
# song_genre = json.loads(result_genre)