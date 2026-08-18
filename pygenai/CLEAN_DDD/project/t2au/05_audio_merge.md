Dưới đây là mã nguồn chi tiết cho lớp `AudioMerger` nằm ở tầng **Infrastructure** (`infrastructure/audio/merger.py`), sử dụng thư viện `pydub` kết hợp với `ffmpeg` để tự động nối các tệp audio ngắn thành một tệp MP3 duy nhất.

---

### Mã nguồn `AudioMerger`

```python
# infrastructure/audio/merger.py
import os
from pathlib import Path
from typing import List, Union
from pydub import AudioSegment


class AudioMerger:
    def __init__(self, crossfade_ms: int = 50, silence_padding_ms: int = 100):
        """
        Khởi tạo AudioMerger với cấu hình mặc định.

        :param crossfade_ms: Thời gian chuyển cảnh mềm giữa các đoạn audio (ms)
        :param silence_padding_ms: Khoảng lặng chèn giữa các chunk (ms)
        """
        self.crossfade_ms = crossfade_ms
        self.silence_padding = AudioSegment.silent(duration=silence_padding_ms)

    def merge(
        self,
        audio_paths: List[Union[str, Path]],
        output_path: Union[str, Path],
        format: str = "mp3",
        bitrate: str = "192k"
    ) -> bool:
        """
        Nối danh sách các file audio ngắn thành một file duy nhất.

        :param audio_paths: Danh sách đường dẫn tệp audio cần ghép (đã sắp xếp đúng thứ tự)
        :param output_path: Đường dẫn lưu tệp audio kết quả
        :param format: Định dạng xuất (mp3, wav, ogg, v.v.)
        :param bitrate: Chất lượng audio đầu ra (chỉ áp dụng cho mp3/aac)
        :return: True nếu thành công
        """
        valid_paths = [Path(p) for p in audio_paths if Path(p).exists()]

        if not valid_paths:
            raise FileNotFoundError("Không tìm thấy tệp audio hợp lệ nào để tiến hành hợp nhất.")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        combined_audio: AudioSegment = AudioSegment.empty()

        for idx, path in enumerate(valid_paths):
            try:
                # pydub tự động nhận diện định dạng nguồn (mp3, wav, ogg...)
                segment = AudioSegment.from_file(str(path))

                if len(combined_audio) == 0:
                    combined_audio = segment
                else:
                    # Chèn một khoảng lặng ngắn giữa các đoạn đọc để tự nhiên hơn
                    combined_audio += self.silence_padding

                    # Áp dụng crossfade nếu âm thanh đủ dài
                    if (
                        self.crossfade_ms > 0
                        and len(combined_audio) > self.crossfade_ms
                        and len(segment) > self.crossfade_ms
                    ):
                        combined_audio = combined_audio.append(segment, crossfade=self.crossfade_ms)
                    else:
                        combined_audio += segment

            except Exception as e:
                raise RuntimeError(f"Lỗi khi đọc tệp chunk {path.name}: {e}")

        # Export ra tệp đích
        try:
            combined_audio.export(
                str(output_file),
                format=format,
                bitrate=bitrate if format in ["mp3", "aac"] else None
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Không thể xuất tệp audio hợp nhất tại {output_file}: {e}")

    def cleanup_temp_files(self, audio_paths: List[Union[str, Path]]) -> None:
        """
        Dọn dẹp các tệp chunk tạm thời sau khi đã ghép nối thành công.
        """
        for path in audio_paths:
            p = Path(path)
            if p.exists():
                try:
                    os.remove(p)
                except OSError as e:
                    print(f"Cảnh báo: Không thể xóa tệp tạm {p.name}: {e}")

```

---

### Yêu cầu cài đặt phụ thuộc

Để `pydub` hoạt động tốt trên hệ thống, bạn cần cài đặt thư viện Python và công cụ `ffmpeg`:

1. **Cài đặt thư viện Python:**
```bash
pip install pydub

```


2. **Cài đặt FFmpeg:**
* **Windows:** Tải bản dựng FFmpeg, giải nén và thêm đường dẫn thư mục `bin` vào biến môi trường PATH.
* **macOS:** `brew install ffmpeg`
* **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install ffmpeg`