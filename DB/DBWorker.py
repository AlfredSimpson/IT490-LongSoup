import pika
import os, sys, json, random
from datetime import datetime, timedelta

# import datetime
import bcrypt

# import LongMongoDB

# import LongDB deprecated for now - will be used later
import pymongo

# import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

from LongAuthMessage import send_email


LIKED_ARTISTS = {
    "uid": "",
    "artists": [
        {
            "artist_id": "",
        }
    ],
}

LIKED_TRACKS = {
    "uid": "",
    "tracks": [
        {
            "track_id": "",
        }
    ],
}

LIKED_ALBUMS = {
    "uid": "",
    "albums": [
        {
            "album_id": "",
        }
    ],
}

LIKED_GENRES = {
    "uid": "",
    "genres": [
        {
            "genre_name": "",
        }
    ],
}


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


myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]

#############
# Methods related to Spotify
#############


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


def storeToken(access_token, refresh_token, expires_in, token_type, uid):
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
    thedate = datetime.now()
    print(f'\nAttempting to add token "{access_token}" to users\n')
    print(f"\nAdding on {thedate}\n")
    db.users.update_one(
        {"uid": uid},
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
# Methods related to messages & taste
#############


def loadMessages(genre):
    """
    loadMessages takes in genre as an argument and returns a list of messages.

    Args:
        genre (_type_): _description_

    Returns:
        _type_: _description_
    """
    pass


def postMessage(message, genre, uid, timestamp):
    """
    postMessage takes in message, genre, and uid as arguments and posts the message to the database.

    Args:
        message (_type_): _description_
        genre (_type_): _description_
        uid (_type_): _description_

    Returns:
        _type_: _description_
    """
    # !Get the user's spotify username
    # TODO! Get the user's spotify username

    try:
        doc = db.messages.find_one({"genre": genre})

        if doc:
            db.messages.update_one(
                {"genre": genre},
                {
                    "$push": {
                        "messages": {
                            "message": message,
                            "uid": uid,
                            "timestamp": timestamp,
                        }
                    }
                },
            )
            # We should also update taste...
            return {
                "returnCode": 0,
                "message": "Successfully posted message",
                "data": {"errorStatus": False, "message": message, "uid": uid},
            }
        else:
            db.messages.insert_one(
                {"genre": genre, "messages": [{"message": message, "uid": uid}]}
            )
            return {
                "returnCode": 0,
                "message": "Successfully posted message",
                "data": {"errorStatus": False, "message": message, "uid": uid},
            }

    except Exception as e:
        print(f"\nError finding genre: {e}\n")
        return {
            "returnCode": 1,
            "message": "Error finding genre",
            "data": {"errorStatus": True, "errorOutput": "Error finding genre"},
        }


def removeLike(uid, spotify_id, like_type):
    # This should remove a like from a user's taste
    pass


def removeDislike(uid, spotify_id, like_type):
    # This should remove a dislike from a user's taste
    pass


def handle_like_event(uid, query_type, spotify_id, like_type):
    """
    handle_like takes in usercookieid, id, and like_type as arguments and handles the like.
    Args:
        uid (string): the userid
        query_type (string): what type of query (artist/track/album)
        id (string): The id of that query type - i.e., they looked up a track, this is the track id.
        like_type (string): Like/Dislike
    Returns:
        Dict: Nothing useful
    """
    print(f'\nHandling like for user "{uid}"\n')
    print(
        f"query_type is {query_type}, spotify_id is {spotify_id}, liketype is {like_type}"
    )

    if like_type == "like":
        # Add to user taste
        print("like received")
        addLike(uid, query_type, spotify_id, like_type)
        # NOTE _ we'll want to change add like to return a T/F value so we can act accordingly. Leaving this now so it doesn't crash in testing
        return {
            "returnCode": 0,
            "message": "Successfully liked track!",
            "data": {
                "errorStatus": False,
                "errorOutput": "Successfully liked",
            },
        }
    elif like_type == "dislike":
        print("dislike received")
        addDislike(uid, query_type, spotify_id, like_type)
        return {
            "returnCode": 0,
            "message": "Successfully disliked track!",
            "data": {
                "errorStatus": False,
                "errorOutput": "Successfully disliked",
            },
        }
    else:
        return {
            "returnCode": 1,
            "message": "Error handling like",
            "data": {
                "errorStatus": True,
                "errorOutput": "Error handling like - like_type not specified",
            },
        }


def addLike(uid, query_type, spotted_id, like_type):
    liked_col = db["liked_" + query_type]
    disliked_col = db["disliked_" + query_type]
    # Check if already liked
    if liked_col.find_one({"uid": uid, "like.id": spotted_id}):
        print("Item already liked")
        return False
    # Check if disliked and remove if necessary

    if disliked_col.find_one({"uid": uid, "dislike.id": spotted_id}):
        print("Removing previously disliked item")
        disliked_col.update_one(
            {"uid": uid}, {"$pull": {"dislike": {"id": spotted_id}}}
        )
    # Add the like
    liked_col.update_one(
        {"uid": uid}, {"$addToSet": {"like": {"id": spotted_id}}}, upsert=True
    )
    print("\nItem liked successfully!")
    return True


def addDislike(uid, query_type, spotted_id, like_type):
    liked_col = db["liked_" + query_type]
    disliked_col = db["disliked_" + query_type]
    # Check if already disliked
    if disliked_col.find_one({"uid": uid, "dislike.id": spotted_id}):
        print("Item already disliked")
        return False
    # Check if liked and remove if necessary
    if liked_col.find_one({"uid": uid, "like.id": spotted_id}):
        print("Removing previously liked item")
        liked_col.update_one({"uid": uid}, {"$pull": {"like": {"id": spotted_id}}})
    # Add the dislike
    disliked_col.update_one(
        {"uid": uid}, {"$addToSet": {"dislike": {"id": spotted_id}}}, upsert=True
    )
    print("Item disliked successfully!")
    return True


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


def auth_login(uid, auth_code):
    print(f'\nAttempting to auth user "{uid}"\n')
    collection = db.users
    user = collection.find_one({"uid": uid})
    if user:
        # Query the db to find the code and expiration_time for the user
        code = user["code"]
        print(f"code is {code} and auth_code is {auth_code}")
        expiration_time = user["expiration_time"]
        print(
            f"Code showing as {code} and expiration_time showing as {expiration_time}"
        )
        auth_code = int(auth_code)
        # Check if the code is valid or expired
        if auth_code == code:
            print("Auth code match confirmation")
            if datetime.utcnow() < expiration_time:
                print("\n[AUTH] Login valid and in time...\n")
                user_fname = db.userinfo.find_one({"uid": uid})["first_name"]
                user_spot_name = db.userinfo.find_one({"uid": uid})["spot_name"]
                genre = random.choice(
                    ["punk", "rock", "pop", "grunge", "country", "rap", "hip-hop"]
                )
                valence = random.uniform(0, 1)
                energy = random.uniform(0, 1)
                popularity = random.randint(0, 100)
                music = get_recs(genre, valence, energy, popularity, True)
                return {
                    "returnCode": 0,
                    "message": "Login Successful!",
                    "sessionValid": True,
                    "music": music["musicdata"],
                    "userinfo": {
                        "name": user_fname,
                        "spot_name": user_spot_name,
                        "uid": uid,
                    },
                    "data": {
                        "loggedin": True,
                        "errorStatus": False,
                        "errorOutput": "Code matches",
                    },
                }
            else:
                print("Code matched, but expired.")
                return {
                    "returnCode": 1,
                    "message": "Code expired",
                    "sessionValid": False,
                    "data": {
                        "loggedin": False,
                        "errorStatus": False,
                        "errorOutput": "Your code has expired. Please request a new one.",
                    },
                }
        else:
            # Code is not correct
            print("\n[LOGIN SUCCESS] Code failure\n")
            return {
                "returnCode": 1,
                "message": "Code expired",
                "sessionValid": False,
                "data": {
                    "loggedin": False,
                    "errorStatus": False,
                    "errorOutput": "Your code was not valid. Please request a new one.",
                },
            }
    pass


def start_login(useremail, password, session_id, usercookieid):
    collection = db.users
    user = collection.find_one({"email": useremail})
    if user:
        dbpassword = user["password"]
        enteredPass = password.encode("utf-8")

        if bcrypt.checkpw(enteredPass, dbpassword.encode("utf-8")):
            # Update/set the session id & user cookie id
            first_result = db.users.find_one({"email": useremail})
            uid = first_result["uid"]
            db.users.update_one(
                {"uid": uid}, {"$set": {"usercookieid": usercookieid}}, upsert=False
            )
            db.users.update_one(
                {"uid": uid}, {"$set": {"sessionid": session_id}}, upsert=False
            )
            # Get the user's name and spot_name to pass back to the front end
            user_uid = uid
            user_fname = db.userinfo.find_one({"uid": uid})["first_name"]
            user_spot_name = db.userinfo.find_one({"uid": uid})["spot_name"]
            auth_num = send_email(useremail)
            expiration_time = datetime.utcnow() + timedelta(minutes=5)
            addCode = {"$set": {"code": auth_num, "expiration_time": expiration_time}}
            db.users.update_one({"uid": uid}, addCode)
            return {
                "returnCode": 0,
                "message": "Login successful - Authentication Needed",
                "sessionValid": "True",
                "authenticated": 0,
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


# Ignore below, this is old
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
        enteredPass = password.encode("utf-8")
        # dbsalt = user["salt"].encode('utf-8')

        if bcrypt.checkpw(enteredPass, dbpassword.encode("utf-8")):
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


def do_register(
    useremail, password, session_id, usercookieid, first_name, last_name, spot_name
):
    """
    # do_register
    Takes useremail and password as arguments and attempts to register the user.

    It returns a message indicating whether the registration was successful or not.
    """
    # Connect to the database

    # See if the user exists already
    users = db.users
    user = users.find_one({"email": useremail})
    if user:
        # User already exists
        print("\n[REGISTRATION ERROR]\tUser already exists!\n")

        msg = {
            "returnCode": 1,
            "message": "Registration failed - useremail exists",
            "session_id": False,
            "e": {"ERROR": "User already exists"},
        }
        return msg
    else:
        print(
            "\n[REGISTRATION]\tUser email not found in users table. Attempting to register user!\n"
        )
        try:
            salt = bcrypt.gensalt()
            encodedpassword = password.encode("utf-8")
            hashed_password = bcrypt.hashpw(encodedpassword, salt)
            print(hashed_password)
            print(f'\nAttempting to add user "{useremail}" to users\n')
            uid = get_next_uid()
            users.insert_one(
                {
                    "uid": uid,
                    "email": useremail,
                    "password": hashed_password.decode("utf-8"),
                    "salt": salt.decode("utf-8"),
                    "sessionid": session_id,
                    "cookieid": usercookieid,
                }
            )
            print(
                f"\nUser {useremail} added to database... moving to add to userinfo\n"
            )
            db.userinfo.insert_one(
                {
                    "uid": uid,
                    "first_name": first_name,
                    "last_name": last_name,
                    "spot_name": spot_name,
                }
            )
            music = get_recs(fromlogin=True)
            music = music["musicdata"]
            return {
                "returnCode": 0,
                "message": "Registration successful",
                "data": {
                    "loggedin": "True",
                    "name": first_name,
                    "sessionValid": "True",
                    "errorStatus": False,
                },
                "music": music,
                "userinfo": {
                    "uid": uid,
                    "user_fname": first_name,
                    "usercookieid": usercookieid,
                },
            }
        except:
            print("\n[REGISTRATION ERROR] Unknown error adding user to database\n")
            # logging.error("[REGISTRATION ERROR] Unknown error adding user to database")
            return {
                "returnCode": 1,
                "message": "[REGISTRATION ERROR] Unable to add user to database. Unknown error.",
                "data": {
                    "errorStatus": True,
                    "errorOutput": "Registration unsuccessful - Please try again with a different email.",
                },
            }


#############
# Methods related to inbound/outbound communication with the web server and DMZ
#############


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


"""
def do_validate(usercookieid, session_id):
    # This takes in the sessionID and validates it by checking the database. If the sessionTable shows that the session is valid for the user, then it returns a boolean True. Otherwise, it returns a boolean False.
    validity = db.validate_session(usercookieid, session_id)
    # TODO: add this to the logging system
    # TODO: fix return statements, port validate_session
    print(f"\nvalidate_session returned: {validity}\n")
    return validity
"""


def request_processor(ch, method, properties, body):
    """# request_processor
    Takes in ch, method, properties, and body as arguments and processes the request based on the type of request received.

    Args:
        ch (_type_):
        method (_type_): _description_
        properties (_type_): _description_
        body (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Try / except added just in case bad JSON is received
    try:
        request = json.loads(body.decode("utf-8"))
        # logging.debug(f"\nReceived request: {request}\n")
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        # logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        # logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "login":
                response = start_login(
                    request["useremail"],
                    request["password"],
                    request["session_id"],
                    request["usercookieid"],
                )
            case "auth_login":
                response = auth_login(
                    request["uid"],
                    request["auth_code"],
                )
            case "backdoor":
                response = do_login(
                    request["useremail"],
                    request["password"],
                    request["session_id"],
                    request["usercookieid"],
                )
            case "logout":
                response = do_logout(
                    request["usercookieid"],
                    request["session_id"],
                )
                pass
            case "validate_session":
                # response = do_validate(
                #     request["usercookieid"],
                #     request["session_id"],
                # )
                return {
                    "returnCode": 1,
                    "message": "Not right now chief I'm in the zone",
                }
            case "register":
                print("\nReceived registration request\n")
                response = do_register(
                    request["useremail"],
                    request["password"],
                    request["session_id"],
                    request["usercookieid"],
                    request["first_name"],
                    request["last_name"],
                    request["spot_name"],
                )
            case "logout":
                response = do_logout(
                    request["usercookieid"],
                    request["session_id"],
                )
            case "simplerecs":
                response = get_recs(
                    request["genre"],
                    request["popularity"],
                    request["valence"],
                )
            case "byArtist":
                response = query_artist(request["artist"], request["typeOf"])
            case "spotToken":
                response = storeToken(
                    request["access_token"],
                    request["refresh_token"],
                    request["expires_in"],
                    request["token_type"],
                    request["uid"],
                )
            case "loadMessages":
                response = ""
                pass
            case "postMessage":
                response = ""
                pass
            case "getMusic":
                response = ""
                pass
            case "like_event":
                response = handle_like_event(
                    request["uid"],
                    request["query_type"],
                    request["spotted_id"],
                    request["like_type"],
                )
            case _:
                # Default case - basically, all else failed.
                response = {
                    "returnCode": 0,
                    "message": "Server received request and processed - no action taken. Unknown type",
                }

    # Send the response back to the client
    print(f"\nWe should have a response here if we're publishing...{response}")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


vHost = BROKER_VHOST
queue2 = BROKER_QUEUE
exchange2 = BROKER_EXCHANGE

creds = pika.PlainCredentials(username=BROKER_USER, password=BROKER_PASS)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=BROKER_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)

channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
