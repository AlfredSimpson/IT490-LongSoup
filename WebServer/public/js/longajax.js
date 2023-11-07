function fetchData() {
    return axios.get('/api/get-songs') // Replace with your API endpoint
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

// Event listener for fetching data and creating the table
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('fetchDataButton').addEventListener('click', () => {
        fetchData()
            .then(data => {
                const tableContainer = document.getElementById('tableContainer');
                const table = document.createElement('table');
                table.classList.add('data-table'); // Optional: Apply CSS class for styling

                // Create table header (optional)
                const headerRow = document.createElement('tr');
                ['Header 1', 'Header 2', 'Header 3', 'Actions'].forEach(headerText => {
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
    });
});