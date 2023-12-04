#!/bin/bash

#Check if RabbitMQ is running
if ! is_process_running "rabbitmq-server"; then
    echo "RabbitMQ server is not running. Restarting..."
    systemctl restart rabbitmq-server
    sleep 15
fi

#Check if DMZWorker.py is working/running
if ! is_process_running DMZWorker.py; then
    echo "DMZWorker.py is not running. Restarting..."
        if is_process_running "rabbitmq-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl restart rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl restart rabbitmq-server
            sleep 15
        
        fi

    python /home/david/Desktop/IT490-LongSoup/DMZ/DMZWorkey.py &
    sleep 2
fi

echo "DMZ's script execution complete."