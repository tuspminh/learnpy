Khi hàm `to_chunks()` bắt buộc phải sử dụng các thư viện NLP chuyên sâu như `underthesea` (cho Tiếng Việt) và `spacy` (cho Tiếng Anh) để cắt câu thông minh, bản chất của hàm này đã thay đổi:

> Từ một hàm tính toán logic chuỗi thuần túy (Domain Model), nó đã trở thành một tác vụ phụ thuộc vào bên thứ ba và có thể tốn tài nguyên phần cứng.

Theo đúng tiêu chuẩn DDD và SOLID, để giải quyết bài toán này mà không làm bẩn (pollute) lớp Domain bởi các chi tiết công nghệ (`underthesea`, `spacy`), chúng ta áp dụng mẫu thiết kế Domain Service kết hợp với Strategy Pattern và Dependency Inversion Principle (DIP).

Dưới đây là cách phân bổ và triển khai code chuẩn chỉnh:

* * *

## 📂 Sơ đồ cấu trúc thư mục mới (DDD)
    
    
    story_reader/
    │
    ├── domain/                      # ─── LỚP DOMAIN (Không chứa mã Spacy/Underthesea) ───
    │   ├── interfaces/
    │   │   └── text_splitter.py     # Định nghĩa Interface trừu tượng (D - DIP)
    │   └── models.py                # Thực thể StoryDocument (Gọi qua Interface)
    │
    └── infrastructure/              # ─── LỚP HẠ TẦNG (Nơi cài đặt công nghệ cụ thể) ───
        └── nlp_text_splitters.py    # Cài đặt chi tiết SpacyTextSplitter và UndertheseaTextSplitter
    

* * *

## 1\. TẦNG DOMAIN: Định nghĩa Interface trừu tượng

Để tuân thủ nguyên lý D (Dependency Inversion Principle), tầng Domain chỉ định nghĩa "hợp đồng" (Interface), không quan tâm thuật toán bên dưới chạy bằng thư viện gì.

`domain/interfaces/text_splitter.py`:
    
    
    from abc import ABC, abstractmethod
    from typing import List
    
    class ITextSplitter(ABC):
        @abstractmethod
        def split_into_chunks(self, text: str, max_chars: int = 2500) -> List[str]:
            """Băm văn bản thành các chunk nhỏ dựa trên ngữ cảnh NLP ngôn ngữ"""
            pass
    

* * *

## 2\. TẦNG INFRASTRUCTURE: Cài đặt chi tiết các bộ thư viện NLP

Tầng này là nơi duy nhất được phép `import spacy` và `import underthesea`. Nếu tương lai bạn đổi sang một thư viện NLP khác, bạn chỉ cần viết thêm một class ở đây mà không cần sửa một dòng code nào trong Domain (O - Open/Closed Principle).

`infrastructure/nlp_text_splitters.py`:
    
    
    import re
    from typing import List
    import spacy
    from underthesea import sent_tokenize  # Dùng hàm tách câu chuyên sâu của underthesea
    
    from domain.interfaces import ITextSplitter
    
    class SpacyEnglishTextSplitter(ITextSplitter):
        """Chi tiết cài đặt tách câu tiếng Anh bằng SpaCy (SOLID - S)"""
        def __init__(self):
            # Tải mô hình nhỏ gọn, tắt các thành phần thừa để tối ưu tốc độ
            self._nlp = spacy.load("en_core_web_sm", disable=["ner", "textcat", "lemmatizer"])
    
        def split_into_chunks(self, text: str, max_chars: int = 2500) -> List[str]:
            if not text or not text.strip(): return []
            
            # Dùng SpaCy băm nhỏ văn bản thành các câu (Sentence Segmentation) chuẩn xác
            doc = self._nlp(text.strip())
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            
            return self._group_sentences_into_chunks(sentences, max_chars)
    
        def _group_sentences_into_chunks(self, sentences: List[str], max_chars: int) -> List[str]:
            """Thuật toán gom các câu thành block dưới max_chars không làm chặt đôi từ"""
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                if current_length + len(sentence) + 1 > max_chars:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence) + 1
    
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            return chunks
    
    
    class UndertheseaVietnameseTextSplitter(ITextSplitter):
        """Chi tiết cài đặt tách câu tiếng Việt bằng Underthesea (SOLID - S)"""
        def split_into_chunks(self, text: str, max_chars: int = 2500) -> List[str]:
            if not text or not text.strip(): return []
            
            # Sử dụng mô hình học máy của Underthesea để nhận diện ranh giới câu tiếng Việt
            sentences = sent_tokenize(text.strip())
            
            # Tái sử dụng thuật toán gom cụm giống tiếng Anh
            # (Để tránh trùng lặp code, hàm gom cụm này có thể đưa vào một Base Class hoặc Helper độc lập)
            return SpacyEnglishTextSplitter()._group_sentences_into_chunks(sentences, max_chars)
    

