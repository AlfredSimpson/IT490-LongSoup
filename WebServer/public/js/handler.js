/**
 * queryAPI Takes 4 params, uid, queryT, query, and by. These are all strings or anything honestly.
 * We pass this to the server, which then passes it to the database consumer, which then passes it to the database.
 * We then await the response and, if we get the response, we return the response data.
 * @param {*} uid 
 * @param {*} queryT 
 * @param {*} query 
 * @param {*} by 
 * @returns JSON of whatever was being queried - hopefully cleaned appropriately. 
 */

function queryAPI(uid, queryT, query, by) {
    return axios.post('/api/query', { "uid": uid, "queryT": queryT, "query": query, "by": by })
        .then(response => response.data)
        .catch(error => {
            throw error;
        });
}

// Function to handle like/dislike button clicks
function handleLikeDislike(rowId, action) {
    // Send the rowId and action to the server for processing
    console.log(`[Handler] \t Sending ${action} for row ${rowId}`);
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

// First, we need to wait for the DOM to be loaded
document.addEventListener('DOMContentLoaded', () => {
    // Then we need to get the query button, which has the id 'queryButton'
    var queryButton = document.getElementById('queryButton');
    // Then we need to add an event listener to the query button
    queryButton.addEventListener('click', (event) => {
        // If the query button is clicked, we need to get the value of the input box AND the value of the select box
        var query = document.getElementById('query').value;
        var queryT = document.getElementById('query_type').value;
        var by = document.getElementById('by_type').value;
        var uid = document.getElementById('uid').innerText;

        /**
         * NOTE: DO NOT REMOVE THIS CONSOLE.LOG STATEMENT. THIS MAKES CHROME SAD. I DO NOT KNOW WHY.
         * If we remove this, the code breaks. Not here, not in mustang, not even on the webserver.
         * For some reason, when it reaches the database consumer, queryT gets yeeted. Again, no explanation. Just acceptance. 
         */
        console.log(`Query: ${donotdeleteme}`);
        // axios.post('/api/query', { "uid": uid, "queryT": queryT, "query": query, "by": by })
        queryAPI(uid, queryT, query, by)
            .then(response => {
                // After the response, for each item in the response, we need to create a table row
                // and add it to the table
                console.log(`[HANDLER]\t Response from server: \n\n${response}\n\n`)
                // console.log(response);
                var table = document.getElementById('query_results');
                table.innerHTML = '';

                response.data.forEach((item) => {
                    var row = document.createElement('tr');
                    var columns = ['Track Name', 'Artist Name', 'URLs', 'Like/Dislike'];
                    row.id = `row-${item.id}`;

                    columns.forEach(columnData => {
                        const column = document.createElement('td');
                        column.textContent = item[columnData];
                        row.appendChild(column);
                    });

                    const likeButton = document.createElement('button');
                    likeButton.classList.add('btn like');
                    likeButton.textContent = 'Like';
                    likeButton.id = `like-${item.id}`;
                    likeButton.addEventListener('click', () => handleLikeDislike(item.id, 'like'));

                    const dislikeButton = document.createElement('button');
                    likeButton.classList.add('btn dislike');
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