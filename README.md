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


## Additional Resources
