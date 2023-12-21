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

# loggingFile = "/home/alfred/Desktop/dbSpotWorker.log"
# logging.basicConfig(filename=loggingFile, level=logging.DEBUG)

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

""" Example of the data we're going to be receiving from the client"""

{
    "album": {
        "album_type": "album",
        "artists": [
            {
                "external_urls": {
                    "spotify": "https://open.spotify.com/artist/1jeYbk5eqo6wgsQPjLeU5w"
                },
                "href": "https://api.spotify.com/v1/artists/1jeYbk5eqo6wgsQPjLeU5w",
                "id": "1jeYbk5eqo6wgsQPjLeU5w",
                "name": "Daniel Johnston",
                "type": "artist",
                "uri": "spotify:artist:1jeYbk5eqo6wgsQPjLeU5w",
            }
        ],
        "available_markets": [
            "AR",
            "AU",
            "AT",
            "BE",
            "BO",
            "BR",
            "BG",
            "CA",
            "CL",
            "CO",
            "CR",
            "CY",
            "CZ",
            "DK",
            "DO",
            "DE",
            "EC",
            "EE",
            "SV",
            "FI",
            "FR",
            "GR",
            "GT",
            "HN",
            "HK",
            "HU",
            "IS",
            "IE",
            "IT",
            "LV",
            "LT",
            "LU",
            "MY",
            "MT",
            "MX",
            "NL",
            "NZ",
            "NI",
            "NO",
            "PA",
            "PY",
            "PE",
            "PH",
            "PL",
            "PT",
            "SG",
            "SK",
            "ES",
            "SE",
            "CH",
            "TW",
            "TR",
            "UY",
            "US",
            "GB",
            "AD",
            "LI",
            "MC",
            "ID",
            "JP",
            "TH",
            "VN",
            "RO",
            "IL",
            "ZA",
            "SA",
            "AE",
            "BH",
            "QA",
            "OM",
            "KW",
            "EG",
            "MA",
            "DZ",
            "TN",
            "LB",
            "JO",
            "PS",
            "IN",
            "BY",
            "KZ",
            "MD",
            "UA",
            "AL",
            "BA",
            "HR",
            "ME",
            "MK",
            "RS",
            "SI",
            "KR",
            "BD",
            "PK",
            "LK",
            "GH",
            "KE",
            "NG",
            "TZ",
            "UG",
            "AG",
            "AM",
            "BS",
            "BB",
            "BZ",
            "BT",
            "BW",
            "BF",
            "CV",
            "CW",
            "DM",
            "FJ",
            "GM",
            "GE",
            "GD",
            "GW",
            "GY",
            "HT",
            "JM",
            "KI",
            "LS",
            "LR",
            "MW",
            "MV",
            "ML",
            "MH",
            "FM",
            "NA",
            "NR",
            "NE",
            "PW",
            "PG",
            "WS",
            "SM",
            "ST",
            "SN",
            "SC",
            "SL",
            "SB",
            "KN",
            "LC",
            "VC",
            "SR",
            "TL",
            "TO",
            "TT",
            "TV",
            "VU",
            "AZ",
            "BN",
            "BI",
            "KH",
            "CM",
            "TD",
            "KM",
            "GQ",
            "SZ",
            "GA",
            "GN",
            "KG",
            "LA",
            "MO",
            "MR",
            "MN",
            "NP",
            "RW",
            "TG",
            "UZ",
            "ZW",
            "BJ",
            "MG",
            "MU",
            "MZ",
            "AO",
            "CI",
            "DJ",
            "ZM",
            "CD",
            "CG",
            "IQ",
            "LY",
            "TJ",
            "VE",
            "ET",
            "XK",
        ],
        "external_urls": {
            "spotify": "https://open.spotify.com/album/24cxJPhtyRyITkV9VEt4E9"
        },
        "href": "https://api.spotify.com/v1/albums/24cxJPhtyRyITkV9VEt4E9",
        "id": "24cxJPhtyRyITkV9VEt4E9",
        "images": [
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab67616d0000b2737adb75a590be058c199fd923",
                "width": 640,
            },
            {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67616d00001e027adb75a590be058c199fd923",
                "width": 300,
            },
            {
                "height": 64,
                "url": "https://i.scdn.co/image/ab67616d000048517adb75a590be058c199fd923",
                "width": 64,
            },
        ],
        "name": "Welcome to My World",
        "release_date": "2006-04-18",
        "release_date_precision": "day",
        "total_tracks": 22,
        "type": "album",
        "uri": "spotify:album:24cxJPhtyRyITkV9VEt4E9",
    },
    "artists": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/1jeYbk5eqo6wgsQPjLeU5w"
            },
            "href": "https://api.spotify.com/v1/artists/1jeYbk5eqo6wgsQPjLeU5w",
            "id": "1jeYbk5eqo6wgsQPjLeU5w",
            "name": "Daniel Johnston",
            "type": "artist",
            "uri": "spotify:artist:1jeYbk5eqo6wgsQPjLeU5w",
        }
    ],
    "available_markets": [
        "AR",
        "AU",
        "AT",
        "BE",
        "BO",
        "BR",
        "BG",
        "CA",
        "CL",
        "CO",
        "CR",
        "CY",
        "CZ",
        "DK",
        "DO",
        "DE",
        "EC",
        "EE",
        "SV",
        "FI",
        "FR",
        "GR",
        "GT",
        "HN",
        "HK",
        "HU",
        "IS",
        "IE",
        "IT",
        "LV",
        "LT",
        "LU",
        "MY",
        "MT",
        "MX",
        "NL",
        "NZ",
        "NI",
        "NO",
        "PA",
        "PY",
        "PE",
        "PH",
        "PL",
        "PT",
        "SG",
        "SK",
        "ES",
        "SE",
        "CH",
        "TW",
        "TR",
        "UY",
        "US",
        "GB",
        "AD",
        "LI",
        "MC",
        "ID",
        "JP",
        "TH",
        "VN",
        "RO",
        "IL",
        "ZA",
        "SA",
        "AE",
        "BH",
        "QA",
        "OM",
        "KW",
        "EG",
        "MA",
        "DZ",
        "TN",
        "LB",
        "JO",
        "PS",
        "IN",
        "BY",
        "KZ",
        "MD",
        "UA",
        "AL",
        "BA",
        "HR",
        "ME",
        "MK",
        "RS",
        "SI",
        "KR",
        "BD",
        "PK",
        "LK",
        "GH",
        "KE",
        "NG",
        "TZ",
        "UG",
        "AG",
        "AM",
        "BS",
        "BB",
        "BZ",
        "BT",
        "BW",
        "BF",
        "CV",
        "CW",
        "DM",
        "FJ",
        "GM",
        "GE",
        "GD",
        "GW",
        "GY",
        "HT",
        "JM",
        "KI",
        "LS",
        "LR",
        "MW",
        "MV",
        "ML",
        "MH",
        "FM",
        "NA",
        "NR",
        "NE",
        "PW",
        "PG",
        "WS",
        "SM",
        "ST",
        "SN",
        "SC",
        "SL",
        "SB",
        "KN",
        "LC",
        "VC",
        "SR",
        "TL",
        "TO",
        "TT",
        "TV",
        "VU",
        "AZ",
        "BN",
        "BI",
        "KH",
        "CM",
        "TD",
        "KM",
        "GQ",
        "SZ",
        "GA",
        "GN",
        "KG",
        "LA",
        "MO",
        "MR",
        "MN",
        "NP",
        "RW",
        "TG",
        "UZ",
        "ZW",
        "BJ",
        "MG",
        "MU",
        "MZ",
        "AO",
        "CI",
        "DJ",
        "ZM",
        "CD",
        "CG",
        "IQ",
        "LY",
        "TJ",
        "VE",
        "ET",
        "XK",
    ],
    "disc_number": 1,
    "duration_ms": 311546,
    "explicit": False,
    "external_ids": {"isrc": "USA370567875"},
    "external_urls": {
        "spotify": "https://open.spotify.com/track/41mErQhqRBmHD41YhChsUB"
    },
    "href": "https://api.spotify.com/v1/tracks/41mErQhqRBmHD41YhChsUB",
    "id": "41mErQhqRBmHD41YhChsUB",
    "is_local": False,
    "name": "Story of an Artist",
    "popularity": 44,
    "preview_url": "https://p.scdn.co/mp3-preview/227ceba354e8692f1f45b9608f6fb57c57e43813?cid=0333477c29da440c828ede4dc2eb6747",
    "track_number": 20,
    "type": "track",
    "uri": "spotify:track:41mErQhqRBmHD41YhChsUB",
}


