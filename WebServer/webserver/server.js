const express = require('express');
const path = require('path');
const accountsRouter = require('./routes/accountsRouter.js');
const api = require('./routes/api.js');
var cache = require('memory-cache');
const axios = require('axios'); // Helps with AJAX requests
const bcrypt = require('bcrypt'); // Helps us encrypt passwords
const jwt = require('jsonwebtoken'); // Helps us with JWTs
const fs = require('fs'); // Helps us with file system tasks
const querystring = require('querystring'); // Helps us with query strings
var https = require('https');
const jwtDecode = require('jwt-decode');
const cookieParser = require('cookie-parser');

require('dotenv').config();

// My own modules
const timber = require('./lumberjack.js');
const mustang = require('./mustang.js');
const statusMessageHandler = require('./status.js');

// Instantiate the server
const app = express();

// Other Constants
// const Port = process.env.PORT || 9001;
const Port = 443;

const options = {
    key: fs.readFileSync(path.join(__dirname, 'cert/key.pem')),
    cert: fs.readFileSync(path.join(__dirname, 'cert/cgs-cert.pem'))
}



// AMQP Constants
const broker_vHost = process.env.BROKER_VHOST;
const broker_Queue = process.env.BROKER_QUEUE;


// Constants used by RMQ

// Set the Constants for Spotify
const REDIRECT_URI = process.env.SPOT_TEST_URI;
const CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
const spotAuthURL = process.env.SPOTIFY_AUTH_URL;
const spotTokenURL = process.env.SPOTIFY_TOKEN_URL;
const spotAPIURL = process.env.SPOTIFY_API_BASE_URL;



const SPOTHOST = process.env.SPOT_HOST;
const SPOTPORT = process.env.SPOT_PORT;
const SPOTUSER = process.env.SPOT_USER;
const SPOTPASS = process.env.SPOT_PASS;
const SPOTVHOST = process.env.SPOT_VHOST;
const SPOTEXCHANGE = process.env.SPOT_EXCHANGE;
const SPOTQUEUE = process.env.SPOT_QUEUE;

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
app.use('/account', express.static(path.join(publicPath, 'account')));
app.use('/account/js', express.static(path.join(publicPath, 'js')));
app.use('/account/css', express.static(path.join(publicPath, 'js')));
app.use(cookieParser());
// Set views and view engine so we can use EJS. Views are the pages, view engine is the template engine
app.set('views', path.join(__dirname, '../views')); // this gets us out of the dir we're in and into the views, for separation
app.set('view engine', 'ejs');



/**
 * These are routing middleware functions. They are called before the request is passed to the router.
 * They are called in the order they are defined.
 * This is important to note and I'm commenting so we all can understand. What they do is tell the express server to use these routers if a request is made to, for example, account/anything or api/anything. Middleware before this should still be called and passed through. 
 */
app.use("/account", function (req, res, next) {
    console.log('no need to send data anymore - we have the jwt token!');
    // req.account_config = {
    //     loggedIn: cache.get('loggedIn'),
    //     uid: cache.get('uid'),
    //     tracks: cache.get('tracks'),
    //     artists: cache.get('artists'),
    //     links: cache.get('links'),
    //     data: cache.get('data'),
    //     oAuthed: cache.get('oAuthed'),
    //     data: cache.get('data'),
    // };
    next();
}, accountsRouter);

// Routing done in accounts.js
app.use("/api", function (req, res, next) {
    console.log('no need to send data anymore - we have the jwt token!')
    let token = req.cookies.token;

    // req.api_config = {
    //     loggedIn: cache.get('loggedIn'),
    //     uid: cache.get('uid'),
    //     tracks: cache.get('tracks'),
    //     artists: cache.get('artists'),
    //     links: cache.get('links'),
    //     data: cache.get('data'),
    //     oAuthed: cache.get('oAuthed'),
    //     data: cache.get('data'),
    // };
    next();
}, api); // Routing done in api.js


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
    // req.session.sessionId = { sessionId: sessionId };
    // res.cookie('sessionId', sessionId, { httpOnly: true });
    // cache.put('sessionId', sessionId, 3600000,);
    return sessionId;
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
    console.log(`\n\n[createUserCookie] usercookieid: ${usercookieid}\n\n`)
    return usercookieid;
};

