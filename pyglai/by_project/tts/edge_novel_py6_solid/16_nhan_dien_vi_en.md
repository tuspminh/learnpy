Để ứng dụng của bạn tự động nhận diện chính xác văn bản đầu vào là Tiếng Việt hay Tiếng Anh (từ đó tự động chọn cấu hình Preset và mã Giọng đọc phù hợp mà người dùng không cần chọn tay), giải pháp tốt nhất là tích hợp một thuật toán Nhận diện ngôn ngữ (Language Detection) vào lớp Domain.

Dưới đây là 3 hướng thuật toán từ đơn giản đến chuyên nghiệp, đi kèm mã nguồn nâng cấp cho ứng dụng CLI của bạn.

* * *

## Hướng 1: Thuật toán dựa trên Bản đồ ký tự đặt trưng (Khuyên dùng - Nhẹ & Không cần cài thư viện)

Tiếng Việt là ngôn ngữ duy nhất dùng hệ chữ Latinh có hệ thống dấu thanh và dấu phụ cực kỳ đặc trưng (`đ`, `â`, `ă`, `ê`, `ô`, `ơ`, `ư`, `á`, `à`, `ả`, `ã`, `ạ`,...). Tiếng Anh thuần túy 100% không bao giờ chứa các ký tự này.

  * Ý tưởng: Đếm tỷ lệ xuất hiện của các ký tự đặc trưng Tiếng Việt trong văn bản. Nếu tỷ lệ vượt quá một ngưỡng nhất định (ví dụ: > 0.5% tổng số ký tự), đó là Tiếng Việt. Ngược lại là Tiếng Anh.



* * *

## Hướng 2: Nâng cấp mã nguồn CLI tự động nhận diện ngôn ngữ

Dưới đây là đoạn code cấu trúc lại lớp Domain và hàm thực thi của ứng dụng để tự động nhận dạng ngôn ngữ. Chúng ta sẽ tích hợp Thuật toán bản đồ ký tự trực tiếp vào `TextNormalizer` để đảm bảo chuẩn SOLID.

## 1\. Cập nhật lớp Domain (`domain/text_normalizer.py`)

Bạn thêm hàm `detect_language` vào bộ công cụ xử lý văn bản:
    
    
    class TextNormalizer:
        @staticmethod
        def detect_language(text: str) -> str:
            """
            Thuật toán nhận dạng ngôn ngữ dựa trên dấu phụ Tiếng Việt.
            Trả về: 'vi' (Tiếng Việt) hoặc 'en' (Tiếng Anh)
            """
            if not text or not text.strip():
                return "en" # Mặc định nếu text rỗng
    
            # Danh sách toàn bộ ký tự dấu phụ đặc trưng của Tiếng Việt (chữ thường và chữ hoa)
            vietnamese_chars = set("đâăêôơưáàảãạấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựíìỉĩịóòỏõọúùủũụýỳỷỹỵ"
                                   "ĐÂĂÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶẾỀỂỄỆỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰÍÌIĨỊÓÒỎÕỌÚÙỦŨỤÝỲỶỸỴ")
            
            # Lọc văn bản chỉ giữ lại ký tự chữ
            letters_only = [char for char in text if char.isalpha()]
            if not letters_only:
                return "en"
    
            # Đếm số ký tự Tiếng Việt xuất hiện
            vi_char_count = sum(1 for char in letters_only if char in vietnamese_chars)
            
            # Tính tỷ lệ phần trăm
            vi_ratio = vi_char_count / len(letters_only)
            
            # Nếu tỷ lệ ký tự có dấu > 1% (0.01), khẳng định là Tiếng Việt
            return "vi" if vi_ratio > 0.01 else "en"
    
        @staticmethod
        def normalize(text: str) -> str:
            # ... Giữ nguyên hàm normalize cũ ...
            return text
    

## 2\. Cập nhật cấu hình tự động ánh xạ Giọng đọc trong lớp CLI (`cli_app.py`)

