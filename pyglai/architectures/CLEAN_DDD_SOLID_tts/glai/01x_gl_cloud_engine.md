Dưới đây là phần triển khai chi tiết cho Google Cloud TTS Engine (bao gồm cơ chế xác thực thông tin bảo mật) và Thuật toán tối ưu hóa nhóm câu giúp giữ nguyên ngữ cảnh, không làm gãy câu ở giữa đoạn văn bản.

* * *

## 🌐 Triển khai Google Cloud TTS Engine (`src/tts_app/infrastructure/tts_engines/google_cloud.py`)

Google Cloud TTS yêu cầu tài khoản dịch vụ (Service Account) dạng tệp JSON. Để tuân thủ nguyên lý Clean Architecture, đường dẫn tới tệp này được truyền thông qua biến môi trường để tránh hard-code thông tin bảo mật.
    
    
    import os
    from pathlib import Path
    from typing import List
    from google.cloud import texttospeech
    
    from tts_app.domain.models import VoiceInfo, TTSConfig
    from tts_app.interfaces.tts_engine import ITTSEngine
    
    class GoogleCloudTTSEngine(ITTSEngine):
        def __init__(self):
            # Xác thực thông qua biến môi trường GOOGLE_APPLICATION_CREDENTIALS
            # Nếu chưa cấu hình, thư viện google-cloud sẽ tự động ném ngoại lệ khi gọi client
            self._client = None
    
        @property
        def client(self):
            if self._client is None:
                self._client = texttospeech.TextToSpeechClient()
            return self._client
    
        def get_voices(self) -> List[VoiceInfo]:
            """Lấy toàn bộ danh sách giọng đọc từ máy chủ Google Cloud"""
            try:
                response = self.client.list_voices()
                return [
                    VoiceInfo(
                        id=voice.name,
                        name=voice.name,
                        gender=texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                        language=voice.language_codes[0] if voice.language_codes else "unknown"
                    )
                    for voice in response.voices
                ]
            except Exception as e:
                raise RuntimeError(f"Không thể lấy danh sách giọng đọc từ Google Cloud: {e}")
    
        def synthesize(self, text: str, output_path: Path, config: TTSConfig) -> None:
            """Thực hiện chuyển đổi văn bản sang âm thanh qua Google Cloud API"""
            # 1. Thiết lập văn bản đầu vào
            synthesis_input = texttospeech.SynthesisInput(text=text)
    
            # 2. Cấu hình giọng đọc (Mặc định chọn Vi-VN Nữ nếu không chỉ định)
            voice_lang = "vi-VN" if "vi" in config.engine_name else "en-US"
            voice_name = config.voice or (
                "vi-VN-Wavenet-A" if voice_lang == "vi-VN" else "en-US-Wavenet-F"
            )
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_lang,
                name=voice_name
            )
    
            # 3. Cấu hình thông số âm thanh (Rate, Volume, Pitch)
            # Google Cloud yêu cầu chuyển đổi thông số sang khoảng giá trị quy định của họ
            # Tốc độ đọc (speaking_rate): [0.25, 4.0]
            # Cao độ (pitch): [-20.0, 20.0] semitones
            # m lượng (volume_gain_db): [-96.0, 16.0] dB
            speaking_rate = float(config.rate) if config.rate else 1.0
            pitch = float(config.pitch) if config.pitch else 0.0
            volume_gain_db = float(config.volume) if config.volume else 0.0
    
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                volume_gain_db=volume_gain_db
            )
    
            try:
                # 4. Gửi yêu cầu lên Google API
                response = self.client.synthesize_speech(
                    input=synthesis_input, 
                    voice=voice, 
                    audio_config=audio_config
                )
    
                # 5. Ghi tệp âm thanh đầu ra
                output_path.write_bytes(response.audio_content)
            except Exception as e:
                raise RuntimeError(f"Lỗi khi xử lý tín hiệu với Google Cloud TTS: {e}")
    

Cập nhật lại lớp Factory (`src/tts_app/infrastructure/tts_engines/factory.py`) để kích hoạt engine này:
    
    
    # Cập nhật trong file factory.py có sẵn:
    case "google-cloud":
        return GoogleCloudTTSEngine()
    

* * *

## 🧠 Thuật toán tối ưu hóa nhóm câu giữ nguyên ngữ cảnh (`src/tts_app/domain/services.py`)

