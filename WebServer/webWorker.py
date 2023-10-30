import pika, os, sys, json
from dotenv import load_dotenv


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


def request_processor(ch, method, properties, body):
    try:
        # Try to decode the body of the message
        request = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        print("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"incoming request: {request}")
    # TODO: handle incoming type
    if "type" not in request:
        print(f"{request}")
        response = "ERROR: unsupported message type"
    else:
        # Check if it's a log request, it should be.
        request_type = request["type"]
        if request_type == "log":
            logSource = request["source"]
            if logSource == "DB":
                logDate = request["date"]
                logMsg = request["log_message"]
                # TODO: add log_level?
                newlog = f"{logSource} - {logDate} - {logMsg}"
                logName = "_DB.log"
                with open(logName, "a") as logFile:
                    logFile.write(newlog)
            elif logSource == "Webserver":
                logDate = request["date"]
                logMsg = request["log_message"]
                logName = "_Web.log"
                newlog = f"{logSource} - {logDate} - {logMsg}"
                with open(logName, "a") as logFile:
                    logFile.write(newlog)
            elif logSource == "RMQ":
                logDate = request["date"]
                logMsg = request["log_message"]
                logName = "_RMQ.log"
                newlog = f"{logSource} - {logDate} - {logMsg}"
                with open(logName, "a") as logFile:
                    logFile.write(newlog)
            elif logSource == "DMZ":
                logDate = request["date"]
                logMsg = request["log_message"]
                logName = "_DMZ.log"
                newlog = f"{logSource} - {logDate} - {logMsg}"
                with open(logName, "a") as logFile:
                    logFile.write(newlog)
            else:
                logDate = request["date"]
                logMsg = request["log_message"]
                logName = "_Unknown-Origins.log"
                newlog = f"{logSource} - {logDate} - {logMsg}"
                with open(logName, "a") as logFile:
                    logFile.write(newlog)


# may need find_dotenv() inside of load_dotenv()
load_dotenv()
logHost = os.getenv("LOG_HOST")
logvHost = os.getenv("LOG_VHOST")
logX = os.getenv("LOG_EXCHANGE")
logQ = os.getenv("LOG_QUEUE")
logUser = os.getenv("LOG_USER")
logPass = os.getenv("LOG_PASS")
logPort = os.getenv("LOG_PORT")
creds = pika.PlainCredentials(username=logUser, password=logPass)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=logHost, port=logPort, credentials=creds, virtual_host=logvHost
    )
)
channel = connection.channel()
channel.exchange_declare(exchange=logX, exchange_type="fanout")
channel.queue_declare(queue=logQ, durable=True)
channel.queue_bind(exchange=logX, queue=logQ)
print(" [*] Waiting for incoming logs. To exit, press Ctrl+C")
channel.basic_consume(queue=logQ, on_message_callback=request_processor, auto_ack=True)
print(" [x] Awaiting Log Updates")
channel.start_consuming()
