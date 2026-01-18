"""
Rain System - Hệ thống thời tiết mưa để dập lửa
"""
import random
from settings import *

class RainSystem:
    def __init__(self):
        self.is_raining = False
        self.rain_start_time = 0
        self.rain_duration = 0
        self.next_rain_check = RAIN_CHECK_INTERVAL  # Lần kiểm tra mưa tiếp theo
        self.last_extinguish_time = 0
        self.rain_particles = []  # Danh sách hạt mưa cho visual effect
        
    def update(self, game_time, fire_system, map_data, game_log):
        """
        Cập nhật hệ thống mưa
        
        Args:
            game_time: Thời gian game hiện tại (ms)
            fire_system: FireSystem để dập lửa
            map_data: Bản đồ game
            game_log: Log để hiển thị thông báo
        """
        # Kiểm tra xem có nên bắt đầu mưa không
        if not self.is_raining and game_time >= self.next_rain_check:
            if random.random() < RAIN_CHANCE:
                self.start_rain(game_time, game_log, fire_system)
            # Đặt lịch kiểm tra lần tiếp theo
            self.next_rain_check = game_time + RAIN_CHECK_INTERVAL
        
        # Nếu đang mưa
        if self.is_raining:
            # Kiểm tra mưa đã hết chưa
            if game_time >= self.rain_start_time + self.rain_duration:
                self.stop_rain(game_log, fire_system)
            else:
                # Chỉ cập nhật hạt mưa, KHÔNG dập lửa
                # Lửa chỉ ngừng lan, không bị tắt
                self.update_rain_particles(game_time)
    
    def start_rain(self, game_time, game_log, fire_system):
        """Bắt đầu trận mưa"""
        self.is_raining = True
        self.rain_start_time = game_time
        self.rain_duration = random.randint(RAIN_MIN_DURATION, RAIN_MAX_DURATION)
        self.last_extinguish_time = game_time
        
        # Tạm dừng lửa lan rộng
        fire_system.spreading_paused = True
        
        game_log.append("Trời bắt đầu mưa!")
        if len(game_log) > 10:
            game_log.pop(0)
    
    def stop_rain(self, game_log, fire_system):
        """Dừng mưa"""
        self.is_raining = False
        self.rain_particles.clear()
        
        # Tiếp tục lửa lan rộng
        fire_system.spreading_paused = False
        
        game_log.append("Mưa đã tạnh")
        if len(game_log) > 10:
            game_log.pop(0)
    
    def extinguish_fires(self, game_time, fire_system, map_data, game_log):
        """Dập lửa khi mưa"""
        # Dập lửa mỗi giây
        if game_time - self.last_extinguish_time >= 1000:
            fire_tiles = list(fire_system.fire_tiles)
            
            if len(fire_tiles) > 0:
                # Dập ngẫu nhiên một số ô lửa
                extinguish_count = min(RAIN_EXTINGUISH_RATE, len(fire_tiles))
                tiles_to_extinguish = random.sample(fire_tiles, extinguish_count)
                
                for (fx, fy) in tiles_to_extinguish:
                    # Xóa lửa khỏi fire system
                    if (fx, fy) in fire_system.fire_tiles:
                        fire_system.fire_tiles.remove((fx, fy))
                    
                    # Đổi lại thành cỏ
                    if 0 <= fy < MAP_HEIGHT and 0 <= fx < MAP_WIDTH:
                        if map_data[fy][fx] == TILE_FIRE:
                            map_data[fy][fx] = TILE_GRASS
                
                # Log thông báo (không spam)
                if game_time - self.last_extinguish_time >= 3000:
                    game_log.append(f"Mưa đang dập lửa...")
                    if len(game_log) > 10:
                        game_log.pop(0)
            
            self.last_extinguish_time = game_time
    
    def update_rain_particles(self, game_time):
        """Cập nhật hạt mưa cho visual effect"""
        # Tạo hạt mưa mới
        if len(self.rain_particles) < 200:  # Giới hạn số hạt
            for _ in range(10):
                particle = {
                    'x': random.randint(0, VIEWPORT_WIDTH),
                    'y': random.randint(-50, 0),
                    'speed': random.randint(400, 600)
                }
                self.rain_particles.append(particle)
        
        # Di chuyển hạt mưa xuống
        for particle in self.rain_particles[:]:
            particle['y'] += particle['speed'] * 0.016  # ~60 FPS
            
            # Xóa hạt mưa khi ra khỏi màn hình
            if particle['y'] > VIEWPORT_HEIGHT:
                self.rain_particles.remove(particle)
    
    def get_rain_particles(self):
        """Trả về danh sách hạt mưa để vẽ"""
        return self.rain_particles
    
    def get_remaining_time(self, game_time):
        """Trả về thời gian mưa còn lại (giây)"""
        if not self.is_raining:
            return 0
        remaining_ms = (self.rain_start_time + self.rain_duration) - game_time
        return max(0, remaining_ms // 1000)
