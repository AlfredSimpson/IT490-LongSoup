#!/bin/bash

# Check if RabbitMQ server is already running
if sudo systemctl is-active --quiet rabbitmq-server; then
    echo "RabbitMQ is already running."
else
    # Start RabbitMQ server
    sudo systemctl start rabbitmq-server
    echo "RabbitMQ is up and running!"
fi


#  Note: we'll want to use chmod +x rabbit.sh to make the script executable, and then we should be okay.