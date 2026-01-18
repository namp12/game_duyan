"""
Monster System - Hệ thống quái vật và combat
"""
import random
import math
from settings import *

class Monster:
    def __init__(self, grid_x, grid_y, level=1):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE
        self.pixel_y = grid_y * TILE_SIZE
        
        # Stats dựa trên level
        self.max_hp = 20 + (level * 10)
        self.hp = self.max_hp
        self.damage = 5 + (level * 2)
        self.speed = 0.8 + (level * 0.1)  # Tiles per second
        self.level = level
        
        # Combat
        self.last_attack_time = 0
        self.attack_cooldown = 2000  # 2 giây
        
        # AI
        self.chase_range = 10  # Bắt đầu đuổi khi player trong 10 tiles
        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        
    def update(self, player_pos, map_data, fire_tiles, game_time):
        """
        Cập nhật AI và di chuyển của quái vật
        
        Args:
            player_pos: (grid_x, grid_y) của player
            map_data: Bản đồ game
            fire_tiles: Set các ô lửa
            game_time: Thời gian game
        """
        # Check khoảng cách đến player
        dx = player_pos[0] - self.grid_x
        dy = player_pos[1] - self.grid_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Nếu player trong phạm vi, đuổi theo
        if distance <= self.chase_range:
            # Di chuyển về phía player
            move_x = 0
            move_y = 0
            
            if abs(dx) > abs(dy):
                # Di chuyển theo trục X
                move_x = 1 if dx > 0 else -1
            else:
                # Di chuyển theo trục Y
                move_y = 1 if dy > 0 else -1
            
            # Thử di chuyển
            new_x = self.grid_x + move_x
            new_y = self.grid_y + move_y
            
            # Kiểm tra có thể di chuyển không
            if self.can_move_to(new_x, new_y, map_data, fire_tiles):
                self.grid_x = new_x
                self.grid_y = new_y
        
        # Smooth movement (interpolation)
        target_pixel_x = self.grid_x * TILE_SIZE
        target_pixel_y = self.grid_y * TILE_SIZE
        
        speed_factor = 0.15  # Smooth movement
        self.pixel_x += (target_pixel_x - self.pixel_x) * speed_factor
        self.pixel_y += (target_pixel_y - self.pixel_y) * speed_factor
    
    def can_move_to(self, grid_x, grid_y, map_data, fire_tiles):
        """Kiểm tra có thể di chuyển đến ô này không"""
        # Kiểm tra biên
        if grid_x < 0 or grid_x >= MAP_WIDTH or grid_y < 0 or grid_y >= MAP_HEIGHT:
            return False
        
        # Tránh lửa
        if (grid_x, grid_y) in fire_tiles:
            return False
        
        # Kiểm tra địa hình
        tile = map_data[grid_y][grid_x]
        if tile in [TILE_WATER, TILE_TREE, TILE_ROCK]:
            return False
        
        return True
    
    def can_attack_player(self, player_pos, game_time):
        """Kiểm tra có thể tấn công player không"""
        # Kiểm tra cooldown
        if game_time - self.last_attack_time < self.attack_cooldown:
            return False
        
        # Kiểm tra khoảng cách (phải sát nhau)
        dx = abs(player_pos[0] - self.grid_x)
        dy = abs(player_pos[1] - self.grid_y)
        
        if dx <= 1 and dy <= 1 and (dx + dy) > 0:  # Sát nhau nhưng không cùng vị trí
            return True
        
        return False
    
    def attack_player(self, player, game_time, game_log):
        """Tấn công player"""
        player.stats["HP"] -= self.damage
        self.last_attack_time = game_time
        
        game_log.append(f"👹 Quái vật tấn công! -{self.damage} HP")
        if len(game_log) > 10:
            game_log.pop(0)
    
    def take_damage(self, damage, game_log):
        """Nhận damage"""
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        
        return self.hp <= 0  # Return True nếu chết


class MonsterSystem:
    def __init__(self):
        self.monsters = []
        
    def spawn_monsters(self, level, map_data, player_pos, fire_tiles):
        """
        Spawn quái vật theo level
        
        Args:
            level: Level hiện tại
            map_data: Bản đồ
            player_pos: Vị trí player (để spawn xa player)
            fire_tiles: Các ô lửa (để tránh spawn ở đó)
        """
        self.monsters.clear()
        
        # Số lượng quái theo level
        if level == 1:
            monster_count = 0  # Tutorial - không có quái
        elif level <= 3:
            monster_count = random.randint(1, 2)
        elif level <= 6:
            monster_count = random.randint(2, 3)
        elif level <= 10:
            monster_count = random.randint(3, 4)
        else:
            monster_count = random.randint(4, 5)
        
        # Spawn quái
        spawn_attempts = 0
        max_attempts = 100
        
        while len(self.monsters) < monster_count and spawn_attempts < max_attempts:
            spawn_attempts += 1
            
            # Random vị trí
            x = random.randint(5, MAP_WIDTH - 5)
            y = random.randint(5, MAP_HEIGHT - 5)
            
            # Kiểm tra xa player (ít nhất 15 tiles)
            dx = abs(x - player_pos[0])
            dy = abs(y - player_pos[1])
            if dx + dy < 15:
                continue
            
            # Kiểm tra không phải lửa hoặc nước/cây/đá
            if (x, y) in fire_tiles:
                continue
            
            tile = map_data[y][x]
            if tile in [TILE_WATER, TILE_TREE, TILE_ROCK, TILE_FIRE]:
                continue
            
            # Spawn monster
            monster = Monster(x, y, level)
            self.monsters.append(monster)
        
        print(f"👹 Đã spawn {len(self.monsters)} quái vật cho level {level}")
    
    def update_all(self, player, map_data, fire_tiles, game_time, game_log):
        """Cập nhật tất cả quái vật"""
        player_pos = (player.grid_x, player.grid_y)
        
        for monster in self.monsters[:]:  # Copy list để có thể xóa
            # Update AI và di chuyển
            monster.update(player_pos, map_data, fire_tiles, game_time)
            
            # Kiểm tra tấn công player
            if monster.can_attack_player(player_pos, game_time):
                monster.attack_player(player, game_time, game_log)
    
    def get_monsters_in_range(self, grid_x, grid_y, attack_range=1.5):
        """Lấy danh sách quái trong tầm tấn công"""
        monsters_in_range = []
        
        for monster in self.monsters:
            dx = abs(monster.grid_x - grid_x)
            dy = abs(monster.grid_y - grid_y)
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance <= attack_range:
                monsters_in_range.append(monster)
        
        return monsters_in_range
    
    def remove_dead_monsters(self):
        """Xóa quái đã chết"""
        self.monsters = [m for m in self.monsters if m.hp > 0]
