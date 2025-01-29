from direct.actor.Actor import Actor
from panda3d.core import Point3, Vec3, CollisionRay, CollisionNode, NodePath, CollisionHandlerQueue
from direct.interval.IntervalGlobal import Sequence, Wait, Parallel, LerpHprInterval
import random

class Weapon:
    def __init__(self, game):
        self.game = game
        
        # Weapon properties
        self.current_weapon = "rifle"
        self.weapons = {
            "pistol": {
                "damage": 25,
                "cooldown": 0.2,
                "spread": 0.02,
                "recoil": {
                    "pitch": (0.5, 1.0),
                    "yaw": (0.3, 0.3)
                },
                "ammo": {
                    "max": 15,
                    "current": 15
                },
                "reload_time": 1.5
            },
            "rifle": {
                "damage": 35,
                "cooldown": 0.1,
                "spread": 0.02,
                "recoil": {
                    "pitch": (1.0, 2.0),
                    "yaw": (-0.5, 0.5)
                },
                "ammo": {
                    "max": 30,
                    "current": 30
                },
                "reload_time": 2.0
            },
            "sniper": {
                "damage": 100,
                "cooldown": 0.5,
                "spread": 0.01,
                "recoil": {
                    "pitch": (2.0, 3.0),
                    "yaw": (-1.0, 1.0)
                },
                "ammo": {
                    "max": 10,
                    "current": 10
                },
                "reload_time": 3.0
            },
            "dual_revolvers": {
                "damage": 50,
                "cooldown": 0.1,
                "spread": 0.02,
                "recoil": {
                    "pitch": (1.0, 2.0),
                    "yaw": (-0.5, 0.5)
                },
                "ammo": {
                    "max": 12,
                    "current": 12
                },
                "reload_time": 2.5
            }
        }
        
        # Current weapon state
        self.can_shoot = True
        self.is_reloading = False
        self.last_shot_time = 0
        
        # Setup weapon models
        self.setup_weapon()
        
        # Setup collision detection for shooting
        self.setup_collision()
        
        # Recoil recovery
        self.recoil_recovery_task = None
    
    def setup_weapon(self):
        # Создаем контейнер для всего оружия
        self.weapon = NodePath("weapon")
        self.weapon.reparentTo(self.game.camera)
        
        # Создаем модели для каждого оружия
        self.weapon_models = {}
        
        # Позиция оружия из настроек
        weapon_x = 0.25
        weapon_y = 0.6
        weapon_z = -0.3
        
        # Создаем пистолет
        pistol = NodePath("pistol")
        pistol.reparentTo(self.weapon)
        
        # Дуло пистолета
        barrel = self.game.loader.loadModel("models/box")
        barrel.setScale(0.05, 0.3, 0.05)  # Тонкое
        barrel.setPos(weapon_x, weapon_y + 0.2, weapon_z - 0.1)  # Выдвигаем вперед
        barrel.setColor(0.1, 0.1, 0.1)  # Темный
        barrel.reparentTo(pistol)
        
        # Рукоять пистолета
        grip = self.game.loader.loadModel("models/box")
        grip.setScale(0.08, 0.15, 0.2)  # Чуть больше
        grip.setPos(weapon_x, weapon_y, weapon_z)  # Основная позиция
        grip.setColor(0.2, 0.2, 0.2)  # Темный
        grip.reparentTo(pistol)
        
        # Затвор пистолета
        slide = self.game.loader.loadModel("models/box")
        slide.setScale(0.07, 0.1, 0.15)  # Компактный
        slide.setPos(weapon_x, weapon_y + 0.1, weapon_z - 0.05)  # Чуть выше и глубже
        slide.setColor(0.15, 0.15, 0.15)  # Темнее
        slide.reparentTo(pistol)
        
        self.weapon_models["pistol"] = pistol
        
        # Создаем винтовку
        rifle = NodePath("rifle")
        rifle.reparentTo(self.weapon)
        
        # Дуло винтовки
        barrel = self.game.loader.loadModel("models/box")
        barrel.setScale(0.04, 0.6, 0.04)  # Тонкое
        barrel.setPos(weapon_x, weapon_y + 0.6, weapon_z - 0.2)  # Длиннее и глубже
        barrel.setColor(0.1, 0.1, 0.1)  # Темный
        barrel.reparentTo(rifle)
        
        # Основная часть винтовки
        body = self.game.loader.loadModel("models/box")
        body.setScale(0.1, 0.4, 0.15)  # Чуть шире
        body.setPos(weapon_x, weapon_y + 0.3, weapon_z - 0.1)  # Чуть выше
        body.setColor(0.2, 0.2, 0.2)  # Темный
        body.reparentTo(rifle)
        
        # Приклад винтовки
        stock = self.game.loader.loadModel("models/box")
        stock.setScale(0.08, 0.3, 0.15)  # Стандартный
        stock.setPos(weapon_x, weapon_y, weapon_z - 0.15)  # Основная позиция
        stock.setColor(0.25, 0.25, 0.25)  # Чуть светлее
        stock.reparentTo(rifle)
        
        # Рукоять винтовки
        grip = self.game.loader.loadModel("models/box")
        grip.setScale(0.08, 0.15, 0.2)  # Стандартная
        grip.setPos(weapon_x, weapon_y + 0.2, weapon_z - 0.25)  # Чуть выше
        grip.setColor(0.3, 0.3, 0.3)  # Светлее
        grip.reparentTo(rifle)
        
        self.weapon_models["rifle"] = rifle
        
        # Создаем снайперскую винтовку
        sniper = NodePath("sniper")
        sniper.reparentTo(self.weapon)
        
        # Дуло снайперской винтовки
        barrel = self.game.loader.loadModel("models/box")
        barrel.setScale(0.03, 0.8, 0.03)  # Очень тонкое
        barrel.setPos(weapon_x, weapon_y + 0.8, weapon_z - 0.2)  # Длиннее
        barrel.setColor(0.1, 0.1, 0.1)  # Темный
        barrel.reparentTo(sniper)
        
        # Основная часть снайперской винтовки
        body = self.game.loader.loadModel("models/box")
        body.setScale(0.1, 0.5, 0.15)  # Чуть длиннее
        body.setPos(weapon_x, weapon_y + 0.5, weapon_z - 0.15)  # Чуть выше
        body.setColor(0.2, 0.2, 0.2)  # Темный
        body.reparentTo(sniper)
        
        # Приклад снайперской винтовки
        stock = self.game.loader.loadModel("models/box")
        stock.setScale(0.08, 0.4, 0.15)  # Длиннее
        stock.setPos(weapon_x, weapon_y + 0.2, weapon_z - 0.2)  # Основная позиция
        stock.setColor(0.25, 0.25, 0.25)  # Чуть светлее
        stock.reparentTo(sniper)
        
        # Рукоять снайперской винтовки
        grip = self.game.loader.loadModel("models/box")
        grip.setScale(0.08, 0.15, 0.2)  # Стандартная
        grip.setPos(weapon_x, weapon_y + 0.4, weapon_z - 0.25)  # Чуть выше
        grip.setColor(0.3, 0.3, 0.3)  # Светлее
        grip.reparentTo(sniper)
        
        self.weapon_models["sniper"] = sniper
        
        # Создаем двойные револьверы
        dual_revolvers = NodePath("dual_revolvers")
        dual_revolvers.reparentTo(self.weapon)
        
        # Левый револьвер
        left_revolver = NodePath("left_revolver")
        left_revolver.reparentTo(dual_revolvers)
        left_revolver.setPos(weapon_x - 0.2, weapon_y, weapon_z)  # Левее
        
        # Правый револьвер
        right_revolver = NodePath("right_revolver")
        right_revolver.reparentTo(dual_revolvers)
        right_revolver.setPos(weapon_x + 0.2, weapon_y, weapon_z)  # Правее
        
        # Создаем модель револьвера (для обоих)
        for revolver in [left_revolver, right_revolver]:
            # Дуло револьвера
            barrel = self.game.loader.loadModel("models/box")
            barrel.setScale(0.04, 0.2, 0.04)  # Тонкое
            barrel.setPos(0, 0.2, 0)
            barrel.setColor(0.1, 0.1, 0.1)  # Темный
            barrel.reparentTo(revolver)
            
            # Барабан револьвера
            cylinder = self.game.loader.loadModel("models/box")
            cylinder.setScale(0.08, 0.15, 0.08)  # Чуть выше
            cylinder.setPos(0, 0, 0)
            cylinder.setColor(0.2, 0.2, 0.2)  # Темный
            cylinder.reparentTo(revolver)
            
            # Рукоять револьвера
            grip = self.game.loader.loadModel("models/box")
            grip.setScale(0.07, 0.1, 0.15)  # Компактная
            grip.setPos(0, -0.2, -0.1)
            grip.setColor(0.25, 0.25, 0.25)  # Чуть светлее
            grip.reparentTo(revolver)
        
        self.weapon_models["dual_revolvers"] = dual_revolvers
        
        # Initially show rifle
        self.switch_weapon("rifle")
    
    def switch_weapon(self, weapon_name):
        # Hide all weapon models
        for model in self.weapon_models.values():
            model.hide()
        
        # Show selected weapon
        self.weapon_models[weapon_name].show()
        self.current_weapon = weapon_name
    
    def setup_collision(self):
        self.ray = CollisionRay()
        rayNode = CollisionNode('weaponRay')
        rayNode.addSolid(self.ray)
        self.rayNodePath = self.game.camera.attachNewNode(rayNode)
        self.rayQueue = CollisionHandlerQueue()
        self.game.cTrav.addCollider(self.rayNodePath, self.rayQueue)
    
    def shoot(self):
        if not self.can_shoot or self.is_reloading:
            return
            
        current_weapon = self.weapons[self.current_weapon]
        current_time = globalClock.getFrameTime()
        
        if current_time - self.last_shot_time < current_weapon["cooldown"]:
            return
            
        if current_weapon["ammo"]["current"] <= 0:
            self.reload()
            return
            
        self.last_shot_time = current_time
        current_weapon["ammo"]["current"] -= 1
        
        # Apply spread
        spread = current_weapon["spread"]
        spread_x = random.uniform(-spread, spread)
        spread_y = random.uniform(-spread, spread)
        
        # Get camera direction with spread
        camera_pos = self.game.camera.getPos()
        camera_direction = self.game.camera.getMat().getRow3(1)
        camera_direction.normalize()
        camera_direction.addX(spread_x)
        camera_direction.addZ(spread_y)
        camera_direction.normalize()
        
        # Set up the collision ray
        self.ray.setOrigin(camera_pos)
        self.ray.setDirection(camera_direction)
        
        # Traverse the collision queue
        self.game.cTrav.traverse(self.game.render)
        
        # Check for hits
        if self.rayQueue.getNumEntries() > 0:
            self.rayQueue.sortEntries()
            hit = self.rayQueue.getEntry(0)
            hit_pos = hit.getSurfacePoint(self.game.render)
            
            # Check if we hit an enemy
            hit_node = hit.getIntoNodePath()
            if hit_node.hasNetTag('enemy'):
                enemy = hit_node.getPythonTag('enemy')
                if enemy:
                    enemy.take_damage(current_weapon["damage"])
        
        # Apply recoil
        self.apply_recoil()
        
        # Update ammo display
        self.game.ammo_text.setText(f"Ammo: {current_weapon['ammo']['current']}")
    
    def reload(self):
        if self.is_reloading:
            return
            
        current_weapon = self.weapons[self.current_weapon]
        if current_weapon["ammo"]["current"] >= current_weapon["ammo"]["max"]:
            return
            
        self.is_reloading = True
        self.can_shoot = False
        
        # Create reload sequence
        reload_sequence = Sequence(
            Wait(current_weapon["reload_time"]),
            name="reload"
        )
        
        def finish_reload():
            current_weapon["ammo"]["current"] = current_weapon["ammo"]["max"]
            self.is_reloading = False
            self.can_shoot = True
            self.game.ammo_text.setText(f"Ammo: {current_weapon['ammo']['current']}")
        
        reload_sequence.setDoneEvent('reloadFinished')
        reload_sequence.start()
        
        # Add callback for when reload is finished
        self.game.accept('reloadFinished', finish_reload)
    
    def apply_recoil(self):
        current_weapon = self.weapons[self.current_weapon]
        recoil = current_weapon["recoil"]
        
        # Random recoil values
        pitch_recoil = random.uniform(recoil["pitch"][0], recoil["pitch"][1])
        yaw_recoil = random.uniform(recoil["yaw"][0], recoil["yaw"][1])
        
        # Apply recoil to camera
        current_pitch = self.game.camera.getP()
        current_heading = self.game.camera.getH()
        
        self.game.camera.setP(current_pitch - pitch_recoil)
        self.game.camera.setH(current_heading + yaw_recoil)
        
        # Weapon kick animation
        kick_sequence = Sequence(
            LerpHprInterval(
                self.weapon_models[self.current_weapon],
                0.05,
                Point3(0, -20, 0),
                startHpr=Point3(0, 0, 0)
            ),
            LerpHprInterval(
                self.weapon_models[self.current_weapon],
                0.1,
                Point3(0, 0, 0),
                startHpr=Point3(0, -20, 0)
            )
        )
        kick_sequence.start()
        
        # Start recoil recovery if not already running
        if not self.recoil_recovery_task:
            self.recoil_recovery_task = self.game.taskMgr.add(
                self.recover_from_recoil,
                "recoilRecovery"
            )
    
    def recover_from_recoil(self, task):
        dt = globalClock.getDt()
        recovery_speed = 5.0  # Adjust this value to control recovery speed
        
        # Recover camera position
        current_p = self.game.camera.getP()
        if abs(current_p) > 0.1:
            new_p = current_p + (0 - current_p) * recovery_speed * dt
            self.game.camera.setP(new_p)
        else:
            self.game.camera.setP(0)
            self.recoil_recovery_task = None
            return task.done
        
        return task.cont
