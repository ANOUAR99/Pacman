import pygame
import sys
from src.config import Config, read_config, remove_comments, parse_config
from src.game import Game
import time
import json
from pathlib import Path


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
        self.font = pygame.font.Font(None, 24)
        self.input_text = ""
        self.menu_options = ["Start Game", "View Highscores", "Instructions", "Exit"]
        self.selected_index = 0
        project_root = Path(__file__).parent.parent
        pacman_path = project_root / "src" / "assets" / "pacman.png"
        ghost_path = project_root / "src" / "assets" / "ghost.png"
        self.pacman_img = pygame.image.load(str(pacman_path)).convert_alpha()
        self.ghost_img = pygame.image.load(str(ghost_path)).convert_alpha()
        self.pacman_img = pygame.transform.scale(
            self.pacman_img,
            (self.cell_size, self.cell_size)
            )
        self.ghost_img = pygame.transform.scale(
            self.ghost_img,
            (self.cell_size, self.cell_size)
            )
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
                            if len(sys.argv) < 2:
                                print("Usage: python3 ui.py <config.json>")
                                sys.exit(1)
                            config_path = sys.argv[1]
                            raw_text = read_config(config_path)
                            clean_text = remove_comments(raw_text)
                            config = parse_config(clean_text)
                            self.game = Game(config)
                        elif self.selected_index == 1:
                            pass
                        elif self.selected_index == 2:
                            pass
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
                        new_score = {"name": self.input_text, "score": self.game.player.score}
                        try:
                            with open(self.game.config.highscore_filename, "a") as f:
                                f.write(json.dumps(new_score) + "\n")
                        except Exception as e:
                            print(f"Failed to save score: {e}")
                        self.input_text = ""  # Reset for next time
                    elif event.key == pygame.K_BACKSPACE:
                        # Slice off the last character
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 10:
                            if event.unicode.isalnum() or\
                                  event.unicode == " ":
                                self.input_text += event.unicode
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
            color = (0, 0, 150)
            tickness = 2
            for y, row in enumerate(self.game.maze.grid):
                for x, cell in enumerate(row):
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                        )
                    if cell & 1:
                        pygame.draw.line(
                            self.screen,
                            color,
                            rect.topleft,
                            rect.topright,
                            tickness
                            )
                    if cell & 2:
                        pygame.draw.line(
                            self.screen,
                            color,
                            rect.topright,
                            rect.bottomright,
                            tickness
                            )
                    if cell & 4:
                        pygame.draw.line(
                            self.screen,
                            color,
                            rect.bottomright,
                            rect.bottomleft,
                            tickness
                            )
                    if cell & 8:
                        pygame.draw.line(
                            self.screen,
                            color,
                            rect.topleft,
                            rect.bottomleft,
                            tickness
                            )
            for x, y in self.game.maze.pacgums:
                center_x = (x * self.cell_size) + (self.cell_size // 2)
                center_y = (y * self.cell_size) + (self.cell_size // 2)
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x, center_y),
                    3
                    )
            for x, y in self.game.maze.super_pacgums:
                center_x = (x * self.cell_size) + (self.cell_size // 2)
                center_y = (y * self.cell_size) + (self.cell_size // 2)
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x, center_y),
                    8
                    )
            for ghost in self.game.ghosts:
                pixel_x = ghost.x * self.cell_size
                pixel_y = ghost.y * self.cell_size
                self.screen.blit(self.ghost_img, (pixel_x, pixel_y))
            player = self.game.player
            pixel_x = player.x * self.cell_size
            pixel_y = player.y * self.cell_size
            self.screen.blit(self.pacman_img, (pixel_x, pixel_y))
            current_score = self.game.player.score
            score_surface = self.font.render(f"Score: {current_score}", True, (255, 255, 255))
            self.screen.blit(score_surface, (10, 10))
            current_lives = self.game.player.lives
            current_level = self.game.level
            lives_surface = self.font.render(f"Lives: {current_lives}", True, (255, 255, 255))
            level_surface = self.font.render(f"Level: {current_level}", True, (255, 255, 255))
            self.screen.blit(lives_surface, (150, 10))
            self.screen.blit(level_surface, (300, 10))
            elapsed = time.monotonic() - self.game.start_time - self.game.paused_time
            remaining_time = max(0, int(self.game.config.level_max_time - elapsed))
            time_surface = self.font.render(f"Remaining Time: {remaining_time}", True, (255, 255, 255))
            self.screen.blit(time_surface, (450, 10))
            if self.state == "PAUSED":
                pause_text = self.font.render("PAUSED", True, (255, 255, 0))
                self.screen.blit(pause_text, (350, 300))
        elif self.state in ["GAME_OVER", "VICTORY"]:
            if self.state == "VICTORY":
                victory = self.font.render("VICTORY", True, (0, 0, 255))
                self.screen.blit(victory, (10, 10))
            else:
                game_over = self.font.render("GAME OVER", True, (255, 0, 0))
                self.screen.blit(game_over, (10, 10))
            input_surface = self.font.render(f"Input Text: {self.input_text}", True, (255, 255, 255))
            self.screen.blit(input_surface, (450, 10))

        pygame.display.flip()

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            self.handle_events()
            if self.state == "PLAYING" and self.game is not None:
                self.game.update()
                if self.game.game_over:
                    self.state = "GAME_OVER"
                elif self.game.level_won:
                    self.state = "VICTORY"
            self.render()
            self.clock.tick(60)


if __name__ == "__main__":
    ui = PacmanUI()
    ui.run()
