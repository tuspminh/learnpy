> Py draft
    bạn là lập trình viên python, thiét kế chi tiếp app sau theo kiến trúc clean, domain driven design và nguyên lý solid:
    app chuyển text thành voice, tiếng việt hoặc tiếng anh. đầu vào là file text hoặc folder chứa các file text.
    app cli dùng click để nhận tham số dòng lệnh. có các tham số sau : file/ folder, tts-engine, voice, rate, volume, pitch, --no-merge (mặc định thì merge các file audio của các chunk của file text thành một file audio, nếu có --no-merge thì không), chunk-size(mặc định 2000 ký tự, max 2500)
    có các lệnh hiển thị engine, voice để người dùng lấy và nhập vô dòng lệnh như engine  --list , engine engine-name voices,....
    output:  chunk audio lưu trong file-text-name/, merged-audio thì lưu chung thư mục với file text.
    xử lý file text, dùng underthesea với tiếng việt và spacy với tiếng anh, tách file text thành các chunk min 1500 ký tự, default 2000, max 2500), tách theo câu, cố gắng giữ ngữ cảnh.
    tts-engine: tuỳ chọn engine hệ thống, edge, google translate, google cloud tts.
    python 3.15 với uv


Dưới đây là thiết kế chi tiết kiến trúc cho ứng dụng CLI Text-to-Speech (TTS) theo các chuẩn **Clean Architecture**, **Domain-Driven Design (DDD)** và tuân thủ chặt chẽ **SOLID**, tối ưu cho **Python 3.15** và quản lý dự án bằng **uv**.

---

## 1. Cấu trúc Dự án (Directory Structure)

```text
pydraft/
├── pyproject.toml               # Cấu hình dự án uv & Python 3.15
├── README.md
└── src/
    └── tts_app/
        ├── __init__.py
        ├── domain/              # [Core] Entities, Value Objects, Interfaces
        │   ├── __init__.py
        │   ├── entities.py      # TextDocument, AudioChunk, TTSConfig
        │   ├── value_objects.py # Language, Rate, Volume, Pitch, ChunkSize
        │   ├── interfaces.py    # Interfaces cho TextSplitter & TTSEngine
        │   └── exceptions.py    # Domain-specific errors
        │
        ├── use_cases/           # [Application Logic] Orchestrates Domain objects
        │   ├── __init__.py
        │   ├── convert_text.py  # Use Case: Chuyển text/folder thành audio
        │   └── list_engines.py  # Use Case: Liệt kê Engines & Voices
        │
        ├── infrastructure/      # [Adapters] Frameworks, Third-party libs
        │   ├── __init__.py
        │   ├── text_splitters/
        │   │   ├── vietnamese.py # Underthesea implementation
        │   │   └── english.py    # spaCy implementation
        │   ├── tts_engines/
        │   │   ├── system_engine.py # pyttsx3
        │   │   ├── edge_engine.py   # edge-tts
        │   │   ├── gtts_engine.py   # gTTS
        │   │   └── gcloud_engine.py # Google Cloud TTS
        │   └── audio_merger.py  # pydub / ffmpeg implementation
        │
        └── presentation/        # [Interface] CLI Interface
            ├── __init__.py
            ├── cli.py           # Entrypoint cho Click Commands
            └── formatters.py    # In dữ liệu danh sách engines/voices

```

---

## 2. Thiết lập Dự án (`pyproject.toml`)

Dự án tận dụng tính năng mới của Python 3.15 và được quản lý bằng `uv`.

```toml
[project]
name = "tts-app"
version = "0.1.0"
description = "Clean Architecture CLI Text-to-Speech Converter"
requires-python = ">=3.15"
dependencies = [
    "click>=8.1.0",
    "underthesea>=6.8.0",
    "spacy>=3.7.0",
    "edge-tts>=6.1.0",
    "gtts>=2.5.0",
    "google-cloud-texttospeech>=2.16.0",
    "pyttsx3>=2.90",
    "pydub>=0.25.1",
]

[project.scripts]
tts = "tts_app.presentation.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

```

