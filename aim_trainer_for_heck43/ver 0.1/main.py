from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, WindowProperties, AmbientLight, DirectionalLight
from panda3d.core import Vec3, BitMask32, CollisionTraverser, CollisionNode
from panda3d.core import CollisionSphere, CollisionRay, CollisionHandlerQueue, CardMaker
from panda3d.core import CollisionHandlerPusher, NodePath, TextNode
from panda3d.core import CollisionBox
import sys
import math
from math import sin, cos, pi, radians as deg2Rad
from weapon import Weapon
from enemy import Enemy, EnemySpawner

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Basic setup
        self.setBackgroundColor(0.1, 0.1, 0.1)
        self.setup_lights()
        
        # Initialize collision system
        self.cTrav = CollisionTraverser('traverser')
        self.cQueue = CollisionHandlerQueue()
        
        # Player setup
        self.setup_player()
        
        # Mouse control
        self.setup_mouse()
        
        # Level setup
        self.setup_level()
        
        # Collision setup
        self.setup_collision()
        
        # Game state
        self.health = 100
        self.score = 0
        
        # Movement settings
        self.move_speed = 10.0
        self.sprint_speed = 15.0
        self.ground_height = 0  # Fixed ground height
        
        # Weapon setup
        self.weapon = Weapon(self)
        
        # Enemy spawner
        # self.enemy_spawner = EnemySpawner(self)
        
        # UI setup
        self.setup_ui()
        
        # Key bindings
        self.setup_keys()
        
        # Add movement task
        self.taskMgr.add(self.move_player, "movePlayerTask")
    
    def setup_lights(self):
        # Ambient light
        alight = AmbientLight('ambient')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        # Directional light
        dlight = DirectionalLight('directional')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
    
    def setup_player(self):
        # Disable default mouse control
        self.disableMouse()
        
        # Player camera settings
        self.camera_height = 1.8
        self.camera.setPos(0, 0, self.camera_height)
        self.camera_pitch = 0  # Initialize camera pitch
        
        # Mouse settings
        self.mouse_sensitivity = 0.1
        
        # Setup player collision
        self.player_collision = CollisionNode('player')
        player_sphere = CollisionSphere(0, 0, 0, 1.0)
        self.player_collision.addSolid(player_sphere)
        self.player_collision_np = self.camera.attachNewNode(self.player_collision)
        
        # Set up collision handler
        self.collision_handler = CollisionHandlerPusher()
        self.collision_handler.addCollider(self.player_collision_np, self.camera)
        self.cTrav.addCollider(self.player_collision_np, self.collision_handler)
    
    def setup_mouse(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)
    
    def setup_level(self):
        # Create temporary floor
        cm = CardMaker('floor')
        cm.setFrame(-50, 50, -50, 50)
        floor = self.render.attachNewNode(cm.generate())
        floor.setPos(0, 0, 0)
        floor.setP(-90)
        floor.setColor(0.3, 0.3, 0.3)
        
        # Add collision to floor
        floor_col = CollisionNode('floor')
        floor_col.addSolid(CollisionBox(Point3(0, 0, -0.5), 50, 50, 0.5))
        floor_col_np = floor.attachNewNode(floor_col)
    
    def setup_collision(self):
        # Ground collision detection
        self.ground_ray = CollisionRay()
        self.ground_ray.setOrigin(0, 0, 0)
        self.ground_ray.setDirection(0, 0, -1)
        
        ground_col = CollisionNode('groundRay')
        ground_col.addSolid(self.ground_ray)
        self.ground_col_np = self.camera.attachNewNode(ground_col)
        self.ground_handler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ground_col_np, self.ground_handler)
    
    def setup_ui(self):
        self.health_text = OnscreenText(
            text=f"Health: {self.health}",
            pos=(-1.3, 0.9),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.07
        )
        
        self.ammo_text = OnscreenText(
            text="Ammo: 30",
            pos=(-1.3, 0.8),
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            scale=0.07
        )
        
        self.score_text = OnscreenText(
            text=f"Score: {self.score}",
            pos=(1.0, 0.9),
            fg=(1, 1, 1, 1),
            align=TextNode.ARight,
            scale=0.07
        )
    
    def setup_keys(self):
        # Movement keys
        self.keys = {
            'w': False,
            's': False,
            'a': False,
            'd': False,
            'shift': False
        }
        
        # Key event bindings for movement
        self.accept('w', self.keys.__setitem__, ['w', True])
        self.accept('w-up', self.keys.__setitem__, ['w', False])
        self.accept('s', self.keys.__setitem__, ['s', True])
        self.accept('s-up', self.keys.__setitem__, ['s', False])
        self.accept('a', self.keys.__setitem__, ['a', True])
        self.accept('a-up', self.keys.__setitem__, ['a', False])
        self.accept('d', self.keys.__setitem__, ['d', True])
        self.accept('d-up', self.keys.__setitem__, ['d', False])
        self.accept('shift', self.keys.__setitem__, ['shift', True])
        self.accept('shift-up', self.keys.__setitem__, ['shift', False])
        
        # Weapon switching keys
        self.accept('1', self.weapon.switch_weapon, ['pistol'])
        self.accept('2', self.weapon.switch_weapon, ['rifle'])
        self.accept('3', self.weapon.switch_weapon, ['sniper'])
        self.accept('4', self.weapon.switch_weapon, ['dual_revolvers'])
        
        # Mouse wheel weapon switching
        self.accept('wheel_up', self.cycle_weapon_next)
        self.accept('wheel_down', self.cycle_weapon_prev)
        
        # Shooting
        self.accept('mouse1', self.weapon.shoot)
        self.accept('r', self.weapon.reload)
    
    def cycle_weapon_next(self):
        weapons = list(self.weapon.weapon_models.keys())
        current_index = weapons.index(self.weapon.current_weapon)
        next_index = (current_index + 1) % len(weapons)
        self.weapon.switch_weapon(weapons[next_index])
    
    def cycle_weapon_prev(self):
        weapons = list(self.weapon.weapon_models.keys())
        current_index = weapons.index(self.weapon.current_weapon)
        prev_index = (current_index - 1) % len(weapons)
        self.weapon.switch_weapon(weapons[prev_index])
    
    def update_key(self, key, value):
        self.keys[key] = value
    
    def move_player(self, task):
        dt = globalClock.getDt()
        
        # Always keep player at ground height
        self.camera.setZ(self.ground_height + 1.8)
        
        # Handle sprinting
        self.is_sprinting = self.keys["shift"]
        current_speed = self.sprint_speed if self.is_sprinting else self.move_speed
        
        # Mouse look
        if self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            
            if self.win.movePointer(0, 
                int(self.win.getProperties().getXSize() / 2), 
                int(self.win.getProperties().getYSize() / 2)):
                # Horizontal rotation (yaw)
                self.camera.setH(self.camera.getH() - 
                               (x - self.win.getProperties().getXSize() / 2) * 
                               self.mouse_sensitivity)
                
                # Vertical rotation (pitch) with limits
                self.camera_pitch -= (y - self.win.getProperties().getYSize() / 2) * self.mouse_sensitivity
                
                # Limit pitch to prevent over-rotation
                self.camera_pitch = max(min(self.camera_pitch, 90), -90)
                
                # Set camera pitch
                self.camera.setP(self.camera_pitch)
        
        # Movement
        move_vec = Vec3(0, 0, 0)
        
        if self.keys['w']: move_vec.addY(1)
        if self.keys['s']: move_vec.addY(-1)
        if self.keys['a']: move_vec.addX(-1)
        if self.keys['d']: move_vec.addX(1)
        
        # Normalize movement vector
        if move_vec.length() > 0:
            move_vec.normalize()
        
        # Apply movement relative to camera direction
        heading_rad = deg2Rad(self.camera.getH())
        move_vec = Vec3(
            move_vec.getX() * cos(heading_rad) - move_vec.getY() * sin(heading_rad),
            move_vec.getX() * sin(heading_rad) + move_vec.getY() * cos(heading_rad),
            0
        )
        
        # Apply movement
        self.camera.setPos(
            self.camera.getPos() + 
            move_vec * current_speed * dt
        )
        
        return Task.cont
    
    def take_damage(self, damage):
        self.health -= damage
        self.health_text.setText(f"Health: {self.health}")
        if self.health <= 0:
            self.game_over()
    
    def update_score(self):
        self.score_text.setText(f"Score: {self.score}")
    
    def game_over(self):
        # Implement game over logic here
        pass

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
