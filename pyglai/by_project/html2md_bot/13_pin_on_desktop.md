Để ghim cửa sổ ứng dụng luôn nằm trên cùng (Always on Top) trong PySide6, bạn chỉ cần bổ sung thêm cờ cấu hình hệ thống `Qt.WindowStaysOnTopHint` vào thuộc tính Window Flags của widget lúc khởi tạo.

Dưới đây là mã nguồn hoàn chỉnh đã được tích hợp tính năng ghim trên cùng:

python
    
    
    import sys
    import time
    import win32clipboard
    import win32api
    import win32con
    from bs4 import BeautifulSoup
    import html2text
    
    # Import các thành phần giao diện từ PySide6
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
    from PySide6.QtCore import QSize, Qt
    
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
    
    def set_clipboard_text(text):
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        except Exception:
            pass
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
    
    
    class MiniConverterApp(QWidget):
        def __init__(self):
            super().__init__()
            
            self.setWindowTitle("MD Converter")
            self.setFixedSize(QSize(200, 80)) # Cửa sổ siêu nhỏ, vừa khít nút bấm
            
            # --- KÍCH HOẠT TÍNH NĂNG GHIM TRÊN CÙNG (ALWAYS ON TOP) ---
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            
            # Cấu hình giao diện dạng dọc
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            
            # Tạo nút bấm duy nhất <Convert>
            self.btn_convert = QPushButton("Convert")
            self.btn_convert.clicked.connect(self.on_click_convert)
            layout.addWidget(self.btn_convert)
    
        def on_click_convert(self):
            raw_html = get_clipboard_html()
            
            if raw_html:
                # Xử lý và ghi đè thẳng vào Clipboard dưới dạng text thuần Markdown
                markdown_text = clean_and_convert(raw_html)
                set_clipboard_text(markdown_text)
                
                # Phát âm thanh thành công và tắt app luôn để đỡ tốn công tắt thủ công
                win32api.MessageBeep(win32con.MB_OK)
                self.close() 
            else:
                # Phát âm thanh lỗi nếu clipboard không chứa nội dung trang web
                win32api.MessageBeep(win32con.MB_ICONERROR)
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MiniConverterApp()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Lệnh đóng gói sang file .exe bằng PyInstaller:

Bạn mở Command Prompt (CMD) tại thư mục chứa file code và chạy lại lệnh:

bash
    
    
    pyinstaller --onefile --noconsole ten_file_cua_ban.py
    

Hãy thận trọng khi sử dụng mã.

Bây giờ khi mở ứng dụng lên, chiếc nút nhỏ này sẽ kiên trì nằm trên mọi cửa sổ trình duyệt hay ứng dụng ghi chú của bạn, giúp bạn click nhanh mà không sợ bị che khuất.

Nếu bạn muốn tùy biến thêm giao diện (ví dụ: làm **nút bấm to hơn** , đổi **màu sắc giao diện cho đẹp** hay **thêm phím tắt tắt nhanh ứng dụng** bằng nút `Esc`), hãy cho mình biết nhé!

