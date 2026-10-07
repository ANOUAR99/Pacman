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

        self.cell_size = 30
        pygame.font.init()
        self.input_text = ""
        self.menu_options = ["Start Game", "View Highscores", "Instructions", "Exit"]
        self.selected_index = 0
        self.last_engine_tick = 0
        self.tick_delay = 250
        self.hud_offset = 60
        self.ghost_normal_imgs = []
        project_root = Path(__file__).parent.parent
        colors = ["red", "pink", "cyan", "orange"]
        for color in colors:
            path = project_root / "src" / "assets" / f"{color}_ghost.png"
            img = pygame.image.load(str(path)).convert_alpha()
            img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
            self.ghost_normal_imgs.append(img)
        open_path = project_root / "src" / "assets" / "pacman.png"
        closed_path = project_root / "src" / "assets" / "pacman_closed.png"
        f_ghost_path = project_root / "src" / "assets" / "f_ghost.png"
        font_path = project_root / "src" / "assets" / "ARCADE_N.TTF"
        self.font = pygame.font.Font(str(font_path), 12)
        w_ghost_path = project_root / "src" / "assets" / "w_ghost.png"
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
            ) # milliseconds per grid move
        if len(sys.argv) < 2:
            print("Usage: python3 ui.py <config.json>")
            sys.exit(1)
        config_path = sys.argv[1]
        raw_text = read_config(config_path)
        clean_text = remove_comments(raw_text)
        self.config = parse_config(clean_text)

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
                        self.game.move_player("N")
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.game.move_player("S")
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.game.move_player("W")
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.game.move_player("E")
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
            tickness = 2
            for y, row in enumerate(self.game.maze.grid):
                for x, cell in enumerate(row):
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size + self.hud_offset,
                        self.cell_size,
                        self.cell_size
                        )
                    outer_glow_color = (0, 0 ,100)
                    inner_core_color = (0, 255, 255)
                    if cell & 1:
                        pygame.draw.line(
                            self.screen,
                            inner_core_color,
                            rect.topleft,
                            rect.topright,
                            tickness
                            )
                        pygame.draw.line(
                            self.screen,
                            outer_glow_color,
                            rect.topleft,
                            rect.topright,
                            tickness + 4
                            )
                    if cell & 2:
                        pygame.draw.line(
                            self.screen,
                            inner_core_color,
                            rect.topright,
                            rect.bottomright,
                            tickness
                            )
                        pygame.draw.line(
                            self.screen,
                            outer_glow_color,
                            rect.topright,
                            rect.bottomright,
                            tickness + 4
                            )
                    if cell & 4:
                        pygame.draw.line(
                            self.screen,
                            inner_core_color,
                            rect.bottomright,
                            rect.bottomleft,
                            tickness
                            )
                        pygame.draw.line(
                            self.screen,
                            outer_glow_color,
                            rect.bottomright,
                            rect.bottomleft,
                            tickness + 4
                            )
                    if cell & 8:
                        pygame.draw.line(
                            self.screen,
                            inner_core_color,
                            rect.topleft,
                            rect.bottomleft,
                            tickness
                            )
                        pygame.draw.line(
                            self.screen,
                            outer_glow_color,
                            rect.topleft,
                            rect.bottomleft,
                            tickness + 4
                            )
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
                pixel_x = ghost.x * self.cell_size
                pixel_y = ghost.y * self.cell_size + self.hud_offset
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
            pixel_x = player.x * self.cell_size
            pixel_y = player.y * self.cell_size + self.hud_offset
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
