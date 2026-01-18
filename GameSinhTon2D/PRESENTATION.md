# THUYẾT TRÌNH: Ứng Dụng Thuật Toán BFS/DFS trong Game Sinh Tồn 2D

**Thời gian:** 10 phút  
**Đối tượng:** Giảng viên, sinh viên  
**Mục đích:** Giới thiệu game và ứng dụng thực tế của BFS/DFS

---

## 📋 SLIDE 1: GIỚI THIỆU (1 phút)

### Chào mừng!

**Đề tài:** Ứng dụng thuật toán BFS (Breadth-First Search) và DFS (Depth-First Search) trong game 2D

**Nội dung trình bày:**
- Tổng quan game "Đảo Hoang Sinh Tồn 2D"
- Giải thích thuật toán BFS và DFS
- Demo ứng dụng thực tế trong game
- Kết luận và đánh giá

---

## 📋 SLIDE 2: TỔNG QUAN GAME (2 phút)

### 🎮 Đảo Hoang Sinh Tồn 2D

**Câu chuyện:**
Người chơi bị mắc kẹt trên đảo hoang, phải:
1. ✅ Thu thập 4-9 mảnh ghép (tùy level)
2. 🔥 Tránh lửa rừng lan rộng
3. 🚢 Bắn pháo hiệu và lên thuyền cứu hộ
4. ⏱️ Thoát đảo với thời gian nhanh nhất

**Thách thức:**
- 🔥 Lửa lan tự động qua cỏ, cây, hoa
- ⚡ Thể lực (Stamina) và HP giới hạn
- 🌧️ Hệ thống mưa tự động (dập lửa)
- 🌙 Chu kỳ ngày/đêm

**Công nghệ:**
- Ngôn ngữ: Python
- Framework: Pygame
- Map: 100x80 tiles procedurally generated

---

## 📋 SLIDE 3: THUẬT TOÁN BFS (Breadth-First Search) (2 phút)

### 🔵 BFS - Tìm Kiếm Theo Chiều Rộng

**Nguyên lý:**
```
1. Bắt đầu từ điểm xuất phát
2. Duyệt tất cả các điểm lân cận trước (cùng cấp độ)
3. Sau đó mới duyệt điểm xa hơn (cấp độ tiếp theo)
4. Sử dụng QUEUE (hàng đợi) - FIFO
```

**Đặc điểm:**
- ✅ **Tìm đường đi NGẮN NHẤT**
- ✅ Duyệt theo từng "lớp" (layer by layer)
- ⏱️ Time: O(V + E) - V: vertices, E: edges
- 💾 Space: O(V) - cần lưu queue

**Cấu trúc dữ liệu:**
```python
from collections import deque

queue = deque([(start_x, start_y, [])])  # FIFO queue
visited = set()

while queue:
    x, y, path = queue.popleft()  # Lấy từ ĐẦU (FIFO)
    # ... xử lý
    queue.append((nx, ny, new_path))  # Thêm vào CUỐI
```

---

## 📋 SLIDE 4: THUẬT TOÁN DFS (Depth-First Search) (1.5 phút)

### 🔴 DFS - Tìm Kiếm Theo Chiều Sâu

**Nguyên lý:**
```
1. Bắt đầu từ điểm xuất phát
2. Đi sâu nhất có thể theo một hướng
3. Nếu막막막막막막막막막막막막막막
4. Sử dụng STACK (ngăn xếp) - LIFO hoặc Recursion
```

**Đặc điểm:**
- ✅ Tìm được đường đi (nhưng **không đảm bảo ngắn nhất**)
- ✅ Duyệt theo "chiều sâu" (depth-first)
- ⏱️ Time: O(V + E)
- 💾 Space: O(V) - call stack/recursion

**Ứng dụng trong game:**
- ✅ Kiểm tra khả năng tới đích (boat placement)
- ✅ Tìm vùng connected components

---

## 📋 SLIDE 5: ỨNG DỤNG #1 - TÌM MẢNH GHÉP (1.5 phút)

### 🧩 [BFS] Tìm Đường Đến Mảnh Ghép

**Yêu cầu:** Tìm đường NGẮN NHẤT đến mảnh ghép gần nhất

