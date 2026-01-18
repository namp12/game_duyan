import os
import pygame
from settings import *

def load_assets():
    game_assets = {}
    
    # Lấy đường dẫn tuyệt đối đến thư mục chứa script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    
    files = {
        TILE_WATER: "water.png",
        TILE_SAND: "sand.png",
        TILE_GRASS: "grass.png",
        TILE_TREE: "tree.png",
        TILE_FLOWER: "flower.png",
        TILE_FIRE: "fire.png",
        TILE_PIECE: "piece.png",
        TILE_BOAT: "boat.png",
        TILE_HEALTH: "health.png",
        TILE_ROCK: "rock.png",
        TILE_STAMINA: "stamina.png",
        "player": "player.png"
    }
    print("--- ĐANG TẢI TÀI NGUYÊN ---")
    print(f"Thư mục assets: {assets_dir}")
    
    for key, filename in files.items():
        path = os.path.join(assets_dir, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                game_assets[key] = img
                print(f"Đã tải: {filename}")
            except Exception as e:
                print(f"Lỗi load ảnh {filename}: {e}")
                game_assets[key] = None
        else:
            print(f"✗ Không tìm thấy: {path}")
            game_assets[key] = None
    return game_assets

def draw_text(surface, text, x, y, font, color, center=False):
    if not font:
        return
    text_obj = font.render(str(text), True, color)
    rect = text_obj.get_rect()
    if center:
        rect.center = (x, y)
        surface.blit(text_obj, rect)
    else:
        surface.blit(text_obj, (x, y))
