Nếu bạn **không muốn làm việc với `time_base` và phân số (Fraction)** của PyAV/FFmpeg, bạn hoàn toàn có thể tự quản lý thời gian bằng cách đếm trực tiếp **số lượng mẫu (sample count)**.

Trong âm thanh số (PCM), mốc thời gian `pts` của frame tiếp theo luôn bằng `pts` của frame hiện tại cộng với **số lượng sample** của frame đó:

$$\text{PTS}_{\text{next}} = \text{PTS}_{\text{current}} + \text{frame.samples}$$

Dưới đây là phiên bản tối giản cả 2 kỹ thuật (Resample nối file & Crossfade) bằng cách dùng **biến đếm sample** hoàn toàn:

---

### 1. Nối file + Resample (Đếm sample trực tiếp)

Không cần chạm vào `in_stream.time_base` hay `out_stream.time_base`, bạn chỉ cần duy trì một biến tích lũy `pts_counter`:

```python
import av


def merge_audio_simple(input_files, output_file, target_rate=44100):
    out_container = av.open(output_file, mode="w")

    # Tạo stream đầu ra
    codec_name = "mp3" if output_file.endswith(".mp3") else "aac"
    out_stream = out_container.add_stream(codec_name, rate=target_rate)
    out_stream.layout = "stereo"
    out_stream.format = "fltp"

    resampler = av.AudioResampler(
        format=out_stream.format, layout=out_stream.layout, rate=out_stream.rate
    )

    pts_counter = 0  # Biến đếm sample tích lũy đơn giản

    for file_path in input_files:
        in_container = av.open(file_path)
        in_stream = in_container.streams.audio[0]

        for frame in in_container.decode(in_stream):
            for resampled_frame in resampler.resample(frame):
                # Gán PTS bằng đúng tổng số sample đã ghi trước đó
                resampled_frame.pts = pts_counter
                pts_counter += resampled_frame.samples

                for packet in out_stream.encode(resampled_frame):
                    out_container.mux(packet)

        in_container.close()

    # Flush resampler
    for resampled_frame in resampler.resample(None):
        resampled_frame.pts = pts_counter
        pts_counter += resampled_frame.samples
        for packet in out_stream.encode(resampled_frame):
            out_container.mux(packet)

    # Flush encoder
    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    print("Nối file thành công!")

```

---

### 2. Crossfade ngắn gọn (Dùng NumPy index, bỏ qua time_base)

Khi xử lý Crossfade qua NumPy, bạn chỉ cần cắt ghép các mảng dữ liệu dựa trên số lượng mẫu `fade_samples = duration * rate`. Sau đó chia chunk và gán `pts` tăng dần bằng chỉ số mảng:

```python
import numpy as np
import av


def merge_crossfade_no_fractions(
    input_files, output_file, fade_sec=2.0, target_rate=44100
):
    fade_samples = int(fade_sec * target_rate)
    resampler = av.AudioResampler(
        format="fltp", layout="stereo", rate=target_rate
    )

    # Đọc toàn bộ file về mảng PCM
    all_tracks = []
    for f in input_files:
        container = av.open(f)
        frames_data = []
        for frame in container.decode(container.streams.audio[0]):
            for r_frame in resampler.resample(frame):
                frames_data.append(r_frame.to_ndarray())
        for r_frame in resampler.resample(None):
            frames_data.append(r_frame.to_ndarray())
        container.close()

        all_tracks.append(np.concatenate(frames_data, axis=1))

    # Xử lý Crossfade bằng mảng NumPy
    combined = all_tracks[0]
    for next_track in all_tracks[1:]:
        overlap = min(fade_samples, combined.shape[1], next_track.shape[1])
        if overlap > 0:
            fade_out = np.linspace(1.0, 0.0, overlap, dtype=np.float32)
            fade_in = np.linspace(0.0, 1.0, overlap, dtype=np.float32)

            cross = (combined[:, -overlap:] * fade_out) + (
                next_track[:, :overlap] * fade_in
            )
            combined = np.concatenate(
                [combined[:, :-overlap], cross, next_track[:, overlap:]], axis=1
            )
        else:
            combined = np.concatenate([combined, next_track], axis=1)

    # Ghi ra file đầu ra bằng đếm sample index
    out_container = av.open(output_file, mode="w")
    codec_name = "mp3" if output_file.endswith(".mp3") else "aac"
    out_stream = out_container.add_stream(codec_name, rate=target_rate)
    out_stream.layout = "stereo"
    out_stream.format = "fltp"

    FRAME_SIZE = 1024
    total_samples = combined.shape[1]

    # Vòng lặp slice mảng theo FRAME_SIZE, index chính là pts
    for pts in range(0, total_samples, FRAME_SIZE):
        chunk = combined[:, pts : pts + FRAME_SIZE]

        if chunk.shape[1] < FRAME_SIZE:
            chunk = np.pad(
                chunk, ((0, 0), (0, FRAME_SIZE - chunk.shape[1])), mode="constant"
            )

        frame = av.AudioFrame.from_ndarray(chunk, format="fltp", layout="stereo")
        frame.rate = target_rate
        frame.pts = pts  # Gán thẳng chỉ số vị trí sample làm PTS

        for packet in out_stream.encode(frame):
            out_container.mux(packet)

    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    print("Ghi file Crossfade thành công!")

```

---

### Tại sao cách này hoạt động không cần `time_base`?

Khi bạn không thiết lập `pts` theo hệ quy chiếu thời gian của container (thường dạng `1/90000` hay `1/44100`), PyAV mặc định hiểu stream âm thanh có `time_base = 1/sample_rate`.

Do đó, **1 đơn vị PTS tương ứng với đúng 1 sample**, giúp bạn chỉ cần lấy chỉ số sample (như `0, 1024, 2048...`) làm PTS mà âm thanh vẫn khớp hoàn toàn, không bị giật hay lệch tiếng.