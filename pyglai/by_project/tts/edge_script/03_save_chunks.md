Dưới đây là đoạn code đã được bổ sung logic tự động tạo thư mục và ghi mỗi chunk ra một file `.txt` riêng biệt.
    
    
    import os
    from underthesea import sent_tokenize
    
    def split_text_to_files(file_path, output_dir="output_chunks", max_chars=2000):
        # 1. Đọc nội dung file gốc
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 2. Tách văn bản thành các câu hoàn chỉnh
        sentences = sent_tokenize(text)
        
        # 3. Gom câu thành các chunk dưới 2000 ký tự
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
            
        # 4. Tạo thư mục đầu ra nếu chưa có
        os.makedirs(output_dir, exist_ok=True)
        
        # 5. Ghi từng chunk ra file riêng biệt
        for idx, chunk in enumerate(chunks, 1):
            output_file = os.path.join(output_dir, f"chunk_{idx}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(chunk)
            print(f"Đã lưu: {output_file} ({len(chunk)} ký tự)")
    
    # Sử dụng hàm
    file_name = "van_ban.txt"
    split_text_to_files(file_name, output_dir="output_chunks", max_chars=2000)
    

## Điểm cải tiến

  * Tự động tạo thư mục: Toàn bộ file con sẽ được gom vào thư mục `output_chunks` để không làm rối thư mục làm việc của bạn.
  * Đánh số thứ tự: Các file được lưu theo tên `chunk_1.txt`, `chunk_2.txt` từ đầu đến cuối văn bản.



Nếu bạn muốn, tôi có thể tiếp tục hỗ trợ:

  * Thêm cấu hình giữ nguyên các đoạn văn (paragraphs) thay vì chỉ gom câu.
  * Tự động nén thư mục output thành file ZIP để tiện tải về hoặc chia sẻ.



Bạn muốn tối ưu thêm phần nào cho luồng xử lý này?