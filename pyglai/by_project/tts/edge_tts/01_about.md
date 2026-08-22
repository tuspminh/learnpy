edge-tts là một thư viện mã nguồn mở miễn phí của Python, cho phép bạn sử dụng dịch vụ Text-to-Speech (TTS) của trình duyệt Microsoft Edge mà không cần đăng ký tài khoản Cloud hay không cần API Key.

Đây là giải pháp thay thế hoàn hảo cho Google Cloud TTS nếu bạn muốn làm các dự án cá nhân, tiết kiệm chi phí, hoặc cần chuyển đổi văn bản dài mà không lo giới hạn ký tự trả phí.

## Ưu điểm vượt trội

  * Hoàn toàn miễn phí: Không giới hạn số lượng ký tự, không cần thẻ tín dụng.
  * Chất lượng cực cao: Sử dụng chung các giọng đọc chuẩn Neural (AI) như Microsoft Azure TTS (bao gồm cả các giọng đọc tiếng Việt rất tự nhiên như HoaiAn hoặc NamMinh).
  * Không cần cấu hình phức tạp: Không cần file JSON xác thực, không cần tạo Project trên đám mây.
  * Tốc độ nhanh: Chạy bất đồng bộ (Asynchronous) dựa trên nền tảng `asyncio`.



* * *

## Hướng dẫn sử dụng Python với `edge-tts`

## 1\. Cài đặt thư viện

Bạn chỉ cần cài đặt thư viện thông qua pip:
    
    
    pip install edge-tts
    

## 2\. Mã nguồn Python cơ bản (Chuyển đổi văn bản sang MP3)

Vì `edge-tts` hoạt động dựa trên cơ chế bất đồng bộ, bạn cần sử dụng từ khóa `async` và `await`.
    
    
    import asyncio
    import edge_tts
    
    # Cấu hình nội dung, giọng đọc và file đầu ra
    TEXT = "Xin chào! Đây là giọng đọc nhân tạo được tạo ra bởi thư viện edge tts."
    VOICE = "vi-VN-HoaiAnNeural" # Giọng nữ tiếng Việt phổ biến và tự nhiên nhất
    OUTPUT_FILE = "edge_output.mp3"
    
    async def main() -> None:
        # Khởi tạo đối tượng Communicate
        communicate = edge_tts.Communicate(TEXT, VOICE)
        
        # Tiến hành chuyển đổi và lưu trực tiếp thành file
        await communicate.save(OUTPUT_FILE)
        print(f"Đã lưu file âm thanh thành công tại: {OUTPUT_FILE}")
    
    # Chạy chương trình
    if __name__ == "__main__":
        asyncio.run(main())
    

## 3\. Tùy chỉnh Tốc độ (Rate) và Cao độ (Pitch)

Bạn có thể thay đổi tốc độ đọc nhanh/chậm hoặc tăng/giảm cao độ bằng cách truyền thêm tham số định dạng chuỗi:
    
    
    # Tăng tốc độ lên 20% (+20%) và giảm cao độ đi 5Hz (-5Hz)
    communicate = edge_tts.Communicate(
        TEXT, 
        VOICE, 
        rate="+20%", 
        pitch="-5Hz"
    )
    

* * *

## So sánh nhanh giữa Google Cloud TTS và Edge-TTS

Tiêu chí| Google Cloud TTS| Edge-TTS (Microsoft Edge)  
---|---|---  
Chi phí| Miễn phí giới hạn, sau đó tính phí| Hoàn toàn miễn phí [1]  
Cài đặt| Phức tạp (Tạo tài khoản, IAM, file JSON)| Rất dễ (Chỉ cần cài thư viện) [1, 2]  
Chất lượng tiếng Việt| Rất tốt (Neural2)| Rất tốt, tự nhiên giống người thật  
Giới hạn ký tự| Giới hạn nghiêm ngặt theo gói [1]| Không giới hạn (Thích hợp cho truyện dài)  
Độ ổn định| Cam kết dịch vụ SLA của Google| Phụ thuộc vào API không chính thức từ Edge  
  
Nếu bạn đang làm ứng dụng thương mại lớn cần độ ổn định tuyệt đối từ nhà cung cấp, hãy chọn Google Cloud TTS. Nếu bạn đang làm tool cào tin tức, đọc truyện tự động, làm video TikTok/YouTube ngắn hoặc tiết kiệm chi phí, edge-tts là sự lựa chọn số một.

Nếu bạn muốn, tôi có thể hướng dẫn bạn cách liệt kê toàn bộ danh sách giọng đọc tiếng Việt/tiếng Anh có sẵn trong thư viện này hoặc cách xử lý đọc luồng (Stream) trực tiếp không cần lưu file!