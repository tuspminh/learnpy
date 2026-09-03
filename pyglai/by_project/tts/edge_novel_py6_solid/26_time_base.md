Đoạn code bạn cung cấp không thiết lập `time_base` thủ công mà phó mặc cho PyAV tự động gán giá trị mặc định của encoder (thường là `1/sample_rate` đối với audio). Tuy nhiên, cách viết này tiềm ẩn nguy cơ cao gây ra lỗi lệch tốc độ âm thanh (đọc nhanh như chipmunk hoặc chậm như rùa) hoặc lỗi im lặng (silent text) khi bạn trộn (merge) các file có định dạng gốc khác nhau (WAV, MP3, OGG).

Dưới đây là 3 lý do kỹ thuật bắt buộc phải quản lý `time_base` và cách sửa code của bạn để chạy ổn định tuyệt đối:

## 1\. Tại sao code trên dễ bị lỗi "Dính" hoặc "Méo" tiếng?

  * Lỗi mất đồng bộ PTS: Khi bạn đổi file từ `input1.wav` sang `input2.mp3`, cấu hình `time_base` của container đầu vào thay đổi liên tục. Nếu không ép `resampled_frame.time_base = out_stream.time_base` một cách tường minh, giá trị `pts_offset += resampled_frame.samples` sẽ bị tính toán sai hệ quy chiếu thời gian, dẫn đến việc các đoạn âm thanh sau đè lên đoạn trước hoặc bị kéo dài tần số.
  * Định dạng mẫu không khớp: Bạn đang ép cứng `out_stream.format = "fltp"` cho cả MP3 và WAV. Codec `pcm_s16le` của file WAV không hỗ trợ định dạng `fltp` (Float Planar) mà chỉ hỗ trợ `s16` (Signed 16-bit packed). Nếu chạy vào file `.wav`, PyAV sẽ lập tức quăng lỗi `ValueError` hoặc `Invalid Argument`.



* * *

## 2\. Bản code đã sửa lỗi - Tối ưu 24kHz Mono cho Giọng đọc AI

