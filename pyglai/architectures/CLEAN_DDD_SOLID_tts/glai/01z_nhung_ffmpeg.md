Để nhúng trực tiếp bản phân phối FFmpeg vào file thực thi độc lập (giúp người dùng cuối không cần cài đặt FFmpeg lên hệ điều hành), chúng ta cần tải bản binary của FFmpeg cho nền tảng tương ứng, cấu hình PyInstaller để đóng gói nó, và cập nhật mã nguồn ở tầng Infrastructure để tự động nhận diện đường dẫn chạy ngầm này.

Dưới đây là các bước triển khai chi tiết:

* * *

## 📥 Bước 1: Chuẩn bị Binary FFmpeg theo Hệ điều hành

Bạn cần tải file thực thi (binary) của FFmpeg phù hợp với hệ điều hành đang đóng gói:

  * Windows: Tải `ffmpeg.exe` (từ gyan.dev hoặc btb结构).
  * Linux/macOS: Tải file thực thi `ffmpeg` tương ứng.



Tạo một thư mục tên là `bin/` ở thư mục gốc của dự án và bỏ file thực thi vào đó:
    
    
    tts_cli_app/
    ├── bin/
    │   └── ffmpeg          # Hoặc ffmpeg.exe trên Windows
    

* * *

## ⚙️ Bước 2: Cập nhật Hàm Merge Audio ở lớp Infrastructure

Khi PyInstaller đóng gói ở chế độ `--onefile`, lúc chạy nó sẽ giải nén toàn bộ tài nguyên vào một thư mục tạm có tên biến môi trường là `_MEIPASS`. Chúng ta cần viết một hàm tiện ích để định vị chính xác file `ffmpeg` trong thư mục tạm này và cấu hình cho `pydub` nhận diện.

Triển khai file gộp Audio (`src/tts_app/infrastructure/audio/ffmpeg_merger.py`):
    
    
    import os
    import sys
    from pathlib import Path
    from pydub import AudioSegment
    from tts_app.interfaces.audio_merger import IAudioMerger  # Giả định đã định nghĩa interface tương ứng
    
    class FfmpegAudioMerger:
        def __init__(self):
            self._configure_ffmpeg_path()
    
        def _configure_ffmpeg_path(self):
            """Tự động định vị file FFmpeg dù chạy trong môi trường phát triển hay sau khi đóng gói."""
            if hasattr(sys, '_MEIPASS'):
                # Khi chạy từ file .exe/.app đã đóng gói bởi PyInstaller
                base_path = Path(sys._MEIPASS)
                ffmpeg_bin = base_path / "bin" / ("ffmpeg.exe" if os.name == 'nt' else "ffmpeg")
            else:
                # Khi chạy trong môi trường phát triển (Development)
                base_path = Path(__file__).resolve().parents[4]  # Đi ra ngoài thư mục gốc tts_cli_app
                ffmpeg_bin = base_path / "bin" / ("ffmpeg.exe" if os.name == 'nt' else "ffmpeg")
    
            if ffmpeg_bin.exists():
                # Ép buộc pydub sử dụng file thực thi FFmpeg đi kèm ứng dụng thay vì tìm trong hệ thống
                AudioSegment.converter = str(ffmpeg_bin)
            else:
                # Nếu không tìm thấy trong bộ nhúng, pydub sẽ tự động fallback tìm trong PATH hệ thống
                pass
    
        def merge(self, files: list[Path], output_path: Path) -> None:
            """Tiến hành nối chuỗi các file audio chunk thành một file duy nhất"""
            if not files:
                return
                
            try:
                # Khởi tạo đoạn âm thanh rỗng
                combined = AudioSegment.empty()
                
                # Đọc và cộng dồn các file chunk
                for file in files:
                    combined += AudioSegment.from_mp3(str(file))
                    
                # Xuất file kết quả chất lượng cao
                combined.export(str(output_path), format="mp3", bitrate="192k")
            except Exception as e:
                raise RuntimeError(f"Lỗi trong quá trình gộp file âm thanh bằng FFmpeg: {e}")
    

Cập nhật lại phương thức `_merge_files` trong Use Case (`src/tts_app/use_cases/process_tts.py`) để gọi `FfmpegAudioMerger`:
    
    
    # Trong src/tts_app/use_cases/process_tts.py
    from tts_app.infrastructure.audio.ffmpeg_merger import FfmpegAudioMerger
    
    # Thay vì tự xử lý pydub trực tiếp, hãy gọi qua Merger đã cấu hình đường dẫn ẩn:
    def _merge_files(self, files: list[Path], output: Path):
        merger = FfmpegAudioMerger()
        merger.merge(files, output)
    

* * *

## 🚀 Bước 3: Cập nhật Lệnh Đóng Gói PyInstaller

Chúng ta cần sử dụng tham số `--add-data` để yêu cầu PyInstaller copy thư mục `bin/` chứa FFmpeg vào bên trong file thực thi cuối cùng.

Cú pháp lệnh trên Linux/macOS:
    
    
    uv run pyinstaller --onefile \
        --name="tts" \
        --additional-hooks-dir=hooks \
        --add-data "bin:bin" \
        --hidden-import="click" \
        --hidden-import="edge_tts" \
        --hidden-import="google.cloud.texttospeech" \
        --hidden-import="pydub" \
        src/tts_app/main.py
    

Cú pháp lệnh trên Windows (Sử dụng dấu chấm phẩy `;` để phân tách nguồn và đích):
    
    
    uv run pyinstaller --onefile `
        --name="tts" `
        --additional-hooks-dir=hooks `
        --add-data "bin;bin" `
        --hidden-import="click" `
        --hidden-import="edge_tts" `
        --hidden-import="google.cloud.texttospeech" `
        --hidden-import="pydub" `
        src/tts_app/main.py
    

* * *

## 🎯 Kiểm tra kết quả

File thực thi `tts` (hoặc `tts.exe`) mới được sinh ra trong thư mục `dist/` bây giờ sẽ có dung lượng nặng hơn (do đã chứa cả phần lõi của FFmpeg bên trong).

Bạn có thể mang file này sang một máy tính hoàn toàn sạch (không có Python, không cài FFmpeg, không có thư viện chữ), chạy lệnh gộp âm thanh:
    
    
    ./tts convert ./truyen_ngan.txt --engine edge
    

Hệ thống sẽ tự động tách câu bằng thuật toán tối ưu ngữ cảnh, chuyển thành âm thanh qua Edge mạng, giải nén ngầm FFmpeg ra thư mục tạm để gộp các file chunk lại thành file `truyen_ngan_merged.mp3` mà không gặp bất kỳ lỗi hệ thống nào.

Nếu bạn muốn tối ưu thêm về giao diện hiển thị tiến trình (Progress Bar) bằng thư viện `rich` hoặc `tqdm` để người dùng thấy rõ tiến độ sinh audio theo từng chunk, hãy phản hồi lại cho tôi nhé!