---

## 3. Lớp Domain (Domain Layer)

Chứa logic cốt lõi, không phụ thuộc bất kỳ thư viện bên ngoài hay UI/CLI nào.

### `domain/value_objects.py`

```python
from dataclasses import dataclass
from enum import Enum


class Language(Enum):
    VIETNAMESE = "vi"
    ENGLISH = "en"


@dataclass(frozen=True)
class ChunkSize:
    value: int = 2000
    MIN_SIZE: int = 1500
    MAX_SIZE: int = 2500

    def __post_init__(self) -> None:
        if not (self.MIN_SIZE <= self.value <= self.MAX_SIZE):
            raise ValueError(
                f"Chunk size phải nằm trong khoảng {self.MIN_SIZE} - {self.MAX_SIZE} ký tự."
            )


@dataclass(frozen=True)
class AudioSettings:
    rate: float = 1.0
    volume: float = 1.0
    pitch: float = 0.0

```

### `domain/entities.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class TextChunk:
    index: int
    content: str


@dataclass
class TextDocument:
    source_path: Path
    language: Language
    raw_text: str
    chunks: List[TextChunk] = field(default_factory=list)


@dataclass
class AudioChunkResult:
    chunk_index: int
    output_path: Path

```

### `domain/interfaces.py`

Mô hình hóa theo **Dependency Inversion Principle (D trong SOLID)**.

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from tts_app.domain.entities import AudioChunkResult, TextChunk
from tts_app.domain.value_objects import AudioSettings, ChunkSize, Language


class ITextSplitter(ABC):

    @abstractmethod
    def split(self, text: str, chunk_size: ChunkSize) -> List[TextChunk]:
        """Tách văn bản thành các đoạn theo ngữ cảnh câu."""
        pass


class ITTSEngine(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def list_voices(self, language: Language | None = None) -> List[str]:
        """Danh sách voice khả dụng."""
        pass

    @abstractmethod
    def synthesize(
        self,
        chunk: TextChunk,
        voice: str,
        settings: AudioSettings,
        output_path: Path,
    ) -> AudioChunkResult:
        """Chuyển đổi TextChunk thành file Audio."""
        pass


class IAudioMerger(ABC):

    @abstractmethod
    def merge(
        self, audio_files: List[Path], output_merged_path: Path
    ) -> Path:
        """Gộp các file audio nhỏ thành 1 file duy nhất."""
        pass

```

---

## 4. Lớp Infrastructure (Adapters)

### Tách đoạn văn bản (Text Splitters)

#### `infrastructure/text_splitters/vietnamese.py`

```python
from typing import List
from underthesea import sent_tokenize
from tts_app.domain.entities import TextChunk
from tts_app.domain.interfaces import ITextSplitter
from tts_app.domain.value_objects import ChunkSize


class VietnameseTextSplitter(ITextSplitter):

    def split(self, text: str, chunk_size: ChunkSize) -> List[TextChunk]:
        sentences = sent_tokenize(text)
        chunks: List[TextChunk] = []
        current_chunk: List[str] = []
        current_length = 0
        idx = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # Nếu 1 câu dài vượt MAX thì phải ép gom
            if current_length + sentence_len > chunk_size.value and current_chunk:
                chunks.append(
                    TextChunk(index=idx, content=" ".join(current_chunk))
                )
                idx += 1
                current_chunk = []
                current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_len + 1

        if current_chunk:
            chunks.append(TextChunk(index=idx, content=" ".join(current_chunk)))

        return chunks

```

#### `infrastructure/text_splitters/english.py`

