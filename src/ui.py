import pygame
import sys
from src.config import read_config, remove_comments, parse_config
from src.game import Game
from src.highscore import HighScore
import time
from pathlib import Path
import math


class PacmanUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("42 Pac-Man")
        self.clock = pygame.time.Clock()

        # The heart of the State Machine
        self.state = "MAIN_MENU"

        # This is where you will eventually hook up your partner's engine
        self.game = None
        pygame.font.init()
        self.input_text = ""
        self.menu_options = ["Start Game", "View Highscores", "Instructions", "Exit"]
        self.selected_index = 0
        self.last_engine_tick = 0
        self.tick_delay = 200
        self.hud_offset = 60
        self.ghost_normal_imgs = []
        project_root = Path(__file__).parent.parent
        colors = ["red", "pink", "cyan", "orange"]
        
        open_path = project_root / "src" / "assets" / "pacman.png"
        closed_path = project_root / "src" / "assets" / "pacman_closed.png"
        f_ghost_path = project_root / "src" / "assets" / "f_ghost.png"
        font_path = project_root / "src" / "assets" / "ARCADE_N.TTF"
        self.font = pygame.font.Font(str(font_path), 12)
        w_ghost_path = project_root / "src" / "assets" / "w_ghost.png"
        if len(sys.argv) < 2:
            print("Usage: python3 ui.py <config.json>")
            sys.exit(1)
        config_path = sys.argv[1]
        raw_text = read_config(config_path)
        clean_text = remove_comments(raw_text)
        self.config = parse_config(clean_text)
        max_width_cell = 800 // self.config.width
        max_height_cell = (600 - self.hud_offset) // self.config.height
        self.cell_size = min(max_width_cell, max_height_cell)
        for color in colors:
            path = project_root / "src" / "assets" / f"{color}_ghost.png"
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
            self.ghost_normal_imgs.append(img)
        self.w_ghost_img = pygame.transform.scale(
            pygame.image.load(str(w_ghost_path)).convert_alpha(),
            (self.cell_size, self.cell_size)
            )
        self.f_ghost_img = pygame.transform.scale(
            pygame.image.load(str(f_ghost_path)).convert_alpha(),
            (self.cell_size, self.cell_size)
            )
        # Assuming you set up the absolute Path as discussed earlier
        self.pac_open = pygame.transform.scale(
            pygame.image.load(str(open_path)).convert_alpha(),
            (self.cell_size, self.cell_size)
            )
        self.pac_closed = pygame.transform.scale(
            pygame.image.load(str(closed_path)).convert_alpha(),
            (self.cell_size, self.cell_size)
            )
        self.prev_player_pos = (0, 0)
        self.prev_ghost_pos = {}  # Maps ghost index to (x, y)
        self.queued_direction = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.KEYDOWN:
                # Route inputs based on the current state
                if self.state == "MAIN_MENU":
                    if event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.menu_options)
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:    
                        if self.selected_index == 0:
                            self.state = "PLAYING"  # Transition state!
                            self.game = Game(self.config)
                            if hasattr(self.game, 'high_scores'):
                                self.real_add_score = self.game.high_scores.add_score
                                self.game.high_scores.add_score = lambda *args, **kwargs: None
                        elif self.selected_index == 1:
                            self.state = "HIGHSCORES"
                        elif self.selected_index == 2:
                            self.state = "INSTRUCTIONS"
                        elif self.selected_index == 3:
                            self.quit_game()
                elif self.state == "PLAYING":
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
                elif self.state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                        self.game.resume()
                elif self.state in ["GAME_OVER", "VICTORY"]:
                    if event.key == pygame.K_RETURN:
                        self.state = "MAIN_MENU"
                        if hasattr(self, 'real_add_score'):
                            self.real_add_score(self.input_text, self.game.player.score)
                            self.game.high_scores.save() # Call partner's save method
                        self.input_text = ""  # Reset for next time
                    elif event.key == pygame.K_BACKSPACE:
                        # Slice off the last character
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 10:
                            if event.unicode.isalnum() or\
                                  event.unicode == " ":
                                self.input_text += event.unicode
                elif self.state in ["HIGHSCORES", "INSTRUCTIONS"]:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "MAIN_MENU"
                print(self.state)

    def render(self):
        self.screen.fill((0, 0, 0))  # Wipe screen

        # Route drawing based on the current state
        if self.state == "MAIN_MENU":
            title = self.font.render("42 PAC-MAN", True, (255, 255, 255))
            self.screen.blit(title, (350, 100))
            for i, option in enumerate(self.menu_options):
                color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
                text_surface = self.font.render(option, True, color)
                y_position = 250 + (i * 50)
                self.screen.blit(text_surface, (350, y_position))
        elif self.state in ["PLAYING", "PAUSED"]:
            grid = self.game.maze.grid
            max_y = self.game.config.height - 1
            max_x = self.game.config.width - 1
            for y, row in enumerate(self.game.maze.grid):
                for x, cell in enumerate(row):
                    is_42 = (cell == 15)
                    draw_n = bool(cell & 1)
                    draw_e = bool(cell & 2)
                    draw_s = bool(cell & 4)
                    draw_w = bool(cell & 8)
                    if is_42:
                        glow_color = (255, 140, 0)
                        if y > 0 and grid[y-1][x] == 15:
                            draw_n = False
                        if y < max_y and grid[y+1][x] == 15:
                            draw_s = False
                        if x < max_x and grid[y][x+1] == 15:
                            draw_e = False
                        if x > 0 and grid[y][x-1] == 15:
                            draw_w = False
                    else:
                        glow_color = (0, 0, 255)  # Arcade Blue
                        if draw_n and y > 0 and grid[y-1][x] == 15: draw_n = False
                        if draw_s and y < max_y and grid[y+1][x] == 15: draw_s = False
                        if draw_e and x < max_x and grid[y][x+1] == 15: draw_e = False
                        if draw_w and x > 0 and grid[y][x-1] == 15: draw_w = False
                    core_color = (0, 0, 0)
                    glow_thick = 6
                    core_thick = 2

                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size + self.hud_offset,
                        self.cell_size,
                        self.cell_size
                        )
                    if draw_n:
                        pygame.draw.line(self.screen, glow_color, rect.topleft, rect.topright, glow_thick)
                        pygame.draw.line(self.screen, core_color, rect.topleft, rect.topright, core_thick)
                    if draw_e:
                        pygame.draw.line(self.screen, glow_color, rect.topright, rect.bottomright, glow_thick)
                        pygame.draw.line(self.screen, core_color, rect.topright, rect.bottomright, core_thick)
                    if draw_s:
                        pygame.draw.line(self.screen, glow_color, rect.bottomleft, rect.bottomright, glow_thick)
                        pygame.draw.line(self.screen, core_color, rect.bottomleft, rect.bottomright, core_thick)
                    if draw_w:
                        pygame.draw.line(self.screen, glow_color, rect.topleft, rect.bottomleft, glow_thick)
                        pygame.draw.line(self.screen, core_color, rect.topleft, rect.bottomleft, core_thick)
            for x, y in self.game.maze.pacgums:
                center_x = (x * self.cell_size) + (self.cell_size // 2)
                center_y = (y * self.cell_size) + (self.cell_size // 2) + self.hud_offset
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x, center_y),
                    3
                    )
            for x, y in self.game.maze.super_pacgums:
                center_x = (x * self.cell_size) + (self.cell_size // 2)
                center_y = (y * self.cell_size) + (self.cell_size // 2) + self.hud_offset
                current_time = pygame.time.get_ticks()
                pulse_radius = 8 + int(2 * math.sin(current_time / 150.0))
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x, center_y),
                    pulse_radius
                    )
            for i, ghost in enumerate(self.game.ghosts):
                current_time = pygame.time.get_ticks()
                # 1. Calculate fractional progress (0.0 to 1.0)
                time_since_tick = current_time - self.last_engine_tick
                progress = min(time_since_tick / self.tick_delay, 1.0)
                # 2. Grab the specific ghost's past and present coordinates
                old_x, old_y = self.prev_ghost_pos[i]
                new_x, new_y = ghost.x, ghost.y
                # 3. Apply the relaxed guard (handles death respawns)
                if abs(new_x - old_x) > 5 or abs(new_y - old_y) > 5:
                    render_x, render_y = new_x, new_y
                else:
                    render_x = old_x + ((new_x - old_x) * progress)
                    render_y = old_y + ((new_y - old_y) * progress)
                # 4. Final screen coordinates
                pixel_x = render_x * self.cell_size
                pixel_y = (render_y * self.cell_size) + self.hud_offset
                if ghost.frightened:
                    elapsed = time.monotonic() - self.game.frightened_start
                    remaining = self.game.frightened_duration - elapsed
                    if remaining < 3.0 and (pygame.time.get_ticks() // 200) % 2 == 0:
                        active_img = self.w_ghost_img
                    else:
                        active_img = self.f_ghost_img
                else:
                    active_img = self.ghost_normal_imgs[i % 4]
                self.screen.blit(active_img, (pixel_x, pixel_y))
            player = self.game.player
            current_time = pygame.time.get_ticks()
            time_since_tick = current_time - self.last_engine_tick
            progress = min(time_since_tick / self.tick_delay, 1.0)
            old_x, old_y = self.prev_player_pos
            new_x, new_y = player.x, player.y
            if abs(new_x - old_x) > 5 or abs(new_y - old_y) > 5:
                render_x, render_y = new_x, new_y
            else:
                render_x = old_x + ((new_x - old_x) * progress)
                render_y = old_y + ((new_y - old_y) * progress)

            pixel_x = render_x * self.cell_size
            pixel_y = (render_y * self.cell_size) + self.hud_offset
            current_time = pygame.time.get_ticks()
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
            self.screen.blit(rotated_sprite, (pixel_x, pixel_y))
            current_score = self.game.player.score
            score_surface = self.font.render(f"Score: {current_score}", True, (255, 255, 255))
            self.screen.blit(score_surface, (20, 10))
            current_lives = self.game.player.lives
            current_level = self.game.level
            lives_surface = self.font.render(f"Lives: {current_lives}", True, (255, 255, 255))
            level_surface = self.font.render(f"Level: {current_level}", True, (255, 255, 255))
            self.screen.blit(lives_surface, (200, 10))
            self.screen.blit(level_surface, (350, 10))
            elapsed = time.monotonic() - self.game.start_time - self.game.paused_time
            remaining_time = max(0, int(self.game.config.level_max_time - elapsed))
            time_surface = self.font.render(f"Remaining Time: {remaining_time}", True, (255, 255, 255))
            self.screen.blit(time_surface, (500, 10))
            if self.state == "PAUSED":
                pause_text = self.font.render("PAUSED", True, (255, 255, 0))
                self.screen.blit(pause_text, (350, 300))
        elif self.state in ["GAME_OVER", "VICTORY"]:
            if self.state == "VICTORY":
                victory = self.font.render("VICTORY", True, (0, 0, 255))
                self.screen.blit(victory, (10, 10))
            else:
                game_over = self.font.render("GAME OVER", True, (255, 0, 0))
                self.screen.blit(game_over, (350, 250))
            input_surface = self.font.render(f"Input Text: {self.input_text}", True, (255, 255, 255))
            self.screen.blit(input_surface, (450, 10))
        elif self.state == "HIGHSCORES":
            title = self.font.render("TOP 10 HIGHSCORES", True, (255, 255, 0))
            self.screen.blit(title, (300, 50))
            hs = HighScore(self.config.highscore_filename)
            hs.load()
            if not hs.scores:
                msg = self.font.render("No highscores yet!", True, (255, 255, 255))
                self.screen.blit(msg, (300, 120))
            else:
                for i, entry in enumerate(hs.scores):
                    score_text = f"{i+1}. {entry.name} - {entry.score} pts"
                    surface = self.font.render(score_text, True, (255, 255, 255))
                    self.screen.blit(surface, (300, 120 + (i*30)))
        elif self.state == "INSTRUCTIONS":
            pass
        pygame.display.flip()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.handle_events()
            if self.state == "PLAYING" and self.game is not None:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_engine_tick > self.tick_delay:
                    # 1. SNAPSHOT: Remember where everyone is before they move
                    self.prev_player_pos = (self.game.player.x, self.game.player.y)
                    for i, ghost in enumerate(self.game.ghosts):
                        self.prev_ghost_pos[i] = (ghost.x, ghost.y)
                    # 2. DISCHARGE BUFFER: Apply the stored keyboard input
                    if self.queued_direction:
                        self.game.move_player(self.queued_direction)
                    self.game.update()
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
