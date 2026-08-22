Khi phát triển ứng dụng với `edge-tts` ở quy mô lớn (như cào truyện, quét cả thư mục file văn bản), bạn chắc chắn sẽ gặp phải một số lỗi hệ thống từ phía server Microsoft hoặc lỗi định dạng.

Dưới đây là cẩm nang xử lý các lỗi phổ biến nhất bằng code Python thực tế để ứng dụng của bạn không bị sập giữa chừng.

* * *

## 1\. Lỗi nghẽn kết nối / Bị chặn IP (Rate Limit / Connection Closed)

  * Dấu hiệu: Xuất hiện lỗi `ConnectionResetError`, `websockets.exceptions.ConnectionClosedError`, hoặc bài đọc bị ngắt quãng giữa chừng khi đang chạy `stream()`.
  * Nguyên nhân: Bạn gửi quá nhiều yêu cầu liên tục trong thời gian ngắn khiến server Microsoft nghi ngờ là DDOS và chặn kết nối tạm thời.
  * Cách xử lý (Mã hóa cơ chế Retry với Exponential Backoff):


    
    
    import asyncio
    import edge_tts
    
    async def safe_communicate_with_retry(text, voice, output_file, max_retries=3):
        """Tự động thử lại (Retry) với thời gian chờ tăng dần nếu gặp lỗi mạng."""
        communicate = edge_tts.Communicate(text, voice)
        delay = 2  # Thời gian chờ ban đầu là 2 giây
    
        for attempt in range(1, max_retries + 1):
            try:
                # Tiến hành tải stream an toàn
                with open(output_file, "wb") as f:
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            f.write(chunk["data"])
                return True  # Thành công, thoát hàm
                
            except Exception as e:
                print(f"   [CẢNH BÁO] Lần thử {attempt}/{max_retries} thất bại do: {e}")
                if attempt == max_retries:
                    raise e  # Nếu hết lượt thử thì báo lỗi thật
                    
                print(f"   -> Đang ngủ {delay} giây trước khi thử lại...")
                await asyncio.sleep(delay)
                delay *= 2  # Tăng gấp đôi thời gian chờ cho lần sau (2s -> 4s -> 8s)
    

* * *

## 2\. Lỗi ký tự lạ / Thẻ HTML / Dấu câu không hợp lệ

  * Dấu hiệu: Giọng đọc AI tự nhiên đọc cả các ký tự code như `&amp;`, `<br>`, hoặc bỏ qua cả một đoạn văn dài không đọc.
  * Nguyên nhân: Văn bản cào từ web về chứa thẻ HTML ẩn, hoặc chứa các ký tự đặc biệt khiến trình phân tích cú pháp XML của Edge bị lỗi.
  * Cách xử lý (Chuẩn hóa Text trước khi gửi):


    
    
    import re
    import html
    
    def clean_text_for_edge(text: str) -> str:
        # 1. Giải mã các thực thể HTML (ví dụ: &amp; thành &, &quot; thành ")
        text = html.unescape(text)
        
        # 2. Xóa bỏ hoàn toàn các thẻ HTML dạng <abc> hoặc </abc>
        text = re.sub(re.compile('<.*?>'), '', text)
        
        # 3. Thay thế các ký tự toán học hoặc ký tự lạ dễ gây lỗi hệ thống
        text = text.replace("<", " nhỏ hơn ").replace(">", " lớn hơn ")
        
        # 4. Thu gọn các khoảng trắng và dấu xuống dòng liên tiếp
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    

* * *

## 3\. Lỗi lệch mốc thời gian WordBoundary (Khi text chứa số/từ tiếng Anh)

  * Dấu hiệu: File phụ đề `.srt` bị lệch dòng, chữ chạy trước hoặc sau tiếng đọc.
  * Nguyên nhân: Khi văn bản có số (ví dụ: `2026`), Edge-TTS sẽ trả về chunk WordBoundary cho từ `"2026"`, nhưng miệng AI lại đọc ra 4 từ tiếng Việt là `"hai nghìn không trăm hai sáu"`. Điều này khiến thuật toán đếm từ đơn bị lệch.
  * Cách xử lý:

    * Cách 1: Sử dụng thư viện `vietnamese-number` hoặc tự viết hàm đổi toàn bộ số thành chữ (ví dụ: `15` -> `mười lăm`) trước khi truyền vào `edge-tts`.
    * Cách 2: Gom câu dựa trên mốc thời gian thực tế thay vì đếm từ, như thuật toán dấu câu `end_punctuation` tôi đã hướng dẫn bạn ở câu hỏi trước (thuật toán đó tự động lấy thời gian kết thúc của ký tự cuối cùng nên hoàn toàn không bị ảnh hưởng bởi việc từ dài hay ngắn).




* * *

## 4\. Lỗi "Giọng đọc không tồn tại" (Unknown Voice)

  * Dấu hiệu: Báo lỗi cấu hình giọng đọc, không sinh được file.
  * Nguyên nhân: Microsoft thỉnh thoảng cập nhật, đổi tên hoặc khai tử một số voice cũ.
  * Cách xử lý: Luôn kiểm tra danh sách giọng đọc thực tế bằng lệnh CLI trực tiếp của thư viện để cập nhật mã nguồn:


    
    
    edge-tts --list-voices | grep vi-VN
    

* * *

## Tổng kết cấu trúc khối `try-except` bọc cho dự án của bạn:

Khi tích hợp vào công cụ quét thư mục, bạn nên bọc toàn bộ tiến trình của một file `.txt` trong khối xử lý ngoại lệ để nếu một file bị lỗi (do text quá dài hoặc mạng sập), hệ thống vẫn bỏ qua và chạy tiếp file tiếp theo thay vì dừng toàn bộ tool:
    
    
    try:
        cleaned_text = clean_text_for_edge(raw_text)
        await safe_communicate_with_retry(cleaned_text, VOICE, output_file)
    except Exception as final_error:
        print(f" [LỖI NGHIÊM TRỌNG] Không thể xử lý file này: {final_error}")
        # Ghi log lỗi ra file để kiểm tra sau, không làm sập hệ thống
        with open("error_log.txt", "a") as log:
            log.write(f"Lỗi tại file X: {str(final_error)}\n")
    

Nếu bạn muốn, tôi có thể hướng dẫn bạn cách viết hàm chuyển đổi số tự động sang chữ tiếng Việt để sửa triệt để lỗi lệch phụ đề, hoặc cách tự động phát hiện và dịch các từ tiếng Anh thông dụng sang phiên âm tiếng Việt trước khi đọc!