Dưới đây là hướng dẫn chi tiết cho cả 3 phần: cấu hình khóa xác thực, sử dụng SSML và tùy chỉnh giọng đọc sâu hơn.

## 1\. Cấu hình khóa xác thực API (Authentication)

Để chạy được đoạn mã Python, bạn cần cấp quyền cho ứng dụng thông qua tài khoản dịch vụ (Service Account).

  * Bước 1: Truy cập Google Cloud Console và tạo một dự án (Project).
  * Bước 2: Bật Text-to-Speech API trong mục API & Services.
  * Bước 3: Vào mục IAM & Admin > Service Accounts > Chọn Create Service Account.
  * Bước 4: Tạo khóa mới (Key) định dạng JSON cho tài khoản đó và tải về máy.
  * Bước 5: Thiết lập biến môi trường trong code Python để nhận diện file JSON này:


    
    
    import os
    
    # Thay đường dẫn tới file JSON thực tế của bạn
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"
    

* * *

## 2\. Sử dụng SSML để ngắt nghỉ câu

SSML (Speech Synthesis Markup Language) giúp bạn điều khiển cách AI đọc văn bản như ngắt quãng, nhấn mạnh hoặc đọc từng ký tự.
    
    
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    # Sử dụng thẻ SSML thay vì văn bản thuần túy
    ssml_text = """
    <speak>
      Chào bạn. <break time="1s"/> Hôm nay thời tiết thế nào?
      <p>Đây là một đoạn văn mới.</p>
      Tôi muốn nhấn mạnh từ <emphasis level="strong">này</emphasis>.
      Hãy đọc từng chữ cái: <say-as interpret-as="characters">Python</say-as>.
    </speak>
    """
    
    input_text = texttospeech.SynthesisInput(ssml=ssml_text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Neural2-A"
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
    with open("ssml_output.mp3", "wb") as out:
        out.write(response.audio_content)
    

* * *

## 3\. Cách tạo giọng đọc tùy chỉnh (Tốc độ & Cao độ)

Bạn có thể thay đổi tần số (cao độ) và tốc độ của giọng đọc có sẵn để phù hợp với nhu cầu.
    
    
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    input_text = texttospeech.SynthesisInput(text="Đoạn văn này sẽ được đọc nhanh hơn và cao giọng hơn.")
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Wavenet-A"
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.2,  # Tốc độ đọc: 1.0 là bình thường, 1.2 là nhanh hơn 20%
        pitch=4.0          # Cao độ: giá trị từ -20.0 đến 20.0 (semitones)
    )
    
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
    with open("custom_voice.mp3", "wb") as out:
        out.write(response.audio_content)
    

Nếu bạn muốn tiếp tục triển khai, hãy cho tôi biết:

  * Bạn có gặp lỗi khi chạy thử mã nguồn không?
  * Bạn có muốn tích hợp đoạn mã này vào một ứng dụng web (như Flask/FastAPI) không?
  * Bạn có cần xử lý các file văn bản dài (Long-form audio) không?