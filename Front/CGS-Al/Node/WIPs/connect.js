/**
 * @fileoverview This is our main router for the server.
 * This file contains the routing for the server.
 * We'll use this to route the requests to the appropriate handlers.
 */

const express = require('express');
const app = express();
const port = process.env.PORT || 8089;
const path = require('path');

Status_Codes = {
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    403: 'Forbidden',
    404: 'Not Found',
    500: 'Internal Server Error'
};

// Main "pages" outside of the profiles
pages = ['index.html', 'login.html', 'bio.html']

// Profile pages
postMain = ['profile.html', 'songs.html']


// Set up the router for main pages, stuff outside of your profile
const mainRouter = express.Router();
app.use('/', mainRouter);

mainRouter.get('/:page', (req, res, next) => {
    let page = req.params.page;
    if (pages.includes(page)) {
        res.status(200).sendFile(__dirname + '/' + page);
    } else {
        res.status(404).sendFile(__dirname + '/404.html');
    }
    next();
})


mainRouter.get('/', (req, res) => {
    console.log('attempting to get index.html');
    res.sendFile(__dirname + '/index.html');});

    console.log("Loading index.html");




let server = app.listen(port, function() {
    let host = server.address().address;
    let port = server.address().port;
    console.log('Example app listening at http://%s:%s', host, port);
});

