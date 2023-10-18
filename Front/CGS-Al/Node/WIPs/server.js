const express = require('express');
const bodyParser = require('body-parser');
const amqp = require('amqplib/callback_api');
const path = require('path');

const app = express();
app.use(bodyParser.json());

// Read RabbitMQ config
const rmqConfig = require('./rmqConfig.conf');

// Function to handle both login and register actions
const handleAction = (action, req, res) => {
    const { useremail, password } = req.body;

    amqp.connect(`amqp://${rmqConfig.TESTREQUEST}`, function (err, conn) {
        if (err) {
            console.error(err);
            res.status(500).send(err);
            return;
        }
        conn.createChannel(function (err, ch) {
            const q = 'tempQueue';
            const replyTo = 'amq.rabbitmq.reply-to';

            const msg = JSON.stringify({ useremail, password, type: action });

            ch.assertQueue(q, { durable: true });

            ch.consume(replyTo, function (reply) {
                res.json(JSON.parse(reply.content.toString()));
                ch.ack(reply);
            }, { noAck: false });

            ch.sendToQueue(q, Buffer.from(msg), { replyTo });
        });
    });
};

// Login endpoint
app.post('/login', (req, res) => {
    handleAction('login', req, res);
});

// Register endpoint
app.post('/register', (req, res) => {
    handleAction('register', req, res);
});

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Serve index.html for the root URL
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const port = 3000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
});
