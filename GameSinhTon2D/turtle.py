import pygame
import random
from settings import *

class TurtleEnemy:
    def __init__(self, x, y):
        """
        Quái rùa - Level 2 enemy
        x, y: vị trí grid trên bản đồ
        """
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        
        # Stats
        self.hp = 20
        self.max_hp = 20
        self.attack_range = 3  # tiles
        self.attack_damage = 5
        self.attack_cooldown = 2000  # ms
        self.last_attack_time = 0
        
        # Movement
        self.move_speed = 500  # ms per tile
        self.last_move_time = 0
        
        # State
        self.is_chasing = False
        self.is_attacking = False
        
        # Water projectile
        self.projectile = None
    
    def get_distance_to(self, target_pos):
        """Tính khoảng cách Manhattan đến vị trí target"""
        return abs(self.grid_x - target_pos[0]) + abs(self.grid_y - target_pos[1])
    
    def is_player_in_range(self, player_pos):
        """Kiểm tra player có trong phạm vi tấn công (3 ô)"""
        distance = self.get_distance_to(player_pos)
        return distance <= self.attack_range
    
    def can_move_to(self, x, y, map_data):
        """Kiểm tra có thể di chuyển đến ô (x, y)"""
        if x < 0 or x >= MAP_WIDTH or y < 0 or y >= MAP_HEIGHT:
            return False
        
        tile = map_data[y][x]
        # Rùa có thể đi trên cỏ, cát, hoa (không qua nước, cây, đá)
        walkable_tiles = [TILE_GRASS, TILE_SAND, TILE_FLOWER]
        return tile in walkable_tiles
    
    def move_toward_player(self, player_pos, map_data, game_time):
        """Di chuyển 1 bước về phía player"""
        if game_time - self.last_move_time < self.move_speed:
            return  # Chưa đến lúc di chuyển
        
        dx = player_pos[0] - self.grid_x
        dy = player_pos[1] - self.grid_y
        
        # Ưu tiên di chuyển theo trục có khoảng cách lớn hơn
        move_x, move_y = 0, 0
        
        if abs(dx) > abs(dy):
            move_x = 1 if dx > 0 else -1
        else:
            move_y = 1 if dy > 0 else -1
        
        # Thử di chuyển
        new_x = self.grid_x + move_x
        new_y = self.grid_y + move_y
        
        if self.can_move_to(new_x, new_y, map_data):
            self.grid_x = new_x
            self.grid_y = new_y
            self.last_move_time = game_time
            
            # Smooth movement
            target_pixel_x = self.grid_x * TILE_SIZE
            target_pixel_y = self.grid_y * TILE_SIZE
            self.pixel_x += (target_pixel_x - self.pixel_x) * 0.2
            self.pixel_y += (target_pixel_y - self.pixel_y) * 0.2
    
    def attack(self, player_pos, game_time):
        """
        Tấn công player bằng nước
        Returns: damage amount if hit, else 0
        """
        if game_time - self.last_attack_time < self.attack_cooldown:
            return 0  # Cooldown chưa xong
        
        # Chỉ tấn công khi player trong phạm vi
        if not self.is_player_in_range(player_pos):
            return 0
        
        # Bắn projectile
        self.last_attack_time = game_time
        self.is_attacking = True
        
        # Tạo water projectile
        self.projectile = {
            'start': (self.grid_x, self.grid_y),
            'target': player_pos,
            'start_time': game_time,
            'duration': 500  # ms để đạn bay đến player
        }
        
        return self.attack_damage
    
    def update(self, player_pos, game_time, map_data):
        """Update turtle behavior"""
        # Smooth pixel movement
        target_pixel_x = self.grid_x * TILE_SIZE
        target_pixel_y = self.grid_y * TILE_SIZE
        self.pixel_x += (target_pixel_x - self.pixel_x) * 0.15
        self.pixel_y += (target_pixel_y - self.pixel_y) * 0.15
        
        # Check if player in range
        in_range = self.is_player_in_range(player_pos)
        
        if in_range:
            # Chase player
            self.is_chasing = True
            self.move_toward_player(player_pos, map_data, game_time)
        else:
            # Player escaped
            self.is_chasing = False
        
        # Update projectile
        if self.projectile:
            elapsed = game_time - self.projectile['start_time']
            if elapsed >= self.projectile['duration']:
                self.projectile = None
                self.is_attacking = False
    
    def draw(self, screen, camera_x, camera_y):
        """Vẽ turtle lên màn hình"""
        # Vị trí trên viewport
        screen_x = int(self.pixel_x - camera_x)
        screen_y = int(self.pixel_y - camera_y)
        
        # Chỉ vẽ nếu trong viewport
        if -TILE_SIZE < screen_x < VIEWPORT_WIDTH and -TILE_SIZE < screen_y < VIEWPORT_HEIGHT:
            # Turtle body (dark green)
            turtle_color = (80, 120, 80)
            pygame.draw.circle(screen, turtle_color, 
                             (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 
                             TILE_SIZE//2 - 2)
            
            # Shell pattern (lighter green)
            shell_color = (100, 150, 100)
            pygame.draw.circle(screen, shell_color, 
                             (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 
                             TILE_SIZE//3)
            
            # HP bar
            if self.hp < self.max_hp:
                bar_width = TILE_SIZE
                bar_height = 4
                bar_x = screen_x
                bar_y = screen_y - 8
                
                # Background (red)
                pygame.draw.rect(screen, (200, 50, 50), 
                               (bar_x, bar_y, bar_width, bar_height))
                
                # HP (green)
                hp_width = int(bar_width * (self.hp / self.max_hp))
                pygame.draw.rect(screen, (50, 200, 50), 
                               (bar_x, bar_y, hp_width, bar_height))
        
        # Draw projectile if exists
        if self.projectile:
            self._draw_projectile(screen, camera_x, camera_y)
    
    def _draw_projectile(self, screen, camera_x, camera_y):
        """Vẽ water projectile đang bay"""
        if not self.projectile:
            return
        
        import pygame.time
        current_time = pygame.time.get_ticks()
        
        start_pos = self.projectile['start']
        target_pos = self.projectile['target']
        start_time = self.projectile['start_time']
        duration = self.projectile['duration']
        
        # Tính vị trí hiện tại của projectile (interpolate)
        elapsed = current_time - start_time
        progress = min(1.0, elapsed / duration)
        
        current_x = start_pos[0] + (target_pos[0] - start_pos[0]) * progress
        current_y = start_pos[1] + (target_pos[1] - start_pos[1]) * progress
        
        # Convert to pixel coordinates
        pixel_x = current_x * TILE_SIZE + TILE_SIZE//2
        pixel_y = current_y * TILE_SIZE + TILE_SIZE//2
        
        screen_x = int(pixel_x - camera_x)
        screen_y = int(pixel_y - camera_y)
        
        # Draw water droplet (blue)
        pygame.draw.circle(screen, (100, 150, 255), (screen_x, screen_y), 6)
        pygame.draw.circle(screen, (150, 200, 255), (screen_x, screen_y), 3)


def spawn_turtles(map_data, count=10):
    """
    Spawn turtle enemies trên bản đồ
    Returns: list of TurtleEnemy
    """
    turtles = []
    attempts = 0
    max_attempts = 1000
    
    while len(turtles) < count and attempts < max_attempts:
        attempts += 1
        
        # Random position
        x = random.randint(5, MAP_WIDTH - 5)
        y = random.randint(5, MAP_HEIGHT - 5)
        
        # Check if valid spawn location
        tile = map_data[y][x]
        if tile in [TILE_GRASS, TILE_SAND, TILE_FLOWER]:
            # Check not too close to other turtles
            too_close = False
            for turtle in turtles:
                dist = abs(turtle.grid_x - x) + abs(turtle.grid_y - y)
                if dist < 10:  # Minimum 10 tiles apart
                    too_close = True
                    break
            
            if not too_close:
                turtles.append(TurtleEnemy(x, y))
    
    return turtles
