/* 
Table definitions for the tournament project - extra credit version.
This implementation by Daniel McVicker, begun 2015-04-30
This file contains SQL 'create table' and 'create view' statements
 
CAUTION: this script will drop your existing database. 
Be certain you want to create or recreate the database before running!

To run this file, start psql from the directory where this file is on your vagrant box and enter: 
"\i tournament.sql"  run from the psql console. 
*/

-----------------------------------ENTER SCRIPT-----------------------------------

-- Create database "tournament" and connect to that database before creating tables
\c vagrant
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

-- Create a table to store player values player_id and name

CREATE TABLE Players
(id serial primary key,
name text
);

-- Create a table to store tournament data
-- This is implemented to allow multiple tournaments

CREATE TABLE Tournaments
(id serial primary key,
name text
);

CREATE TABLE Registrants
(
id serial primary key,
tournament_id integer references Tournaments(id),
player_id integer references Players(id)
);

/*
Create a table to store match information tournament, player_1, player_2, and winner
Note that player_2 must be nullable to support odd numbers of players 
and winner must be nullable to support tie games


 Don't know how to restrict player_1 and player_2 to registered players in the 
 tournament only. Constraints can only deal with the current row, no subqueries.
 Feel like I could create a function but I worry about that being sane.  
 */


CREATE TABLE Matches
(id serial primary key,
tournament_id integer references Tournaments (id),
player_1 integer references Players (id), 
player_2 integer references Players (id), 
winner integer CONSTRAINT match_player CHECK (winner IS NULL OR winner IN (player_1, player_2))
);

--view of registered players

CREATE VIEW v_registrant_names AS
SELECT Registrants.tournament_id, Registrants.player_id, name 
FROM Registrants, Players WHERE registrants.player_id=Players.id AND registrants.player_id!=0;

--view of the wins accumulated
CREATE VIEW v_wins AS
SELECT Tournaments.id AS tournament_id, Matches.winner AS player_id, count (*) as wins
FROM Players, Tournaments, Matches
WHERE Matches.winner = Players.id AND
Tournaments.id = Matches.tournament_id
GROUP BY Tournaments.id, Matches.winner
ORDER BY player_id;

--view of the matches for each registrant
CREATE VIEW v_registrant_matches AS
SELECT Registrants.player_id, count (*) AS matches FROM  Matches , Registrants
WHERE Matches.player_1=Registrants.player_id OR Matches.player_2=Registrants.player_id
GROUP BY Registrants.player_id;

--create functions to create Opponent Match Wins Functionality

--gets OMW for a single player
CREATE OR REPLACE FUNCTION getplayeropponents(player integer)
RETURNS TABLE(player_id int, omw numeric) AS $$
	SELECT $1 as omw_Player, SUM (wins) as omw from (SELECT DISTINCT PLAYER_2 AS player_id FROM
	Matches WHERE player_1=$1
	UNION
	SELECT DISTINCT PLAYER_1 AS player_id FROM Matches WHERE player_2=$1
	order by player_id) j 
	join v_wins on j.player_id = v_wins.player_id;
$$ LANGUAGE SQL;

--loops through all registered players for a given tournament, getting OMW for each
CREATE OR REPLACE FUNCTION gettournamentomw(tournament integer)
RETURNS TABLE(player_id int, omw numeric) AS $BODY$
DECLARE
	r Registrants%rowtype;
BEGIN
	FOR r IN SELECT * FROM registrants WHERE Registrants.player_id != 0 and tournament_id = $1 ORDER BY player_id LOOP 
	RETURN QUERY SELECT * from getplayeropponents(r.player_id);	 	
	END LOOP;
	RETURN;
END
$BODY$
LANGUAGE 'plpgsql' ;

-- compile the overall standings: id, name, wins, matches

CREATE OR REPLACE FUNCTION getstandings(tournament integer)
--this function returns more data than is absolutely necessary to pass the tests
RETURNS TABLE(tournament_id int, player_id int, name text, wins bigint, omw numeric, matches bigint) AS $$
	WITH omw AS (SELECT * FROM gettournamentomw($1))
	SELECT v_registrant_names.tournament_id, v_registrant_names.player_id, v_registrant_names.name, 
	COALESCE (v_wins.wins, 0) AS wins,
	COALESCE (omw.omw, 0) AS omw,
	COALESCE (v_registrant_matches.matches, 0) AS matches
	FROM v_registrant_names
	LEFT OUTER JOIN v_wins ON (v_registrant_names.player_id = v_wins.player_id)
	LEFT OUTER JOIN v_registrant_matches ON (v_registrant_matches.player_id=v_registrant_names.player_id)
	LEFT OUTER JOIN omw ON (v_wins.player_id = omw.player_id)
    WHERE v_registrant_names.tournament_id = $1
	ORDER BY wins desc, omw desc;
$$ LANGUAGE SQL;

--insert an artificial player to act as the bye round. 
INSERT INTO Players (id, name) VALUES (0, 'bye round');


