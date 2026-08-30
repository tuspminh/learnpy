Để tạo file cấu hình cố định cho `yt-dlp` trên Windows, giúp phần mềm luôn tự động sử dụng Deno và tự tối ưu chất lượng tải mà không cần gõ lại lệnh dài, bạn làm như sau:

## 1\. Tạo file cấu hình

  1. Bấm tổ hợp phím `Windows + R`, nhập `notepad` và nhấn Enter để mở Notepad.
  2. Sao chép và dán toàn bộ nội dung cấu hình chuẩn dưới đây vào:


    
    
    # Ép buộc sử dụng Deno làm JS Runtime để tránh lỗi thuật toán YouTube
    --js-runtimes deno
    
    # Tự động chọn chất lượng Video + Audio tốt nhất
    -f "bv+ba/b"
    
    # Tự động gộp video và audio thành định dạng mkv hoặc mp4 phổ biến
    --merge-output-format mkv/mp4
    
    # Lưu video vào thư mục Downloads của Windows (Tùy chỉnh nếu muốn)
    -o "~/Downloads/%(title)s.%(ext)s"
    

## 2\. Lưu file vào đúng vị trí hệ thống

Để `yt-dlp` tự nhận diện file này mỗi khi chạy, bạn phải lưu nó vào thư mục cấu hình của người dùng:

  1. Trong Notepad, chọn File > Save As...
  2. Tại mục Save as type, bạn bắt buộc phải chọn là All Files (_._).
  3. Tại mục File name, bạn nhập chính xác tên: `config.txt`
  4. Ở thanh địa chỉ phía trên, bạn xóa đường dẫn cũ đi, dán đoạn mã sau vào và nhấn Enter:
         
         %APPDATA%\yt-dlp
         

_(Nếu hệ thống báo lỗi không tìm thấy thư mục, bạn hãy lưu tạm file`config.txt` ra Desktop, sau đó bấm `Windows + R`, gõ `%APPDATA%`, tạo một thư mục mới tên là `yt-dlp` rồi kéo file vào đó)._
  5. Nhấn Save.



## 3\. Kiểm tra kết quả

Bây giờ, file cấu hình đã hoạt động. Từ lần này trở đi, mỗi khi muốn tải video, bạn chỉ cần mở CMD và gõ lệnh siêu ngắn gọn:
    
    
    yt-dlp https://youtube.com
    

`yt-dlp` sẽ tự động gọi Deno, tự tải chất lượng cao nhất và lưu thẳng vào thư mục Downloads của bạn mà không còn bất kỳ dòng cảnh báo nào.

Nếu bạn muốn tùy chỉnh thêm như tự động tải phụ đề (subtitles) hoặc chuyển đổi file sang MP3, hãy cho tôi biết để tôi bổ sung vào file cấu hình nhé!