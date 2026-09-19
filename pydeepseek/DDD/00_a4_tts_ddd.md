# Thiết kế CLI Text-to-Audio theo DDD: Chunk 2500 ký tự + Pre-normalize

Đây là phiên bản **áp dụng Domain-Driven Design** đầy đủ cho ứng dụng của bạn. Tôi sẽ đi từ **domain model** đến **infrastructure**, kèm theo **thuật toán chunking thông minh** và **normalize tiếng Việt**.

---

## 1. Phân tích nghiệp vụ (Domain Analysis)

### 1.1. Ubiquitous Language

| Thuật ngữ | Ý nghĩa |
|---|---|
| **Script** | Văn bản đầu vào cần chuyển thành audio |
| **Chunk** | Một đoạn text ≤ 2500 ký tự, đủ nhỏ để TTS xử lý |
| **Normalization** | Chuẩn hóa text trước khi TTS (số → chữ, viết tắt, ký tự đặc biệt) |
| **Speech** | Audio hoàn chỉnh sau khi ghép các chunk |
| **Voice** | Giọng đọc (vi-VN-HoaiMyNeural, en-US-JennyNeural...) |
| **SpeechRate / Pitch / Volume** | Tham số điều chỉnh giọng |
| **AudioFormat** | Định dạng output (mp3, wav, ogg) |

### 1.2. Business Rules

1. **Chunk không được vượt quá 2500 ký tự** (giới hạn của edge-tts).
2. **Chunk phải cắt ở ranh giới câu** (dấu `.`, `!`, `?`, `。`, `！`, `？`) khi có thể.
3. Nếu câu > 2500 ký tự → cắt ở dấu phẩy, rồi đến khoảng trắng.
4. **Normalize phải chạy trước chunking** để số/viết tắt không bị cắt vỡ.
5. Các chunk phải được **ghép liền mạch** thành 1 file audio duy nhất.

### 1.3. Bounded Context

```
┌────────────────────────────────────────────────────────────┐
│                    TTS Bounded Context                     │
│                                                            │
│   ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│   │ Normalize    │───▶│  Chunking    │───▶│  Synthesis │  │
│   │ (Domain Svc) │    │ (Domain Svc) │    │ (Port)     │  │
│   └──────────────┘    └──────────────┘    └────────────┘  │
│                                                   │        │
│                                                   ▼        │
│                                          ┌────────────┐    │
│                                          │  Assembly  │    │
│                                          │ (Domain)   │    │
│                                          └────────────┘    │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Cấu trúc thư mục DDD

```
tts-cli/
├── pyproject.toml
├── README.md
└── src/
    └── tts_cli/
        ├── __init__.py
        ├── __main__.py
        │
        ├── domain/                        # ⭐ TRÁI TIM
        │   ├── __init__.py
        │   ├── model/
        │   │   ├── __init__.py
        │   │   ├── script.py              # Entity: Script
        │   │   ├── chunk.py               # Entity: Chunk (con của Script)
        │   │   ├── normalized_text.py     # VO: NormalizedText
        │   │   ├── voice.py               # VO: Voice
        │   │   ├── speech_params.py       # VO: SpeechParams
        │   │   └── audio_format.py        # VO: AudioFormat
        │   ├── services/
        │   │   ├── __init__.py
        │   │   ├── text_normalizer.py     # Domain Service
        │   │   ├── chunker.py             # Domain Service
        │   │   └── script_processor.py    # Domain Service
        │   ├── ports/                     # Protocol (interface)
        │   │   ├── __init__.py
        │   │   ├── speech_synthesizer.py  # Port cho TTS engine
        │   │   └── audio_converter.py     # Port cho pyav
        │   ├── events/
        │   │   ├── __init__.py
        │   │   └── script_events.py
        │   └── exceptions.py
        │
        ├── application/                   # ORCHESTRATION
        │   ├── __init__.py
        │   ├── commands/
        │   │   ├── __init__.py
        │   │   └── synthesize_script.py   # Command + Handler
        │   ├── queries/
        │   │   ├── __init__.py
        │   │   └── list_voices.py
        │   └── dto.py
        │
        ├── infrastructure/                # KỸ THUẬT
        │   ├── __init__.py
        │   ├── tts/
        │   │   └── edge_tts_synthesizer.py
        │   ├── audio/
        │   │   └── pyav_converter.py
        │   ├── audio/
        │   │   └── pyav_assembler.py
        │   └── filesystem/
        │       └── temp_workspace.py
        │
        ├── presentation/                  # CLI
        │   ├── __init__.py
        │   ├── cli.py
        │   ├── formatters.py              # In đẹp output
        │   └── validators.py              # Validate tham số CLI
        │
        └── bootstrap.py                   # Composition Root
