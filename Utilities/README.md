# Utility Files

This directory contains utility files that are used by the other scripts in this repository. It may also include scripts that are no longer used, but were once useful.


## Contents
- Active use
  - [clipboard.sh](clipboard.sh) - This script was made because Ubuntu in VirtualBox liked to stop allowing copy and paste...
  - [keephopping.py](keephopping.py) - This script is used to keep the rabbitmq connection alive on the Backend server. It continuously checks the connection and restarts RabbitMQ if disconnected, and then restarts dependent files.
  - [rabbitmq-install.sh](rabbitmq-install.sh) - This script is used to install the rabbitmq on servers. It is not original work and came straight from the rabbitmq website.
  - [webWorker.py](webWorker.py) - This script is used to handle distributed logging. It was/is run on the Front end. it is a worker that listens to the logging queue and writes to the log file which then gets distributed to all servers.

- Not in use
 
  - [apache-startup.sh](apache-startup.sh) - This script was used to start the apache server on the front-end server. 
  - [migration-test.sh](migration-test.sh) - This script was used to test the migration of files from the repo to /var/www.
  - [migrate-web.sh](migrate-web.sh) - This script was used to migrate files from the repo to /var/www.
  - [worker.py](worker.py) - This script is used to handle the RabbitMQ messaging. It was/is run on the Backend server. It is a worker that listens to the queue and responds to requests.