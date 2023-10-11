import pika, mysql.connector, os, sys, json
import LongDB


# Function to perform login
def do_login(useremail, password):
    # Connect to the database
    db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    # Validate the user - consider adding a try catch.
    result = db.auth_user(table="users", useremail=useremail, password=password)
    if result:
        return {"returnCode": "0", "message": "Login successful"}
    else:
        print("And here we see it fails")
        return "ERROR: Invalid username/password"


def do_register(useremail, password):
    """
    do_register takes useremail and password as arguments and attempts to register the user.
    It returns a message indicating whether the registration was successful or not.
    However, it does not log the user in.
    Also, the password is not yet hashed.
    TODO: hash the password
    """

    # Connect to the database
    db = LongDB.LongDB("localhost", "example", "exampl3!", "tester")
    # See if the user exists already
    exists = db.user_exists_email(useremail)
    print(exists)
    if exists:
        e = {"ERROR": "User already exists"}
        return e
    else:
        try:
            result = db.add_user(table="users", useremail=useremail, password=password)
            if result:
                return {"returnCode": "0", "message": "Registration successful"}
            else:
                print("And here we see it fails")
                return "ERROR: Invalid username/password"
        except:
            print("Error adding user to database")
            return "ERROR: Unable to add user to database"


def return_error(ch, method, properties, body, msg):
    ch.basic_public(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


def do_validate(sessionId):
    pass


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
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f'incoming request: {request}')
    if "type" not in request:
        print(f'{request}')
        response = "ERROR: unsupported message type"
    else:
        request_type = request["type"]
        if request_type == "login":
            response = do_login(request["useremail"], request["password"])
        elif request_type == "validate_session":
            print("Received session validation request")
            response = do_validate(request["sessionId"])
        elif request_type == "register":
            print("Received registration request")
            response = do_register(request["useremail"], request["password"])
        else:
            response = {
                "returnCode": "0",
                "message": "Server received request and processed",
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
