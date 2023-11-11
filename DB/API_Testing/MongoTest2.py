#import spotipy
#from spotipy.oauth2 import SpotifyOAuth
import pymongo
import base64
from requests import post, get
import json
#import os

# Set your Spotify API credentials
client_id = '10c241e9a6b944928d20497ef814ef7d'
client_secret = 'b1cb224681ee4f8ea9d3f54ea1a3966a'

# Initialize Spotipy with OAuth2 authentication
#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret))

maindb = 'cgs'#os.getenv("MONGO_DB")
maindbuser = 'longestsoup'#os.getenv("MONGO_USER")
maindbpass = 'shorteststraw'#os.getenv("MONGO_PASS")
maindbhost = 'localhost'#os.getenv("MONGO_HOST")

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]
#mycol = db["RPD"]

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    #Above encodes the token into base64

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"

    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {'Authorization': 'Bearer ' + token}

def search_for_artist(token, artist_name):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    api_json = json.loads(result.content)

    if 'artists' in api_json and 'items' in api_json['artists']:
        artists = api_json['artists']['items']
        if artists:
            artist = artists[0]
            # Extract artist data from the API response
            spotify_name = artist['name']
            spotify_popularity = artist['popularity']
            genre_types = artist['genres']
            spotify_link = artist['external_urls']['spotify']
            spotify_id = artist['id']
            spotify_images = artist.get('images', [])

            artist_data = {
                "spotifyName": spotify_name,
                "spotify_data": {
                    "popularity": spotify_popularity,
                    "spotifyId": spotify_id,
                    "Genres": genre_types,
                    "spotifyUrl": spotify_link,
                    "spotifyPictures": spotify_images,
                },
            }

            try:
                db.Artists.insert_one(artist_data)
                print("Successfully added ") + spotify_name + (" to Artists")
            except Exception as e:
                print(f"Could not add artist into the database: {str(e)}")
        else:
            print("No artist found for the given name.")

    else:
        print("Error in the Spotify API response.")

# Get the access token
token = get_token()

# Search for an artist (e.g., Nirvana)
search_for_artist(token, 'Nirvana')