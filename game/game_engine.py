import pygame
import random
from .target import Target
from .sound import SoundManager

# Game Engine

# Difficulty presets: (base_radius, min_radius, lifespan_frames at 60 FPS)
DIFFICULTIES = {
    "Easy":   {"base_radius": 50, "min_radius": 18, "lifespan_frames": 120},
    "Medium": {"base_radius": 40, "min_radius": 12, "lifespan_frames": 90},
    "Hard":   {"base_radius": 28, "min_radius": 8,  "lifespan_frames": 60},
}
GRAY = (200, 200, 200)
BUTTON = (70, 70, 85)
BUTTON_HOVER = (100, 100, 125)

WHITE = (255, 255, 255)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.round_seconds = 30
        self.font = pygame.font.SysFont("Arial", 26)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.sounds = SoundManager()
        self.should_quit = False
        self.difficulty = "Medium"

        # Game-over menu buttons: three difficulties in a row + quit
        bw, bh, gap = 150, 50, 20
        x0 = self.width // 2 - (3 * bw + 2 * gap) // 2
        self.buttons = {
            name: pygame.Rect(x0 + i * (bw + gap), 340, bw, bh)
            for i, name in enumerate(DIFFICULTIES)
        }
        self.quit_button = pygame.Rect(self.width // 2 - 75, 410, 150, 44)

        self.start_round(self.difficulty)

    def start_round(self, difficulty):
        """(Re)start a round with the chosen difficulty."""
        self.difficulty = difficulty
        self.time_left_frames = self.round_seconds * 60
        self.hits = 0
        self.misses = 0
        self.score = 0
        self.game_over = False
        self.game_over_frames = 0  # frames since the round ended
        self.target = self._spawn_target()

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(x, y, **DIFFICULTIES[self.difficulty])

    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_game_over_event(self, event):
        # Ignore input for a moment so a frantic last click doesn't
        # instantly pick an option before the screen can be read.
        if self.game_over_frames <= 30:
            return
        if event.type == pygame.KEYDOWN:
            keys = {pygame.K_1: "Easy", pygame.K_2: "Medium", pygame.K_3: "Hard"}
            if event.key in keys:
                self.start_round(keys[event.key])
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                self.should_quit = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.start_round(name)
                    return
            if self.quit_button.collidepoint(event.pos):
                self.should_quit = True

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.sounds.play_hit()
            self.target = self._spawn_target()
        else:
            self.misses += 1
            self.sounds.play_miss()

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            self.game_over_frames += 1
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.game_over = True
            self.sounds.play_end()
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
            self.sounds.play_miss()
            self.target = self._spawn_target()

    def accuracy(self):
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return round(100 * self.hits / total, 1)

    def render(self, screen):
        if self.game_over:
            self._render_game_over(screen)
            return

        r = int(self.target.visual_radius())
        pygame.draw.circle(screen, RED, (self.target.x, self.target.y), r)
        pygame.draw.circle(screen, WHITE, (self.target.x, self.target.y), r, 2)
        self._render_hud(screen)

    def _render_hud(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        seconds_left = max(0, self.time_left_frames // 60)
        timer_text = self.font.render(f"Time: {seconds_left}s", True, WHITE)
        screen.blit(timer_text, (self.width - 140, 10))

        acc_text = self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE)
        screen.blit(acc_text, (self.width // 2 - 90, 10))

    def _blit_centered(self, screen, surf, y):
        screen.blit(surf, (self.width // 2 - surf.get_width() // 2, y))

    def _render_game_over(self, screen):
        self._render_hud(screen)
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        self._blit_centered(screen, self.big_font.render("GAME OVER", True, WHITE), 70)
        self._blit_centered(screen, self.font.render(f"Final Score: {self.score}", True, WHITE), 160)
        self._blit_centered(screen, self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE), 200)
        self._blit_centered(
            screen,
            self.font.render(f"Hits: {self.hits}   Misses: {self.misses}", True, WHITE),
            240,
        )
        if self.game_over_frames > 30:
            self._blit_centered(screen, self.font.render("Play again - choose difficulty:", True, GRAY), 300)
            mouse = pygame.mouse.get_pos()
            for i, (name, rect) in enumerate(self.buttons.items(), start=1):
                self._draw_button(screen, rect, f"{i}. {name}", mouse)
            self._draw_button(screen, self.quit_button, "Q. Quit", mouse)

    def _draw_button(self, screen, rect, label, mouse):
        color = BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
        text = self.font.render(label, True, WHITE)
        screen.blit(text, text.get_rect(center=rect.center))
