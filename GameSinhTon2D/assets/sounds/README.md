# Hướng Dẫn Tải File Âm Thanh

Tôi đã tạo hệ thống sound manager. Bây giờ bạn cần tải các file âm thanh sau vào thư mục `assets/sounds/`:

## File Âm Thanh Cần Thiết

### Nhạc Nền (Music) - Format: .ogg
1. **menu_music.ogg** - Nhạc menu chờ
2. **gameplay_music.ogg** - Nhạc nền khi chơi
3. **win_music.ogg** - Nhạc chiến thắng
4. **gameover_music.ogg** - Nhạc thua cuộc

### Hiệu Ứng Âm Thanh (SFX) - Format: .wav
1. **item_pickup.wav** - Âm thanh nhặt vật phẩm
2. **fire_warning.wav** - Âm thanh cảnh báo lửa
3. **button_click.wav** - Âm thanh click nút
4. **flare.wav** - Âm thanh bắn pháo hiệu
5. **win.wav** - Âm thanh chiến thắng ngắn
6. **lose.wav** - Âm thanh thua cuộc ngắn

## Nguồn Tải Miễn Phí (CC0/Royalty-Free)

### Mixkit (Dễ nhất - Không cần đăng ký)
- URL: https://mixkit.co/free-sound-effects/game/
- URL Music: https://mixkit.co/free-stock-music/
- Tìm kiếm: "game music", "8-bit", "adventure", "epic"
- Tải trực tiếp, không cần attribution

### Freesound (Cần đăng ký miễn phí)
- URL: https://freesound.org/
- Tìm kiếm: "game pickup", "fire alarm", "victory", "game over"
- Chọn license: CC0 hoặc CC-BY

### OpenGameArt.org
- URL: https://opengameart.org/
- Browse > Audio
- Filter: CC0 Public Domain

## Gợi Ý Cụ Thể

### Menu Music:
- Tìm: "calm ambient music", "menu theme", "chill background"
- Thời lượng: 1-2 phút (sẽ loop)

### Gameplay Music:
- Tìm: "adventure music", "survival game", "tension background"
- Thời lượng: 2-3 phút (sẽ loop)

### Item Pickup:
- Tìm: "coin pickup", "item collect", "power up"
- Thời lượng: < 1 giây

### Fire Warning:
- Tìm: "alarm", "warning siren", "danger alert"
- Thời lượng: 1-2 giây

### Win/Lose:
- Tìm: "victory fanfare", "game over", "success jingle"
- Thời lượng: 2-5 giây

## Hướng Dẫn Tải Nhanh

```bash
# Sau khi tải xong, đặt tất cả file vào:
E:\GameSinhTon2D\GameSinhTon2D\assets\sounds\

# Cấu trúc thư mục sẽ như sau:
assets/
  sounds/
    menu_music.ogg
    gameplay_music.ogg
    win_music.ogg
    gameover_music.ogg
    item_pickup.wav
    fire_warning.wav
    button_click.wav
    flare.wav
    win.wav
    lose.wav
```

## Lưu Ý
- Music files nên dùng format .ogg (nhỏ gọn hơn .mp3)
- SFX nên dùng .wav (chất lượng tốt, delay thấp)
- Nếu tải được .mp3, có thể convert sang .ogg bằng online converter
- Game vẫn chạy được nếu thiếu file âm thanh (sẽ im lặng)
