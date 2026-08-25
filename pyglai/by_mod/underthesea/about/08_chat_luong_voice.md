Khi đặt module `tts` của Underthesea (hoạt động dựa trên lõi học sâu mã nguồn mở [vietTTS](https://github.com/ntt123/vietTTS) hoặc kết hợp các kiến trúc FastSpeech/MeloTTS) lên bàn cân với các hệ thống TTS khác tại Việt Nam, chất lượng giọng nói có những điểm khác biệt rất rõ ràng dựa trên mục đích sử dụng. [1, 2] 

Bảng so sánh chi tiết dưới đây phân tích chất lượng của Underthesea so với 3 nhóm công cụ phổ biến:

## Bảng so sánh chất lượng giọng nói (TTS)

Tiêu chí so sánh| Underthesea TTS| Thương mại VN (Vbee, FPT.AI, Viettel)| Quốc tế Cao cấp (ElevenLabs, OpenAI)| Mã nguồn mở chuyên sâu (F5-TTS, Piper)  
---|---|---|---|---  
Độ tự nhiên & Ngữ điệu| Khá (Đọc đúng dấu câu, ngắt nghỉ cơ bản)| Tốt (Có ngữ điệu vùng miền Bắc/Trung/Nam rất chuẩn)| Xuất sắc (Giọng đọc như người thật, biểu cảm cao)| Rất tốt (Ngữ điệu tự nhiên nhờ lượng data huấn luyện lớn)  
Độ mượt (Tránh tiếng robot)| Trung bình - Khá (Vẫn có cảm giác hơi đều đều ở câu dài)| Tốt (Rất ít khi bị dính chữ hay biến dạng âm)| Xuất sắc (Hầu như không có cảm giác máy móc)| Tốt (Mô hình khuếch tán âm thanh xử lý tiếng ồn tốt)  
Xử lý từ mượn/Số/Từ viết tắt| Trung bình (Cần chuẩn hóa thủ công trước bằng `text_normalize`)| Xuất sắc (Tự dịch số "2026", đọc "km/h" rất chuẩn)| Khá (Đôi khi đọc từ viết tắt tiếng Việt theo kiểu tiếng Anh)| Khá (Phụ thuộc hoàn toàn vào cách tiền xử lý text)  
Sự đa dạng giọng đọc| Rất ít (Chỉ có 1-2 giọng mặc định cố định)| Rất nhiều (Hàng chục giọng nam/nữ, già/trẻ, đủ vùng miền)| Phong phú (Hàng trăm giọng, hỗ trợ tạo giọng/Clone giọng)| Tùy biến cao (Cho phép tự đem dữ liệu vào để train giọng riêng)  
Chi phí & Bản quyền| Miễn phí hoàn toàn (Mã nguồn mở GPL-3.0)| Trả phí theo ký tự (Có gói miễn phí giới hạn thấp)| Phí cao (Tính theo ký tự/tháng bằng USD)| Miễn phí hoàn toàn (Cần có kiến thức kỹ thuật để tự cài)  
  
* * *

## Đánh giá chi tiết ưu và nhược điểm của Underthesea TTS

## 👍 Điểm mạnh:

  * Xử lý dấu thanh cực chuẩn: Nhờ tích hợp sâu với bộ công cụ NLP của chính [Underthesea](https://github.com/undertheseanlp/underthesea), hệ thống phân tích từ ghép và 6 thanh điệu tiếng Việt (`ma, má, mà, mả, mã, mạ`) rất chính xác, không bị hiện tượng méo tiếng ở các nguyên âm khó. [3] 
  * Hoạt động Offline hoàn toàn: Bạn không cần kết nối mạng, không cần tạo tài khoản, không lo bị lộ dữ liệu nội bộ ra ngoài Internet và không sợ bị giới hạn số lượng ký tự hằng tháng. [4, 5] 
  * Tích hợp sâu vào Code: Phù hợp nhất để làm các tác vụ tự động hóa, thông báo dòng lệnh, hoặc nhúng trực tiếp vào các Local AI Agent (Trợ lý ảo chạy trên máy cá nhân). [6, 7] 



## 👎 Điểm yếu:

  * Thiếu biểu cảm (Cảm xúc): Giọng đọc của Underthesea mang tính chất "đọc văn bản" (đọc báo, đọc tài liệu) phẳng và đều. Nó không có các tông giọng biểu cảm vui, buồn, tức giận hay thì thầm giống như [ElevenLabs](https://elevenlabs.io/) hay các nền tảng thương mại. [4, 8, 9] 
  * Tốn tài nguyên máy tính: Do chạy trực tiếp trên máy của bạn (`Local`), nếu không có card đồ họa GPU rời để tăng tốc deep learning, tốc độ sinh file âm thanh trên CPU sẽ bị chậm đối với các đoạn văn dài. [4] 



Nếu bạn muốn nâng cấp chất lượng giọng nói, tôi có thể hướng dẫn:

  * Cách cấu hình Underthesea gọi API của OpenAI / Google Gemini để lấy giọng đọc cao cấp thông qua module `providers`.
  * Cách cài đặt F5-TTS Tiếng Việt hoặc MeloTTS nếu bạn muốn dùng một giải pháp mã nguồn mở khác có giọng đọc tự nhiên hơn. [2, 6, 7, 10] 



Bạn đang cần dùng TTS cho dự án dạng nào (làm video, tổng đài tự động, hay trợ lý ảo)?

  


[1] [https://viblo.asia](https://viblo.asia/p/tim-hieu-1-so-mo-hinh-text-to-speech-p1-vyDZORjQKwj)

[2] [https://huggingface.co](https://huggingface.co/nmcuong/MeloTTS-Vietnamese/blame/main/README.md)

[3] [https://anyspeech.io](https://anyspeech.io/vi/vietnamese-text-to-speech)

[4] [https://anyspeech.io](https://anyspeech.io/vi/blog/best-text-to-speech-tools)

[5] [https://vbee.vn](https://vbee.vn/blog/chuyen-van-ban-thanh-giong-noi/linh-vuc/truyen-thong/)

[6] [https://github.com](https://github.com/undertheseanlp/underthesea)

[7] [https://github.com](https://github.com/undertheseanlp/underthesea)

[8] [https://ai-hay.vn](https://ai-hay.vn/giong-noi-nhan-ban-khac-text-to-speech-tieu-chuan-the-nao-pN1UmIxSMFW)

[9] [https://sider.ai](https://sider.ai/vi/blog/ai-tools/the-strategic-stack-of-voice-a-comparative-analysis-of-top-tts-tools)

[10] [https://www.facebook.com](https://www.facebook.com/groups/machinelearningcoban/posts/2247841805673214/)