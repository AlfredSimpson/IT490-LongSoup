// /**
//  * Mustang.js consists of a few functions that help to automate the process of connecting to and from the rmq broker.
//  * 
//  * @NOTE: This is a work in progress and is not yet fully functional.
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


        amqp.connect(amqpUrl, (error, connection) => {
            if (error) {
                console.error('Connection Error:', error);
                timber.logAndSend(`Error connecting to RMQ: ${error}. Error caught with ${amqpUrl}, ${requestPayload}, ${callback}`, 'RMQ');
                throw error;
            }
            console.log('Connected. Creating channel.');
            connection.createChannel((error1, channel) => {
                if (error1) {
                    console.error('Channel Creation Error:', error1);
                    timber.logAndSend(`Error creating channel in RMQ: ${error1}. Error caught with ${amqpUrl}, ${requestPayload}, ${callback}`, 'RMQ');
                    throw error1;
                }
                console.log('Channel created. Asserting queue.');
                channel.assertQueue('', { exclusive: true }, (error2, q) => {
                    if (error2) {
                        timber.logAndSend(`Error asserting queue in RMQ: ${error2}. Error caught using queue: ${queueName}`, 'RMQ');
                        console.error('Queue Assertion Error:', error2);
                        throw error2;
                    }
                    console.log('Queue asserted. Setting up consumer.');
                    const correlationId = generateUuid();
                    console.log(`Correlation ID is ${correlationId}`);

                    channel.consume(q.queue, (msg) => {
                        console.log('Message received.', msg.properties.correlationId, correlationId);
                        if (msg.properties.correlationId === correlationId) {
                            console.log('Correlation ID matched. Calling callback.');
                            callback(msg);
                            setTimeout(() => {
                                console.log('Closing connection.');
                                connection.close();
                            }, 500);
                        }
                    }, { noAck: true });

                    console.log(`\n[MUSTANG exports] Sending message to queue ${queueName}\n`);
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
