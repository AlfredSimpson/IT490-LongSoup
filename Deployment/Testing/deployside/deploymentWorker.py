import os

import shutil
import pymongo
import pika

# import paramiko
import pysftp
import json
import time
import sys
import re

# import subprocess
import logging
import threading


from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

host_user = os.getenv("remote_host_user")
host_pass = os.getenv("remote_host_pass")

qa_host_user = os.getenv("qa_host_user")
qa_host_pass = os.getenv("qa_host_pass")

prod_host_user = os.getenv("prod_host_user")
prod_host_pass = os.getenv("prod_host_pass")

db_name = "test_gather"
current = "current_packages"
previous = "previous_packages"
backups = "backup_packages"

IN_SERVERS = ["front", "back", "dmz"]

# Load the environmental variables
# First, the AMQP variables
vHost = os.getenv("DEPLOYMENT_vHOST")
D_USER = os.getenv("DEPLOYMENT_USER")
D_PASS = os.getenv("DEPLOYMENT_PASSWORD")
D_HOST = os.getenv("DEPLOYMENT_HOST")
D_Q = os.getenv("DEPLOYMENT_QUEUE")
D_X = os.getenv("DEPLOYMENT_EXCHANGE")

# Then the MongoDB variables
mongo_user = os.getenv("MONGO_USER_D")
mongo_pass = os.getenv("MONGO_PASSWORD_D")
mongo_host = os.getenv("MONGO_HOST_D")
mongo_port = os.getenv("MONGO_PORT_D")
mongo_db = os.getenv("MONGO_DB_D")


LOCAL_PATH = "/home/longsoup/DEPLOY/"

mongo_client = pymongo.MongoClient("mongodb://longsoup:njit#490@localhost:27017/")
db = mongo_client["deployment"]
current = "current_packages"
backups = "backup_packages"
all_packages = "all_packages"

package_schema = {
    "name": "",
    "version": 0,
    "date": "",
    "description": "",
    "server": "",
    "absolute_path": "",
    "qa_status": "",
}


def store_package(package_name, file_name, version):
    """So that we can keep track of all the packages, we need to store them in a local directory. All packages are stored in /home/longsoup/STORE.
    This function will take in the package_name and the version number and copy the package from /home/longsoup/DEPLOY to /home/longsoup/STORE.
    It modifies the name of the package to include the version number.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    Args:
        package_name (string): The name of the package we are storing.
        version (int): The version number

    Returns:
        bool: True or False if the package was copied successfully.
    """
    DEPLOY_PATH = "/home/longsoup/DEPLOY"
    LOCAL_STORE = "/home/longsoup/STORE"
    new_name = package_name + "_" + str(version) + ".tar.gz"
    try:
        shutil.copy2(DEPLOY_PATH + "/" + file_name, LOCAL_STORE + "/" + new_name)
        print(f"Package {package_name} copied to {LOCAL_STORE}")
        return True
    except Exception as e:
        print(f"Error copying package: {e}")
        return False


def retrieve_package(host_name, file_path, file_name):
    """Retrieve_packages takes in the host_name, the file_path, and the file_name.
    It will then connect to the host_name and retrieve the file from the file_path.
    It will then save the file to the local server in the /home/longsoup/DEPLOY/ directory.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    Args:
        host_name (string): The name of the host/server we are connecting to.
        file_path (string): The absolute path of the file we are retrieving.
        file_name (string): The name of the file we are retrieving.
    """
    LOCAL_NAME = "/home/longsoup/DEPLOY/" + file_name
    try:
        with pysftp.Connection(
            host=host_name, username=host_user, password=host_pass
        ) as sftp:
            print(f"Connected to {host_name}")
            sftp.get(file_path, LOCAL_NAME, callback=None, preserve_mtime=True)
            return True
    except Exception as e:
        print(f"Error retrieving package: {e}")
        return False


def get_last_version(db, package_name):
    """get_last_version will check the database to see if the package exists AND if it does, it will return the last version number.
    If the package does not exist, then it will return 0.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    Args:
        db (object): The database object we are connecting to.
        package_name (string): The name of the package we are checking for.

    Returns:
        int: 0 if the package does not exist, otherwise it will return the last version number.
    """

    cur = db[current]
    if cur.find_one({"name": package_name}):
        # If the package exists, then we need to get the last version number.
        last_version = cur.find_one({"name": package_name})["version"]
        print(
            f'\nPackage "{package_name}" exists in the database with version {last_version}.'
        )
        return last_version
    else:
        # If the package does not exist, then we need to create a new package.
        return 0