const getSessionCookie = (req) => {
    let sessionId = req.cookies.sessionId;
    return sessionId;
}


/**
 * getCookies - gets the cookies from the request
 * @param {*} req - a request object
 */
function getCookie(req) {
    // let c = req.cookies.usercookie
    // let cookie = jwtDecode.jwtDecode(c);
    let cookie = req.cookies.usercookie;
    console.log(`\n\n[getCookie] Cookie: ${cookie}\n\n`);
    return cookie;
};


function getUID(token) {
    var decodedToken = jwtDecode.jwtDecode(token);
    var uid = decodedToken.uid;
    return uid;
}


/**
 * =====================================================
 * SPOTIFY USER TESTING BEGINS HERE
 * =====================================================
 */

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
    var userinfo = req.cookies.token;
    var uid = getUID(userinfo) ?? null;
    let usercookie = req.cookies.usercookie;

    console.log(`\n\n[Callback] thecooks: ${uid}\n\n`);
    const code = req.query.code || null;
    try {
        console.log(`\n\n[Callback] code: ${code}\n\n`);
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
            // console.log('\n[Callback] Received response from Spotify, parsing it...\n');
            // Probably can clean this up and import up top before sending to production
            var spotvHost = process.env.BROKER_VHOST;
            var spotQueue = process.env.BROKER_QUEUE;
            const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(spotvHost)}`;
            // All of the data we need to send to the broker so that we can get the user's Spotify data
            let access_token = response.data.access_token;
            let refresh_token = response.data.refresh_token;
            let expires_in = response.data.expires_in;
            let token_type = response.data.token_type;

            mustang.sendAndConsumeMessage(amqpUrl, spotQueue, {
                type: "spotToken",
                "uid": uid,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "token_type": token_type
            }, (msg) => {
                const response = JSON.parse(msg.content.toString());
                if (response.returnCode === 0) {
                    console.log(`[Spotify Token Grab] Success!`);
                    timber.logAndSend('User requested some jams, got some.', "_SPOTIFY_");
                    // cache.put('oAuthed', true, 3600000);
                    let oAuth = true;
                    let oAuthed = jwt.sign({ oAuthed: oAuth }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '45m' });
                    res.cookie('oAuthed', oAuthed, { httpOnly: true, secure: true });
                    res.status(200).render('success', { oAuthed: oAuth });
                } else {
                    console.log(`[Spotify Token Grab] Failure!`);
                    res.status(401).send('You have failed to authorize Spotify - did we do something?');
                }
            }
            );
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



app.get("/:page", (req, res) => {
    page = req.params.page;
    console.log(`page: ${page}`);
    var errorStatus = null;
    var errorOutput = null;
    data = { errorStatus: errorStatus, errorOutput: errorOutput };
    switch (page) {
        case "login":
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
        case "authenticate":
            // ! We'll disable this later as it should only be rendered from post/login
            data = { origin_: "authentication", errorStatus: errorStatus, errorOutput: errorOutput };
            res.status(200).render('authenticate', { data }), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render authenticate page.`
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
        // case "account":
        //     res.status(200).render('account', { data }), err => {
        //         if (err) {
        //             d = new Date();
        //             d = d.toTimeString();
        //             msg = `${d} : Failed to render account page.`
        //             timber.logAndSend(msg);
        //         }
        //     }
        //     break;
        case "backdoor":
            res.status(200).render('testinglogin'), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render backdoor page.`
                    timber.logAndSend(msg);
                }
            };
        default:
            res.status(200).render('index'), err => {
                if (err) {
                    d = new Date();
                    d = d.toTimeString();
                    msg = `${d} : Failed to render index page.`
                    timber.logAndSend(msg);
                }
            };
            break;
    }
});

app.get('/api/:param', (req, res) => {
    let type = req.params.param;
    // var uid = cache.get('uid');
    // handle where it goes
    switch (type) {
        case "query":
            const queryT = req.query.queryT;
            const query = req.query.query;
            const by = req.query.by_type;
            let token = req.cookies.token;
            var uid = getUID(token) ?? null;
            query = encodeURIComponent(query);
            console.log(`Sending a request to the query function in server.js`);
            console.log(`queryT: ${queryT}, query: ${query}, by: ${by}`);
            break;
        case 'oops':
            break;
        default:
            break;
    }
});

app.post('/account', (req, res) => {
    const genre = req.body.genres;
    const popularity = req.body.pop;
    const valence = req.body.vibe;
    console.log(`\ngenre: ${genre}, popularity: ${popularity}, valence: ${valence}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(broker_vHost)}`;
    mustang.sendAndConsumeMessage(amqpUrl, broker_Queue, {
        type: "simplerecs",
        genre,
        popularity,
        valence
    }, (msg) => {
        try {
            const response = JSON.parse(msg.content.toString());
            if (response.returnCode === 0) {
                console.log("\n['/account'] Success!");
                timber.logAndSend('\n[Account Post]\tUser requested some jams, got some.\n');
                data = response.data;
                musicdata = response.music
                userinfo = response.userinfo;
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
                let t = req.cookies.token;
                let uid = getUID(t) ?? null;
                let loggedIn = jwtDecode.jwtDecode(t).loggedIn ?? false;
                let authCookie = req.cookies.oAuthed;
                let oAuthed = jwtDecode.jwtDecode(authCookie);
                oAuthed = oAuthed.oAuthed;

                console.log('\n[Account] Setting session data\n');
                // set jwt tokens
                const profilemusic = jwt.sign({ tracks: tracks, artists: artists, links: links }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '1h' });
                const token = jwt.sign({ data: data, uid: uid, loggedIn: loggedIn, userinfo: userinfo }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '1h' });
                res.cookie('profilemusic', profilemusic, { httpOnly: true, secure: true });
                res.cookie('token', token, { httpOnly: true, secure: true });
                res.render('account', { data: data, tracks: tracks, artists: artists, links: links, oAuthed: oAuthed, uid: uid });
            } else {
                console.log("Failure!");
                console.log("Sending response data");
                console.log("Showing data");
                console.log(musicdata);
                res.status(401).render('account', musicdata);
            }
        } catch (error) {
            console.log("Error:", error);
            res.status(500).send("An error occurred");
        }
    });
});



/**
 * =====================================================
 * USER REGISTRATION BEGINS HERE
 * =====================================================
 * This is the login process after a user has clicked login.
 */

app.post('/login', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    // Check to see if a session cookie exists, if not call the create sessionCookie function
    let session_id = createSessionCookie(req, res);

    let usercookieid = createUserCookie(req, res);

    console.log(`session cookie Created?: ${session_id}`);
    console.log(`user cookie Created?: ${usercookieid}`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(broker_vHost)}`;
    console.log(amqpUrl);

    getCookie(req);

    mustang.sendAndConsumeMessage(amqpUrl, broker_Queue, {
        type: "login",
        "useremail": useremail,
        "password": password,
        "session_id": session_id,
        "usercookieid": usercookieid
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === 0) {
            timber.logAndSend('User logged in successfully.');
            data = response.data;
            userinfo = response.userinfo;
            // cache.put('uid', userinfo.uid, 3600000);
            // cache.put('name', userinfo.name, 3600000);
            // cache.put('spot_name', userinfo.spot_name, 3600000);
            // cache.put('data', data, 3600000);
            let authed = response.authenticated;
            console.log(`authed: ${authed}, uid = ${userinfo.uid}`);

            res.status(200).render('authenticate', { data: data, authed: authed, userinfo: userinfo });
        }
        else {
            let errorMSG = 'You have failed to login.';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            // let outcome = response.data['loggedin'];
            console.log("Sending response data");
            // console.log(response.data['loggedin']);
            data = response.data;
            data.errorStatus = true;
            console.log("showing data");
            console.log(data);
            res.status(401).render('login', { data });
        }
    });
});

