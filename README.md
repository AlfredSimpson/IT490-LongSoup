# IT490-LongSoup
A repository for the IT490 Systems Integration Course.

**Date** : Fall 2023

## Contributing Members

- [Alfred Simpson](https://github.com/AlfredSimpson)
- [David Villafranca](https://github.com/theamazins17)
- [Justin Tecson](https://github.com/JustinTecson)
- [Ricky Hernandez](https://github.com/rickyhernandez1000)*

## Attribitution

Source Code initially copied from [engineerOfLies](https://github.com/engineerOfLies/rabbitmqphp_example).

## Project Summary

This project is pulling multiple APIs to create a music & social media web app with (hopefully) better recommendations than Spotify.

- Front End
  - [WebServer](./WebServer/) : All active development work
    - [Public](./WebServer/public) : Contains the front end js, css, img files
    - [views](./WebServer/views/) : Contains the front end .ejs files
    - [webserver](./WebServer/webserver/) : Contains the back end node js/express files, and multiple custom middleware functions
- Database
  - [DB](./DB/): All active development
    - [DBWorker](./DB/DBWorker.py) : Listens for and processes primary requests to the database
    - [DBProfileWorker](./DB/DBProfileWorker.py) : Assists with updating and accessing profile information.
    - [DBMessageWorker](./DB/DBmbWorker.py) : Listens for and processes messages from the webserver specifically related to the messageboard
    - [DBSpotWorker](./DB/DBSpotWorker.py) : Listens for and responds to requests for spotify information
    - [Long*](./DB/): If it starts with Long, there's a good chance it's a class that was build for use in another location
- DMZ
  - Actually sourced most from the DB directory, we need to move them over.
- RabbitMQ
  - Similarly, the listeners that reside on the Broker server were just repurposed from WebServer or DB
- Utilities
  - Within the Utilities directory you'll find various scripts we created to make our lives easier, including systemd management scripts, configuration files for keepalived, and more.


# Languages and Frameworks used

- Node.js
  - Express
  - EJS
  - Axios
  - Body-Parser
  - Express-Sessions
- Python
- MongoDB
- RabbitMQ
- HTML
- CSS
- Javascript
- Bootstrap CSS 5
- JSON
- Spotify API
- TheAudioDB API

# Deliverables

This project had numerous deliverables. Some deliverables were common and required by all students, and some were required by our team specifically.

- [x] Authentication
  - Users can register and log in to our website. If they provide false information, it rejects their login attempt
- [x] Distributed Logging
  - Logging is set up on each server and distributed to all servers.
- [x] Functioning Website
  - Website turns on and works
- [x] Secured Database
  - Remove default settings, enable access only from localhost
- [x] Messaging through RabbitMQ
  - Servers do not communicate directly - Front, DMZ and Backend servers must communicate through a queueing system only.
- [x] Procedural Data Generation
  - Establish a system for gathering data in the DMZ to fill the databse with.
- [x] Create a system for importing different APIs and display this in the UI **
  - Users should see the scope of what we can access through our connection to an API of our choosing. We used Spotify.
- [ ] Recommendation System **
  - Collect data on what a user likes and dislikes and provide recommendations based on these actions.
- [x] Message Boards **
  - Give users a place to communicate.
- [x] Browse Songs and artists **
  - Users can browse songs, artists, albums, etc. 
- [x] Users can like/dislike items **
  - Users can like or dislike songs.
- [x] Users have a profile/account page **
  - Users get a page specific to them.
- [x] Prod, QA, and Development clusters/vms built
  - Establish servers for QA and Production. The first 3 (4 originally) servers are set as the development cluster.
- [x] Hot Standby servers established
  - Production servers will have replicas set up. If the primary production server fails, the hot standby will take over.
- [x] Replicated Databases
  - The production database will receive an exact replication in its hot standby server.
- [x] Deployment System from scratch
  - Without using a third party, create a system that enables developers to send packages to the deployment server which will then be relayed to QA. QA can then approve it or reject it. If approved, it will be sent to production and enabled. If rejected, it is marked as failed.
  - The Deployment Server must keep a database of all packages, their statuses, and enable reverting if necessary.
- [x] Systemd server management in production
  - Establish a systemd service which ensures necessary programs and options are running.
- [x] Firewalls that protect the backend servers.
  - Enable a firewall that denys connections from outside sources. Should allow only necessary connections.
- [x] Passwords in DB are hashed
  - Ensure all passwords stored in the database are hashed before storing.
- [x] Responsive Website design
  - Website should be visually appealing and not break based on window size. We used Bootstrap v5.3 to make this happen.
- [x] Enable SSL/HTTPS on all pages
  - All webpages should be accessible through https only.
- [x] Users can add songs found on our application to spotify **
  - While finding items, a user will be able to add the songs to a playlist on spotify.
- [x] Users can create a playlist on our application **
  - Users can also create this playlist through our application. This is done at the same time as adding songs.
- [x] Users can mark things public or private on their profiles **
  - Users can mark thigns as public or private on their profiles. We were able to do this, but not stop it from displaying fully.
- [x] Establish Nagios in production servers ***
  - Nagios should be set up on one server and montior many others.
- [ ] OSSIM in production servers ***
  - Use OSSIM instead of ubuntu
- [x] Create 2FA system from scratch (no third party apps) ***
  - Without the use of third party apps, create a mode of two-factor authentication. We chose to use email.
- [x] DataDog agents installed on servers ****
  - Not a requirement, just something we asked if we would be allowed to do.

** Indicates a personal deliverable - something specific to our team
*** Indicates an optional deliverable
**** Indicates an extra feature we asked about implementing



## Additional Resources
