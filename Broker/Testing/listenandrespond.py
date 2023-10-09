import pika, mysql.connector, os, sys, json

vHost = "tempHost"
queue2 = "tempQueue"
exchange2 = "tempExchange"
creds = pika.PlainCredentials(username="test", password="test")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="192.168.1.25", port=5672, credentials=creds, virtual_host=vHost
    )
)
channel = connection.channel()
channel.queue_declare(queue=queue2, durable=True)
channel.queue_bind(exchange=exchange2, queue=queue2)
print(" [*] Waiting for a message from the webserver. To exit, press Ctrl+C")


def callback(ch, method, properties, body):
    print(f"[x] Received {body.decode()}")

    print("[x] Sending a message back. Done?")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue2, on_message_callback=callback)
# Now send a message through the queue to the websert with delivery mode 2. Delivery mode 2 means it will be saved to disk.
msg = json.JSONEncoder().encode(
    {"Type": "Login", "Username": "test", "Password": "test"}
)
channel.basic_publish(
    exchange=exchange2,
    routing_key=queue2,
    properties=pika.BasicProperties(delivery_mode=2),
    body=msg,
)

channel.start_consuming()
