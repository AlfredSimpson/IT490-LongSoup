-- Create a database, longsoup, and multiple tables within it.
CREATE DATABASE longsoup;

-- Create a table, users, with a primary key, userid, and two unique fields, username and usermail.
CREATE TABLE users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    usermail VARCHAR(50) UNIQUE
);

-- Create a table, userpass, with a foreign key, userid, and a field, userpass. userid INT is a foreign key from the users table. userpass is hashed using the SHA2 algorithm.
CREATE TABLE userpass (
    userid INT,
    userpass VARCHAR(64),
    FOREIGN KEY (userid) REFERENCES users(userid)
);

-- Create a table, userinfo, with a foreign key, userid, and two fields, userfname and userlname.
CREATE TABLE userinfo (
    userid INT,
    userfname VARCHAR(50),
    userlname VARCHAR(50),
    FOREIGN KEY (userid) REFERENCES users(userid)
);

-- Prepopulate the table users with a single user, longsoup, which uses the username longsoup and the usermail nicc-group@njit.edu.
INSERT INTO
    users (username, usermail)
VALUES
    ('longsoup', 'nicc-group@njit.edu');