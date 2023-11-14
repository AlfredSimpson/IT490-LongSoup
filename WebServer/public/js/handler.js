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
            var return_type = response.data.return_type;
            console.log(`Return Type showing as: ${return_type}`);
            var query_results = response.data.message.query_results;
            console.log(query_results);
            // document.getElementById("query_results").innerHTML = query_results;
            populateData(returnType, query_results);
        })
        .catch(error => {
            console.error(error);
        });
});

function createTableRow(data, rowIndex) {
    const row = document.createElement('tr');
    // const columns = ['Track Name', 'Artist Name', 'URLs'];
    // use the keys of the data object to create the column headers
    const columns = Object.keys(data);
    // columns.classList.add("bg-secondary");

    row.id = `row-${data.id}`; // Optional: Add a unique ID to each row

    console.log(`data is showing as ${data}`);
    // display the about of keys in the data object
    console.log(`data keys are showing as ${Object.keys(data)}`);
    // Create and add table columns

    // For each key in data, create a column with the key's value.
    Object.keys(data).forEach(key => {
        // console.log(`key is showing as ${key}`);
        const column = document.createElement('td');
        column.textContent = data[key];
        row.appendChild(column);
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
    likeButton.addEventListener('click', () => handleLikeDislike(data.id, 'like'));

    const dislikeButton = document.createElement('button');
    dislikeButton.textContent = 'Dislike';
    dislikeButton.type = "button";
    dislikeButton.classList.add("btn");
    dislikeButton.classList.add("btn-warning");
    dislikeButton.classList.add("rounded");
    dislikeButton.classList.add("bg-warning");
    dislikeButton.id = `dislike-${data.id}`;
    dislikeButton.addEventListener('click', () => handleLikeDislike(data.id, 'dislike'));

    // Create the fourth column with buttons
    const buttonsColumn = document.createElement('td');
    buttonsColumn.appendChild(likeButton);
    buttonsColumn.appendChild(dislikeButton);
    row.appendChild(buttonsColumn);

    return row;
}

function populateData(query_results) {
    console.log('Attempting to populate the data');
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
    trackquery = ["Track Name", "Artist Name", "URLs", "Like/Dislike"] // If they're looking for
    artistquery = ["Artist Name", "Track Name", "URLs", "Like/Dislike"]
    albumquery = ["Album Name", "Artist Name", "URLs", "Like/Dislike"]

    switch (returnType) {
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
    table.appendChild(headerRow);

    query_results.forEach((item) => {
        // console.log(`item: ${item} name as ${item.name} artist as ${item.artist} and url as ${item.url}`);
        const row = createTableRow(item);
        table.appendChild(row);
    });
    if (query_results_container.firstChild) {
        query_results_container.removeChild(query_results_container.firstChild);
    }
    query_results_container.appendChild(table);

}

// // Function to handle like/dislike button clicks
function handleLikeDislike(rowId, action) {
    // Send the rowId and action to the server for processing
    console.log(`[Handler] \t Sending ${action} for row ${rowId}`);
    axios.get('/api/like-dislike', { rowId, action }) // Replace with your API endpoint
        .then(response => {
            // Handle the response from the server (e.g., update UI)
            console.log(response.data);
        })
        .catch(error => {
            // Handle errors
            console.error(error);
        });
}