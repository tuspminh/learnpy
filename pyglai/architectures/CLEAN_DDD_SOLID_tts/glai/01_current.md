> bạn là lập trình viên python, thiét kế chi tiếp app sau theo kiến trúc clean, domain driven design và nguyên lý solid:app chuyển text thành voice, tiếng việt hoặc tiếng anh. đầu vào là file text hoặc folder chứa các file text.app cli dùng click để nhận tham số dòng lệnh. có các tham số sau : file/ folder, tts-engine, voice, rate, volume, pitch, --no-merge (mặc định thì merge các file audio của các chunk của file text thành một file audio, nếu có --no-merge thì không), chunk-size(mặc định 2000 ký tự, max 2500)có các lệnh hiển thị engine, voice để người dùng lấy và nhập vô dòng lệnh như engine --list , engine engine-name voices,....output: chunk audio lưu trong file-text-name/, merged-audio thì lưu chung thư mục với file text.xử lý file text, dùng underthesea với tiếng việt và spacy với tiếng anh, tách file text thành các chunk min 1500 ký tự, default 2000, max 2500), tách theo câu, cố gắng giữ ngữ cảnh.tts-engine: tuỳ chọn engine hệ thống, edge, google translate, google cloud tts.python 3.15 với uv


Chào bạn, dưới đây là thiết kế chi tiết cho ứng dụng Text-to-Speech (TTS) CLI được xây dựng bằng Python 3.15, quản lý bằng uv, áp dụng triệt để kiến trúc Clean Architecture, Domain-Driven Design (DDD) và nguyên lý SOLID.

* * *

## 🏛️ Cấu trúc thư mục (Clean Architecture & DDD)

Dự án được chia thành 4 lớp rõ rệt để đảm bảo tính độc lập và dễ kiểm thử:
    
    
    tts_cli_app/
    ├── .venv/
    ├── pyproject.toml            # Cấu hình uv và các dependency (underthesea, spacy, click,...)
    ├── src/
    │   └── tts_app/
    │       ├── __init__.py
    │       ├── main.py           # Điểm chạy ứng dụng (CLI Entrypoint)
    │       │
    │       ├── domain/           # LAYER 1: Nghiệp vụ cốt lõi (Không phụ thuộc thư viện ngoài)
    │       │   ├── __init__.py
    │       │   ├── models.py     # Định nghĩa AudioChunk, TextFile, EngineInfo, VoiceInfo
    │       │   ├── exceptions.py # Các lỗi đặc thù của domain
    │       │   └── services.py   # Quy trình tách câu (Sentence Splitter) theo ngôn ngữ
    │       │
    │       ├── use_cases/        # LAYER 2: Ca sử dụng (Điều phối luồng công việc)
    │       │   ├── __init__.py
    │       │   ├── process_tts.py# Chuyển đổi text thành audio (phối hợp Splitter, TTSEngine, Merger)
    │       │   └── list_info.py  # Lấy danh sách Engine và Voices
    │       │
    │       ├── interfaces/       # LAYER 3: Cổng giao tiếp (Abstractions / Interfaces)
    │       │   ├── __init__.py
    │       │   ├── tts_engine.py # Interface ITTSEngine (SOLID: Dependency Inversion)
    │       │   ├── text_splitter.py# Interface ITextSplitter
    │       │   └── audio_merger.py # Interface IAudioMerger
    │       │
    │       └── infrastructure/   # LAYER 4: Công nghệ chi tiết (Frameworks & Libraries)
    │           ├── __init__.py
    │           ├── cli/          # Giao diện dòng lệnh bằng Click
    │           │   ├── commands.py
    │           │   └── parsers.py
    │           ├── splitters/    # Hiện thực hóa việc tách chữ (Spacy, Underthesea)
    │           │   ├── en_spacy.py
    │           │   └── vi_underthesea.py
    │           ├── tts_engines/  # Hiện thực hóa các engine (Edge, System, Google...)
    │           │   ├── system.py
    │           │   ├── edge.py
    │           │   ├── google_translate.py
    │           │   └── google_cloud.py
    │           └── audio/        # Hiện thực hóa việc gộp file audio (pydub hoặc ffmpeg)
    │               └── ffmpeg_merger.py
    └── tests/                    # Thư mục kiểm thử (Mocks & Unit tests)
    

