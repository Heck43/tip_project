import pygame

class Ship:
    def __init__(self, length, x, y, ship_type, board):
        self.length = length
        self.hits = 0
        self.sunk = False
        self.x = x
        self.y = y
        self.horizontal = True
        self.is_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.cell_size = 40
        self.placed = False
        self.ship_type = ship_type
        self.board = board
        
    def draw(self, screen):
        if not self.placed:
            width = self.length * self.cell_size if self.horizontal else self.cell_size
            height = self.cell_size if self.horizontal else self.length * self.cell_size
            
            # Основной прямоугольник корабля
            rect = pygame.Rect(self.x, self.y, width, height)
            
            # Цвет корабля зависит от его размера
            colors = {
                4: (70, 130, 180),   # Линкор - темно-синий
                3: (100, 149, 237),  # Крейсер - синий
                2: (135, 206, 235),  # Эсминец - голубой
                1: (176, 224, 230)   # Катер - светло-голубой
            }
            ship_color = colors.get(self.length, (128, 128, 128))
            
            # Рисуем корпус корабля
            pygame.draw.rect(screen, ship_color, rect)
            
            # Добавляем обводку
            pygame.draw.rect(screen, (0, 0, 0), rect, 2)
            
            # Добавляем внутренние детали
            if self.horizontal:
                # Горизонтальные секции
                for i in range(1, self.length):
                    x = self.x + i * self.cell_size
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (x, self.y), 
                                   (x, self.y + height), 2)
            else:
                # Вертикальные секции
                for i in range(1, self.length):
                    y = self.y + i * self.cell_size
                    pygame.draw.line(screen, (0, 0, 0), 
                                   (self.x, y), 
                                   (self.x + width, y), 2)
            
            # Если корабль перетаскивается, добавляем подсветку
            if self.is_dragging:
                pygame.draw.rect(screen, (255, 215, 0), rect, 3)
    
    def start_drag(self, mouse_pos):
        self.is_dragging = True
        self.drag_offset_x = self.x - mouse_pos[0]
        self.drag_offset_y = self.y - mouse_pos[1]
    
    def update_position(self, mouse_pos):
        if self.is_dragging:
            self.x = mouse_pos[0] + self.drag_offset_x
            self.y = mouse_pos[1] + self.drag_offset_y
    
    def stop_drag(self):
        self.is_dragging = False
    
    def rotate(self):
        if not self.placed:
            self.horizontal = not self.horizontal
    
    def get_grid_position(self, board_x, board_y):
        rel_x = self.x - board_x
        rel_y = self.y - board_y
        grid_x = int(rel_x / self.cell_size)
        grid_y = int(rel_y / self.cell_size)
        return grid_x, grid_y
    
    def hit(self):
        self.hits += 1
        if self.hits >= self.length:
            self.sunk = True
            
    def is_sunk(self):
        return self.sunk

    def is_destroyed(self):
        """Проверяет, полностью ли уничтожен корабль"""
        # Проверяем все клетки корабля
        for x, y in self.get_all_cells():
            cell = self.board.cells[y][x]
            if not cell.was_shot:
                return False
        return True

    def get_all_cells(self):
        """Возвращает все клетки, занимаемые кораблём"""
        cells = []
        if self.horizontal:
            for dx in range(self.length):
                cells.append((self.x + dx, self.y))
        else:
            for dy in range(self.length):
                cells.append((self.x, self.y + dy))
        return cells
