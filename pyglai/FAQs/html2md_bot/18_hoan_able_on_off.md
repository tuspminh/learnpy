Để bổ sung tính năng bật/tắt chế độ tự động, chúng ta sẽ biến đổi giao diện thành một công cụ có thể chuyển đổi linh hoạt. Mình sẽ thiết kế một nút bấm dạng **Toggle Button** (Nút chuyển trạng thái Bật/Tắt).

  * **Khi nút ở trạng thái Bật (ON):** Nút hiển thị màu xanh lá với chữ "AUTO: ON", ứng dụng sẽ tự động lắng nghe và chuyển đổi mỗi khi bạn nhấn `Ctrl + C` trên trình duyệt.
  * **Khi nút ở trạng thái Tắt (OFF):** Nút hiển thị màu xám với chữ "AUTO: OFF", ứng dụng sẽ bỏ qua toàn bộ sự kiện và hoạt động của clipboard trả về bình thường như mặc định của máy tính.



Dưới đây là mã nguồn PySide6 hoàn chỉnh, hoạt động mượt mà bằng phương pháp trì hoãn `QTimer` và tích hợp công tắc thông minh:

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
            
            self.setWindowTitle("MD Switch")
            self.setFixedSize(QSize(200, 80))
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) # Luôn ghim trên cùng
            
            # Biến cờ chặn vòng lặp vô hạn
            self.is_processing = False
            
            # Cấu hình giao diện dạng dọc
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Tạo nút bấm bật tắt dạng Toggle
            self.btn_toggle = QPushButton("AUTO: ON")
            self.btn_toggle.setCheckable(True) # Biến nút bấm thành nút công tắc có 2 trạng thái
            self.btn_toggle.setChecked(True)   # Mặc định mở app lên là BẬT luôn
            self.btn_toggle.clicked.connect(self.on_toggle_clicked)
            
            # Đặt màu sắc ban đầu cho nút (Màu xanh lá cho trạng thái Bật)
            self.btn_toggle.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px;")
            layout.addWidget(self.btn_toggle)
            
            # Cấu hình Clipboard hệ thống của PySide6
            self.clipboard = QApplication.clipboard()
            self.clipboard.dataChanged.connect(self.on_clipboard_changed)
    
        def on_toggle_clicked(self, checked):
            """Hàm xử lý khi nhấn vào nút công tắc để đổi giao diện"""
            if checked:
                self.btn_toggle.setText("AUTO: ON")
                self.btn_toggle.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; font-size: 14px;")
            else:
                self.btn_toggle.setText("AUTO: OFF")
                self.btn_toggle.setStyleSheet("background-color: #95a5a6; color: white; font-weight: bold; font-size: 14px;")
    
        def on_clipboard_changed(self):
            # NẾU CÔNG TẮC ĐANG TẮT (not checked): Dừng ngay lập tức không làm gì cả
            if not self.btn_toggle.isChecked():
                return
                
            # Nếu app đang tự ghi đè, chặn không cho chạy tiếp
            if self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            
            # Chỉ xử lý nếu dữ liệu copy có định dạng HTML (bôi đen từ trình duyệt)
            if mime_data.hasHtml():
                # Trì hoãn 50ms để hệ thống hoàn tất việc ghi nhận HTML gốc, tránh lỗi trống clipboard
                QTimer.singleShot(50, self.delayed_process_clipboard)
    
        def delayed_process_clipboard(self):
            # Kiểm tra lại các điều kiện an toàn
            if not self.btn_toggle.isChecked() or self.is_processing:
                return
                
            mime_data = self.clipboard.mimeData()
            if not mime_data.hasHtml():
                return
                
            try:
                self.is_processing = True # Bật khiên chặn vòng lặp
                
                # Đọc HTML, dọn rác và dịch sang Markdown
                raw_html = mime_data.html()
                markdown_text = clean_and_convert(raw_html)
                
                # Ghi đè vào clipboard dạng text thuần Markdown
                self.clipboard.setText(markdown_text)
                
            except Exception:
                pass
            finally:
                self.is_processing = False # Hạ khiên chặn để chuẩn bị cho lượt Ctrl+C tiếp theo
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = AutoMarkdownConverter()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các điểm nâng cấp tiện lợi của bản này:

  1. **`QPushButton.setCheckable(True)`** : Hàm này biến nút bấm thông thường thành một công tắc giữ trạng thái. Bạn bấm 1 lần nó sẽ lún xuống (Bật), bấm lần nữa nó nảy lên (Tắt).
  2. **Kiểm tra trạng thái thời gian thực (`self.btn_toggle.isChecked()`)**: Ngay đầu sự kiện thay đổi dữ liệu, app sẽ kiểm tra trạng thái nút. Nếu bạn đang Tắt, app sẽ đứng im hoàn toàn, trả lại tính năng `Ctrl + C` và `Ctrl + V` bình thường cho hệ thống Windows của bạn (bạn có thể copy ảnh, file, văn bản thoải mái không sợ bị can thiệp).



Bạn hãy chạy thử nghiệm bản cập nhật nút bấm thông minh này xem đã hoạt động mượt mà và đúng ý bạn muốn chưa nhé! Để tiến xa hơn, bạn có muốn công cụ này **tự động lưu trạng thái Bật/Tắt** của lần dùng cuối, để lần sau mở app lên nó tự nhớ cấu hình cũ không?