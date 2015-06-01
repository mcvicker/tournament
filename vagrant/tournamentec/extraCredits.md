* Don’t assume an even number of players. If there is an odd number of players, assign one player a “bye” (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
	(Believe that this will be pythonic logic)
* Support games where a draw (tied game) is possible. This will require changing the arguments to reportMatch.
	(Tie games will also need to be represented in the database somehow)
* When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
	(May need to implement a view to reflect this?)
* Support more than one tournament in the database, so matches do not have to be deleted between tournaments. This will require distinguishing between “a registered player” and “a player who has entered in tournament #123”, 
so it will require changes to the database schema.