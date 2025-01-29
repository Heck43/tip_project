import pygame
from cell import Cell, CellState

class Board:
    def __init__(self, x, y, cell_size=40):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.width = 10
        self.height = 10
        self.grid = [[Cell(i, j) for j in range(self.height)] for i in range(self.width)]
        self.surface = pygame.Surface((self.width * cell_size, self.height * cell_size))
        
    def draw(self, screen, hide_ships=False):
        self.surface.fill((255, 255, 255))
        for i in range(self.width):
            for j in range(self.height):
                cell = self.grid[i][j]
                rect = pygame.Rect(i * self.cell_size, j * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.surface, (0, 0, 0), rect, 1)
                
                if cell.get_state() == CellState.SHIP:
                    if not hide_ships:  # Показываем корабли только если hide_ships=False
                        pygame.draw.rect(self.surface, (128, 128, 128), rect)
                elif cell.get_state() == CellState.HIT:
                    pygame.draw.rect(self.surface, (255, 0, 0), rect)
                elif cell.get_state() == CellState.MISS:
                    pygame.draw.circle(self.surface, (0, 0, 255), 
                                    (i * self.cell_size + self.cell_size // 2, 
                                     j * self.cell_size + self.cell_size // 2), 5)
                    
        screen.blit(self.surface, (self.x, self.y))
        
    def get_cell_at_pos(self, mouse_pos):
        rel_x = mouse_pos[0] - self.x
        rel_y = mouse_pos[1] - self.y
        
        if 0 <= rel_x < self.width * self.cell_size and 0 <= rel_y < self.height * self.cell_size:
            cell_x = rel_x // self.cell_size
            cell_y = rel_y // self.cell_size
            return self.grid[cell_x][cell_y]
        return None
    
    def can_place_ship(self, x, y, length, horizontal):
        if horizontal:
            if x + length > self.width:
                return False
            for i in range(max(0, x-1), min(self.width, x+length+1)):
                for j in range(max(0, y-1), min(self.height, y+2)):
                    if not self.grid[i][j].is_empty():
                        return False
        else:
            if y + length > self.height:
                return False
            for i in range(max(0, x-1), min(self.width, x+2)):
                for j in range(max(0, y-1), min(self.height, y+length+1)):
                    if not self.grid[i][j].is_empty():
                        return False
        return True
    
    def place_ship(self, x, y, length, horizontal):
        if self.can_place_ship(x, y, length, horizontal):
            if horizontal:
                for i in range(x, x + length):
                    self.grid[i][y].set_state(CellState.SHIP)
            else:
                for j in range(y, y + length):
                    self.grid[x][j].set_state(CellState.SHIP)
            return True
        return False

    def mark_around_destroyed_ship(self, ship):
        """Отмечает клетки вокруг уничтоженного корабля как пустые (с крестиком)"""
        # Получаем все клетки вокруг корабля
        cells_to_mark = set()
        for x, y in ship.get_all_cells():
            # Проверяем все соседние клетки
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    new_x, new_y = x + dx, y + dy
                    # Проверяем, что клетка находится в пределах поля
                    if 0 <= new_x < self.width and 0 <= new_y < self.height:
                        # Не отмечаем клетки, где находится сам корабль
                        if not any(new_x == ship_x and new_y == ship_y 
                                 for ship_x, ship_y in ship.get_all_cells()):
                            cells_to_mark.add((new_x, new_y))
        
        # Отмечаем все найденные клетки как пустые (с крестиком)
        for x, y in cells_to_mark:
            self.grid[y][x].set_state(CellState.MISS)

    def shoot(self, x, y):
        """Выстрел по указанным координатам"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False, None
        
        cell = self.grid[x][y]
        if cell.get_state() != CellState.EMPTY:
            return False, None
            
        # Если в клетке есть корабль
        if cell.get_state() == CellState.SHIP:
            cell.set_state(CellState.HIT)
            # Проверяем, уничтожен ли корабль полностью
            # NOTE: This part is not implemented as the ship object is not defined in the given code
            # if ship.is_destroyed():
            #     # Отмечаем клетки вокруг уничтоженного корабля
            #     self.mark_around_destroyed_ship(ship)
            return True, True
        
        cell.set_state(CellState.MISS)
        return True, False
