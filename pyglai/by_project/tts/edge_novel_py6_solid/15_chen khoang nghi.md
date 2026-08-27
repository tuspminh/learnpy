Để chèn khoảng nghỉ (silent pause) giữa các đoạn văn hoặc các câu trong `edge-tts`, cách chuẩn nhất là sử dụng thẻ SSML (Speech Synthesis Markup Language) với thẻ `<break time="..." />`.

Tuy nhiên, `edge-tts` (qua thư viện Python mặc định) sẽ báo lỗi nếu bạn truyền một văn bản chứa mã SSML thô vào hàm `edge_tts.Communicate()`. Bạn buộc phải đổi hàm gọi từ truyền văn bản thuần sang cấu trúc tạo chuỗi SSML hoàn chỉnh.

Dưới đây là cách cập nhật mã nguồn theo đúng chuẩn DDD/SOLID để hỗ trợ tính năng này:

## 1\. Cập nhật Quy tắc chèn khoảng nghỉ trong Domain

Chúng ta sẽ quy ước: Cứ mỗi khi người đọc xuống dòng (`\n`), hệ thống sẽ tự động chèn một thẻ nghỉ với thời gian tùy chọn (ví dụ: `2s` hoặc `1500ms`).

Bạn hãy cập nhật lại hàm `normalize` trong lớp `TextNormalizer`:
    
    
    class TextNormalizer:
        @staticmethod
        def normalize(text: str) -> str:
            if not text: return ""
            # ... (giữ nguyên các bước xử lý dấu câu 1, 2, 3, 4, 5 từ code trước) ...
    
            # 6. Dọn dẹp khoảng trắng thừa giữa các từ
            lines = text.split('\n')
            cleaned_lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in lines]
            
            # Loại bỏ các dòng trống liên tiếp, chỉ giữ lại nội dung thực tế
            cleaned_lines = [line for line in cleaned_lines if line]
            
            # Gộp lại bằng dấu xuống dòng chuẩn
            return '\n'.join(cleaned_lines)
            
        @staticmethod
        def convert_to_ssml(text: str, voice_id: str, rate: str, pitch: str, pause_duration: str = "2s") -> str:
            """
            Chuyển đổi văn bản thuần có dấu xuống dòng (\n) thành chuỗi SSML hợp lệ.
            Mỗi dấu xuống dòng sẽ được thay thế bằng thẻ <break time="..." /> để tạo khoảng nghỉ.
            """
            # Chia văn bản thành các đoạn theo dấu xuống dòng
            paragraphs = text.split('\n')
            
            # Bao bọc từng đoạn bằng thẻ XML, chèn thẻ break ở giữa các đoạn
            ssml_parts = []
            for p in paragraphs:
                if p.strip():
                    # Ép kiểu an toàn cho các ký tự đặc biệt trong XML để tránh lỗi cú pháp
                    p_escaped = p.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    ssml_parts.append(p_escaped)
            
            # Nối các đoạn văn lại với nhau bằng thẻ nghỉ
            break_tag = f'<break time="{pause_duration}"/>'
            ssml_content = break_tag.join(ssml_parts)
            
            # Tạo khung SSML hoàn chỉnh theo tiêu chuẩn của Microsoft Edge
            ssml = f"""<speak version='1.0' xmlns='http://w3.org' xml:lang='en-US'>
                <voice name='{voice_id}'>
                    <prosody rate='{rate}' pitch='{pitch}'>
                        {ssml_content}
                    </prosody>
                </voice>
            </speak>"""
            return ssml
    

## 2\. Cập nhật Hạ tầng (Infrastructure) để đọc SSML

Thay vì gọi `edge_tts.Communicate(text, voice)`, ta sẽ đổi sang hàm `edge_tts.Communicate(ssml=ssml_string)` (bỏ tham số voice, rate, pitch ngoài vì nó đã được định nghĩa trực tiếp bên trong chuỗi SSML).

Cập nhật file `infrastructure/tts_service.py`:
    
    
    class EdgeTTSService(ITTSService):
        async def convert_chunk_to_mp3(self, text: str, voice: Voice, rate: str, pitch: str, output_path: str) -> None:
            # 1. Chuyển đổi text của chunk đó sang định dạng SSML, chèn khoảng nghỉ 1.5 giây giữa các dòng nhỏ
            ssml_data = TextNormalizer.convert_to_ssml(
                text=text, 
                voice_id=voice.id, 
                rate=rate, 
                pitch=pitch, 
                pause_duration="1.5s" # Bạn có thể đổi thành 1s, 2s, 500ms tùy ý
            )
            
            # 2. Truyền tham số thông qua biến 'ssml' thay vì 'text'
            communicate = edge_tts.Communicate(ssml=ssml_data)
            await communicate.save(output_path)
    

## 3\. Cách sử dụng và bổ sung tham số CLI

Để người dùng có thể tự cấu hình thời gian nghỉ từ màn hình dòng lệnh, bạn chỉ cần mở file `cli_app.py` ra và thêm một tùy chọn `@click.option` mới:
    
    
    @click.option('--pause', '-pa', default='1.5s', help='Thời gian nghỉ giữa các đoạn văn, ví dụ: 1s, 2s, 500ms.', show_default=True)
    

Sau đó, trong hàm `convert_chunk_to_mp3` của lớp hạ tầng, bạn hãy truyền biến `pause` này vào tham số `pause_duration` của hàm `convert_to_ssml` là xong.

## 💡 Lưu ý quan trọng khi dùng Thẻ Nghỉ (`<break/>`):

  * Thời gian tối đa: Microsoft Edge giới hạn thời gian nghỉ tối đa của một thẻ `<break/>` là `5s` (5 giây) hoặc `5000ms`. Nếu bạn truyền `6s`, API sẽ báo lỗi cú pháp XML.
  * Tự động ngắt dấu câu: Mặc định, hệ thống AI của Microsoft đã tự động nghỉ khoảng `200ms - 400ms` sau dấu chấm câu (`.`) và `100ms` sau dấu phẩy (`,`). Do đó, bạn chỉ nên dùng thẻ break này cho các đoạn văn xuống dòng để phân tách mạch truyện rõ ràng hơn.



Nếu bạn cần tôi cập nhật lại toàn bộ file CLI hoàn chỉnh đã tích hợp sẵn tính năng chèn SSML break này, hãy báo cho tôi biết nhé!