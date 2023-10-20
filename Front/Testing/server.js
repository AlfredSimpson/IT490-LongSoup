const express = require('express');
const app = express();
const port = 3000;

// Set Content-Security-Policy
app.use((req, res, next) => {
    res.setHeader("Content-Security-Policy", "default-src 'self' http://localhost:3000;");
    next();
  });

// Serve static files from your directory
app.use(express.static('/home/vboxuser/IT490-LongSoup'));

// Handle POST requests
app.post('/home/vboxuser/IT490-LongSoup/Front/Testing/send.php', (req, res) => {
  // Your POST handling code here
  res.send('POST request received');
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});
