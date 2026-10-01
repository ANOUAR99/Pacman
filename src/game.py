from src.config import Config
from src.maze import Maze
from src.player import Player
from src.ghost import Ghost


class Game:
    """Coordinate the Pac-Man game."""

    def __init__(self, config: Config) -> None:
        """Initialize the game."""
        self.config = config

        player_x = config.width // 2
        player_y = config.height // 2

        self.maze = Maze(
            width=config.width,
            height=config.height,
            seed=config.seed,
            player_start=(player_x, player_y),
        )

        self.player = Player(
            player_x,
            player_y,
            config.lives,
        )

        ghost_positions = [
            (0, 0),
            (config.width - 1, 0),
            (0, config.height - 1),
            (config.width - 1, config.height - 1),
        ]

        self.ghosts = [
            Ghost(x, y)
            for x, y in ghost_positions
        ]

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

    def update(self) -> None:
        """Update the game state."""
        self.collect_items()

        for ghost in self.ghosts:
            ghost.chase(
                self.maze,
                self.player.x,
                self.player.y,
            )
