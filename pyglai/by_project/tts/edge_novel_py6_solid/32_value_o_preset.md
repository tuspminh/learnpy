Dưới đây là cách nâng cấp các cấu hình thể loại truyện (Preset) thành một Value Object hoàn chỉnh. Hệ thống sẽ tự động liên kết Preset và Voice lại với nhau thông qua một lớp Catalog Repository tập trung tại tầng Domain, giúp mã nguồn đạt điểm tối đa về tính an toàn và khả năng bảo trì.

* * *

## 1\. TẦNG DOMAIN: Định nghĩa Value Object Preset và Nâng cấp Catalog

Chúng ta sẽ đưa các thông số `rate` và `pitch` vào bên trong cấu trúc tự kiểm tra dữ liệu của Value Object. Mọi thông số dạng chuỗi (như `-10%`, `+2Hz`) sẽ được chuẩn hóa tự động (SOLID - S).

`domain/value_objects.py` (Bổ sung thêm `AudioPreset`):
    
    
    import re
    from dataclasses import dataclass
    
    @dataclass(frozen=True)
    class AudioPreset:
        name: str    # Tên thể loại: "Cổ tích", "Kinh dị"...
        rate: str    # Tốc độ: "-12%"
        pitch: str   # Cao độ: "+3Hz"
    
        def __post_init__(self) -> None:
            """Tự động kiểm tra cấu pháp tham số chuẩn của Edge-TTS"""
            if not self.name.strip():
                raise ValueError("Tên thể loại truyện (Preset Name) không được để trống!")
                
            # Kiểm tra định dạng Rate phải chứa dấu % (Ví dụ: -10%, +0%, +5%)
            if not re.match(r'^[+-]?\d+%$', self.rate):
                raise ValueError(f"Định dạng tốc độ (Rate) sai quy chuẩn: '{self.rate}'. Ví dụ đúng: -10% hoặc +5%")
                
            # Kiểm tra định dạng Pitch phải chứa dấu Hz (Ví dụ: -3Hz, +0Hz, +2Hz)
            if not re.match(r'^[+-]?\d+Hz$', self.pitch):
                raise ValueError(f"Định dạng cao độ (Pitch) sai quy chuẩn: '{self.pitch}'. Ví dụ đúng: -2Hz hoặc +3Hz")
    

* * *

## 2\. TẦNG DOMAIN: Tích hợp Danh mục Preset & Voice tập trung

Bây giờ, chúng ta sẽ mở rộng lớp `StaticVoiceCatalog` trước đó để kiêm nhiệm quản lý toàn bộ cấu hình âm thanh mặc định của hệ thống.

`domain/repositories.py` (Bản nâng cấp toàn diện):
    
    
    from typing import List, Optional
    from domain.value_objects import Language, Voice, AudioPreset
    
    class StaticAudioCatalog:
        """
        DDD Static Repository: Quản lý tập trung toàn bộ danh mục Voice và Preset.
        Bảo vệ hệ thống khỏi các lỗi sai lệch cú pháp cấu hình âm thanh.
        """
        
        # 1. Khởi tạo dữ liệu ngôn ngữ cốt lõi
        LANG_EN = Language(code="en")
        LANG_VI = Language(code="vi")
    
        # 2. Danh mục Giọng đọc (Voice Catalog)
        _VOICES: List[Voice] = [
            Voice(id="en-US-AriaNeural", display_name="en-US-AriaNeural (Nữ Mỹ - Truyền cảm)", language=LANG_EN),
            Voice(id="en-US-JennyNeural", display_name="en-US-JennyNeural (Nữ Mỹ - Cổ tích)", language=LANG_EN),
            Voice(id="en-US-GuyNeural", display_name="en-US-GuyNeural (Nam Mỹ - Trầm ấm)", language=LANG_EN),
            Voice(id="en-GB-SoniaNeural", display_name="en-GB-SoniaNeural (Nữ Anh - Cổ điển)", language=LANG_EN),
            Voice(id="vi-VN-HoaiAnNeural", display_name="vi-VN-HoaiAnNeural (Nữ Việt - Dịu dàng)", language=LANG_VI),
            Voice(id="vi-VN-NamMinhNeural", display_name="vi-VN-NamMinhNeural (Nam Việt - Trầm hùng)", language=LANG_VI)
        ]
    
        # 3. Danh mục Thể loại truyện (Preset Catalog) với thông số đã được đóng gói an toàn
        _PRESETS: List[AudioPreset] = [
            AudioPreset(name="Cổ tích / Thần thoại (Fairy Tales)", rate="-12%", pitch="+3Hz"),
            AudioPreset(name="Kinh dị / Trinh thám (Horror / Thriller)", rate="-16%", pitch="-4Hz"),
            AudioPreset(name="Ngôn tình / Tâm lý xã hội (Drama / Romance)", rate="-15%", pitch="-1Hz"),
            AudioPreset(name="Kiếm hiệp / Tiên hiệp (Fantasy Martial Arts)", rate="-13%", pitch="-3Hz"),
            AudioPreset(name="Truyện cười / Thiếu nhi (Fables / Kids)", rate="-6%", pitch="+5Hz"),
            AudioPreset(name="Mặc định / Phổ thông (Default)", rate="+0%", pitch="+0Hz")
        ]
    
        # --- CÁC PHƯƠNG THỨC TRUY VẤN VOICE ---
        @classmethod
        def get_all_voices(cls) -> List[Voice]:
            return cls._VOICES
    
        @classmethod
        def get_voice_by_id(cls, voice_id: str) -> Optional[Voice]:
            for voice in cls._VOICES:
                if voice.id == voice_id:
                    return voice
            return None
    
        @classmethod
        def get_default_voice(cls, language: Language) -> Voice:
            return cls.get_voice_by_id("vi-VN-HoaiAnNeural") if language.is_vietnamese else cls.get_voice_by_id("en-US-AriaNeural")
    
        # --- CÁC PHƯƠNG THỨC TRUY VẤN PRESET ---
        @classmethod
        def get_all_presets(cls) -> List[AudioPreset]:
            """Trả về danh sách toàn bộ thể loại truyện phục vụ UI hiển thị"""
            return cls._PRESETS
    
        @classmethod
        def get_preset_by_name(cls, name: str) -> Optional[AudioPreset]:
            """Tìm nhanh Preset dựa trên tên thể loại"""
            for preset in cls._PRESETS:
                if preset.name == name:
                    return preset
            return None
    

