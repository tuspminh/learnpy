# Preset gợi ý cho các thể loại đọc

Dựa trên 2 giọng tiếng Việt có sẵn (`vi-VN-HoaiMyNeural` - nữ, `vi-VN-NamMinhNeural` - nam), dưới đây là các preset điều chỉnh `rate`, `pitch`, `volume` phù hợp với từng thể loại:

```python
PRESETS = {
    "co_tich": {
        # Cổ tích: giọng ấm áp, chậm rãi, như bà kể chuyện cho cháu nghe
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "-15%",
        "pitch": "-2Hz",
        "volume": "+0%",
    },
    "ngon_tinh": {
        # Ngôn tình: giọng nữ nhẹ nhàng, tha thiết, hơi chậm để tạo cảm xúc
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "-10%",
        "pitch": "+3Hz",
        "volume": "+0%",
    },
    "kiem_hiep": {
        # Kiếm hiệp: giọng nam mạnh mẽ, dứt khoát, tốc độ vừa phải
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+0%",
        "pitch": "-5Hz",
        "volume": "+0%",
    },
    "kinh_di": {
        # Kinh dị: giọng trầm, chậm, tạo cảm giác rùng rợn, căng thẳng
        "voice": "vi-VN-NamMinhNeural",
        "rate": "-20%",
        "pitch": "-8Hz",
        "volume": "-5%",
    },
    "tin_tuc": {
        # Tin tức / thời sự: rõ ràng, dứt khoát, tốc độ nhanh hơn bình thường
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+10%",
        "pitch": "+0Hz",
        "volume": "+0%",
    },
    "truyen_thieu_nhi": {
        # Truyện thiếu nhi: vui tươi, giọng cao, nhí nhảnh
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+5%",
        "pitch": "+8Hz",
        "volume": "+0%",
    },
    "hoat_hinh_action": {
        # Hành động / phiêu lưu: nhanh, dứt khoát, kịch tính
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+15%",
        "pitch": "+2Hz",
        "volume": "+5%",
    },
    "tam_su_nhe_nhang": {
        # Tâm sự, podcast tâm lý: chậm, trầm ấm, dễ chịu
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "-10%",
        "pitch": "-2Hz",
        "volume": "+0%",
    },
    "hai_huoc": {
        # Truyện hài / châm biếm: nhanh, giọng cao, sinh động
        "voice": "vi-VN-NamMinhNeural",
        "rate": "+10%",
        "pitch": "+5Hz",
        "volume": "+0%",
    },
    "quang_cao": {
        # Quảng cáo / giới thiệu sản phẩm: năng lượng cao, thu hút
        "voice": "vi-VN-HoaiMyNeural",
        "rate": "+15%",
        "pitch": "+5Hz",
        "volume": "+10%",
    },
}
```

## Áp dụng vào code

```python
import asyncio
import edge_tts


async def speak_with_preset(text: str, preset_name: str, output_file: str):
    preset = PRESETS.get(preset_name)
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
    speak_with_preset(
        "Ngày xửa ngày xưa, ở một vương quốc xa xôi...", "co_tich", "co_tich_demo.mp3"
    )
)
```

**Lưu ý:**
- Các giá trị trên là điểm khởi đầu hợp lý — bạn nên nghe thử và tinh chỉnh thêm vì cảm nhận "phù hợp" khá chủ quan.
- `pitch` chỉ hỗ trợ đơn vị `Hz` (dạng `+/-nHz`), không phải phần trăm.
- Nếu cần giọng đa dạng hơn (ví dụ giọng trẻ em, giọng già), tiếng Việt hiện chỉ có 2 giọng neural, nhưng bạn có thể mô phỏng bằng cách kết hợp `pitch` cao/thấp + `rate` khác nhau.

Bạn muốn mình viết thêm phần **tách lời thoại nhân vật** (để mỗi nhân vật trong truyện dùng giọng/preset khác nhau) không?