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

maindb = 'RPD'#os.getenv("MONGO_DB")
maindbuser = 'rpdTest'#os.getenv("MONGO_USER")
maindbpass = 'password'#os.getenv("MONGO_PASS")
maindbhost = 'localhost'#os.getenv("MONGO_HOST")

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/RPD" % (maindbuser, maindbpass)
)
db = myclient[maindb]
mycol = db["STARS"]

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
    json_result = json.loads(result.content)# what will exist for json result
    mycol.insert_one(json_result)
print("Stored in database!")

token = get_token()

result = search_for_artist(token, 'Nirvana')
