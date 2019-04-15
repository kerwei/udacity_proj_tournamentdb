# Project: Tournament Database
This is a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament.
The game tournament will use the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

## REQUIREMENTS
  * Python 3
  * PostgreSQL

## INSTRUCTIONS
1. From the command line interface (CLI), run psql and execute tournament.sql to set up the database and tables used by the module. 
  - > \i tournament.sql
2. Check that the setup is complete and ready by running the packaged unittest
  - > python -m unittest tests/tournament_test.py
3. If everything is set up properly, you should see the following:
  > Ran 8 tests in 0.593s
  >
  > OK
3. To use the module for your own Swiss system tournament, place tournament.py in the root
directory or the imports directory of your project. For further information on the methods provided by the module, please refer to the tournament.py file.

