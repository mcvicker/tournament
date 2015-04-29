-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
-- \i and path to this file to run
-- set default values for wins and matches

CREATE DATABASE tournament;
\c tournament;

-- Create database "tournament" and change to that database before creating tables

CREATE TABLE players
(id serial primary key,
name varchar(255),
wins integer NOT NULL DEFAULT 0,
matches integer NOT NULL DEFAULT 0);

CREATE TABLE match
(p1_id integer references players (id),
p2_id integer references players (id),
winner integer references players (id),
primary key (p1_id,p2_id)
);

