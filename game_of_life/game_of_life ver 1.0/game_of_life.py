import pygame
import numpy as np
import time
from math import sin
import pygame.gfxdraw

# Инициализация pygame
pygame.init()
pygame.font.init()

# Константы
WIDTH, HEIGHT = 1000, 800
CELL_SIZE = 15
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
STATS_HEIGHT = 50
FPS = 60
ANIMATION_SPEED = 0.05

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
TEAM_BLUE = 1
TEAM_RED = 2
CURRENT_MODE = "classic"  # или "battle"

# Настройка экрана
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
GAME_HEIGHT = HEIGHT - STATS_HEIGHT
COLS, ROWS = WIDTH // CELL_SIZE, GAME_HEIGHT // CELL_SIZE
font = pygame.font.SysFont('Arial', 16)

# Создание сеток
grid = np.zeros((COLS, ROWS))  # 0 - пусто, 1 - синие, 2 - красные
age_grid = np.zeros((COLS, ROWS))

# Предустановленные фигуры
PATTERNS = {
    'глайдер': np.array([[0, 1, 0],
                         [0, 0, 1],
                         [1, 1, 1]]),
    'осциллятор': np.array([[1, 1, 1]]),
    'блок': np.array([[1, 1],
                      [1, 1]])
}

def place_pattern(pattern, pos):
    x, y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
    h, w = pattern.shape
    grid[x:x+h, y:y+w] = pattern

def count_neighbors(grid, x, y):
    total = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            row = (x + i + COLS) % COLS
            col = (y + j + ROWS) % ROWS
            total += grid[row, col]
    total -= grid[x, y]
    return total

def update_grid():
    global grid, age_grid
    new_grid = grid.copy()
    for i in range(COLS):
        for j in range(ROWS):
            neighbors = count_neighbors(grid, i, j)
            if grid[i, j] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[i, j] = 0
                    age_grid[i, j] = 0
                else:
                    age_grid[i, j] += 1
            else:
                if neighbors == 3:
                    new_grid[i, j] = 1
                    age_grid[i, j] = 1
    grid = new_grid

def update_grid_battle():
    global grid, age_grid
    new_grid = grid.copy()
    
    for i in range(COLS):
        for j in range(ROWS):
            if grid[i, j] == 0:
                continue
                
            team = grid[i, j]
            enemy_team = TEAM_RED if team == TEAM_BLUE else TEAM_BLUE
            
            # Подсчет врагов вокруг
            enemy_count = 0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if di == 0 and dj == 0:
                        continue
                    ni = (i + di + COLS) % COLS
                    nj = (j + dj + ROWS) % ROWS
                    if grid[ni, nj] == enemy_team:
                        enemy_count += 1
            
            # Вычисляем шанс быть съеденным в зависимости от количества врагов
            eat_chance = 0
            if enemy_count >= 2:
                eat_chance = (enemy_count - 1) * 0.15  # 15% за каждого врага после первого
            
            # Если клетку съели
            if np.random.random() < eat_chance:
                new_grid[i, j] = enemy_team
                age_grid[i, j] = 1
            else:
                # Клетка стареет
                age_grid[i, j] += 1
                
                # Случайное распространение
                spread_chance = 0.05 + (age_grid[i, j] - 5) * 0.02  # Увеличиваем шанс с возрастом
                if age_grid[i, j] > 5 and np.random.random() < spread_chance:
                    # Выбор случайной соседней пустой клетки
                    empty_neighbors = []
                    for di in range(-1, 2):
                        for dj in range(-1, 2):
                            if di == 0 and dj == 0:
                                continue
                            ni = (i + di + COLS) % COLS
                            nj = (j + dj + ROWS) % ROWS
                            if grid[ni, nj] == 0:
                                empty_neighbors.append((ni, nj))
                    
                    if empty_neighbors:  # Если есть пустые соседние клетки
                        ni, nj = empty_neighbors[np.random.randint(len(empty_neighbors))]
                        new_grid[ni, nj] = team
                        age_grid[ni, nj] = 1
    
    grid = new_grid

def get_cell_color(team, age, pulse):
    if team == 0:
        return BLACK
    
    if team == TEAM_BLUE:
        if age == 1:
            c = int(128 * pulse)
            return (c, c, 255)
        elif age < 5:
            return (0, 0, int(255 * pulse))
        else:
            return (0, int(128 * pulse), 255)
    else:  # TEAM_RED
        if age == 1:
            c = int(128 * pulse)
            return (255, c, c)
        elif age < 5:
            return (int(255 * pulse), 0, 0)
        else:
            return (255, int(128 * pulse), 0)

# Основной цикл игры
running = True
paused = True
selected_pattern = None
drawing = False  # Флаг для отслеживания зажатия кнопки мыши
animation_time = 0  # Счетчик времени для анимации
clock = pygame.time.Clock()  # Для контроля FPS

