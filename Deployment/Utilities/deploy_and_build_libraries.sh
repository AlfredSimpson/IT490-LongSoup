#!/bin/bash

# This script is used to deploy and build the libraries for the project.
# It should read from library_reqs.txt and install the libraries listed there.

exec python3 -m pip install -r library_reqs.txt
