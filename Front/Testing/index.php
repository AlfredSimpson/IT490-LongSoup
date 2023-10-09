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
    <form action="" method="post">
        <label for="nothingbutton">Send a nothing burger to the server</label>
        <input type="submit" name="nothingbutton" value="button pressed">
    </form>
    <!-- A button that, when clicked, gets the user from the database whose user id = 1 -->
    <form action="./getuser.php" method="post">
        <label for="somethingButton">Get user from database</label>
        <input type="submit" name="somethingButton" value="button pressed">
    </form>
    <form id="login" class="login">
        <div>
            <label for="uname"><b>Username</b></label>
            <input id="username" name="uname" required />
        </div>
        <div>
            <label for="password"><b>Password</b></label>
            <input id="password" type="password" name="password" required />
        </div>
        <div>
            <input type="submit" value="Login" />
        </div>
    </form>
    <p id="textResponse">
    </p>

    <!-- After pressing the somethingButton, if a user is found, it will display the user's name. If not, it will display "no user found" -->
    <script>
        function SendLoginRequest(username, password) {
            var request = new XMLHttpRequest();
            request.open("POST", "send.php", true);
            request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            request.onreadystatechange = function () {

                if ((this.readyState == 4) && (this.status == 200)) {
                    HandleLoginResponse(this.responseText);
                }
            }
            if (username != null && password != null) {
                request.send("type=login&uname=" + username + "&password=" + password);
            }
        }
    </script>
    <script>
        function HandleLoginResponse(response) {
            var text = JSON.parse(response);
            console.log(response);
            //    document.getElementById("textResponse").innerHTML = response+"<p>";
            console.log(text);
            document.getElementById("textResponse").innerHTML = "Login Here!" + "<p>";
            if (text.errorMessage) {
                document.getElementById("textResponse").innerHTML = text.errorMessage + "<p>";
            }
            else {
                // Note, we didn't create this yet. We will create it in the next step.
                if (text.returnCode == 1) {
                    window.location.href = "/userprofile.php";
                }

                if (text.returnCode == 0) {
                    document.getElementById("textResponse").innerHTML = "Invalid Login" + "<p>";
                }
            }
        }

    </script>
    <script>   const params = new Proxy(new URLSearchParams(window.location.search), {
            get: (searchParams, prop) => searchParams.get(prop),
        });
        const username = params.uname;
        const password = params.password;
        SendLoginRequest(username, password);    
    </script>

</body>

</html>