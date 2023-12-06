document.getElementById("queryButton").addEventListener("click", function (e) {
    e.preventDefault(); // Prevent the form from submitting the traditional way

    // Get the form data
    const query_type = document.getElementById("query_type").value;
    const by = document.getElementById("by_type").value;
    const query = document.getElementById("query").value;

    // Create a payload object with the form data
    const payload = {
        query_type: query_type,
        by_type: by,
        query: query,
    };
    axios.post('/api/query', payload)
        .then(response => {
            // Isolate the query_results from the response
            var return_type = response.data.returnType;
            var query_results = response.data.message.query_results;
            var return_type = response.data.returnType;
            // console.log(query_results);
            populateData(return_type, query_results);
        })
        .catch(error => {
            console.error(error);
        });
});

function createTableRow(data, rowIndex, type_of) {
    // console.log(`\n\tType of: ${type_of}    Data: ${data}`);
    const row = document.createElement('tr');

    // use the keys of the data object to create the column headers
    const columns = Object.keys(data);

    row.id = `row-${data.id}`; // Optional: Add a unique ID to each row


    // For each key in data, create a column with the key's value.
    Object.keys(data).forEach(key => {
        // If key is url, create a link that says Listen Now. If the key is id, skip it. Using a switch statement:

        switch (key) {
            case 'url':
                var column = document.createElement('td');
                var link = document.createElement('a');
                link.classList.add("bg-info");
                link.classList.add("link-dark");
                link.href = data[key];
                link.textContent = 'Listen Now';
                link.target = "_blank";
                column.appendChild(link);
                row.appendChild(column);
                break;
            case 'id':
                console.log(`Skipping ${key}`);
                break;
            default:
                var column = document.createElement('td');
                column.textContent = data[key];
                row.appendChild(column);
                break;
        }
    });


    // Create like and dislike buttons
    const likeButton = document.createElement('button');
    likeButton.type = "button";
    likeButton.classList.add("btn");
    likeButton.classList.add("btn-success");
    likeButton.classList.add("rounded");
    likeButton.classList.add("bg-success");
    likeButton.textContent = 'Like';
    likeButton.id = `like-${data.id}`;
    console.log(`\n type_of is ${type_of} just before handling like/dislike\n`);
    likeButton.addEventListener('click', () => handleLikeDislike(data.id, 'like', type_of));

    const dislikeButton = document.createElement('button');
    dislikeButton.textContent = 'Dislike';
    dislikeButton.type = "button";
    dislikeButton.classList.add("btn");
    dislikeButton.classList.add("btn-warning");
    dislikeButton.classList.add("rounded");
    dislikeButton.classList.add("bg-warning");
    dislikeButton.id = `dislike-${data.id}`;
    dislikeButton.addEventListener('click', () => handleLikeDislike(data.id, 'dislike', query_type));

    // Create the fourth column with buttons
    const buttonsColumn = document.createElement('td');
    buttonsColumn.appendChild(likeButton);
    buttonsColumn.appendChild(dislikeButton);
    row.appendChild(buttonsColumn);

    return row;
}

function populateData(return_type, query_results) {
    console.log(`\nAttempting to populate the data for ${return_type}`);
    const QTYPE = return_type;
    query_results_container = document.getElementById("query_results_container");

    // get the table container by class name
    table = document.getElementById("query_results_table");
    // Get the table container and set the id of the table being generated
    // Create the header row with the column names

    // Delete everything in the table
    table.innerHTML = "";

    const headerRow = document.createElement("tr");
    headerRow.classList.add("bg-secondary");
    headerRow.classList.add("text-white");

    var tableheaders = Object.keys(query_results[0]);
    console.log(`tableheaders is showing as ${tableheaders}`);
    trackquery = ["Track", "Artist", "URLs", "Like/Dislike"] // If they're looking for
    artistquery = ["Artist", "Genres", "URLs", "Like/Dislike"]
    albumquery = ["Album", "Artist", "URLs", "Like/Dislike"]

    switch (return_type) {
        case "track":
            trackquery.forEach((columnData) => {
                const column = document.createElement("th");
                column.textContent = columnData;
                headerRow.appendChild(column);
            });
            break;
        case "album":
            albumquery.forEach((columnData) => {
                const column = document.createElement("th");
                column.textContent = columnData;
                headerRow.appendChild(column);
            });
            break;
        case "artist":
            artistquery.forEach((columnData) => {
                const column = document.createElement("th");
                column.textContent = columnData;
                headerRow.appendChild(column);
            });
            break;
        default:
            break;
    }
    // console.log(`\nPost switch statement, the QTYPE is ${QTYPE}`);
    table.appendChild(headerRow);
    // console.log(`\nAttempting to populate the data for ${QTYPE} after he header row\n`);
    query_results.forEach((item) => {
        // console.log(`\nQTYPE IS ${QTYPE} within the forEach loop`)
        const row = createTableRow(data = item, rowIndex = 0, type_of = return_type);
        table.appendChild(row);
    });
    if (query_results_container.firstChild) {
        query_results_container.removeChild(query_results_container.firstChild);
    }
    query_results_container.appendChild(table);

}

/**
 * Function to handle like/dislike button clicks
 * TODO: update the server side to handle the logic.
 */
function handleLikeDislike(rowId, action, query_type) {
    // Send the rowId and action to the server for processing
    // We also need to get the type of query that was performed

    console.log(`[Handler] \t Sending ${action} for row ${rowId} for query type ${query_type}`);
    axios.post('/api/like-dislike', { rowId, action, query_type })
        .then(response => {
            // Handle the response from the server (e.g., update UI)
            console.log(response.data);
        })
        .catch(error => {
            // Handle errors
            console.error(error);
        });
}