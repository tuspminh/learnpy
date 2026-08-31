Để thay thế hoàn toàn thư viện `pydub` (vốn phụ thuộc vào command-line của FFmpeg) bằng một giải pháp Python thuần thông qua các ràng buộc C của FFmpeg, `PyAV` là sự lựa chọn tối ưu nhất.

Khi làm việc với `PyAV` để merge âm thanh từ các chunk khác nhau, việc đồng bộ Sample Rate (Tần số lấy mẫu), Layout (Số kênh) và Format (Định dạng mẫu) là bắt buộc để file output không bị méo tiếng, giật tiếng, hoặc lỗi đồng bộ thời gian (`pts`).

Dưới đây là module hạ tầng xử lý việc gộp file sử dụng lớp `av.AudioResampler` và cấu trúc tính toán thời gian `pts` chuẩn theo thiết kế DDD / SOLID. [1] 

## 1\. Cài đặt thư viện bằng `uv`

Bạn cần cài đặt thư viện `av` vào môi trường của mình:
    
    
    uv pip install av
    

## 2\. Cập nhật mã nguồn lớp Hạ tầng (`infrastructure/audio_merger.py`)

Trong kiến trúc SOLID, lớp này sẽ triển khai lại Interface `IAudioMerger` đã định nghĩa trước đó. Thuật toán sử dụng một cấu hình đầu ra đích (Target: `44100Hz`, `Stereo`, `s16` format) để ép toàn bộ các file chunk đầu vào (dù có khác biệt sample rate) về cùng một hệ quy chiếu đồng bộ trước khi ghi vào container.
    
    
    import os
    from typing import List
    import av
    from domain.interfaces import IAudioMerger
    
    class PyAVAudioMerger(IAudioMerger):
        def merge_mp3_files(self, src_paths: List[str], dest_path: str) -> None:
            """
            Gộp các file âm thanh tạm thời thành một file duy nhất bằng PyAV.
            Tự động resample đồng bộ sample rate, layout và format của toàn bộ chunk.
            """
            if not src_paths:
                return
    
            # 1. Cấu hình thông số đầu ra chuẩn cố định cho Audiobook
            TARGET_RATE = 44100      # 44.1 kHz chuẩn CD
            TARGET_LAYOUT = "stereo"  # 2 Kênh (Stereo)
            TARGET_FORMAT = "s16p"    # Kênh phẳng 16-bit signed (Phù hợp mã hóa MP3)
            TARGET_CODEC = "mp3"
    
            # 2. Khởi tạo Container đầu ra để ghi dữ liệu
            output_container = av.open(dest_path, mode="w", format="mp3")
            
            # Thêm một stream âm thanh vào container đầu ra
            out_stream = output_container.add_stream(TARGET_CODEC, rate=TARGET_RATE)
            out_stream.layout = TARGET_LAYOUT
            out_stream.format = TARGET_FORMAT
    
            # Khởi tạo bộ chuyển đổi tần số (Resampler) của FFmpeg
            resampler = av.AudioResampler(
                format=TARGET_FORMAT,
                layout=TARGET_LAYOUT,
                rate=TARGET_RATE
            )
    
            current_pts = 0  # Biến theo dõi dòng thời gian (Presentation Timestamp) để nối tiếp liên tục
    
            try:
                for path in src_paths:
                    if not os.path.exists(path):
                        continue
    
                    # Mở từng file chunk đầu vào để giải mã
                    with av.open(path, mode="r") as input_container:
                        # Lấy stream audio đầu tiên của file chunk
                        in_stream = input_container.streams.audio[0]
    
                        # Duyệt qua từng gói dữ liệu (packet) trong stream
                        for packet in input_container.demux(in_stream):
                            # Giải mã packet thành các khung âm thanh (AudioFrame)
                            for frame in packet.decode():
                                
                                # Thực hiện đồng bộ Sample Rate / Layout / Format thông qua Resampler
                                resampled_frames = resampler.resample(frame)
                                
                                # Nếu resampler trả về dữ liệu (có thể gom nhiều frame nhỏ thành lớn)
                                if resampled_frames:
                                    # Tính toán chính xác thời gian hiển thị PTS để tránh âm thanh bị đè hoặc ngắt quãng
                                    resampled_frames.pts = current_pts
                                    resampled_frames.time_base = out_stream.time_base
                                    
                                    # Tăng tiến PTS dựa trên số lượng mẫu đã ghi vào hệ thống
                                    current_pts += resampled_frames.samples
    
                                    # Mã hóa khung âm thanh đã chuẩn hóa thành packet đầu ra
                                    for out_packet in out_stream.encode(resampled_frames):
                                        output_container.mux(out_packet)
    
                # 3. Flush encoder: Giải phóng nốt dữ liệu còn sót lại trong hàng đợi của encoder
                for out_packet in out_stream.encode(None):
                    output_container.mux(out_packet)
    
            finally:
                # Luôn đóng container để lưu file xuống ổ đĩa an toàn
                output_container.close()
    

