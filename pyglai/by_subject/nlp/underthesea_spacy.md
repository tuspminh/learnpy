Để xử lý phân tách đoạn và phân tách câu cho 2 file riêng biệt (Anh và Việt), giải pháp tối ưu nhất là sử dụng kết hợp spaCy (cho tiếng Anh) và Underthesea (hoặc PyVi cho tiếng Việt).

Quy trình xử lý chung cho cả hai ngôn ngữ: Phân tách đoạn bằng ký tự xuống dòng (`\n`), sau đó đưa từng đoạn vào thư viện để phân tách thành các câu nhỏ.

Dưới đây là hướng dẫn chi tiết và mã nguồn Python hoàn chỉnh cho từng file.

## 1\. Chuẩn bị thư viện

Bạn mở terminal và cài đặt các thư viện cần thiết bằng lệnh sau:
    
    
    pip install underthesea spacy
    python -m spacy download en_core_web_sm
    

* * *

## 2\. Code xử lý File Tiếng Anh (Dùng spaCy)

spaCy sử dụng mô hình ngôn ngữ `en_core_web_sm` để nhận diện cấu trúc ngữ pháp tiếng Anh, giúp phân tách câu chính xác kể cả khi gặp các từ viết tắt như "Mr.", "Dr.", hay "e.g.".
    
    
    import spacy
    
    # Tải mô hình tiếng Anh của spaCy
    nlp = spacy.load("en_core_web_sm")
    
    def process_english_file(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    
        # Bước 1: Phân tách đoạn dựa trên dấu xuống dòng
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    
        print(f"--- KẾT QUẢ XỬ LÝ FILE TIẾNG ANH ({len(paragraphs)} đoạn) ---")
        for i, para in enumerate(paragraphs, 1):
            print(f"\n[Đoạn {i}]: {para}")
            
            # Bước 2: Phân tách câu trong từng đoạn
            doc = nlp(para)
            for j, sentence in enumerate(doc.sents, 1):
                print(f"  -> (Câu {j}): {sentence.text.strip()}")
    
    # Chạy thử nghiệm (Thay 'english.txt' bằng đường dẫn file của bạn)
    # process_english_file("english.txt")
    

* * *

## 3\. Code xử lý File Tiếng Việt (Dùng Underthesea)

Underthesea cung cấp hàm `sent_tokenize` giúp nhận diện ngữ cảnh tiếng Việt rất tốt, không bị nhầm lẫn bởi các dấu chấm trong từ viết tắt tiếng Việt (v.v, ths, ts).
    
    
    from underthesea import sent_tokenize
    
    def process_vietnamese_file(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    
        # Bước 1: Phân tách đoạn dựa trên dấu xuống dòng
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    
        print(f"--- KẾT QUẢ XỬ LÝ FILE TIẾNG VIỆT ({len(paragraphs)} đoạn) ---")
        for i, para in enumerate(paragraphs, 1):
            print(f"\n[Đoạn {i}]: {para}")
            
            # Bước 2: Phân tách câu bằng Underthesea
            sentences = sent_tokenize(para)
            for j, sentence in enumerate(sentences, 1):
                print(f"  -> (Câu {j}): {sentence}")
    
    # Chạy thử nghiệm (Thay 'vietnamese.txt' bằng đường dẫn file của bạn)
    # process_vietnamese_file("vietnamese.txt")
    

* * *

## Lưu ý khi xử lý dữ liệu thực tế

  * Dấu xuống dòng thừa: Nếu file của bạn có nhiều dòng trống liên tiếp, đoạn code `if p.strip()` ở trên đã tự động loại bỏ chúng để tránh tạo ra đoạn rỗng.
  * Xuất kết quả: Nếu bạn muốn lưu kết quả ra file mới thay vì in lên màn hình, hãy cho biết bạn muốn lưu ở định dạng nào (ví dụ: file text mới, file Excel, hoặc JSON).



Nếu bạn muốn tích hợp đoạn code này vào một hệ thống tự động lưu kết quả ra file, hãy chia sẻ định dạng đầu ra mong muốn để mình bổ sung đoạn code ghi file nhé!