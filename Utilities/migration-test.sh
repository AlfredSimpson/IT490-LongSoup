#!/bin/bash

# Destination directory (where to copy to)
destination_dir="/var/www/cgs/"

# Check if the destination directory exists, create it if not
if [ ! -d "$destination_dir" ]; then
    sudo mkdir -p "$destination_dir"
fi

# Copy all files and directories recursively from the current directory to the destination
# Note --- This currently goes to /Testing/, just remove it when we're moving back to the main.
sudo cp -r ./Testing/* "$destination_dir"

# For some reason the .inc files don't copy, so let's do them manually

#

# Change ownership of copied files and directories to the web server user. We can change this if we need or want to though.
sudo chown -R www-data:www-data "$destination_dir"

echo "Files and directories copied to $destination_dir"

echo "Confirm that the host information is correctly stored in hosts and hostname";

# Note, this should be run from the directory we have our git repo in. This will move everything to the appropriate directory