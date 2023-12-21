"use strict";
const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const querystring = require('querystring');
var cache = require('memory-cache');
const jwt = require('jsonwebtoken');
const jwtDecode = require('jwt-decode');
const cookieParser = require('cookie-parser');
const multer = require('multer')

// My own modules
const timber = require('../lumberjack.js');
const mustang = require('../mustang.js');


require('dotenv').config();

// AMQP Constants for spotify queues and stuff

const SPOTHOST = process.env.SPOT_HOST;
const SPOTPORT = process.env.SPOT_PORT;
const SPOTUSER = process.env.SPOT_USER;
const SPOTPASS = process.env.SPOT_PASS;
const SPOTVHOST = process.env.SPOT_VHOST;
const SPOTEXCHANGE = process.env.SPOT_EXCHANGE;
const SPOTQUEUE = process.env.SPOT_QUEUE;

//AMQP For Profiles

const PRO_HOST = process.env.PROFILE_HOST;
const PRO_PORT = process.env.PROFILE_PORT;
const PRO_USER = process.env.PROFILE_USER;
const PRO_PASS = process.env.PROFILE_PASS;
const PRO_VHOST = process.env.PROFILE_VHOST;
const PRO_X = process.env.PROFILE_EXCHANGE;
const PRO_Q = process.env.PROFILE_QUEUE;



// AMQP Constants for main broker /DBWorker queues

const DB_HOST = process.env.BROKER_HOST;
const DB_PORT = process.env.BROKER_PORT;
const DB_EX = process.env.BROKER_EXCHANGE;
const DB_Q = process.env.BROKER_QUEUE;
const DB_USER = process.env.BROKER_USERNAME;
const DB_PASS = process.env.BROKER_PASSWORD;
const DB_V = process.env.BROKER_VHOST;


const MB_HOST = process.env.MBOARD_HOST;
const MB_PORT = process.env.MBOARD_PORT;
const MB_USER = process.env.MBOARD_USER;
const MB_PASS = process.env.MBOARD_PASS;
const MB_V = process.env.MBOARD_VHOST;
const MB_EX = process.env.MBOARD_EXCHANGE;
const MB_Q = process.env.MBOARD_QUEUE;


router.use(cookieParser());
router.use(function (req, res, next) {
    let d = new Date();
    console.log(req.url, "@", d.toTimeString());
    next();
});

// A function, requireAuthentication, which will be used as middleware to check if a user is logged in or not
function requireAuthentication(req, res, next) {
    let token = req.cookies.token;
    var decoded = jwtDecode.jwtDecode(token);
    var loggedIn = decoded.loggedIn ?? false;
    // var loggedIn = req.account_config.loggedIn ?? false;
    if (loggedIn === true) {
        next();
    } else {
        // if the user is not logged in, redirect them to the login page
        res.redirect('/login');
    }
}

function authenticateToken(req, res, next) {
    const token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    var uid = decodedToken.uid;
    if (!token) return res.sendStatus(401);
    jwt.verify(token, process.env.SESSION_SECRET_KEYMAKER, (err, user) => {
        if (err) return res.status(403).send('Man we goofed up here...');
        req.user = user;
        next();
    });
}

function decodeToken(token) {
    var decodedToken = jwtDecode.jwtDecode(token);
    return decodedToken;
}

function getUID(token) {
    var decodedToken = jwtDecode.jwtDecode(token);
    var uid = decodedToken.uid;
    return uid;
}

router.use(authenticateToken);

router.get('/', (req, res, next) => {
    var token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    var profilemusic = req.cookies.profilemusic;
    var decodedProfileMusic = jwtDecode.jwtDecode(profilemusic);
    var uid = decodedToken.uid;
    var loggedIn = decodedToken.loggedIn ?? false;
    var oAuthed = decodedToken.oAuthed ?? null;
    var data = decodedToken.data ?? null;
    var links = decodedProfileMusic.links ?? null;
    var artists = decodedProfileMusic.artists ?? null;
    var tracks = decodedProfileMusic.tracks ?? null;
    var attributes = {}
    attributes['uid'] = uid;
    attributes['loggedIn'] = loggedIn;
    attributes['oAuthed'] = oAuthed;
    attributes['data'] = data;
    attributes['links'] = links;
    attributes['artists'] = artists;
    attributes['tracks'] = tracks;
    // console.log(`attributes: ${attributes}, ${attributes['uid']}`);
    next();
});

