const express = require('express');
const amqp = require('amqplib/callback_api');

const app = express();

// the middleman for the POST data
app.use(express.urlencoded({ extended: true }));

// send messege to rmq
const sendToQueue = (message) => {
  amqp.connect('amqp://admin:admin@localhost', (error0, connection) => {
    if (error0) {
      throw error0;
    }
    connection.createChannel((error1, channel) => {
      if (error1) {
        throw error1;
      }
      const queue = 'messageQueue';

      channel.assertQueue(queue, {
        durable: false
      });

      channel.sendToQueue(queue, Buffer.from(message));
      console.log(` [x] Sent ${message}`);
    });
  });
};

// GET and POST routes
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/messageBoard.html');
});

app.post('/submit-post', (req, res) => {
  const username = req.body.username;
  const message = req.body.message;

  const fullMessage = `Received post from ${username}: ${message}`;
  console.log(fullMessage);

  // send to RMQ queue 
  sendToQueue(fullMessage);

  res.send('Your post has been submitted!');
});

// spin up server
app.listen(8080, () => {
  console.log('Server running on http://localhost:8080/');
});
