import random
from settings import *

class RescueSystem:
    def __init__(self, pieces_required=TOTAL_PIECES, boat_time=BOAT_ARRIVAL_TIME):
        self.pieces_collected = 0
        self.piece_positions = []  # List of (col, row)
        
        # Level-specific parameters
        self.pieces_required = pieces_required
        self.boat_arrival_time = boat_time
        
        # Flare states
        self.flare_activated = False
        self.flare_fire_time = 0
        self.flare_fired = False
        
        # Boat states
        self.boat_arriving = False
        self.boat_arrival_start = 0
        self.boat_arrived = False
        self.boat_position = None  # (col, row)
        
        # Boarding states
        self.near_boat = False
        self.near_boat_start = 0
        self.can_board = False
        self.boarding = False
        
        # Win state
        self.escaped = False
    
    def place_pieces(self, map_data):
        """Đặt N mảnh ghép ngẫu nhiên trên bản đồ (N = pieces_required)"""
        valid_tiles = []
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                # Chỉ đặt trên cỏ hoặc hoa
                if map_data[row][col] in [TILE_GRASS, TILE_FLOWER]:
                    valid_tiles.append((col, row))
        
        # Chọn N vị trí ngẫu nhiên
        if len(valid_tiles) >= self.pieces_required:
            self.piece_positions = random.sample(valid_tiles, self.pieces_required)
            for col, row in self.piece_positions:
                map_data[row][col] = TILE_PIECE
    
    def check_piece_pickup(self, player, map_data, game_log):
        """Kiểm tra xem player có nhặt được mảnh ghép không"""
        player_pos = (player.grid_x, player.grid_y)
        
        if player_pos in self.piece_positions:
            self.piece_positions.remove(player_pos)
            self.pieces_collected += 1
            map_data[player.grid_y][player.grid_x] = TILE_GRASS
            game_log.append(f"Nhặt được mảnh ghép! ({self.pieces_collected}/{self.pieces_required})")
            if len(game_log) > 10:
                game_log.pop(0)
            
            # Kiểm tra đủ N mảnh
            if self.pieces_collected >= self.pieces_required:
                return True
        return False
    
    def activate_flare(self, game_time, game_log):
        """Kích hoạt pháo cứu hộ"""
        if not self.flare_activated:
            self.flare_activated = True
            self.flare_fire_time = game_time
            game_log.append("Đang kích hoạt pháo cứu hộ...")
            if len(game_log) > 10:
                game_log.pop(0)
    
    def update(self, game_time, map_data, game_log, fire_system=None):
        """Cập nhật trạng thái cứu hộ"""
        # Kiểm tra và đẩy vật phẩm ra ngoài nếu bị lửa bao quanh
        if fire_system:
            self.check_and_push_items(map_data, fire_system, game_log)
        
        # Kiểm tra pháo đã bắn chưa
        if self.flare_activated and not self.flare_fired:
            if game_time - self.flare_fire_time >= FLARE_DELAY:
                self.flare_fired = True
                self.boat_arriving = True
                self.boat_arrival_start = game_time
                game_log.append("Pháo cứu hộ đã bắn! Thuyền đang đến...")
                if len(game_log) > 10:
                    game_log.pop(0)
        
        # Kiểm tra thuyền đến (dùng boat_arrival_time từ level config)
        if self.boat_arriving and not self.boat_arrived:
            if game_time - self.boat_arrival_start >= self.boat_arrival_time:
                self.boat_arrived = True
                # Đặt thuyền ở bờ biển (tìm ô cát gần nước)
                self.spawn_boat(map_data)
                game_log.append("Thuyền đã đến! Hãy chạy đến thuyền!")
                if len(game_log) > 10:
                    game_log.pop(0)
    
    def spawn_boat(self, map_data):
        """Đặt thuyền ở vị trí ngẫu nhiên có thể đi đến được (dùng BFS)"""
        from collections import deque
        
        # Bước 1: Tìm tất cả các ô cát gần nước (nước không phải đá)
        valid_sand_positions = []
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                if map_data[row][col] == TILE_SAND:
                    # Kiểm tra có nước lân cận không (không phải đá ngầm)
                    has_water = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = col + dx, row + dy
                        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                            if map_data[ny][nx] == TILE_WATER:
                                has_water = True
                                break
                    if has_water:
                        valid_sand_positions.append((col, row))
        
        # Bước 2: Dùng DFS kiểm tra vị trí nào có thể đi đến được từ trung tâm đảo
        def dfs_can_reach(start_col, start_row, target_col, target_row, map_data):
            """Kiểm tra xem có đường đi từ start đến target không (DFS)"""
            if start_col == target_col and start_row == target_row:
                return True
            
            visited = set()
            stack = [(start_col, start_row)]  # DFS dùng stack
            visited.add((start_col, start_row))
            
            while stack:
                col, row = stack.pop()  # Pop từ cuối (LIFO)
                
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = col + dx, row + dy
                    
                    if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                        if (nx, ny) not in visited:
                            tile = map_data[ny][nx]
                            # Có thể đi qua: cỏ, cát, hoa, mảnh ghép, lửa, health
                            if tile not in [TILE_WATER, TILE_TREE, TILE_ROCK]:
                                visited.add((nx, ny))
                                
                                if nx == target_col and ny == target_row:
                                    return True
                                
                                stack.append((nx, ny))
            
            return False
        
        # Bước 3: Lọc các vị trí có thể đi đến được
        center_x, center_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
        reachable_positions = []
        
        for col, row in valid_sand_positions:
            if dfs_can_reach(center_x, center_y, col, row, map_data):
                reachable_positions.append((col, row))
        
        # Bước 4: Chọn ngẫu nhiên một vị trí
        if reachable_positions:
            self.boat_position = random.choice(reachable_positions)
            col, row = self.boat_position
            map_data[row][col] = TILE_BOAT
            print(f"Thuyền đậu tại ({col}, {row})")
        else:
            # Fallback: chọn bất kỳ vị trí cát nào
            if valid_sand_positions:
                self.boat_position = random.choice(valid_sand_positions)
                col, row = self.boat_position
                map_data[row][col] = TILE_BOAT
    
    def check_near_boat(self, player, game_time):
        """Kiểm tra player có gần thuyền không"""
        if not self.boat_arrived or not self.boat_position:
            self.near_boat = False
            self.can_board = False
            return
        
        player_pos = (player.grid_x, player.grid_y)
        boat_col, boat_row = self.boat_position
        
        # Kiểm tra khoảng cách (trong 2 ô)
        distance = abs(player_pos[0] - boat_col) + abs(player_pos[1] - boat_row)
        
        if distance <= 2:
            if not self.near_boat:
                self.near_boat = True
                self.near_boat_start = game_time
            
            # Kiểm tra đã đủ 5 giây chưa
            if game_time - self.near_boat_start >= BOARD_BOAT_TIME:
                self.can_board = True
        else:
            self.near_boat = False
            self.near_boat_start = 0
            self.can_board = False
    
    def board_boat(self):
        """Lên thuyền và thoát"""
        if self.can_board:
            self.escaped = True
            return True
        return False
    
    def is_player_frozen(self, game_time):
        """Kiểm tra player có bị đóng băng (đang bắn pháo) không"""
        if self.flare_activated and not self.flare_fired:
            return True
        return False
    
    def get_board_progress(self, game_time):
        """Trả về tiến độ lên thuyền (0.0 - 1.0)"""
        if not self.near_boat:
            return 0.0
        elapsed = game_time - self.near_boat_start
        return min(1.0, elapsed / BOARD_BOAT_TIME)
    
    def check_and_push_items(self, map_data, fire_system, game_log):
        """Kiểm tra và đẩy vật phẩm ra ngoài khi bị lửa bao quanh"""
        items_to_push = []
        
        # Kiểm tra từng mảnh ghép
        for pos in list(self.piece_positions):
            col, row = pos
            if self.is_surrounded_by_fire(col, row, fire_system):
                items_to_push.append(pos)
        
        # Đẩy các vật phẩm ra vị trí an toàn
        for pos in items_to_push:
            col, row = pos
            # Tìm vị trí mới ngẫu nhiên
            new_pos = self.find_random_safe_position(map_data, fire_system)
            if new_pos:
                # Xóa vật phẩm ở vị trí cũ
                self.piece_positions.remove(pos)
                map_data[row][col] = TILE_GRASS
                
                # Đặt vật phẩm ở vị trí mới
                new_col, new_row = new_pos
                self.piece_positions.append(new_pos)
                map_data[new_row][new_col] = TILE_PIECE
                
                game_log.append(f"Mảnh ghép bị đẩy ra vị trí mới!")
                if len(game_log) > 10:
                    game_log.pop(0)
    
    def is_surrounded_by_fire(self, col, row, fire_system):
        """Kiểm tra vật phẩm có bị lửa bao quanh không"""
        # Đếm số ô lửa xung quanh (4 hướng chính)
        fire_count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = col + dx, row + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                if fire_system.is_position_in_fire((nx, ny)):
                    fire_count += 1
        
        # Nếu 3/4 hướng bị lửa = bị bao quanh
        return fire_count >= 3
    
    def find_random_safe_position(self, map_data, fire_system):
        """Tìm vị trí ngẫu nhiên an toàn (không có lửa, có thể đi được)"""
        valid_positions = []
        
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                pos = (col, row)
                tile = map_data[row][col]
                
                # Chỉ đặt trên cỏ hoặc hoa, không có lửa xung quanh
                if tile in [TILE_GRASS, TILE_FLOWER]:
                    if not fire_system.is_position_in_fire(pos):
                        # Kiểm tra không có lửa gần (ít nhất 3 ô)
                        min_dist = float('inf')
                        for fire_pos in fire_system.fire_tiles:
                            dist = abs(fire_pos[0] - col) + abs(fire_pos[1] - row)
                            min_dist = min(min_dist, dist)
                        
                        if min_dist >= 3:  # Ít nhất 3 ô cách lửa
                            valid_positions.append(pos)
        
        # Chọn ngẫu nhiên
        if valid_positions:
            return random.choice(valid_positions)
        return None
