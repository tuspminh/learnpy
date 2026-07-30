Để chuyển đổi công cụ này sang giao diện đồ họa (GUI) trực quan bằng **PySide6** , chúng ta sẽ thiết kế một cửa sổ gồm một nút bấm **Get Clipboard** ở phía trên và một khung nhập liệu **Plain Text Editor** lớn ở phía dưới.

Khi bấm nút, chương trình sẽ tự động lấy dữ liệu HTML từ clipboard, xử lý lọc bỏ Meta/Quảng cáo, chuyển sang Markdown và hiển thị thẳng lên khung Text Editor để bạn chỉnh sửa hoặc copy nhanh.

1\. Cài đặt PySide6

Nếu chưa cài đặt thư viện đồ họa này, bạn hãy mở Command Prompt lên và chạy lệnh:

bash
    
    
    pip install PySide6
    

Hãy thận trọng khi sử dụng mã.

2\. Đoạn mã Python hoàn chỉnh với giao diện PySide6

Bạn lưu đoạn code dưới đây thành một file mới (ví dụ: `gui_html_to_md.py`) và chạy:

python
    
    
    import sys
    import time
    import win32clipboard
    import win32api
    import win32con
    from bs4 import BeautifulSoup
    import html2text
    
    # Import các thành phần giao diện từ PySide6
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit
    from PySide6.QtCore import QSize
    
    def get_clipboard_html():
        win32clipboard.OpenClipboard()
        try:
            html_format = win32clipboard.RegisterClipboardFormat("HTML Format")
            if win32clipboard.IsClipboardFormatAvailable(html_format):
                data_raw = win32clipboard.GetClipboardData(html_format)
                return data_raw.decode('utf-8', errors='ignore')
            return None
        except Exception:
            return None
        finally:
            win32clipboard.CloseClipboard()
    
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
    
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("HTML to Markdown Converter")
            self.setMinimumSize(QSize(600, 400)) # Định kích thước tối thiểu cho cửa sổ
            
            # Tạo widget tổng và cấu hình Layout dạng dọc (Vertical Layout)
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # 1. Tạo nút bấm <getCB>
            self.btn_get_cb = QPushButton("Get Clipboard")
            # Kết nối sự kiện Click của nút bấm tới hàm xử lý
            self.btn_get_cb.clicked.connect(self.on_click_get_cb)
            layout.addWidget(self.btn_get_cb)
            
            # 2. Tạo khung hiển thị văn bản plain text editor
            self.text_editor = QPlainTextEdit()
            self.text_editor.setPlaceholderText("Nội dung Markdown sau khi chuyển đổi sẽ hiển thị tại đây...")
            layout.addWidget(self.text_editor)
    
        def on_click_get_cb(self):
            """Hàm xử lý khi người dùng nhấn nút Get Clipboard"""
            raw_html = get_clipboard_html()
            
            if raw_html:
                # Tiến hành chuyển đổi
                markdown_text = clean_and_convert(raw_html)
                
                # Cập nhật (update) nội dung vào khung text plain editor
                self.text_editor.setPlainText(markdown_text)
                
                # Phát âm thanh thành công
                win32api.MessageBeep(win32con.MB_OK)
            else:
                self.text_editor.setPlainText("Không tìm thấy dữ liệu HTML trong Clipboard. Hãy copy lại từ trình duyệt!")
                # Phát âm thanh cảnh báo lỗi
                win32api.MessageBeep(win32con.MB_ICONERROR)
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Các ưu điểm khi đổi sang giao diện PySide6 này:

  * **Không cần quyền Admin:** Vì chúng ta đã bỏ thư viện `keyboard` (lắng nghe phím bấm toàn hệ thống), ứng dụng GUI này chạy bình thường như mọi phần mềm khác mà không bao giờ bị Windows chặn hay đòi quyền Administrator.
  * **Xem trước nội dung tiện lợi:** Bạn có thể nhìn thấy ngay kết quả chuyển đổi để kiểm tra xem cấu trúc Markdown có bị lệch dòng hay thiếu thành phần nào không trước khi copy sang công cụ khác.



Cách đóng gói sang file .exe cho ứng dụng GUI:

Khi đóng gói ứng dụng có giao diện đồ họa, bạn chỉ cần bỏ tham số `--uac-admin` đi. Hãy mở CMD tại thư mục chứa file và gõ:

bash
    
    
    pyinstaller --onefile --noconsole gui_html_to_md.py
    

Hãy thận trọng khi sử dụng mã.

_(Tham số`--noconsole` vẫn được giữ lại để khi bạn mở file `.exe`, nó chỉ hiển thị duy nhất giao diện app PySide6 mà không kèm theo cửa sổ CMD đen thui đằng sau)._

Bạn có muốn mình bổ sung thêm một nút ****bên cạnh nút cũ để khi bạn chỉnh sửa xong trong ô text box là có thể copy ngược lại ngay lập tức không?

