const mustang = require('./mustang');
const { exec } = require('child_process');
require('dotenv').config();

// Load the dotenv files

D_USER = process.env.D_USER;
D_PASS = process.env.D_PASS;
D_HOST = process.env.D_HOST;
D_PORT = process.env.D_PORT;
D_VHOST = process.env.D_VHOST;
D_QUEUE = process.env.D_QUEUE;



/**
 * This is my attempt to create a function that will send a message to our deployment server.
 * Mustang handles the actual sending, just as before.
 * This application is run via app.js, where we are.
 * It will prompt a user for input, and then send that input to the deployment server's rabbitmq queue.
 * 
 */

// Prompt the user for input
const prompt = require('prompt-sync')();


function tarDirectory(deploy_file, dir_path) {
    /**
     * This tars the file and moves it to the outbox
     * @param {string} deploy_file The file we are creating
     * @param {string} dir_path The directory we are tarring
     */
    console.log(`[TARRING] ${dir_path} to ${deploy_file}`)
    exec(`tar -czvf ${deploy_file} ${dir_path}`, (error, stdout, stderr) => {
        if (error) {
            console.log(`[APP] error: ${error.message}`);
            return;
        }
        if (stderr) {
            console.log(`[APP] stderr: ${stderr}`);
            return;
        }
        console.log(`[APP] stdout: ${stdout}`);
    });
}


function sendToDeploymentServer() {
    /**
     * This will gather the information we need and then send it to the deployment server.
     * It takes no parameters, but prompts the user for input.
     * 
     * */
    console.log(`Starting Deployment process - Sit tight. I need information. This should tar everything up for you, I just need to know what to tar and where.`);
    const deploy_url = `amqp://${D_USER}:${D_PASS}@${D_HOST}:${D_PORT}/${D_VHOST}`;

    const deploy_queue = D_QUEUE;
    var cluster = "dev";
    // var cluster = "qa";
    // var cluster = "prod";
    var dir_path = prompt('Provide the full filepath of the directory we are transporting: ');
    var file_name = prompt('What is this package called? Use the name of the directory usually... : ');
    var server = prompt('Provide the name of the home server(front, back, dmz): ');

    const deploy_dir = "/home/outbox";
    const deploy_file = `${deploy_dir}/${file_name}.tar.gz`;
    // This tars the file and moves it to the outbox
    try {
        tarDirectory(deploy_file, dir_path);

    } catch (error) {
        console.log(`[APP] error: ${error.message}`);
        return;
    }
    file_name = `${file_name}.tar.gz`;
    mustang.sendAndConsumeMessage(deploy_url, deploy_queue,
        {
            "type": "deploy",
            "cluster": cluster,
            "server": server,
            "file_name": file_name,
            "file_path": deploy_file
        }, (response) => {
            console.log(`[APP] The response is ${response}`);
        })
    /**
     * This will gather the information we need and then send it to the deployment server. 
     */
    // exec(`tar -cvf ${fileName}.tar ${filePath}`, (error, stdout, stderr) => {
    //     if (error) {
    //         console.log(`[APP] error: ${error.message}`);
    //         return;
    //     }
    //     if (stderr) {
    //         console.log(`[APP] stderr: ${stderr}`);
    //         return;
    //     }
    //     console.log(`[APP] stdout: ${stdout}`);
    // });
}

sendToDeploymentServer();