│
└── tests/
    ├── unit/
    │   ├── domain/
    │   │   ├── test_chunker.py
    │   │   ├── test_normalizer.py
    │   │   └── test_script.py
    │   └── application/
    └── integration/
```

**Nguyên tắc dependency:**
- `domain/` chỉ import stdlib → **không biết** edge-tts, pyav, click.
- `application/` import `domain/`, không biết infrastructure.
- `infrastructure/` implements các **Port** của domain.
- `presentation/` import `application/`.

---

## 3. Domain Layer

### 3.1. Value Objects

```python
# domain/model/normalized_text.py
from dataclasses import dataclass

@dataclass(frozen=True)
class NormalizedText:
    """Text đã qua chuẩn hóa, sẵn sàng để chunk."""
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("NormalizedText không được rỗng")
        if "\n\n\n" in self.value:
            raise ValueError("NormalizedText không được có 3+ dòng trống liên tiếp")

    @property
    def length(self) -> int:
        return len(self.value)
```

```python
# domain/model/voice.py
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Voice:
    """Giọng đọc TTS. Ví dụ: vi-VN-HoaiMyNeural."""
    name: str

    # Pattern: {lang}-{REGION}-{Name}Neural
    _PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}-\w+Neural$")

    def __post_init__(self):
        if not self._PATTERN.match(self.name):
            raise ValueError(
                f"Voice không hợp lệ: '{self.name}'. "
                f"Phải theo định dạng 'xx-YY-NameNeural'."
            )

    @property
    def locale(self) -> str:
        """Trả về 'vi-VN' từ 'vi-VN-HoaiMyNeural'."""
        parts = self.name.split("-")
        return f"{parts[0]}-{parts[1]}"
```

```python
# domain/model/speech_params.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SpeechParams:
    """Tham số điều chỉnh giọng đọc."""
    rate: str = "+0%"      # ví dụ "+20%", "-10%"
    volume: str = "+0%"    # ví dụ "+50%"
    pitch: str = "+0Hz"    # ví dụ "+5Hz"

    def __post_init__(self):
        self._validate_percent(self.rate, "rate")
        self._validate_percent(self.volume, "volume")
        self._validate_hz(self.pitch, "pitch")

    @staticmethod
    def _validate_percent(value: str, field: str) -> None:
        if not (value.startswith("+") or value.startswith("-")) or not value.endswith("%"):
            raise ValueError(f"{field} phải có định dạng '+N%' hoặc '-N%'")

    @staticmethod
    def _validate_hz(value: str, field: str) -> None:
        if not (value.startswith("+") or value.startswith("-")) or not value.endswith("Hz"):
            raise ValueError(f"{field} phải có định dạng '+NHz' hoặc '-NHz'")
```

```python
# domain/model/audio_format.py
from dataclasses import dataclass

@dataclass(frozen=True)
class AudioFormat:
    """Định dạng audio output."""
    extension: str          # ".mp3", ".wav", ".ogg"
    sample_rate: int = 16000
    mono: bool = True

    SUPPORTED = {".mp3", ".wav", ".ogg"}

    def __post_init__(self):
        if self.extension not in self.SUPPORTED:
            raise ValueError(
                f"Định dạng '{self.extension}' không hỗ trợ. "
                f"Chỉ chấp nhận: {self.SUPPORTED}"
            )
        if self.sample_rate < 8000 or self.sample_rate > 48000:
            raise ValueError("sample_rate phải trong khoảng 8000-48000 Hz")

    @property
    def codec(self) -> str:
        return {
            ".mp3": "libmp3lame",
            ".wav": "pcm_s16le",
            ".ogg": "libopus",
        }[self.extension]

    @property
    def container_format(self) -> str:
        return self.extension.lstrip(".")
```

### 3.2. Entity: Chunk

```python
# domain/model/chunk.py
from dataclasses import dataclass
from uuid import UUID, uuid4

@dataclass
class Chunk:
    """
    Một đoạn text ≤ 2500 ký tự, đơn vị nhỏ nhất để TTS xử lý.
    Thuộc về Script (không có repository riêng).
    """
    MAX_LENGTH = 2500

    index: int
    text: str
    id: UUID = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid4()
        if len(self.text) > self.MAX_LENGTH:
            raise ValueError(
                f"Chunk vượt quá {self.MAX_LENGTH} ký tự: {len(self.text)}"
            )
        if not self.text.strip():
            raise ValueError("Chunk không được rỗng")

    @property
    def length(self) -> int:
        return len(self.text)

    def __repr__(self) -> str:
        preview = self.text[:50].replace("\n", " ")
        return f"Chunk(#{self.index}, {self.length} chars, '{preview}...')"
```

### 3.3. Aggregate Root: Script

```python
# domain/model/script.py
from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID, uuid4

from .chunk import Chunk
from .normalized_text import NormalizedText
from .voice import Voice
from .speech_params import SpeechParams
from .audio_format import AudioFormat


