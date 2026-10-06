import json

from dataclasses import dataclass


@dataclass
class Score:
    """Represent a highscore entry."""

    name: str
    score: int


class HighScore:
    """Manage persistent Pac-Man high scores."""

    def __init__(self, filename: str) -> None:
        """Initialize an empty high-score list."""
        self.scores: list[Score] = []
        self.filename = filename

    def add_score(self, name: str, score: int) -> None:
        """Add a score and keep only the top ten scores."""
        scr = Score(name, score)
        self.scores.append(scr)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        if len(self.scores) > 10:
            self.scores.pop()

    def load(self) -> None:
        """Load high scores from the JSON file."""
        try:
            loaded_scores = []

            with open(self.filename, "r") as file:
                data = json.load(file)

                if not isinstance(data, list):
                    self.scores = []
                    return

                for entry in data:
                    if not isinstance(entry, dict):
                        self.scores = []
                        return

                    if "name" not in entry or "score" not in entry:
                        self.scores = []
                        return

                    name = entry["name"]
                    score = entry["score"]

                    if not isinstance(name, str):
                        self.scores = []
                        return

                    if not isinstance(score, int) or score < 0:
                        self.scores = []
                        return

                    if len(name) > 10 or not name.replace(" ", "").isalnum():
                        self.scores = []
                        return
                    loaded_scores.sort(key=lambda x: x.score, reverse=True)
                    if len(loaded_scores) > 10:
                        loaded_scores = loaded_scores[:10]
                    loaded_scores.append(Score(name, score))

                self.scores = loaded_scores

        except (FileNotFoundError, json.JSONDecodeError):
            self.scores = []

    def save(self) -> None:
        """Dump high scores to the JSON file."""
        json_scores = []
        for x in self.scores:
            json_scores.append({"name": x.name, "score": x.score})
        with open(self.filename, "w") as file:
            json.dump(json_scores, file)
