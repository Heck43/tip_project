from enum import Enum

class CellState(Enum):
    EMPTY = 0
    BARRIER = 1
    SHIP = 2
    CHECKED = 3
    HIT = 4
    MISS = 5

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = CellState.EMPTY
        
    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def is_empty(self):
        return self.state == CellState.EMPTY
    
    def is_ship(self):
        return self.state == CellState.SHIP
    
    def is_hit(self):
        return self.state == CellState.HIT
