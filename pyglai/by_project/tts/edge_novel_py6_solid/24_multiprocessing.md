Để tối ưu tốc độ xử lý khi nối danh sách nhiều file audio, bạn có thể áp dụng mô hình **Producer-Consumer (Producer = Multiprocessing, Consumer = Single Thread Encoder)**.

Lý do là công đoạn nặng nhất chiếm CPU chính là **Decode & Resample** từng file audio đầu vào. Chúng ta sẽ dùng `multiprocessing.Pool` để decode/resample song song các file này ra đĩa tạm dạng **PCM thô (raw pcm)**. Sau đó, tiến trình chính (Main Process) chỉ việc đọc nối tiếp các file PCM tạm này để **Encode** ra file hoàn chỉnh.

---

### Mã nguồn Multiprocessing Merge & Resample Audio

```python
import os
import tempfile
from multiprocessing import Pool
import numpy as np
import av

# 1. Hàm worker chạy trên từng Process riêng biệt
def process_single_file(args):
    """
    Decode + Resample một file audio duy nhất và ghi kết quả PCM thô ra file tạm.
    Hàm này sẽ được thực thi song song trên nhiều nhân CPU.
    """
    file_index, input_path, target_rate, temp_dir = args
    temp_raw_path = os.path.join(temp_dir, f"temp_{file_index}.pcm")
    
    container = av.open(input_path)
    stream = container.streams.audio[0]
    resampler = av.AudioResampler(format="fltp", layout="stereo", rate=target_rate)
    
    # Mở file nhị phân tạm để ghi PCM raw float32
    with open(temp_raw_path, "wb") as f_out:
        total_samples = 0
        
        for frame in container.decode(stream):
            for r_frame in resampler.resample(frame):
                arr = r_frame.to_ndarray() # Shape: (2, samples), float32
                f_out.write(arr.tobytes())
                total_samples += r_frame.samples
                
        # Flush resampler
        for r_frame in resampler.resample(None):
            arr = r_frame.to_ndarray()
            f_out.write(arr.tobytes())
            total_samples += r_frame.samples
            
    container.close()
    return temp_raw_path, total_samples


# 2. Hàm chính điều khiển tiến trình ghép nối
def merge_audio_multiprocessing(input_files, output_file, target_rate=44100, num_workers=None):
    # Tạo thư mục tạm để lưu các file PCM thô
    with tempfile.TemporaryDirectory() as temp_dir:
        # Chuẩn bị danh sách tham số cho các Worker Processes
        tasks = [
            (i, file_path, target_rate, temp_dir) 
            for i, file_path in enumerate(input_files)
        ]
        
        # --- BƯỚC 1: Xử lý song song Decode & Resample (MULTIPROCESSING) ---
        print(f"Đang Decode & Resample {len(input_files)} file song song...")
        with Pool(processes=num_workers) as pool:
            # imap hoặc map để đảm bảo thứ tự file trả về đúng như đầu vào
            results = pool.map(process_single_file, tasks)
            
        print("Tất cả worker đã hoàn thành! Bắt đầu Encode file đầu ra...")
        
        # --- BƯỚC 2: Encode trực tiếp theo dạng Streaming từ các file PCM tạm ---
        out_container = av.open(output_file, mode="w")
        codec_name = "mp3" if output_file.endswith(".mp3") else "aac"
        out_stream = out_container.add_stream(codec_name, rate=target_rate)
        out_stream.layout = "stereo"
        out_stream.format = "fltp"
        
        pts_counter = 0
        FRAME_SIZE = 1024 # Kích thước chuẩn cho 1 AAC/MP3 frame
        bytes_per_sample = 4 * 2 # float32 (4 bytes) * 2 kênh (stereo)
        frame_bytes = FRAME_SIZE * bytes_per_sample
        
        # Đọc nối tiếp từng file tạm và Encode
        for temp_raw_path, total_samples in results:
            with open(temp_raw_path, "rb") as f_in:
                while True:
                    data = f_in.read(frame_bytes)
                    if not data:
                        break
                    
                    # Khôi phục numpy array từ raw bytes
                    arr = np.frombuffer(data, dtype=np.float32)
                    arr = arr.reshape(2, -1) # Reshape về (channels, samples)
                    
                    # Padding nếu chunk cuối của file chưa đủ FRAME_SIZE
                    if arr.shape[1] < FRAME_SIZE:
                        pad_len = FRAME_SIZE - arr.shape[1]
                        arr = np.pad(arr, ((0, 0), (0, pad_len)), mode='constant')
                    
                    # Đóng gói PyAV AudioFrame
                    f = av.AudioFrame.from_ndarray(arr, format="fltp", layout="stereo")
                    f.rate = target_rate
                    f.pts = pts_counter
                    pts_counter += arr.shape[1]
                    
                    for packet in out_stream.encode(f):
                        out_container.mux(packet)
        
        # Flush Encoder
        for packet in out_stream.encode(None):
            out_container.mux(packet)
            
        out_container.close()
        print(f"Đã hoàn thành! File lưu tại: {output_file}")


# --- VÍ DỤ SỬ DỤNG ---
if __name__ == "__main__":
    audio_list = ["input1.mp3", "input2.wav", "input3.flac", "input4.m4a"]
    
    # Chạy nối file dùng tối đa số nhân CPU hiện có
    merge_audio_multiprocessing(audio_list, "output_fast_merged.mp3", target_rate=44100)

```

---

### Kiến trúc này tối ưu hiệu năng như thế nào?

1. **Vượt qua rào cản Python GIL**: Mỗi file audio được đảm nhận bởi một Process Python độc lập, giúp tận dụng tối đa 100% các nhân CPU (Multi-core) cho việc Decode và Resample.
2. **Ghi đĩa dạng Streaming (Low RAM)**: Các Worker ghi trực tiếp chuỗi byte âm thanh (`.tobytes()`) xuống đĩa dưới dạng PCM thô. RAM của từng tiến trình luôn duy trì ở mức rất thấp.
3. **Đảm bảo tính liên tục của Timeline**: Do kết quả `results` của `pool.map` giữ nguyên thứ tự danh sách file ban đầu, tiến trình chính đọc lần lượt các file tạm để cộng dồn `pts_counter` chuẩn xác mà không bị đè hay lệch tiếng.

*(Lưu ý: Luôn đặt mã thực thi trong khối `if __name__ == "__main__":` khi làm việc với `multiprocessing` trên Python để tránh lỗi spawn process lặp vô tận).*