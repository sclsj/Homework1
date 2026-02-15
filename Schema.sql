/* Only for mysql */

DROP DATABASE IF EXISTS Homework_1;

CREATE DATABASE Homework_1;
USE Homework_1;

/* Only for mysql */

/* no longer needed since we dropped database
DROP TABLE IF EXISTS SENATOR;
DROP TABLE IF EXISTS VOTE;
DROP TABLE IF EXISTS VOTECAST;
*/

CREATE TABLE SENATOR (
    MemberId VARCHAR(4) PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Party CHAR(1),
    State VARCHAR(30)
);

CREATE TABLE VOTE (
    CongressNumber INT,
    SessionNumber INT,
    Year YEAR,
    Date DATETIME,
    VoteNumber INT,
    PRIMARY KEY (CongressNumber, SessionNumber, VoteNumber)
);

CREATE TABLE VOTECAST (
    MemberId VARCHAR(4),
    CongressNumber INT,
    SessionNumber INT,
    VoteNumber INT,
    VoteChar CHAR(1),
    FOREIGN KEY (MemberId) REFERENCES SENATOR(MemberId),
    FOREIGN KEY (CongressNumber, SessionNumber, VoteNumber) REFERENCES VOTE(CongressNumber, SessionNumber, VoteNumber),
    PRIMARY KEY (MemberId, CongressNumber, SessionNumber, VoteNumber)
);