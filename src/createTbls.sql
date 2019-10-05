-- create database if not exists papers ;
-- use papers;
-- create table for papers/topics
CREATE TABLE IF NOT EXISTS Document(
  docID VARCHAR(255) PRIMARY KEY,
  title TEXT NOT NULL,
  year INTEGER,
  source TEXT,
  type VARCHAR(30),
  description TEXT,
  bib TEXT
);
-- create table for authors
CREATE TABLE IF NOT EXISTS Author(
  authorID INTEGER PRIMARY KEY auto_increment,
  lastname VARCHAR(255) NOT NULL,
  firstname VARCHAR(255) NOT NULL,
  organization VARCHAR(255),
  description TEXT
);
-- create table for author-paper relation
CREATE TABLE IF NOT EXISTS Possess(
  docID VARCHAR(255) NOT NULL,
  authorID INTEGER NOT NULL,
  description TEXT,
  FOREIGN KEY (docID) REFERENCES Document(docID) ON DELETE CASCADE,
  FOREIGN KEY (authorID) REFERENCES Author(authorID) ON DELETE CASCADE,
  PRIMARY KEY (docID, authorID)
);
-- create table for papers relation
CREATE TABLE IF NOT EXISTS Connection(
  srcDocId VARCHAR(255) NOT NULL,
  dstDocId VARCHAR(255) NOT NULL,
  description TEXT,
  FOREIGN KEY (srcDocId) REFERENCES Document(docID) ON DELETE CASCADE,
  FOREIGN KEY (dstDocId) REFERENCES Document(docID) ON DELETE CASCADE,
  PRIMARY KEY (srcDocId, dstDocId)
);
