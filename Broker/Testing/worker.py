#!/usr/bin/env python3
import time
import pika

vHost = "tempHost"
queue_name = "tempQueue"
exchange_name = "tempExchange"

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", virtual_host=vHost)
)
channel = connection.channel()

channel.queue_declare(queue=queue_name, durable=True)
channel.queue_bind(exchange=exchange_name, queue=queue_name)
print(" [*] Waiting for messages. To exit press CTRL+C")


def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=callback)

channel.start_consuming()
