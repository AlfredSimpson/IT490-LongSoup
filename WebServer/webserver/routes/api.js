"use strict";
const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const axios = require('axios');
const querystring = require('querystring');
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


router
    .route("/:param")
    .get((req, res) => {
        var attributes = {}
        attributes['uid'] = uid;
        attributes['loggedIn'] = loggedIn;
        attributes['oAuthed'] = oAuthed;
        attributes['data'] = data;
        attributes['links'] = links;
        attributes['artists'] = artists;
        attributes['tracks'] = tracks;
        console.log(`attributes: ${attributes}, ${attributes['uid']}`);

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
        // let uid = req.body.uid;
        // handle where it goes
        switch (type) {
            case "query":
                // Get the Params to send to the query function
                console.log(`Sending a request to the query function in api.js`);
                let query = req.body.query;
                let queryT = req.body.query_type;
                let by = req.body.by_type;
                let uid = req.body.uid;
                console.log(`[LINE 69] Query: ${query} | Type: ${queryT} | By Type: ${by} | UID: ${uid}`);
                // url encode query
                query = encodeURIComponent(query);
                const amqpURL = `amqp://${SPOTUSER}:${SPOTPASS}@${SPOTHOST}:${SPOTPORT}/${SPOTVHOST}`;
                mustang.sendAndConsumeMessage(amqpURL, SPOTQUEUE, {
                    type: "spot_query",
                    "uid": uid,
                    "queryT": queryT,
                    "query": query,
                    "by": by
                }, (msg) => {
                    const response = JSON.parse(msg.content.toString());
                    if (response.returnCode === 0) {
                        console.log(`Generation success!`);

                        res.status(200).render('success', { oAuthed: oAuthed });
                    } else {
                        res.status(401).send('UGh fuck this ');
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