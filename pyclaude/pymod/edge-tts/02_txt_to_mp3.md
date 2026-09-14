Đây là ví dụ đọc nội dung từ file `.txt` rồi chuyển thành giọng nói bằng `edge-tts`:

```python
import asyncio
import edge_tts


async def text_file_to_speech(
    input_file: str, output_file: str, voice: str = "vi-VN-HoaiMyNeural"
):
    # Đọc nội dung file text
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        print("File rỗng, không có nội dung để đọc.")
        return

    # Chuyển thành giọng nói
    communicate = edge_tts.Communicate(text, voice, rate="+0%")
    await communicate.save(output_file)
    print(f"Đã tạo file âm thanh: {output_file}")


asyncio.run(text_file_to_speech("input.txt", "output.mp3"))
```

## Xử lý file text dài (chia nhỏ theo đoạn)

Với văn bản rất dài, Microsoft có giới hạn độ dài mỗi request, nên nên chia theo đoạn và ghép file lại:

```python
import asyncio
import edge_tts


async def process_large_text(
    input_file: str, output_file: str, voice: str = "vi-VN-HoaiMyNeural"
):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Chia theo đoạn văn (dòng trống)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    with open(output_file, "wb") as out:
        for i, para in enumerate(paragraphs, 1):
            print(f"Đang xử lý đoạn {i}/{len(paragraphs)}...")
            communicate = edge_tts.Communicate(para, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"Hoàn tất: {output_file}")


asyncio.run(process_large_text("truyen_dai.txt", "audiobook.mp3"))
```

## Đọc file text kèm thanh tiến trình (tqdm)

```python
import asyncio
import edge_tts
from tqdm import tqdm


async def process_with_progress(
    input_file: str, output_file: str, voice: str = "vi-VN-HoaiMyNeural"
):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    with open(output_file, "wb") as out:
        for para in tqdm(paragraphs, desc="Chuyển đổi"):
            communicate = edge_tts.Communicate(para, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])


asyncio.run(process_with_progress("truyen_dai.txt", "audiobook.mp3"))
```

**Lưu ý quan trọng:**
- Nếu file text quá dài (vài chục nghìn ký tự trở lên), nên chia nhỏ như ví dụ trên để tránh lỗi timeout/kết nối.
- Cần cài thêm `tqdm` nếu dùng thanh tiến trình: `pip install tqdm`
- Đảm bảo file input đọc đúng encoding UTF-8, nhất là với tiếng Việt có dấu.

Bạn có file text cụ thể muốn mình viết code xử lý riêng không (ví dụ: bỏ qua ký tự đặc biệt, giữ định dạng chương/mục...)?