import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush

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

class BounceBall(QMainWindow):
    def __init__(self):
        super().__init__()

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

        # Таймер для обновления позиции мячика
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(30)

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
            # Запоминаем начальную позицию мыши
            self.start_x = event.x()
            self.start_y = event.y()
            # Проверка, попадает ли курсор на мячик
            if (self.ball_x - self.ball_radius <= self.start_x <= self.ball_x + self.ball_radius and
                self.ball_y - self.ball_radius <= self.start_y <= self.ball_y + self.ball_radius):
                self.is_dragging = True
                self.last_interaction_time = 0  # Сбрасываем время последнего взаимодействия

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            # Перемещение мячика в зависимости от положения мыши
            self.ball_x = event.x()
            self.ball_y = event.y()
            self.last_interaction_time = 0  # Сбрасываем время последнего взаимодействия

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            # Вычисляем скорость на основе разницы между начальной и конечной позицией
            self.ball_speed_x = (event.x() - self.start_x) / 1  # Делим для уменьшения скорости
            self.ball_speed_y = (event.y() - self.start_y) / 1
            self.last_interaction_time = 0  # Сбрасываем время последнего взаимодействия

    def update_position(self):
        if not self.is_dragging:
            # Уменьшаем скорость мячика
            self.ball_speed_x *= self.speed_decay
            self.ball_speed_y *= self.speed_decay
            
            # Обновление позиции мячика, если он не перетаскивается
            self.ball_x += self.ball_speed_x
            self.ball_y += self.ball_speed_y

            # Логика отскока от рамки
            if self.ball_x - self.ball_radius < self.frame_x or self.ball_x + self.ball_radius > self.frame_x + self.frame_width:
                self.ball_speed_x = -self.ball_speed_x * random.uniform(0.5, 1.5)  # Случайное изменение скорости
                self.ball_x = max(self.frame_x + self.ball_radius, min(self.ball_x, self.frame_x + self.frame_width - self.ball_radius))
                # Создаем волну при столкновении
                self.waves.append(WaveEffect(self.ball_x, self.ball_y))

            if self.ball_y - self.ball_radius < self.frame_y or self.ball_y + self.ball_radius > self.frame_y + self.frame_height:
                self.ball_speed_y = -self.ball_speed_y * random.uniform(0.5, 1.5)  # Случайное изменение скорости
                self.ball_y = max(self.frame_y + self.ball_radius, min(self.ball_y, self.frame_y + self.frame_height - self.ball_radius))
                # Создаем волну при столкновении
                self.waves.append(WaveEffect(self.ball_x, self.ball_y))

        # Обновляем эффекты волн
        for wave in self.waves:
            wave.update()
        self.waves = [wave for wave in self.waves if not wave.finished]  # Удаляем завершенные волны

        self.update()  # Перерисовать окно

    def auto_throw_ball(self):
        self.last_interaction_time += 1  # Увеличиваем время без взаимодействия
        if self.last_interaction_time >= 10:  # Если прошло 10 секунд
            self.ball_speed_x = random.uniform(-20, 20)  # Задаем случайную скорость
            self.ball_speed_y = random.uniform(-20, 20)
            self.last_interaction_time = 0  # Сбрасываем время последнего взаимодействия

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Рисуем рамку фиксированного размера
        painter.setPen(QColor(255, 255, 255))
        painter.drawRect(self.frame_x, self.frame_y, self.frame_width, self.frame_height)

        # Рисуем мячик
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawEllipse(int(self.ball_x - self.ball_radius), int(self.ball_y - self.ball_radius), 
                             int(self.ball_radius * 2), int(self.ball_radius * 2))

        # Рисуем эффекты волн
        for wave in self.waves:
            painter.setBrush(QBrush(QColor(0, 0, 255, 150)))  # Полупрозрачный синий цвет
            painter.drawEllipse(int(wave.x - wave.radius), int(wave.y - wave.radius), 
                                int(wave.radius * 2), int(wave.radius * 2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BounceBall()
    window.show()
    sys.exit(app.exec_())