function updateProfile(profile_field, field_data, privacy, uid) {
    console.log('[API] \t Updating profile');
    console.log(`[API] \t Profile field is ${profile_field}, field data is ${field_data}, privacy is ${privacy} and uid is ${uid}`);
    // return 1;
    var amqpURL = `amqp://${PRO_USER}:${PRO_PASS}@${PRO_HOST}:${PRO_PORT}/${PRO_VHOST}`;
    mustang.sendAndConsumeMessage(amqpURL, PRO_Q, {
        type: "updateProfile",
        uid: uid,
        profile_field: profile_field,
        field_data: field_data,
        privacy: privacy
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        console.log(`[API] \t Response is ${response}`);
        return response;
    });
}

router
    .route("/:param")
    .get((req, res) => {
        var token = req.cookies.token;
        var decodedToken = jwtDecode.jwtDecode(token);
        var profilemusic = req.cookies.profilemusic;
        var decodedProfileMusic = jwtDecode.jwtDecode(profilemusic);
        var uid = decodedToken.uid;
        var loggedIn = decodedToken.loggedIn ?? false;
        var oAuthed = decodedToken.oAuthed ?? null;
        var data = decodedToken.data ?? null;
        var links = decodedProfileMusic.links ?? null;
        var artists = decodedProfileMusic.artists ?? null;
        var tracks = decodedProfileMusic.tracks ?? null;
        var attributes = {}
        attributes['uid'] = uid;
        attributes['loggedIn'] = loggedIn;
        attributes['oAuthed'] = oAuthed;
        attributes['data'] = data;
        attributes['links'] = links;
        attributes['artists'] = artists;
        attributes['tracks'] = tracks;
        let page = req.params.param;
        // handle where it goes
        switch (page) {
            case "browse":
                break;
            case "query":
                // console.log(`This should not have sent from the get section...`);
                break;
            case "get-all-boards":
                var mbURL = `amqp://${MB_USER}:${MB_PASS}@${MB_HOST}:${MB_PORT}/${MB_V}`;
                mustang.sendAndConsumeMessage(mbURL, MB_Q, {
                    type: "loadMessages",
                    uid: uid,
                    board: "all",
                    limit: 20,
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    // console.log(`[API] \t Received response: ${response}`);
                    let msgs = response.messages;

                    if (res.headersSent) {
                        console.log(`[API] \t Headers already sent, returning`);
                        return;
                    }
                    if (response.returnCode == 0) {
                        // console.log(`\n\nSuccessfully loaded all messages!\n\n`);
                        // Send it back to the front client handler.
                        res.status(200).json(msgs);
                    }
                    else {
                        res.status(500).send('Ugh yo this is not working.');
                    }
                });
                break;
            default:
                res.send(page);
                break;
        }
    })
    .post((req, res) => {
        let type = req.params.param;
        // handle where it goes
        switch (type) {
            case "updateProfile":
                console.log(`[API] \t Updating profile`);
                var profile_field = req.body.profile_field;
                console.log(`[API] \t Profile field is ${profile_field}`);
                var field_data = req.body.field_data;
                var privacy = req.body.privacy;
                var token = req.cookies.token;
                var uid = getUID(token);
                var amqpURL = `amqp://${PRO_USER}:${PRO_PASS}@${PRO_HOST}:${PRO_PORT}/${PRO_VHOST}`;
                mustang.sendAndConsumeMessage(amqpURL, PRO_Q, {
                    type: "updateProfile",
                    uid: uid,
                    profile_field: profile_field,
                    field_data: field_data,
                    privacy: privacy
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    console.log(`[API] \t Response is ${response.returnCode}`);
                    if (response.returnCode == 0) {
                        console.log(`Successfully updated profile!`);
                        res.status(200).json(response);
                    }
                    else {
                        res.status(401).json(response);
                    }
                });
                // let response = updateProfile(profile_field, field_data, privacy, uid);
                // console.log(`[API] \t Response is ${response}`);
                // if (response.returnCode == 0) {
                //     console.log(`Successfully updated profile!`);
                //     res.status(200).json(response);
                // }
                // else {

                //     res.status(401).send('Ugh yo this is not working.');
                // }

                break;
            case "uploadProfilePic":
                console.log(`[API] \t Uploading profile pic`);
                // var token = req.cookies.token;
                //! Left on the backburner - this is a bit more complicated than I thought and we have other things to get done.
                break;
            case "set-username":
                break;
            case "add-to-playlist":
                console.log(`[API] \t Adding to playlist`);
                var token = req.cookies.token;
                var uid = getUID(token);
                var track_id = req.body.rowId;
                var action = req.body.action;
                var query_type = req.body.query_type;
                var amqpURL = `amqp://${SPOTUSER}:${SPOTPASS}@${SPOTHOST}:${SPOTPORT}/${SPOTVHOST}`;
                mustang.sendAndConsumeMessage(amqpURL, SPOTQUEUE, {
                    type: "add_to_playlist",
                    uid: uid,
                    track_id: track_id,
                    action: action,
                    query_type: query_type
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode == 0) {
                        console.log(`Successfully added to playlist!`);
                        // Send it back to the front client handler.
                        res.status(200).json(response);
                    }
                    else {
                        res.json(response);
                    }
                });
                break;
            case "query":
                var token = req.cookies.token;
                var uid = getUID(token);
                var query = req.body.query;
                var queryT = req.body.query_type;
                var by = req.body.by_type;
                console.log(`[API] \t Querying ${queryT} by ${by} for ${query}`);
                // url encode query to prevent errors in sending
                query = encodeURIComponent(query);
                var amqpURL = `amqp://${SPOTUSER}:${SPOTPASS}@${SPOTHOST}:${SPOTPORT}/${SPOTVHOST}`;
                mustang.sendAndConsumeMessage(amqpURL, SPOTQUEUE, {
                    type: "spot_query",
                    uid: uid,
                    queryT: queryT,
                    query: query,
                    by: by
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode == 0) {
                        // Send it back to the front client handler.
                        res.status(200).json(response);
                        // console.log(`Successfully added to playlist!`);
                    }
                    else {
                        res.status(401).send('Ugh yo this is not working.');
                    }
                });
                break;
            case "showsuggested":
                break;
            case "like-dislike":
                var uid = cache.get('uid');
                var spotted_id = req.body.rowId; // The track/artist/album id (whatever was requested)
                var like_type = req.body.action; // the like_type (like/dislike)
                var query_type = req.body.query_type; // the query type (track/artist/album)

                var amqpURL = `amqp://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_V}`;

                mustang.sendAndConsumeMessage(amqpURL, DB_Q, {
                    type: "like_event",
                    uid: uid,
                    query_type: query_type,
                    like_type: like_type,
                    spotted_id: spotted_id
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode == 0) {
                        console.log(`Successfully liked or disliked item!`);
                        console.log(`[API] \t Response is ${response.message}`);
                        res.status(200).json(response);
                    }
                    else {
                        res.json(response);
                    }
                });
                break;
            case "send-message":
                var token = req.cookies.token;
                var uid = getUID(token);
                var messageContent = req.body.messageContent;
                // var board = req.body.board;
                var board = "alltalk";
                var mbURL = `amqp://${MB_USER}:${MB_PASS}@${MB_HOST}:${MB_PORT}/${MB_V}`;
                mustang.sendAndConsumeMessage(mbURL, MB_Q, {
                    type: "postMessage",
                    uid: uid,
                    message: messageContent,
                    board: board
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode == 0) {
                        console.log(`Successfully sent message!`);
                        // Send it back to the front client handler.
                        res.status(200).json(response);
                    }
                    else {
                        res.status(401).send('Ugh yo this is not working.');
                    }
                });
                break;
            default:
                break;
        }
        // res.send(page);
    });


module.exports = router;