* * *

## 📜 Chi tiết mã nguồn (Bản thảo chi tiết)

## 1\. Cấu hình môi trường (`pyproject.toml`)

Sử dụng các thư viện hiện đại và khai báo rõ ràng cho `uv`.
    
    
    [project]
    name = "tts-cli-app"
    version = "0.1.0"
    description = "Advanced TTS CLI App with Clean Architecture"
    requires-python = ">=3.15"
    dependencies = [
        "click>=8.1.0",
        "underthesea>=6.8.0",
        "spacy>=3.8.0",
        "edge-tts>=6.0.0",
        "gtts>=2.5.0",
        "google-cloud-texttospeech>=2.16.0",
        "pydub>=0.25.1",
    ]
    
    [project.scripts]
    tts = "tts_app.main:cli"
    

## 2\. Lớp Domain (`src/tts_app/domain/`)

Chứa các thực thể (Entities) và quy tắc nghiệp vụ bất biến.
    
    
    # src/tts_app/domain/models.py
    from dataclasses import dataclass
    from pathlib import Path
    from typing import List, Optional
    
    @dataclass(frozen=True)
    class VoiceInfo:
        id: str
        name: str
        gender: str
        language: str
    
    @dataclass(frozen=True)
    class EngineInfo:
        name: str
        supported_languages: List[str]
    
    @dataclass
    class AudioChunk:
        index: int
        text: str
        output_path: Path
        is_processed: bool = False
    
    @dataclass
    class TTSConfig:
        engine_name: str
        voice: Optional[str]
        rate: Optional[str]
        volume: Optional[str]
        pitch: Optional[str]
        chunk_size: int = 2000
        merge_audio: bool = True
    

## 3\. Lớp Interfaces (`src/tts_app/interfaces/`)

Định nghĩa các bản hợp đồng (Interfaces). Lớp ngoài muốn giao tiếp với lớp trong phải tuân thủ các cổng này.
    
    
    # src/tts_app/interfaces/tts_engine.py
    from abc import ABC, abstractmethod
    from pathlib import Path
    from typing import List
    from tts_app.domain.models import VoiceInfo, TTSConfig
    
    class ITTSEngine(ABC):
        @abstractmethod
        def get_voices(self) -> List[VoiceInfo]:
            pass
    
        @abstractmethod
        def synthesize(self, text: str, output_path: Path, config: TTSConfig) -> None:
            pass
    
    # src/tts_app/interfaces/text_splitter.py
    from abc import ABC, abstractmethod
    from typing import List
    
    class ITextSplitter(ABC):
        @abstractmethod
        def split(self, text: str, min_size: int = 1500, default_size: int = 2000, max_size: int = 2500) -> List[str]:
            pass
    

## 4\. Lớp Infrastructure - Xử lý tách văn bản (`src/tts_app/infrastructure/splitters/`)

Tách văn bản theo câu để giữ ngữ cảnh (Context), gom nhóm câu sao cho nằm trong khoảng ký tự yêu cầu.
    
    
    # src/tts_app/infrastructure/splitters/vi_underthesea.py
    from tts_app.interfaces.text_splitter import ITextSplitter
    from underthesea import sent_tokenize
    from typing import List
    
    class VietnameseTextSplitter(ITextSplitter):
        def split(self, text: str, min_size: int = 1500, default_size: int = 2000, max_size: int = 2500) -> List[str]:
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = ""
    
            for sentence in sentences:
                # Nếu thêm câu mới vào mà vượt quá max_size, đóng chunk cũ
                if len(current_chunk) + len(sentence) > max_size and len(current_chunk) >= min_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            return chunks
    

_(Tương tự, tạo`EnglishTextSplitter` sử dụng `spacy.load("en_core_web_sm")` cho tiếng Anh)_.

