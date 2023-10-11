<?php
require_once('path.inc');
require_once('get_host_info.inc');
require_once('rabbitMQLib.inc');

// Per Prof - we can probably comment out most of this.
// Note, rabbit.ini and tempServer are *currently being used* for testing purposes.
$client = new rabbitMQClient("rabbit.ini", "tempServer");

//  This stays, but only bc message needs defined. This takes command line args.
if (isset($argv[1])) {
    $msg = $argv[1];
} else {
    $msg = "oh hi mark";
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $useremail = $_POST['useremail'] ?? null;
    $password = $_POST['password'] ?? null;

    // Existing RabbitMQ code
    $request = array();
    if ($request['type'] == "login") {
        $request['type'] = "login";
        $request['useremail'] = $useremail;
        $request['password'] = $password;
        $request['message'] = "email = " . $useremail . " and password " . $password . ". and this was uname: " . $_POST;
    } elseif ($request['type'] == "register") {
        $request['type'] = "register";
        $request['first_name'] = $first_name;
        $request['last_name'] = $last_name;
        $request['useremail'] = $useremail;
        $request['password'] = $password;
        $request['message'] = "A new user is attempting to register.";
    }

    $response = $client->send_request($request);
    echo JSON_encode($response);
}
?>