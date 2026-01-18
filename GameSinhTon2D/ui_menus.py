# ui_menus.py - New menu screens for main menu, level select, and leaderboard

import pygame
from settings import *
from utils import draw_text
from score import format_time, get_high_score_for_level, load_high_scores

def draw_main_menu_screen(screen, font_menu, font_title, font_body, mouse_pos):
    """
    Draw main menu with 3 options:
    - Vượt Ải (Campaign)
    - Chọn Màn (Level Select)
    - Bảng Kỷ Lục (Leaderboard)
    
    Returns: dict of button rects
    """
    # Background
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
    draw_text(screen, "CHỌN MÀN CHƠI", TOTAL_SCREEN_WIDTH // 2, 50,
             font_menu, (255, 215, 0), center=True)
    
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
    """Helper to draw a level selection button"""
    is_hover = btn_rect.collidepoint(mouse_pos) and is_unlocked
    
    if is_unlocked:
        # Unlocked level
        bg_color = (0, 150, 100) if is_hover else (0, 100, 70)
        border_color = (0, 255, 150) if is_hover else (0, 200, 120)
        
        # Background
        pygame.draw.rect(screen, bg_color, btn_rect, border_radius=15)
        pygame.draw.rect(screen, border_color, btn_rect, 3, border_radius=15)
        
        # Level number
        draw_text(screen, str(level_num), btn_rect.centerx, btn_rect.centery - 30,
                 font_title, (255, 255, 255), center=True)
        
        # Level name
        level_text = f"Level {level_num}"
        draw_text(screen, level_text, btn_rect.centerx, btn_rect.centery + 10,
                 font_body, (200, 200, 200), center=True)
        
        # High score
        if high_score > 0:
            score_text = format_time(high_score)
            draw_text(screen, score_text, btn_rect.centerx, btn_rect.centery + 40,
                     font_body, (255, 215, 0), center=True)
    else:
        # Locked level
        bg_color = (50, 50, 50)
        
        # Background
        pygame.draw.rect(screen, bg_color, btn_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 100, 100), btn_rect, 2, border_radius=15)
        
        # Lock icon (text)
        draw_text(screen, "🔒", btn_rect.centerx, btn_rect.centery - 10,
                 font_title, (150, 150, 150), center=True)
        
        # Level number
        draw_text(screen, str(level_num), btn_rect.centerx, btn_rect.centery + 30,
                 font_body, (100, 100, 100), center=True)