###################################
#
#  All of the functions below are used to clean the data we get from the Spotify API.
#
###################################


def cleanTrackData(results):
    """Take in a JSON object from the Spotify API and clean it up for storage in the database, as well as for sending back to the client.
    It should return only the track name, artist, spotify url.

    Args:
        data (JSON): JSON Object from the Spotify API gathered after requesting tracks.
    """
    # Take the data, and pull the track name, artist, and spotify url.
    tracks = results["tracks"]["items"]

    # For each item in tracks, store it in a new cgs table called "rawSpotifyTracks".
    try:
        db.rawSpotifyTracks.insert_many(tracks)
    except Exception as e:
        print("error", e)

    # print(f"Tracks displaying as follows: {tracks}")
    data = {"query_results": []}
    for i in tracks:
        name = i["name"]
        artist = i["artists"][0]["name"]
        url = i["external_urls"]["spotify"]
        id_num = i["id"]
        data["query_results"].append(
            {"name": name, "artist": artist, "url": url, "id": id_num}
        )
    return data


def cleanAlbumData(data):
    """Take in a JSON object from the Spotify API and clean it up for storage in the database, as well as for sending back to the client.
    It should return only the album name, artist, spotify url.

    Args:
        data (JSON): JSON Object from the Spotify API gathered after requesting albums.
    """
    # Take the data, and pull the album name, artist, and spotify url.
    albums = data["albums"]["items"]
    try:
        db.rawSpotifyAlbums.insert_many(albums)
    except Exception as e:
        print("error", e)

    data = {"query_results": []}
    for i in albums:
        name = i["name"]
        artist = i["artists"][0]["name"]
        url = i["external_urls"]["spotify"]
        id_num = i["id"]
        data["query_results"].append(
            {"name": name, "artist": artist, "url": url, "id": id_num}
        )
    return data


