"use strict";
const express = require('express');
const router = express.Router();
const timber = require('../lumberjack.js');
const mustang = require('../mustang.js');
var cache = require('memory-cache');
const cookieParser = require('cookie-parser');
const path = require('path');
const jwt = require('jsonwebtoken');
// We cam apply middleware here that only applies for this section as well - such as my logic for checking if a user is logged in or not!

router.use(cookieParser());




router.use(function (req, res, next) {
    let d = new Date();
    console.log(req.url, "@", d.toTimeString());
    // console.log(`accountPath: ${accountPath}`);
    console.log(`req.url: ${req.url}`);
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
    console.log('\n\ntrying to recache stuff');
    console.log(`\n\nstuff is: ${stuff}`);
    // Iterate over a dictionary, and cache each key/value pair
    for (let [key, value] of Object.entries(stuff)) {
        console.log(`\n${key}: ${value}`);
        cache.put(key, value);
    }
}

//! Added this, can delete. 
//TODO: Fix or delete
function authenticateToken(req, res, next) {
    console.log('[SERVER.JS]attempting to authenticate the token');
    const token = req.cookies.token;
    console.log(`token is: ${token}`);
    if (!token) return res.sendStatus(401);

    jwt.verify(token, process.env.SESSION_SECRET_KEYMAKER, (err, user) => {
        if (err) return res.status(403).send('Man we goofed up here...');
        req.user = user;
        next();
    });
}

router.use(authenticateToken);

// router.all('*', requireAuthentication);
router.get('/', requireAuthentication, (req, res) => {

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
    cacheAgain(attributes);
    var accountPath = path.join(__dirname, '../../views/account.ejs');
    res.render(accountPath, {
        loggedIn: loggedIn,
        uid: uid,
        tracks: tracks,
        artists: artists,
        links: links,
        data: data,
        oAuthed: oAuthed
    });
});


router.route("/:page")
    .get(requireAuthentication, (req, res) => {
        console.log('checking for page in the accounts router');
        var page = req.params.page;
        var viewPath = path.join(__dirname, '../../views/account/', page + '.ejs');
        console.log('__dirname is: ', __dirname);
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
        switch (page) {
            case "":
                console.log(`Rendering ${page}...Is it blank ? `);
                break;
            case "account":
                console.log(`Rendering ${page}...Is it account ? `);
                break;
            case 'stats':
                console.log(`passing through the stats page... `);
            case 'messageboard':
                console.log(`passing through the messageboard case...`);
            case 'browse':
                // const viewPath = path.join(__dirname, '../../views/account/', page + '.ejs');
                // console.log('viewPath is: ', viewPath);

                console.log(`Rendering ${page}...`);
                res.status(200).render(viewPath, {
                    // your context objects here
                });
                break;
            default:
                console.log(`Unknown request: ${page}`);
                res.status(404).send('Page not found');
                break;
        }
    })
    .post((req, res) => {
        res.send("Hello, world!");
    }
    );

// Additional handlers (like POST, PUT, etc.) can be chained here if needed in the future



// accounts/:param
// router.get("/:page", (req, res) => {
//     var page = req.params.page;
//     // page = path.join(accountPath, page + '.ejs');
//     console.log(`Requesting ${ page }...`);
//     const viewPath = path.join(__dirname, '../views/account/', page + '.ejs');
//     console.log(`Requesting ${ viewPath }... - but where is it ? `);

//     // handle where it goes
//     switch (page) {
//         case "/":
//             console.log(`Requesting ${ page }...`);
//             res.render('account', {
//                 loggedIn: loggedIn,
//                 uid: uid,
//                 tracks: tracks,
//                 artists: artists,
//                 links: links,
//                 data: data

//             })
//             break;
//         case "account":
//             console.log(page);
//             res.render('account', {
//                 loggedIn: loggedIn,
//                 uid: uid,
//                 tracks: tracks,
//                 artists: artists,
//                 links: links,
//                 data: data

//             })
//             break;
//         case "browse":
//             console.log(`passed to switch case ${ page }...`);
//             res.render('browse', {
//                 loggedIn: loggedIn,
//                 uid: uid,
//                 tracks: tracks,
//                 artists: artists,
//                 links: links,
//                 data: data

//             });
//             break;
//         default:
//             console.log(page);
//             break;
//     }
//     res.send('we could not find what you were looking for...');
// })
//     .post((req, res) => {
//         res.send("Hello, world!");
//     });



module.exports = router;