#!/bin/bash

# Use this as a part of a daemon to keep the clipboard active.

while true; do
    sudo VBoxClient --clipboard;
    sudo VBoxClient --draganddrop;
    sleep 60;
done

# To enable as in the daemon, see devutils subdirector