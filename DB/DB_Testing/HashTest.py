import pika
import os, sys, json, random
import datetime

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


# TODO change the db to the maindb, add the user and pass to the connection
myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]


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
    """# do_login
    Takes useremail and password as arguments and attempts to login the user.
    It stores thes session_id and usercookieid

    Args:
        useremail (string): The useremail to check
        password (string): The password to check
        session_id (string): The session_id to store
        usercookieid (string): The usercookieid to store

    Returns:
        _type_: _description_
    """
    # LMDB = LongMongoDB.LongMongoDB(maindbuser, maindbpass, maindbhost, maindb)

    # Connect to the database
    collection = db.users
    user = collection.find_one({"email": useremail})
    if user and user["password"] == password:
        # update/set the session id & user cookie id
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
        # get the user's name and spot_name to pass back to the front end
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
            print(f'\nAttempting to add user "{useremail}" to users\n')
            uid = get_next_uid()
            users.insert_one(
                {
                    "uid": uid,
                    "email": useremail,
                    "password": password,
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
            logging.error("[REGISTRATION ERROR] Unknown error adding user to database")
            return {
                "returnCode": 1,
                "message": "[REGISTRATION ERROR] Unable to add user to database. Unknown error.",
                "data": {
                    "errorStatus": True,
                    "errorOutput": "Registration unsuccessful - Please try again with a different email.",
                },
            }
def test_do_register():
    # Mock data
    useremail = "hashbrown@gmail.com"
    password = "hashbrown"
    session_id = "sessionid"
    usercookieid = "usercookieid"
    first_name = "hash"
    last_name = "brown"
    spot_name = "hashbrown"

    # Call do_register with mock data
    result = do_register(
        useremail, password, session_id, usercookieid, first_name, last_name, spot_name
    )

    # Print the result for inspection
    print(result)

# Run the test
test_do_register()


