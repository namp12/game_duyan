"""
Helper System - Sử dụng BFS và DFS để hỗ trợ người chơi
"""
import pygame
from collections import deque
from settings import *

class PathHelper:
    def __init__(self):
        # DFS: Tìm mảnh ghép
        self.piece_path = []
        self.piece_targets = []  # Vị trí các mảnh ghép đích
        self.piece_path_visible = False
        self.piece_path_time = 0
        
        # BFS: Thoát hiểm
        self.escape_path = []
        self.escape_path_visible = False
        self.escape_path_time = 0
        
        # BFS: Dự đoán lửa lan
        self.danger_tiles = set()
    
    # ==================== BFS: TÌM MẢNH GHÉP ====================
    def find_all_pieces_bfs(self, player_pos, map_data, piece_positions):
        """
        Thuật toán BFS tìm đường đến TẤT CẢ các mảnh ghép
        Trả về: dict{piece_pos: path} - đường đi từ player đến mỗi piece
        """
        if not piece_positions:
            return {}
        
        start_col, start_row = player_pos
        all_paths = {}
        
        # Tìm đường đến từng mảnh ghép
        for target_piece in piece_positions:
            # Queue: (col, row, path) - BFS dùng queue
            queue = deque([(start_col, start_row, [])])
            visited = set()
            visited.add((start_col, start_row))
            found_path = None
            
            while queue:
                col, row, path = queue.popleft()  # FIFO - lấy từ đầu
                
                # Kiểm tra đã đến mảnh ghép đích chưa
                if (col, row) == target_piece:
                    found_path = path  # BFS đảm bảo đường ngắn nhất
                    break
                
                # Duyệt 4 hướng: phải, xuống, trái, lên
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    nx, ny = col + dx, row + dy
                    
                    if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                        if (nx, ny) not in visited:
                            tile = map_data[ny][nx]
                            # Có thể đi qua: cỏ, cát, hoa, mảnh ghép, health
                            if tile not in [TILE_WATER, TILE_TREE, TILE_FIRE, TILE_ROCK]:
                                visited.add((nx, ny))
                                new_path = path + [(nx, ny)]
                                queue.append((nx, ny, new_path))
            
            if found_path:
                all_paths[target_piece] = found_path
        
        return all_paths
    
    def activate_piece_finder(self, player, map_data, piece_positions, game_time, game_log):
        """Kích hoạt DFS tìm mảnh ghép GẦN NHẤT - Cần Stamina >= 30"""
        # Kiểm tra còn mảnh ghép không
        if not piece_positions:
            game_log.append("Đã thu thập đủ mảnh ghép! Sẵn sàng bắn tín hiệu!")
            if len(game_log) > 10:
                game_log.pop(0)
            return False
        
        # Kiểm tra điều kiện Stamina
        if player.stats["Stamina"] < HELPER_STAMINA_COST:
            game_log.append(f"Cần ít nhất {HELPER_STAMINA_COST} Stamina!")
            if len(game_log) > 10:
                game_log.pop(0)
            return False
        
        # Trừ Stamina VÀ giảm max_stamina vĩnh viễn
        player.stats["Stamina"] -= HELPER_STAMINA_COST
        player.max_stamina -= HELPER_STAMINA_COST  # Không thể hồi lại
        
        player_pos = (player.grid_x, player.grid_y)
        all_paths = self.find_all_pieces_bfs(player_pos, map_data, piece_positions)
        
        # Tìm đường đi NGẮN NHẤT (đến mảnh ghép gần nhất)
        self.piece_path = []
        self.piece_targets = []
        
        if all_paths:
            # Chọn đường ngắn nhất
            nearest_piece = None
            shortest_path = None
            for piece_pos, path in all_paths.items():
                if shortest_path is None or len(path) < len(shortest_path):
                    shortest_path = path
                    nearest_piece = piece_pos
            
            if shortest_path:
                self.piece_path = shortest_path
                self.piece_targets = [nearest_piece]
        
        if self.piece_path:
            self.piece_path_visible = True
            self.piece_path_time = game_time
            steps = len(self.piece_path)
            remaining = len(piece_positions)
            game_log.append(f"[BFS] Đường đến mảnh ghép: {steps} bước ({remaining} còn lại)")
        else:
            game_log.append("Không tìm được đường đến mảnh ghép!")
        
        if len(game_log) > 10:
            game_log.pop(0)
        return True
    
    # ==================== BFS: THOÁT HIỂM ====================
    def find_safe_path_bfs(self, player_pos, map_data, fire_tiles):
        """
        Thuật toán BFS tìm đường ngắn nhất đến vùng an toàn
        Vùng an toàn = cách xa lửa ít nhất 3 ô
        """
        start_col, start_row = player_pos
        
        # Queue: (col, row, path)
        queue = deque([(start_col, start_row, [])])
        visited = set()
        visited.add((start_col, start_row))
        
        while queue:
            col, row, path = queue.popleft()
            
            # Kiểm tra đã an toàn chưa (cách xa lửa >= 3 ô)
            is_safe = True
            for fire_col, fire_row in fire_tiles:
                distance = abs(col - fire_col) + abs(row - fire_row)
                if distance < 4:  # Khoảng cách Manhattan < 4
                    is_safe = False
                    break
            
            if is_safe and path:  # Đã an toàn và có đường đi
                return path
            
            # Duyệt 4 hướng
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = col + dx, row + dy
                
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    if (nx, ny) not in visited:
                        tile = map_data[ny][nx]
                        # Có thể đi qua (tránh lửa)
                        if tile not in [TILE_WATER, TILE_TREE, TILE_FIRE, TILE_ROCK]:
                            visited.add((nx, ny))
                            new_path = path + [(nx, ny)]
                            queue.append((nx, ny, new_path))
        
        return []
    
    def activate_escape_finder(self, player, map_data, fire_tiles, game_time, game_log):
        """Kích hoạt BFS thoát hiểm - Cần HP <= 50"""
        # Kiểm tra điều kiện HP
        if player.stats["HP"] > HELPER_ESCAPE_HP_THRESHOLD:
            game_log.append(f"Chỉ dùng được khi HP <= {HELPER_ESCAPE_HP_THRESHOLD}!")
            if len(game_log) > 10:
                game_log.pop(0)
            return False
        
        player_pos = (player.grid_x, player.grid_y)
        self.escape_path = self.find_safe_path_bfs(player_pos, map_data, fire_tiles)
        
        if self.escape_path:
            self.escape_path_visible = True
            self.escape_path_time = game_time
            game_log.append(f"[BFS] Đã tìm đường thoát hiểm! ({len(self.escape_path)} bước)")
        else:
            game_log.append("Không tìm được đường thoát hiểm!")
        
        if len(game_log) > 10:
            game_log.pop(0)
        return True
    
    # ==================== BFS: DỰ ĐOÁN LỬA LAN ====================
    def predict_fire_spread_bfs(self, fire_tiles, map_data, depth=2):
        """
        BFS dự đoán các ô sẽ bị cháy trong depth bước tiếp
        """
        self.danger_tiles = set()
        
        if not fire_tiles:
            return
        
        # BFS từ mỗi ô lửa
        for fire_pos in fire_tiles:
            queue = deque([(fire_pos[0], fire_pos[1], 0)])
            visited = set()
            visited.add(fire_pos)
            
            while queue:
                col, row, dist = queue.popleft()
                
                if dist >= depth:
                    continue
                
                for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                    nx, ny = col + dx, row + dy
                    
                    if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                        if (nx, ny) not in visited:
                            tile = map_data[ny][nx]
                            # Lửa có thể lan sang cỏ, cây, hoa
                            if tile in [TILE_GRASS, TILE_TREE, TILE_FLOWER]:
                                visited.add((nx, ny))
                                self.danger_tiles.add((nx, ny))
                                queue.append((nx, ny, dist + 1))
    
    # ==================== UPDATE ====================
    def update(self, game_time, fire_tiles, map_data, player_pos):
        """Cập nhật trạng thái helper mỗi frame"""
        # Xóa các ô đường đi mà player đã đi qua (DFS path)
        if self.piece_path_visible and self.piece_path:
            # Xóa các ô mà player đang đứng hoặc đã đi qua
            while self.piece_path and self.piece_path[0] == player_pos:
                self.piece_path.pop(0)
            
            # Nếu hết đường đi thì tắt hiển thị
            if not self.piece_path:
                self.piece_path_visible = False
                self.piece_targets = []
        
        # Xóa các ô đường đi mà player đã đi qua (BFS escape path)
        if self.escape_path_visible and self.escape_path:
            while self.escape_path and self.escape_path[0] == player_pos:
                self.escape_path.pop(0)
            
            if not self.escape_path:
                self.escape_path_visible = False
        
        # Tắt hiển thị đường đến mảnh ghép sau 5 giây
        if self.piece_path_visible:
            if game_time - self.piece_path_time >= HELPER_DISPLAY_TIME:
                self.piece_path_visible = False
                self.piece_path = []
                self.piece_targets = []
        
        # Tắt hiển thị đường thoát hiểm sau 5 giây
        if self.escape_path_visible:
            if game_time - self.escape_path_time >= HELPER_DISPLAY_TIME:
                self.escape_path_visible = False
                self.escape_path = []
        
        # Tự động dự đoán lửa lan nếu lửa gần player
        if fire_tiles:
            player_col, player_row = player_pos
            min_dist = float('inf')
            for fire_col, fire_row in fire_tiles:
                dist = abs(player_col - fire_col) + abs(player_row - fire_row)
                min_dist = min(min_dist, dist)
            
            if min_dist <= 5:  # Lửa trong phạm vi 5 ô
                self.predict_fire_spread_bfs(fire_tiles, map_data, depth=2)
            else:
                self.danger_tiles = set()
    
    # ==================== GETTERS ====================
    def get_piece_path(self):
        """Trả về đường đi đến mảnh ghép (để vẽ)"""
        if self.piece_path_visible:
            return self.piece_path
        return []
    
    def get_escape_path(self):
        """Trả về đường thoát hiểm (để vẽ)"""
        if self.escape_path_visible:
            return self.escape_path
        return []
    
    def get_danger_tiles(self):
        """Trả về các ô nguy hiểm (để vẽ cảnh báo)"""
        return self.danger_tiles
    
    # ==================== PUBLIC API (Called from main.py) ====================
    def find_path_to_piece(self, map_data, player_pos, rescue_system, player, game_log):
        """
        Wrapper cho activate_piece_finder - Phím 1
        Tìm đường đến mảnh ghép gần nhất bằng BFS
        """
        game_time = pygame.time.get_ticks()
        piece_positions = rescue_system.piece_positions
        self.activate_piece_finder(player, map_data, piece_positions, game_time, game_log)
    
    def find_escape_route(self, map_data, player_pos, fire_system, player, game_log):
        """
        Wrapper cho activate_escape_finder - Phím 2
        Tìm lối thoát hiểm bằng BFS
        """
        game_time = pygame.time.get_ticks()
        fire_tiles = fire_system.fire_tiles
        self.activate_escape_finder(player, map_data, fire_tiles, game_time, game_log)
    
    def find_path_to_boat(self, map_data, player_pos, rescue_system, player, game_log):
        """
        Phím 3 - Tìm đường đến thuyền cứu hộ bằng BFS
        """
        if not rescue_system.boat_arrived:
            game_log.append("Thuyền chưa đến! Hãy thu thập mảnh ghép trước.")
            if len(game_log) > 10:
                game_log.pop(0)
            return
        
        if not rescue_system.boat_position:
            game_log.append("Không tìm thấy vị trí thuyền!")
            if len(game_log) > 10:
                game_log.pop(0)
            return
        
        # Sử dụng BFS tìm đường đến thuyền
        from collections import deque
        
        start_col, start_row = player_pos
        target_col, target_row = rescue_system.boat_position
        
        queue = deque([(start_col, start_row, [])])
        visited = set()
        visited.add((start_col, start_row))
        
        boat_path = []
        
        while queue:
            col, row, path = queue.popleft()
            
            # Đã đến thuyền
            if (col, row) == (target_col, target_row):
                boat_path = path
                break
            
            # Duyệt 4 hướng
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = col + dx, row + dy
                
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    if (nx, ny) not in visited:
                        tile = map_data[ny][nx]
                        # Có thể đi qua
                        if tile not in [TILE_WATER, TILE_TREE, TILE_FIRE, TILE_ROCK]:
                            visited.add((nx, ny))
                            new_path = path + [(nx, ny)]
                            queue.append((nx, ny, new_path))
        
        if boat_path:
            # Hiển thị đường đi đến thuyền (dùng escape_path để hiển thị)
            self.escape_path = boat_path
            self.escape_path_visible = True
            self.escape_path_time = pygame.time.get_ticks()
            game_log.append(f"[BFS] Đường đến thuyền: {len(boat_path)} bước")
        else:
            game_log.append("Không tìm được đường đến thuyền!")
        
        if len(game_log) > 10:
            game_log.pop(0)
    
    def predict_fire_spread(self, map_data, fire_system, player, game_log):
        """
        Wrapper cho predict_fire_spread_bfs - Phím 4
        Dự đoán vùng lửa sắp lan tới
        """
        fire_tiles = fire_system.fire_tiles
        
        if not fire_tiles:
            game_log.append("Chưa có lửa để dự đoán!")
            if len(game_log) > 10:
                game_log.pop(0)
            return
        
        self.predict_fire_spread_bfs(fire_tiles, map_data, depth=2)
        
        danger_count = len(self.danger_tiles)
        if danger_count > 0:
            game_log.append(f"[BFS] Cảnh báo: {danger_count} ô sắp cháy!")
        else:
            game_log.append("An toàn! Chưa có nguy cơ lửa lan.")
        
        if len(game_log) > 10:
            game_log.pop(0)
