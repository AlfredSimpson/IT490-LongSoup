// function fetchRockBoards() {
//     return axios.get('/api/get-rock-boards')
//         .then(response => response.data)
//         .catch(error => {
//             throw error;
//         });
// }
// function fetchRapBoards() {
//     return axios.get('/api/get-rap-boards')
//         .then(response => response.data)
//         .catch(error => {
//             throw error;
//         });
// }
// function fetchPunkBoards() {
//     return axios.get('/api/get-punk-boards')
//         .then(response => response.data)
//         .catch(error => {
//             throw error;
//         });
// }
// function fetchPopBoards() {
//     return axios.get('/api/get-pop-boards')
//         .then(response => response.data)
//         .catch(error => {
//             throw error;
//         });
// }
function fetchAllTalkBoards() {
    console.log(`[fetch all talk boards] \t Fetching all talk boards`);
    return axios.get('/api/get-all-boards')
        .then(response => response.data)
        .catch(error => {
            console.error(`[fetch all talk boards] \t Error fetching all talk boards: ${error.message}`);
            throw error;
        });
}

function replaceTable(tableContainer, newTable) {
    tableContainer.innerHTML = '';
    tableContainer.appendChild(newTable);
}

function createTable(data) {
    const table = document.createElement('table');
    table.classList.add('table', 'table-hover', 'table-bordered', 'table-striped', 'table-dark');
    table.innerHTML = `
        <thead>
            <tr>
                <th scope="col">Author</th>
                <th scope="col">Date</th>
                <th scope="col">Message</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    `;

    const tableBody = table.querySelector('tbody');
    data.forEach(message => {
        const row = document.createElement('tr');
        // TODO: update message.author to link to a profile - we'll needt to pass in a url and store urls in the database first, though.
        row.innerHTML = `
            <td>${message.author}</td>
            <td>${message.date}</td>
            <td>${message.message}</td>
        `;
        tableBody.appendChild(row);
    });

    return table;
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
                // case 'rocktalk':
                //     fetchFunction = fetchRockBoards;
                //     break;
                // case 'punktalk':
                //     fetchFunction = fetchPunkBoards;
                //     break;
                // case 'poptalk':
                //     fetchFunction = fetchPopBoards;
                //     break;
                // case 'raptalk':
                //     fetchFunction = fetchRapBoards;
                //     break;
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
        const board = document.getElementById('genreSelect').value;

        if (messageContent && board) {
            try {
                console.log(`Sending message ${messageContent} to board ${board}`);
                await sendMessage(messageContent, board);

            } catch (error) {
                console.error(`Error sending message: ${error.message}`);
            }
        } else {
            console.error('Message content and genre are required.');
        }
    });

    // Make the sendMessage function async
    async function sendMessage(messageContent, board) {
        console.log(`[sendMessage()] - Sending message ${messageContent} to board ${board}`);
        try {
            const response = await axios.post('/api/send-message', {
                messageContent,
                board
            });
            return response.data;
        } catch (error) {
            throw new Error(`Error sending message: ${error.message}`);
        }
    }
});
