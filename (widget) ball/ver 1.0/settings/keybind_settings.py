from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

class KeybindButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.waiting_for_key = False
        self.clicked.connect(self.start_listening)
        self.current_key = text

    def start_listening(self):
        if not self.waiting_for_key:
            self.waiting_for_key = True
            self.setText("Нажмите клавишу...")
            self.setFocus()

    def keyPressEvent(self, event):
        if self.waiting_for_key:
            self.current_key = event.text() if event.text() else QKeySequence(event.key()).toString().lower()
            self.setText(self.current_key)
            self.waiting_for_key = False
            self.clearFocus()
            event.accept()
        else:
            super().keyPressEvent(event)

class KeybindSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        # Выход
        exit_layout = QHBoxLayout()
        exit_label = QLabel("Выход:")
        self.exit_key = KeybindButton("esc")
        exit_layout.addWidget(exit_label)
        exit_layout.addWidget(self.exit_key)
        self.layout.addLayout(exit_layout)

        # Добавить шарик
        add_ball_layout = QHBoxLayout()
        add_ball_label = QLabel("Добавить шарик:")
        self.add_ball_key = KeybindButton("space")
        add_ball_layout.addWidget(add_ball_label)
        add_ball_layout.addWidget(self.add_ball_key)
        self.layout.addLayout(add_ball_layout)

        # Очистить шарики
        clear_balls_layout = QHBoxLayout()
        clear_balls_label = QLabel("Очистить шарики:")
        self.clear_balls_key = KeybindButton("c")
        clear_balls_layout.addWidget(clear_balls_label)
        clear_balls_layout.addWidget(self.clear_balls_key)
        self.layout.addLayout(clear_balls_layout)

        # Открыть настройки
        settings_layout = QHBoxLayout()
        settings_label = QLabel("Открыть настройки:")
        self.settings_key = KeybindButton("s")
        settings_layout.addWidget(settings_label)
        settings_layout.addWidget(self.settings_key)
        self.layout.addLayout(settings_layout)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def get_settings(self):
        return {
            'exit': self.exit_key.current_key,
            'add_ball': self.add_ball_key.current_key,
            'clear_balls': self.clear_balls_key.current_key,
            'open_settings': self.settings_key.current_key
        }

    def load_settings(self, settings):
        if 'exit' in settings:
            self.exit_key.setText(settings['exit'])
            self.exit_key.current_key = settings['exit']
        if 'add_ball' in settings:
            self.add_ball_key.setText(settings['add_ball'])
            self.add_ball_key.current_key = settings['add_ball']
        if 'clear_balls' in settings:
            self.clear_balls_key.setText(settings['clear_balls'])
            self.clear_balls_key.current_key = settings['clear_balls']
        if 'open_settings' in settings:
            self.settings_key.setText(settings['open_settings'])
            self.settings_key.current_key = settings['open_settings'] 