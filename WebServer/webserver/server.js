// Import Existing Modules
const express = require('express'); // Helps us create a server
const axios = require('axios'); // Helps us make HTTP requests
const bodyParser = require('body-parser'); // Helps us parse incoming requests
const path = require('path'); // Helps us navigate file paths
const bcrypt = require('bcrypt'); // Helps us encrypt passwords
const cors = require('cors'); // May help us if I get it to work
const session = require('express-session'); // Helps us manage sessions - or will if I can get it to work
const MemoryStore = require('memorystore')(session); // Helps us store sessions in memory
const fs = require('fs'); // Helps us read & write files
const amqp = require('amqplib/callback_api'); // Helps us connect to RabbitMQ, but might not be used any more
var https = require('https'); // Helps us create a secure server
const querystring = require('node:querystring'); // Helps us parse query strings

// Import .env files
require('dotenv').config();
// Possibly deprecated in usage locally
const { error } = require('console');
// Import custom modules
const timber = require('./lumberjack.js');
const mustang = require('./mustang.js');
const handshake = require('./formHelper.js');
const { get } = require('http');


// Create the server
const app = express();


app.use(express.json());
// Set up the session, it will last one hour. If we move to SSL fully and use https, secure must be true
// TODO: Note, MemoryStore will need replaced with something that works in production - not here.
app.use(session({
    secret: process.env.SESSION_SECRET_KEYMAKER,
    resave: false,
    name: 'CGS-sessions',
    saveUninitialized: true,
    cookie: {
        secure: false,
        maxAge: 3600000
    },
    store: new MemoryStore({
        checkPeriod: 3600000
    })
}));




/**
 * Custom Middleware
 */


// Handles Status Messages
const statusMessageHandler = (req, res, next) => {
    res.statusMessageHandler = (statusCode) => {
        const statusMessages = {
            200: 'uhhh. OK',
            201: "Created! You're good to go.",
            202: 'ACK! We got your message.',
            204: 'No Content! Nothing to see here, I guess.',
            212: 'You are already logged in.',
            300: "Multiple Choices! We don't know what to do with you.",
            301: 'Moved Permanently! We moved, but you can still find us.',
            302: 'Found! We moved, but you can still find us - and did.',
            304: 'Not Modified! You already have the latest version.',
            305: 'Use Proxy! We are not allowed to talk to you directly.',
            307: 'Temporary Redirect! We moved, but you can still find us.',
            400: 'That is a Bad Request! You did something wrong.',
            401: 'Unauthorized! You are not allowed here.',
            402: 'Payment Required! You must pay to access this.',
            403: 'Forbidden! You are not allowed here.',
            404: 'Not Found! This does *not* rock.',
            405: 'Method Not Allowed! You cannot do that here.',
            406: 'Not Acceptable! We cannot give you what you want.',
            407: 'Proxy Authentication Required! You must authenticate.',
            408: 'Request Timeout! You took too long.',
            409: 'Conflict! You are not allowed to do that.',
            418: 'I am a teapot! I cannot do that.', // Legitimately a real error code
            500: 'Internal Server Error... you caught us slipping.',
            501: 'We would do anything for love... but we can\'t do that.',
            502: 'Bad Gateway! We cannot do that.',
            503: 'Come back later, we are sleeping.',
            // We can add more as needed
        };
        return statusMessages[statusCode] || 'Unknown Status';
    };
    next();
};

//  Middleware to log traffic 
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

// Custom middleware for checking if a user is logged in and setting session data. This is used for dynamic pages
// sessionconstants
app.use((req, res, next) => {
    res.locals.usercookieid = req.session.usercookieid || null;
    // console.log('\n[Custom Middleware] Checking if user is logged in\n');
    res.locals.loggedIn = req.session.loggedIn || false;
    // console.log(`[Custom Middleware] Logged in? ${res.locals.loggedIn}`)
    res.locals.uid = req.session.uid || null;
    // console.log(`[Custom Middleware] User ID: ${res.locals.uid}`);
    res.locals.name = req.session.name || null;
    // console.log(`[Custom Middleware] User Name: ${res.locals.name}`);
    // Add more session data as needed
    next();
});


