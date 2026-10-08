import math

class Target:
    def __init__(self, x, y, base_radius=40, min_radius=12, lifespan_frames=90):
        self.x = x
        self.y = y
        self.base_radius = base_radius
        self.min_radius = min_radius
        self.lifespan_frames = lifespan_frames
        self.age = 0

    def update(self):
        self.age += 1

    def expired(self):
        return self.age >= self.lifespan_frames

    def visual_radius(self):
        # The target shrinks as it ages, giving the player less time
        # to react the longer it's been on screen.
        t = min(1.0, self.age / self.lifespan_frames)
        return self.base_radius - (self.base_radius - self.min_radius) * t

    def contains_point(self, x, y):
        # Hit-testing uses the same radius that render() draws, so the
        # clickable area always matches the visible (shrinking) circle.
        return math.hypot(self.x - x, self.y - y) <= self.visual_radius()
