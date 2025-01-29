import sys
import random
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush
import keyboard  # Добавляем новый импорт для глобальных хоткеев

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

class BounceBall(QWidget):
    def __init__(self):
        super().__init__()

        # Настройка глобального хоткея для выхода
        keyboard.on_press_key('esc', lambda _: self.close_application())

        # Установка флагов для прозрачного окна
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Установка размеров окна
        self.setGeometry(100, 100, 1920, 1080)

        # Центрируем окно на экране
        self.center_window()

        # Параметры рамки фиксированного размера
        self.frame_width = 1920
        self.frame_height = 1080
        self.frame_x = (1920 - self.frame_width) // 2
        self.frame_y = (1080 - self.frame_height) // 2

        # Параметры мячика
        self.ball_radius = 30
        self.ball_x = self.frame_x + self.frame_width // 2
        self.ball_y = self.frame_y + self.frame_height // 2
        self.ball_speed_x = 0
        self.ball_speed_y = 0
        
        # Параметры для перетаскивания
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.target_x = self.ball_x
        self.target_y = self.ball_y
        
        # Параметры физики
        self.smoothing = 0.2  # Коэффициент сглаживания движения
        self.throw_power = 3.0  # Увеличиваем силу броска
        self.gravity = 0.15  # Значительно уменьшаем гравитацию
        self.bounce_energy = 0.85  # Сохранение энергии при отскоке
        self.friction = 0.999  # Минимальное трение для длительного движения
        self.air_resistance = 0.9999  # Сопротивление воздуха

        # Оптимизация FPS
        self.fps = 144  # Увеличиваем FPS для более плавного движения
        self.frame_time = 1000 // self.fps
        self.last_frame_time = time.time()

        # Таймер для обновления позиции мячика
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(self.frame_time)

        # Ограничение количества волн
        self.max_waves = 5

        # Переменные для управления мячиком
        self.is_dragging = False
        self.start_x = 0
        self.start_y = 0

        # Коэффициент уменьшения скорости
        self.speed_decay = 0.99999999999999999999  # Уменьшение скорости на 2% каждый раз

        # Эффекты волн
        self.waves = []

        # Таймер для автоматического броска
        self.auto_throw_timer = QTimer()
        self.auto_throw_timer.timeout.connect(self.auto_throw_ball)
        self.auto_throw_timer.start(1000)  # Проверяем каждую секунду

        # Время последнего взаимодействия
        self.last_interaction_time = 0

    def center_window(self):
        # Центрируем окно на экране
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Проверка, попадает ли курсор на мячик
            if (self.ball_x - self.ball_radius <= event.x() <= self.ball_x + self.ball_radius and
                self.ball_y - self.ball_radius <= event.y() <= self.ball_y + self.ball_radius):
                self.is_dragging = True
                # Запоминаем смещение от центра мяча до точки захвата
                self.drag_offset_x = self.ball_x - event.x()
                self.drag_offset_y = self.ball_y - event.y()
                self.prev_mouse_x = event.x()
                self.prev_mouse_y = event.y()
                self.ball_speed_x = 0
                self.ball_speed_y = 0
                self.last_interaction_time = 0

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            new_x = event.pos().x()
            new_y = event.pos().y()
            
            # Рассчитываем скорость броска на основе движения мыши
            self.ball_speed_x = (new_x - self.ball_x) * self.throw_power
            self.ball_speed_y = (new_y - self.ball_y) * self.throw_power
            
            # Ограничиваем максимальную скорость броска
            max_speed = 40
            speed = (self.ball_speed_x ** 2 + self.ball_speed_y ** 2) ** 0.5
            if speed > max_speed:
                scale = max_speed / speed
                self.ball_speed_x *= scale
                self.ball_speed_y *= scale
            
            self.target_x = new_x
            self.target_y = new_y
            self.ball_x = new_x
            self.ball_y = new_y
            self.last_interaction_time = 0

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.last_interaction_time = 0

    def update_position(self):
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time

        if not self.is_dragging:
            # Применяем гравитацию только если шарик движется медленно
            speed = (self.ball_speed_x ** 2 + self.ball_speed_y ** 2) ** 0.5
            gravity_scale = min(1.0, 15.0 / (speed + 1)) # Уменьшаем гравитацию при большой скорости
            self.ball_speed_y += self.gravity * gravity_scale
            
            # Применяем минимальное сопротивление воздуха
            self.ball_speed_x *= self.friction
            self.ball_speed_y *= self.friction
            
            # Обновляем целевую позицию
            self.target_x += self.ball_speed_x
            self.target_y += self.ball_speed_y

            # Обработка столкновений с рамкой
            if self.target_x - self.ball_radius < self.frame_x:
                self.target_x = self.frame_x + self.ball_radius
                self.ball_speed_x = abs(self.ball_speed_x) * self.bounce_energy
            elif self.target_x + self.ball_radius > self.frame_x + self.frame_width:
                self.target_x = self.frame_x + self.frame_width - self.ball_radius
                self.ball_speed_x = -abs(self.ball_speed_x) * self.bounce_energy

            if self.target_y - self.ball_radius < self.frame_y:
                self.target_y = self.frame_y + self.ball_radius
                self.ball_speed_y = abs(self.ball_speed_y) * self.bounce_energy
            elif self.target_y + self.ball_radius > self.frame_y + self.frame_height:
                self.target_y = self.frame_y + self.frame_height - self.ball_radius
                self.ball_speed_y = -abs(self.ball_speed_y) * self.bounce_energy
                # Применяем трение при касании пола
                self.ball_speed_x *= self.friction

            # Останавливаем мяч при очень малой скорости
            if abs(self.ball_speed_x) < 0.1 and abs(self.ball_speed_y) < 0.1:
                self.ball_speed_x = 0
                self.ball_speed_y = 0

        # Плавное движение к целевой позиции
        self.ball_x += (self.target_x - self.ball_x) * self.smoothing
        self.ball_y += (self.target_y - self.ball_y) * self.smoothing

        # Запрашиваем перерисовку только если есть движение
        if (abs(self.target_x - self.ball_x) > 0.01 or 
            abs(self.target_y - self.ball_y) > 0.01 or 
            abs(self.ball_speed_x) > 0.01 or 
            abs(self.ball_speed_y) > 0.01):
            self.update()

    def auto_throw_ball(self):
        self.last_interaction_time += 1  # Увеличиваем время без взаимодействия
        if self.last_interaction_time >= 10:  # Если прошло 10 секунд
            self.ball_speed_x = random.uniform(-20, 20)  # Задаем случайную скорость
            self.ball_speed_y = random.uniform(-20, 20)
            self.last_interaction_time = 0  # Сбрасываем время последнего взаимодействия

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем только видимую область
        visible_rect = event.rect()
        
        # Рисуем рамку только если она видима
        if visible_rect.intersects(QRect(self.frame_x, self.frame_y, self.frame_width, self.frame_height)):
            painter.setPen(QColor(255, 255, 255))
            painter.drawRect(self.frame_x, self.frame_y, self.frame_width, self.frame_height)

        # Рисуем мячик только если он виден
        ball_rect = QRect(int(self.ball_x - self.ball_radius), int(self.ball_y - self.ball_radius),
                         int(self.ball_radius * 2), int(self.ball_radius * 2))
        if visible_rect.intersects(ball_rect):
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawEllipse(ball_rect)

        # Рисуем эффекты волн только если они видимы
        for wave in self.waves:
            wave_rect = QRect(int(wave.x - wave.radius), int(wave.y - wave.radius),
                            int(wave.radius * 2), int(wave.radius * 2))
            if visible_rect.intersects(wave_rect):
                painter.setBrush(QBrush(QColor(0, 0, 255, 150)))
                painter.drawEllipse(wave_rect)

    def close_application(self):
        # Очищаем обработчик клавиши перед выходом
        keyboard.unhook_all()
        # Закрываем приложение
        QApplication.quit()

    def keyPressEvent(self, event):
        # Дополнительная обработка Esc когда окно в фокусе
        if event.key() == Qt.Key_Escape:
            self.close_application()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BounceBall()
    window.show()
    sys.exit(app.exec_())