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
PROFILE_QUEUE = os.getenv("PROFILE_QUEUE")
PROFILE_EXCHANGE = os.getenv("PROFILE_EXCHANGE")
BROKER_EXCHANGE = os.getenv("BROKER_EXCHANGE")


# Primary Mongo DB
DB_PROFILES = os.getenv("DB_PROFILES")
DB_MAIN_USER = os.getenv("MONGO_USER")
DB_MAIN_PASS = os.getenv("MONGO_PASS")

# Connect to the database - we're going to use cgs_mb

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/" % (DB_MAIN_USER, DB_MAIN_PASS)
)

db = myclient[DB_PROFILES]


def setUsername(username, uid):
    """# setUsername
    This function sets the username for the user with the given uid.

    Args:
        username (_type_): _description_
        uid (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        db.profiles.update_one({"uid": uid}, {"$set": {"username": username}})
        return True
    except Exception as e:
        print(f"\nError setting username: {e}\n")
        return False


def updateProfile(uid, data, public=False):
    """# updateProfile
    This function updates the profile data for the given user.

    Args:
        username (_type_): _description_
        uid (_type_): _description_
        data (_type_): _description_

    Returns:
        _type_: _description_
    """

    try:
        if public:
            # Data is a dict containing a key (the name of the field updating) and a value (the value to update to)
            # We need to update the profile data for the given user
            # We will update the data in the database, regardless of whether public is true or false, but if it is true, we will need to note that. If it's false, we'll update the data with a public value of 0

            # We need to check if the requesting user is the same as the requested user. It should be... but, just in case, we'll check.

            if data["uid"] == uid:
                # The requesting user is the same as the requested user, so we'll update all the data
                db.profiles.update_one({"uid": uid}, {"$set": data})
            else:
                # The requesting user is not the same as the requested user, so we'll update only the public data
                return {"returnCode": 1, "message": "Error updating profile"}
        return {"returnCode": 0, "message": "success"}
    except Exception as e:
        print(f"\nError updating profile: {e}\n")
        return {"returnCode": 1, "message": "Error updating profile"}


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
                    request["username"], request["uid"], request["data"]
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


creds = pika.PlainCredentials(username=BROKER_USER, password=BROKER_PASS)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=BROKER_HOST,
        port=5672,
        credentials=creds,
        virtual_host=BROKER_VHOST,
        heartbeat=0,
    )
)

channel = connection.channel()
channel.queue_declare(queue=PROFILE_QUEUE, durable=True)
channel.queue_bind(exchange=PROFILE_EXCHANGE, queue=PROFILE_QUEUE)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=PROFILE_QUEUE, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
