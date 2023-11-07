import spotipy
import pymongo
import os, sys, json, time, requests
from datetime import datetime
import schedule
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()

# Spotify secrets
SPOTID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTSECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTURI = os.getenv("SPOT_TEST_URI")  # Shouldn't be used in DB tbh but still importing
SPOTAPIBASE = os.getenv("SPOTIFY_API_BASE_URL")
SPOTAUTHURL = os.getenv("SPOTIFY_AUTH_URL")
SPOTTOKENURL = os.getenv("SPOTIFY_TOKEN_URL")
SPOTSCOPE = "user-read-currently-playing playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-top-read user-read-playback-position user-read-recently-played user-library-read user-library-modify user-read-email user-read-private"  # probably also not necessary here

# Mongo DB Secrets
maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")


myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]


track_schema = ""

album_schema = ""

artist_schema = ""


def processProfile(api_json, uid):
    """# processProfile

    This takes in the json from the spotify api pull of a user profile and processes it into the schema.

    Args:
        api_json (json): The json from the spotify api for the user profile
        uid (int): the integere of the user id. Or string. Whatever.
    """

    # First, read the data it receives, and then process it into the schema
    display_name = api_json["display_name"]
    given_email = api_json["email"]
    spotify_link = api_json["external_urls"]["spotify"]
    spotify_id = api_json["id"]
    spotify_country = api_json["country"]
    spotify_product = api_json["product"]  # premium, free, etc

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

    user_data = {
        "uid": uid,
        "spotify_data": {
            "spotifyId": spotify_id,
            "spotifyName": display_name,
            "spotifyEmail": given_email,
            "spotifyCountry": spotify_country,
            "spotifyProduct": spotify_product,
            "spotifyUrl": spotify_link,
            "spotifyPictures": spotify_images,
        },
    }

    # Now we take user_data and shove it into the database
    db.spotifyUsers.insert_one(user_data)


def processArtist():
    pass


def processAlbum():
    pass


def processTrack():
    pass


def get_and_store_artists_by_genre(genre, offset=0, limit=50):
    access_token = get_our_token()
    spotify_client = SPOTID
    spotify_secret = SPOTSECRET
    spotify_base_url = SPOTAPIBASE

    print("Starting Spotify API pull")
    print(
        f"Client ID: {spotify_client}, Client Secret: {spotify_secret}, Base URL: {spotify_base_url}"
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    #  Build the query url
    query_url = f"{spotify_base_url}/search?q=genre%3A{genre}&type=artist&{limit}&offset={offset}"
    # Query the API by getting it with the headers
    response = requests.get(query_url, headers=headers).json()
    collection = db.spotifyArtists
    try:
        items = response["artists"]["items"]
        for item in items:
            existing_item = collection.find_one({"id": item["id"]})

            if existing_item is None:
                collection.insert_one(item)
                print(f"Added {item['name']} to the database")
            else:
                print(f'{item["name"]} already exists in the database')

    except Exception as e:
        print(f"an error occurred: {e}")


def get_our_token():
    spotify_client = SPOTID
    spotify_secret = SPOTSECRET

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = {
        "grant_type": "client_credentials",
        "client_id": spotify_client,
        "client_secret": spotify_secret,
    }

    response = requests.post(SPOTTOKENURL, data=body)
    print(response.json())
    return response.json()["access_token"]


get_our_token()
myclient.close()
# get_and_store_artists_by_genre("rock")
