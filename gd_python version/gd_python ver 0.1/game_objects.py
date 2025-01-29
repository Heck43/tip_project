import pygame

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen, camera_x):
        pygame.draw.rect(screen, (0, 255, 0), (self.x - camera_x + 25, self.y, self.width, self.height))

    def collide(self, cube_x, cube_y, cube_width, cube_height):
        # Collision detection logic here
        pass