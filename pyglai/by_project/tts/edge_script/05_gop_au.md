Để gộp các file MP3 nhỏ thành một file duy nhất, thư viện chuẩn và mạnh mẽ nhất trong Python là `pydub`. Thư viện này xử lý nối âm thanh rất mượt mà, không bị vấp giữa các đoạn chuyển tiếp.

## Cài đặt thư viện bổ sung

Bạn cần cài đặt `pydub`:
    
    
    pip install pydub
    

> Lưu ý quan trọng: `pydub` yêu cầu máy tính của bạn phải cài đặt sẵn FFmpeg để xử lý file MP3.
> 
>   * Windows: Tải FFmpeg, giải nén và thêm đường dẫn thư mục `bin` vào Environment Variables (Path) của hệ thống.
>   * Mac: Chạy lệnh `brew install ffmpeg` qua Terminal.
> 


## Đoạn code Python tích hợp hoàn chỉnh

Dưới đây là mã nguồn toàn diện: Tách chữ bằng `underthesea` → Chuyển thành audio bằng `edge-tts` → Tự động gộp thành một file `ket_qua_cuoi_cung.mp3`.
    
    
    import os
    import asyncio
    from underthesea import sent_tokenize
    import edge_tts
    from pydub import AudioSegment
    
    # 1. Hàm tách chunk từ file text
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
    
    # 2. Hàm chuyển text thành Audio
    async def text_to_speech(text, output_file, voice, rate, pitch):
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_file)
    
    # 3. Hàm gộp các file MP3 trong một thư mục theo đúng thứ tự số
    def merge_mp3_files(input_dir, output_file_path):
        print("\nĐang tiến hành gộp các file MP3...")
        
        # Lấy danh sách file và sắp xếp theo số thứ tự (chunk_1, chunk_2,...)
        audio_files = [f for f in os.listdir(input_dir) if f.endswith('.mp3')]
        audio_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        
        if not audio_files:
            print("Không tìm thấy file MP3 nào để gộp!")
            return
    
        # Khởi tạo đoạn âm thanh trống đầu tiên
        combined_audio = AudioSegment.empty()
        
        for file_name in audio_files:
            file_path = os.path.join(input_dir, file_name)
            print(f"-> Đang nối: {file_name}")
            
            # Đọc file audio nhỏ và cộng dồn vào file tổng
            current_audio = AudioSegment.from_mp3(file_path)
            combined_audio += current_audio
            
            # Tùy chọn: Thêm 0.5 giây im lặng giữa các chunk (500ms) để ngắt nghỉ tự nhiên
            # combined_audio += AudioSegment.silent(duration=500)
    
        # Xuất ra file MP3 duy nhất
        combined_audio.export(output_file_path, format="mp3")
        print(f"\n Hoàn thành xuất sắc! File tổng đã được lưu tại: {output_file_path}")
    
    # 4. Hàm chính điều phối quy trình
    async def main():
        input_file = "van_ban.txt"
        output_dir = "output_audio_chunks"
        final_audio_file = "ket_qua_cuoi_cung.mp3"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Cấu hình giọng đọc
        VOICE = "vi-VN-HoaiAnNeural" 
        RATE = "+0%"     
        PITCH = "+0Hz"   
    
        print("Đang tách nhỏ file văn bản...")
        chunks = split_text_to_chunks(input_file, max_chars=2000)
        print(f"Tổng số chunk được tạo ra: {len(chunks)}")
    
        # Quy trình tạo các file MP3 nhỏ
        for idx, chunk in enumerate(chunks, 1):
            audio_path = os.path.join(output_dir, f"chunk_{idx}.mp3")
            print(f"Đang xử lý Audio {idx}/{len(chunks)}...")
            await text_to_speech(chunk, audio_path, VOICE, RATE, PITCH)
    
        # Tiến hành gộp file sau khi tất cả các chunk đã tạo xong
        merge_mp3_files(output_dir, final_audio_file)
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Điểm mấu chốt khi gộp file

  * Sắp xếp thông minh: Hàm gộp sử dụng `key=lambda x: int(...)` để đảm bảo file `chunk_10.mp3` sẽ được nối sau `chunk_9.mp3` chứ không bị nhảy lên sau `chunk_1.mp3` như bộ lọc chữ cái thông thường.
  * Khoảng lặng ngắt nghỉ (Tùy chọn): Tôi có để lại một dòng code ẩn (bị còm) `# combined_audio += AudioSegment.silent(duration=500)`. Nếu bạn muốn giữa các chunk có một khoảng nghỉ ngắn 0.5 giây cho tự nhiên thì có thể mở dấu `#` đó ra.



Nếu bạn cần tinh chỉnh thêm, hãy cho biết:

  * Bạn có muốn tự động xóa thư mục chứa các file chunk nhỏ sau khi đã gộp xong để sạch máy không?
  * Bạn có gặp bất kỳ lỗi liên quan đến FFmpeg khi chạy đoạn code gộp này không?