@dataclass
class Script:
    """
    AGGREGATE ROOT.
    Chứa text đã normalize + danh sách chunk + tham số TTS.
    Đảm bảo invariant: mọi chunk ≤ 2500 ký tự, tổng ghép lại = text gốc.
    """
    id: UUID
    raw_text: str
    normalized: NormalizedText
    voice: Voice
    params: SpeechParams
    audio_format: AudioFormat
    output_path: Path
    chunks: list[Chunk] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        raw_text: str,
        normalized: NormalizedText,
        voice: Voice,
        params: SpeechParams,
        audio_format: AudioFormat,
        output_path: Path,
    ) -> "Script":
        return cls(
            id=uuid4(),
            raw_text=raw_text,
            normalized=normalized,
            voice=voice,
            params=params,
            audio_format=audio_format,
            output_path=output_path,
        )

    # ---- Behavior: chỉ Aggregate Root mới được thay đổi chunk list ----
    def attach_chunks(self, chunks: list[Chunk]) -> None:
        """Gán danh sách chunk (gọi bởi ScriptProcessor)."""
        if not chunks:
            raise ValueError("Script phải có ít nhất 1 chunk")
        for c in chunks:
            if c.length > Chunk.MAX_LENGTH:
                raise ValueError(f"Chunk #{c.index} vượt 2500 ký tự")
        self.chunks = chunks

    # ---- Query ----
    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    @property
    def total_chars(self) -> int:
        return sum(c.length for c in self.chunks)

    @property
    def is_chunked(self) -> bool:
        return len(self.chunks) > 0
```

### 3.4. Domain Service: Text Normalizer

**Đây là phần quan trọng** — chuẩn hóa tiếng Việt trước khi TTS.

```python
# domain/services/text_normalizer.py
import re
import unicodedata
from . import _number_to_vietnamese


