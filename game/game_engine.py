import pygame
import random
from .target import Target

# Game Engine

WHITE = (255, 255, 255)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.margin = 60
        self.hud_height = 60
        self.target = self._spawn_target()

        self.round_seconds = 30
        self.time_left_frames = self.round_seconds * 60

        self.hits = 0
        self.misses = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 26)
        self.game_over = False
        self.should_quit = False
        self.game_over_frames = 0  # frames since the round ended
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)

    def _spawn_target(self):
        x = random.randint(self.margin, self.width - self.margin)
        y = random.randint(self.margin + self.hud_height, self.height - self.margin)
        return Target(x, y)

    def handle_event(self, event):
        if self.game_over:
            # Ignore input for a moment so a frantic last click doesn't
            # instantly dismiss the screen before it can be read.
            if self.game_over_frames > 30 and event.type in (
                pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN
            ):
                self.should_quit = True
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        x, y = pos
        if self.target.contains_point(x, y):
            self.hits += 1
            self.score += 1
            self.target = self._spawn_target()
        else:
            self.misses += 1

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
            return

        self.target.update()
        if self.target.expired():
            self.misses += 1  # letting a target time out counts as a miss too
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

        self._blit_centered(screen, self.big_font.render("GAME OVER", True, WHITE), 110)
        self._blit_centered(screen, self.font.render(f"Final Score: {self.score}", True, WHITE), 200)
        self._blit_centered(screen, self.font.render(f"Accuracy: {self.accuracy()}%", True, WHITE), 240)
        self._blit_centered(
            screen,
            self.font.render(f"Hits: {self.hits}   Misses: {self.misses}", True, WHITE),
            280,
        )
        if self.game_over_frames > 30:
            self._blit_centered(
                screen, self.font.render("Press any key or click to exit", True, (200, 200, 200)), 370
            )