// Set the middleware. Order matters -> It's like a pipeline and goes top to bottom, so we've gotta make sure we maintain this integrity. If something isn't quite working - it might be why
// app.use(express.json()); -- testing moving this up top
app.use(cors());
// app.use(cookieParser());
app.use(bodyParser.json());
app.use(express.urlencoded({ extended: true }));
app.use(statusMessageHandler);
// app.use(trafficLogger)


// These are set to help us navigate the file system to pull static files
app.use(express.static(__dirname + '../public'));
app.use('/css', express.static(__dirname + '../public/css'));
app.use('/css', express.static('public'));
app.use('/js', express.static(__dirname + '../public/js'));
app.use('img', express.static(__dirname + '../public/img'));

// We'll need an error handler here.

// Set views and view engine so we can use EJS. Views are the pages, view engine is the template engine
app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', 'ejs');


// Other Constants
const Port = process.env.PORT || 9001;

// AMQP Constants
const tempHost = process.env.BROKER_VHOST;
const tempQueue = process.env.BROKER_QUEUE;

// const https_options = {
//     key: fs.readFileSync(__dirname + "/cert/key.pem"),
//     cert: fs.readFileSync(__dirname + "/cert/cert.pem")
// };



/*I commented these out but  we might need them eventually. */
// const { get } = require('http');
// const { deprecate } = require('util');
// var SpotifyWebApi = require('spotify-web-api-node'); // Only used up front to get the access token
// const store = new sessions.MemoryStore();

// Middleware - check for cookies
// function checkCookies(req, res, next) {
//     if (req.cookies.usercookieid && req.cookies.sessionId) {
//         next();
//     } else {
//         res.redirect('/login');
//     }
// }

/**
 * getCookies - gets the cookies from the request
 * @param {*} req - a request object
 */
function getCookie(req) {
    let cookie = req.headers.cookie;
    console.log(`\n\n[getCookie] Cookie: ${cookie}\n\n`);
    return cookie;
};

/**
 * createSessionCookie - creates a session cookie
 * @param {*} req - a request object
 * @param {*} res - a response object
 * @returns the session id
 */
const createSessionCookie = (req, res) => {
    const saltRounds = 10;
    const plains = process.env.SESSION_SECRET_ID;
    let salt = bcrypt.genSaltSync(saltRounds);
    let sessionId = bcrypt.hashSync(plains, salt);
    req.session.sessionId = { sessionId: sessionId };
    // res.cookie('sessionId', sessionId, { httpOnly: true });
    return req.session.sessionId;
};


/**
 * createUserCookie - creates a user cookie
 * @param {*} req - a request object
 * @param {*} res - a response object
 * @returns a user cookie id
 */
const createUserCookie = (req, res) => {
    const saltRounds = 5;
    const plains = process.env.USER_SECRET_ID;
    let salt = bcrypt.genSaltSync(saltRounds);
    let usercookieid = bcrypt.hashSync(plains, salt);
    req.session.usercookieid = { usercookieid: usercookieid };
    // res.cookie('usercookieid', usercookieid, { httpOnly: true });
    return req.session.usercookieid;
};


/**
 * There are two main types of pages:
 * 1. Non-session pages (login, register, etc.)
 * 2. Session pages (home, etc.) - Dynamic pages that require a session to access
 */

// Non-session pages

/**
 * =====================================================
 * SPOTIFY USER TESTING BEGINS HERE
 * =====================================================
 */

// Set the Constants for Spotify
const REDIRECT_URI = process.env.SPOT_TEST_URI;
const CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
const spotAuthURL = process.env.SPOTIFY_AUTH_URL;
const spotTokenURL = process.env.SPOTIFY_TOKEN_URL;
const spotAPIURL = process.env.SPOTIFY_API_BASE_URL;

