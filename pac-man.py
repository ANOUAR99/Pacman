from src.config import Config
from src.game import Game

config = Config(width=15, height=11)
game = Game(config)

print("Start:", game.player.x, game.player.y)
print("Score:", game.player.score)

game.move_player("E")

print("After:", game.player.x, game.player.y)
print("Score:", game.player.score)

print("Before:")

for i, ghost in enumerate(game.ghosts):
    print(i + 1, ghost.x, ghost.y)

game.update()

print("After:")

for i, ghost in enumerate(game.ghosts):
    print(i + 1, ghost.x, ghost.y)
