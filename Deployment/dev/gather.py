# This is my attempt at simplifying the process for the deployment process. Previously we used embedded documents, this time I'm going to separate them into three collections: current_packages, previous_packages, and backup_packages.
import os
import shutil
import pymongo
import pika
import paramiko
import json
import time
import sys
import re
import subprocess
import logging
import threading


from datetime import datetime
from dotenv import load_dotenv

db_name = "test_gather"
current = "current_packages"
previous = "previous_packages"
backups = "backup_packages"

IN_SERVERS = ["front", "back", "dmz"]

DEV_DB = "192.168.68.64"
DEV_FRONT = "192.168.68.64"
DEV_DMZ = "broidk"
DEPLOY_SERVER = "192.168.68.73"

"""
name is the name of the package
version is the version of the package
date is the date the package was created
description is a brief description of what the package does
server is the server that the package is being deployed to (front, back, dmz)
source_path is the path to the directory where the package is stored so we can get it
route_key is the route key that we'll use to send the package to the correct server and control where it is inserted to
qa_status is the status of the package (pass, fail, testing). Testing means it's will be sent to QA for testing. After QA is done, it will be updated to pass or fail.

current_packages is the core collection. This is where we store our current packages in use.

current_packages = {
    "name": "",
    "version": 0,
    "date": "",
    "description": "",
    "server": "",
    "source_path": "",
    "route_key": "",
    "qa_status": "",
}

previous_packages is where we store the previous versions of the packages. This is an array of documents, where each document is a previous version of the package - including the pass/fail status messages later incorporated.

previous_packages = [
    {
        "name": "",
        "version": 0,
        "date": "",
        "description": "",
        "server": "",
        "source_path": "",
        "route_key": "",
        "qa_status": "",
    }
]

Finally, backup packages (not yet live) will be where we store the package information related to the most recent 2 successful packages. This is so that we can revert to a previous version if necessary. The difference here is that source_path will actually refer to the path where the package is stored on the server, not the local path - as we'll need to retain backups. We also state primary and secondary packages, as we'll need to know which one to revert to. Primary is the most recent successful package, and secondary will be if, for some reason, this primary fails. As of 11/19/2023 this is not incorporated completely. 

backup_packages = {
    "name": "",
    "primary": {
        "name": "",
        "version": 0,
        "date": "",
        "description": "",
        "server": "",
        "source_path": "",
        "route_key": "",
        "qa_status": "",
    },
    "secondary": {
        "name": "",
        "version": 0,
        "date": "",
        "description": "",
        "server": "",
        "source_path": "",
        "route_key": "",
        "qa_status": "",
    },
}
"""


def hunter(pathway, package_name, srcServer, destServer):
    # Using paramiko, connect to srcServer and check to see if the package exists. If it does, scp it back home to a specific directory.
    # We'll leave the file on the source server for now.
    # We'll start by creating a connection to the source server.
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(srcServer, username="alfred", password="njit#IT#490")
    # Now we'll check to see if the package exists on the source server.
    stdin, stdout, stderr = ssh.exec_command(f"ls {pathway}")
    # We'll read the output of the command and split it into a list.
    output = stdout.read().decode("utf-8").split()
    # Now we'll check to see if the package exists in the output.
    print(f"Checking for {package_name} in {output}")
    if package_name in output:
        print(f"Found {package_name} in {output}")
        # If it does, we'll scp it to the destination server.
        # We'll start by creating a connection to the destination server.
        ssh2 = paramiko.SSHClient()
        ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh2.connect(destServer, username="longsoup", password="njit#490")
        # We'll need to tar the package before we can scp it.
        # We'll start by tarring the package.
        stdin, stdout, stderr = ssh.exec_command(
            f"tar -czvf {package_name}.tar.gz {pathway}/{package_name}"
        )
        # Now we'll need to scp the package to the destination server.
        stdin, stdout, stderr = ssh2.exec_command(
            f"scp {srcServer}:{pathway}/{package_name}.tar.gz /home/longsoup/Desktop/Deployment"
        )

        # Now we'll scp the package to the destination server.
        stdin, stdout, stderr = ssh2.exec_command(
            f"scp {srcServer}:{pathway}/{package_name} /home/longsoup/Desktop/Deployment"
        )
        # We'll read the output of the command and split it into a list.
        output = stdout.read().decode("utf-8").split()
        # Now we'll check to see if the package exists in the output.
        if package_name in output:
            # If it does, we'll return True.
            return True
        else:
            # If it doesn't, we'll return False.
            return False


