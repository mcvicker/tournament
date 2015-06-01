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
    # First we have to remove registered people before we can delete the tournaments. 
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
    c.execute("INSERT INTO Tournaments (id, name)SELECT %s, %s WHERE NOT EXISTS (SELECT id FROM Tournaments WHERE id = %s)", (id, name, id))
    pg.commit()
    pg.close()
    
def createPlayer(name):
    pg = connect()
    c = pg.cursor()
    #inserting new player
    c.execute("INSERT INTO Players (name) VALUES (%s)", (name,))
    pg.commit()
    pg.close()

def enterTournament(player_id, tournament_id=1):
    pg = connect()
    c = pg.cursor()
    #inserting new player into tournament
    c.execute("INSERT INTO Registrants (tournament_id, player_id) VALUES (%s, %s)", (tournament_id, player_id))
    pg.commit()
    pg.close()

def countPlayers(tournament=1):
    """Returns the number of players currently registered."""
    pg = connect()
    c = pg.cursor()
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
    #inserting new player
    #c.execute("INSERT INTO Players (name) VALUES (%s)", (name,))
    #registers the current player into the tournament
    #c.execute("INSERT INTO Registrants (tournament_id, player_id) VALUES (%s, (SELECT currval('Players_id_seq')))", (tournament,))
    c.execute("SELECT id FROM Players ORDER BY id DESC LIMIT 1")
    player_id = c.fetchone()
    pg.close()
    enterTournament(player_id[0], tournament)
    
def isRegistered(player_id=0,tournament_id=1):
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
    c.execute("SELECT player_id, name, wins, matches FROM v_standings WHERE tournament_id = %s", ([tournament]))
    fetch = c.fetchall()
    
    
    #query = """SELECT %s as Player, SUM (wins) AS OMW 
    #FROM (SELECT DISTINCT winner, wins 
    #      FROM v_wins, Matches 
    #      WHERE (Matches.player_1 = %s OR Matches.player_2 = %s)
    #             AND Matches.winner != %s
    #             AND v_wins.player_id = matches.winner
    #      ) o"""
    #
    #for player in fetch:
    #    c.execute(query,(player[0],player[0],player[0],player[0]));
    #    refetch = c.fetchall()
    #    player.append(refetch)
    #for player in fetch:
    #    c.execute("SELECT %s as player, SUM (wins)ASWinner FROM Matches WHERE (player_1 = %s OR player_2 = %s) AND winner != %s AND tournament_id = %s",(player[0],player[0],player[0],tournament))
    #    gotIt = c.fetchall()
    #    print gotIt
    #    print
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
        #c.execute("UPDATE players SET matches = matches + 1 where id = %s OR id = %s", (winner,loser))
    if tied=="y":
        c.execute("INSERT INTO Matches (tournament_id, player_1, player_2) VALUES (%s, %s, %s)", (tournament, winner, loser))
    pg.commit()
    pg.close()
    
def byeMatch(tournament=1):
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
    #if there are an odd number of players for your tournament, register a bye week
    if len(standings)%2==1 and not isRegistered(0,tournament):
        enterTournament(0,tournament)
    #if player 0 (bye week) is registered, determine the bye week match up
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
        
    #else:    
    #    while i < len(standings):
    #        extender = (standings[i])[:2] + (standings [i+1])[:2]
    #        result.append(extender)
    #        i += 2
           
    return result   
    #if there are an odd number of entrants, enter the 'bye round' player into the tournament.
    # adding pseudocode here:
    # if a player has playedBye then go on to the next player.
    # once a player who hasn't playedBye is found
    # match that player with the bye round.
    # exclude that player and the bye round from the standings and reseed the remaining players.
   
    
    
'''   
    pg = connect()
            c = pg.cursor() 
            extender = ()
            c.execute("SELECT player_id, name FROM v_standings WHERE tournament_id = %s ORDER BY wins desc LIMIT 2 offset %s", (tournament,i))
            fetch = c.fetchall()
            pg.close()
            extender = fetch[0] + fetch[1]
            result.append(extender)
            i += 2 
    registerPlayer("Son Goku")
    registerPlayer("Vegeta")
    registerPlayer("Piccolo")
    registerPlayer("Son Gohan")
    registerPlayer("Krillin")
        playedBye = True
        while playedBye == True:
            pg = connect()
            c = pg.cursor() 
            extender = ()
            c.execute("SELECT player_id FROM v_standings ORDER BY wins desc")
            fetch = c.fetchall()
            pg.close()
            for row in fetch:
                pg = connect()
                c = pg.cursor() 
                c.execute("")
                fetch = c.fetchall()
                pg.close()
                playedBye = (
            result.append(extender)
            i += 2
        
    else:     
 
        
        
   
        ## how do you determine if a player has played 'bye round' (player 0) before?
        pg = connect()
        c = pg.cursor()          
        c.execute("SELECT player_id, name FROM v_standings ORDER BY wins desc LIMIT 1 offset %s", (i,))
        fetch = c.fetchall()
        pg.close()
        extender = fetch[0] + (0, 'bye round')
        result.append(extender)
        i += 1
        ## everyone else gets another matchup
        while i < len(standings):
            pg = connect()
            c = pg.cursor()
            extender = ()
            c.execute("SELECT player_id, name FROM v_standings ORDER BY wins desc LIMIT 2 offset %s", (i,))
            fetch = c.fetchall()
            pg.close()
            extender = fetch[0] + fetch[1]
            result.append(extender)
            i += 2
 
    
        fetch = (1,)
        extender = ()
        for player in standings:
            while fetch[0] > 0:
                extender = player
                pg = connect()
                c = pg.cursor() 
                c.execute("SELECT COUNT (*) FROM Matches where tournament_id = %s AND player_1 = %s AND player_2 = 0;", (tournament, player[0]))
                fetch = c.fetchone()
                pg.close()
                
        pg = connect()
        c = pg.cursor() 
        extender = ()
        c.execute("SELECT player_id, name FROM v_standings ORDER BY wins desc LIMIT 2 offset %s", (i,))
        fetch = c.fetchall()
        pg.close()
        extender = fetch[0] + fetch[1]
        result.append(extender)
        i += 2    
            
 '''    
    
    
    