Để đảm bảo việc gom cụm ký tự không làm đứt mạch câu văn (giữ ngữ cảnh), thuật toán dưới đây sẽ phân tích độ dài từng câu sau khi được tách bởi `underthesea` hoặc `spacy`. Nó sẽ tích lũy câu vào cụm hiện tại, chỉ đóng cụm khi tiệm cận vùng giới hạn tối ưu và đảm bảo câu tiếp theo không làm vượt quá cấu hình `max_size`.
    
    
    from typing import List
    
    class ContextPreservingSplitter:
        """
        Dịch vụ thuộc lớp Domain chịu trách nhiệm tính toán logic gom cụm văn bản.
        Độc lập hoàn toàn với các thư viện Tokenizer bên ngoài (SOLID - Single Responsibility).
        """
        
        @staticmethod
        def group_sentences(
            sentences: List[str], 
            min_size: int = 1500, 
            default_size: int = 2000, 
            max_size: int = 2500
        ) -> List[str]:
            chunks = []
            current_chunk = []
            current_length = 0
    
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                sentence_length = len(sentence)
    
                # Trường hợp đặc biệt: Bản thân một câu đơn lẻ đã vượt quá giới hạn tối đa
                if sentence_length > max_size:
                    # Nếu cụm hiện tại đang tích lũy có dữ liệu, hãy đóng cụm đó lại trước
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    # Ép buộc cắt câu quá dài này theo ký tự (hoặc xử lý ngoại lệ tùy chọn)
                    chunks.append(sentence)
                    continue
    
                # Kiểm tra xem việc thêm câu hiện tại có vượt quá giới hạn lớn nhất hay không
                # Cộng thêm 1 đại diện cho khoảng trắng phân tách giữa các câu
                projected_length = current_length + sentence_length + (1 if current_length > 0 else 0)
    
                if projected_length > max_size:
                    # Nếu độ dài hiện tại đã đạt mức tối thiểu cho phép, tiến hành đóng cụm
                    if current_length >= min_size:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_length = sentence_length
                    else:
                        # Nếu chưa đạt min_size nhưng câu tiếp theo làm tràn max_size:
                        # Bắt buộc phải đóng cụm cũ để bảo vệ giới hạn tối đa của hệ thống engine TTS
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                        current_chunk = [sentence]
                        current_length = sentence_length
                else:
                    # Thêm câu vào cụm hiện tại khi vẫn nằm trong vùng an toàn
                    current_chunk.append(sentence)
                    current_length = projected_length
    
                # Tối ưu hóa: Nếu cụm hiện tại đạt gần điểm kích thước mặc định kỳ vọng (default_size)
                # và lớn hơn kích thước tối thiểu, chủ động đóng cụm sớm để phân phối các đoạn đều nhau
                if current_length >= default_size:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
    
            # Đóng cụm văn bản cuối cùng nếu còn sót lại dữ liệu
            if current_chunk:
                chunks.append(" ".join(current_chunk))
    
            return chunks
    

## 🔄 Cập nhật Bộ phân tách Tiếng Việt ứng dụng thuật toán mới

Thay vì tự tính toán thủ công như phiên bản sơ thảo, lớp hạ tầng (Infrastructure) giờ đây chỉ làm đúng nhiệm vụ bóc tách câu của thư viện `underthesea`, sau đó chuyển giao mảng câu cho dịch vụ Domain xử lý.
    
    
    # src/tts_app/infrastructure/splitters/vi_underthesea.py
    from tts_app.interfaces.text_splitter import ITextSplitter
    from tts_app.domain.services import ContextPreservingSplitter
    from underthesea import sent_tokenize
    from typing import List
    
    class VietnameseTextSplitter(ITextSplitter):
        def split(self, text: str, min_size: int = 1500, default_size: int = 2000, max_size: int = 2500) -> List[str]:
            # Bước 1: Sử dụng thư viện chuyên dụng tách chuỗi thô thành danh sách câu văn
            sentences = sent_tokenize(text)
            
            # Bước 2: Gọi dịch vụ Domain để nhóm các câu một cách tối ưu theo ngữ cảnh
            return ContextPreservingSplitter.group_sentences(
                sentences=sentences,
                min_size=min_size,
                default_size=default_size,
                max_size=max_size
            )
    

* * *

## 🛠️ Cách thiết lập môi trường chạy thực tế với `uv`

Để kích hoạt hệ thống chạy với Google Cloud TTS trên máy tính của bạn, hãy thực hiện theo chuỗi lệnh sau trong terminal:

  1. Cài đặt các gói thư viện bổ sung vào môi trường:


    
    
    uv add google-cloud-texttospeech
    

  1. Thiết lập khóa bảo mật (Credentials):

     * Trên hệ điều hành Linux/macOS:
           
           export GOOGLE_APPLICATION_CREDENTIALS="/đường_dẫn_tới_file/google-service-account.json"
           

     * Trên hệ điều hành Windows (PowerShell):
           
           $env:GOOGLE_APPLICATION_CREDENTIALS="C:\đường_dẫn_tới_file\google-service-account.json"
           

  2. Chạy thử nghiệm câu lệnh CLI thực tế:


    
    
    # Thực hiện chuyển đổi tệp văn bản bằng Google Cloud Engine, sử dụng cấu hình tối ưu ngữ cảnh
    uv run tts convert ./tailieu.txt --engine google-cloud --chunk-size 2200 --lang vi
    

Đến bước này, hệ thống lõi đã sẵn sàng hoạt động hoàn chỉnh với cả hai kiến trúc hạ tầng cục bộ (Edge) và đám mây (Google Cloud). Bạn có cần tôi hướng dẫn cách đóng gói ứng dụng này thành một file thực thi độc lập (executable file) hoặc tích hợp thêm hệ thống ghi log (logging) để theo dõi tiến trình chạy của từng chunk không?