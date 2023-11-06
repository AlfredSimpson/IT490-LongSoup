const mysql = require('mysql');

// setting up ccommunication with db

const con = mysql.createConnection({
    host:"localhost",
    user:"admin",
    password:"admin",
    database:"securesoupdb"
    });


con.connect((err) => {
  if (err) throw err;
  console.log("Connected to the MySQL server.");
});




// setting up the rmq connection
const amqp = require('amqplib/callback_api');


// the motherload

amqp.connect('amqp://admin:admin@localhost', (error0, connection) => {
  if (error0) {
    throw error0;
  }
  connection.createChannel((error1, channel) => {
    if (error1) {
      throw error1;
    }
    const queue = 'messageQueue';
    const confirmQueue = 'confirmationQueue';
    //the db gets the messege delivered from the 'messegeQueue'
    channel.consume(queue, (msg) => {
      //converts the rmq messege to a string
      console.log(`Received: ${msg.content.toString()}`);
      
      // insert into the db
      const query = "INSERT INTO MessagingPosts (message) VALUES (?)";
      // parameterized queries can help prevent SQL injection
      con.query(query, [msg.content.toString()], (err, result) => {
        if (err) throw err;

        
        console.log("Record inserted");
        
    channel.sendToQueue(confirmQueue, Buffer.from("Message inserted!"));

        
        // Send acknowledgment to rmq that is was sent
        channel.ack(msg);
      });
    });
  });
});




