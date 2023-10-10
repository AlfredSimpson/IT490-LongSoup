<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');

// Per Prof - we can probably comment out most of this shit.
// Note, rabbit.ini and tempServer are *currently being used* for testing purposes.
$client = new rabbitMQClient("rabbit.ini", "tempServer");

//  This stays, but only bc message needs defined. This takes command line args.
if (isset($argv[1])) {
    $msg = $argv[1];
} else {
    $msg = "Testing testing test";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $useremail = $_POST['useremail'] ?? null;
    $password = $_POST['password'] ?? null;

    // Existing RabbitMQ code
    $request = array();
    $request['type'] = "Login";
    $request['useremail'] = $useremail;
    $request['password'] = $password;
    $request['message'] = "email = " . $useremail . " and password " . $password . ". and this was uname: " . $_POST;

    $response = $client->send_request($request);
    echo JSON_encode($response);
}
?>