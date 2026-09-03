Theo đúng tiêu chuẩn kiến trúc DDD (Domain-Driven Design) và các nguyên lý SOLID, câu trả lời ngắn gọn là: Nên tách riêng các hàm này ra thành các class độc lập và phần lớn chúng sẽ thuộc về Tầng Domain (Lớp Lõi Nghiệp Vụ) chứ không phải Infrastructure hay Application.

Mặc dù chúng hoàn toàn có thể viết dưới dạng `staticmethod` (hàm tiện ích không trạng thái), việc gom chung tất cả vào một file `utils.py` bừa bãi sẽ vi phạm nghiêm trọng nguyên lý S (Single Responsibility Principle).

Dưới đây là sơ đồ phân bổ vị trí chi tiết cho từng hàm theo chuẩn kiến trúc Clean Architecture / DDD:

* * *

## 📂 Bản đồ phân bổ cấu trúc thư mục (DDD)
    
    
    story_reader/
    │
    ├── domain/                      # ─── LỚP DOMAIN (Chứa quy tắc nghiệp vụ cốt lõi) ───
    │   ├── services/
    │   │   ├── text_normalizer.py   # S: Chỉ chịu trách nhiệm chuẩn hóa văn bản (Regex/Spacy/Underthesea)
    │   │   ├── lang_detector.py     # S: Chỉ chịu trách nhiệm nhận diện ngôn ngữ
    │   │   └── slug_generator.py    # S: Chỉ chịu trách nhiệm tạo slug từ chuỗi
    │   │
    │   └── models.py                # Chứa thực thể StoryDocument (Có hàm to_chunks() bên trong)
    

* * *

## Đánh giá & Vị trí chi tiết của từng hàm (Hợp thức hóa SOLID)

## 1\. Hàm `to_chunks(text)` ➔ Đặt tại Domain Model (Thực thể)

  * Vị trí: Thuộc lớp Domain, nằm trực tiếp bên trong phương thức của thực thể (Entity) hoặc đối tượng giá trị (Value Object) như `StoryDocument` hoặc `AudioBook`.
  * Lý do (DDD & SOLID): Trong DDD, chúng ta cần tránh mô hình thực thể thiếu máu (_Anemic Domain Model_ \- tức là Class Model chỉ chứa thuộc tính, còn logic nằm ở chỗ khác). Việc chia văn bản lớn thành từng block dưới 2500 ký tự để nạp cho AI là một quy tắc nghiệp vụ bất biến của truyện. Thực thể giữ văn bản đó phải tự biết cách băm nhỏ chính nó (`story.get_chunks()`).



## 2\. Hàm `detect_language(text)` ➔ Đặt tại Domain Service

  * Vị trí: Thuộc lớp Domain, tách thành một Class dịch vụ nghiệp vụ riêng biệt (ví dụ: `LanguageDetectorService`).
  * Lý do (SOLID): Hàm này thực hiện một nhiệm vụ tính toán chuyên biệt (thuật toán đếm ký tự hoặc gọi thư viện học máy). Nó không thay đổi trạng thái của thực thể nào. Việc tách riêng giúp bạn dễ dàng viết Unit Test độc lập và có thể thay đổi thuật toán nhận diện (từ đếm ký tự sang học máy) mà không làm ảnh hưởng đến logic dọn dẹp văn bản (O - Open/Closed Principle).



## 3\. Hàm `normalize(text)` ➔ Đặt tại Domain Service

  * Vị trí: Thuộc lớp Domain, tách thành Class độc lập (ví dụ: `TextNormalizationService`).
  * Lý do: Chuẩn hóa văn bản văn học (sửa lỗi dấu câu, viết hoa đầu câu để AI lấy hơi) là quy tắc thuần túy của bài toán Audiobook, không phụ thuộc vào công nghệ lưu trữ dữ liệu (Database) hay giao diện (UI). Nó là "Trái tim" nghiệp vụ của ứng dụng.



## 4\. Hàm `to_slug(text)` ➔ Đặt tại Domain Service hoặc Application Service (Tùy ngữ cảnh)

  * Trường hợp 1 (Đặt ở Domain): Nếu cái `slug` này được dùng để định danh duy nhất cho một thực thể trong hệ thống (ví dụ: URL để truy cập cuốn truyện `audios/chuyen-co-tich-01.mp3`), nó là logic nghiệp vụ định danh ➔ Thuộc về Domain Service.
  * Trường hợp 2 (Đặt ở Infrastructure): Nếu hàm này chỉ đơn thuần làm sạch tên file thô khi lưu xuống ổ đĩa Windows (bỏ ký tự tiếng Việt để tránh lỗi OS), nó là chi tiết kỹ thuật ➔ Thuộc về Infrastructure. Tuy nhiên, với bài toán Audiobook, đặt nó ở Domain dưới dạng một `SlugGenerator` độc lập là an toàn nhất.



* * *

## Minh họa cách triển khai code thực tế theo chuẩn SOLID

Thay vì viết hàm tự do, ta đóng gói chúng thành các class chuyên trách, sử dụng `staticmethod` nếu chúng không giữ trạng thái (stateless):

`domain/services/text_services.py`:
    
    
    import re
    
    class LanguageDetector:
        """S - Single Responsibility: Chỉ chịu trách nhiệm nhận dạng ngôn ngữ"""
        @staticmethod
        def detect(text: str) -> str:
            vietnamese_chars = set("đâăêôơưáàảãạ...")
            letters = [c for c in text if c.isalpha()]
            if not letters: return "en"
            vi_count = sum(1 for c in letters if c in vietnamese_chars)
            return "vi" if (vi_count / len(letters)) > 0.01 else "en"
    
    class SlugGenerator:
        """S - Single Responsibility: Chỉ chịu trách nhiệm tạo chuỗi URL/Filename an toàn"""
        @staticmethod
        def generate(text: str) -> str:
            text = text.lower().strip()
            text = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', text)
            text = re.sub(r'[đ]', 'd', text)
            # ... các ký tự khác ...
            text = re.sub(r'[^a-z0-9\s-]', '', text)
            return re.sub(r'[\s-]+', '-', text)
    

## 💡 Tại sao tuyệt đối KHÔNG NÊN gom vào tầng `Infrastructure` hoặc `Application`?

  * Tầng Infrastructure (Hạ tầng): Chỉ dùng để chứa các chi tiết cài đặt liên quan đến công nghệ bên ngoài như: Kết nối database, gọi API mạng của Edge-TTS, đọc ghi file vật lý, cấu hình PyAV. Logic tính toán chuỗi/văn bản không được nằm ở đây.
  * Tầng Application (Ứng dụng): Chỉ đóng vai trò là "Người điều phối" (Orchestrator). Nó tiếp nhận request từ giao diện, gọi Domain Model thực hiện logic, rồi gọi Infrastructure để lưu file. Tầng này phải cực kỳ "mỏng" và không chứa bất kỳ thuật toán phân tích chuỗi nào.



Việc bạn phân rã các utils này thành các cấu trúc class nhỏ, nằm trọn vẹn trong tầng Domain, sẽ giúp mã nguồn của bạn đạt điểm tuyệt đối về tính cô lập, dễ bảo trì, và sẵn sàng đóng gói mở rộng mà không sợ phá vỡ hệ thống cũ!