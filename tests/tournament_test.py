# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.
import unittest
import tournament

class TestPlayerCount(unittest.TestCase):
    player_count = -1

    def setUp(self):
        tournament.deleteMatches()
        tournament.deletePlayers()
        self.player_count = tournament.countPlayers()

    def zero_initState(self):
        """
        1. countPlayers() returns 0 after initial deletePlayers() execution
        """
        self.assertEqual(self.player_count, 0)

    def test_registerPlayer(self):
        """
        2. countPlayers() returns 1 after one player is registered
           countPlayers() returns 2 after two players are registered
        """
        tournament.registerPlayer("Chandra Nalaar")
        self.player_count = tournament.countPlayers()
        self.assertEqual(self.player_count, 1)

        tournament.registerPlayer("Jace Beleren")
        self.player_count = tournament.countPlayers()
        self.assertEqual(self.player_count, 2)

    def test_resetPlayer(self):
        """
        3. countPlayers() returns zero after registered players are deleted
        """
        self.player_count = tournament.countPlayers()
        self.assertEqual(self.player_count, 0)


class TestStandings(unittest.TestCase):
    standings = []

    def setUp(self):
        tournament.deleteMatches()
        tournament.deletePlayers()
        tournament.registerPlayer("Melpomene Murray")
        tournament.registerPlayer("Randy Schwartz")
        self.standings = tournament.playerStandings()

    def test_hasStanding(self):
        """
        4. Only registered players appear in the standings
        """
        self.assertEqual(len(self.standings), 2)

    def test_zeroMatches(self):
        """
        5. Newly registered players appear in the standings with no matches
        """
        [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = self.standings
        self.assertTrue(all([matches1 == 0, matches2 == 0, wins1 == 0, wins2 == 0]))
        self.assertEqual(set([name1, name2]), set(["Melpomene Murray", "Randy Schwartz"]))

    def test_refhasStanding(self):
        """
        5.1. (Refactored) Newly registered players appear in the standings with no matches
        """
        self.standings = tournament.refplayerStandings()
        [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = self.standings
        self.assertTrue(all([matches1 == 0, matches2 == 0, wins1 == 0, wins2 == 0]))
        self.assertEqual(set([name1, name2]), set(["Melpomene Murray", "Randy Schwartz"]))


class TestMatchUpdates(unittest.TestCase):
    standings = []
    id1 = -1
    id2 = -1
    id3 = -1
    id4 = -1

    def setUp(self):
        tournament.deleteMatches()
        tournament.deletePlayers()
        tournament.registerPlayer("Bruno Walton")
        tournament.registerPlayer("Boots O'Neal")
        tournament.registerPlayer("Cathy Burton")
        tournament.registerPlayer("Diane Grant")
        self.standings = tournament.playerStandings()

        [self.id1, self.id2, self.id3, self.id4] = [row[0] for row in self.standings]
        tournament.reportMatch(self.id1, self.id2)
        tournament.reportMatch(self.id3, self.id4)
        self.standings = tournament.playerStandings()

    def test_updateMatch(self):
        """
        6. After a match, players have updated standings
        """
        # One match record for each player
        match = [r[3] for r in self.standings]
        self.assertTrue(all([m == 1 for m in match]))
        # Each match winner should have one win recorded
        winners = [r[2] for r in self.standings if r[0] in (self.id1, self.id3)]
        self.assertTrue(all([w == 1 for w in winners]))
        # Each match loser should have zero wins recorded
        losers = [r[2] for r in self.standings if r[0] in (self.id2, self.id4)]
        self.assertTrue(all([l == 0 for l in losers]))

    def test_deleteMatch(self):
        """
        7. After match deletion, player standings are properly reset
        """
        tournament.deleteMatches()
        self.standings = tournament.playerStandings()
        # Match deletion should not change number of players in standings
        self.assertEqual(len(self.standings), 4)
        # After deleting matches, players should have zero matches recorded
        match = [r[3] for r in self.standings]
        self.assertTrue(all([m == 0 for m in match]))
        # After deleting matches, players should have zero wins recorded
        winners = [r[2] for r in self.standings]
        self.assertTrue(all([w == 0 for w in winners]))


class TestPairings(unittest.TestCase):
    standings = []
    pairings = []
    id1 = -1
    id2 = -1
    id3 = -1
    id4 = -1
    id5 = -1
    id6 = -1
    id7 = -1
    id8 = -1

    def setUp(self):
        tournament.deleteMatches()
        tournament.deletePlayers()
        tournament.registerPlayer("Twilight Sparkle")
        tournament.registerPlayer("Fluttershy")
        tournament.registerPlayer("Applejack")
        tournament.registerPlayer("Pinkie Pie")
        tournament.registerPlayer("Rarity")
        tournament.registerPlayer("Rainbow Dash")
        tournament.registerPlayer("Princess Celestia")
        tournament.registerPlayer("Princess Luna")
        self.standings = tournament.playerStandings()
        [self.id1, self.id2, self.id3, self.id4, self.id5, self.id6, self.id7, self.id8] = [row[0] for row in self.standings]
        self.pairings = tournament.swissPairings(tournament.playerStandings())

        tournament.reportMatch(self.id1, self.id2)
        tournament.reportMatch(self.id3, self.id4)
        tournament.reportMatch(self.id5, self.id6)
        tournament.reportMatch(self.id7, self.id8)
        self.pairings = tournament.swissPairings(tournament.playerStandings())


    def test_fourPairs(self):
        """
        8. For eight players, swissPairings should return 4 pairs
        """
        self.assertEqual(len(self.pairings), 4)

    def test_winPair(self):
        """
        9. After one match, players with one win should be paired
        """
        [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = self.pairings
        possible_pairs = set([frozenset([self.id1, self.id3]), frozenset([self.id1, self.id5]),
                            frozenset([self.id1, self.id7]), frozenset([self.id3, self.id5]),
                            frozenset([self.id3, self.id7]), frozenset([self.id5, self.id7]),
                            frozenset([self.id2, self.id4]), frozenset([self.id2, self.id6]),
                            frozenset([self.id2, self.id8]), frozenset([self.id4, self.id6]),
                            frozenset([self.id4, self.id8]), frozenset([self.id6, self.id8])
                            ])
        actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), frozenset([pid5, pid6]), frozenset([pid7, pid8])])
        self.assertEqual(len(actual_pairs.intersection(possible_pairs)), 4)