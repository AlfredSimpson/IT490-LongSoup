import spotipy
from spotipy.oauth2 import SpotifyOAuth
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
    url = 'https://api.spotify.com/v1/search' #spotify api search link
    headers = get_auth_header(token)          #authentication header with our token to access api url
    query = f"?q={artist_name}&type=artist&limit=1" #querying specifically only 1 artist --> change limit

    query_url = url + query
    result = get(query_url, headers=headers)
    api_json = json.loads(result.content)# what will exist for json result
    #return api_json
    #mycol.insert_one(json_result)
    spotify_name = api_json["name"]
    spotify_popularity=["popularity"]
    genre_types = api_json["genres"]
    spotify_link = api_json["external_urls"]["spotify"]
    spotify_id = api_json["id"]
    spotify_images = []
    if "images" in api_json:
        for image_data in api_json["images"]:
            url = image_data.get("url")
            height = image_data.get("height")
            width = image_data.get("width")
            image_info = {
                "url": url,
                "height": height,
                "width": width,
            }
            spotify_images.append(image_info)
    artist_data = {
        "spotify_data": {
            "spotifyName": spotify_name,
            "popularity": spotify_popularity,
            "spotifyId": spotify_id,
            "Genres": genre_types,
            "spotifyUrl": spotify_link,
            "spotifyPictures": spotify_images,
        },
    }
    # Now we take user_data and shove it into the database
    try:
        db.spotifyArtists.insert_one(artist_data)
        print("Successfully added user data to spotifyArtists")
    except:
        print("Could not add artist into the database")

token = get_token()
result = search_for_artist(token, 'Nirvana')

def processProfile(api_json):
    """# processProfile
    This takes in the json from the spotify api pull of a user profile and processes it into the schema.
    Args:
        api_json (json): The json from the spotify api for the user profile
        uid (int): the integer of the user id. Or string. Whatever.
    """
    # First, read the data it receives, and then process it into the schema
    spotify_name = api_json["name"]
    spotify_popularity=["popularity"]
    genre_types = api_json["genres"]
    spotify_link = api_json["external_urls"]["spotify"]
    spotify_id = api_json["id"]
    spotify_images = []
    if "images" in api_json:
        for image_data in api_json["images"]:
            url = image_data.get("url")
            height = image_data.get("height")
            width = image_data.get("width")
            image_info = {
                "url": url,
                "height": height,
                "width": width,
            }
            spotify_images.append(image_info)
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
    # Now we take user_data and shove it into the database
    try:
        db.spotifyArtists.insert_one(artist_data)
        print("Successfully added user data to spotifyUsers")
    except:
        print("Could not add user data into the database")


#def getMe(uid=None):
    #users = db.users.find_one({"uid":uid})
    #access_token = users['spotify_token']
    #headers = {'Authorization': f'Bearer {access_token}'}
    #url = 'https://api.spotify.com/v1/me'
    #r = requests.get(url, headers=headers)
    #r = r.json()
    #print(r)
    #processProfile(r, uid)