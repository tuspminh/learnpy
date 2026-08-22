Google Cloud Text-to-Speech là dịch vụ đám mây thông minh. Nó giúp bạn đổi văn bản thành giọng nói giống người thật bằng công nghệ AI của Google. Dịch vụ hỗ trợ hơn 220 giọng đọc và hơn 40 ngôn ngữ khác nhau.

## Tính năng chính

  * Giọng đọc WaveNet và Neural2: Sử dụng mô hình học sâu để tạo âm thanh tự nhiên, mượt mà như người thật.
  * Tùy chỉnh giọng nói: Dễ dàng chỉnh tốc độ đọc, cao độ và âm lượng.
  * Hỗ trợ SSML: Dùng thẻ XML để ngắt nghỉ, nhấn mạnh từ ngữ hoặc thêm âm thanh.
  * Đa định dạng: Xuất file âm thanh dạng MP3, LINEAR16 hoặc OGG OPUS.



## Cách dùng Python cơ bản

Bạn cần cài thư viện và chuẩn bị file xác thực tài khoản.
    
    
    pip install google-cloud-texttospeech
    

Mã nguồn Python mẫu:
    
    
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    input_text = texttospeech.SynthesisInput(text="Xin chào, đây là Google Cloud Text to Speech.")
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN", name="vi-VN-Neural2-A", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
        print("Đã lưu file âm thanh output.mp3")
    

Nếu bạn muốn, tôi có thể hướng dẫn thêm về:

  * Cách dùng SSML để ngắt nghỉ câu
  * Cách tạo giọng đọc tùy chỉnh
  * Cách cấu hình khóa xác thực API