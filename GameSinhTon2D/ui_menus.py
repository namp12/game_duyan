# ui_menus.py - New menu screens for main menu, level select, and leaderboard

import pygame
import os
from settings import *
from utils import draw_text
from score import format_time, get_high_score_for_level, load_high_scores

# Load menu background once
_menu_bg = None

def _get_menu_background():
    """Load and cache menu background image"""
    global _menu_bg
    if _menu_bg is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, "assets", "menu_bg.png")
        if os.path.exists(bg_path):
            try:
                _menu_bg = pygame.image.load(bg_path).convert()
                _menu_bg = pygame.transform.scale(_menu_bg, (TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
                print("✓ Đã tải hình nền menu")
            except Exception as e:
                print(f"✗ Lỗi load menu_bg.png: {e}")
                _menu_bg = False  # Mark as failed
        else:
            print(f"✗ Không tìm thấy: {bg_path}")
            _menu_bg = False
    return _menu_bg if _menu_bg else None

def draw_main_menu_screen(screen, font_menu, font_title, font_body, mouse_pos):
    """
    Draw main menu with 3 options:
    - Vượt Ải (Campaign)
    - Chọn Màn (Level Select)
    - Bảng Kỷ Lục (Leaderboard)
    
    Returns: dict of button rects
    """
    # Background - try to use image, fallback to solid color
    bg = _get_menu_background()
    if bg:
        screen.blit(bg, (0, 0))
        # Add semi-transparent overlay for better text visibility
        overlay = pygame.Surface((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill((20, 40, 60))
        # Gradient overlay
        for i in range(TOTAL_SCREEN_HEIGHT):
            alpha = int(100 + (i / TOTAL_SCREEN_HEIGHT) * 100)
            surf = pygame.Surface((TOTAL_SCREEN_WIDTH, 1), pygame.SRCALPHA)
            surf.fill((0, 20, 40, alpha))
            screen.blit(surf, (0, i))
    
    # Title
    draw_text(screen, "ĐẢO HOANG SINH TỒN", TOTAL_SCREEN_WIDTH // 2, 80, 
             font_menu, (255, 215, 0), center=True)
    
    # Subtitle
    draw_text(screen, "Hãy chọn chế độ chơi", TOTAL_SCREEN_WIDTH // 2, 150,
             font_body, (200, 200, 200), center=True)
    
    # Button positions
    btn_width = 300
    btn_height = 70
    btn_x = (TOTAL_SCREEN_WIDTH - btn_width) // 2
    start_y = 220
    spacing = 90
    
    # Button 1: Campaign
    campaign_btn = pygame.Rect(btn_x, start_y, btn_width, btn_height)
    _draw_menu_button(screen, campaign_btn, mouse_pos, "VƯỢT ẢI", font_title,
                     (0, 180, 100), (0, 220, 130))
    
    # Button 2: Level Select
    level_select_btn = pygame.Rect(btn_x, start_y + spacing, btn_width, btn_height)
    _draw_menu_button(screen, level_select_btn, mouse_pos, "CHỌN MÀN", font_title,
                     (180, 100, 0), (220, 130, 0))
    
    # Button 3: Leaderboard
    leaderboard_btn = pygame.Rect(btn_x, start_y + spacing * 2, btn_width, btn_height)
    _draw_menu_button(screen, leaderboard_btn, mouse_pos, "BẢNG KỶ LỤC", font_title,
                     (100, 0, 180), (130, 0, 220))
    
    return {
        'campaign': campaign_btn,
        'level_select': level_select_btn,
        'leaderboard': leaderboard_btn
    }

def draw_level_select_screen(screen, font_menu, font_title, font_body, mouse_pos, level_manager):
    """
    Draw level selection grid
    Returns: dict with level buttons and back button
    """
    # Background
    screen.fill((20, 40, 60))
    
    # Title
    draw_text(screen, "CHỌN MÀN CHƠI", TOTAL_SCREEN_WIDTH // 2, 40,
             font_menu, (255, 215, 0), center=True)
    
    # Progress indicator
    completed_count = sum(1 for lvl in range(1, 10) if get_high_score_for_level(lvl) > 0)
    unlocked_count = level_manager.max_level_reached
    progress_text = f"Đã mở: {unlocked_count}/9 | Hoàn thành: {completed_count}/9"
    draw_text(screen, progress_text, TOTAL_SCREEN_WIDTH // 2, 90,
             font_body, (150, 200, 150), center=True)
    
    # Level grid (3x3 for 9 levels)
    levels_per_row = 3
    total_levels = 9
    
    btn_size = 150
    spacing_x = 180
    spacing_y = 160
    start_x = (TOTAL_SCREEN_WIDTH - (spacing_x * levels_per_row)) // 2 + spacing_x // 2
    start_y = 130
    
    level_buttons = {}
    
    for i in range(total_levels):
        level_num = i + 1
        row = i // levels_per_row
        col = i % levels_per_row
        
        x = start_x + col * spacing_x
        y = start_y + row * spacing_y
        
        btn_rect = pygame.Rect(x - btn_size//2, y - btn_size//2, btn_size, btn_size)
        
        is_unlocked = level_manager.is_level_unlocked(level_num)
        high_score = get_high_score_for_level(level_num)
        
        _draw_level_button(screen, btn_rect, mouse_pos, level_num, is_unlocked, 
                          high_score, font_title, font_body)
        
        if is_unlocked:
            level_buttons[level_num] = btn_rect
    
    # Back button
    back_btn = pygame.Rect(50, TOTAL_SCREEN_HEIGHT - 80, 150, 50)
    _draw_menu_button(screen, back_btn, mouse_pos, "← QUAY LẠI", font_body,
                     (80, 80, 80), (120, 120, 120))
    
    return {
        'levels': level_buttons,
        'back': back_btn
    }

def draw_leaderboard_screen(screen, font_menu, font_title, font_body, mouse_pos):
    """
    Draw high score leaderboard
    Returns: dict with back button
    """
    # Background
    screen.fill((20, 40, 60))
    
    # Title
    draw_text(screen, "BẢNG KỶ LỤC", TOTAL_SCREEN_WIDTH // 2, 50,
             font_menu, (255, 215, 0), center=True)
    
    # Table header
    header_y = 120
    draw_text(screen, "Level", TOTAL_SCREEN_WIDTH // 2 - 200, header_y,
             font_title, (200, 200, 200))
    draw_text(screen, "Tên Màn", TOTAL_SCREEN_WIDTH // 2, header_y,
             font_title, (200, 200, 200))
    draw_text(screen, "Kỷ Lục", TOTAL_SCREEN_WIDTH // 2 + 200, header_y,
             font_title, (200, 200, 200))
    
    # Line under header
    pygame.draw.line(screen, (100, 100, 100),
                    (100, header_y + 30),
                    (TOTAL_SCREEN_WIDTH - 100, header_y + 30), 2)
    
    # Load all high scores
    all_scores = load_high_scores()
    
    # Display levels
    y_pos = header_y + 60
    for level in range(1, 10):  # Show first 9 levels
        # Level number
        draw_text(screen, str(level), TOTAL_SCREEN_WIDTH // 2 - 200, y_pos,
                 font_body, (255, 255, 255))
        
        # Level name
        level_name = f"Level {level}"
        draw_text(screen, level_name, TOTAL_SCREEN_WIDTH // 2, y_pos,
                 font_body, (200, 200, 200))
        
        # High score
        high_score = all_scores.get(level, 0)
        if high_score > 0:
            score_text = format_time(high_score)
            color = (255, 215, 0)
        else:
            score_text = "-"
            color = (100, 100, 100)
        
        draw_text(screen, score_text, TOTAL_SCREEN_WIDTH // 2 + 200, y_pos,
                 font_body, color)
        
        y_pos += 40
    
    # Back button
    back_btn = pygame.Rect(50, TOTAL_SCREEN_HEIGHT - 80, 150, 50)
    _draw_menu_button(screen, back_btn, mouse_pos, "← QUAY LẠI", font_body,
                     (80, 80, 80), (120, 120, 120))
    
    return {'back': back_btn}

def _draw_menu_button(screen, btn_rect, mouse_pos, text, font, normal_color, hover_color):
    """Helper to draw a menu button"""
    is_hover = btn_rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else normal_color
    
    # Shadow
    shadow_rect = btn_rect.copy()
    shadow_rect.y += 5
    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=10)
    
    # Button body
    pygame.draw.rect(screen, color, btn_rect, border_radius=10)
    
    # Border
    pygame.draw.rect(screen, (255, 255, 255), btn_rect, 3, border_radius=10)
    
    # Text
    draw_text(screen, text, btn_rect.centerx, btn_rect.centery, font, 
             (255, 255, 255), center=True)

def _draw_level_button(screen, btn_rect, mouse_pos, level_num, is_unlocked, high_score, font_title, font_body):
    """Helper to draw a level selection button with improved visuals"""
    is_hover = btn_rect.collidepoint(mouse_pos) and is_unlocked
    has_completed = high_score > 0
    
    if is_unlocked:
        # Unlocked level
        if has_completed:
            # Completed - GREEN with glow + checkmark
            bg_color = (0, 120, 60) if is_hover else (0, 100, 50)
            border_color = (0, 255, 100)
            text_color = (255, 255, 255)
            
            # Green glow effect
            for i in range(5, 0, -1):
                glow_rect = btn_rect.inflate(i*4, i*4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                alpha = 30 - i * 5
                pygame.draw.rect(glow_surf, (0, 255, 100, alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
                screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
        else:
            # Unlocked but not completed - GOLD
            bg_color = (160, 130, 0) if is_hover else (140, 110, 0)
            border_color = (255, 215, 0)
            text_color = (255, 255, 255)
        
        # Background with gradient
        pygame.draw.rect(screen, bg_color, btn_rect, border_radius=15)
        
        # Bright border
        pygame.draw.rect(screen, border_color, btn_rect, 3, border_radius=15)
        
        # Level number - larger
        level_font = pygame.font.SysFont('Segoe UI', 48, bold=True)
        num_text = level_font.render(str(level_num), True, text_color)
        num_rect = num_text.get_rect(center=(btn_rect.centerx, btn_rect.centery - 35))
        screen.blit(num_text, num_rect)
        
        # Level name
        level_name = f"Level {level_num}"
        draw_text(screen, level_name, btn_rect.centerx, btn_rect.centery + 5,
                 font_body, (220, 220, 220), center=True)
        
        # High score or checkmark
        if has_completed:
            # Checkmark
            check_font = pygame.font.SysFont('Segoe UI', 32)
            check_text = check_font.render("✓", True, (0, 255, 100))
            check_rect = check_text.get_rect(topright=(btn_rect.right - 10, btn_rect.top + 10))
            screen.blit(check_text, check_rect)
            
            # Time at bottom
            score_text = format_time(high_score)
            draw_text(screen, score_text, btn_rect.centerx, btn_rect.centery + 40,
                     font_body, (255, 215, 0), center=True)
        else:
            # "NEW" or "PLAY" indicator
            play_text = "➤ PLAY" if is_hover else "NEW"
            draw_text(screen, play_text, btn_rect.centerx, btn_rect.centery + 40,
                     font_body, (255, 215, 0), center=True)
    else:
        # Locked level - GRAY
        bg_color = (50, 50, 50)
        
        # Background
        pygame.draw.rect(screen, bg_color, btn_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 100), btn_rect, 2, border_radius=15)
        
        # Lock icon (larger)
        lock_font = pygame.font.SysFont('Segoe UI', 56)
        lock_text = lock_font.render("🔒", True, (150, 150, 150))
        lock_rect = lock_text.get_rect(center=(btn_rect.centerx, btn_rect.centery - 15))
        screen.blit(lock_text, lock_rect)
        
        # Level number below lock
        draw_text(screen, str(level_num), btn_rect.centerx, btn_rect.centery + 45,
                 font_body, (100, 100, 100), center=True)
