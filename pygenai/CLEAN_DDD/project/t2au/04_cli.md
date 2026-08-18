Dưới đây là tệp `presentation/cli.py` hoàn chỉnh. Đây là Entry Point (điểm khởi đầu) của ứng dụng, đóng vai trò **Dependency Injection Container** để khởi tạo các module từ lớp Infrastructure, đóng gói dữ liệu đầu vào thành Domain Value Objects, và truyền cho Application Use Case (`TTSOrchestrator`) xử lý.

```python
# presentation/cli.py
import sys
import click
import asyncio
from pathlib import Path
from typing import List

# Import Domain
from domain.value_objects import VoiceConfig, Language, ProviderType

# Import Application
from application.tts_orchestrator import TTSOrchestrator

# Import Infrastructure
from infrastructure.tts_providers.factory import TTSProviderFactory
from infrastructure.persistence.state_repository import StateRepository
from infrastructure.nlp.text_splitter import SmartTextSplitter
from infrastructure.audio.merger import AudioMerger

def get_input_files(input_path: Path) -> List[Path]:
    """Phân giải đường dẫn đầu vào thành danh sách các file text."""
    if input_path.is_file():
        if input_path.suffix != '.txt':
            click.secho(f"Cảnh báo: Tệp {input_path.name} không phải là .txt", fg="yellow")
        return [input_path]
    elif input_path.is_dir():
        files = list(input_path.glob("*.txt"))
        if not files:
            click.secho(f"Lỗi: Không tìm thấy tệp .txt nào trong thư mục {input_path}", fg="red")
            sys.exit(1)
        return files
    else:
        click.secho("Lỗi: Đường dẫn đầu vào không hợp lệ.", fg="red")
        sys.exit(1)

@click.group()
def cli():
    """Hệ thống chuyển đổi Text-to-Speech đa Provider CLI."""
    pass

@cli.command()
@click.option('--input', '-i', 'input_path', required=True, type=click.Path(exists=True, path_type=Path), help='Đường dẫn tới file .txt hoặc thư mục chứa các file .txt')
@click.option('--output', '-o', 'output_dir', default="./output", type=click.Path(path_type=Path), help='Thư mục lưu file audio đầu ra (Mặc định: ./output)')
@click.option('--lang', '-l', type=click.Choice(['vi', 'en']), default='vi', help='Ngôn ngữ văn bản (Mặc định: vi)')
@click.option('--provider', '-p', type=click.Choice(['system', 'edge', 'google_translate', 'google_cloud']), default='edge', help='Engine TTS (Mặc định: edge)')
@click.option('--voice', default=None, help='Tên voice cụ thể (VD: vi-VN-HoaiMyNeural)')
@click.option('--rate', type=float, default=1.0, help='Tốc độ đọc (1.0 là bình thường, 1.2 là nhanh)')
@click.option('--pitch', type=float, default=0.0, help='Cao độ (Mặc định: 0.0)')
@click.option('--volume', type=float, default=1.0, help='Âm lượng (Mặc định: 1.0)')
@click.option('--api-key', envvar='GOOGLE_API_KEY', help='API Key cho Google Cloud TTS (Có thể dùng biến môi trường GOOGLE_API_KEY)')
@click.option('--credentials-path', type=click.Path(exists=True), help='Đường dẫn file JSON service account cho Google Cloud')
@click.option('--retry-failed', is_flag=True, help='Chỉ chạy lại các chunk đã bị đánh dấu FAILED trước đó')
@click.option('--resume', is_flag=True, help='Khôi phục trạng thái và tiếp tục chạy các chunk PENDING')
@click.option('--max-retries', type=int, default=3, help='Số lần thử lại tối đa cho mỗi chunk lỗi (Mặc định: 3)')
def convert(
    input_path: Path, output_dir: Path, lang: str, provider: str, 
    voice: str, rate: float, pitch: float, volume: float, 
    api_key: str, credentials_path: str, retry_failed: bool, resume: bool, max_retries: int
):
    """Chuyển đổi file/folder text thành file audio hợp nhất."""
    
    # 1. Khởi tạo Domain Value Objects
    language = Language.VIETNAMESE if lang == 'vi' else Language.ENGLISH
    provider_type = ProviderType(provider)
    
    config = VoiceConfig(
        voice_id=voice,
        rate=rate,
        pitch=pitch,
        volume=volume,
        language=language
    )

    # 2. Dependency Injection: Khởi tạo các thành phần Infrastructure
    try:
        tts_provider = TTSProviderFactory.create(
            provider_type=provider_type,
            api_key=api_key,
            credentials_path=credentials_path
        )
    except Exception as e:
        click.secho(f"Lỗi khởi tạo Provider: {e}", fg="red")
        sys.exit(1)

    state_repo = StateRepository(state_file=Path(".tts_state.json"))
    text_splitter = SmartTextSplitter(min_chars=2000, max_chars=3000)
    audio_merger = AudioMerger()

    # 3. Khởi tạo Use Case Orchestrator
    orchestrator = TTSOrchestrator(
        provider=tts_provider,
        state_repo=state_repo,
        text_splitter=text_splitter,
        audio_merger=audio_merger,
        temp_dir=Path(".tts_temp")
    )

    # 4. Phân giải danh sách file đầu vào
    files_to_process = get_input_files(input_path)
    click.secho(f"Bắt đầu xử lý {len(files_to_process)} tệp văn bản...", fg="cyan")
    click.echo(f"Cấu hình: Provider={provider_type.value}, Lang={language.value}, Rate={rate}, Voice={voice or 'Auto'}")

    # 5. Thực thi bất đồng bộ Orchestrator Use Case
    async def run_orchestrator():
        await orchestrator.execute(
            file_paths=files_to_process,
            config=config,
            output_dir=output_dir,
            max_retries=max_retries,
            resume=resume,
            retry_failed_only=retry_failed
        )

    try:
        asyncio.run(run_orchestrator())
        click.secho("\nĐã hoàn thành toàn bộ quá trình xử lý!", fg="green", bold=True)
    except KeyboardInterrupt:
        click.secho("\nĐã hủy quá trình bởi người dùng (Ctrl+C). Dùng cờ --resume để chạy tiếp lần sau.", fg="yellow")
        sys.exit(0)
    except Exception as e:
        click.secho(f"\nLỗi hệ thống không mong muốn: {e}", fg="red", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()

```

### Cách chạy kiểm thử CLI

Bạn có thể chạy thử CLI thông qua terminal như sau:

**Xử lý thư mục với tùy chọn Edge-TTS và Resume:**

```bash
python -m presentation.cli convert -i /path/to/text_folder -o /path/to/output_folder -p edge --lang vi --resume

```

**Thử lại các chunk bị lỗi với Provider Google Cloud:**

```bash
python -m presentation.cli convert -i /path/to/text.txt -p google_cloud --credentials-path ./service-account.json --retry-failed

```