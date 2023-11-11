const express = require('express');
const path = require('path');
const accounts = require('./routes/accounts.js');
const api = require('./routes/api.js');

const axios = require('axios'); // Helps with AJAX requests
const bcrypt = require('bcrypt'); // Helps us encrypt passwords
const fs = require('fs'); // Helps us with file system tasks
const querystring = require('querystring'); // Helps us with query strings
var https = require('https');

require('dotenv').config();

// My own modules
const timber = require('./lumberjack.js');
const mustang = require('./mustang.js');
const statusMessageHandler = require('./status.js');

// Instantiate the server
const app = express();

// Other Constants
const Port = process.env.PORT || 9001;

// AMQP Constants
const tempHost = process.env.BROKER_VHOST;
const tempQueue = process.env.BROKER_QUEUE;


// Constants used by RMQ




app.use(express.json());
app.use(statusMessageHandler);
app.use(express.urlencoded({ extended: true }));

// set up paths

app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', 'ejs');

const publicPath = path.join(__dirname, '../public');
app.use(express.static(publicPath));
app.use('/css', express.static(path.join(publicPath, 'css')));
app.use('/js', express.static(path.join(publicPath, 'js')));
app.use('/img', express.static(path.join(publicPath, 'img')));
// app.use('/partials', express.static(path.join(publicPath, 'partials')));
app.use('/account', express.static(path.join(publicPath, 'account')));
app.use('/account/js', express.static(path.join(publicPath, 'js')));
app.use('/account/css', express.static(path.join(publicPath, 'js')));


// Set views and view engine so we can use EJS. Views are the pages, view engine is the template engine
app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', 'ejs');

/**
 * These are routing middleware functions. They are called before the request is passed to the router.
 * They are called in the order they are defined.
 * This is important to note and I'm commenting so we all can understand. What they do is tell the express server to use these routers if a request is made to, for example, account/anything or api/anything. Middleware before this should still be called and passed through. 
 */
app.use("/account", accounts); // Routing done in accounts.js
app.use("/api", api); // Routing done in api.js




// Gets


app.get('/', (req, res) => {
    res.status(200).render('index'), err => {
        if (err) {
            msg = 'Failed to render index page.'
            timber.logAndSend(msg);
            console.error(err);
        }
    };
});

// We call account separately because it has its own router, or at least that's why i am.

app.get("/account", (req, res) => {
    res.send("pointing at account");
});

app.get("/:page", (req, res) => {
    page = req.params.page;
    console.log(`page: ${page}`);
    var errorStatus = null;
    var errorOutput = null;
    data = { errorStatus: errorStatus, errorOutput: errorOutput };
    switch (page) {
        case "login":
            // let errorStatus = null;
            // let errorOutput = null;
            data = { errorStatus: errorStatus, errorOutput: errorOutput }
            res.status(200).render('login', { data }), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render login page.`
                    timber.logAndSend(msg);
                }
            };
            break;
        case "about":
            res.status(200).render('about'), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render about page.`
                    timber.logAndSend(msg);
                }
            };
            break;
        case "register":
            res.status(200).render('register', { data }), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render register page.`
                    timber.logAndSend(msg);
                }
            };
            break;
        default:
            res.status(200).render('/');
            break;
    }
});




app.listen(9001, () => {
    console.log('Listening on port 9001');
});
