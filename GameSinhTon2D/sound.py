"""
Sound System - Hệ thống âm thanh cho game
Lưu ý: Cần file âm thanh trong thư mục assets/sounds/
"""
import pygame
import os

class SoundSystem:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Đường dẫn thư mục sounds
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.sounds_dir = os.path.join(script_dir, "assets", "sounds")
        
        # Volume settings
        self.music_volume = 0.3  # 30% volume cho nhạc nền
        self.sfx_volume = 0.5    # 50% volume cho sound effects
        
        # Sound effects dictionary
        self.sounds = {}
        
        # Load sounds
        self.load_sounds()
        
        # Background music
        self.is_music_playing = False
    
    def load_sounds(self):
        """Load tất cả sound effects"""
        # Tạo thư mục sounds nếu chưa có
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)
            print(f"⚠️ Tạo thư mục sounds: {self.sounds_dir}")
            print("⚠️ Thêm file .mp3/.wav vào thư mục này:")
            print("   - bgm.mp3 (nhạc nền)")
            print("   - pickup.wav (nhặt vật phẩm)")
            print("   - attack.wav (tấn công)")
            print("   - damage.wav (nhận sát thương)")
            print("   - jump.wav (nhảy)")
            print("   - victory.wav (chiến thắng)")
            return
        
        # Danh sách sound effects cần load
        sound_files = {
            'pickup': 'pickup.wav',
            'attack': 'attack.wav', 
            'damage': 'damage.wav',
            'jump': 'jump.wav',
            'victory': 'victory.wav',
            'fire': 'fire.wav',
            'rain': 'rain.wav'
        }
        
        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(self.sounds_dir, filename)
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(self.sfx_volume)
                    print(f"✓ Loaded sound: {filename}")
            except Exception as e:
                print(f"✗ Lỗi load sound {filename}: {e}")
    
    def play_bgm(self, loop=True):
        """Phát nhạc nền"""
        if self.is_music_playing:
            return
        
        bgm_path = os.path.join(self.sounds_dir, "bgm.mp3")
        
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.is_music_playing = True
                print("🎵 Phát nhạc nền")
            except Exception as e:
                print(f"✗ Lỗi phát nhạc nền: {e}")
        else:
            print(f"⚠️ Không tìm thấy bgm.mp3 tại {bgm_path}")
    
    def stop_bgm(self):
        """Dừng nhạc nền"""
        pygame.mixer.music.stop()
        self.is_music_playing = False
    
    def play_sound(self, sound_name):
        """
        Phát sound effect
        
        Args:
            sound_name: Tên sound ('pickup', 'attack', 'damage', v.v.)
        """
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                print(f"✗ Lỗi phát sound {sound_name}: {e}")
    
    def set_music_volume(self, volume):
        """Đặt volume nhạc nền (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Đặt volume sound effects (0.0 - 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_music(self):
        """Bật/tắt nhạc nền"""
        if self.is_music_playing:
            pygame.mixer.music.pause()
            self.is_music_playing = False
        else:
            pygame.mixer.music.unpause()
            self.is_music_playing = True
