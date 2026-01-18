import pygame
import os
from settings import *

class SoundManager:
    """Quản lý tất cả âm thanh trong game"""
    
    def __init__(self):
        """Khởi tạo Sound Manager"""
        # Khởi tạo mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Volume settings
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Đường dẫn thư mục sounds
        self.sounds_dir = os.path.join("assets", "sounds")
        
        # Các kênh âm thanh
        self.channels = {
            "fire_warning": pygame.mixer.Channel(0),
            "item": pygame.mixer.Channel(1),
            "ui": pygame.mixer.Channel(2)
        }
        
        # Sound effects dictionary
        self.sounds = {}
        self._load_sounds()
        
        # Music states
        self.current_music = None
        self.music_playing = False
        
    def _load_sounds(self):
        """Tải tất cả sound effects"""
        sound_files = {
            # Sound effects
            "item_pickup": "item_pickup.wav",
            "fire_warning": "fire_warning.wav",
            "win": "win.wav",
            "lose": "lose.wav",
            "button_click": "button_click.wav",
            "flare": "flare.wav"
        }
        
        for name, filename in sound_files.items():
            filepath = os.path.join(self.sounds_dir, filename)
            try:
                if os.path.exists(filepath):
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    self.sounds[name].set_volume(self.sfx_volume)
                else:
                    print(f"[Sound] Không tìm thấy: {filepath}")
                    # Tạo âm thanh giả tạm thời (silence)
                    self.sounds[name] = None
            except Exception as e:
                print(f"[Sound] Lỗi khi tải {filename}: {e}")
                self.sounds[name] = None
    
    def play_music(self, music_name, loops=-1, fade_ms=1000):
        """
        Phát nhạc nền
        
        Args:
            music_name: Tên file nhạc (menu, gameplay, etc.)
            loops: Số lần lặp (-1 = vô hạn)
            fade_ms: Thời gian fade in (milliseconds)
        """
        music_files = {
            "menu": "menu_music.ogg",
            "gameplay": "gameplay_music.ogg",
            "win": "win_music.ogg",
            "gameover": "gameover_music.ogg"
        }
        
        if music_name not in music_files:
            print(f"[Music] Không có nhạc: {music_name}")
            return
        
        music_path = os.path.join(self.sounds_dir, music_files[music_name])
        
        try:
            if os.path.exists(music_path):
                # Dừng nhạc hiện tại nếu đang phát
                if self.music_playing:
                    pygame.mixer.music.fadeout(500)
                
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
                self.current_music = music_name
                self.music_playing = True
            else:
                print(f"[Music] Không tìm thấy: {music_path}")
        except Exception as e:
            print(f"[Music] Lỗi khi phát {music_name}: {e}")
    
    def stop_music(self, fade_ms=1000):
        """Dừng nhạc nền"""
        if self.music_playing:
            pygame.mixer.music.fadeout(fade_ms)
            self.music_playing = False
            self.current_music = None
    
    def play_sound(self, sound_name, channel_name=None):
        """
        Phát sound effect
        
        Args:
            sound_name: Tên sound effect
            channel_name: Tên kênh (nếu muốn chỉ định)
        """
        if sound_name not in self.sounds:
            print(f"[SFX] Không có sound: {sound_name}")
            return
        
        sound = self.sounds[sound_name]
        if sound is None:
            return
        
        try:
            if channel_name and channel_name in self.channels:
                # Phát trên kênh chỉ định
                self.channels[channel_name].play(sound)
            else:
                # Phát trên kênh tự động
                sound.play()
        except Exception as e:
            print(f"[SFX] Lỗi khi phát {sound_name}: {e}")
    
    def set_music_volume(self, volume):
        """Đặt âm lượng nhạc nền (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Đặt âm lượng sound effects (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sfx_volume)
    
    def pause_music(self):
        """Tạm dừng nhạc nền"""
        if self.music_playing:
            pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Tiếp tục nhạc nền"""
        if self.music_playing:
            pygame.mixer.music.unpause()
    
    def toggle_music(self):
        """Bật/tắt nhạc nền"""
        if self.music_playing:
            if pygame.mixer.music.get_busy():
                self.pause_music()
            else:
                self.unpause_music()
    
    def cleanup(self):
        """Dọn dẹp tài nguyên âm thanh"""
        self.stop_music(fade_ms=0)
        pygame.mixer.quit()
