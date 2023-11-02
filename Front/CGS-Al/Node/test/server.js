const express = require('express');
const bodyParser = require('body-parser');
const amqp = require('amqplib/callback_api');
const path = require('path');
const rmqConfig = require('./rmqConfig.conf');

const app = express();
app.use(bodyParser.json());

// Example GET request handlers
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/getstarted', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'getstarted.html'));
});

// POST for login
app.post('/login', (req, res) => {
    const { useremail, password } = req.body;
    amqp.connect(`amqp://${rmqConfig.TESTREQUEST}`, function (err, conn) {
        if (err) {
            return res.status(500).json({ success: false, message: 'RabbitMQ connection failed.' });
        }
        conn.createChannel(function (err, channel) {
            if (err) {
                return res.status(500).json({ success: false, message: 'RabbitMQ channel creation failed.' });
            }
            const queueName = 'tempQueue';
            channel.assertQueue(queueName, { durable: true });
            channel.sendToQueue(queueName, Buffer.from(JSON.stringify({ type: 'login', useremail, password, msg: " " })));
            res.status(200).json({ success: true, message: 'Login details sent to RabbitMQ.' });
        });
    });
	res.redirect('/getstarted.html');
});

// New endpoint to initiate Spotify OAuth
app.post('/initiateSpotifyOAuth', (req, res) => {
    amqp.connect(`amqp://${rmqConfig.TESTREQUEST}`, function (err, conn) {
        if (err) {
            return res.status(500).json({ success: false, message: 'RabbitMQ connection failed.' });
        }
        conn.createChannel(function (err, channel) {
            if (err) {
                return res.status(500).json({ success: false, message: 'RabbitMQ channel creation failed.' });
            }
            const queueName = 'spotifyOAuthInitiation';
            channel.assertQueue(queueName, { durable: false });
            channel.sendToQueue(queueName, Buffer.from(JSON.stringify({ action: 'initiateSpotifyOAuth' })));
            res.status(200).json({ success: true, message: 'Spotify OAuth initiation message sent to RabbitMQ.' });
        });
    });
});

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req,res) => {
	res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});

