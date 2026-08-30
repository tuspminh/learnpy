Nếu bạn muốn ưu tiên xuất ra định dạng webm thay vì mp4 hay mkv, bạn chỉ cần sửa lại dòng cấu hình đó trong file `config.txt` thành:
    
    
    # Tự động gộp video và audio thành định dạng webm
    --merge-output-format webm
    

## Một số lưu ý quan trọng khi dùng định dạng WEBM:

  * Chất lượng gốc: Thường thì các video 2K/4K/8K trên YouTube được lưu trữ gốc bằng codec video VP9/AV1 và codec âm thanh Opus. Định dạng `.webm` là "thùng chứa" hoàn hảo cho các codec này, giúp bạn giữ nguyên chất lượng gốc mà không cần convert (chuyển mã), giúp tốc độ tải và gộp file cực kỳ nhanh.
  * Khả năng tương thích: Webm xem rất mượt trên các trình duyệt web (Chrome, Edge, Firefox) và các phần mềm xem phim phổ biến (VLC, PotPlayer). Tuy nhiên, một số thiết bị cũ hoặc ứng dụng chỉnh sửa video (như CapCut bản cũ, Premiere Pro) có thể sẽ không mở được trực tiếp file webm.



## Gợi ý cấu hình tối ưu nhất cho WEBM:

Nếu mục tiêu của bạn là luôn lấy file `.webm` chất lượng cao nhất, bạn nên cập nhật lại file `config.txt` với nội dung sau:
    
    
    # Ép buộc sử dụng Deno làm JS Runtime để tránh lỗi thuật toán YouTube
    --js-runtimes deno
    
    # Ưu tiên tải video định dạng webm chất lượng cao nhất, nếu không có mới lấy định dạng khác
    -f "bv*[ext=webm]+ba*[ext=webm]/bv+ba/b"
    
    # Tự động gộp video và audio thành định dạng webm
    --merge-output-format webm
    
    # Lưu video vào thư mục Downloads của Windows
    -o "~/Downloads/%(title)s.%(ext)s"
    

Bạn có muốn cấu hình thêm tính năng tự động tải phụ đề (subtitles) đi kèm với file webm này luôn không?