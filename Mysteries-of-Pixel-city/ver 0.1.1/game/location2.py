import pygame
import sys
import math

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Устанавливаем размеры окна
screen_width = 1628
screen_height = 1017
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mysteries of the Pixel City")

# Загружаем изображения
background_image = pygame.image.load('image/location2.jpg').convert()  # Нужно будет создать это изображение
character_image = pygame.image.load('image/Sprite-detective.png').convert_alpha()

# Создаем объект для управления временем
clock = pygame.time.Clock()

# Устанавливаем шрифты
default_font = pygame.font.Font('font/better-vcr_0.ttf', 30)
loud_font = pygame.font.Font('font/GhastlyPanicCyr.otf', 60)
name_font = pygame.font.Font('font/better-vcr_0.ttf', 20)

# Название предыдущей локации для перехода обратно
prev_location_name = "Начальная локация"
next_location_name = "Следующая локация"

# Параметры для отображения названия локации
location_display_x = 150  # Для левой стороны
right_location_display_x = screen_width - 150  # Для правой стороны
location_display_radius = 200

class Character(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=pos)

    def update(self, dx=0, dy=0):
        self.rect.x += dx
        self.rect.y += dy

def location_transition_animation(surface, location_name):
    # Сохраняем текущее состояние экрана
    current_screen = surface.copy()
    
    # Создаем черную поверхность
    black_surface = pygame.Surface((screen_width, screen_height))
    black_surface.fill((0, 0, 0))
    
    # Создаем поверхность для текста
    location_name_surface = loud_font.render(location_name, True, (255, 255, 255))
    location_name_rect = location_name_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    
    # Затемнение экрана
    for alpha in range(0, 255, 5):
        surface.blit(current_screen, (0, 0))
        black_surface.set_alpha(alpha)
        surface.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Показываем название локации
    for alpha in range(0, 255, 5):
        surface.fill((0, 0, 0))
        location_name_surface.set_alpha(alpha)
        surface.blit(location_name_surface, location_name_rect)
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Задержка, чтобы текст был виден
    pygame.time.delay(500)
    
    # Затемняем название локации
    for alpha in range(255, 0, -5):
        surface.fill((0, 0, 0))
        location_name_surface.set_alpha(alpha)
        surface.blit(location_name_surface, location_name_rect)
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Черный экран перед переходом
    surface.fill((0, 0, 0))
    pygame.display.flip()
    pygame.time.delay(100)  # Небольшая задержка для уверенности в черном экране
    
    return True

def fade_from_black(screen):
    black_surface = pygame.Surface((screen.get_width(), screen.get_height()))
    black_surface.fill((0, 0, 0))
    
    # Плавно уменьшаем прозрачность черного экрана
    for alpha in range(255, -1, -5):  # От полностью непрозрачного до прозрачного
        screen.blit(background_image, (0, 0))  # Отрисовываем фон локации
        black_surface.set_alpha(alpha)
        screen.blit(black_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)  # Небольшая задержка для плавности

def transition_to_location(direction):
    if direction == "prev":
        location_transition_animation(screen, prev_location_name)
        import location
        location.main()
    elif direction == "next":
        location_transition_animation(screen, next_location_name)
        import location3
        location3.main()

def main():
    global running, screen, all_sprites, character
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    
    # Инициализация спрайтов
    all_sprites = pygame.sprite.Group()
    character = Character(character_image, (600, 600))
    all_sprites.add(character)
    
    # Определяем границы области, в которой может перемещаться персонаж
    boundary_rect = pygame.Rect(-100, 50, screen_width - -120, screen_height - 130)
    
    # Эффект появления из черного экрана при запуске локации
    fade_from_black(screen)
    
    running = True
    while running:
        delta_time = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
                    # Проверяем, находится ли игрок в зоне перехода
                    if abs(character.rect.centerx - location_display_x) <= location_display_radius:
                        transition_to_location("prev")
                    elif abs(character.rect.centerx - right_location_display_x) <= location_display_radius:
                        transition_to_location("next")

        # Управление движением персонажа
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 10
        if keys[pygame.K_RIGHT]:
            dx += 10
        if keys[pygame.K_UP]:
            dy -= 10
        if keys[pygame.K_DOWN]:
            dy += 10

        character.update(dx, dy)
        character.rect.clamp_ip(boundary_rect)

        # Отрисовка
        screen.blit(background_image, (0, 0))
        all_sprites.draw(screen)
        
        # Отображение названий локаций при приближении
        if abs(character.rect.centerx - location_display_x) <= location_display_radius:
            location_name_surface = loud_font.render(prev_location_name, True, (255, 255, 255))
            location_name_rect = location_name_surface.get_rect(center=(location_display_x, screen_height // 2))
            screen.blit(location_name_surface, location_name_rect)
        
        if abs(character.rect.centerx - right_location_display_x) <= location_display_radius:
            location_name_surface = loud_font.render(next_location_name, True, (255, 255, 255))
            location_name_rect = location_name_surface.get_rect(center=(right_location_display_x, screen_height // 2))
            screen.blit(location_name_surface, location_name_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

main()
