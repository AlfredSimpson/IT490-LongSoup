import pika
import os, sys, json
from dotenv import load_dotenv

load_dotenv()

# This will handle messages from the out-going machine to the deployment server.
# vHost = os.getenv("DEPLOYMENT_VHOST")
# D_Q = os.getenv("DEPLOYMENT_QUEUE")
# D_X = os.getenv("DEPLOYMENT_EXCHANGE")
# D_HOST = os.getenv("DEPLOYMENT_HOST")  # The IP of the deployment server
# D_USER = os.getenv("DEPLOYMENT_USER")
# D_PASS = os.getenv("DEPLOYMENT_PASS")

vHost = "deployment"
D_Q = "dep_q"
D_USER = "longsoup"
D_PASS = "puosgnol"
D_X = "dep_x"
D_HOST = "192.168.68.51"


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange=D_X,
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(delivery_mode=2),
        body=json.dumps({"error": msg}),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def request_processor(ch, method, properties, body):
    try:
        request = json.loads(body.decode("utf-8"))
    except:
        return_error(ch, method, properties, body, "Invalid JSON")
        return
    if "type" not in request:
        return_error(ch, method, properties, body, "Invalid request type")
        return
    else:
        match request["type"]:
            case "test":
                response = {
                    "returnCode": 0,
                    "message": "Test request received and processed.",
                }
            case _:
                response = {
                    "returnCode": 1,
                    "message": "Request received, but no type was specified.",
                }

    print("\n[*] Received a request from a cluster. Processing request.\n")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        body=json.dumps(response),
    )
    pass


creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=D_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=D_Q, durable=True)
channel.queue_bind(exchange=D_X, queue=D_Q, routing_key="")
print("\n[*] Waiting for Deployment requests from a cluster. To exit press CTRL+C\n")
channel.basic_consume(queue=D_Q, on_message_callback=request_processor, auto_ack=True)
print("\n Awaiting requests from clusters...")
channel.start_consuming()