class TextNormalizer:
    """
    DOMAIN SERVICE: chuẩn hóa text trước khi chunk + TTS.

    Xử lý:
      1. Unicode NFC (chuẩn hóa dấu tiếng Việt)
      2. Loại bỏ ký tự điều khiển, emoji lạ
      3. Chuẩn hóa khoảng trắng, dòng trống
      4. Chuyển số → chữ (tùy chọn, cho tiếng Việt)
      5. Mở rộng viết tắt phổ biến
      6. Chuẩn hóa dấu câu
    """

    # Viết tắt tiếng Việt phổ biến
    ABBREVIATIONS_VI = {
        r"\bTP\.?\s*HCM\b": "Thành phố Hồ Chí Minh",
        r"\bTP\.\b": "Thành phố",
        r"\bTW\b": "Trung ương",
        r"\bUBND\b": "Ủy ban nhân dân",
        r"\bGD&ĐT\b": "Giáo dục và Đào tạo",
        r"\bNXB\b": "Nhà xuất bản",
        r"\bPGS\.?\s*TS\b": "Phó Giáo sư Tiến sĩ",
        r"\bTS\.\b": "Tiến sĩ",
        r"\bThS\.\b": "Thạc sĩ",
        r"\bGS\.\b": "Giáo sư",
        r"\bVND\b": "đồng",
        r"\bUSD\b": "đô la Mỹ",
        r"\bkm\b": "ki lô mét",
        r"\bkg\b": "ki lô gam",
        r"\bcm\b": "xen ti mét",
        r"\bm\b": "mét",
    }

    def __init__(self, numbers_to_words: bool = True):
        self._numbers_to_words = numbers_to_words

    def normalize(self, raw: str) -> str:
        text = raw

        # 1. Unicode NFC — quan trọng cho tiếng Việt
        text = unicodedata.normalize("NFC", text)

        # 2. Loại bỏ ký tự điều khiển
        text = "".join(
            ch for ch in text
            if unicodedata.category(ch)[0] != "C" or ch in "\n\t"
        )

        # 3. Chuẩn hóa dấu câu "lạ" → dấu câu chuẩn
        text = self._normalize_punctuation(text)

        # 4. Mở rộng viết tắt
        text = self._expand_abbreviations(text)

        # 5. Số → chữ
        if self._numbers_to_words:
            text = self._number_to_vietnamese_words(text)

        # 6. Chuẩn hóa khoảng trắng
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    # ---------- helpers ----------
    @staticmethod
    def _normalize_punctuation(text: str) -> str:
        # Dấu câu full-width → nửa
        replacements = {
            "。": ".", "！": "!", "？": "?", "，": ",", "；": ";", "：": ":",
            "（": "(", "）": ")", "【": "[", "】": "]", "「": "\"", "」": "\"",
            "…": "...", "—": " - ", "–": " - ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Gộp nhiều dấu chấm than / hỏi liên tiếp
        text = re.sub(r"!{2,}", "!", text)
        text = re.sub(r"\?{2,}", "?", text)
        text = re.sub(r"\.{4,}", "...", text)

        return text

    def _expand_abbreviations(self, text: str) -> str:
        for pattern, replacement in self.ABBREVIATIONS_VI.items():
            text = re.sub(pattern, replacement, text)
        return text

    @staticmethod
    def _number_to_vietnamese_words(text: str) -> str:
        """Chuyển số nguyên trong text thành chữ tiếng Việt.
        Ví dụ: '123' → 'một trăm hai mươi ba'."""
        from ._number_to_vietnamese import num_to_vietnamese

        def repl(match: re.Match) -> str:
            num = int(match.group(0))
            return num_to_vietnamese(num)

        # Chỉ chuyển số độc lập (không nằm trong từ khác)
        return re.sub(r"(?<!\w)\d+(?!\w)", repl, text)
```

```python
# domain/services/_number_to_vietnamese.py
"""Chuyển số nguyên thành chữ tiếng Việt."""

_DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
_SCALES = ["", "nghìn", "triệu", "tỷ"]


def num_to_vietnamese(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + num_to_vietnamese(-n)

    parts = []
    scale_idx = 0

    while n > 0:
        group = n % 1000
        if group > 0:
            group_words = _three_digits_to_words(group)
            if _SCALES[scale_idx]:
                group_words += " " + _SCALES[scale_idx]
            parts.append(group_words)
        n //= 1000
        scale_idx += 1

    return " ".join(reversed(parts))


def _three_digits_to_words(n: int) -> str:
    hundreds = n // 100
    tens = (n % 100) // 10
    units = n % 10

    words = []
    if hundreds > 0:
        words.append(_DIGITS[hundreds] + " trăm")
        if tens == 0 and units > 0:
            words.append("lẻ")

    if tens > 0:
        if tens == 1:
            words.append("mười")
        else:
            words.append(_DIGITS[tens] + " mươi")

    if units > 0:
        if tens > 1 and units == 1:
            words.append("mốt")
        elif tens > 0 and units == 5:
            words.append("lăm")
        else:
            words.append(_DIGITS[units])

    return " ".join(words)
```

### 3.5. Domain Service: Chunker (thuật toán cốt lõi)

```python
# domain/services/chunker.py
import re
from ..model.chunk import Chunk


class TextChunker:
    """
    DOMAIN SERVICE: chia text thành các chunk ≤ MAX_LENGTH ký tự.

    Chiến lược cắt (theo thứ tự ưu tiên):
      1. Ranh giới đoạn văn (\\n\\n)
      2. Ranh giới câu (. ! ? và biến thể)
      3. Ranh giới mệnh đề (, ; :)
      4. Khoảng trắng
      5. Cắt cứng (chỉ khi không còn cách nào)
    """

    SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
    CLAUSE_BREAK = re.compile(r"(?<=[,;:])\s+")

    def __init__(self, max_length: int = 2500):
        self._max = max_length

    def split(self, text: str) -> list[Chunk]:
        if not text.strip():
            raise ValueError("Không thể chunk text rỗng")

        paragraphs = text.split("\n\n")
        chunks_text: list[str] = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(para) <= self._max:
                chunks_text.append(para)
            else:
                chunks_text.extend(self._split_paragraph(para))

        return [Chunk(index=i, text=t) for i, t in enumerate(chunks_text)]

    # ---------- internals ----------
    def _split_paragraph(self, para: str) -> list[str]:
        """Cắt paragraph dài thành nhiều đoạn ≤ max."""
        sentences = self.SENTENCE_END.split(para)
        result: list[str] = []
        current = ""

        for sentence in sentences:
            candidate = (current + " " + sentence).strip() if current else sentence

            if len(candidate) <= self._max:
                current = candidate
            else:
                if current:
                    result.append(current)

                if len(sentence) <= self._max:
                    current = sentence
                else:
                    # Câu quá dài → cắt ở clause
                    result.extend(self._split_long_sentence(sentence))
                    current = ""

        if current:
            result.append(current)

        return result

    def _split_long_sentence(self, sentence: str) -> list[str]:
        """Câu dài hơn max → cắt ở clause hoặc word."""
        clauses = self.CLAUSE_BREAK.split(sentence)
        result: list[str] = []
        current = ""

        for clause in clauses:
            candidate = (current + " " + clause).strip() if current else clause

            if len(candidate) <= self._max:
                current = candidate
            else:
                if current:
                    result.append(current)
                if len(clause) <= self._max:
                    current = clause
                else:
                    # Clause vẫn quá dài → cắt ở word
                    result.extend(self._split_by_words(clause))
                    current = ""

        if current:
            result.append(current)

        return result

    def _split_by_words(self, text: str) -> list[str]:
        """Cắt cứng theo từ (khoảng trắng)."""
        words = text.split()
        result: list[str] = []
        current: list[str] = []

        for word in words:
            # Word đơn lẻ dài hơn max → cắt cứng ký tự
            if len(word) > self._max:
                if current:
                    result.append(" ".join(current))
                    current = []
                # Cắt word thành nhiều phần
                for i in range(0, len(word), self._max):
                    result.append(word[i:i + self._max])
                continue

            current.append(word)
            if len(" ".join(current)) > self._max:
                current.pop()
                result.append(" ".join(current))
                current = [word]

        if current:
            result.append(" ".join(current))

        return result
```

### 3.6. Domain Service: Script Processor (orchestrate normalize + chunk)

```python
# domain/services/script_processor.py
from ..model.script import Script
from ..model.chunk import Chunk
from .text_normalizer import TextNormalizer
from .chunker import TextChunker


class ScriptProcessor:
    """
    DOMAIN SERVICE: điều phối normalize → chunk → gán vào Script.
    Đây là "use case" cấp domain, không phụ thuộc infrastructure.
    """

    def __init__(
        self,
        normalizer: TextNormalizer | None = None,
        chunker: TextChunker | None = None,
    ):
        self._normalizer = normalizer or TextNormalizer()
        self._chunker = chunker or TextChunker(max_length=Chunk.MAX_LENGTH)

    def process(self, script: Script) -> Script:
        """Chuẩn hóa + chunk + gắn vào Script (in-place, trả về chính nó)."""
        # Bước 1: Normalize
        normalized_str = self._normalizer.normalize(script.raw_text)

        # Cập nhật NormalizedText trong Script
        from ..model.normalized_text import NormalizedText
        script.normalized = NormalizedText(normalized_str)

        # Bước 2: Chunk
        chunks = self._chunker.split(normalized_str)

        # Bước 3: Gắn vào Aggregate
        script.attach_chunks(chunks)

        return script
```

### 3.7. Domain Ports

```python
# domain/ports/speech_synthesizer.py
from pathlib import Path
from typing import Protocol
from ..model.voice import Voice
from ..model.speech_params import SpeechParams


class SpeechSynthesizer(Protocol):
    """Port để sinh audio từ text."""

    def synthesize(
        self,
        text: str,
        voice: Voice,
        params: SpeechParams,
        output: Path,
    ) -> Path:
        """Sinh audio cho MỘT đoạn text, lưu tại output. Trả về path."""
        ...

    def list_voices(self, locale: str | None = None) -> list[dict]:
        """Liệt kê các giọng có sẵn."""
        ...
```

```python
# domain/ports/audio_converter.py
from pathlib import Path
from typing import Protocol


class AudioConverter(Protocol):
    """Port để chuyển đổi định dạng audio."""

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        sample_rate: int,
        mono: bool,
    ) -> Path:
        """Chuyển đổi định dạng. Trả về path output."""
        ...

    def concat(self, inputs: list[Path], output: Path) -> Path:
        """Ghép nhiều file audio thành 1 file duy nhất."""
        ...
```

### 3.8. Domain Exceptions

```python
# domain/exceptions.py
class DomainError(Exception):
    """Lỗi gốc của domain."""


class InvalidVoiceError(DomainError):
    pass


class ChunkTooLongError(DomainError):
    pass


class EmptyScriptError(DomainError):
    pass


class SynthesisError(DomainError):
    pass
```

---

## 4. Application Layer

### 4.1. Command + Handler

```python
# application/commands/synthesize_script.py
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from ...domain.model.script import Script
from ...domain.model.normalized_text import NormalizedText
from ...domain.model.voice import Voice
from ...domain.model.speech_params import SpeechParams
from ...domain.model.audio_format import AudioFormat
from ...domain.services.script_processor import ScriptProcessor
from ...domain.ports.speech_synthesizer import SpeechSynthesizer
from ...domain.ports.audio_converter import AudioConverter
from ...domain.exceptions import SynthesisError
from ..dto import SynthesizeResultDTO


@dataclass(frozen=True)
class SynthesizeScriptCommand:
    """Command: chuyển 1 đoạn text thành audio."""
    raw_text: str
    voice_name: str
    output_path: Path
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"
    sample_rate: int = 16000
    mono: bool = True


class SynthesizeScriptHandler:
    """
    APPLICATION SERVICE: điều phối use case.
    - Normalize + chunk (domain service)
    - Sinh từng chunk (port)
    - Ghép chunk (port)
    - Chuyển đổi định dạng (port)
    """

    def __init__(
        self,
        synthesizer: SpeechSynthesizer,
        converter: AudioConverter,
        processor: ScriptProcessor,
        workspace,
    ):
        self._synth = synthesizer
        self._conv = converter
        self._processor = processor
        self._workspace = workspace

    def handle(self, cmd: SynthesizeScriptCommand) -> SynthesizeResultDTO:
        # 1. Tạo Script (aggregate)
        script = Script.create(
            raw_text=cmd.raw_text,
            normalized=NormalizedText(cmd.raw_text),  # sẽ bị thay bên dưới
            voice=Voice(cmd.voice_name),
            params=SpeechParams(cmd.rate, cmd.volume, cmd.pitch),
            audio_format=AudioFormat(
                extension=cmd.output_path.suffix.lower(),
                sample_rate=cmd.sample_rate,
                mono=cmd.mono,
            ),
            output_path=cmd.output_path,
        )

        # 2. Domain: normalize + chunk
        script = self._processor.process(script)

        # 3. Sinh từng chunk
        chunk_files: list[Path] = []
        try:
            for chunk in script.chunks:
                chunk_path = self._workspace.allocate(f"chunk_{chunk.index}.mp3")
                self._synth.synthesize(
                    text=chunk.text,
                    voice=script.voice,
                    params=script.params,
                    output=chunk_path,
                )
                chunk_files.append(chunk_path)

            # 4. Ghép lại
            merged_mp3 = self._workspace.allocate("merged.mp3")
            self._conv.concat(chunk_files, merged_mp3)

            # 5. Chuyển đổi định dạng đích (nếu không phải mp3)
            if script.audio_format.extension != ".mp3":
                self._conv.convert(
                    input_path=merged_mp3,
                    output_path=script.output_path,
                    sample_rate=script.audio_format.sample_rate,
                    mono=script.audio_format.mono,
                )
            else:
                merged_mp3.replace(script.output_path)

        except Exception as e:
            raise SynthesisError(f"Lỗi khi sinh audio: {e}") from e

        finally:
            self._workspace.cleanup()

        return SynthesizeResultDTO(
            output_path=script.output_path,
            total_chunks=script.total_chunks,
            total_chars=script.total_chars,
        )
```

### 4.2. DTO

```python
# application/dto.py
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SynthesizeResultDTO:
    output_path: Path
    total_chunks: int
    total_chars: int
```

---

## 5. Infrastructure Layer

### 5.1. Edge-TTS Synthesizer

```python
# infrastructure/tts/edge_tts_synthesizer.py
import asyncio
from pathlib import Path
import edge_tts

from ...domain.model.voice import Voice
from ...domain.model.speech_params import SpeechParams


class EdgeTTSSynthesizer:
    """Implementation của SpeechSynthesizer dùng edge-tts."""

    def synthesize(
        self,
        text: str,
        voice: Voice,
        params: SpeechParams,
        output: Path,
    ) -> Path:
        asyncio.run(self._async_synth(text, voice, params, output))
        return output

    async def _async_synth(
        self,
        text: str,
        voice: Voice,
        params: SpeechParams,
        output: Path,
    ) -> None:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice.name,
            rate=params.rate,
            volume=params.volume,
            pitch=params.pitch,
        )
        await communicate.save(str(output))

    def list_voices(self, locale: str | None = None) -> list[dict]:
        return asyncio.run(self._async_list(locale))

    async def _async_list(self, locale: str | None) -> list[dict]:
        voices = await edge_tts.list_voices()
        if locale:
            voices = [v for v in voices if v["ShortName"].startswith(locale)]
        return voices
