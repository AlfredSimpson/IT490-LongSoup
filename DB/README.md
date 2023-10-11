# Database Server

This is the database server. This handles the database and the data within it.

## Languages and frameworks used:

- MySQL

## Setup

Information coming soon


## Planning Documentation:
## First table - users

This table is a baseline for users.

Name of table: users

userid = int
username = varchar
usermail = varchar (email addresses)


## Second table - Passwords
Should be hashed

This is our password table, stored separately.
Name of table: userpass

userid - int (FK)
userpass - varchar (encrypt)

# Third table - User Information

This is additional information about the user that we may want to add to in the future.

Name of table: userinfo
userid - int - pk/fk
userfname - varchar - firstname
userlname - varchar - lastname
