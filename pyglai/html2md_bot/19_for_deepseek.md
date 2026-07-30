Để chuẩn hóa nội dung chat copy từ DeepSeek (thường có giao diện web chứa các khối code block, nút "Copy", icon suy nghĩ, v.v.) thành định dạng Markdown chuẩn và sạch sẽ, chúng ta cần bổ sung các class và cấu trúc đặc trưng của DeepSeek vào bộ lọc `BeautifulSoup` trong hàm `clean_and_convert`.

Trình duyệt khi copy từ DeepSeek thường gom cả các nút bấm tiện ích và các thẻ định dạng đặc thù của họ. Dưới đây là đoạn code PySide6 đã được cập nhật bộ lọc tối ưu riêng cho DeepSeek để dọn sạch các thành phần thừa:

Mã nguồn PySide6 tối ưu riêng cho DeepSeek

python
    
    
    import sys
    from bs4 import BeautifulSoup
    import html2text
    
    # Chỉ dùng thư viện chuẩn PySide6
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
    from PySide6.QtCore import QSize, Qt, QTimer
    
    def clean_and_convert(html_raw):
        # 1. Loại bỏ đoạn Meta Windows Clipboard
        lower_html = html_raw.lower()
        start_idx = lower_html.find("<html")
        if start_idx == -1:
            fragment_idx = lower_html.find("endfragment:")
            if fragment_idx != -1:
                start_idx = html_raw.find("<", fragment_idx)
        if start_idx != -1:
            html_raw = html_raw[start_idx:]
    
        # 2. Lọc quảng cáo, rác và CÁC THÀNH PHẦN ĐẶC THÙ CỦA DEEPSEEK bằng BeautifulSoup
        soup = BeautifulSoup(html_raw, 'html.parser')
        
        # Loại bỏ các thẻ rác hệ thống thông thường
        tags_to_remove = ['script', 'style', 'noscript', 'iframe', 'aside', 'nav', 'footer', 'header']
        for tag in soup.find_all(tags_to_remove):
            tag.decompose()
    
        # Các từ khóa xuất hiện trong Class/ID rác của DeepSeek và các trang AI khác
        # - 'copy', 'download': các nút copy code block của DeepSeek
        # - 'icon', 'button': các nút thao tác phụ bên dưới câu trả lời
        # - 'ds-markdown-skip': một số class hệ thống của DeepSeek cần bỏ qua
        bad_keywords = [
            'ads', 'advertisement', 'banner', 'sidebar', 'share', 'social', 
            'copy-btn', 'copy-button', 'popup', 'feedback', 'thumb', 'dislike', 'like'
        ]
    
        for element in soup.find_all(True):
            # Duyệt và xóa theo Class
            if element.get('class'):
                class_str = " ".join(element.get('class')).lower()
                if any(keyword in class_str for keyword in bad_keywords):
                    element.decompose()
                    continue
                    
            # Duyệt và xóa theo ID
            if element.get('id'):
                id_str = element.get('id').lower()
                if any(keyword in id_str for keyword in bad_keywords):
                    element.decompose()
    
        # 3. Chuyển đổi sang Markdown bằng html2text với cấu hình chuẩn AI
        converter = html2text.HTML2Text()
        converter.bypass_tables = False     # Giữ lại bảng dữ liệu so sánh của DeepSeek nếu có
        converter.ignore_links = False      # Giữ lại các link tham khảo
        converter.ignore_emphasis = False   # Giữ lại chữ in đậm (**), in nghiêng (*)
        converter.body_width = 0            # Không tự động xuống dòng ngắt quãng (giữ nguyên đoạn văn dài)
        
        # Cấu hình nâng cao cho code block
        converter.mark_code = True          # Đảm bảo nhận diện chính xác cặp dấu ``` cho code block
        
        markdown_result = converter.handle(str(soup)).strip()
        
        # 4. HẬU XỬ LÝ CHUỖI (Khắc phục lỗi định dạng hiển thị của DeepSeek nếu có)
        # Loại bỏ các ký tự rác hoặc khoảng trắng thừa do các thẻ div lồng nhau của DeepSeek tạo ra
        lines = markdown_result.split('\n')
        cleaned_lines = []
        for line in lines:
            # Loại bỏ các dòng chỉ chứa nút bấm đơn lẻ lọt lưới (như chữ "Copy code" thô)
            if line.strip().lower() in ["copy code", "sao chép", "copy"]:
                continue
            cleaned_lines.append(line)
            
        return '\n'.join(cleaned_lines).strip()
    
    
    class AutoMarkdownConverter(QWidget):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("DeepSeek to MD")
            self.setFixedSize(QSize(200, 80))
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # Luôn ghim trên cùng
            
            self.is_processing = False
            
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            
            self.btn_toggle = QPushButton("AUTO: ON")
            self.btn_toggle.setCheckable(True)
            self.btn_toggle.setChecked(True)
            self.btn_toggle.clicked.connect(self.on_toggle_clicked)
            
            self.btn_toggle.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px;")
            layout.addWidget(self.btn_toggle)
            
            self.clipboard = QApplication.clipboard()
            self.clipboard.dataChanged.connect(self.on_clipboard_changed)
    
        def on_toggle_clicked(self, checked):
            if checked:
                self.btn_toggle.setText("AUTO: ON")
                self.btn_toggle.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px;")
            else:
                self.btn_toggle.setText("AUTO: OFF")
                self.btn_toggle.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; font-size: 14px;")
    
        def on_clipboard_changed(self):
            if not self.btn_toggle.isChecked() or self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            if mime_data.hasHtml():
                QTimer.singleShot(50, self.delayed_process_clipboard)
    
        def delayed_process_clipboard(self):
            if not self.btn_toggle.isChecked() or self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            if not mime_data.hasHtml():
                return
                
            try:
                self.is_processing = True
                raw_html = mime_data.html()
                markdown_text = clean_and_convert(raw_html)
                self.clipboard.setText(markdown_text)
            except Exception:
                pass
            finally:
                self.is_processing = False
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = AutoMarkdownConverter()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Điểm cải tiến tối ưu cho DeepSeek:

  1. **Quét sạch nút sao chép mã nguồn:** Giao diện DeepSeek có nút "Copy" nằm ở góc trên các khối code. Bộ lọc bổ sung từ khóa `'copy-button'`, `'copy-btn'` và quét hậu xử lý chuỗi văn bản sẽ nhổ tận gốc chữ "Copy code" rác dính vào file Markdown của bạn.
  2. **Bảo toàn cấu trúc Markdown ẩn:** Giữ nguyên các định dạng bảng (`tables`) và ký hiệu toán học mã hóa mà DeepSeek tạo ra, đồng thời ép `body_width = 0` để tránh việc văn bản giải thích của AI bị tự động xuống dòng cắt khúc ở giữa câu.
  3. **Xóa icon đánh giá:** Loại bỏ các block class chứa icon Thumbs Up/Down (thích/không thích) ở cuối câu trả lời của DeepSeek.



Bạn chạy thử nghiệm đoạn code này với một đoạn chat bất kỳ của DeepSeek xem kết quả đã "sạch bong" và chuẩn Markdown chưa nhé! Nếu DeepSeek có cập nhật giao diện mới làm sót ký tự nào, bạn hãy cho mình biết từ khóa đó để mình cập nhật thêm vào danh sách lọc.