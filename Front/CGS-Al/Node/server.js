const express = require('express');
const bodyParser = require('body-parser');
const amqp = require('amqplib/callback_api');
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Read RabbitMQ config
const rmqConfig = require('./rmqConfig.conf');

// Connect to RabbitMQ, send it a type authorizeSpotify
app.post('/authorizeSpotify', (req, res) => {
    console.log("Made it to the authorizeSpotify endpoint")
    amqp.connect(`amqp://${rmqConfig.TESTREQUEST}`, function (err, conn) {
        if (err) {
            console.error(err);
            return;
        }
        conn.createChannel(function (err, ch) {
            console.log("Attempting to send authorization request to RabbitMQ");
            const q = 'spotQueue';
            let type = 'authorizeSpotify';
            let message = '';
            const msg = JSON.stringify({ type, message });
            console.log(msg);
            ch.assertQueue(q, { durable: true });
            ch.sendToQueue(q, Buffer.from(msg));
        });
    });
    console.log(res.body);
    res.redirect('/success.html');
});

// Login endpoint
app.post('/login', (req, res) => {
    const { useremail, password } = req.body;
    console.log(password);
    amqp.connect(`amqp://${rmqConfig.TESTREQUEST}`, function (err, conn) {
        if (err) {
            console.error(err);
            return;
        }
        conn.createChannel(function (err, ch) {
            console.log("Made it to the channel creation");
            const q = 'tempQueue';
            let type = 'login';
            let message = '';
            const msg = JSON.stringify({ type, useremail, password, message });
            console.log(msg)
            ch.assertQueue(q, { durable: true });
            ch.sendToQueue(q, Buffer.from(msg));
        });
    });

    // Redirect to getstarted.html after successful login
    console.log("Should redirect to authorizeSpotify.html...")
    // res.redirect('/getstarted.html');
    res.redirect('/authorizeSpotify.html')
});

// Register endpoint
// TODO: create it

// Serve static files from a folder named 'public'
app.use(express.static(path.join(__dirname, 'public')));

// Fallback for root URL to serve index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});




// Start the server
const port = 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
});
