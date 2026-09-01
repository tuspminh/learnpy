Để nối (merge) các file audio có thể khác nhau về sample rate, channel layout hay format thành 1 file duy nhất bằng PyAV, bạn **bắt buộc phải qua bước decode, resample (chuyển đổi định dạng mẫu) và encode lại**.

Dưới đây là mã nguồn chuẩn chỉnh từng bước để thực hiện công việc này:

### Mã nguồn PyAV Merge & Resample Audio

```python
import av


def merge_audio_files(input_files, output_file, target_sample_rate=44100):
    # 1. Tạo container đầu ra và cấu hình Audio Stream
    output_container = av.open(output_file, mode="w")

    # Chọn codec đầu ra (vd: AAC cho mp3/m4a/mp4, hoặc pcm_s16le cho wav)
    if output_file.endswith(".mp3"):
        codec_name = "mp3"
    elif output_file.endswith(".wav"):
        codec_name = "pcm_s16le"
    else:
        codec_name = "aac"

    out_stream = output_container.add_stream(codec_name, rate=target_sample_rate)
    out_stream.layout = "stereo"  # Chuẩn hóa về 2 kênh (stereo)
    out_stream.format = "fltp"  # Format mẫu chuẩn cho encoder (float planar)

    # 2. Khởi tạo bộ chuyển đổi Resampler (AudioResampler)
    resampler = av.AudioResampler(
        format=out_stream.format,
        layout=out_stream.layout,
        rate=out_stream.rate,
    )

    pts_offset = 0  # Biến theo dõi mốc thời gian (Presentation Time Stamp)

    # 3. Duyệt qua từng file đầu vào
    for file_path in input_files:
        print(f"Đang xử lý: {file_path}")
        in_container = av.open(file_path)

        # Lấy audio stream đầu tiên của file
        in_stream = in_container.streams.audio[0]

        for frame in in_container.decode(in_stream):
            # Resample frame về đúng rate, format, layout mục tiêu
            resampled_frames = resampler.resample(frame)

            for resampled_frame in resampled_frames:
                # Đặt lại PTS cho frame để đảm bảo tính liên tục khi nối
                resampled_frame.pts = pts_offset
                pts_offset += resampled_frame.samples

                # Encode frame và ghi gói tin (packet) vào file đầu ra
                for packet in out_stream.encode(resampled_frame):
                    output_container.mux(packet)

        in_container.close()

    # 4. Flush bộ nhớ đệm của Resampler và Stream encoder
    for resampled_frame in resampler.resample(None):
        resampled_frame.pts = pts_offset
        pts_offset += resampled_frame.samples
        for packet in out_stream.encode(resampled_frame):
            output_container.mux(packet)

    for packet in out_stream.encode(None):
        output_container.mux(packet)

    output_container.close()
    print(f"Đã hoàn thành! File lưu tại: {output_file}")


# --- Ví dụ sử dụng ---
files_to_merge = ["input1.wav", "input2.mp3", "input3.ogg"]
merge_audio_files(files_to_merge, "output_merged.mp3", target_sample_rate=44100)

```

---

### Giải thích các điểm quan trọng trong code:

1. **`AudioResampler`**: Đây là trái tim của việc đồng bộ hóa. Dù các file đầu vào có là 22050Hz, 48000Hz, Mono hay Stereo, `AudioResampler` sẽ đưa tất cả về cùng một định dạng chuẩn (ở đây là `44100Hz`, `stereo`, `fltp`).
2. **Quản lý PTS (`pts_offset`)**: Khi nối nhiều file, bạn phải tự tính toán và thiết lập lại mốc thời gian (`pts`) cho các frame nối tiếp. Nếu không reset `pts`, âm thanh sẽ bị đè lên nhau hoặc file đầu ra bị hỏng timeline.
3. **Flush Buffer (`resample(None)` & `encode(None)`)**: PyAV/FFmpeg lưu một lượng mẫu trong bộ nhớ đệm (buffer). Cuối tiến trình, việc truyền `None` vào là bắt buộc để ép nó xả toàn bộ dữ liệu âm thanh còn sót lại ra file.