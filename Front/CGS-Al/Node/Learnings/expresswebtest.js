/**
 * @fileoverview process.js
 * This file contains testing for the server framework. If we use node and express, we can forgo apache entirely
 */
// So we start by requiring express, which is our middleware.
// We then create an instance of express and assign it to app.
let express = require('express');
let app = express();
const path = require('path');


const port = process.env.PORT || 8089;
// We then create a server using the app.listen() method. This method takes two arguments: the port to listen on and a callback function.

app.get('/', (req, res) => {
    console.log('attempting to get index.html');
    res.sendFile(__dirname + '/index.html');});

    console.log("Loading index.html");

let server = app.listen(port, function() {
    let host = server.address().address;
    let port = server.address().port;
    console.log('Example app listening at http://%s:%s', host, port);
});



// Now we need to set up our RabbitMQ connection.
// We'll start by requiring amqplib.
let amqp = require('amqplib/callback_api');
// We'll also require the rmqConfig.conf file.
let conf = require('./rmqConfig.conf');

// Now we'll connect to the RabbitMQ server.
// We'll use the same connection string as before, but this time we'll use the TESTREQUEST queue.
// We'll also use the same callback function as before.
// amqp.connect(`amqp://${conf.TESTREQUEST}`, function(error0, connection) {
//     if (error0) {
//         throw error0;
//     }
//     connection.createChannel(function(error1, channel) {
//         if (error1) {
//             throw error1;
//         }
//         let queue = 'tempQueue';
//         channel.assertQueue(queue, {
//             durable: true
//         });
//         channel.consume(queue, function(msg) {
//             console.log(" [x] Received %s", msg.content.toString());
//         }, {
//             noAck: true
//         });
//     });
// });


