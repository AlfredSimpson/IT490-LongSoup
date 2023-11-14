document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const type = "login";
        const useremail = document.getElementById("useremail").value;
        const password = document.getElementById("password").value;
        const message = "";
	console.log(password came as `${password}`);
        sendData("/login", { type, useremail, password, message });
    });

    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const type = "register";
        const regemail = document.getElementById("regemail").value;
        const regpassword = document.getElementById("regpassword").value;
        const message = "";
        sendData("/register", { type, regemail, regpassword, message });
    });

    function sendData(endpoint, data) {
        fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        }).then((response) => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
    }
});
