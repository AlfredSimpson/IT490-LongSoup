# Deployment



We're tasked with creating our own deployment server.

## Setup the helpers

Our helpers should do the following:
1. Install necessary python libraries.
2. Make a clean copy of the files needed, zip them, and send them to the deployment server.
3. Once on the deployment server, send them to where they need to go. 
4. Once on the required server, unzip them and run the necessary commands to get them up and running.
5. If there are any errors, send them back to the deployment server.
6. If there are no errors, send a success message back to the deployment server.
7. If the deployment server receives a success message from the QA Cluster, send it to the Prod Cluster.

## dev_worker.py

This handles requests to and from the development cluster.


## qa_worker.py



# What's needed on each server

## Front

Each of these can be modularly updated and packaged to prevent downtime and over usage of resources. We will package by directory in WebServer.

- public
  - These are the static files and their directories
  - css/
    - bootstrap.css
    - bootstrap.min.css
    - style.css
    - styles.min.css
  - js/
    - accounts.js (handles account AJAX Requests)
    - handler.js (handles other the primary querying ajax) 
    - index.js (used for scrolling on the front landing page))
    - longajax.js (May not be necessary)
    - messageboards.js (may combine with handler or accounts)
    - script.min.js (bootstrap)
  - img/
    - A bunch of images
- views
  - These are the pages that are served to the user
- webserver
  - These are the server specific files served to the user.
  - This should include:
    - server.js
      - Our primary server
    - mustang.js
      - Our engine for delivering things to the queue
    - formHelper.js
      - A helper for forms
    - lumberjack.js
      - Our logging mechanism
    - cert directory and it's key/pem
      - How we get SSL/HTTPS
    - routes directory and all routes
      - Necessary for router
    - package-lock.json
    - package.json
    - status.js
      - Necessary for status codes.


## Back

Each of these should be packaged and sent to the server. We will package these files into their own directory to be sent together
- requirements.txt
  - This is the list of python libraries needed to run the server.
- DBWorker.py
- DBSpotWorker.py
  

## DMZ



## Setting up Deployment

- [x] Install RabbitMQ
  - [ ] Establish users, queues, hosts, exchanges, and all necessary settings
  - [ ] Establish a way to send messages to the queues
  - [ ] Establish a way to receive messages from the queues
  - [ ] Establish a way to execute commands based on the messages received using rpc
  - [ ] 
- [x] Install MongoDB
  - [x] Set up the database
  - [x] Set up the user and password
  - [ ] Create the necessary collections
- [x] Install Utilities for QoL improvements.