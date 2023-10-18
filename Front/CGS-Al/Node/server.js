const express = require('express');
const bodyParser = require('body-parser');
const amqp = require('amqplib/callback_api');

const app = express();
app.use(bodyParser.json());

// Read RabbitMQ config
const rmqConfig = require('./rmqConfig.conf');

app.post('/login', (req, res) => {
    const { username, password } = req.body;

    amqp.connect(rmqConfig.url, function (err, conn) {
        conn.createChannel(function (err, ch) {
            const q = 'loginQueue';
            const msg = JSON.stringify({ username, password });

            ch.assertQueue(q, { durable: false });
            ch.sendToQueue(q, Buffer.from(msg));
        });
    });

    // Redirect to getstarted.html after successful login
    res.redirect('/getstarted.html');
});

// Serve static files
app.use(express.static('public'));

// Start the server
const port = 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
});
