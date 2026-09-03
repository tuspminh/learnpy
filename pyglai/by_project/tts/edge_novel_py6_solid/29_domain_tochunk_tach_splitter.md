Ý tưởng này của bạn hoàn toàn chính xác và vô cùng thông minh. Nó giải quyết triệt để bài toán kiến trúc theo cách thanh lịch nhất:

  1. Giữ Domain sạch sẽ: Hàm `to_chunks()` của Domain thực thể (`StoryDocument`) quay về đúng bản chất ban đầu: Chỉ làm một việc toán học đơn giản là duyệt chuỗi, gom các dòng văn bản (`\n`) lại thành khối sao cho tổng ký tự dưới 2500. Domain hoàn toàn không bị dính líu đến SpaCy hay Underthesea.
  2. Đưa NLP về đúng vị trí (Tầng Tiền xử lý / Hạ tầng): Việc băm nhỏ một khối văn bản thô thành cấu trúc gồm các câu phân tách bằng dấu xuống dòng (`Sentence + \n`) chính là bài toán Dọn dẹp & Tiền xử lý dữ liệu (Data Sanitization).



Dưới đây là cách tái cấu trúc mã nguồn hoàn chỉnh theo đúng tư duy này, đảm bảo chuẩn DDD và SOLID.

* * *

## 📂 Sơ đồ cấu trúc thư mục (DDD)
    
    
    story_reader/
    │
    ├── domain/                      # ─── LỚP DOMAIN (Thuần túy logic chuỗi) ───
    │   ├── interfaces/
    │   │   └── text_preprocessor.py # Giao diện trừu tượng cho bộ tiền xử lý
    │   └── models.py                # Thực thể StoryDocument (Chứa hàm to_chunks dựa trên \n)
    │
    └── infrastructure/              # ─── LỚP HẠ TẦNG (Chi tiết cài đặt công nghệ) ───
        └── nlp_preprocessors.py     # Cài đặt Spacy (EN) và Underthesea (VI) để thêm \n vào mỗi câu
    

* * *

## 1\. TẦNG DOMAIN: Quy tắc băm nhỏ dựa trên dòng (`\n`)

Thực thể Domain lúc này cực kỳ gọn nhẹ. Nó mặc định hiểu rằng văn bản nạp vào đã được chuẩn hóa cấu trúc theo từng dòng rõ ràng.

`domain/models.py`:
    
    
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class StoryDocument:
        name: str
        text: str  # Văn bản đã được tiền xử lý dạng: Câu 1 \n Câu 2 \n Câu 3
    
        def is_empty(self) -> bool:
            return not self.text.strip()
    
        def to_chunks(self, max_chars: int = 2500) -> List[str]:
            """
            S - Single Responsibility: Chỉ chịu trách nhiệm gom các dòng (\n) 
            thành từng khối dưới max_chars để nạp cho API.
            """
            if self.is_empty():
                return []
    
            # Tách văn bản thành danh sách các câu dựa trên dấu \n đã có sẵn
            sentences = [s.strip() for s in self.text.split('\n') if s.strip()]
            
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                # Trường hợp bất khả kháng: Một câu đơn lẻ dài vượt quá max_chars
                if len(sentence) > max_chars:
                    if current_chunk:
                        chunks.append("\n".join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    # Cắt ép buộc câu quá dài theo số ký tự
                    for i in range(0, len(sentence), max_chars):
                        chunks.append(sentence[i:i+max_chars])
                    continue
    
                # Nếu thêm câu này vào mà vượt quá giới hạn khối
                if current_length + len(sentence) + 1 > max_chars:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence) + 1 # +1 đại diện cho dấu \n khi gộp
    
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                
            return chunks
    

`domain/interfaces/text_preprocessor.py`:  
Định nghĩa cổng trừu tượng cho bộ tiền xử lý.
    
    
    from abc import ABC, abstractmethod
    
    class ITextPreprocessor(ABC):
        @abstractmethod
        def preprocess(self, text: str) -> str:
            """Chuẩn hóa văn bản và phân tách cấu trúc bằng dấu '\\n' sau mỗi câu"""
            pass
    

* * *

## 2\. TẦNG INFRASTRUCTURE: Mô hình NLP băm câu và nối bằng `\n`

Lớp hạ tầng chịu trách nhiệm sử dụng mô hình học máy để tìm ranh giới câu, dọn dẹp lỗi chữ hoa/dấu câu, sau đó dùng `\n.join()` để trả về chuỗi cấu trúc chuẩn.

