Dưới đây là đoạn code Python giúp bạn đọc file văn bản và tách thành các phần (chunks) khoảng 2000 ký tự bằng cách gom các câu hoàn chỉnh sử dụng thư viện `underthesea`.

## Cài đặt thư viện

Chạy lệnh sau nếu bạn chưa cài đặt `underthesea`:
    
    
    pip install underthesea
    

## Đoạn code Python
    
    
    from underthesea import sent_tokenize
    
    def split_text_file(file_path, max_chars=2000):
        # Đọc nội dung file text
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Tách văn bản thành các câu tiếng Việt
        sentences = sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Kiểm tra nếu thêm câu mới vượt quá giới hạn 2000 ký tự
            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                # Lưu chunk hiện tại và bắt đầu chunk mới
                chunks.append(current_chunk)
                current_chunk = sentence
                
        # Thêm chunk cuối cùng
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    # Sử dụng hàm
    file_name = "van_ban.txt"
    chunks = split_text_file(file_name, max_chars=2000)
    
    # Hiển thị kết quả từng chunk
    for idx, chunk in enumerate(chunks):
        print(f"--- CHUNK {idx + 1} ({len(chunk)} ký tự) ---")
        print(chunk[:100] + "...\n")  # In ra 100 ký tự đầu của mỗi chunk
    

## Cách thức hoạt động

  * Sử dụng `sent_tokenize` từ [Underthesea](https://github.com/undertheseanlp/underthesea) để nhận diện biên giới câu tiếng Việt chính xác.
  * Duyệt qua từng câu và dồn lại cho đến khi gần đạt mốc 2000 ký tự thì ngắt sang chunk mới để không làm đứt đoạn câu giữa chừng.



Nếu bạn muốn, tôi có thể hỗ trợ:

  * Viết thêm logic ghi các chunk ra các file riêng biệt (`chunk_1.txt`, `chunk_2.txt`,...)
  * Điều chỉnh cách tách theo số lượng từ (tokens) thay vì số ký tự



Hãy cho tôi biết yêu cầu của bạn.