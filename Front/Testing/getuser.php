<!-- A php file that will call to the DB server and try to confirm if a user exists. if It does, it will return the user's name. If not, it will return "no user found" -->
<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');

// Note, rabbit.ini and dbServer are *currently being used* for testing purposes.

// Establish a connection to the DB server with the rabbit.ini file
$client = new rabbitMQClient("rabbit.ini", "dbServer");

// send a request to the DB server to get the user with the id of 1
$request = array();
$request['type'] = "getUser";
$request['id'] = 1;
$response = $client->send_request($request);

// If no user was found, return "no user found". If a user was found, display their name
if ($response == "no user found") {
    echo "no user found";
} else {
    echo "user found: " . $response;
}

echo "\n\n";

echo $argv[0] . " END" . PHP_EOL;
?>