def make_package(name, version, date, description, server, source, route, qastatus):
    """This is used to make a tidy little package object that we can use to insert wherever packages exist in our database  here, which is everywhere.
    Args:
        name (_type_): _description_
        version (_type_): _description_
        date (_type_): _description_
        description (_type_): _description_
        server (_type_): _description_
        source (_type_): _description_
        route (_type_): _description_
        qastatus (_type_): _description_
    """
    package = {
        "name": name,
        "version": version,
        "date": date,
        "description": description,
        "server": server,
        "source_path": source,
        "route_key": route,
        "qa_status": qastatus,
    }
    return package


def tar_and_move_package(db, package_name, version_num):
    """
    This function will tar the package and move it to the correct location.
    """
    # Source is where the path is, destination is where we're moving it to.
    SRC = "/tmp/_packages_"
    DEST = "/home/longsoup/Desktop/Deployment"
    package_name = package_name + "_" + version_num

    os.system(f"sudo tar -czvf {DEST}/{package_name}.tar.gz -C {SRC} {package_name}")
    # Now that we moved the file, we can remove it from tmp. This isn't necessary since tmp does delete files, but I'm doing it anyway.
    shutil.rmtree(os.path.join(SRC, package_name))


def move_it(package_name, source_path):
    """Moves an entire directory using the copytree function from shutil. This is used to move the package to the correct location in /tmp/_packages_ so that we can tar it and move it to the correct location.

    Args:
        package_name (str): name of the package
        source_path (str): Where is the package?

    Returns:
        bool: did you do it or not?
    """
    # SRC here is where the package directory is.
    SRC = source_path
    DEST = "/tmp/_packages_"
    try:
        # Check if the SRC directory still exists
        if os.path.exists(SRC):
            # Check if the DEST directory exists, make it if not.
            if not os.path.exists(DEST):
                os.mkdir(DEST)
            # shutil.copytree will move the directory to the destination.
            shutil.copytree(SRC, os.path.join(DEST, package_name))
            return True
        else:
            return False
    except Exception as e:
        print(f"The source file doesn't exist. {e}")
        return False


def revert_package(db, package_name):
    """
    This function will revert the package to the previous version.
    """
    # First, we need to check our database to see the current version of the package.
    cur = db[current]
    prev = db[previous]
    backups = db[backups]
    # We'll start by checking to see if the package exists in the current_packages collection.

    #! This is untested, but it ***SHOULD*** work.
    if package_exists(db, package_name):
        # If it does, we'll get the current version number and the date.
        current_version = cur.find_one({"name": package_name})["version"]
        current_date = cur.find_one({"name": package_name})["date"]
        # Now we'll get the previous version number and date.
        previous_version = prev.find_one({"name": package_name})["packages"][-1][
            "version"
        ]
        previous_date = prev.find_one({"name": package_name})["packages"][-1]["date"]
        # Now we'll get the backup version number and date.
        backup_version = backups.find_one({"name": package_name})["primary"]["version"]
        backup_date = backups.find_one({"name": package_name})["primary"]["date"]
        # Now we'll check to see if the current version is the same as the backup version. If it is, then we'll revert to the previous version. If it isn't, then we'll revert to the backup version.
        if current_version == backup_version:
            # If they're the same, we'll revert to the previous version.
            # We'll start by getting the package information from the previous_packages collection.
            package = prev.find_one({"name": package_name})["packages"][-1]
            # Now we'll update the current_packages collection with the information from the previous_packages collection.
            cur.update_one(
                {"name": package_name},
                {
                    "$set": {
                        "version": previous_version,
                        "date": previous_date,
                        "description": package["description"],
                        "server": package["server"],
                        "source_path": package["source_path"],
                        "route_key": package["route_key"],
                        "qa_status": package["qa_status"],
                    }
                },
            )
            # Now we'll update the previous_packages collection by removing the last package in the array.
            prev.update_one({"name": package_name}, {"$pop": {"packages": 1}})
            # Now we'll update the backup_packages collection by updating the primary package with the information from the current_packages collection.
            backups.update_one(
                {"name": package_name},
                {
                    "$set": {
                        "primary": {
                            "name": package_name,
                            "version": current_version,
                            "date": current_date,
                            "description": package["description"],
                            "server": package["server"],
                            "source_path": package["source"],
                            "route_key": package["route_key"],
                            "qa_status": package["qa_status"],
                        }
                    }
                },
            )
            # Now we'll update the backup_packages collection by updating the secondary package with the information from the previous_packages collection.
            backups.update_one(
                {"name": package_name},
                {
                    "$set": {
                        "secondary": {
                            "name": package_name,
                            "version": previous_version,
                            "date": previous_date,
                            "description": package["description"],
                            "server": package["server"],
                            "source_path": package["source"],
                            "route_key": package["route_key"],
                            "qa_status": package["qa_status"],
                        }
                    }
                },
            )
            #! This is untested!!