**Tại sao dùng BFS?**
- ✅ Cần đường đi ngắn nhất
- ✅ Giúp người chơi tiết kiệm thời gian
- ✅ Tránh lãng phí stamina

**Implementation** ([helper.py:25-68](file:///d:/game_duyan/GameSinhTon2D/helper.py#L25-L68)):

```python
def find_all_pieces_bfs(self, player_pos, map_data, piece_positions):
    \"\"\"Tìm đường đến TẤT CẢ các mảnh ghép bằng BFS\"\"\"
    queue = deque([(start_col, start_row, [])])
    visited = set()
    
    while queue:
        col, row, path = queue.popleft()  # BFS: FIFO
        
        if (col, row) == target_piece:
            return path  # Đảm bảo đường ngắn nhất!
        
        # Duyệt 4 hướng: ↑ ↓ ← →
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            # ... kiểm tra hợp lệ
            if tile not in [WATER, TREE, FIRE, ROCK]:
                queue.append((nx, ny, path + [(nx, ny)]))
```

**Visual:** Đường màu xanh dương hiển thị trên map

**Phím tắt:** `1` hoặc `H`

**Chi phí:** -30 Stamina (vĩnh viễn)

---

## 📋 SLIDE 6: ỨNG DỤNG #2 - THOÁT HIỂM (1 phút)

### 🏃 [BFS] Tìm Lối Thoát Khẩn Cấp

**Yêu cầu:** Tìm đường NGẮN NHẤT đến vùng an toàn (cách lửa ≥4 ô)

**Tại sao dùng BFS?**
- ✅ Cần đường thoát nhanh nhất khi HP thấp
- ✅ Tránh lửa lan
- ✅ Đảm bảo an toàn

**Implementation** ([helper.py:124-163](file:///d:/game_duyan/GameSinhTon2D/helper.py#L124-L163)):

```python
def find_safe_path_bfs(self, player_pos, map_data, fire_tiles):
    \"\"\"BFS tìm đường đến vùng an toàn\"\"\"
    queue = deque([(start_col, start_row, [])])
    
    while queue:
        col, row, path = queue.popleft()
        
        # Kiểm tra an toàn: khoảng cách Manhattan ≥ 4
        is_safe = True
        for fire_col, fire_row in fire_tiles:
            distance = abs(col - fire_col) + abs(row - fire_row)
            if distance < 4:
                is_safe = False
                break
        
        if is_safe and path:
            return path  # Tìm thấy lối thoát!
```

**Visual:** Đường màu xanh lá hiển thị trên map

**Phím tắt:** `2` hoặc `E`

**Điều kiện:** HP ≤ 50

---

## 📋 SLIDE 7: ỨNG DỤNG #3 - DỰ ĐOÁN LỬA LAN (1 phút)

### 🔥 [BFS] Dự Đoán Vùng Nguy Hiểm

**Yêu cầu:** Hiển thị các ô sẽ bị lửa lan tới trong 2 bước tiếp theo

**Tại sao dùng BFS?**
- ✅ Mô phỏng lan truyền theo "lớp"
- ✅ Tính toán khoảng cách chính xác
- ✅ Cảnh báo sớm cho người chơi

**Implementation** ([helper.py:189-220](file:///d:/game_duyan/GameSinhTon2D/helper.py#L189-L220)):

```python
def predict_fire_spread_bfs(self, fire_tiles, map_data, depth=2):
    \"\"\"BFS dự đoán lửa lan trong depth bước\"\"\"
    for fire_pos in fire_tiles:
        queue = deque([(fire_pos[0], fire_pos[1], 0)])
        
        while queue:
            col, row, dist = queue.popleft()
            
            if dist >= depth:  # Giới hạn độ sâu
                continue
            
            # Lửa lan sang cỏ, cây, hoa
            if tile in [GRASS, TREE, FLOWER]:
                self.danger_tiles.add((nx, ny))
                queue.append((nx, ny, dist + 1))
```

**Visual:** Overlay màu cam nhấp nháy

**Phím tắt:** `4`

**Tự động:** Kích hoạt khi lửa cách player ≤5 ô

---

## 📋 SLIDE 8: ỨNG DỤNG #4 - ĐẶT THUYỀN CỨU HỘ (1 phút)

### 🚢 [DFS] Kiểm Tra Khả Năng Tiếp Cận Thuyền

**Yêu cầu:** Đảm bảo thuyền spawn ở vị trí player có thể tới được

**Tại sao dùng DFS?**
- ✅ Chỉ cần kiểm tra "có đường đi hay không"
- ✅ Không cần đường ngắn nhất
- ✅ DFS đơn giản, tiết kiệm bộ nhớ hơn

**Implementation** ([rescue.py:121-152](file:///d:/game_duyan/GameSinhTon2D/rescue.py#L121-L152)):

```python
def dfs_can_reach(start_col, start_row, target_col, target_row, map_data):
    \"\"\"DFS kiểm tra có thể đến được đích không\"\"\"
    stack = [(start_col, start_row)]  # LIFO stack
    visited = set()
    
    while stack:
        col, row = stack.pop()  # Lấy từ CUỐI (LIFO)
        
        if (col, row) == (target_col, target_row):
            return True  # Tìm được đường!
        
        for dx, dy in [(1,0), (0,1), (-1,0), (0,-1)]:
            if (nx, ny) not in visited:
                stack.append((nx, ny))  # Thêm vào CUỐI
    
    return False  # Không có đường đi
```

**Kết quả:** Thuyền chỉ spawn nếu player có thể đến được

---

## 📋 SLIDE 9: SO SÁNH BFS vs DFS (1 phút)

### 📊 Bảng So Sánh

| Tiêu chí | BFS | DFS |
|----------|-----|-----|
| **Cấu trúc** | Queue (FIFO) | Stack (LIFO) / Recursion |
| **Duyệt** | Theo chiều rộng | Theo chiều sâu |
| **Đường đi** | ✅ Ngắn nhất | ❌ Không đảm bảo |
| **Bộ nhớ** | Nhiều hơn (O(V)) | Ít hơn |
| **Ứng dụng trong game** | - Tìm mảnh ghép<br>- Thoát hiểm<br>- Dự đoán lửa<br>- Tìm đường đến thuyền | - Kiểm tra reachability<br>- Spawn validation |
| **Tốc độ** | O(V + E) | O(V + E) |

### Khi nào dùng gì?

- **BFS:** Khi cần đường đi ngắn nhất hoặc khoảng cách chính xác
- **DFS:** Khi chỉ cần biết "có/không" hoặc duyệt toàn bộ graph

---

## 📋 SLIDE 10: DEMO THỰC TẾ (Nếu có thời gian)

### 🎬 Chạy Game Demo

**Các bước:**
1. Chạy game: `python main.py`
2. Chọn "VƯỢT ẢI" để bắt đầu Level 1
3. Demo các phím helper:

**Thao tác demo:**

| Phím | Tính năng | Thuật toán |
|------|-----------|------------|
| `1` hoặc `H` | Tìm mảnh ghép | BFS |
| `2` hoặc `E` | Thoát hiểm | BFS |
| `4` | Dự đoán lửa lan | BFS |
| _(tự động)_ | Spawn thuyền | DFS |

**Các điểm nhấn mạnh:**
- ✨ Đường màu xanh dương = BFS tìm mảnh ghép
- ✨ Đường màu xanh lá = BFS thoát hiểm  
- ✨ Overlay cam = BFS dự đoán lửa
- ✨ Đường tự động biến mất khi player di chuyển
- ✨ Giới hạn 10s hiển thị (tránh spam)

---

## 📋 SLIDE 11: KẾT LUẬN (1 phút)

### 🎯 Tổng Kết

**Đã thực hiện:**
- ✅ Implement thành công BFS/DFS trong game 2D thực tế
- ✅ Ứng dụng 4 tính năng helper với BFS/DFS:
  - 🧩 Tìm mảnh ghép (BFS)
  - 🏃 Thoát hiểm (BFS)
  - 🔥 Dự đoán lửa (BFS)
  - 🚢 Kiểm tra thuyền (DFS)
- ✅ Tối ưu hiệu suất với visited set và time limits
- ✅ UX tốt: visual feedback rõ ràng, tự động ẩn đường đi

**Kết quả:**
- Game playable, hoàn chỉnh với 9 levels
- Thuật toán hoạt động chính xác và hiệu quả
- Code clean, dễ bảo trì ([helper.py](file:///d:/game_duyan/GameSinhTon2D/helper.py))

**Bài học:**
- 💡 BFS phù hợp cho shortest path problems
- 💡 DFS tốt cho existence/reachability checks
- 💡 Lựa chọn thuật toán dựa vào yêu cầu bài toán
- 💡 Visualization giúp người chơi hiểu rõ thuật toán

---

## 📋 SLIDE 12: Q&A (Dự phòng)

### ❓ Câu Hỏi Thường Gặp

**Q1: Tại sao không dùng A* thay vì BFS?**
- A: BFS đủ tốt cho grid nhỏ, không có heuristic phức tạp. A* sẽ hữu ích hơn cho map lớn hoặc có trọng số.

**Q2: Tại sao giới hạn 10 giây hiển thị?**
- A: Tránh spam helpers, khuyến khích người chơi suy nghĩ và tương tác.

**Q3: Stamina cost có cân bằng không?**
- A: Có, cost -30 và vĩnh viễn → người chơi phải sử dụng có chiến thuật.

**Q4: Game support bao nhiêu levels?**
- A: 9 levels với độ khó tăng dần (pieces: 4→9, fire spread tăng).

**Q5: Có thể thêm multiplayer không?**
- A: Có thể! Nhưng cần networking và sync state - đó là project mở rộng.

---

## 📚 TÀI LIỆU THAM KHẢO

### Source Code
- **Game:** [d:\\game_duyan\\GameSinhTon2D](file:///d:/game_duyan/GameSinhTon2D)
- **BFS/DFS Helper:** [helper.py](file:///d:/game_duyan/GameSinhTon2D/helper.py)
- **Main Game Loop:** [main.py](file:///d:/game_duyan/GameSinhTon2D/main.py)

### Thuật Toán
- Introduction to Algorithms (CLRS) - Chapter 22: Elementary Graph Algorithms
- Wikipedia: BFS, DFS
- GeeksforGeeks: Graph Traversal Algorithms

### Game Design
- Pygame Documentation: https://www.pygame.org/docs/
- Procedural Generation: Perlin Noise, Cellular Automata

---

## 🎤 CHUẨN BỊ THUYẾT TRÌNH

### Checklist Trước Khi Trình Bày

- [ ] Cài đặt Pygame: `pip install pygame`
- [ ] Test chạy game: `python main.py`
- [ ] Prepare backup: video recording hoặc screenshots
- [ ] Kiểm tra file nhạc nền (1.mp3, 2.mp3) đã có chưa
- [ ] Print slides hoặc chuẩn bị PDF
- [ ] Chuẩn bị pointer/laser để chỉ vào code

### Timeline Gợi Ý (10 phút)

| Thời gian | Nội dung | Slide |
|-----------|----------|-------|
| 0:00 - 1:00 | Giới thiệu | 1 |
| 1:00 - 3:00 | Tổng quan game | 2 |
| 3:00 - 5:00 | Giải thích BFS | 3 |
| 5:00 - 6:30 | Giải thích DFS | 4 |
| 6:30 - 8:00 | Ứng dụng #1, #2 | 5-6 |
| 8:00 - 9:00 | Ứng dụng #3, #4 | 7-8 |
| 9:00 - 10:00 | So sánh & Kết luận | 9, 11 |

### Tips Thuyết Trình

1. **Mở đầu mạnh mẽ:** "Game này không chỉ là entertainment - nó là minh chứng sống động cho thuật toán!"
2. **Sử dụng visual:** Chạy game live hoặc show screenshots/video
3. **Tương tác:** Hỏi khán giả: "Theo bạn nên dùng BFS hay DFS?"
4. **Nhấn mạnh:** BFS = shortest path, DFS = reachability
5. **Kết thúc:** Mời Q&A, thank you slide

---

## 🎯 MỤC TIÊU HỌC TẬP

Sau buổi thuyết trình, khán giả sẽ:

✅ Hiểu rõ cách BFS và DFS hoạt động  
✅ Phân biệt được khi nào dùng BFS, khi nào dùng DFS  
✅ Thấy ứng dụng thực tế của thuật toán trong game development  
✅ Có thể implement tương tự trong project của mình  

---

**Chúc bạn thuyết trình thành công! 🎉**
