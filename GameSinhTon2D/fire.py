import random
from settings import *

class FireSystem:
    def __init__(self, level_config=None):
        self.fire_tiles = set()  # Set of (col, row) that are on fire
        self.warning_tiles = {}  # Dict {(col, row): warning_start_time}
        self.fire_intensity = {}  # Dict {(col, row): burn_time} - thời gian đã cháy
        self.last_spread_time = 0
        self.fire_started = False
        self.game_start_time = 0
        
        # Level-specific parameters
        if level_config:
            self.spread_interval = level_config.get("fire_spread_interval", FIRE_SPREAD_INTERVAL)
            self.start_delay = level_config.get("fire_start_delay", FIRE_START_DELAY)
            self.spawn_points = level_config.get("fire_spawn_points", 1)
        else:
            self.spread_interval = FIRE_SPREAD_INTERVAL
            self.start_delay = FIRE_START_DELAY
            self.spawn_points = 1
        
        # Player damage tracking
        self.last_damage_time = 0
        self.damage_invuln_until = 0  # Thời gian miễn damage
        self.consecutive_hits = 0      # Số lần bị hit liên tiếp
        
        # Rain control
        self.spreading_paused = False  # Tạm dừng lan rộng khi mưa
    
    def start_fire(self, map_data, game_time):
        """Bắt đầu đám cháy tại N vị trí ngẫu nhiên (dựa trên spawn_points)"""
        if self.fire_started:
            return
        
        self.game_start_time = game_time
        
        # Tìm các ô cỏ hoặc cây ngẫu nhiên để bắt đầu cháy
        valid_tiles = []
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                if map_data[row][col] in [TILE_GRASS, TILE_TREE, TILE_FLOWER]:
                    valid_tiles.append((col, row))
        
        if valid_tiles:
            # Spawn multiple fire points
            spawn_count = min(self.spawn_points, len(valid_tiles))
            for i in range(spawn_count):
                start_pos = random.choice(valid_tiles)
                self.fire_tiles.add(start_pos)
                self.fire_intensity[start_pos] = game_time
                # Remove để tránh spawn chồng lên nhau
                valid_tiles.remove(start_pos)
                print(f"🔥 Điểm lửa {i+1}/{spawn_count} tại ({start_pos[0]}, {start_pos[1]})!")
            
            self.fire_started = True
            self.last_spread_time = game_time
    
    def get_neighbors(self, col, row, distance=1):
        """Lấy tất cả ô lân cận trong khoảng cách distance"""
        neighbors = []
        for dx in range(-distance, distance + 1):
            for dy in range(-distance, distance + 1):
                if dx == 0 and dy == 0:
                    continue
                new_col, new_row = col + dx, row + dy
                if 0 <= new_col < MAP_WIDTH and 0 <= new_row < MAP_HEIGHT:
                    neighbors.append((new_col, new_row))
        return neighbors
    
    def is_flammable(self, tile_type):
        """Kiểm tra tile có thể cháy không"""
        return tile_type in [TILE_GRASS, TILE_TREE, TILE_FLOWER]
    
    def is_safe_zone(self, tile_type):
        """Kiểm tra tile có phải vùng an toàn (chặn lửa) không"""
        return tile_type in [TILE_WATER, TILE_SAND, TILE_ROCK]
    
    def update(self, map_data, game_time):
        """Cập nhật và lan rộng lửa"""
        if not self.fire_started:
            # Kiểm tra xem đã đến lúc bắt đầu cháy chưa (dùng start_delay từ level config)
            if game_time > self.start_delay:
                self.start_fire(map_data, game_time)
            return
        
        # Cập nhật warning tiles (kiểm tra tiles đã hết thời gian cảnh báo)
        tiles_to_ignite = []
        for pos, warn_time in list(self.warning_tiles.items()):
            if game_time - warn_time >= FIRE_WARNING_TIME:
                tiles_to_ignite.append(pos)
        
        # Đốt các tiles đã hết thời gian cảnh báo
        for pos in tiles_to_ignite:
            self.fire_tiles.add(pos)
            self.fire_intensity[pos] = game_time
            del self.warning_tiles[pos]
        
        # Kiểm tra thời gian lan lửa (dùng spread_interval từ level config)
        if game_time - self.last_spread_time < self.spread_interval:
            return
        
        # Kiểm tra xem có đang mưa không (tạm dừng lan rộng)
        if self.spreading_paused:
            return
        
        self.last_spread_time = game_time
        
        # Lan lửa sang các ô lân cận (với warning)
        new_warning_tiles = {}
        for (col, row) in self.fire_tiles:
            # Kiểm tra 4 hướng chính
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_col, new_row = col + dx, row + dy
                
                # Kiểm tra biên
                if 0 <= new_col < MAP_WIDTH and 0 <= new_row < MAP_HEIGHT:
                    tile = map_data[new_row][new_col]
                    pos = (new_col, new_row)
                    
                    # Chỉ lan sang tiles có thể cháy
                    if self.is_flammable(tile):
                        if pos not in self.fire_tiles and pos not in self.warning_tiles:
                            # 60% cơ hội lan sang (tăng từ 50%)
                            if random.random() < 0.6:
                                new_warning_tiles[pos] = game_time
        
        # Thêm warning tiles mới
        self.warning_tiles.update(new_warning_tiles)
        
        # Cập nhật map_data để hiển thị lửa
        for (col, row) in self.fire_tiles:
            map_data[row][col] = TILE_FIRE
    
    def get_fire_intensity_at(self, pos, game_time):
        """Tính cường độ lửa tại vị trí (để xác định damage)"""
        if pos not in self.fire_tiles:
            return 0
        
        burn_time = game_time - self.fire_intensity[pos]
        
        # Đếm số ô lửa xung quanh (fire density)
        neighbors = self.get_neighbors(pos[0], pos[1], distance=1)
        fire_neighbors = sum(1 for n in neighbors if n in self.fire_tiles)
        
        # Lửa yếu: mới cháy (< 5s) hoặc ít lửa xung quanh
        if burn_time < 5000 or fire_neighbors < 2:
            return FIRE_DAMAGE_LIGHT
        # Lửa trung bình: cháy lâu hoặc nhiều lửa xung quanh
        elif burn_time < 15000 or fire_neighbors < 5:
            return FIRE_DAMAGE_MEDIUM
        # Lửa mạnh: trung tâm đám cháy
        else:
            return FIRE_DAMAGE_HEAVY
    
    def check_player_damage(self, player, game_time):
        """
        Kiểm tra và áp dụng damage cho player
        Returns: (should_damage, damage_amount, heat_level)
        heat_level: 0=safe, 1=warning, 2=danger, 3=on_fire
        """
        player_pos = (player.grid_x, player.grid_y)
        
        # 1. Kiểm tra xem player có trong lửa không
        if player_pos in self.fire_tiles:
            # Kiểm tra invulnerability
            if game_time < self.damage_invuln_until:
                return (False, 0, 3)  # On fire but invulnerable
            
            # Kiểm tra damage interval
            if game_time - self.last_damage_time < FIRE_DAMAGE_INTERVAL:
                return (False, 0, 3)
            
            # Áp dụng damage dựa trên fire intensity
            damage = self.get_fire_intensity_at(player_pos, game_time)
            self.last_damage_time = game_time
            self.damage_invuln_until = game_time + FIRE_INVULN_TIME
            self.consecutive_hits += 1
            
            return (True, damage, 3)
        
        # 2. Kiểm tra heat zones (warning zones)
        min_distance = float('inf')
        for fire_pos in self.fire_tiles:
            distance = abs(fire_pos[0] - player_pos[0]) + abs(fire_pos[1] - player_pos[1])
            min_distance = min(min_distance, distance)
        
        # Reset consecutive hits nếu thoát khỏi lửa
        if player_pos not in self.fire_tiles:
            self.consecutive_hits = 0
        
        # Trả về heat level
        if min_distance == float('inf'):
            return (False, 0, 0)  # Safe
        elif min_distance <= HEAT_WARNING_DISTANCE:
            return (False, 0, 2)  # Danger zone (red warning)
        elif min_distance <= HEAT_DANGER_DISTANCE:
            return (False, 0, 1)  # Warning zone (yellow warning)
        else:
            return (False, 0, 0)  # Safe
    
    def get_warning_tiles_visual(self, game_time):
        """Lấy danh sách tiles cần hiển thị warning (nhấp nháy)"""
        # Chỉ hiển thị nếu đang trong chu kỳ blink
        should_show = (game_time % (WARNING_BLINK_SPEED * 2)) < WARNING_BLINK_SPEED
        if should_show:
            return list(self.warning_tiles.keys())
        return []
    
    def is_tile_blocked_by_safe_zone(self, from_pos, to_pos, map_data):
        """Kiểm tra xem lửa có bị chặn bởi safe zone không"""
        # Simple check: if target is in safe zone, fire cannot spread
        to_row, to_col = to_pos[1], to_pos[0]
        if self.is_safe_zone(map_data[to_row][to_col]):
            return True
        return False
    
    def is_position_in_fire(self, pos):
        """Kiểm tra vị trí có đang cháy không (chỉ ô thực sự đang cháy)"""
        return pos in self.fire_tiles
    
    def can_move_to_position(self, from_pos, to_pos):
        """
        Kiểm tra có thể di chuyển đến vị trí không
        Chặn di chuyển từ ô lửa -> ô lửa khác (chỉ tính ô đang cháy thực sự)
        """
        # Chỉ kiểm tra ô đang cháy THỰC SỰ (trong fire_tiles), không tính ô cảnh báo
        from_is_fire = from_pos in self.fire_tiles
        to_is_fire = to_pos in self.fire_tiles
        
        # Nếu cả hai đều đang cháy thực sự -> chặn di chuyển
        if from_is_fire and to_is_fire:
            return False
        
        return True
