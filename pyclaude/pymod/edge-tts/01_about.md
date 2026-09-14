# Thư viện `edge-tts`

`edge-tts` là thư viện Python dùng dịch vụ Text-to-Speech của Microsoft Edge (miễn phí, không cần API key) để chuyển văn bản thành giọng nói tự nhiên, hỗ trợ nhiều ngôn ngữ kể cả tiếng Việt.

## Cài đặt

```bash
pip install edge-tts
```

## 1. Dùng qua dòng lệnh (CLI)

```bash
# Xem danh sách giọng đọc
edge-tts --list-voices

# Chuyển text thành file mp3
edge-tts --text "Xin chào, đây là giọng nói tiếng Việt" --voice vi-VN-HoaiMyNeural --write-media hello.mp3
```

Một vài giọng tiếng Việt phổ biến:
- `vi-VN-HoaiMyNeural` (nữ)
- `vi-VN-NamMinhNeural` (nam)

## 2. Dùng trong code Python (bất đồng bộ)

```python
import asyncio
import edge_tts


async def main():
    text = "Xin chào, tôi đang học thư viện edge-tts."
    voice = "vi-VN-HoaiMyNeural"

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")


asyncio.run(main())
```

## 3. Tùy chỉnh tốc độ, cao độ, âm lượng

```python
communicate = edge_tts.Communicate(
    text,
    voice,
    rate="+20%",  # tăng tốc độ 20%
    volume="+0%",  # âm lượng
    pitch="+0Hz",  # cao độ giọng
)
```

## 4. Lấy danh sách giọng bằng code

```python
import asyncio
import edge_tts


async def list_voices():
    voices = await edge_tts.list_voices()
    for v in voices:
        if v["Locale"].startswith("vi"):
            print(v["ShortName"], v["Gender"])


asyncio.run(list_voices())
```

## 5. Streaming (đọc từng đoạn, không đợi tạo xong toàn bộ file)

```python
async def stream_speech():
    communicate = edge_tts.Communicate(text, voice)
    with open("output.mp3", "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                print(chunk)  # timestamp từng từ - hữu ích cho làm phụ đề
```

## 6. Tạo file phụ đề (subtitle) đi kèm

```python
async def with_subtitle():
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()
    
    with open("output.mp3", "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    
    with open("output.srt", "w", encoding="utf-8") as file:
        file.write(submaker.get_srt())
```

Bạn muốn mình viết luôn một ví dụ hoàn chỉnh (ví dụ: đọc file text lớn, hoặc app đơn giản có giao diện) không?