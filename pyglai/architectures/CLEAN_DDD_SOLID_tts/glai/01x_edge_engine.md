Dưới đây là phần triển khai mã nguồn chi tiết cho Edge TTS Engine (asyncio), bộ ghép nối âm thanh, cấu hình hoàn chỉnh cho CLI và bộ khung Unit Test via Mocking tuân thủ nghiêm ngặt Clean Architecture.

* * *

## 🚀 Triển khai Edge TTS Engine (`src/tts_app/infrastructure/tts_engines/edge.py`)

Do `edge-tts` hoạt động theo cơ chế bất đồng bộ (`asyncio`), chúng ta sẽ dùng bộ điều phối luồng để bọc mã nguồn bất đồng bộ lại, giúp lớp `Use Case` phía trên giữ được giao diện đồng bộ (synchronous) đơn giản.
    
    
    import asyncio
    from pathlib import Path
    from typing import List
    import edge_tts
    
    from tts_app.domain.models import VoiceInfo, TTSConfig
    from tts_app.interfaces.tts_engine import ITTSEngine
    
    class EdgeTTSEngine(ITTSEngine):
        def get_voices(self) -> List[VoiceInfo]:
            """Lấy danh sách các giọng đọc từ Edge TTS (Chạy đồng bộ bằng cách bọc loop)"""
            async def _fetch():
                voices = await edge_tts.VoicesManager.create()
                return voices.voices
    
            loop = asyncio.get_event_loop()
            raw_voices = loop.run_until_complete(_fetch())
            
            return [
                VoiceInfo(
                    id=v["Name"],
                    name=v["ShortName"],
                    gender=v["Gender"],
                    language=v["Locale"]
                )
                for v in raw_voices
            ]
    
        def synthesize(self, text: str, output_path: Path, config: TTSConfig) -> None:
            """Đóng gói mã async của edge-tts vào hàm sync phù hợp Interface"""
            async def _communicate():
                # Cấu hình mặc định nếu người dùng bỏ trống
                voice = config.voice or "vi-VN-HoaiAnNeural"
                
                # Khởi tạo tiến trình sinh tín hiệu của Edge TTS
                communicate = edge_tts.Communicate(text, voice)
                
                # Áp dụng rate (tốc độ) và volume (âm lượng) theo chuẩn của edge-tts (ví dụ: "+10%", "-5%")
                if config.rate:
                    communicate.rate = config.rate
                if config.volume:
                    communicate.volume = config.volume
                    
                await communicate.save(str(output_path))
    
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_communicate())
    

* * *

## 📦 Factory mẫu khởi tạo Engine (`src/tts_app/infrastructure/tts_engines/factory.py`)

Áp dụng mẫu thiết kế Simple Factory để cô lập việc khởi tạo các Engine cụ thể, giúp ứng dụng dễ dàng mở rộng (Open/Closed Principle).
    
    
    from tts_app.interfaces.tts_engine import ITTSEngine
    from tts_app.infrastructure.tts_engines.edge import EdgeTTSEngine
    # Giả định bạn đã import các engine khác tại đây
    
    class TTSEngineFactory:
        @staticmethod
        def create(engine_name: str) -> ITTSEngine:
            match engine_name.lower():
                case "edge":
                    return EdgeTTSEngine()
                case "system" | "google-translate" | "google-cloud":
                    # Ném lỗi hoặc trả về lớp tương ứng khi bạn cài đặt xong
                    raise NotImplementedError(f"Engine '{engine_name}' đang được phát triển.")
                case _:
                    raise ValueError(f"Không tìm thấy TTS Engine có tên: {engine_name}")
    

* * *

