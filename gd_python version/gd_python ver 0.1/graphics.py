import pygame

def draw_cube(cube, screen, camera_x, camera_y):
    # Draw cube graphics here
    rotated_surface = pygame.transform.rotate(cube.image, cube.rotation_angle)
    rect = rotated_surface.get_rect(center=(cube.x + 25, cube.y + 25))
    screen.blit(rotated_surface, rect.move(-camera_x, 0))

def draw_platform(platform, screen, camera_x, camera_y):
    # Draw platform graphics here
    pygame.draw.rect(screen, (0, 255, 0), (platform.x - camera_x, platform.y, platform.width, platform.height))

def draw_wave(wave, screen, camera_x, camera_y):
    screen.blit(wave.image, (wave.x - camera_x, wave.y - camera_y))
    
def draw_spike(spike, screen, camera_x, camera_y, rotation_angle=90):
    if rotation_angle == 0:
        points = [
            (spike.x - camera_x, spike.y),
            (spike.x - camera_x + 30, spike.y),
            (spike.x - camera_x + 15, spike.y + 30)
        ]
    elif rotation_angle == 90:
        points = [
            (spike.x - camera_x, spike.y + 30),
            (spike.x - camera_x, spike.y),
            (spike.x - camera_x + 30, spike.y + 15)
        ]
    elif rotation_angle == 180:
        points = [
            (spike.x - camera_x + 30, spike.y + 30),
            (spike.x - camera_x, spike.y + 30),
            (spike.x - camera_x + 15, spike.y)
        ]
    elif rotation_angle == 270:
        points = [
            (spike.x - camera_x + 30, spike.y),
            (spike.x - camera_x + 30, spike.y + 30),
            (spike.x - camera_x, spike.y + 15)
        ]
    pygame.draw.polygon(screen, (255, 0, 0), [(spike.x - camera_x, spike.y + 30), 
                                                (spike.x - camera_x + 15, spike.y), 
                                                (spike.x - camera_x + 30, spike.y + 30)])