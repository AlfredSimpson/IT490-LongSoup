"""__sumary__
    LongSpotWorker is a worker file that will run to handle spotify related messages on the queue
"""
import pika
import mysql.connector
import json
import spotipy  # The Spotify python wrapper
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util
import time
import datetime
import sys
import os
import Scopes
from dotenv import load_dotenv

import LongDB

load_dotenv()

# Load all env variables

SPOT_USER = os.getenv("SPOT_USER")
SPOT_PASS = os.getenv("SPOT_PASS")
SPOT_VHOST = os.getenv("SPOT_VHOST")
SPOT_QUEUE = os.getenv("SPOT_QUEUE")
SPOT_EXCHANGE = os.getenv("SPOT_EXCHANGE")
SPOT_PORT = os.getenv("SPOT_PORT")
SPOT_HOST = os.getenv("SPOT_HOST")

spotClient = os.getenv("SPOTIFY_CLIENT_ID")
spotSecret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotURI = os.getenv("SPOT_TEST_URI")
SP_AUTH_URL = os.getenv("SPOTIFY_AUTH_URL")
SP_TOKEN_URL = os.getenv("SPOTIFY_TOKEN_URL")
SP_API_BASE_URL = os.getenv("SPOTIFY_API_BASE_URL")


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )


def authorizeSpotify():
    """_summary_
    authorizeSpotify uses spotipy to use oAuth to authorize a user to use the spotify API
    it will process the data and return the ncessary information to the webserver so that the webserver can return that to the spotify client
    """

    sc = Scopes.Scopes()
    allScopes = f"{sc.read_collab_playlist} {sc.read_currently_playing} {sc.read_email} {sc.read_following} {sc.read_library} {sc.read_playback_state} {sc.read_private_playlists} {sc.read_recent} {sc.read_subscription} {sc.read_top} {sc.upload_img} {sc.mod_following} {sc.mod_library} {sc.mod_playback_state} {sc.mod_priv_playlist} {sc.mod_pub_playlist} {sc.mod_user_entitlements} {sc.mod_user_soa} {sc.mod_user_soa_unlink}"
    params = {
        "client_id": spotClient,
        "response_type": "code",
        "scope": allScopes,
        "redirect_uri": "http://localhost:8080/account.html",
        "show_dialog": True,
    }

    # spot = spotipy.Spotify(
    #     auth_manager=SpotifyOAuth(
    #         client_id=spotClient,
    #         client_secret=spotSecret,
    #         redirect_uri="http://localhost:8080",
    #         scope=allScopes,
    #     )
    # )
    # return response
    pass


# TODO: Fill out the request processor with necessary info
def request_processor(ch, method, properties, body):
    try:
        request = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        print("Error decoding incoming JSON")
        # TODO: save this as a log file as well
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"incoming request: {request}")
    if "type" not in request:
        print(f"{request}")
        # TODO: save this as a log file as well
        response = "ERROR: unsupported message type"
    else:
        request_type = request["type"]
        if request_type == "authorizeSpotify":
            # response = do_login(request["useremail"], request["password"])
            response = authorizeSpotify()
        elif request_type == "":
            # print("Received session validation request")
            # response = do_validate(request["sessionId"])
            pass
        elif request_type == "":
            # print("Received registration request")
            # response = do_register(
            #     request["useremail"],
            #     request["password"],
            #     request["first_name"],
            #     request["last_name"],
            # )
            pass
        else:
            response = {
                "returnCode": "0",
                "message": "Server received request and processed it successfully",
            }

    print(f"We should have a response here if we're publishing...{response}")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    # Maybe auto ack? I'm not sure. TODO: verify?
    ch.basic_ack(delivery_tag=method.delivery_tag)

    pass


# TODO: sort out auto creation of queue and assignment to spotVHOST, update rmq to reflect autodelete once done

creds = pika.PlainCredentials(username=SPOT_USER, password=SPOT_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.68.65", port=5672, credentials=creds, virtual_host=SPOT_VHOST
    )
)
channel = connection.channel()
channel.queue_declare(queue=SPOT_QUEUE, durable=True)
channel.queue_bind(exchange=SPOT_EXCHANGE, queue=SPOT_QUEUE)
print(
    " [*] Waiting for a message from the webserver from spotify requests. To exit, press Ctrl+C"
)
channel.basic_consume(queue=SPOT_QUEUE, on_message_callback=request_processor)
print(" [x] Awaiting Spotify User requests")
channel.start_consuming()