## 📝 Hiện thực hóa bộ tách chữ Tiếng Anh (`src/tts_app/infrastructure/splitters/en_spacy.py`)
    
    
    import spacy
    from typing import List
    from tts_app.interfaces.text_splitter import ITextSplitter
    
    class EnglishTextSplitter(ITextSplitter):
        def __init__(self):
            # Tải mô hình nhỏ của Spacy để tối ưu tốc độ phân tách câu
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Tự động tải nếu môi trường chưa cài đặt gói ngôn ngữ
                from spacy.cli import download
                download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
    
        def split(self, text: str, min_size: int = 1500, default_size: int = 2000, max_size: int = 2500) -> List[str]:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents]
            
            chunks = []
            current_chunk = ""
    
            for sentence in sentences:
                if len(current_chunk) + len(sentence) > max_size and len(current_chunk) >= min_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk = f"{current_chunk} {sentence}".strip()
            
            if current_chunk:
                chunks.append(current_chunk)
                
            return chunks
    

* * *

## ⚙️ Triển khai mã lệnh CLI hoàn chỉnh (`src/tts_app/infrastructure/cli/commands.py`)

Cập nhật lại lệnh CLI để kết nối mượt mà với `ProcessTTSUseCase` thông qua `Factory`.
    
    
    import click
    from pathlib import Path
    
    from tts_app.domain.models import TTSConfig
    from tts_app.use_cases.process_tts import ProcessTTSUseCase
    from tts_app.infrastructure.tts_engines.factory import TTSEngineFactory
    from tts_app.infrastructure.splitters.vi_underthesea import VietnameseTextSplitter
    from tts_app.infrastructure.splitters.en_spacy import EnglishTextSplitter
    
    @click.group()
    def cli():
        """Hệ thống quản lý và chuyển đổi văn bản sang âm thanh (TTS)."""
        pass
    
    @cli.group(name="engine")
    def engine_group():
        """Tra cứu cấu hình bộ máy phát tín hiệu (Engine)."""
        pass
    
    @engine_group.command(name="list")
    def list_engines():
        """Liệt kê danh sách các công nghệ TTS được tích hợp."""
        engines = ["system", "edge", "google-translate", "google-cloud"]
        for eng in engines:
            click.echo(f"• {eng}")
    
    @engine_group.command(name="voices")
    @click.argument("engine_name")
    def list_voices(engine_name):
        """Xem danh sách giọng đọc dựa theo từng Engine cụ thể."""
        try:
            engine = TTSEngineFactory.create(engine_name)
            voices = engine.get_voices()
            click.echo(f"{'ID Giọng':<50} | {'Ngôn ngữ':<12} | {'Giới tính':<10}")
            click.echo("-" * 80)
            for voice in voices:
                click.echo(f"{voice.id:<50} | {voice.language:<12} | {voice.gender:<10}")
        except Exception as e:
            click.echo(f"❌ Lỗi: {e}", err=True)
    
    @cli.command(name="convert")
    @click.argument("path", type=click.Path(exists=True, path_type=Path))
    @click.option("--engine", "engine_name", default="edge", help="Lựa chọn engine xử lý.")
    @click.option("--voice", help="Mã định danh giọng đọc.")
    @click.option("--rate", help="Tốc độ (ví dụ với edge: '+10%', '-5%').")
    @click.option("--volume", help="Âm lượng nói.")
    @click.option("--pitch", help="Độ trầm bổng.")
    @click.option("--chunk-size", default=2000, type=click.IntRange(1500, 2500), help="Giới hạn ký tự mỗi chunk.")
    @click.option("--no-merge", is_flag=True, help="Giữ nguyên các chunk riêng lẻ, không gộp lại.")
    @click.option("--lang", default="vi", type=click.Choice(["vi", "en"]), help="Mã ngôn ngữ nguồn.")
    def convert_text(path, engine_name, voice, rate, volume, pitch, chunk_size, no_merge, lang):
        """Chuyển đổi tệp .txt hoặc toàn bộ tệp trong thư mục chỉ định sang MP3."""
        config = TTSConfig(
            engine_name=engine_name,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            chunk_size=chunk_size,
            merge_audio=not no_merge
        )
        
        try:
            engine = TTSEngineFactory.create(engine_name)
            use_case = ProcessTTSUseCase(
                engine=engine,
                vi_splitter=VietnameseTextSplitter(),
                en_splitter=EnglishTextSplitter()
            )
    
            # Hỗ trợ quét thư mục hoặc tệp đơn lẻ dựa trên cấu trúc DDD
            targets = list(path.glob("*.txt")) if path.is_dir() else [path]
            
            if not targets:
                click.echo("⚠️ Không tìm thấy file văn bản phù hợp.")
                return
    
            for target in targets:
                click.echo(f"🔄 Đang xử lý: {target.name}")
                use_case.execute(target, config, language=lang)
                
            click.echo("🎉 Xử lý hoàn tất!")
            
        except Exception as e:
            click.echo(f"❌ Lỗi hệ thống: {e}", err=True)
    

