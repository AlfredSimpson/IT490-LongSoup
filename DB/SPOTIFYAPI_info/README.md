# All about the Spotify API

https://developer.spotify.com/documentation/web-api/

We are using, among others, the Spotify API.

## Concepts


<details>
<summary>Everything Spotify says about API calls</summary>

### API Call Types
<details>
<summary>Different API call types</summary>

- GET
  - Retrieves a resources
- POST
  - Creates a resource
- PUT
  - Changes and/or replaces resources/collections
- DELETE
  - Deletes resources
</details>

#### Response Codes

<details>
<summary>Each of these should be considered as a possibile response code for any API call.</summary>

- 200
  - OK - Successful request
- 201
  - Created - Request fulfilled. New resource created
- 202
  - Accepted - the request has been accepted for processing, but the processing has not been completed
- 204
  - No Content - Request fulfilled. No content to return
- 304
  - Not modified (conditional request)
- 400
  - bad request
- 401
  - Unauthorized request. The request requires authentication or authorization.
- 403
  - Forbidden request. The server understood it, but will not do it.
- 404
  - Not Found. The requested resource is not found.
- 429
  - **Too Many Requests** - the death knell.
- 500
    - Internal server error. Spotify broke?
- 502
  - Bad Gateway - The server was acting as a gateway or proxy, received invalid response from upstream.
- 503
  - Service unavailable - Spotify broke.
</details>

### Response Errors

<details>
<summary>Different Web API error responses</summary>

- error
  - A high level description of the error
- error_description
  - A more detailed description of the error
</details>

### Regular Error Object

<details>
<summary> Unsuccessful responses return JSON objects containing other information: </summary>

  - status
    - An integer
    - HTTP status code that is also returned in the response header
  - message
    - A string
    - A short description of the cause of the error
</details>

### Conditional Requests
Most API responses contain appropriate cache-control headers set to assist in client-side caching

### Time Stamps
Spotify returns in YYY-MM-DDTHH:MM:SSZ format, 0 offset

### Pagination
As some requests may return extensive information, it may be paginated. These requests support offset and limits as query params

</details>


## Authorization


<details>
<summary>Authorization overview</summary>

- End user
  - The spotify user
- My App
  - Our app
- Server
  - Which hosts the protected resources and provides access to them via the Spotify API

</details>