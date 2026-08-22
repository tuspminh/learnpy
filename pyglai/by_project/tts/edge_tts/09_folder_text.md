Dưới đây là mã nguồn Python hoàn chỉnh giúp bạn tự động hóa toàn bộ quy trình: Quét toàn bộ thư mục để tìm file văn bản (`.txt`), chuyển đổi sang giọng nói bằng `edge-tts`, tính toán phụ đề, gộp file qua FFmpeg CLI và quản lý đầu ra một cách ngăn nắp.

## Cấu trúc thư mục ứng dụng

Bạn chỉ cần tạo một thư mục dự án với cấu trúc đơn giản như sau:
    
    
    project_folder/
    │
    ├── main.py                <- File mã nguồn Python dưới đây
    ├── input_txt/             <- Thư mục chứa các file .txt cần đọc (ví dụ: chuong_1.txt, chuong_2.txt)
    └── output_audio/          <- Thư mục tự động sinh ra chứa file MP3 và SRT hoàn chỉnh
    

## Mã nguồn Python hoàn chỉnh
    
    
    import asyncio
    import os
    import subprocess
    import re
    import shutil
    
    # --- CẤU HÌNH HỆ THỐNG ---
    VOICE = "vi-VN-HoaiAnNeural"
    MAX_CHARS = 2000              # Giới hạn số ký tự an toàn cho mỗi lần gọi API
    INPUT_DIR = "input_txt"       # Thư mục chứa các file văn bản đầu vào
    OUTPUT_DIR = "output_audio"   # Thư mục chứa kết quả xuất ra
    
    # --- 1. HÀM CẮT VĂN BẢN THEO CÂU ---
    def split_text_by_sentences(text, max_chars=MAX_CHARS):
        """Cắt nhỏ văn bản thành các đoạn dưới max_chars để tránh lỗi API Edge-TTS."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
    
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current_chunk) + len(sentence) + 1 > max_chars:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
            else:
                current_chunk += sentence + " "
                
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks
    
    # --- 2. HÀM QUY ĐỔI THỜI GIAN SRT ---
    def ms_to_srt_time(ms: float) -> str:
        """Đổi mili-giây sang định dạng thời gian phụ đề SRT (HH:MM:SS,mmm)."""
        hours = int(ms // 3600000)
        minutes = int((ms % 3600000) // 60000)
        seconds = int((ms % 60000) // 1000)
        milliseconds = int(ms % 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    # --- 3. XỬ LÝ CHUYỂN ĐỔI MỘT ĐOẠN VĂN BẢN NHỎ ---
    async def process_chunk(chunk_text, index, temp_dir):
        """Tải âm thanh stream và trích xuất dữ liệu WordBoundary."""
        audio_file = os.path.join(temp_dir, f"chunk_{index}.mp3")
        communicate = edge_tts.Communicate(chunk_text, VOICE)
        
        raw_words = []
        sentences_data = []
    
        with open(audio_file, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    raw_words.append({
                        "word": chunk["text"],
                        "start": chunk["offset"] / 10000,
                        "duration": chunk["duration"] / 10000
                    })
    
        end_punctuation = ('.', '?', '!', ';', ':', '...', '..')
        current_sentence = []
    
        for item in raw_words:
            current_sentence.append(item)
            if item["word"].endswith(end_punctuation):
                start_time = current_sentence[0]["start"]
                end_time = current_sentence[-1]["start"] + current_sentence[-1]["duration"]
                sentence_string = " ".join([w["word"] for w in current_sentence])
                sentences_data.append({"start": start_time, "end": end_time, "text": sentence_string})
                current_sentence = []
    
        if current_sentence:
            start_time = current_sentence[0]["start"]
            end_time = current_sentence[-1]["start"] + current_sentence[-1]["duration"]
            sentence_string = " ".join([w["word"] for w in current_sentence])
            sentences_data.append({"start": start_time, "end": end_time, "text": sentence_string})
    
        return audio_file, sentences_data
    
    # --- 4. GỘP CÁC FILE MP3 BẰNG FFMPEG CLI ---
    def concat_audio_files(audio_files, output_mp3, temp_dir):
        """Gọi FFmpeg CLI ghép nối luồng trực tiếp (Demuxer), không nén lại âm thanh."""
        txt_list = os.path.join(temp_dir, "ffmpeg_list.txt")
        with open(txt_list, "w", encoding="utf-8") as f:
            for file in audio_files:
                f.write(f"file '{os.path.abspath(file).replace('\\', '/')}'\n")
    
        command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_list, "-c", "copy", output_mp3]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # --- 5. HÀM XỬ LÝ ĐỘC LẬP TỪNG FILE .TXT ---
    async def process_single_txt_file(txt_path, base_name):
        """Đọc file .txt, chia nhỏ, chạy TTS, tính toán tịnh tiến SRT và xuất kết quả."""
        print(f"\n[BẮT ĐẦU] Đang xử lý file văn bản: {base_name}.txt")
        
        # Tạo thư mục tạm riêng cho file này để tránh xung đột dữ liệu
        temp_dir = f"temp_{base_name}"
        os.makedirs(temp_dir, exist_ok=True)
    
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read().strip()
    
        if not full_text:
            print(f" -> Bỏ qua vì file trống: {base_name}.txt")
            shutil.rmtree(temp_dir)
            return
    
        text_chunks = split_text_by_sentences(full_text)
        print(f" -> Đã cắt thành {len(text_chunks)} phân đoạn nhỏ.")
    
        audio_files = []
        all_srt_blocks = []
        global_time_offset = 0.0
        srt_index = 1
    
        for idx, chunk in enumerate(text_chunks):
            audio_file, sentences = await process_chunk(chunk, idx, temp_dir)
            audio_files.append(audio_file)
    
            max_duration_in_chunk = 0
            for s_data in sentences:
                real_start = s_data["start"] + global_time_offset
                real_end = s_data["end"] + global_time_offset
                
                start_str = ms_to_srt_time(real_start)
                end_str = ms_to_srt_time(real_end)
    
                block = f"{srt_index}\n{start_str} --> {end_str}\n{s_data['text']}\n"
                all_srt_blocks.append(block)
                srt_index += 1
                
                if s_data["end"] > max_duration_in_chunk:
                    max_duration_in_chunk = s_data["end"]
    
            global_time_offset += max_duration_in_chunk
    
        # Đường dẫn xuất file cuối cùng
        final_mp3 = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        final_srt = os.path.join(OUTPUT_DIR, f"{base_name}.srt")
    
        # Gộp âm thanh và ghi file phụ đề srt tổng hợp
        concat_audio_files(audio_files, final_mp3, temp_dir)
        with open(final_srt, "w", encoding="utf-8") as f_srt:
            f_srt.write("\n".join(all_srt_blocks))
    
        # Xóa dọn dẹp thư mục tạm
        shutil.rmtree(temp_dir)
        print(f"[THÀNH CÔNG] Đã xuất bộ file: {base_name}.mp3 & .srt")
    
    # --- 6. HÀM ĐIỀU KHIỂN CHÍNH (QUÉT THƯ MỤC) ---
    async def main():
        # Tự động tạo các thư mục làm việc nếu chưa có
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
        # Lấy toàn bộ danh sách các file .txt trong thư mục đầu vào
        txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    
        if not txt_files:
            print(f" Không tìm thấy file .txt nào trong thư mục '{INPUT_DIR}'!")
            print(f"Hãy copy các file văn bản của bạn vào thư mục '{INPUT_DIR}' rồi chạy lại tool nhé.")
            return
    
        print(f"Tìm thấy tổng cộng {len(txt_files)} file văn bản cần xử lý.")
    
        # Vòng lặp quét tuần tự từng file văn bản một
        for filename in sorted(txt_files):
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(INPUT_DIR, filename)
            
            try:
                await process_single_txt_file(txt_path, base_name)
            except Exception as e:
                print(f" [LỖI] Thất bại khi xử lý file {filename}: {str(e)}")
    
        print("\n Toàn bộ thư mục đã được quét và xử lý thành công!")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Các điểm thông minh của hệ thống này:

  1. Quét tự động sắp xếp: Hàm sử dụng `sorted(txt_files)` để đảm bảo nếu bạn đặt tên file dạng `01_chuong1.txt`, `02_chuong2.txt`, hệ thống sẽ đọc và dịch tuần tự theo đúng thứ tự logic.
  2. Quản lý thư mục tạm (`temp_`) an toàn: Mỗi file `.txt` khi chạy sẽ tự đẻ ra một thư mục tạm riêng để chứa các mảnh nhỏ (`chunk_X.mp3`). Sau khi gộp bằng FFmpeg xong, thư mục rác này được xóa sạch sẽ bằng `shutil.rmtree()`, đảm bảo máy tính không bị đầy ổ cứng.
  3. Không lo treo luồng mạng: Xử lý vòng lặp tuần tự từng file giúp tránh việc gửi hàng loạt yêu cầu đồng thời lên máy chủ Microsoft Edge, giảm thiểu nguy cơ bị khóa IP tạm thời (Rate Limit).



Bạn có muốn phát triển tính năng này nâng cao hơn bằng cách tự động chèn thêm nhạc nền (Background Music) chạy nhỏ phía dưới giọng đọc cho sinh động không?