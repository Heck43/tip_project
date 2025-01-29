from direct.showbase.ShowBase import ShowBase
from panda3d.core import Point3, Vec3, Vec4, Vec2, WindowProperties, MouseWatcher, NodePath
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerQueue
from panda3d.core import CollisionRay, CollisionSphere, CollisionBox, BitMask32
from panda3d.core import TextNode, TextureStage, Texture, TransparencyAttrib
from panda3d.core import AmbientLight, DirectionalLight, LineSegs
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from direct.task import Task
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.IntervalGlobal import Sequence, LerpColorScaleInterval, Parallel
from direct.filter.CommonFilters import CommonFilters
from menu import MainMenu
from target import Target
import random
import math
import time
from direct.actor.Actor import Actor
from math import sin, cos, pi, radians as deg2Rad
import sys

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Настройки игры
        self.mouse_sensitivity = 15.0  # Стандартное значение чувствительности
        self.show_score = True
        self.show_timer = True

        # Игровая статистика
        self.score = 0
        self.combo_multiplier = 1.0  # Множитель комбо
        self.last_hit_time = 0  # Время последнего попадания
        self.combo_window = 2.0  # Окно времени для комбо (в секундах)
        self.start_time = 0
        self.game_time = 0
        
        # UI элементы
        self.score_text = OnscreenText(
            text="Score: 0",
            pos=(-1.3, 0.9),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.07,
            mayChange=True
        )
        self.score_text.hide()
        
        self.timer_text = OnscreenText(
            text="Time: 0:00",
            pos=(1.3, 0.9),
            fg=(1, 1, 1, 1),
            align=TextNode.ARight,
            scale=0.07,
            mayChange=True
        )
        self.timer_text.hide()
        
        # Отключаем стандартное управление мышью
        self.disableMouse()

        # Инициализация коллизий
        self.cTrav = CollisionTraverser()
        self.cQueue = CollisionHandlerQueue()
        
        # Настройки окна
        properties = WindowProperties()
        properties.setTitle("Aim Trainer")
        properties.setSize(1280, 720)
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)
        
        # Настраиваем FOV (поле зрения)
        self.camLens.setFov(90)  # Увеличиваем FOV до 90 градусов
        
        # Базовые настройки
        self.move_speed = 15.0
        self.jump_power = 20.0
        self.gravity = -50.0
        self.vertical_velocity = 0.0
        self.is_jumping = False
        self.ground_height = 0
        
        # Настройка камеры
        self.camera_height = 1.8
        self.camera.setPos(0, 0, self.camera_height)
        self.camera_pitch = 0
        self.camera_heading = 0
        
        # Создаем пол
        self.ground = self.loader.loadModel("models/box")
        self.ground.setScale(100, 100, 1)
        self.ground.setPos(0, 0, -1)
        self.ground.setColor(0.2, 0.2, 0.2)
        self.ground.reparentTo(self.render)

        # Создаем цель
        self.targets = []
        
        # Создаем прицел
        self.crosshair = OnscreenText(
            text="+",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(0, 0),
            scale=.05)

        # Параметры стрельбы
        self.can_shoot = True
        self.shoot_cooldown = 0.2  # Задержка между выстрелами в секундах
        self.recoil_time = 0.05
        self.is_shooting = False
        self.shoot_time = 0
        self.original_weapon_pos = None
        self.original_weapon_hpr = None
        
        # Загрузка звуков
        self.shot_sound = self.loader.loadSfx("sounds/shot.wav")
        self.hit_sound = self.loader.loadSfx("sounds/hit.wav")
        # Настройка громкости
        self.shot_sound.setVolume(0.5)
        self.hit_sound.setVolume(0.7)
        
        # Настройка информационных текстов
        self.fps_text = self.create_text(-1.3, 0.95)
        self.pos_text = self.create_text(-1.3, 0.85)
        self.speed_text = self.create_text(-1.3, 0.75)
        
        # Список для хранения всех визуальных эффектов
        self.shot_effects = []  # Каждый элемент это кортеж (line_node, marker_node, task)
        
        # Список для хранения текста урона
        self.damage_texts = []  # Каждый элемент это кортеж (text_node, start_time, start_pos)
        
        # Список для хранения 2D маркеров попадания
        self.hit_markers = []  # Каждый элемент это NodePath
        
        # Настройка управления
        self.accept("escape", self.return_to_menu)
        self.accept("space", self.start_jump)
        
        # Инициализируем keyMap
        self.keyMap = {
            "w": False,
            "s": False,
            "a": False,
            "d": False
        }
        
        # Настройка клавиш
        self.accept("w", self.updateKeyMap, ["w", True])
        self.accept("w-up", self.updateKeyMap, ["w", False])
        self.accept("s", self.updateKeyMap, ["s", True])
        self.accept("s-up", self.updateKeyMap, ["s", False])
        self.accept("a", self.updateKeyMap, ["a", True])
        self.accept("a-up", self.updateKeyMap, ["a", False])
        self.accept("d", self.updateKeyMap, ["d", True])
        self.accept("d-up", self.updateKeyMap, ["d", False])
        
        # Добавляем задачи
        self.previous_time = 0
        self.frame_count = 0
        self.fps = 0
        self.fps_update_time = 0
        
        # Добавляем задачу обновления текста урона
        self.taskMgr.add(self.update_damage_texts, "update_damage_texts")
        
        # Set up collision traverser and handler
        self.cTrav = CollisionTraverser('Main traverser')
        self.cQueue = CollisionHandlerQueue()
        
        # Create the collision ray
        self.ray = CollisionRay()
        rayNode = CollisionNode('mouseRay')
        rayNode.addSolid(self.ray)
        rayNode.setFromCollideMask(BitMask32.bit(1))
        rayNode.setIntoCollideMask(BitMask32.allOff())
        self.rayNodePath = self.camera.attachNewNode(rayNode)
        self.cTrav.addCollider(self.rayNodePath, self.cQueue)
        
        # Настройка выхода из игры
        self.accept("window-event", self.cleanup)
        
        # Создаем главное меню
        self.main_menu = MainMenu(self)
        self.main_menu.show()
        
        # Настраиваем motion blur
        self.filters = CommonFilters(self.win, self.cam)
        self.filters.setBlurSharpen(0.0)  # Начальное значение - без размытия
        
        # Параметры для motion blur
        self.last_camera_hpr = self.camera.getHpr()
        self.blur_amount = 0.0
        self.max_blur = 0.5  # Максимальная сила размытия
        self.blur_decay = 0.1  # Скорость затухания размытия
        self.rotation_threshold = 3.0  # Порог скорости поворота для активации размытия
        
        # Добавляем задачу обновления motion blur
        self.taskMgr.add(self.update_motion_blur, "update_motion_blur")

    def create_text(self, x, y):
        return OnscreenText(
            text="",
            style=1,
            fg=(1, 1, 1, 1),
            pos=(x, y),
            align=TextNode.ALeft,
            scale=.05)

    def create_cross_marker(self, position):
        # Создаем узел для крестика
        marker_node = NodePath("hit_marker")
        marker_node.reparentTo(self.render)
        marker_node.setPos(position)
        
        # Создаем линии крестика
        segs = LineSegs()
        segs.setColor(1, 0, 0, 1)  # Красный цвет
        segs.setThickness(1.5)  # Толщина линий
        
        # Размер крестика
        size = 0.1
        
        # Центральная точка
        center = Point3(0, 0, 0)
        
        # Создаем шесть линий (по две для каждой оси)
        # X axis (вперед-назад)
        segs.moveTo(center + Point3(-size, 0, 0))
        segs.drawTo(center + Point3(size, 0, 0))
        
        # Y axis (влево-вправо)
        segs.moveTo(center + Point3(0, -size, 0))
        segs.drawTo(center + Point3(0, size, 0))
        
        # Z axis (вверх-вниз)
        segs.moveTo(center + Point3(0, 0, -size))
        segs.drawTo(center + Point3(0, 0, size))
        
        # Создаем и прикрепляем линии к узлу
        cross_lines = segs.create()
        cross_node = NodePath(cross_lines)
        cross_node.reparentTo(marker_node)
        
        # Настраиваем billboarding
        marker_node.setBillboardPointEye()
        
        return marker_node

    def create_hit_marker(self, position):
        # Создаем линии для крестика
        segs = LineSegs()
        segs.setColor(1, 0, 0, 1)  # Красный цвет
        segs.setThickness(2.0)
        
        # Размер крестика
        size = 0.2
        
        # Горизонтальная линия
        segs.moveTo(position + Point3(-size, 0, 0))
        segs.drawTo(position + Point3(size, 0, 0))
        
        # Вертикальная линия
        segs.moveTo(position + Point3(0, 0, -size))
        segs.drawTo(position + Point3(0, 0, size))
        
        # Создаем узел с крестиком
        marker_node = self.render.attachNewNode(segs.create())
        
        # Добавляем анимацию увеличения и исчезновения
        scale_sequence = Sequence(
            marker_node.scaleInterval(0.1, 1.5),  # Увеличение
            marker_node.scaleInterval(0.1, 1.0)   # Уменьшение
        )
        scale_sequence.start()
        
        return marker_node

    def setup_targets(self):
        # Позиции для манекенов (x, y)
        target_positions = [
            (0, 20),      # Центральный манекен
            (-10, 25),    # Левый дальний
            (10, 25),     # Правый дальний
            (0, 30),      # Дальний центральный
        ]
        
        # Создаем манекены в указанных позициях
        for pos_x, pos_y in target_positions:
            target = Target(self, Point3(pos_x, pos_y, 1))
            self.targets.append(target)

    def setup_weapon(self):
        # Создаем контейнер для всего оружия
        self.weapon = NodePath("weapon")
        self.weapon.reparentTo(self.camera)
        
        # Создаем дуло (удлиненный прямоугольник)
        barrel = self.loader.loadModel("models/box")
        barrel.setScale(0.08, 0.4, 0.08)  # Тонкое и длинное
        barrel.setPos(0, 1.0, -0.1)  # Выдвигаем дальше вперед
        barrel.setColor(0.2, 0.2, 0.2)  # Тёмно-серый цвет
        barrel.reparentTo(self.weapon)
        
        # Создаем рукоять (прямоугольник)
        grip = self.loader.loadModel("models/box")
        grip.setScale(0.1, 0.1, 0.25)  # Размер рукояти
        grip.setPos(0, 0.8, -0.3)  # Располагаем под дулом
        grip.setColor(0.3, 0.3, 0.3)  # Чуть светлее серый
        grip.reparentTo(self.weapon)
        
        # Позиционируем всё оружие
        self.weapon.setPos(0.3, 0.8, -0.4)  # Справа от камеры
        self.weapon.setHpr(0, 0, 0)  # Без наклона
        
        # Сохраняем начальную позицию для анимации отдачи
        self.original_weapon_pos = self.weapon.getPos()
        self.original_weapon_hpr = self.weapon.getHpr()

    def animate_weapon_recoil(self):
        # Сохраняем текущую позицию
        start_pos = self.weapon.getPos()
        
        # Создаем отдачу (назад и вверх)
        recoil_pos = Point3(
            start_pos.getX(),  # X остается тем же
            start_pos.getY() - 0.1,  # Немного назад
            start_pos.getZ() + 0.05   # Немного вверх
        )
        
        # Создаем последовательность анимации
        recoil_sequence = Sequence(
            # Быстрое движение назад и вверх
            self.weapon.posInterval(
                0.05,  # Длительность движения назад
                recoil_pos,
                start_pos,
                blendType='easeOut'
            ),
            # Медленное возвращение в исходную позицию
            self.weapon.posInterval(
                0.1,  # Длительность возврата
                start_pos,
                recoil_pos,
                blendType='easeIn'
            )
        )
        
        # Запускаем анимацию
        recoil_sequence.start()

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def start_jump(self):
        if not self.is_jumping and abs(self.camera.getZ() - self.camera_height) < 0.1:
            self.is_jumping = True
            self.vertical_velocity = self.jump_power

    def reset_shoot(self, task):
        self.can_shoot = True
        return task.done

    def shoot(self):
        if not self.can_shoot:
            return
            
        self.can_shoot = False
        
        # Устанавливаем таймер на возможность следующего выстрела
        self.taskMgr.doMethodLater(
            self.shoot_cooldown,
            self.reset_shoot,
            'reset_shoot'
        )
        
        # Анимация отдачи оружия
        self.animate_weapon_recoil()
        
        if not self.mouseWatcherNode.hasMouse():
            return
            
        # Получаем позицию мыши
        mouse_pos = self.mouseWatcherNode.getMouse()
        
        # Создаем луч от камеры
        from_pos = Point3(0, 0, 0)
        from_pos = self.render.getRelativePoint(self.camera, from_pos)
        
        to_pos = Point3(mouse_pos.getX(), 1.0, mouse_pos.getY())
        to_pos = self.render.getRelativePoint(self.camera, Point3(to_pos.getX() * 100, 100, to_pos.getZ() * 100))
        
        # Создаем CollisionRay для определения попадания
        self.ray.setFromLens(self.camNode, mouse_pos.getX(), mouse_pos.getY())
        
        self.cTrav.traverse(self.render)
        
        if self.cQueue.getNumEntries() > 0:
            # Сортируем попадания по расстоянию
            self.cQueue.sortEntries()
            hit = self.cQueue.getEntry(0)
            
            # Вызываем handle_collision для подсчета очков
            self.handle_collision(hit)
            
            hit_pos = hit.getSurfacePoint(self.render)
            
            # Генерируем уникальное имя для задачи
            task_name = f"remove_effect_{len(self.shot_effects)}"
            
            # Создаем задачу для удаления эффекта через 6 секунд
            remove_task = self.taskMgr.doMethodLater(
                6.0,
                self.remove_specific_effect,
                task_name,
                extraArgs=[len(self.shot_effects)],
                appendTask=True
            )
            
            # Добавляем эффект в список
            self.shot_effects.append((None, self.create_hit_marker(hit_pos), remove_task))

    def remove_specific_effect(self, effect_index, task):
        if 0 <= effect_index < len(self.shot_effects):
            _, marker_node, _ = self.shot_effects[effect_index]
            if marker_node:
                marker_node.removeNode()
            self.shot_effects[effect_index] = (None, None, None)
        return task.done

    def show_damage(self, position, damage):
        # Создаем текст с уроном
        damage_text = TextNode('damage')
        damage_text.setText(f"{damage}")
        damage_text.setAlign(TextNode.ACenter)
        
        # Создаем узел для текста и прикрепляем к aspect2d (2D слой)
        text_node_path = self.aspect2d.attachNewNode(damage_text)
        
        # Генерируем случайное смещение от центра
        offset_x = random.uniform(-0.15, 0.15)
        offset_y = random.uniform(-0.15, 0.15)
        
        # Располагаем текст со случайным смещением от центра
        text_node_path.setPos(offset_x, 0, offset_y)
        
        # Устанавливаем размер текста
        text_node_path.setScale(0.07)
        
        # Устанавливаем цвет в зависимости от урона
        if damage >= 100:  # Хедшот
            text_node_path.setColor(1, 0, 0, 1)  # Красный
        elif damage >= 60:  # Высокий урон
            text_node_path.setColor(1, 0.5, 0, 1)  # Оранжевый
        else:  # Обычный урон
            text_node_path.setColor(1, 1, 1, 1)  # Белый
        
        # Создаем анимацию движения вверх и исчезновения
        fade_interval = LerpColorScaleInterval(
            text_node_path,
            0.5,  # Длительность
            Vec4(1, 1, 1, 0),  # Конечное значение (прозрачный)
            Vec4(1, 1, 1, 1)   # Начальное значение (непрозрачный)
        )
        
        # Конечная позиция будет немного выше начальной, сохраняя случайное X-смещение
        pos_interval = text_node_path.posInterval(
            0.5,  # Длительность
            Point3(offset_x, 0, offset_y + 0.2),  # Конечная позиция
            Point3(offset_x, 0, offset_y)         # Начальная позиция
        )
        
        # Запускаем обе анимации одновременно
        Parallel(fade_interval, pos_interval).start()
        
        # Удаляем текст через 0.5 секунды
        self.taskMgr.doMethodLater(
            0.5,
            lambda task: text_node_path.removeNode(),
            'remove_damage_text'
        )

    def update_damage_texts(self, task):
        current_time = globalClock.getFrameTime()
        
        # Обновляем каждый текст
        for i in range(len(self.damage_texts) - 1, -1, -1):
            text_node, start_time, start_pos = self.damage_texts[i]
            age = current_time - start_time
            
            if age > 1.0:  # Текст живет 1 секунду
                text_node.removeNode()
                self.damage_texts.pop(i)
            else:
                # Поднимаем текст вверх и делаем его прозрачным
                alpha = 1.0 - age
                z_offset = age * 2  # Поднимаем на 2 единицы за секунду
                text_node.setPos(start_pos + Point3(0, 0, z_offset))
                text_node.setAlphaScale(alpha)
        
        return task.cont

    def recoil_animation(self, task):
        # Время с начала анимации
        dt = task.time - self.shoot_time
        
        if dt < self.recoil_time:
            # Фаза отдачи (назад и вверх)
            progress = dt / self.recoil_time
            recoil_back = -0.15
            recoil_up = 0.08
            recoil_rot = 8
            
            # Интерполируем позицию и поворот
            current_pos = self.original_weapon_pos + Point3(0, recoil_back * progress, recoil_up * progress)
            current_rot = self.original_weapon_hpr + Vec3(0, -recoil_rot * progress, 0)
            
            self.weapon.setPos(current_pos)
            self.weapon.setHpr(current_rot)
            
            return task.cont
        elif dt < self.recoil_time * 2:
            # Фаза возврата (плавное возвращение в исходную позицию)
            progress = (dt - self.recoil_time) / self.recoil_time
            
            # Линейная интерполяция обратно к исходной позиции
            current_pos = self.weapon.getPos() + (self.original_weapon_pos - self.weapon.getPos()) * progress
            current_rot = self.weapon.getHpr() + (self.original_weapon_hpr - self.weapon.getHpr()) * progress
            
            self.weapon.setPos(current_pos)
            self.weapon.setHpr(current_rot)
            
            if progress >= 1:
                # Убеждаемся, что оружие точно вернулось в исходное положение
                self.weapon.setPos(self.original_weapon_pos)
                self.weapon.setHpr(self.original_weapon_hpr)
                self.is_shooting = False
                return task.done
            
            return task.cont
        
        # На всякий случай возвращаем в исходное положение
        self.weapon.setPos(self.original_weapon_pos)
        self.weapon.setHpr(self.original_weapon_hpr)
        self.is_shooting = False
        return task.done

    def update(self, task):
        dt = task.time - self.previous_time
        self.previous_time = task.time
        
        # Обновляем анимацию оружия
        # self.update_weapon(dt)
        
        # Обновление FPS
        self.frame_count += 1
        if task.time - self.fps_update_time > 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.fps_update_time = task.time
        
        # Инициализируем вектор движения
        move_vec = Vec3(0, 0, 0)
        
        # Обновляем поворот камеры на основе движения мыши
        if self.mouseWatcherNode.hasMouse():
            mouse_x = self.mouseWatcherNode.getMouseX()
            mouse_y = self.mouseWatcherNode.getMouseY()
            
            self.camera_heading -= mouse_x * self.mouse_sensitivity
            self.camera_pitch += mouse_y * self.mouse_sensitivity
            
            # Ограничиваем угол подъема/спуска камеры
            self.camera_pitch = min(89, max(-89, self.camera_pitch))
            
            self.camera.setHpr(self.camera_heading, self.camera_pitch, 0)
            
            # Возвращаем курсор в центр экрана
            self.win.movePointer(0,
                int(self.win.getProperties().getXSize() / 2),
                int(self.win.getProperties().getYSize() / 2))
        
        # Обрабатываем движение
        if self.keyMap["w"]: move_vec.setY(move_vec.getY() + 1)
        if self.keyMap["s"]: move_vec.setY(move_vec.getY() - 1)
        if self.keyMap["a"]: move_vec.setX(move_vec.getX() - 1)
        if self.keyMap["d"]: move_vec.setX(move_vec.getX() + 1)
        
        # Если есть движение
        if move_vec.length() > 0:
            move_vec.normalize()
            # Преобразуем движение относительно поворота камеры
            angle = math.radians(self.camera_heading)
            x = move_vec.getX() * math.cos(angle) - move_vec.getY() * math.sin(angle)
            y = move_vec.getX() * math.sin(angle) + move_vec.getY() * math.cos(angle)
            
            # Применяем движение
            self.camera.setPos(
                self.camera.getX() + x * self.move_speed * dt,
                self.camera.getY() + y * self.move_speed * dt,
                self.camera.getZ()
            )
        
        # Обрабатываем прыжок и гравитацию
        if self.is_jumping:
            self.vertical_velocity += self.gravity * dt
            new_z = self.camera.getZ() + self.vertical_velocity * dt
            
            if new_z <= self.camera_height:
                new_z = self.camera_height
                self.vertical_velocity = 0
                self.is_jumping = False
            
            self.camera.setZ(new_z)
        
        # Обновление информационных текстов
        self.fps_text.setText(f"FPS: {self.fps}")
        self.pos_text.setText(f"Pos: ({self.camera.getX():.1f}, {self.camera.getY():.1f}, {self.camera.getZ():.1f})")
        
        # Вычисляем текущую скорость движения
        current_speed = math.sqrt(move_vec.getX()**2 + move_vec.getY()**2) * self.move_speed if move_vec.length() > 0 else 0
        self.speed_text.setText(f"Speed: {current_speed:.1f}")
        
        # Обработка стрельбы при нажатии левой кнопки мыши
        if self.mouseWatcherNode.isButtonDown(0):  # 0 = левая кнопка мыши
            self.shoot()
        
        return Task.cont

    def cleanup(self, window=None):
        # Очищаем все эффекты
        for line_node, marker_node, task in self.shot_effects:
            if line_node:
                line_node.removeNode()
            if marker_node:
                marker_node.removeNode()
            if task:
                self.taskMgr.remove(task)
        self.shot_effects.clear()
        
        # Очищаем все тексты урона
        for text_node, _, _ in self.damage_texts:
            text_node.removeNode()
        self.damage_texts.clear()

    def return_to_menu(self):
        # Скрываем UI элементы
        self.score_text.hide()
        self.timer_text.hide()
        self.taskMgr.remove("timer_task")
        
        # Отключаем игровые компоненты
        self.taskMgr.remove("update")
        self.ignore("mouse1")
        
        # Очищаем старые цели
        for target in self.targets:
            target.destroy()
        self.targets.clear()
        
        # Очищаем оружие если оно есть
        if hasattr(self, 'weapon'):
            self.weapon.removeNode()
        
        # Показываем меню
        self.main_menu.show()

    def start_game(self):
        # Настраиваем окно для игры
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        
        # Очищаем старые цели если они есть
        for target in self.targets:
            target.destroy()
        self.targets.clear()
        
        # Включаем игровые компоненты
        self.setup_targets()
        self.setup_weapon()
        
        # Включаем управление
        self.taskMgr.add(self.update, "update")
        self.accept("mouse1", self.shoot)
        
        # Сбрасываем и показываем счет и таймер
        self.score = 0
        self.start_time = time.time()
        self.update_score_display()
        self.update_timer_display()
        
        if self.show_score:
            self.score_text.show()
        if self.show_timer:
            self.timer_text.show()
            self.taskMgr.add(self.update_timer_task, "timer_task")

    def update_score_display(self):
        self.score_text.setText(f"Score: {self.score}")
    
    def update_timer_display(self):
        minutes = int(self.game_time) // 60
        seconds = int(self.game_time) % 60
        self.timer_text.setText(f"Time: {minutes}:{seconds:02d}")
    
    def update_timer_task(self, task):
        if not self.show_timer:
            return task.done
        self.game_time = time.time() - self.start_time
        self.update_timer_display()
        return task.cont
    
    def handle_collision(self, entry):
        # Получаем целевой объект
        target = entry.getIntoNodePath().getParent()
        
        # Получаем часть тела, в которую попали
        hit_node = entry.getIntoNode()
        damage = self.get_damage_for_part(hit_node.getName())
        
        # Обновляем комбо множитель
        current_time = time.time()
        if current_time - self.last_hit_time < self.combo_window:
            self.combo_multiplier = min(2.0, self.combo_multiplier + 0.2)  # Максимум x2
        else:
            self.combo_multiplier = 1.0
        self.last_hit_time = current_time
        
        # Вычисляем очки с учетом комбо
        points = int(damage * self.combo_multiplier)
        
        # Добавляем очки
        self.score += points
        
        # Обновляем отображение счета
        if hasattr(self, 'score_text') and self.show_score:
            self.score_text.setText(f"Score: {self.score}")
        
        # Показываем текст с очками
        self.spawn_damage_text(f"+{points}", entry.getSurfacePoint(render))
        
        # Удаляем манекен
        target.removeNode()
        
        # Создаем новый манекен через случайное время
        delay = random.uniform(0.5, 2.0)
        taskMgr.doMethodLater(delay, self.spawn_target, 'spawn_target')
        
    def get_damage_for_part(self, part_name):
        if part_name == 'target_head':
            return 100  # Хедшот
        elif part_name in ['target_body', 'target_left_arm', 'target_right_arm']:
            return random.randint(40, 80)  # Случайный урон для тела и рук
        elif part_name == 'target_legs':
            return 40  # Фиксированный урон для ног
        return 0

    def spawn_damage_text(self, text, pos):
        # Создаем текст с уроном
        damage_text = TextNode('damage')
        damage_text.setText(text)
        damage_text.setAlign(TextNode.ACenter)
        
        # Создаем узел для текста и прикрепляем к aspect2d (2D слой)
        text_node_path = self.aspect2d.attachNewNode(damage_text)
        
        # Генерируем случайное смещение от центра
        offset_x = random.uniform(-0.15, 0.15)
        offset_y = random.uniform(-0.15, 0.15)
        
        # Располагаем текст со случайным смещением от центра
        text_node_path.setPos(offset_x, 0, offset_y)
        
        # Устанавливаем размер текста
        text_node_path.setScale(0.07)
        
        # Устанавливаем цвет в зависимости от урона
        if int(text) >= 100:  # Хедшот
            text_node_path.setColor(1, 0, 0, 1)  # Красный
        elif int(text) >= 60:  # Высокий урон
            text_node_path.setColor(1, 0.5, 0, 1)  # Оранжевый
        else:  # Обычный урон
            text_node_path.setColor(1, 1, 1, 1)  # Белый
        
        # Создаем анимацию движения вверх и исчезновения
        fade_interval = LerpColorScaleInterval(
            text_node_path,
            0.5,  # Длительность
            Vec4(1, 1, 1, 0),  # Конечное значение (прозрачный)
            Vec4(1, 1, 1, 1)   # Начальное значение (непрозрачный)
        )
        
        # Конечная позиция будет немного выше начальной, сохраняя случайное X-смещение
        pos_interval = text_node_path.posInterval(
            0.5,  # Длительность
            Point3(offset_x, 0, offset_y + 0.2),  # Конечная позиция
            Point3(offset_x, 0, offset_y)         # Начальная позиция
        )
        
        # Запускаем обе анимации одновременно
        Parallel(fade_interval, pos_interval).start()
        
        # Удаляем текст через 0.5 секунды
        self.taskMgr.doMethodLater(
            0.5,
            lambda task: text_node_path.removeNode(),
            'remove_damage_text'
        )

    def spawn_target(self, task):
        # Генерируем случайную позицию для нового манекена
        x = random.uniform(-10, 10)
        y = random.uniform(20, 30)
        
        # Создаем новый манекен
        target = Target(self, Point3(x, y, 1))
        self.targets.append(target)
        
        return task.done

    def update_motion_blur(self, task):
        current_hpr = self.camera.getHpr()
        dt = globalClock.getDt()
        
        # Вычисляем скорость поворота (в градусах в секунду)
        rotation_speed = abs((current_hpr[0] - self.last_camera_hpr[0]) / dt)
        
        # Если скорость поворота выше порога, уменьшаем размытие
        if rotation_speed > self.rotation_threshold:
            self.blur_amount = max(0.0, self.blur_amount - dt * 2.0)
        else:
            # Иначе увеличиваем размытие
            self.blur_amount = min(self.max_blur, self.blur_amount + self.blur_decay)
        
        # Применяем текущее значение размытия
        self.filters.setBlurSharpen(self.blur_amount)
        
        # Сохраняем текущее положение камеры
        self.last_camera_hpr = current_hpr
        
        return task.cont

if __name__ == "__main__":
    game = Game()
    game.run()
