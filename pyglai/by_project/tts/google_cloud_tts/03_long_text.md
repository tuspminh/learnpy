Khi xử lý văn bản dài (vượt quá 5.000 ký tự), API `synthesize_speech` thông thường sẽ trả về lỗi giới hạn. Đối với các tài liệu dài như sách truyện hoặc bài báo, Google Cloud cung cấp API Long Audio Synthesis (`synthesize_long_audio`). Phương thức này xử lý bất đồng bộ, hỗ trợ tối đa 1 triệu ký tự và lưu trực tiếp file kết quả lên Google Cloud Storage (GCS).

Tôi đã tạo sẵn cho bạn một file hướng dẫn chi tiết và mã nguồn Python hoàn chỉnh để xử lý tác vụ này.

## Tải file hướng dẫn cấu hình và mã nguồn Python

Sử dụng script Python bên dưới để tạo file `huong_dan_long_audio.md` chứa toàn bộ code mẫu chuẩn hóa:

Here is your file: 

## Tóm tắt các điểm cốt lõi khi xử lý văn bản dài:

  * Sử dụng API Bất đồng bộ (`SynthesizeLongAudioRequest`): Thay vì nhận dữ liệu nhị phân trả về trực tiếp (đồng bộ), API này sẽ tạo một tiến trình chạy ngầm để chuyển đổi văn bản lên tới 1.000.000 ký tự.
  * Bắt buộc có Google Cloud Storage (GCS): Kết quả âm thanh đầu ra không trả về biến trong Python mà được lưu thẳng vào một Bucket dạng `gs://ten-bucket/file.wav` do bạn chỉ định.
  * Thư viện v1beta1: Tính năng này hiện tại hoạt động ổn định nhất trên phân hệ mã nguồn `google.cloud.texttospeech_v1beta1`.



Bạn hãy cho tôi biết nếu cần hướng dẫn thêm về cách tự động chia nhỏ văn bản bằng Python (nếu không muốn dùng Cloud Storage) hoặc cách tải file kết quả từ GCS về máy tính nhé!