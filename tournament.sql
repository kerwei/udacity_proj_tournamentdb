-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


-- DROP DATABASE
-- Drop existing connection solution provided by GoatWalker on
-- http://stackoverflow.com/questions/5408156/how-to-drop-a-postgresql-database-if-there-are-active-connections-to-it
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'tournament'
AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

-- PLAYER TABLE
DROP TABLE IF EXISTS Player CASCADE;

CREATE TABLE Player
(
  id SERIAL primary key,
  name varchar(100),
  created timestamp default current_timestamp
);


-- TOURNAMENT TABLE
DROP TABLE IF EXISTS Tournament CASCADE;

CREATE TABLE Tournament
(
  id SERIAL primary key,
  name varchar(300),
  created timestamp default current_timestamp
);

INSERT INTO Tournament VALUES (DEFAULT , 'default_tournament', DEFAULT);


-- REGISTER TABLE
DROP TABLE IF EXISTS Register;

CREATE TABLE Register
(
  tournament_id int REFERENCES Tournament(id),
  player_id int REFERENCES Player(id)
);


-- MATCH TABLE
DROP TABLE IF EXISTS Match;

CREATE TABLE Match
(
  round int not null,
  tournament_id int REFERENCES Tournament(id),
  winner_id int REFERENCES Player(id),
  loser_id int REFERENCES Player(id)
);