import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Меню с настройками")

# Определение цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)  # Фиолетовый цвет
RED = (255, 0, 0)
# Шрифты
font = pygame.font.Font(None, 36)

# Глобальные настройки
settings = {
    "graphics": "Низкие",
    "hdr": False,
    "controls": "Стандартные"
}

# Функция для отрисовки текста
def draw_text(text, font, surface, x, y):
    textobj = font.render(text, True, BLACK)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Функция для отображения меню настроек
def settings_menu():
    graphics_rect = pygame.Rect(20, 60, 200, 30)
    hdr_rect = pygame.Rect(20, 100, 50, 30)
    controls_rect = pygame.Rect(20, 140, 200, 30)

    graphics_options = ["Низкие", "Средние", "Высокие"]
    graphics_index = graphics_options.index(settings["graphics"])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if graphics_rect.collidepoint(event.pos):
                    graphics_index = (graphics_index + 1) % len(graphics_options)
                    settings["graphics"] = graphics_options[graphics_index]
                if hdr_rect.collidepoint(event.pos):
                    settings["hdr"] = not settings["hdr"]

        # Заливка фона
        screen.fill(PURPLE)  # Заменяем цвет фона на фиолетовый

        # Отрисовка элементов меню
        draw_text('Настройки', font, screen, 20, 20)
        pygame.draw.rect(screen, WHITE, graphics_rect)
        draw_text('Графика: ' + settings["graphics"], font, screen, graphics_rect.x + 5, graphics_rect.y + 5)
        pygame.draw.rect(screen, WHITE, hdr_rect)
        if settings["hdr"]:
            pygame.draw.rect(screen, GREEN, (hdr_rect.x + 5, hdr_rect.y + 5, 40, 20))
        else:
            pygame.draw.rect(screen, RED, (hdr_rect.x + 5, hdr_rect.y + 5, 40, 20))
        draw_text('HDR', font, screen, hdr_rect.x + 55, hdr_rect.y + 5)
        draw_text('Управление: ' + settings["controls"], font, screen, 20, 140)
        draw_text('Нажмите ESC для выхода', font, screen, 20, 220)

        # Обновление экрана
        pygame.display.flip()

# Основной игровой цикл
def main():
    settings_menu()  # Открываем меню настроек сразу при запуске

# Запуск игры
main()