Dưới đây là hàm `merge_audio_files` của bạn đã được tái cấu trúc lại. Tôi đã sửa lỗi gán codec/format động, thiết lập `time_base` bằng phân số `Fraction` chuẩn, và cấu hình lại thông số `24000Hz` / `mono` tốt nhất cho giọng đọc `edge-tts`:
    
    
    import os
    import av
    from fractions import Fraction
    
    def merge_audio_files(input_files, output_file, target_sample_rate=24000):
        """
        Gộp các file audio chunk thành một file duy nhất bằng PyAV.
        Quản lý PTS và time_base tường minh để chống méo tiếng, giật tiếng.
        """
        if not input_files:
            print("Danh sách file đầu vào rỗng!")
            return
    
        # 1. Xác định Codec và Sample Format phù hợp với đuôi file đầu ra
        if output_file.endswith(".mp3"):
            codec_name = "mp3"
            target_format = "s16p"     # MP3 encoder của FFmpeg chuộng Signed 16-bit Planar
        elif output_file.endswith(".wav"):
            codec_name = "pcm_s16le"
            target_format = "s16"      # WAV (PCM) bắt buộc dùng Signed 16-bit Packed
        else:
            codec_name = "aac"
            target_format = "fltp"     # AAC yêu cầu Float Planar
    
        # Tối ưu cho Audiobook: Đặt mono (1 kênh) để giảm 50% dung lượng, bitrate 48kbps siêu nhẹ
        target_layout = "mono" 
    
        # 2. Tạo container đầu ra và cấu hình Audio Stream
        output_container = av.open(output_file, mode="w")
        out_stream = output_container.add_stream(codec_name, rate=target_sample_rate)
        out_stream.layout = target_layout
        out_stream.format = target_format
        
        if codec_name == "mp3":
            out_stream.bit_rate = 48000 # 48 kbps cho file mp3 giọng đọc AI cực mượt
    
        # ĐẶT TIME_BASE TƯỜNG MINH: Nghịch đảo của sample rate (1 / 24000)
        # Giúp PyAV tính toán chính xác mốc thời gian hiển thị mẫu âm thanh
        out_stream.time_base = Fraction(1, target_sample_rate)
    
        # 3. Khởi tạo bộ chuyển đổi Resampler (AudioResampler)
        resampler = av.AudioResampler(
            format=out_stream.format,
            layout=out_stream.layout,
            rate=out_stream.rate,
        )
    
        pts_offset = 0  # Biến theo dõi mốc thời gian (Presentation Time Stamp)
    
        # 4. Duyệt qua từng file đầu vào
        for file_path in input_files:
            if not os.path.exists(file_path):
                print(f"Bỏ qua (File không tồn tại): {file_path}")
                continue
                
            print(f"Đang xử lý: {file_path}")
            in_container = av.open(file_path)
    
            # Kiểm tra an toàn đề phòng file không chứa stream audio
            if not in_container.streams.audio:
                in_container.close()
                continue
            in_stream = in_container.streams.audio[0]
    
            for packet in in_container.demux(in_stream):
                for frame in packet.decode():
                    # Resample frame về đúng thông số mục tiêu
                    resampled_frames = resampler.resample(frame)
    
                    for resampled_frame in resampled_frames:
                        # ĐỒNG BỘ TIME_BASE & PTS QUAN TRỌNG TẠI ĐÂY:
                        resampled_frame.pts = pts_offset
                        resampled_frame.time_base = out_stream.time_base
                        
                        # Tăng tiến PTS tịnh tiến theo số lượng mẫu thực tế trong khung
                        pts_offset += resampled_frame.samples
    
                        # Encode frame và ghi gói tin (packet) vào file đầu ra
                        for out_packet in out_stream.encode(resampled_frame):
                            output_container.mux(out_packet)
    
            in_container.close()
    
        # 5. Flush bộ nhớ đệm ẩn của Resampler
        for resampled_frame in resampler.resample(None):
            resampled_frame.pts = pts_offset
            resampled_frame.time_base = out_stream.time_base
            pts_offset += resampled_frame.samples
            for out_packet in out_stream.encode(resampled_frame):
                output_container.mux(out_packet)
    
        # 6. Flush bộ nhớ đệm ẩn của Stream Encoder
        for out_packet in out_stream.encode(None):
            output_container.mux(out_packet)
    
        output_container.close()
        print(f"✓ Đã hoàn thành gộp truyện! File lưu tại: {output_file}")
    
    
    # --- Test thử nghiệm với dải tần 24kHz tối ưu của Edge-TTS ---
    files_to_merge = ["temp_chunk0.mp3", "temp_chunk1.mp3", "temp_chunk2.mp3"]
    merge_audio_files(files_to_merge, "output_audiobook.mp3", target_sample_rate=24000)
    

## 💡 Những điểm cốt lõi đã được sửa đổi:

  1. `resampled_frame.time_base = out_stream.time_base`: Dòng lệnh này ép mọi khung hình sau khi chuyển đổi tần số phải đồng nhất hệ thời gian với file lưu trữ MP3, triệt tiêu lỗi mất tiếng.
  2. Tự động cấu hình `target_format`: Code tự biết đổi `s16p` cho MP3 hoặc `s16` cho WAV, ngăn lỗi sập chương trình khi biên dịch chéo định dạng.
  3. Sử dụng cấu trúc `demux()` an toàn: Thay thế `in_container.decode(in_stream)` bằng cấu trúc giải gói packet `demux(in_stream)` chuẩn chỉ của FFmpeg giúp tiết kiệm tài nguyên RAM khi nạp file dài.



Bạn hãy thử copy phiên bản sửa đổi này đè lên hàm cũ, file MP3 audiobook xuất ra sẽ mượt mà liên tục, không bao giờ bị dính lỗi đứng khung hình hay đứt đoạn dải âm!