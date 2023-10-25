import spotipy

def get_from_spotify():
    data = spotipy.Spotify()
    results = data.search(q="artist + Queen", type = "artist")
    print(results)

    data1 = spotipy.Spotify()
    results1 = data1.search(q="artist + Connor Price", type = "artist")
    print(results1)