Bây giờ, chúng ta cấu hình lại mã nguồn ở tầng giao diện người dùng để khi người dùng không truyền tham số `--voice`, hệ thống sẽ tự động phân tích văn bản và gán giọng đọc phù hợp.
    
    
    # Cấu hình giọng đọc mặc định cho từng ngôn ngữ
    DEFAULT_LANG_VOICES = {
        "en": "en-US-AriaNeural",  # Mặc định tiếng Anh
        "vi": "vi-VN-HoaiAnNeural" # Mặc định tiếng Việt
    }
    
    # Cập nhật bên trong hàm @click.command() run_cli của bạn:
    @click.option('--voice', '-v', default=None, help='Mã giọng đọc Edge-TTS. Nếu để trống, hệ thống tự động nhận diện ngôn ngữ để chọn giọng.')
    def run_cli(path: str, output: Optional[str], preset: Optional[str], rate: str, pitch: str, voice: Optional[str], normalize: bool):
        
        # ... (Khởi tạo các repo, orchestrator giống như bước trước) ...
    
        for file_p in txt_files:
            # Đọc văn bản gốc trước
            raw_content = file_repo.read_text(file_p)
            
            # 1. Thực hiện nhận dạng ngôn ngữ ngay tại đây
            detected_lang = TextNormalizer.detect_language(raw_content)
            
            # 2. Tự động chọn giọng đọc dựa trên kết quả nhận dạng nếu người dùng không chỉ định --voice
            final_voice = voice if voice else DEFAULT_LANG_VOICES[detected_lang]
            
            lang_name = "Tiếng Việt" if detected_lang == "vi" else "Tiếng Anh"
            click.echo(click.style(f"[*] Nhận diện ngôn ngữ: {lang_name} -> Chọn giọng: {final_voice}", fg="magenta"))
    
            # 3. Tiến hành chuẩn hóa (nếu có flag --normalize)
            if normalize:
                cleaned_content = TextNormalizer.normalize(raw_content)
                file_repo.write_text(file_p, cleaned_content)
                raw_content = cleaned_content # Cập nhật nội dung sạch để chạy TTS
    
            # ... (Đoạn sau tiến hành cắt chunk và chạy edge-tts truyền final_voice vào xử lý bình thường) ...
    

* * *

## Hướng 3: Giải pháp nâng cao sử dụng Thư viện học máy (Machine Learning)

Nếu truyện của bạn là thể loại truyện dịch chèn lẫn lộn từ ngữ hoặc bạn muốn độ chính xác tuyệt đối 100% dựa trên ngữ cảnh phân tích từ ngữ thay vì đếm ký tự, bạn có thể sử dụng thuật toán N-gram thông qua thư viện `langdetect`.

  1. Cài đặt bằng uv:
         
         uv pip install langdetect
         

  2. Cập nhật hàm nhận diện trong Domain:
         
         from langdetect import detect, DetectorFactory
         # Đảm bảo kết quả nhận diện nhất quán giữa các lần chạy
         DetectorFactory.seed = 0 
         
         class TextNormalizer:
             @staticmethod
             def detect_language(text: str) -> str:
                 try:
                     # Thuật toán tự động phân tích tần suất xuất hiện của các cụm từ (N-gram)
                     lang = detect(text) 
                     return "vi" if lang == "vi" else "en"
                 except Exception:
                     return "en" # Trả về tiếng Anh nếu văn bản quá ngắn hoặc lỗi không nhận diện được
         




## 💡 Nên chọn thuật toán nào?

  * Bạn nên chọn Hướng 1 & 2 (Đếm ký tự đặc trưng): Vì nó chạy nhanh tuyệt đối, không làm tăng dung lượng file `.exe` khi đóng gói bằng PyInstaller, và cực kỳ hiệu quả với văn bản truyện dài (do truyện Tiếng Việt luôn luôn có dấu).
  * Chỉ chọn Hướng 3: Nếu bạn có ý định mở rộng phần mềm này cho các ngôn ngữ khác trong tương lai như Tiếng Pháp, Tiếng Đức, Tiếng Nhật,...



Bạn có cần tôi viết lại đoạn tích hợp thuật toán đếm ký tự này vào cấu trúc nạp mã SSML chèn khoảng nghỉ (`<break/>`) ở câu hỏi trước không?