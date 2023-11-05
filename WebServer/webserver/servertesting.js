require('dotenv').config();
const express = require('express');
const axios = require('axios');
const app = express();

const CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
const REDIRECT_URI = process.env.SPOTIFY_TEST_URI;
const PORT = 3900;

// Route to handle login
app.get('/spotlog', (req, res) => {
    const scopes = 'user-read-private user-read-email';
    res.redirect('https://accounts.spotify.com/authorize' +
        '?response_type=code' +
        '&client_id=' + CLIENT_ID +
        (scopes ? '&scope=' + encodeURIComponent(scopes) : '') +
        '&redirect_uri=' + encodeURIComponent(REDIRECT_URI));
});

// Route to handle the callback from Spotify's OAuth
app.get('/callback', async (req, res) => {
    const code = req.query.code || null;

    try {
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

            console.log(`response.data.access_token: ${response.data.access_token}`);
            console.log(`response.data.refresh_token: ${response.data.refresh_token}`);
            console.log(`response.data.expires_in: ${response.data.expires_in}`);
            res.send('Login Successful');
        } else {
            res.send('Access Token Missing');
        }
    } catch (error) {
        res.status(500).send('Authentication Failed');
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`);
});
