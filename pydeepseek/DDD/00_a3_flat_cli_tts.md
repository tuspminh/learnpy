# Thiết kế ứng dụng CLI Python chuyển Text thành Audio: Giải pháp hoàn chỉnh

Dưới đây là thiết kế hoàn chỉnh cho một ứng dụng CLI dựa trên **edge-tts + pyav + click**. Tôi sẽ trình bày từ kiến trúc, code đến các điểm cần lưu ý.

---

## 1. Giải thích lựa chọn thư viện

| Thư viện | Vai trò | Tại sao chọn |
|---|---|---|
| **edge-tts** | Lõi TTS | Dùng giọng neural của Microsoft Edge, không cần API Key, hỗ trợ 40+ ngôn ngữ, chất lượng tự nhiên |
| **pyav** | Chuyển đổi định dạng audio | Binding Python của FFmpeg, gọi thuần Python là có thể transcode, resample, đổi kênh |
| **click** | Framework CLI | Phong cách decorator, tự sinh help, validate tham số mạnh, phù hợp xây CLI chuyên nghiệp |

**Cài đặt:**
```bash
pip install edge-tts av click
```

---

## 2. Kiến trúc ứng dụng

```
tts-cli/
├── pyproject.toml
├── README.md
└── src/
    └── tts_cli/
        ├── __init__.py
        ├── __main__.py          # Entry point cho python -m tts_cli
        ├── cli.py               # Định nghĩa lệnh Click
        ├── tts.py               # Wrapper edge-tts (bất đồng bộ)
        ├── audio.py             # Xử lý audio bằng pyav (transcode/resample)
        ├── config.py            # Preset giọng nói phổ biến
        └── exceptions.py        # Exception tùy chỉnh
```

**Ý tưởng cốt lõi:** Tầng CLI chỉ chịu trách nhiệm phân tích tham số và điều phối. **Sinh TTS** và **chuyển đổi audio** được tách thành các module độc lập, dễ test và tái sử dụng.

---

## 3. Cài đặt các module cốt lõi

### 3.1 `tts.py` — Wrapper edge-tts

edge-tts là bất đồng bộ (async), cần `asyncio` điều khiển:

```python
"""Sinh TTS dùng edge-tts."""
import asyncio
from pathlib import Path
import edge_tts


async def generate_speech(
    text: str,
    voice: str,
    output: Path,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> None:
    """Sinh giọng nói từ văn bản và lưu dưới dạng MP3."""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    await communicate.save(str(output))


def generate_speech_sync(text: str, voice: str, output: Path, **kwargs) -> None:
    """Wrapper đồng bộ cho CLI sử dụng."""
    asyncio.run(generate_speech(text, voice, output, **kwargs))


async def list_voices(locale: str | None = None) -> list[dict]:
    """Liệt kê giọng nói có sẵn, có thể lọc theo prefix locale (ví dụ 'en-US')."""
    voices = await edge_tts.list_voices()
    if locale:
        voices = [v for v in voices if v["ShortName"].startswith(locale)]
    return voices
```

**Điểm quan trọng:**
- `rate`/`volume`/`pitch` là tham số gốc edge-tts hỗ trợ, định dạng như `"+20%"`, `"-5Hz"`
- Tên giọng như `en-US-JennyNeural`, `zh-CN-YunxiNeural`, `ko-KR-SunHiNeural`, `vi-VN-HoaiMyNeural`

### 3.2 `audio.py` — Chuyển đổi định dạng bằng pyav

edge-tts xuất ra MP3. Nếu cần WAV/OGG hoặc định dạng khác, dùng pyav chuyển:

```python
"""Chuyển đổi định dạng audio dùng PyAV."""
from pathlib import Path
import av


def convert_audio(
    input_path: Path,
    output_path: Path,
    sample_rate: int = 16000,
    mono: bool = True,
) -> Path:
    """
    Chuyển audio sang định dạng đích dựa trên phần mở rộng của output.

    Hỗ trợ output: .wav (pcm_s16le), .ogg (opus), .mp3 (mp3)
    """
    suffix = output_path.suffix.lower()

    codec_map = {
        ".wav": "pcm_s16le",
        ".ogg": "libopus",
        ".mp3": "libmp3lame",
    }
    codec = codec_map.get(suffix)
    if not codec:
        raise ValueError(f"Định dạng output không hỗ trợ: {suffix}")

    layout = "mono" if mono else "stereo"

    with av.open(str(input_path)) as in_container:
        in_stream = in_container.streams.audio[0]

        with av.open(str(output_path), "w", format=suffix.lstrip(".")) as out_container:
            out_stream = out_container.add_stream(
                codec, rate=sample_rate, layout=layout
            )

            for frame in in_container.decode(in_stream):
                for packet in out_stream.encode(frame):
                    out_container.mux(packet)

            # Flush encoder
            for packet in out_stream.encode(None):
                out_container.mux(packet)

    return output_path
```

