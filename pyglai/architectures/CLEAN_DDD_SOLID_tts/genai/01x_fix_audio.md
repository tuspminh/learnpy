> * 3.15 khong the cai spacy, spacy chi ho tro 3.12 3.13
>   pin python 3.13
>
> * audio, khong cai duoc goi pyaudioop, nen chuyen sang dung cais khac
>
>
>

Chính xác! Trên **Python 3.13**, gói `pyaudioop` trên PyPI chưa dựng sẵn binary (wheels) hoặc gặp lỗi build C extension trên Windows.

Để giải quyết vấn đề này triệt để mà **không cần đụng tới `audioop` hay C extension**, giải pháp chuẩn xác nhất cho Python 3.13+ là **gỡ bỏ `pydub**` và thay bằng giải pháp ghép file MP3/Audio thuần Python hoặc dùng thư viện hiện đại.

---

### Phương án 1: Ghép file MP3 trực tiếp (Không cần thêm thư viện ngoài - Khuyên dùng)

Do tất cả các Engine TTS (`edge-tts`, `gtts`, `gcloud`) đều xuất ra định dạng `.mp3`, việc ghép các đoạn audio MP3 thực chất chỉ là nối chuỗi binary (bytes) của các file lại với nhau theo thứ tự.

Bạn **không cần** dùng `pydub`, `pyaudioop` hay `ffmpeg` cho việc này!

#### Cập nhật `infrastructure/audio_merger.py`:

```python
from pathlib import Path
from typing import List
from tts_app.domain.interfaces import IAudioMerger


class DirectBinaryAudioMerger(IAudioMerger):

    def merge(
        self, audio_files: List[Path], output_merged_path: Path
    ) -> Path:
        if not audio_files:
            raise ValueError("Danh sách file audio trống, không thể gộp.")

        # Sắp xếp các file audio theo thứ tự chunk (chunk_0000.mp3, chunk_0001.mp3, ...)
        sorted_files = sorted(audio_files, key=lambda p: p.name)

        output_merged_path.parent.mkdir(parents=True, exist_ok=True)

        # Mở file đích và ghi nối tiếp binary của từng chunk
        with open(output_merged_path, "wb") as outfile:
            for file_path in sorted_files:
                outfile.write(file_path.read_bytes())

        return output_merged_path

```

---

### Phương án 2: Dùng `pedalboard` (Thư viện xử lý Audio hiện đại hỗ trợ Python 3.13+)

Nếu về sau bạn cần ghép file dạng WAV hoặc xử lý tín hiệu âm thanh phức tạp:

1. **Cài đặt `pedalboard`:**
```bash
uv add pedalboard

```


2. **Cập nhật `infrastructure/audio_merger.py`:**
```python
from pathlib import Path
from typing import List
from pedalboard.io import AudioFile
import numpy as np
from tts_app.domain.interfaces import IAudioMerger


class PedalboardAudioMerger(IAudioMerger):

    def merge(
        self, audio_files: List[Path], output_merged_path: Path
    ) -> Path:
        if not audio_files:
            raise ValueError("Danh sách file audio trống, không thể gộp.")

        sorted_files = sorted(audio_files, key=lambda p: p.name)

        audio_data_list = []
        sample_rate = None

        for file_path in sorted_files:
            with AudioFile(str(file_path)) as f:
                if sample_rate is None:
                    sample_rate = f.sample_rate
                audio = f.read(f.frames)
                audio_data_list.append(audio)

        combined_audio = np.concatenate(audio_data_list, axis=1)

        output_merged_path.parent.mkdir(parents=True, exist_ok=True)
        with AudioFile(
            str(output_merged_path),
            "w",
            samplerate=sample_rate,
            num_channels=combined_audio.shape[0],
        ) as f:
            f.write(combined_audio)

        return output_merged_path

```



---

### Các bước áp dụng ngay

1. **Gỡ bỏ `pydub` khỏi dự án:**
```bash
uv remove pydub

```


2. **Cập nhật DI trong `presentation/cli.py`:**
Dùng `DirectBinaryAudioMerger` (từ Phương án 1):
```python
from tts_app.infrastructure.audio_merger import DirectBinaryAudioMerger

# ...
audio_merger = DirectBinaryAudioMerger()

```


3. **Chạy lại lệnh CLI:**
```bash
uv run tts engine --list-engines

```


Lệnh sẽ thực thi ngay lập tức mà không còn bất kỳ cảnh báo hay lỗi `audioop` nào!