from src.maze import Maze
from src.player import Player


class Ghost:
    """Represent a Pac-Man ghost."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize the ghost."""
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.direction = "N"
        self.frightened = False

    def collides_with(self, player_x: int, player_y: int) -> bool:
        """Return True if the ghost occupies the player's position."""
        return self.x == player_x and self.y == player_y

    def handle_collision(self, player: Player) -> str:
        """Handle a collision with the player."""
        if not self.collides_with(player.x, player.y):
            return "none"

        if self.frightened:
            return "ghost_defeated"

        player.lose_life()
        return "player_hit"

    def move(self, maze: Maze, direction: str) -> bool:
        """Move the ghost if the destination is not blocked."""
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

    def frighten(self) -> None:
        """Put the ghost into frightened mode."""
        self.frightened = True

    def recover(self) -> None:
        """Return the ghost to its normal state."""
        self.frightened = False

    def reset_position(self) -> None:
        """Return the ghost to its starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.direction = "N"

    def chase(self, maze: Maze, target_x: int, target_y: int) -> bool:
        """Move one step toward the target position."""
        directions = ["N", "S", "E", "W"]

        best_direction = None
        best_distance = float("inf")

        for direction in directions:
            if not maze.can_move(self.x, self.y, direction):
                continue

            new_x = self.x
            new_y = self.y

            if direction == "N":
                new_y -= 1
            elif direction == "S":
                new_y += 1
            elif direction == "E":
                new_x += 1
            elif direction == "W":
                new_x -= 1

            distance = abs(new_x - target_x) + abs(new_y - target_y)

            if distance < best_distance:
                best_distance = distance
                best_direction = direction

        if best_direction is None:
            return False

        return self.move(maze, best_direction)
