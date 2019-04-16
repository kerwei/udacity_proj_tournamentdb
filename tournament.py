#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import os
import psycopg2
import string

from functools import wraps

BASEDIR = os.getcwd()

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def injectQryString(f):
    """
    Fetch the SQL query, based on the given query name.
    Returns the function called, with an additional query kwarg

    Relies on fixed formatting applied to sql files.
    Python script imports the section after the second pipe 
    character. 
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        qname = f.__name__
        qpath = ''.join(['qry_', qname, '.sql'])
        with open(os.path.join(BASEDIR, 'sql', qpath)) as qfile:
            qstring = qfile.read()
            # Further split by forward slash to clear out comment chars at both ends
            query = qstring.split('|')[2].split('/')[1]
        kwargs['query'] = query
        return f(*args, **kwargs)
    
    return decorated_function


@injectQryString
def refplayerStandings(tournament_id=1, qname='playerStandings', **kwargs):
    """
        Refactored function of playerStandings()
        Returns a list of the players and their win records, sorted by wins.

        The first entry in the list should be the player in first place, or a player
        tied for first place if there is currently a tie.

        Returns:
            A list of tuples, each of which contains (id, name, wins, matches):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            wins: the number of matches the player has won
            matches: the number of matches the player has played
    """
    kwargs['query'] = kwargs['query'].replace('@tour_id', r'%s')
    with connect() as conn:
        with conn.cursor() as csor:
            csor.execute(
                kwargs['query'], 
                (str(tournament_id), str(tournament_id)))
            res = csor.fetchall()
    
    conn.close()
    return res


def deleteMatches(tournament_id = 1):
    """Remove all the match records from the database."""
    conn = connect()
    point = conn.cursor()

    qry = '''
        DELETE FROM Match
        WHERE tournament_id = %s
    '''
    point.execute(qry, str(tournament_id))
    conn.commit()
    point.close()
    conn.close()


def deletePlayers(tournament_id = 1):
    """Remove all the player records from the database."""
    conn = connect()
    point = conn.cursor()

    qry = '''
        DELETE FROM Register
        WHERE tournament_id = %s;
    '''
    point.execute(qry, str(tournament_id))
    conn.commit()
    point.close()
    conn.close()


def countPlayers(tournament_id = 1):
    """Returns the number of players currently registered."""
    conn = connect()
    point = conn.cursor()

    qry = '''
        SELECT COUNT(*) FROM Register
        WHERE tournament_id = %s;
    '''
    point.execute(qry, str(tournament_id))
    res = point.fetchone()[0]
    point.close()
    conn.close()

    return res


def registerPlayer(name, tournament_id = 1):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    point = conn.cursor()

    # Adds the player
    qry1 = '''
        INSERT INTO Player VALUES (DEFAULT, %s, DEFAULT);
    '''
    point.execute(qry1, (name,))
    conn.commit()

    # Includes the newly added player to the register
    # Gets the player id first
    qry2 = '''
        SELECT id FROM Player
        ORDER BY created DESC
        LIMIT 1;
    '''
    point.execute(qry2)
    res = point.fetchone()[0]

    # Adds the player id to the register
    qry3 = '''
        INSERT INTO Register(tournament_id, player_id)
        VALUES (%s, %s);
    '''
    point.execute(qry3, (str(tournament_id), str(res)))
    conn.commit()

    point.close()
    conn.close()


def playerStandings(tournament_id = 1):
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
    conn = connect()
    point = conn.cursor()

    # Gets the win record of players
    qry = '''
        ;WITH WinCount AS
        (
            SELECT 
                winner_id, 
                count(winner_id) AS win 
            FROM 
                Match
            WHERE tournament_id = %s
            GROUP BY winner_id
        ),
        MatchCount AS
        (
            SELECT DISTINCT
                regplyr.player_id,
                COALESCE(MAX(mthwin.round), MAX(mthlss.round)) AS round
            FROM 
                Register AS regplyr
            LEFT JOIN Match mthwin ON regplyr.player_id = mthwin.winner_id
            LEFT JOIN Match mthlss ON regplyr.player_id = mthlss.loser_id
            WHERE regplyr.tournament_id = %s
            GROUP BY regplyr.player_id
        )
        SELECT 
            regplyr.player_id,
            plyr.name,
            COALESCE(wc.win, 0) AS win,
            COALESCE(rnd.round, 0) AS matches
        FROM
            Register AS regplyr
        INNER JOIN Player AS plyr ON regplyr.player_id = plyr.id
        LEFT JOIN WinCount AS wc ON regplyr.player_id = wc.winner_id
        LEFT JOIN MatchCount AS rnd ON regplyr.player_id = rnd.player_id
        ORDER BY wc.win DESC;
    '''

    point.execute(qry, (str(tournament_id), str(tournament_id)))
    res = point.fetchall()

    point.close()
    conn.close()

    return res


def reportMatch(winner, loser, tournament_id = 1):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    point = conn.cursor()

    # Gets the maximum number of matches in a round
    qry1 = '''
        SELECT COUNT(*) FROM Register
        WHERE tournament_id = %s;
    '''
    point.execute(qry1, str(tournament_id))
    total_match = int(point.fetchone()[0])/2

    # Checks the number of matches that have been completed in the round
    qry2 = '''
        SELECT (CASE WHEN round IS NULL THEN 1 END),
            (CASE WHEN count(round) IS NULL THEN 0 END) FROM Match
        WHERE tournament_id = %s
        GROUP BY round
        ORDER BY round DESC;
    '''
    point.execute(qry2, str(tournament_id))
    try:
        count_match = point.fetchone()[1]
        curr_round = point.fetchone()[0]
    except:
        count_match = 0
        curr_round = 1

    curr_match = curr_round if count_match < total_match else curr_round + 1

    # Adds the match record
    qry3 = '''
        INSERT INTO Match(round, tournament_id, winner_id, loser_id)
        VALUES (%s, %s, %s, %s);
    '''
    point.execute(
        qry3, (curr_match, str(tournament_id), str(winner), str(loser)))
    conn.commit()

    point.close()
    conn.close()


def swissPairings(standings):
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
    lst = []

    for i in range(len(standings))[::2]:
        lst.append((
            standings[i][0],
            standings[i][1],
            standings[i+1][0],
            standings[i+1][1]))

    return lst

