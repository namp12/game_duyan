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

    def _draw_fancy_button(self, btn_rect, mouse_pos, text, font, normal_color, hover_color, border_color):
        """Draw a fancy button with shadow and glow"""
        is_hover = btn_rect.collidepoint(mouse_pos)
        color = hover_color if is_hover else normal_color
        
        # Shadow
        shadow_rect = btn_rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=12)
        
        # Button background
        pygame.draw.rect(self.screen, color, btn_rect, border_radius=12)
        
        # Glow effect when hover
        if is_hover:
            for i in range(3):
                grow = (i + 1) * 2
                glow_rect = btn_rect.inflate(grow, grow)
                alpha = 40 - i * 10
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*hover_color, alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
                self.screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Border
        pygame.draw.rect(self.screen, border_color, btn_rect, 3, border_radius=12)
        
        # Text with shadow
        draw_text(self.screen, text, btn_rect.centerx + 2, btn_rect.centery + 2, font, (0, 0, 0, 150), center=True)
        draw_text(self.screen, text, btn_rect.centerx, btn_rect.centery, font, (255, 255, 255), center=True)
