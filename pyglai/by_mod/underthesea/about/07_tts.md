Dưới đây là hướng dẫn chi tiết cách cài đặt, viết code chạy và xử lý file âm thanh đầu ra khi sử dụng chức năng `tts` (Text-to-Speech) của [Underthesea](https://github.com/undertheseanlp/underthesea).

* * *

## 1\. Cài đặt các thư viện bổ trợ

Tính năng chuyển văn bản thành giọng nói (TTS) yêu cầu hệ thống học sâu và xử lý âm thanh phức tạp. Để chạy được hàm này, bạn cần cài đặt phiên bản hỗ trợ `deep` và thư viện lưu file âm thanh bằng lệnh sau trong Terminal/CMD:
    
    
    pip install underthesea[deep] soundfile
    

* * *

## 2\. Viết Code chạy TTS cơ bản

Hàm `tts()` của Underthesea nhận đầu vào là một chuỗi văn bản tiếng Việt và trả về một mảng dữ liệu âm thanh (Numpy array) cùng với tần số lấy mẫu (sample rate). Bạn cần sử dụng thư viện `soundfile` để xuất mảng dữ liệu này thành một file nghe `.wav` thực tế. [1] 
    
    
    import soundfile as sf
    from underthesea import tts
    
    # 1. Định nghĩa văn bản tiếng Việt cần đọc
    text = "Xin chào, chúc bạn một ngày tốt lành và làm việc hiệu quả."
    
    # 2. Gọi hàm tts để xử lý (Mô hình sẽ tự động tính toán dữ liệu âm thanh)
    # audio: chứa mảng số biểu diễn sóng âm thanh
    # sample_rate: tần số lấy mẫu của giọng đọc (thường là 16000Hz hoặc 22050Hz)
    audio, sample_rate = tts(text)
    
    # 3. Ghi dữ liệu ra file âm thanh .wav để nghe trực tiếp
    output_filename = "output_voice.wav"
    sf.write(output_filename, audio, sample_rate)
    
    print(f"Đã chuyển đổi thành công! File âm thanh được lưu tại: {output_filename}")
    

* * *

## 3\. Quy trình nâng cao: Chuẩn hóa kết hợp TTS

Khi văn bản có chứa các số, ngày tháng, hoặc ký tự lạ, giọng đọc của AI có thể bị vấp hoặc bỏ sót. Để có giọng đọc mượt mà nhất, bạn nên chạy qua module `text_normalize` trước khi đưa vào `tts`: [2] 
    
    
    import soundfile as sf
    from underthesea import text_normalize, tts
    
    raw_text = "Hôm nay là ngày 25 tháng 8, thời tiết ở Hoà Lạc rất đẹp!"
    
    # Chuẩn hóa dấu thanh và mã Unicode trước để AI không bị lỗi giọng
    clean_text = text_normalize(raw_text)
    
    # Tiến hành đọc văn bản sạch
    audio, sample_rate = tts(clean_text)
    sf.write("vietnamese_speech.wav", audio, sample_rate)
    

## Lưu ý quan trọng khi chạy:

  * Tốc độ xử lý (CPU vs GPU): Nếu máy tính của bạn không có card đồ họa rời (GPU Nvidia) hỗ trợ CUDA, mô hình Deep Learning chạy ngầm của chức năng TTS sẽ xử lý hoàn toàn bằng CPU. Quá trình này có thể mất từ vài giây đến một phút tùy thuộc vào độ dài câu văn của bạn. [3] 
  * Thời gian tải mô hình lần đầu: Ở lần chạy code đầu tiên, Underthesea sẽ tự động tải các file trọng số (weights) của mô hình giọng nói từ máy chủ về máy tính của bạn. Các lần chạy sau đó sẽ diễn ra ngay lập tức và không cần tải lại nữa. [4] 



Nếu bạn gặp lỗi trong quá trình cài đặt hoặc muốn tìm hiểu cách tích hợp file `.wav` này vào một AI Agent tự động nói, hãy cho tôi biết nhé!

  


[1] [https://github.com](https://github.com/ntt123/vietTTS)

[2] [https://github.com](https://github.com/topics/offline-tts?o=desc&s=updated)

[3] [https://github.com](https://github.com/undertheseanlp/underthesea/issues)

[4] [https://github.com](https://github.com/undertheseanlp/underthesea)