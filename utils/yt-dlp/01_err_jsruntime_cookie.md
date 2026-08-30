Để xử lý triệt để hai cảnh báo trên hệ điều hành Windows, bạn hãy thực hiện nhanh các bước sau:

## 1\. Sửa lỗi JavaScript Runtime (Sửa lỗi mất định dạng video)

YouTube yêu cầu một trình chạy JS để giải mã thuật toán. Hãy cài đặt Node.js hoặc Deno để `yt-dlp` tự động nhận diện:

  * Cách nhanh nhất (Dùng Winget có sẵn trên Windows):

    1. Bấm phím `Windows`, gõ cmd, chuột phải chọn Run as administrator.
    2. Copy và chạy lệnh sau:
           
           winget install OpenJS.NodeJS
           

    3. Khởi động lại cửa sổ CMD/Terminal để áp dụng thay đổi.




## 2\. Sửa lỗi Cookies hết hạn (Tránh bị YouTube chặn)

YouTube liên tục làm mới mã bảo mật khiến file cookies cũ bị vô hiệu hóa.

  * Nếu video công khai: Bạn hãy xóa bỏ tham số `--cookies` hoặc `--cookies-from-browser` ra khỏi câu lệnh của mình. Không dùng cookies sẽ giúp lệnh chạy mượt mà và an toàn hơn.
  * Nếu bắt buộc phải dùng cookies (Video riêng tư/Giới hạn độ tuổi): Bạn cần mở trình duyệt, đăng xuất rồi đăng nhập lại YouTube, sau đó xuất lại file cookie mới để thay thế file cũ.



* * *

## Gợi ý các lệnh tải video tối ưu trên Windows

Dưới đây là một số câu lệnh chuẩn, không cần dùng cookies (đã tích hợp sẵn bộ gộp video/âm thanh `ffmpeg`):

  * Tải video chất lượng cao nhất (Tự động gộp Video + Audio chất lượng cao):
        
        yt-dlp -f "bv+ba/b" https://youtube.com
        

  * Chỉ tải âm thanh (Chuyển thành file MP3 chất lượng cao 320kbps):
        
        yt-dlp -x --audio-format mp3 --audio-quality 0 https://youtube.com
        




Nếu bạn gặp khó khăn trong quá trình cài đặt Node.js hoặc muốn thiết lập tự động tải toàn bộ Playlist, hãy phản hồi để tôi hướng dẫn chi tiết nhé!