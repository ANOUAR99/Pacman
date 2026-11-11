
import time
from src.config import Config
from src.game import Game
from src.player import Player
from src.ghost import Ghost


def test_update_both_moving():
    print("\nTEST: Both moving during Game.update()")

    game = Game.__new__(Game)

    game.config = Config(
        width=7,
        height=5,
        lives=3,
        seed=42,
    )

    # Controlled player and ghost positions
    game.player = Player(4, 3, 3)
    game.player.direction = "E"

    ghost = Ghost(6, 3)
    game.ghosts = [ghost]

    # Fake maze: every movement is allowed
    class FakeMaze:
        pacgums = set()
        super_pacgums = set()

        def can_move(self, x, y, direction):
            return True

    game.maze = FakeMaze()

    # Configure update state
    game.game_over = False
    game.level_won = False
    game.player_eaten = False
    game.queued_direction = None
    game.frightened_start = None
    game.frightened_duration = 10
    game.ghost_move_delay = 0.25
    game.ghost_detect_range = 5
    game.ghost_respawn_delay = 5
    game.last_ghost_move = time.monotonic() - 1
    game.start_time = time.monotonic()
    game.paused_time = 0
    game.paused = False
    game.high_scores = None
    game.score_saved = False

    # Prevent level transition and timeout from affecting this test
    game.check_win = lambda: None
    game.check_timeout = lambda: None

    print("Initial player:", (game.player.x, game.player.y))
    print("Initial ghost:", (ghost.x, ghost.y))

    game.update()

    print("Final player:", (game.player.x, game.player.y))
    print("Final ghost:", (ghost.x, ghost.y))
    print("Lives:", game.player.lives)

    assert game.player.lives == 2, "Expected a collision!"
    print("\nPASSED: Front collision detected")


if __name__ == "__main__":
    test_update_both_moving()
