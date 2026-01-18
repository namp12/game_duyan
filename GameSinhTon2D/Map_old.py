import pygame
import sys
import random
import math
import os

# --- 1. CẤU HÌNH & HẰNG SỐ ---
TILE_SIZE = 40
MAP_WIDTH = 60
MAP_HEIGHT = 40

# Kích thước giao diện
VIEWPORT_WIDTH = 800
VIEWPORT_HEIGHT = 600
SIDEBAR_WIDTH = 220
TOTAL_SCREEN_WIDTH = SIDEBAR_WIDTH + VIEWPORT_WIDTH + SIDEBAR_WIDTH
TOTAL_SCREEN_HEIGHT = VIEWPORT_HEIGHT
FPS = 60

# --- MÀU SẮC ---
COLOR_BG_SIDEBAR = (30, 30, 40)
COLOR_TEXT_TITLE = (255, 215, 0)
COLOR_TEXT_BODY = (200, 200, 200)
COLOR_BORDER = (100, 100, 120)

# Màu cho Menu
COLOR_MENU_BG = (20, 20, 30)       # Màu nền menu tối
COLOR_BTN_NORMAL = (0, 128, 0)     # Màu nút xanh lá
COLOR_BTN_HOVER = (0, 200, 0)      # Màu nút sáng lên khi di chuột
COLOR_BTN_TEXT = (255, 255, 255)

# Định nghĩa địa hình
TILE_WATER = 0; TILE_SAND = 1; TILE_GRASS = 2; TILE_TREE = 3
COLORS = {
    TILE_WATER: (65, 105, 225), TILE_SAND: (238, 214, 175),
    TILE_GRASS: (34, 139, 34), TILE_TREE: (139, 69, 19)
}
PLAYER_COLOR = (255, 0, 0)

# --- 2. QUẢN LÝ TÀI NGUYÊN ---
game_assets = {}
font_title = None
font_body = None
font_menu = None # Font to cho nút bấm

