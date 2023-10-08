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
        <label for="nothingbutton">Send a nothing burger to the server</label>
        <input type="submit" name="nothingbutton" value="button pressed">
    </form>
    <!-- A button that, when clicked, gets the user from the database whose user id = 1 -->
    <form action="./getuser.php" method="post">
        <label for="somethingButton">Get user from database</label>
        <input type="submit" name="somethingButton" value="button pressed">
    </form>
    <!-- After pressing the somethingButton, if a user is found, it will display the user's name. If not, it will display "no user found" -->



</body>

</html>