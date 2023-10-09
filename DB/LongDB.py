# A python class called LonbDB that accesses a mysql database and performs queries

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
        """
        self.mycursor.execute("SELECT * FROM users WHERE id = '" + id + "'")
        myresult = self.mycursor.fetchall()
        return myresult

    def validate_user(self, table, useremail, password):
        """
        validate_user is a function that returns a user from the database.
        It requires the following parameters:
        useremail: the useremail of the user to return
        password: the password of the user to return
        """
        # self.mycursor.execute(
        #     "SELECT * FROM "
        #     + table
        #     + " WHERE useremail = '"
        #     + useremail
        #     + "' AND password = '"
        #     + password
        #     + "'"
        # )
        # myresult = self.mycursor.fetchall()
        # print(myresult)
        self.mycursor.execute(
            "Select useremail from " + table + " where useremail = '" + useremail + "'"
        )
        myresult = self.mycursor.fetchall()
        # strip the tuple, leaving behind only the useremail
        myresult = myresult[0]

        print(f"Did {myresult[0]} match {useremail}?")
        # Note, it did not. It returned [('test@example',)]We need index0
        print(f"The length of myresult[0] is {len(myresult[0])}")
        if useremail in myresult:
            print(
                f"It looks like myresult is {myresult}. Useremail {useremail} matches {myresult}."
            )
            myresult = True
        return myresult

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
