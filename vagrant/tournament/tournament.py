#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches():
    """Remove all the match records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("DELETE FROM Matches")
    pg.commit()
    pg.close()

def deletePlayers():
    """Remove all the player records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("DELETE FROM Registrants")
    c.execute("DELETE FROM Players where id !=0")
    pg.commit()
    pg.close()
    
def deleteTournaments():
    """remove all the tournament records from the database."""
    pg = connect()
    c = pg.cursor()
    # First we have to remove registrants before we can delete the tournaments. 
    c.execute("DELETE FROM Registrants")
    # Since matches are associated with a specific tournament, we have to delete those as well
    c.execute("DELETE FROM Matches")
    c.execute("DELETE FROM Tournaments")
    pg.commit()
    pg.close()

def createTournament(id=1, name="Tournament 1"):
    """Create a new tournament."""
    pg = connect()
    c = pg.cursor()
	#insert the values provided into the Tournaments table if it doesn't already exist.
    c.execute("INSERT INTO Tournaments (id, name)SELECT %s, %s WHERE NOT EXISTS (SELECT id FROM Tournaments WHERE id = %s)", (id, name, id))
    pg.commit()
    pg.close()
    
def createPlayer(name):
    """Create a new player."""
    pg = connect()
    c = pg.cursor()
    #inserting new player
    c.execute("INSERT INTO Players (name) VALUES (%s)", (name,))
    pg.commit()
    pg.close()

def enterTournament(player_id, tournament_id=1):
    """Insert an existing player into a tournament."""
    pg = connect()
    c = pg.cursor()
    #Inserts player into the Registrants table
    c.execute("INSERT INTO Registrants (tournament_id, player_id) VALUES (%s, %s)", (tournament_id, player_id))
    pg.commit()
    pg.close()

def countPlayers(tournament=1):
    """Returns the number of players currently registered for the given tournament."""
    pg = connect()
    c = pg.cursor()
	#only looking for the specified tournament
    c.execute("SELECT COUNT (*) FROM Registrants WHERE tournament_id=(%s)", (tournament,))
    fetch = c.fetchone()[0]
    pg.close()
    return int(fetch)

def registerPlayer(name, tournament=1, tournament_name="Tournament"):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    #checks for the existence of the Tournament and creates it if needed
    createTournament(tournament, tournament_name)
    createPlayer(name)
    pg = connect()
    c = pg.cursor()
	#gets the most recent player
    c.execute("SELECT id FROM Players ORDER BY id DESC LIMIT 1")
    player_id = c.fetchone()
    pg.close()
    enterTournament(player_id[0], tournament)
    
def isRegistered(player_id=0,tournament_id=1):
    """Determines if a specific player is registered for a tournament."""
    pg = connect()
    c = pg.cursor() 
    extender = ()
    c.execute("SELECT COUNT (*) FROM Registrants WHERE tournament_id = %s AND player_id = %s", (tournament_id,player_id))
    isRegistered = c.fetchone()
    pg.close()
    if isRegistered[0] == 1:
        return True
    else:
        return False

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
    pg = connect()
    c = pg.cursor()
    c.execute("SELECT player_id, name, wins, matches FROM getstandings(%s)", ([tournament]))
    fetch = c.fetchall()
    pg.close()  
    return fetch

def reportMatch(winner, loser, tournament=1, tied="n"):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    createTournament()
    pg = connect()
    c = pg.cursor()
    if tied=="n":
        c.execute("INSERT INTO Matches (tournament_id, player_1, player_2, winner) VALUES (%s, %s, %s, %s)", (tournament, winner, loser, winner))
    if tied=="y":
        c.execute("INSERT INTO Matches (tournament_id, player_1, player_2) VALUES (%s, %s, %s)", (tournament, winner, loser))
    pg.commit()
    pg.close()
    
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
            pg = connect()
            c = pg.cursor() 
            c.execute("SELECT COUNT (*) FROM Matches where tournament_id = %s AND player_1 = %s AND player_2 = 0;", (tournament, (standings[i])[0]))
            fetch = c.fetchone()
            pg.close()
            if fetch[0] == 0:
                extender = (standings)[i]
            i += 1
        result = extender
    return result
    
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