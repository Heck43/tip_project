import sys
import os
import json
import time
import random
import keyboard
import pygame
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                            QDoubleSpinBox, QTabWidget, QGridLayout,
                            QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QIcon
from settings import (SoundSettingsTab, ShapeSettingsTab, MainSettingsTab,
                     KeybindSettingsTab, PhysicsSettingsTab)

# Константы
DEFAULT_SETTINGS = {
    'balls': {
        'count': 5,
        'size': 20,
        'shape': 'Круг',
        'roundness': 0,
        'random_motion': False
    },
    'physics': {
        'gravity': 0.5,
        'bounce_energy': 0.8,
        'friction': 0.999
    },
    'keybinds': {
        'exit': 'esc',
        'add_ball': 'space',
        'clear_balls': 'c',
        'open_settings': 's'
    },
    'sound': {
        'selected_sound': '',
        'volume': 0.5
    }
}

class Simulation:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.collision_sound = None
        self.balls = []
        
    def add_ball(self, x, y, radius=20, dx=0, dy=0):
        ball = {
            'x': x,
            'y': y,
            'radius': radius,
            'dx': dx,
            'dy': dy
        }
        self.balls.append(ball)
        
    def update(self, dt):
        for ball in self.balls:
            # Update position
            ball['x'] += ball['dx'] * dt
            ball['y'] += ball['dy'] * dt
            
            # Apply gravity
            ball['dy'] += 9.81 * dt
            
            # Wall collisions
            if ball['x'] - ball['radius'] < 0:
                ball['x'] = ball['radius']
                ball['dx'] *= -0.8
                if self.collision_sound and abs(ball['dx']) > 1:
                    self.collision_sound.play()
            elif ball['x'] + ball['radius'] > self.width:
                ball['x'] = self.width - ball['radius']
                ball['dx'] *= -0.8
                if self.collision_sound and abs(ball['dx']) > 1:
                    self.collision_sound.play()
                    
            if ball['y'] - ball['radius'] < 0:
                ball['y'] = ball['radius']
                ball['dy'] *= -0.8
                if self.collision_sound and abs(ball['dy']) > 1:
                    self.collision_sound.play()
            elif ball['y'] + ball['radius'] > self.height:
                ball['y'] = self.height - ball['radius']
                ball['dy'] *= -0.8
                if self.collision_sound and abs(ball['dy']) > 1:
                    self.collision_sound.play()
                    
            # Apply friction
            ball['dx'] *= 0.999
            ball['dy'] *= 0.999

    def clear_balls(self):
        self.balls.clear()

