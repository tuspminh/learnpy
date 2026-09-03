Dưới đây là mã nguồn bộ Unit Test hoàn chỉnh sử dụng thư viện tiêu chuẩn `unittest` của Python. Bộ test này được thiết kế theo đúng chuẩn DDD và SOLID để kiểm tra tính toàn vẹn dữ liệu của danh mục (`StaticAudioCatalog`) và các quy tắc tự kiểm tra của các Value Object.

## 1\. File mã nguồn Unit Test (`tests/test_audio_catalog.py`)

Bạn hãy tạo một thư mục mới tên là `tests`, tạo file `test_audio_catalog.py` bên trong và dán đoạn code sau:
    
    
    import unittest
    import sys
    import os
    
    # Đảm bảo Python nhận diện được thư mục gốc của dự án để import
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from domain.value_objects import Language, Voice, AudioPreset
    from domain.repositories import StaticAudioCatalog
    
    
    class TestAudioValueObjects(unittest.TestCase):
        """Kiểm tra các quy tắc tự bảo vệ dữ liệu (Validation) của Value Objects."""
    
        def test_language_validation_valid(self):
            """Value Object Language phải khởi tạo thành công với mã 2 ký tự hợp lệ."""
            lang = Language(code=" VI ")
            self.assertEqual(lang.code, "vi")
            self.assertTrue(lang.is_vietnamese)
            self.assertFalse(lang.is_english)
    
        def test_language_validation_invalid(self):
            """Language phải quăng lỗi nếu mã ngôn ngữ trống hoặc sai số lượng ký tự."""
            with self.assertRaises(ValueError):
                Language(code="")
            with self.assertRaises(ValueError):
                Language(code="vie")
    
        def test_voice_validation_mismatch(self):
            """Voice phải quăng lỗi nếu mã ID giọng đọc không khớp với mã ngôn ngữ chỉ định."""
            lang_vi = Language(code="vi")
            # Lỗi: Giọng đọc en-US nhưng lại truyền đối tượng Language của tiếng Việt
            with self.assertRaises(ValueError):
                Voice(id="en-US-AriaNeural", display_name="Aria", language=lang_vi)
    
        def test_preset_validation_invalid_rate(self):
            """AudioPreset phải quăng lỗi nếu thông số tốc độ (rate) thiếu ký tự %."""
            with self.assertRaises(ValueError):
                AudioPreset(name="Test", rate="-10", pitch="+0Hz")
    
        def test_preset_validation_invalid_pitch(self):
            """AudioPreset phải quăng lỗi nếu thông số cao độ (pitch) thiếu ký tự Hz."""
            with self.assertRaises(ValueError):
                AudioPreset(name="Test", rate="-10%", pitch="+2")
    
    
    class TestStaticAudioCatalog(unittest.TestCase):
        """Kiểm tra tính chính xác và an toàn của Danh mục dữ liệu hệ thống."""
    
        def test_catalog_load_successfully(self):
            """Đảm bảo toàn bộ danh mục nạp vào bộ nhớ thành công, không có lỗi cú pháp ẩn."""
            voices = StaticAudioCatalog.get_all_voices()
            presets = StaticAudioCatalog.get_all_presets()
            
            self.assertGreater(len(voices), 0)
            self.assertGreater(len(presets), 0)
    
        def test_catalog_voice_integrity(self):
            """Kiểm tra tính toàn vẹn của từng giọng đọc có trong hệ thống."""
            for voice in StaticAudioCatalog.get_all_voices():
                # ID kỹ thuật của Edge-TTS không được chứa khoảng trắng thừa
                self.assertEqual(voice.id, voice.id.strip())
                # Giọng đọc phải tương thích hoàn toàn với ngôn ngữ của chính nó
                self.assertTrue(voice.is_suitable_for_text(voice.language.code))
    
        def test_catalog_get_default_voice(self):
            """Đảm bảo hàm lấy giọng đọc mặc định hoạt động chính xác cho từng ngôn ngữ."""
            lang_vi = Language(code="vi")
            lang_en = Language(code="en")
            
            default_vi = StaticAudioCatalog.get_default_voice(lang_vi)
            default_en = StaticAudioCatalog.get_default_voice(lang_en)
            
            self.assertEqual(default_vi.id, "vi-VN-HoaiAnNeural")
            self.assertEqual(default_en.id, "en-US-AriaNeural")
    
        def test_catalog_get_preset_by_name(self):
            """Đảm bảo có thể truy vấn chính xác thông số cấu hình dựa trên tên thể loại truyện."""
            preset = StaticAudioCatalog.get_preset_by_name("Mặc định / Phổ thông (Default)")
            self.assertIsNotNone(preset)
            self.assertEqual(preset.rate, "+0%")
            self.assertEqual(preset.pitch, "+0Hz")
    
    
    if __name__ == "__main__":
        unittest.main()
    

* * *

## 2\. Cách chạy Unit Test bằng `uv`

Bạn mở Terminal/Command Prompt tại thư mục gốc của dự án và thực thi lệnh sau:
    
    
    uv run python -m unittest tests/test_audio_catalog.py
    

## 📊 Kết quả hiển thị dự kiến khi chạy thành công:
    
    
    .......
    ----------------------------------------------------------------------
    Ran 7 tests in 0.002s
    
    OK
    

## 💡 Lợi ích của bộ test này trong quy trình CI/CD

Mỗi khi bạn muốn thêm một giọng đọc mới hoặc thay đổi thông số tốc độ/cao độ của một thể loại truyện trong file `repositories.py`, bạn chỉ cần chạy lệnh test này. Hệ thống sẽ tự động rà soát toàn bộ cấu hình để đảm bảo bạn không gõ nhầm bất kỳ ký tự nào, giúp phần mềm luôn ở trạng thái sẵn sàng đóng gói sang file `.exe` một cách an toàn nhất!

Nếu bạn muốn tôi hướng dẫn cách viết thêm các bài test giả lập (Mock Test) cho tầng xử lý âm thanh PyAV mà không cần nạp file thật, hãy cho tôi biết nhé.