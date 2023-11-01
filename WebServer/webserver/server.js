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
// const session = require('express-session');
const sessions = require('express-session');
const cookieParser = require('cookie-parser');
const { get } = require('http');

// const store = new sessions.MemoryStore();
app.use(express.json());
app.use(cookieParser());

// app.use(sessions({
//     secret: "secretkeylol",
//     resave: false,
//     saveUninitialized: false,
//     store
// })
// );

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
    //timber.logAndSend(`Incoming request: \ ${req.method} ${req.url}`);

    const send = res.send;
    res.send = function (string) {
        //
        // const body = string instanceof Buffer ? string.toString() : string;
        //timber.logAndSend(`Outgoing response: ${res.statusCode}`);
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
// app.use('/css', express.static(__dirname + '../public/css'));
app.use('/css', express.static('public'));
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

    // if (page === 'login' || page === 'register') {
    if (page == 'login') {
        let errorStatus = null;
        let errorOutput = '';
        res.status(200).render(page, { data: { error_status: errorStatus, error_output: errorOutput } }), err => {
            timber.logAndSend(err);
        }

    }
    else {
        if (sessionPages.includes(page)) {
            let checkSession = ""; // call the db server and see if the session is valid
            if (page === 'account') {
                req.session.data = response.data; //added to help retain data
                console.log(data.name);
                let data = response.data;

                res.status(200).render(page, data), err => {
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


        }
    }
});

// app.get('/getRecked', function (req, res) {


//     // Parse the rawData to extract the required information
//     let parsedData = rawData.map(item => {
//         return {
//             artist: data.artists.name, // replace with actual keys if different
//             track: data.tracks.name,   // replace with actual keys if different
//             url: data.tracks.external_urls.spotify,       // replace with actual keys if different
//         };
//     });

//     res.render('getRecked', { recommendations: parsedData });
// });
const userData = [];
app.post('/getrecked', (req, res) => {
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const genre = req.body.genres;
    const popularity = req.body.pop;
    const valence = req.body.vibe;
    console.log(`genre: ${genre}, popularity: ${popularity}, valence: ${valence}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${tempHost}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;


    // getCookie(req);
    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "simplerecs",
        genre,
        popularity,
        valence
    }, (msg) => {
        try {
            const response = JSON.parse(msg.content.toString());
            // let parsedData = response.map(item => {
            //     return {
            //         artist: data.artists.name, // replace with actual keys if different
            //         track: data.tracks.name,   // replace with actual keys if different
            //         url: data.tracks.external_urls.spotify,       // replace with actual keys if different
            //     };
            // });

            // Create the data object to send to client 

            if (response.returnCode === 0) {
                console.log("Success!");
                timber.logAndSend('User requested some jams, got some.');
                userData.push(parsedData);
                res.render('account', userData);
            } else {
                console.log("Failure!");
                console.log("Sending response data");
                console.log("showing data");
                console.log(musicdata);
                res.status(401).render('account', musicdata);
            }
        } catch (error) {
            console.log("Error:", error);
            // Handle the error appropriately, maybe render an error page
            res.status(500).send("An error occurred");
        }
    });
});

app.post('/account', (req, res) => {
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const genre = req.body.genres;
    const popularity = req.body.pop;
    const valence = req.body.vibe;
    console.log(`genre: ${genre}, popularity: ${popularity}, valence: ${valence}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;


    // getCookie(req);
    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "simplerecs",
        genre,
        popularity,
        valence
    }, (msg) => {
        try {
            const response = JSON.parse(msg.content.toString());


            // Create the data object to send to client

            if (response.returnCode === 0) {
                console.log("Success!");
                let musicdata = response.data;
                timber.logAndSend('User requested some jams, got some.');
                res.render('account', { musicdata });
            } else {
                console.log("Failure!");
                console.log("Sending response data");
                console.log("showing data");
                console.log(musicdata);
                res.status(401).render('account', musicdata);
            }
        } catch (error) {
            console.log("Error:", error);
            // Handle the error appropriately, maybe render an error page
            res.status(500).send("An error occurred");
        }
    });

    // mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
    //     type: "simplerecs",
    //     genre,
    //     popularity,
    //     valence
    // }, (msg) => {
    //     const response = JSON.parse(msg.content.toString());
    //     // console.log(response);
    //     let musicdata = response.data;
    //     let rectracks = musicdata.tracks;;
    //     let artist = rectracks.album
    //     console.log(artist);
    //     if (response.returnCode === 0) {
    //         console.log("Success!");
    //         // console.log(response.data.name);
    //         timber.logAndSend('User requested some jams, got some.');

    //         res.render('account', data);
    //     } else {
    //         console.log("Failure!");
    //         let errorMSG = 'Could not get recommendations.';
    //         const filePath = path.join(__dirname, 'public', 'account' + '.ejs');
    //         // let outcome = response.data['loggedin'];
    //         console.log("Sending response data");

    //         console.log("showing data");
    //         console.log(data);
    //         res.status(401).render('account', data);
    //     }
    // });

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
            console.log(response.data.name);
            timber.logAndSend('User logged in successfully.');
            data = response.data;
            console.log(data);
            res.render('account', data);
            // res.redirect('/account');
        } else {
            let errorMSG = 'You have failed to login.';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            // let outcome = response.data['loggedin'];
            console.log("Sending response data");
            console.log(response.data['loggedin']);
            data = response.data;
            console.log("showing data");
            console.log(data);
            res.status(401).render('login', data);
        }
    });
});


app.post('/register', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const last_name = req.body.last_name;
    const first_name = req.body.first_name;
    const spot_name = req.body.spot_name;
    let session_id = createSessionCookie(req, res);
    let usercookieid = createUserCookie(req, res);
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
        usercookieid,
        spot_name
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode == "0") {
            // Set a cookie for userid to track locally; this will be used to validate session
            console.log("trying to redirect to account");
            data = response.data;
            res.render('account', data);

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