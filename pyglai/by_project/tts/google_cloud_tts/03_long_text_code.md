# Hướng dẫn Xử lý Văn bản Dài với Google Cloud Text-to-Speech

Khi văn bản vượt quá giới hạn 5.000 ký tự, bạn phải sử dụng API `synthesize_long_audio`. Dưới đây là quy trình 3 bước chuẩn hóa bằng Python.

## 1. Điều kiện tiên quyết

- Bạn phải tạo một **Google Cloud Storage Bucket** (ví dụ: `my-bucket-audio`).
- API sẽ ghi trực tiếp file âm thanh `.wav` hoặc `.mp3` vào bucket này.

## 2. Mã nguồn Python Hoàn chỉnh

```python
import os
import time
from google.cloud import texttospeech_v1beta1 as texttospeech

# 1. Cấu hình biến môi trường xác thực
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-key.json"

def synthesize_long_text(project_id, location, bucket_name, output_filename, long_text):
    """Tạo file âm thanh từ văn bản dài và lưu lên Google Cloud Storage."""

    # Khởi tạo client phiên bản v1beta1 (hỗ trợ Long Audio)
    client = texttospeech.TextToSpeechLongAudioSynthesizeClient()

    # Cấu hình đầu vào văn bản
    input_text = texttospeech.SynthesisInput(text=long_text)

    # Cấu hình giọng đọc (Ví dụ: Giọng tiếng Việt Neural2)
    voice = texttospeech.VoiceSelectionParams(
        language_code="vi-VN",
        name="vi-VN-Neural2-A"
    )

    # Cấu hình file đầu ra (Long Audio khuyến khích dùng LINEAR16 - file .wav)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Cấu hình đường dẫn lưu file trên GCS (Bắt đầu bằng gs://)
    gcs_output_uri = f"gs://{bucket_name}/{output_filename}"

    # Cấu hình yêu cầu gửi đi
    parent = f"projects/{project_id}/locations/{location}"
    request = texttospeech.SynthesizeLongAudioRequest(
        parent=parent,
        input=input_text,
        voice=voice,
        audio_config=audio_config,
        output_gcs_uri=gcs_output_uri
    )

    print("Đang gửi yêu cầu xử lý văn bản dài (Bất đồng bộ)...")
    operation = client.synthesize_long_audio(request=request)

    # Chờ cho đến khi API xử lý xong văn bản
    print("Văn bản đang được chuyển đổi. Vui lòng đợi...")
    response = operation.result(timeout=600)  # Timeout 10 phút

    print(f"Thành công! File âm thanh đã được lưu tại: {gcs_output_uri}")

# --- CÁCH SỬ DỤNG ---
if __name__ == "__main__":
    PROJECT_ID = "ten-du-an-google-cloud-cua-ban"
    LOCATION = "us-central1"  # Long Audio yêu cầu chỉ định vị trí cụ thể (ví dụ: us-central1)
    BUCKET_NAME = "my-bucket-audio"
    OUTPUT_FILE = "sach_noi_output.wav"

    # Đoạn văn bản mẫu dài hơn 5000 ký tự
    VAN_BAN_DAI = "Trích đoạn sách hoặc bài báo dài của bạn ở đây... " * 500 

    synthesize_long_text(PROJECT_ID, LOCATION, BUCKET_NAME, OUTPUT_FILE, VAN_BAN_DAI)
```

## 3. Các lưu ý quan trọng khi làm việc với Văn bản dài

1. **Vị trí (Location):** Không phải vùng nào cũng hỗ trợ Long Audio. Hãy kiểm tra tài liệu Google Cloud để chọn đúng vùng hỗ trợ (thường dùng `us-central1`).
2. **Chi phí:** Giọng đọc Neural2 và WaveNet có mức giá tính theo mỗi 1 triệu ký tự. Hãy quản lý chặt chẽ số lượng ký tự gửi lên để tránh phát sinh chi phí ngoài ý muốn.
3. **Tải file về máy:** Sau khi script chạy xong, bạn có thể tải file từ Google Cloud Storage về máy thông qua giao diện Console hoặc dùng thư viện `google-cloud-storage` bằng Python.