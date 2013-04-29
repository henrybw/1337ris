#
# 1337ris -- 1337ris.py
# Henry Weiss (a.k.a. Henry Baba-Weiss)
#
# Contains the main execution code for the game. Separated from the rest of
# the source to (a) make it easier for users to run the game, and (b) make
# the main directory less crowded.
#

from src.headers import *

# Initialize and run the game
app = Main()
app.load_resources()
app.run()