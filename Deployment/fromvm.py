import os
import shutil
import pymongo

from datetime import datetime


def create_new_package(db):
    # Start by getting the package name, path, and description from the user. We'll also want to get the server name.
    package_name = input("Enter the package name: ")
    package_path = input("Enter the absolute package path: ")
    package_description = input("Enter the package description: ")
    package_server = input("Enter the server name: ")
    # Note, we should probably check if the package path exists. If it doesn't, we should return an error and ask them to try again.
    if not os.path.exists(package_path):
        print("Package path does not exist!")
        create_new_package(db)
    # Now we can create the package in the database.
    # Since this is a new package, the current version will be 1.0.0.
    # We'll also want to get the current date and time.
    current_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    # Now we can create the package in the database by updating the current_packages list to include the new package. As there are no previous versions of this package, we should fill in the previous_versions list with the current version.
    db.packages.update_one(
        {},
        {
            "$push": {
                "current_packages": {
                    "name": package_name,
                    "current_version": 1,
                    "information": [
                        {
                            "version": 1,
                            "server": package_server,
                            "date": current_date,
                            "path": package_path,
                            "description": package_description,
                            "rank": "primary",
                            "passed_qa": "true",
                            "previous_versions": [
                                {
                                    "version": 1,
                                    "server": package_server,
                                    "date": current_date,
                                    "path": package_path,
                                    "description": package_description,
                                    "rank": "secondary",
                                    "passed_qa": "true",
                                }
                            ],
                        }
                    ],
                }
            }
        },
    )

    # Once we've updated the database, we can tar the package and move it to the deployment directory.

    # We'll want to create a directory in /tmp/_packages_/{package_name} and copy the package to that directory.

    try:
        os.system("sudo mkdir /tmp/_packages_")

    except Exception as e:
        print(e)

    shutil.copytree(package_path, f"/tmp/_packages_/{package_name}")

    # Now we can call tar_and_move_package.

    if tar_and_move_package(db, package_name, "1.0.0"):
        # If we could tar and move the package, let's delete the copy in /tmp/_packages_.

        shutil.rmtree(f"/tmp/_packages_/{package_name}")

    return True


def tar_and_move_package(db, package_name, new_version):
    # We can now tar the package.
    SRC_DIR = "/tmp/_packages_"
    DEST_DIR = "/home/longsoup/Desktop/Deployment"
    # We'll want to tar the directory with the package name in tmp, saving the new tar file in _packages_ as the package_name + new_version, separated by a hyphen
    os.system(
        f"sudo tar -czvf {DEST_DIR}/{package_name}-{new_version}.tar.gz -C {SRC_DIR} {package_name}"
    )
    # Now we can move the tar file to the Deployment directory.
    # os.system(

    #        f"sudo mv {SRC}/{package_name}-{new_version}.tar.gz {DEST}/{package_name}-{new_version}.tar.gz"

    #    )
    shutil.rmtree(f"/tmp/_packages_/{package_name}")


