# A python class called LongDB that accesses a mysql database and performs queries. We should eventually simplify this and make it more secure.
# This should also be used to extend the functionality of other, subsequent classes

import mysql.connector
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
            host=host, user=user, password=password, database=database
        )
        self.mycursor = self.mydb.cursor()

    def get_user_by_username(self, username):
        """
        get_user is a function that returns a user from the database.
        It requires the following parameters:
        username: the username of the user to return
        """
        self.mycursor.execute("SELECT * FROM users WHERE username = '" + username + "'")
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

    def auth_user(self, table, useremail, password):
        """
        auth_user(table, useremail,password) is a function that returns a user from the database.
        It requires the following parameters:
        useremail: the useremail of the user to return
        password: the password of the user to return
        """
        self.mycursor.execute(
            "Select useremail from " + table + " where useremail = '" + useremail + "'"
        )
        emailResult = self.mycursor.fetchall()
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

        return emailMatch and passMatch

    # User modification methods

    def add_user(self, table, useremail, password):
        """
        add_user is a function that adds a user to the database.
        It requires the following parameters:
        table: the table to add the user to
        useremail: the username of the user to add
        password: the password of the user to add
        """
        sql = "INSERT INTO " + table + " (useremail, password) VALUES (%s, %s)"
        val = (useremail, password)
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return self.mycursor.rowcount, f"{useremail} added!"

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
