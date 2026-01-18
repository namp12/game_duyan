import random
import math
from settings import *

def generate_island_map(width, height):
    new_map = []
    center_x = width // 2
    center_y = height // 2
    
    # Tính khoảng cách tối đa từ tâm ra góc (để chuẩn hóa)
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        row = []
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            # Chuẩn hóa khoảng cách (càng xa tâm càng lớn, max ~ 1.0)
            # Chia cho (max_dist * 0.65) để đảo to hơn một chút
            norm_dist = dist / (max_dist * 0.65)
            
            noise = random.uniform(-0.15, 0.15)
            val = norm_dist + noise
            
            # Quy định các lớp địa hình dựa trên giá trị val (càng nhỏ càng gần tâm -> đất liền)
            if val > 0.8: 
                tile = TILE_WATER
            elif val > 0.65: 
                tile = TILE_SAND
            elif val > 0.35: 
                tile = TILE_GRASS
            else: 
                tile = TILE_GRASS
            
            # Thêm cây ngẫu nhiên trên cỏ
            if tile == TILE_GRASS:
                rnd = random.random()
                if rnd < 0.15: # 15% Cây
                    tile = TILE_TREE
                elif rnd < 0.20: # 5% Hoa (15-20)
                    tile = TILE_FLOWER
            
            row.append(tile)
        new_map.append(row)
    
    # Thêm vật phẩm hồi máu
    spawn_health_items(new_map)
    
    # Thêm hộp hồi Stamina
    spawn_stamina_items(new_map)
    
    # Thêm đá ngầm trong nước
    spawn_rocks(new_map)
    
    return new_map

def spawn_health_items(map_data):
    """Đặt vật phẩm hồi máu ngẫu nhiên trên bản đồ"""
    valid_tiles = []
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if map_data[row][col] == TILE_GRASS:
                valid_tiles.append((col, row))
    
    if len(valid_tiles) >= HEALTH_SPAWN_COUNT:
        positions = random.sample(valid_tiles, HEALTH_SPAWN_COUNT)
        for col, row in positions:
            map_data[row][col] = TILE_HEALTH

def spawn_rocks(map_data):
    """Đặt đá ngầm ngẫu nhiên trong nước"""
    rock_count = 0
    target_rocks = 50  # Số lượng đá ngầm
    
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if map_data[row][col] == TILE_WATER:
                # 5% cơ hội có đá ngầm
                if random.random() < 0.05 and rock_count < target_rocks:
                    map_data[row][col] = TILE_ROCK
                    rock_count += 1

def spawn_stamina_items(map_data):
    """Đặt hộp hồi Stamina ngẫu nhiên trên cỏ"""
    valid_tiles = []
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            if map_data[row][col] == TILE_GRASS:
                valid_tiles.append((col, row))
    
    stamina_count = 8  # Số lượng hộp Stamina
    if len(valid_tiles) >= stamina_count:
        positions = random.sample(valid_tiles, stamina_count)
        for col, row in positions:
            map_data[row][col] = TILE_STAMINA
