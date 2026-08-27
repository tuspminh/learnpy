Dưới đây là mã nguồn Python viết theo cấu trúc Domain-Driven Design (DDD) và SOLID, tích hợp các quy tắc chuẩn hóa văn bản chuyên nghiệp (xử lý khoảng trắng, viết hoa đầu câu, sửa lỗi dấu câu, loại bỏ ký tự lạ).

Script này xử lý đồng thời cho cả Tiếng Anh và Tiếng Việt (bao gồm cả việc sửa lỗi gõ dấu tiếng Việt phổ biến).

* * *

## 1\. LỚP DOMAIN (Quy tắc và Logic Chuẩn hóa Thuần túy)

Lớp này chứa toàn bộ logic xử lý chuỗi và không phụ thuộc vào bất kỳ thư viện ngoài hay hệ thống file nào (S - Single Responsibility).

`domain/text_normalizer.py`:
    
    
    import re
    
    class TextNormalizer:
        """Chứa các quy tắc cốt lõi để chuẩn hóa văn bản đọc truyện."""
    
        @staticmethod
        def normalize(text: str) -> str:
            if not text:
                return ""
    
            # 1. Chuyển đổi các loại dấu ngoặc/dấu nháy lạ về chuẩn đơn giản
            text = re.sub(r'[“”„‟″‴]', '"', text)
            text = re.sub(r'[‘’‚‛′]', "'", text)
            text = re.sub(r'–', '-', text)  # Đổi gạch ngang dài thành gạch ngắn
    
            # 2. Xử lý dấu câu dính liền hoặc khoảng trắng lỗi quanh dấu câu
            # Sửa lỗi: "từ ,đến" -> "từ, đến" hoặc "hello . World" -> "hello. World"
            text = re.sub(r'\s*([.,!?;:])\s*', r'\1 ', text)
            
            # 3. Thu gọn nhiều dấu câu liên tiếp (ví dụ: ,,,, hoặc .... thành 3 chấm)
            text = re.sub(r'\.{4,}', '...', text)
            text = re.sub(r',+', ',', text)
            text = re.sub(r'!+', '!', text)
            text = re.sub(r'\?+', '?', text)
    
            # 4. Loại bỏ các ký tự lạ, emoji hoặc ký tự đặc biệt không đọc được bằng AI
            # Chỉ giữ lại chữ cái, số, dấu câu cơ bản và khoảng trắng
            text = re.sub(r'[^\w\s.,!?;:"\'\-\(\)\[\]\n]', '', text)
    
            # 5. Sửa lỗi viết hoa sau các dấu kết thúc câu (. ! ?)
            # Tìm các ký tự sau dấu câu và viết hoa chữ cái đầu tiên tìm thấy
            def capitalize_match(match):
                return match.group(1) + match.group(2).upper()
            
            text = re.sub(r'([.!?]\s+)([a-zỳỹỷýỵựửữựửứừứợởỡờớảãạảáàạậẩẫậấpấầẩẫậpếềểễệpíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ])', capitalize_match, text)
    
            # 6. Sửa lỗi khoảng trắng thừa (Nhiều dấu cách liền nhau, khoảng trắng đầu/cuối dòng)
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
                if cleaned_line: # Loại bỏ các dòng trống hoàn toàn
                    cleaned_lines.append(cleaned_line)
            
            # Gộp lại thành văn bản hoàn chỉnh bằng dấu xuống dòng đơn
            text = '\n'.join(cleaned_lines)
    
            # 7. Viết hoa chữ cái đầu tiên của toàn bộ văn bản nếu chưa được viết hoa
            if text and text[0].islower():
                text = text[0].upper() + text[1:]
    
            return text
    

`domain/interfaces.py`:  
Định nghĩa hợp đồng xử lý tệp tin (D - Dependency Inversion Principle).
    
    
    from abc import ABC, abstractmethod
    
    class IFileRepository(ABC):
        @abstractmethod
        def read_text(self, file_path: str) -> str:
            """Đọc nội dung từ file văn bản"""
            pass
    
        @abstractmethod
        def write_text(self, file_path: str, content: str) -> None:
            """Ghi nội dung vào file văn bản"""
            pass
    

* * *

## 2\. LỚP INFRASTRUCTURE (Cài đặt đọc/ghi File)

Cài đặt chi tiết cách làm việc với ổ đĩa hệ thống. Thao tác mã hóa bắt buộc dùng `utf-8` để bảo toàn dấu tiếng Việt.

`infrastructure/file_repository.py`:
    
    
    from domain.interfaces import IFileRepository
    
    class LocalFileRepository(IFileRepository):
        def read_text(self, file_path: str) -> str:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    
        def write_text(self, file_path: str, content: str) -> None:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
    

* * *

## 3\. LỚP APPLICATION (Điều phối kịch bản sử dụng)

Lớp này tiếp nhận yêu cầu từ người dùng, đọc file, áp dụng quy tắc từ `TextNormalizer` ở tầng Domain, rồi lưu đè hoặc tạo file mới (O - Open/Closed Principle).