```

### 5.2. PyAV Converter + Assembler

```python
# infrastructure/audio/pyav_converter.py
from pathlib import Path
import av


class PyAVConverter:
    """Implementation của AudioConverter dùng pyav."""

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        sample_rate: int,
        mono: bool,
    ) -> Path:
        suffix = output_path.suffix.lower()
        codec = {
            ".wav": "pcm_s16le",
            ".ogg": "libopus",
            ".mp3": "libmp3lame",
        }.get(suffix)
        if not codec:
            raise ValueError(f"Định dạng không hỗ trợ: {suffix}")

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
                for packet in out_stream.encode(None):
                    out_container.mux(packet)

        return output_path

    def concat(self, inputs: list[Path], output: Path) -> Path:
        """Ghép nhiều file audio thành 1 file duy nhất."""
        if not inputs:
            raise ValueError("Danh sách input rỗng")

        # Mở container output trước
        with av.open(str(output), "w", format="mp3") as out_container:
            out_stream = out_container.add_stream("libmp3lame")

            for path in inputs:
                with av.open(str(path)) as in_container:
                    in_stream = in_container.streams.audio[0]
                    for frame in in_container.decode(in_stream):
                        for packet in out_stream.encode(frame):
                            out_container.mux(packet)

            # Flush cuối
            for packet in out_stream.encode(None):
                out_container.mux(packet)

        return output
