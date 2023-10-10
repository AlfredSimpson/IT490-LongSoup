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
    if "type" not in request:
        response = "ERROR: unsupported message type"
    else:
        request_type = request["type"]
        if request_type == "Login":
            response = do_login(request["useremail"], request["password"])
        elif request_type == "validate_session":
            print("Received session validation request")
            response = do_validate(request["sessionId"])
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
