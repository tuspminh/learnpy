# Kết hợp nhiều giọng trong 1 file (người kể chuyện + nhân vật)

Ý tưởng: chia văn bản thành các đoạn, gán giọng khác nhau cho từng đoạn (dựa vào dấu ngoặc kép hoặc gán thủ công theo nhân vật), sau đó tạo audio riêng cho từng đoạn rồi ghép lại.

## Cách 1: Gán giọng theo cấu trúc script (đơn giản, dễ kiểm soát nhất)

```python
import asyncio
import edge_tts

# Định nghĩa giọng cho từng vai
VOICES = {
    "narrator": {"voice": "en-US-AriaNeural", "rate": "-5%", "pitch": "+0Hz"},
    "hero": {"voice": "en-US-GuyNeural", "rate": "+0%", "pitch": "-3Hz"},
    "villain": {"voice": "en-US-ChristopherNeural", "rate": "-10%", "pitch": "-8Hz"},
    "princess": {"voice": "en-US-JennyNeural", "rate": "+0%", "pitch": "+5Hz"},
}

# Kịch bản: mỗi dòng là (vai, lời thoại)
script = [
    (
        "narrator",
        "Once upon a time, in a faraway kingdom, a young hero stood before the castle gate.",
    ),
    ("hero", "I have come to save the princess!"),
    ("villain", "You think you can defeat me, boy?"),
    ("narrator", "The hero drew his sword, ready for battle."),
    ("princess", "Please, save me from this dreadful dragon!"),
]


async def build_audio_drama(script, output_file="story.mp3"):
    with open(output_file, "wb") as out:
        for i, (role, line) in enumerate(script, 1):
            preset = VOICES.get(role, VOICES["narrator"])
            print(f"[{i}/{len(script)}] ({role}): {line[:40]}...")

            communicate = edge_tts.Communicate(
                line,
                voice=preset["voice"],
                rate=preset["rate"],
                pitch=preset["pitch"],
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"\nHoàn tất: {output_file}")


asyncio.run(build_audio_drama(script))
```

**Ưu điểm:** Kiểm soát chính xác 100% ai nói câu nào — phù hợp khi bạn tự viết/chuẩn hóa kịch bản.

## Cách 2: Tự động tách lời thoại từ truyện (dựa vào dấu ngoặc kép)

Khi bạn có sẵn 1 đoạn văn dạng truyện, không muốn tách thủ công:

```python
import asyncio
import re
import edge_tts

NARRATOR = {"voice": "en-US-AriaNeural", "rate": "-5%", "pitch": "+0Hz"}
DIALOGUE = {"voice": "en-US-GuyNeural", "rate": "+0%", "pitch": "+0Hz"}


def split_narration_and_dialogue(text: str):
    """Tách đoạn văn thành list (loại, nội dung) dựa theo dấu ngoặc kép "..." """
    parts = re.split(r'("(?:[^"\\]|\\.)*")', text)
    segments = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith('"') and part.endswith('"'):
            segments.append(("dialogue", part.strip('"')))
        else:
            segments.append(("narrator", part))
    return segments


async def build_from_story(text: str, output_file="auto_story.mp3"):
    segments = split_narration_and_dialogue(text)

    with open(output_file, "wb") as out:
        for i, (kind, content) in enumerate(segments, 1):
            preset = NARRATOR if kind == "narrator" else DIALOGUE
            print(f"[{i}/{len(segments)}] ({kind}): {content[:50]}...")

            communicate = edge_tts.Communicate(
                content,
                voice=preset["voice"],
                rate=preset["rate"],
                pitch=preset["pitch"],
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"\nHoàn tất: {output_file}")


story_text = """
The old man walked slowly into the tavern. "Give me your strongest ale," he said to the bartender.
The bartender looked up, surprised. "Rough day, old friend?"
"""

asyncio.run(build_from_story(story_text))
```

**Lưu ý:** Cách này chỉ tách được narrator vs. dialogue (2 giọng), chưa phân biệt được *nhân vật nào* đang nói — vì text thường không ghi rõ ai nói câu nào theo cấu trúc máy đọc được.

## Cách 3: Kết hợp AI để tự động gán nhân vật (nâng cao)

Nếu muốn tách chính xác nhân vật nào nói câu nào từ 1 đoạn truyện thô (không có cấu trúc sẵn), bạn cần dùng thêm 1 LLM (ví dụ Claude API) để phân tích văn bản trước, xuất ra JSON dạng `[{"role": "hero", "text": "..."}]`, sau đó đưa vào Cách 1.

Ví dụ prompt gửi cho LLM:
```
Phân tích đoạn truyện sau, tách thành các đoạn narrator/nhân vật, 
xuất JSON dạng [{"role": "narrator" hoặc tên nhân vật, "text": "..."}]:

<đoạn truyện>
```

---

Bạn có văn bản truyện cụ thể muốn mình thử áp dụng luôn không? Nếu có, mình có thể viết code tách + gán giọng theo đúng nội dung đó.