def storeGenres(artist, genres, id):
    """storeGenres takes in the genres from a query, checks to see if they're already in the database, and if they're not, stores them in the database."""
    # Loop through each genre in the list
    for genre in genres:
        # Check if the genre already exists in the database
        existing_genre = db.spotifyGenres.find_one({"genre": genre})

        if existing_genre:
            # Check if the artist is already in the genre
            if any(a["name"] == artist for a in existing_genre["artists_in_genre"]):
                # Artist already exists, do nothing
                continue
            else:
                # Artist doesn't exist in the genre, add them
                db.spotifyGenres.update_one(
                    {"genre": genre},
                    {"$addToSet": {"artists_in_genre": {"name": artist, "id": id}}},
                )
        else:
            # Genre doesn't exist, create a new document
            new_genre_document = {
                "genre": genre,
                "artists_in_genre": [{"name": artist, "id": id}],
            }
            db.spotifyGenres.insert_one(new_genre_document)

    return True


def cleanArtistData(data):
    """Take in a JSON object from the Spotify API and clean it up for storage in the database, as well as for sending back to the client.
    It should return only the artist name, spotify url.

    Args:
        data (JSON): JSON Object from the Spotify API gathered after requesting artists.
    """
    # Take the data, and pull the artist name, and spotify url.
    artists = data["artists"]["items"]
    try:
        db.rawSpotifyArtists.insert_many(artists)
    except Exception as e:
        print("error", e)
    data = {"query_results": []}
    for i in artists:
        name = i["name"]
        genres = i[
            "genres"
        ]  # Not actually sure if this will work. Limiting it to just one genre for now.
        url = i["external_urls"]["spotify"]
        id_num = i["id"]
        storeGenres(name, genres, id_num)
        data["query_results"].append(
            {
                "name": name,
                "genres": genres,
                "url": url,
                "id": id_num,
            }
        )
    return data


