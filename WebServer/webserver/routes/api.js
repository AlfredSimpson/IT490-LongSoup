"use strict";
const express = require('express');
const router = express.Router();

// My own modules
const timber = require('../lumberjack.js');
const mustang = require('../mustang.js');

// We cam apply middleware here that only applies for this section as well - such as my logic for checking if a user is logged in or not!

// Using a console log as an example.

router.use(function (req, res, next) {
    let d = new Date();
    console.log(req.url, "@", d.toTimeString());
    next();
});


router
    .route("/:param")
    .get((req, res) => {
        console.log('account param');
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
        res.send("Hello, world!");
    });


module.exports = router;