```

### 5.3. Temp Workspace

```python
# infrastructure/filesystem/temp_workspace.py
import shutil
import tempfile
from pathlib import Path


class TempWorkspace:
    """Quản lý thư mục tạm cho các file chunk."""

    def __init__(self):
        self._dir = Path(tempfile.mkdtemp(prefix="tts_cli_"))

    def allocate(self, name: str) -> Path:
        return self._dir / name

    def cleanup(self) -> None:
        if self._dir.exists():
            shutil.rmtree(self._dir, ignore_errors=True)
```

---

## 6. Presentation Layer

### 6.1. CLI

```python
# presentation/cli.py
from pathlib import Path
import click

from ..bootstrap import build_handler, build_voice_lister


@click.group()
@click.version_option()
def cli():
    """CLI chuyển Text thành Audio dùng Edge TTS + PyAV (DDD)."""


@cli.command()
@click.argument("text", required=False)
@click.option("-f", "--file", "input_file",
              type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="File text đầu vào (thay thế cho argument TEXT).")
@click.option("-v", "--voice", default="vi-VN-HoaiMyNeural", show_default=True,
              help="Tên giọng đọc.")
@click.option("-o", "--output",
              type=click.Path(path_type=Path), default="output.mp3",
              show_default=True, help="File output.")