## 3\. Cập nhật file Khởi chạy (`main.py`)

Để hệ thống chuyển sang dùng module `PyAV` thay thế cho `pydub`, bạn chỉ cần thay đổi duy nhất dòng khai báo đối tượng hạ tầng kỹ thuật trong file Composition Root (`main.py`). Đúng tinh thần của nguyên tắc D (Dependency Inversion), toàn bộ giao diện GUI hay logic Application sẽ không phải sửa bất kỳ dòng code nào.
    
    
    import sys
    from PySide6.QtWidgets import QApplication
    from infrastructure.tts_service import EdgeTTSService
    from infrastructure.audio_merger import PyAVAudioMerger  # <--- Thay đổi ở đây
    from infrastructure.file_repository import LocalFileRepository
    from application.tts_orchestrator import TTSOrchestrator
    from presentation.main_window import MainWindow
    
    def main():
        app = QApplication(sys.argv)
        
        # 1. Khởi tạo các Module hạ tầng kỹ thuật
        tts_service = EdgeTTSService()
        audio_merger = PyAVAudioMerger()  # <--- Khởi tạo đối tượng PyAV mới thay cho Pydub
        file_repo = LocalFileRepository()
        
        # 2. Tiêm các dependency vào lớp ứng dụng
        orchestrator = TTSOrchestrator(
            tts_service=tts_service, 
            audio_merger=audio_merger, 
            file_repo=file_repo
        )
        
        # 3. Khởi chạy giao diện
        window = MainWindow(orchestrator=orchestrator)
        window.show()
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
    

## 💡 Tại sao giải pháp này tối ưu hơn Pydub?

  * Không phụ thuộc file `.exe` ngoài: Bạn không cần bắt người dùng cài đặt phần mềm FFmpeg thủ công vào biến môi trường hệ thống (PATH) nữa. Thư viện `av` đã tự tích hợp sẵn các file nhị phân thư viện liên kết động (`.dll` / `.so`) của FFmpeg bên trong nó.
  * Đồng bộ hóa PTS (Presentation Timestamp): Thuật toán tính toán `current_pts += resampled_frames.samples` giúp gộp trực tiếp ở mức độ byte-stream, triệt tiêu hoàn toàn hiện tượng xuất hiện tiếng "bụp" hoặc khoảng lặng `0.1s` giữa các mối nối chunk âm thanh.



Bây giờ bạn hoàn toàn có thể chạy hoặc đóng gói ứng dụng (bằng `uv run` hoặc `pyinstaller`) mà không lo các máy tính khác bị lỗi thiếu FFmpeg! Bạn có gặp khó khăn gì khi triển khai resampler này không?

  


[1] [https://pyav.org](https://pyav.org/docs/develop/api/audio.html)