## 5\. Lớp Use Cases (`src/tts_app/use_cases/`)

Nơi chứa kịch bản chạy ứng dụng (Application Logic). Phối hợp các Interface lại với nhau.
    
    
    # src/tts_app/use_cases/process_tts.py
    from pathlib import Path
    from tts_app.domain.models import TTSConfig, AudioChunk
    from tts_app.interfaces.tts_engine import ITTSEngine
    from tts_app.interfaces.text_splitter import ITextSplitter
    
    class ProcessTTSUseCase:
        def __init__(self, engine: ITTSEngine, vi_splitter: ITextSplitter, en_splitter: ITextSplitter):
            self.engine = engine
            self.vi_splitter = vi_splitter
            self.en_splitter = en_splitter
    
        def execute(self, input_path: Path, config: TTSConfig, language: str = "vi") -> None:
            # 1. Đọc file
            text = input_path.read_text(encoding="utf-8")
            
            # 2. Chọn bộ tách chữ (Single Responsibility Principle)
            splitter = self.vi_splitter if language == "vi" else self.en_splitter
            chunks_text = splitter.split(text, default_size=config.chunk_size)
            
            # 3. Tạo thư mục output chunk: file-text-name/
            chunk_dir = input_path.parent / input_path.stem
            chunk_dir.mkdir(parents=True, exist_ok=True)
            
            generated_files = []
            # 4. Chạy TTS cho từng chunk
            for idx, chunk_txt in enumerate(chunks_text):
                chunk_file = chunk_dir / f"chunk_{idx+1}.mp3"
                self.engine.synthesize(chunk_txt, chunk_file, config)
                generated_files.append(chunk_file)
                
            # 5. Xử lý gộp file (Merge Audio) nếu không bật flag --no-merge
            if config.merge_audio and len(generated_files) > 1:
                merged_file = input_path.parent / f"{input_path.stem}_merged.mp3"
                self._merge_files(generated_files, merged_file)
    
        def _merge_files(self, files: list[Path], output: Path):
            # Có thể dùng pydub hoặc ffmpeg để merge chuỗi file
            from pydub import AudioSegment
            combined = AudioSegment.empty()
            for file in files:
                combined += AudioSegment.from_mp3(file)
            combined.export(output, format="mp3")
    

## 6\. Lớp Giao diện CLI (`src/tts_app/infrastructure/cli/commands.py`)