```python
from typing import List
import spacy
from tts_app.domain.entities import TextChunk
from tts_app.domain.interfaces import ITextSplitter
from tts_app.domain.value_objects import ChunkSize


class EnglishTextSplitter(ITextSplitter):

    def __init__(self) -> None:
        # Load mô hình spacy nhẹ cho tiếng Anh
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "tagger"])

    def split(self, text: str, chunk_size: ChunkSize) -> List[TextChunk]:
        doc = self.nlp(text)
        chunks: List[TextChunk] = []
        current_chunk: List[str] = []
        current_length = 0
        idx = 0

        for sent in doc.sents:
            sentence = sent.text.strip()
            sentence_len = len(sentence)

            if current_length + sentence_len > chunk_size.value and current_chunk:
                chunks.append(
                    TextChunk(index=idx, content=" ".join(current_chunk))
                )
                idx += 1
                current_chunk = []
                current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_len + 1

        if current_chunk:
            chunks.append(TextChunk(index=idx, content=" ".join(current_chunk)))

        return chunks

```

### Các Engine TTS Engine Adapters

#### `infrastructure/tts_engines/edge_engine.py` (Ví dụ triển khai Edge TTS)

```python
import asyncio
from pathlib import Path
from typing import List
import edge_tts
from tts_app.domain.entities import AudioChunkResult, TextChunk
from tts_app.domain.interfaces import ITTSEngine
from tts_app.domain.value_objects import AudioSettings, Language


class EdgeTTSEngine(ITTSEngine):

    @property
    def name(self) -> str:
        return "edge"

    def list_voices(self, language: Language | None = None) -> List[str]:
        voices = asyncio.run(edge_tts.list_voices())
        if language:
            return [
                v["ShortName"]
                for v in voices
                if v["Locale"].startswith(language.value)
            ]
        return [v["ShortName"] for v in voices]

    def synthesize(
        self,
        chunk: TextChunk,
        voice: str,
        settings: AudioSettings,
        output_path: Path,
    ) -> AudioChunkResult:
        # Định dạng rate/volume theo cú pháp edge-tts (% ví dụ "+0%", "+10%")
        rate_str = f"{int((settings.rate - 1) * 100):+d}%"
        volume_str = f"{int((settings.volume - 1) * 100):+d}%"
        pitch_str = f"{int(settings.pitch):+d}Hz"

        communicate = edge_tts.Communicate(
            text=chunk.content,
            voice=voice,
            rate=rate_str,
            volume=volume_str,
            pitch=pitch_str,
        )
        asyncio.run(communicate.save(str(output_path)))
        return AudioChunkResult(
            chunk_index=chunk.index, output_path=output_path
        )

```

*(Triển khai tương tự cho `SystemTTSEngine`, `GoogleTranslateEngine`, và `GCloudTTSEngine`)*

---

## 5. Lớp Use Cases (Application Layer)

Điều phối dữ liệu giữa Domain và Infrastructure.

### `use_cases/convert_text.py`

```python
from pathlib import Path
from typing import Dict, List
from tts_app.domain.entities import TextDocument
from tts_app.domain.interfaces import IAudioMerger, ITextSplitter, ITTSEngine
from tts_app.domain.value_objects import AudioSettings, ChunkSize, Language


class ConvertTextToAudioUseCase:

    def __init__(
        self,
        splitters: Dict[Language, ITextSplitter],
        engines: Dict[str, ITTSEngine],
        audio_merger: IAudioMerger,
    ):
        self.splitters = splitters
        self.engines = engines
        self.audio_merger = audio_merger

    def execute(
        self,
        input_path: Path,
        engine_name: str,
        voice: str,
        language: Language,
        settings: AudioSettings,
        chunk_size: ChunkSize,
        merge_audio: bool = True,
    ) -> None:
        files = (
            [input_path]
            if input_path.is_file()
            else list(input_path.glob("*.txt"))
        )
        engine = self.engines[engine_name]
        splitter = self.splitters[language]

        for file in files:
            raw_text = file.read_text(encoding="utf-8")
            doc = TextDocument(
                source_path=file, language=language, raw_text=raw_text
            )

            # 1. Tách văn bản thành các Chunk
            doc.chunks = splitter.split(doc.raw_text, chunk_size)

            # 2. Tạo thư mục lưu các chunk audio: file-text-name/
            chunk_dir = file.parent / file.stem
            chunk_dir.mkdir(parents=True, exist_ok=True)

            chunk_audio_files: List[Path] = []

            # 3. Tổng hợp audio cho từng chunk
            for chunk in doc.chunks:
                out_chunk_path = chunk_dir / f"chunk_{chunk.index:04d}.mp3"
                engine.synthesize(
                    chunk=chunk,
                    voice=voice,
                    settings=settings,
                    output_path=out_chunk_path,
                )
                chunk_audio_files.append(out_chunk_path)

            # 4. Gộp audio nếu được yêu cầu (--no-merge không bật)
            if merge_audio and chunk_audio_files:
                merged_output_path = file.parent / f"{file.stem}.mp3"
                self.audio_merger.merge(
                    chunk_audio_files, output_merged_path=merged_output_path
                )

```

