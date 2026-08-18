Dưới đây là mã nguồn chi tiết triển khai **4 Provider TTS** tuân thủ nguyên tắc **Dependency Inversion** (Interface `BaseTTSProvider`) và áp dụng **Strategy Pattern** để tích hợp mượt mà vào `TTSOrchestrator`.

---

### 1. Domain Base Interface

```python
# domain/services.py
from abc import ABC, abstractmethod
from domain.value_objects import VoiceConfig

class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, config: VoiceConfig, output_path: str) -> bool:
        """
        Tổng hợp văn bản thành tệp âm thanh (.mp3 hoặc .wav).
        
        :param text: Đoạn văn bản cần chuyển đổi (2000-3000 ký tự)
        :param config: Cấu hình giọng đọc (voice, rate, pitch, volume, language)
        :param output_path: Đường dẫn tệp đầu ra
        :return: True nếu thành công, raise Exception nếu thất bại
        """
        pass

```

---

### 2. Edge-TTS Provider (Edge Web Service)

Sử dụng thư viện `edge-tts` giao tiếp qua WebSocket không tốn phí, hỗ trợ giọng đọc tự nhiên (Azure Neural Voices) cho cả tiếng Việt (`vi-VN-HoaiMyNeural`, `vi-VN-NamMinhNeural`) và tiếng Anh (`en-US-JennyNeural`).

```python
# infrastructure/tts_providers/edge_provider.py
import edge_tts
from domain.services import BaseTTSProvider
from domain.value_objects import VoiceConfig, Language

class EdgeTTSProvider(BaseTTSProvider):
    DEFAULT_VOICES = {
        Language.VIETNAMESE: "vi-VN-HoaiMyNeural",
        Language.ENGLISH: "en-US-JennyNeural"
    }

    async def synthesize(self, text: str, config: VoiceConfig, output_path: str) -> bool:
        voice = config.voice_id or self.DEFAULT_VOICES.get(config.language, "vi-VN-HoaiMyNeural")

        # Định dạng tham số cho edge-tts (+10%, -5Hz, +20%)
        rate_str = f"{int((config.rate - 1.0) * 100):+d}%"
        pitch_str = f"{int(config.pitch):+d}Hz"
        volume_str = f"{int((config.volume - 1.0) * 100):+d}%"

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate_str,
            pitch=pitch_str,
            volume=volume_str
        )
        
        await communicate.save(output_path)
        return True

```

---

### 3. Google Translate TTS Provider (gTTS)

Sử dụng `gTTS` gói API dịch tự động của Google. Đơn giản, miễn phí, hỗ trợ tốt tiếng Việt (`vi`) và tiếng Anh (`en`). Giới hạn: không can thiệp sâu được pitch/volume.

```python
# infrastructure/tts_providers/google_translate_provider.py
import asyncio
from gtts import gTTS
from domain.services import BaseTTSProvider
from domain.value_objects import VoiceConfig

class GoogleTranslateTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, config: VoiceConfig, output_path: str) -> bool:
        lang_code = config.language.value  # 'vi' or 'en'
        
        # gTTS không hỗ trợ async gốc, chạy trên executor để tránh block loop
        loop = asyncio.get_running_loop()
        
        def _run_gtts():
            # config.rate > 1.0 dùng tts bình thường, < 1.0 dùng tts đọc chậm (slow=True)
            is_slow = config.rate < 0.9
            tts = gTTS(text=text, lang=lang_code, slow=is_slow)
            tts.save(output_path)

        await loop.run_in_executor(None, _run_gtts)
        return True

```

---

### 4. Google Cloud Text-to-Speech API Provider (Official SDK)

Provider chính thức sử dụng `google-cloud-texttospeech` với API Key / Service Account credentials. Cung cấp giọng Wavenet / Neural2 chất lượng cao, can thiệp chính xác Pitch, Rate, Volume Gain.

