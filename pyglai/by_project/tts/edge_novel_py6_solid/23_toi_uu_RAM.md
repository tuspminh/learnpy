Khi xử lý các file audio dung lượng lớn (hoặc nối hàng chục file cùng lúc), việc đọc toàn bộ dữ liệu vào RAM dưới dạng mảng NumPy sẽ nhanh chóng làm tràn bộ nhớ (Out of Memory).

Để tối ưu RAM xuống mức cố định **chỉ tốn vài Megabyte** bất kể file đầu vào lớn bao nhiêu, bạn áp dụng chiến thuật **Stream-based Processing (Xử lý theo luồng con trỏ trượt)**:

* Chỉ load phần đuôi của File A và phần đầu của File B vào RAM để làm hiệu ứng Crossfade.
* Toàn bộ phần thân của các file audio sẽ được **decode, resample và encode trực tiếp theo từng frame (Streaming)** ngay ra đĩa cứng.

---

### Mã nguồn tối ưu RAM: Crossfade & Merge Audio theo luồng (Streaming)

```python
import numpy as np
import av


def stream_decode_and_encode(
    in_container,
    in_stream,
    resampler,
    out_container,
    out_stream,
    pts_offset,
    stop_at_sample=None,
):
    """Decode và encode trực tiếp từ file vào -> file ra mà không lưu toàn bộ vào RAM.

    Dừng lại khi đạt đến stop_at_sample (dùng cho đoạn chuẩn bị crossfade).
    """
    samples_processed = 0

    for frame in in_container.decode(in_stream):
        for r_frame in resampler.resample(frame):
            n_samples = r_frame.samples

            # Nếu giới hạn mẫu (để dành phần đuôi làm crossfade)
            if (
                stop_at_sample is not None
                and samples_processed + n_samples > stop_at_sample
            ):
                # Trả lại phần frame dư cho bước xử lý tiếp theo nếu cần
                needed = stop_at_sample - samples_processed
                if needed > 0:
                    arr = r_frame.to_ndarray()
                    chunk = arr[:, :needed]
                    out_f = av.AudioFrame.from_ndarray(
                        chunk, format="fltp", layout="stereo"
                    )
                    out_f.rate = out_stream.rate
                    out_f.pts = pts_offset
                    pts_offset += needed
                    samples_processed += needed

                    for packet in out_stream.encode(out_f):
                        out_container.mux(packet)
                return pts_offset, samples_processed

            # Encode bình thường
            r_frame.pts = pts_offset
            pts_offset += n_samples
            samples_processed += n_samples

            for packet in out_stream.encode(r_frame):
                out_container.mux(packet)

    return pts_offset, samples_processed


def extract_samples(
    in_container, in_stream, resampler, max_samples, start_from_sample=0
):
    """Lấy đúng số lượng sample cần thiết từ một vị trí cụ thể vào RAM (dùng cho vùng fade)."""
    collected = []
    current_sample = 0
    total_collected = 0

    for frame in in_container.decode(in_stream):
        for r_frame in resampler.resample(frame):
            arr = r_frame.to_ndarray()
            n = r_frame.samples

            # Bỏ qua các sample chưa tới lượt
            if current_sample + n <= start_from_sample:
                current_sample += n
                continue

            # Cắt lấy đoạn nằm trong khoảng yêu cầu
            offset_in = max(0, start_from_sample - current_sample)
            needed = max_samples - total_collected
            take = min(n - offset_in, needed)

            collected.append(arr[:, offset_in : offset_in + take])
            total_collected += take
            current_sample += n

            if total_collected >= max_samples:
                break
        if total_collected >= max_samples:
            break

    if not collected:
        return np.zeros((2, 0), dtype=np.float32)
    return np.concatenate(collected, axis=1)


def merge_large_files_with_crossfade(
    input_files, output_file, fade_sec=3.0, target_rate=44100
):
    fade_samples = int(fade_sec * target_rate)

    out_container = av.open(output_file, mode="w")
    codec_name = "mp3" if output_file.endswith(".mp3") else "aac"
    out_stream = out_container.add_stream(codec_name, rate=target_rate)
    out_stream.layout = "stereo"
    out_stream.format = "fltp"

    resampler = av.AudioResampler(
        format="fltp", layout="stereo", rate=target_rate
    )
    pts_offset = 0

    for i in range(len(input_files)):
        file_path = input_files[i]
        is_last = i == len(input_files) - 1

        print(f"Đang xử lý file [{i+1}/{len(input_files)}]: {file_path}")

        # 1. Tính tổng số sample của file hiện tại
        container = av.open(file_path)
        stream = container.streams.audio[0]

        # Đếm tổng sample bằng resampler
        total_samples = 0
        for frame in container.decode(stream):
            for r_frame in resampler.resample(frame):
                total_samples += r_frame.samples
        for r_frame in resampler.resample(None):
            total_samples += r_frame.samples
        container.close()

        # 2. Xử lý phần THÂN (Body) của file (Streaming trực tiếp ra ổ đĩa)
        container = av.open(file_path)
        stream = container.streams.audio[0]

        # Nếu không phải file cuối, giữ lại đúng `fade_samples` ở đuôi để làm crossfade
        body_samples = (
            total_samples - fade_samples if not is_last else total_samples
        )
        body_samples = max(0, body_samples)

        pts_offset, _ = stream_decode_and_encode(
            container,
            stream,
            resampler,
            out_container,
            out_stream,
            pts_offset,
            stop_at_sample=body_samples,
        )
        container.close()

        # 3. Xử lý phần CROSSFADE (Chỉ load đúng đoạn fade ngắn vào RAM)
        if not is_last and (total_samples > body_samples):
            next_file = input_files[i + 1]

            # Đuôi file hiện tại
            container_a = av.open(file_path)
            tail_a = extract_samples(
                container_a,
                container_a.streams.audio[0],
                resampler,
                max_samples=fade_samples,
                start_from_sample=body_samples,
            )
            container_a.close()

            # Đầu file kế tiếp
            container_b = av.open(next_file)
            head_b = extract_samples(
                container_b,
                container_b.streams.audio[0],
                resampler,
                max_samples=fade_samples,
                start_from_sample=0,
            )
            container_b.close()

            # Áp dụng Crossfade trên mảng cực nhỏ này
            actual_fade = min(tail_a.shape[1], head_b.shape[1])
            if actual_fade > 0:
                fade_out = np.linspace(1.0, 0.0, actual_fade, dtype=np.float32)
                fade_in = np.linspace(0.0, 1.0, actual_fade, dtype=np.float32)

                cross = (tail_a[:, :actual_fade] * fade_out) + (
                    head_b[:, :actual_fade] * fade_in
                )

                # Stream đoạn Crossfade vừa hòa trộn ra file
                FRAME_SIZE = 1024
                for idx in range(0, actual_fade, FRAME_SIZE):
                    chunk = cross[:, idx : idx + FRAME_SIZE]
                    if chunk.shape[1] < FRAME_SIZE:
                        chunk = np.pad(
                            chunk,
                            ((0, 0), (0, FRAME_SIZE - chunk.shape[1])),
                            mode="constant",
                        )

                    f = av.AudioFrame.from_ndarray(
                        chunk, format="fltp", layout="stereo"
                    )
                    f.rate = target_rate
                    f.pts = pts_offset
                    pts_offset += chunk.shape[1]

                    for packet in out_stream.encode(f):
                        out_container.mux(packet)

    # Flush encoder
    for packet in out_stream.encode(None):
        out_container.mux(packet)

    out_container.close()
    print("Hoàn tất nối các file dung lượng lớn!")


# --- Sử dụng ---
big_files = ["huge_audio1.wav", "huge_audio2.flac", "huge_audio3.mp3"]
merge_large_files_with_crossfade(big_files, "huge_output.mp3", fade_sec=3.0)

```

---

### Các kỹ thuật tối ưu RAM chính đã áp dụng:

1. **Chunk-by-Chunk Encoding**: Thay vì tích lũy mảng `ndarray` của cả bài hát vào danh sách Python (`list`), đoạn code đọc từng `AudioFrame` và truyền trực tiếp tới `out_stream.encode()` để ghi thẳng dữ liệu nén xuống ổ đĩa.
2. **Loại bỏ bộ nhớ đệm dư thừa**: Chỉ có duy nhất khoảng **3 giây âm thanh** (`fade_samples`) của phần giao nhau giữa 2 bài được nạp vào RAM dưới dạng NumPy array để nhân ma trận gain.
3. **Giải phóng Container chủ động**: Dùng `container.close()` ngay khi trích xuất hoặc ghi xong một phân đoạn để giải phóng bộ nhớ C-level của FFmpeg underlying wrapper trong PyAV.