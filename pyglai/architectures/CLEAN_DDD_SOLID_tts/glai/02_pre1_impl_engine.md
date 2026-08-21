Dưới đây là phần mã nguồn chi tiết cho các thành phần Cơ sở hạ tầng (Infrastructure) còn lại bao gồm Google Cloud TTS Engine, System TTS Engine (sử dụng thư viện `pyttsx3`), và Google Translate TTS (sử dụng thư viện `gTTS`), cùng với các hướng dẫn thiết lập biến môi trường chuẩn xác.

* * *

## 1\. Cài đặt Google Cloud TTS Engine

Engine này sử dụng thư viện chính thức từ Google Cloud. Để chạy được, bạn cần tạo một Service Account trên Google Cloud Console, cấp quyền `Text-to-Speech API Admin`, tải file JSON credential về máy và cấu hình biến môi trường.

## `infrastructure/tts_engines/google_cloud_engine.py`
    
    
    from pathlib import Path
    from google.cloud import texttospeech
    from tts_cli.domain.interfaces import ITTSEngine
    from tts_cli.domain.models import TextChunk, TTSConfig, AudioArtifact
    
    class GoogleCloudTTSEngine(ITTSEngine):
        def __init__(self):
            # Tự động tìm kiếm file credentials cấu hình qua biến môi trường:
            # GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
            self._client = texttospeech.TextToSpeechClient()
    
        def synthesize(self, chunk: TextChunk, config: TTSConfig, output_path: Path) -> AudioArtifact:
            # 1. Thiết lập cấu hình văn bản đầu vào
            synthesis_input = texttospeech.SynthesisInput(text=chunk.text)
    
            # 2. Cấu hình lựa chọn Voice & Ngôn ngữ
            lang_code = "vi-VN" if chunk.language == "vi" else "en-US"
            # Nếu người dùng truyền vào tên voice cụ thể thì dùng, ngược lại dùng mặc định hệ thống
            voice_name = config.voice or ("vi-VN-Neural2-A" if chunk.language == "vi" else "en-US-Neural2-F")
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=lang_code,
                name=voice_name
            )
    
            # 3. Cấu hình các thông số Audio (Rate, Pitch, Volume)
            # Google Cloud yêu cầu chuyển đổi giá trị số:
            # speaking_rate: từ 0.25 đến 4.0 (mặc định 1.0)
            # pitch: từ -20.0 đến 20.0 semitones (mặc định 0.0)
            # volume_gain_db: từ -96.0 đến 16.0 dB (mặc định 0.0)
            
            speaking_rate = float(config.rate) if config.rate else 1.0
            pitch = float(config.pitch) if config.pitch else 0.0
            volume_gain_db = float(config.volume) if config.volume else 0.0
    
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospevest.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                volume_gain_db=volume_gain_db
            )
    
            # 4. Thực thi request gửi lên API Google Cloud
            response = self._client.synthesize_speech(
                input=synthesis_input, 
                voice=voice, 
                audio_config=audio_config
            )
    
            # 5. Ghi dữ liệu nhị phân trả về ra file
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
    
            return AudioArtifact(file_path=output_path)
    

* * *

## 2\. Cài đặt Google Translate TTS Engine (gTTS)

Engine này miễn phí, không cần token hay credentials vì nó gọi trực tiếp API không chính thức của Google Translate. Tuy nhiên, nó bị giới hạn các tùy chọn cấu hình nâng cao như tinh chỉnh sâu giọng nói, độ cao (pitch) hay âm lượng.

Cập nhật gói phụ thuộc bằng cách thêm `gtts` vào danh sách dependency nếu chưa có.

## `infrastructure/tts_engines/google_translate_engine.py`
    
    
    from pathlib import Path
    from gtts import gTTS
    from tts_cli.domain.interfaces import ITTSEngine
    from tts_cli.domain.models import TextChunk, TTSConfig, AudioArtifact
    
    class GoogleTranslateTTSEngine(ITTSEngine):
        def synthesize(self, chunk: TextChunk, config: TTSConfig, output_path: Path) -> AudioArtifact:
            lang_code = "vi" if chunk.language == "vi" else "en"
            
            # Thư viện gTTS hỗ trợ tham số 'slow' (True/False) để đổi tốc độ đọc.
            # Chúng ta giả định nếu config.rate được đặt là "slow" thì đọc chậm, ngược lại đọc bình thường.
            is_slow = True if config.rate == "slow" else False
    
            # Khởi tạo đối tượng gTTS
            tts = gTTS(text=chunk.text, lang=lang_code, slow=is_slow)
            
            # Lưu file trực tiếp xuống ổ đĩa
            tts.save(str(output_path))
            
            return AudioArtifact(file_path=output_path)
    

* * *

## 3\. Cài đặt System TTS Engine (Offline Hoàn Toàn)

Engine này sử dụng phần cứng và các thư viện TTS có sẵn của hệ điều hành máy chủ (SAPI5 trên Windows, NSSpeechSynthesizer trên macOS, hoặc espeak trên Linux). Nó chạy hoàn toàn offline mà không tốn băng thông internet.

_Để sử dụng, bạn cần bổ sung gói phụ thuộc`pyttsx3>=2.90` vào file `pyproject.toml`._

