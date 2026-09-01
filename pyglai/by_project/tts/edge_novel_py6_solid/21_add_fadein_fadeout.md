Để làm hiệu ứng **Crossfade** (âm thanh file 1 nhỏ dần - *fade out*, đồng thời âm thanh file 2 to dần - *fade in* đè lên nhau) với PyAV, bạn cần làm việc trực tiếp với mảng số liệu âm thanh (Audio Buffer).

Trong Python, cách tốt nhất là chuyển `AudioFrame` thành **NumPy Array**, áp dụng các trọng số âm lượng (gain matrix), sau đó nối lại thành `AudioFrame` chuẩn trước khi encode.

---

### Mã nguồn hoàn chỉnh: Merge Audio với Crossfade bằng PyAV + NumPy

Trước khi chạy, hãy đảm bảo bạn đã cài đặt `numpy`: `pip install numpy av`

```python
import numpy as np
import av


def frame_to_ndarray(frame):
    """Chuyển đổi PyAV AudioFrame sang mảng NumPy dạng float32 (-1.0 đến 1.0)."""
    # Lấy dữ liệu dưới dạng numpy array
    arr = frame.to_ndarray()

    # Xử lý tùy theo format nguyên bản của frame
    if frame.format.name in ("flt", "fltp"):
        return arr.astype(np.float32)
    elif frame.format.name in ("s16", "s16p"):
        return arr.astype(np.float32) / 32768.0
    elif frame.format.name in ("s32", "s32p"):
        return arr.astype(np.float32) / 2147483648.0
    return arr.astype(np.float32)


def decode_and_resample_all(file_path, target_rate=44100):
    """Đọc file đầu vào, resample và load toàn bộ PCM data thành 1 mảng numpy dạng Stereo (2, N)."""
    container = av.open(file_path)
    in_stream = container.streams.audio[0]

    resampler = av.AudioResampler(format="fltp", layout="stereo", rate=target_rate)

    pcm_chunks = []
    for frame in container.decode(in_stream):
        for r_frame in resampler.resample(frame):
            pcm_chunks.append(frame_to_ndarray(r_frame))

    for r_frame in resampler.resample(None):
        pcm_chunks.append(frame_to_ndarray(r_frame))

    container.close()

    if not pcm_chunks:
        return np.zeros((2, 0), dtype=np.float32)

    # Nối tất cả các frame trong cùng 1 file thành mảng 2D (channels, samples)
    return np.concatenate(pcm_chunks, axis=1)


def merge_with_crossfade(
    input_files, output_file, fade_duration_sec=2.0, target_rate=44100
):
    fade_samples = int(fade_duration_sec * target_rate)

    # 1. Đọc và chuẩn hóa toàn bộ các file audio về mảng NumPy PCM
    print("Đang đọc và chuyển đổi định dạng các file...")
    audio_tracks = [
        decode_and_resample_all(f, target_rate) for f in input_files
    ]

    if not audio_tracks:
        return

    # 2. Thực hiện ghép nhạc và trộn Crossfade trên mảng NumPy
    print("Đang hòa trộn hiệu ứng Crossfade...")
    combined_audio = audio_tracks[0]

    for next_track in audio_tracks[1:]:
        # Tính toán độ dài thực tế của đoạn overlap (tránh trường hợp file ngắn hơn fade_duration)
        overlap = min(fade_samples, combined_audio.shape[1], next_track.shape[1])

        if overlap > 0:
            # Tạo đường cong âm lượng linear: 1 -> 0 (fade out) và 0 -> 1 (fade in)
            fade_out = np.linspace(1.0, 0.0, overlap, dtype=np.float32)
            fade_in = np.linspace(0.0, 1.0, overlap, dtype=np.float32)

            # Áp dụng gain vào đoạn nối
            fade_out_part = combined_audio[:, -overlap:] * fade_out
            fade_in_part = next_track[:, :overlap] * fade_in

            # Cộng 2 tín hiệu âm thanh lại với nhau ở đoạn chuyển tiếp
            crossfaded_part = fade_out_part + fade_in_part

            # Ghép lại: [Phần trước] + [Phần Crossfade] + [Phần sau của track mới]
            main_part = combined_audio[:, :-overlap]
            tail_part = next_track[:, overlap:]

            combined_audio = np.concatenate(
                [main_part, crossfaded_part, tail_part], axis=1
            )
        else:
            combined_audio = np.concatenate([combined_audio, next_track], axis=1)

    # 3. Chuyển mảng NumPy hòa trộn hoàn chỉnh thành các PyAV AudioFrame và Encode ra file
    print("Đang encode và xuất file đầu ra...")
    out_container = av.open(output_file, mode="w")

    codec_name = "mp3" if output_file.endswith(".mp3") else "aac"
    out_stream = out_container.add_stream(codec_name, rate=target_rate)
    out_stream.layout = "stereo"
    out_stream.format = "fltp"

    frame_size = 1024  # Kích thước tiêu chuẩn của 1 AAC/MP3 frame
    total_samples = combined_audio.shape[1]
    pts_offset = 0

    for idx in range(0, total_samples, frame_size):
        chunk = combined_audio[:, idx : idx + frame_size]

        # Padding nếu chunk cuối cùng ngắn hơn frame_size
        if chunk.shape[1] < frame_size:
            pad_width = frame_size - chunk.shape[1]
            chunk = np.pad(chunk, ((0, 0), (0, pad_width)), mode="constant")

        # Khởi tạo PyAV AudioFrame từ NumPy array
        frame = av.AudioFrame.from_ndarray(chunk, format="fltp", layout="stereo")
        frame.rate = target_rate
        frame.pts = pts_offset
        pts_offset += chunk.shape[1]

        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    # Flush encoder
    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    print(f"Đã xuất file thành công: {output_file}")


# --- Ví dụ sử dụng ---
files = ["song1.mp3", "song2.wav", "song3.m4a"]
# Trộn 3 file trên với đoạn crossfade dài 3 giây
merge_with_crossfade(files, "output_crossfade.mp3", fade_duration_sec=3.0)

```

---

### Nguyên lý hoạt động của đoạn Code:

1. **Load toàn bộ về Memory Buffer**:
Khi làm hiệu ứng Crossfade, bạn bắt buộc phải có thông tin của đoạn đầu file sau và đoạn cuối file trước tại cùng một thời điểm. Việc chuyển dữ liệu về mảng NumPy `(2, N)` giúp thao tác xử lý toán học trên sóng âm (waveform) diễn ra rất nhanh.
2. **Công thức toán học của Crossfade**:
Tại đoạn đè lên nhau (dài `overlap` mẫu):

$$\text{Signal}_{\text{out}} = (\text{Track}_1 \times \text{FadeOut}) + (\text{Track}_2 \times \text{FadeIn})$$


* `fade_out` chạy giảm dần từ `1.0` về `0.0`.
* `fade_in` chạy tăng dần từ `0.0` lên `1.0`.


3. **Tái đóng gói AudioFrame (`from_ndarray`)**:
Sau khi đã có mảng âm thanh hòa trộn hoàn chỉnh, code chia mảng này thành các block `1024 samples` (chuẩn AAC/MP3) và gán lại `pts` liên tục trước khi đẩy vào Stream Encoder.