from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QSpinBox)

class ShapeSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()  # Make layout accessible as instance variable
        self.initUI()

    def initUI(self):
        # Shape selection
        shape_layout = QHBoxLayout()
        shape_label = QLabel("Форма шарика:")
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["Круг", "Квадрат", "Треугольник"])
        shape_layout.addWidget(shape_label)
        shape_layout.addWidget(self.shape_combo)
        self.layout.addLayout(shape_layout)
        
        # Corner roundness for square and triangle
        roundness_layout = QHBoxLayout()
        roundness_label = QLabel("Скругление углов:")
        self.roundness_spin = QSpinBox()
        self.roundness_spin.setRange(0, 50)
        self.roundness_spin.setValue(0)
        self.roundness_spin.setSuffix("%")
        roundness_layout.addWidget(roundness_label)
        roundness_layout.addWidget(self.roundness_spin)
        self.layout.addLayout(roundness_layout)
        
        self.layout.addStretch()
        self.setLayout(self.layout)

    def get_settings(self):
        return {
            'shape': self.shape_combo.currentText(),
            'roundness': self.roundness_spin.value()
        }

    def load_settings(self, settings):
        if 'shape' in settings:
            index = self.shape_combo.findText(settings['shape'])
            if index >= 0:
                self.shape_combo.setCurrentIndex(index)
        if 'roundness' in settings:
            self.roundness_spin.setValue(settings['roundness'])