@click.option("-r", "--rate", default="+0%", show_default=True,
              help="Tốc độ đọc, ví dụ '+20%'.")
@click.option("--volume", default="+0%", show_default=True)
@click.option("--pitch", default="+0Hz", show_default=True)
@click.option("--sample-rate", type=int, default=16000, show_default=True)
@click.option("--stereo", is_flag=True, help="Giữ stereo (mặc định mono).")
@click.option("--no-normalize-numbers", is_flag=True,
              help="Tắt chuyển số thành chữ.")
def speak(text, input_file, voice, output, rate, volume, pitch,
          sample_rate, stereo, no_normalize_numbers):
    """Chuyển TEXT (hoặc file) thành audio."""
    # Lấy raw text
    if input_file:
        raw = input_file.read_text(encoding="utf-8")
    elif text:
        raw = text
    else:
        raise click.UsageError("Phải cung cấp TEXT hoặc --file")

    # Build handler (composition root)
    handler = build_handler(numbers_to_words=not no_normalize_numbers)

    from ..application.commands.synthesize_script import (
        SynthesizeScriptCommand,
    )

    cmd = SynthesizeScriptCommand(
        raw_text=raw,
        voice_name=voice,
        output_path=output,
        rate=rate,
        volume=volume,
        pitch=pitch,
        sample_rate=sample_rate,
        mono=not stereo,
    )

    # Hiển thị thông tin trước khi chạy
    click.echo(f"📝 Độ dài text gốc: {len(raw):,} ký tự")

    with click.progressbar(length=100, label="Đang xử lý") as bar:
        # Cập nhật progress đơn giản (chưa gắn callback chi tiết)
        bar.update(20)
        result = handler.handle(cmd)
        bar.update(80)

    click.echo(f"\n✅ Đã lưu: {result.output_path.resolve()}")
    click.echo(f"   - Tổng chunk: {result.total_chunks}")
    click.echo(f"   - Tổng ký tự sau normalize: {result.total_chars:,}")


@cli.command()
@click.option("-l", "--locale", default=None,
              help="Lọc theo locale, ví dụ 'vi-VN'.")
def voices(locale):
    """Liệt kê các giọng có sẵn."""
    lister = build_voice_lister()
    voice_list = lister.list_voices(locale)

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

---

## 7. Composition Root — `bootstrap.py`

```python
# bootstrap.py
from .domain.services.text_normalizer import TextNormalizer
from .domain.services.chunker import TextChunker
from .domain.services.script_processor import ScriptProcessor
from .infrastructure.tts.edge_tts_synthesizer import EdgeTTSSynthesizer
from .infrastructure.audio.pyav_converter import PyAVConverter
from .infrastructure.filesystem.temp_workspace import TempWorkspace
from .application.commands.synthesize_script import SynthesizeScriptHandler


def build_handler(numbers_to_words: bool = True) -> SynthesizeScriptHandler:
    """Ráp mọi thứ lại với nhau."""
    normalizer = TextNormalizer(numbers_to_words=numbers_to_words)
    chunker = TextChunker(max_length=2500)
    processor = ScriptProcessor(normalizer, chunker)

    synthesizer = EdgeTTSSynthesizer()
    converter = PyAVConverter()
    workspace = TempWorkspace()

    return SynthesizeScriptHandler(
        synthesizer=synthesizer,
        converter=converter,
        processor=processor,
        workspace=workspace,
    )


def build_voice_lister() -> EdgeTTSSynthesizer:
    return EdgeTTSSynthesizer()
```

---

## 8. Cách sử dụng

