Để chuẩn hóa văn bản tiếng Anh một cách chuyên nghiệp nhất, việc sử dụng thư viện xử lý ngôn ngữ tự nhiên `spacy` là giải pháp tối ưu. Khác với Regex thông thường, `spacy` sử dụng các mô hình học máy (Machine Learning) để phân tích cấu trúc cú pháp của câu.

Hệ thống sẽ dựa vào mô hình để tách câu thông minh (Sentence Segmentation) (không bị nhầm lẫn bởi các dấu chấm viết tắt như _Mr._ , _Dr._ , _approx._), nhận diện từ viết tắt, dọn dẹp khoảng trắng thừa, sửa lỗi viết hoa đầu câu và ép chuẩn các ký tự đặc biệt giúp AI `edge-tts` đọc đúng ngữ điệu.

* * *

## Bước 1: Cài đặt thư viện và Tải mô hình ngôn ngữ bằng `uv`

Bạn cần cài đặt `spacy` và tải mô hình ngôn ngữ tiếng Anh loại nhỏ (nhưng rất nhanh và chính xác) là `en_core_web_sm`:
    
    
    # Cài đặt thư viện spacy
    uv pip install spacy
    
    # Tải mô hình tiếng Anh core
    uv run python -m spacy download en_core_web_sm
    

* * *

## Bước 2: Cập nhật Lớp Domain (`domain/text_normalizer.py`)

Chúng ta sẽ tạo lớp `EnglishTextNormalizer` sử dụng `spacy` để xử lý văn bản tiếng Anh. Lớp này kế thừa đúng tinh thần S (Single Responsibility) trong SOLID.
    
    
    import re
    import spacy
    
    class EnglishTextNormalizer:
        """Bộ chuẩn hóa văn bản tiếng Anh chuyên sâu sử dụng học máy (SpaCy)."""
        
        # Tải mô hình ngôn ngữ tiếng Anh của SpaCy (disable các pipeline không cần thiết để tăng tốc độ)
        _nlp = spacy.load("en_core_web_sm", disable=["ner", "textcat"])
    
        @staticmethod
        def normalize(text: str) -> str:
            if not text or not text.strip():
                return ""
    
            # 1. Ép chuẩn các loại dấu ngoặc, dấu nháy lạ từ web về dạng cơ bản
            text = re.sub(r'[“”„‟″‴]', '"', text)
            text = re.sub(r'[‘’‚‛′]', "'", text)
            text = re.sub(r'–', '-', text)
    
            # 2. Xử lý khoảng trắng lỗi quanh các dấu câu dính liền
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            text = re.sub(r'\.{4,}', '...', text)
    
            # 3. Loại bỏ ký tự lạ hoặc emoji không đọc được bằng AI
            text = re.sub(r'[^\w\s.,!?;:"\'\-\(\)\[\]\n]', '', text)
    
            # 4. Sử dụng SpaCy để phân tách đoạn văn và sửa lỗi ngữ pháp/viết hoa đầu câu
            paragraphs = text.split('\n')
            normalized_paragraphs = []
    
            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue
                    
                # Đưa đoạn văn vào mô hình SpaCy để phân tích cấu trúc câu
                doc = EnglishTextNormalizer._nlp(paragraph.strip())
                normalized_sentences = []
                
                # Duyệt qua từng câu được SpaCy phân tách thông minh (đã nhận diện Mr., Dr.,...)
                for sent in doc.sents:
                    sentence_text = sent.text.strip()
                    if not sentence_text:
                        continue
                    
                    # Viết hoa chữ cái đầu tiên của câu (giữ nguyên các phần sau để tránh hỏng danh từ riêng)
                    sentence_text = sentence_text[0].upper() + sentence_text[1:]
                    normalized_sentences.append(sentence_text)
                    
                # Gộp các câu trong đoạn lại bằng khoảng trắng
                normalized_paragraphs.append(" ".join(normalized_sentences))
    
            # 5. Dọn dẹp khoảng trắng thừa giữa các từ và dòng trống
            final_text = '\n'.join(normalized_paragraphs)
            final_text = re.sub(r'[ \t]+', ' ', final_text)
            
            return final_text
    

* * *

