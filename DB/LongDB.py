# A python class called LongDB that accesses a mysql database and performs queries. We should eventually simplify this and make it more secure.
# This should also be used to extend the functionality of other, subsequent classes

import mysql.connector as mysql
import os, sys, json


class LongDB:
    """
    This is a class used to access a mysql database and perform queries.
    """

    def __init__(self, host, user, password, database):
        """
        __init__ is the constructor for the LongDB class. It requires the following parameters:
        host: the host of the mysql database
        user: the username of the mysql database user.
        password: the password of the mysql database
        database: the name of the database to connect to
        """
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=42069,
        )
        self.mycursor = self.mydb.cursor()

    def get_user_by_username(self, useremail):
        """
        get_user is a function that returns a user from the database.
        It requires the following parameters:
        username: the username of the user to return
        """
        self.mycursor.execute(
            "SELECT * FROM users WHERE useremail = '" + useremail + "'"
        )
        myresult = self.mycursor.fetchall()
        return myresult

    def get_name(self, usercookieid):
        """
        get_user is a function that returns a user from the database.
        It requires the following parameters:
        username: the username of the user to return
        """
        self.mycursor.execute(
            "SELECT useremail FROM users WHERE usercookieid = '" + usercookieid + "'"
        )
        myresult = self.mycursor.fetchall()
        return myresult

    def get_user_by_id(self, id):
        """
        get_user_by_id is a function that returns a user from the database.
        It requires the following parameters:
        id: the id of the user to return
        It returns a string of the user's information, if it exists

        """
        self.mycursor.execute("SELECT * FROM users WHERE id = '" + id + "'")
        myresult = self.mycursor.fetchall()
        return myresult

    def set_session(self, session_id, useremail):
        """
        set_session is a function that sets a session for a user in the database.
        It requires the following parameters:
        session_id: the session_id of the user to set
        useremail: the useremail of the user to set
        """
        sql = (
            "UPDATE users SET sessionid = '"
            + session_id
            + "' WHERE useremail = '"
            + useremail
            + "'"
        )
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{useremail} updated!"

    def set_usercookieid(self, usercookieid, useremail):
        """
        setusercookieid is a function that sets a usercookieid for a user in the database.
        It is called when a user registers or logs in - always.

        Args:
            usercookieid (_type_): _description_
            useremail (_type_): _description_
        """
        sql = (
            "UPDATE users SET usercookieid = '"
            + usercookieid
            + "' WHERE useremail = '"
            + useremail
            + "'"
        )
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{useremail} updated!"

    def getsession(self, usercookieid):
        pass

    def invalidate_session(self, usercookieid, session_id):
        """When a user logs out, find their session id and delete it.

        Args:
            usercookieid (_type_): _description_
            session_id (_type_): _description_
        """
        sql = (
            "UPDATE users SET sessionid = NULL WHERE usercookieid = '"
            + usercookieid
            + "'"
        )
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{usercookieid}'s session invalidated!"

    def validate_session(self, usercookieid, session_id):
        """
        validate_session is a function that returns a user from the database.
        It requires the following parameters:
        session_id: the session_id of the user to return
        """

        # TODO: check for usercookieid first, then sessionid
        self.mycursor.execute(
            "SELECT sessionid FROM users WHERE usercookieid = '" + usercookieid + "'"
        )
        sessionResult = self.mycursor.fetchall()
        # Check for a null value
        if len(sessionResult) == 0:
            print(f"No session found for {usercookieid}")
            return False
        session = sessionResult[0]

        if session_id in session:
            print(f"Supplied session {session_id} matched sessionResult: {session}")
            myresult = True
        else:
            print(
                f"Supplied session {session_id} did not match sessionResult: {session}"
            )
            myresult = False
        print(f"validate_session returned: {myresult}")
        # TODO: add this to DB Log
        return myresult

    def auth_user(self, table, useremail, password, session_id, usercookieid):
        """
        auth_user(table, useremail,password) is a function that returns a user from the database.
        It requires the following parameters:
        useremail: the useremail of the user to return
        password: the password of the user to return
        session_id: the session_id of the user to return
        usercookieid: the usercookieid of the user to return
        """
        self.mycursor.execute(
            "Select useremail from " + table + " where useremail = '" + useremail + "'"
        )
        emailResult = self.mycursor.fetchall()
        # This is to check for null values
        if len(emailResult) == 0:
            print(f"No email found for {useremail}")
            return False
        email = emailResult[0]
        print(f"Passed by email")
        self.mycursor.execute(
            "Select password from " + table + " where useremail ='" + useremail + "';"
        )
        passResult = self.mycursor.fetchall()
        pwd = passResult[0]
        emailMatch = False
        passMatch = False
        if useremail in email:
            emailMatch = True
            if password in pwd:
                print(f"Supplied password {password} matched passResult: {pwd}")
                passMatch = True
        else:
            emailMatch = False
            return False

        if passMatch:
            # If the password matches, we need to set the session ID
            self.set_session(session_id, useremail)
            self.set_usercookieid(usercookieid, useremail)
            # return True
        # Assuming success, we now need to verify the session ID and return a bool if it matches

        return emailMatch and passMatch

    # User modification methods

    def add_user(
        self,
        table,
        useremail,
        password,
        sessionid,
        usercookieid,
    ):
        """
        add_user is a function that adds a user to the database.
        It requires the following parameters:
        table: the table to add the user to
        useremail: the username of the user to add
        password: the password of the user to add
        sessionid: the sessionid of the user to add
        usercoookieid: the usercookieid of the user to add
        """
        sql = (
            "INSERT INTO "
            + table
            + " (useremail, password, sessionid, usercookieid) VALUES (%s, %s, %s, %s)"
        )
        val = (useremail, password, sessionid, usercookieid)
        self.mycursor.execute(sql, val)
        self.mydb.commit()

        return self.mycursor.rowcount, f"{useremail} added!"

    def initialUpdate(self, useremail, fname, lname, spot_name):
        """
        initialUpdate takes the first name, last name, and spotify username and adds it into userinfo after querying the userid from users.
        """
        sql = (
            "INSERT INTO userinfo set spotify_username = '"
            + spot_name
            + "', fname = '"
            + fname
            + "', lname = '"
            + lname
            + "', uid = (SELECT uid FROM users WHERE useremail = '"
            + useremail
            + "')"
        )
        # val = (spot_name, fname, lname)
        # TODO: verify that userid as a string doesn't break this
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{fname} added to userinfo!"

    def update_user_password(self, table, useremail, password):
        """
        update_user is a function that updates a user in the database.
        It requires the following parameters:
        table: the table to update the user in
        useremail: the username of the user to update
        password: the password of the user to update
        """
        sql = (
            "UPDATE "
            + table
            + " SET password = '"
            + password
            + "' WHERE useremail = '"
            + useremail
            + "'"
        )
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{useremail} updated!"

    # update first name
    def update_user_fname(self, table, useremail, fname):
        """
        update_user_fname isn't built yet - but takes useremail and a first name.
        I'll need to know how we list the names in the database to update them.
        """
        pass

    # update last name
    def update_user_lname(self, table, useremail, lname):
        """
        update_user_lname isn't built yet - but takes useremail and a last name.
        I'll need to know how we list the names in the database to update them.
        """
        pass

    # update email address
    def update_user_email(self, table, useremail):
        """
        update_user isn't built yet - but takes useremail and an email address.
        I'll need to know how we list the names in the database to update them.
        """
        pass

    # TODO: Note, this doesn't *fully* delete a user - it only deletes them from one table. We'd have to query all tables in a database to fully delete a user.
    def delete_user(self, table, useremail):
        """
        delete_user is a function that deletes a user from the database.
        It requires the following parameters:
        table: the table to delete the user from
        useremail: the username of the user to delete
        """
        sql = "DELETE FROM " + table + " WHERE useremail = '" + useremail + "'"
        self.mycursor.execute(sql)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{useremail} deleted!"

    # TODO: We should have a function that sends an email to a user, such as a password reset email.

    # These are ways to confirm if a user is in the database or not:

    def user_exists_uname(self, username):
        """
        user_exists(username) is a function that checks if a user exists in the database.
        This method returns a boolean statement.
        It requires only the username of the user to check.
        """
        sql = "SELECT * FROM users WHERE username = '" + username + "'"
        self.mycursor.execute(sql)
        result = self.mycursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def user_exists_email(self, email):
        """
        user_exists(email) is a function that checks if a user exists in the database.
        This method returns a boolean statement.
        It requires only the email of the user to check.
        """
        sql = "SELECT * FROM users WHERE useremail = '" + email + "'"
        self.mycursor.execute(sql)
        result = self.mycursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True

    def user_exists_id(self, id):
        """
        user_exists(id) is a function that checks if a user exists in the database.
        This method returns a boolean statement.
        It requires only the id of the user to check.
        """
        sql = "SELECT * FROM users WHERE userid = '" + id + "'"
        self.mycursor.execute(sql)
        result = self.mycursor.fetchall()
        if len(result) == 0:
            return False
        else:
            return True
