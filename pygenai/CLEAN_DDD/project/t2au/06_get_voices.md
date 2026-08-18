Dưới đây là mã nguồn chi tiết để bổ sung lệnh **`voice-list`** (hoặc `voices`) vào CLI Click. Lệnh này cho phép người dùng tra cứu danh sách các voice khả dụng theo **Provider** và **Ngôn ngữ** (vi/en).

---

### 1. Bổ sung Method `get_voices` vào các TTS Provider

Thêm phương thức trả về danh sách giọng đọc trong `BaseTTSProvider` và triển khai trên các provider:

```python
# domain/services.py (Bổ sung vào BaseTTSProvider)
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseTTSProvider(ABC):
    # ... (giữ nguyên hàm synthesize cũ) ...

    @abstractmethod
    async def get_voices(self, language_code: str) -> List[Dict[str, str]]:
        """Trả về danh sách voice dưới dạng [{id: ..., name: ..., gender: ...}]"""
        pass

```

```python
# infrastructure/tts_providers/edge_provider.py (Triển khai get_voices)
import edge_tts
from domain.services import BaseTTSProvider

class EdgeTTSProvider(BaseTTSProvider):
    # ... (giữ nguyên hàm synthesize cũ) ...

    async def get_voices(self, language_code: str) -> list[dict[str, str]]:
        all_voices = await edge_tts.list_voices()
        # Lọc theo ngôn ngữ ('vi' -> 'vi-VN', 'en' -> 'en-US' / 'en-')
        filtered_voices = []
        for v in all_voices:
            locale = v.get("Locale", "").lower()
            if (language_code == "vi" and "vi-" in locale) or (language_code == "en" and "en-" in locale):
                filtered_voices.append({
                    "id": v["ShortName"],
                    "name": v["FriendlyName"],
                    "gender": v.get("Gender", "Unknown")
                })
        return filtered_voices

```

```python
# infrastructure/tts_providers/google_translate_provider.py
class GoogleTranslateTTSProvider(BaseTTSProvider):
    async def get_voices(self, language_code: str) -> list[dict[str, str]]:
        # Google Translate TTS dùng voice mặc định của hệ thống Google theo mã quốc gia
        default_voice = "vi" if language_code == "vi" else "en"
        return [{
            "id": default_voice,
            "name": f"Google Translate Default ({default_voice.upper()})",
            "gender": "Standard"
        }]

```

```python
# infrastructure/tts_providers/google_cloud_provider.py
class GoogleCloudTTSProvider(BaseTTSProvider):
    async def get_voices(self, language_code: str) -> list[dict[str, str]]:
        loop = asyncio.get_running_loop()
        target_lang = "vi-VN" if language_code == "vi" else "en-US"

        def _fetch():
            response = self.client.list_voices(language_code=target_lang)
            results = []
            for voice in response.voices:
                results.append({
                    "id": voice.name,
                    "name": voice.name,
                    "gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name
                })
            return results

        return await loop.run_in_executor(None, _fetch)

```

```python
# infrastructure/tts_providers/system_provider.py
import pyttsx3

class SystemTTSProvider(BaseTTSProvider):
    async def get_voices(self, language_code: str) -> list[dict[str, str]]:
        loop = asyncio.get_running_loop()

        def _fetch():
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            results = []
            for v in voices:
                v_id = v.id.lower()
                v_name = v.name.lower()
                # Kiểm tra tương đối mã ngôn ngữ trong thông tin voice
                if language_code in v_id or language_code in v_name:
                    results.append({
                        "id": v.id,
                        "name": v.name,
                        "gender": "Native OS"
                    })
            return results

        return await loop.run_in_executor(None, _fetch)

```

---

### 2. Thêm Lệnh `voices` vào `presentation/cli.py`

Thêm sub-command mới vào file `cli.py` hiển thị dạng bảng trực quan:

```python
# presentation/cli.py (Bổ sung lệnh mới vào group cli)

@cli.command(name="voices")
@click.option('--provider', '-p', type=click.Choice(['system', 'edge', 'google_translate', 'google_cloud']), default='edge', help='Engine TTS cần xem danh sách voice')
@click.option('--lang', '-l', type=click.Choice(['vi', 'en']), default='vi', help='Lọc giọng theo ngôn ngữ (Mặc định: vi)')
@click.option('--api-key', envvar='GOOGLE_API_KEY', help='API Key nếu xem Google Cloud TTS')
def list_voices(provider: str, lang: str, api_key: str):
    """Hiển thị danh sách Voice hỗ trợ theo Provider và Ngôn ngữ."""
    
    provider_type = ProviderType(provider)
    
    try:
        tts_provider = TTSProviderFactory.create(
            provider_type=provider_type,
            api_key=api_key
        )
    except Exception as e:
        click.secho(f"Lỗi khởi tạo Provider: {e}", fg="red")
        sys.exit(1)

    async def fetch_and_display():
        voices = await tts_provider.get_voices(lang)
        if not voices:
            click.secho(f"Không tìm thấy voice nào cho provider '{provider}' với ngôn ngữ '{lang}'.", fg="yellow")
            return

        click.secho(f"\nDanh sách Voice cho [{provider.upper()}] - Ngôn ngữ [{lang.upper()}]:", fg="cyan", bold=True)
        click.echo("=" * 70)
        click.echo(f"{'Voice ID':<35} | {'Giới tính':<10} | {'Tên hiển thị'}")
        click.echo("-" * 70)
        
        for v in voices:
            click.echo(f"{v['id']:<35} | {v['gender']:<10} | {v['name']}")
        click.echo("=" * 70)

    asyncio.run(fetch_and_display())

```

---

### 3. Cú pháp sử dụng CLI

Liệt kê giọng **tiếng Việt** của **Edge-TTS**:

```bash
python -m presentation.cli voices -p edge -l vi

```

Liệt kê giọng **tiếng Anh** của **Google Cloud**:

```bash
python -m presentation.cli voices -p google_cloud -l en --api-key "YOUR_KEY"

```

Liệt kê giọng **tiếng Việt** cài sẵn trên **Hệ thống (OS)**:

```bash
python -m presentation.cli voices -p system -l vi

```