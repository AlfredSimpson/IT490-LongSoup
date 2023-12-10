import pika
import os, sys, json, random
from datetime import datetime, timedelta
import bcrypt

# Script below imports email + 2FA code
from LongAuthMessage import send_email, sentNumber

# import LongMongoDB
# import LongDB deprecated for now - will be used later
import pymongo
import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


load_dotenv()


maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")
maindbhost = os.getenv("MONGO_HOST")  # This is localhost so... we can omit this later.


BROKER_HOST = os.getenv("BROKER_HOST")
BROKER_VHOST = os.getenv("BROKER_VHOST")
BROKER_QUEUE = os.getenv("BROKER_QUEUE")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE")
BROKER_USER = os.getenv("BROKER_USERNAME")
BROKER_PASS = os.getenv("BROKER_PASSWORD")

# TODO change the db to the maindb, add the user and pass to the connection
myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]

#############
# Methods related to Spotify
#############


# TODO: Move spotify related things to spotify class - and this should only be called IF the user is logged in. It should also store the data in the database.
def get_recs(
    genre="punk", valence="0.2", energy="0.7", popularity="25", fromlogin=False
):
    """
    # get_recs
    takes in genre, valence, energy, and popularity as arguments and returns a list of recommended songs.

    Args:
        genre (str, optional): The seed_genre that spotify allows. Defaults to "punk".
        valence (str, optional): Valence is how spotify defines happiness. Defaults to "0.2".
        energy (str, optional): Energy is presumed to be the amplitude of the song. Defaults to "0.7".
        popularity (str, optional): How popular a song is. 0-100. Defaults to "25".
        fromlogin (bool, optional): Necessary to define, optional param, allows us to stay on the page and return new recs with correct data. Defaults to False.

    Returns:
        returnCode: 0 if successful, 1 if not
        message: Success or failure message
        gotrecs: True or False
        data: Logged in or not
        music: List of recommended songs

    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
    )

    genre = genre
    valence = valence
    energy = energy
    popularity = popularity

    results = sp.recommendations(
        seed_genres=[genre],
        target_valence=valence,
        target_energy=energy,
        min_popularity=popularity,
        limit=4,
    )
    data = {"musicdata": []}
    for i in results["tracks"]:
        # Should really set up a try catch here
        track = i["name"]  # Get the track name
        artist = i["artists"][0]["name"]  # Get the artist name
        url = i["external_urls"]["spotify"]  # Get the url
        data["musicdata"].append({"track": track, "artist": artist, "url": url})
    if fromlogin:
        return data
    else:
        # return music as a narrowed json object
        music = data["musicdata"]
        # return necessary information to front end
        return {
            "returnCode": 0,
            "message": "Success",
            "gotrecs": "True",
            "data": {
                "loggedin": "True",
                "name": "buddy",
            },
            "music": music,
        }


def query_artist(artist, typebyartist=None):
    """
    query_artist takes in artist and typebyartist as arguments and returns a list of albums, tracks, or related artists.
    Args:
        artist (_type_): the artist you want to query
        typebyartist (_type_): the type of query you want to do. Can be albums, tracks, or related.

    Returns:
        what the variable typebyartist dictates.
    """
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    # Initialize
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
    )
    # Query
    results = sp.search(q="artist:" + artist, type="artist")
    items = results["artists"]["items"]

    if len(items) < 1:
        return print(
            "Oh this doesn't rock - this artist doesn't exist by how it was spelled"
        )
    else:
        if type == "albums":
            artist_id = items[0]["id"]
            # Get albums
            albums = sp.artist_albums(artist_id, album_type="album")
            albums = albums["items"]
            album_names = []
            album_urls = []
            music = []
            for album in albums:
                album_names.append(album["name"])
                album_urls.append(album["href"])
            for i in range(0, len(album_names)):
                music.append({"album": album_names[i], "url": album_urls[i]})
            print(f"Albums returning as {music}")
            return {
                "returnCode": 0,
                "message": "Success",
                "gotrecs": "True",
                "data": {
                    "loggedin": "True",
                    "name": "buddy",
                    "byArtist": "True",
                    "findAlbums": "True",
                },
                "music": music,
            }
        elif type == "tracks":
            artist_id = items[0]["id"]
            tracks = sp.artist_top_tracks(artist_id)
            tracks = tracks["tracks"]
            track_names = []
            track_urls = []
            music = []
            for track in tracks:
                track_names.append(track["name"])
                track_urls.append(track["href"])
            for i in range(0, len(track_names)):
                music.append({"track": track_names[i], "url": track_urls[i]})
            return {
                "returnCode": 0,
                "message": "Success",
                "data": {
                    "loggedin": "True",
                    "name": "buddy",
                    "byArtist": "True",
                    "findTracks": "True",
                },
                "music": music,
            }
        elif type == "related":
            artist_id = items[0]["id"]
            related = sp.artist_related_artists(artist_id)
            related = related["artists"]
            related_names = []
            related_urls = []
            music = []
            for artist in related:
                related_names.append(artist["name"])
                related_urls.append(artist["href"])
            for i in range(0, len(related_names)):
                music.append({"artist": related_names[i], "url": related_urls[i]})
            return {
                "returnCode": 0,
                "message": "Success",
                "gotrecs": "True",
                "data": {
                    "loggedin": "True",
                    "name": "buddy",
                    "byArtist": "True",
                    "findRelated": "True",
                },
                "music": music,
            }


def storeToken(access_token, refresh_token, expires_in, token_type, usercookieid):
    """
    storeToken takes in token and uid as arguments and stores the token in the database.

    Args:
        access_token (string): the token to access Spotify
        refresh_token (string): the refresh token to Spotify
        expires_in (string): the time the token expires
        token_type (string): the type of token
        usercookie (string): the usercookie to query with to tie it to an account. May switch to uid after sessions fully implemented

    Returns:
        _type_: _description_
    """
    thedate = datetime.datetime.now()
    print(f'\nAttempting to add token "{access_token}" to users\n')
    print(f"\nAdding on {thedate}\n")
    db.users.update_one(
        {"usercookieid": usercookieid},
        {
            "$set": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": token_type,
                "expires_in": expires_in,
                "spotify_token_time_in": thedate,
            }
        },
    )
    # We'll want to call a way to check this - or set up another script on the dmz which queries us to query the database for any access tokens.
    return {"returnCode": 0, "message": "Successfully added token to database"}


#############
# Methods related to user management
#############


def get_next_uid():
    """
    get_next_uid() returns the next available uid for a new user.
    This is done by finding the highest uid in the database and adding 1 to it.
    We use this to keep our uids unique and to add relational data to a non relational database.
    """
    nextid = 0
    # db = myclient.testDB
    col = db.users
    highest_id = col.find_one(sort=[("uid", -1)])
    if highest_id:
        nextid = 1
        nextid += highest_id["uid"]
    return nextid


def addUser(email, password, sessionid, cookieid):
    uid = get_next_uid()
    db = myclient.testDB
    col = db.users

    col.insert_one(
        {
            "uid": uid,
            "email": email,
            "password": password,
            "sessionid": sessionid,
            "cookieid": cookieid,
        }
    )


def TEST_auth_user(useremail, password):
    """auth_user takes in useremail and password as arguments and returns a boolean True if the user exists and the password matches. Otherwise, it returns a boolean False. This is not used currently as it is for the login method, but can be reused for other methods so I'm leaving for now since it's a good tester.

    Args:
        useremail (_type_): the useremail to check
        password (_type_): the password to check

    Returns:
        bool: True or False
    """
    db = myclient.testDB
    col = db.users
    user = col.find_one({"email": useremail})
    if user and user["password"] == password:
        print("okay then, we got in")
        return True
    else:
        print("did notwork")
        return False


def do_logout(usercookieid, session_id):
    """# do_logout
    Takes in usercookieid and session_id as arguments and logs the user out.

    Args:
        usercookieid (string): the usercookieid to logout
        session_id (string): the session_id to destroy
    """

    # Query db.users. and unset the session id where the usercookieid matches
    # LMDB = LongMongoDB.LongMongoDB(maindbuser, maindbpass, maindbhost, maindb)
    # LMDB.invalidate_session(usercookieid, session_id)
    # An alternative:
    db.users.update_one({"cookieid": usercookieid}, {"$unset": {"sessionid": ""}})
    # print(f"User {usercookieid} logged out")
    return {"\nreturnCode": 0, "message": "Logout successful\n"}

def do_login(useremail, password, session_id, usercookieid):
    """
    # do_login
    Takes useremail and password as arguments and attempts to login the user.
    It stores the session_id and usercookieid

    Args:
        useremail (string): The useremail to check
        password (string): The password to check
        session_id (string): The session_id to store
        usercookieid (string): The usercookieid to store

    Returns:
        dict: A dictionary containing the login result
    """
    # LMDB = LongMongoDB.LongMongoDB(maindbuser, maindbpass, maindbhost, maindb)

    # Connect to the database
    collection = db.users
    user = collection.find_one({"email": useremail})
    if user:
        dbpassword = user["password"]
        enteredPass = password.encode('utf-8')
        #dbsalt = user["salt"].encode('utf-8')

        if bcrypt.checkpw(enteredPass, dbpassword.encode('utf-8')):
            # Send mail (Referencing LongAuthMessage script to send 2FA code)
            send_email()
            userInput = sentNumber

            # Create a document with a field titled "code" and an expiration time
            expiration_time = datetime.utcnow() + timedelta(minutes=5)
            addCode = {
                "$set": {
                    "code": userInput,
                    "expiration_time": expiration_time
                }
            }  
            # Insert updated document into the collection
            collection.update_one(addCode)

            if  userInput == sentNumber: #result from form == sentNumber: # add else statement to allow user to try again to type 2FA code
                # Update/set the session id & user cookie id
                # LMDB.set_usercookieid(useremail, usercookieid)
                first_result = db.users.find_one({"email": useremail})
                uid = first_result["uid"]
                db.users.update_one(
                    {"uid": uid}, {"$set": {"usercookieid": usercookieid}}, upsert=False
                )
                # LMDB.set_session(session_id, useremail)
                db.users.update_one(
                    {"uid": uid}, {"$set": {"sessionid": session_id}}, upsert=False
                )
                # Get the user's name and spot_name to pass back to the front end
                # user_fname = LMDB.get_name(usercookieid)
                user_uid = uid
                user_fname = db.userinfo.find_one({"uid": uid})["first_name"]
                user_spot_name = db.userinfo.find_one({"uid": uid})["spot_name"]

                # Get some tunes
                genre = random.choice(["punk", "rock", "pop", "country", "rap", "hip-hop"])
                valence = random.uniform(0, 1)
                energy = random.uniform(0, 1)
                popularity = random.randint(0, 100)
                music = get_recs(genre, valence, energy, popularity, True)

                return {
                    "returnCode": 0,
                    "message": "Login successful",
                    "sessionValid": "True",
                    "music": music["musicdata"],
                    "userinfo": {
                        "name": user_fname,
                        "spot_name": user_spot_name,
                        "uid": user_uid,
                    },
                    "data": {
                        "loggedin": "True",
                    },
                }
        else:
            print("\n[LOGIN ERROR] User Not Found\n")
            return {
                "returnCode": 1,
                "message": "You have failed to login.",
                "sessionValid": False,
                "data": {
                    "loggedin": False,
                    "errorStatus": False,
                    "errorOutput": "Either the password or email provided does not match. Please try again.",
                },
            }
       
def test_do_login():
    # Mock data
    useremail = "8bitjava5354@gmail.com"
    password = "hashbrown"
    session_id = "sessionid"
    usercookieid = "usercookieid"
    first_name = "hash"
    last_name = "brown"
    spot_name = "hashbrown"

    # Call do_register with mock data
    result = do_login(
        useremail, password, session_id, usercookieid, first_name, last_name, spot_name
    )

    # Print the result for inspection
    print(result)

# Run the test
test_do_login()