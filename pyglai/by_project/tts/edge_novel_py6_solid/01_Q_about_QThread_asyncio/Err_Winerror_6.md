Lỗi `OSError: [WinError 6] The handle is invalid` kèm thông báo `Cancelling an overlapped future failed` là một lỗi kinh điển của hệ điều hành Windows khi chạy các thư viện bất đồng bộ với Python kể từ phiên bản 3.8 trở đi. [1, 2] 

## Nguyên nhân cốt lõi

  *   * Vấn đề cấu hình: Từ Python 3.8, Windows tự động chuyển `asyncio` sang sử dụng vòng lặp sự kiện mặc định là `ProactorEventLoop` để tăng tốc độ xử lý I/O.
  * Xung đột đa luồng: Khi bạn đóng vòng lặp (`loop.close()`) ngay trên luồng phụ (`QThread`), `ProactorEventLoop` cố gắng hủy bỏ cấu trúc I/O ngầm của Windows (Overlapped I/O). Tuy nhiên, do luồng này sắp kết thúc hoặc tài nguyên I/O đã bị giải phóng trước đó bởi Windows, hàm `self._ov.cancel()` cố dọn dẹp một handle không còn tồn tại, dẫn đến lỗi crash hệ thống. [1, 2, 3, 4, 5] 
  * 


* * *

## 🛠️ Giải pháp khắc phục triệt để

Có hai cách để xử lý lỗi này. Cách thứ nhất là đổi Policy (chính sách) của Event Loop sang `SelectorEventLoopPolicy` (mô hình cũ hơn nhưng cực kỳ ổn định trên luồng phụ). Cách thứ hai là bắt và bỏ qua ngoại lệ này tại hàm dọn dẹp lỗi toàn cục của loop. [1, 2, 4, 6] 

Dưới đây là mã nguồn `TTSWorker.py` áp dụng đồng thời cả hai giải pháp để chấm dứt hoàn toàn lỗi handle trên Windows, đảm bảo tuân thủ nghiêm ngặt Ruff BLE001 và UP041:
    
    
    import asyncio
    import sys
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
            # Giải pháp 1: Nếu chạy trên Windows, thiết lập SelectorEventLoop cho luồng phụ này.
            # SelectorEventLoop không dùng Overlapped I/O nên loại bỏ hoàn toàn lỗi WinError 6.
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
            loop = None
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Giải pháp 2 (Dự phòng): Thiết lập bộ lọc ngoại lệ tùy biến cho loop.
                # Nếu phát sinh lỗi 'Cancelling an overlapped future failed', loop sẽ bỏ qua thay vì báo crash.
                def custom_exception_handler(loop_context, context):
                    msg = context.get("message")
                    if msg and "Cancelling an overlapped future failed" in msg:
                        return  # Bỏ qua lỗi dọn dẹp handle vô hại của Windows
                    loop_context.default_exception_handler(context)
                    
                loop.set_exception_handler(custom_exception_handler)
    
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
                if loop and not loop.is_closed():
                    loop.close()
    

## 💡 Giải thích cơ chế sửa đổi:

  1. `asyncio.WindowsSelectorEventLoopPolicy()`: Thay vì sử dụng bộ quản lý I/O `Proactor` nâng cao của Windows 10/11 thường bị lỗi handle khi kết thúc luồng đột ngột, chúng ta hạ cấp xuống `Selector`. Đối với các tác vụ đơn giản như tải và lưu audio thông qua `edge-tts`, sự thay đổi này hoàn toàn không làm giảm hiệu suất mà lại mang lại sự an toàn tuyệt đối. [1, 2] 
  2. `loop.set_exception_handler(...)`: Tạo một bộ lọc lỗi "màng bọc". Nếu trong quá trình đóng loop, Windows ném ra thông điệp thông báo lỗi hủy luồng thất bại, ứng dụng sẽ âm thầm nuốt lỗi này một cách hợp lệ vì nó không gây ảnh hưởng đến file audio đã được lưu trước đó. [4, 6] 



Bạn hãy lưu file và chạy lại lệnh `uv run app_qthread_etts.py`, lỗi dọn dẹp luồng của Windows sẽ biến mất.

Nếu dự án của bạn cần thêm chức năng tự động cắt nhỏ chuỗi văn bản dài (vì Microsoft giới hạn số ký tự gửi lên cho mỗi lượt đọc), hãy phản hồi để tôi bổ sung nhé!

  


[1] [https://cloud.tencent.com](https://cloud.tencent.com/developer/ask/sof/108118419)

[2] [https://stackoverflow.com](https://stackoverflow.com/questions/62412754/python-asyncio-errors-oserror-winerror-6-the-handle-is-invalid-and-runtim)

[3] [https://github.com](https://github.com/python/cpython/issues/82505)

[4] [https://github.com](https://github.com/wbenny/python-graceful-shutdown/blob/master/README.md)

[5] [https://github.com](https://github.com/wbenny/python-graceful-shutdown)

[6] [https://github.com](https://github.com/wbenny/python-graceful-shutdown/blob/master/complex.py)