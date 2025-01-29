from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QDoubleSpinBox)

class PhysicsSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        # Гравитация
        gravity_layout = QHBoxLayout()
        gravity_label = QLabel("Гравитация:")
        self.gravity = QDoubleSpinBox()
        self.gravity.setRange(0, 10)
        self.gravity.setSingleStep(0.1)
        self.gravity.setValue(0.5)
        gravity_layout.addWidget(gravity_label)
        gravity_layout.addWidget(self.gravity)
        self.layout.addLayout(gravity_layout)

        # Энергия отскока
        bounce_layout = QHBoxLayout()
        bounce_label = QLabel("Энергия отскока:")
        self.bounce_energy = QDoubleSpinBox()
        self.bounce_energy.setRange(0, 1)
        self.bounce_energy.setSingleStep(0.05)
        self.bounce_energy.setValue(0.8)
        bounce_layout.addWidget(bounce_label)
        bounce_layout.addWidget(self.bounce_energy)
        self.layout.addLayout(bounce_layout)

        # Трение
        friction_layout = QHBoxLayout()
        friction_label = QLabel("Трение:")
        self.friction = QDoubleSpinBox()
        self.friction.setRange(0.9, 1)
        self.friction.setSingleStep(0.001)
        self.friction.setValue(0.999)
        self.friction.setDecimals(3)
        friction_layout.addWidget(friction_label)
        friction_layout.addWidget(self.friction)
        self.layout.addLayout(friction_layout)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def get_settings(self):
        return {
            'gravity': self.gravity.value(),
            'bounce_energy': self.bounce_energy.value(),
            'friction': self.friction.value()
        }

    def load_settings(self, settings):
        if 'gravity' in settings:
            self.gravity.setValue(settings['gravity'])
        if 'bounce_energy' in settings:
            self.bounce_energy.setValue(settings['bounce_energy'])
        if 'friction' in settings:
            self.friction.setValue(settings['friction']) 