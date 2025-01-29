import pygame
from player import Player
from cell import CellState

class Game:
    def __init__(self):
        pygame.init()
        self.width = 1024
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Морской бой")
        
        # Создаем игроков с их полями
        self.player1 = Player(50, 50, True)  # Левое поле, первый игрок
        self.player2 = Player(550, 50, False)  # Правое поле, второй игрок
        self.current_player = 1
        self.game_phase = "placing"  # "placing", "transition", "playing" или "game_over"
        self.winner = None
        self.transition_timer = 0
        self.show_transition = False
        
        # Размеры рамки подсветки
        self.highlight_padding = 10
        self.highlight_thickness = 3
        
    def handle_click(self, pos):
        if self.game_phase == "playing":
            target_player = self.player2 if self.current_player == 1 else self.player1
            cell = target_player.board.get_cell_at_pos(pos)
            
            if cell and cell.get_state() not in [CellState.HIT, CellState.MISS]:
                hit = target_player.receive_shot(cell.x, cell.y)
                if target_player.is_defeated():
                    self.game_phase = "game_over"
                    self.winner = self.current_player
                elif not hit:
                    self.current_player = 1 if self.current_player == 2 else 2
    
    def handle_mouse_down(self, pos):
        if self.game_phase == "placing":
            current_player = self.player1 if self.current_player == 1 else self.player2
            if current_player.handle_mouse_down(pos):
                return True
        return False
    
    def handle_mouse_up(self, pos):
        if self.game_phase == "placing":
            current_player = self.player1 if self.current_player == 1 else self.player2
            current_player.handle_mouse_up(pos)
            
            # Проверяем, все ли корабли расставлены
            if current_player.all_ships_placed():
                self.show_transition = True
                self.transition_timer = 180  # 3 секунды при 60 FPS
                self.game_phase = "transition"
    
    def handle_mouse_motion(self, pos):
        if self.game_phase == "placing":
            current_player = self.player1 if self.current_player == 1 else self.player2
            current_player.handle_mouse_motion(pos)
    
    def draw_transition_screen(self):
        self.screen.fill((0, 0, 0))  # Черный экран
        font = pygame.font.Font(None, 48)
        if self.current_player == 1:
            text = "Передайте ход Игроку 2"
        else:
            text = "Приготовьтесь к битве!"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surface, text_rect)
        
        # Добавляем таймер
        timer_text = f"Подождите: {self.transition_timer // 60 + 1}"
        timer_surface = font.render(timer_text, True, (255, 255, 255))
        timer_rect = timer_surface.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(timer_surface, timer_rect)
    
    def draw_board_highlight(self, x, y):
        # Рисуем рамку вокруг активного поля
        rect = pygame.Rect(
            x - self.highlight_padding,
            y - self.highlight_padding,
            400 + self.highlight_padding * 2,  # 10 клеток по 40 пикселей
            400 + self.highlight_padding * 2
        )
        pygame.draw.rect(self.screen, (255, 215, 0), rect, self.highlight_thickness)
        
        # Добавляем текст "Ваше поле" или "Поле противника"
        font = pygame.font.Font(None, 30)
        if self.game_phase == "placing":
            text = "Ваше поле"
        else:
            if (x < 500 and self.current_player == 1) or (x > 500 and self.current_player == 2):
                text = "Ваше поле"
            else:
                text = "Поле противника"
        
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(centerx=x + 200, y=y - 30)
        self.screen.blit(text_surface, text_rect)
    
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.show_transition:  # Левый клик
                        if self.game_phase == "playing":
                            self.handle_click(event.pos)
                        else:
                            self.handle_mouse_down(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and not self.show_transition:
                        self.handle_mouse_up(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.game_phase == "placing":
                        current_player = self.player1 if self.current_player == 1 else self.player2
                        current_player.handle_rotation()
                    elif event.key == pygame.K_r and self.game_phase == "game_over":
                        # Рестарт игры
                        self.__init__()
            
            # Обработка перехода между игроками
            if self.game_phase == "transition":
                self.transition_timer -= 1
                if self.transition_timer <= 0:
                    self.show_transition = False
                    if self.current_player == 1:
                        self.current_player = 2
                        self.game_phase = "placing"
                    else:
                        self.current_player = 1
                        self.game_phase = "playing"
            
            # Отрисовка
            if self.show_transition:
                self.draw_transition_screen()
            else:
                self.screen.fill((200, 200, 255))
                
                if self.game_phase == "placing":
                    # Показываем только поле текущего игрока во время расстановки
                    current_player = self.player1 if self.current_player == 1 else self.player2
                    current_player.draw(self.screen)
                    # Подсвечиваем активное поле
                    self.draw_board_highlight(
                        50 if self.current_player == 1 else 550,
                        50
                    )
                else:
                    # Во время игры показываем оба поля без кораблей
                    self.player1.draw(self.screen, is_opponent=True)
                    self.player2.draw(self.screen, is_opponent=True)
                    # Подсвечиваем поле противника (куда нужно стрелять)
                    self.draw_board_highlight(
                        550 if self.current_player == 1 else 50,
                        50
                    )
                
                # Отображение текущей фазы и игрока
                font = pygame.font.Font(None, 36)
                if self.game_phase == "placing":
                    text = f"Игрок {self.current_player} расставляет корабли (Пробел для поворота)"
                elif self.game_phase == "playing":
                    text = f"Ход игрока {self.current_player}"
                else:  # game_over
                    text = f"Игрок {self.winner} победил! Нажмите R для новой игры"
                
                text_surface = font.render(text, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(self.width // 2, 500))
                self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
