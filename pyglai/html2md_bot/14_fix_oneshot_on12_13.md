fix code 12, 13 sau khi thực hiện xong thì thoát luôn.

Đó là do trong hàm xử lý click của nút bấm (`on_click_convert`), mình có chèn thêm lệnh **`self.close()`** ở cuối tiến trình thành công. Mục đích ban đầu là muốn giúp bạn tiết kiệm thao tác tắt ứng dụng bằng tay sau khi đã cập nhật clipboard, nhưng điều này vô tình làm app bị thoát luôn và không thể bấm liên tục nhiều lần được.

Để ứng dụng **luôn mở, ghim trên màn hình và cho phép bạn bấm nút`<Convert>` liên tục nhiều lần**, bạn chỉ cần xóa bỏ lệnh `self.close()` đi là xong.

Dưới đây là đoạn code đã sửa lỗi đó (bỏ lệnh tự tắt app):

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
            
            # Ghim trên cùng (Always on Top)
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
                
                # Phát âm thanh thành công
                win32api.MessageBeep(win32con.MB_OK)
                
                # ĐÃ XÓA dòng self.close() tại đây để app không bị thoát nữa
            else:
                # Phát âm thanh lỗi nếu clipboard không chứa nội dung trang web
                win32api.MessageBeep(win32con.MB_ICONERROR)
    
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = MiniConverterApp()
        window.show()
        sys.exit(app.exec())
    

Hãy thận trọng khi sử dụng mã.

Bây giờ bạn có thể mở app lên, ghim nó ở một góc màn hình, rồi thoải mái lướt web copy ➔ click convert liên tục mà không lo ứng dụng bị tự động đóng nữa.

Bạn hãy chạy thử lại bản này xem đã đúng ý chưa nhé. Nếu bạn muốn đóng gói lại thành file `.exe` bằng **PyInstaller** , bạn hãy chạy lại lệnh cũ:

bash
    
    
    pyinstaller --onefile --noconsole ten_file_cua_ban.py
    

Hãy thận trọng khi sử dụng mã.

Bạn có muốn mình thêm tính năng thay đổi **màu sắc của nút bấm** (ví dụ chuyển sang màu xanh lá khi convert thành công để nhận diện bằng mắt trực quan hơn tiếng bíp) không?