def add_backup(db, package_name):
    """
    This function will add the package to the backup collection.
    """
    pass


def update_package(db):
    cur = db[current]
    package_names = {}
    count = 0
    for package in cur.find():
        package_names[count] = package["name"]
        count += 1
    print(f'\n{"-"*10} Package Names {"-"*10}')
    for key, value in package_names.items():
        print(f"{key} : {value}\n")
    p_name = ""
    while p_name not in package_names.values():
        try:
            p_name = package_names[int(input("Select a package to update by digit:\n"))]
        except Exception as e:
            print(f"uhhh... {e}? Not seeing that here... Try again.\n")
            p_name = ""
    for key, value in db[current].find_one({"name": p_name}).items():
        print(f"{key}: \t{value}")
    confirm = input("\nUpdate this package? (y/n)\n")
    if confirm.lower() == "n":
        print("Okay, starting over.")
        update_package(db)
    # If we get here, then we're going to update the package. We'll start by getting the values we need to update along the way. new information will be prefixed by new_, and the old information will be prefixed by old_.
    # start with the old information. Most of this should stay the same, but we'll need to update the version number and the date.

    old_version = db[current].find_one({"name": p_name})["version"]
    old_date = db[current].find_one({"name": p_name})["date"]
    old_description = db[current].find_one({"name": p_name})["description"]
    old_server = db[current].find_one({"name": p_name})["server"]
    old_source_path = db[current].find_one({"name": p_name})["source_path"]
    old_route_key = db[current].find_one({"name": p_name})["route_key"]
    old_qa_status = db[current].find_one({"name": p_name})["qa_status"]
    old_package = make_package(
        p_name,
        old_version,
        old_date,
        old_description,
        old_server,
        old_source_path,
        old_route_key,
        old_qa_status,
    )
    # Now we just generate the new info - the date and the new version number.
    new_version = old_version + 1
    new_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    # Now we'll update our collections. The "current_packages" collection will be updated with the new information and the "previous_packages" collection will be updated with the old information. The "backup_packages" collection will be updated AFTER the package makes it through QA. So, not here.
    # We'll start with the current_packages collection.
    cur.update_one(
        {"name": p_name},
        {
            "$set": {
                "version": new_version,
                "date": new_date,
                "description": old_description,
                "server": old_server,
                "source_path": old_source_path,
                "route_key": old_route_key,
                "qa_status": "Testing",
            }
        },
    )
    # Next we'll update previous_packages by inserting the older information as a new document associated with the name of the package. We want all packages of the same name to be grouped together, which is why previous_packages is an array of documents.
    prev = db[previous]
    prev.update_one({"name": p_name}, {"$push": {"packages": old_package}})
    # We aren't updating backup_packages here because we need to wait for QA to finish testing the package.
    return True


def create_package(db):
    """#create_package
    This function will create a new package in our database.
    It has moderate error handling, but it's not perfect.

    Args:
        db (obj): the database object we're using to connect to the database.

    Returns:
        boolean: True or False for creating a package.
    """
    try:
        need_valid = True
        while need_valid:
            package_name = input("Provide a name for the package: ")
            need_valid = package_exists(db, package_name)
            if need_valid:
                print(
                    "\nNeed a valid name there, Chief. You're trying to make a package that already exists.\n"
                )
        print(f"Okay, the package_name is : {package_name}")
        invalid_path = True
        while invalid_path:
            package_path = input(
                "Enter the path to the directory where the package is stored: "
            )
            invalid_path = not verify_path(package_path)
            if invalid_path:
                print(
                    "Check to make sure you're giving the right path to the directory. This doesn't seem to match anything."
                )
        current_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        description = input("Enter a brief description of what this does:\n")
        server = 0
        while server not in [1, 2, 3, 4]:
            try:
                server = int(
                    input(
                        "\nChoose a server to send this to:\n1 for Front,\n2 for back,\n3 for dmz\n"
                    )
                )
                print(f"Server is {server}")
            except Exception as e:
                print(f"whoops... {e}")
                server = 0
        match server:
            case 1:
                server = ("Front",)
            case 2:
                server = ("Back",)
            case 3:
                server = ("DMZ",)
            case 4:
                server = ("Deployment",)
            case _:
                print("You goofed. Start over and suffer")
                create_package(db)
        package = {
            "name": package_name,
            "version": 1,
            "date": current_date,
            "description": description,
            "server": server,
            "qa_status": "Testing",
        }
    except Exception as e:
        print(f"whoops... {e}")
        return False
    return True


