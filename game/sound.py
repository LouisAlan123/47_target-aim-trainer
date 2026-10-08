import math
import struct

import pygame

SAMPLE_RATE = 44100


def _tone(freq_start, freq_end, duration, volume=0.4):
    """Build a short sine sweep as a pygame Sound (no audio files needed)."""
    n = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = freq_start + (freq_end - freq_start) * t
        phase += 2 * math.pi * freq / SAMPLE_RATE
        envelope = min(1.0, (1 - t) * 4)  # quick fade-out to avoid clicks
        samples.append(int(32767 * volume * envelope * math.sin(phase)))
    data = struct.pack("<" + "h" * n, *samples)
    return pygame.mixer.Sound(buffer=data)


class SoundManager:
    """Hit / miss / round-end sounds. Silently disabled if audio is unavailable."""

    def __init__(self):
        self.enabled = False
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            self.hit = _tone(660, 990, 0.12)       # rising blip
            self.miss = _tone(220, 110, 0.18)      # low falling buzz
            self.end = _tone(880, 220, 0.6)        # long descending tone
            self.enabled = True
        except pygame.error:
            pass

    def _play(self, sound):
        if self.enabled:
            sound.play()

    def play_hit(self):
        self._play(self.hit)

    def play_miss(self):
        self._play(self.miss)

    def play_end(self):
        self._play(self.end)
