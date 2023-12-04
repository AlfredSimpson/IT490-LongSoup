#!/bin/bash

#Check if RabbitMQ is running
if ! is_process_running "rabbitmq-server"; then
    echo "RabbitMQ server is not running. Restarting..."
    systemctl restart rabbitmq-server
    sleep 15
fi

#Checks if procedural_data_script.py is running
if ! is_process_running procedural_data_script.py; then
    echo "procedural_data_script is not running. Restarting..."
        if is_process_running "rabbit-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl restart rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl restart rabbitmq-server
            sleep
        fi

    python /home/david/Desktop/IT490-LongSoup/DMZ/pocedural_data_script.py &
    sleep 2
fi

echo "procedural_data_script execution complete."