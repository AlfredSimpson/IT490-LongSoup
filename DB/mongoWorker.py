import pika
import os, sys, json, random
import pymongo
import logging
from dotenv import load_dotenv

load_dotenv()

maindb = os.getenv("MONGO_DB")
maindbuser = os.getenv("MONGO_USER")
maindbpass = os.getenv("MONGO_PASS")
maindbhost = os.getenv("MONGO_HOST")

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient.maindb


def get_next_uid():
    nextid = 0
    db = myclient.testDB
    col = db.users
    highest_id = col.find_one(sort=[("uid", -1)])
    if highest_id:
        nextid = 1
        nextid += highest_id["uid"]
    return nextid


def addUser(email, password, sessionid, cookieid):
    uid = get_next_uid()
    db = myclient.testDB
    col = db.users

    col.insert_one(
        {
            "uid": uid,
            "email": email,
            "password": password,
            "sessionid": sessionid,
            "cookieid": cookieid,
        }
    )


def auth_user(useremail, password):
    given_useremail = useremail
    given_pass = password
    query = {"useremail": "test@test.com"}
    db = myclient.testDB
    col = db.users
    q = {"email": useremail, "password": password}
    result = col.find(q)
    user = col.find_one({"email": useremail})

    if user and user["password"] == password:
        print("okay then, we got in")
        return True
    else:
        print("did notwork")
        return False
