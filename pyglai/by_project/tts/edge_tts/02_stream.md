Xử lý luồng dữ liệu âm thanh (Streaming) với `edge-tts` cho phép bạn nhận các đoạn dữ liệu nhỏ (chunks) ngay khi hệ thống đang xử lý, thay vì phải đợi toàn bộ văn bản được chuyển đổi xong.

Cách này cực kỳ hữu ích khi bạn muốn phát âm thanh ngay lập tức lên loa (giảm độ trễ) hoặc truyền dữ liệu qua WebSockets cho ứng dụng frontend.

Dưới đây là 2 cách xử lý stream phổ biến nhất bằng Python:

* * *

## 1\. Lưu luồng dữ liệu theo thời gian thực (Tránh quá tải RAM)

Thay vì dùng hàm `.save()`, bạn có thể duyệt qua từng chunk dữ liệu khi nó vừa được tải về và ghi trực tiếp vào file. Cách này giúp bạn kiểm soát được tiến trình tải.
    
    
    import asyncio
    import edge_tts
    
    TEXT = "Hệ thống đang xử lý luồng âm thanh theo thời gian thực từ API của Microsoft Edge."
    VOICE = "vi-VN-HoaiAnNeural"
    OUTPUT_FILE = "stream_output.mp3"
    
    async def main() -> None:
        communicate = edge_tts.Communicate(TEXT, VOICE)
        
        # Mở file ở chế độ ghi nhị phân (wb)
        with open(OUTPUT_FILE, "wb") as f:
            # Duyệt qua từng gói dữ liệu (chunk) nhận được từ luồng
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                    print(".", end="", flush=True) # Hiển thị tiến trình dạng chấm
                    
        print(f"\nĐã ghi xong luồng dữ liệu vào file: {OUTPUT_FILE}")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

* * *

## 2\. Stream và phát trực tiếp ra loa (Không tạo file trung gian)

Để phát trực tiếp âm thanh từ bộ nhớ ra loa mà không cần lưu xuống ổ cứng, bạn cần cài đặt thêm thư viện `pyaudio`.
    
    
    pip install pyaudio
    

_(Lưu ý: Thư viện`pyaudio` yêu cầu máy tính của bạn phải cài đặt sẵn trình điều khiển âm thanh C++ hoặc PortAudio)._

Mã nguồn Python để phát trực tiếp ra loa:
    
    
    import asyncio
    import edge_tts
    import pyaudio
    
    TEXT = "Xin chào! Tôi đang nói trực tiếp từ bộ nhớ mà không cần lưu vào bất kỳ file âm thanh nào."
    VOICE = "vi-VN-NamMinhNeural" # Đổi sang giọng nam tiếng Việt
    
    async def stream_to_speaker():
        # 1. Khởi tạo cấu hình âm thanh bằng PyAudio
        # Các file MP3/WAV từ edge-tts thường có Sample Rate chuẩn là 24000Hz, Mono (1 channel)
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True
        )
    
        communicate = edge_tts.Communicate(TEXT, VOICE)
    
        print("Đang bắt đầu phát âm thanh...")
        
        # 2. Đọc luồng dữ liệu và đẩy thẳng ra loa
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                # Đẩy dữ liệu nhị phân vào luồng phát của loa
                stream.write(chunk["data"])
    
        # 3. Dọn dẹp và đóng cổng âm thanh sau khi kết thúc
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("\nĐã phát xong!")
    
    if __name__ == "__main__":
        asyncio.run(stream_to_speaker())
    

* * *

## Một số lưu ý quan trọng khi Stream

  * Thông tin metadata: Trong vòng lặp `communicate.stream()`, ngoài chunk có `type == "audio"`, bạn còn nhận được các chunk có `type == "WordBoundary"`. Các chunk này chứa vị trí ký tự và thời gian chính xác của từng từ đang được đọc, rất thích hợp nếu bạn muốn làm tính năng chạy chữ karaoke khớp với giọng nói.
  * Xử lý bất đồng bộ: Do luồng dữ liệu tải về qua mạng, việc sử dụng các thư viện phát âm thanh đồng bộ (synchronous) có thể gây giật lag âm thanh nếu mạng yếu. Bạn nên kết hợp với cơ chế hàng đợi (`asyncio.Queue`) nếu làm ứng dụng lớn.



Nếu bạn quan tâm, tôi có thể hướng dẫn tiếp về cách:

  * Lấy dữ liệu WordBoundary để làm hiệu ứng chữ chạy theo lời nói (Karaoke)
  * Tạo một API Server bằng FastAPI để stream âm thanh này lên trang web (giao diện HTML5)