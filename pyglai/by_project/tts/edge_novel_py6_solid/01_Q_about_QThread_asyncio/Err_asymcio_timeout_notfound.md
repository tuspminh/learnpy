Yêu cầu của bạn rất chính xác để giữ mã nguồn luôn sạch sẽ và hiện đại. Theo luật Ruff UP041 (nâng cấp cú pháp Python), kể từ Python 3.11, `asyncio.TimeoutError` đã trở thành một bí danh (alias) của ngoại lệ built-in `TimeoutError`. Việc sử dụng trực tiếp `TimeoutError` giúp code ngắn gọn và nhất quán hơn.

Dưới đây là mã nguồn `TTSWorker` đã được cập nhật hoàn toàn để tuân thủ cả hai luật Ruff BLE001 và Ruff UP041:
    
    
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
                
            # Ruff UP041: Thay thế asyncio.TimeoutError bằng builtin TimeoutError
            except TimeoutError:
                self.tts_finished.emit(False, "Lỗi kết nối: Quá thời gian phản hồi từ server Microsoft.")
                
            finally:
                if loop and loop.is_open():
                    loop.close()
    

## 🛠️ Điểm cải tiến chính:

  * `except TimeoutError:`: Bắt lỗi vượt quá thời gian chờ bằng ngoại lệ tích hợp sẵn của Python. Lớp này tự động bắt được cả lỗi timeout của các tác vụ mạng thông thường lẫn tác vụ bất đồng bộ (`asyncio`) trên các phiên bản Python hiện đại.



Nếu bạn cần kiểm tra thêm các quy tắc linting khác của Ruff liên quan đến PyQt/PySide (như cách đặt tên slot hoặc quản lý bộ nhớ), hãy cho tôi biết nhé!