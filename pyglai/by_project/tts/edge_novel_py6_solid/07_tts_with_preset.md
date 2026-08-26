Để tạo ra file âm thanh đọc truyện chuyên nghiệp, nhịp điệu (Rate) và độ trầm bổng (Pitch) đóng vai trò quyết định cảm xúc. Đối với `edge-tts`, giọng tiếng Anh (Neural) xử lý biến điệu cực tốt, trong khi giọng tiếng Việt (HoaiAn, NamMinh) cần tinh chỉnh kỹ hơn để tránh bị đều đều như đọc tin tức.

Dưới đây là các bảng thông số Preset (Cấu hình sẵn) tối ưu cho từng thể loại truyện để bạn cấu hình vào mã nguồn:

## 1\. Preset cho Truyện Tiếng Anh (English Stories)

Thể loại truyện| Giọng đọc khuyên dùng| Tốc độ (`rate`)| Cao độ (`pitch`)| Đặc trưng phong cách  
---|---|---|---|---  
Cổ tích / Thần thoại  
 _(Fairy Tales / Myths)_| `en-US-JennyNeural` (Nữ)  
`en-GB-SoniaNeural` (Nữ)| `-12%` đến `-15%`| `+2Hz` đến `+4Hz`| Giọng đọc chậm rãi, trong trẻo, hơi cao nhẹ để tạo cảm giác phép thuật, mơ màng.  
Kinh dị / Trinh thám  
 _(Horror / Thriller)_| `en-US-GuyNeural` (Nam)  
`en-US-SteffanNeural` (Nam)| `-15%` đến `-18%`| `-3Hz` đến `-5Hz`| Đọc rất chậm, hạ thấp tông giọng xuống trầm sâu để tạo không khí u ám, kịch tính, hồi hộp.  
Tiểu thuyết / Tâm lý  
 _(Drama / Romance)_| `en-US-AriaNeural` (Nữ)  
`en-GB-RyanNeural` (Nam)| `-8%` đến `-10%`| `0Hz` (Mặc định)| Nhịp điệu thong thả, giữ nguyên tông giọng tự nhiên để tập trung vào biểu cảm nội tâm nhân vật.  
Truyện Ngụ ngôn / Thiếu nhi  
 _(Fables / Kids)_| `en-US-JennyNeural` (Nữ)| `-5%` đến `-8%`| `+5Hz` đến `+8Hz`| Tốc độ vừa phải, nâng cao độ lên hẳn để tạo sự vui tươi, hóm hỉnh, thu hút trẻ nhỏ.  
  
* * *

## 2\. Preset cho Truyện Tiếng Việt

 _Lưu ý: Giọng AI tiếng Việt có xu hướng đọc hơi nhanh và đều đều, vì vậy bắt buộc phải giảm tốc độ sâu hơn tiếng Anh để nghe tự nhiên._

Thể loại truyện| Giọng đọc khuyên dùng| Tốc độ (`rate`)| Cao độ (`pitch`)| Đặc trưng phong cách  
---|---|---|---|---  
Ngôn tình / Tâm lý xã hội| `vi-VN-HoaiAnNeural` (Nữ)| `-15%` đến `-18%`| `-1Hz` đến `-2Hz`| Ép tốc độ chậm lại, hạ nhẹ tông để giọng Hoài An trở nên ấm áp, dịu dàng, hợp truyện sướt mướt.  
Kiếm hiệp / Tiên hiệp / Linh dị| `vi-VN-NamMinhNeural` (Nam)| `-12%` đến `-15%`| `-2Hz` đến `-4Hz`| Giọng Nam Minh trầm, khi hạ pitch sẽ tạo độ vang, uy lực, rất hợp để mô tả chiêu thức hoặc cảnh u ám.  
Truyện cười / Trinh thám hiện đại| `vi-VN-NamMinhNeural` (Nam)  
`vi-VN-HoaiAnNeural` (Nữ)| `-8%` đến `-10%`| `0Hz` (Mặc định)| Giữ nhịp đọc vừa phải để người nghe kịp bắt trend, theo dõi các tình tiết phá án hoặc mảng miếng hài.  
  
* * *

## 3\. Cách cập nhật Danh mục Preset này vào Code PySide6 của bạn

Để phần mềm có thêm tính năng chọn thể loại truyện (Tự động áp thông số Rate/Pitch), bạn có thể cập nhật cấu trúc Code như sau:

Bước 1: Khai báo Dictionary chứa cấu hình thể loại
    
    
    STORY_GENRES = {
        "Cổ tích / Thiếu nhi": {"rate": "-12%", "pitch": "+3Hz"},
        "Kinh dị / Trinh thám": {"rate": "-16%", "pitch": "-4Hz"},
        "Ngôn tình / Tâm lý": {"rate": "-15%", "pitch": "-1Hz"},
        "Kiếm hiệp / Tiên hiệp": {"rate": "-13%", "pitch": "-3Hz"},
        "Phổ thông / Tin tức": {"rate": "+0%", "pitch": "+0Hz"},
    }
    

Bước 2: Thêm một QComboBox chọn thể loại vào Giao diện (GUI)
    
    
    # Trong hàm __init__ của giao diện:
    vbox_genre = QVBoxLayout()
    vbox_genre.addWidget(QLabel("Thể loại truyện (Preset):"))
    self.genre_combo = QComboBox()
    self.genre_combo.addItems(list(STORY_GENRES.keys()))
    vbox_genre.addWidget(self.genre_combo)
    config_layout.addLayout(vbox_genre) # Thêm vào khung cấu hình
    

Bước 3: Truyền tham số `pitch` vào hàm `edge_tts.Communicate`
    
    
    # Trong hàm start_conversion hoặc Worker Thread:
    selected_genre = self.genre_combo.currentText()
    preset = STORY_GENRES[selected_genre]
    
    # Gọi edge-tts với cả 2 tham số rate và pitch từ preset
    communicate = edge_tts.Communicate(
        text=text, 
        voice=voice_code, 
        rate=preset["rate"], 
        pitch=preset["pitch"]
    )
    

Bạn có muốn tôi viết lại toàn bộ file code PySide6 hoàn chỉnh tích hợp sẵn menu chọn Thể loại truyện (Preset) tự động này để bạn copy đè lên file cũ không?