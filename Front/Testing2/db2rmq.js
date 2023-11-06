const mustang = require('./mustang.js');
const mysql = require('mysql');


const dbConnection = mysql.createConnection({
    host:"localhost",
    user:"admin",
    password:"admin",
    database:"securesoupdb"
    });


dbConnection.connect((err) => {
  if (err) {
    console.error('Database connection failed:', err);
    return;
  }
  console.log('Connected to the database');


  const query = 'SELECT * FROM securedsoupdb';
  dbConnection.query(query, (queryErr, results) => {
    if (queryErr) {
      console.error('Error executing query:', queryErr);
      return;
    }


    const message = {
      type: 'forum_posts',
      data: results, // will be the table
    };


    mustang.sendToQueue('your_queue_name', message);

    // end connection
    dbConnection.end((endErr) => {
      if (endErr) {
        console.error('Error closing database connection:', endErr);
      }
      console.log('Database connection closed');
    });
  });
});
