function fetchRock() {
    return axios.get('/api/get-rock') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchRap() {
    return axios.get('/api/get-rap') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchPunk() {
    return axios.get('/api/get-punk') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchPop() {
    return axios.get('/api/get-pop') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}
function fetchSuggested() {
    return axios.get('/api/get-suggested') // Replace with your API endpoint
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}

// Function to create the table row with like/dislike buttons
function createTableRow(data, rowIndex) {
    const row = document.createElement('tr');
    const columns = ['Track Name', 'Artist Name', 'URLs'];

    row.id = `row-${data.id}`; // Optional: Add a unique ID to each row

    // Create and add table columns
    columns.forEach(columnData => {
        const column = document.createElement('td');
        column.textContent = columnData;
        row.appendChild(column);
    });

    // Create like and dislike buttons
    const likeButton = document.createElement('button');
    likeButton.textContent = 'Like';
    likeButton.id = `like-${data.id}`;
    likeButton.addEventListener('click', () => handleLikeDislike(data.id, 'like'));

    const dislikeButton = document.createElement('button');
    dislikeButton.textContent = 'Dislike';
    dislikeButton.id = `dislike-${data.id}`;
    dislikeButton.addEventListener('click', () => handleLikeDislike(data.id, 'dislike'));

    // Create the fourth column with buttons
    const buttonsColumn = document.createElement('td');
    buttonsColumn.appendChild(likeButton);
    buttonsColumn.appendChild(dislikeButton);
    row.appendChild(buttonsColumn);

    return row;
}

// Function to handle like/dislike button clicks
function handleLikeDislike(rowId, action) {
    // Send the rowId and action to the server for processing
    axios.post('/api/like-dislike', { rowId, action }) // Replace with your API endpoint
        .then(response => {
            // Handle the response from the server (e.g., update UI)
            console.log(response.data);
        })
        .catch(error => {
            // Handle errors
            console.error(error);
        });
}

document.addEventListener('DOMContentLoaded', () => {
    const genreButtons = document.getElementById('genreButtons');
    genreButtons.addEventListener('click', (event) => {
        if (event.target.classList.contains('genreButton')) {
            const genre = event.target.id;
            let fetchFunction;
            switch (genre) {
                case 'rock':
                    fetchFunction = fetchRock;
                    break;
                case 'rap':
                    fetchFunction = fetchRap;
                    break;
                case 'punk':
                    fetchFunction = fetchPunk;
                    break;
                case 'pop':
                    fetchFunction = fetchPop;
                    break;
                case 'suggestedartists':
                    fetchFunction = fetchSuggested;
                    break;
            }
            fetchFunction()
                .then(data => {
                    const tableContainer = document.getElementById('tableContainer');
                    const table = document.createElement('table');
                    table.classList.add('data-table'); // Optional: Apply CSS class for styling

                    // Create table header (optional)
                    const headerRow = document.createElement('tr');
                    ['Track Name', 'Artist Name', 'URLs', 'Actions'].forEach(headerText => {
                        const th = document.createElement('th');
                        th.textContent = headerText;
                        headerRow.appendChild(th);
                    });
                    table.appendChild(headerRow);

                    // Create table rows and add data
                    data.forEach(item => {
                        const row = createTableRow(item);
                        table.appendChild(row);
                    });

                    // Replace existing table if it exists
                    if (tableContainer.firstChild) {
                        tableContainer.removeChild(tableContainer.firstChild);
                    }

                    // Append the new table to the container
                    tableContainer.appendChild(table);
                })
                .catch(error => {
                    // Handle errors
                    console.error(error);
                });
        }
    })
    const genreTalkButtons = document.getElementById('genreTalkButtons');
    genreTalkButtons.addEventListener('click', (event) => {
        if (event.target.classList.contains('genreButton')) {
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

    // Functions to fetch data from your server using Axios
    async function fetchData(apiEndpoint) {
        try {
            const response = await axios.get(apiEndpoint);
            return response.data;
        } catch (error) {
            throw new Error(`Error fetching data from ${apiEndpoint}: ${error.message}`);
        }
    }

    // Functions for fetching boards
    async function fetchAllTalkBoards() {
        return fetchData('/api/get-all-talk');
    }
    function fetchRockBoards() {
        return axios.get('/api/get-rock-boards')
            .then(response => response.data)
            .catch(error => {
                throw error;
            });
    }
    async function fetchRockBoards() {
        return fetchData('/api/get-rock-boards');
    }

    async function fetchPunkBoards() {
        return fetchData('/api/get-punk-boards');
    }

    async function fetchRapBoards() {
        return fetchData('/api/get-rap-boards');
    }

    async function fetchPopBoards() {
        return fetchData('/api/get-pop-boards');
    }


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
