# Tách lời dẫn truyện + lời thoại nam/nữ cho file tiếng Việt

Vì tiếng Việt không có cấu trúc rõ ràng để máy tự nhận biết ai đang nói (nam hay nữ) 100% chính xác, mình đề xuất 2 cách: **tự động đoán theo ngữ cảnh** (nhanh, tiện nhưng không hoàn hảo) và **đánh dấu thủ công** (chậm hơn nhưng chính xác tuyệt đối). Bạn nên dùng cách 2 cho truyện quan trọng.

## Cách 1: Tự động đoán giới tính người nói (dựa vào từ khóa ngữ cảnh)

```python
import asyncio
import re
import edge_tts

PRESETS = {
    "narrator": {"voice": "vi-VN-HoaiMyNeural", "rate": "-10%", "pitch": "-2Hz"},
    "male": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "-3Hz"},
    "female": {"voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+5Hz"},
}

# Từ khóa gợi ý giới tính nhân vật, xuất hiện gần câu thoại
MALE_HINTS = ["chàng", "anh", "gã", "hắn", "ông", "chàng trai", "người đàn ông", "cậu"]
FEMALE_HINTS = ["nàng", "cô", "chị", "ả", "bà", "cô gái", "người phụ nữ", "em"]


def guess_gender(context_before: str, context_after: str) -> str:
    """Đoán giới tính dựa vào từ khóa xuất hiện ngay trước/sau câu thoại."""
    text = (context_before[-30:] + " " + context_after[:30]).lower()
    for w in MALE_HINTS:
        if w in text:
            return "male"
    for w in FEMALE_HINTS:
        if w in text:
            return "female"
    return "male"  # mặc định nếu không đoán được


def split_text(content: str):
    """Tách thành list (role, text) dựa vào dấu ngoặc kép "..." """
    pattern = r'"([^"]+)"'
    segments = []
    last_end = 0

    for m in re.finditer(pattern, content):
        before = content[last_end : m.start()]
        if before.strip():
            segments.append(("narrator", before.strip()))

        after = content[m.end() : m.end() + 40]
        gender = guess_gender(before, after)
        segments.append((gender, m.group(1).strip()))

        last_end = m.end()

    remaining = content[last_end:].strip()
    if remaining:
        segments.append(("narrator", remaining))

    return segments


async def process_file(input_file: str, output_file: str = "output.mp3"):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    segments = split_text(content)

    with open(output_file, "wb") as out:
        for i, (role, text) in enumerate(segments, 1):
            preset = PRESETS[role]
            print(f"[{i}/{len(segments)}] ({role}): {text[:50]}...")

            communicate = edge_tts.Communicate(
                text, voice=preset["voice"], rate=preset["rate"], pitch=preset["pitch"]
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"\nHoàn tất: {output_file}")


asyncio.run(process_file("truyen.txt", "truyen_audio.mp3"))
```

**Hạn chế:** Độ chính xác đoán giới tính phụ thuộc từ khóa gần đó (VD: `"Anh yêu em", chàng nói.` → đoán đúng là nam). Nếu văn bản không có từ khóa rõ ràng, sẽ đoán sai.

## Cách 2: Đánh dấu thủ công trong file text (khuyên dùng — chính xác 100%)

Bạn chuẩn bị file `.txt` theo cú pháp đơn giản:

```
[N]Ngày xưa, ở một ngôi làng nhỏ, có một chàng trai tên An sống cùng mẹ.
[M]Mẹ ơi, con phải đi tìm việc làm để nuôi mẹ.
[N]Người mẹ già rơm rớm nước mắt nhìn con trai.
[F]Con hãy cẩn thận, đừng để mẹ phải lo lắng.
[N]An gật đầu rồi bước ra khỏi nhà.
```

Trong đó: `[N]` = lời dẫn (narrator), `[M]` = nhân vật nam (male), `[F]` = nhân vật nữ (female).

```python
import asyncio
import re
import edge_tts

PRESETS = {
    "N": {"voice": "vi-VN-HoaiMyNeural", "rate": "-10%", "pitch": "-2Hz"},  # narrator
    "M": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "-3Hz"},  # nam
    "F": {"voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+5Hz"},  # nữ
}


def parse_tagged_file(content: str):
    """Tách theo tag [N] [M] [F] ở đầu mỗi dòng."""
    lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
    segments = []
    for line in lines:
        m = re.match(r"^\[(N|M|F)\](.*)", line)
        if m:
            role, text = m.group(1), m.group(2).strip()
            if text:
                segments.append((role, text))
        else:
            # Dòng không có tag -> mặc định coi là lời dẫn
            segments.append(("N", line))
    return segments


async def process_tagged_file(input_file: str, output_file: str = "output.mp3"):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    segments = parse_tagged_file(content)

    with open(output_file, "wb") as out:
        for i, (role, text) in enumerate(segments, 1):
            preset = PRESETS[role]
            role_name = {"N": "Dẫn truyện", "M": "Nam", "F": "Nữ"}[role]
            print(f"[{i}/{len(segments)}] ({role_name}): {text[:50]}...")

            communicate = edge_tts.Communicate(
                text, voice=preset["voice"], rate=preset["rate"], pitch=preset["pitch"]
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"\nHoàn tất: {output_file}")


asyncio.run(process_tagged_file("truyen_tagged.txt", "truyen_audio.mp3"))
```

## Kết hợp: dùng AI để tự động gắn tag trước (chính xác gần như thủ công)

Nếu bạn có file truyện thô (chưa gắn tag) và muốn tự động hóa hoàn toàn, cách tốt nhất là dùng một LLM để đọc và gắn tag `[N]/[M]/[F]` giúp bạn trước, sau đó chạy Cách 2. Mình có thể giúp bạn gắn tag cho một đoạn truyện cụ thể nếu bạn dán nội dung vào đây — độ chính xác sẽ cao hơn nhiều so với đoán bằng regex.

Bạn muốn thử theo cách nào — dán thử một đoạn truyện để mình gắn tag mẫu, hay dùng luôn code tự động đoán ở Cách 1?