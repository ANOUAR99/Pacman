from mazegenerator import MazeGenerator


class Maze:
    """Represent a generated Pac-Man maze."""

    def __init__(self, width: int, height: int, seed: int) -> None:
        """Generate a maze with the given dimensions and seed."""
        generator = MazeGenerator(size=(width, height), seed=seed)
        self.grid = generator.maze
        self.entry = generator.maze_entry
        self.exit = generator.maze_exit
        self.shortest_path = generator.shortest_path

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
