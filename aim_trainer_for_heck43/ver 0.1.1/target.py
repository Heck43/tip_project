from panda3d.core import Point3, Vec3, NodePath, CollisionNode, CollisionBox, CollisionSphere, BitMask32
import random

class Target:
    def __init__(self, game, pos):
        self.game = game
        self.position = pos
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.is_active = True
        self.create_model()

    def create_model(self):
        # Create root node
        self.model = NodePath("target_root")
        self.model.setPos(self.position)
        self.model.reparentTo(self.game.render)
        
        # Create collision nodes for different body parts
        
        # Head (100 damage) - сфера наверху
        head_node = CollisionNode('target_head')
        head_sphere = CollisionSphere(Point3(0, 0, 2.0), 0.4)  # Поднимаем голову выше
        head_node.addSolid(head_sphere)
        head_node.setIntoCollideMask(BitMask32.bit(1))
        self.head_np = self.model.attachNewNode(head_node)
        
        # Body (40-80 damage) - основной бокс тела
        body_node = CollisionNode('target_body')
        body_box = CollisionBox(Point3(0, 0, 1.2), 0.4, 0.3, 0.6)  # Центрируем тело
        body_node.addSolid(body_box)
        body_node.setIntoCollideMask(BitMask32.bit(1))
        self.body_np = self.model.attachNewNode(body_node)
        
        # Left arm (40-80 damage) - левая рука
        left_arm_node = CollisionNode('target_left_arm')
        left_arm_box = CollisionBox(Point3(-0.6, 0, 1.4), 0.2, 0.2, 0.5)  # Сдвигаем левую руку
        left_arm_node.addSolid(left_arm_box)
        left_arm_node.setIntoCollideMask(BitMask32.bit(1))
        self.left_arm_np = self.model.attachNewNode(left_arm_node)
        
        # Right arm (40-80 damage) - правая рука
        right_arm_node = CollisionNode('target_right_arm')
        right_arm_box = CollisionBox(Point3(0.6, 0, 1.4), 0.2, 0.2, 0.5)  # Сдвигаем правую руку
        right_arm_node.addSolid(right_arm_box)
        right_arm_node.setIntoCollideMask(BitMask32.bit(1))
        self.right_arm_np = self.model.attachNewNode(right_arm_node)
        
        # Legs (40 damage) - ноги внизу
        legs_node = CollisionNode('target_legs')
        legs_box = CollisionBox(Point3(0, 0, 0.4), 0.4, 0.3, 0.8)  # Опускаем ноги вниз
        legs_node.addSolid(legs_box)
        legs_node.setIntoCollideMask(BitMask32.bit(1))
        self.legs_np = self.model.attachNewNode(legs_node)
        
        # Make all parts visible with red color
        for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
            np.show()
            np.setColor(0.8, 0.2, 0.2, 1)

    def get_damage_for_part(self, part_name):
        if part_name == 'target_head':
            return 100
        elif part_name in ['target_body', 'target_left_arm', 'target_right_arm']:
            return random.randint(40, 80)
        elif part_name == 'target_legs':
            return 40
        return 0

    def check_hit(self, from_point, direction):
        if not self.is_active:
            return False, None, 0
            
        # Use collision queue from the game's traverser
        self.game.cTrav.traverse(self.model)
        
        if self.game.cQueue.getNumEntries() > 0:
            self.game.cQueue.sortEntries()
            entry = self.game.cQueue.getEntry(0)
            
            hit_node = entry.getIntoNode()
            if hit_node.getName().startswith('target_'):
                hit_pos = entry.getSurfacePoint(self.game.render)
                damage = self.get_damage_for_part(hit_node.getName())
                self.take_damage(damage)
                return True, hit_pos, damage
                
        return False, None, 0

    def take_damage(self, damage):
        if not self.is_active:
            return
            
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.respawn()
        else:
            # Change color based on remaining health
            health_fraction = self.current_hp / self.max_hp
            for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
                np.setColor(0.8, 0.2 + 0.6 * (1 - health_fraction), 0.2, 1)

    def disable_collisions(self):
        for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
            np.node().setIntoCollideMask(BitMask32.allOff())

    def enable_collisions(self):
        for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
            np.node().setIntoCollideMask(BitMask32.bit(1))

    def respawn(self):
        self.is_active = False
        # Скрываем все части манекена и отключаем коллизии
        for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
            np.hide()
        self.disable_collisions()
        
        # Через 3 секунды восстанавливаем манекен
        taskMgr.doMethodLater(3.0, self.restore_target, 'restore_target')
    
    def restore_target(self, task):
        self.current_hp = self.max_hp
        self.is_active = True
        # Показываем все части и включаем коллизии
        for np in [self.head_np, self.body_np, self.left_arm_np, self.right_arm_np, self.legs_np]:
            np.show()
            np.setColor(0.8, 0.2, 0.2, 1)  # Возвращаем исходный цвет
        self.enable_collisions()
        return task.done

    def destroy(self):
        if hasattr(self, 'model') and self.model:
            self.model.removeNode()
