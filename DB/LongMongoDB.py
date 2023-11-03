# A python class called LongDB that accesses a mongo database and performs queries.
# This should also be used to extend the functionality of other, subsequent classes

import os, sys, json
import pymongo


class LongDB:
    """
    This was originally configured for mysql, I am in the process of rebuilding this for mongodb.
    """

    def __init__(self, host, user, password, database):
        """
        __init__ is the constructor for the LongDB class. It requires the following parameters:
        host: the host of the mysql database
        user: the username of the database user.
        password: the password of the mysql database
        database: the name of the database to connect to
        """
        self.myClient = pymongo.MongoClient(
            host="localhost",
            username=user,
            password=password,
            authSource=database,
            authMechanism="SCRAM-SHA-256",
        )
        self.db = self.myClient[database]

    def get_uid_by_email(self, useremail):
        """
        get_user is a function that returns a user from the database.
        It requires the following parameters:
        username: the username of the user to return
        """
        result = self.db.users.find_one({"email": useremail})

        return result["uid"]

    def get_name(self, usercookieid):
        """
        get_user is a function that returns a user from the database.
        It requires the following parameters:
        username: the username of the user to return
        """
        result = self.db.user.find_one({"usercookieid": usercookieid})
        result = result["uid"]
        name_result = self.db.userinfo.find_one({"uid": result})
        return name_result["first_name"]

    def get_spot_name(self, userid):
        """
        get_spot_name is a function that returns a spotify username from the database.

        It requires the following parameters:
        userid: the uid of the user to return. Usually found in users table as well.
        """
        result = self.db.userinfo.find_one({"uid": userid})
        return result["spot_name"]

    def set_session(self, session_id, useremail):
        """
        set_session is a function that sets a session for a user in the mongo database.
        It requires the following parameters:
        session_id: the session_id of the user to set
        useremail: the useremail of the user to set
        """
        first_result = self.db.users.find_one({"email": useremail})
        uid = first_result["uid"]
        self.db.users.update_one(
            {"uid": uid}, {"$set": {"sessionid": session_id}}, upsert=False
        )

    def set_usercookieid(self, usercookieid, useremail):
        """
        setusercookieid is a function that sets a usercookieid for a user in the database.
        It is called when a user registers or logs in - always.

        Args:
            usercookieid (_type_): _description_
            useremail (_type_): _description_
        """
        first_result = self.db.users.find_one({"email": useremail})
        uid = first_result["uid"]
        self.db.users.update_one(
            {"uid": uid}, {"$set": {"usercookieid": usercookieid}}, upsert=False
        )

    def invalidate_session(self, usercookieid, session_id):
        """#invalidate_session
        When a user logs out, find their session id and delete it.

        Args:
            usercookieid (string): a long string used to identify a user, created a login or registration.
            session_id (string): a  long string tied to a user for their session.
        """
        self.db.users.update_one(
            {"usercookieid": usercookieid}, {"$unset": {"sessionid": session_id}}
        )
        return True

    def ___NOTUPDATED__validate_session(self, usercookieid, session_id):
        """
        validate_session is a function that returns a user from the database.
        It requires the following parameters:
        session_id: the session_id of the user to return
        """

        # # TODO: check for usercookieid first, then sessionid
        # self.mycursor.execute(
        #     "SELECT sessionid FROM users WHERE usercookieid = '" + usercookieid + "'"
        # )
        # sessionResult = self.mycursor.fetchall()
        # # Check for a null value
        # if len(sessionResult) == 0:
        #     print(f"No session found for {usercookieid}")
        #     return False
        # session = sessionResult[0]

        # if session_id in session:
        #     print(f"Supplied session {session_id} matched sessionResult: {session}")
        #     myresult = True
        # else:
        #     print(
        #         f"Supplied session {session_id} did not match sessionResult: {session}"
        #     )
        #     myresult = False
        # print(f"validate_session returned: {myresult}")
        # # TODO: add this to DB Log
        # return myresult
        # TODO: move to mongo
        pass

    def get_next_uid(self):
        """#get_next_uid()
        returns the next available uid for a new user.
        This is done by finding the highest uid in the database and adding 1 to it.
        We use this to keep our uids unique and to add relational data to a non relational database.


        Returns:
            int: the next available uid
        """

        nextid = 0
        # db = myclient.testDB
        col = self.db.users
        highest_id = col.find_one(sort=[("uid", -1)])
        if highest_id:
            nextid = 1
            nextid += highest_id["uid"]
        return nextid

    def authorize_user(self, useremail, password):
        """
        authorize_user is a function that returns whether or not a user and password are correct.
        It only returns a boolean.

        Args:
            useremail (string): The user's email
            password (string): The user's password

        Returns:
            Boolean: Whether or not the user is who they say they are
        """
        # First, see if the user exists
        try:
            # See if a user exists with that email
            user = self.db.users.find_one({"email": useremail})
            # If the user exists, does the password match?
            if user and user["password"] == password:
                return True
            else:
                return False
        except:
            return False

    # User modification methods

    def addUser(self, email, password, sessionid, cookieid):
        uid = self.get_next_uid()
        col = self.db.users

        col.insert_one(
            {
                "uid": uid,
                "email": email,
                "password": password,
                "sessionid": sessionid,
                "cookieid": cookieid,
            }
        )

    # def initialUpdate(self, useremail, fname, lname, spot_name):
    #     """
    #     initialUpdate takes the first name, last name, and spotify username and adds it into userinfo after querying the userid from users.
    #     """
    #     sql = (
    #         "INSERT INTO userinfo set spotify_username = '"
    #         + spot_name
    #         + "', fname = '"
    #         + fname
    #         + "', lname = '"
    #         + lname
    #         + "', uid = (SELECT uid FROM users WHERE useremail = '"
    #         + useremail
    #         + "')"
    #     )
    #     # val = (spot_name, fname, lname)
    #     # TODO: verify that userid as a string doesn't break this
    #     self.mycursor.execute(sql)
    #     self.mydb.commit()
    #     return self.mycursor.rowcount, f"{fname} added to userinfo!"

    # def update_user_password(self, table, useremail, password):
    #     """
    #     update_user is a function that updates a user in the database.
    #     It requires the following parameters:
    #     table: the table to update the user in
    #     useremail: the username of the user to update
    #     password: the password of the user to update
    #     """
    #     sql = (
    #         "UPDATE "
    #         + table
    #         + " SET password = '"
    #         + password
    #         + "' WHERE useremail = '"
    #         + useremail
    #         + "'"
    #     )
    #     self.mycursor.execute(sql)
    #     self.mydb.commit()
    #     return self.mycursor.rowcount, f"{useremail} updated!"

    # update first name
    # def update_user_fname(self, table, useremail, fname):
    #     """
    #     update_user_fname isn't built yet - but takes useremail and a first name.
    #     I'll need to know how we list the names in the database to update them.
    #     """
    #     pass

    # update last name
    # def update_user_lname(self, table, useremail, lname):
    #     """
    #     update_user_lname isn't built yet - but takes useremail and a last name.
    #     I'll need to know how we list the names in the database to update them.
    #     """
    #     pass

    # update email address
    # def update_user_email(self, table, useremail):
    #     """
    #     update_user isn't built yet - but takes useremail and an email address.
    #     I'll need to know how we list the names in the database to update them.
    #     """
    #     pass

    # TODO: Note, this doesn't *fully* delete a user - it only deletes them from one table. We'd have to query all tables in a database to fully delete a user.
    # def delete_user(self, table, useremail):
    #     """
    #     delete_user is a function that deletes a user from the database.
    #     It requires the following parameters:
    #     table: the table to delete the user from
    #     useremail: the username of the user to delete
    #     """
    #     sql = "DELETE FROM " + table + " WHERE useremail = '" + useremail + "'"
    #     self.mycursor.execute(sql)
    #     self.mydb.commit()
    #     return self.mycursor.rowcount, f"{useremail} deleted!"

    # TODO: We should have a function that sends an email to a user, such as a password reset email.

    # These are ways to confirm if a user is in the database or not:

    # def user_exists_uname(self, username):
    #     """
    #     user_exists(username) is a function that checks if a user exists in the database.
    #     This method returns a boolean statement.
    #     It requires only the username of the user to check.
    #     """
    #     sql = "SELECT * FROM users WHERE username = '" + username + "'"
    #     self.mycursor.execute(sql)
    #     result = self.mycursor.fetchall()
    #     if len(result) == 0:
    #         return False
    #     else:
    #         return True

    # def user_exists_email(self, email):
    #     """
    #     user_exists(email) is a function that checks if a user exists in the database.
    #     This method returns a boolean statement.
    #     It requires only the email of the user to check.
    #     """
    #     sql = "SELECT * FROM users WHERE useremail = '" + email + "'"
    #     self.mycursor.execute(sql)
    #     result = self.mycursor.fetchall()
    #     if len(result) == 0:
    #         return False
    #     else:
    #         return True

    # def user_exists_id(self, id):
    #     """
    #     user_exists(id) is a function that checks if a user exists in the database.
    #     This method returns a boolean statement.
    #     It requires only the id of the user to check.
    #     """
    #     sql = "SELECT * FROM users WHERE userid = '" + id + "'"
    #     self.mycursor.execute(sql)
    #     result = self.mycursor.fetchall()
    #     if len(result) == 0:
    #         return False
    #     else:
    #         return True
