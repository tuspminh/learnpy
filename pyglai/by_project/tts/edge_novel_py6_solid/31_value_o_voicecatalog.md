Dưới đây là cách triển khai danh mục dữ liệu tĩnh (Voice Catalog) được thiết kế theo đúng chuẩn DDD (Domain-Driven Design).

Bằng cách áp dụng mô hình Repository Pattern ở tầng Domain, danh mục này sử dụng trực tiếp hai Value Object `Language` và `Voice` đã hoàn thiện ở bước trước, giúp triệt tiêu hoàn toàn lỗi khai báo nhầm cấu hình.

* * *

## 1\. TẦNG DOMAIN: Khai báo Danh mục và Cổng truy vấn mẫu

Chúng ta tạo một lớp Repository tĩnh thuộc tầng Domain để quản lý việc tra cứu dữ liệu. Lớp này tuân thủ nguyên lý S (Single Responsibility Principle): Chỉ chịu trách nhiệm quản lý danh sách giọng đọc hợp lệ của hệ thống.

`domain/repositories.py`:
    
    
    from typing import List, Optional
    from domain.value_objects import Language, Voice
    
    class StaticVoiceCatalog:
        """
        DDD Static Repository: Quản lý danh mục các giọng đọc AI chất lượng cao.
        Sử dụng trực tiếp các Value Object để đảm bảo tính toàn vẹn dữ liệu.
        """
        
        # Khởi tạo các Value Object Language dùng chung
        LANG_EN = Language(code="en")
        LANG_VI = Language(code="vi")
    
        # Danh mục giọng đọc được kiểm tra nghiêm ngặt (Validation) ngay khi nạp vào bộ nhớ
        _CATALOG: List[Voice] = [
            # NHÓM GIỌNG TIẾNG ANH (Mỹ & Anh)
            Voice(id="en-US-AriaNeural", display_name="en-US-AriaNeural (Nữ Mỹ - Truyền cảm)", language=LANG_EN),
            Voice(id="en-US-JennyNeural", display_name="en-US-JennyNeural (Nữ Mỹ - Cổ tích)", language=LANG_EN),
            Voice(id="en-US-GuyNeural", display_name="en-US-GuyNeural (Nam Mỹ - Trầm ấm)", language=LANG_EN),
            Voice(id="en-US-SteffanNeural", display_name="en-US-SteffanNeural (Nam Mỹ - Cuốn hút)", language=LANG_EN),
            Voice(id="en-GB-SoniaNeural", display_name="en-GB-SoniaNeural (Nữ Anh - Cổ điển)", language=LANG_EN),
            Voice(id="en-GB-RyanNeural", display_name="en-GB-RyanNeural (Nam Anh - Tự nhiên)", language=LANG_EN),
            
            # NHÓM GIỌNG TIẾNG VIỆT
            Voice(id="vi-VN-HoaiAnNeural", display_name="vi-VN-HoaiAnNeural (Nữ Việt - Dịu dàng)", language=LANG_VI),
            Voice(id="vi-VN-NamMinhNeural", display_name="vi-VN-NamMinhNeural (Nam Việt - Trầm hùng)", language=LANG_VI)
        ]
    
        @classmethod
        def get_all(cls) -> List[Voice]:
            """Lấy toàn bộ danh sách giọng đọc phục vụ hiển thị trên giao diện (GUI/CLI)"""
            return cls._CATALOG
    
        @classmethod
        def get_by_id(cls, voice_id: str) -> Optional[Voice]:
            """Tìm kiếm chính xác đối tượng Voice dựa trên mã ID kỹ thuật"""
            for voice in cls._CATALOG:
                if voice.id == voice_id:
                    return voice
            return None
    
        @classmethod
        def get_by_language(cls, language: Language) -> List[Voice]:
            """Lọc danh sách giọng đọc theo đối tượng ngôn ngữ cụ thể"""
            return [voice for voice in cls._CATALOG if voice.language == language]
    
        @classmethod
        def get_default_for_language(cls, language: Language) -> Voice:
            """Lấy giọng đọc mặc định tối ưu nhất cho từng ngôn ngữ"""
            if language.is_vietnamese:
                return cls.get_by_id("vi-VN-HoaiAnNeural")
            return cls.get_by_id("en-US-AriaNeural")
    

* * *

## 2\. TẦNG PRESENTATION: Ứng dụng Catalog vào Giao diện (GUI/CLI)

Nhờ có `StaticVoiceCatalog`, mã nguồn ở tầng hiển thị sẽ không cần phải khai báo các mảng dictionary thô nữa. Dữ liệu được đổ trực tiếp từ Domain sang UI một cách an toàn và nhất quán.

## Minh họa đổ dữ liệu vào QComboBox (PySide6 UI)
    
    
    # Bên trong hàm khởi tạo UI _init_ui() của presentation/main_window.py
    
    from domain.repositories import StaticVoiceCatalog
    
    # Lấy dữ liệu danh mục chuẩn từ Domain
    self.all_voices = StaticVoiceCatalog.get_all()
    
    # Đổ tên hiển thị vào ComboBox trên giao diện
    self.voice_combo = QComboBox()
    self.voice_combo.addItems([v.display_name for v in self.all_voices])
    
    # Khi người dùng bấm nút Xuất Audio, lấy đúng thực thể Voice được chọn:
    def _start_conversion(self):
        selected_index = self.voice_combo.currentIndex()
        # Lấy ra đối tượng Value Object Voice chuẩn chỉ
        voice_value_object = self.all_voices[selected_index]
        
        # Truyền trực tiếp đối tượng an toàn này sang cho tầng Application xử lý
        self._orchestrator.generate_audiobook(..., selected_voice=voice_value_object)
    

## Minh họa xử lý tự động nhận diện giọng trong ứng dụng CLI (Click CLI)
    
    
    # Bên trong hàm thực thi của cli_app.py
    
    from domain.repositories import StaticVoiceCatalog
    from domain.value_objects import Language
    
    # Giả sử thuật toán nhận diện được văn bản đầu vào là Tiếng Việt
    detected_lang = Language(code="vi")
    
    # CLI tự động truy vấn ra giọng đọc mặc định tối ưu từ Catalog
    automatic_voice = StaticVoiceCatalog.get_default_for_language(detected_lang)
    
    click.echo(f"[*] Đã chọn giọng mặc định: {automatic_voice.id}")
    

* * *

## 💡 Lợi ích thu được theo SOLID và DDD

  * Độc lập công nghệ: Catalog này hoàn toàn độc lập với API mạng của `edge-tts`. Nếu Microsoft bổ sung hoặc khai tử một mã giọng đọc, bạn chỉ cần sửa đổi danh sách `_CATALOG` tập trung tại file này mà không cần chạm vào UI hay logic xử lý âm thanh.
  * Ngăn chặn lỗi runtime: Vì `Voice` tự kiểm tra logic khi khởi tạo (`__post_init__`), nếu bạn lỡ tay gõ nhầm mã ngôn ngữ của một giọng đọc mới trong danh sách, hệ thống sẽ quăng lỗi báo động ngay lập tức khi ứng dụng vừa được load, thay vì đợi đến khi người dùng đang xuất file audio mới crash.



Hệ thống quản lý dữ liệu cấu hình của bạn giờ đây đã đạt trạng thái chuẩn mực và chuyên nghiệp. Bạn có muốn tiếp tục nâng cấp thêm bộ Preset (Thể loại truyện) thành một Value Object và tích hợp vào Catalog này không?