* * *

## 🧪 Viết Unit Test cho lớp Nghiệp vụ cốt lõi (`tests/test_process_tts.py`)

Do chúng ta tuân thủ nguyên lý Dependency Inversion, lớp `ProcessTTSUseCase` hoàn toàn không phụ thuộc vào thư viện bên ngoài. Chúng ta có thể tạo các Mock Object dựa trên các Interface để kiểm thử logic nghiệp vụ một cách cô lập, tốc độ chạy siêu nhanh mà không sợ tốn chi phí gọi API thật.

Khai báo dependencies kiểm thử bằng lệnh `uv`:
    
    
    uv add pytest --dev
    

Nội dung tệp kiểm thử:
    
    
    import pytest
    from pathlib import Path
    from unittest.mock import MagicMock
    
    from tts_app.domain.models import TTSConfig
    from tts_app.interfaces.tts_engine import ITTSEngine
    from tts_app.interfaces.text_splitter import ITextSplitter
    from tts_app.use_cases.process_tts import ProcessTTSUseCase
    
    class TestProcessTTSUseCase:
        @pytest.fixture
        def mock_dependencies(self):
            """Khởi tạo các mock tuân thủ cấu trúc Interface"""
            engine = MagicMock(spec=ITTSEngine)
            vi_splitter = MagicMock(spec=ITextSplitter)
            en_splitter = MagicMock(spec=ITextSplitter)
            return engine, vi_splitter, en_splitter
    
        def test_execute_should_split_text_and_call_engine_synthesize(self, tmp_path, mock_dependencies):
            # Arrange (Thiết lập giả lập)
            engine, vi_splitter, en_splitter = mock_dependencies
            
            # Giả lập file text đầu vào
            test_file = tmp_path / "tailieu.txt"
            test_file.write_text("Nội dung bài viết mẫu.", encoding="utf-8")
            
            # Giả lập bộ tách chữ trả về 2 đoạn văn bản riêng biệt
            vi_splitter.split.return_value = ["Đoạn thứ nhất", "Đoạn thứ hai"]
            
            config = TTSConfig(
                engine_name="edge",
                voice=None,
                rate=None,
                volume=None,
                pitch=None,
                chunk_size=2000,
                merge_audio=False # Tắt merge để kiểm thử riêng phần xuất chunk
            )
            
            use_case = ProcessTTSUseCase(engine, vi_splitter, en_splitter)
    
            # Act (Thực thi hành động)
            use_case.execute(test_file, config, language="vi")
    
            # Assert (Kiểm tra kết quả)
            # 1. Đảm bảo bộ tách chữ tiếng Việt được gọi đúng cấu hình ký tự
            vi_splitter.split.assert_called_once_with("Nội dung bài viết mẫu.", default_size=2000)
            
            # 2. Đảm bảo engine sinh file chạy chính xác số lần tương ứng với các chunk văn bản
            assert engine.synthesize.call_count == 2
            
            # 3. Kiểm tra xem thư mục chunk có được sinh tự động hay không
            expected_chunk_dir = tmp_path / "tailieu"
            assert expected_chunk_dir.exists()
    

Để chạy toàn bộ hệ thống test, bạn chỉ cần gõ lệnh sau trong Terminal:
    
    
    uv run pytest
    

Nếu cần tôi hỗ trợ cài đặt nâng cao cho Google Cloud TTS Engine (phần yêu cầu cài đặt khóa bảo mật `Google Credentials`) hay tùy biến sâu hơn về thuật toán tối ưu hóa ngữ cảnh câu, bạn hãy cho tôi biết nhé!