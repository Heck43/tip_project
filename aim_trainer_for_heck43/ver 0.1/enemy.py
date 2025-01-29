from direct.actor.Actor import Actor
from panda3d.core import Vec3, Point3, CollisionNode, CollisionSphere
import random
import math

class Enemy:
    def __init__(self, game, pos):
        self.game = game
        
        # Load enemy model (temporary cube for now)
        self.model = loader.loadModel("models/box")
        self.model.reparentTo(render)
        self.model.setPos(pos)
        self.model.setScale(0.5)
        self.model.setColor(1, 0, 0)  # Red color for enemies
        
        # Enemy properties
        self.health = 100
        self.speed = 5
        self.damage = 10
        self.attack_range = 2
        
        # Setup collision
        self.setup_collision()
        
        # AI state
        self.state = "chase"  # States: chase, attack, stunned
        
        # Add to game's update task
        self.game.taskMgr.add(self.update, "enemyUpdate")
    
    def setup_collision(self):
        # Collision sphere for enemy
        collision_sphere = CollisionSphere(0, 0, 0, 0.5)
        cnode = CollisionNode('enemy')
        cnode.addSolid(collision_sphere)
        self.collision_node = self.model.attachNewNode(cnode)
    
    def update(self, task):
        if not hasattr(self, 'model'):
            return task.done
            
        dt = globalClock.getDt()
        
        if self.state == "chase":
            self.chase_player(dt)
        elif self.state == "attack":
            self.attack_player()
            
        return task.cont
    
    def chase_player(self, dt):
        # Get direction to player
        player_pos = self.game.camera.getPos()
        enemy_pos = self.model.getPos()
        direction = player_pos - enemy_pos
        
        # Calculate distance to player
        distance = direction.length()
        
        if distance < self.attack_range:
            self.state = "attack"
            return
            
        # Normalize direction and move
        if distance > 0:
            direction.normalize()
            new_pos = enemy_pos + direction * self.speed * dt
            self.model.setPos(new_pos)
            
            # Make enemy face player
            self.model.lookAt(player_pos)
    
    def attack_player(self):
        # Simple attack implementation
        player_pos = self.game.camera.getPos()
        enemy_pos = self.model.getPos()
        distance = (player_pos - enemy_pos).length()
        
        if distance < self.attack_range:
            self.game.take_damage(self.damage)
            self.state = "chase"
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()
    
    def die(self):
        self.model.removeNode()
        self.game.score += 100
        self.game.update_score()
        
class EnemySpawner:
    def __init__(self, game):
        self.game = game
        self.enemies = []
        self.spawn_radius = 20
        self.max_enemies = 10
        self.spawn_interval = 3.0
        
        # Start spawning
        self.game.taskMgr.doMethodLater(self.spawn_interval, 
                                      self.spawn_enemy, 
                                      "spawnEnemy")
    
    def spawn_enemy(self, task):
        if len(self.enemies) < self.max_enemies:
            # Random position around player
            angle = random.uniform(0, 2 * math.pi)
            x = math.cos(angle) * self.spawn_radius
            y = math.sin(angle) * self.spawn_radius
            pos = self.game.camera.getPos() + Point3(x, y, 0)
            
            # Create new enemy
            enemy = Enemy(self.game, pos)
            self.enemies.append(enemy)
        
        return task.again  # Repeat after interval
