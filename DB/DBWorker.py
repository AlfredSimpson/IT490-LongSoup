import pika, mysql.connector, os, sys, json, random
import LongDB
import spotipy
import spotipy.util as util
import logging
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load the variables
load_dotenv()

# Set globals
global testUser
global testPass
global testDB
testUser = os.getenv("TESTSECUREUSER")
testPass = os.getenv("TESTSECUREPASS")
testDB = os.getenv("TESTSECUREDB")

# logging.basicConfig(level=logging.ERROR)
# Import the spotify handler

# Spotify info


def query_artist(artist, typebyartist=None):
    """NOTE: NOT READY FOR PROD YET, STILL IN TESTING PHASE. DOES NOT ACTUALLY RETURN ANYTHING THAT WOULD BE USEFUL OR PARSED

    Args:
        artist (_type_): _description_

    Returns:
        what the variable dictates.
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


def get_recs(
    genre="punk", valence="0.2", energy="0.7", popularity="25", fromlogin=False
):
    """get_recs takes in genre, valence, energy, and popularity as arguments and returns a list of recommended songs.

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


# def generateSimpleRecs(genre, popularity, valence):
#     client_id = os.getenv("SPOTIFY_CLIENT_ID")
#     client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
#     # redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
#     spotify_token = os.getenv("SPOTIFY_TOKEN_URL")
#     spotify_api_url = os.getenv("SPOTIFY_API_BASE_URL")

#     sp = spotipy.Spotify(
#         auth_manager=SpotifyClientCredentials(
#             client_id=client_id, client_secret=client_secret
#         )
#     )
#     genre = [genre]
#     print(genre)
#     results = sp.recommendations(
#         seed_genres=genre, limit=5, target_popularity=popularity, target_valence=valence
#     )

#     print(results)
#     return {
#         "returnCode": 0,
#         "message": "Success",
#         "gotrecs": "True",
#         "data": {
#             "loggedin": "True",
#             "recs": results,
#         },
#         "recs": results,
#     }


