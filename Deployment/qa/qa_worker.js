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





function check_qa() {

    mustang.sendAndConsumeMessage(deploy_url, deploy_queue,
        {
            "type": "stage_1",
            "cluster": cluster,
            "server": server,
            "file_path": deploy_file,
            "package_name": package_name,
            "file_name": file_name,
            "description": description
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
            var packages = response.packages;
            // console.log(`[APP] ${packages}`);
            // packages should have a key number and value name, so we should iterate over all of them, printing the key and value

            for (const [key, value] of Object.entries(packages)) {
                console.log(`${key}: ${value}`);
            }
            var choice = prompt(`Which package do you want to check (type the number of the package): `);
            // if the user selects a number that is not in the list, we should prompt them again until they select a valid number
            while (!(choice in packages)) {
                console.log(`[APP] ${choice} is not a valid choice`);
                choice = prompt(`Which package do you want to check (type the number of the package): `);
            }
            console.log(`[APP] You selected ${choice}, which is ${packages[choice]}`);
            var task = prompt(`Choose a task:\n1\tApprove package, \n2\tFail package, \n3\tExit\n`);
            // if the user selects a number that is not in the list, we should prompt them again until they select a valid number
            while (!(task in [1, 2, 3])) {
                console.log(`[APP] ${task} is not a valid choice`);
                task = prompt(`Choose a task:\n1\tApprove package, \n2\tFail package, \n3\tExit\n`);
            }
            if (task == 1 || task == 2) {
                // send to the deployment server
                if (task == 1) {
                    task = 0;
                } else {
                    task = -1;
                }
                console.log(`[APP] Sending ${packages[choice]} to deployment server with status of ${task}`);
                mustang.sendAndConsumeMessage(deploy_url, deploy_queue, {
                    type: "qa",
                    cluster: cluster,
                    server: server,
                    package: packages[choice],
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
                console.log(`[APP] ${returnMessage}`);
            }
        }
        //     if (returnCode == 0) {
        //         console.log(`[APP] ${returnMessage}`);
        //         var packages = response.packages;
        //         console.log(`[APP] ${packages}`);
        //         var package = prompt(`Which package do you want to check (type the name of the package): `);
        //         console.log(`[APP] You selected ${package}`);
        //         var status = prompt(`Did the package pass qa (y/n): `);
        //         console.log(`[APP] You selected ${status}`);
        //         if (status == "y") {
        //             status = "pass";
        //         } else {
        //             status = "fail";
        //         }
        //         console.log(`[APP] Sending ${package} to deployment server with status of ${status}`);
        //         mustang.sendAndConsumeMessage(deploy_url, deploy_queue, {
        //             type: "qa",
        //             cluster: cluster,
        //             server: server,
        //             package: package,
        //             status: status
        //         }, (response) => {
        //             var response = JSON.parse(response.content.toString());
        //             var returnCode = response.returnCode;
        //             var returnMessage = response.message;
        //             if (returnCode == 0) {
        //                 console.log(`[APP] ${returnMessage}`);
        //             } else {
        //                 console.log(`[APP] ${returnMessage}`);
        //             }
        //         })
        //     } else {
        //         console.log(`[APP] ${returnMessage}`);
        //     }
        // })
    })
}


start_qa()