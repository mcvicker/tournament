#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before"
                         " they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in "
                         "standings, even if they have no matches played.")
    print ("6. Newly registered players appear in "
           "the standings with no matches.")


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError(
                "Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

# tests after this point were written to test the extended functionality.

# this is to test the results of an Odd Number of registrants
# one player should get paired with a bye round in each round
# of a tournament with an odd number of entrants.
# A player should only be matched with the bye round once.


def testOdd():
    deleteMatches()
    deletePlayers()
    registerPlayer("Rock")
    registerPlayer("Scissors")
    registerPlayer("Paper")
    standings = playerStandings()
    [id1, id2, id3] = [row[0] for row in standings]
    pairings1 = swissPairings()
    if len(pairings1) != 2:
        raise ValueError(
            "For three players, swissPairings should return two pairs."
            " (Including one bye)")
    print "9. With zero matches, one player gets a bye."
    reportMatch(id1, 0)
    reportMatch(id2, id3)
    pairings2 = swissPairings()
    standings = playerStandings()
    if pairings1 == pairings2:
        raise ValueError(
            "After one match, the bye round should not repeat.")
    print "10. After one match, the bye round does not repeat."

# this function tests if ties are supported


def testTied():
    deleteMatches()
    deletePlayers()
    registerPlayer("Rams")
    registerPlayer("49ers")
    standings = playerStandings()
    [id1, id2] = [row[0] for row in standings]
    reportMatch(id1, id2, 1, "y")
    standings = playerStandings()
    pairings = swissPairings()
    [(pid1, pname1, pid2, pname2)] = pairings
    correct_pairs = set([frozenset([id1, id2])])
    actual_pairs = set([frozenset([pid1, pid2])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Tied matches not supported.")
    print "11. Tied matches can be reported."

# this function tests if multiple tournaments are supported.
# it is explicitly based on linusdong's method here:
# https://github.com/linusdong/Udacity_Nanodegree_FullStackWeb/blob/master/P2/extra_test.py


def testMultipleTourneys():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    createTournament(2015, "Stanley Cup")
    createTournament(2014, "Super Bowl")
    registerPlayer("Denver Broncos", 2014)
    registerPlayer("New England Patriots", 2014)
    registerPlayer("Seattle Seahawks", 2014)
    registerPlayer("Green Bay Packers", 2014)
    registerPlayer("Chicago Blackhawks", 2015)
    registerPlayer("Tampa Bay Lightning", 2015)
    registerPlayer("Anaheim Mighty Ducks", 2015)
    registerPlayer("New York Rangers", 2015)
    standings = playerStandings(2014)
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2, 2014)
    reportMatch(id3, id4, 2014)
    standings = playerStandings(2015)
    [id1_2015, id2_2015, id3_2015, id4_2015] = [row[0] for row in standings]
    reportMatch(id1_2015, id2_2015, 2015)
    reportMatch(id4_2015, id3_2015, 2015)
    pairings = swissPairings(2014)
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print ("12. After one match,"
           " players with one win in each tourney are paired.")

# this function tests to see if results are sorted by opponent match wins.
# this test is explicitly based on this example:
# http://www.johnpratt.com/items/docs/ranker/swiss.html
# and the approach is very similar to Jeff from Udacity's approach:
# https://gist.github.com/jeffudacity/d4ccde9860a7ae40070a


def testOMW():
    deleteMatches()
    deletePlayers()
    deleteTournaments()
    createTournament(1, "World Martial Arts Tournament")
    players = [
        (1, 'Goku'),
        (2, 'Freeza'),
        (3, 'Piccolo'),
        (4, 'Cell'),
        (5, 'Vegeta'),
        (6, 'Android 18'),
        (7, 'Yamcha'),
        (8, 'Tien'),
        (9, 'Trunks'),
        (10, 'Gohan')
    ]

    for player in players:
        registerPlayer(player[1])
    standings = playerStandings()
    [id1, id2, id3, id4, id5,
     id6, id7, id8, id9, id10] = [row[0]for row in standings]
    reportMatch(id1, id6)
    reportMatch(id2, id7)
    reportMatch(id3, id8)
    reportMatch(id4, id9)
    reportMatch(id5, id10)

    # end of round 1

    reportMatch(id1, id3)
    reportMatch(id2, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id9)
    reportMatch(id8, id10)

    # end of round 2

    reportMatch(id1, id4)
    reportMatch(id2, id6)
    reportMatch(id3, id10)
    reportMatch(id5, id7)
    reportMatch(id8, id9)

    # end of round 3

    standings2 = playerStandings()
    [pid1, pid2, pid3, pid4, pid5,
     pid6, pid7, pid8, pid9, pid10] = [row[0]for row in standings2]
    initial_standings = ([id1, id2, id5, id3, id8, id4, id7, id6, id10, id9])
    final_standings = (
        [pid1, pid2, pid3, pid4, pid5, pid6, pid7, pid8, pid9, pid10])

    # used a tuple instead of a set to make sure that the order matters.

    if initial_standings != final_standings:
        raise ValueError(
            "Players are not sorted by Opponent Match Wins.")
    print "13. Standings are sorted by Opponent Match Wins."


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "All basic tests pass. \n"
    testOdd()
    testTied()
    testMultipleTourneys()
    testOMW()
    print "Success!  All tests pass! \n"
