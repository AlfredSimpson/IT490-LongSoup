// Store a script here or something. Just holding a space until we're ready to go.

function SendLoginRequest(useremail, password) {
    var request = new XMLHttpRequest();
    request.open("POST", "send.php", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    request.onreadystatechange = function () {
        if ((this.readyState == 4) && (this.status == 200)) {
            HandleLoginResponse(this.responseText);
        }
    }
    if (useremail != null && password != null) {
        request.send("type=login&useremail=" + useremail + "&password=" + password);
    }
}

function sendRegisterRequest(useremail, password, firstname, lastname) {
    var request = new XMLHttpRequest();
    request.open("POST", "send.php", true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
   // console.log("user_email",user_email,password,firstname,lastname)
    console.log(useremail);
	console.log(password);
	console.log(firstname);
	console.log(lastname);
	request.onreadystatechange = function () {
        if ((this.readyState == 4) && (this.status == 200)) {
            HandleRegisterResponse(this.responseText);
        }
    }
    if (useremail != null && password != null && firstname != null && lastname != null) {
        request.send("type=register&useremail=" + useremail + "&password=" + password + "&firstname=" + first_name + "&lastname=" + last_name);
    }
}
function HandleLoginResponse(response) {
    var text = JSON.parse(response);
    console.log("Login response and text:");
    console.log(response);
    console.log(text);
    //    document.getElementById("textResponse").innerHTML = response+"<p>";
    document.getElementById("textResponse").innerHTML = "Yeah, that's a user alright!" + "<p>";
    if (text.errorMessage) {
        document.getElementById("textResponse").innerHTML = text.errorMessage + "<p>";
    }
    else {
        // Note, we didn't create this yet. We will create it in the next step. This would *actually be the the login*
        if (text.returnCode == 1) {
            console.log("redirecting to user profile");
            window.location.href = "/userprofile.php";
        }
        if (text.returnCode == 0) {
            document.getElementById("textResponse").innerHTML = "Login Result 0 - No meaning yet." + "<p>";
        }
    }
}

function sendFormData() {
    // Prevent default form submission
    event.preventDefault();

    // Get username and password from form
    var useremail = document.getElementById('useremail').value;
    var password = document.getElementById('password').value;

    // Call your existing function to send the data
    SendLoginRequest(useremail, password);

    // Return false to prevent normal form submission
    return false;
}

function sendRegisterFormData() {
    // Prevent default form submission
    event.preventDefault();

    // Get username and password from form
    var useremail = document.getElementById('regemail').value;
	console.log("useremail in sendRegForm", useremail);
    var password = document.getElementById('regpassword').value;
	console.log("password in sendRegForm", password);
    var firstname = document.getElementById('first_name').value;
    var lastname = document.getElementById('last_name').value;

    // Call your existing function to send the data
    sendRegisterRequest(useremail, password, firstname, lastname);

    // Return false to prevent normal form submission
    return false;
}
