import pygame

class Level:
    def __init__(self, platforms, spikes):
        self.platforms = platforms
        self.spikes = spikes

def generate_level():
    platforms = [
        Platform(0, 480 - 20, 9000, 20),  # Ground
        Platform(2950, 420, 50, 50),
        Platform(3150, 360, 50, 100),
        Platform(3350, 300, 50, 180),
    ]
    spikes = [
        Spike(1500, 420, 50, 50),
        Spike(2100, 420, 50, 50),
        Spike(2150, 420, 50, 50),
        Spike(2850, 420, 50, 50),
        Spike(2900, 420, 50, 50),
    ]
    return Level(platforms, spikes)

class Spike:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Triangle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height