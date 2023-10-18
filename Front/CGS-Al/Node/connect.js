document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const useremail = document.getElementById("useremail").value;
        const userpassword = document.getElementById("userpassword").value;
        sendData("/login", { useremail, userpassword });
    });

    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const regemail = document.getElementById("regemail").value;
        const regpassword = document.getElementById("regpassword").value;
        sendData("/register", { regemail, regpassword });
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
