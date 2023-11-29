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
    exec(`tar -czvf ${deploy_file} -C${dir_path} .`, (error, stdout, stderr) => {
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
    var package_name = prompt('What is this package called? Use the name of the directory usually... : ');
    var server = prompt('Provide the name of the home server(front, back, dmz): ');
    var description = prompt('Provide a short description of the package: ');

    const deploy_dir = "/home/outbox";
    const deploy_file = `${deploy_dir}/${package_name}.tar.gz`;
    // This tars the file and moves it to the outbox
    try {
        tarDirectory(deploy_file, dir_path);

    } catch (error) {
        console.log(`[APP] error: ${error.message}`);
        return;
    }
    var file_name = `${package_name}.tar.gz`;
    /**
     * Now we send it to the deployment server. 
     * Type is used to specify what stage of the deployment process we are in
     * Server is used so we know where this is coming from and going to. It helps the deploymentWorker locate the file.
     * file_path is the full path to the file we are sending.
     * package_name is used to identify the package later.
     * file_name is the name with .tar.gz at the end - so we can find the tarred file.
     * description is a short description of the package.
     * */
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

sendToDeploymentServer();

