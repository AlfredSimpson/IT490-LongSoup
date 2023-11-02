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
const cors = require('cors');
// const session = require('express-session');
const sessions = require('express-session');
const cookieParser = require('cookie-parser');
const { get } = require('http');
const { deprecate } = require('util');
const querystring = require('node:querystring');
var https = require('https');

// const store = new sessions.MemoryStore();
app.use(express.json());
app.use(cookieParser());


const https_options = {
    key: fs.readFileSync(__dirname + "/cert/key.pem"),
    cert: fs.readFileSync(__dirname + "/cert/cert.pem")
};





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
// app.use(bodyParser.urlencoded({ extended: false }));
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

/**
 * =====================================================
 * SPOTIFY USER TESTING BEGINS HERE
 * =====================================================
 */

// app.use(express.json()); // Commented out, already declared above
app.use(express.urlencoded({ extended: true })); // Commented out the one above which was false
app.use(cors());

const spotURI = process.env.SPOT_TEST_URI;
const spotClientID = process.env.SPOTIFY_CLIENT_ID;
const spotClientSecret = process.env.SPOTIFY_CLIENT_SECRET;
const spotAuthURL = process.env.SPOTIFY_AUTH_URL;
const spotTokenURL = process.env.SPOTIFY_TOKEN_URL;
const spotAPIURL = process.env.SPOTIFY_API_BASE_URL;

app.get('/test', (req, res) => {
    res.status(200).render('test'), err => {
        if (err) {
            msg = 'Failed to render index page.'
            timber.logAndSend(msg);
            console.error(err);
        }
    };
});

app.get('/spotcallback', (req, res) => {
    var code = req.query.code || null;
    var state = req.query.state || null;

    if (state === null) {
        res.render('/');
        console.log('[SPOT ERROR] state_mismatch');
        timber.logAndSend('[SPOT ERROR] state_mismatch', "SPOTIFY");

    } else {
        var authOptions = {
            url: spotTokenURL,
            form: {
                code: code,
                redirect_uri: spotURI,
                grant_type: 'authorization_code'
            },
            headers: {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + (new Buffer.from(spotClientID + ':' + spotClientSecret).toString('base64'))
            },
            json: true
        };
        // TODO: send and store this to the database through rmq!!!
    }
    // request.post(authOptions, function (error, response, body) {
    //     var access_token = body.access_token;
    //     var refresh_token = body.refresh_token;
    //     var options = {
    //         url: spotAPIURL + 'me',
    //         headers: { 'Authorization': 'Bearer ' + access_token },
    //         json: true
    //     };
    //     // use the access token to access the Spotify Web API
    //     request.get(options, function (error, response, body) {
    //         console.log(body);
    //     });
    //     // we can also pass the token to the browser to make requests from there
    //     res.redirect('/#' +
    //         querystring.stringify({
    //             access_token: access_token,
    //             refresh_token: refresh_token
    //         }));
    // });
});

app.get('/spotLog', (req, res) => {
    // var state = generateRandomString(16);
    var scope = 'user-read-private user-read-email user-library-modify playlist-modify-private playlist-modify-public playlist-read-private playlist-read-collaborative user-library-read user-top-read user-read-recently-played user-read-playback-state user-modify-playback-state user-read-currently-playing';
    //var scope = 'user-library-modify playlist-read-private playlist-read-collaborative user-read-recently-played user-top-read';
    console.log('spotClientID = ', spotClientID);
    console.log('spotURI = ', spotURI);
    res.redirect(`https://accounts.spotify.com/authorize?` + querystring.stringify({ response_type: 'code', client_id: spotClientID, scope: scope, redirect_uri: spotURI })), err => {
        if (err) {
            msg = 'Failed to redirect to spotify.'
            timber.logAndSend(msg);
            console.error(err);
        }
        else {
            console.log('redirected to spotify');

        }
    };
});

app.get('/callback', function (req, res) {

    var code = req.query.code || null;
    var state = req.query.state || null;

    if (state === null) {
        res.redirect('/#' +
            querystring.stringify({
                error: 'state_mismatch'
            }));
    } else {
        var authOptions = {
            url: 'https://accounts.spotify.com/api/token',
            form: {
                code: code,
                redirect_uri: redirect_uri,
                grant_type: 'authorization_code'
            },
            headers: {
                'content-type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + (new Buffer.from(client_id + ':' + client_secret).toString('base64'))
            },
            json: true
        };
    }
});

/**
 * =====================================================
 * SPOTIFY USER TESTING ENDS HERE
 * =====================================================
 */



try {
    https = require('https');
    console.log("Seems like we're good to go with https!");
} catch (err) {
    console.log('https module not found, using http instead');
    https = require('http');
}


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
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${tempHost}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    typeOf = req.params.param;
    console.log('\n[Posting to /account:param] with typeOf: ', typeOf, '\n');
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
    else if (page == 'artists') {
        const tempHost = process.env.BROKER_VHOST;
        const tempQueue = process.env.BROKER_QUEUE;
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
            if (response.returnCode === '0') {
                console.log('[Approx Line 181] Success reponse query artist\n');
                console.log(response.data.name);
                // timber.logAndSend('User logged in successfully.');
                data = response.data;
                musicdata = response.music;
                console.log("\n[Approx line 186] testing query artist data");
                // let tracks = [];
                // let artists = [];
                // let links = [];
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
                    let checkSession = ""; // call the db server and see if the session is valid
                    if (page === 'account') {
                        // req.session.data = response.data; //added to help retain data

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
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
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
                console.log("\n\nwe made it to getRecs, here's response.music/musicdata\n");
                console.log(musicdata);
                console.log("\n['account'] \ttesting musicdata\n");
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
            musicdata = response.music;
            console.log("testing musicdata");
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            res.render('account', { data: data, tracks: tracks, artists: artists, links: links });
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
        if (response.returnCode == "0") {
            // Set a cookie for userid to track locally; this will be used to validate session
            console.log("\n[Register - response] Successful registration, parsing data\n");
            data = response.data;
            musicdata = response.music;
            console.log("[Register - response] testing musicdata");
            console.log('\n', musicdata, '\n');
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
            res.status(401).send('You have failed to register.');
            // add handling for render isntead that prints message to user
        }
    });
});


const httpsServer = https.createServer(https_options, app);

const newport = 9001;
httpsServer.listen(newport, () => {
    console.log(`Listening on port ${newport}`);
})

// Listen

// app.listen(Port, () => {
// console.log(`Listening on port ${Port}`);
// });