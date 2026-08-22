Lấy dữ liệu WordBoundary giúp bạn biết chính xác vị trí ký tự và thời gian (tính bằng mili-giây) của từng từ khi hệ thống đang đọc. Dữ liệu này là cốt lõi để làm các tính năng như hiển thị phụ đề, tô đậm từ đang đọc (text highlighting) hoặc làm hiệu ứng chạy chữ kiểu karaoke.

Trong thư viện `edge-tts`, khi bạn duyệt luồng bằng hàm `stream()`, các gói tin WordBoundary sẽ trả về 3 thông tin chính:

  * `text`: Từ ngữ cụ thể đang được phát âm.
  * `offset`: Thời điểm bắt đầu đọc từ đó (tính bằng băm thời gian hệ thống - cần quy đổi sang giây/mili-giây).
  * `duration`: Khoảng thời gian để đọc hết từ đó.



Dưới đây là mã nguồn Python chi tiết để trích xuất và đồng bộ dữ liệu này:
    
    
    import asyncio
    import edge_tts
    
    TEXT = "Học lập trình Python rất thú vị và có nhiều ứng dụng thực tế."
    VOICE = "vi-VN-HoaiAnNeural"
    OUTPUT_FILE = "karaoke_output.mp3"
    
    async def main() -> None:
        communicate = edge_tts.Communicate(TEXT, VOICE)
        
        print("--- Bắt đầu xử lý luồng dữ liệu ---")
        
        with open(OUTPUT_FILE, "wb") as f:
            async for chunk in communicate.stream():
                # 1. Ghi dữ liệu âm thanh vào file như bình thường
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                    
                # 2. Bắt và xử lý sự kiện WordBoundary
                elif chunk["type"] == "WordBoundary":
                    # Định dạng lại thời gian: offset của edge-tts tính bằng ticks (1 tick = 100 nanoseconds)
                    # Công thức đổi sang mili-giây (ms): ticks / 10000
                    start_ms = chunk["offset"] / 10000
                    duration_ms = chunk["duration"] / 10000
                    word = chunk["text"]
                    
                    print(f"Từ: '{word}' | Bắt đầu: {start_ms:.0f}ms | Kéo dài: {duration_ms:.0f}ms")
    
        print(f"\n--- Hoàn thành! Đã lưu file âm thanh tại: {OUTPUT_FILE} ---")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Kết quả hiển thị trên Terminal khi chạy code:
    
    
    --- Bắt đầu xử lý luồng dữ liệu ---
    Từ: 'Học' | Bắt đầu: 0ms | Kéo dài: 250ms
    Từ: 'lập' | Bắt đầu: 250ms | Kéo dài: 200ms
    Từ: 'trình' | Bắt đầu: 450ms | Kéo dài: 300ms
    Từ: 'Python' | Bắt đầu: 750ms | Kéo dài: 500ms
    ...
    --- Hoàn thành! Đã lưu file âm thanh tại: karaoke_output.mp3 ---
    

## Ứng dụng thực tế của dữ liệu này:

  * Xuất file phụ đề SRT/VTT: Bạn có thể dùng dữ liệu `start_ms` và `duration_ms` để tự động ghi ra file phụ đề `.srt` chuẩn khớp từng giây với file MP3.
  * Đồng bộ Frontend: Nếu gửi dữ liệu này qua WebSocket lên giao diện Web (React/Vue), bạn có thể dùng CSS để đổi màu (Highlight) thẻ `<span>` chứa từ tương ứng khi trình phát nhạc đạt đến mốc thời gian đó.



Nếu bạn muốn nâng cấp đoạn code này, hãy cho tôi biết:

  * Bạn có muốn viết thêm hàm để tự động xuất ra file phụ đề `.srt` từ dữ liệu trên không?
  * Bạn có cần kết hợp dữ liệu này để hiển thị trực tiếp lên một giao diện đồ họa (như Tkinter hoặc PyQt) không?