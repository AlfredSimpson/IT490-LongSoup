# Database


## First table - users

This table is a baseline for users.

userid = int
username = varchar
usermail = varchar (email addresses)


## Second table - Passwords
Should be hashed

This is our password table, stored separately.

userid - int (FK)
userpass - varchar (encrypt)

# Third table - User Information

This is additional information about the user that we may want to add to in the future.

userid - int - pk/fk
userfname - varchar - firstname
userlname - varchar - lastname