app.post('/authenticate', (req, res) => {
    let t = req.cookies.token;
    let uid = getUID(t) ?? null;
    console.log(`\n\n[authenticate] We're in authenticate\n\n`);
    console.log(`\n\n[authenticate] uid: ${uid}\n\n`);
    const authcode = req.body.authCode;
    console.log(`\n\n[authenticate] authcode: ${authcode}\n\n`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(broker_vHost)}`;
    mustang.sendAndConsumeMessage(amqpUrl, broker_Queue, {
        type: "auth_login",
        "uid": uid,
        "auth_code": authcode
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === 0) {
            console.log(`\n\n[authenticate] Success!\n\n`);
            // Now we need to get the rest of the data from DBWorker originally sent during do_login...
            timber.logAndSend('User authenticated successfully.');
            data = response.data;
            musicdata = response.music;
            userinfo = response.userinfo;
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            console.log('\n[Login] Setting session data\n');
            // cache.put('uid', userinfo.uid, 3600000);
            // console.log(`uid is ${userinfo.uid}`);
            // cache.put('name', userinfo.name, 3600000);
            let loggedIn = true;
            let t = req.cookies.token;
            let uid = getUID(t) ?? null;
            // let uid = cache.get('uid');
            // cache.put('loggedIn', loggedIn, 3600000);
            // cache.put('tracks', tracks, 3600000);
            // cache.put('artists', artists, 3600000);
            // cache.put('links', links, 3600000);
            // cache.put('data', data, 3600000);
            // let oAuthed = cache.get('oAuthed');
            let oAuthed = false; // setting to false so whenever logging in we can authorize it.
            const token = jwt.sign({ data: data, oAuthed: oAuthed, uid: uid, loggedIn: loggedIn }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '3h' });
            const profilemusic = jwt.sign({ tracks: tracks, artists: artists, links: links }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '3h' });
            res.cookie('token', token, { httpOnly: true, secure: true });
            res.cookie('profilemusic', profilemusic, { httpOnly: true, secure: true });

            res.status(200).render('account', { data: data, tracks: tracks, artists: artists, links: links, oAuthed: oAuthed, uid: uid });
        }
        else {
            console.log(`\n\n[authenticate] Failure!\n\n`);
            res.status(403).send('Your authentication code was incorrect. Pitiful.');
        }
    });
});

app.post('/backdoor', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    // Check to see if a session cookie exists, if not call the create sessionCookie function
    var session_id = createSessionCookie(req, res);

    var usercookieid = createUserCookie(req, res);
    const usercookie = jwt.sign({ usercookieid: usercookieid }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '3h' });
    res.cookie('usercookie', usercookie, { httpOnly: true, secure: true });

    console.log(`session cookie Created?: ${session_id}`);
    console.log(`\n\n[BACKDOOR] user cookie Created?: ${usercookieid}\n\n`);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(broker_vHost)}`;
    console.log(amqpUrl);


    mustang.sendAndConsumeMessage(amqpUrl, broker_Queue, {
        type: "backdoor",
        "useremail": useremail,
        "password": password,
        "session_id": session_id,
        "usercookieid": usercookieid
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === 0) {
            timber.logAndSend('\nUser logged in successfully.\n');
            data = response.data;
            musicdata = response.music;
            userinfo = response.userinfo;
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            console.log('\n[BACKDOOR] Setting session data\n');
            // cache.put('uid', userinfo.uid, 3600000);
            // console.log(`uid is ${userinfo.uid}`);
            // cache.put('name', userinfo.name, 3600000);
            let loggedIn = true;


            let uid = userinfo.uid;
            let oAuthed = false;
            console.log(`Attempting to set JWT token`);
            // context = { data: data, tracks: tracks, artists: artists, links: links, oAuthed: oAuthed, uid: uid };
            const token = jwt.sign({ data: data, oAuthed: oAuthed, uid: uid, loggedIn: loggedIn }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '3h' });
            const profilemusic = jwt.sign({ tracks: tracks, artists: artists, links: links }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '3h' });
            res.cookie('token', token, { httpOnly: true, secure: true });
            res.cookie('profilemusic', profilemusic, { httpOnly: true, secure: true });
            console.log(`\n\n[BACKDOOR] token: ${token}\n\n`);
            /**
             * END JWT STUFF HERE
             */
            res.status(200).render('account', { data: data, tracks: tracks, artists: artists, links: links, oAuthed: oAuthed, uid: uid });
            //res.redirect('/account');
        } else {
            let errorMSG = 'You have failed to login.';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            // let outcome = response.data['loggedin'];
            console.log("Sending response data");
            // console.log(response.data['loggedin']);
            data = response.data;
            data.errorStatus = true;
            console.log("showing data");
            console.log(data);
            res.status(401).render('login', { data });
        }
    });
});

