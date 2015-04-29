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
    c.execute("DELETE FROM match")
    pg.commit()
    pg.close()

def deletePlayers():
    """Remove all the player records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute("DELETE FROM players")
    pg.commit()
    pg.close()

def countPlayers():
    """Returns the number of players currently registered."""
    pg = connect()
    c = pg.cursor()
    c.execute("SELECT COUNT (*) FROM players")
    fetch = c.fetchone()[0]
    pg.close()
    return int(fetch)

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    pg = connect()
    c = pg.cursor()
    c.execute("INSERT INTO players (name, wins, matches) VALUES (%s, 0, 0)", (name,))
    pg.commit()
    pg.close()


def playerStandings():
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
    c.execute("SELECT * FROM players ORDER BY wins desc")
    fetch = c.fetchall()
    pg.close()
    return fetch

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    pg = connect()
    c = pg.cursor()
    c.execute("INSERT INTO match (p1_id, p2_id, winner) VALUES (%s, %s, %s)", (winner,loser,winner))
    c.execute("UPDATE players SET wins = wins + 1 where id = %s", (winner,))
    c.execute("UPDATE players SET matches = matches + 1 where id = %s OR id = %s", (winner,loser))
    pg.commit()
    pg.close()
 
def swissPairings():
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
    standings = playerStandings()
    i = 0
    result = []
    while (i < (len(standings))):
        pg = connect()
        c = pg.cursor()
        extender = ()
        c.execute("SELECT id, name FROM players ORDER BY wins desc LIMIT 2 offset %s", (i,))
        fetch = c.fetchall()
        pg.close()
        extender = fetch[0] + fetch[1]
        result.append(extender)
        i += 2
        
    return result
    
    

