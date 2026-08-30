Để cài đặt và cấu hình Deno làm trình chạy JavaScript cho `yt-dlp` trên Windows, bạn làm theo 2 bước cực kỳ đơn giản sau:

## 1\. Cách cài đặt Deno nhanh nhất

Bạn mở CMD hoặc PowerShell (không cần quyền Admin) và chạy duy nhất lệnh sau để cài đặt qua Winget có sẵn của Windows:
    
    
    winget install Deno.Deno
    

> Lưu ý quan trọng: Sau khi chạy lệnh xong, bạn phải tắt cửa sổ CMD/PowerShell hiện tại đi và mở lại một cửa sổ mới để hệ thống cập nhật đường dẫn (PATH) của Deno.

## 2\. Cấu hình để yt-dlp nhận diện Deno

Thực tế, `yt-dlp` tự động nhận diện Deno ngay khi bạn cài đặt xong mà không cần cấu hình gì thêm.

Nếu bạn muốn chắc chắn hoặc muốn ép buộc `yt-dlp` luôn luôn sử dụng Deno, hãy thêm tham số `--js-runtimes deno` vào cuối câu lệnh tải của bạn.

Ví dụ câu lệnh hoàn chỉnh:
    
    
    yt-dlp --js-runtimes deno -f "bv+ba/b" https://youtube.com
    

Khi chạy lệnh này, dòng cảnh báo `WARNING: No supported JavaScript runtime could be found` sẽ biến mất hoàn toàn, giúp bạn lấy được đầy đủ các định dạng video chất lượng cao nhất.

Nếu bạn muốn tạo một file cấu hình cố định để không phải gõ lại tham số này mỗi lần tải, hãy cho tôi biết để tôi hướng dẫn cách làm nhé!