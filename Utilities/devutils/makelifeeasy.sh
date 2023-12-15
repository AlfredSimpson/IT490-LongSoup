#!/bin/bash

# Install some of the necessary tools in our development.
sudo apt update && sudo apt upgrade -y
sudo apt install vim -y
sudo apt install python3-pip -y
sudo apt install python3-venv -y
sudo apt install git -y
sudo apt install curl -y
sudo apt install gnupg -y
sudo apt install net-tools -y
sudo apt install openssh-server -y