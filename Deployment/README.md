# Deployment



We're tasked with creating our own deployment server.

## Setup the helpers

Our helpers should do the following:
1. Install necessary python libraries.
2. Make a clean copy of the files needed, zip them, and send them to the deployment server.
3. Once on the deployment server, send them to where they need to go. 
4. Once on the required server, unzip them and run the necessary commands to get them up and running.
5. If there are any errors, send them back to the deployment server.
6. If there are no errors, send a success message back to the deployment server.
7. If the deployment server receives a success message from the QA Cluster, send it to the Prod Cluster.

