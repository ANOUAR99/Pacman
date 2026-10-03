from src.config import Config
from src.game import Game
from src.highscore import HighScore
# import time

config = Config(width=15, height=11)
high_scores = HighScore("highscores.json")

# high_scores = HighScore("highscores.json")
high_scores.load()
print(high_scores.scores)