## Bước 3: Đồng bộ kiến trúc bằng mô hình đa ngôn ngữ (Factory Pattern)

Để ứng dụng của bạn (GUI hoặc CLI) tự động nhận diện ngôn ngữ rồi gọi đúng bộ chuẩn hóa (`underthesea` cho tiếng Việt và `spacy` cho tiếng Anh), ta tạo một lớp Factory ở tầng Domain để quản lý:
    
    
    # domain/text_normalizer.py (Mở rộng thêm lớp điều phối)
    
    from domain.text_normalizer_vi import VietnameseTextNormalizer # File chứa underthesea đã viết ở bước trước
    
    class TextNormalizerFactory:
        @staticmethod
        def detect_language(text: str) -> str:
            """Thuật toán nhận diện nhanh ngôn ngữ dựa trên dấu phụ đặc trưng."""
            vietnamese_chars = set("đâăêôơưáàảãạấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựíìỉĩịóòỏõọúùủũụýỳỷỹỵ"
                                   "ĐÂĂÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰẲẴẶẾỀỂỄỆỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰÍÌIĨỊÓÒỎÕỌÚÙỦŨỤÝỲỶỸỴ")
            letters = [c for c in text if c.isalpha()]
            if not letters: 
                return "en"
            vi_count = sum(1 for c in letters if c in vietnamese_chars)
            return "vi" if (vi_count / len(letters)) > 0.01 else "en"
    
        @staticmethod
        def normalize_by_context(text: str) -> str:
            """Tự động chọn bộ chuẩn hóa dựa trên ngôn ngữ văn bản."""
            lang = TextNormalizerFactory.detect_language(text)
            if lang == "vi":
                return VietnameseTextNormalizer.normalize(text)
            else:
                return EnglishTextNormalizer.normalize(text)
    

* * *

## Bước 4: Cập nhật Tầng Ứng dụng (`application/normalize_uc.py`)

Bây giờ bạn chỉ cần sửa hàm xử lý tệp tin để gọi qua `TextNormalizerFactory`. Dù file truyện đầu vào là tiếng Anh hay tiếng Việt, hệ thống đều tự nhận diện và tối ưu hóa hoàn hảo:
    
    
    import os
    from domain.interfaces import IFileRepository
    from domain.text_normalizer import TextNormalizerFactory
    
    class NormalizeUseCase:
        def __init__(self, file_repo: IFileRepository):
            self._file_repo = file_repo
    
        def normalize_single_file(self, input_path: str, output_path: str = None) -> None:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Không tìm thấy file: {input_path}")
                
            raw_text = self._file_repo.read_text(input_path)
            
            # Tự động định tuyến qua bộ chuẩn hóa SpaCy (EN) hoặc Underthesea (VI)
            normalized_text = TextNormalizerFactory.normalize_by_context(raw_text)
            
            save_path = output_path if output_path else input_path
            self._file_repo.write_text(save_path, normalized_text)
            print(f"[✓] Đã chuẩn hóa thành công: {os.path.basename(save_path)}")
    

## 💡 Điểm vượt trội khi dùng SpaCy cho Audio tiếng Anh:

  1. Bảo vệ chữ viết tắt thông minh: Regex thông thường khi thấy dấu chấm ở các từ như `Mr. Smith` hoặc `St. Patrick` sẽ lầm tưởng đó là kết thúc câu và ép viết hoa từ tiếp theo (`Mr. Smith -> Mr. Smith`), đồng thời làm AI ngắt nghỉ hẳn 1 giây sai luật. Mô hình NLP của SpaCy nhận diện được các từ viết tắt này để không băm câu sai vị trí.
  2. Xử lý danh từ riêng: Giữ nguyên trạng thái viết hoa chính xác của các tên riêng, địa danh có sẵn trong văn bản truyện mà không bị thuật toán ép viết hoa lỗi.



Bạn chạy lệnh `uv run main_nomalize.py` để kiểm tra hiệu năng xử lý văn bản tiếng Anh của SpaCy nhé! Nếu bạn cần đóng gói ứng dụng có kèm SpaCy bằng PyInstaller, hãy cho tôi biết vì mô hình dữ liệu của SpaCy cần thêm một vài tham số cấu hình ẩn (Hidden Imports) khi đóng gói file `.exe`.