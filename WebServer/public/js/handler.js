

// First, we need to wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', () => {
    // Then we need to get the query button, which has the id 'queryButton'
    var queryButton = document.getElementById('queryButton');
    // Then we need to add an event listener to the query button
    queryButton.addEventListener('click', (event) => {
        // If the query button is clicked, we need to get the value of the input box AND the value of the select box
        var queryInput = document.getElementById('query').value;
        var querySelect = document.getElementById('query_type').value;
        console.log(`Query: ${queryInput} | Type: ${querySelect}`);
        // Then we need to send the query to the server
        axios.post('/api/query', { queryInput, querySelect })
            .then(response => {
                // After the response, for each item in the response, we need to create a table row
                // and add it to the table
                var table = document.getElementById('query_results');
                table.innerHTML = '';

                response.data.forEach((item) => {
                    var row = document.createElement('tr');
                    var columns = ['Track Name', 'Artist Name', 'URLs'];
                    row.id = `row-${item.id}`;

                    columns.forEach(columnData => {
                        const column = document.createElement('td');
                        column.textContent = item[columnData];
                        row.appendChild(column);
                    });

                    const likeButton = document.createElement('button');
                    likeButton.textContent = 'Like';
                    likeButton.id = `like-${item.id}`;
                    likeButton.addEventListener('click', () => handleLikeDislike(item.id, 'like'));

                    const dislikeButton = document.createElement('button');
                    dislikeButton.textContent = 'Dislike';
                    dislikeButton.id = `dislike-${item.id}`;
                    dislikeButton.addEventListener('click', () => handleLikeDislike(item.id, 'dislike'));

                    // Create the fourth column with buttons
                    const buttonsColumn = document.createElement('td');
                    buttonsColumn.appendChild(likeButton);
                    buttonsColumn.appendChild(dislikeButton);
                    row.appendChild(buttonsColumn);

                    table.appendChild(row);
                });

                // Handle the response from the server (e.g., update UI)
                console.log(response.data);
            })
            .catch(error => {
                // Handle errors
                console.error(error);
            });

    });
});