const messageBoard = document.getElementById('message-board');
        const newMessageInput = document.getElementById('new-message');
        const postMessageButton = document.getElementById('post-message');

        postMessageButton.addEventListener('click', function() {
            const message = newMessageInput.value.trim();
            if (message !== '') {
                const messageElement = document.createElement('div');
                messageElement.textContent = message;
                messageBoard.appendChild(messageElement);
                newMessageInput.value = '';

                // Scroll to the bottom to show the latest message
                messageBoard.scrollTop = messageBoard.scrollHeight;
            }
        });


function showSpotUsers(spotifyUsers) {
    var userInfo;
    if (spotifyUsers = ""){
        document.getElementById("users").innerHTML = "";
        return;
    }
    userInfo = new XMLHttpRequest();
    userInfo.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200)
            document.getElementById("users").innerHTML = this.responseText;
    }
};
user.open("POST", "test.txt", true);
userInfo.send();