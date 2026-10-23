import math
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import pygame
from src.config import parse_config, read_config, remove_comments
from src.game import Game
from src.highscore import HighScore


class PacmanUI:
    """
    Manages the graphical View layer and Finite State Machine for Pac-Man.

    This class handles all Pygame rendering, event listening, and UI state
    transitions (MainMenu -> Playing -> GameOver). It acts as the frontend
    to the headless `Game` backend model, decoupling logic from rendering.
    """

    def __init__(self) -> None:
        """
        Initializes the Pygame display, font assets, and memory allocations.

        Calculates dynamic screen geometry for fullscreen rendering, scales
        sprite assets relative to the monitor's resolution, and pre-allocates
        the sliding window buffers for cheat codes.
        """
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN
        )
        screen_info = pygame.display.Info()
        self.hud_reserved_space: int = 80
        self.screen_width: int = screen_info.current_w
        self.screen_height: int = screen_info.current_h
        pygame.display.set_caption("42 Pac-Man")
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # The heart of the State Machine
        self.state: str = "MAIN_MENU"

        # Game Model & Dynamic Methods
        self.game: Optional[Game] = None
        self.real_add_score: Optional[Callable] = None

        pygame.font.init()
        self.input_text: str = ""
        self.menu_options: List[str] = [
            "Start Game",
            "View Highscores",
            "Instructions",
            "Exit",
        ]
        self.selected_index: int = 0
        self.last_engine_tick: int = 0
        self.tick_delay: int = 170

        # Memory allocations for Lerp and Input
        self.prev_player_pos: Tuple[float, float] = (0.0, 0.0)
        self.prev_ghost_pos: Dict[int, Tuple[float, float]] = {}
        self.active_direction: Optional[str] = "E"
        self.queued_direction: Optional[str] = None
        self.secret_code: List[int] = [
            pygame.K_UP,
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_DOWN,
        ]
        self.input_buffer: List[int] = []

        # Assets & Paths
        project_root: Path = Path(__file__).parent.parent
        colors: List[str] = ["red", "pink", "cyan", "orange"]
        open_path: Path = project_root / "src" / "assets" / "pacman.png"
        closed_path: Path = (
            project_root / "src" / "assets" / "pacman_closed.png"
        )
        f_ghost_path: Path = project_root / "src" / "assets" / "f_ghost.png"
        font_path: Path = project_root / "src" / "assets" / "ARCADE_N.TTF"
        eyes_path: Path = project_root / "src" / "assets" / "eyes.png"
        w_ghost_path: Path = project_root / "src" / "assets" / "w_ghost.png"

        # Fonts
        self.main_size: int = min(40, max(16, self.screen_width // 60))
        self.small_size: int = min(20, max(10, self.screen_width // 90))
        self.font: pygame.font.Font = pygame.font.Font(
            str(font_path), self.main_size
        )
        self.small_font: pygame.font.Font = pygame.font.Font(
            str(font_path), self.small_size
        )

        # Config & Grid Math
        if len(sys.argv) < 2:
            print("Usage: python3 ui.py <config.json>")
            sys.exit(1)
        config_path: str = sys.argv[1]
        raw_text: str = read_config(config_path)
        clean_text: str = remove_comments(raw_text)
        self.config = parse_config(clean_text)

        max_width_cell = self.screen_width // self.config.width
        max_height_cell = (
            self.screen_height - self.hud_reserved_space
        ) // self.config.height
        self.cell_size: int = min(max_width_cell, max_height_cell)

        maze_pixel_width = self.config.width * self.cell_size
        maze_pixel_height = self.config.height * self.cell_size

        self.left_offset: int = (self.screen_width - maze_pixel_width) // 2
        self.top_offset: int = (self.screen_height - maze_pixel_height) // 2
        if self.top_offset < self.hud_reserved_space:
            self.top_offset = self.hud_reserved_space

        # Image Loading & Scaling
        self.ghost_normal_imgs: List[pygame.Surface] = []
        for color in colors:
            path = project_root / "src" / "assets" / f"{color}_ghost.png"
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
            self.ghost_normal_imgs.append(img)

        self.w_ghost_img: pygame.Surface = pygame.transform.scale(
            pygame.image.load(str(w_ghost_path)).convert_alpha(),
            (self.cell_size, self.cell_size),
        )
        self.eyes_img: pygame.Surface = pygame.transform.scale(
            pygame.image.load(str(eyes_path)).convert_alpha(),
            (self.cell_size, self.cell_size),
        )
        self.f_ghost_img: pygame.Surface = pygame.transform.scale(
            pygame.image.load(str(f_ghost_path)).convert_alpha(),
            (self.cell_size, self.cell_size),
        )
        self.pac_open: pygame.Surface = pygame.transform.scale(
            pygame.image.load(str(open_path)).convert_alpha(),
            (self.cell_size, self.cell_size),
        )
        self.pac_closed: pygame.Surface = pygame.transform.scale(
            pygame.image.load(str(closed_path)).convert_alpha(),
            (self.cell_size, self.cell_size),
        )

    def handle_events(self) -> None:
        """
        Intercepts OS-level hardware inputs and routes them based on the FSM.
        Captures keyboard events and updates internal UI buffers, state strngs,
        or triggers backend Model state changes (like pausing or god mode).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                if self.state == "MAIN_MENU":
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(
                            self.menu_options
                        )
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(
                            self.menu_options
                        )
                    elif event.key == pygame.K_RETURN:
                        if self.selected_index == 0:
                            self.state = "PLAYING"
                            self.game = Game(self.config)
                            if hasattr(self.game, "high_scores"):
                                self.real_add_score = getattr(
                                    self.game.high_scores, "add_score"
                                )
                                # Overwrite with a dummy lambda
                                setattr(
                                    self.game.high_scores,
                                    "add_score",
                                    lambda *args, **kwargs: None,
                                )
                        elif self.selected_index == 1:
                            self.state = "HIGHSCORES"
                        elif self.selected_index == 2:
                            self.state = "INSTRUCTIONS"
                        elif self.selected_index == 3:
                            self.quit_game()

                elif self.state == "PLAYING" and self.game is not None:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"
                        self.game.pause()
                    elif event.key in (pygame.K_w, pygame.K_UP):
                        self.queued_direction = "N"
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.queued_direction = "S"
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.queued_direction = "W"
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.queued_direction = "E"

                    self.input_buffer.append(event.key)
                    if len(self.input_buffer) > len(self.secret_code):
                        self.input_buffer.pop(0)

                    if self.input_buffer == self.secret_code:
                        is_god = not getattr(
                            self.game.player, "god_mode", False
                        )
                        setattr(self.game.player, "god_mode", is_god)
                        print(f"[SYSTEM] GOD MODE: {is_god}")
                        self.input_buffer.clear()

                elif self.state == "PAUSED" and self.game is not None:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        self.game.resume()

                elif self.state in ["GAME_OVER", "VICTORY"]:
                    if event.key == pygame.K_RETURN:
                        self.state = "MAIN_MENU"
                        if self.real_add_score and self.game:
                            self.real_add_score(
                                self.input_text, self.game.player.score
                            )
                            if hasattr(self.game, "high_scores"):
                                self.game.high_scores.save()
                        self.input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 10:
                            if event.unicode.isalnum() or event.unicode == " ":
                                self.input_text += event.unicode

                elif self.state in ["HIGHSCORES", "INSTRUCTIONS"]:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MAIN_MENU"

    def render(self) -> None:
        """
        Paints the current frame to the Pygame display surface.

        Executes dynamic geometric anchoring for HUD elements and applies
        Linear Interpolation (Lerp) to smoothly draw the discrete backend
        engine coordinates across continuous 60 FPS frames.
        """
        self.screen.fill((0, 0, 0))

        if self.state == "MAIN_MENU":
            title = self.font.render("42 PAC-MAN", True, (255, 255, 255))
            title_rect = title.get_rect(
                center=(self.screen_width // 2, self.screen_height // 4)
            )
            self.screen.blit(title, title_rect)
            for i, option in enumerate(self.menu_options):
                color = (
                    (255, 255, 0)
                    if i == self.selected_index
                    else (255, 255, 255)
                )
                text_surface = self.font.render(option, True, color)
                y_pos = (self.screen_height // 2) + (i * (self.main_size + 20))
                option_rect = text_surface.get_rect(
                    center=(self.screen_width // 2, y_pos)
                )
                self.screen.blit(text_surface, option_rect)

        elif self.state in ["PLAYING", "PAUSED"]:
            if self.game is None:
                return  # Mypy safety guard

            grid = self.game.maze.grid
            max_y = self.game.config.height - 1
            max_x = self.game.config.width - 1

            for y, row in enumerate(grid):
                for x, cell in enumerate(row):
                    is_42 = cell == 15
                    draw_n = bool(cell & 1)
                    draw_e = bool(cell & 2)
                    draw_s = bool(cell & 4)
                    draw_w = bool(cell & 8)

                    if is_42:
                        glow_color = (255, 140, 0)
                        if y > 0 and grid[y - 1][x] == 15:
                            draw_n = False
                        if y < max_y and grid[y + 1][x] == 15:
                            draw_s = False
                        if x < max_x and grid[y][x + 1] == 15:
                            draw_e = False
                        if x > 0 and grid[y][x - 1] == 15:
                            draw_w = False
                    else:
                        glow_color = (0, 0, 255)
                        if draw_n and y > 0 and grid[y - 1][x] == 15:
                            draw_n = False
                        if draw_s and y < max_y and grid[y + 1][x] == 15:
                            draw_s = False
                        if draw_e and x < max_x and grid[y][x + 1] == 15:
                            draw_e = False
                        if draw_w and x > 0 and grid[y][x - 1] == 15:
                            draw_w = False

                    core_color = (0, 0, 0)
                    glow_thick = 6
                    core_thick = 2
                    rect = pygame.Rect(
                        x * self.cell_size + self.left_offset,
                        y * self.cell_size + self.top_offset,
                        self.cell_size,
                        self.cell_size,
                    )

                    if draw_n:
                        pygame.draw.line(
                            self.screen,
                            glow_color,
                            rect.topleft,
                            rect.topright,
                            glow_thick,
                        )
                        pygame.draw.line(
                            self.screen,
                            core_color,
                            rect.topleft,
                            rect.topright,
                            core_thick,
                        )
                    if draw_e:
                        pygame.draw.line(
                            self.screen,
                            glow_color,
                            rect.topright,
                            rect.bottomright,
                            glow_thick,
                        )
                        pygame.draw.line(
                            self.screen,
                            core_color,
                            rect.topright,
                            rect.bottomright,
                            core_thick,
                        )
                    if draw_s:
                        pygame.draw.line(
                            self.screen,
                            glow_color,
                            rect.bottomleft,
                            rect.bottomright,
                            glow_thick,
                        )
                        pygame.draw.line(
                            self.screen,
                            core_color,
                            rect.bottomleft,
                            rect.bottomright,
                            core_thick,
                        )
                    if draw_w:
                        pygame.draw.line(
                            self.screen,
                            glow_color,
                            rect.topleft,
                            rect.bottomleft,
                            glow_thick,
                        )
                        pygame.draw.line(
                            self.screen,
                            core_color,
                            rect.topleft,
                            rect.bottomleft,
                            core_thick,
                        )

            gum_radius = max(2, self.cell_size // 10)
            for x, y in self.game.maze.pacgums:
                cx = (
                    (x * self.cell_size)
                    + (self.cell_size // 2)
                    + self.left_offset
                )
                cy = (
                    (y * self.cell_size)
                    + (self.cell_size // 2)
                    + self.top_offset
                )
                pygame.draw.circle(
                    self.screen, (255, 255, 255), (cx, cy), gum_radius
                )

            base_super_radius = max(4, self.cell_size // 4)
            for x, y in self.game.maze.super_pacgums:
                cx = (
                    (x * self.cell_size)
                    + (self.cell_size // 2)
                    + self.left_offset
                )
                cy = (
                    (y * self.cell_size)
                    + (self.cell_size // 2)
                    + self.top_offset
                )
                pulse = int(
                    (self.cell_size // 10)
                    * math.sin(pygame.time.get_ticks() / 150.0)
                )
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (cx, cy),
                    base_super_radius + pulse,
                )

            current_time = pygame.time.get_ticks()
            for i, ghost in enumerate(self.game.ghosts):
                time_since_tick = current_time - self.last_engine_tick
                progress = min(time_since_tick / self.tick_delay, 1.0)

                old_x, old_y = self.prev_ghost_pos.get(i, (ghost.x, ghost.y))
                new_x, new_y = ghost.x, ghost.y

                if abs(new_x - old_x) > 5 or abs(new_y - old_y) > 5:
                    render_x, render_y = float(new_x), float(new_y)
                else:
                    render_x = old_x + ((new_x - old_x) * progress)
                    render_y = old_y + ((new_y - old_y) * progress)

                pixel_x = int(render_x * self.cell_size + self.left_offset)
                pixel_y = int((render_y * self.cell_size) + self.top_offset)

                if ghost.frightened:
                    elapsed = time.monotonic() - self.game.frightened_start
                    remaining = self.game.frightened_duration - elapsed
                    if remaining < 3.0 and (current_time // 200) % 2 == 0:
                        active_img = self.w_ghost_img
                    elif ghost.eaten_time:
                        active_img = self.eyes_img
                    else:
                        active_img = self.f_ghost_img
                else:
                    active_img = self.ghost_normal_imgs[i % 4]
                self.screen.blit(active_img, (pixel_x, pixel_y))

            player = self.game.player
            time_since_tick = current_time - self.last_engine_tick
            progress = min(time_since_tick / self.tick_delay, 1.0)
            p_old_x, p_old_y = self.prev_player_pos
            p_new_x, p_new_y = player.x, player.y

            if abs(p_new_x - p_old_x) > 5 or abs(p_new_y - p_old_y) > 5:
                p_ren_x, p_ren_y = float(p_new_x), float(p_new_y)
            else:
                p_ren_x = p_old_x + ((p_new_x - p_old_x) * progress)
                p_ren_y = p_old_y + ((p_new_y - p_old_y) * progress)

            px_x = int(p_ren_x * self.cell_size + self.left_offset)
            px_y = int((p_ren_y * self.cell_size) + self.top_offset)

            if (current_time // 200) % 2 == 0:
                current_sprite = self.pac_open
            else:
                current_sprite = self.pac_closed

            if player.direction == "N":
                rotated_sprite = pygame.transform.rotate(current_sprite, 90)
            elif player.direction == "W":
                rotated_sprite = pygame.transform.rotate(current_sprite, 180)
            elif player.direction == "S":
                rotated_sprite = pygame.transform.rotate(current_sprite, 270)
            else:
                rotated_sprite = current_sprite
            self.screen.blit(rotated_sprite, (px_x, px_y))

            maze_pixel_width = self.game.config.width * self.cell_size
            hud_y = self.top_offset - (self.hud_reserved_space // 2)

            score_surf = self.small_font.render(
                f"SCORE: {player.score}", True, (255, 255, 255)
            )
            score_rect = score_surf.get_rect(midleft=(self.left_offset, hud_y))
            self.screen.blit(score_surf, score_rect)

            center_x = self.left_offset + (maze_pixel_width // 2)
            stats_surf = self.small_font.render(
                f"LIVES: {player.lives}   LEVEL: {self.game.level}",
                True,
                (255, 255, 255),
            )
            stats_rect = stats_surf.get_rect(center=(center_x, hud_y))
            self.screen.blit(stats_surf, stats_rect)

            t_elapsed = (
                time.monotonic() - self.game.start_time - self.game.paused_time
            )
            remaining_time = max(
                0, int(self.game.config.level_max_time - t_elapsed)
            )
            time_surf = self.small_font.render(
                f"TIME: {remaining_time}", True, (255, 255, 255)
            )
            time_rect = time_surf.get_rect(
                midright=(self.left_offset + maze_pixel_width, hud_y)
            )
            self.screen.blit(time_surf, time_rect)

            if self.state == "PAUSED":
                pause_text = self.font.render("PAUSED", True, (255, 255, 0))
                pause_rect = pause_text.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 2)
                )
                self.screen.blit(pause_text, pause_rect)

            if getattr(player, "god_mode", False):
                cheat_surf = self.small_font.render(
                    "GOD MODE", True, (0, 255, 0)
                )
                self.screen.blit(
                    cheat_surf,
                    cheat_surf.get_rect(
                        bottomright=(
                            self.screen_width - 20,
                            self.screen_height - 20,
                        )
                    ),
                )

        elif self.state in ["GAME_OVER", "VICTORY"]:
            if self.state == "VICTORY":
                victory = self.font.render("VICTORY", True, (0, 0, 255))
                victory_rect = victory.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 3)
                )
                self.screen.blit(victory, victory_rect)
            else:
                game_over = self.font.render("GAME OVER", True, (255, 0, 0))
                gameover_rect = game_over.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 3)
                )
                self.screen.blit(game_over, gameover_rect)

            input_surf = self.font.render(
                f"Input Text: {self.input_text}", True, (255, 255, 255)
            )
            input_rect = input_surf.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2)
            )
            self.screen.blit(input_surf, input_rect)

        elif self.state == "HIGHSCORES":
            title = self.font.render("TOP 10 HIGHSCORES", True, (255, 255, 0))
            title_rect = title.get_rect(
                center=(self.screen_width // 2, self.screen_height // 6)
            )
            self.screen.blit(title, title_rect)

            hs = HighScore(self.config.highscore_filename)
            hs.load()
            start_y = self.screen_height // 3
            row_spacing = self.small_size + 15

            if not hs.scores:
                msg = self.font.render(
                    "No highscores yet!", True, (255, 255, 255)
                )
                msg_rect = msg.get_rect(
                    center=(self.screen_width // 2, start_y)
                )
                self.screen.blit(msg, msg_rect)
            else:
                for i, entry in enumerate(hs.scores):
                    score_text = f"{i+1}. {entry.name} - {entry.score} pts"
                    surface = self.font.render(
                        score_text, True, (255, 255, 255)
                    )
                    score_rect = surface.get_rect(
                        center=(
                            self.screen_width // 2,
                            start_y + (i * row_spacing),
                        )
                    )
                    self.screen.blit(surface, score_rect)

        elif self.state == "INSTRUCTIONS":
            title = self.font.render("HOW TO PLAY", True, (0, 255, 255))
            self.screen.blit(
                title,
                title.get_rect(
                    center=(self.screen_width // 2, self.screen_height // 6)
                ),
            )
            instructions_list = [
                "USE ARROW KEYS TO MOVE",
                "EAT ALL DOTS TO WIN",
                "AVOID THE GHOSTS",
                "SUPER GUMS MAKE GHOSTS EDIBLE",
                "",
                "PRESS ESC TO RETURN",
            ]
            start_y = self.screen_height // 3
            row_spacing = self.small_size + 20

            for i, line in enumerate(instructions_list):
                color = (255, 255, 0) if "ESC" in line else (255, 255, 255)
                text_surface = self.small_font.render(line, True, color)
                text_rect = text_surface.get_rect(
                    center=(
                        self.screen_width // 2,
                        start_y + (i * row_spacing),
                    )
                )
                self.screen.blit(text_surface, text_rect)
        pygame.display.flip()

    def quit_game(self) -> None:
        """
        Safely shuts down the Pygame engine and exits the Python interpreter.
        """
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        """
        The main execution loop for the View layer.

        Locks the game logic to a specific millisecond tick_delay while
        allowing the render loop to uncap up to 60 FPS. Manages the forgiving
        cornering system by discharging UI movement buffers into the Model.
        """
        while True:
            self.handle_events()
            if self.state == "PLAYING" and self.game is not None:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_engine_tick > self.tick_delay:
                    self.prev_player_pos = (
                        float(self.game.player.x),
                        float(self.game.player.y),
                    )
                    for i, ghost in enumerate(self.game.ghosts):
                        self.prev_ghost_pos[i] = (
                            float(ghost.x),
                            float(ghost.y),
                        )

                    px, py = self.game.player.x, self.game.player.y
                    current_cell = self.game.maze.grid[py][px]

                    wall_bits = {"N": 1, "E": 2, "S": 4, "W": 8}
                    opposites = {"N": "S", "S": "N", "E": "W", "W": "E"}

                    if self.queued_direction:
                        turn_mask = wall_bits[self.queued_direction]
                        if self.queued_direction == opposites.get(
                            self.active_direction or ""
                        ):
                            self.active_direction = self.queued_direction
                            self.queued_direction = None
                        elif (current_cell & turn_mask) == 0:
                            self.active_direction = self.queued_direction
                            self.queued_direction = None

                    if self.active_direction:
                        forward_mask = wall_bits[self.active_direction]
                        if (current_cell & forward_mask) == 0:
                            self.game.player.direction = self.active_direction

                    current_lives = self.game.player.lives
                    self.game.update()

                    if current_lives > self.game.player.lives:
                        self.active_direction = None
                        self.queued_direction = None

                    self.last_engine_tick = current_time

                    if self.game.game_over:
                        self.state = "GAME_OVER"
                    elif self.game.level_won:
                        self.state = "VICTORY"

            self.render()
            self.clock.tick(60)


if __name__ == "__main__":
    ui = PacmanUI()
    ui.run()