**Điểm quan trọng:**
- Dùng `av.open()` mở container input và output
- `add_stream()` chỉ định codec, sample rate, layout kênh
- Phải **flush encoder** (truyền `None` cho `encode()`), nếu không vài frame cuối sẽ mất
- Chuyển định dạng tin nhắn thoại Telegram: OGG Opus, sample rate giữ mặc định

### 3.3 `cli.py` — Định nghĩa lệnh Click

Thiết kế 2 subcommand: `speak` (sinh giọng) và `voices` (liệt kê giọng).

```python
"""Entry point CLI dùng Click."""
import asyncio
from pathlib import Path

import click

from .tts import generate_speech_sync, list_voices
from .audio import convert_audio


@click.group()
@click.version_option()
def cli():
    """CLI Text-to-Audio dùng Edge TTS và PyAV."""


@cli.command()
@click.argument("text")
@click.option(
    "-v", "--voice",
    default="en-US-JennyNeural",
    show_default=True,
    help="Tên giọng (xem lệnh 'voices' để biết các lựa chọn).",
)
@click.option(
    "-o", "--output",
    type=click.Path(path_type=Path),
    default="output.mp3",
    show_default=True,
    help="Đường dẫn file output. Định dạng suy ra từ phần mở rộng.",
)
@click.option(
    "-r", "--rate",
    default="+0%",
    show_default=True,
    help="Tốc độ nói, ví dụ '+20%' hoặc '-10%'.",
)
@click.option(
    "--volume",
    default="+0%",
    show_default=True,
    help="Điều chỉnh âm lượng, ví dụ '+10%'.",
)
@click.option(
    "--pitch",
    default="+0Hz",
    show_default=True,
    help="Điều chỉnh cao độ, ví dụ '+5Hz'.",
)
@click.option(
    "--sample-rate",
    type=int,
    default=16000,
    show_default=True,
    help="Sample rate đích (Hz) cho output không phải MP3.",
)
@click.option(
    "--stereo",
    is_flag=True,
    help="Giữ layout stereo (mặc định: mono).",
)
def speak(text, voice, output, rate, volume, pitch, sample_rate, stereo):
    """
    Chuyển TEXT thành giọng nói.

    Ví dụ:

        tts-cli speak "Hello world" -v en-US-GuyNeural -o hello.wav
    """
    output = Path(output)
    is_mp3 = output.suffix.lower() == ".mp3"

    # Bước 1: Sinh MP3 (edge-tts luôn xuất MP3)
    mp3_path = output if is_mp3 else output.with_suffix(".mp3")

    with click.progressbar(length=2, label="Đang xử lý") as bar:
        click.echo(f"\n→ Đang sinh giọng với voice: {voice}")
        generate_speech_sync(
            text=text,
            voice=voice,
            output=mp3_path,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        bar.update(1)

        # Bước 2: Chuyển đổi nếu cần
        if not is_mp3:
            click.echo(f"\n→ Đang chuyển sang {output.suffix}...")
            convert_audio(
                input_path=mp3_path,
                output_path=output,
                sample_rate=sample_rate,
                mono=not stereo,
            )
            bar.update(1)
            mp3_path.unlink()  # Dọn file MP3 tạm

    click.echo(f"\n✅ Đã lưu tại: {output.resolve()}")


@cli.command()
@click.option(
    "-l", "--locale",
    default=None,
    help="Lọc theo prefix locale, ví dụ 'en-US' hoặc 'vi-VN'.",
)
def voices(locale):
    """
    Liệt kê các giọng có sẵn.

    Ví dụ:

        tts-cli voices -l vi-VN
    """
    voice_list = asyncio.run(list_voices(locale))

    if not voice_list:
        click.echo("Không tìm thấy giọng nào.")
        return

    click.echo(f"{'ShortName':<40} {'Gender':<10} {'Locale'}")
    click.echo("-" * 60)

    for v in voice_list:
        click.echo(f"{v['ShortName']:<40} {v['Gender']:<10} {v['Locale']}")


if __name__ == "__main__":
    cli()
```

**Điểm quan trọng:**
- Dùng `@click.group()` định nghĩa lệnh chính, `@cli.command()` đăng ký subcommand
- `@click.argument("text")` là tham số vị trí, bắt buộc
- `@click.option()` là tham số tùy chọn, dùng `show_default=True` để hiển thị giá trị mặc định
- `click.Path(path_type=Path)` để Click tự validate đường dẫn và chuyển thành `Path`
- `click.progressbar()` cung cấp phản hồi tiến độ (2 bước: sinh + chuyển đổi)

### 3.4 `__main__.py` — Entry point module

```python
from .cli import cli

if __name__ == "__main__":
    cli()
```

