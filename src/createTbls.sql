-- create database if not exists papers ;
-- use papers;
-- order cares, because of the dependence
DROP TABLE IF EXISTS Possess;
DROP TABLE IF EXISTS Connection;
DROP TABLE IF EXISTS Document;
DROP TABLE IF EXISTS Author;

-- create table for papers/topics
CREATE TABLE IF NOT EXISTS Document(
  docID VARCHAR(255) PRIMARY KEY,
  title TEXT NOT NULL,
  year INT(4),
  source TEXT,
  type VARCHAR(30),
  description TEXT,
  bib TEXT
);
-- create table for authors
CREATE TABLE IF NOT EXISTS Author(
  authorID INT PRIMARY KEY auto_increment,
  lastname VARCHAR(255) NOT NULL,
  firstname VARCHAR(255) NOT NULL,
  organization VARCHAR(255),
  description TEXT
);
-- create table for author-paper relation
CREATE TABLE IF NOT EXISTS Possess(
  docID VARCHAR(255) NOT NULL,
  authorID INT NOT NULL,
  description TEXT,
  FOREIGN KEY (docID) REFERENCES Document(docID),
  FOREIGN KEY (authorID) REFERENCES Author(authorID),
  PRIMARY KEY (docID, authorID)
);
-- create table for papers relation
CREATE TABLE IF NOT EXISTS Connection(
  srcDocId VARCHAR(255) NOT NULL,
  dstDocId VARCHAR(255) NOT NULL,
  description TEXT,
  FOREIGN KEY (srcDocId) REFERENCES Document(docID),
  FOREIGN KEY (dstDocId) REFERENCES Document(docID),
  PRIMARY KEY (srcDocId, dstDocId)
);