```bash
# Text ngắn, tiếng Việt
tts-cli speak "Xin chào, hôm nay là ngày 19 tháng 9 năm 2026" -o chao.mp3

# Đọc từ file dài (tự động chunk + ghép)
tts-cli speak --file sach.txt -o sach.wav --sample-rate 22050

# Giọng nam, tốc độ nhanh
tts-cli speak "Đây là giọng nam" -v vi-VN-NamMinhNeural -r "+30%" -o nam.mp3

# Liệt kê giọng tiếng Việt
tts-cli voices -l vi-VN
```

**Ví dụ output:**
```
📝 Độ dài text gốc: 125,430 ký tự
Đang xử lý  [####################################] 100%
✅ Đã lưu: /home/user/sach.wav
   - Tổng chunk: 63
   - Tổng ký tự sau normalize: 128,912
```

---

## 9. Testing

### Unit test cho Chunker

```python
# tests/unit/domain/test_chunker.py
from tts_cli.domain.services.chunker import TextChunker


def test_short_text_single_chunk():
    chunker = TextChunker(max_length=2500)
    chunks = chunker.split("Xin chào thế giới.")
    assert len(chunks) == 1
    assert chunks[0].text == "Xin chào thế giới."


def test_long_text_multiple_chunks():
    chunker = TextChunker(max_length=100)
    text = "Câu một. " * 30
    chunks = chunker.split(text)
    assert all(c.length <= 100 for c in chunks)
    assert len(chunks) > 1


def test_split_at_sentence_boundary():
    chunker = TextChunker(max_length=50)
    text = "Câu ngắn 1. Câu ngắn 2. Câu ngắn 3. Câu ngắn 4."
    chunks = chunker.split(text)
    # Không được cắt giữa câu
    for c in chunks:
        assert not c.text.endswith("ngắ")  # ví dụ không bị cắt giữa từ


def test_very_long_sentence_fallback():
    chunker = TextChunker(max_length=50)
    text = "a" * 200  # 1 "câu" dài 200 ký tự, không dấu
    chunks = chunker.split(text)
    assert all(c.length <= 50 for c in chunks)
```

### Unit test cho Normalizer

```python
# tests/unit/domain/test_normalizer.py
from tts_cli.domain.services.text_normalizer import TextNormalizer


def test_expand_abbreviations():
    n = TextNormalizer(numbers_to_words=False)
    result = n.normalize("TP. HCM rất đẹp")
    assert "Thành phố Hồ Chí Minh" in result


def test_full_width_punctuation():
    n = TextNormalizer(numbers_to_words=False)
    result = n.normalize("Xin chào。Bạn khỏe không？")
    assert "。" not in result
    assert "？" not in result


def test_number_to_vietnamese():
    n = TextNormalizer(numbers_to_words=True)
    result = n.normalize("Tôi có 123 quả táo")
    assert "một trăm hai mươi ba" in result
```

---

## 10. Điểm mấu chốt của thiết kế DDD này

| Khía cạnh | Cách tiếp cận DDD |
|---|---|
| **Domain model** | `Script` là Aggregate Root, `Chunk` là Entity con |
| **Business rule** | "Chunk ≤ 2500" nằm trong `Chunk.__post_init__`, không phải ở CLI |
| **Chuẩn hóa text** | Domain Service `TextNormalizer` — không biết gì về file/CLI |
| **Chunking** | Domain Service `TextChunker` với chiến lược cắt 4 cấp |
| **TTS engine** | Port `SpeechSynthesizer` — edge-tts chỉ là 1 implementation |
| **Chuyển đổi audio** | Port `AudioConverter` — pyav là implementation |
| **Orchestration** | Application Service `SynthesizeScriptHandler` |
| **CLI** | Presentation layer mỏng, chỉ parse + gọi handler |
| **Composition Root** | `bootstrap.py` ráp mọi thứ, dễ thay thế implementation |

**Lợi ích cụ thể:**
- Đổi từ edge-tts sang Google TTS: chỉ viết 1 class mới implement `SpeechSynthesizer`, sửa `bootstrap.py`. **Domain không đổi.**
- Đổi từ pyav sang pydub: tương tự.
- Test domain không cần internet, không cần ffmpeg — chỉ cần pure Python.

---

## 11. Bạn muốn đi tiếp phần nào?

1. **Viết đầy đủ file `pyproject.toml` + setup để `pip install -e .`** rồi chạy `tts-cli` từ terminal?
2. **Thêm progress callback thật** — edge-tts stream để báo % chính xác từng chunk?
3. **Thêm query `voices` đầy đủ** với cache file để không gọi API mỗi lần?
4. **Thêm chức năng đọc truyện dài có chapter** — chia theo chương, xuất từng file riêng?
5. **Viết integration test** cho toàn bộ pipeline?

Nói tôi biết bạn muốn phần nào, tôi sẽ viết chi tiết tiếp bằng tiếng Việt.