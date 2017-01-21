Project: Tournament Database
This is a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament.
The game tournament will use the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

REQUIREMENTS
1. Python 2 and above
2. PostgreSQL

INSTRUCTIONS
1. From the command line interface (CLI), run psql and execute tournament.sql to set up the database and tables used by the module. Type '\i tournament.sql' into the CLI and hit enter.
2. To test the module, type 'python tournament_test.py tournament.py' into the CLI and hit enter. If the setup is successful, the test script should return "Success! All tests pass!".
3. To use the module for your own Swiss system tournament, simply import the tournament module into your application. For further information on the methods provided by the module, please refer to the tournament.py file.

