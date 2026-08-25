Làm app đọc truyện tiểu thuyết bằng Edge-TTS là một lựa chọn cực kỳ sáng suốt vì giọng tiếng Việt của nó rất mượt, ngắt nghỉ tự nhiên, nghe lâu không bị mỏi tai.

Tuy nhiên, truyện tiểu thuyết có đặc thù là văn bản rất dài (hàng nghìn chữ mỗi chương). Nếu bạn quăng cả chương truyện vào Edge-TTS cùng một lúc, hệ thống chắc chắn sẽ bị lỗi (Timeout) hoặc bị Microsoft chặn IP vì gửi request quá lớn.

Dưới đây là giải pháp kiến trúc và code mẫu tối ưu nhất để bạn làm app đọc truyện.

* * *

## 🛠️ Chiến lược xử lý truyện dài (Kiến trúc App)

  1. Tách văn bản theo dấu câu: Chia chương truyện thành các đoạn nhỏ (khoảng 2–3 câu hoặc dưới 300 ký tự).
  2. Hàng đợi tải xuống (Queue): Gửi các đoạn nhỏ này lên Edge-TTS để chuyển thành các file âm thanh ngắn (`part_1.mp3`, `part_2.mp3`...).
  3. Gộp file (Merge): Dùng thư viện âm thanh để nối các file nhỏ đó lại thành một file chương hoàn chỉnh, hoặc phát (stream) cuốn chiếu từng file cho người dùng nghe.



* * *

## 💻 Code mẫu Python: Tạo file âm thanh cho cả chương truyện

Đoạn code dưới đây tự động chia nhỏ văn bản dài, gửi lên server để tránh bị chặn, và ghép lại thành một file truyện duy nhất bằng thư viện `pydub`.

## Bước 1: Cài đặt thêm thư viện xử lý âm thanh
    
    
    pip install edge-tts asyncio pydub
    

_(Lưu ý: Để chạy được`pydub`, máy bạn cần cài sẵn phần mềm FFmpeg)._

## Bước 2: Viết Code xử lý chương truyện
    
    
    import asyncio
    import edge_tts
    import os
    import re
    from pydub import AudioSegment
    
    # Giọng đọc phù hợp cho truyện: HoaiAn (Nữ Nam Bộ) hoặc NamMinh (Nam Bắc)
    VOICE = "vi-VN-HoaiAnNeural" 
    OUTPUT_FINAL = "chuong_1_hoan_thanh.mp3"
    
    # Giả lập một đoạn truyện dài
    CHAPTER_TEXT = (
        "Đêm đã khuya, gió lạnh thổi qua khe cửa sổ. Lâm Phong ngồi xếp bằng trên giường đá, "
        "linh khí xung quanh cơ thể gợn lên từng hồi. Hắn khẽ mở mắt, thở ra một ngụm trọc khí. "
        "Hơn ba năm qua, hắn đã chịu đủ mọi sự sỉ nhục của gia tộc. Hôm nay, cuối cùng hắn cũng "
        "đột phá đến Luyện Khí tầng thứ chín! Con đường tu tiên của hắn, giờ mới thực sự bắt đầu."
    )
    
    def split_text(text, max_chars=200):
        """Tách văn bản dài thành các câu nhỏ dựa trên dấu câu để tránh quá tải API"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    async def process_chapter():
        chunks = split_text(CHAPTER_TEXT)
        print(f"Truyện được chia làm {len(chunks)} phần để xử lý...")
        
        temp_files = []
        combined_audio = AudioSegment.empty()
    
        for i, chunk in enumerate(chunks):
            temp_filename = f"temp_{i}.mp3"
            print(f"Đang xử lý phần {i+1}/{len(chunks)}...")
            
            # Gửi request lên Edge-TTS
            communicate = edge_tts.Communicate(chunk, VOICE, rate="+0%") # rate="+10%" nếu muốn đọc nhanh hơn
            await communicate.save(temp_filename)
            temp_files.append(temp_filename)
            
            # Đọc file vừa tải và nối vào file tổng
            segment = AudioSegment.from_mp3(temp_filename)
            combined_audio += segment
            
            # Nghỉ 1-2 giây giữa các request để tránh bị khóa IP (Rate Limit)
            await asyncio.sleep(1.5)
    
        # Xuất file hoàn chỉnh
        combined_audio.export(OUTPUT_FINAL, format="mp3")
        print(f"🎉 Đã tạo xong file chương truyện: {OUTPUT_FINAL}")
    
        # Xóa các file tạm
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
    
    if __name__ == "__main__":
        asyncio.run(process_chapter())
    

* * *

## 💡 Kinh nghiệm xương máu khi làm App đọc truyện

  * Tùy chỉnh tốc độ đọc (`rate`): Truyện tiên hiệp hoặc đô thị thường có nhịp điệu nhanh. Bạn nên chỉnh thuộc tính `rate="+10%"` hoặc `rate="+15%"` trong code để giọng đọc nhanh và cuốn hơn, tránh bị buồn ngủ.
  * Xử lý từ viết tắt/Hán Việt: Các từ như _“đạo hữu”, “linh thạch”, “vạn”_ Edge-TTS đọc rất tốt. Nhưng các từ viết tắt như _“thần bí nhân A”, “V/v”_ thì bạn nên viết một hàm Python để tự động chuyển thành chữ thường (_“người bí ẩn A”, “về việc”_) trước khi gửi đi.
  * Cơ chế Cache âm thanh: Đừng tạo đi tạo lại một chương truyện. Khi người dùng đầu tiên bấm nghe Chương 1, hãy lưu file MP3 đó vào bộ nhớ Server (hoặc điện thoại). Người dùng thứ 2 vào nghe chỉ việc phát file có sẵn, vừa tiết kiệm băng thông vừa không sợ bị Microsoft ban IP.



Bạn định làm app này trên nền tảng nào (App di động React Native/Flutter hay là Website đọc truyện)? Hãy chia sẻ để tôi tư vấn cách thiết kế luồng phát âm thanh (Streaming) trực tiếp cho người nghe mà không cần bắt họ đợi tải xong cả file dài!