import pygame
import sys
import io

# Fix encoding issue on Windows console
sys.stdout.reconfigure(encoding='utf-8')

from settings import *
from utils import load_assets
from world import generate_island_map
from player import Player
from ui import UI
from fire import FireSystem
from rescue import RescueSystem
from score import format_time, get_high_score_for_level, update_high_score
from helper import PathHelper
from level_manager import LevelManager
from rain import RainSystem
from sound import SoundSystem
from turtle import spawn_turtles
from ui_menus import draw_main_menu_screen, draw_level_select_screen, draw_leaderboard_screen

def main():
    pygame.init()
    
    # Fonts - Sử dụng Segoe UI để hỗ trợ tiếng Việt tốt hơn
    font_title = pygame.font.SysFont('Segoe UI', 32, bold=True)
    font_body = pygame.font.SysFont('Segoe UI', 20)
    font_menu = pygame.font.SysFont('Segoe UI', 50, bold=True)
    
    # Setup Screen
    screen_total = pygame.display.set_mode((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
    pygame.display.set_caption("Game Sinh Tồn 2D")
    clock = pygame.time.Clock()
    
    # High Scores per level (loaded dynamically)
    # Will get current level's high score when needed
    
    # Init Objects
    game_assets = load_assets()
    
    # Sound System
    sound_system = SoundSystem()
    sound_system.play_menu_bgm()  # Phát nhạc nền menu (1.mp3)
    
    # Level Manager
    level_manager = LevelManager()
    
    # Rain System (global - persistent across levels)
    rain_system = RainSystem()
    
    # Helper function to start a new level
    def start_new_level():
        """Khởi tạo level mới với cấu hình thích hợp"""
        config = level_manager.get_level_config()
        
        # Generate map
        map_data = generate_island_map(MAP_WIDTH, MAP_HEIGHT)
        
        # Setup Player Position
        start_x, start_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
        while map_data[start_y][start_x] in [TILE_WATER, TILE_TREE]:
            start_x += 1
            start_y += (start_x % 2)
        
        player = Player(start_x, start_y)
        
        # Fire System với level config
        fire_system = FireSystem(config)
        
        # Rescue System với level config
        rescue_system = RescueSystem(
            pieces_required=config["pieces_required"],
            boat_time=config["boat_arrival_time"]
        )
        rescue_system.place_pieces(map_data)
        
        # Path Helper
        path_helper = PathHelper()
        
        return map_data, player, fire_system, rescue_system, path_helper
    
    # Initialize first level
    map_data, player, fire_system, rescue_system, path_helper = start_new_level()
    
    ui_manager = UI(screen_total)
    
    # Game State
    current_state = GAME_STATE_MAIN_MENU
    game_log = ["- Sẵn sàng...", "- Bấm nút để chơi."]
    
    # Survival Timer
    game_start_time = 0
    survival_time = 0
    
    # Menu button states
    main_menu_buttons = {}
    level_select_buttons = {}
    leaderboard_buttons = {}
    volume_buttons = {}  # Volume control buttons
    
    # Turtle enemies (Level 2)
    turtles = []
    
    # Camera
    camera_x = 0
    camera_y = 0
    
    # Menu Button
    btn_width, btn_height = 200, 80
    btn_x = (TOTAL_SCREEN_WIDTH // 2) - (btn_width // 2)
    btn_y = (TOTAL_SCREEN_HEIGHT // 2) - (btn_height // 2)
    start_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)
    
    # Game Over Buttons
    retry_btn = pygame.Rect(btn_x - 110, btn_y + 100, btn_width, 60)
    home_btn = pygame.Rect(btn_x + 110, btn_y + 100, btn_width, 60)
    
    # Win Screen Buttons - 3 nút riêng cho màn WIN (điều chỉnh vị trí xuống dưới)
    win_next_btn = pygame.Rect(btn_x, btn_y + 100, btn_width, 60)  # Next Level (giữa, di chuyển xuống)
    win_retry_btn = pygame.Rect(btn_x - 110, btn_y + 200, btn_width, 60)  # Chơi lại (trái)
    win_home_btn = pygame.Rect(btn_x + 110, btn_y + 200, btn_width, 60)  # Trang chủ (phải)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # --- INPUT HANDLER ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Handle Main Menu clicks
                if current_state == GAME_STATE_MAIN_MENU:
                    if 'campaign' in main_menu_buttons and main_menu_buttons['campaign'].collidepoint(mouse_pos):
                        # Start campaign - Level 1
                        level_manager.current_level = 1
                        map_data, player, fire_system, rescue_system, path_helper = start_new_level()
                        turtles = spawn_turtles(map_data, level_manager.current_level)
                        game_start_time = pygame.time.get_ticks()
                        current_state = GAME_STATE_PLAYING
                        sound_system.play_game_bgm()  # Chuyển sang nhạc gameplay
                        game_log = ["- Bắt đầu Level 1!", "- Tìm 4 mảnh ghép để thoát đảo."]
                    elif 'level_select' in main_menu_buttons and main_menu_buttons['level_select'].collidepoint(mouse_pos):
                        current_state = GAME_STATE_LEVEL_SELECT
                        # Duy trì nhạc menu
                    elif 'leaderboard' in main_menu_buttons and main_menu_buttons['leaderboard'].collidepoint(mouse_pos):
                        current_state = GAME_STATE_LEADERBOARD
                        # Duy trì nhạc menu
                
                # Handle Level Select clicks
                elif current_state == GAME_STATE_LEVEL_SELECT:
                    if 'back' in level_select_buttons and level_select_buttons['back'].collidepoint(mouse_pos):
                        current_state = GAME_STATE_MAIN_MENU
                        # Duy trì nhạc menu
                    elif 'levels' in level_select_buttons:
                        for level_num, btn_rect in level_select_buttons['levels'].items():
                            if btn_rect.collidepoint(mouse_pos):
                                level_manager.current_level = level_num
                                map_data, player, fire_system, rescue_system, path_helper = start_new_level()
                                turtles = spawn_turtles(map_data, level_manager.current_level)
                                game_start_time = pygame.time.get_ticks()
                                current_state = GAME_STATE_PLAYING
                                sound_system.play_game_bgm()  # Chuyển sang nhạc gameplay
                                game_log = [f"- Bắt đầu Level {level_num}!", "- Tìm mảnh ghép để thoát đảo."]
                                break
                
                # Handle Leaderboard clicks
                elif current_state == GAME_STATE_LEADERBOARD:
                    if 'back' in leaderboard_buttons and leaderboard_buttons['back'].collidepoint(mouse_pos):
                        current_state = GAME_STATE_MAIN_MENU
                        # Duy trì nhạc menu
                
                # Handle Game Over clicks
                elif current_state == GAME_STATE_GAMEOVER:
                    if retry_btn.collidepoint(mouse_pos):
                        # Retry current level
                        map_data, player, fire_system, rescue_system, path_helper = start_new_level()
                        turtles = spawn_turtles(map_data, level_manager.current_level)
                        game_start_time = pygame.time.get_ticks()
                        current_state = GAME_STATE_PLAYING
                        sound_system.play_game_bgm()  # Chuyển sang nhạc gameplay
                        game_log = ["- Chơi lại!", "- Cố gắng lên!"]
                    elif home_btn.collidepoint(mouse_pos):
                        current_state = GAME_STATE_MAIN_MENU
                        sound_system.play_menu_bgm()  # Chuyển về nhạc menu
                
                # Handle Win Screen clicks
                elif current_state == GAME_STATE_WIN:
                    if win_next_btn.collidepoint(mouse_pos):
                        # Unlock next level if this is the highest reached
                        if level_manager.current_level >= level_manager.max_level_reached:
                            level_manager.max_level_reached = level_manager.current_level + 1
                            # Save progress
                            from score import save_level_progress
                            save_level_progress(level_manager.max_level_reached)
                            game_log.append(f"🎉 Level {level_manager.max_level_reached} unlocked!")
                        
                        # Move to next level
                        level_manager.current_level += 1
                        if level_manager.current_level > 9:
                            level_manager.current_level = 9
                        map_data, player, fire_system, rescue_system, path_helper = start_new_level()
                        turtles = spawn_turtles(map_data, level_manager.current_level)
                        game_start_time = pygame.time.get_ticks()
                        current_state = GAME_STATE_PLAYING
                        sound_system.play_game_bgm()  # Chuyển sang nhạc gameplay
                        game_log = [f"- Level {level_manager.current_level}!", "- Tiếp tục nào!"]
                    elif win_retry_btn.collidepoint(mouse_pos):
                        # Replay current level
                        map_data, player, fire_system, rescue_system, path_helper = start_new_level()
                        turtles = spawn_turtles(map_data, level_manager.current_level)
                        game_start_time = pygame.time.get_ticks()
                        current_state = GAME_STATE_PLAYING
                        sound_system.play_game_bgm()  # Chuyển sang nhạc gameplay
                        game_log = ["- Chơi lại!", "- Cải thiện kỷ lục!"]
                    elif win_home_btn.collidepoint(mouse_pos):
                        current_state = GAME_STATE_MAIN_MENU
                        sound_system.play_menu_bgm()  # Chuyển về nhạc menu
                
                # Handle Volume Button clicks during PLAYING state
                elif current_state == GAME_STATE_PLAYING:
                    if 'down' in volume_buttons and volume_buttons['down'].collidepoint(mouse_pos):
                        # Decrease volume by 10%
                        sound_system.adjust_volume(-0.1)
                    elif 'up' in volume_buttons and volume_buttons['up'].collidepoint(mouse_pos):
                        # Increase volume by 10%
                        sound_system.adjust_volume(0.1)
            
            # Handle keyboard input for gameplay
            elif event.type == pygame.KEYDOWN and current_state == GAME_STATE_PLAYING:
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    dx = -1
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    dx = 1
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    dy = -1
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    dy = 1
                
                if dx != 0 or dy != 0:
                    player.move(dx, dy, map_data, game_log, sprint=False, jump=False, sound_system=sound_system, fire_system=fire_system)
                
                # Helper keys - Số và chữ cái
                if event.key == pygame.K_1 or event.key == pygame.K_h:
                    path_helper.find_path_to_piece(map_data, (player.grid_x, player.grid_y), rescue_system, player, game_log)
                elif event.key == pygame.K_2 or event.key == pygame.K_e:
                    path_helper.find_escape_route(map_data, (player.grid_x, player.grid_y), fire_system, player, game_log)
                elif event.key == pygame.K_3:
                    path_helper.find_path_to_boat(map_data, (player.grid_x, player.grid_y), rescue_system, player, game_log)
                elif event.key == pygame.K_4:
                    path_helper.predict_fire_spread(map_data, fire_system, player, game_log)
                
                # Lên thuyền - SPACE key
                elif event.key == pygame.K_SPACE:
                    if rescue_system.can_board:
                        if rescue_system.board_boat():
                            current_state = GAME_STATE_WIN
                            game_log.append("THẮNG! Bạn đã thoát đảo!")
                            if len(game_log) > 10:
                                game_log.pop(0)
                    elif rescue_system.near_boat:
                        game_log.append("Đứng gần thuyền thêm chút nữa...")
                        if len(game_log) > 10:
                            game_log.pop(0)
            
        # --- UPDATE & RENDER ---
        if current_state == GAME_STATE_MAIN_MENU:
            main_menu_buttons = draw_main_menu_screen(screen_total, font_menu, font_title, font_body, mouse_pos)
            
        elif current_state == GAME_STATE_LEVEL_SELECT:
            level_select_buttons = draw_level_select_screen(screen_total, font_menu, font_title, font_body, mouse_pos, level_manager)
            
        elif current_state == GAME_STATE_LEADERBOARD:
            leaderboard_buttons = draw_leaderboard_screen(screen_total, font_menu, font_title, font_body, mouse_pos)
            
        elif current_state == GAME_STATE_PLAYING:
            player.update()
            
            # Camera Update (Target pixel position for smoothness)
            target_cam_x = player.pixel_x - (VIEWPORT_WIDTH // 2) + (TILE_SIZE // 2)
            target_cam_y = player.pixel_y - (VIEWPORT_HEIGHT // 2) + (TILE_SIZE // 2)
            
            camera_x += (target_cam_x - camera_x) * 0.1
            camera_y += (target_cam_y - camera_y) * 0.1
            
            # Kẹp camera
            max_cam_x = (MAP_WIDTH * TILE_SIZE) - VIEWPORT_WIDTH
            max_cam_y = (MAP_HEIGHT * TILE_SIZE) - VIEWPORT_HEIGHT
            camera_x = max(0, min(camera_x, max_cam_x))
            camera_y = max(0, min(camera_y, max_cam_y))
            
            game_time = pygame.time.get_ticks()
            survival_time = game_time - game_start_time
            
            # Fire System Update
            fire_system.update(map_data, game_time)
            
            # Kiểm tra nhân vật bị bao vây bởi lửa
            if player.is_surrounded_by_fire(fire_system):
                player.teleport_to_safety(map_data, fire_system, game_log)
            
            # Rain System Update - Dập lửa khi mưa
            rain_system.update(game_time, fire_system, map_data, game_log)
            
            # Rescue System Update
            if rescue_system.check_piece_pickup(player, map_data, game_log):
                # Đủ 4 mảnh - kích hoạt pháo
                rescue_system.activate_flare(game_time, game_log)
            
            rescue_system.update(game_time, map_data, game_log, fire_system)
            rescue_system.check_near_boat(player, game_time)
            
            # Helper System Update
            path_helper.update(game_time, fire_system.fire_tiles, map_data, (player.grid_x, player.grid_y))
            
            # Check player fire damage (Progressive System)
            should_damage, damage_amount, heat_level = fire_system.check_player_damage(player, game_time)
            
            # Apply damage
            if should_damage and damage_amount > 0:
                player.stats["HP"] -= damage_amount
                
                # Damage message dựa trên intensity
                if damage_amount == FIRE_DAMAGE_LIGHT:
                    game_log.append(f"Bạn bị lửa thiêu! -{damage_amount} HP")
                elif damage_amount == FIRE_DAMAGE_MEDIUM:
                    game_log.append(f"Lửa ngày càng mạnh! -{damage_amount} HP")
                else:
                    game_log.append(f"Trung tâm đám cháy! -{damage_amount} HP")
                
                if len(game_log) > 10:
                    game_log.pop(0)
                
                if player.stats["HP"] <= 0:
                    player.stats["HP"] = 0
                    current_state = GAME_STATE_GAMEOVER
            
            # Heat zone warnings (không damage nhưng cảnh báo)
            elif heat_level == 2:
                # Danger zone - cực kỳ nguy hiểm
                if game_time % 2000 < 100:  # Cảnh báo mỗi 2 giây
                    if not any("CỰC KỲ NGUY HIỂM" in msg for msg in game_log[-3:]):
                        game_log.append("CỰC KỲ NGUY HIỂM! Lửa rất gần!")
                        if len(game_log) > 10:
                            game_log.pop(0)
            elif heat_level == 1:
                # Warning zone - cảnh báo
                if game_time % 3000 < 100:  # Cảnh báo mỗi 3 giây
                    if not any("Cẩn thận" in msg for msg in game_log[-3:]):
                        game_log.append("Cẩn thận! Lửa đang lan tới gần")
                        if len(game_log) > 10:
                            game_log.pop(0)
            
            volume_buttons = ui_manager.draw_game_screen(
                player, map_data, camera_x, camera_y, 
                game_assets, game_log, (font_title, font_body), game_time, fire_system, level_manager, rain_system, rescue_system, sound_system
            )
            
            # Vẽ đường đi helper (DFS/BFS)
            ui_manager.draw_helper_paths(
                path_helper, camera_x, camera_y, game_time
            )
            
            # Draw turtles
            for turtle in turtles:
                turtle.draw(ui_manager.viewport_area, camera_x, camera_y)

            ui_manager.draw_minimap(map_data, player)
            
            # Vẽ icon thuyền trên minimap nếu thuyền đã đến
            if rescue_system.boat_arrived:
                ui_manager.draw_boat_on_minimap(rescue_system.boat_position)
            
            # Vẽ UI cứu hộ và thời gian sống sót
            ui_manager.draw_rescue_ui(rescue_system, font_title, font_body, mouse_pos, game_time)
            level_high_score = get_high_score_for_level(level_manager.current_level)
            ui_manager.draw_survival_time(survival_time, level_high_score, font_body)
        
        elif current_state == GAME_STATE_GAMEOVER:
            # Vẽ game screen phía sau (tối mờ)
            ui_manager.draw_game_screen(
                player, map_data, camera_x, camera_y, 
                game_assets, game_log, (font_title, font_body), pygame.time.get_ticks(), fire_system, level_manager, rain_system
            )
            ui_manager.draw_game_over(font_menu, font_title, retry_btn, home_btn, mouse_pos)

        
        elif current_state == GAME_STATE_WIN:
            ui_manager.draw_game_screen(
                player, map_data, camera_x, camera_y, 
                game_assets, game_log, (font_title, font_body), pygame.time.get_ticks(), fire_system, level_manager, rain_system
            )
            # Get current level's high score for display
            level_high_score = get_high_score_for_level(level_manager.current_level)
            is_new_record, _ = update_high_score(level_manager.current_level, survival_time)
            
            ui_manager.draw_win_screen(font_menu, font_title, win_next_btn, win_retry_btn, win_home_btn,
                                      mouse_pos, survival_time, level_high_score, is_new_record, level_manager)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