def verify_path(pathway):
    """
    This function will verify that the path exists and is valid.
    """
    if os.path.exists(pathway):
        return True
    else:
        return False


def package_exists(db, package_name):
    """
    This function will check to see if the package exists in the database within the current_packages collection.
    """
    cur = db[current]
    if cur.find_one({"name": package_name}):
        return True
    else:
        return False


def determine_route_key(server):
    """We'll ask the user for information to determine where it goes. The route key will first depend on the server it's going to, then individual factors.
    Right now this is a placeholder - but we could use this to determine a more nuanced position of objects being packaged to deliver them. So, for example, Front has 3 main directories with different purposes, and with other subdirectories. Determine_route_key, and the route key in general, could be used to determine where to insert this.

    THIS IS NOT REQUIRED (YET) FOR THE PROJECT. THIS IS A PLACEHOLDER FOR FUTURE USE.
    #! JUST A FRIENDLY NOTE TO SELF lol
    """
    if server == "front":
        print("Front server selected. Additional information needed.")
        return
    elif server == "back":
        route_key = "back"
    elif server == "dmz":
        route_key = "dmz"
    else:
        route_key = "front"
    return route_key


############################################
##       This was used for testing        ##
############################################


def clear_tables(db):
    db[current].drop()
    db[backups].drop()
    db[previous].drop()
    print("All tables dropped, refilling with test data...")


def makeFakeData(db):
    current_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    ipsum = {
        "name": "test",
        "version": 1,
        "date": current_date,
        "description": "This is a test package.",
        "server": "front",
        "absolute_path": "/home/longsoup/Desktop/testing",
        "qa_status": "pass",
    }
    lorum = {
        "name": "testing2",
        "version": 1,
        "date": current_date,
        "description": "This is a test package.",
        "server": "front",
        "absolute_path": "/home/longsoup/Desktop/Utilities",
        "qa_status": "pass",
    }
    if not package_exists(db, "test"):
        db[current].insert_one(ipsum)
        # First, create add the name of the package to the previous_packages collection.
        # Then, we'll add the package to the current_packages collection associated with that name in an array associated as "packages"
        db[previous].insert_one({"name": "test", "packages": []})
        db[previous].update_one({"name": "test"}, {"$push": {"packages": ipsum}})
        db[backups].insert_one(ipsum)
    else:
        print("Test Package already existed in db")
    if not package_exists(db, "testing2"):
        db[current].insert_one(lorum)
        db[previous].insert_one({"name": "test", "packages": []})
        db[previous].update_one({"name": "test"}, {"$push": {"packages": ipsum}})
        db[backups].insert_one(lorum)
    else:
        print("Testing2 package already existed in db")


def main():
    mongo_client = pymongo.MongoClient("mongodb://longsoup:njit#490@localhost:27017/")
    db = mongo_client[db_name]
    #### This is testing data. ####
    clear_tables(db)
    makeFakeData(db)
    # options = int(
    #     input(
    #         "Choose:\n1 to fill tables with fake data,\n2 to clear the tables,\n3 to test paths,\n4 to add to db,\n5 to update the existing packages,\n6 to rollback,\n7 to exit\n"
    #     )
    # )
    # match options:
    #     case 1:
    #         print("Testing data validity...")
    #         print(f"Current Packages: {db[current].find()}")
    #         print(f"Previous Packages: {db[previous].find()}")
    #         print(f"Backup Packages: {db[backups].find()}")
    #     case 2:
    #         print("Testing paths...")
    #         print(f"Test path: {verify_path('/home/longsoup/Desktop/testing')}")
    #         print(f"Test path: {verify_path('/home/longsoup/Desktop/Utilities')}")
    #         new_path = input("Enter a new path to test: ")
    #         print(f"Test path: {verify_path(new_path)}")
    #     case 3:
    #         print("Entering new data...")
    #         create_package(db)
    #     case 4:
    #         print("Updating existing data...")
    #         update_package(db)
    #     case 5:
    #         print("Reverting data...")
    #         revert_package(db)
    #     case 6:
    #         print("Exiting...")
    #         exit()
    #     case _:
    #         print("Invalid option!")
    #         exit()
    #### THIS IS REAL CODE, uncomment to start using ####
    # option = input(
    #     "Are you updating an existing package or creating a new package? (update/new): "
    # )
    # if option.lower() == "update":
    #     print(f"Checking for packages...")
    #     update_package(db)
    # elif option.lower() == "new":
    #     create_package(db)
    # else:
    #     print("Invalid option!")
    #     return


if __name__ == "__main__":
    main()
