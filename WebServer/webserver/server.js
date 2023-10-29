// Imports
const express = require('express');
const fs = require('fs');
const bodyParser = require('body-parser');
const app = express();
const path = require('path');
const timber = require('./lumberjack.js');
const handshake = require('./formHelper.js');
const amqp = require('amqplib/callback_api');
const mustang = require('./mustang.js');
const bcrypt = require('bcrypt');
const session = require('express-session');
const cookieParser = require('cookie-parser');
const { get } = require('http');

app.use(cookieParser());

const Port = process.env.PORT || 9001;

// Load environment variables
require('dotenv').config();


// Middleware - check for cookies
// function checkCookies(req, res, next) {
//     if (req.cookies.usercookieid && req.cookies.sessionId) {
//         next();
//     } else {
//         res.redirect('/login');
//     }
// }

function getCookie(req) {
    let cookie = req.headers.cookie;
    console.log(cookie.split('; '));
};

// status codes

const statusMessageHandler = (req, res, next) => {
    res.statusMessageHandler = (statusCode) => {
        const statusMessages = {
            200: 'OK',
            404: 'Not Found! This does *not* rock.',
            500: 'Internal Server Error... you caught us slipping.',
            // We can add more as needed
        };
        return statusMessages[statusCode] || 'Unknown Status';
    };

    next();
};

//  Middleware to log traffic 
const trafficLogger = (req, res, next) => {
    timber.logAndSend(`Incoming request: \ ${req.method} ${req.url}`);

    const send = res.send;
    res.send = function (string) {
        //
        // const body = string instanceof Buffer ? string.toString() : string;
        timber.logAndSend(`Outgoing response: ${res.statusCode}`);
        send.call(this, string);
    };
    next();
};

// session Cookies for login/validation after
const createSessionCookie = (req, res) => {
    const saltRounds = 10;
    const plains = process.env.SESSION_SECRET_ID;
    let salt = bcrypt.genSaltSync(saltRounds);
    let sessionId = bcrypt.hashSync(plains, salt);
    req.session = { sessionId: sessionId };
    res.cookie('sessionId', sessionId, { httpOnly: true });
    return req.session.sessionId;
};

const createUserCookie = (req, res) => {
    const saltRounds = 5;
    const plains = process.env.USER_SECRET_ID;
    let salt = bcrypt.genSaltSync(saltRounds);
    let usercookieid = bcrypt.hashSync(plains, salt);
    req.session = { usercookieid: usercookieid };
    res.cookie('usercookieid', usercookieid, { httpOnly: true });
    return req.session.usercookieid;
};


app.use(trafficLogger);
app.use(statusMessageHandler);
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static(__dirname + '../public'));
app.use('/css', express.static(__dirname + '../public/css'));
app.use('/js', express.static(__dirname + '../public/js'));
app.use('img', express.static(__dirname + '../public/img'));


// Set views
app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', 'ejs');


app.use((err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    const message = res.statusMessageHandler(statusCode);
    res.status(statusCode).send(message);
});


/**
 * There are two main types of pages:
 * 1. Non-session pages (login, register, etc.)
 * 2. Session pages (home, etc.) - Dynamic pages that require a session to access
 */


// Non-session pages


app.get('/', (req, res) => {
    res.status(200).render('index'), err => {
        if (err) {
            msg = 'Failed to render index page.'
            timber.logAndSend(msg);
            console.error(err);
        }
    };
});


app.get('/:page', (req, res) => {
    const page = req.params.page;
    let sessionPages = ['account', 'dashboard', 'profile', 'forum', 'logout']
    if (page === 'login' || page === 'register') {
        let errorStatus = false;
        let errorOutput = 'Whoa - not so fast. That a fake ID? Check your details and try again.';
        // console.log(errorOutput);
        res.status(200).render(page, { data: { error_status: errorStatus, error_output: errorOutput } }), err => {
            timber.logAndSend(err);

        }
    }
    else {
        if (sessionPages.includes(page)) {
            if (page === 'account') {
                let name = 'Test User';
                res.status(200).render(page, { data: { name: name } }), err => {
                    if (err) {
                        timber.logAndSend(err);
                        console.error(err);
                    }
                }
            }
            else {
                res.status(200).render(page), err => {
                    if (err) {
                        timber.logAndSend(err);
                        console.error(err);
                    }
                }
            }
            // run session check in another function, validate or reject, and render with data.
            //check to see if session cookie exists. If so, check db. If it passes, let them in. If not, redirect to login.
        }
        else {
            res.status(200).render(page), err => {
                if (err) {
                    timber.logAndSend(err);
                    // console.error(err);
                }
            }
            //     const filePath = path.join(__dirname, page + '.ejs');
            //     // check if session cookie exists
            //     if (!fs.existsSync(filePath)) {
            //         res.status(404).send('Page not found');
            //         timber.logAndSend(`404: ${filePath} - Page not found`);
            //         return;
            //     }
            //     console.log(page);
            //     res.status(200).render(page), err => {
            //         if (err) {
            //             timber.logAndSend(err);
            //             console.error(err);
            //         }
            //     };

        }
    }
});





app.post('/login', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    let session_id = createSessionCookie(req, res);
    let usercookieid = createUserCookie(req, res);
    console.log(`session cookie Created?: ${session_id}`);
    console.log(`user cookie Created?: ${usercookieid}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    console.log(amqpUrl);

    getCookie(req);

    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "login",
        useremail,
        password,
        session_id,
        usercookieid
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === '0') {
            console.log('Login successful!');
            timber.logAndSend('User logged in successfully.');
            // if (response.sessionValid === true) {} --- may not be necessary as cookie is set at login
            res.redirect('/account');
        } else {
            let errorMSG = '<p class="er-msg"> You have failed to login. <p>';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            res.status(401).render('login', errorMSG);
        }
    });
});


app.post('/register', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const last_name = req.body.last_name;
    const first_name = req.body.first_name;
    const session_id = req.session.sessionId;
    const usercookieid = req.session.usercookieid;
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;

    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "register",
        useremail,
        password,
        last_name,
        first_name,
        session_id,
        usercookieid
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === '0') {
            // Set a cookie for userid to track locally; this will be used to validate session

            res.redirect('/account');
        } else {
            res.status(401).send('You have failed to register.');
            // add handling for render isntead that prints message to user
        }
    });
});




// Listen

app.listen(Port, () => {
    console.log(`Listening on port ${Port}`);
});