---

## 6. Lớp Presentation (CLI Interface với Click)

Giao diện CLI tiếp nhận tham số từ người dùng.

### `presentation/cli.py`

```python
from pathlib import Path
import click
from tts_app.domain.value_objects import AudioSettings, ChunkSize, Language
from tts_app.infrastructure.audio_merger import PyDubAudioMerger
from tts_app.infrastructure.text_splitters.english import EnglishTextSplitter
from tts_app.infrastructure.text_splitters.vietnamese import (
    VietnameseTextSplitter,
)
from tts_app.infrastructure.tts_engines.edge_engine import EdgeTTSEngine
from tts_app.use_cases.convert_text import ConvertTextToAudioUseCase

# Dependency Injection setup
engines = {"edge": EdgeTTSEngine()}
splitters = {
    Language.VIETNAMESE: VietnameseTextSplitter(),
    Language.ENGLISH: EnglishTextSplitter(),
}
audio_merger = PyDubAudioMerger()


@click.group()
def main():
    """Ứng dụng chuyển đổi Văn bản thành Giọng nói (TTS CLI)."""
    pass


@main.command()
@click.option(
    "--list-engines",
    is_flag=True,
    help="Hiển thị danh sách các TTS Engine khả dụng.",
)
@click.option(
    "--list-voices", help="Hiển thị danh sách voices của 1 engine chỉ định."
)
def engine(list_engines: bool, list_voices: str):
    """Lệnh quản lý và tra cứu Engine / Voice."""
    if list_engines:
        click.echo("Các TTS Engines khả dụng:")
        for name in engines.keys():
            click.echo(f" - {name}")
    elif list_voices:
        if list_voices not in engines:
            click.echo(f"Lỗi: Engine '{list_voices}' không tồn tại.")
            return
        voices = engines[list_voices].list_voices()
        click.echo(f"Voices khả dụng cho engine {list_voices}:")
        for v in voices:
            click.echo(f" - {v}")


@main.command()
@click.argument(
    "input-path", type=click.Path(exists=True, path_type=Path)
)
@click.option(
    "--tts-engine",
    default="edge",
    help="Chọn engine TTS (system, edge, gtts, gcloud)",
)
@click.option("--voice", required=True, help="Tên voice sử dụng")
@click.option(
    "--lang",
    type=click.Choice(["vi", "en"]),
    default="vi",
    help="Ngôn ngữ văn bản",
)
@click.option(
    "--rate", type=float, default=1.0, help="Tốc độ đọc (Mặc định: 1.0)"
)
@click.option(
    "--volume", type=float, default=1.0, help="Âm lượng (Mặc định: 1.0)"
)
@click.option(
    "--pitch", type=float, default=0.0, help="Độ cao giọng (Mặc định: 0.0)"
)
@click.option(
    "--chunk-size",
    type=int,
    default=2000,
    help="Kích thước tối đa chunk (1500 - 2500)",
)
@click.option(
    "--no-merge",
    is_flag=True,
    default=False,
    help="Không gộp các file audio chunk lại thành file đơn",
)
def convert(
    input_path: Path,
    tts_engine: str,
    voice: str,
    lang: str,
    rate: float,
    volume: float,
    pitch: float,
    chunk_size: int,
    no_merge: bool,
):
    """Chuyển đổi file hoặc thư mục chứa file txt thành audio."""
    try:
        use_case = ConvertTextToAudioUseCase(
            splitters=splitters, engines=engines, audio_merger=audio_merger
        )

        use_case.execute(
            input_path=input_path,
            engine_name=tts_engine,
            voice=voice,
            language=Language(lang),
            settings=AudioSettings(rate=rate, volume=volume, pitch=pitch),
            chunk_size=ChunkSize(value=chunk_size),
            merge_audio=not no_merge,
        )
        click.echo("Chuyển đổi hoàn tất thành công!")
    except Exception as e:
        click.echo(f"Lỗi: {e}", err=True)


if __name__ == "__main__":
    main()

```

