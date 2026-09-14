# Preset cho tiếng Anh

Tiếng Anh có rất nhiều giọng neural chất lượng cao, đa dạng hơn tiếng Việt nhiều (Mỹ, Anh, Úc, Ấn...). Dưới đây là một số giọng phổ biến hay dùng:

**Giọng nữ:** `en-US-AriaNeural`, `en-US-JennyNeural`, `en-US-AvaNeural`, `en-GB-SoniaNeural`
**Giọng nam:** `en-US-GuyNeural`, `en-US-ChristopherNeural`, `en-GB-RyanNeural`, `en-US-EricNeural`
**Giọng trẻ em:** `en-US-AnaNeural` (bé gái)

Xem đầy đủ: `edge-tts --list-voices | grep en-US` hoặc `en-GB`

## Preset theo thể loại

```python
PRESETS_EN = {
    "fairy_tale": {
        # Cổ tích: ấm áp, chậm, gợi cảm giác kể chuyện đêm khuya
        "voice": "en-US-AriaNeural",
        "rate": "-15%",
        "pitch": "-2Hz",
        "volume": "+0%",
    },
    "romance": {
        # Ngôn tình / lãng mạn: nhẹ nhàng, tha thiết
        "voice": "en-US-JennyNeural",
        "rate": "-10%",
        "pitch": "+3Hz",
        "volume": "+0%",
    },
    "fantasy_adventure": {
        # Kiếm hiệp / fantasy: mạnh mẽ, uy nghi
        "voice": "en-US-GuyNeural",
        "rate": "+0%",
        "pitch": "-5Hz",
        "volume": "+0%",
    },
    "horror": {
        # Kinh dị: trầm, chậm, rùng rợn
        "voice": "en-US-ChristopherNeural",
        "rate": "-20%",
        "pitch": "-8Hz",
        "volume": "-5%",
    },
    "news": {
        # Tin tức: rõ ràng, chuyên nghiệp
        "voice": "en-US-EricNeural",
        "rate": "+10%",
        "pitch": "+0Hz",
        "volume": "+0%",
    },
    "kids_story": {
        # Truyện thiếu nhi: vui tươi, nhí nhảnh
        "voice": "en-US-AnaNeural",
        "rate": "+5%",
        "pitch": "+8Hz",
        "volume": "+0%",
    },
    "action_adventure": {
        # Hành động: nhanh, kịch tính
        "voice": "en-US-GuyNeural",
        "rate": "+15%",
        "pitch": "+2Hz",
        "volume": "+5%",
    },
    "calm_talk": {
        # Podcast tâm sự / thiền / thư giãn
        "voice": "en-GB-SoniaNeural",
        "rate": "-10%",
        "pitch": "-2Hz",
        "volume": "+0%",
    },
    "comedy": {
        # Hài hước: nhanh, giọng cao, sinh động
        "voice": "en-US-GuyNeural",
        "rate": "+10%",
        "pitch": "+5Hz",
        "volume": "+0%",
    },
    "advertisement": {
        # Quảng cáo: năng lượng cao, cuốn hút
        "voice": "en-US-AvaNeural",
        "rate": "+15%",
        "pitch": "+5Hz",
        "volume": "+10%",
    },
    "british_formal": {
        # Trang trọng kiểu Anh: audiobook, tài liệu học thuật
        "voice": "en-GB-RyanNeural",
        "rate": "-5%",
        "pitch": "+0Hz",
        "volume": "+0%",
    },
}
```

## Sử dụng

```python
import asyncio
import edge_tts


async def speak_with_preset_en(text: str, preset_name: str, output_file: str):
    preset = PRESETS_EN.get(preset_name)
    if not preset:
        print(f"Không tìm thấy preset '{preset_name}'")
        return

    communicate = edge_tts.Communicate(
        text,
        voice=preset["voice"],
        rate=preset["rate"],
        pitch=preset["pitch"],
        volume=preset["volume"],
    )
    await communicate.save(output_file)
    print(f"Đã tạo: {output_file} (preset: {preset_name})")


asyncio.run(
    speak_with_preset_en(
        "Once upon a time, in a kingdom far, far away...",
        "fairy_tale",
        "fairy_tale_demo.mp3",
    )
)
```

**Khác biệt so với tiếng Việt:**
- Tiếng Anh có nhiều giọng hơn nên bạn linh hoạt chọn giọng đặc trưng cho từng thể loại (thay vì chỉ chỉnh pitch/rate trên cùng 1-2 giọng).
- `en-US-GuyNeural` và `en-US-ChristopherNeural` hợp với giọng trầm, nam tính, kịch tính.
- Một số giọng còn hỗ trợ **style** (vui, buồn, giận...) qua SSML nếu bạn dùng `edge-tts` kết hợp SSML nâng cao — cho phép biểu cảm chi tiết hơn là chỉ rate/pitch.

Bạn có muốn mình viết ví dụ kết hợp **nhiều giọng trong 1 file** (ví dụ: người kể chuyện dùng 1 giọng, nhân vật dùng giọng khác) không?