app.post('/register', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const first_name = req.body.first_name;
    const last_name = req.body.last_name;
    const spot_name = req.body.spot_name;
    let session_id = createSessionCookie(req, res);
    let usercookieid = createUserCookie(req, res);
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(broker_vHost)}`;

    getCookie(req); // Might not work anymore!

    mustang.sendAndConsumeMessage(amqpUrl, broker_Queue, {
        type: "register",
        "useremail": useremail,
        "password": password,
        "session_id": session_id,
        "usercookieid": usercookieid,
        "first_name": first_name,
        "last_name": last_name,
        "spot_name": spot_name
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode == 0) {
            timber.logAndSend('[REGISTRATION] User registered successfully.', "_REGISTRATION_");
            data = response.data;
            musicdata = response.music;
            userinfo = response.userinfo;
            let tracks = [];
            let artists = [];
            let links = [];
            for (var i = 0; i < musicdata.length; i++) {
                tracks.push(musicdata[i].track);
                artists.push(musicdata[i].artist);
                links.push(musicdata[i].url);
            }
            cache.put('uid', userinfo.uid, 3600000);
            cache.put('name', userinfo.name, 3600000);
            let loggedIn = true;
            let uid = userinfo.uid;
            // cache.put('loggedIn', loggedIn, 3600000);
            // cache.put('tracks', tracks, 3600000);
            // cache.put('artists', artists, 3600000);
            // cache.put('links', links, 3600000);
            // cache.put('data', data, 3600000);
            let oAuthed = false; // If they're registering they did not oAuth.
            // console.log(`We are passing oAuthed: ${oAuthed}, uid: ${uid}, loggedIn: ${loggedIn}, data: ${data}, tracks: ${tracks}, artists: ${artists}, links: ${links}`)
            const token = jwt.sign({ data: data, uid: uid, loggedIn: loggedIn }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '1h' });
            const profilemusic = jwt.sign({ tracks: tracks, artists: artists, links: links }, process.env.SESSION_SECRET_KEYMAKER, { expiresIn: '1h' });
            res.cookie('token', token, { httpOnly: true, secure: true });
            res.cookie('profilemusic', profilemusic, { httpOnly: true, secure: true });
            res.status(200).render('account', { data: data, tracks: tracks, artists: artists, links: links, oAuthed: oAuthed, uid: uid });
        } else {
            data = { "errorStatus": true, "errorOutput": "You have failed to register." };
            res.status(401).render('register', { data });
        }
    }
    );
});


// app.listen(9001, () => {
//     console.log('Listening on port 9001');
// });
const server = https.createServer(options, app);

server.listen(Port, () => {
    console.log(`Listening on port ${Port}`);
});