# This is designed to test deploymentWorker.py piece by piece.
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
# current = "current_packages"
# all_p = "all_packages"
# backups = "backup_packages"

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
ALL_P = "all_packages"
backups = "backup_packages"
package_schema = {
    "name": "",
    "version": 0,
    "date": "",
    "description": "",
    "server": "",
    "absolute_path": "",
    "qa_status": "",
}

# all_packages_schema = {
#     "name": "",
#     "current_version": 0,
#     "packages" = [
#         {
#             "version": 0,
#             "date": "",
#             "description": "",
#             "server": "",
#             "absolute_path": "",
#             "qa_status": "",
#         },
#     ],
# }

#########################
# Get/Put Package Funcs #
#########################


def retrieve_package(host_name, file_path, LOCAL_NAME):
    """This function retrieves the package from the server and stores it locally."""
    LOCAL_PATH = "/home/longsoup/DEPLOY/"
    try:
        with pysftp.Connection(
            host=host_name, username=host_user, password=host_pass
        ) as sftp:
            print(f"Connected to {host_name}")
            sftp.get(file_path, LOCAL_PATH, callback=None, preserve_mtime=True)
            return True
    except Exception as e:
        print(f"Error retrieving package: {e}")
        return False


def dev_to_deploy(cluster, server, file_path, package_name, file_name, description):
    """This function will move the package from dev to deployment. It will also update the database accordingly."""
    host_name = server + "_" + cluster
    # Step 2: retrieve the package
    retrieved = retrieve_package(host_name, file_path, file_name)
    if retrieved:
        print("Package retrieved successfully")
        print("move to step 3")
        # exit()
        # Step 3: Check the database for the package, create or update accordingly.
        if package_exists(db, package_name):
            print("Package exists in the database")
            print("Moving to step 4")
            # Step 4: Version Number - get the old one and increase by 1.
            # Step 5: Update the database. Simply replace the old package with the new one in current_packages and and insert into all_packages under the package name.
            date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            package = make_package(
                package_name, version, date, description, server, file_path, 1
            )
            print(f"Package: {package}")
        #     update_package(db, package)
        else:
            print("Package does not exist in the database")
            print("We'll create the package with the given information")
            # Step 4: Version Number
            version = 1
            # Step 5: Update the database - add to current and all. Do not add to backups yet.
            date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            package = make_package(
                package_name, version, date, description, server, file_path, 1
            )
            print(f"Package: {package}")
        #     create_package(db, package)
    else:
        print("Package not retrieved successfully")
        return {
            "returnCode": 0,
            "message": "Package was not found. Please check the server and file path and try again.",
        }


###########################
#  Deploy Side Functions  #
###########################


