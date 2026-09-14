# Wrap thành CLI đồng bộ (sync)

Dùng `asyncio.run()` bên trong hàm `main()` sync, kết hợp `argparse` để nhận tham số dòng lệnh.

```python
import argparse
import asyncio
import re
import sys
import edge_tts

PRESETS = {
    "N": {"voice": "vi-VN-HoaiMyNeural", "rate": "-10%", "pitch": "-2Hz"},  # narrator
    "M": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "-3Hz"},  # nam
    "F": {"voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+5Hz"},  # nữ
}

ROLE_NAMES = {"N": "Dẫn truyện", "M": "Nam", "F": "Nữ"}


def parse_tagged_file(content: str):
    lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
    segments = []
    for line in lines:
        m = re.match(r"^\[(N|M|F)\](.*)", line)
        if m:
            role, text = m.group(1), m.group(2).strip()
            if text:
                segments.append((role, text))
        else:
            segments.append(("N", line))
    return segments


async def process_tagged_file(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    segments = parse_tagged_file(content)
    if not segments:
        print("Không tìm thấy nội dung hợp lệ trong file.")
        return

    with open(output_file, "wb") as out:
        for i, (role, text) in enumerate(segments, 1):
            preset = PRESETS[role]
            print(f"[{i}/{len(segments)}] ({ROLE_NAMES[role]}): {text[:50]}...")

            communicate = edge_tts.Communicate(
                text, voice=preset["voice"], rate=preset["rate"], pitch=preset["pitch"]
            )
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out.write(chunk["data"])

    print(f"\nHoàn tất: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Chuyển file text tiếng Việt (có tag [N]/[M]/[F]) thành audio."
    )
    parser.add_argument("input", help="Đường dẫn file text đầu vào (.txt)")
    parser.add_argument(
        "-o",
        "--output",
        default="output.mp3",
        help="Đường dẫn file audio đầu ra (mặc định: output.mp3)",
    )
    args = parser.parse_args()

    try:
        asyncio.run(process_tagged_file(args.input, args.output))
    except FileNotFoundError:
        print(f"Lỗi: không tìm thấy file '{args.input}'")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nĐã hủy.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Cách dùng

```bash
python tts_cli.py truyen_tagged.txt -o truyen_audio.mp3
```

Hoặc dùng output mặc định (`output.mp3`):

```bash
python tts_cli.py truyen_tagged.txt
```

**Giải thích cách wrap async → sync:**
- `asyncio.run(coro)` tạo event loop mới, chạy coroutine `process_tagged_file()` cho đến khi xong, rồi tự đóng loop — đây là cách chuẩn để gọi code `async` từ một hàm `sync` (như `main()` trong CLI).
- Không gọi `asyncio.run()` lồng nhau (VD bên trong 1 async function khác) — sẽ bị lỗi `RuntimeError: asyncio.run() cannot be called from a running event loop`.
- Toàn bộ phần `argparse`, `try/except`, `sys.exit()` đều là code sync bình thường — chỉ có đúng 1 điểm chuyển sang async là dòng gọi `asyncio.run(...)`.

**Muốn biến thành package cài đặt được (`pip install -e .`) với entry point kiểu `edge-tts` không?** Mình có thể hướng dẫn thêm `pyproject.toml` + `console_scripts`.