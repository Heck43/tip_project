from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math

class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='cube', 
            color=color.blue, 
            scale=(1, 2, 1),
            collider='box',
            **kwargs
        )
        # Параметры движения
        self.speed = 10  # Базовая скорость
        self.acceleration = 30  # Ускорение
        self.deceleration = 20  # Замедление
        self.max_speed = 15  # Максимальная скорость
        
        # Параметры поворота
        self.rotation_speed = 5  # Скорость поворота
        self.camera_rotation_speed = 3  # Скорость поворота камеры
        self.target_rotation_y = 0  # Целевой угол поворота
        
        # Физика
        self.velocity = Vec3(0, 0, 0)
        self.jump_strength = 5
        self.gravity = 9.8
        self.grounded = False
        
        # Создаем камеру с улучшенной логикой
        self.camera_pivot = Entity(parent=self, y=2)
        self.camera = camera
        self.camera.parent = self.camera_pivot
        self.camera.position = (0, 0, -5)
        self.camera.rotation = (0, 0, 0)
        self.camera.fov = 90
        
        # Параметры плавности камеры
        self.camera_smoothing = 0.1  # Коэффициент плавности
        self.last_camera_rotation = 0
        
    def update(self):
        # Получаем входные данные
        move_x = held_keys['d'] - held_keys['a']
        move_z = held_keys['w'] - held_keys['s']
        
        # Создаем вектор движения относительно камеры
        forward = self.camera_pivot.forward
        right = self.camera_pivot.right
        
        # Вычисляем направление движения
        move_direction = (forward * move_z + right * move_x).normalized()
        
        # Расчет целевого угла поворота
        if move_direction.x != 0 or move_direction.z != 0:
            target_rotation = math.degrees(math.atan2(-move_direction.x, -move_direction.z))
            
            # Плавный поворот персонажа
            self.target_rotation_y = lerp(
                self.target_rotation_y, 
                target_rotation, 
                time.dt * self.rotation_speed
            )
            
            # Плавный поворот камеры
            self.camera_pivot.rotation_y = lerp(
                self.camera_pivot.rotation_y, 
                self.target_rotation_y, 
                time.dt * self.camera_rotation_speed
            )
        
        # Плавный поворот персонажа
        current_rotation = self.rotation_y
        self.rotation_y = lerp(
            current_rotation, 
            self.target_rotation_y, 
            time.dt * self.rotation_speed
        )
        
        # Улучшенная логика поворота камеры
        camera_target_rotation = self.rotation_y
        self.camera_pivot.rotation_y = lerp(
            self.camera_pivot.rotation_y, 
            camera_target_rotation, 
            self.camera_smoothing
        )
        
        # Ускорение
        target_velocity = move_direction * self.max_speed
        
        # Плавное изменение скорости
        if move_direction:
            # Ускорение
            self.velocity = lerp(
                self.velocity, 
                target_velocity, 
                time.dt * self.acceleration
            )
        else:
            # Торможение
            self.velocity = lerp(
                self.velocity, 
                Vec3(0, self.velocity.y, 0), 
                time.dt * self.deceleration
            )
        
        # Гравитация
        self.velocity.y -= self.gravity * time.dt
        
        # Прыжок
        if held_keys['space'] and self.grounded:
            self.velocity.y = self.jump_strength
            self.grounded = False
        
        # Перемещение
        move = self.velocity * time.dt
        self.position += move
        
        # Простая проверка земли
        if self.y < 1:
            self.y = 1
            self.velocity.y = 0
            self.grounded = True

class Platform(Entity):
    def __init__(self, position=(0,0,0), scale=(10,1,10), color=color.green, **kwargs):
        super().__init__(
            model='cube', 
            position=position, 
            scale=scale, 
            color=color, 
            collider='box',
            **kwargs
        )

class Game:
    def __init__(self):
        self.app = Ursina()
        
        # Создание платформ
        self.platforms = [
            Platform(position=(0,0,0), scale=(20,1,20)),
            Platform(position=(10,3,5), scale=(5,1,5), color=color.azure),
            Platform(position=(-10,6,10), scale=(5,1,5), color=color.orange)
        ]
        
        # Создание игрока
        self.player = Player(position=(0,2,0))
        
        # Создание врагов (необязательно)
        self.enemies = []
        for i in range(3):
            enemy = Entity(
                model='cube', 
                color=color.red, 
                scale=(1,2,1), 
                position=(random.randint(-15,15), 2, random.randint(-15,15))
            )
            self.enemies.append(enemy)
        
        # Текст для отладки
        self.debug_text = Text(
            text='Позиция: ', 
            position=(-.8, .45), 
            scale=1, 
            color=color.white
        )
    
    def update(self):
        # Обновление отладочного текста
        self.debug_text.text = f'Позиция: {self.player.position}'
        
        # Простая логика врагов (опционально)
        for enemy in self.enemies:
            # Простое преследование игрока
            direction = self.player.position - enemy.position
            enemy.position += direction.normalized() * time.dt

# Запуск игры
if __name__ == '__main__':
    game = Game()
    game.app.run()
