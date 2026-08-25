Hệ sinh thái [Underthesea trên GitHub](https://github.com/undertheseanlp/underthesea) bao gồm hai nhóm module chính: Các module xử lý ngôn ngữ truyền thống và các module tính năng nâng cao phục vụ cho hệ thống AI thế hệ mới. [1, 2] 

* * *

## 1\. Nhóm Module Xử Lý Ngôn Ngữ Cốt Lõi (Core NLP Modules)

Đây là các cấu phần cơ bản cấu thành nên thư viện, mỗi module đảm nhận một bài toán xử lý chuỗi và ngữ pháp độc lập: [3, 4] 

  * `pipeline`: Module quản lý luồng dữ liệu. Nó kết nối kết quả của bước này làm đầu vào cho bước tiếp theo (ví dụ: Tách câu ➔ Tách từ ➔ Gán nhãn từ loại).
  * `text_normalize`: Module chuẩn hóa văn bản tiếng Việt chuyên sâu. Giải quyết triệt để lỗi Unicode tổ hợp/dựng sẵn và quy tắc gõ dấu kiểu cũ/mới (như sửa lỗi `hoà` thành `hòa`). [3, 5] 
  * `word_tokenize`: Module tách từ phức. Chuyển đổi chuỗi ký tự thành tập hợp các từ đơn và từ ghép có nghĩa dựa trên mô hình từ điển và học máy. [3, 4] 
  * `pos_tag`: Module gán nhãn từ loại tiếng Việt. Phân tích ngữ pháp để dán nhãn Danh từ (`N`), Động từ (`V`), Tính từ (`A`)... cho từng từ trong câu. [4, 6] 
  * `ner`: Module nhận dạng thực thể có tên. Trích xuất tự động các thông tin về Tên người (`PER`), Địa danh (`LOC`), hoặc Tổ chức (`ORG`). [3, 4] 
  * `classification`: Module phân loại. Chứa thuật toán phân loại văn bản theo chủ đề (thể thao, pháp luật, kinh tế) và phân tích cảm xúc người dùng (Sentiment Analysis). [3, 7, 8] 



* * *

## 2\. Nhóm Module Nâng Cao & Tích Hợp (Advanced Modules)

Từ các phiên bản hiện đại, [Underthesea đã chuyển mình](https://pypi.org/project/underthesea/) thành một bộ công cụ Agentic AI Toolkit mạnh mẽ, bổ sung các module giao tiếp và chuyển đổi ngoại vi: [2, 9] 

  * `agent`: Module điều phối AI Agent. Cho phép xây dựng các trợ lý ảo đa nhiệm tự động gọi chuỗi công cụ (Tools Execution) mà không phụ thuộc vào thư viện bên ngoài.
  * `cloud` / `providers`: Module tích hợp các API ngôn ngữ lớn (LLM) phổ biến như OpenAI, Azure OpenAI, Anthropic Claude và Google Gemini chỉ bằng các thư viện Python tiêu chuẩn (`stdlib`).
  * `models`: Nơi lưu trữ cấu trúc mạng và các tham số trọng số (weights) đã được huấn luyện trước (Pre-trained models) của dự án.
  * `translate`: Module dịch thuật đa ngôn ngữ (cần cài đặt thêm gói `underthesea[deep]`).
  * `tts` (Text-to-Speech): Module chuyển đổi văn bản sạch thành giọng nói tiếng Việt tự nhiên. [2, 5, 10] 



* * *

## 3\. Module Tối Ưu Hiệu Năng (Extension Module)

  * `underthesea-core`: Đây là một package bổ trợ độc lập được [viết bằng ngôn ngữ Rust](https://pypi.org/project/underthesea-core/). Khi tích hợp vào Python, module này giúp tăng tốc độ xử lý dữ liệu lớn (như tính toán suy luận FastText, chuẩn hóa chuỗi) lên gấp nhiều lần so với code Python thuần. [5, 11] 



Nếu bạn muốn tiếp tục nghiên cứu, tôi có thể hỗ trợ:

  * Cách gọi trực tiếp các sub-module nội bộ thay vì dùng hàm rút gọn ngoài wrapper.
  * Hướng dẫn sử dụng module `agent` kết hợp với các LLM để làm chatbot tiếng Việt.



Bạn muốn tìm hiểu sâu vào mã nguồn của module nào cụ thể?

  


[1] [https://github.com](https://github.com/undertheseanlp)

[2] [https://github.com](https://github.com/undertheseanlp/underthesea)

[3] [https://protonx.io](https://protonx.io/courses/66487737f91fdc001a81ce3a/topics/665057c88c287e0019bb800b)

[4] [https://github.com](https://github.com/undertheseanlp/underthesea/wiki/H%E1%BB%8Dc-NLP-n%C3%AAn-b%E1%BA%AFt-%C4%91%E1%BA%A7u-t%E1%BB%AB-%C4%91%C3%A2u%3F)

[5] [https://github.com](https://github.com/undertheseanlp/underthesea/blob/main/NLP.md)

[6] [https://thuedoan.vn](https://thuedoan.vn/xu-ly-ngon-ngu-tieng-viet-voi-underthesea.html)

[7] [https://ongxuanhong.wordpress.com](https://ongxuanhong.wordpress.com/2016/02/06/gioi-thieu-cac-cong-cu-xu-ly-ngon-ngu-tu-nhien/)

[8] [https://underthesea.readthedocs.io](https://underthesea.readthedocs.io/en/latest/readme.html)

[9] [https://www.facebook.com](https://www.facebook.com/groups/miaigroup/posts/2244095006361759/)

[10] [https://github.com](https://github.com/undertheseanlp/underthesea/releases)

[11] [https://pypi.org](https://pypi.org/project/underthesea-core/)