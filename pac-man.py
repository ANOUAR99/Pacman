from src.config import Config
from src.game import Game
from src.highscore import HighScore
# import time

config = Config(width=15, height=11)
high_scores = HighScore("highscores.json")

# high_scores = HighScore("highscores.json")
high_scores.load()
print(high_scores.scores)
game = Game(config)
game.player.score = 3000
game.start_time -= config.level_max_time + 1
game.update()
print("Game over:", game.game_over)
print("Scores:", game.high_scores.scores)
