import logging
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="myusername",
    password="mypassword"
)

print(mydb)

logging.basicConfig(filename='longsoup.log', level=logging.DEBUG,
                    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
