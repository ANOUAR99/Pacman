import json


class HighScore:
    """Manage persistent Pac-Man high scores."""

    def __init__(self, filename: str) -> None:
        """Initialize an empty high-score list."""
        self.scores: list[int] = []
        self.filename = filename

    def add_score(self, score: int) -> None:
        """Add a score and keep only the top ten scores."""
        self.scores.append(score)
        self.scores.sort(reverse=True)
        if len(self.scores) > 10:
            self.scores.pop()

    def load(self) -> None:
        """Load high scores from the JSON file."""
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                if isinstance(data, list) and all(
                    isinstance(score, int) for score in data
                ):
                    self.scores = data
                else:
                    self.scores = []
        except (FileNotFoundError, json.JSONDecodeError):
            self.scores = []

    def save(self) -> None:
        """Dump high scores to the JSON file."""
        with open(self.filename, "w") as file:
            json.dump(self.scores, file)