def make_package(name, version, date, description, server, source_path, qa_status):
    """# make_package is a function that will create a package object.
    It takes in the name, version, date, description, server, source_path, and qa_status.
    It will then return a package object.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    Args:
        name (string): The name of the package
        version (int): Version Number
        date (date): Date of the package
        description (string): Short Description of the package
        server (string): Which server does this package live on?
        source_path (string): Where did this package come from?
        qa_status (int): This is the status of the package. If it is in qa = 1, if it passes qa = 0, if it fails qa = -1.

    Returns:
        object: A package object to insert into the database.
    """
    package = {
        "name": name,
        "version": version,
        "date": date,
        "description": description,
        "server": server,
        "source_path": source_path,
        "qa_status": qa_status,
    }
    return package


def package_exists(db, package_name):
    """This function checks if the package exists in the database.

    This method works - but it is not actively used currently. I am not deleting it just in case we need it again in the future.
    """
    cur = db["current"]
    if cur.find_one({"name": package_name}):
        return True
    else:
        return False


def create_package(db, package_name, version, description, server, file_path):
    """# create_package
    This function will create a package in the database. It takes in the db, package_name, version, description, server, and file_path.
    It will *automatically* update the version number.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    #! Note: This requires strict naming - any deviation (i.e. capitalization) will result in a new package being created.

    Args:
        db (object): database object
        package_name (string): the name of the package
        version (int): The version number of the package
        description (string): A brief description of the package
        server (string): Which server does this package live on?
        file_path (string): Where did this package come from?

    Returns:
        bool: True or False based on if the package was created successfully.
    """

    date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    cur = db[current]
    version = version + 1
    try:
        cur.insert_one(
            {
                "name": package_name,
                "version": version,
                "date": date,
                "description": description,
                "server": server,
                "source_path": file_path,
                "qa_status": 1,
            }
        )
        print(f'Package "{package_name}" created successfully in database')
        # Now insert it into all_packages
        all_p = db["all_packages"]
        all_p.insert_one(
            {
                "name": package_name,
                "current_version": version,
                "packages": [
                    {
                        "version": version,
                        "date": date,
                        "description": description,
                        "server": server,
                        "source_path": file_path,
                    }
                ],
            }
        )
        return True
    except Exception as e:
        print(f"Error creating package: {e}")
        return False


def update_package(db, package_name, version, description, server, file_path):
    """# update_package
    This function will update a package in the database. It takes in the db, package_name, version, description, server, and file_path.
    It will *automatically* update the version number.
    #! Note: This requires strict naming - any deviation (i.e. capitalization) will result in a new package being created.

    #* Method Status: Passed Testing
    #* 11/28/2023
    #* Author: Alfred Simpson

    Args:
        db (object): database object
        package_name (string): the name of the package
        version (int): The version number of the package
        description (string): A brief description of the package
        server (string): Which server does this package live on?
        file_path (string): Where did this package come from?

    Returns:
        bool: True or False based on if the package was updated successfully.
    """
    date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    cur = db[current]
    version = version + 1
    try:
        cur.update_one(
            {"name": package_name},
            {
                "$set": {
                    "version": version,
                    "date": date,
                    "description": description,
                    "server": server,
                    "source_path": file_path,
                    "qa_status": 1,
                }
            },
        )
        all_p = db["all_packages"]
        all_p.update_one(
            {"name": package_name},
            {
                "$set": {
                    "current_version": version,
                }
            },
        )
        all_p.update_one(
            {"name": package_name},
            {
                "$push": {
                    "packages": {
                        "version": version,
                        "date": date,
                        "description": description,
                        "server": server,
                        "source_path": file_path,
                    }
                }
            },
        )

        print(f'Package "{package_name}" updated successfully')
        return True
    except Exception as e:
        print(f"Error updating package: {e}")
        return False


def qa_to_prod(db):
    """Similar to deploy, this function will move the package from qa to prod. It will also update the database accordingly."""
    pass


def send_to_qa(server, package_name, version):
    """This function will send the package to QA. It will also update the database accordingly."""
    destination = "/home/longsoup/inbox/"
    build = "/home/longsoup/build/"
    LOCAL_PATH = "/home/longsoup/STORE/"
    print(f"package_name: {package_name}")
    current_file = (
        package_name + "_" + str(version) + ".tar.gz"
    )  # This is the most recent version of the package.
    print(f"current_file: {current_file}")
    host_name = server + "_qa"
    try:
        with pysftp.Connection(
            host=host_name, username=qa_host_user, password=qa_host_pass
        ) as sftp:
            local_path = LOCAL_PATH + current_file
            sftp.put(localpath=local_path, remotepath=destination + current_file)
            sftp.execute("tar -xzf " + (destination + current_file) + " -C " + build)
            sftp.close()
            return True
    except Exception as e:
        print(f"Error sending package to QA: {e}")
        return False