// Route to handle login
app.get('/spotlog', (req, res) => {
    /**
     * spotlog - logs the user into Spotify for oAuth
     */
    // Set the scopes for the Spotify API
    const scopes = 'user-read-currently-playing playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-top-read user-read-playback-position user-read-recently-played user-library-read user-library-modify user-read-email user-read-private';
    // Redirect to the Spotify login page with the scopes and other params set
    // Generate a random state for the request, at least 16 digits long
    var state = '';
    for (var i = 0; i < 17; i++) {
        state += Math.floor(Math.random() * 10);
    };
    res.redirect('https://accounts.spotify.com/authorize' +
        '?response_type=code' +
        '&client_id=' + CLIENT_ID +
        (scopes ? '&scope=' + encodeURIComponent(scopes) : '') + '&show_dialog=true' +
        '&redirect_uri=' + encodeURIComponent(REDIRECT_URI) + '&state=' + state);
});

// Route to handle the callback from Spotify's OAuth
app.get('/callback', async (req, res) => {
    /**
     * callback - handles the callback from Spotify's OAuth
     * @param {*} req - a request object
     * @param {*} res - a response object
     */

    const code = req.query.code || null;
    try {
        let uid = req.session.uid;
        let usercookie = req.session.usercookieid;
        console.log(`\n[Callback] Received code from Spotify: ${code}, attempting to get the real one\n`);
        const response = await axios({
            method: 'post',
            url: 'https://accounts.spotify.com/api/token',
            data: new URLSearchParams({
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: REDIRECT_URI
            }).toString(),
            headers: {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + (new Buffer.from(CLIENT_ID + ':' + CLIENT_SECRET).toString('base64'))
            }
        });
        if (response.data.access_token) {
            console.log('\n[Callback] Received response from Spotify, parsing it...\n');
            console.log(`response.data.access_token: ${response.data.access_token}`);
            // Probably can clean this up and import up top before sending to production
            var spotvHost = process.env.BROKER_VHOST;
            var spotQueue = process.env.BROKER_QUEUE;
            const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(spotvHost)}`;
            // console.log(amqpUrl);
            // All of the data we need to send to the broker so that we can get the user's Spotify data
            let access_token = response.data.access_token;
            let refresh_token = response.data.refresh_token;
            let expires_in = response.data.expires_in;
            let token_type = response.data.token_type;
            let usercookie = res.locals.usercookieid;
            console.log(`[Spotify Token Grab] What's the usercookie? ${usercookie}`);
            mustang.sendAndConsumeMessage(amqpUrl, spotQueue, {
                type: "spotToken",
                "usercookie": usercookie,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "token_type": token_type
            }, (msg) => {
                console.log(`[Spotify Token Grab] Received message from broker, parsing response`);
                const response = JSON.parse(msg.content.toString());
                console.log(`[Spotify Token Grab] Response: ${response}`);
                console.log(`[Spotify Token Grab] Response.returnCode: ${response.returnCode}`);
                console.log(`[Spotify Token Grab] Response.data: ${response.message}`);
                if (response.returnCode === 0) {
                    console.log(`[Spotify Token Grab] Success!`);
                    timber.logAndSend('User requested some jams, got some.', "_SPOTIFY_");
                    res.status(200).render('success');
                } else {
                    console.log(`[Spotify Token Grab] Failure!`);
                    res.status(401).send('You have failed to authorize Spotify - did we do something?');
                }
            });
        }
    } catch (error) {
        res.status(500).send('Authentication Failed');
    }
});

/**
 * =====================================================
 * SPOTIFY USER TESTING ENDS HERE
 * =====================================================
 */


// try {
//     https = require('https');
//     console.log("Seems like we're good to go with https!");
// } catch (err) {
//     console.log('https module not found, using http instead');
//     https = require('http');
// }


app.get('/', (req, res) => {
    res.status(200).render('index'), err => {
        if (err) {
            msg = 'Failed to render index page.'
            timber.logAndSend(msg);
            console.error(err);
        }
    };
});
app.post('/account:param', (req, res) => {
    // const tempHost = process.env.BROKER_VHOST;
    // const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${tempHost}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    typeOf = req.params.param;
    console.log('\n[Posting to /account:param] with typeOf: ', typeOf, '\n');
});

