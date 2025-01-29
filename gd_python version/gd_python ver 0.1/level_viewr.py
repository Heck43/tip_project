import pygame
import sys

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Classes for Level, Platforms, and Spikes
class Level:
    def __init__(self, platforms, spikes):
        self.platforms = platforms
        self.spikes = spikes

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

class Spike:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

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

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

def draw_level(level, screen, camera):
    # Draw platforms
    for platform in level.platforms:
        pygame.draw.rect(screen, (0, 255, 0), (platform.x - camera.x, platform.y - camera.y, platform.width, platform.height))
    
    # Draw spikes
    for spike in level.spikes:
        pygame.draw.rect(screen, (255, 0, 0), (spike.x - camera.x, spike.y - camera.y, spike.width, spike.height))  # Spikes as red squares

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Level Viewer")

    level = generate_level()
    camera = Camera(0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            camera.move(-30, 0)
        if keys[pygame.K_RIGHT]:
            camera.move(30, 0)
        if keys[pygame.K_UP]:
            camera.move(0, -30)
        if keys[pygame.K_DOWN]:
            camera.move(0, 30)

        screen.fill((0, 0, 0))  # Clear screen with black
        draw_level(level, screen, camera)  # Draw the level
        pygame.display.flip()  # Update the display
        pygame.time.Clock().tick(90)  # Limit to 60 FPS

if __name__ == "__main__":
    main()