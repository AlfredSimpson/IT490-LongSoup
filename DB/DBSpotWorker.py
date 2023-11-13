import pika
import os, sys, json, random
import datetime
import requests
import pymongo
import logging
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


load_dotenv()

# spotify rabbitmq stuff
spotHost = os.getenv("SPOT_HOST")
spotPort = os.getenv("SPOT_PORT")
spotUser = os.getenv("SPOT_USER")
spotPass = os.getenv("SPOT_PASS")
spotQueue = os.getenv("SPOT_QUEUE")
spotVhost = os.getenv("SPOT_VHOST")
spotExchange = os.getenv("SPOT_EXCHANGE")

# Mongo creds
maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")
maindbhost = os.getenv("MONGO_HOST")

# Spotify creds
spotClientID = os.getenv("SPOTIFY_CLIENT_ID")
spotClientSecret = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

# Connect to MongoDB

myclient = pymongo.MongoClient(
    "mongodb://%s:%s@localhost:27017/cgs" % (maindbuser, maindbpass)
)
db = myclient[maindb]


def spotQuery(uid, query_type, by_type, query, limit=10):
    # First, check our database to see if we have the query stored already
    # If we do, return the query
    # If we don't, query the Spotify API and store the result in the database
    # Return the query

    # We start by querying the db by uid to see if the user has an access token
    # If they do, we use that access token to query the Spotify API
    # If they don't, we use the client credentials flow to query the Spotify API
    try:
        results = db.users.find_one({"uid": uid})
        print(f"\nResults: {results}\n")

    except Exception as e:
        print("\nNo user found in db\n")
        results = None
        return {"returnCode": 1, "message": "This did not go as planned"}

    print(f"\nResults: {results}\n")
    if results:
        if "access_token" in results:
            access_token = results["access_token"]
            print(f"\nFound access token in db: {access_token}\n")
        else:
            print("\nNo access token found in db\n")
            access_token = None
            return {
                "returnCode": 1,
                "message": "This did not go as planned - No access token!",
            }
    else:
        print("\nNo user found in db\n")
        access_token = None
    if by_type == "anything":
        by_type = ""

    query = query_type + "%3A" + query
    print(f"\nQuery: {query}\n")

    access_token = results["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        SPOTIFY_API_BASE_URL + "/search?q=" + query + "&type=" + query_type,
        headers=headers,
    )
    formatted_response = response.json()
    print(f"\nFormatted response: {formatted_response}\n")
    # We need to clean the data and then return it - issue here is that each type might return different things...
    return {"returnCode": 0, "message": formatted_response}


def return_error():
    pass


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
        logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        # iterate over all key value pairs in the request
        for key, value in request.items():
            print(f"\nKey: {key}\n")
            print(f"\nValue: {value}\n")
            # if value == "":
            #     print(f"\nValue is empty\n")
            #     logging.error(
            #         f"Error in value. Request received with empty value: {key}"
            #     )
            #     response = "ERROR: Empty value specified by message"
            #     return return_error(ch, method, properties, body, response)
            # else:
            #     print(f"\nValue is not empty\n")
            #     logging.debug(f"\nValue is not empty: {value}\n")
            #     response = "ERROR: No value specified by message"

        match request["type"]:
            case "spot_query":
                response = spotQuery(
                    request["uid"],
                    request["queryT"],
                    request["query"],
                    request["by"],
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


vHost = spotVhost
queue2 = spotQueue
exchange2 = spotExchange
creds = pika.PlainCredentials(username="longsoup", password="puosgnol")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.68.65", port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print("\n [*] Waiting for spotify API requests. To exit, press Ctrl+C\n")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
