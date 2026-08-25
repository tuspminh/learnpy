Dưới đây là các phương thức (methods) và thuộc tính (properties) cốt lõi của thư viện Underthesea phục vụ cho các tác vụ Xử lý Ngôn ngữ Tự nhiên (NLP) tiếng Việt.

## Các phương thức xử lý NLP chính (Core Methods)

Các phương thức này được import trực tiếp từ package `underthesea` và là những công cụ phổ biến nhất:

  * `word_tokenize(text, format=None)`: Tách từ tiếng Việt. Biến văn bản thành danh sách các từ đơn hoặc từ phức. Nếu dùng `format="text"`, các từ phức sẽ nối với nhau bằng dấu gạch dưới `_`.
  * `pos_tag(text)`: Gán nhãn từ loại. Trả về danh sách các tuple chứa `(từ, nhãn_từ_loại)` như N (Danh từ), V (Động từ), A (Tính từ).
  * `ner(text)`: Nhận dạng thực thể có tên. Xác định các thực thể như B-PER (Tên người), B-LOC (Địa danh), B-ORG (Tổ chức).
  * `classify(text)`: Phân loại văn bản. Tự động dự đoán chủ đề hoặc nhãn của đoạn văn bản dựa trên các mô hình huấn luyện sẵn.
  * `sentiment(text)`: Phân tích cảm xúc. Trả về trạng thái cảm xúc của văn bản (Tích cực/Tiêu cực/Trung lập).
  * `chunking(text)`: Tách cụm từ. Xác định các cụm danh từ (NP) hoặc cụm động từ (VP) trong câu.
  * `dependency_parse(text)`: Phân tích cú pháp phụ thuộc. Trả về cấu trúc cây quan hệ ngữ pháp giữa các từ.



## Thuộc tính cấu hình và Siêu dữ liệu (Properties / Metadata)

Các thuộc tính này giúp bạn kiểm tra phiên bản và cấu hình hệ thống:

  * `__version__`: Chuỗi ký tự hiển thị phiên bản hiện tại của thư viện đang cài đặt.
  * `__file__`: Đường dẫn tuyệt đối đến tệp khởi tạo nguồn của thư viện trên máy tính.



## Ví dụ code minh họa nhanh
    
    
    import underthesea
    
    text = "Học viện Công nghệ Bưu chính Viễn thông nằm ở Hà Nội."
    
    # Sử dụng method tách từ
    print(underthesea.word_tokenize(text))
    # Output: ['Học viện', 'Công nghệ', 'Bưu chính', 'Viễn thông', 'nằm', 'ở', 'Hà Nội', '.']
    
    # Sử dụng method gán nhãn từ loại
    print(underthesea.pos_tag(text))
    # Output: [('Học viện', 'N'), ('Công nghệ', 'N'), ...]
    
    # Xem thuộc tính phiên bản
    print(underthesea.__version__)
    

Nếu bạn muốn đi sâu hơn, tôi có thể:

  * Cung cấp bảng tra cứu toàn bộ nhãn từ loại (POS tags) (như N, V, A, Nu...)
  * Hướng dẫn tùy biến từ điển (custom dictionary) để sửa lỗi tách từ sai



Bạn muốn thực hiện tác vụ nào tiếp theo?