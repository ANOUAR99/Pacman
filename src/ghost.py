from src.maze import Maze
from src.player import Player
import time
from collections import deque
import random


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
        self.eaten_time = None

    def collides_with(self, player_x: int, player_y: int) -> bool:
        """Return True if the ghost occupies the player's position."""
        return self.x == player_x and self.y == player_y

    def handle_collision(self, player: Player) -> str:
        """Handle a collision with the player."""
        if not self.collides_with(player.x, player.y):
            return "none"

        if self.frightened:
            self.eaten_time = time.monotonic()
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

    def find_target(
        self, maze: Maze, target_x: int, target_y: int, max_range: int
    ) -> str | None:
        """Return the first move toward the target if it is within
        max_range steps along the maze, otherwise None."""
        DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        start = (self.x, self.y)
        target = (target_x, target_y)
        if start == target:
            return None

        first_move: dict[tuple[int, int], str | None] = {start: None}
        depth = {start: 0}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            if depth[(x, y)] >= max_range:
                continue
            for direction, (dx, dy) in DIRECTIONS.items():
                if not maze.can_move(x, y, direction):
                    continue
                nxt = (x + dx, y + dy)
                if nxt in first_move:
                    continue
                first_move[nxt] = first_move[(x, y)] or direction
                depth[nxt] = depth[(x, y)] + 1
                if nxt == target:
                    return first_move[nxt]
                queue.append(nxt)
        return None

    def chase(
        self, maze: Maze, target_x: int, target_y: int, max_range: int
    ) -> bool:
        """Chase the target if detected, otherwise wander."""
        direction = self.find_target(maze, target_x, target_y, max_range)
        if direction is not None:
            return self.move(maze, direction)
        return self.wander(maze)

    def wander(self, maze: Maze) -> bool:
        """Move randomly, avoiding U-turns unless in a dead end."""
        DIRECTIONS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
        OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
        options = [d for d in DIRECTIONS if maze.can_move(self.x, self.y, d)]
        forward = [d for d in options if d != OPPOSITE[self.direction]]
        choices = forward or options
        if not choices:
            return False
        return self.move(maze, random.choice(choices))
