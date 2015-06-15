#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
# by Daniel McVicker, begun 2015-04-30
# Completed 2015-06-15

import psycopg2

# utility functions to deal with the database

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    pg = psycopg2.connect("dbname=tournament")
    return pg
    
def sql(type,query,params=()):
    """Runs SQL commands in the tournament database.
    
    Args:
    type is the type of query:
    type "commit" is used for statements that require a commit (e.g. DELETE, INSERT, etc.).
    type "fetchone" is used for SELECT statements that return one row.
    type "fetchall" is used for SELECT statements that return a table.
    
    query is the language of the query.
    
    params are the parameters you use for parameter replacement in the query.
  
    """
    if type not in ["commit","fetchone","fetchall"]:
        raise ValueError(
            "Type is unknown, please use \"commit\", \"fetchone\", or \"fetchall.\" ")
    pg = connect()
    c = pg.cursor()
    c.execute(query,params)
    if type=="commit":
        pg.commit()
        result = None
    elif type=="fetchone":
        result = c.fetchone()
    elif type=="fetchall":
        result = c.fetchall()
    pg.close()
    return result
    
# "create" functions

def createTournament(id=1, name="Tournament 1"):
    """Create a new tournament."""
	#insert the values provided into the Tournaments table if it doesn't already exist.
    if tournamentExists()==False:
        query = "INSERT INTO Tournaments (id, name)SELECT %s, %s WHERE NOT EXISTS (SELECT id FROM Tournaments WHERE id = %s)"
        params = (id, name, id)
        sql("commit",query, params)
    else:
        raise ValueError(
            "Tournament %d already exists." % id)
    
    
def createPlayer(name):
    """Create a new player."""
    #inserting new player
    query = "INSERT INTO Players (name) VALUES (%s)"
    params = (name,)
    sql("commit",query, params)
    
def reportMatch(winner, loser, tournament=1, tied="n"):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    if tournamentExists(tournament)==False:
        createTournament(tournament)
    if tied=="n":
        query = "INSERT INTO Matches (tournament_id, player_1, player_2, winner) VALUES (%s, %s, %s, %s)"
        params = (tournament, winner, loser, winner)
    elif tied=="y":
        query = "INSERT INTO Matches (tournament_id, player_1, player_2) VALUES (%s, %s, %s)"
        params = (tournament, winner, loser)    
    else:
        raise ValueError(
            "Matches must either be tied or not tied. Please use y or n.")
    sql("commit",query,params)

# "read" functions

def countPlayers(tournament=1):
    """Returns the number of players currently registered for the given tournament."""
    query = "SELECT COUNT (*) FROM Registrants WHERE tournament_id=(%s)"
    params = (tournament,)
    fetch = sql("fetchone",query,params)[0]
    return int(fetch)
    
def isRegistered(player_id=0,tournament_id=1):
    """Determines if a specific player is registered for a tournament."""
    query = "SELECT COUNT (*) FROM Registrants WHERE tournament_id = %s AND player_id = %s"
    params = (tournament_id,player_id)
    isRegistered = sql("fetchone",query,params)
    if isRegistered[0] == 1:
        return True
    else:
        return False

def tournamentExists(tournament=1):
    """Determines if a specific tournament already exists or not."""
    query = "SELECT COUNT(*) FROM Tournaments WHERE id = %s"
    params = (tournament,)
    fetch = sql("fetchone",query,params)
    if fetch[0] == 0:
        return False
    elif fetch[0] == 1:
        return True
    else:
        raise ValueError(
            "Check database for consistency.")
            
def playerStandings(tournament=1):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    query = "SELECT player_id, name, wins, matches FROM getstandings(%s)"
    params =(tournament,)
    fetch = sql("fetchall",query,params) 
    return fetch

def swissPairings(tournament=1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings(tournament)
    i = 0
    result = []
    #if there are an odd number of players for your tournament, register a bye round
    if len(standings)%2==1 and not isRegistered(0,tournament):
        enterTournament(0,tournament)
    #if player 0 (bye round) is registered, determine the bye round match up
    if isRegistered(0,tournament):
        byePlayer = byeMatch()
        standings.remove(byePlayer)
        extender = byePlayer[:2] + (0, 'bye round')
        result.append(extender)
    #now create the standings
    while i < len(standings):
        extender = (standings[i])[:2] + (standings [i+1])[:2]
        result.append(extender)
        i += 2
           
    return result
    
# "update" functions

def enterTournament(player_id, tournament_id=1):
    """Insert an existing player into a tournament."""
    #Inserts player into the Registrants table
    query = "INSERT INTO Registrants (tournament_id, player_id) VALUES (%s, %s)" 
    params = (tournament_id, player_id)
    sql("commit",query,params)

def registerPlayer(name, tournament=1, tournament_name="Tournament 1"):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    #checks for the existence of the Tournament and creates it if needed
    if tournamentExists(tournament)==False:
        createTournament(tournament, tournament_name)
    createPlayer(name)
	#gets the most recent player
    query = "SELECT id FROM Players ORDER BY id DESC LIMIT 1"
    player_id = sql("fetchone",query)
    enterTournament(player_id[0], tournament)
    
def byeMatch(tournament=1):
    """Creates a bye match."""
    standings = playerStandings(tournament)
    i = 0
    result = []
    if isRegistered(0,tournament):
        fetch = (1,)
        extender = ()
        while i < len(standings) and fetch[0] > 0:
            extender = standings[i]
            query = "SELECT COUNT (*) FROM Matches where tournament_id = %s AND player_1 = %s AND player_2 = 0;"
            params = tournament, (standings[i])[0]
            fetch = sql("fetchone",query,params)
            if fetch[0] == 0:
                extender = (standings)[i]
            i += 1
        result = extender
    return result
    
# "delete" functions
    
def deleteMatches():
    """Remove all the match records from the database."""
    query = "DELETE FROM Matches"
    sql("commit",query)

def deletePlayers():
    """Remove all the player records from the database."""
    # We want to remove all registrants, but don't want to delete our bye player
    query = "DELETE FROM Registrants; DELETE FROM Players where id !=0"
    sql("commit",query)
    
def deleteTournaments():
    """remove all the tournament records from the database."""
    query = "DELETE FROM Tournaments"
    sql("commit",query)
    

    
