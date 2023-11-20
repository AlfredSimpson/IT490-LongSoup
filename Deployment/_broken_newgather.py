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


# import os
# import shutil
# import pymongo
# from bson.son import SON

# from datetime import datetime


# col = {
#     "packages": [
#         {
#             "name": "",
#             "current_version": 0,
#             "information": {
#                 "version": 0,
#                 "server": "",
#                 "date": "",
#                 "path": "",
#                 "description": "",
#                 "passed_qa": "",
#             },
#             "previous_versions": [
#                 {
#                     "version": 0,
#                     "server": "",
#                     "date": "",
#                     "path": "",
#                     "description": "",
#                     "passed_qa": "true",
#                 }
#             ],
#         }
#     ],
# }


# def revert_package(db):
#     pass


# def update_existing_package(db):
#     # This function is a little more complicated than the create_new_package function. We'll need to first get all of the package names from the collection's "packages" collection.
#     package_names = db["packages"].distinct("name")
#     # Then we'll want to ask the user which package they want to update.
#     package_name = input("Which package do you want to update? ")
#     # Then we'll want to check to see if the package name exists in the database.
#     if package_name not in package_names:
#         print("Package does not exist!")
#         return update_existing_package(db)
#     # Now we'll want to get the package document from the database.
#     package = db["packages"].find_one({"name": package_name})
#     # Since the package already exists, we will require that the absolute path remain the same. We'll print out the document related to the package first, and ask if they want to update this package.
#     print(f"Package: {package}")
#     update = input("Do you want to update this package? (y/n): ")
#     if update.lower() == "n":
#         return exit(0)
#     # If they want to update the package, we'll assume that everything bu the version number is the same. We'll automatically give it a new version number 1 higher than the previous version.
#     new_version = package["current_version"] + 1
#     # Now we'll want to get the current date and time.
#     current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     # Now we'll check if the /tmp/_packages_ directory exists. If it doesn't, we'll create it.
#     if not os.path.exists("/tmp/_packages_"):
#         os.mkdir("/tmp/_packages_")
#     # Next, we'll try to make a directory for the package in /tmp/_packages_/{package_name}. If it already exists, we'll remove it and create a new one.
#     if os.path.exists(f"/tmp/_packages_/{package_name}"):
#         shutil.rmtree(f"/tmp/_packages_/{package_name}")
#     os.mkdir(f"/tmp/_packages_/{package_name}")
#     # Now we'll want to copy the package to the /tmp/_packages_/{package_name} directory.
#     shutil.copytree(package["information"]["path"], f"/tmp/_packages_/{package_name}")
#     # Now we'll want to tar the package and move it to the correct directory.
#     if tar_and_move_package(db, package_name, new_version):
#         # Now we can remove the /tmp/_packages_/{package_name} directory.
#         shutil.rmtree(f"/tmp/_packages_/{package_name}")
#     # Now we'll want to update the package document in the database.
#     # First, we'll take the existing package document, excluding the previous_versions field, and append it to the previous_versions field.
#     package["previous_versions"].append(package["information"])
#     # Then we'll want to update the "information" field and the "current_version" field.
#     package["information"]["version"] = new_version
#     package["information"]["date"] = current_date
#     package["information"]["passed_qa"] = "false"
#     package["current_version"] = new_version
#     # Then we'll want to update the package document in the database.
#     db["packages"].update_one({"name": package_name}, {"$set": package}, upsert=True)
#     # upsert=True means that if the document doesn't exist, it will be created. If it does, we don't do anything. This will help us prevent duplication.

#     # package["previous_versions"].append(package["information"])
#     # # Then we'll want to update the "information" field.
#     # package["information"]["version"] = new_version
#     # package["information"]["date"] = current_date
#     # package["information"]["passed_qa"] = "false"
#     # # Then we'll want to update the "current_version" field.
#     # package["current_version"] = new_version
#     # # Then we'll want to update the package document in the database.

#     pass


# def check_package_name(db, package_name):
#     # This function will check to see if the package name exists in the database.
#     package_exists = db["packages"].find_one({"name": package_name})
#     if package_exists:
#         print("Package already exists!")
#         return True
#     return False


# def check_package_path(db, package_path):
#     # This function will check to see if the package path exists.
#     if not os.path.exists(package_path):
#         print("The package path does not exist!")
#         return False
#     return True


# def create_new_package(db):
#     # This function will create a new package document in the database, which is modeled after the col variable above.
#     # We'll need to ask the user for the package name, version, and description.
#     package_name = input("Enter the package name: ")
#     # Check to see if the package name exists in the database, repeat until unique name given.
#     if check_package_name(db, package_name):
#         return create_new_package(db)
#     package_path = input("Enter the absolute package path: ")
#     # Check to see if the package path exists, repeat until we get a valid path.
#     if not check_package_path(db, package_path):
#         return create_new_package(db)
#     package_description = input("Enter the package description: ")
#     package_server = input("Enter the server name: ")

#     # Then, we'll check to see if the package path exists. If it doesn't, we should return an error and make the user start again.
#     # if not os.path.exists(package_path):
#     #     print("The package path does not exist!")
#     #     return create_new_package(db)
#     # Now that we know we have the package name, the path, description, and server, we can create the package document.
#     # We should also get the current date and time.
#     current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # package_exists = db["packages"].find_one({"name": package_name})
#     # if package_exists:
#     #     print("Package already exists!")
#     #     exit(0)
#     # If the package doesn't exist, we can create it.
#     package = {
#         "name": package_name,
#         "current_version": 1,
#         "information": {
#             "version": 1,
#             "server": package_server,
#             "date": current_date,
#             "path": package_path,
#             "description": package_description,
#             "passed_qa": "false",
#         },
#         "previous_versions": [],
#     }
#     # Then we just want to insert this package into the collection as a new document under the "packages" collection.
#     db["packages"].insert_one(package)
#     # Now we'll want to create a directory in /tmp/_packages_/{package_name} and copy the package to that directory.
#     try:
#         os.system("sudo mkdir /tmp/_packages_")
#     except Exception as e:
#         print(e)
#     shutil.copytree(package_path, f"/tmp/_packages_/{package_name}")
#     # Now we can call tar_and_move_package.
#     tar_and_move_package(db, package_name, 1)
#     return True


# def tar_and_move_package(db, package_name, new_version):
#     # We can now tar the package.
#     SRC_DIR = "/tmp/_packages_"
#     DEST_DIR = "/home/longsoup/Desktop/Deployment"
#     # We'll want to tar the entire directory found in /tmp/_packages_/{package_name}, but not /tmp/_packages_. Only the package_name directory.
#     print("In tar_and_move_package")
#     os.system(
#         f"sudo tar -czvf {DEST_DIR}/{package_name}-{new_version}.tar.gz -C {SRC_DIR} {package_name}"
#     )
#     # Clean up the /tmp/_packages_ directory - removing the entire {package_name} directory but leaving _packages_ intact.
#     shutil.rmtree(f"/tmp/_packages_/{package_name}")
#     return True


# def main():
#     mongo_client = pymongo.MongoClient(
#         "mongodb://longsoup:fakepassword@localhost:27017/"
#     )
#     db = mongo_client["thedatabase"]

#     option = input(
#         "Are you updating an existing package or creating a new package? (update/new): "
#     )

#     if option.lower() == "update":
#         update_existing_package(db)
#     elif option.lower() == "new":
#         create_new_package(db)
#     else:
#         print("Invalid option!")
#         return


# if __name__ == "__main__":
#     main()
