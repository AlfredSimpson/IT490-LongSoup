#!/bin/bash

# Note, run as sudo only

sudo apt-get update;
sudo apt-get install virtualbox-guest-x11 -y;

sudo VBoxClient --clipboard;

echo "Clipboard ready for use again...";

# Note - this was created only because Ubuntu keeps disabling shared clipboard.