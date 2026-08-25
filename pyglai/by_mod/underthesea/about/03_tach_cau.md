Để thực hiện tác vụ tách câu và tách đoạn văn bản tiếng Việt, bạn có thể kết hợp phương thức có sẵn của `underthesea` và các kỹ thuật xử lý chuỗi tiêu chuẩn trong Python.

* * *

## 1\. Tách văn bản thành các câu (Sentence Segmentation)

Thư viện [Underthesea](https://github.com/undertheseanlp/underthesea) cung cấp sẵn hàm `sent_tokenize()`. Hàm này sử dụng các quy tắc ngữ pháp và mô hình để nhận biết dấu kết thúc câu (như `.`, `?`, `!`) một cách thông minh, tránh bị tách nhầm ở các dấu chấm viết tắt (ví dụ: `TP.`, `ThS.`). [1, 2, 3] 
    
    
    from underthesea import sent_tokenize
    
    text = "Học viện Công nghệ Bưu chính Viễn thông nằm ở Hà Nội. Hôm nay bạn có đi học không? Ôi, trời đẹp quá!"
    
    # Thực hiện tách câu
    sentences = sent_tokenize(text)
    
    print(sentences)
    # Output: 
    # [
    #   'Học viện Công nghệ Bưu chính Viễn thông nằm ở Hà Nội.', 
    #   'Hôm nay bạn có đi học không?', 
    #   'Ôi, trời đẹp quá!'
    # ]
    

* * *

## 2\. Tách văn bản thành các đoạn (Paragraph Segmentation)

Hiện tại, cấu trúc một đoạn văn bản (Paragraph) thường được phân định bằng ký tự xuống dòng (`\n` hoặc `\n\n`). Underthesea không cần một hàm riêng cho tác vụ này vì bạn có thể xử lý triệt để bằng phương thức `.split()` mặc định cực kỳ nhanh của Python.

Cách xử lý tối ưu:
    
    
    text_doc = """Đoạn văn thứ nhất nói về lợi ích của xử lý ngôn ngữ tự nhiên. Nó giúp máy tính hiểu con người.
    
    Đoạn văn thứ hai nói về thư viện Underthesea. Đây là một thư viện mã nguồn mở rất mạnh mẽ."""
    
    # Tách đoạn bằng dấu xuống dòng và loại bỏ khoảng trắng thừa (nếu có)
    paragraphs = [p.strip() for p in text_doc.split("\n") if p.strip()]
    
    print(paragraphs)
    # Output:
    # [
    #   'Đoạn văn thứ nhất nói về lợi ích của xử lý ngôn ngữ tự nhiên. Nó giúp máy tính hiểu con người.', 
    #   'Đoạn văn thứ hai nói về thư viện Underthesea. Đây là một thư viện mã nguồn mở rất mạnh mẽ.'
    # ]
    

* * *

## 3\. Quy trình kết hợp: Tách đoạn ➔ Tách câu

Trong các bài toán tiền xử lý dữ liệu lớn (như làm chatbot, hệ thống tìm kiếm RAG), quy trình chuẩn là Tách văn bản thành các đoạn trước, sau đó mới Tách từng đoạn thành các câu.
    
    
    from underthesea import sent_tokenize
    
    text_corpus = """Hôm nay trời rất đẹp. Tôi đi dạo ngoài công viên.
    Bạn có muốn tham gia cùng không? Nhớ phản hồi cho tôi sớm nhé!"""
    
    # Bước 1: Tách đoạn
    paragraphs = [p.strip() for p in text_corpus.split("\n") if p.strip()]
    
    # Bước 2: Tách câu trong từng đoạn
    for i, para in enumerate(paragraphs):
        print(f"--- Đoạn {i+1} ---")
        sentences = sent_tokenize(para)
        for j, sentence in enumerate(sentences):
            print(f"  Câu {j+1}: {sentence}")
    

Nếu bạn đang xây dựng một ứng dụng cụ thể, tôi có thể hỗ trợ:

  * Viết hàm làm sạch văn bản (xóa icon, loại bỏ liên kết ẩn) trước khi tiến hành tách câu.
  * Cách cấu hình Chunking văn bản dựa trên giới hạn số lượng từ cho mô hình AI.



Bạn muốn áp dụng việc tách câu này vào bài toán nào?

  


[1] [https://protonx.io](https://protonx.io/courses/66487737f91fdc001a81ce3a/topics/665057c88c287e0019bb800b)

[2] [https://underthesea.readthedocs.io](https://underthesea.readthedocs.io/en/latest/readme.html)

[3] [https://thuedoan.vn](https://thuedoan.vn/xu-ly-ngon-ngu-tieng-viet-voi-underthesea.html)