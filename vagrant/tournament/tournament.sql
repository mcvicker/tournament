/* 
Table definitions for the tournament project - extra credit version.
This implementation by Daniel McVicker, begun 2015-04-30
Completed 2015-06-15
This file contains SQL 'create table' and 'create view' statements
as well as some SQL and PG/SQL functions. 
 
CAUTION: this script will drop your existing database. 
Be certain you want to create or recreate the database before running!

To run this file, start psql from the directory where this file is on your 
box and enter: 
"\i tournament.sql"  
from the psql console. 
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
tournament_id integer references Tournaments(id),
player_id integer references Players(id),
PRIMARY KEY (tournament_id, player_id)
);


/*Create a table to store match information: tournament, player_1, player_2, and winner
Winner must be nullable to support tie games. Matches are constrained so that only registered players
can have a match and they must be registered for the same tournament. 
Matches are also constrained so that a player can't play himself. 
*/

CREATE TABLE Matches
(tournament_id integer, 
player_1 integer,
player_2 integer
CONSTRAINT different_player CHECK (player_1 != player_2),
FOREIGN KEY (tournament_id, player_1) REFERENCES Registrants(tournament_id, player_id),
FOREIGN KEY (tournament_id, player_2) REFERENCES Registrants(tournament_id, player_id), 
winner integer CONSTRAINT match_player CHECK (winner IS NULL OR winner IN (player_1, player_2)),
PRIMARY KEY (tournament_id, player_1, player_2)
);

/* A final constraint on matches so that players can only be matched up once per tournament
This still allows for the same players to be matched in subsequent tournaments.
For example: Players A and B can play each other in tournament 1, but then B, A 
cannot play each other in the same tournament. A and B can play each other again in tournament 2 but again, only
once. */

CREATE UNIQUE INDEX isinglematchup on Matches(tournament_id,GREATEST(player_1,player_2), LEAST(player_1,player_2));

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
-- This function returns more data than is strictly needed to pass the test cases.
-- It is limited in the python portion but could easily deliver all this information with minor modification.

CREATE OR REPLACE FUNCTION getstandings(tournament integer)
RETURNS TABLE(tournament_id int, player_id int, name text, wins bigint, omw numeric, matches bigint) AS $$
	WITH omw AS (SELECT * FROM gettournamentomw($1))
	SELECT v_registrant_names.tournament_id, v_registrant_names.player_id, v_registrant_names.name, 
	COALESCE (v_wins.wins, 0) AS wins,
	COALESCE (omw.omw, 0) AS omw,
	COALESCE (v_registrant_matches.matches, 0) AS matches
	FROM v_registrant_names
	LEFT OUTER JOIN v_wins ON (v_registrant_names.player_id = v_wins.player_id)
	LEFT OUTER JOIN v_registrant_matches ON (v_registrant_matches.player_id=v_registrant_names.player_id)
	LEFT OUTER JOIN omw ON (v_registrant_names.player_id = omw.player_id)
    WHERE v_registrant_names.tournament_id = $1
	ORDER BY wins desc, omw desc, player_id;
$$ LANGUAGE SQL;

--insert an artificial player to act as the bye round. 

INSERT INTO Players (id, name) VALUES (0, 'bye round');


