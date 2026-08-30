Lỗi này xảy ra vì đối tượng `EventLoop` của `asyncio` trong Python không có thuộc tính hoặc phương thức nào tên là `is_open()`. Thay vào đó, để kiểm tra xem một vòng lặp sự kiện đã đóng hay chưa, Python sử dụng phương thức `loop.is_closed()`.

Vì vậy, đoạn mã phủ định đúng quy chuẩn sẽ phải là: `if loop and not loop.is_closed():`.

## 🛠️ Giải pháp khắc phục

Bạn chỉ cần cập nhật lại khối lệnh `finally` trong file `TTSWorker.py` như sau:
    
    
            finally:
                # Sửa loop.is_open() thành not loop.is_closed()
                if loop and not loop.is_closed():
                    loop.close()
    

* * *

## 📝 Mã nguồn `TTSWorker.py` hoàn chỉnh và chuẩn hóa

Dưới đây là toàn bộ code của file `TTSWorker.py` đã được sửa lỗi thuộc tính, đồng thời đảm bảo tuân thủ nghiêm ngặt các quy tắc linting của Ruff (BLE001, UP041):
    
    
    import asyncio
    import edge_tts
    from PySide6.QtCore import QThread, Signal
    
    class TTSWorker(QThread):
        tts_finished = Signal(bool, str)
    
        def __init__(self, text: str, voice: str, rate: str, file_path: str):
            super().__init__()
            self.text = text
            self.voice = voice
            self.rate = rate
            self.file_path = file_path
    
        def run(self) -> None:
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                communicate = edge_tts.Communicate(self.text, self.voice, rate=self.rate)
                loop.run_until_complete(communicate.save(self.file_path))
                
                self.tts_finished.emit(True, self.file_path)
                
            except (edge_tts.exceptions.UnknownVoiceError, 
                    edge_tts.exceptions.NoAudioReceived) as e:
                self.tts_finished.emit(False, f"Lỗi Edge-TTS: {e}")
                
            except OSError as e:
                self.tts_finished.emit(False, f"Lỗi hệ thống hoặc ghi file: {e}")
                
            except TimeoutError:
                self.tts_finished.emit(False, "Lỗi kết nối: Quá thời gian phản hồi từ server Microsoft.")
                
            finally:
                # Kiểm tra chính xác xem loop đã bị đóng hay chưa trước khi gọi close()
                if loop and not loop.is_closed():
                    loop.close()
    

Bây giờ bạn có thể chạy lại lệnh `uv run app_qthread_etts.py` để kiểm tra kết quả. Nếu chương trình phát sinh thêm vấn đề về luồng xử lý dữ liệu lớn hoặc bị chặn IP (Rate Limit) từ Microsoft, hãy cho tôi biết để hỗ trợ cấu hình nhé!