def spotQuery(uid, query_type, query, by_type, limit=10):
    """spotQuery takes in a query, and returns the results of that query from the Spotify API.

    Args:
        uid (int): The user requesting the data. Required to get the access token.
        query_type (string): The type of query we're making. Are we looking for an artist, a track, or an album?
        query (string): What are we looking for in query_type? Do we want an artist in particular, or a track, or an album?
        by_type (string): And do we want to find the query by another type? For example, if we're looking for an album, do we want to find it by a particular artist?
        limit (int, optional): _description_. Defaults to 10.

    Returns:
        _type_: _description_
    """

    # First, check our database to see if we have the query stored already
    # If we do, return the query
    # If we don't, query the Spotify API and store the result in the database
    # Return the query

    # We start by querying the db by uid to see if the user has an access token
    # If they do, we use that access token to query the Spotify API
    # If they don't, we use the client credentials flow to query the Spotify API
    try:
        results = db.users.find_one({"uid": uid})
        # print(f"\nResults: {results}\n")

    except Exception as e:
        print("\nNo user found in db\n")
        results = None
        return {"returnCode": 1, "message": "This did not go as planned"}

    # print(f"\nResults: {results}\n")
    if results:
        if "access_token" in results:
            access_token = results["access_token"]
            # print(f"\nFound access token in db: {access_token}\n")
        else:
            print("\n[ERROR] No access token found in db\n")
            # logging.debug(f"[ERROR] Could not find access token in db for user {uid}")
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
    # If "" we will need to pass a different query style... right now it's "":query
    query_1 = by_type + "%3A" + query
    # Find me an artist by this query param.

    access_token = results["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        SPOTIFY_API_BASE_URL
        + "/search?q="
        + query_1
        + "&type="
        + query_type
        + "&limit="
        + str(limit),
        headers=headers,
    )
    response = response.json()
    # For each response in response, let's store it in our database as "spotifyUncleaned"
    # We'll also need to store the query type, and the query itself.

    print(response)
    # We need to clean the data and then return it - issue here is that each type might return different things...

    # With the data gathered, we can call one of the cleaning functions based on the query_type.
    if query_type == "track":
        returnType = "track"
        response = cleanTrackData(response)
    elif query_type == "album":
        returnType = "album"
        response = cleanAlbumData(response)
    elif query_type == "artist":
        returnType = "artist"
        response = cleanArtistData(response)
    else:
        #! We should do error handling here... but for now, we'll just return the response.
        returnType = "unknown"
        response = response  # Do nothing else.

    return {"returnCode": 0, "message": response, "returnType": returnType}

