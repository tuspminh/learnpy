Để chuyển các chunk văn bản thành file âm thanh sử dụng giọng đọc của Microsoft Edge, chúng ta sẽ sử dụng thư viện `edge-tts`. Thư viện này kết nối trực tiếp với API của Microsoft Edge TTS, hỗ trợ đầy đủ các tùy chỉnh về giọng đọc (`voice`), tốc độ (`rate`), và cao độ (`pitch`).

## Cài đặt thư viện

Bạn cần cài đặt thêm thư viện `edge-tts` (hỗ trợ bất đồng bộ `asyncio`):
    
    
    pip install edge-tts asyncio
    

## Đoạn code Python tích hợp

Đoạn code dưới đây sẽ lấy văn bản từ file gốc, chia chunk bằng `underthesea`, sau đó chuyển đổi từng chunk thành file `.mp3` và lưu vào thư mục chỉ định:
    
    
    import os
    import asyncio
    from underthesea import sent_tokenize
    import edge_tts
    
    # 1. Hàm tách chunk từ file text (giữ nguyên từ bước trước)
    def split_text_to_chunks(file_path, max_chars=2000):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                current_chunk = f"{current_chunk} {sentence}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    # 2. Hàm bất đồng bộ chuyển chunk thành file Audio
    async def text_to_speech(text, output_file, voice, rate, pitch):
        # Khởi tạo tiến trình TTS với các tham số chỉ định
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        # Ghi file audio đầu ra
        await communicate.save(output_file)
    
    # 3. Hàm chính điều phối toàn bộ quy trình
    async def main():
        input_file = "van_ban.txt"
        output_dir = "output_audio"
        os.makedirs(output_dir, exist_ok=True)
        
        # Cấu hình giọng đọc, tốc độ và cao độ của Edge
        # Các giọng tiếng Việt phổ biến:
        # - "vi-VN-HoaiAnNeural" (Giọng Nam)
        # - "vi-VN-NamMinhNeural" (Giọng Nữ)
        VOICE = "vi-VN-HoaiAnNeural" 
        RATE = "+0%"     # Tốc độ: mặc định là "+0%", nhanh hơn ví dụ "+20%", chậm hơn ví dụ "-10%"
        PITCH = "+0Hz"   # Cao độ: mặc định là "+0Hz", trầm hơn ví dụ "-5Hz", thanh hơn ví dụ "+5Hz"
    
        print("Đang tách nhỏ file văn bản...")
        chunks = split_text_to_chunks(input_file, max_chars=2000)
        print(f"Tổng số chunk được tạo ra: {len(chunks)}")
    
        for idx, chunk in enumerate(chunks, 1):
            audio_path = os.path.join(output_dir, f"chunk_{idx}.mp3")
            print(f"Đang xử lý Audio cho Chunk {idx}/{len(chunks)} ({len(chunk)} ký tự)...")
            
            # Gọi hàm chuyển đổi TTS
            await text_to_speech(chunk, audio_path, VOICE, RATE, PITCH)
            print(f"-> Đã lưu: {audio_path}")
    
        print("\nHoàn thành! Toàn bộ file audio đã được lưu trong thư mục:", output_dir)
    
    # Chạy chương trình
    if __name__ == "__main__":
        asyncio.run(main())
    

## Cách tùy chỉnh các thông số:

  * `voice`: Bạn có thể đổi sang `"vi-VN-NamMinhNeural"` nếu muốn nghe giọng nữ.
  * `rate`: Thay đổi tốc độ đọc. Định dạng bắt buộc phải có dấu `+` hoặc `-` và ký hiệu `%` (Ví dụ: `"+15%"` để đọc nhanh hơn 15%, hoặc `"-10%"` để đọc chậm lại).
  * `pitch`: Thay đổi độ trầm/bổng của giọng. Định dạng bắt buộc phải có dấu `+` hoặc `-` đi kèm đơn vị `Hz` (Ví dụ: `"+2Hz"` hoặc `"-3Hz"`).



Để hoàn thiện hơn dự án này, bạn có muốn tôi hỗ trợ:

  * Thêm tính năng gộp tất cả các file MP3 nhỏ thành một file MP3 duy nhất sau khi chạy xong?
  * Tạo file phụ đề đi kèm (.srt) dựa trên các chunk để khớp với audio?



Hãy phản hồi lại lựa chọn mà bạn muốn nâng cấp tiếp theo nhé!