import pika, mysql.connector, os, sys, json


# Function to perform login
def do_login(username, password):
    return True

def do_validate(request['sessionId']):
    return True

# Define a callback function for processing requests
def request_processor(ch, method, properties, body):
    print("Received request")
    request = eval(body.decode("utf-8"))

    if "type" not in request:
        response = "ERROR: unsupported message type"
    else:
        request_type = request["type"]
        if request_type == "login":
            response = do_login(request["username"], request["password"])
        elif request_type == "validate_session":
            response = do_validate(request["sessionId"])
        else:
            response = {
                "returnCode": "0",
                "message": "Server received request and processed",
            }

    # Send the response back to the client
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=str(response),
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
