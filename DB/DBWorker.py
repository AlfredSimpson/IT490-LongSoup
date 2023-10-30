import pika, mysql.connector, os, sys, json
import LongDB

# Import the spotify handler

# Spotify info

# get user top tracks
# get user recommended tracks
# get user recommended artists


# Function to perform login
def do_login(useremail, password, session_id, usercookieid):
    # Connect to the database
    # db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    db = LongDB.LongDB(
        host="localhost",
        user="longestsoup",
        password="shortS0up!",
        database="securesoupdb",
    )
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
        return {
            "returnCode": "0",
            "message": "Login successful",
            "sessionValid": True,
            "name": name,
            "currentTop": current_top,
            "recommendedTracks": recommended_tracks,
            "recommendedArtists": recommended_artists,
            "data": {
                "loggedin": True,
            },
        }
    else:
        print("And here we see it fails")
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
    TODO: hash the password
    """

    # Connect to the database
    # db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    db = LongDB.LongDB(
        host="localhost",
        user="longestsoup",
        password="shortS0up!",
        database="securesoupdb",
    )
    # See if the user exists already
    exists = db.user_exists_email(useremail)
    print(exists)
    if exists:
        e = {"ERROR": "User already exists"}
        # TODO: log this locally
        return e
    else:
        try:
            result = db.add_user(
                table="users",
                useremail=useremail,
                password=password,
                sessionid=session_id,
                usercookieid=usercookieid,
            )
            if result:
                print(
                    f"User {useremail} added to database, attempting to update userinfo next"
                )
                name = db.get_name(usercookieid)
                db.initialUpdate(useremail, first_name, last_name, spot_name)
                return {
                    "returnCode": "0",
                    "message": "Registration successful",
                    session_id: True,
                    "name": name,
                }
            else:
                print("And here we see it fails")
                return {
                    "returnCode": "1",
                    "message": "Registration failed - useremail exists",
                    session_id: False,
                }
        except:
            print("Error adding user to database")
            # TODO: log this locally, send to all
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
    # TODO: get password from justin - update appropriately
    db = LongDB.LongDB(
        host="localhost",
        user="longestsoup",
        password="shortS0up!",
        database="securesoupdb",
    )
    validity = db.validate_session(usercookieid, session_id)
    # TODO: add this to the logging system
    print(f"validate_session returned: {validity}")
    return validity


def do_logout(usercookieid, session_id):
    # Connect to the database
    db = LongDB.LongDB(
        host="localhost",
        user="longestsoup",
        password="shortS0up!",
        database="securesoupdb",
    )
    db.invalidate_session(usercookieid, session_id)
    print(f"User {usercookieid} logged out")
    return {"returnCode": "0", "message": "Logout successful"}


def request_processor(ch, method, properties, body):
    """
    The request_processor() method takes in the channel, method, properties, and body of the message.
    This method is called whenever a message is received from the web server.
    It takes the message, decodes it, and then processes it. It then sends a response back to the web server.
    """
    # Try / except added just in case bad JSON is received
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
                request["first_name"],
                request["last_name"],
                request["session_id"],
                request["usercookieid"],
                request["spot_name"],
            )
        elif request_type == "logout":
            # Handles logout requests
            print("Received logout request")
            response = do_logout(
                request["usercookieid"],
                request["session_id"],
            )
        else:
            response = {
                "returnCode": "0",
                "message": "Server received request and processed - no action taken. Unknown type",
            }

    # Send the response back to the client
    print(f"We should have a response here if we're publishing...{response}")
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
print(" [*] Waiting for a message from the webserver. To exit, press Ctrl+C")
channel.basic_consume(queue=queue2, on_message_callback=request_processor)
print(" [x] Awaiting RPC requests")
channel.start_consuming()