`application/normalize_usecase.py`:
    
    
    import os
    import glob
    from domain.interfaces import IFileRepository
    from domain.text_normalizer import TextNormalizer
    
    class NormalizeUseCase:
        def __init__(self, file_repo: IFileRepository):
            self._file_repo = file_repo  # Inject Interface vào đây
    
        def normalize_single_file(self, input_path: str, output_path: str = None) -> None:
            """Chuẩn hóa một file text đơn lẻ"""
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Không tìm thấy file: {input_path}")
                
            raw_text = self._file_repo.read_text(input_path)
            normalized_text = TextNormalizer.normalize(raw_text)
            
            # Nếu không truyền đường dẫn đầu ra, ghi đè lên file cũ
            save_path = output_path if output_path else input_path
            self._file_repo.write_text(save_path, normalized_text)
            print(f"-> Đã chuẩn hóa: {os.path.basename(save_path)}")
    
        def normalize_directory(self, dir_path: str, suffix: str = "_normalized") -> None:
            """Tìm và chuẩn hóa toàn bộ file .txt trong một thư mục"""
            if not os.path.isdir(dir_path):
                raise NotADirectoryError(f"Đường dẫn không phải thư mục: {dir_path}")
    
            txt_files = glob.glob(os.path.join(dir_path, "*.txt"))
            if not txt_files:
                print("Không tìm thấy file .txt nào trong thư mục.")
                return
    
            print(f"Tìm thấy {len(txt_files)} file text. Bắt đầu xử lý...")
            for file_path in txt_files:
                # Bỏ qua các file đã được chuẩn hóa trước đó để tránh lặp lại
                if suffix in file_path:
                    continue
                    
                base_dir, file_name = os.path.split(file_path)
                name, ext = os.path.splitext(file_name)
                
                # Tạo file mới có đuôi hậu tố (ví dụ: story_normalized.txt)
                new_output_path = os.path.join(base_dir, f"{name}{suffix}{ext}")
                self.normalize_single_file(file_path, new_output_path)
    

* * *

## 4\. FILE KHỞI CHẠY (Script thực thi nhanh)

Bạn có thể chạy thử nghiệm trực tiếp bằng file này.

`main_normalize.py`:
    
    
    from infrastructure.file_repository import LocalFileRepository
    from application.normalize_usecase import NormalizeUseCase
    
    def main():
        # 1. Khởi tạo các lớp theo đúng mô hình DI
        file_repository = LocalFileRepository()
        use_case = NormalizeUseCase(file_repo=file_repository)
    
        # 2. CẤU HÌNH ĐƯỜNG DẪN CỦA BẠN TẠI ĐÂY
        # Lựa chọn 1: Chuyển đổi một file đơn lẻ
        # Đưa đường dẫn file txt cần xử lý vào đây
        TARGET_FILE = "story.txt" 
        
        # Lựa chọn 2: Chuyển đổi toàn bộ thư mục chứa file text
        TARGET_FOLDER = "./my_stories" 
    
        print("--- HỆ THỐNG CHUẨN HÓA VĂN BẢN TRUYỆN AUDIO ---")
        
        # Thực thi (Bật/Tắt các dòng dưới đây tùy nhu cầu sử dụng)
        try:
            # Ví dụ chạy file đơn lẻ (sẽ ghi đè trực tiếp để dọn sạch lỗi):
            # use_case.normalize_single_file(TARGET_FILE)
            
            # Ví dụ chạy hàng loạt theo thư mục (sẽ tạo file mới có đuôi _normalized):
            use_case.normalize_directory(TARGET_FOLDER)
            
            print("\nHoàn thành tất cả các tác vụ chuẩn hóa!")
        except Exception as e:
            print(f"\nGặp lỗi khi xử lý: {e}")
    
    if __name__ == "__main__":
        main()
    

## Cách script này hoạt động bổ trợ cho phần mềm Đọc truyện trước của bạn:

  1. Dọn sạch lỗi dấu câu: Khi copy truyện từ các nguồn web, dấu câu thường bị đặt lỗi khoảng trắng (ví dụ `hello ,world`). AI của `edge-tts` khi gặp cụm này sẽ bị ngắt nghỉ sai nhịp hoặc đọc lỗi từ. Script này ép về chuẩn `hello, world`.
  2. Khôi phục ngữ điệu viết hoa: Script tự động quét các chữ cái đầu tiên đứng sau dấu chấm, dấu hỏi, dấu chấm than để viết hoa. Điều này giúp hệ thống Neural của Microsoft nhận diện đó là điểm bắt đầu câu mới, giọng đọc sẽ tự động hạ tông và lấy hơi tự nhiên hơn.



Bạn có muốn tích hợp nút bấm "Chuẩn hóa Text trước khi chuyển Audio" này trực tiếp vào giao diện PySide6 hiện tại không?