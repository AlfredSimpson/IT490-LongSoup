
// Requiring the module
const express = require('express');
const app = express();

const http = require('http');
 
// Route handling
app.get('/', (req, res) => {
    res.send('<h2>Hello from Express.js server!!</h2>');
});
 
// Server setup
app.listen(8080, () => {
    console.log('server listening on port 8080');
});