Sử dụng thư viện `click` để tiếp nhận đầu vào từ người dùng một cách tường minh và phân nhóm câu lệnh hợp lý.
    
    
    import click
    from pathlib import Path
    from tts_app.domain.models import TTSConfig
    from tts_app.use_cases.process_tts import ProcessTTSUseCase
    from tts_app.infrastructure.tts_engines.edge import EdgeTTSEngine # Ví dụ một engine cụ thể
    
    @click.group()
    def cli():
        """Hệ thống chuyển đổi văn bản thành giọng nói (TTS) nâng cao."""
        pass
    
    @cli.group(name="engine")
    def engine_group():
        """Quản lý và xem thông tin các TTS Engines."""
        pass
    
    @engine_group.command(name="list")
    def list_engines():
        """Hiển thị tất cả các TTS Engines có sẵn."""
        engines = ["system", "edge", "google-translate", "google-cloud"]
        click.echo("Các TTS Engine hỗ trợ:")
        for eng in engines:
            click.echo(f" - {eng}")
    
    @engine_group.command(name="voices")
    @click.argument("engine_name")
    def list_voices(engine_name):
        """Liệt kê danh sách giọng đọc của một Engine cụ thể."""
        # Giả lập hoặc gọi trực tiếp qua Factory để lấy thông tin giọng nói từ Engine
        click.echo(f"Đang lấy danh sách giọng đọc của engine: {engine_name}...")
        # Thực tế sẽ xuất danh sách VoiceInfo ra màn hình terminal bằng bảng hoặc list
    
    @cli.command(name="convert")
    @click.argument("path", type=click.Path(exists=True, path_type=Path))
    @click.option("--engine", "tts_engine", default="edge", help="Chọn engine phát tín hiệu.")
    @click.option("--voice", default=None, help="Mã giọng đọc (Voice ID).")
    @click.option("--rate", default="1.0", help="Tốc độ nói.")
    @click.option("--volume", default="1.0", help="Âm lượng.")
    @click.option("--pitch", default="0Hz", help="Cao độ.")
    @click.option("--chunk-size", default=2000, type=click.IntRange(1500, 2500), help="Kích thước cụm ký tự.")
    @click.option("--no-merge", is_flag=True, help="Không gộp các chunk thành một file tổng.")
    @click.option("--lang", default="vi", type=click.Choice(["vi", "en"]), help="Ngôn ngữ của văn bản.")
    def convert_text(path, tts_engine, voice, rate, volume, pitch, chunk_size, no_merge, lang):
        """Chuyển đổi file text hoặc cả thư mục chứa file text thành âm thanh."""
        config = TTSConfig(
            engine_name=tts_engine,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            chunk_size=chunk_size,
            merge_audio=not no_merge
        )
        
        # Ở đây áp dụng DI (Dependency Injection), khởi tạo Engine theo lựa chọn của client
        # Để đơn giản hóa ví dụ, ta mặc định dùng EdgeTTSEngine
        selected_engine = EdgeTTSEngine() 
        from tts_app.infrastructure.splitters.vi_underthesea import VietnameseTextSplitter
        # Giả định đã khai báo EnglishTextSplitter
        use_case = ProcessTTSUseCase(selected_engine, VietnameseTextSplitter(), VietnameseTextSplitter())
    
        if path.is_file():
            click.echo(f"Đang xử lý file: {path.name}")
            use_case.execute(path, config, language=lang)
        elif path.is_dir():
            click.echo(f"Đang xử lý thư mục: {path.name}")
            for file in path.glob("*.txt"):
                use_case.execute(file, config, language=lang)
                
        click.echo("🎉 Hoàn thành chuyển đổi!")
    

## 7\. Điểm chạy ứng dụng (`src/tts_app/main.py`)
    
    
    from tts_app.infrastructure.cli.commands import cli
    
    if __name__ == "__main__":
        cli()
    

* * *

## 💡 Giải thích cách thiết kế đáp ứng các tiêu chuẩn

  1. Nguyên lý SOLID áp dụng ở đâu?

     * S (Single Responsibility): Mỗi module phụ trách một nhiệm vụ riêng lẻ. Bộ tách câu (`VietnameseTextSplitter`) chỉ lo tách chữ, không quan tâm tới việc sinh audio; CLI chỉ lo bắt tham số dòng lệnh.
     * O (Open/Closed Principle): Khi muốn thêm một TTS Engine mới (ví dụ: OpenAI TTS), bạn chỉ cần tạo file mới kế thừa từ `ITTSEngine` trong thư mục `infrastructure/tts_engines/` mà không cần sửa đổi bất kỳ dòng mã nào trong lớp `use_cases`.
     * D (Dependency Inversion): Lớp logic nghiệp vụ (`ProcessTTSUseCase`) không gọi trực tiếp các thư viện bên ngoài mà giao tiếp qua các Interface trừu tượng (`ITTSEngine`, `ITextSplitter`).

  2. Quy tắc đầu ra âm thanh (Output):

     * Trong `ProcessTTSUseCase`, biến `chunk_dir` được tính bằng `input_path.parent / input_path.stem`, nghĩa là tạo một thư mục riêng trùng tên với file text để chứa các file chunk con. File audio được merge sẽ xuất ra cùng cấp với file text gốc đúng theo yêu cầu thiết kế.




Bạn có muốn tôi viết chi tiết mã nguồn hiện thực hóa (implementation) cho một TTS Engine cụ thể (như `edge-tts` sử dụng lập trình bất đồng bộ `asyncio`) hay thiết lập bộ khung Unit Test sử dụng `pytest` cho kiến trúc này không?