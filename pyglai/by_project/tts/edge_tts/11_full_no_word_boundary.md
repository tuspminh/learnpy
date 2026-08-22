Dưới đây là mã nguồn Python bản full hoàn chỉnh, được tối ưu hóa ở mức cao nhất để chỉ chuyển đổi văn bản sang file âm thanh MP3, loại bỏ hoàn toàn phần xử lý phụ đề WordBoundary để tăng tốc độ chạy.

Đoạn code này tích hợp sẵn:

  1. Quét thư mục `input_txt` để tìm tất cả file `.txt`.
  2. Tự động chia nhỏ các văn bản dài (tránh lỗi ngắt kết nối).
  3. Cơ chế Retry (Thử lại) thông minh nếu mạng chập chằn.
  4. FFmpeg CLI để gộp các đoạn nhỏ thành 1 file MP3 duy nhất cho mỗi file văn bản.



## 1\. Chuẩn bị thư viện và công cụ

Cài đặt thư viện `edge-tts`:
    
    
    pip install edge-tts
    

_Đảm bảo máy tính của bạn đã cài đặt công cụ dòng lệnh FFmpeg để hệ thống gọi lệnh gộp file._

## 2\. Mã nguồn Python toàn diện (`main.py`)
    
    
    import asyncio
    import os
    import subprocess
    import re
    import shutil
    
    # --- CẤU HÌNH HỆ THỐNG ---
    VOICE = "vi-VN-HoaiAnNeural"   # Giọng đọc tiếng Việt (Nữ)
    MAX_CHARS = 3000              # Số ký tự an toàn tối đa cho mỗi phân đoạn
    INPUT_DIR = "input_txt"       # Thư mục chứa các file .txt đầu vào
    OUTPUT_DIR = "output_audio"   # Thư mục chứa file .mp3 đầu ra
    MAX_RETRIES = 3               # Số lần tự động thử lại nếu gặp lỗi mạng
    
    # --- 1. HÀM CẮT VĂN BẢN THEO CÂU TRÁNH LỖI QUÁ TẢI ---
    def split_text_by_sentences(text, max_chars=MAX_CHARS):
        """Chia nhỏ văn bản dài thành các đoạn nhỏ không vượt quá max_chars."""
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
    
    # --- 2. HÀM TẢI STREAM ÂM THANH CÓ CƠ CHẾ RETRY ---
    async def download_audio_chunk_with_retry(chunk_text, output_file, chunk_idx):
        """Tải stream âm thanh từ Edge-TTS, tự động thử lại nếu lỗi mạng."""
        delay = 2  # Thời gian chờ ban đầu tính bằng giây
    
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Khởi tạo đối tượng chỉ lấy Audio (Tốc độ tối đa)
                communicate = edge_tts.Communicate(chunk_text, VOICE)
                
                with open(output_file, "wb") as f:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                return True  # Tải thành công phân đoạn
                
            except Exception as e:
                print(f"      [CẢNH BÁO] Lần thử {attempt}/{MAX_RETRIES} phân đoạn {chunk_idx} thất bại: {e}")
                if attempt == MAX_RETRIES:
                    raise e  # Hết lượt thử, ném lỗi ra ngoài
                
                await asyncio.sleep(delay)
                delay *= 2  # Tăng thời gian chờ cho lần thử kế tiếp
    
    # --- 3. HÀM GỘP CÁC FILE MP3 NHỎ QUA FFMPEG CLI ---
    def concat_audio_files(audio_files, output_mp3, temp_dir):
        """Gọi FFmpeg CLI ghép nối luồng trực tiếp (Demuxer) siêu tốc độ, không nén lại âm thanh."""
        txt_list = os.path.join(temp_dir, "ffmpeg_list.txt")
        with open(txt_list, "w", encoding="utf-8") as f:
            for file in audio_files:
                # Chuẩn hóa đường dẫn phù hợp với cú pháp FFmpeg
                f.write(f"file '{os.path.abspath(file).replace('\\', '/')}'\n")
    
        command = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", txt_list, "-c", "copy", output_mp3]
        # Chạy CLI ẩn không bật cửa sổ dòng lệnh đen
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    # --- 4. TIẾN TRÌNH XỬ LÝ CHO TỪNG FILE VĂN BẢN VÀO ---
    async def process_single_txt_file(txt_path, base_name):
        """Đọc file .txt, chia cắt, tải song song/tuần tự audio và gộp file."""
        print(f"\n[BẮT ĐẦU] Đang xử lý: {base_name}.txt")
        
        # Tạo thư mục chứa các mảnh file nhỏ tạm thời
        temp_dir = f"temp_{base_name}"
        os.makedirs(temp_dir, exist_ok=True)
    
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read().strip()
    
        if not full_text:
            print(f" -> Bỏ qua vì file văn bản rỗng.")
            shutil.rmtree(temp_dir)
            return
    
        # Cắt chữ thành các phân đoạn nhỏ hơn để Edge-TTS xử lý mượt mà
        text_chunks = split_text_by_sentences(full_text)
        print(f" -> Đã chia nhỏ văn bản thành {len(text_chunks)} phân đoạn.")
    
        audio_files = []
    
        # Tải tuần tự từng phân đoạn để bảo vệ IP khỏi bị Rate Limit bởi Microsoft
        for idx, chunk in enumerate(text_chunks):
            chunk_file = os.path.join(temp_dir, f"chunk_{idx}.mp3")
            print(f"   - Đang tải âm thanh đoạn {idx + 1}/{len(text_chunks)}...")
            
            await download_audio_chunk_with_retry(chunk, chunk_file, idx + 1)
            audio_files.append(chunk_file)
    
        # Khởi tạo đường dẫn lưu file đích cuối cùng
        final_mp3 = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
    
        print(" -> Đang gộp các mảnh âm thanh bằng FFmpeg CLI...")
        concat_audio_files(audio_files, final_mp3, temp_dir)
    
        # Giải phóng và xóa thư mục rác tạm thời
        shutil.rmtree(temp_dir)
        print(f"[THÀNH CÔNG] Đã tạo file: {final_mp3}")
    
    # --- 5. HÀM KHỞI CHẠY CHÍNH QUÉT TOÀN BỘ THƯ MỤC ---
    async def main():
        # Khởi tạo các thư mục làm việc nếu chưa tồn tại trên ổ đĩa
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
        # Quét lấy toàn bộ danh sách file văn bản có đuôi mở rộng .txt
        txt_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".txt")]
    
        if not txt_files:
            print(f"[-] Không tìm thấy file .txt nào trong thư mục '{INPUT_DIR}'!")
            print(f"[-] Vui lòng copy các file .txt cần chuyển đổi vào mục '{INPUT_DIR}' và chạy lại.")
            return
    
        print(f"[HỆ THỐNG] Tìm thấy {len(txt_files)} file .txt sẵn sàng xử lý.")
    
        # Tiến hành duyệt qua lần lượt từng file văn bản một
        for filename in sorted(txt_files):
            base_name = os.path.splitext(filename)[0]
            txt_path = os.path.join(INPUT_DIR, filename)
            
            try:
                await process_single_txt_file(txt_path, base_name)
            except Exception as e:
                print(f" [LỖI NGHIÊM TRỌNG] Thất bại khi xử lý file {filename}: {str(e)}")
                # Ghi nhận log lỗi vào file văn bản để rà soát lại sau, không chặn đứng luồng của file khác
                with open("system_error_log.txt", "a", encoding="utf-8") as log:
                    log.write(f"File lỗi: {filename} | Chi tiết lỗi: {str(e)}\n")
    
        print("\n[HOÀN THÀNH TÁC VỤ] Toàn bộ thư mục đã được chuyển đổi sang Audio hoàn tất!")
    
    if __name__ == "__main__":
        asyncio.run(main())
    

## Cách vận hành ứng dụng:

  1. Bạn tạo thư mục `input_txt` nằm cùng cấp với file `main.py`.
  2. Ném toàn bộ các file `.txt` (sách truyện, bài báo, tài liệu dài) vào thư mục `input_txt`.
  3. Chạy lệnh: `python main.py`.
  4. Toàn bộ file kết quả âm thanh `.mp3` chất lượng cao sẽ tự động nằm gọn gàng trong thư mục `output_audio`.



Nếu bạn muốn tiếp tục nâng cấp hệ thống này, cho tôi biết bạn có cần thay đổi cấu hình giọng đọc sang tiếng Anh (`en-US`) hay cần tăng tốc độ đọc lên (Ví dụ: x1.25, x1.5) không?