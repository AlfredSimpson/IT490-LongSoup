import pika, mysql.connector

vHost = "tempHost"
queue2 = "tempQueue"
exchange2 = "tempExchange"
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="192.168.68.65", virtual_host=vHost)
)

channel = connection.channel()

channel.queue_declare(queue=queue2, durable=True)

channel.queue_bind(exchange=exchange2, queue=queue2)

print(" [*] Waiting for a message from the webserver. To exit, press Ctrl+C")


def callback(ch, method, properties, body):
    print(f"[x] Received {body.decode()}")

    print("[x] Sending a message back. Done?")

    ch.basic_ack(deliver_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)

channel.basic_consume(queue=queue2, on_message_callback=callback)
channel.basic_publish(exchange=exchange2, routing_key=queue2, body="It's me")
channel.start_consuming()