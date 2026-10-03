from src.config import Config
from src.maze import Maze
from src.player import Player
from src.ghost import Ghost
from src.highscore import HighScore
import time


class Game:
    """Coordinate the Pac-Man game."""

    def __init__(self, config: Config) -> None:
        """Initialize the game."""
        self.config = config
        self.game_over = False
        self.level_won = False
        self.level = 1
        self.frightened_start = None
        self.frightened_duration = 10
        self.high_scores = HighScore(config.highscore_filename)
        self.high_scores.load()
        self.start_level(self.config.lives)

    def start_level(self, lives: int, score: int = 0) -> None:
        """Initialize the current level."""
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
            lives,
        )
        self.player.score = score

        ghost_positions = [
            (0, 0),
            (self.config.width - 1, 0),
            (0, self.config.height - 1),
            (self.config.width - 1, self.config.height - 1),
        ]

        self.ghosts = [Ghost(x, y) for x, y in ghost_positions]
        self.start_time = time.monotonic()
        self.paused = False
        self.paused_time = 0.0
        self.pause_start = 0.0

    def next_level(self) -> None:
        """Start the next level while preserving lives and score."""
        self.level += 1
        self.level_won = False

        self.start_level(
            self.player.lives,
            self.player.score,
        )

    def collect_items(self) -> None:
        """Collect any item at the player's current position."""
        self.player.collect_pacgum(
            self.maze,
            self.config.points_per_pacgum,
        )

        super_collected = self.player.collect_super_pacgum(
            self.maze,
            self.config.points_per_super_pacgum,
        )

        if super_collected:
            for ghost in self.ghosts:
                ghost.frighten()
            self.frightened_start = time.monotonic()

    def move_player(self, direction: str) -> None:
        """Move the player and collect any item at the new position."""
        moved = self.player.move(self.maze, direction)

        if not moved:
            return

        self.collect_items()

    def handle_collisions(self) -> None:
        """Handle collisions between ghosts and the player."""
        player_hit = False

        for ghost in self.ghosts:
            result = ghost.handle_collision(self.player)

            if result == "ghost_defeated":
                self.player.score += self.config.points_per_ghost
                ghost.reset_position()
                ghost.recover()

            elif result == "player_hit":
                player_hit = True

        if player_hit:
            if self.player.lives == 0:
                self.game_over = True
            else:
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
            if not self.score_saved:
                self.high_scores.add_score(self.player.score)
                self.high_scores.save()
                self.score_saved = True
            return
        self.collect_items()
        if self.frightened_start is not None:
            elapsed = time.monotonic() - self.frightened_start
            if elapsed >= self.frightened_duration:
                for ghost in self.ghosts:
                    ghost.recover()
                self.frightened_start = None

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
        if self.game_over and not self.score_saved:
            self.high_scores.add_score(self.player.score)
            self.high_scores.save()
            self.score_saved = True
