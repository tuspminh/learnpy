Dưới đây là nội dung tài liệu hướng dẫn nhanh (README.md) được viết ngắn gọn, trực quan và scannable để bạn đính kèm chung với file `.exe` hoặc mã nguồn. Người dùng chỉ cần nhìn qua là biết cách gõ lệnh ngay lập tức.

* * *

## 📘 Edge-TTS Audiobook Studio CLI

Bộ công cụ dòng lệnh (CLI) chuyên nghiệp hỗ trợ dọn dẹp văn bản văn học, tự động chia nhỏ (chunking 2500 ký tự) và chuyển đổi thành truyện audio chất lượng cao bằng AI Neural Voices.

* * *

## 🚀 Tính năng nổi bật

  * Chuẩn hóa văn bản (`--normalize`): Tự động sửa lỗi dấu câu dính liền, viết hoa đầu câu sau dấu `. ! ?` giúp AI lấy hơi và ngắt nghỉ tự nhiên.
  * Xử lý file lớn: Tự động băm văn bản thành các khối nhỏ dưới 2500 ký tự để tránh giới hạn API, sau đó tự động gộp (merge) thành file MP3 hoàn chỉnh.
  * Chế độ hàng loạt: Hỗ trợ quét toàn bộ một thư mục chứa nhiều file `.txt` và xuất ra các file âm thanh tương ứng độc lập.



* * *

## 📥 Yêu cầu hệ thống (Yêu cầu bắt buộc)

Để tính năng gộp file âm thanh hoạt động không bị lỗi, máy tính của bạn phải cài đặt FFmpeg và thêm vào biến môi trường `PATH` của hệ thống.

  * Cách cài nhanh qua Scoop (Windows): `scoop install ffmpeg`
  * Cách cài nhanh qua Chocolatey (Windows): `choco install ffmpeg`



* * *

## 💻 Hướng dẫn sử dụng chi tiết

## 1\. Cú pháp câu lệnh cơ bản
    
    
    # Nếu chạy bằng mã nguồn Python:
    uv run cli_app.py [ĐƯỜNG_DẪN_INPUT] [CÁC_THAM_SỐ]
    
    # Nếu chạy bằng file .exe đã đóng gói:
    story-tts.exe [ĐƯỜNG_DẪN_INPUT] [CÁC_THAM_SỐ]
    

## 2\. Các tham số cấu hình (Options)

  * `-o, --output TEXT`: Đường dẫn file MP3 đích (nếu chọn 1 file) hoặc thư mục lưu MP3 (nếu chọn folder).
  * `-p, --preset [co-tich|kinh-di|ngon-tinh|kiem-hiep|mac-dinh]`: Áp dụng cấu hình Rate/Pitch tối ưu có sẵn cho từng thể loại truyện.
  * `-r, --rate TEXT`: Tốc độ đọc tự do (Ví dụ: `-10%`, `+5%`). _Bị bỏ qua nếu dùng`--preset`_.
  * `-pi, --pitch TEXT`: Cao độ giọng tự do (Ví dụ: `-3Hz`, `+2Hz`). _Bị bỏ qua nếu dùng`--preset`_.
  * `-v, --voice TEXT`: Mã giọng đọc từ hệ thống Edge-TTS. _(Mặc định:`en-US-AriaNeural`)_.
  * `--normalize`: Bật cờ tự động sửa lỗi dấu câu và viết hoa văn bản gốc trước khi chuyển audio.



* * *

## 💡 Các câu lệnh mẫu thực tế hay dùng

Ví dụ 1: Đọc 1 file truyện cổ tích Tiếng Anh, tự dọn sạch lỗi text đầu vào
    
    
    story-tts.exe story.txt --preset co-tich --voice en-US-JennyNeural --normalize -o output.mp3
    

Ví dụ 2: Đọc 1 file truyện kinh dị Tiếng Việt trầm hùng, tự cấu hình tốc độ thủ công
    
    
    story-tts.exe ghost.txt --rate "-16%" --pitch "-4Hz" --voice vi-VN-NamMinhNeural -o ghost_story.mp3
    

Ví dụ 3: Xử lý hàng loạt toàn bộ thư mục chứa nhiều chương truyện ngắn
    
    
    story-tts.exe ./my_chapters_folder/ --preset ngon-tinh --voice vi-VN-HoaiAnNeural --normalize -o ./audio_outputs/
    

* * *

## 🛠 Bảng danh sách giọng đọc kể chuyện khuyên dùng

Mã Giọng (`--voice`)| Ngôn ngữ| Đặc trưng phong cách  
---|---|---  
`en-US-AriaNeural`| Tiếng Anh (Mỹ)| Giọng nữ quốc dân, truyền cảm xúc cực mượt  
`en-US-JennyNeural`| Tiếng Anh (Mỹ)| Giọng nữ trong trẻo, rất hợp cổ tích thần thoại  
`en-US-GuyNeural`| Tiếng Anh (Mỹ)| Giọng nam trầm ấm, kể chuyện tự sự có chiều sâu  
`en-GB-SoniaNeural`| Tiếng Anh (Anh)| Giọng nữ sang trọng, mang phong cách hoàng gia  
`vi-VN-HoaiAnNeural`| Tiếng Việt| Giọng nữ miền Nam dịu dàng, hợp ngôn tình, tâm lý  
`vi-VN-NamMinhNeural`| Tiếng Việt| Giọng nam miền Bắc trầm hùng, hợp kiếm hiệp, tiên hiệp  
  
* * *

Chúc bạn thiết lập và sử dụng bộ công cụ này thành công! Nếu cần tùy biến thêm bất kỳ tính năng nào khác (như tự động thêm nhạc nền, chèn khoảng nghỉ giữa các chương...), hãy cho tôi biết nhé.