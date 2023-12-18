#!/bin/bash

#Check if RabbitMQ is running
if ! is_process_running "rabbitmq-server"; then
    echo "RabbitMQ server is not running. Restarting..."
    systemctl restart rabbitmq-server
    sleep 15
fi

#Check if LongDMZQuery.py is working/running
if ! is_process_running LongDMZQuery.py; then
    echo "LongDMZQuery.py is not running. Restarting..."
        if is_process_running "rabbitmq-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl restart rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl restart rabbitmq-server
            sleep 15
        
        fi

    python /home/david/Desktop/IT490-LongSoup/DMZ/API_Scripts/LongDMZQuery.py &
    sleep 2
fi

echo "LongDMZQuery's script execution complete."