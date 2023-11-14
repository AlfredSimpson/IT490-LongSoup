const express = require('express');
const bodyParser = require('body-parser');
const app = express();
const path = require('path');
const timber = require('./lumberjack.js');
const handshake = require('./formHelper.js');
const amqp = require('amqplib/callback_api');
const session = require('express-session');
const bcrypt = require('bcrypt');
const mustang = require('./mustang.js');
require('dotenv').config();

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
    timber.logAndSend(`Incoming request: \ ${req.method} ${req.url}`);

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


const createSessionCookie = (req, res) => {
    const saltRounds = 10;
    const plains = process.env.SESSION_SECRET_ID;
    let salt = bcrypt.genSaltSync(saltRounds);
    let sessionId = bcrypt.hashSync(plains, salt);
    req.session = { sessionId: sessionId };
    res.cookie('sessionId', sessionId, { httpOnly: true });
};




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
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;
    console.log(amqpUrl);

    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "login",
        useremail,
        password
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === '0') {
            res.redirect('/account');
        } else {
            let errorMSG = 'You have failed to login.';
            const filePath = path.join(__dirname, 'public', 'login' + '.html');
            res.status(401).sendFile(filePath, errorMSG);
        }
    });
});


// This is meant to fail, it's just the login page currently, but it's a good test to see if the broker is working and if the db fails. It does not
app.post('/testing123', (req, res) => {
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const brokerHost = process.env.BROKER_HOST;
    const brokerPort = process.env.BROKER_PORT;
    const brokerUser = process.env.BROKER_USERNAME;
    const brokerPass = process.env.BROKER_PASSWORD;
    const amqpUrl = `amqp://${brokerUser}:${brokerPass}@${brokerHost}:${brokerPort}/${encodeURIComponent(tempHost)}`;

    console.log(amqpUrl);
    console.log('testing');
    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "failme",
    }, (msg) => {
        console.log("Message going out");
        console.log(msg);
        const response = JSON.parse(msg.content.toString());
        console.log(response);
        if (response.returnCode === '0') {
            console.log('success');
            res.status(200).send('Congrats you failed by succeeding. Status 200.');
        } else {
            console.log('fail');
            res.status(401).send('You have succeeded at failing. Status 401.');
        }

    });
});

app.post('/register', (req, res) => {
    const useremail = req.body.useremail;
    const password = req.body.password;
    const last_name = req.body.last_name;
    const first_name = req.body.first_name;
    const tempHost = process.env.BROKER_VHOST;
    const tempQueue = process.env.BROKER_QUEUE;
    const amqpUrl = `amqp://longsoup:puosgnol@${process.env.BROKER_HOST}:${process.env.BROKER_PORT}/${encodeURIComponent(tempHost)}`;

    mustang.sendAndConsumeMessage(amqpUrl, tempQueue, {
        type: "register",
        useremail,
        password,
        last_name,
        first_name
    }, (msg) => {
        const response = JSON.parse(msg.content.toString());
        if (response.returnCode === '0') {
            res.redirect('/account');
        } else {
            res.status(401).send('You have failed to register.');
        }
    });
});

// app.post('/login', (req, res) => {
//     // TODO: use dotenv
//     const useremail = req.body.useremail;
//     const password = req.body.password;
//     const tempHost = "tempHost"; // process.env.BROKER_VHOST;
//     const tempQueue = "tempQueue"; // process.env.BROKER_QUEUE;
//     const amqpUrl = `amqp://longsoup:puosgnol@192.168.68.65:5672/${encodeURIComponent(tempHost)}`; // process.env.TESTREQUEST;
//     createSessionCookie(req, res);
//     console.log(req.session);
//     amqp.connect(amqpUrl, (error, connection) => {
//         if (error) {
//             // TODO: specify this is an rmq error
//             throw error;
//         }
//         connection.createChannel((error1, channel) => {
//             if (error1) {
//                 throw error1;
//             }
//             channel.assertQueue('', { exclusive: true }, (error2, q) => {
//                 if (error2) {
//                     throw error2;
//                 }

//                 const correlationId = generateUuid();
//                 const msg = JSON.stringify({ type: "login", useremail, password });

