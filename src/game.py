from src.config import Config
from src.maze import Maze
from src.player import Player
from src.ghost import Ghost
import time


class Game:
    """Coordinate the Pac-Man game."""

    def __init__(self, config: Config) -> None:
        """Initialize the game."""
        self.config = config
        self.game_over = False
        self.level_won = False
        self.paused = False
        self.paused_time = 0.0
        self.pause_start = 0.0
        self.level = 1
        self.start_level()

    def start_level(self) -> None:
        self.start_time = time.monotonic()
        player_x = self.config.width // 2
        player_y = self.config.height // 2

        self.maze = Maze(
            width=self.config.width,
            height=self.config.height,
            seed=self.config.seed,
            player_start=(player_x, player_y),
        )

        self.player = Player(
            player_x,
            player_y,
            self.config.lives,
        )

        ghost_positions = [
            (0, 0),
            (self.config.width - 1, 0),
            (0, self.config.height - 1),
            (self.config.width - 1, self.config.height - 1),
        ]

        self.ghosts = [Ghost(x, y) for x, y in ghost_positions]

    def collect_items(self) -> None:
        """Collect any item at the player's current position."""
        self.player.collect_pacgum(
            self.maze,
            self.config.points_per_pacgum,
        )

        self.player.collect_super_pacgum(
            self.maze,
            self.config.points_per_super_pacgum,
        )

    def move_player(self, direction: str) -> None:
        """Move the player and collect any item at the new position."""
        moved = self.player.move(self.maze, direction)

        if not moved:
            return

        self.collect_items()

    def handle_collisions(self) -> None:
        """Handle collisions between ghosts and the player."""
        for ghost in self.ghosts:
            result = ghost.handle_collision(self.player)

            if result == "ghost_defeated":
                self.player.score += self.config.points_per_ghost
                ghost.recover()

            elif result == "player_hit":
                if self.player.lives == 0:
                    self.game_over = True
                elif self.player.lives > 0:
                    self.player.reset_position(
                        self.config.width // 2,
                        self.config.height // 2,
                    )

    def check_win(self) -> None:
        """Check whether the player has collected all Pac-Gums."""
        if not self.maze.pacgums and not self.maze.super_pacgums:
            self.level_won = True

    def pause(self) -> None:
        """Pause the game timer."""
        if self.paused:
            return

        self.paused = True
        self.pause_start = time.monotonic()

    def resume(self) -> None:
        """Resume the game timer."""
        if not self.paused:
            return

        self.paused_time += time.monotonic() - self.pause_start
        self.paused = False

    def check_timeout(self) -> None:
        """Check whether the level time limit has expired."""
        if self.paused:
            return

        elapsed = time.monotonic() - self.start_time - self.paused_time
        if elapsed >= self.config.level_max_time:
            self.game_over = True

    def update(self) -> None:
        """Update the game state."""
        if self.game_over:
            return
        self.collect_items()

        for ghost in self.ghosts:
            ghost.chase(
                self.maze,
                self.player.x,
                self.player.y,
            )
        self.handle_collisions()
        self.check_win()
        if not self.level_won:
            self.check_timeout()