`infrastructure/nlp_preprocessors.py`:
    
    
    import re
    import spacy
    from underthesea import sent_tokenize
    from domain.interfaces import ITextPreprocessor
    
    class SpacyEnglishPreprocessor(ITextPreprocessor):
        """Tiền xử lý văn bản tiếng Anh bằng SpaCy (SOLID - S)"""
        def __init__(self):
            self._nlp = spacy.load("en_core_web_sm", disable=["ner", "textcat", "lemmatizer"])
    
        def preprocess(self, text: str) -> str:
            if not text or not text.strip(): return ""
            
            # Sửa lỗi khoảng trắng quanh dấu câu thô trước
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            
            # Dùng SpaCy tách câu thông minh
            doc = self._nlp(text.strip())
            cleaned_sentences = []
            
            for sent in doc.sents:
                s_text = sent.text.strip()
                if s_text:
                    # Sửa lỗi viết hoa chữ cái đầu câu
                    s_text = s_text[0].upper() + s_text[1:]
                    cleaned_sentences.append(s_text)
                    
            # Trả về văn bản được nối với nhau bằng dấu \n sau mỗi câu
            return "\n".join(cleaned_sentences)
    
    
    class UndertheseaVietnamesePreprocessor(ITextPreprocessor):
        """Tiền xử lý văn bản tiếng Việt bằng Underthesea (SOLID - S)"""
        def preprocess(self, text: str) -> str:
            if not text or not text.strip(): return ""
            
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            
            # Dùng Underthesea tách câu học máy tiếng Việt
            sentences = sent_tokenize(text.strip())
            cleaned_sentences = []
            
            for sent in sentences:
                s_text = sent.strip()
                if s_text:
                    s_text = s_text[0].upper() + s_text[1:]
                    cleaned_sentences.append(s_text)
                    
            return "\n".join(cleaned_sentences)
    

* * *

## 3\. TẦNG APPLICATION: Điều phối luồng xử lý (Orchestrator)

Tại đây, `TTSOrchestrator` sẽ điều phối theo kịch bản: Chạy tiền xử lý NLP trước để lấy chuỗi có định dạng `Sentence + \n` → Khởi tạo Entity `StoryDocument` → Gọi hàm `to_chunks()` để lấy dữ liệu nạp cho AI.
    
    
    from domain.models import StoryDocument
    from domain.interfaces import ITextPreprocessor
    from infrastructure.nlp_preprocessors import SpacyEnglishPreprocessor, UndertheseaVietnamesePreprocessor
    
    class TTSOrchestrator:
        def __init__(self, vi_processor: ITextPreprocessor, en_processor: ITextPreprocessor, tts_service):
            self._vi_processor = vi_processor
            self._en_processor = en_processor
            self._tts_service = tts_service
    
        def _detect_language(self, text: str) -> str:
            vietnamese_chars = set("đâăêôơưáàảãạ...")
            letters = [c for c in text if c.isalpha()]
            if not letters: return "en"
            vi_count = sum(1 for c in letters if c in vietnamese_chars)
            return "vi" if (vi_count / len(letters)) > 0.01 else "en"
    
        async def generate_audiobook(self, raw_text: str, filename: str):
            # 1. Định tuyến bộ tiền xử lý NLP phù hợp theo ngôn ngữ
            lang = self._detect_language(raw_text)
            processor = self._vi_processor if lang == "vi" else self._en_processor
            
            # 2. Tiền xử lý văn bản thô thành cấu trúc chuẩn (Mỗi câu một dòng \n)
            formatted_text = processor.preprocess(raw_text)
            
            # 3. Khởi tạo Domain Entity và để Domain tự xử lý băm nhỏ (to_chunks)
            doc = StoryDocument(name=filename, text=formatted_text)
            chunks = doc.to_chunks(max_chars=2500)
            
            # 4. Duyệt các chunk gửi sang Edge-TTS qua mạng
            for idx, chunk in enumerate(chunks):
                # Với cấu trúc này, khi chunk nạp vào edge-tts, các câu đã cách nhau bằng \n, 
                # Giúp bạn dễ dàng chèn thêm thẻ nghỉ <break/> bằng SSML (như đã thiết kế ở bước trước).
                await self._tts_service.convert_chunk_to_mp3(chunk, ...)
    

## 💡 Ưu điểm tuyệt đối của kiến trúc này:

  * Hàm `to_chunks` cực kỳ trong sáng: Nó chỉ làm đúng một nhiệm vụ toán học thuần túy (SRP). Bạn có thể viết Unit Test cho thuật toán gom cụm này vô cùng dễ dàng bằng cách truyền vào các chuỗi text mẫu có dấu `\n` mà không cần quan tâm máy có cài SpaCy hay không.
  * Tận dụng tối đa dấu `\n` cho SSML: Vì văn bản của mỗi chunk xuất ra từ Domain lúc này luôn giữ cấu trúc phân tách các câu bằng dấu `\n`, bộ sinh mã SSML ở tầng Hạ tầng kỹ thuật chỉ cần làm một lệnh `chunk.split('\n')` rồi chèn thẻ `<break time="1s"/>` vào giữa là giọng đọc AI sẽ ngắt nghỉ vô cùng chuyên nghiệp.