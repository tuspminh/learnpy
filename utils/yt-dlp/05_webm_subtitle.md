Để tự động tải thêm phụ đề (subtitles) đi kèm với file video `.webm`, bạn hãy cập nhật lại file `config.txt` theo hướng dẫn dưới đây.

## 1\. Cập nhật nội dung file `config.txt`

Bạn mở lại file `config.txt` (nằm ở đường dẫn `%APPDATA%\yt-dlp\config.txt`) và dán toàn bộ đoạn cấu hình tối ưu này vào để thay thế cấu hình cũ:
    
    
    # Ép buộc sử dụng Deno làm JS Runtime để tránh lỗi thuật toán YouTube
    --js-runtimes deno
    
    # Ưu tiên tải video định dạng webm chất lượng cao nhất
    -f "bv*[ext=webm]+ba*[ext=webm]/bv+ba/b"
    
    # Tự động gộp video và audio thành định dạng webm
    --merge-output-format webm
    
    # Lưu video vào thư mục Downloads của Windows
    -o "~/Downloads/%(title)s.%(ext)s"
    
    # CẤU HÌNH PHỤ ĐỀ (SUBTITLES)
    # Tự động tải file phụ đề nếu có phụ đề do người dùng dịch (human-created)
    --write-subs
    
    # Tự động tải phụ đề do YouTube tự dịch (auto-generated) nếu không có phụ đề gốc
    --write-auto-subs
    
    # Ưu tiên tải phụ đề tiếng Việt (vi), nếu không có thì lấy tiếng Anh (en)
    --sub-langs "vi,en"
    
    # Nhúng trực tiếp phụ đề vào trong file .webm (Bật/tắt được khi xem bằng VLC/PotPlayer)
    --embed-subs
    

## 2\. Cách hoạt động sau khi cấu hình

  * Xem bằng phần mềm (VLC, PotPlayer): Phụ đề đã được nhúng thẳng vào trong file `.webm`. Khi xem, bạn chỉ cần nhấn chuột phải vào màn hình video, chọn mục Subtitle để bật/tắt hoặc chuyển đổi giữa tiếng Việt và tiếng Anh.
  * Nếu muốn xuất file phụ đề rời (.srt hoặc .vtt): Nếu bạn không muốn nhúng phụ đề vào video mà muốn nó nằm thành một file riêng biệt bên cạnh file video, hãy xóa dòng `--embed-subs` trong file cấu hình đi là được.



Bây giờ bạn chỉ cần mở CMD và chạy lệnh ngắn gọn `yt-dlp [link_video]` để tận hưởng thành quả. Bạn có cần hỗ trợ thêm về cách tải hàng loạt video từ một playlist hay tính năng nào khác không?