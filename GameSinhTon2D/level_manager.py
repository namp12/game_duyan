"""
Level Manager - Quản lý màn chơi và độ khó
"""
from settings import *
from score import load_level_progress, save_level_progress

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_level_reached = load_level_progress()  # Load from file
        print(f"🎮 Level Manager initialized: Level {self.max_level_reached} unlocked")
        
    def get_level_config(self):
        """
        Trả về cấu hình cho level hiện tại
        
        Returns:
            dict: Cấu hình level với các parameters
        """
        level = self.current_level
        
        # Base configuration
        config = {
            "level": level,
            "fire_spread_interval": FIRE_SPREAD_INTERVAL,
            "fire_start_delay": FIRE_START_DELAY,
            "fire_spawn_points": 1,  # Số điểm lửa khởi đầu
            "map_width": MAP_WIDTH,
            "map_height": MAP_HEIGHT,
            "pieces_required": TOTAL_PIECES,
            "boat_arrival_time": BOAT_ARRIVAL_TIME,
        }
        
        # Level 1: Tutorial (Easy)
        if level == 1:
            config["fire_spread_interval"] = 2500  # Chậm hơn
            config["fire_start_delay"] = 3000       # Delay lâu hơn
            config["fire_spawn_points"] = 1
            
        # Level 2-3: Normal
        elif level <= 3:
            config["fire_spread_interval"] = 2000  # Normal
            config["fire_start_delay"] = 2000
            config["fire_spawn_points"] = 1
            
        # Level 4-6: Hard
        elif level <= 6:
            config["fire_spread_interval"] = 1500  # Nhanh hơn
            config["fire_start_delay"] = 1500
            config["fire_spawn_points"] = 2        # 2 điểm lửa
            
        # Level 7-10: Expert
        elif level <= 10:
            config["fire_spread_interval"] = 1200  # Rất nhanh
            config["fire_start_delay"] = 1000
            config["fire_spawn_points"] = 3        # 3 điểm lửa
            config["pieces_required"] = 5          # Cần nhiều mảnh hơn
            
        # Level 11+: Master
        else:
            config["fire_spread_interval"] = 1000  # Cực nhanh
            config["fire_start_delay"] = 800
            config["fire_spawn_points"] = 4        # 4 điểm lửa
            config["pieces_required"] = 6
            config["boat_arrival_time"] = 8000     # Thuyền đến chậm hơn
        
        return config
    
    def get_level_name(self):
        """Trả về tên level"""
        level = self.current_level
        
        if level == 1:
            return "Level 1 - Tutorial"
        elif level <= 3:
            return f"Level {level} - Normal"
        elif level <= 6:
            return f"Level {level} - Hard"
        elif level <= 10:
            return f"Level {level} - Expert"
        else:
            return f"Level {level} - Master"
    
    def get_level_color(self):
        """Trả về màu hiển thị theo độ khó"""
        level = self.current_level
        
        if level == 1:
            return (0, 255, 0)      # Xanh lá - Easy
        elif level <= 3:
            return (255, 255, 0)    # Vàng - Normal
        elif level <= 6:
            return (255, 165, 0)    # Cam - Hard
        elif level <= 10:
            return (255, 0, 0)      # Đỏ - Expert
        else:
            return (148, 0, 211)    # Tím - Master
    
    def next_level(self):
        """Chuyển sang level tiếp theo"""
        self.current_level += 1
        if self.current_level > self.max_level_reached:
            self.max_level_reached = self.current_level
        print(f"🎯 Chuyển sang {self.get_level_name()}")
    
    def reset_to_level_1(self):
        """Reset về level 1"""
        self.current_level = 1
    
    def get_progress_text(self):
        """Trả về text hiển thị tiến độ"""
        return f"Level {self.current_level} | Best: {self.max_level_reached}"
    
    def is_level_unlocked(self, level_num):
        """
        Kiểm tra xem level có được mở khóa chưa
        
        Args:
            level_num: Số level cần kiểm tra
            
        Returns:
            bool: True nếu level đã mở khóa
        """
        # Level 1 luôn mở khóa
        # Các level khác mở khóa khi đã hoàn thành level trước đó
        return level_num <= self.max_level_reached