* * *

## 3\. TẦNG APPLICATION: Kịch bản sử dụng đồng bộ cấu trúc mới

Tầng Application (Orchestrator) lúc này sẽ tiếp nhận hai Value Object an toàn là `Voice` và `AudioPreset` để chuyển tiếp xuống lớp Hạ tầng kỹ thuật vật lý mà không cần bận tâm về tính đúng đắn của dữ liệu.

`application/tts_orchestrator.py`:
    
    
    from domain.value_objects import Voice, AudioPreset
    from domain.models import StoryDocument
    
    class TTSOrchestrator:
        def __init__(self, preprocessor, tts_service):
            self._preprocessor = preprocessor
            self._tts_service = tts_service
    
        async def generate_audiobook(self, raw_text: str, voice: Voice, preset: AudioPreset, output_path: str):
            # 1. Chạy NLP phân tách dòng câu tiền xử lý
            formatted_text = self._preprocessor.preprocess(raw_text)
            
            # 2. Tạo Entity
            doc = StoryDocument(name="book", text=formatted_text)
            
            # 3. Thực hiện băm nhỏ và truyền cặp đôi Value Object xuống tầng Hạ tầng
            chunks = doc.to_chunks(max_chars=2500)
            for chunk in chunks:
                # Tầng hạ tầng vật lý (EdgeTTSService) sẽ bóc tách: voice.id, preset.rate, preset.pitch để nạp vào API mạng
                await self._tts_service.convert_chunk_to_mp3(
                    text=chunk, 
                    voice=voice, 
                    preset=preset, 
                    output_path=output_path
                )
    

* * *

## 💡 Lợi ích thu được từ cấu trúc nâng cấp này:

  1. Chặn đứng lỗi nhập liệu thủ công: Nếu trong quá trình bảo trì, một lập trình viên vô tình gõ nhầm cấu hình dạng: `AudioPreset(name="Kinh dị", rate="-16", pitch="sau-lam")` (thiếu dấu `%` và viết sai `Hz`), PyAV hoặc Edge-TTS sẽ không bị crash ở giữa chu kỳ chạy của người dùng. Hệ thống sẽ báo lỗi ngay tại thời điểm khởi chạy ứng dụng (Compile/Load Time) nhờ hàm `__post_init__`.
  2. Kiến trúc đồng bộ và sạch sẽ: Giao diện đồ họa (PySide6) hay dòng lệnh (Click CLI) giờ đây sẽ đồng nhất gọi chung qua phương thức `StaticAudioCatalog.get_all_presets()` và `StaticAudioCatalog.get_all_voices()`. Việc chỉnh sửa thông số âm thanh cho từng thể loại truyện (ví dụ: muốn truyện kinh dị đọc chậm hơn nữa từ `-16%` xuống `-20%`) chỉ cần sửa duy nhất 1 dòng code tại file Repository này.



Hệ thống Core Logic cho ứng dụng AudioBook của bạn hiện đã đạt mức độ hoàn thiện cực kỳ cao theo đúng mô hình kiến trúc doanh nghiệp! Bạn có cần tôi hỗ trợ viết một bộ Unit Test mẫu để tự động kiểm tra tính hợp lệ của toàn bộ Catalog này không?