"use strict";
const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const querystring = require('querystring');
var cache = require('memory-cache');
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

router.use(function (req, res, next) {
    let d = new Date();
    console.log(req.url, "@", d.toTimeString());
    next();
});

// A function, requireAuthentication, which will be used as middleware to check if a user is logged in or not
function requireAuthentication(req, res, next) {
    var loggedIn = req.account_config.loggedIn ?? false;
    if (loggedIn === true) {
        next();
    } else {
        // if the user is not logged in, redirect them to the login page
        res.redirect('/login');
    }
}

function cacheAgain(stuff) {
    console.log('[Cache Again - API] trying to recache stuff');
    // console.log(`stuff is: ${stuff}`);
    // Iterate over a dictionary, and cache each key/value pair
    for (let [key, value] of Object.entries(stuff)) {
        // console.log(`${key}: ${value}`);
        cache.put(key, value);
    }
}

router.get('/', (req, res, next) => {
    var uid = req.account_config.uid;
    var loggedIn = req.account_config.loggedIn ?? false;
    var oAuthed = req.account_config.oAuthed ?? null;
    var data = req.account_config.data ?? null;
    var links = req.account_config.links ?? null;
    var artists = req.account_config.artists ?? null;
    var tracks = req.account_config.tracks ?? null;
    var attributes = {}
    attributes['uid'] = uid;
    attributes['loggedIn'] = loggedIn;
    attributes['oAuthed'] = oAuthed;
    attributes['data'] = data;
    attributes['links'] = links;
    attributes['artists'] = artists;
    attributes['tracks'] = tracks;
    console.log(`attributes: ${attributes}, ${attributes['uid']}`);
    next();
});


router
    .route("/:param")
    .get((req, res) => {
        var attributes = {}
        attributes['uid'] = cache.get('uid');
        attributes['loggedIn'] = cache.get('loggedIn');
        attributes['oAuthed'] = cache.get('oAuthed');
        attributes['data'] = cache.get('data');
        attributes['links'] = cache.get('links');
        attributes['artists'] = cache.get('artists');
        attributes['tracks'] = cache.get('tracks');
        cacheAgain(attributes);
        // console.log(`\n\nattributes: ${uid}, ${loggedIn}, ${oAuthed}, ${data}, ${links}, ${artists}, ${tracks}\n\n`);

        let page = req.params.param;
        // handle where it goes
        switch (page) {
            case "browse":
                break;
            case "query":
                console.log(`This should not have sent from the get section...`);
                break;
            case "get-all-boards":
                var mbURL = `amqp://${MB_USER}:${MB_PASS}@${MB_HOST}:${MB_PORT}/${MB_V}`;
                mustang.sendAndConsumeMessage(mbURL, MB_Q, {
                    type: "loadMessages",
                    uid: cache.get('uid'),
                    board: "all",
                    limit: 20,
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode == 0) {
                        console.log(`Successfully loaded all messages!`);
                        // Send it back to the front client handler.
                        res.status(200).json(response);
                    }
                    else {
                        res.status(401).send('Ugh yo this is not working.');
                    }
                });
                console.log('Switch case statement - get-all-boards');
                break;
            case "get-punk-boards":
                console.log(`Switch case statement - get-punk-boards\n\n`);
                break;
            case "get-pop-boards":
                console.log(`Switch case statement - get-pop-boards\n\n`);
                break;
            case "get-rap-boards":
                console.log(`Switch case statement - get-rap-boards\n\n`);
                break;
            case "get-messages":
                console.log(`Switch case statement - get-messages\n\n`);
                break;
            default:
                break;
        }
        res.send(page);
    })
    .post((req, res) => {
        let type = req.params.param;
        // handle where it goes
        switch (type) {
            case "query":
                // Get the Params to send to the query function
                var uid = cache.get('uid');
                var query = req.body.query;
                var queryT = req.body.query_type;
                var by = req.body.by_type;
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
                        console.log(`Generation success!`);
                        // Send it back to the front client handler.
                        res.status(200).json(response);
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
                console.log(`[API] \t Received like-dislike request by ${uid}`);
                var spotted_id = req.body.rowId; // The track/artist/album id (whatever was requested)
                var like_type = req.body.action; // the like_type (like/dislike)
                var query_type = req.body.query_type; // the query type (track/artist/album)
                console.log(`[API] \t Received like-dislike request by ${uid} for ${spotted_id} to ${like_type} it for query type ${query_type}`);

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

                    }
                    else {
                        // res.status(401).send('Something went wrong');
                    }
                });

            case "get-all-boards":
                console.log('Switch case statement - get-all-boards');
                break;
            case "get-punk-boards":
                console.log(`Switch case statement - get-punk-boards\n\n`);
                break;
            default:
                break;
        }
        // res.send(page);
    });


module.exports = router;