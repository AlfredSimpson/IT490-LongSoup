# This is my attempt at simplifying the process for the deployment process. Previously we used embedded documents, this time I'm going to separate them into three collections: current_packages, previous_packages, and backup_packages.
import os
import shutil
import pymongo
import pika
import paramiko

from datetime import datetime
from dotenv import load_dotenv

db_name = "test_gather"
current = "current_packages"
previous = "previous_packages"
backups = "backup_packages"

IN_SERVERS = ["front", "back", "dmz"]

"""
name is the name of the package
version is the version of the package
date is the date the package was created
description is a brief description of what the package does
server is the server that the package is being deployed to (front, back, dmz)
source_path is the path to the directory where the package is stored so we can get it
route_key is the route key that we'll use to send the package to the correct server and control where it is inserted to
qa_status is the status of the package (pass, fail, testing). Testing means it's will be sent to QA for testing. After QA is done, it will be updated to pass or fail.
"""
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


def tar_and_movepackage(db, package_name, path, new_version):
    """
    This function will tar the package and move it to the correct location.
    """
    # Source is where the path is, destination is where we're moving it to.
    SRC = "/tmp/_packages_"
    DEST = "/home/longsoup/Desktop/Deployment"

    os.system(f"sudo tar -czvf {DEST}/{package_name}.tar.gz {SRC}/{package_name}")


def revert_package(db, package_name):
    """
    This function will revert the package to the previous version.
    """
    pass


def add_backup(db, package_name):
    """
    This function will add the package to the backup collection.
    """
    pass


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
    # clear_tables(db)
    # makeFakeData(db)
    # options = input(
    #     "Choose:\n1 to fill tables with fake data,\n2 to clear the tables,\n3 to test paths,\n4 to add to db,\n5 to update the existing packages,\n6 to rollback,\n7 to exit\n"
    # )
    # match options:
    #     case "1":
    #         print("Testing data validity...")
    #         print(f"Current Packages: {db[current].find()}")
    #         print(f"Previous Packages: {db[previous].find()}")
    #         print(f"Backup Packages: {db[backups].find()}")
    #     case "2":
    #         print("Testing paths...")
    #         print(f"Test path: {verify_path('/home/longsoup/Desktop/testing')}")
    #         print(f"Test path: {verify_path('/home/longsoup/Desktop/Utilities')}")
    #         new_path = input("Enter a new path to test: ")
    #         print(f"Test path: {verify_path(new_path)}")
    #     case "3":
    #         print("Entering new data...")
    #         create_package(db)
    #     case "4":
    #         print("Updating existing data...")
    #         update_package(db)
    #     case "5":
    #         print("Reverting data...")
    #         revert_package(db)
    #     case "6":
    #         print("Exiting...")
    #         exit()
    #     case _:
    #         print("Invalid option!")
    #         exit()
    #### THIS IS REAL CODE, uncomment to start using ####
    option = input(
        "Are you updating an existing package or creating a new package? (update/new): "
    )
    if option.lower() == "update":
        print(f"Checking for packages...")
        update_package(db)
    elif option.lower() == "new":
        create_package(db)
    else:
        print("Invalid option!")
        return


if __name__ == "__main__":
    main()
