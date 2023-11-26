import pika
import os, sys, json

vHost = "deployment"
D_Q = "dep_q"
D_USER = "longsoup"
D_PASS = "puosgnol"
D_X = "dep_x"
D_HOST = "192.168.68.51"


def return_error(ch, method, properties, body, msg):
    print("\n\n Errors be here")
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(delivery_mode=2),
        body=json.dumps({"error": msg}),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def request_processor(ch, method, properties, body):
    print("Request received...")
    try:
        request = json.loads(body.decode("utf-8"))
    except:
        print("Invalid json found")
        return_error(ch, method, properties, body, "Invalid JSON")
        return
    print(f"Request coming in as {request}")
    if "type" not in request:
        return_error(ch, method, properties, body, "Invalid request type")
        return
    else:
        match request["type"]:
            case "test":
                print("test type received")
                response = {
                    "returnCode": 0,
                    "message": "Test request received and processed.",
                }
            case _:
                print("unknown type received")
                response = {
                    "returnCode": 1,
                    "message": "Request received, but no type was specified.",
                }
    print("\n[*] Received a request from a cluster. Processing request.\n")
    ch.basic_publish(
        exchange="",
        routing_key=D_Q,
        body=json.dumps(response),
    )


creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=D_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)

channel = connection.channel()
channel.queue_declare(queue=D_Q, durable=True)
channel.exchange_declare(exchange=D_X, exchange_type="direct", durable=True)
channel.queue_bind(exchange=D_X, queue=D_Q)
print("\n[*] Waiting for Deployment requests from a cluster. To exit press CTRL+C\n")
channel.basic_consume(queue=D_Q, on_message_callback=request_processor, auto_ack=True)
print("\n Awaiting requests from clusters...")
channel.start_consuming()