Sau đó có thể gọi `python -m tts_cli speak "hello"`.

---

## 4. Ví dụ sử dụng

```bash
# Cách dùng cơ bản: sinh MP3
tts-cli speak "Xin chào thế giới!" -o hello.mp3

# Chỉ định giọng và tốc độ
tts-cli speak "Xin chào Việt Nam" -v vi-VN-HoaiMyNeural -r "+20%" -o tiengviet.mp3

# Sinh WAV (16kHz mono, phù hợp nhận dạng giọng nói)
tts-cli speak "Chuyển sang WAV" -o output.wav --sample-rate 16000

# Sinh OGG (phù hợp tin nhắn thoại Telegram)
tts-cli speak "Tin nhắn thoại" -o voice.ogg

# Liệt kê giọng tiếng Việt
tts-cli voices -l vi-VN
```

**Ví dụ output:**
```
Đang xử lý  [###-------------------------------------]   0%
→ Đang sinh giọng với voice: vi-VN-HoaiMyNeural
Đang xử lý  [##################------------------]  50%
→ Đang chuyển sang .wav...
Đang xử lý  [####################################] 100%

✅ Đã lưu tại: /home/user/output.wav
```

---

## 5. Quyết định thiết kế và các điểm cần lưu ý

### 5.1 Tại sao dùng MP3 làm định dạng trung gian?

edge-tts **chỉ xuất được MP3**. Nên kiến trúc là **MP3 → pyav transcode → định dạng đích**. Nếu đích là MP3 thì bỏ qua bước chuyển đổi.

### 5.2 Các lỗi thường gặp khi transcode bằng pyav

| Lỗi | Cách xử lý |
|---|---|
| Mất frame ở cuối file output | Phải flush encoder bằng `encode(None)` |
| Sample rate không khớp | Chỉ định `rate=sample_rate` khi `add_stream()` |
| Layout kênh sai | Dùng `layout="mono"` hoặc `"stereo"` |
| Lỗi đường dẫn trên Windows | Truyền `str(path)` cho `av.open()` |

### 5.3 Vấn đề Unicode với Click

Trên terminal Windows, `click.echo()` xuất tiếng Việt có thể gặp `UnicodeEncodeError`. Giải pháp:

```bash
# Đặt biến môi trường
set PYTHONUTF8=1
# Hoặc chỉ định runtime
python -X utf8 -m tts_cli speak "Xin chào"
```

Hoặc ép UTF-8 trong code:
```python
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
```

### 5.4 Chiến lược đơn giản hóa xử lý bất đồng bộ

edge-tts là thư viện bất đồng bộ, nhưng CLI là kịch bản đồng bộ. Dùng `asyncio.run()` bọc một lớp là đủ. Nếu sau này cần sinh hàng loạt, có thể chuyển sang `asyncio.gather()` để chạy song song, nhưng CLI gọi một lần thì không cần thiết.

---

## 6. Hướng mở rộng

Nếu CLI này dùng cho production, có thể xem xét:

1. **File cấu hình**: Dùng `click.get_app_dir()` + `tomllib` đọc `~/.config/tts-cli/config.toml` để lưu voice mặc định, thư mục output
2. **Xử lý hàng loạt**: Thêm option `--input-file`, đọc file text và sinh từng dòng
3. **File phụ đề**: edge-tts hỗ trợ `--write-subtitles`, có thể thêm option sinh SRT
4. **Chức năng phát**: Sau khi sinh, dùng `mpv` hoặc `ffplay` phát trực tiếp
5. **Tối ưu progress bar**: `save()` của edge-tts không cung cấp callback tiến độ, nếu sinh đoạn text dài có thể dùng phương thức `stream()` để tự đếm byte

---

## Tổng kết

Cấu trúc ứng dụng CLI này rất rõ ràng:

```
Click (phân tích tham số) → tts.py (edge-tts sinh bất đồng bộ) → audio.py (pyav transcode) → output
```

Mỗi module có trách nhiệm đơn nhất. pyav chỉ can thiệp khi cần chuyển đổi định dạng. edge-tts luôn xuất MP3. Toàn bộ ứng dụng chưa đến 200 dòng code nhưng đã bao phủ quy trình hoàn chỉnh: **sinh TTS + chuyển đổi định dạng + liệt kê giọng nói**.

---

Bạn có muốn tôi:
1. **Viết đầy đủ code từng file** thành một project hoàn chỉnh để bạn copy-paste chạy luôn?
2. **Thêm chức năng đọc file text** để sinh audio từ file dài?
3. **Hướng dẫn đóng gói** thành package cài bằng `pip install`?
4. **Thêm preset giọng tiếng Việt** (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`) làm mặc định?

Nói tôi biết bạn muốn phần nào, tôi sẽ viết chi tiết tiếp bằng tiếng Việt.