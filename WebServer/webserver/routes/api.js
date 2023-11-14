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

// AMQP Constants

const SPOTHOST = process.env.SPOT_HOST;
const SPOTPORT = process.env.SPOT_PORT;
const SPOTUSER = process.env.SPOT_USER;
const SPOTPASS = process.env.SPOT_PASS;
const SPOTVHOST = process.env.SPOT_VHOST;
const SPOTEXCHANGE = process.env.SPOT_EXCHANGE;
const SPOTQUEUE = process.env.SPOT_QUEUE;




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
    console.log('trying to recache stuff');
    console.log(`stuff is: ${stuff}`);
    // Iterate over a dictionary, and cache each key/value pair
    for (let [key, value] of Object.entries(stuff)) {
        console.log(`${key}: ${value}`);
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
    .get(cacheAgain, (req, res) => {
        var attributes = {}
        attributes['uid'] = cache.get('uid');
        attributes['loggedIn'] = cache.get('loggedIn');
        attributes['oAuthed'] = cache.get('oAuthed');
        attributes['data'] = cache.get('data');
        attributes['links'] = cache.get('links');
        attributes['artists'] = cache.get('artists');
        attributes['tracks'] = cache.get('tracks');
        console.log(`\n\nattributes: ${uid}, ${loggedIn}, ${oAuthed}, ${data}, ${links}, ${artists}, ${tracks}\n\n`);

        let page = req.params.param;
        // handle where it goes
        switch (page) {
            case "browse":
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
                let uid = cache.get('uid');
                let query = req.body.query;
                let queryT = req.body.query_type;
                let by = req.body.by_type;
                // url encode query to prevent errors in sending
                query = encodeURIComponent(query);
                const amqpURL = `amqp://${SPOTUSER}:${SPOTPASS}@${SPOTHOST}:${SPOTPORT}/${SPOTVHOST}`;
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
            default:
                break;
        }
        // res.send(page);
    });


module.exports = router;