Để đóng gói ứng dụng Python 3.15 quản lý bằng uv thành một file thực thi độc lập (Executable File) có thể chạy trên các máy tính khác mà không cần cài đặt Python, công cụ tối ưu nhất hiện nay là PyInstaller.

Tuy nhiên, do dự án sử dụng các thư viện xử lý ngôn ngữ tự nhiên đặc thù là `underthesea` và `spacy` (có chứa các file dữ liệu data model lớn và cấu trúc thư mục ngầm), việc đóng gói cần cấu hình chính xác để không bị lỗi thiếu file (`FileNotFoundError`) khi chạy.

Dưới đây là quy trình 3 bước đóng gói ứng dụng hoàn chỉnh:

* * *

## 📦 Bước 1: Cài đặt PyInstaller vào môi trường phát triển

Sử dụng `uv` để thêm `pyinstaller` vào nhóm công cụ phát triển (dev dependencies):
    
    
    uv add pyinstaller --dev
    

* * *

## ⚙️ Bước 2: Tạo tệp cấu hình đóng gói nâng cao (`hook-tts_app.py`)

Do `spacy` và `underthesea` tải dữ liệu ngầm từ thư mục cài đặt của chúng, bạn cần tạo một file hook để chỉ định PyInstaller gom toàn bộ file dữ liệu (data files) và các module ẩn (hidden imports) vào trong file thực thi.

Tạo một thư mục tên là `hooks/` ở thư mục gốc của dự án và tạo file `hooks/hook-spacy.py`:
    
    
    # hooks/hook-spacy.py
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules
    
    # Gom toàn bộ dữ liệu cấu trúc câu và gói ngôn ngữ của Spacy
    datas = collect_data_files('spacy') + collect_data_files('en_core_web_sm')
    hiddenimports = collect_submodules('spacy') + ['en_core_web_sm']
    

Tương tự, tạo file `hooks/hook-underthesea.py` để giữ lại dữ liệu phân tách từ tiếng Việt:
    
    
    # hooks/hook-underthesea.py
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules
    
    datas = collect_data_files('underthesea')
    hiddenimports = collect_submodules('underthesea')
    

* * *

## 🚀 Bước 3: Thực hiện lệnh đóng gói tổng lực

Chạy lệnh dưới đây trong Terminal của dự án để bắt đầu quá trình biên dịch. Lệnh này sử dụng môi trường ảo được quản lý tự động bởi `uv run`:
    
    
    uv run pyinstaller --onefile \
        --name="tts" \
        --additional-hooks-dir=hooks \
        --hidden-import="click" \
        --hidden-import="edge_tts" \
        --hidden-import="google.cloud.texttospeech" \
        --hidden-import="pydub" \
        src/tts_app/main.py
    

Giải thích ý nghĩa các tham số:

  * `--onefile`: Nén toàn bộ mã nguồn, thư viện, gói ngôn ngữ và môi trường Python 3.15 vào đúng 1 file thực thi duy nhất.
  * `--name="tts"`: Đặt tên cho file xuất ra là `tts` (hoặc `tts.exe` trên Windows).
  * `--additional-hooks-dir=hooks`: Yêu cầu PyInstaller đọc các file cấu hình bổ sung cho `spacy` và `underthesea` mà ta vừa tạo ở Bước 2.
  * `--hidden-import`: Ép buộc hệ thống đóng gói các thư viện động mà Click hoặc Google API gọi ngầm.



* * *

## 📂 Kết quả đầu ra

Sau khi tiến trình chạy xong, bạn sẽ thấy xuất hiện 2 thư mục mới:

  1. `build/`: Chứa các tệp tạm trong quá trình biên dịch (bạn có thể xóa sau khi hoàn thành).
  2. `dist/`: Nơi chứa file thực thi cuối cùng. Tại đây bạn sẽ thấy file `tts` (Linux/macOS) hoặc `tts.exe` (Windows).



## 🛠️ Cách sử dụng file sau khi đóng gói

Bây giờ bạn có thể sao chép file `tts` từ thư mục `dist/` ra bất kỳ vị trí nào hoặc gửi cho người khác sử dụng trực tiếp thông qua Terminal/CMD mà không cần gõ chữ `uv run` nữa:
    
    
    # Xem danh sách engine trực tiếp từ file thực thi
    ./tts engine list
    
    # Chuyển đổi file văn bản bằng file thực thi độc lập
    ./tts convert ./document.txt --engine edge --chunk-size 1800
    

Nếu bạn muốn tôi cấu hình thêm phần tự động phát hiện và nhúng các file thực thi của FFmpeg vào trong ứng dụng để việc gộp file audio (merge) không phụ thuộc vào việc máy tính client có cài FFmpeg hay chưa, hãy cho tôi biết nhé!