* * *

## 3\. ĐIỀU PHỐI CHIẾN LƯỢC (Strategy Pattern) Ở TẦNG DOMAIN

Để tự động điều tuyến ngôn ngữ, ta tạo một Domain Service (Dịch vụ nghiệp vụ) đóng vai trò là Context điều phối bộ Strategy phù hợp.

`domain/services/text_splitter_factory.py`:
    
    
    from domain.interfaces import ITextSplitter
    
    class TextSplitterStrategySelector:
        """Tự động nhận diện ngôn ngữ và điều hướng Strategy cắt chữ phù hợp"""
        def __init__(self, vi_splitter: ITextSplitter, en_splitter: ITextSplitter):
            self._vi_splitter = vi_splitter
            self._en_splitter = en_splitter
    
        def get_splitter(self, text: str) -> ITextSplitter:
            # Thuật toán nhận dạng ngôn ngữ thuần túy của Domain (đã viết ở câu hỏi trước)
            vietnamese_chars = set("đâăêôơưáàảãạ...")
            letters = [c for c in text if c.isalpha()]
            if not letters: 
                return self._en_splitter
                
            vi_count = sum(1 for c in letters if c in vietnamese_chars)
            is_vietnamese = (vi_count / len(letters)) > 0.01
            
            return self._vi_splitter if is_vietnamese else self._en_splitter
    

* * *

## 4\. TẦNG APPLICATION: Cách sử dụng trong UseCase điều phối

Tại tầng khởi chạy hệ thống (Composition Root - `main.py`), bạn khởi tạo các đối tượng và "tiêm" (Inject) chúng vào nhau. Tầng Application khi cần băm nhỏ file chỉ việc gọi lớp điều phối:
    
    
    # Bên trong Orchestrator hoặc UseCase ở tầng Application
    class TTSOrchestrator:
        def __init__(self, splitter_selector: TextSplitterStrategySelector, tts_service: ITTSService):
            self._splitter_selector = splitter_selector
            self._tts_service = tts_service
    
        async def process_document(self, raw_text: str, output_path: str):
            # 1. Tự động tìm bộ cắt chữ (Spacy hoặc Underthesea) dựa trên văn bản
            text_splitter = self._splitter_selector.get_splitter(raw_text)
            
            # 2. Thực hiện băm nhỏ thông minh bằng mô hình NLP
            chunks = text_splitter.split_into_chunks(raw_text, max_chars=2500)
            
            # 3. Tiến hành vòng lặp nạp các chunk cho edge-tts như bình thường...
            for chunk in chunks:
                await self._tts_service.convert_chunk_to_mp3(chunk, ...)
    

## 💡 Tổng kết lợi ích theo SOLID

  * Tách biệt hoàn toàn (Decoupling): Lớp logic nghiệp vụ cốt lõi không hề biết sự tồn tại của `spacy` hay `underthesea`. Nó chỉ giao tiếp qua giao diện `ITextSplitter`.
  * Dễ dàng viết Unit Test: Bạn có thể tạo ra một lớp `MockTextSplitter` trả về chuỗi giả lập để test ứng dụng mà không cần phải cài đặt hay tải các mô hình ML nặng nề của Spacy về máy khi chạy kiểm thử.
  * Tuân thủ đúng SRP: Mỗi Class đảm nhận duy nhất một công nghệ tách câu của một ngôn ngữ cụ thể.