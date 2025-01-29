import pygame
from board import Board
from ship import Ship
from cell import CellState

class Player:
    def __init__(self, x, y, is_first_player=True):
        self.board = Board(x, y)
        self.ships = []
        self.available_ships = []  # Корабли для размещения
        self.dragging_ship = None
        self.board_x = x
        self.board_y = y
        self.is_first_player = is_first_player
        self.initialize_ships()
        
    def initialize_ships(self):
        # Создаем корабли для размещения
        ship_configs = [
            {"length": 4, "count": 1, "name": "Линкор"},
            {"length": 3, "count": 2, "name": "Крейсер"},
            {"length": 2, "count": 3, "name": "Эсминец"},
            {"length": 1, "count": 4, "name": "Катер"}
        ]
        
        # Базовые отступы для кораблей
        if self.is_first_player:
            base_x = self.board_x + 450
        else:
            base_x = self.board_x - 350
            
        y_offset = self.board_y + 30
        
        # Расставляем корабли по группам
        for ship_type in ship_configs:
            # Добавляем корабли одного типа
            for i in range(ship_type["count"]):
                x = base_x + (i * 80)
                ship = Ship(ship_type["length"], x, y_offset, ship_type["name"], self.board)
                self.available_ships.append(ship)
            
            # Переходим к следующей группе кораблей
            y_offset += 100
    
    def handle_mouse_down(self, pos):
        # Проверяем, не начали ли тащить корабль
        for ship in self.available_ships:
            if not ship.placed:
                width = ship.length * ship.cell_size if ship.horizontal else ship.cell_size
                height = ship.cell_size if ship.horizontal else ship.length * ship.cell_size
                ship_rect = pygame.Rect(ship.x, ship.y, width, height)
                
                if ship_rect.collidepoint(pos):
                    ship.start_drag(pos)
                    self.dragging_ship = ship
                    return True
        return False
    
    def handle_mouse_up(self, pos):
        if self.dragging_ship:
            # Получаем позицию на сетке
            grid_x, grid_y = self.dragging_ship.get_grid_position(self.board_x, self.board_y)
            
            # Пытаемся разместить корабль на доске
            if self.board.can_place_ship(grid_x, grid_y, self.dragging_ship.length, 
                                       self.dragging_ship.horizontal):
                self.board.place_ship(grid_x, grid_y, self.dragging_ship.length, 
                                    self.dragging_ship.horizontal)
                self.dragging_ship.placed = True
                self.ships.append(self.dragging_ship)
            else:
                # Возвращаем корабль на исходную позицию
                self._reset_ship_position(self.dragging_ship)
            
            self.dragging_ship.stop_drag()
            self.dragging_ship = None
    
    def _reset_ship_position(self, ship):
        # Находим все корабли того же типа
        ships_of_same_type = [s for s in self.available_ships if s.length == ship.length]
        # Находим позицию корабля среди кораблей того же типа
        index = ships_of_same_type.index(ship)
        
        # Определяем базовую позицию X
        if self.is_first_player:
            base_x = self.board_x + 450
        else:
            base_x = self.board_x - 350
            
        # Находим первый корабль этого типа для определения Y позиции
        first_ship_of_type = ships_of_same_type[0]
        
        # Устанавливаем позицию
        ship.x = base_x + (index * 80)
        ship.y = first_ship_of_type.y
    
    def handle_mouse_motion(self, pos):
        if self.dragging_ship:
            self.dragging_ship.update_position(pos)
    
    def handle_rotation(self):
        if self.dragging_ship:
            self.dragging_ship.rotate()
    
    def receive_shot(self, x, y):
        cell = self.board.grid[x][y]
        if cell.is_ship():
            cell.set_state(CellState.HIT)
            return True
        cell.set_state(CellState.MISS)
        return False
    
    def all_ships_placed(self):
        return all(ship.placed for ship in self.available_ships)
    
    def is_defeated(self):
        for i in range(self.board.width):
            for j in range(self.board.height):
                if self.board.grid[i][j].get_state() == CellState.SHIP:
                    return False
        return True
        
    def draw(self, screen, is_opponent=False):
        # Рисуем доску
        self.board.draw(screen, hide_ships=is_opponent)
        
        # Рисуем доступные корабли и их названия
        if not is_opponent:
            # Определяем базовую позицию X для заголовков
            base_x = self.board_x + 450 if self.is_first_player else self.board_x - 350
            
            # Сначала группируем корабли по типам
            ship_groups = {}
            for ship in self.available_ships:
                if not ship.placed and not ship.is_dragging:  
                    if ship.ship_type not in ship_groups:
                        ship_groups[ship.ship_type] = []
                    ship_groups[ship.ship_type].append(ship)
            
            # Отрисовываем заголовки только если есть неразмещенные корабли этого типа
            for ship_type, ships in ship_groups.items():
                if ships:  
                    # Берем Y-координату первого корабля в группе
                    header_y = ships[0].y - 25
                    # Рисуем заголовок типа корабля
                    font = pygame.font.Font(None, 24)
                    text = font.render(ship_type, True, (0, 0, 0))
                    screen.blit(text, (base_x, header_y))
            
            # Отрисовываем все корабли
            for ship in self.available_ships:
                if not ship.placed:
                    ship.draw(screen)
