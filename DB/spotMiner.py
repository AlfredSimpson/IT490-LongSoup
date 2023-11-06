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


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTID,
        client_secret=SPOTSECRET,
        redirect_uri=SPOTURI,
        scope=SPOTSCOPE,
        cache_path=".cache",
    )
)


def keepActive():
    """
    This was designed to be called every hour.
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


# def get_recent_topArtists(uid=None, time_range="shrot_term", limit=10):
#     """A user's top artists"""
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
#     # If all of this is good, we can continue to get the top artists


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


def get_playlists(access_token=None, uid=None):
    """Get a user's playlists"""

    db.users.find_one({"uid": uid})
    if access_token is None:
        raise ValueError("No access token provided")
    if uid is None:
        raise ValueError("No user id provided")
    else:
        headers = {"Authorization": "Bearer " + access_token}


####################
# Schedule things
####################

# As spotify requires us to refresh the token every hour, we'll do it every 50 minutes to be safe.
schedule.every(50).minutes.do(keepActive)

while True:
    schedule.run_pending()
    time.sleep(1)
