import pygame
import os
import math
from settings import *
from utils import draw_text
from score import format_time

class UI:
    def __init__(self, screen):
        self.screen = screen
        
        # Rects
        self.rect_left = pygame.Rect(0, 0, SIDEBAR_WIDTH, TOTAL_SCREEN_HEIGHT)
        self.rect_viewport = pygame.Rect(SIDEBAR_WIDTH, 0, VIEWPORT_WIDTH, TOTAL_SCREEN_HEIGHT)
        self.rect_right = pygame.Rect(SIDEBAR_WIDTH + VIEWPORT_WIDTH, 0, SIDEBAR_WIDTH, TOTAL_SCREEN_HEIGHT)
        
        self.viewport_area = self.screen.subsurface(self.rect_viewport)
        
        # Load menu background
        self.menu_bg = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "assets", "menu_bg.png")
        if os.path.exists(bg_path):
            try:
                self.menu_bg = pygame.image.load(bg_path).convert()
                self.menu_bg = pygame.transform.scale(self.menu_bg, (TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
                print(f"✓ Đã tải hình nền menu")
            except Exception as e:
                print(f"✗ Lỗi load hình nền menu: {e}")

    def draw_menu(self, font_menu, font_body, font_title, start_button_rect, mouse_pos, high_score=0):
        # Vẽ hình nền menu
        if self.menu_bg:
            self.screen.blit(self.menu_bg, (0, 0))
        else:
            self.screen.fill(COLOR_MENU_BG)
        
        draw_text(self.screen, "ĐẢO HOANG SINH TỒN", TOTAL_SCREEN_WIDTH // 2, 120, font_menu, COLOR_TEXT_TITLE, center=True)
        draw_text(self.screen, "Nhấn nút bên dưới để bắt đầu", TOTAL_SCREEN_WIDTH // 2, 190, font_body, COLOR_TEXT_BODY, center=True)
        
        # Hiển thị kỷ lục
        if high_score > 0:
            high_str = format_time(high_score)
            draw_text(self.screen, f"Kỷ lục: {high_str}", TOTAL_SCREEN_WIDTH // 2, 240, font_title, (255, 215, 0), center=True)
        else:
            draw_text(self.screen, "Chưa có kỷ lục", TOTAL_SCREEN_WIDTH // 2, 240, font_title, (150, 150, 150), center=True)

        # Button logic
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_BTN_HOVER, start_button_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, COLOR_BTN_NORMAL, start_button_rect, border_radius=10)
        
        pygame.draw.rect(self.screen, (255,255,255), start_button_rect, 2, border_radius=10)
        draw_text(self.screen, "BẮT ĐẦU", start_button_rect.centerx, start_button_rect.centery, font_title, COLOR_BTN_TEXT, center=True)

    def draw_game_screen(self, player, map_data, camera_x, camera_y, game_assets, game_log, fonts, game_time, fire_system=None, level_manager=None, rain_system=None, rescue_system=None, sound_system=None):
        # fonts = (font_title, font_body)
        font_title, font_body = fonts
        
        # Initialize volume buttons dict
        volume_buttons = {}

        # 1. Clear Screen
        self.screen.fill(COLOR_BG_SIDEBAR)
        self.viewport_area.fill((0,0,0))

        # 2. Draw Map Layer
        start_col = int(camera_x // TILE_SIZE)
        end_col = int((camera_x + VIEWPORT_WIDTH) // TILE_SIZE) + 1
        start_row = int(camera_y // TILE_SIZE)
        end_row = int((camera_y + VIEWPORT_HEIGHT) // TILE_SIZE) + 1
        
        start_col = max(0, start_col)
        end_col = min(MAP_WIDTH, end_col)
        start_row = max(0, start_row)
        end_row = min(MAP_HEIGHT, end_row)
        
        # Lấy warning tiles từ fire system
        warning_tiles = []
        if fire_system:
            warning_tiles = fire_system.get_warning_tiles_visual(game_time)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile = map_data[row][col]
                dx = (col * TILE_SIZE) - camera_x
                dy = (row * TILE_SIZE) - camera_y
                
                img = game_assets.get(tile)
                if img:
                    # Water Shimmer Effect
                    if tile == TILE_WATER:
                        # Simple shimmer by varying alpha or color slightly
                        shimmer = (game_time // 200) % 2 == 0
                        if shimmer and (col + row)%2 == 0:
                            # Draw a slightly brighter overlay
                            self.viewport_area.blit(img, (dx, dy))
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((255, 255, 255, 30))
                            self.viewport_area.blit(s, (dx, dy))
                        else:
                            self.viewport_area.blit(img, (dx, dy))
                            
                    elif tile == TILE_TREE or tile == TILE_FLOWER: 
                        # Vẽ nền cỏ dưới cây hoặc hoa
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img: 
                            self.viewport_area.blit(g_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                    
                    elif tile == TILE_FIRE:
                        # Vẽ nền cỏ dưới lửa + hiệu ứng nhấp nháy
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img:
                            self.viewport_area.blit(g_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                        # Hiệu ứng nhấp nháy lửa
                        flicker = (game_time // 100) % 3
                        if flicker == 0:
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((255, 100, 0, 40))
                            self.viewport_area.blit(s, (dx, dy))
                    
                    elif tile == TILE_PIECE:
                        # Vẽ nền cỏ dưới mảnh ghép + hiệu ứng lấp lánh
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img:
                            self.viewport_area.blit(g_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                        # Hiệu ứng lấp lánh
                        sparkle = (game_time // 300) % 2
                        if sparkle == 0:
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((255, 255, 100, 50))
                            self.viewport_area.blit(s, (dx, dy))
                    
                    elif tile == TILE_HEALTH:
                        # Vẽ nền cỏ dưới vật phẩm hồi máu + hiệu ứng pulse
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img:
                            self.viewport_area.blit(g_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                        # Hiệu ứng pulse xanh
                        pulse = (game_time // 400) % 2
                        if pulse == 0:
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((0, 255, 100, 40))
                            self.viewport_area.blit(s, (dx, dy))
                    
                    elif tile == TILE_BOAT:
                        # Vẽ nền cát dưới thuyền + hiệu ứng vàng nổi bật
                        sand_img = game_assets.get(TILE_SAND)
                        if sand_img:
                            self.viewport_area.blit(sand_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                        # Hiệu ứng highlight thuyền
                        highlight = (game_time // 500) % 2
                        if highlight == 0:
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((255, 255, 0, 30))
                            self.viewport_area.blit(s, (dx, dy))
                    
                    elif tile == TILE_ROCK:
                        # Vẽ nền nước dưới đá ngầm
                        water_img = game_assets.get(TILE_WATER)
                        if water_img:
                            self.viewport_area.blit(water_img, (dx, dy))
                        self.viewport_area.blit(img, (dx, dy))
                    
                    elif tile == TILE_STAMINA:
                        # Vẽ nền cỏ dưới hộp Stamina + hiệu ứng xanh cyan
                        g_img = game_assets.get(TILE_GRASS)
                        if g_img:
                            self.viewport_area.blit(g_img, (dx, dy))
                        # Vẽ hộp Stamina (màu xanh cyan nếu không có ảnh)
                        if img:
                            self.viewport_area.blit(img, (dx, dy))
                        else:
                            pygame.draw.rect(self.viewport_area, (0, 200, 255), 
                                           (dx + 10, dy + 10, TILE_SIZE - 20, TILE_SIZE - 20))
                        # Hiệu ứng pulse xanh cyan
                        pulse = (game_time // 350) % 2
                        if pulse == 0:
                            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                            s.fill((0, 200, 255, 50))
                            self.viewport_area.blit(s, (dx, dy))
                    
                    else:
                        self.viewport_area.blit(img, (dx, dy))
                else:
                    color = COLORS.get(tile, (255,255,255))
                    pygame.draw.rect(self.viewport_area, color, (dx, dy, TILE_SIZE, TILE_SIZE))
                
                # Vẽ warning overlay cho tiles sắp cháy
                if (col, row) in warning_tiles:
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((255, 255, 0, 120))  # Vàng nhấp nháy
                    self.viewport_area.blit(s, (dx, dy))
                    # Viền cảnh báo
                    pygame.draw.rect(self.viewport_area, (255, 200, 0), 
                                   (dx, dy, TILE_SIZE, TILE_SIZE), 3)

        # 3. Draw Player (Smooth position)
        px = player.pixel_x - camera_x
        py = player.pixel_y - camera_y
        
        # Jump animation - nhảy lên
        if player.is_jumping:
            py -= 15  # Nâng player lên 15 pixels khi nhảy
        
        p_img = game_assets.get("player")
        if p_img:
            self.viewport_area.blit(p_img, (px, py))
            
            # Hiệu ứng glow khi nhảy
            if player.is_jumping:
                s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                s.fill((255, 255, 100, 80))  # Vàng nhạt
                self.viewport_area.blit(s, (px, py))
        else:
            pygame.draw.rect(self.viewport_area, PLAYER_COLOR, (px+5, py+5, 30, 30))

        # 4. Day/Night Overlay (Smooth Transitions)
        # Calculate darkness based on time
        # Cycle: 0 -> DAY_DURATION (now 240 seconds: 120 day + 120 night)
        import math
        
        cycle_pos = game_time % DAY_DURATION
        half_day = DAY_DURATION // 2
        
        # Normalize position to 0-1 range for the cycle
        normalized_pos = cycle_pos / DAY_DURATION
        
        # Use cosine for smooth transition
        # cos goes from 1 (noon) -> -1 (midnight) -> 1 (noon)
        # We want: Day (0 dark) at 0.25, Night (full dark) at 0.75
        # Shift by 0.25 so midnight is at 0.5
        shifted_pos = (normalized_pos + 0.25) % 1.0
        
        # Cosine interpolation: 0 at day, 1 at night
        factor = (1 - math.cos(shifted_pos * 2 * math.pi)) / 2
        
        alpha = int(factor * MAX_DARKNESS)
        if alpha > 0:
            overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 20, alpha)) # Dark blue-ish tint
            self.viewport_area.blit(overlay, (0, 0))
        
        # Heat Zone Warning Overlay
        if fire_system:
            _, _, heat_level = fire_system.check_player_damage(player, game_time)
            
            if heat_level == 2:  # Danger zone - màu đỏ nhấp nháy
                pulse = (game_time // 200) % 2
                if pulse == 0:
                    # Viền đỏ cảnh báo
                    pygame.draw.rect(self.viewport_area, (255, 0, 0), 
                                   (0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT), 8)
                    # Overlay đỏ mờ
                    danger_overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
                    danger_overlay.fill((255, 0, 0, 40))
                    self.viewport_area.blit(danger_overlay, (0, 0))
            
            elif heat_level == 1:  # Warning zone - màu vàng
                pulse = (game_time // 400) % 2
                if pulse == 0:
                    # Viền vàng cảnh báo
                    pygame.draw.rect(self.viewport_area, (255, 200, 0), 
                                   (0, 0, VIEWPORT_WIDTH, VIEWPORT_HEIGHT), 5)

        # RAIN VISUAL EFFECTS
        if rain_system and rain_system.is_raining:
            # 1. Vẽ hạt mưa (particles)
            rain_particles = rain_system.get_rain_particles()
            for particle in rain_particles:
                # Vẽ giọt mưa (đường thẳng ngắn)
                pygame.draw.line(
                    self.viewport_area,
                    (150, 200, 255),  # Màu xanh nhạt
                    (int(particle['x']), int(particle['y'])),
                    (int(particle['x']), int(particle['y'] + 10)),
                    1
                )
            
            # 2. Overlay xanh mờ để tạo cảm giác mưa
            rain_overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
            rain_overlay.fill((100, 150, 200, 30))  # Xanh dương nhạt
            self.viewport_area.blit(rain_overlay, (0, 0))
            
            # 3. Hiển thị trạng thái mưa
            remaining_time = rain_system.get_remaining_time(game_time)
            rain_text = f"Mưa - {remaining_time}s"
            rain_bg = pygame.Surface((130, 30), pygame.SRCALPHA)
            rain_bg.fill((0, 100, 200, 180))
            self.viewport_area.blit(rain_bg, (VIEWPORT_WIDTH - 140, 10))
            font_rain = pygame.font.SysFont('Segoe UI', 16, bold=True)
            rain_surface = font_rain.render(rain_text, True, (255, 255, 255))
            self.viewport_area.blit(rain_surface, (VIEWPORT_WIDTH - 135, 15))


        # 5. Draw Borders & Sidebars
        pygame.draw.rect(self.screen, COLOR_BORDER, self.rect_viewport, 3)
        
        # Sidebar Left (Stats) - Enhanced with gradient and progress bars
        # Gradient background
        for i in range(TOTAL_SCREEN_HEIGHT):
            alpha = int(100 - (i / TOTAL_SCREEN_HEIGHT) * 50)
            color = (30 + i//20, 30 + i//20, 40 + i//15, alpha)
            surf = pygame.Surface((SIDEBAR_WIDTH, 1), pygame.SRCALPHA)
            surf.fill(color)
            self.screen.blit(surf, (0, i))
        
        # Title with shadow
        draw_text(self.screen, "THÔNG TIN", self.rect_left.x+22, 22, font_title, (0, 0, 0, 100))
        draw_text(self.screen, "THÔNG TIN", self.rect_left.x+20, 20, font_title, COLOR_TEXT_TITLE)
        
        # Decorative line with gradient
        pygame.draw.line(self.screen, (100, 150, 120), (10, 60), (SIDEBAR_WIDTH-10, 60), 3)
        pygame.draw.line(self.screen, (150, 200, 170), (10, 62), (SIDEBAR_WIDTH-10, 62), 1)
        
        y_pos = 85
        
        # HP Bar with icon and gradient
        hp_percent = player.stats["HP"] / 100.0
        draw_text(self.screen, "Máu", self.rect_left.x+20, y_pos, font_body, (255, 100, 100))
        y_pos += 25
        
        # HP Progress Bar
        bar_x, bar_y = 15, y_pos
        bar_w, bar_h = SIDEBAR_WIDTH - 30, 20
        pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
        
        # HP Fill with gradient
        hp_color = (255, 50, 50) if hp_percent > 0.5 else (255, 150, 0) if hp_percent > 0.2 else (200, 0, 0)
        pygame.draw.rect(self.screen, hp_color, (bar_x, bar_y, int(bar_w * hp_percent), bar_h), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
        
        # HP Text
        hp_text = f"{int(player.stats['HP'])}/100"
        draw_text(self.screen, hp_text, bar_x + bar_w//2, bar_y + 10, font_body, (255, 255, 255), center=True)
        y_pos += 35
        
        # Stamina Bar with icon
        stamina_percent = player.stats["Stamina"] / 100.0
        draw_text(self.screen, "Thể Lực", self.rect_left.x+20, y_pos, font_body, (100, 200, 255))
        y_pos += 25
        
        # Stamina Progress Bar
        bar_y = y_pos
        pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
        pygame.draw.rect(self.screen, (50, 180, 255), (bar_x, bar_y, int(bar_w * stamina_percent), bar_h), border_radius=10)
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)
        
        stamina_text = f"{int(player.stats['Stamina'])}/100"
        draw_text(self.screen, stamina_text, bar_x + bar_w//2, bar_y + 10, font_body, (255, 255, 255), center=True)
        y_pos += 45
        
        # Mảnh ghép - Panel nổi bật hơn (FIX: spacing)
        piece_panel_w = SIDEBAR_WIDTH - 20
        piece_panel_h = 65  # Tăng chiều cao để tránh đè chữ
        piece_panel_x = 10
        piece_panel_y = y_pos
        
        # Panel background with gradient
        piece_surf = pygame.Surface((piece_panel_w, piece_panel_h), pygame.SRCALPHA)
        for i in range(piece_panel_h):
            progress = i / piece_panel_h
            gold_val = int(150 + progress * 50)
            alpha = int(200 - progress * 40)
            piece_surf.fill((gold_val, gold_val - 50, 0, alpha), (0, i, piece_panel_w, 1))
        
        # Border
        pygame.draw.rect(piece_surf, (255, 215, 0, 220), (0, 0, piece_panel_w, piece_panel_h), 3, border_radius=12)
        pygame.draw.rect(piece_surf, (255, 255, 150, 150), (0, 0, piece_panel_w, piece_panel_h), 1, border_radius=12)
        self.screen.blit(piece_surf, (piece_panel_x, piece_panel_y))
        
        # Text - FIX: spacing
        draw_text(self.screen, "Mảnh ghép", piece_panel_x + piece_panel_w//2, piece_panel_y + 18, 
                 font_body, (255, 255, 200), center=True)
        
        # Big counter - use actual data from rescue_system
        piece_count = f"{rescue_system.pieces_collected}/{TOTAL_PIECES}" if rescue_system else "0/4"
        draw_text(self.screen, piece_count, piece_panel_x + piece_panel_w//2, piece_panel_y + 45, 
                 font_title, (255, 255, 0), center=True)
        
        y_pos += 75  # Space after piece panel
        
        # Level Display on Sidebar (moved from viewport)
        if level_manager:
            level_text = level_manager.get_level_name()
            level_color = level_manager.get_level_color()
            
            # Level panel
            level_panel_w = SIDEBAR_WIDTH - 20
            level_panel_h = 40
            level_panel_x = 10
            level_panel_y = y_pos
            
            # Background
            level_surf = pygame.Surface((level_panel_w, level_panel_h), pygame.SRCALPHA)
            for i in range(level_panel_h):
                progress = i / level_panel_h
                alpha = int(180 - progress * 40)
                level_surf.fill((0, 0, 0, alpha), (0, i, level_panel_w, 1))
            
            # Border with level color
            pygame.draw.rect(level_surf, level_color, (0, 0, level_panel_w, level_panel_h), 3, border_radius=10)
            pygame.draw.rect(level_surf, (255, 255, 255, 80), (0, 0, level_panel_w, level_panel_h), 1, border_radius=10)
            self.screen.blit(level_surf, (level_panel_x, level_panel_y))
            
            # Text centered in panel
            draw_text(self.screen, level_text, level_panel_x + level_panel_w//2, level_panel_y + 20, 
                     font_body, level_color, center=True)
            
            y_pos += 50  # Space after level panel
        
        # VOLUME CONTROLS - New panel
        if sound_system:
            volume_panel_w = SIDEBAR_WIDTH - 20
            volume_panel_h = 60
            volume_panel_x = 10
            volume_panel_y = y_pos if level_manager else 460
            
            # Panel background with gradient
            volume_surf = pygame.Surface((volume_panel_w, volume_panel_h), pygame.SRCALPHA)
            for i in range(volume_panel_h):
                progress = i / volume_panel_h
                alpha = int(180 - progress * 40)
                volume_surf.fill((40, 40, 60, alpha), (0, i, volume_panel_w, 1))
            
            # Border
            pygame.draw.rect(volume_surf, (100, 150, 200), (0, 0, volume_panel_w, volume_panel_h), 3, border_radius=10)
            pygame.draw.rect(volume_surf, (150, 200, 255, 80), (0, 0, volume_panel_w, volume_panel_h), 1, border_radius=10)
            self.screen.blit(volume_surf, (volume_panel_x, volume_panel_y))
            
            # Volume icon (speaker)
            draw_text(self.screen, "🔊", volume_panel_x + 15, volume_panel_y + 15, font_body, (200, 200, 255))
            
            # Volume percentage
            current_volume = sound_system.get_music_volume()
            volume_percent = int(current_volume * 100)
            volume_text = f"{volume_percent}%"
            draw_text(self.screen, volume_text, volume_panel_x + volume_panel_w//2, volume_panel_y + 18, 
                     font_body, (255, 255, 255), center=True)
            
            # Volume buttons
            btn_size = 35
            btn_y = volume_panel_y + volume_panel_h - btn_size - 5
            
            # [-] button (left)
            vol_down_btn = pygame.Rect(volume_panel_x + 15, btn_y, btn_size, btn_size)
            pygame.draw.rect(self.screen, (180, 50, 50), vol_down_btn, border_radius=5)
            pygame.draw.rect(self.screen, (255, 100, 100), vol_down_btn, 2, border_radius=5)
            draw_text(self.screen, "-", vol_down_btn.centerx, vol_down_btn.centery, font_title, (255, 255, 255), center=True)
            
            # [+] button (right)
            vol_up_btn = pygame.Rect(volume_panel_x + volume_panel_w - btn_size - 15, btn_y, btn_size, btn_size)
            pygame.draw.rect(self.screen, (50, 180, 50), vol_up_btn, border_radius=5)
            pygame.draw.rect(self.screen, (100, 255, 100), vol_up_btn, 2, border_radius=5)
            draw_text(self.screen, "+", vol_up_btn.centerx, vol_up_btn.centery, font_title, (255, 255, 255), center=True)
            
            # Store button rects for click detection
            volume_buttons['down'] = vol_down_btn
            volume_buttons['up'] = vol_up_btn
        # Level indicator removed from viewport (now in sidebar)
            
        # Sidebar Right (Log) - Enhanced gradient
        # Gradient background
        for i in range(TOTAL_SCREEN_HEIGHT):
            alpha = int(100 - (i / TOTAL_SCREEN_HEIGHT) * 50)
            color = (30 + i//20, 30 + i//20, 40 + i//15, alpha)
            surf = pygame.Surface((SIDEBAR_WIDTH, 1), pygame.SRCALPHA)
            surf.fill(color)
            self.screen.blit(surf, (self.rect_right.x, i))
        
        # Title with shadow
        draw_text(self.screen, "NHẬT KÝ", self.rect_right.x+22, 22, font_title, (0, 0, 0, 100))
        draw_text(self.screen, "NHẬT KÝ", self.rect_right.x+20, 20, font_title, COLOR_TEXT_TITLE)
        
        # Decorative line
        pygame.draw.line(self.screen, (100, 150, 120), (self.rect_right.x+10, 60), (self.rect_right.right-10, 60), 3)
        pygame.draw.line(self.screen, (150, 200, 170), (self.rect_right.x+10, 62), (self.rect_right.right-10, 62), 1)
        
        y_pos = 80
        for i, log in enumerate(game_log):
            # Fade effect for older logs
            alpha = max(150, 255 - (len(game_log) - i - 1) * 20)
            color = (200, 200, 200, alpha)
            
            # Log entry with background
            if "Thiêu" in log or "cháy" in log:
                color = (255, 150, 100)
            elif "Mảnh ghép" in log or "Thoát" in log:
                color = (255, 255, 150)
            elif "Mưa" in log:
                color = (150, 200, 255)
            
            draw_text(self.screen, log, self.rect_right.x+20, y_pos, font_body, color)
            y_pos += 25

        # Return volume buttons for click handling
        return volume_buttons


    def draw_minimap(self, map_data, player):
        # Tạo surface cho minimap với alpha
        minimap = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT), pygame.SRCALPHA)
        minimap.fill((0, 0, 0, 100))  # Nền đen mờ thay vì đen đậm
        
        # Tỉ lệ thu nhỏ
        scale_x = MINIMAP_WIDTH / (MAP_WIDTH * TILE_SIZE)
        scale_y = MINIMAP_HEIGHT / (MAP_HEIGHT * TILE_SIZE)
        
        # Kích thước mỗi ô trên minimap
        mini_tile_w = max(1, int(TILE_SIZE * scale_x))
        mini_tile_h = max(1, int(TILE_SIZE * scale_y))
        
        # Vẽ từng ô
        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                tile = map_data[row][col]
                color = COLORS.get(tile, (100, 100, 100))
                
                mx = int(col * TILE_SIZE * scale_x)
                my = int(row * TILE_SIZE * scale_y)
                pygame.draw.rect(minimap, color, (mx, my, mini_tile_w, mini_tile_h))
        
        # Vẽ vị trí player (chấm đỏ)
        px = int(player.pixel_x * scale_x)
        py = int(player.pixel_y * scale_y)
        pygame.draw.circle(minimap, (255, 0, 0), (px, py), 4)
        
        # Viền minimap - Bright cyan for better visibility
        pygame.draw.rect(minimap, (100, 220, 255), (0, 0, MINIMAP_WIDTH, MINIMAP_HEIGHT), 3)
        pygame.draw.rect(minimap, (150, 255, 255), (1, 1, MINIMAP_WIDTH-2, MINIMAP_HEIGHT-2), 1)
        
        # Vẽ lên viewport (góc trên bên trái của viewport)
        self.viewport_area.blit(minimap, (MINIMAP_X, MINIMAP_Y))
    
    def draw_boat_on_minimap(self, boat_position):
        """Vẽ icon thuyền trên minimap"""
        if boat_position:
            scale_x = MINIMAP_WIDTH / (MAP_WIDTH * TILE_SIZE)
            scale_y = MINIMAP_HEIGHT / (MAP_HEIGHT * TILE_SIZE)
            
            bx = int(boat_position[0] * TILE_SIZE * scale_x) + MINIMAP_X
            by = int(boat_position[1] * TILE_SIZE * scale_y) + MINIMAP_Y
            
            # Vẽ icon thuyền (hình tam giác + thanh ngang)
            pygame.draw.polygon(self.viewport_area, (139, 90, 43), [
                (bx, by - 5),
                (bx - 5, by + 5),
                (bx + 5, by + 5)
            ])
            pygame.draw.circle(self.viewport_area, (255, 255, 0), (bx, by), 6, 2)

    def draw_game_over(self, font_menu, font_title, retry_btn, home_btn, mouse_pos):
        # Nền tối mờ
        overlay = pygame.Surface((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Chữ END GAME to đùng
        draw_text(self.screen, "END GAME", TOTAL_SCREEN_WIDTH // 2, 180, font_menu, (255, 50, 50), center=True)
        draw_text(self.screen, "Bạn đã bị thiêu cháy!", TOTAL_SCREEN_WIDTH // 2, 260, font_title, COLOR_TEXT_BODY, center=True)
        
        # Nút Chơi lại
        if retry_btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, COLOR_BTN_HOVER, retry_btn, border_radius=10)
        else:
            pygame.draw.rect(self.screen, COLOR_BTN_NORMAL, retry_btn, border_radius=10)
        pygame.draw.rect(self.screen, (255,255,255), retry_btn, 2, border_radius=10)
        draw_text(self.screen, "CHƠI LẠI", retry_btn.centerx, retry_btn.centery, font_title, COLOR_BTN_TEXT, center=True)
        
        # Nút Trang chủ
        if home_btn.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (200, 100, 0), home_btn, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (150, 75, 0), home_btn, border_radius=10)
        pygame.draw.rect(self.screen, (255,255,255), home_btn, 2, border_radius=10)
        draw_text(self.screen, "TRANG CHỦ", home_btn.centerx, home_btn.centery, font_title, COLOR_BTN_TEXT, center=True)

    def draw_rescue_ui(self, rescue_system, font_title, font_body, mouse_pos, game_time):
        # Piece counter is now shown in the gold panel on sidebar - removed duplicate
        
        # Hiển thị trạng thái pháo
        if rescue_system.flare_activated and not rescue_system.flare_fired:
            draw_text(self.viewport_area, "ĐANG BẮN PHÁO...", VIEWPORT_WIDTH // 2, 100, font_title, (255, 255, 0), center=True)
        
        # Hiển thị thuyền đang đến
        if rescue_system.boat_arriving and not rescue_system.boat_arrived:
            remaining = (BOAT_ARRIVAL_TIME - (game_time - rescue_system.boat_arrival_start)) // 1000
            draw_text(self.viewport_area, f"Thuyền đến trong: {remaining}s", VIEWPORT_WIDTH // 2, 50, font_body, (255, 255, 255), center=True)
        
        # Hiển thị nút lên thuyền
        if rescue_system.near_boat:
            progress = rescue_system.get_board_progress(game_time)
            
            # Thanh tiến độ
            bar_width = 200
            bar_height = 30
            bar_x = (VIEWPORT_WIDTH - bar_width) // 2
            bar_y = VIEWPORT_HEIGHT - 100
            
            pygame.draw.rect(self.viewport_area, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.viewport_area, (0, 200, 0), (bar_x, bar_y, int(bar_width * progress), bar_height))
            pygame.draw.rect(self.viewport_area, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            
            if rescue_system.can_board:
                draw_text(self.viewport_area, "NHẤN ĐỂ LÊN THUYỀN!", VIEWPORT_WIDTH // 2, bar_y - 30, font_title, (0, 255, 0), center=True)
            else:
                draw_text(self.viewport_area, "Đang lên thuyền...", VIEWPORT_WIDTH // 2, bar_y - 30, font_body, (255, 255, 255), center=True)

    def draw_win_screen(self, font_menu, font_title, next_level_btn, retry_btn, home_btn, 
                        mouse_pos, survival_time=0, high_score=0, is_new_record=False, level_manager=None):
        # Gradient background - beautiful green
        for i in range(TOTAL_SCREEN_HEIGHT):
            progress = i / TOTAL_SCREEN_HEIGHT
            green_dark = int(20 + progress * 40)
            green_light = int(50 + progress * 30)
            alpha = int(180 + progress * 60)
            surf = pygame.Surface((TOTAL_SCREEN_WIDTH, 1), pygame.SRCALPHA)
            surf.fill((0, green_dark, green_light, alpha))
            self.screen.blit(surf, (0, i))
        
        # VICTORY text with multiple shadow layers for glow
        victory_y = 80
        # Outer glow
        for offset in range(8, 0, -2):
            alpha = 30 + (8 - offset) * 10
            glow_color = (255, 255, 0, alpha)
            draw_text(self.screen, "VICTORY!", TOTAL_SCREEN_WIDTH // 2, victory_y + offset, 
                     font_menu, glow_color, center=True)
        # Main text with gradient effect
        draw_text(self.screen, "VICTORY!", TOTAL_SCREEN_WIDTH // 2, victory_y, 
                 font_menu, (255, 255, 100), center=True)
        
        # Level completed with icon and shadow
        level_y = 150
        if level_manager:
            completed_text = f"{level_manager.get_level_name()} - Hoàn thành!"
            # Shadow
            draw_text(self.screen, completed_text, TOTAL_SCREEN_WIDTH // 2 + 3, level_y + 3, 
                     font_title, (0, 0, 0, 120), center=True)
            # Main text
            draw_text(self.screen, completed_text, TOTAL_SCREEN_WIDTH // 2, level_y, 
                     font_title, level_manager.get_level_color(), center=True)
        
        # Info panel with gradient and border
        panel_w, panel_h = 450, 120
        panel_x = (TOTAL_SCREEN_WIDTH - panel_w) // 2
        panel_y = 200
        
        # Panel shadow
        shadow_surf = pygame.Surface((panel_w + 8, panel_h + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), (0, 0, panel_w + 8, panel_h + 8), border_radius=20)
        self.screen.blit(shadow_surf, (panel_x - 4, panel_y + 4))
        
        # Panel background with gradient
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        for i in range(panel_h):
            progress = i / panel_h
            green = int(30 + progress * 20)
            alpha = int(220 - progress * 40)
            pygame.draw.line(panel_surf, (10, green, 15, alpha), (0, i), (panel_w, i))
        
        # Panel border - double line
        pygame.draw.rect(panel_surf, (100, 220, 120, 200), (0, 0, panel_w, panel_h), 4, border_radius=18)
        pygame.draw.rect(panel_surf, (150, 255, 170, 255), (0, 0, panel_w, panel_h), 2, border_radius=18)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Time info with icons
        time_str = format_time(survival_time)
        high_str = format_time(high_score)
        
        # Time display
        time_y = panel_y + 30
        draw_text(self.screen, "Thời gian:", TOTAL_SCREEN_WIDTH // 2 - 100, time_y, 
                 font_title, (200, 200, 200), center=False)
        draw_text(self.screen, time_str, TOTAL_SCREEN_WIDTH // 2 + 80, time_y, 
                 font_title, (255, 255, 150), center=False)
        
        # Record display
        record_y = panel_y + 70
        if is_new_record:
            # Pulsing new record
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.004)) * 0.4 + 0.6
            glow_color = (255, int(215 * pulse), 0)
            
            # Glow effect
            for offset in [4, 3, 2]:
                draw_text(self.screen, "KỶ LỤC MỚI!", TOTAL_SCREEN_WIDTH // 2, 
                         record_y + offset, font_title, (*glow_color, 60), center=True)
            
            draw_text(self.screen, "KỶ LỤC MỚI!", TOTAL_SCREEN_WIDTH // 2, record_y, 
                     font_title, (255, 255, 0), center=True)
        else:
            draw_text(self.screen, "Kỷ lục:", TOTAL_SCREEN_WIDTH // 2 - 100, record_y, 
                     font_title, (200, 200, 200), center=False)
            draw_text(self.screen, high_str, TOTAL_SCREEN_WIDTH // 2 + 80, record_y, 
                     font_title, (255, 215, 0), center=False)
        
        # Buttons with better spacing and 3D effect
        btn_y_start = 350
        
        # Next Level Button (Primary)
        self._draw_3d_button(next_level_btn, mouse_pos, "NEXT LEVEL ➤", font_title,
                            (0, 180, 50), (0, 230, 80), (100, 255, 150))
        
        # Secondary buttons side by side
        self._draw_3d_button(retry_btn, mouse_pos, "CHƠI LẠI", font_title,
                            (180, 120, 0), (230, 160, 0), (255, 200, 50))
        
        self._draw_3d_button(home_btn, mouse_pos, "TRANG CHỦ", font_title,
                            (120, 60, 0), (170, 90, 0), (220, 140, 30))
    
    def _draw_3d_button(self, btn_rect, mouse_pos, text, font, normal_color, hover_color, border_color):
        """Draw a 3D-style button with depth and glow"""
        is_hover = btn_rect.collidepoint(mouse_pos)
        color = hover_color if is_hover else normal_color
        
        # 3D depth effect - bottom shadow
        depth = 6
        for i in range(depth, 0, -1):
            shadow_rect = btn_rect.copy()
            shadow_rect.y += i
            darkness = int(255 - (i * 30))
            shadow_color = (darkness // 4, darkness // 6, darkness // 8)
            pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=15)
        
        # Button main body with gradient
        btn_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
        for i in range(btn_rect.height):
            progress = i / btn_rect.height
            darker = tuple(max(0, int(c * (0.7 + progress * 0.3))) for c in color)
            pygame.draw.line(btn_surf, darker, (0, i), (btn_rect.width, i))
        
        pygame.draw.rect(btn_surf, color, (0, 0, btn_rect.width, btn_rect.height), border_radius=15)
        self.screen.blit(btn_surf, (btn_rect.x, btn_rect.y))
        
        # Glow effect when hover
        if is_hover:
            for i in range(3):
                grow = (i + 1) * 3
                glow_rect = btn_rect.inflate(grow, grow)
                alpha = 50 - i * 15
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*hover_color, alpha), 
                               (0, 0, glow_rect.width, glow_rect.height), border_radius=18)
                self.screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Highlight on top
        highlight_rect = pygame.Rect(btn_rect.x + 5, btn_rect.y + 5, 
                                     btn_rect.width - 10, btn_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 40), 
                        (0, 0, highlight_rect.width, highlight_rect.height), border_radius=10)
        self.screen.blit(highlight_surf, (highlight_rect.x, highlight_rect.y))
        
        # Border with double line
        pygame.draw.rect(self.screen, border_color, btn_rect, 3, border_radius=15)
        inner_rect = btn_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, (255, 255, 255, 100), inner_rect, 1, border_radius=12)
        
        # Text with shadow
        text_y_offset = -2 if is_hover else 0
        draw_text(self.screen, text, btn_rect.centerx + 2, btn_rect.centery + 2 + text_y_offset, 
                 font, (0, 0, 0, 180), center=True)
        draw_text(self.screen, text, btn_rect.centerx, btn_rect.centery + text_y_offset, 
                 font, (255, 255, 255), center=True)


    def draw_survival_time(self, survival_time, high_score, font_body):
        # Hiển thị thời gian sống sót ở góc trên phải viewport
        time_str = format_time(survival_time)
        high_str = format_time(high_score)
        
        # Nền tối
        bg_rect = pygame.Rect(VIEWPORT_WIDTH - 130, 10, 120, 55)
        pygame.draw.rect(self.viewport_area, (0, 0, 0, 150), bg_rect, border_radius=5)
        pygame.draw.rect(self.viewport_area, COLOR_BORDER, bg_rect, 2, border_radius=5)
        
        draw_text(self.viewport_area, f"{time_str}", VIEWPORT_WIDTH - 70, 25, font_body, (255, 255, 255), center=True)
        draw_text(self.viewport_area, f"{high_str}", VIEWPORT_WIDTH - 70, 50, font_body, COLOR_TEXT_TITLE, center=True)

    def draw_helper_paths(self, path_helper, camera_x, camera_y, game_time):
        """Vẽ đường đi DFS/BFS và cảnh báo nguy hiểm"""
        
        # 1. Vẽ cảnh báo lửa lan (cam nhấp nháy)
        danger_tiles = path_helper.get_danger_tiles()
        if danger_tiles:
            flicker = (game_time // 300) % 2
            if flicker == 0:
                for col, row in danger_tiles:
                    dx = (col * TILE_SIZE) - camera_x
                    dy = (row * TILE_SIZE) - camera_y
                    
                    # Chỉ vẽ nếu trong viewport
                    if -TILE_SIZE < dx < VIEWPORT_WIDTH and -TILE_SIZE < dy < VIEWPORT_HEIGHT:
                        s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        s.fill((255, 100, 0, 100))  # Cam
                        self.viewport_area.blit(s, (dx, dy))
                        # Vẽ viền cảnh báo
                        pygame.draw.rect(self.viewport_area, (255, 50, 0), 
                                       (dx, dy, TILE_SIZE, TILE_SIZE), 2)
        
        # 2. Vẽ đường DFS đến mảnh ghép (xanh dương)
        piece_path = path_helper.get_piece_path()
        if piece_path:
            for i, (col, row) in enumerate(piece_path):
                dx = (col * TILE_SIZE) - camera_x
                dy = (row * TILE_SIZE) - camera_y
                
                if -TILE_SIZE < dx < VIEWPORT_WIDTH and -TILE_SIZE < dy < VIEWPORT_HEIGHT:
                    # Hiệu ứng nhấp nháy
                    alpha = 150 + int(50 * ((game_time // 200 + i) % 2))
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((50, 150, 255, alpha))  # Xanh dương
                    self.viewport_area.blit(s, (dx, dy))
                    
                    # Vẽ số thứ tự bước
                    font = pygame.font.SysFont('Segoe UI', 14, bold=True)
                    step_text = font.render(str(i + 1), True, (255, 255, 255))
                    self.viewport_area.blit(step_text, (dx + TILE_SIZE//3, dy + TILE_SIZE//3))
        
        # 3. Vẽ đường BFS thoát hiểm (xanh lá)
        escape_path = path_helper.get_escape_path()
        if escape_path:
            for i, (col, row) in enumerate(escape_path):
                dx = (col * TILE_SIZE) - camera_x
                dy = (row * TILE_SIZE) - camera_y
                
                if -TILE_SIZE < dx < VIEWPORT_WIDTH and -TILE_SIZE < dy < VIEWPORT_HEIGHT:
                    # Hiệu ứng nhấp nháy
                    alpha = 150 + int(50 * ((game_time // 200 + i) % 2))
                    s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    s.fill((50, 255, 100, alpha))  # Xanh lá
                    self.viewport_area.blit(s, (dx, dy))
                    
                    # Vẽ mũi tên hướng đi
                    font = pygame.font.SysFont('Segoe UI', 14, bold=True)
                    step_text = font.render(str(i + 1), True, (0, 0, 0))
                    self.viewport_area.blit(step_text, (dx + TILE_SIZE//3, dy + TILE_SIZE//3))
