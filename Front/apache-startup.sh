#!/bin/bash

echo "reloading and restarting apache";

sudo systemctl reload apache2;

sudo systemctl restart apache2;

echo "Apache reloaded and restarted If issues persist, check the logs.";