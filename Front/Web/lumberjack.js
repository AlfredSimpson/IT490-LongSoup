const logAndSend = async (message) => {
    const amqp = require('amqplib');
    const dotenv = require('dotenv');
    const fs = require('fs').promises;
    //load our config info from the .env and store locally
    dotenv.config();
    const LOGHOST = process.env.LOG_HOST;
    const LOGvHOST = process.env.LOG_VHOST;
    const LOGX = process.env.LOG_EXCHANGE;
    const LOGQ = process.env.LOG_QUEUE;
    const LOGUSER = process.env.LOG_USER;
    const LOGPASS = process.env.LOG_PASS;
    const LOGPORT = process.env.LOG_PORT;
    const LOG_URL = `amqp://${LOGUSER}:${LOGPASS}@${LOGHOST}:${LOGPORT}/${encodeURIComponent(LOGvHOST)}`;

    const logMessage = `[${new Date()}] ${message}\n`;
    // try catch to write the log message to our internal logs
    try {
        await fs.appendFile('server.log', logMessage);
    } catch (err) {
        console.error('Error writing to log file:', err);
    }
    //now connect to rmq
    let connection;
    try {
        connection = await amqp.connect(LOG_URL);
        const channel = await connection.createChannel();
        await channel.assertExchange(LOGX, 'fanout', { durable: false });
        channel.publish(LOGX, '', Buffer.from(message));
    } catch (error) {
        console.error('An error occured while connecting to RMQ:', error);
        try {
            await fs.appendFile('server.log', `Error connecting to RMQ: ${error}\n`);
        }
        catch (err) {
            console.error('Error writing to log file (no saved log available):', err);
        }
    } finally {
        if (connection) {
            setTimeout(() => {
                connection.close();
            }, 500);
        }
    }
};

module.exports = { logAndSend };
