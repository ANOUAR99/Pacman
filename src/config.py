import json
from pydantic import BaseModel, ValidationError, Field


class Config(BaseModel):
    """Store and validate Pac-Man configuration."""

    highscore_filename: str = Field(default="highscores.json")
    width: int = Field(default=7, ge=5)
    height: int = Field(default=5, ge=5)
    lives: int = Field(default=3, ge=1)
    pacgum: int = Field(default=42, ge=0)
    points_per_pacgum: int = Field(default=10, ge=1)
    points_per_super_pacgum: int = Field(default=50, ge=1)
    points_per_ghost: int = Field(default=200, ge=1)
    seed: int = Field(default=42, ge=0)
    level_max_time: int = Field(default=90, ge=1)


def read_config(path: str) -> str:
    """Read the configuration file and return its contents."""
    try:
        with open(path) as file:
            return file.read()
    except (FileNotFoundError, OSError) as error:
        print(f"Could not read configuration file: {error}")
        return ""


def remove_comments(text: str) -> str:
    """Remove comments from configuration text."""
    parsed_text = ""
    lines = text.splitlines()
    for line in lines:
        if line.lstrip().startswith("#"):
            continue
        parsed_text += line
    return parsed_text


def parse_config(config: str) -> Config | None:
    """Parse and validate the configuration."""
    try:
        conf = json.loads(config)
    except json.JSONDecodeError as error:
        print(f"Invalid configuration format: {error}")
        return Config()
    try:
        return Config(**conf)
    except ValidationError as error:
        for error_info in error.errors():
            field = error_info["loc"][0]
            default = Config.model_fields[field].default

            print(f"Invalid field: {field}")
            print(f"Using default: {default}")

            conf[field] = default

    return Config(**conf)


if __name__ == "__main__":
    text = read_config("config.json")
    cleaned = remove_comments(text)
    config = parse_config(cleaned)

    print(config)
