Khi merge các file âm thanh từ edge-tts (hoặc đa số các hệ thống Cloud TTS hiện nay như Google, OpenAI, Microsoft Azure), bạn nên đặt Sample Rate chuẩn là `24000 Hz` (24 kHz).

Dưới đây là lý do kỹ thuật chi tiết giải thích tại sao con số này là tối ưu nhất cho Audiobook:

## 1\. Bản chất Sample Rate gốc của Edge-TTS là 24 kHz

Mặc định, các mô hình AI giọng đọc Neural cao cấp của Microsoft Edge xuất ra âm thanh ở định dạng 24 kHz, 16-bit, Mono.

  * Nếu bạn ép (upsample) file lên 44.1 kHz hoặc 48 kHz: Dung lượng file MP3 xuất ra sẽ bị phình to gấp đôi một cách lãng phí, trong khi chất lượng giọng đọc hoàn toàn không tăng lên (vì dữ liệu gốc từ AI phát ra chỉ có độ phân giải tối đa là 24 kHz).
  * Nếu bạn hạ (downsample) xuống 16 kHz hoặc 8 kHz: Giọng đọc sẽ bị mất đi các dải tần số cao (âm gió, âm bật hơi như _s, ch, t, p_), khiến giọng AI nghe bị nghẹt, đục và mang nặng "tiếng máy" giống như đang nghe qua điện thoại bàn đới cũ.



## 2\. Định dạng xuất ra (Output Specification) chuẩn nhất cho Audiobook

Khi gộp (merge) các chunk âm thanh bằng script PyAV hoặc bất kỳ công cụ nào, hãy cấu hình các thông số đích cố định như sau:

  * Sample Rate: `24000` (24 kHz)
  * Channels (Layout): `mono` (1 kênh). Giọng đọc truyện chỉ có một nguồn âm duy nhất từ miệng nhân vật. Việc xuất file `stereo` (2 kênh) chỉ làm tăng gấp đôi dung lượng file mà không mang lại hiệu ứng không gian nào.
  * Bitrate khi lưu file MP3: `48 kbps` hoặc tối đa là `64 kbps`. Đối với giọng nói thuần túy (Speech), mức bitrate này là quá đủ để giữ trọn vẹn độ trong trẻo mà file lại cực kỳ nhẹ, giúp người nghe dễ dàng tải về điện thoại.



* * *

## 🛠 Đoạn code cấu hình tham số tối ưu cho PyAV

Bạn hãy cập nhật lại các hằng số cấu hình ở đầu hàm `merge_mp3_files` trong file hạ tầng `infrastructure/audio_merger.py` theo đúng chuẩn tối ưu này:
    
    
    # Cấu hình chuẩn hóa tài nguyên tối ưu tuyệt đối cho Giọng đọc AI (Audiobook)
    TARGET_RATE = 24000      # Giữ nguyên độ phân giải gốc của Edge-TTS
    TARGET_LAYOUT = "mono"    # Giọng nói đơn kênh giúp tiết kiệm 50% dung lượng file
    TARGET_FORMAT = "s16p"    # Định dạng mẫu chuẩn mã hóa
    TARGET_CODEC = "mp3"
    
    # Thêm stream đầu ra vào container
    out_stream = output_container.add_stream(TARGET_CODEC, rate=TARGET_RATE)
    out_stream.layout = TARGET_LAYOUT
    out_stream.format = TARGET_FORMAT
    out_stream.bit_rate = 48000 # Thiết lập bitrate 48 kbps siêu nhẹ, mượt mà
    out_stream.time_base = Fraction(1, TARGET_RATE)
    

Việc đồng bộ toàn bộ hệ thống về mức 24 kHz / Mono / 48 kbps sẽ giúp ứng dụng của bạn xử lý gộp file nhanh hơn gấp 3 lần (do giảm tải tính toán cho bộ Resampler) và tạo ra những file truyện Audio thành phẩm có dung lượng siêu nhỏ gọn nhưng chất lượng âm thanh vẫn rõ ràng, sắc nét.

Nếu bạn cần tối ưu thêm về khoảng lặng ngắt nghỉ giữa các chương truyện khi gộp file, hãy cho tôi biết nhé!