```python
# infrastructure/tts_providers/google_cloud_provider.py
import asyncio
import os
from google.cloud import texttospeech
from domain.services import BaseTTSProvider
from domain.value_objects import VoiceConfig, Language

class GoogleCloudTTSProvider(BaseTTSProvider):
    DEFAULT_VOICES = {
        Language.VIETNAMESE: "vi-VN-Wavenet-A",
        Language.ENGLISH: "en-US-Neural2-F"
    }

    def __init__(self, api_key: str = None, credentials_path: str = None):
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            self.client = texttospeech.TextToSpeechClient()
        elif api_key:
            self.client = texttospeech.TextToSpeechClient(client_options={"api_key": api_key})
        else:
            # Tự động đọc từ biến môi trường mặc định
            self.client = texttospeech.TextToSpeechClient()

    async def synthesize(self, text: str, config: VoiceConfig, output_path: str) -> bool:
        loop = asyncio.get_running_loop()

        def _call_api():
            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice_name = config.voice_id or self.DEFAULT_VOICES.get(config.language, "vi-VN-Wavenet-A")
            lang_code = "vi-VN" if config.language == Language.VIETNAMESE else "en-US"

            voice_params = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_name
            )

            # Quy đổi Volume sang dB (-96.0 dB đến 16.0 dB)
            # Volume scale 1.0 = 0dB; 2.0 ≈ +6dB; 0.5 ≈ -6dB
            import math
            volume_gain_db = 20 * math.log10(config.volume) if config.volume > 0 else -96.0

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=config.rate,          # Range [0.25, 4.0]
                pitch=config.pitch,                 # Range [-20.0, 20.0] semitones
                volume_gain_db=volume_gain_db
            )

            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config
            )

            with open(output_path, "wb") as out:
                out.write(response.audio_content)

        await loop.run_in_executor(None, _call_api)
        return True

```

---

### 5. System TTS Provider (OS Native: pyttsx3)

Sử dụng engine TTS có sẵn của HĐH (SAPI5 trên Windows, NSSpeechSynthesizer trên macOS, espeak trên Linux) thông qua thư viện `pyttsx3`. Không yêu cầu kết nối Internet.

```python
# infrastructure/tts_providers/system_provider.py
import asyncio
import pyttsx3
from domain.services import BaseTTSProvider
from domain.value_objects import VoiceConfig

class SystemTTSProvider(BaseTTSProvider):
    async def synthesize(self, text: str, config: VoiceConfig, output_path: str) -> bool:
        loop = asyncio.get_running_loop()

        def _run_system_tts():
            # Khởi tạo engine mới cho từng luồng để tránh lỗi threading của pyttsx3
            engine = pyttsx3.init()

            # 1. Chỉnh Voice ID
            if config.voice_id:
                engine.setProperty('voice', config.voice_id)
            else:
                # Tự chọn voice phù hợp với ngôn ngữ nếu không chỉ định
                voices = engine.getProperty('voices')
                lang_tag = config.language.value
                for v in voices:
                    if lang_tag in v.id.lower() or lang_tag in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break

            # 2. Chỉnh Tốc độ (Default rate của pyttsx3 ~ 200 wpm)
            default_rate = engine.getProperty('rate')
            engine.setProperty('rate', int(default_rate * config.rate))

            # 3. Chỉnh Âm lượng [0.0 -> 1.0]
            engine.setProperty('volume', min(max(config.volume, 0.0), 1.0))

            # 4. Xuất file audio
            engine.save_to_file(text, output_path)
            engine.runAndWait()

        await loop.run_in_executor(None, _run_system_tts)
        return True

```

---

### 6. Provider Factory (Inversion of Control)

Lớp Factory hỗ trợ `TTSOrchestrator` hoặc Click CLI dễ dàng khởi tạo Provider đúng dựa theo chuỗi cấu hình.

```python
# infrastructure/tts_providers/factory.py
from domain.services import BaseTTSProvider
from domain.value_objects import ProviderType
from infrastructure.tts_providers.edge_provider import EdgeTTSProvider
from infrastructure.tts_providers.google_translate_provider import GoogleTranslateTTSProvider
from infrastructure.tts_providers.google_cloud_provider import GoogleCloudTTSProvider
from infrastructure.tts_providers.system_provider import SystemTTSProvider

class TTSProviderFactory:
    @staticmethod
    def create(provider_type: ProviderType, **kwargs) -> BaseTTSProvider:
        if provider_type == ProviderType.EDGE:
            return EdgeTTSProvider()
        elif provider_type == ProviderType.GOOGLE_TRANSLATE:
            return GoogleTranslateTTSProvider()
        elif provider_type == ProviderType.GOOGLE_CLOUD:
            return GoogleCloudTTSProvider(
                api_key=kwargs.get("api_key"),
                credentials_path=kwargs.get("credentials_path")
            )
        elif provider_type == ProviderType.SYSTEM:
            return SystemTTSProvider()
        else:
            raise ValueError(f"Provider {provider_type} không được hỗ trợ.")

```