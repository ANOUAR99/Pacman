*This project has been created as part of the 42 curriculum by [melmoara] and [anbenaay].*

## Description
This project is a complete, playable recreation of the classic arcade game Pac-Man, built in Python 3.10+ using `pygame`. The goal of this project is to implement a robust 2D game engine utilizing Object-Oriented Programming, a strict Finite State Machine (FSM), and a Model-View-Controller (MVC) architecture. It features dynamic maze generation, autonomous ghost AI, and a persistent highscore system.

## Instructions
**Prerequisites:**
Ensure you have Python 3.10+ installed on your system.

**Installation & Execution:**
We have provided a strict `Makefile` to handle dependencies and execution automatically.
1. Clone the repository and navigate to the root directory.
2. To install dependencies and run the game, execute:
   ```bash
   make run
   ```
3. To run the static typing and style linters (Flake8 and Mypy):
   ```bash
   make lint
   ```
4. To cleanly remove the virtual environment and caches:
   ```bash
   make fclean
   ```

## Resources
* Pygame Official Documentation: https://www.pygame.org/docs/
* PEP 8 Style Guide: https://peps.python.org/pep-0008/
* **AI Usage:** During this project, AI was utilized strictly as a mentoring tool to understand architectural concepts. Specifically, AI was prompted to explain Pygame `Rect` geometry, assist in designing the Finite State Machine routing in `ui.py`, and explain the mathematical logic behind non-blocking modulo clocks (`pygame.time.get_ticks()`). No code was blindly copied; all AI-assisted logic was manually integrated and refactored to fit our MVC pipeline.

## Configuration
The game is initialized via a `config.json` file passed as a command-line argument. The configuration file supports comments (lines starting with `#`).
* **Structure:** The file expects keys such as `highscore_filename`, `lives`, `pacgum`, `points_per_pacgum`, `points_per_super_pacgum`, `points_per_ghost`, `seed`, and `level_max_time`.
* **Defaults:** If the file is missing, contains invalid values, or is missing keys, the engine clamps to safe defaults (e.g., `lives: 3`, `level_max_time: 90`) and logs a clear warning without crashing.

## Highscore
The game features a persistent highscore system that tracks the top 10 players. 
* **Implementation:** Scores are stored in a local `.json` file defined by the `highscore_filename` configuration key. 
* **Justification:** JSON was chosen for persistent storage because it is native to Python's standard library, human-readable for debugging, and easily parsed. The system gracefully handles missing or corrupted highscore files by generating a fresh, empty leaderboard upon boot.

## Maze Generation
The mazes are generated using the assigned `A-Maze-ing` package provided by another group. 
* Our loader integrates their package as a black box without modifying their source code. 
* We pass `PERFECT = False` to their generator to ensure the maze produces Pac-Man-compatible loops and corridors rather than a strict single-path labyrinth. The first level uses the seed provided in the config, while subsequent levels use random seeds.

## Implementation
The engine runs on a strict 60 FPS loop, heavily relying on Pygame's hardware clock for frame-independent logic. We utilized Pygame `Surface` caching to optimize memory (rendering static text only once during initialization) and `Rect` anchoring to dynamically scale the UI to the display resolution. Error handling uses `try-except` blocks around file operations to guarantee the game never crashes with a Python traceback.

## General Software Architecture
To prevent circular dependencies, the codebase is strictly separated into a Model-View-Controller (MVC) pattern:
* **The Model (`game.py`):** The isolated backend. It handles matrix calculations, grid collision mathematics, and Ghost AI pathfinding. It has no knowledge of Pygame or rendering.
* **The View & Controller (`ui.py`):** The Pygame frontend interface. It captures hardware inputs (keyboard/mouse) via the OS event pump, routes them through a Finite State Machine (`MAIN_MENU`, `PLAYING`, `PAUSED`), modifies the Model's state, and rasterizes the screen based on the Model's data variables.

## Project Management
This project was managed using an agile approach. 
* We tracked our progress, milestones, and assigned tasks using <YOUR_TOOL_HERE (e.g., a Trello Kanban board / GitHub Projects)>.
* A detailed breakdown of our timeline, risk analysis, and acceptance testing plan can be found in our dedicated project management directory: [Link to your internal directory, e.g., `./project_management/`].