---

## 7. Đánh giá tính tuân thủ SOLID & Clean Architecture

* **Single Responsibility Principle (SRP):** Tách bạch rõ ràng giữa xử lý tách đoạn văn bản (`ITextSplitter`), gọi Service TTS (`ITTSEngine`), gộp Audio (`IAudioMerger`) và nhận dữ liệu CLI (`presentation`).
* **Open/Closed Principle (OCP):** Dễ dàng thêm 1 TTS Engine mới (như Amazon Polly) hoặc thuật toán tách câu mới bằng cách tạo class triển khai Interface tương ứng mà không phải sửa lại logic ứng dụng hiện tại.
* **Liskov Substitution Principle (LSP):** Các Engine triển khai từ `ITTSEngine` hoàn toàn có thể thay thế lẫn nhau trong `ConvertTextToAudioUseCase`.
* **Interface Segregation Principle (ISP):** Các Interface được định nghĩa nhỏ gọn, chỉ chứa đúng những phương thức cần thiết.
* **Dependency Inversion Principle (DIP):** Lớp Use Case phụ thuộc vào các Abstraction (Interfaces), các triết lý hạ tầng cụ thể (`edge-tts`, `underthesea`, `spacy`) phụ thuộc ngược lại vào Core Domain.

## 8. Hướng dẫn chạy dự án với `uv`

```bash
# 1. Cài đặt các thư viện phụ thuộc và tạo môi trường ảo
uv sync

# 2. Tải model cho spacy (Tiếng Anh)
uv run python -m spacy download en_core_web_sm

# 3. Xem danh sách engine
uv run tts engine --list-engines

# 4. Xem danh sách voice của Edge TTS
uv run tts engine --list-voices edge

# 5. Chuyển đổi một file text
uv run tts convert document.txt --tts-engine edge --voice vi-VN-HoaiMyNeural --lang vi

```

## cac engine con lai

Dưới đây là phần hiện thực chi tiết các Engine TTS còn lại (`SystemTTSEngine`, `GoogleTranslateEngine`, `GCloudTTSEngine`) và Module gộp file Audio (`PyDubAudioMerger`), đảm bảo tuân thủ đầy đủ chuẩn Clean Architecture & SOLID đã thiết lập.

---

## 1. System TTS Engine (`pyttsx3`)

Engine sử dụng thư viện `pyttsx3` để gọi TTS offline sẵn có của hệ điều hành (SAPI5 trên Windows, NSSpeechSynthesizer trên macOS, espeak trên Linux).

`infrastructure/tts_engines/system_engine.py`

