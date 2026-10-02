from src.config import Config
from src.game import Game
import time

config = Config(width=15, height=11)
game = Game(config)
game.config.level_max_time = 1

print("Paused:", game.paused)

time.sleep(0.5)
game.update()

print("Game over after 0.5s:", game.game_over)

game.pause()
time.sleep(1.0)
game.update()

print("Game over while paused:", game.game_over)

game.resume()
time.sleep(0.6)
game.update()

print("Game over after resume:", game.game_over)
