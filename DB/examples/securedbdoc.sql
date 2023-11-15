--PREQUISITES: mysql secure installation, aka a secured database that only allows specific passwords and privileges for users.
-- mysqli command line interface with access to commands like 'mysql -u root' 

-- create the securesoupdb2
CREATE DATABASE securesoupdb2;

-- to use the securesoupdb2
' use securesoupdb2 '

-- to create a user in mysql (stored in mysql's user table)
' CREATE USER 'SecureSoupAdmin'@'localhost' IDENTIFIED BY 'password-goes-here' '

-- grant privileges for SecureSoupAdmin to access securesoupdb2
'GRANT ALL PRIVILEGES ON securesoupdb2.* TO 'SecureSoupAdmin'@'localhost'; '

-- Creating the tables for securesoupdb2
create table users(
    uid int primary key not null auto_increment, 
    usermail varchar(50) unique not null, 
    password varchar(50) unique not null, 
    sessionid varchar(255) unique, 
    usercookieid varchar(255) unique 
);

create table userinfo(
    uid int, 
    spotify_username varchar(50) not null PRIMARY KEY, 
    fname varchar(50) not null, 
    lname varchar(50) not null, 
    FOREIGN KEY (uid) REFERENCES users(uid)
);

create table spotusers(
    spotid int primary key not null auto_increment, 
    uid int, spotname varchar(32) not null, 
    spotTokens varchar(255) not null, 
    spotTokenExp datetime not null, 
    FOREIGN KEY (uid) REFERENCES users(uid)
);

create table spotTaste(
    spotTasteID int PRIMARY KEY not null auto_increment, 
    spotid int, 
    avgPopularity int, 
    recommendation varchar(255), 
    topGenres json, 
    topTracks json, 
    topArtists json, 
    FOREIGN KEY spotid REFERENCES spotusers(spotid)
);

create table session(
    uid int, 
    token varchar(255) PRIMARY KEY not null, 
    date date, 
    FOREIGN KEY (uid) REFERENCES users(uid)
);

-- add a user to users
INSERT INTO
    users (usermail, password)
VALUES
    ('minecraftsteve2011@gmail.com', 'MineDiamonds2!');

-- view users

SELECT * FROM users; 

-- alter existing tables 

ALTER TABLE users ADD -- new column name, data type, etc. (ex. 'usermail varchar(50) unique not null);')

