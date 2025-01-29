import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((1628, 1017))

pygame.display.set_caption("Mysteries of the Pixel City")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
background_image = pygame.image.load('background.jpg')
clock = pygame.time.Clock()
# Устанавливаем шрифт и размер
font = pygame.font.Font(None, 74)  # None - использовать системный шрифт, 74 - размер шрифта

# Создаем текст
text = font.render('Mysteries of the Pixel City', True, (0, 0, 0))  # Черный цвет текста

# Получаем прямоугольник текста для позиционирования
text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
running = True
while running:
    scren = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    screen.blit(background_image, (0, 0))
    clock.tick(60)
    screen.blit(text, text_rect)
                        

    
    