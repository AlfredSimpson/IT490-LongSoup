function fetchRockBoards() {
    return axios.get('/api/get-rock-boards') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchRapBoards() {
    return axios.get('/api/get-rap-boards') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchPunkBoards() {
    return axios.get('/api/get-punk-boards') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchPopBoards() {
    return axios.get('/api/get-pop-boards') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchAllTalkBoards() {
    return axios.get('/api/get-all-boards') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}


document.addEventListener('DOMContentLoaded', () => {
    const genreTalkButtons = document.getElementById('genreTalkButtons');
    genreTalkButtons.addEventListener('click', (event) => {
        if (event.target.classList.contains('genreTalkButton')) {
            const genre = event.target.id;
            let fetchFunction;

            switch (genre) {
                case 'alltalk':
                    fetchFunction = fetchAllTalkBoards;
                    break;
                case 'rocktalk':
                    fetchFunction = fetchRockBoards;
                    break;
                case 'punktalk':
                    fetchFunction = fetchPunkBoards;
                    break;
                case 'poptalk':
                    fetchFunction = fetchPopBoards;
                    break;
                case 'raptalk':
                    fetchFunction = fetchRapBoards;
                    break;
            }

            fetchFunction()
                .then(data => {
                    const tableContainer = document.getElementById('tableContainer');
                    const table = createTable(data);
                    replaceTable(tableContainer, table);
                })
                .catch(error => {
                    console.error(`Error fetching data: ${error.message}`);
                });
        }
    });

    const sendButton = document.getElementById('sendMessageButton');
    sendButton.addEventListener('click', async () => {
        const messageContent = document.getElementById('messageContentInput').value;
        const genre = document.getElementById('genreSelect').value;

        if (messageContent && genre) {
            try {
                await sendMessage(messageContent, genre);

            } catch (error) {
                console.error(`Error sending message: ${error.message}`);
            }
        } else {
            console.error('Message content and genre are required.');
        }
    });

    // Make the sendMessage function async
    async function sendMessage(messageContent, genre) {
        try {
            const response = await axios.post('/api/send-message', {
                messageContent,
                genre
            });
            return response.data;
        } catch (error) {
            throw new Error(`Error sending message: ${error.message}`);
        }
    }
});
