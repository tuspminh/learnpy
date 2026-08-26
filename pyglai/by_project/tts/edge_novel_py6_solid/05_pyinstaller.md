Để đóng gói code PySide6 + edge-tts thành một file `.exe` chạy độc lập (chạy được trên máy tính khác mà không cần cài Python), công cụ tốt nhất và ổn định nhất là PyInstaller.

Dưới đây là các bước thực hiện chi tiết:

## Bước 1: Cài đặt PyInstaller

Bạn mở Terminal / Command Prompt lên và chạy lệnh sau để cài đặt phiên bản PyInstaller mới nhất:
    
    
    pip install pyinstaller
    

## Bước 2: Chuẩn bị file code

Hãy đảm bảo đoạn code PySide6 ở bước trước đã được lưu thành một file có tên rõ ràng, ví dụ: `app.py`. Bạn nên copy file `app.py` này vào một thư mục trống riêng biệt để tránh đóng gói nhầm các file không liên quan.

## Bước 3: Chạy lệnh đóng gói

Tại cửa sổ Terminal, bạn dùng lệnh `cd` để di chuyển vào thư mục chứa file `app.py`. Sau đó, chạy lệnh đóng gói tối ưu sau:
    
    
    pyinstaller --noconsole --onefile --name="EdgeTTS_StoryReader" app.py
    

Giải thích các tham số trong câu lệnh:

  * `--noconsole`: Ẩn cửa sổ dòng lệnh màu đen (cmd) khi phần mềm chạy, chỉ hiển thị duy nhất giao diện đồ họa PySide6 của bạn.
  * `--onefile`: Gom tất cả thư viện, mã nguồn và các file phụ thuộc vào duy nhất 1 file `.exe` để bạn dễ dàng gửi cho người khác.
  * `--name="EdgeTTS_StoryReader"`: Đặt tên cho file `.exe` sau khi xuất bản.



## Bước 4: Lấy file `.exe` thành phẩm

Sau khi PyInstaller chạy xong (thường mất khoảng 1-2 phút tùy cấu hình máy), trong thư mục của bạn sẽ xuất hiện thêm một số thư mục mới.

Bạn hãy vào thư mục `dist`, tại đây bạn sẽ tìm thấy file `EdgeTTS_StoryReader.exe`. Bạn chỉ cần copy duy nhất file này mang sang các máy tính Windows khác là có thể click đúp chạy ngay lập tức.

* * *

## 💡 Mẹo nâng cao: Thêm Icon tùy chỉnh cho phần mềm

Nếu bạn muốn file `.exe` của mình có biểu tượng (icon) đẹp mắt thay vì icon mặc định của Windows, bạn chỉ cần chuẩn bị một file hình ảnh định dạng `.ico` (ví dụ: `app_icon.ico`) đặt chung thư mục với file code, sau đó thêm tham số `--icon` vào lệnh chạy:
    
    
    pyinstaller --noconsole --onefile --icon=app_icon.ico --name="EdgeTTS_StoryReader" app.py
    

Nếu trong quá trình đóng gói bạn gặp bất kỳ thông báo lỗi (Error) nào từ PyInstaller, hãy copy đoạn lỗi đó gửi lên đây để tôi hỗ trợ bạn xử lý nhé!