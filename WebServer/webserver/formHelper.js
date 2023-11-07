// This is largely deprecated for now

const sendLogin = async function (useremail, password) {
    const amqp = require('amqplib');
    const dotenv = require('dotenv');
    const fs = require('fs').promises;
    //load our config info from the .env and store locally
    dotenv.config();
    const BROKERHOST = process.env.BROKER_HOST;
    const BROKERVHOST = process.env.BROKER_VHOST;
    const BROKERX = process.env.BROKER_EXCHANGE;
    const BROKERQ = process.env.BROKER_QUEUE;
    const BROKERUSER = process.env.BROKER_USERNAME;
    const BROKERPASS = process.env.BROKER_PASSWORD;
    const BROKERPORT = process.env.BROKER_PORT;
    const BROKERURL = `amqp://${BROKERUSER}:${BROKERPASS}@${BROKERHOST}:${BROKERPORT}/${encodeURIComponent(BROKERVHOST)}`;
    console.log(BROKERURL);
};



const sendRegister = function (useremail, password) {
};

const handleAction = (action, req, res) => {
    const { useremail, password } = req.body;
    switch (action) {
        case 'login':
            sendLogin(useremail, password);
            break;
        case 'register':
            sendRegister(useremail, password);
            break;
        default:
            res.status(400).send('Unknown action');
    }
}

// export modules so that server.js can use them

module.exports = { sendLogin }