def update_existing_package(db):
    """This function will update an existing package in the database. Our database is structured like we see defined in col
    Args:
        db (_type_): _description_
    """
    # We will need to first pass into current_packages, then get the name of each package.
    # We can do this by using the following code:
    db.packages.find_one({})["current_packages"]
    # This will return a list of all current packages in the database.
    # We can then iterate through each package and get the name of each package.
    # We'll also want to store all package names in a list so we can check if the package exists.
    package_names = []
    # We can do this by using the following code:
    for package in db.packages.find_one({})["current_packages"]:
        package_names.append(package["name"])
        print(package["name"])
    # Now we can check if the package exists in the database.
    # We can do this by using the following code:
    package_name = input("Enter the package name: ")
    if package_name not in package_names:
        print("Package does not exist!")
        return
    # But if the package name does exist, we should print out the package information and the current version.
    else:
        for package in db.packages.find_one({})["current_packages"]:
            if package["name"] == package_name:
                print(f"Package Name: {package['name']}")
                print(f"Current Version: {package['current_version']}")
                print(f"Current Path: {package['information'][0]['path']}")
                print(
                    f"Current Description: {package['information'][0]['description']}"
                )
                print(f"Current Host Server: {package['information'][0]['server']}")
                print(f"Current Date: {package['information'][0]['date']}")
                print(f"Current Rank: {package['information'][0]['rank']}")
                print(f"Current Passed QA: {package['information'][0]['passed_qa']}")
                option = input("Update package? (y/n): ")
                if option.lower() == "y":
                    # We can now update the package.
                    # First, we'll want to get the new version number, which is increasing the previous by 1.
                    # We can do this by using the following code:
                    new_version = package["current_version"] + 1
                    # Next, we should try to make a directory using sudo. This directory is /tmp/_packages_.
                    # We can do this by using the following code:
                    # os.system("sudo mkdir /tmp/_packages_")
                    # Now we can copy the package to the /tmp/_packages_ directory.
                    shutil.copytree(
                        package["information"][0]["path"],
                        f"/tmp/_packages_/{package_name}",
                    )
                    if tar_and_move_package(db, package_name, new_version):
                        # If we could tar and mov ethe package, let's delete the copy in /tmp/_packages_.
                        shutil.rmtree(f"/tmp/_packages_/{package_name}")
                    db.packages.update_one(
                        {"current_packages.name": package_name},
                        {
                            "$set": {
                                "current_packages.$.current_version": new_version,
                                "current_packages.$.information": [
                                    {
                                        "version": new_version,
                                        "server": package["information"][0]["server"],
                                        "date": package["information"][0]["date"],
                                        "path": package["information"][0]["path"],
                                        "description": package["information"][0][
                                            "description"
                                        ],
                                        "rank": "primary",
                                        "passed_qa": "true",
                                        "previous_versions": [
                                            {
                                                "version": package["current_version"],
                                                "server": package["information"][0][
                                                    "server"
                                                ],
                                                "date": package["information"][0][
                                                    "date"
                                                ],
                                                "path": package["information"][0][
                                                    "path"
                                                ],
                                                "description": package["information"][
                                                    0
                                                ]["description"],
                                                "rank": "secondary",
                                                "passed_qa": "true",
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                    )
                    # Now we can update the last_working_packages list.
                    # We want to make sure this doesn't duplicate existing data, but moves the existing data to the previous_versions list inside of last_working_packages.
                    # We can do this by using the following code:
                    db.packages.update_one(
                        {},
                        {
                            "$set": {
                                "last_working_packages": {
                                    "name": package_name,
                                    "version": package["current_version"],
                                    "information": [
                                        {
                                            "version": package["current_version"],
                                            "server": package["information"][0][
                                                "server"
                                            ],
                                            "date": package["information"][0]["date"],
                                            "path": package["information"][0]["path"],
                                            "description": package["information"][0][
                                                "description"
                                            ],
                                            "rank": "secondary",
                                            "passed_qa": "true",
                                            "previous_versions": [
                                                {
                                                    "version": package[
                                                        "current_version"
                                                    ],
                                                    "server": package["information"][0][
                                                        "server"
                                                    ],
                                                    "date": package["information"][0][
                                                        "date"
                                                    ],
                                                    "path": package["information"][0][
                                                        "path"
                                                    ],
                                                    "description": package[
                                                        "information"
                                                    ][0]["description"],
                                                    "rank": "tertiary",
                                                    "passed_qa": "true",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            }
                        },
                    )


def main():
    mongo_client = pymongo.MongoClient("mongodb://longsoup:njit#490@localhost:27017/")
    db = mongo_client["test_gather"]
    option = input(
        "Are you updating an existing package or creating a new package? (update/new): "
    )
    if option.lower() == "update":
        print(f"Checking for packages...")
        update_existing_package(db)
    elif option.lower() == "new":
        create_new_package(db)
    else:
        print("Invalid option!")
        return


if __name__ == "__main__":
    main()