app.get('/:page', (req, res) => {
    const page = req.params.page;
    let sessionPages = ['account', 'dashboard', 'profile', 'forum', 'logout']
    if (page == 'login') {
        let errorStatus = null;
        let errorOutput = '';
        res.status(200).render(page, { data: { error_status: errorStatus, error_output: errorOutput } }), err => {
            timber.logAndSend(err);
        }
    }
    else if (page == 'register') {
        let errorStatus = null;
        let errorOutput = '';
        res.status(200).render(page, { data: { error_status: errorStatus, error_output: errorOutput } }), err => {
            timber.logAndSend(err);
        }
    }
    else if (page == 'artists') {
        // const tempHost = process.env.BROKER_VHOST;
        // const tempQueue = process.env.BROKER_QUEUE;
        const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
        console.log(amqpUrl);
        const artist = req.body.artist;
        const typeOf = req.params.param;
        mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
            type: "byArtist",
            artist: artist,
            typeOf: typeOf,
        }, (msg) => {
            const response = JSON.parse(msg.content.toString());
            if (response.returnCode === 0) {
                data = response.data;
                musicdata = response.music;
                console.log("\n[Approx line 186] testing query artist data");

                if (data.findAlbums) {
                    let albums = [];
                    let external_urls = [];
                    for (var i = 0; i < musicdata.length; i++) {
                        albums.push(musicdata[i].album);
                        external_urls.push(musicdata[i].external_urls);
                        res.render('account', { data: data, tracks: tracks })
                    }
                }
                res.render('account', { data: data, tracks: tracks, artists: artists, links: links });
            }
            else {
                if (sessionPages.includes(page)) {
                    let checkSession = ""; // call the db server and see if the session is valid. Doesn't work, sessions aren't implemented yet.
                    if (page === 'account') {
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
    }
});


const userData = [];
/**
 * @deprecated
 */
app.post('/getrecked', (req, res) => {
    console.log('\n[Posting to /getrecked]\n');
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
            console.log("[getrecked] Received message from broker, parsing response\n\n\n");
            const response = JSON.parse(msg.content.toString());
            console.log(response);
            // Create the data object to send to client 

            if (response.returnCode === 0) {
                console.log("\n[from getrecked post] Success!");
                timber.logAndSend('\nUser requested some jams, got some.\n');
                data = response.data;
                musicdata = response.music
                console.log("\n\nwe made it to getRecs, here's response.music/musicdata\n");
                console.log(musicdata);
                console.log("\ntesting musicdata\n");
                let tracks = [];
                let artists = [];
                let links = [];
                for (var i = 0; i < musicdata.length; i++) {
                    tracks.push(musicdata[i].track);
                    artists.push(musicdata[i].artist);
                    links.push(musicdata[i].url);
                }

                res.render('account', { data: data, tracks: tracks, artists: artists, links: links });
            } else {
                console.log("\nFailure!");
                console.log("\nSending response data");
                console.log("\nshowing data");
                console.log(musicdata);
                res.status(401).render('account', musicdata);
            }
        } catch (error) {
            console.log("\nError:", error);
            // Handle the error appropriately, maybe render an error page
            res.status(500).send("An error occurred");
        }
    });
});

