// This is my attempt to create a better web server than the one I made in the past. It will be more modular and easier to use. Further, I'm building my own view engine.

const express = require('express');
const axios = require('axios'); // Helps with AJAX requests
const bcrypt = require('bcrypt'); // Helps us encrypt passwords
const path = require('path'); // Helps us with file paths
const fs = require('fs'); // Helps us with file system tasks
const querystring = require('querystring'); // Helps us with query strings

// Import .env files
require('dotenv').config();

// Custom imports
const timber = require('./lumberjack.js');
const mustang = require('./mustang.js');
const cgs = require('./cgs.js'); // Custom Modules -> statusMessageHandler
const alsviewer = require('./alsviewer.js'); // Custom Modules -> alsviewer


// Instantiate the app
const app = express();

// Set views and view engine so we can use EJS. Views are the pages, view engine is the template engine
app.engine('.alv', alsviewer);
app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', '.alv');


// Variables/Constants needed for the server

const Port = process.env.PORT || 9001;
const publicPath = path.join(__dirname, '../public');

// AMQP constants



// Custom Middleware functions

const trafficLogger = (req, res, next) => {
    timber.logAndSend(`Incoming request:  ${req.method}`);
    const send = res.send;
    res.send = function (string) {
        const body = string instanceof Buffer ? string.toString() : string;
        // console.log('req.session', req.session);
        console.log(`res.status`, res.statusCode);
        if (res.statusCode != 200) {
            timber.logAndSend(`Outgoing response: ${res.statusCode}`);
            send.call(this, string);
        }
    };
    next();
};



// Middleware

app.use(express.static(publicPath));
app.use('/css', express.static(path.join(publicPath, 'css')));
app.use('/js', express.static(path.join(publicPath, 'js')));
app.use('/img', express.static(path.join(publicPath, 'img')));
app.use('/account', express.static(path.join(publicPath, 'account')));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cgs.statusMessageHandler);
// Set the paths






// Routing below here

// Gets

app.get('/', (req, res) => {
    res.status(200).render('index');
});

app.get('/:page', (req, res) => {
    const page = req.params.page;
    // res.status(200).send(`You are on page ${page}`);
    // res.status(200).render(page, { page });
    switch (page) {
        case 'index':
            res.status(200).render(page);
            break;
        case 'test':
            res.status(200).render(page, {
                title: "Test Page",
                message: "<h1>Oh hey hi hello!</h1>"
            });
            break;
        default:
            break;
    }
});

// Posts



app.listen(Port, () => {
    console.log(`Server listening on port ${Port}`);
});