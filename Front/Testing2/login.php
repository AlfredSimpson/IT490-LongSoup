<!-- A php file of a front end webpage that logs into the database through rabbitmq using the information in ../database/example.sql -->

<?php
// seesion_start() is used to start a session
session_start();
// include_once() is used to include and evaluate the specified file only once
include_once('../rabbit/rabbitMQLib.inc');
// rabbitMQClient() is used to create a new rabbitMQClient using the specified ini file
$client = new rabbitMQClient("../rabit/rabbitMQ.ini", "testServer");
// if() is used to determine if a variable is set and is not NULL
if (isset($argv[1])) {
    // $msg is set to the first argument given
    $msg = $argv[1];
} else {
    $msg = "test message";
}

// Generate a session token
$session_token = bin2hex(random_bytes(64));  // NEW LINE

// $request is set to an array with the type of request, username, and password
$request = array();
$request['type'] = "login";
$request['username'] = $_POST['username'];
$request['password'] = $_POST['password'];
$request['session_token'] = $session_token;  // NEW LINE
// $response is set to the response from the server after providing the request
$response = $client->send_request($request);
//$response = $client->publish($request);

echo "client received response: " . PHP_EOL;
print_r($response);
echo "\n\n";
if ($response == 1) {
    $_SESSION['username'] = $_POST['username'];
    $_SESSION['session_token'] = $session_token;  // NEW LINE
    setcookie("session_token", $session_token, time() + 3600, "/");  // <-- NEW LINE, TOKEN SET FOR AN HOUR
    header("location: ../index.php");
} else {
    header("location: ../login.php");
}
?>