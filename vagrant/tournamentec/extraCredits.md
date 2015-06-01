**This is the extra credit version of the Tournament Project. **
*EC is designed to implement the following changes:*

* Don’t assume an even number of players. If there is an odd number of players, assign one player a “bye” (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
* Support games where a draw (tied game) is possible. This will require changing the arguments to reportMatch.
* When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
*Support more than one tournament in the database, so matches do not have to be deleted between tournaments. This will require distinguishing between “a registered player” and “a player who has entered in tournament #123”.
