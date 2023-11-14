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
            var query_results = response.data.message.query_results;
            console.log(query_results);
            // document.getElementById("query_results").innerHTML = query_results;
            populateData(query_results);
        })
        .catch(error => {
            console.error(error);
        });
});

function createTableRow(data, rowIndex) {
    const row = document.createElement('tr');
    const columns = ['Track Name', 'Artist Name', 'URLs'];

    // row.id = `row-${data.id}`; // Optional: Add a unique ID to each row

    console.log(`data is showing as ${data}`);
    // display the about of keys in the data object
    console.log(`data keys are showing as ${Object.keys(data)}`);
    // Create and add table columns

    // For each key in data, create a column with the key's value.
    Object.keys(data).forEach(key => {
        console.log(`key is showing as ${key}`);
        const column = document.createElement('td');
        column.textContent = data[key];
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

function populateData(query_results) {
    console.log('Attempting to populate the data');
    query_results_container = document.getElementById("query_results_container");
    // get the table container by class name
    table = document.createElement("table");
    // Get the table container and set the id of the table being generated
    table.id = "query_results_table";
    table.classList.add("table-dark");
    table.classList.add("table-striped");
    // Create the header row with the column names
    const headerRow = document.createElement("tr");
    ["Track Name", "Artist Name", "URLs", "Like/Dislike"].forEach((columnData) => {
        const column = document.createElement("th");
        column.textContent = columnData;
        headerRow.appendChild(column);
    });
    table.appendChild(headerRow);

    query_results.forEach((item) => {
        console.log(`item: ${item} name as ${item.name} artist as ${item.artist} and url as ${item.url}`);
        const row = createTableRow(item);
        table.appendChild(row);
    });
    if (query_results_container.firstChild) {
        query_results_container.removeChild(query_results_container.firstChild);
    }
    query_results_container.appendChild(table);

}

// // Function to handle like/dislike button clicks
// function handleLikeDislike(rowId, action) {
//     // Send the rowId and action to the server for processing
//     console.log(`[Handler] \t Sending ${action} for row ${rowId}`);
//     axios.get('/api/like-dislike', { rowId, action }) // Replace with your API endpoint
//         .then(response => {
//             // Handle the response from the server (e.g., update UI)
//             console.log(response.data);
//         })
//         .catch(error => {
//             // Handle errors
//             console.error(error);
//         });
// }



// // // First, we need to wait for the DOM to be loaded
// document.addEventListener('DOMContentLoaded', () => {
//     // Then we need to get the query button, which has the id 'queryButton'
//     var queryButton = document.getElementById('queryButton');
//     // Then we need to add an event listener to the query button
//     queryButton.addEventListener('click', (event) => {
//         // If the query button is clicked, we need to get the value of the input box AND the value of the select box
//         var query = document.getElementById('query').value;
//         var queryT = document.getElementById('query_type').value;
//         var by = document.getElementById('by_type').value;
//         var uid = document.getElementById('uid').innerText;
//         console.log(`[HANDLER]          Query: ${query}, Query Type: ${queryT}, By Type: ${by}, UID: ${uid}`);
//         /**
//          * NOTE: DO NOT REMOVE THIS CONSOLE.LOG STATEMENT. THIS MAKES CHROME SAD. I DO NOT KNOW WHY.
//          * If we remove this, the code breaks. Not here, not in mustang, not even on the webserver.
//          * For some reason, when it reaches the database consumer, queryT gets yeeted. Again, no explanation. Just acceptance.
//          */
//         // console.log(`Query: ${donotdeleteme}`);
//         // axios.post('/api/query', { "uid": uid, "queryT": queryT, "query": query, "by": by })
//         console.log('We are about to query the API');
//         axios.post('/api/query', { "uid": uid, "queryT": queryT, "query": query, "by": by })
//             .then(query_results => {
//                 console.log('API has been queried... right?');
//                 // After the response, for each item in the response, we need to create a table row
//                 // and add it to the table
//                 // var m = response.message;
//                 // console.log(`[HANDLER]           Message from server: ${m}`);
//                 // var query_results = m.query_results;
//                 console.log(`[HANDLER]          Response from server: ${query_results}`)
//                 // console.log(response);
//                 var table = document.getElementById('query_results');
//                 table.innerHTML = '';

//                 query_results.forEach((item) => {
//                     var row = document.createElement('tr');
//                     var columns = ['Track Name', 'Artist Name', 'URLs', 'Like/Dislike'];
//                     row.id = `row-${item.id}`;

//                     columns.forEach(columnData => {
//                         const column = document.createElement('td');
//                         column.textContent = item[columnData];
//                         row.appendChild(column);
//                     });

//                     const likeButton = document.createElement('button');
//                     likeButton.classList.add('btn like');
//                     likeButton.textContent = 'Like';
//                     likeButton.id = `like-${item.id}`;
//                     likeButton.addEventListener('click', () => handleLikeDislike(item.id, 'like'));

//                     const dislikeButton = document.createElement('button');
//                     likeButton.classList.add('btn dislike');
//                     dislikeButton.textContent = 'Dislike';
//                     dislikeButton.id = `dislike-${item.id}`;
//                     dislikeButton.addEventListener('click', () => handleLikeDislike(item.id, 'dislike'));

//                     // Create the fourth column with buttons
//                     const buttonsColumn = document.createElement('td');
//                     buttonsColumn.appendChild(likeButton);
//                     buttonsColumn.appendChild(dislikeButton);
//                     row.appendChild(buttonsColumn);

//                     table.appendChild(row);
//                 });

//                 // Handle the response from the server (e.g., update UI)
//                 console.log(response.data);
//             })
//             .catch(error => {
//                 // Handle errors
//                 console.error(error);
//             });

//     });
// });