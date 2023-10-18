#!/usr/bin/env node
// Import the callback_api version of amqplib
const amqp = require('amqplib/callback_api');
// Import the rmqConfig.conf file as conf, which is where we have our connection information saved
const conf = require('./rmqConfig.conf');

/**
 * Now that we have our connection information, we can connect to the RabbitMQ server.
 * We do this by calling amqp.connect() and passing in the connection string.
 * The connection string is formatted as follows:
 * amqp://username:password@host:port/vhost
 * I've presaved the entire string in the conf object, so we can just pass that in. I think. 
 */

/**
 * Examine the structure. amqp.connect() - this method is part of amqp. It takes two arguments: the connection  string and a callback function. The callback function takes two arguments: error0 and connection.
 * A callback function is a function that is passed into another function as an argument. 
 * The callback function is then called inside the outer function to complete some kind of routine or action.
 * In terms of rabbitMQ, the callback function is called when the connection is established (or isn't).
 * The callback function is defined in the second argument of amqp.connect(). It is an anonymous function that takes two arguments: error0 and connection.
 * If there is an error, the error is passed into error0. If there is no error, error0 is null.
 * TODO: we'll need to remember this for the future, because we need logging!
 */
amqp.connect(`amqp://${conf.TESTREQUEST}`, function(error0, connection) {
    if (error0) {
        throw error0;
    }
    connection.createChannel(function(error1, channel) {
        if (error1) {
            throw error1;
        }
        // Establish the queues, msg we'll use.
        // We could probably streamline this further by using the conf object and creating a special function to use. For now, this will work.
        // Establish a queue
        let queue = 'tempQueue';
        // Establish a message:
        let msg = 'Hello World!';
        // Now we need to assert the queue. This is done with channel.assertQueue(). This method takes two arguments: the queue name and an object of options.
        // The options object is where we can set the durability of the queue.
        // We'll set it to true for now as our tempQueue is durable
        channel.assertQueue(queue, {
            durable: true
        });
        
        channel.sendToQueue(queue, Buffer.from(msg));
        console.log(" [x] Sent %s", msg);
    });
    // We can also close the connection after we send the message, as we don't need to keep it open unless we're listening for messages.
    // We'll do that now:
    setTimeout(function() {
        connection.close();
        process.exit(0);
    }, 500); 
});

// To summarize, we connect to rabbitmq first, then we connect to a channel. We then assert a queue, and send a message to that queue.
// We'll also need to remember to run the script with node send.js
// We can also run it with ./send.js if we add the following line to the top of the file:
// #!/usr/bin/env node

// Now we can run the script with ./send.js