const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const path = require('path');
const timber = require('./lumberjack.js');
const handshake = require('./formHelper.js');
const amqp = require('amqplib/callback_api');

const PORT = process.env.PORT || 9001;

const statusMessageHandler = (req, res, next) => {
    res.statusMessageHandler = (statusCode) => {
        const statusMessages = {
            200: 'OK',
            404: 'Not Found! This does *not* rock.',
            500: 'Internal Server Error... you caught us slipping.',
            // Add more codes and messages as needed
        };
        return statusMessages[statusCode] || 'Unknown Status';
    };

    next();
};

const trafficLogger = (req, res, next) => {
    timber.logAndSend(`Incoming request: ${req.method} ${req.url}`);

    const send = res.send;
    res.send = function (string) {
        //
        const body = string instanceof Buffer ? string.toString() : string;

        timber.logAndSend(`Outgoing response: ${res.statusCode} ${body}`);
        send.call(this, string);
    };
    next();
};

app.use(trafficLogger);
app.use(statusMessageHandler);
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());



app.get('/', (req, res, next) => {
    res.status(200).sendFile(path.join(__dirname, 'public', 'index.html'), err => {
        if (err) {
            next(err);
        }
    });
});

app.get('/:page', (req, res, next) => {
    const filePath = path.join(__dirname, 'public', req.params.page + '.html');
    res.sendFile(filePath, (err) => {
        if (err) {
            next(err);
        }
    });
});

app.use((err, req, res, next) => {
    const statusCode = err.statusCode || 500;
    const message = res.statusMessageHandler(statusCode);
    res.status(statusCode).send(message);
});


app.post('/login', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const tempHost = "tempHost";
    const tempQueue = "tempQueue";
    const amqpUrl = `amqp://longsoup:puosgnol@192.168.68.65:5672/${encodeURIComponent(tempHost)}`;

    amqp.connect(amqpUrl, (error, connection) => {
        if (error) {
            throw error;
        }
        connection.createChannel((error1, channel) => {
            if (error1) {
                throw error1;
            }
            channel.assertQueue('', { exclusive: true }, (error2, q) => {
                if (error2) {
                    throw error2;
                }

                const correlationId = generateUuid();
                const msg = JSON.stringify({ type: "login", useremail, password });

                // Setup consumer for reply first
                channel.consume(q.queue, function reply(msg) {
                    if (msg.properties.correlationId === correlationId) {
                        const response = JSON.parse(msg.content.toString());
                        if (response.returnCode === '0') {
                            res.redirect('/about');  // Redirect to 'thispage' if login is successful
                        } else {
                            res.status(401).send('You have failed to login.');  // Send failure message otherwise
                        }
                        setTimeout(() => {
                            connection.close();
                        }, 500);
                    }
                }, {
                    noAck: true
                });

                // Send message after consumer is set up
                channel.sendToQueue(tempQueue,
                    Buffer.from(msg),
                    {
                        correlationId: correlationId,
                        replyTo: q.queue
                    });

                console.log(" [x] Sent %s", msg);
            });
        });
    });
});


app.post('/register', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const last_name = req.body.last_name;
    const first_name = req.body.first_name;
    const tempHost = "tempHost";
    const tempQueue = "tempQueue";
    const amqpUrl = `amqp://longsoup:puosgnol@192.168.68.65:5672/${encodeURIComponent(tempHost)}`;

    amqp.connect(amqpUrl, (error, connection) => {
        if (error) {
            throw error;
        }
        connection.createChannel((error1, channel) => {
            if (error1) {
                throw error1;
            }
            channel.assertQueue('', { exclusive: true }, (error2, q) => {
                if (error2) {
                    throw error2;
                }

                const correlationId = generateUuid();
                const msg = JSON.stringify({ type: "register", useremail, password, first_name, last_name });

                // Setup consumer for reply first
                channel.consume(q.queue, function reply(msg) {
                    if (msg.properties.correlationId === correlationId) {
                        const response = JSON.parse(msg.content.toString());
                        if (response.returnCode === '0') {
                            res.redirect('/account');  // Redirect to '/account' if registration is successful
                        } else {
                            res.status(401).send('You have failed to register.');  // Send failure message otherwise
                        }
                        setTimeout(() => {
                            connection.close();
                        }, 500);
                    }
                }, {
                    noAck: true
                });

                // Send message after consumer is set up
                channel.sendToQueue(tempQueue,
                    Buffer.from(msg),
                    {
                        correlationId: correlationId,
                        replyTo: q.queue
                    });

                console.log(" [x] Sent %s", msg);
            });
        });
    });
});


function generateUuid() {
    return Math.random().toString() +
        Math.random().toString() +
        Math.random().toString();
}


app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}.`);
})