//                 // Setup consumer for reply first
//                 channel.consume(q.queue, function reply(msg) {
//                     if (msg.properties.correlationId === correlationId) {
//                         const response = JSON.parse(msg.content.toString());
//                         if (response.returnCode === '0') {
//                             res.redirect('/account');
//                         } else {
//                             res.status(401).send('You have failed to login.');
//                         }
//                         setTimeout(() => {
//                             connection.close();
//                         }, 500);
//                     }
//                 }, {
//                     noAck: true
//                 });

//                 // Send message after consumer is set up
//                 channel.sendToQueue(tempQueue,
//                     Buffer.from(msg),
//                     {
//                         correlationId: correlationId,
//                         replyTo: q.queue
//                     });

//                 console.log(" [x] Sent %s", msg);
//             });
//         });
//     });
// });


// app.post('/register', (req, res) => {
//     const useremail = req.body.useremail;
//     const password = req.body.password;
//     const last_name = req.body.last_name;
//     const first_name = req.body.first_name;
//     const tempHost = "tempHost";
//     const tempQueue = "tempQueue";
//     const amqpUrl = `amqp://longsoup:puosgnol@192.168.68.65:5672/${encodeURIComponent(tempHost)}`;

//     amqp.connect(amqpUrl, (error, connection) => {
//         if (error) {
//             throw error;
//         }
//         connection.createChannel((error1, channel) => {
//             if (error1) {
//                 throw error1;
//             }
//             channel.assertQueue('', { exclusive: true }, (error2, q) => {
//                 if (error2) {
//                     throw error2;
//                 }

//                 const correlationId = generateUuid();
//                 const msg = JSON.stringify({ type: "register", useremail, password, first_name, last_name });

//                 // Setup consumer for reply first
//                 channel.consume(q.queue, function reply(msg) {
//                     if (msg.properties.correlationId === correlationId) {
//                         const response = JSON.parse(msg.content.toString());
//                         if (response.returnCode === '0') {
//                             res.redirect('/account');  // Redirect to '/account' if registration is successful
//                         } else {
//                             res.status(401).send('You have failed to register.');  // Send failure message otherwise
//                         }
//                         setTimeout(() => {
//                             connection.close();
//                         }, 500);
//                     }
//                 }, {
//                     noAck: true
//                 });

//                 // Send message after consumer is set up
//                 channel.sendToQueue(tempQueue,
//                     Buffer.from(msg),
//                     {
//                         correlationId: correlationId,
//                         replyTo: q.queue
//                     });

//                 console.log(" [x] Sent %s", msg);
//             });
//         });
//     });
// });


function generateUuid() {
    /**
     * generateUuid() is a helper function that generates a random UUID
     * This helps us to identify the correlation between the request and the response
     */
    return Math.random().toString() +
        Math.random().toString() +
        Math.random().toString();
}

function sendPost() {
};
function getData() {

};



function handleActions() {
    /**
     * handleActions() is a helper function that handles the actions from the form
     * It is used to determine what action to take based on the form
     */
    switch (req.body.action) {
        case 'sendMessage':
            sendMessage(req, res);
            break;
        case 'receiveMessage':
            receiveMessage(req, res);
            break;
        case 'addToPlaylist':
            addToPlaylist(req, res);
            break;
        case 'removeFromPlaylist':
            removeFromPlaylist(req, res);
            break;
        case 'likethis':
            likethis(req, res);
            break;
        case 'dislikethis':
            dislikethis(req, res);
            break;
        case 'getRecommendations':
            getRecommendations(req, res);
            break;
        case 'followArtist':
            followArtist(req, res);
            break;
        case 'unfollowArtist':
            unfollowArtist(req, res);
            break;
        case 'followUser':
            followUser(req, res);
            break;
        case 'unfollowUser':
            unfollowUser(req, res);
            break;
        default:
            //TODO: write to log
            console.log('Invalid action');
            break;
    }
};

// app.listen(PORT, "192.168.68.66", () => {
//     console.log(`Server is running on port ${PORT}.`);
// });
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}.`);
});


