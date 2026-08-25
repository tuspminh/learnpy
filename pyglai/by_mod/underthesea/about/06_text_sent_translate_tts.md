Dưới đây là chi tiết về cách hoạt động, cú pháp gọi hàm và ví dụ thực tế cho 4 tính năng bạn vừa liệt kê trong [thư viện Underthesea](https://github.com/undertheseanlp/underthesea).

* * *

## 1\. `text_normalize` (Chuẩn hóa văn bản)

Module này dùng để xử lý các vấn đề đặc thù của tiếng Việt, bao gồm việc sửa sai vị trí dấu thanh (ví dụ: gõ kiểu cũ `hoà` sang kiểu mới `hòa`), chuẩn hóa bảng mã Unicode tổ hợp về Unicode dựng sẵn, và chuẩn hóa địa chỉ viết tắt. [1, 2] 

  * Cú pháp: `text_normalize(text)`
  * Ví dụ: [3] 


    
    
    from underthesea import text_normalize
    
    # Sửa lỗi sai dấu thanh và lỗi gõ nhầm ký tự
    raw = "Ðảm baỏ chất lựơng phòng thí nghịêm hoá học"
    clean = text_normalize(raw)
    
    print(clean)
    # Output: "Đảm bảo chất lượng phòng thí nghiệm hóa học"
    

* * *

## 2\. `sent_tokenize` (Tách câu)

Hàm này nhận diện các dấu kết thúc câu (`.`, `?`, `!`) một cách thông minh. Nó có thể phân biệt được đâu là dấu chấm kết thúc câu thật sự và đâu là dấu chấm viết tắt (như `TP. HCM`, `ThS.`, `đ/c`) để tránh tách nhầm. [1, 4] 

  * Cú pháp: `sent_tokenize(text)`
  * Ví dụ: [3, 4] 


    
    
    from underthesea import sent_tokenize
    
    text = "Taylor cho biết lúc đầu cô cảm thấy ngại với cô bạn thân Amanda nhưng rồi mọi thứ trôi qua nhanh chóng. Amanda cũng thoải mái với mối quan hệ này."
    sentences = sent_tokenize(text)
    
    print(sentences)
    # Output: 
    # [
    #   "Taylor cho biết lúc đầu cô cảm thấy ngại với cô bạn thân Amanda nhưng rồi mọi thứ trôi qua nhanh chóng.",
    #   "Amanda cũng thoải mái với mối quan hệ này."
    # ]
    

* * *

## 3\. `translate` (Dịch thuật)

Module dịch thuật của Underthesea tích hợp các mô hình Deep Learning hỗ trợ dịch hai chiều giữa tiếng Anh và tiếng Việt. Bạn cần cài đặt phiên bản hỗ trợ học sâu bằng lệnh: `pip install underthesea[deep]`. [5, 6] 

  * Cú pháp: `translate(text, source_lang='vi', target_lang='en')` (Mặc định nếu không truyền tham số sẽ tự hiểu là dịch từ `vi` sang `en`).
  * Ví dụ: [5] 


    
    
    from underthesea import translate
    
    # Dịch mặc định từ Việt sang Anh
    en_text = translate("Hà Nội là thủ đô của Việt Nam")
    print(en_text)
    # Output: 'Hanoi is the capital of Vietnam'
    
    # Dịch từ Anh sang Việt bằng cách chỉ định ngôn ngữ
    vi_text = translate("I love Vietnamese food", source_lang='en', target_lang='vi')
    print(vi_text)
    # Output: 'Tôi yêu ẩm thực Việt Nam'
    

* * *

## 4\. `tts` (Text-to-Speech - Chuyển văn bản thành giọng nói)

Module này chuyển đổi chuỗi văn bản tiếng Việt thành file âm thanh nói tự nhiên. Tính năng này hoạt động dựa trên sự tích hợp và tối ưu hóa từ thư viện mã nguồn mở [vietTTS của tác giả NTT123](https://github.com/undertheseanlp/underthesea/blob/main/NLP.md). [6] 

  * Cú pháp thông dụng:


    
    
    from underthesea import tts
    
    text = "Xin chào, chúc bạn một ngày tốt lành."
    
    # Hàm này xử lý ngôn ngữ và xuất ra mảng dữ liệu âm thanh 
    # hoặc lưu trực tiếp thành file .wav tùy cấu hình phiên bản
    audio = tts(text) 
    

_(Lưu ý: Tính năng này yêu cầu cài đặt thêm các thư viện xử lý âm thanh bổ trợ tùy thuộc vào hệ điều hành bạn đang dùng)._ [7] 

Bạn có muốn tôi hướng dẫn cách cài đặt gói `underthesea[deep]` để chạy thử tính năng dịch thuật (`translate`) không?

  


[1] [https://github.com](https://github.com/undertheseanlp/underthesea/blob/main/NLP.md)

[2] [https://github.com](https://github.com/undertheseanlp/text_normalization)

[3] [https://github.com](https://github.com/undertheseanlp/underthesea)

[4] [https://underthesea.readthedocs.io](https://underthesea.readthedocs.io/en/latest/readme.html)

[5] [https://github.com](https://github.com/undertheseanlp/underthesea/blob/main/NLP.md)

[6] [https://github.com](https://github.com/undertheseanlp/underthesea/blob/main/NLP.md)

[7] [https://github.com](https://github.com/undertheseanlp/underthesea/issues/727)