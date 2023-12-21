# This is the worker class for the DBProfiles - handling things separately. It is like DBWorker, but specifically for the profiles on CGS


import pika
import os, sys, json, random
from datetime import datetime, timedelta
import bcrypt
import pymongo
import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
BROKER_HOST = os.getenv("BROKER_HOST")
BROKER_USER = os.getenv("BROKER_USER")
BROKER_PASS = os.getenv("BROKER_PASS")
BROKER_VHOST = os.getenv("BROKER_VHOST")
BROKER_QUEUE = os.getenv("BROKER_QUEUE")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE")

# profile connection info
PRO_PASS = os.getenv("PROFILE_PASS")
PRO_USER = os.getenv("PROFILE_USER")
PRO_HOST = os.getenv("PROFILE_HOST")
PRO_PORT = os.getenv("PROFILE_PORT")
PRO_VHOST = os.getenv("PROFILE_VHOST")
PRO_QUEUE = os.getenv("PROFILE_QUEUE")
PRO_EXCHANGE = os.getenv("PROFILE_EXCHANGE")


# Primary Mongo DB
db_profiles = os.getenv("DB_PROFILES")
DB_MAIN_USER = os.getenv("DB_PRO_USER")
DB_MAIN_PASS = os.getenv("DB_PRO_PASS")

# Connect to the database - we're going to use cgs_mb

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/" % (DB_MAIN_USER, DB_MAIN_PASS)
)

db = myclient[db_profiles]


def setUsername(username, uid, privacy):
    """# setUsername
    This function sets the username for the user with the given uid.

    Args:
        username (_type_): _description_
        uid (_type_): _description_

    Returns:
        _type_: _description_
    """
    allprofiles = db.allprofiles
    try:
        if allprofiles.find_one({"uid": uid}):
            # We found the user, so we're going to update the username
            allprofiles.update_one(
                {"uid": uid},
                {"$set": {"username": username, "username_privacy": "public"}},
            )
        else:
            # The user didn't previously have a profile started, so we're going to create one
            allprofiles.update_one({"uid": uid}, {"$set": {"username": username}})
        return {"returnCode": 0, "message": "success"}
    except Exception as e:
        print(f"\nError setting username: {e}\n")
        return False


def updateProfile(uid, profile_field, field_data, privacy="private"):
    """# updateProfile
    This function updates the profile data for the given user.

    Args:
        username (_type_): _description_
        uid (_type_): _description_
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    match profile_field:
        case "username":
            # We're going to set the username
            return setUsername(field_data, uid, privacy)
        case "location":
            pass
        case "bio":
            pass
        case "playlists":
            pass
        case _:
            return {"returnCode": 1, "message": "Invalid profile field"}


def getProfileData(username):
    """# getProfileData
    This function gets the profile data from the database and returns it.
    """
    try:
        data = db.profiles.find_one({"username": username})
        return True, data
    except Exception as e:
        print(f"\nError retrieving profile: {e}\n")
        data = ""
        return False, data


def load_profile(username_requested, uid_requesting):
    try:
        result, data = getProfileData(username_requested)
        if result:
            # We found the profile, so we're going to return it

            # We need to check if the requesting user is the same as the requested user

            if data["uid"] == uid_requesting:
                # The requesting user is the same as the requested user, so we'll return all the data
                return {"returnCode": 0, "message": "success", "data": data}
            else:
                # The requesting user is not the same as the requested user, so we'll return only the public data
                # as data will contain all the data for the requested user, we need to remove items where public is marked 0
                #! TODO: Figure out how to remove private data before returning. For now, we'll just return all the data.

                return {"returnCode": 0, "message": "success", "data": data}
            # return {"returnCode": 0, "message": "success", "data": data}
        else:
            # We didn't find the profile, so we're going to return an error
            return {"returnCode": 1, "message": "Profile not found"}
    except Exception as e:
        print(f"\nError retrieving profile: {e}\n")
        return {"returnCode": 1, "message": "Error retrieving profile"}


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


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
        logging.debug(f"\nReceived request: {request}\n")
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "setUsername":
                response = setUsername(request["username"], request["uid"])
            case "updateProfile":
                response = updateProfile(
                    request["uid"],
                    request["profile_field"],
                    request["field_data"],
                    request["privacy"],
                )
            case "loadProfile":
                response = load_profile(request["username"], request["uid"])
            case "this":
                print(f"\n Received a request to \n")
                response = "none"
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


creds = pika.PlainCredentials(username=PRO_USER, password=PRO_PASS)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=PRO_HOST,
        port=5672,
        credentials=creds,
        virtual_host=PRO_VHOST,
        heartbeat=0,
    )
)

channel = connection.channel()
channel.queue_declare(queue=PRO_QUEUE, durable=True)
channel.queue_bind(exchange=PRO_EXCHANGE, queue=PRO_QUEUE)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=PRO_QUEUE, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
