// /**
//  * Mustang.js consists of a few functions that help to automate the process of connecting to and from the rmq broker.
//  * 
//  * @NOTE: This is a work in progress and is not yet fully functional for all.
//  * - We'll need to standardize the way we send and receive messages.
//  */

const amqp = require('amqplib/callback_api');
const timber = require('./lumberjack.js');
// Generate a unique ID for the correlationId
const generateUuid = () => {
    return Math.random().toString() +
        Math.random().toString() +
        Math.random().toString();
};

module.exports = {
    // Send and receive messages through RabbitMQ  
    sendAndConsumeMessage: function (amqpUrl, queueName, requestPayload, callback) {
        /**
         * Sends a message to the specified queue and waits for a response.
         * @param {string} amqpUrl - The URL for the RabbitMQ broker
         * @param {string} queueName - The name of the queue to send the message to
         * @param {object} requestPayload - The payload to send to the queue
         * @param {function} callback - The callback function to run when a response is received
         */

        amqp.connect(amqpUrl, (error, connection) => {
            // Attempt to connect to the RMQ broker
            if (error) {
                // console.error('Connection Error:', error);
                timber.logAndSend(`Error connecting to RMQ: ${error}. Error caught with ${amqpUrl}, ${requestPayload}, ${callback}`, 'RMQ');
                throw error;
            }
            console.log('Connected. Creating channel.');
            // Create a channel, if successful, assert the queue
            connection.createChannel((error1, channel) => {
                if (error1) {
                    console.error('\nChannel Creation Error:', error1);
                    timber.logAndSend(`Error creating channel in RMQ: ${error1}. Error caught with ${amqpUrl}, ${requestPayload}, ${callback}`, 'RMQ');
                    throw error1;
                }
                console.log('\nChannel created. Asserting queue.');
                // Assert the queue, if successful, create a consumer
                channel.assertQueue('', { exclusive: true }, (error2, q) => {
                    if (error2) {
                        timber.logAndSend(`Error asserting queue in RMQ: ${error2}. Error caught using queue: ${queueName}`, 'RMQ');
                        // console.error('\nQueue Assertion Error:', error2);
                        throw error2;
                    }
                    // console.log('\nQueue asserted. Setting up consumer.');
                    // Create a correlation ID and consume the queue. A correlation ID is used to match the response to the request.
                    const correlationId = generateUuid();
                    // console.log(`Correlation ID is ${correlationId}`);
                    // Consume the queue - Consume means to listen for messages on the queue.
                    channel.consume(q.queue, (msg) => {
                        // console.log('\nMessage received:\t', msg.properties.correlationId, correlationId);
                        // If the correlation ID matches, call the callback function and close the connection.
                        if (msg.properties.correlationId === correlationId) {
                            console.log('Correlation ID matched. Calling callback.');
                            // Call the callback function with the message. A callback function is a function that is passed as an argument to another function.
                            callback(msg);
                            // Close the connection after a short delay.
                            setTimeout(() => {
                                console.log('Closing connection.');
                                connection.close();
                            }, 500);
                        }
                    }, { noAck: true }); // noAck means that the message is not acknowledged. This means that the message will be lost if the consumer dies before the message is processed.

                    console.log(`\n[MUSTANG exports] Sending message to queue ${queueName}\n`);
                    // Send the message to the queue
                    channel.sendToQueue(
                        queueName,
                        Buffer.from(JSON.stringify(requestPayload)),
                        {
                            correlationId: correlationId,
                            replyTo: q.queue
                        }
                    );
                });
            });
        });
    }
};