class SimulationWidget(QWidget):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings if settings else DEFAULT_SETTINGS.copy()
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background: transparent;")
        
        # Получаем размеры экрана
        screen = QApplication.primaryScreen().geometry()
        self.frame_x = 0
        self.frame_y = 0
        self.frame_width = screen.width()
        self.frame_height = screen.height()
        
        # Инициализация pygame mixer для звуков
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.init_physics()
        
        # Список шариков
        self.balls = []
        for _ in range(self.settings['balls']['count']):
            self.add_ball()
        
        # Таймер для обновления
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # ~60 FPS
        
        # Время последнего взаимодействия
        self.last_interaction_time = 0
        
        # Таймер для автоматического броска
        self.auto_throw_timer = QTimer()
        self.auto_throw_timer.timeout.connect(self.auto_throw_ball)
        self.auto_throw_timer.start(1000)
        
        # Звук столкновения
        self.collision_sound = None
    
    def init_physics(self):
        # Параметры физики
        self.smoothing = 0.2
        self.throw_power = 3.0
        self.gravity = self.settings['physics']['gravity']
        self.bounce_energy = self.settings['physics']['bounce_energy']
        self.friction = self.settings['physics']['friction']
        self.air_resistance = 0.9999
        self.ball_bounce_energy = 0.95
    
    def update_settings(self, new_settings):
        try:
            old_count = len(self.balls)
            new_count = new_settings['balls']['count']
            
            # Обновляем настройки
            self.settings = new_settings.copy()
            
            # Обновляем физические параметры
            self.init_physics()
            
            # Обновляем размер существующих шариков
            for ball in self.balls:
                ball.radius = self.settings['balls']['size']
            
            # Добавляем или удаляем шарики при необходимости
            if new_count > old_count:
                for _ in range(new_count - old_count):
                    self.add_ball()
            elif new_count < old_count:
                self.balls = self.balls[:new_count]
            
            self.update()
        except Exception as e:
            print(f"Error updating simulation settings: {e}")
    
    def set_collision_sound(self, sound):
        self.collision_sound = sound
    
    def add_ball(self):
        x = random.randint(self.frame_x + 50, self.frame_x + self.frame_width - 50)
        y = random.randint(self.frame_y + 50, self.frame_y + self.frame_height - 50)
        self.balls.append(Ball(x, y, self.settings['balls']['size']))
    
    def clear_balls(self):
        self.balls.clear()
        self.update()
    
    def auto_throw_ball(self):
        if self.settings['balls'].get('random_motion', False):
            self.last_interaction_time += 1
            if self.last_interaction_time >= 10:
                for ball in self.balls:
                    ball.speed_x = random.uniform(-20, 20)
                    ball.speed_y = random.uniform(-20, 20)
                self.last_interaction_time = 0
    
    def update_position(self):
        for ball in self.balls:
            if ball.is_dragging:
                # Если шарик захвачен, устанавливаем его позицию в точку захвата
                old_x = ball.x
                old_y = ball.y
                ball.x = ball.drag_x
                ball.y = ball.drag_y
                # Вычисляем скорость движения захваченного шарика
                ball.speed_x = (ball.x - old_x) * 0.5  # Уменьшаем передачу скорости
                ball.speed_y = (ball.y - old_y) * 0.5
            else:
                speed = (ball.speed_x ** 2 + ball.speed_y ** 2) ** 0.5
                gravity_scale = min(1.0, 15.0 / (speed + 1))
                ball.speed_y += self.gravity * gravity_scale
                
                ball.speed_x *= self.friction
                ball.speed_y *= self.friction
                
                ball.x += ball.speed_x
                ball.y += ball.speed_y
            
            # Wall collisions
            if ball.x - ball.radius < self.frame_x:
                ball.x = self.frame_x + ball.radius
                if not ball.is_dragging:
                    ball.speed_x = abs(ball.speed_x) * self.bounce_energy
                if self.collision_sound and abs(ball.speed_x) > 1:
                    self.collision_sound.play()
            elif ball.x + ball.radius > self.frame_x + self.frame_width:
                ball.x = self.frame_x + self.frame_width - ball.radius
                if not ball.is_dragging:
                    ball.speed_x = -abs(ball.speed_x) * self.bounce_energy
                if self.collision_sound and abs(ball.speed_x) > 1:
                    self.collision_sound.play()
            
            if ball.y - ball.radius < self.frame_y:
                ball.y = self.frame_y + ball.radius
                if not ball.is_dragging:
                    ball.speed_y = abs(ball.speed_y) * self.bounce_energy
                if self.collision_sound and abs(ball.speed_y) > 1:
                    self.collision_sound.play()
            elif ball.y + ball.radius > self.frame_y + self.frame_height:
                ball.y = self.frame_y + self.frame_height - ball.radius
                if not ball.is_dragging:
                    ball.speed_y = -abs(ball.speed_y) * self.bounce_energy
                    ball.speed_x *= self.friction
                if self.collision_sound and abs(ball.speed_y) > 1:
                    self.collision_sound.play()
            
            # Ball-to-ball collisions
            for other_ball in self.balls:
                if ball != other_ball:
                    dx = ball.x - other_ball.x
                    dy = ball.y - other_ball.y
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    
                    if distance < ball.radius + other_ball.radius:
                        # Normal vector
                        nx = dx / distance
                        ny = dy / distance
                        
                        # Separate balls
                        overlap = (ball.radius + other_ball.radius - distance) / 2
                        if not ball.is_dragging:
                            ball.x += overlap * nx
                        if not other_ball.is_dragging:
                            other_ball.x -= overlap * nx
                        if not ball.is_dragging:
                            ball.y += overlap * ny
                        if not other_ball.is_dragging:
                            other_ball.y -= overlap * ny
                        
                        # Если хотя бы один из шариков не захвачен, обрабатываем столкновение
                        if not other_ball.is_dragging:
                            # Relative velocity
                            dvx = ball.speed_x - other_ball.speed_x
                            dvy = ball.speed_y - other_ball.speed_y
                            
                            # Collision response
                            dot_product = dvx * nx + dvy * ny
                            
                            # Apply collision impulse
                            impulse = (1 + self.ball_bounce_energy) * dot_product / 2
                            
                            # Update velocities
                            if not ball.is_dragging:
                                ball.speed_x -= impulse * nx
                                ball.speed_y -= impulse * ny
                            
                            # Для незахваченного шарика применяем нормальный импульс
                            if ball.is_dragging:
                                # Если ударяющий шарик захвачен, передаем больше импульса
                                impulse_scale = 1.2
                            else:
                                # Если оба шарика свободны, используем нормальный импульс
                                impulse_scale = 1.0
                            
                            other_ball.speed_x += impulse * nx * impulse_scale
                            other_ball.speed_y += impulse * ny * impulse_scale
                            
                            # Play collision sound
                            if self.collision_sound and abs(dot_product) > 1:
                                self.collision_sound.play()
            
            if not ball.is_dragging:
                if abs(ball.speed_x) < 0.1 and abs(ball.speed_y) < 0.1:
                    ball.speed_x = 0
                    ball.speed_y = 0
            
            ball.target_x = ball.x
            ball.target_y = ball.y
        
        # Smooth movement только для незахваченных шариков
        for ball in self.balls:
            if not ball.is_dragging:
                ball.x += (ball.target_x - ball.x) * self.smoothing
                ball.y += (ball.target_y - ball.y) * self.smoothing
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.HighQualityAntialiasing
        )
        
        # Draw frame (optional, можно убрать если не нужна рамка)
        # painter.setPen(QColor(200, 200, 200))
        # painter.drawRect(self.frame_x, self.frame_y, self.frame_width, self.frame_height)
        
        # Draw balls
        for ball in self.balls:
            ball_size = round(ball.radius * 2)
            
            shape = self.settings['balls'].get('shape', 'Круг')
            roundness = self.settings['balls'].get('roundness', 0)
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(ball.color)
            
            if shape == 'Круг':
                painter.drawEllipse(
                    round(ball.x - ball.radius),
                    round(ball.y - ball.radius),
                    ball_size,
                    ball_size
                )
            elif shape == 'Квадрат':
                if roundness > 0:
                    painter.drawRoundedRect(
                        round(ball.x - ball.radius),
                        round(ball.y - ball.radius),
                        ball_size,
                        ball_size,
                        roundness,
                        roundness
                    )
                else:
                    painter.drawRect(
                        round(ball.x - ball.radius),
                        round(ball.y - ball.radius),
                        ball_size,
                        ball_size
                    )
            elif shape == 'Треугольник':
                path = QPainterPath()
                x = round(ball.x - ball.radius)
                y = round(ball.y - ball.radius)
                
                if roundness == 0:
                    path.moveTo(x + ball_size/2, y)
                    path.lineTo(x + ball_size, y + ball_size)
                    path.lineTo(x, y + ball_size)
                    path.lineTo(x + ball_size/2, y)
                else:
                    r = roundness * ball_size / 100
                    path.moveTo(x + ball_size/2, y + r)
                    path.arcTo(x + ball_size/2 - r, y, 2*r, 2*r, 60, 60)
                    path.lineTo(x + ball_size - r, y + ball_size - r)
                    path.arcTo(x + ball_size - 2*r, y + ball_size - 2*r, 2*r, 2*r, 0, 60)
                    path.lineTo(x + r, y + ball_size - r)
                    path.arcTo(x, y + ball_size - 2*r, 2*r, 2*r, 180, 60)
                    path.lineTo(x + ball_size/2, y + r)
                
                painter.drawPath(path)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            for ball in self.balls:
                if (ball.x - ball.radius <= event.x() <= ball.x + ball.radius and
                    ball.y - ball.radius <= event.y() <= ball.y + ball.radius):
                    ball.is_dragging = True
                    ball.drag_x = event.x()
                    ball.drag_y = event.y()
                    self.last_interaction_time = 0
    
    def mouseMoveEvent(self, event):
        for ball in self.balls:
            if ball.is_dragging:
                ball.drag_x = event.x()
                ball.drag_y = event.y()
                self.last_interaction_time = 0
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            for ball in self.balls:
                ball.is_dragging = False
            self.last_interaction_time = 0

class SettingsMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Инициализация настроек
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()
        
        # Переменная для хранения окна симуляции
        self.simulation = None
        
        # Создаем центральный виджет и его компоновку
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Создаем вкладку "Основные"
        self.main_tab = MainSettingsTab()
        tab_widget.addTab(self.main_tab, "Основные")
        
        # Создаем вкладку "Физика"
        self.physics_tab = PhysicsSettingsTab()
        tab_widget.addTab(self.physics_tab, "Физика")
        
        # Создаем вкладку "Форма"
        self.shape_tab = ShapeSettingsTab()
        tab_widget.addTab(self.shape_tab, "Форма")
        
        # Создаем вкладку "Звуки"
        self.sound_tab = SoundSettingsTab()
        tab_widget.addTab(self.sound_tab, "Звуки")
        
        # Создаем вкладку "Управление"
        self.keybind_tab = KeybindSettingsTab()
        tab_widget.addTab(self.keybind_tab, "Управление")
        
        # Создаем кнопки управления
        buttons_layout = QHBoxLayout()
        
        start_button = QPushButton("Запустить симуляцию")
        start_button.clicked.connect(self.start_simulation)
        buttons_layout.addWidget(start_button)
        
        exit_button = QPushButton("Выход")
        exit_button.clicked.connect(self.close_application)
        buttons_layout.addWidget(exit_button)
        
        layout.addLayout(buttons_layout)
        
        # Устанавливаем размеры окна
        self.setGeometry(100, 100, 400, 500)
        self.setWindowTitle('Настройки симуляции')
        
        # Настройка иконки в трее
        self.setup_tray()
        
        # Загружаем настройки в каждую вкладку
        self.load_tab_settings()
        
        # Показываем окно
        self.show()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon.png'))
        
        # Создаем контекстное меню
        tray_menu = QMenu()
        show_action = QAction("Показать", self)
        quit_action = QAction("Выход", self)
        
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.close_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def load_tab_settings(self):
        self.main_tab.load_settings(self.settings['balls'])
        self.physics_tab.load_settings(self.settings['physics'])
        self.shape_tab.load_settings(self.settings['balls'])
        self.sound_tab.load_settings(self.settings['sound'])
        self.keybind_tab.load_settings(self.settings['keybinds'])
    
    def save_settings(self):
        # Собираем настройки со всех вкладок
        self.settings['balls'].update(self.main_tab.get_settings())
        self.settings['balls'].update(self.shape_tab.get_settings())
        self.settings['physics'] = self.physics_tab.get_settings()
        self.settings['keybinds'] = self.keybind_tab.get_settings()
        self.settings['sound'] = self.sound_tab.get_settings()
        
        # Если симуляция запущена, обновляем её настройки
        if self.simulation:
            self.simulation.update_settings(self.settings)
        
        try:
            with open('ball_settings.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        try:
            if os.path.exists('ball_settings.json'):
                with open('ball_settings.json', 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge loaded settings with defaults
                    for key in self.settings:
                        if key in loaded_settings:
                            self.settings[key].update(loaded_settings[key])
        except Exception as e:
            print(f"Error loading settings: {e}")

    def start_simulation(self):
        # Сохраняем текущие настройки
        self.save_settings()
        
        # Скрываем окно настроек
        self.hide()
        
        # Создаем и показываем окно симуляции
        if not self.simulation or not self.simulation.isVisible():
            if self.simulation:
                self.simulation.close()
                self.simulation = None
            self.simulation = BounceBall(self.settings, self)
            self.simulation.show()
            self.simulation.activateWindow()
        else:
            self.simulation.show()
            self.simulation.activateWindow()
        
        # Обновляем подсказку в трее
        self.tray_icon.setToolTip("Симуляция запущена")

    def closeEvent(self, event):
        self.save_settings()
        # Закрываем окно симуляции при закрытии настроек
        if self.simulation:
            self.simulation.close()
        event.accept()

    def close_application(self):
        self.save_settings()
        # Закрываем окно симуляции при выходе
        if self.simulation:
            self.simulation.close()
        QApplication.quit()

class WaveEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 50
        self.growth_rate = 2
        self.finished = False

    def update(self):
        if self.radius < self.max_radius:
            self.radius += self.growth_rate
        else:
            self.finished = True

class Ball:
    def __init__(self, x, y, radius=30):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = random.uniform(-5, 5)  
        self.speed_y = random.uniform(-5, 5)
        self.target_x = x
        self.target_y = y
        self.is_dragging = False
        self.drag_x = x
        self.drag_y = y
        self.color = QColor(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

class BounceBall(QMainWindow):
    def __init__(self, settings=None, parent_settings_menu=None):
        super().__init__()
        
        # Применяем настройки из меню
        if settings:
            self.settings = settings.copy()
        else:
            self.settings = DEFAULT_SETTINGS.copy()
        
        # Сохраняем ссылку на родительское окно настроек
        self.settings_window = parent_settings_menu
        
        # Инициализация звука
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.init_sound()
        
        # Настройка окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Создаем центральный виджет и его компоновку
        central_widget = QWidget()
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы
        
        # Создаем виджет для симуляции
        self.simulation_widget = SimulationWidget(self, self.settings)
        self.simulation_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.simulation_widget.setStyleSheet("background: transparent;")
        # Передаем звук в виджет симуляции
        self.simulation_widget.set_collision_sound(self.collision_sound)
        layout.addWidget(self.simulation_widget)
        
        # Устанавливаем размеры окна на весь экран
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Настройка горячих клавиш
        self.setup_keybinds()
        
        # Показываем окно
        self.show()
    
    def init_sound(self):
        # Загрузка звука столкновения
        self.collision_sound = None
        if self.settings['sound']['selected_sound']:
            sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    'settings', 'sounds', self.settings['sound']['selected_sound'])
            try:
                self.collision_sound = pygame.mixer.Sound(sound_path)
                self.collision_sound.set_volume(self.settings['sound']['volume'])
            except Exception as e:
                print(f"Error loading collision sound: {e}")
                self.collision_sound = None
    
    def update_settings(self, new_settings):
        try:
            # Обновляем настройки
            self.settings = new_settings.copy()
            
            # Обновляем звук
            self.init_sound()
            
            # Обновляем горячие клавиши
            keyboard.unhook_all()
            self.setup_keybinds()
            
            # Обновляем настройки в виджете симуляции
            if hasattr(self, 'simulation_widget') and self.simulation_widget:
                self.simulation_widget.update_settings(self.settings)
                self.simulation_widget.set_collision_sound(self.collision_sound)
        except Exception as e:
            print(f"Error updating settings: {e}")
    
    def setup_keybinds(self):
        keyboard.on_press_key(self.settings['keybinds']['exit'], lambda _: self.close_application())
        keyboard.on_press_key(self.settings['keybinds']['add_ball'], lambda _: self.simulation_widget.add_ball())
        keyboard.on_press_key(self.settings['keybinds']['clear_balls'], lambda _: self.simulation_widget.clear_balls())
        keyboard.on_press_key(self.settings['keybinds']['open_settings'], lambda _: self.show_settings())
    
    def show_settings(self):
        if self.settings_window:
            self.settings_window.show()
            self.settings_window.activateWindow()
    
    def close_application(self):
        # Отключаем горячие клавиши
        keyboard.unhook_all()
        # Закрываем окно
        QTimer.singleShot(0, self.close)

    def closeEvent(self, event):
        self.close_application()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsMenu()
    window.show()
    sys.exit(app.exec_())