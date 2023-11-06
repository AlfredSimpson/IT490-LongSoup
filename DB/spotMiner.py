import spotipy
import pymongo
import os, sys, json, time, requests
from datetime import datetime
import schedule
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

spotSchema = {
    "uid": "",
    "tasteid": "",
    "spotifyInformation": {
        "spotifyId": "",
        "spotifyName": "",
        "spotifyEmail": "",
        "spotifyProfileImage": "",
        "spotifyCountry": "",
        "spotifyProduct": "",
        "spotifyFollowers": "",
        "spotifyUrl": "",
        "spotAccessToken": "",
        "spotRefreshToken": "",
    },
    "likes": [
        {
            "artists": [{"artist_name": "", "genres": "", "value": ""}],
            "tracks": [
                {
                    "artist_name": "",
                    "track_name": "",
                    "popularity": "",
                    "genres": "",
                    "value": "",
                }
            ],
            "genres": [{"genre_name": "", "value": ""}],
        }
    ],
    "dislikes": [
        {
            "artists": [{"artist_name": "", "genres": "", "value": ""}],
            "tracks": [
                {
                    "artist_name": "",
                    "track_name": "",
                    "popularity": "",
                    "genres": "",
                    "value": "",
                }
            ],
            "genres": [{"genre_name": "", "value": ""}],
        }
    ],
    "recentlyPlayed": [
        {
            "artist_name": "",
            "artist_info": [
                {
                    "images": [{"height": "", "url": "", "width": ""}],
                    "genres": [],
                    "popularity": "",
                    "uri": "",
                }
            ],
            "track_name": "",
            "track_info": [
                {
                    "album": {},
                    "href": "",
                    "id": "",
                }
            ],
            "genres": [],
        }
    ],
    "knownArtists": [
        {
            "artist_name": "",
        }
    ],
    "knownTracks": [
        {
            "artist_name": "",
            "track_name": "",
            "track_url": "",
        }
    ],
}

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


# sp = spotipy.Spotify(
#     auth_manager=SpotifyOAuth(
#         client_id=SPOTID,
#         client_secret=SPOTSECRET,
#         redirect_uri=SPOTURI,
#         scope=SPOTSCOPE,
#         cache_path=".cache",
#     )
# )


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
    spotify_product = api_json["product"] # premium, free, etc

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



def keepActive():
    """
    This was designed to be called every hour... but we can only do that once lol
    """
    users = db["users"]
    tokens = {}
    for user in users.find():
        if "refresh_token" in user:
            tokens[user["uid"]] = user["refresh_token"]
            print(f'\nPrevious refresh token: {user["refresh_token"]}\n')
            req_body = {
                "grant_type": "refresh_token",
                "refresh_token": user["refresh_token"],
                "client_id": SPOTID,
                "client_secret": SPOTSECRET,
            }
            try:
                r = requests.post(SPOTTOKENURL, data=req_body)
                print(f"\nSent a request out, got {r.status_code}\n")
                if r.status_code == 200:
                    print("\n\nSuccessfully refreshed token for user %s" % user["uid"])
                    print(f"Full JSON response:\n\n\t {r.json()}\n\n\t")
                    # Update the database
                    print(f'Attempting to access db by going to uid: {user["uid"]}')
                    users.update_one(
                        {"uid": user["uid"]},
                        {
                            "$set": {
                                "access_token": r.json()["access_token"],
                                "refresh_info": {"last_refresh": datetime.utcnow()},
                                "spotify_token_time_in": datetime.utcnow(),
                                "token_type": r.json()["token_type"],
                            }
                        },
                    )
                else:
                    print("Failed to refresh token for user %s" % user["uid"])
                    # unset the refresh token - Comment out
                    users.update_one(
                        {"uid": user["uid"]},
                        {"$unset": {"refresh_token": ""}},
                    )
            except:
                print(
                    "Error while attempting to refresh token for user %s" % user["uid"]
                )
                # unset the refresh token
                users.update_one(
                    {"uid": user["uid"]},
                    {"$unset": {"refresh_token": ""}},
                )

        else:
            print("No refresh token found for user %s" % user["uid"])


def readAccessToken():
    """
    This is a helper function that will return the access token for a user.
    """
    users = db["users"]
    tokens = {}
    for user in users.find():
        if "refresh_token" in user:
            tokens[user["uid"]] = user["refresh_token"]


def getProfile():
    

# def get_user_info(uid=None):
#     """Get a user's info"""
#     if uid is None:
#         raise ValueError("No user id provided")
#     users = db["users"]
#     user = users.find_one({"uid": uid})
#     if user is None:
#         raise ValueError("User not found")
#     if "access_token" not in user:
#         raise ValueError("User has no access token")
#     if "refresh_token" not in user:
#         raise ValueError("User has no refresh token")
#     # If all of this is good, we can continue to get the user info
#     r = requests.get(
#         SPOTAPIBASE + "/v1/me",
#         headers={"Authorization": "Bearer " + user["access_token"]},
#     )
#     if r.status_code == 200:
#         print(r.json())
#     else:
#         print(r.status_code)
#         print(r.json())


# def get_user_info(uid=None):
#     """Get a user's info"""
#     if uid is None:
#         raise ValueError("No user id provided")
#     users = db["users"]
#     user = users.find_one({"uid": uid})
#     if user is None:
#         raise ValueError("User not found")
#     if "spotify_token" not in user:
#         raise ValueError("User has no access token")
#     if "refresh_token" not in user:
#         raise ValueError("User has no refresh token")
#     # If all of this is good, we can continue to get the user info
#     print(sp.current_user_top_tracks(limit=3))


def get_user_playlists(uid=None, access_token=None):
    users = db.users.find_one({"uid": uid})
    access_token = users["spotify_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SPOTAPIBASE + "/me/playlists", headers=headers)
    new_r = response.json()

    return new_r


####################
# Schedule things
####################

# As spotify requires us to refresh the token every hour, we'll do it every 50 minutes to be safe.
schedule.every(50).minutes.do(keepActive)

while True:
    schedule.run_pending()
    time.sleep(1)
