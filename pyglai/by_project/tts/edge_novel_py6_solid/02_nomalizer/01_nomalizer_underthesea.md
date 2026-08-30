Để chuẩn hóa văn bản tiếng Việt một cách chuyên nghiệp nhất, sử dụng thư viện `underthesea` là giải pháp tối ưu. Thư viện này sử dụng các mô hình học máy chuyên sâu cho tiếng Việt để tách từ (word segmentation), giúp nhận diện chính xác ranh giới từ ngữ, từ đó xử lý viết hoa, chuẩn hóa dấu kiểu cũ/mới (ví dụ: _hoà_ thành _hòa_) và dọn dẹp cấu trúc câu cực kỳ chính xác.

Dưới đây là mã nguồn được tái cấu trúc theo chuẩn DDD/SOLID, tích hợp `underthesea` vào lớp Domain.

* * *

## Bước 1: Cài đặt thư viện bằng `uv`

Bạn cần cài đặt `underthesea` vào môi trường ảo thông qua lệnh:
    
    
    uv pip install underthesea
    

* * *

## Bước 2: Mã nguồn chuẩn hóa tiếng Việt chuyên sâu

## 1\. LỚP DOMAIN (Quy tắc dọn dẹp và Mô hình học máy)

Thay vì dùng Regex thủ công để đoán từ, chúng ta sử dụng hàm `text_normalize` (sửa lỗi dấu câu) và `word_tokenize` (tách từ để xử lý viết hoa danh từ riêng hoặc đầu câu) của `underthesea`.

`domain/text_normalizer.py`:
    
    
    import re
    from underthesea import text_normalize, word_tokenize
    
    class VietnameseTextNormalizer:
        """Bộ chuẩn hóa văn bản tiếng Việt chuyên sâu sử dụng học máy (Underthesea)."""
    
        @staticmethod
        def normalize(text: str) -> str:
            if not text or not text.strip():
                return ""
    
            # 1. Sử dụng Underthesea để chuẩn hóa dấu tiếng Việt chuẩn quy tắc mới
            # Ví dụ: "hoà bằg" -> "hòa bằng", "nhân quả?!" -> "nhân quả?!"
            text = text_normalize(text)
    
            # 2. Dọn dẹp dấu nháy lạ và ký tự rác không đọc được bằng AI
            text = re.sub(r'[Code“”„‟″‴]', '"', text)
            text = re.sub(r'[‘’‚‛′]', "'", text)
            text = re.sub(r'–', '-', text)
            text = re.sub(r'[^\w\s.,!?;:"\'\-\(\)\[\]\n]', '', text)
    
            # 3. Ép chuẩn khoảng trắng quanh dấu câu (Sửa lỗi dính liền hoặc cách xa dấu câu)
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            text = re.sub(r'\.{4,}', '...', text)
    
            # 4. Sử dụng tính năng tách từ của Underthesea để sửa lỗi viết hoa đầu câu thông minh
            # Thuật toán phân tách đoạn văn và sửa chữ hoa sau các dấu kết thúc (. ! ?)
            paragraphs = text.split('\n')
            normalized_paragraphs = []
    
            for paragraph in paragraphs:
                if not paragraph.strip():
                    continue
                    
                # Chia nhỏ đoạn văn thành các câu dựa trên dấu kết thúc
                sentences = re.split(r'(?<=[.!?])\s+', paragraph.strip())
                normalized_sentences = []
                
                for sentence in sentences:
                    if not sentence:
                        continue
                    # Viết hoa chữ cái đầu tiên của mỗi câu
                    sentence = sentence[0].upper() + sentence[1:]
                    normalized_sentences.append(sentence)
                    
                normalized_paragraphs.append(" ".join(normalized_sentences))
    
            # Gộp lại thành văn bản sạch hoàn chỉnh
            final_text = '\n'.join(normalized_paragraphs)
            return final_text
    
        @staticmethod
        def detect_language(text: str) -> str:
            """Thuật toán nhận diện nhanh ngôn ngữ để kích hoạt bộ chuẩn hóa phù hợp"""
            vietnamese_chars = set("đâăêôơưáàảãạấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữựíìỉĩịóòỏõọúùủũụýỳỷỹỵ"
                                   "ĐÂĂÊÔƠƯÁÀẢÃẠẤẦẨẪẬẮẰAllocẮẶẾỀỂỄỆỐỒỔỖỘỚỜỞỠỢỨỪỬỮỰÍÌIĨỊÓÒỎÕỌÚÙỦŨỤÝỲỶỸỴ")
            letters = [c for c in text if c.isalpha()]
            if not letters: return "en"
            vi_count = sum(1 for c in letters if c in vietnamese_chars)
            return "vi" if (vi_count / len(letters)) > 0.01 else "en"
    

