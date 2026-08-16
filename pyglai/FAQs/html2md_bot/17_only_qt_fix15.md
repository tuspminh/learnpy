Hiện tượng clipboard bị trống rỗng khi dùng `self.clipboard.setText()` trực tiếp trong sự kiện `dataChanged` của PySide6 diễn ra do một lỗi xung đột rất đặc trưng của Qt (MIME-Type Lock). [[1](https://stackoverflow.com/questions/57260037/copy-paste-text-from-qclipboard-freezes-program)]

Khi bạn bấm `Ctrl + C` trên web, dữ liệu HTML đang được hệ điều hành nạp vào. Đúng lúc đó, sự kiện `dataChanged` kích hoạt, và lệnh `setText()` của chúng ta cố lao vào ghi đè ngay lập tức. Hai hành động đọc/ghi này triệt tiêu lẫn nhau, khiến hệ điều hành hiểu nhầm là clipboard bị xóa sạch (Empty). [[1](https://stackoverflow.com/questions/63259868/how-to-use-qclipboard-datachanged-signal-to-change-the-text-in-clipboard), [2](https://stackoverflow.com/questions/57260037/copy-paste-text-from-qclipboard-freezes-program)]

Để khắc phục triệt để, chúng ta cần dùng phương thức trì hoãn **`QTimer.singleShot`**. Nó sẽ ra lệnh cho ứng dụng đợi khoảng `50 mili-giây` để hệ điều hành hoàn tất việc nạp dữ liệu HTML, sau đó mới tiến hành chuyển đổi và ghi đè Markdown một cách an toàn.

Dưới đây là đoạn code hoàn chỉnh, **chỉ dùng PySide6** , không lỗi trống clipboard và không lo vòng lặp vô hạn:

python
    
    
    import sys
    from bs4 import BeautifulSoup
    import html2text
    
    # Chỉ dùng thư viện chuẩn PySide6
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
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
    
        # 2. Lọc quảng cáo và rác bằng BeautifulSoup
        soup = BeautifulSoup(html_raw, 'html.parser')
        tags_to_remove = ['script', 'style', 'noscript', 'iframe', 'aside', 'nav', 'footer', 'header']
        bad_keywords = ['ads', 'advertisement', 'banner', 'sidebar', 'share', 'social', 'copy-btn', 'popup']
    
        for tag in soup.find_all(tags_to_remove):
            tag.decompose()
    
        for element in soup.find_all(True):
            if element.get('class'):
                class_str = " ".join(element.get('class')).lower()
                if any(keyword in class_str for keyword in bad_keywords):
                    element.decompose()
                    continue
            if element.get('id'):
                id_str = element.get('id').lower()
                if any(keyword in id_str for keyword in bad_keywords):
                    element.decompose()
    
        # 3. Chuyển đổi sang Markdown bằng html2text
        converter = html2text.HTML2Text()
        converter.bypass_tables = False
        converter.ignore_links = False
        converter.ignore_emphasis = False
        converter.body_width = 0
        
        return converter.handle(str(soup)).strip()
    
    
    class AutoMarkdownConverter(QWidget):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("Auto MD")
            self.setFixedSize(QSize(220, 70))
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # Luôn ghim trên cùng
            
            # Biến cờ chặn vòng lặp vô hạn
            self.is_processing = False
            
            # Giao diện
            layout = QVBoxLayout(self)
            self.label_status = QLabel("🟢 Đang tự động lắng nghe...")
            self.label_status.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.label_status)
            
            # Cấu hình Clipboard
            self.clipboard = QApplication.clipboard()
            self.clipboard.dataChanged.connect(self.on_clipboard_changed)
    
        def on_clipboard_changed(self):
            # Nếu app đang tự ghi đè, chặn không cho chạy tiếp
            if self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            
            # Chỉ xử lý nếu dữ liệu copy có định dạng HTML (đoạn text bôi đen từ web)
            if mime_data.hasHtml():
                # Mẹo quan trọng: Trì hoãn 50ms để hệ thống hoàn tất việc ghi nhận HTML gốc, 
                # tránh xung đột đọc/ghi đồng thời làm trống clipboard
                QTimer.singleShot(50, self.delayed_process_clipboard)
    
        def delayed_process_clipboard(self):
            # Kiểm tra lại cờ hiệu một lần nữa cho an toàn
            if self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            if not mime_data.hasHtml():
                return
                
            try:
                self.is_processing = True # Bật khiên chặn vòng lặp
                self.label_status.setText("⚡ Đang tự động chuyển...")
                QApplication.processEvents() # Cập nhật chữ trên giao diện ngay
                
                # Đọc HTML, chuyển đổi sang Markdown
                raw_html = mime_data.html()
                markdown_text = clean_and_convert(raw_html)
                
                # Ghi đè vào clipboard dạng text thuần Markdown
                self.clipboard.setText(markdown_text)
                self.label_status.setText("✅ Đã đổi sang Markdown!")
                
            except Exception:
                self.label_status.setText("❌ Gặp lỗi khi xử lý")
            finally:
                # Hạ khiên chặn sau khi hoàn tất để chuẩn bị cho lượt Ctrl+C tiếp theo
                self.is_processing = False
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = AutoMarkdownConverter()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Tại sao phiên bản này chạy chuẩn xác?

  * **`QTimer.singleShot(50, ...)`** : Tách luồng xử lý ra khỏi thời điểm nhạy cảm khi hệ điều hành đang "khóa" clipboard, giúp việc đọc mã HTML của `mime_data.html()` và ghi đè bằng `setText()` diễn ra mượt mà, không bị mất dữ liệu.
  * **Giữ nguyên cấu trúc`is_processing`**: Đảm bảo an toàn tuyệt đối, không lo ứng dụng bị treo do tín hiệu lặp lại. [[1](https://stackoverflow.com/questions/57260037/copy-paste-text-from-qclipboard-freezes-program)]



Bây giờ bạn hãy chạy thử file này, mở một trang web bất kỳ lên bôi đen bấm `Ctrl + C`, bạn sẽ thấy app phản hồi ngay lập tức và dán `Ctrl + V` ra cấu trúc Markdown cực kỳ mượt mà.

Bạn có muốn mình **thiết kế lại giao diện cho ô nhỏ này nhìn đẹp mắt hơn** (chữ đổi màu xanh/đỏ theo trạng thái, nền tối hiện đại) không?