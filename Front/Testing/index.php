<!-- This is the index of a test page -->
<!DOCTYPE html>
<html>

<head>
    <title>Test Page</title>
</head>

<body>
    <h1>Test Page</h1>
    <p>This is a test page.</p>
    <p>It is used to test rabbit connectivitiy.</p>
    <!-- A button that, when clicked, sends "button pressed" to the Broker using php-->
    <form action="./send.php" method="post">
        <input type="submit" name="button" value="button pressed">
</body>

</html>