## `infrastructure/tts_engines/system_engine.py`
    
    
    from pathlib import Path
    import pyttsx3
    from tts_cli.domain.interfaces import ITTSEngine
    from tts_cli.domain.models import TextChunk, TTSConfig, AudioArtifact
    
    class SystemTTSEngine(ITTSEngine):
        def synthesize(self, chunk: TextChunk, config: TTSConfig, output_path: Path) -> AudioArtifact:
            # Khởi tạo engine của hệ thống
            engine = pyttsx3.init()
    
            # 1. Tìm và thiết lập Voice dựa trên ngôn ngữ hệ thống hỗ trợ
            voices = engine.getProperty("voices")
            selected_voice_id = None
            
            # Nếu người dùng truyền chính xác tên/ID voice qua CLI
            if config.voice:
                for v in voices:
                    if config.voice in v.name or config.voice == v.id:
                        selected_voice_id = v.id
                        break
    
            # Nếu không tìm thấy hoặc không truyền, tự động chọn dựa trên ngôn ngữ chunk
            if not selected_voice_id:
                for v in voices:
                    # Kiểm tra thuộc tính ngôn ngữ của giọng đọc hệ thống
                    lang_identifiers = [l.lower() for l in getattr(v, "languages", [])]
                    target_lang = "vi" if chunk.language == "vi" else "en"
                    
                    if any(target_lang in lang for lang in lang_identifiers) or target_lang in v.name.lower():
                        selected_voice_id = v.id
                        break
            
            if selected_voice_id:
                engine.setProperty("voice", selected_voice_id)
    
            # 2. Cấu hình Tốc độ đọc (Rate) - Mặc định của pyttsx3 thường là ~200 từ/phút
            if config.rate:
                try:
                    engine.setProperty("rate", int(config.rate))
                except ValueError:
                    pass  # Bỏ qua nếu định dạng đầu vào CLI không phải là số nguyên
    
            # 3. Cấu hình Âm lượng (Volume) - Giá trị chạy từ 0.0 đến 1.0
            if config.volume:
                try:
                    engine.setProperty("volume", float(config.volume))
                except ValueError:
                    pass
    
            #Lưu ý: pyttsx3 không hỗ trợ can thiệp sâu vào cao độ (Pitch) trực tiếp qua code.
    
            # 4. Thực thi tác vụ sinh tệp âm thanh (Hỗ trợ định dạng wav/mp3 tùy thuộc OS)
            # Để đảm bảo tính đồng bộ mp3, pyttsx3 sẽ ghi ra file tạm thời rồi bạn có thể xuất chuẩn.
            engine.save_to_file(chunk.text, str(output_path))
            engine.runAndWait()
    
            return AudioArtifact(file_path=output_path)
    

* * *

## 4\. Cập nhật Hàm Khởi Chạy (Main Entrypoint) để Đăng Ký Engine

Để các Engine này hoạt động, chúng ta đăng ký chúng vào `dict` điều phối ở lớp Giao diện (`main.py`). Bản thân kiến trúc Core của UseCase sẽ không cần chỉnh sửa bất cứ thứ gì, tuân thủ tuyệt đối nguyên lý Open/Closed Principle.

## Cập nhật trong `main.py`
    
    
    # Thêm các import mới ở đầu file main.py
    from tts_cli.infrastructure.tts_engines.system_engine import SystemTTSEngine
    from tts_cli.infrastructure.tts_engines.google_translate_engine import GoogleTranslateTTSEngine
    from tts_cli.infrastructure.tts_engines.google_cloud_engine import GoogleCloudTTSEngine
    
    # ... Giữ nguyên phần khai báo @click.command() bên trên ...
    
    def cli(input_path, lang, tts_engine, voice, rate, volume, pitch, no_merge, chunk_size):
        try:
            config = TTSConfig(
                engine=tts_engine,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch,
                chunk_size=chunk_size,
                merge_audio=not no_merge
            )
    
            processors = {
                "vi": VietnameseTextProcessor(),
                "en": EnglishTextProcessor()
            }
            
            # Đăng ký toàn bộ các dịch vụ Engine mới vào Dictionary (Dependency Injection thủ công)
            tts_engines = {
                "edge": EdgeTTSEngine(),
                "system": SystemTTSEngine(),
                "google-translate": GoogleTranslateTTSEngine(),
                "google-cloud": GoogleCloudTTSEngine()
            }
            
            merger = PydubAudioMerger()
    
            # Thực thi xử lý dòng chảy UseCase độc lập
            use_case = ProcessTextToSpeechUseCase(processors, tts_engines, merger)
            use_case.execute(input_path, config, lang)
            
            click.echo(click.style("Xử lý Text-to-Speech thành công hoàn tất!", fg="green"))
    
        except Exception as e:
            click.echo(click.style(f"Lỗi hệ thống: {str(e)}", fg="red"), err=True)
    

* * *

## 5\. Cách chạy ứng dụng bằng `uv` trên CLI

Sau khi hoàn tất cấu trúc, bạn kích hoạt môi trường và thực thi trực tiếp ứng dụng bằng các lệnh sau:
    
    
    # Cài đặt toàn bộ dependencies trong file pyproject.toml tự động qua uv
    uv sync
    
    # Chạy kiểm tra với thư mục chứa nhiều file text sử dụng Edge-TTS (mặc định)
    uv run tts-processor /path/to/text_folder/ --lang vi --tts-engine edge
    
    # Chạy với Google Cloud TTS, truyền config cấu hình giọng đọc cụ thể
    export GOOGLE_APPLICATION_CREDENTIALS="/Users/project/secrets/gcp-key.json"
    uv run tts-processor /path/to/document.txt --lang en --tts-engine google-cloud --voice en-US-Neural2-F --rate 1.1
    
    # Chạy ứng dụng và yêu cầu không merge file tổng (chỉ giữ lại các chunk cô lập)
    uv run tts-processor /path/to/vietnamese_doc.txt --lang vi --tts-engine google-translate --no-merge --chunk-size 1800
    

Bạn có muốn tôi bổ sung thêm phần Unit Test độc lập bằng `pytest` để kiểm thử phần xử lý Logic bóc tách ngữ cảnh văn bản (`TextChunkerService`) trong tầng Domain không?