def create_playlist(uid):
    """
    This function creates a new playlist for a Spotify user
    """
    try:
        # Fetch user data from the database
        user_data = db.users.find_one({"uid": uid})

        if not user_data or "access_token" not in user_data:
            return {
                "returnCode": 1,
                "message": "User does not exist or no access token found",
            }

        access_token = user_data["access_token"]
        print("Access token: " + access_token)
        # Get the Spotify user id
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(SPOTIFY_API_BASE_URL + "/me", headers=headers)
        user_info = user_info_response.json()
        print(user_info)

        if "id" not in user_info:
            return {
                "returnCode": 1,
                "message": "Failed to get Spotify user id.",
            }

        user_id = user_info["id"]
        print(user_id)

        # Create a new playlist info to post

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        req_url = SPOTIFY_API_BASE_URL + f"/users/{user_id}/playlists"
        playlist_data = {
            "name": "New CGS Playlist",
            "description": "your shiny new playlist",
            "public": True,  # Set to True if you want the playlist to be public
        }
        response = requests.post(req_url, headers=headers, json=playlist_data)
        print(response)

        if response.status_code == 201:
            print("creation works")
            # Extracting playlist ID from the response
            playlist_uri = response.json().get("id")

            # Add playlist URI to UserPlaylists collection
            db.UserPlaylists.update_one(
                {"uid": uid},
                {"$push": {"playlists": {"playlist_uri": playlist_uri}}},
                upsert=True,
            )

            return {
                "returnCode": 0,
                "message": "Playlist created successfully",
                "playlist_uri": playlist_uri,
            }
        else:
            return {
                "returnCode": 1,
                "message": f"Failed to create the playlist. Status: {response.status_code}",
            }
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return {
            "returnCode": 1,
            "message": "An error occurred while creating the playlist.",
        }


# test
# playlist_creation_result = create_playlist(uid=0)
# print(playlist_creation_result)

def addToPlaylist(uid, track_id):

    """
    This function adds a song to an existing playlist or creates a new playlist for a Spotify user
    """
    try:
        # Fetch user playlists from the database
        user_playlists = db.UserPlaylists.find_one({"uid": uid})

        if user_playlists:
            # selects the first playlist in the list (most recent)
            playlist_uri = user_playlists["playlists"][0]["playlist_uri"]
        else:
            # Call our previous create_playlist function passing uid
            create_playlist_result = create_playlist(uid)

            if create_playlist_result["returnCode"] == 0:
                playlist_uri = create_playlist_result["playlist_uri"]
            else:
                return create_playlist_result

        # Fetch user data from the database
        user_data = db.users.find_one({"uid": uid})

        if not user_data or "access_token" not in user_data:
            return {
                "returnCode": 1,
                "message": "User does not exist or no access token found",
            }

        access_token = user_data["access_token"]

        # Get the Spotify user id
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(SPOTIFY_API_BASE_URL + "/me", headers=headers)
        user_info = user_info_response.json()

        if "id" not in user_info:
            return {
                "returnCode": 1,
                "message": "Failed to get Spotify user id.",
            }

        user_id = user_info["id"]

        # Add a song to the existing or newly created playlist
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        req_url = SPOTIFY_API_BASE_URL + f"/playlists/{playlist_uri}/tracks"

        playlist_data = {
            "uris": [f"spotify:track:{track_id}"],
        }
        response = requests.post(req_url, headers=headers, json=playlist_data)

        if response.status_code == 201:
            return {
                "returnCode": 0,
                "message": "Song added to the playlist successfully",
            }
        else:
            return {
                "returnCode": 1,
                "message": f"Failed to add the song to the playlist. Status: {response.status_code}",
            }
    except Exception as e:
        print(f"Error adding song to playlist: {e}")
        return {
            "returnCode": 1,
            "message": "An error occurred while adding the song to the playlist.",
        }


# test
# add_to_playlist_result = addToPlaylist(0, "70LcF31zb1H0PyJoS1Sx1r")
# print(add_to_playlist_result)


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
        # iterate over all key value pairs in the request
        # for key, value in request.items():
        # print(f"\nKey: {key}\n")
        # print(f"\nValue: {value}\n")
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
            case "add_to_playlist":
                try:
                    response = addToPlaylist(
                        request["uid"],
                        request["track_id"],
                    )
                except Exception as e:
                    print(f"\nError adding to playlist: {e}\n")
                    response = {
                        "returnCode": 1,
                        "message": "Error adding to playlist",
                    }
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
        host=spotHost, port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print("\n [*] Waiting for spotify API requests. To exit, press Ctrl+C\n")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
