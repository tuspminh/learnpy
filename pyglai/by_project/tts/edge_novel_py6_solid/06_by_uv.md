Nếu bạn đang sử dụng `uv` (công cụ quản lý Python cực nhanh của Astral), quy trình cài đặt và đóng gói sẽ nhanh hơn gấp nhiều lần, nhưng bản chất câu lệnh đóng gói của `pyinstaller` thì vẫn giữ nguyên.

Dưới đây là cách thực hiện chuẩn nhất bằng `uv`:

## Bước 1: Tạo môi trường ảo và cài đặt thư viện bằng `uv`

Tại thư mục chứa file `app.py`, bạn chạy cụm lệnh sau. `uv` sẽ tự động tạo môi trường ảo và cài đặt tất cả các thư viện chỉ trong vòng 1-2 giây:
    
    
    # Tạo môi trường ảo .venv
    uv venv
    
    # Kích hoạt môi trường ảo (Windows)
    .venv\Scripts\activate
    
    # Cài đặt toàn bộ thư viện cần thiết bằng uv
    uv pip install PySide6 edge-tts pyinstaller
    

## Bước 2: Chạy lệnh đóng gói

Sau khi đã cài đặt xong các thư viện vào môi trường ảo, bạn dùng lệnh `pyinstaller` như bình thường để đóng gói file:
    
    
    pyinstaller --noconsole --onefile --name="EdgeTTS_StoryReader" app.py
    

## 💡 Cách thay thế: Đóng gói siêu tốc không cần kích hoạt môi trường ảo (`uv run`)

Nếu bạn muốn tận dụng tính năng chạy app trực tiếp trong môi trường cô lập của `uv` mà không cần cài đặt thủ công hay kích hoạt môi trường `.venv`, bạn có thể chạy duy nhất một dòng lệnh này (áp dụng cho phiên bản `uv` mới):
    
    
    uv run --with PySide6 --with edge-tts --with pyinstaller pyinstaller --noconsole --onefile --name="EdgeTTS_StoryReader" app.py
    

_Lệnh này sẽ tự động tải các công cụ về bộ nhớ đệm (cache), đóng gói file`app.py` thành `.exe`, sau đó trả lại môi trường sạch sẽ cho máy tính của bạn._

Sau khi chạy xong, file `.exe` thành phẩm vẫn nằm trong thư mục `dist` như bình thường. Bạn có thể copy file đó ra và sử dụng ngay lập tức.