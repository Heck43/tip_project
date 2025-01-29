from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QSpinBox, QPushButton)

class MainSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        # Количество шариков
        balls_layout = QHBoxLayout()
        balls_label = QLabel("Количество шариков:")
        self.balls_count = QSpinBox()
        self.balls_count.setRange(1, 100)
        self.balls_count.setValue(5)
        balls_layout.addWidget(balls_label)
        balls_layout.addWidget(self.balls_count)
        self.layout.addLayout(balls_layout)

        # Размер шариков
        size_layout = QHBoxLayout()
        size_label = QLabel("Размер шариков:")
        self.ball_size = QSpinBox()
        self.ball_size.setRange(5, 100)
        self.ball_size.setValue(20)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.ball_size)
        self.layout.addLayout(size_layout)
        
        # Случайное движение
        random_motion_layout = QHBoxLayout()
        random_motion_label = QLabel("Случайное движение:")
        self.random_motion = QPushButton("Выключено")
        self.random_motion.setCheckable(True)
        self.random_motion.clicked.connect(self.toggle_random_motion)
        random_motion_layout.addWidget(random_motion_label)
        random_motion_layout.addWidget(self.random_motion)
        self.layout.addLayout(random_motion_layout)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def toggle_random_motion(self):
        if self.random_motion.isChecked():
            self.random_motion.setText("Включено")
        else:
            self.random_motion.setText("Выключено")

    def get_settings(self):
        return {
            'count': self.balls_count.value(),
            'size': self.ball_size.value(),
            'random_motion': self.random_motion.isChecked()
        }

    def load_settings(self, settings):
        if 'count' in settings:
            self.balls_count.setValue(settings['count'])
        if 'size' in settings:
            self.ball_size.setValue(settings['size'])
        if 'random_motion' in settings:
            self.random_motion.setChecked(settings['random_motion'])
            self.toggle_random_motion() 