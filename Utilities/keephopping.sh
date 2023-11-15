#!/bin/bash

# Function to check if a process is running
is_process_running() {
    pgrep -f "$1" > /dev/null
}

# Check if RabbitMQ server is running
if ! is_process_running "rabbitmq-server"; then
    echo "RabbitMQ server is not running. Restarting..."
    systemctl restart rabbitmq-server
    sleep 15
fi

# Check if DBWorker.py is running
if ! is_process_running "DBWorker.py"; then
    echo "DBWorker.py is not running. Restarting..."
        if is_process_running "rabbitmq-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl restart rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl restart rabbitmq-server
            sleep 15
        
        fi

    python /home/alfred/Desktop/IT490-LongSoup/DB/DBWorker.py &
    sleep 2
fi

# Check if DBSpotWorker.py is running
if ! is_process_running "DBSpotWorker.py"; then
    echo "DBSpotworker.py failed... Restarting..."
        if is_process_running "rabbitmq-server"; then
            echo "RabbitMQ server is running. Restarting..."
            systemctl start rabbitmq-server
            sleep 15; else
            echo "RabbitMQ server is not running. Attempting to restart..."
            systemctl start rabbitmq-server
            sleep 15
        fi
    python3 /home/alfred/Desktop/IT490-LongSoup/DB/DBSpotWorker.py &
    sleep 2
fi

echo "Script execution complete."
