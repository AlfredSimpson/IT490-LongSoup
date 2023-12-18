#!/bin/bash

#Check if RabbitMQ is running
if ! is_process_running "rabbitmq-server"; then
    echo "RabbitMQ server is not running. Restarting..."
    systemctl restart rabbitmq-server
    sleep 15
fi

#Checks if procedural_data_script.py is running
if ! is_process_running StoreDMZtoDB.py; then
    echo "StoreDMZtoDB is not running. Restarting..."
        if is_process_running "rabbit-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl restart rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl restart rabbitmq-server
            sleep
        fi

    python /home/david/Desktop/IT490-LongSoup/DB/DMZ_Testing/StoreDMZtoDB.py &
    sleep 2
fi

echo "StoreDMZtoDB execution complete."