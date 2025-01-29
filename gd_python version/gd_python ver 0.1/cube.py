import pygame

class Cube:
    def __init__(self, x, y, rotation_angle=0):
        self.x = x
        self.y = y
        self.size = 50
        self.rotation_angle = rotation_angle
        self.target_rotation_angle = 0
        self.velocity = 0
        self.is_on_ground = True
        self.distance_traveled = 0
        self.image = pygame.image.load('cube_image.png').convert_alpha()  # Замените на ваш файл изображения
        self.image = pygame.transform.scale(self.image, (50, 50))  # Изменение размера изображения на 50x50

    def update_rotation(self):
        # Update rotation logic here
        if not self.is_on_ground:
            delta_angle = (self.target_rotation_angle - self.rotation_angle) % 360
            if delta_angle > 180:
                delta_angle -= 360
            self.rotation_angle += delta_angle * 0.05
            if abs(self.rotation_angle - self.target_rotation_angle) < 5:
                self.rotation_angle = self.target_rotation_angle
        else:
            self.rotation_angle = self.target_rotation_angle