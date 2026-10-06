from src.ghost import Ghost
from src.game import Game
from src.config import Config
from src.highscore import HighScore
import time

ghost = Ghost(2, 3)
config = Config()
score = HighScore(filename="highscores.json")
game = Game(config)

# Pretend Level 1 has already been running for a long time.
game.start_time = time.monotonic() - 1000

highscores = HighScore("test_highscores.json")

highscores.add_score("Alice", 500)
highscores.add_score("Bob", 900)
highscores.add_score("Anouar", 750)

highscores.save()

print("Saved:", highscores.scores)

highscores.scores = []
highscores.load()

for score in highscores.scores:
    print(score.name, score.score)