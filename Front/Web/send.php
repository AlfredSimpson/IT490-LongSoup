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
    $type = $_POST['type'] ?? null;

    // Existing RabbitMQ code
    $request = array();
    if ($type == "login") {
        $request['type'] = "login";
        $request['useremail'] = $useremail;
        $request['password'] = $password;
        $request['message'] = "email = " . $useremail . " and password " . $password . ". and this was uname: " . $_POST;
    } elseif ($type == "register") {
	    $fname = $_POST['firstname'] ?? null;
	    $lname = $_POST['lastname'] ?? null;
	    $email = $_POST['useremail'] ?? null;
	    $pass  = $_POST['password'] ??null;

            $request['type'] = "register";
            $request['first_name'] = $fname;
        $request['last_name'] = $lname;
        $request['useremail'] = $email;
        $request['password'] = $pass;
        $request['message'] = $_POST['first_name']."is a new user is attempting to register.";
    }

    $response = $client->send_request($request);
    echo JSON_encode($response);
}
?>