app.post('/account', (req, res) => {
    // const tempHost = process.env.BROKER_VHOST;
    // const tempQueue = process.env.BROKER_QUEUE;
    const genre = req.body.genres;
    const popularity = req.body.pop;
    const valence = req.body.vibe;
    console.log(`\ngenre: ${genre}, popularity: ${popularity}, valence: ${valence}`);
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
            console.log('\n[Posting to /account]\t Received response, parsing\n');
            // Create the data object to send to client 

            if (response.returnCode === 0) {
                console.log("\n['/account'] Success!");
                timber.logAndSend('\nUser requested some jams, got some.\n');
                data = response.data;
                musicdata = response.music
                console.log("\n\nWe made it to simpleRecs, here's response.music/musicdata\n");
                console.log(musicdata);
                console.log("\n['account'] \tTesting musicdata\n");
                let tracks = [];
                let artists = [];
                let links = [];
                for (var i = 0; i < musicdata.length; i++) {
                    tracks.push(musicdata[i].track);
                    artists.push(musicdata[i].artist);
                    links.push(musicdata[i].url);
                }

                res.render('account', { data: data, tracks: tracks, artists: artists, links: links });
            } else {
                console.log("Failure!");
                console.log("Sending response data");
                console.log("Showing data");
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
    // let session_id = req.session.sessionId;
    // let usercookieid = req.session.usercookieid;
    let usercookieid = createUserCookie(req, res);
    console.log(`session cookie Created?: ${req.session.sessionId['sessionId']}`);
    console.log(`user cookie Created?: ${usercookieid}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    console.log(amqpUrl);

    getCookie(req);

    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "login",
        "useremail": useremail,
        "password": password,
        "session_id": session_id['sessionId'],
        "usercookieid": usercookieid['usercookieid']
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === 0) {
            // console.log(`Name: Line, 606 \t ${response.userinfo.name}`);
            timber.logAndSend('User logged in successfully.');
            data = response.data;
            musicdata = response.music;
            userinfo = response.userinfo;
            // console.log("testing musicdata");
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            console.log('\n[Login] Setting session data\n');
            req.session.uid = userinfo.uid;
            req.session.name = userinfo.name;
            req.session.loggedIn = true; // TODO: 11/4/2023 - come back here if it breaks.
            let uidtest = req.session.uid;
            let uname = req.session.name;
            req.session.music = musicdata;
            console.log(`\n[Login] Attempted to store session data: ${uidtest}, ${uname}\n`)
            // we may want to add other session information to keep, like username, spotify name, etc.
            // passing back the uid may be good for messaging and other things.
            res.status(200).render('account', { data: data, tracks: tracks, artists: artists, links: links });
            //res.redirect('/account');
        } else {
            let errorMSG = 'You have failed to login.';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            // let outcome = response.data['loggedin'];
            console.log("Sending response data");
            // console.log(response.data['loggedin']);
            data = response.data;
            console.log("showing data");
            console.log(data);
            res.status(401).render('login', data);
        }
    });
});

app.post('/account:param', (req, res) => {
    //NOTE: come back here and fix your mess
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${tempHost}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    typeOf = req.params.param;
    console.log('\n[Posting to /account:param] with typeOf: ', typeOf, '\n');
    console.log('[TYPE OF] ', typeOf);
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
        if (response.returnCode == 0) {
            // Set a cookie for userid to track locally; this will be used to validate session
            console.log("\n[Register - response] Successful registration, parsing data\n");
            data = response.data;
            musicdata = response.music;
            userinfo = response.userinfo;
            console.log(`[Register - response] testing data --- ${userinfo}`);
            console.log("[Register - response] testing musicdata");
            console.log('\n', musicdata, '\n');
            console.log(userinfo);
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            // req.session.loggedIn = true; // TODO: 11/4/2023 - come back here if it breaks.
            // req.session.userId = user.id; // TODO: come back here if it breaks.
            req.session.uid = userinfo.uid;
            req.session.name = userinfo.user_fname;
            req.session.loggedIn = true;
            res.render('account', { data: data, tracks: tracks, artists: artists, links: links });

        } else {
            // res.status(401).send('You have failed to register.');
            data = response.data;
            console.log("showing data");
            console.log(data);
            res.status(401).render('register', data);
            // add handling for render isntead that prints message to user
        }
    });
});


// const httpsServer = https.createServer(https_options, app);

// const newport = 9001;
// httpsServer.listen(newport, () => {
//     console.log(`Listening on port ${newport}`);
// })

// Listen

app.listen(Port, () => {
    console.log(`Listening on port ${Port}`);
});