def make_package(name, version, date, description, server, source_path, qa_status):
    """This creates the package that will be stored in the databse wherever packages exist - current, previous, and backups.

    Args:
        name (_type_): The name of the package
        version (_type_): Version Number
        date (_type_): Date of the package
        description (_type_): Short Description of the package
        server (_type_): Which server does this package live on?
        source_path (_type_): Where did this package come from?
        qa_status (int): This is the status of the package. pass = 1, fail = 0
        in_prod (int): Is this package in production? 1 = yes, 0 = no

    Returns:
        _type_: _description_
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
    """This function checks if the package exists in the database."""
    cur = db["current"]
    if cur.find_one({"name": package_name}):
        return True
    else:
        return False


def create_package(db, package_name, version, description, server, file_path):
    print(f'Creating package "{package_name}"')
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
        print(f'Package "{package_name}" created successfully')
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
    print(f'Updating package "{package_name}"')
    date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    cur = db[current]
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


def await_package():
    """This function will wait for a package to be sent to the queue. It kind of acts like the main inside the main... Once it is received, it will check if the package exists in the database. If it does, it will check if the version number is the same. If it is, it will return a message to the webserver saying that the package is already in the database. If it is not, it will retrieve the package from the server and store it locally. If the package does not exist in the database, it will retrieve the package from the server and store it locally. It will then add the package to the database."""

    def get_last_version(db, package_name):
        """This function retrieves the last version number of the package from the database."""
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

    def create_package(db, package_name, version, description, server, file_path):
        """Creates a package if none exists in the database.

        Args:
            db (_type_): _description_
            package_name (_type_): _description_
            version (_type_): _description_
            description (_type_): _description_
            server (_type_): _description_
            file_path (_type_): _description_

        Returns:
            _type_: _description_
        """
        print(f'Creating package "{package_name}"')
        date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        cur = db[current]
        # Create the first version!
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
        print(f'Updating package "{package_name}"')
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

    def check_qa(server):
        """This function looks for any packages on the server that are awaiting approval (1). If there are any, it will return a list of them. If there are none, it will return a message saying so."""
        cur = db[current]
        packages = cur.find({"server": server, "qa_status": 1})
        # Create a new dictionary with the key being a number and the value being the package.
        # This will allow us to easily select a package by number.
        new_packages = {}
        for i, package in enumerate(packages):
            new_packages[i] = package["name"]
        print(f"new_packages: {new_packages}")
        # If the amount of keys in the dictionary is greater than 0, then we have packages awaiting approval.
        if len(new_packages.keys()) > 0:
            print(f'Packages found on server "{server}" awaiting approval')
            return {
                "returnCode": 0,
                "message": "Packages found on server awaiting approval",
                "packages": new_packages,
            }
        else:
            # If the package does not exist, then we need to create a new package.
            return {
                "returnCode": 1,
                "message": "No packages found on server awaiting approval",
            }

    def store_package(package_name, file_name, version):
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
        """This function retrieves the package from the server and stores it locally."""
        # file_name has .tar.gz already, so we're good now.
        LOCAL_NAME = "/home/longsoup/DEPLOY/" + file_name
        try:
            with pysftp.Connection(
                host=host_name, username=host_user, password=host_pass
            ) as sftp:
                print(f"Connected to {host_name}")
                sftp.get(file_path, LOCAL_NAME, callback=None, preserve_mtime=True)
                sftp.close()
                return True
        except Exception as e:
            print(f"Error retrieving package: {e}")
            return False

    def dev_to_deploy(cluster, server, file_path, package_name, file_name, description):
        """This function will move the package from dev to deployment. It will also update the database accordingly."""
        host_name = server + "_" + cluster
        print(f"host_name: {host_name}")
        print(f"file_path: {file_path}")
        print(f"file_name: {file_name}")
        # Step 2: retrieve the package
        retrieved = retrieve_package(host_name, file_path, file_name)
        if retrieved:
            print("Package retrieved successfully")
            # Step 3: Check the database for the package, create or update accordingly.
            version = get_last_version(db, package_name)
            print(f"Version Check shows current version is : {version}")
            if version >= 1:
                # update package
                p_status = update_package(
                    db, package_name, version, description, server, file_path
                )
            else:
                # create package
                p_status = create_package(
                    db, package_name, version, description, server, file_path
                )
            if p_status:
                store_package(package_name, file_name, version)
                print(
                    "Package was successfully added to the database or updated, and updated the file to the store."
                )
                # Now we need to send the package to QA
                print(
                    f'Sending package "{package_name}" to QA as version {version} to {server}_qa'
                )
                delivery = send_to_qa(server, package_name, version)
                if delivery:
                    print("Package was successfully sent to QA")
                    return {
                        "returnCode": 1,
                        "message": "Package was successfully sent to QA",
                    }
                else:
                    print("Package was not sent to QA")
                    return {
                        "returnCode": 0,
                        "message": "Package was not sent to QA",
                    }
        else:
            print("Package not retrieved successfully")
            return {
                "returnCode": 0,
                "message": "Package was not found. Please check the server and file path and try again.",
            }

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
                sftp.execute(
                    "tar -xzf " + (destination + current_file) + " -C " + build
                )
                sftp.close()
                return True
        except Exception as e:
            print(f"Error sending package to QA: {e}")
            return False

    def send_to_prod(server, package_name, version):
        """This function will send the package to production. It will also update the database accordingly."""
        destination = "/home/longsoup/active/"
        host_name = server + "_prod"
        host_inbox = "/home/longsoup/inbox/"
        host_build = "/home/longsoup/build/"
        localfile = package_name + "_" + str(version) + ".tar.gz"
        localpath = "/home/longsoup/STORE/" + localfile
        print(
            f'Package "{package_name}" is being sent to production server at {host_name}'
        )
        try:
            with pysftp.Connection(
                host=host_name, username=prod_host_user, password=prod_host_pass
            ) as sftp:
                sftp.put(
                    localpath=localpath,
                    remotepath=host_inbox + localfile,
                    preserve_mtime=True,
                )
                sftp.execute(
                    "tar -xzf " + (host_inbox + localfile) + " -C " + host_build
                )
                sftp.close()
                print(
                    f'Package "{package_name}" successfully sent to production. Unzipped and is ready to go.'
                )
                return True
        except Exception as e:
            print(f"Error sending package to production: {e}")
            return False

    def fail_package_in_qa(db, package_name):
        """This function will update the database with the results of the QA testing when they fail."""
        cur = db[current]
        all_p = db["all_packages"]
        # we don't update backups since it failed and was never added to backups.
        # Update current_packages
        try:
            cur.update_one(
                {"name": package_name},
                {
                    "$set": {
                        "qa_status": -1,
                    }
                },
            )
            print(
                f'Package "{package_name}" updated qa_status successfully --- marked as failed'
            )
        except Exception as e:
            print(f"Error updating package in current_packages: {e}")
            return False
        try:
            # Get the version number
            v_num = cur.find_one({"name": package_name})["version"]
            # Update all_packages
            all_p.update_one(
                {"name": package_name, "version": v_num},
                {
                    "$set": {
                        "qa_status": -1,
                    }
                },
            )
            print(
                f'Updated all_packages with version {v_num} successfully for package "{package_name}"'
            )
            return True
        except Exception as e:
            print(f"Error updating package in all_packages: {e}")
            return False

    def pass_package_in_qa(db, package_name):
        """This function will update the database with the results of the QA testing when they pass."""
        cur = db[current]
        all_p = db["all_packages"]
        backups = db["backup_packages"]
        # Update current_packages
        try:
            cur.update_one(
                {"name": package_name},
                {
                    "$set": {
                        "qa_status": 0,
                    }
                },
            )
            print(f'Package "{package_name}" updated qa_status successfully')
        except Exception as e:
            print(f"Error updating package in current_packages: {e}")
            return False
        try:
            # Get the version number
            v_num = cur.find_one({"name": package_name})["version"]
            # Update all_packages
            all_p.update_one(
                {"name": package_name, "version": v_num},
                {
                    "$set": {
                        "qa_status": 0,
                    }
                },
            )
            print(
                f'Updated all_packages with version {v_num} successfully for package "{package_name}"'
            )
        except Exception as e:
            print(f"Error updating package in all_packages: {e}")
            return False
        # Add to backups
        try:
            exists = backups.find_one({"name": package_name})
            if exists:
                print(f'Package "{package_name}" already exists in backups')
                backups.update_one(
                    {"name": package_name},
                    {
                        "$set": {
                            "version": v_num,
                            "date": cur.find_one({"name": package_name})["date"],
                            "description": cur.find_one({"name": package_name})[
                                "description"
                            ],
                            "server": cur.find_one({"name": package_name})["server"],
                            "stored_path": "/home/longsoup/STORE/"
                            + package_name
                            + "_"
                            + str(v_num)
                            + ".tar.gz",
                            "qa_status": 0,
                        }
                    },
                )
                print(f'Package "{package_name}" updated in backups successfully')
                return True
            else:
                print(f'Package "{package_name}" does not exist in backups')
                backups.insert_one(
                    {
                        "name": package_name,
                        "version": v_num,
                        "date": cur.find_one({"name": package_name})["date"],
                        "description": cur.find_one({"name": package_name})[
                            "description"
                        ],
                        "server": cur.find_one({"name": package_name})["server"],
                        "stored_path": "/home/longsoup/STORE/"
                        + package_name
                        + "_"
                        + str(v_num)
                        + ".tar.gz",
                        "qa_status": 0,
                    }
                )
            print(f'Package "{package_name}" added to backups successfully')
            return True
        except Exception as e:
            print(f"Error adding package to backups: {e}")
            return False

    def qa_results(cluster, server, package_name, status):
        """This function will update the database with the results of the QA testing."""
        if status == 0:
            updated = pass_package_in_qa(db, package_name)
            print("Able to now move it to production...")
            if updated:
                print(
                    "Package passed QA. Database updated to remove QA status, added to backups."
                )
                version = get_last_version(db, package_name)
                in_prod = send_to_prod(server, package_name, version)
                if in_prod:
                    print(f'Package "{package_name}" successfully sent to production')
                    return {
                        "returnCode": 1,
                        "message": "Package passed QA. Database updated to remove QA status, added to backups.",
                    }
                else:
                    print(f'Package "{package_name}" was not sent to production')
                    return {
                        "returnCode": 0,
                        "message": "Package could not reach production. Please check the server and try again.",
                    }
            # qa_to_prod(db)
        elif status == -1:
            print('Package failed QA. Updating database with status of "failed"')
            fail_package_in_qa(db, package_name)
            # After failing, we just don't do anything. We just wait for the next package to come in.
            return {
                "returnCode": 0,
                "message": "Package failed QA. Updating database with status of failed",
            }
        else:
            print("Invalid status code received")
            return {
                "returnCode": 1,
                "message": "Invalid status code received",
            }

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
                case "check_qa":
                    response = check_qa(request["server"])
                case "stage_1":
                    response = dev_to_deploy(
                        request["cluster"],
                        request["server"],
                        request["file_path"],
                        request["package_name"],
                        request["file_name"],
                        request["description"],
                    )
                case "stage_2":
                    response = qa_results(
                        request["cluster"],
                        request["server"],
                        request["package"],
                        request["status"],
                    )
                case "revert":
                    pass
                    # response = revert_package(request["package"])
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


def main():
    while True:
        await_package()


if __name__ == "__main__":
    main()
