#!/bin/bash
# Check if the primary_ip is running
primary_ip="192.168.68.71"

# How many times to ping before giving up
ping_attempts=3

# Ping the primary_ip and send the output to /dev/null
ping -c $ping_attempts $primary_ip > /dev/null

# Check the exit code of the ping command
# If it's 0 then the ping was successful
if [ $? -eq 0 ]; then
        exit 0
else
        exit 1
fi