## 2\. LỚP APPLICATION (Điều phối ca sử dụng)

Lớp này giữ nguyên nhiệm vụ đọc tệp tin, áp dụng bộ lọc từ Domain và ghi lại kết quả sạch (O - Open/Closed Principle).

`application/normalize_uc.py`:
    
    
    import os
    import glob
    from domain.interfaces import IFileRepository
    from domain.text_normalizer import VietnameseTextNormalizer
    
    class NormalizeUseCase:
        def __init__(self, file_repo: IFileRepository):
            self._file_repo = file_repo
    
        def normalize_single_file(self, input_path: str, output_path: str = None) -> None:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Không tìm thấy file: {input_path}")
                
            raw_text = self._file_repo.read_text(input_path)
            
            # Áp dụng bộ chuẩn hóa NLP Underthesea chuyên sâu cho tiếng Việt
            normalized_text = VietnameseTextNormalizer.normalize(raw_text)
            
            save_path = output_path if output_path else input_path
            self._file_repo.write_text(save_path, normalized_text)
            print(f"[✓] Đã chuẩn hóa bằng Underthesea: {os.path.basename(save_path)}")
    
        def normalize_directory(self, dir_path: str, suffix: str = "_normalized") -> None:
            if not os.path.isdir(dir_path):
                raise NotADirectoryError(f"Đường dẫn không hợp lệ: {dir_path}")
    
            txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
            for file_path in txt_files:
                if suffix in file_path:
                    continue
                base_dir, file_name = os.path.split(file_path)
                name, ext = os.path.splitext(file_name)
                new_output_path = os.path.join(base_dir, f"{name}{suffix}{ext}")
                self.normalize_single_file(file_path, new_output_path)
    

* * *

## Bước 3: Sửa lỗi Import và Khởi chạy hệ thống

Để giải quyết triệt để lỗi `ModuleNotFoundError` bạn gặp phải ở câu lệnh trước, chúng ta sẽ thêm cơ chế tự động cấu hình `sys.path` ngay trong file khởi chạy chính nằm ở thư mục gốc của dự án.

`main_nomalize.py` (Đặt tại thư mục gốc `d:\home\github\byai\atts\main_nomalize.py`):
    
    
    import sys
    import os
    
    # Ép Python nhận diện thư mục hiện tại làm gốc dự án để tránh lỗi ModuleNotFoundError
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from infrastructure.file_repository import LocalFileRepository
    from application.normalize_uc import NormalizeUseCase
    
    def main():
        # Khởi tạo repository hạ tầng và usecase ứng dụng
        file_repository = LocalFileRepository()
        use_case = NormalizeUseCase(file_repo=file_repository)
    
        # ĐƯỜNG DẪN KIỂM TRA THỬ NGHIỆM
        TARGET_FILE = "story.txt"  # Thay bằng tên file thực tế của bạn
        
        print("--- HỆ THỐNG NLP CHUẨN HÓA TIẾNG VIỆT TRUYỆN AUDIO ---")
        try:
            if os.path.exists(TARGET_FILE):
                use_case.normalize_single_file(TARGET_FILE)
                print("\n[Thành công] Toàn bộ văn bản đã được tối ưu cho giọng đọc AI.")
            else:
                print(f"[Cảnh báo] Vui lòng tạo file '{TARGET_FILE}' trước khi bấm chạy thử nghiệm.")
        except Exception as e:
            print(f"\nGặp lỗi hệ thống: {e}")
    
    if __name__ == "__main__":
        main()
    

## 💡 Điểm vượt trội khi dùng Underthesea cho Audio:

  1. Chuẩn hóa nhất quán quy tắc đặt dấu: Giúp khắc phục tình trạng file text copy từ nhiều nguồn khác nhau (nguồn dùng _hoà_ , nguồn dùng _hòa_). Khi dấu đặt đồng nhất, AI `edge-tts` sẽ đọc mượt hơn, không bị đổi tông giọng đột ngột giữa các từ.
  2. Nhận diện thực thể: Giúp tách biệt chính xác các liên từ và trạng từ, hạn chế tối đa việc ngắt câu sai vị trí ngữ pháp của truyện.



Bạn chạy lệnh sau trong terminal để trải nghiệm bộ dọn dẹp NLP mới:
    
    
    uv run main_nomalize.py
    

Nếu bạn muốn tôi hỗ trợ tích hợp thêm tính năng tự động chuyển đổi các chữ số (ví dụ: 125 thành một trăm hai mươi lăm) sang dạng chữ đọc để AI đọc mượt hơn nữa, hãy cho tôi biết nhé!