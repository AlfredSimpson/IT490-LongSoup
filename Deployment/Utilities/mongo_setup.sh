#!/bin/bash

sudo apt-get install gnupg curl -y

curl -fsSL https://pgp.mongodb.com/server-4.4.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-4.4.gpg \
   --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-4.4.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list

sudo apt-get update -y
# This is required so taht we can install the correct version of libssl1.1 that mongo uses
echo "deb http://security.ubuntu.com/ubuntu focal-security main" | sudo tee /etc/apt/sources.list.d/focal-security.list

sudo apt-get update

sudo apt-get install libssl1.1 -y
# Now we can remove it
sudo rm /etc/apt/sources.list.d/focal-security.list

sudo apt-get update
# Finally install the moving parts.
sudo apt-get install -y mongodb-org=4.4.25 mongodb-org-server=4.4.25 mongodb-org-shell=4.4.25 mongodb-org-mongos=4.4.25 mongodb-org-tools=4.4.25

echo "Setting hold status on packages to prevent upgrades to non working versions"
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections

sudo systemctl start mongod

echo "MongoDB should be live."