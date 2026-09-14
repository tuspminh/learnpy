# Biến thành package cài đặt được với entry point CLI

## 1. Cấu trúc thư mục

```
vi_tts_cli/
├── pyproject.toml
├── README.md
└── src/
    └── vi_tts_cli/
        ├── __init__.py
        └── cli.py
```

## 2. Di chuyển code vào `src/vi_tts_cli/cli.py`

```python
import argparse
import asyncio
import re
import sys
import edge_tts

PRESETS = {
    "N": {"voice": "vi-VN-HoaiMyNeural", "rate": "-10%", "pitch": "-2Hz"},
    "M": {"voice": "vi-VN-NamMinhNeural", "rate": "+0%", "pitch": "-3Hz"},
    "F": {"voice": "vi-VN-HoaiMyNeural", "rate": "+0%", "pitch": "+5Hz"},
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
        prog="vi-tts",
        description="Chuyển file text tiếng Việt (tag [N]/[M]/[F]) thành audio bằng edge-tts.",
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

`src/vi_tts_cli/__init__.py` để trống là được:

```python
```

## 3. `pyproject.toml`

```toml
[project]
name = "vi-tts-cli"
version = "0.1.0"
description = "CLI chuyển file text tiếng Việt thành audio, phân giọng dẫn truyện/nam/nữ, dùng edge-tts"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "edge-tts>=6.1.0",
]

[project.scripts]
vi-tts = "vi_tts_cli.cli:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

Phần quan trọng nhất là `[project.scripts]`:

```toml
[project.scripts]
vi-tts = "vi_tts_cli.cli:main"
```

Nghĩa là: sau khi cài, gõ lệnh `vi-tts` ở terminal sẽ gọi hàm `main()` trong file `src/vi_tts_cli/cli.py`.

## 4. Cài đặt ở chế độ phát triển (editable)

```bash
cd vi_tts_cli
pip install -e .
```

`-e` (editable) nghĩa là bạn sửa code trong `cli.py`, chạy lại `vi-tts` sẽ áp dụng thay đổi ngay, không cần cài lại.

## 5. Dùng lệnh

```bash
vi-tts truyen_tagged.txt -o truyen_audio.mp3
```

Hoạt động y hệt `python cli.py ...` trước đó, chỉ khác là giờ gõ được `vi-tts` từ bất kỳ đâu (miễn còn trong cùng virtual environment đã cài).

## 6. (Tùy chọn) Đóng gói để chia sẻ / đăng lên PyPI

```bash
pip install build twine
python -m build          # tạo dist/*.whl và dist/*.tar.gz
twine upload dist/*      # đăng lên PyPI (cần tài khoản PyPI)
```

Sau đó ai cũng có thể `pip install vi-tts-cli` và dùng lệnh `vi-tts` luôn.

**Lưu ý:**
- Nếu đang dùng `venv`, nhớ activate venv trước khi `pip install -e .`, nếu không lệnh `vi-tts` sẽ không tìm thấy.
- Tên package (`vi-tts-cli`) và tên lệnh (`vi-tts`) có thể đổi tùy ý — chỉ cần sửa cả hai trong `pyproject.toml`.

Bạn có muốn mình thêm subcommand khác vào cùng CLI này không, ví dụ `vi-tts voices` để liệt kê giọng, hay `vi-tts tag` gọi AI tự động gắn tag cho file thô?