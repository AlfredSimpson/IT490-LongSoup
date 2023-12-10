const mustang = require('./mustang');
const { exec } = require('child_process');
require('dotenv').config();
// Prompt the user for input
const prompt = require('prompt-sync')();

// Load the dotenv files

D_USER = process.env.DEPLOYMENT_USER;
D_PASS = process.env.DEPLOYMENT_PASSWORD;
D_HOST = process.env.DEPLOYMENT_HOST;
D_PORT = process.env.DEPLOYMENT_PORT;
D_VHOST = process.env.DEPLOYMENT_vHOST;
D_QUEUE = process.env.DEPLOYMENT_QUEUE;



function start_qa() {
    /**
     * start_qa() is our main function - it will start by asking the user which server they are on. Then it will message the deployment server.
     * Deployment server will respond letting it know if there are packages to check.
     * If there are packages to check, it will prompt the user to select one.
     * It will then prompt the user to state if it passed or failed in qa.
     * Finally, it sends this information to the deployment server.
     */
    console.log(`[APP] Starting QA Process`);
    cluster = "qa";
    server = prompt(`Which server are you on (front, back, dmz): `);
    console.log('[APP] Checking if there are any packages awaiting approval');
    const deploy_url = `amqp://${D_USER}:${D_PASS}@${D_HOST}:${D_PORT}/${D_VHOST}`;
    const deploy_queue = D_QUEUE;
    mustang.sendAndConsumeMessage(deploy_url, deploy_queue, {
        type: "check_qa",
        cluster: cluster,
        server: server
    }, (response) => {
        var response = JSON.parse(response.content.toString());
        var returnCode = response.returnCode;
        var returnMessage = response.message;
        if (returnCode == 0) {
            console.log(`[APP] ${returnMessage}`);
            var packages = response.packages
            // packages should have a key number and value name, so we should iterate over all of them, printing the key and value

            // If packages is empty, we should exit
            if (Object.keys(packages).length === 0) {
                console.log(`[APP] No packages to check`);
                time.sleep(10);
                exit(0);
            }

            for (const [key, value] of Object.entries(packages)) {
                console.log(`${key}: ${value}`);
            }
            var choice = prompt(`\nWhich package do you want to check (type the number of the package): `);
            // if the user selects a number that is not in the list, we should prompt them again until they select a valid number
            while (!(choice in packages)) {
                console.log(`\n[APP] ${choice} is not a valid choice\n`);
                choice = prompt(`\nWhich package do you want to check (type the number of the package): `);
            }
            console.log(`\n[APP] You selected ${choice}, which is ${packages[choice]}\n`);
            var task = prompt(`\nChoose a task:\n1\tApprove package, \n2\tFail package, \n3\tExit\n`);

            if (task == 1 || task == 2) {
                // send to the deployment server
                if (task == 1) {
                    task = 0;
                } else {
                    task = -1;
                }
                console.log(`[APP] Sending ${packages[choice]} to deployment server with status of ${task}`);
                mustang.sendAndConsumeMessage(deploy_url, deploy_queue, {
                    type: "stage_2",
                    cluster: cluster,
                    server: server,
                    package_name: packages[choice],
                    status: task
                }, (response) => {
                    var response = JSON.parse(response.content.toString());
                    var returnCode = response.returnCode;
                    var returnMessage = response.message;
                    if (returnCode == 0) {
                        console.log(`[APP] ${returnMessage}`);
                    } else {
                        console.log(`[APP] ${returnMessage}`);
                    }
                })
            }
            else {
                console.log('[APP] Exiting');
                return

            }
        }
        else {
            console.log(`[APP] ${returnMessage}`);
        }
    })
}


start_qa()