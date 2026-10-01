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

    def collect_pacgum(self, maze: Maze, points: int) -> bool:
        """Collect a Pac-Gum at the player's current position."""
        position = (self.x, self.y)

        if position not in maze.pacgums:
            return False

        maze.pacgums.remove(position)
        self.score += points
        return True

    def collect_super_pacgum(self, maze: Maze, points: int) -> bool:
        """Collect a super Pac-Gum at the player's current position."""
        position = (self.x, self.y)

        if position not in maze.super_pacgums:
            return False

        maze.super_pacgums.remove(position)
        self.score += points
        return True

    def lose_life(self) -> bool:
        """Remove one life and return whether the player is still alive."""
        if self.lives > 0:
            self.lives -= 1
        return self.lives > 0

    def reset_position(self, x: int, y: int) -> None:
        """Reset the player's position after losing a life."""
        self.x = x
        self.y = y
        self.direction = "N"
