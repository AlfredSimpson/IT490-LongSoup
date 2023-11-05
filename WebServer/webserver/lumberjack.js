const logAndSend = async (message, source = 'Webserver') => {
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

    const logMessage = message + "\n";
    // console.log(logMessage);
    // const source_of_log = 'Webserver';
    const d = new Date();
    let date_of_log = d.toISOString();
    // Now we can modify date_of_log to reflect NYC local time by subtracting 5 hours, accounting for any possible change in day as well.
    // Not a perfect solution, but for this project, it works - especially since the time just went back an hour! We'll also remove markers that it was UTC time.
    date_of_log = new Date(date_of_log);
    date_of_log.setHours(date_of_log.getHours() - 5);
    date_of_log = date_of_log.toISOString();
    date_of_log = date_of_log.replace('Z', 'EST');



    // Set outmessage to a JSON string with type, source, date, log_message.
    const outmsg = JSON.stringify({ type: "log", source: source, date: date_of_log, log_message: logMessage });
    let fileName = '_webserver.log';
    // This will allow us to modularly log rmq and also webserver logs - to pinpoint origin
    if (source === 'RMQ') {
        fileName = '_webserver_rmq.log';
    }

    // try catch to write the log message to our internal logs
    try {
        await fs.appendFile(fileName, outmsg + '\n');
    } catch (err) {
        console.error('Error writing to log file:', err);
    }
    //now connect to rmq
    let connection;
    try {
        connection = await amqp.connect(LOG_URL);
        const channel = await connection.createChannel();
        await channel.assertExchange(LOGX, 'fanout', { durable: false });
        // console.log(outmsg);
        channel.publish(LOGX, '', Buffer.from(outmsg));
    } catch (error) {
        console.error('An error occured while connecting to RMQ:', error);
        try {
            await fs.appendFile(fileName, `Error connecting to RMQ: ${error}\n`);
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
