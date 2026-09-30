from src.maze import Maze


class Player:
    """Represent the Pac-Man player."""

    def __init__(
        self,
        x: int,
        y: int,
        lives: int,
    ) -> None:
        """Initialize the player."""
        self.x = x
        self.y = y
        self.lives = lives
        self.score = 0
        self.direction = "N"

    def move(self, maze: Maze, direction: str) -> bool:
        """Move the player if the destination is not blocked."""
        if not maze.can_move(self.x, self.y, direction):
            return False

        if direction == "N":
            self.y -= 1
        elif direction == "S":
            self.y += 1
        elif direction == "E":
            self.x += 1
        elif direction == "W":
            self.x -= 1

        self.direction = direction
        return True
