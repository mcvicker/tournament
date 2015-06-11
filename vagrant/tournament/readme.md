##Udacity's Full-stack Nanodegree Tournament Project

###Prerequisites:

**To run this project, you'll need to install vagrant.** For a brief overview of installing vagrant, check here:

https://www.udacity.com/wiki/ud197/install-vagrant

Once you've installed vagrant, start a session with the vagrant machine by navigating to the \vagrant\tournament directory
(in git bash for Windows or your terminal program for Mac) and type the following commands:

    vagrant up

Once the machine comes up, start an ssh session by typing

    vagrant ssh

Once that is complete, navigate to the \fullstack\vagrant\tournament\ directory.

**Installing and Running the Project Test Cases**

You can set up the database and run the test cases very easily by using the tournament.sh script as follows:

    bash tournament.sh

The results of the setup script and the tests will be printed into the terminal.

Alternately, you may create the database independently by starting psql from the terminal then typing 

    \i /vagrant/tournament/tournament.sql

This will allow you to interact with the database directly. If you need to quickly add data, check out this gist from Jeff at Udacity:

https://gist.github.com/jeffudacity/d4ccde9860a7ae40070a

**Purpose of the Project**

*The Tournament Project is to model a Swiss-Style tournament in a database format.*

This project is intended to show the ability to model data in a database using a PostgreSQL back-end with program logic in Python. You can read more about the goals of this project here: https://www.udacity.com/course/viewer#!/c-ud197-nd/l-3521918727/m-3519689284

The basic functionality includes these functions:

    registerPlayer(name)

Adds a player to the tournament by putting an entry in the database. The database assigns an ID number to the player. Different players may have the same names but will receive different ID numbers.

    countPlayers()

Returns the number of currently registered players (counted directly in the database).

    deletePlayers()

Clear out all the player records from the database.

    reportMatch(winner, loser)

Stores the outcome of a single match between two players in the database.

    deleteMatches()

Clears out all the match records from the database.

    playerStandings()

Returns a list of (id, name, wins, matches) for each player, sorted by the number of wins each player has.

    swissPairings()

Given the existing set of registered players and the matches they have played, generates and returns a list of pairings according to the Swiss system. Each pairing is a tuple (id1, name1, id2, name2), giving the ID and name of the paired players. For instance, if there are eight registered players, this function should return four pairings. This function should use playerStandings to find the ranking of players.

*In addition, I have implemented the following extra options*

* If there is an odd number of players, assign one player a “bye” (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
* Games where a draw (tied game) is possible are supported.
* When two players have the same number of wins, they are ranked according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
* More than one tournament is now supported in the database, so matches do not have to be deleted between tournaments. This distinguishes between “a registered player” and “a player who has entered in tournament #123”.