def dev_to_deploy(cluster, server, file_path, package_name, file_name, description):
    """dev_to_deploy is a function that will take in the cluster, server, file_path, package_name, file_name, and description.
    It will then retrieve the package from the server and store it locally.
    It will then check if the package exists in the database. If it does, then it will update the package.
    If it does not, then it will create the package.
    Once the package is created/updated, it will then ship the package to QA.
    Upon successful shipping, it will return a message to our node apps.

    Args:
        cluster (string): What cluster is the server in?
        server (string): Which server is the package on?
        file_path (string): Where is the package located - provide the absolute path?
        package_name (string): What is the name of the package? No file extensions!
        file_name (string): What is the name of the file? Include the file extension!
        description (string): This is a brief description of the package. It does not matter what you write.

    Returns:
        bool: T/F if the package was successfully deployed.
    """

    host_name = server + "_" + cluster
    retrieved = retrieve_package(host_name, file_path, file_name)
    if retrieved:
        version = get_last_version(db, package_name)
        if version == 0:
            # make_package(package_name, version, date, description, server, file_path, 1)
            p_status = create_package(
                db, package_name, version, description, server, file_path
            )
            print("\nPackage created successfully in database! Shipping to QA\n")
        else:
            # make_package(package_name, version, date, description, server, file_path, 1)
            p_status = update_package(
                db, package_name, version, description, server, file_path
            )
            print("\nPackage updated successfully in database! Shipping to QA\n")
        if p_status:
            print("\nPackage created successfully in database! Shipping to QA\n")
            # Now we need to ship the package to QA
    else:
        return {
            "returnCode": 1,
            "message": f"Error retrieving package from {host_name}",
        }


# def deploy(cluster, server, file_path, file_name):
#     """This function begins the deployment steps from dev to qa."""

#     # set the host name to the server and cluster. This will help us connect to the server.
#     host_name = server + "_" + cluster
#     p_name = re.search(r"(.*)\.tar\.gz", file_name).group(
#         1
#     )  #! This is resolved in testDeploy,
#     retrieved = retrieve_package(host_name, file_path, LOCAL_PATH + file_name)
#     if retrieved:
#         # if we were able to get the file, now we need to check if the package exists in the db
#         print("Package received. Checking if package exists in db...")
#         if package_exists(file_name):
#             # If the package exists, then we need to update the previous package.
#             print("Package exists in db. Updating previous package...")
#             # We find the last version and increase by 1
#             version = get_last_version(db, p_name) + 1
#             print(f"The new version is {version}")
#             # Before we update the previous package, we need to migrate it to the backup packages.

#         else:
#             # If the package does not exist, then we need to create a new package.
#             print("Creating the initial package in the database")

#     else:
#         return {
#             "returnCode": 1,
#             "message": f"Error retrieving package from {host_name}",
#         }


def return_error(ch, method, properties, body, msg):
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(msg),
    )
    ch.basic_ack(delivery_tag=method.deliver_tag)


def request_processor(ch, method, properties, body):
    try:
        request = json.loads(body.decode("utf-8"))
        # logging.debug(f"\nReceived request: {request}\n")
    except json.JSONDecodeError:
        print("\n\tError decoding incoming JSON\n")
        # logging.error("Error decoding incoming JSON")
        response = {"ERROR": "Invalid JSON Format Received"}
        return return_error(ch, method, properties, body, response)
    print(f"\nIncoming request: {request}\n")
    if "type" not in request:
        print(f"\n The Request coming is looks like this: {request}\n")
        # logging.error(f"Error in type. Request received without type: {request}")
        response = "ERROR: No type specified by message"
    else:
        match request["type"]:
            case "test":
                response = "test"
            case "stage_1":
                response = dev_to_deploy(
                    request["cluster"],
                    request["server"],
                    request["file_path"],
                    request["file_name"],
                )
            case _:
                response = "ERROR: Invalid type specified by message"
    ch.basic_publish(
        exchange="",
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=json.dumps(response),
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


creds = pika.PlainCredentials(username=D_USER, password=D_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=D_HOST, port=5672, credentials=creds, virtual_host=vHost
    )
)

channel = connection.channel()
channel.queue_declare(queue=D_Q, durable=True)
channel.queue_bind(exchange=D_X, queue=D_Q)
print("\n [*] Waiting for a message from the webserver. To exit, press Ctrl+C\n")
channel.basic_consume(queue=D_Q, on_message_callback=request_processor)
print("\n[x] Awaiting RPC requests\n")
channel.start_consuming()
