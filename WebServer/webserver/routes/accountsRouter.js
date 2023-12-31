"use strict";
const express = require('express');
const router = express.Router();
const timber = require('../lumberjack.js');
const mustang = require('../mustang.js');
// var cache = require('memory-cache');
const cookieParser = require('cookie-parser');
const path = require('path');
const jwt = require('jsonwebtoken');
const jwtDecode = require('jwt-decode');
const axios = require('axios');
require('dotenv').config();


// We cam apply middleware here that only applies for this section as well - such as my logic for checking if a user is logged in or not!

router.use(cookieParser());

router.use(function (req, res, next) {
    let d = new Date();
    console.log(req.url, "@", d.toTimeString());
    console.log(`req.url: ${req.url}`);
    next();
});

// A function, requireAuthentication, which will be used as middleware to check if a user is logged in or not
function requireAuthentication(req, res, next) {
    let token = req.cookies.token;
    var decoded = jwtDecode.jwtDecode(token);
    var loggedIn = decoded.loggedIn;
    var loggedIn = loggedIn ?? false;
    // console.log(`\n\n[ACCOUNTS MIDDLEWARE] loggedIn is: ${loggedIn}`);

    if (loggedIn === true) {
        next();
    } else {
        res.redirect('/login');
    }
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


function authenticateToken(req, res, next) {
    const token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    // console.log(`\n\n[MIDDLEWARE - ACCOUNTS] decodedToken is: ${decodedToken}`);
    var uid = decodedToken.uid;
    // console.log(`\n\n[MIDDLEWARE- ACCOUNTS] uid is: ${uid}`);
    if (!token) return res.sendStatus(401);
    jwt.verify(token, process.env.SESSION_SECRET_KEYMAKER, (err, user) => {
        if (err) return res.status(403).send('Man we goofed up here...');
        req.user = user;
        next();
    });
}


async function getUserProfile(req, res, next) {
    const token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    var uid = decodedToken.uid;
    var loggedIn = decodedToken.loggedIn ?? false;
    var oAuthed = decodedToken.oAuthed ?? null;
    var data = decodedToken.data ?? null;
    var userinfo = decodedToken.userinfo ?? null;
    console.log(`[ACCOUNTS ROUTER] getUserProfile() called`);
    return attributes;
}

function getOtherUserData(uid, username) {
    // using axios we will request the data from our database related to the username. It uses the requester's uid and the requested username to get the data
    // and then returns the data as an object
    console.log(`[ACCOUNTS ROUTER - get other user data] getOtherUserData() called`);
    console.log(`[ACCOUNTS ROUTER] uid is: ${uid}`);
    console.log(`[ACCOUNTS ROUTER] username is: ${username}`);

    const pro_host = process.env.PROFILE_HOST;
    const pro_port = process.env.PROFILE_PORT;
    const pro_v = process.env.PROFILE_VHOST;
    const pro_user = process.env.PROFILE_USER;
    const pro_pass = process.env.PROFILE_PASS;
    const pro_q = process.env.PROFILE_QUEUE;
    const pro_x = process.env.PROFILE_EXCHANGE;
    const amqpUrl = `amqp://${pro_user}:${pro_pass}@${pro_host}:${pro_port}/${encodeURIComponent(pro_v)}`;
    console.log(`[ACCOUNTS ROUTER] amqpUrl is: ${amqpUrl}`);
    mustang.sendAndConsumeMessage(amqpUrl, pro_q, {
        "type": "load_profile",
        "username": username,
        "uid": uid
    }, (response) => {
        if (response.returnCode == 0) {
            console.log(`[ACCOUNTS ROUTER] Success!`);
            let profile = response.profile;
            console.log(`getOtherUserData() profile is: ${profile}`);
            return profile
        } else {
            console.log(`[ACCOUNTS ROUTER] Error: ${response.message}`);
            let profile = response.profile;
            return profile
        }
    }
    );
}

// async function loadProfile(){
//     const response = await axios.get('')
// }

router.use(authenticateToken);

// router.all('*', requireAuthentication);
router.get('/', requireAuthentication, (req, res) => {
    var token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    var profilemusic = req.cookies.profilemusic;
    var decodedProfileMusic = jwtDecode.jwtDecode(profilemusic);
    var uid = decodedToken.uid;
    var loggedIn = decodedToken.loggedIn ?? false;
    try {
        let t = req.cookies.oAuthed;
        var decodedOAuthed = jwtDecode.jwtDecode(t);
        var oAuthed = decodedOAuthed.oAuthed ?? null;
    }
    catch (err) {
        console.log(`[ACCOUNTS ROUTER] Error: ${err}`);
        var oAuthed = null;
    }
    var data = decodedToken.data ?? null;
    var links = decodedProfileMusic.links ?? null;
    var artists = decodedProfileMusic.artists ?? null;
    var tracks = decodedProfileMusic.tracks ?? null;
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
router.get('/p/:username', requireAuthentication, (req, res) => {
    var page = "userprofile";
    var viewPath = path.join(__dirname, '../../views/account/', page + '.ejs');
    var username = req.params.username;
    console.log(`username is: ${username}`);
    var token = req.cookies.token;
    var decodedToken = jwtDecode.jwtDecode(token);
    var uid = decodedToken.uid;

    var profile = getOtherUserData(uid, username);
    console.log(`profile - username is: ${profile}`);
    var loggedIn = decodedToken.loggedIn ?? false;
    var oAuthed = decodedToken.oAuthed ?? null;
    var data = decodedToken.data ?? null;
    var links = decodedToken.links ?? null;
    var artists = decodedToken.artists ?? null;
    var tracks = decodedToken.tracks ?? null;
    var data = {
        "loggeduser": "Jim",
        "loggedIn": loggedIn,
        "oAuthed": oAuthed,
        "data": data,
        "links": links,
        "artists": artists,
        "tracks": tracks,
    }
    res.status(200).render(viewPath, {
        data: data,
        profile: profile
    });
});

router.route("/:page")
    .get(requireAuthentication, (req, res) => {
        console.log('checking for page in the accounts router');
        var page = req.params.page;
        var viewPath = path.join(__dirname, '../../views/account/', page + '.ejs');
        // console.log('__dirname is: ', __dirname);
        let token = req.cookies.token;
        token = decodeToken(token);
        var uid = token.uid;
        var loggedIn = token.loggedIn ?? false;
        var oAuthed = token.oAuthed ?? null;
        var data = token.data ?? null;
        token = req.cookies.profilemusic;
        token = decodeToken(token);
        var links = token.links ?? null;
        var artists = token.artists ?? null;
        var tracks = token.tracks ?? null;
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
                    // will need to put context objects here
                });
                break;
            case 'profile':
                console.log(`Rendering ${page}...`);
                // let username = "al";
                // let loggedUser = "al";

                data = {
                    username_set: false,
                    loggedUser: "al",
                    username: "al",
                    profilePicture: false,
                    spotify_username: "alfredhsimpson",
                }
                res.status(200).render(viewPath, {
                    data: data
                });
                // actual testing of the code
                let t = req.cookies.token;
                var uid = getUID(t);



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

module.exports = router;