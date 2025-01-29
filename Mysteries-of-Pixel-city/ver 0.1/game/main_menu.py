import pygame
import sys
import math
import threading

pygame.init()

screen_width = 1628
screen_height = 1017
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mysteries of the Pixel City")

icon = pygame.image.load('image/icon.png')
pygame.display.set_icon(icon)

background_image = pygame.image.load('image/background.jpg')

clock = pygame.time.Clock()

font = pygame.font.Font(None, 74)

menu_text = font.render('Mysteries of the Pixel City', True, (237, 201, 0))
menu_text_rect = menu_text.get_rect(center=(screen_width // 2, 300))

loading_complete = False
loading_in_progress = False

class Button:
    def __init__(self, text, pos):
        self.font = pygame.font.Font(None, 50)
        self.text = text
        self.rect = pygame.Rect(pos[0], pos[1], 200, 60)
        self.color = (128, 0, 128)
        self.hover_color = (160, 0, 160)
        self.pressed_color = (255, 0, 255)
        self.current_color = self.color
        self.loading_thread = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            if pygame.mouse.get_pressed()[0]:
                self.current_color = self.pressed_color
                if self.text == "Play":
                    if not self.loading_thread or not self.loading_thread.is_alive():
                        self.loading_thread = threading.Thread(target=load_level)
                        self.loading_thread.start()
        else:
            self.current_color = self.color

def draw_spinner(surface, center, angle):
    radius = 20
    num_segments = 6
    for i in range(num_segments):
        segment_angle = angle + (i * (360 / num_segments))
        x = center[0] + radius * math.cos(math.radians(segment_angle))
        y = center[1] + radius * math.sin(math.radians(segment_angle))
        
        # Изменяем размер точки в зависимости от ее положения
        size = int(5 + 3 * math.sin(math.radians(segment_angle - angle)))
        
        # Изменяем прозрачность в зависимости от положения
        alpha = int(255 * (1 - 0.7 * ((i + 1) / num_segments)))
        
        color = (255, 255, 255, alpha)
        
        # Рисуем круг с изменяющимся размером
        pygame.draw.circle(surface, color, (int(x), int(y)), size)

def load_level():
    global loading_complete, loading_in_progress
    loading_in_progress = True
    
    # Имитация загрузки
    pygame.time.wait(3000)  # Ждем 3 секунды

    loading_complete = True
    loading_in_progress = False

def main_menu():
    global loading_complete, loading_in_progress
    button = Button("Play", (screen_width // 2 - 100, screen_height // 2 - 30))
    loading_complete = False
    
    spinner_angle = 0
    start_time = pygame.time.get_ticks()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        spinner_angle = (elapsed_time // 10) % 360  # Медленное вращение

        if not loading_in_progress:
            screen.blit(background_image, (0, 0))
            screen.blit(menu_text, menu_text_rect)
            button.update()
            button.draw(screen)
        else:
            # Отображаем загрузочный экран, пока идет загрузка
            loading_surface = pygame.Surface((screen_width, screen_height))
            loading_surface.fill((0, 0, 0))
            loading_text = font.render('Loading...', True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(screen_width // 2, screen_height // 2))
            loading_surface.blit(loading_text, loading_rect)
            
            # Анимируем спиннер
            draw_spinner(loading_surface, (screen_width // 2, screen_height // 2 + 60), spinner_angle)
            
            screen.blit(loading_surface, (0, 0))
        
        if loading_complete:
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill((0, 0, 0))
            for alpha in range(0, 255, 5):
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
                pygame.display.flip()
                clock.tick(60)

            start_game()

        pygame.display.flip()
        clock.tick(60)

def start_game():
    import location
    location.main()

if __name__ == "__main__":
    main_menu()