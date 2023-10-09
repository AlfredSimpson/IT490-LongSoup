<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');

// Per Prof - we can probably comment out most of this shit.
// Note, rabbit.ini and tempServer are *currently being used* for testing purposes.
$client = new rabbitMQClient("rabbit.ini", "tempServer");
if (isset($argv[1])) {
    $msg = $argv[1];
} else {
    $msg = "test message";
}

// Note, this doesn't pass the username or password yet, only these fake ones.
$request = array();
$request['type'] = "Login";
$request['username'] = $_POST['username'];
$request['password'] = $_POST['password'];
$request['message'] = $msg;
$response = $client->send_request($request);
//$response = $client->publish($request);

//echo "client received response: " . PHP_EOL;
//print_r($response);
echo JSON_encode($response);
// var_dump($response);
//echo "\n\n";
echo $argv[0] . " END" . PHP_EOL;
?>