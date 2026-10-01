from mazegenerator import MazeGenerator


class Maze:
    """Represent a generated Pac-Man maze."""

    def __init__(
        self,
        width: int,
        height: int,
        seed: int,
        player_start: tuple[int, int],
    ) -> None:
        """Generate a maze with the given dimensions and seed."""
        generator = MazeGenerator(size=(width, height), seed=seed)
        self.grid = generator.maze
        self.entry = generator.maze_entry
        self.exit = generator.maze_exit
        self.shortest_path = generator.shortest_path
        self.player_start = player_start
        self.pacgums: set[tuple[int, int]] = set()
        self.super_pacgums: set[tuple[int, int]] = set()
        self._place_pacgums()
        self._place_super_pacgums()

    def _place_pacgums(self) -> None:
        """Place Pac-Gums on walkable cells."""
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                position = (x, y)

                if cell == 15:
                    continue

                if position == self.entry:
                    continue

                if position == self.exit:
                    continue

                if position == self.player_start:
                    continue

                self.pacgums.add(position)

    def _place_super_pacgums(self) -> None:
        """Place four Super Pac-Gums in the maze corners."""
        width = len(self.grid[0])
        height = len(self.grid)

        corners = [
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        ]

        for position in corners:
            self.pacgums.discard(position)
            self.super_pacgums.add(position)

    def is_wall(self, x: int, y: int, direction: str) -> bool:
        """Return True if the cell has a wall in the given direction."""
        wall_codes = {
            "N": 1,
            "E": 2,
            "S": 4,
            "W": 8,
        }

        return bool(self.grid[y][x] & wall_codes[direction])

    def can_move(self, x: int, y: int, direction: str) -> bool:
        """Return True if movement is possible in the given direction."""
        return not self.is_wall(x, y, direction)


if __name__ == "__main__":
    maze = Maze(20, 15, 42)
    print(maze.grid)
    print("Entry:", maze.entry)
    print("Exit:", maze.exit)
    print("Path:", maze.shortest_path)
    print("Can move North:", maze.can_move(0, 0, "N"))
    print("Can move East:", maze.can_move(0, 0, "E"))
