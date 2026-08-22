Để gộp cả file âm thanh MP3 và file phụ đề SRT tương ứng của nhiều đoạn văn bản, lập trình viên Python sẽ kết hợp FFmpeg CLI (gộp âm thanh) và tính toán tịnh tiến thời gian bằng Python thuần (gộp phụ đề).

Khi không dùng PySide6, mã nguồn sẽ chuyển về dạng bất đồng bộ thuần túy (`asyncio`), giúp xử lý nhanh tối đa công suất.

## Hướng dẫn chuẩn bị thư viện

Bạn chỉ cần cài đặt thư viện `edge-tts`:
    
    
    pip install edge-tts
    

_(Hãy chắc chắn máy tính của bạn đã cài đặt công cụ dòng lệnh FFmpeg như hướng dẫn trước)._

* * *

## Mã nguồn Python hoàn chỉnh (Cắt văn bản -> Chuyển TTS -> Gộp MP3 & SRT)

Đoạn code dưới đây nhận vào một văn bản cực dài, tự động chia nhỏ dưới 2000 ký tự, gọi `edge-tts` để lấy âm thanh và mốc câu, sau đó gộp tất cả thành 1 file MP3 duy nhất và 1 file SRT duy nhất khớp chuẩn xác mốc thời gian.
    
    
    import asyncio
    import os
    import subprocess
    import re
    
    # --- CẤU HÌNH ---
    VOICE = "vi-VN-HoaiAnNeural"
    MAX_CHARS = 2000  # Giới hạn an toàn cho mỗi đoạn text gửi lên API
    OUTPUT_MP3 = "sach_noi_hoan_chinh.mp3"
    OUTPUT_SRT = "sach_noi_hoan_chinh.srt"
    
    # --- 1. HÀM TỰ ĐỘNG CẮT VĂN BẢN THEO CÂU ---
    def split_text_by_sentences(text, max_chars=MAX_CHARS):
        """Cắt nhỏ văn bản dài thành các đoạn nhỏ không vượt quá max_chars, không làm đứt câu."""
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
    
    # --- 2. HÀM QUY ĐỔI THỜI GIAN CHUẨN SRT ---
    def ms_to_srt_time(ms: float) -> str:
        """Đổi mili-giây sang định dạng thời gian SRT (HH:MM:SS,mmm)"""
        hours = int(ms // 3600000)
        minutes = int((ms % 3600000) // 60000)
        seconds = int((ms % 60000) // 1000)
        milliseconds = int(ms % 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    # --- 3. HÀM XỬ LÝ CHUYỂN ĐỔI 1 ĐOẠN VĂN BẢN ---
    async def process_chunk(chunk_text, index):
        """Tải âm thanh và trích xuất dữ liệu câu đã gom cho một đoạn văn bản."""
        audio_file = f"temp_part_{index}.mp3"
        communicate = edge_tts.Communicate(chunk_text, VOICE)
        
        raw_words = []
        sentences_data = []
    
        # Đọc stream lưu file âm thanh và bắt tọa độ từ
        with open(audio_file, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    raw_words.append({
                        "word": chunk["text"],
                        "start": chunk["offset"] / 10000,       # đổi sang ms
                        "duration": chunk["duration"] / 10000   # đổi sang ms
                    })
    
        # Gom từ đơn lẻ thành câu dựa trên dấu câu
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
    
    # --- 4. HÀM GỘP FILE ÂM THANH BẰNG FFMPEG CLI ---
    def concat_audio_files(audio_files, output_mp3):
        """Gọi FFmpeg CLI để gộp các file MP3 tốc độ siêu nhanh."""
        txt_list = "temp_ffmpeg_list.txt"
        with open(txt_list, "w", encoding="utf-8") as f:
            for file in audio_files:
                f.write(f"file '{os.path.abspath(file).replace('\\', '/')}'\n")
    
        command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_list, "-c", "copy", output_mp3]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        os.remove(txt_list)
    
    # --- 5. LUỒNG ĐIỀU KHIỂN CHÍNH (MAIN) ---
    async def main():
        # Văn bản mẫu cực dài (Giả lập việc bạn đọc cả chương sách)
        van_ban_dai = (
            "Chào mừng bạn đến với hướng dẫn lập trình nâng cao. Hôm nay chúng ta học về edge-tts. "
            "Đây là một công cụ mã nguồn mở tuyệt vời giúp chuyển đổi văn bản dài thành giọng nói. "
            "Hệ thống sẽ tự động cắt nhỏ tài liệu của bạn ra thành nhiều phần để tránh lỗi quá tải hệ thống đám mây. "
            "Sau khi tải xong, thuật toán thông minh sẽ tự động tính toán lại mốc thời gian để gộp file phụ đề srt. "
            "Cuối cùng, lệnh CLI từ FFmpeg sẽ nối tất cả các file âm thanh lại với nhau một cách hoàn hảo và mượt mà nhất."
        )
    
        print("Bước 1: Đang phân tích và cắt nhỏ văn bản...")
        text_chunks = split_text_by_sentences(van_ban_dai, max_chars=200) # Cắt nhỏ hơn để dễ kiểm tra
        print(f"-> Đã chia văn bản thành {len(text_chunks)} đoạn nhỏ.")
    
        audio_files = []
        all_srt_blocks = []
        global_time_offset = 0.0  # Biến tích lũy tổng thời gian để tịnh tiến phụ đề
        srt_index = 1
    
        print("\nBước 2: Đang tải dữ liệu âm thanh và tạo mốc phụ đề từ Edge-TTS...")
        for idx, chunk in enumerate(text_chunks):
            print(f"   - Đang xử lý đoạn {idx + 1}/{len(text_chunks)}...")
            audio_file, sentences = await process_chunk(chunk, idx)
            audio_files.append(audio_file)
    
            # Xử lý gộp phụ đề và dịch chuyển mốc thời gian (Tịnh tiến theo global_time_offset)
            max_duration_in_chunk = 0
            for s_data in sentences:
                # Tịnh tiến thời gian của câu dựa trên độ dài của các file trước đó
                real_start = s_data["start"] + global_time_offset
                real_end = s_data["end"] + global_time_offset
                
                start_str = ms_to_srt_time(real_start)
                end_str = ms_to_srt_time(real_end)
    
                block = f"{srt_index}\n{start_str} --> {end_str}\n{s_data['text']}\n"
                all_srt_blocks.append(block)
                srt_index += 1
                
                # Ghi nhận mốc thời gian lớn nhất trong đoạn hiện tại
                if s_data["end"] > max_duration_in_chunk:
                    max_duration_in_chunk = s_data["end"]
    
            # Cập nhật tổng thời gian tích lũy cho đoạn tiếp theo
            global_time_offset += max_duration_in_chunk
    
        print("\nBước 3: Đang gộp các file MP3 bằng FFmpeg CLI...")
        concat_audio_files(audio_files, OUTPUT_MP3)
    
        print("Bước 4: Đang ghi file phụ đề SRT hoàn chỉnh...")
        with open(OUTPUT_SRT, "w", encoding="utf-8") as f_srt:
            f_srt.write("\n".join(all_srt_blocks))
    
        print("\nBước 5: Tiến hành dọn dẹp các file rác tạm thời...")
        for file in audio_files:
            if os.path.exists(file):
                os.remove(file)
    
        print(f"\n Hoàn thành xuất sắc! Hệ thống đã tạo ra:\n - File âm thanh: {OUTPUT_MP3}\n - File phụ đề: {OUTPUT_SRT}")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Cách thức hoạt động của thuật toán gộp phụ đề (Cốt lõi):

Khi gộp file `.srt`, nếu bạn chỉ bê nguyên mốc thời gian của từng đoạn nhỏ đặt cạnh nhau, file phụ đề sẽ bị lỗi vì đoạn số 2 sẽ lại bắt đầu chạy từ giây `00:00:00`.  
Để sửa lỗi này, mã nguồn sử dụng biến `global_time_offset`. Mỗi khi một đoạn âm thanh nhỏ xử lý xong, độ dài của nó (tính bằng mili-giây) sẽ được cộng dồn vào biến này. Đoạn văn bản tiếp theo khi tạo phụ đề sẽ lấy mốc thời gian gốc của nó cộng thêm `global_time_offset` để tịnh tiến thời gian chuẩn xác theo dòng thời gian của file MP3 tổng.

Bạn có muốn phát triển thêm hệ thống này thành một ứng dụng tự động quét và đọc toàn bộ các file `.txt` có trong thư mục không?