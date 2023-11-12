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
                let query = req.body.query;
                let query_type = req.body.query_type;
                // url encode query
                query = encodeURIComponent(query);
                const amqpURL = `amqp://${SPOTUSER}:${SPOTPASS}@${SPOTHOST}:${SPOTPORT}/${SPOTVHOST}`;
                mustang.sendAndConsumeMessage(amqpURL, SPOTQUEUE, {
                    type: "spot_query",
                });
                return "hi"; // Keep hi here for a few until we come back and add the query to the db
                break;
            case "showsuggested":
                break;

            default:
                break;
        }
        res.send(page);
    });


module.exports = router;