# Function to perform login
def do_login(useremail, password, session_id, usercookieid):
    # Connect to the database
    db = LongDB.LongDB("localhost", testUser, testPass, testDB)
    # db = LongDB.LongDB(host="localhost",user="longestsoup",password="shortS0up!",database="securesoupdb")
    # Validate the user - consider adding a try catch.
    result = db.auth_user(
        table="users",
        useremail=useremail,
        password=password,
        session_id=session_id,
        usercookieid=usercookieid,
    )

    # Initialize the spotify handler

    name = db.get_name(usercookieid)
    current_top = ""  # TODO: get user top tracks
    recommended_tracks = ""  # TODO: get user recommended tracks
    recommended_artists = ""  # TODO: get user recommended artists
    if result:
        genre = random.choice(["punk", "rock", "pop", "country", "rap", "hip-hop"])
        valence = random.uniform(0, 1)
        energy = random.uniform(0, 1)
        popularity = random.randint(0, 100)
        music = get_recs(genre, valence, energy, popularity, True)
        return {
            "returnCode": "0",
            "message": "Login successful",
            "sessionValid": "True",
            # "name": name,
            # "currentTop": current_top,
            # "recommendedTracks": recommended_tracks,
            # "recommendedArtists": recommended_artists,
            "music": music["musicdata"],
            "data": {
                "name": name[0],
                "loggedin": "True",
            },
        }
    else:
        print("\nAnd here we see it fails\n")
        return {
            "returnCode": "1",
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
    do_register takes useremail and password as arguments and attempts to register the user.
    It returns a message indicating whether the registration was successful or not.
    However, it does not log the user in.
    Also, the password is not yet hashed.
    """
    # Connect to the database
    db = LongDB.LongDB("localhost", testUser, testPass, testDB)
    # db = LongDB.LongDB(host="localhost",user="longestsoup",password="shortS0up!",database="securesoupdb",)
    # See if the user exists already
    exists = db.user_exists_email(useremail)
    print(f"\nUser email exists? {exists}")
    if exists:
        print("\n\tUser already exists\n")
        e = {"ERROR": "User already exists"}
        return e
    else:
        try:
            print(f'\nAttempting to add user "{useremail}" to database\n')
            result = db.add_user(
                table="users",
                useremail=useremail,
                password=password,
                sessionid=session_id,
                usercookieid=usercookieid,
            )
            if result:
                print(
                    f"\nUser {useremail} added to database, attempting to update userinfo next\n"
                )
                db.initialUpdate(useremail, first_name, last_name, spot_name)
                music = get_recs(fromlogin=True)
                music = music["musicdata"]
                return {
                    "returnCode": "0",
                    "message": "Registration successful",
                    "data": {
                        "loggedin": "True",
                        "name": first_name,
                        "sessionValid": "True",
                    },
                    "music": music,
                }
            else:
                print("\nAnd here we see it fails\n")
                return {
                    "returnCode": "1",
                    "message": "Registration failed - useremail exists",
                    session_id: False,
                }
        except:
            print("\nError adding user to database\n")
            logging.error("Error adding user to database")
            return "ERROR: Unable to add user to database"


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


def do_validate(usercookieid, session_id):
    # This takes in the sessionID and validates it by checking the database. If the sessionTable shows that the session is valid for the user, then it returns a boolean True. Otherwise, it returns a boolean False.
    # Connect to the database
    # db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    global testUser
    global testPass
    global testDB
    db = LongDB.LongDB("localhost", testUser, testPass, testDB)
    # db = LongDB.LongDB(host="localhost",user="longestsoup",password="shortS0up!",database="securesoupdb",)
    validity = db.validate_session(usercookieid, session_id)
    # TODO: add this to the logging system
    print(f"\nvalidate_session returned: {validity}\n")
    return validity


def do_logout(usercookieid, session_id):
    # Connect to the database
    db = LongDB.LongDB("localhost", testUser, testPass, testDB)
    # db = LongDB.LongDB(host="localhost",user="longestsoup",password="shortS0up!",database="securesoupdb",)
    db.invalidate_session(usercookieid, session_id)
    print(f"User {usercookieid} logged out")
    return {"\nreturnCode": "0", "message": "Logout successful\n"}


def request_processor(ch, method, properties, body):
    """
    The request_processor() method takes in the channel, method, properties, and body of the message.
    This method is called whenever a message is received from the web server.
    It takes the message, decodes it, and then processes it. It then sends a response back to the web server.
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
        request_type = request["type"]
        if request_type == "login":
            # Handles login attempts
            response = do_login(
                request["useremail"],
                request["password"],
                request["session_id"],
                request["usercookieid"],
            )
        elif request_type == "validate_session":
            # Handles session validation requests
            print("Received session validation request")
            response = do_validate(request["usercookieid"], request["sessionId"])
        elif request_type == "register":
            # Handles registration requests
            print("Received registration request")
            response = do_register(
                request["useremail"],
                request["password"],
                request["session_id"],
                request["usercookieid"],
                request["spot_name"],
                request["first_name"],
                request["last_name"],
            )
        elif request_type == "logout":
            # Handles logout requests
            print("Received logout request")
            response = do_logout(
                request["usercookieid"],
                request["session_id"],
            )
        elif request_type == "simplerecs":
            # Handles simple recs from their profile page
            print("\nReceived simple recs request\n")
            response = get_recs(
                request["genre"],
                request["popularity"],
                request["valence"],
            )
        elif request_type == "byArtist":
            response = query_artist(request["artist"], request["typeOf"])
        else:
            response = {
                "returnCode": "0",
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


vHost = "tempHost"
queue2 = "tempQueue"
exchange2 = "tempExchange"
creds = pika.PlainCredentials(username="longsoup", password="puosgnol")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.68.65", port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
