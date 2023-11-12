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


def spotQuery(query_type, by_type, query, uid=None, limit=10):
    # First, check our database to see if we have the query stored already
    # If we do, return the query
    # If we don't, query the Spotify API and store the result in the database
    # Return the query

    # We start by querying the db by uid to see if the user has an access token
    # If they do, we use that access token to query the Spotify API
    # If they don't, we use the client credentials flow to query the Spotify API

    results = db.users.find_one({"uid": uid})

    print(f"\nResults: {results}\n")
    # if results:
    #     if "access_token" in results:
    #         access_token = results["access_token"]
    #         print(f"\nFound access token in db: {access_token}\n")
    #     else:
    #         print("\nNo access token found in db\n")
    #         access_token = None
    # else:
    #     print("\nNo user found in db\n")
    #     access_token = None
    if by_type == "anything":
        by_type = ""

    query = by_type + "%3A" + query
    print(f"\nQuery: {query}\n")

    access_token = results["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        SPOTIFY_API_BASE_URL + "/search?q=" + query, headers=headers
    )
    formatted_response = response.json()
    print(f"\nFormatted response: {formatted_response}\n")

    pass


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
    print(f"\nincoming request: {request}\n")
    if "type" not in request:
        print(f"\n{request}\n")
        logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "spot_query":
                response = spotQuery(
                    request["uid"],
                    request["query_type"],
                    request["by_type"],
                    request["query"],
                )
                pass
            # case "simplerecs":
            #     response = get_recs(
            #         request["genre"],
            #         request["popularity"],
            #         request["valence"],
            #     )
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
