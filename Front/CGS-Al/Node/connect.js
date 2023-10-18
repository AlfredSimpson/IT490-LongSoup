const amqp = require('amqplib');

async function connectToRabbitMQ() {
    const connection = await amqp.connect('amqp://your-rabbitmq-server:5672');
    const channel = await connection.createChannel();

    // Define your RabbitMQ logic here (e.g., send/receive messages)
}

connectToRabbitMQ();