```python
from pathlib import Path
from typing import List
import pyttsx3
from tts_app.domain.entities import AudioChunkResult, TextChunk
from tts_app.domain.interfaces import ITTSEngine
from tts_app.domain.value_objects import AudioSettings, Language


class SystemTTSEngine(ITTSEngine):

    @property
    def name(self) -> str:
        return "system"

    def list_voices(self, language: Language | None = None) -> List[str]:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        result: List[str] = []

        for voice in voices:
            voice_id = voice.id
            if language:
                # Kiểm tra ngôn ngữ dựa trên thuộc tính languages hoặc id của voice
                lang_code = language.value.lower()
                if hasattr(voice, "languages") and voice.languages:
                    if any(lang_code in str(l).lower() for l in voice.languages):
                        result.append(voice_id)
                elif lang_code in voice_id.lower():
                    result.append(voice_id)
            else:
                result.append(voice_id)

        engine.stop()
        return result

    def synthesize(
        self,
        chunk: TextChunk,
        voice: str,
        settings: AudioSettings,
        output_path: Path,
    ) -> AudioChunkResult:
        engine = pyttsx3.init()

        # Thiết lập voice
        if voice:
            engine.setProperty("voice", voice)

        # Đổi tốc độ (Rate mặc định pyttsx3 khoảng 200 wpm)
        base_rate = engine.getProperty("rate")
        engine.setProperty("rate", int(base_rate * settings.rate))

        # Đổi âm lượng (Range: 0.0 -> 1.0)
        volume = max(0.0, min(1.0, settings.volume))
        engine.setProperty("volume", volume)

        # Lưu ra file audio (.wav hoặc .mp3 tùy thuộc OS)
        engine.save_to_file(chunk.content, str(output_path))
        engine.runAndWait()
        engine.stop()

        return AudioChunkResult(
            chunk_index=chunk.index, output_path=output_path
        )

```

---

## 2. Google Translate TTS Engine (`gTTS`)

Engine miễn phí, sử dụng API public của Google Translate qua thư viện `gtts`.

`infrastructure/tts_engines/gtts_engine.py`

```python
from pathlib import Path
from typing import List
from gtts import gTTS
from gtts.lang import tts_langs
from tts_app.domain.entities import AudioChunkResult, TextChunk
from tts_app.domain.interfaces import ITTSEngine
from tts_app.domain.value_objects import AudioSettings, Language


class GoogleTranslateEngine(ITTSEngine):

    @property
    def name(self) -> str:
        return "gtts"

    def list_voices(self, language: Language | None = None) -> List[str]:
        # gTTS không hỗ trợ nhiều giọng nhân tạo riêng biệt, chỉ hỗ trợ danh sách mã ngôn ngữ
        supported_langs = tts_langs()
        if language:
            lang_code = language.value
            if lang_code in supported_langs:
                return [f"{lang_code} (Default)"]
            return []
        return [f"{code} ({name})" for code, name in supported_langs.items()]

    def synthesize(
        self,
        chunk: TextChunk,
        voice: str,
        settings: AudioSettings,
        output_path: Path,
    ) -> AudioChunkResult:
        # Lấy lang code từ chuỗi voice (ví dụ "vi (Default)" -> "vi") hoặc trích từ tham số
        lang_code = voice.split()[0] if voice else "vi"

        # gTTS hỗ trợ đọc chậm bằng bool `slow` (nếu rate < 1.0)
        is_slow = settings.rate < 0.85

        tts = gTTS(text=chunk.content, lang=lang_code, slow=is_slow)
        tts.save(str(output_path))

        return AudioChunkResult(
            chunk_index=chunk.index, output_path=output_path
        )

```

---

## 3. Google Cloud TTS Engine (`google-cloud-texttospeech`)

Engine doanh nghiệp cao cấp từ Google Cloud Platform. Yêu cầu cấu hình credentials GCP (`GOOGLE_APPLICATION_CREDENTIALS`).

`infrastructure/tts_engines/gcloud_engine.py`