# Создадим поверхности для отрисовки
game_surface = pygame.Surface((WIDTH, GAME_HEIGHT))
stats_surface = pygame.Surface((WIDTH, STATS_HEIGHT))

current_team = TEAM_BLUE

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_c:  # Очистка поля
                grid.fill(0)
                age_grid.fill(0)
            elif event.key == pygame.K_UP:  # Увеличение скорости
                FPS = min(FPS + 10, 120)
            elif event.key == pygame.K_DOWN:  # Уменьшение скорости
                FPS = max(FPS - 10, 10)
            elif event.key == pygame.K_1:  # Выбор глайдера
                selected_pattern = 'глайдер'
            elif event.key == pygame.K_2:  # Выбор осциллятора
                selected_pattern = 'осциллятор'
            elif event.key == pygame.K_3:  # Выбор блока
                selected_pattern = 'блок'
            elif event.key == pygame.K_ESCAPE:  # Выход по Escape
                running = False
            elif event.key == pygame.K_m:  # Переключение режима
                CURRENT_MODE = "battle" if CURRENT_MODE == "classic" else "classic"
                grid.fill(0)
                age_grid.fill(0)
            elif event.key == pygame.K_b:  # Выбор синей команды
                selected_pattern = None
                current_team = TEAM_BLUE
            elif event.key == pygame.K_r:  # Выбор красной команды
                selected_pattern = None
                current_team = TEAM_RED
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            pos = pygame.mouse.get_pos()
            if pos[1] < GAME_HEIGHT:
                i, j = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                if 0 <= i < COLS and 0 <= j < ROWS:
                    if selected_pattern:
                        place_pattern(PATTERNS[selected_pattern], pos)
                        selected_pattern = None
                    else:
                        if CURRENT_MODE == "classic":
                            grid[i, j] = not grid[i, j]
                            age_grid[i, j] = 1 if grid[i, j] else 0
                        else:
                            if grid[i, j] == current_team:
                                grid[i, j] = 0
                                age_grid[i, j] = 0
                            else:
                                grid[i, j] = current_team
                                age_grid[i, j] = 1
        
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            
        elif event.type == pygame.MOUSEMOTION and drawing:
            pos = pygame.mouse.get_pos()
            if pos[1] < GAME_HEIGHT:  # Проверка, что курсор в пределах игрового поля
                i, j = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                if 0 <= i < COLS and 0 <= j < ROWS:
                    if CURRENT_MODE == "classic" and not selected_pattern:
                        grid[i, j] = 1
                        age_grid[i, j] = 1
                    elif CURRENT_MODE == "battle" and not selected_pattern:
                        grid[i, j] = current_team
                        age_grid[i, j] = 1

    animation_time += 1

    # Очищаем игровую поверхность
    game_surface.fill(BLACK)

    # Рассчитываем pulse один раз за кадр
    pulse = abs(sin(animation_time * ANIMATION_SPEED)) * 0.3 + 0.7
    cell_size = int(CELL_SIZE * (0.95 + 0.05 * sin(animation_time * ANIMATION_SPEED)))
    offset = (CELL_SIZE - cell_size) // 2

    # Отрисовка клеток
    alive_cells = np.where(grid != 0)
    for x, y in zip(alive_cells[0], alive_cells[1]):
        color = get_cell_color(grid[x, y], age_grid[x, y], pulse)
        pygame.draw.rect(game_surface, color,
                        (x * CELL_SIZE + offset,
                         y * CELL_SIZE + offset,
                         cell_size - 1,
                         cell_size - 1))

    # Отрисовка статистики
    stats_surface.fill(GRAY)
    living_cells = np.sum(grid)
    stats_text = f"Режим: {'Классический' if CURRENT_MODE == 'classic' else 'Битва'} "
    if CURRENT_MODE == "battle":
        blue_cells = np.sum(grid == TEAM_BLUE)
        red_cells = np.sum(grid == TEAM_RED)
        stats_text += f"Синие: {blue_cells} Красные: {red_cells} "
        stats_text += f"Команда: {'Синие' if current_team == TEAM_BLUE else 'Красные'} "
    else:
        stats_text += f"Живые клетки: {living_cells} "
    stats_text += f"Скорость: {FPS} FPS "
    stats_text += f"{'На паузе' if paused else 'Играет'} "
    text_surface = font.render(stats_text, True, WHITE)
    stats_surface.blit(text_surface, (10, 15))

    # Отрисовка на экран
    screen.fill(BLACK)
    screen.blit(game_surface, (0, 0))
    screen.blit(stats_surface, (0, GAME_HEIGHT))

    if not paused:
        if CURRENT_MODE == "classic":
            update_grid()
        else:
            update_grid_battle()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit() 