def load_assets():
    files = {TILE_WATER: "water.png", TILE_SAND: "sand.png", TILE_GRASS: "grass.png", TILE_TREE: "tree.png", "player": "player.png"}
    print("--- ĐANG TẢI TÀI NGUYÊN ---")
    for key, filename in files.items():
        path = os.path.join("assets", filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                game_assets[key] = img
            except: game_assets[key] = None
        else: game_assets[key] = None

def draw_text(surface, text, x, y, font, color, center=False):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect()
    if center:
        rect.center = (x, y)
        surface.blit(text_obj, rect)
    else:
        surface.blit(text_obj, (x, y))

# --- 3. LOGIC GAME (MAP & WALK) ---
def generate_island_map(width, height):
    new_map = []
    center_x = width // 2; center_y = height // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)
    for y in range(height):
        row = []
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            norm_dist = dist / (max_dist * 0.65)
            noise = random.uniform(-0.15, 0.15)
            val = norm_dist + noise
            if val > 0.8: tile = TILE_WATER
            elif val > 0.65: tile = TILE_SAND
            elif val > 0.35: tile = TILE_GRASS
            else: tile = TILE_GRASS
            if tile == TILE_GRASS and random.random() < 0.1: tile = TILE_TREE
            row.append(tile)
        new_map.append(row)
    return new_map

# --- 4. KHỞI TẠO ---
pygame.init()
font_title = pygame.font.SysFont('Arial', 32, bold=True)
font_body = pygame.font.SysFont('Arial', 20)
font_menu = pygame.font.SysFont('Arial', 50, bold=True) # Font lớn cho Menu

screen_total = pygame.display.set_mode((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
pygame.display.set_caption("Game Sinh Tồn 2D")
clock = pygame.time.Clock()

load_assets()
map_data = generate_island_map(MAP_WIDTH, MAP_HEIGHT)

# Setup nhân vật
player_grid_x, player_grid_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
while map_data[player_grid_y][player_grid_x] in [TILE_WATER, TILE_TREE]:
    player_grid_x += 1; player_grid_y += (player_grid_x%2)

camera_x = 0; camera_y = 0

# Setup các vùng hiển thị
rect_left = pygame.Rect(0, 0, SIDEBAR_WIDTH, TOTAL_SCREEN_HEIGHT)
rect_viewport = pygame.Rect(SIDEBAR_WIDTH, 0, VIEWPORT_WIDTH, TOTAL_SCREEN_HEIGHT)
rect_right = pygame.Rect(SIDEBAR_WIDTH + VIEWPORT_WIDTH, 0, SIDEBAR_WIDTH, TOTAL_SCREEN_HEIGHT)
viewport_area = screen_total.subsurface(rect_viewport)

# Dữ liệu hiển thị
player_stats = {"HP": 100, "Stamina": 100, "Gỗ": 0, "Đá": 0}
game_log = ["- Sẵn sàng...", "- Bấm nút để chơi."]

# --- 5. CẤU HÌNH TRẠNG THÁI GAME & NÚT BẤM ---
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
current_state = GAME_STATE_MENU # Mặc định vào game là Menu

# Tạo hình chữ nhật cho nút Start (giữa màn hình)
btn_width, btn_height = 200, 80
btn_x = (TOTAL_SCREEN_WIDTH // 2) - (btn_width // 2)
btn_y = (TOTAL_SCREEN_HEIGHT // 2) - (btn_height // 2)
start_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

# --- 6. VÒNG LẶP CHÍNH ---
running = True
while running:
    # Lấy vị trí chuột
    mouse_pos = pygame.mouse.get_pos()
    
    # A. XỬ LÝ SỰ KIỆN (INPUT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- XỬ LÝ KHI Ở MENU ---
        if current_state == GAME_STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Chuột trái
                    # Kiểm tra xem có bấm vào nút Start không
                    if start_button_rect.collidepoint(mouse_pos):
                        print("Bắt đầu game!")
                        current_state = GAME_STATE_PLAYING

        # --- XỬ LÝ KHI ĐANG CHƠI ---
        elif current_state == GAME_STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_a: dx = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: dx = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w: dy = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s: dy = 1
                
                # Check va chạm
                target_x, target_y = player_grid_x + dx, player_grid_y + dy
                if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                    if map_data[target_y][target_x] not in [TILE_WATER, TILE_TREE]:
                        player_grid_x, player_grid_y = target_x, target_y
                        game_log.append(f"- Đi đến ({player_grid_x}, {player_grid_y})")
                        if len(game_log) > 10: game_log.pop(0)

    # B. VẼ MÀN HÌNH (RENDER)
    
    # --- VẼ GIAO DIỆN MENU ---
    if current_state == GAME_STATE_MENU:
        screen_total.fill(COLOR_MENU_BG)
        
        # Tiêu đề lớn
        draw_text(screen_total, "ĐẢO HOANG SINH TỒN", TOTAL_SCREEN_WIDTH // 2, 150, font_menu, COLOR_TEXT_TITLE, center=True)
        draw_text(screen_total, "Nhấn nút bên dưới để bắt đầu", TOTAL_SCREEN_WIDTH // 2, 220, font_body, COLOR_TEXT_BODY, center=True)

        # Kiểm tra hiệu ứng Hover (chuột đè lên nút)
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen_total, COLOR_BTN_HOVER, start_button_rect, border_radius=10)
        else:
            pygame.draw.rect(screen_total, COLOR_BTN_NORMAL, start_button_rect, border_radius=10)
        
        # Viền nút
        pygame.draw.rect(screen_total, (255,255,255), start_button_rect, 2, border_radius=10)
        
        # Chữ trong nút
        draw_text(screen_total, "BẮT ĐẦU", btn_x + btn_width//2, btn_y + btn_height//2, font_title, COLOR_BTN_TEXT, center=True)

    # --- VẼ GIAO DIỆN CHƠI GAME ---
    elif current_state == GAME_STATE_PLAYING:
        # 1. Update Camera
        target_cam_x = (player_grid_x * TILE_SIZE) - (VIEWPORT_WIDTH // 2) + (TILE_SIZE // 2)
        target_cam_y = (player_grid_y * TILE_SIZE) - (VIEWPORT_HEIGHT // 2) + (TILE_SIZE // 2)
        camera_x += (target_cam_x - camera_x) * 0.1
        camera_y += (target_cam_y - camera_y) * 0.1
        
        # Kẹp camera trong map
        max_cam_x = (MAP_WIDTH * TILE_SIZE) - VIEWPORT_WIDTH
        max_cam_y = (MAP_HEIGHT * TILE_SIZE) - VIEWPORT_HEIGHT
        camera_x = max(0, min(camera_x, max_cam_x))
        camera_y = max(0, min(camera_y, max_cam_y))

        # 2. Xóa màn hình
        screen_total.fill(COLOR_BG_SIDEBAR)
        viewport_area.fill((0,0,0))

        # 3. Vẽ Map vào Viewport
        start_col = int(camera_x // TILE_SIZE)
        end_col = int((camera_x + VIEWPORT_WIDTH) // TILE_SIZE) + 1
        start_row = int(camera_y // TILE_SIZE)
        end_row = int((camera_y + VIEWPORT_HEIGHT) // TILE_SIZE) + 1
        
        # Kẹp chỉ số mảng
        start_col = max(0, start_col); end_col = min(MAP_WIDTH, end_col)
        start_row = max(0, start_row); end_row = min(MAP_HEIGHT, end_row)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = map_data[row][col]
                dx = (col * TILE_SIZE) - camera_x
                dy = (row * TILE_SIZE) - camera_y
                
                img = game_assets.get(tile)
                if img:
                    if tile == TILE_TREE: # Vẽ nền đất dưới cây
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img: viewport_area.blit(g_img, (dx, dy))
                    viewport_area.blit(img, (dx, dy))
                else:
                    color = COLORS.get(tile, (255,255,255))
                    pygame.draw.rect(viewport_area, color, (dx, dy, TILE_SIZE, TILE_SIZE))

        # 4. Vẽ Nhân vật
        px = (player_grid_x * TILE_SIZE) - camera_x
        py = (player_grid_y * TILE_SIZE) - camera_y
        p_img = game_assets.get("player")
        if p_img: viewport_area.blit(p_img, (px, py))
        else: pygame.draw.rect(viewport_area, PLAYER_COLOR, (px+5, py+5, 30, 30))

        # 5. Vẽ Viền & Sidebar
        pygame.draw.rect(screen_total, COLOR_BORDER, rect_viewport, 3)
        
        # Sidebar Trái
        draw_text(screen_total, "THÔNG TIN", rect_left.x+20, 20, font_title, COLOR_TEXT_TITLE)
        pygame.draw.line(screen_total, COLOR_BORDER, (10, 60), (SIDEBAR_WIDTH-10, 60), 2)
        y_pos = 80
        for k, v in player_stats.items():
            draw_text(screen_total, f"{k}: {v}", rect_left.x+20, y_pos, font_body, COLOR_TEXT_BODY)
            y_pos += 30
            
        # Sidebar Phải
        draw_text(screen_total, "NHẬT KÝ", rect_right.x+20, 20, font_title, COLOR_TEXT_TITLE)
        pygame.draw.line(screen_total, COLOR_BORDER, (rect_right.x+10, 60), (rect_right.right-10, 60), 2)
        y_pos = 80
        for log in game_log:
            draw_text(screen_total, log, rect_right.x+20, y_pos, font_body, COLOR_TEXT_BODY)
            y_pos += 25

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()