```python
from pathlib import Path
from typing import List
from google.cloud import texttospeech
from tts_app.domain.entities import AudioChunkResult, TextChunk
from tts_app.domain.interfaces import ITTSEngine
from tts_app.domain.value_objects import AudioSettings, Language


class GoogleCloudTTSEngine(ITTSEngine):

    def __init__(self) -> None:
        self._client: texttospeech.TextToSpeechClient | None = None

    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        # Lazy initialization client để tránh crash khi chưa set credentials
        if self._client is None:
            self._client = texttospeech.TextToSpeechClient()
        return self._client

    @property
    def name(self) -> str:
        return "gcloud"

    def list_voices(self, language: Language | None = None) -> List[str]:
        response = self.client.list_voices()
        result: List[str] = []

        target_lang = language.value if language else None

        for voice in response.voices:
            for lang_code in voice.language_codes:
                if target_lang is None or lang_code.startswith(target_lang):
                    result.append(f"{voice.name} ({voice.ssml_gender.name})")
                    break

        return result

    def synthesize(
        self,
        chunk: TextChunk,
        voice: str,
        settings: AudioSettings,
        output_path: Path,
    ) -> AudioChunkResult:
        synthesis_input = texttospeech.SynthesisInput(text=chunk.content)

        # Trích xuất tên voice chính xác từ tham số người dùng nhập
        voice_name = voice.split()[0] if voice else "vi-VN-Wavenet-A"
        # Trích xuất mã ngôn ngữ từ tên voice (vd: vi-VN từ vi-VN-Wavenet-A)
        lang_code = "-".join(voice_name.split("-")[:2])

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=lang_code, name=voice_name
        )

        # Mapping AudioSettings
        # speaking_rate: range [0.25, 4.0]
        # pitch: range [-20.0, 20.0] semitones
        # volume_gain_db: range [-96.0, 16.0] dB
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=max(0.25, min(4.0, settings.rate)),
            pitch=max(-20.0, min(20.0, settings.pitch)),
            volume_gain_db=max(-96.0, min(16.0, (settings.volume - 1.0) * 10)),
        )

        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        output_path.write_bytes(response.audio_content)

        return AudioChunkResult(
            chunk_index=chunk.index, output_path=output_path
        )

```

---

## 4. Audio Merger Adapter (`pydub`)

Triển khai adapter ghép nhiều file audio chunk thành một file duy nhất.

`infrastructure/audio_merger.py`

```python
from pathlib import Path
from typing import List
from pydub import AudioSegment
from tts_app.domain.interfaces import IAudioMerger


class PyDubAudioMerger(IAudioMerger):

    def merge(
        self, audio_files: List[Path], output_merged_path: Path
    ) -> Path:
        if not audio_files:
            raise ValueError("Danh sách file audio trống, không thể gộp.")

        # Sắp xếp danh sách file theo đúng thứ tự chunk
        sorted_files = sorted(audio_files, key=lambda p: p.name)

        combined = AudioSegment.empty()
        for file_path in sorted_files:
            format_ext = file_path.suffix.lstrip(".")
            audio = AudioSegment.from_file(str(file_path), format=format_ext)
            combined += audio

        # Xuất file gộp chung thư mục với file text gốc
        out_format = output_merged_path.suffix.lstrip(".") or "mp3"
        combined.export(str(output_merged_path), format=out_format)

        return output_merged_path

```

---

## 5. Cập nhật Dependency Injection trong Entrypoint CLI

Cập nhật file `presentation/cli.py` để đăng ký toàn bộ các engine mới vào dictionary `engines`:

`presentation/cli.py` (Đoạn cấu hình container)

```python
from tts_app.infrastructure.audio_merger import PyDubAudioMerger
from tts_app.infrastructure.text_splitters.english import EnglishTextSplitter
from tts_app.infrastructure.text_splitters.vietnamese import (
    VietnameseTextSplitter,
)
from tts_app.infrastructure.tts_engines.edge_engine import EdgeTTSEngine
from tts_app.infrastructure.tts_engines.gcloud_engine import GoogleCloudTTSEngine
from tts_app.infrastructure.tts_engines.gtts_engine import GoogleTranslateEngine
from tts_app.infrastructure.tts_engines.system_engine import SystemTTSEngine

# Khởi tạo và đăng ký các Engine vào Container
engines = {
    "system": SystemTTSEngine(),
    "edge": EdgeTTSEngine(),
    "gtts": GoogleTranslateEngine(),
    "gcloud": GoogleCloudTTSEngine(),
}

splitters = {
    Language.VIETNAMESE: VietnameseTextSplitter(),
    Language.ENGLISH: EnglishTextSplitter(),
}

audio_merger = PyDubAudioMerger()

```
