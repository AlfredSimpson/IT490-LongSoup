import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
# from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="0333477c29da440c828ede4dc2eb6747",
                                                            client_secret="512ee493749c4959af01f8c32f3cd7d5"))


results = sp.search(q='tobymac', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'], track['artists'], "\n")


# results = sp.search(q='rock', limit=20)
# for idx, genre in enumerate(results['genre']['items']):
#     print(idx, genre['name'])

# results = sp.search(q='connor price', limit=20)
# for idx, track in enumerate(results['tracks']['items']):

#     print(idx, track['name'])
