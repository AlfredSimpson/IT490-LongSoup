#!/usr/bin/env node

var amqp = require('amqplib/callback_api');

const rmqConf = {
	host: '192.168.68.65',
	port: 5672,
	username: 'longsoup',
	password: 'puosgnol',
	vhost: 'tempHost'
};

amqp.connect(`amqp://${rmqConf.username}:${rmqConf.password}@${rmqConf.host}:${rmqConf.port}/${encodeURIComponent(rmqConf.vhost)}`, {
}, function (error0, connection) {
	if (error0) {
		throw error0;
	}
	connection.createChannel(function(error1, channel) {
		if (error1) {
			throw error1;
		}

		var queue = 'tempQueue';
		var msg = 'Hello World!';
		
		channel.assertQueue(queue, {
			durable: true
		});
		channel.sendToQueue(queue, Buffer.from(msg));

		console.log("[x] Sent %s", msg);
	});
	setTimeout(function() {
		connection.close();
		process.exit(0);
	}, 500);
});
