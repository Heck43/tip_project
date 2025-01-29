import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSlider, QListWidget, QPushButton)
from PyQt5.QtCore import Qt
import pygame

class SoundSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Sound directory
        self.sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sounds')
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir)
            
        # Default volume
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        
        self.setup_ui()
        self.load_sounds()
        
    def setup_ui(self):
        self.layout = QVBoxLayout()
        
        # Список звуков
        self.layout.addWidget(QLabel("Выберите звук:"))
        self.sound_list = QListWidget()
        self.layout.addWidget(self.sound_list)
        
        # Регулятор громкости
        volume_layout = QVBoxLayout()
        volume_layout.addWidget(QLabel("Громкость:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.volume * 100))
        self.volume_slider.valueChanged.connect(self.update_volume)
        volume_layout.addWidget(self.volume_slider)
        self.layout.addLayout(volume_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Apply sound button
        self.apply_button = QPushButton("Применить звук")
        self.apply_button.clicked.connect(self.apply_sound)
        buttons_layout.addWidget(self.apply_button)
        
        # Test sound button
        self.test_button = QPushButton("Проверить звук")
        self.test_button.clicked.connect(self.test_sound)
        buttons_layout.addWidget(self.test_button)
        
        # Refresh button
        refresh_button = QPushButton("Обновить список")
        refresh_button.clicked.connect(self.load_sounds)
        buttons_layout.addWidget(refresh_button)
        
        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)
        
    def load_sounds(self):
        if os.path.exists(self.sound_dir):
            sound_files = [f for f in os.listdir(self.sound_dir) if f.lower().endswith(('.wav', '.mp3', '.ogg'))]
            self.sound_list.clear()
            self.sound_list.addItems(sound_files)

    def update_volume(self, value):
        self.volume = value / 100.0
        pygame.mixer.music.set_volume(self.volume)
        if hasattr(self.parent(), 'simulation') and self.parent().simulation:
            if self.parent().simulation.collision_sound:
                self.parent().simulation.collision_sound.set_volume(self.volume)

    def apply_sound(self):
        selected_items = self.sound_list.selectedItems()
        if selected_items:
            selected_sound = selected_items[0].text()
            sound_path = os.path.join(self.sound_dir, selected_sound)
            
            if hasattr(self.parent(), 'simulation') and self.parent().simulation:
                try:
                    # Initialize pygame mixer if not initialized
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    
                    # Load and set the collision sound
                    collision_sound = pygame.mixer.Sound(sound_path)
                    collision_sound.set_volume(self.volume)
                    
                    # Test the sound
                    collision_sound.play()
                    
                    # If test successful, set it as the collision sound
                    self.parent().simulation.collision_sound = collision_sound
                    # Передаем звук в виджет симуляции
                    self.parent().simulation.simulation_widget.set_collision_sound(collision_sound)
                    
                    # Update settings
                    if hasattr(self.parent(), 'settings'):
                        if 'sound' not in self.parent().settings:
                            self.parent().settings['sound'] = {}
                        self.parent().settings['sound']['selected_sound'] = selected_sound
                        self.parent().settings['sound']['volume'] = self.volume
                        self.parent().save_settings()
                    
                    print(f"Successfully applied sound: {selected_sound}")
                except Exception as e:
                    print(f"Error applying sound: {e}")

    def test_sound(self):
        selected_items = self.sound_list.selectedItems()
        if selected_items:
            selected_sound = selected_items[0].text()
            sound_path = os.path.join(self.sound_dir, selected_sound)
            try:
                # Initialize pygame mixer if not initialized
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                
                # Load and play test sound
                test_sound = pygame.mixer.Sound(sound_path)
                test_sound.set_volume(self.volume)
                test_sound.play()
            except Exception as e:
                print(f"Error testing sound: {e}")

    def get_settings(self):
        selected_items = self.sound_list.selectedItems()
        selected_sound = selected_items[0].text() if selected_items else ""
        return {
            'selected_sound': selected_sound,
            'volume': self.volume
        }

    def load_settings(self, settings):
        if 'volume' in settings:
            self.volume = settings['volume']
            self.volume_slider.setValue(int(self.volume * 100))
            pygame.mixer.music.set_volume(self.volume)
        
        if 'selected_sound' in settings and settings['selected_sound']:
            # Найти и выбрать звук в списке
            items = self.sound_list.findItems(settings['selected_sound'], Qt.MatchExactly)
            if items:
                self.sound_list.setCurrentItem(items[0])
