from settings import *

class Player:
    def __init__(self, start_x, start_y):
        self.grid_x = start_x
        self.grid_y = start_y
        self.stats = {
            "HP": 100, 
            "Stamina": 100
        }
        self.max_stamina = 100  # Stamina tối đa (giảm khi dùng H)
        self.pixel_x = self.grid_x * TILE_SIZE
        self.pixel_y = self.grid_y * TILE_SIZE
        self.is_sprinting = False
        self.is_jumping = False  # Trạng thái nhảy
        self.jump_start_time = 0  # Thời gian bắt đầu nhảy (cho animation)

    def move(self, dx, dy, map_data, game_log, sprint=False, jump=False, sound_system=None, fire_system=None):
        # Kiểm tra sprint
        if sprint and self.stats["Stamina"] >= SPRINT_STAMINA_COST:
            self.is_sprinting = True
            self.stats["Stamina"] -= SPRINT_STAMINA_COST
        else:
            self.is_sprinting = False
        
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy
        
        # Kiểm tra biên map
        if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
            tile = map_data[target_y][target_x]
            
            # Kiểm tra vòng lửa thứ 2 (KHÔNG CHO ĐI VÀO)
            if fire_system:
                current_pos = (self.grid_x, self.grid_y)
                target_pos = (target_x, target_y)
                if not fire_system.can_move_to_position(current_pos, target_pos):
                    game_log.append("Không thể đi vào vòng lửa thứ 2!")
                    if len(game_log) > 10:
                        game_log.pop(0)
                    return False
            
            # JUMP MECHANIC - Nhảy qua cây và đá theo MỌI HƯỚNG (MIỄN PHÍ)
            if jump:  # Nhảy được ở mọi hướng: lên, xuống, trái, phải
                if tile == TILE_TREE:
                    # Nhảy qua cây
                    self.grid_x = target_x
                    self.grid_y = target_y
                    self.is_jumping = True
                    game_log.append("Nhảy qua cây!")
                    if len(game_log) > 10:
                        game_log.pop(0)
                    # Play jump sound
                    if sound_system:
                        sound_system.play_sound('jump')
                    return True
                elif tile == TILE_ROCK:
                    # Nhảy qua đá
                    self.grid_x = target_x
                    self.grid_y = target_y
                    self.is_jumping = True
                    game_log.append("Nhảy qua đá!")
                    if len(game_log) > 10:
                        game_log.pop(0)
                    # Play jump sound
                    if sound_system:
                        sound_system.play_sound('jump')
                    return True
            
            # Kiểm tra chướng ngại vật (Nước, Cây - không đi qua được khi không nhảy)
            if tile not in [TILE_WATER, TILE_TREE, TILE_ROCK]:
                self.grid_x = target_x
                self.grid_y = target_y
                
                # Kiểm tra nhặt vật phẩm hồi máu
                if tile == TILE_HEALTH:
                    self.stats["HP"] = min(100, self.stats["HP"] + HEALTH_RESTORE)
                    map_data[target_y][target_x] = TILE_GRASS
                    game_log.append(f"Hồi máu! +{HEALTH_RESTORE} HP")
                    if len(game_log) > 10:
                        game_log.pop(0)
                    # Play pickup sound
                    if sound_system:
                        sound_system.play_sound('pickup')
                
                # Kiểm tra nhặt hộp hồi Stamina
                if tile == TILE_STAMINA:
                    self.stats["Stamina"] = min(100, self.stats["Stamina"] + 10)
                    map_data[target_y][target_x] = TILE_GRASS
                    game_log.append("Hồi Stamina! +10 Stamina")
                    if len(game_log) > 10:
                        game_log.pop(0)
                    # Play pickup sound
                    if sound_system:
                        sound_system.play_sound('pickup')
                
                return True
        return False

    def update(self):
        target_pixel_x = self.grid_x * TILE_SIZE
        target_pixel_y = self.grid_y * TILE_SIZE
        
        # Interpolation (Smooth movement) - nhanh hơn khi sprint
        speed = 0.3 if self.is_sprinting else 0.2
        self.pixel_x += (target_pixel_x - self.pixel_x) * speed
        self.pixel_y += (target_pixel_y - self.pixel_y) * speed
        
        # Reset jump state sau khi di chuyển xong
        if self.is_jumping:
            # Kiểm tra đã đến vị trí đích chưa
            if abs(self.pixel_x - target_pixel_x) < 5 and abs(self.pixel_y - target_pixel_y) < 5:
                self.is_jumping = False
        
        # Hồi stamina (chỉ hồi đến max_stamina)
        if self.stats["Stamina"] < self.max_stamina:
            self.stats["Stamina"] = min(self.max_stamina, self.stats["Stamina"] + STAMINA_REGEN)
    
    def is_surrounded_by_fire(self, fire_system):
        """Kiểm tra nhân vật có bị lửa bao vây không (4 hướng)"""
        fire_count = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = self.grid_x + dx, self.grid_y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                if fire_system.is_position_in_fire((nx, ny)):
                    fire_count += 1
        
        # Nếu 3/4 hướng bị lửa = bị bao vây
        return fire_count >= 3
    
    def teleport_to_safety(self, map_data, fire_system, game_log):
        """Dịch chuyển nhân vật ra vị trí an toàn cách lửa 5 ô"""
        import random
        
        valid_positions = []
        
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                pos = (col, row)
                tile = map_data[row][col]
                
                # Chỉ teleport đến ô có thể đi được
                if tile in [TILE_GRASS, TILE_SAND, TILE_FLOWER]:
                    # Kiểm tra cách lửa ít nhất 5 ô
                    min_dist = float('inf')
                    for fire_pos in fire_system.fire_tiles:
                        dist = abs(fire_pos[0] - col) + abs(fire_pos[1] - row)
                        min_dist = min(min_dist, dist)
                    
                    if min_dist == 3:  # ĐÚNG 3 ô cách lửa
                        valid_positions.append(pos)
        
        if valid_positions:
            new_pos = random.choice(valid_positions)
            self.grid_x, self.grid_y = new_pos
            self.pixel_x = self.grid_x * TILE_SIZE
            self.pixel_y = self.grid_y * TILE_SIZE
            
            game_log.append("Thoát hiểm! Dịch chuyển ra vị trí an toàn!")
            if len(game_log) > 10:
                game_log.pop(0)
            return True
        
        return False
    
    def attack(self, monster_system, game_time, game_log):
        """
        Tấn công quái vật
        
        Args:
            monster_system: MonsterSystem để lấy quái trong tầm
            game_time: Thời gian game
            game_log: Log để hiển thị
            
        Returns:
            bool: True nếu tấn công thành công
        """
        # Kiểm tra cooldown
        if not hasattr(self, 'last_attack_time'):
            self.last_attack_time = 0
        
        attack_cooldown = 1000  # 1 giây
        if game_time - self.last_attack_time < attack_cooldown:
            return False
        
        # Lấy quái trong tầm
        monsters_in_range = monster_system.get_monsters_in_range(self.grid_x, self.grid_y, attack_range=1.5)
        
        if len(monsters_in_range) > 0:
            # Tấn công quái đầu tiên trong list
            monster = monsters_in_range[0]
            damage = 15
            is_dead = monster.take_damage(damage, game_log)
            
            self.last_attack_time = game_time
            
            if is_dead:
                game_log.append(f"⚔️ Tiêu diệt quái vật! +{damage} DMG")
                monster_system.remove_dead_monsters()
            else:
                game_log.append(f"⚔️ Tấn công! -{damage} HP")
            
            if len(game_log) > 10:
                game_log.pop(0)
            
            return True
        
        return False

