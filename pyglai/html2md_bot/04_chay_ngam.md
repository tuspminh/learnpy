> đóng gói đoạn code này thành một công cụ chạy ngầm (ví dụ: nhấn một phím tắt Ctrl + Alt + M là tự động chuyển đổi luôn mà không cần mở app Python để chạy thủ công)
>


Version:0.9 StartHTML:00000097 EndHTML:00109686 StartFragment:00000131 EndFragment:00109650 

Để biến đoạn code trên thành một công cụ chạy ngầm và kích hoạt bằng phím tắt `Ctrl + Alt + M`, chúng ta sẽ sử dụng thêm thư viện `keyboard`. Thư viện này giúp lắng nghe các sự kiện phím bấm trên Windows ngay cả khi ứng dụng đang ẩn.

1\. Cài đặt thêm thư viện

Bạn mở Command Prompt và cài đặt thư viện `keyboard`:

bash
    
    
    pip install keyboard
    

Hãy thận trọng khi sử dụng mã.

2\. Đoạn mã Python chạy ngầm hoàn chỉnh

Dưới đây là mã nguồn đã được tích hợp trình lắng nghe phím tắt. Khi chạy, nó sẽ giữ một vòng lặp vô hạn ở chế độ nền để chờ bạn nhấn tổ hợp phím.

python
    
    
    import win32clipboard
    from bs4 import BeautifulSoup
    import html2text
    import keyboard
    import time
    
    def get_clipboard_html():
        """Lấy dữ liệu HTML thô từ Windows Clipboard"""
        win32clipboard.OpenClipboard()
        try:
            html_format = win32clipboard.RegisterClipboardFormat("HTML Format")
            if win32clipboard.IsClipboardFormatAvailable(html_format):
                data_raw = win32clipboard.GetClipboardData(html_format)
                return data_raw.decode('utf-8', errors='ignore')
            return None
        except Exception as e:
            return None
        finally:
            win32clipboard.CloseClipboard()
    
    def set_clipboard_text(text):
        """Ghi đè đoạn Markdown vào Windows Clipboard"""
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        except Exception as e:
            print(f"Lỗi ghi clipboard: {e}")
        finally:
            win32clipboard.CloseClipboard()
    
    def html_to_markdown(html_raw):
        """Lọc và chuyển đổi nội dung sang Markdown"""
        soup = BeautifulSoup(html_raw, 'html.parser')
        converter = html2text.HTML2Text()
        converter.bypass_tables = False
        converter.ignore_links = False
        converter.ignore_emphasis = False
        converter.body_width = 0
        return converter.handle(str(soup)).strip()
    
    def process_clipboard():
        """Hàm xử lý chính khi bấm phím tắt"""
        # Chờ một chút để hệ điều hành nhả phím, tránh xung đột dữ liệu
        time.sleep(0.1)
        
        raw_html = get_clipboard_html()
        if raw_html:
            markdown_text = html_to_markdown(raw_html)
            set_clipboard_text(markdown_text)
            print("➔ Đã chuyển đổi thành công sang Markdown!")
        else:
            print("➔ Không tìm thấy dữ liệu HTML trong clipboard.")
    
    if __name__ == "__main__":
        # Đăng ký phím tắt Ctrl + Alt + M
        # Khi nhấn tổ hợp phím này, hàm process_clipboard sẽ được gọi
        keyboard.add_hotkey('ctrl+alt+m', process_clipboard)
        
        print("Công cụ đang chạy ngầm... Hãy nhấn Ctrl + Alt + M để chuyển đổi clipboard.")
        print("Nhấn Ctrl + C tại cửa sổ dòng lệnh này để thoát.")
        
        # Giữ chương trình luôn chạy ngầm để lắng nghe phím tắt
        keyboard.wait()
    

Hãy thận trọng khi sử dụng mã.

3\. Cách chạy ẩn hoàn toàn không hiện cửa sổ Đen (CMD)

Nếu bạn không muốn nhìn thấy cửa sổ dòng lệnh (CMD) hiện lên khi công cụ này đang chạy, hãy làm theo 2 cách sau:

  * **Cách tạm thời (Đổi đuôi file):** Đổi tên file từ `script.py` thành `script.pyw`. Khi bạn double-click vào file `.pyw`, Windows sẽ chạy nó ngầm bằng tiến trình `pythonw.exe` mà không mở cửa sổ CMD.
  * **Cách cố định (Chạy cùng Windows):** Nếu muốn máy tính vừa bật lên là tính năng này tự hoạt động:
    1. Nhấn `Windows + R`, gõ `shell:startup` rồi nhấn Enter. Cửa sổ thư mục `Startup` của Windows sẽ hiện ra.
    2. Tạo một Shortcut của file `script.pyw` nêu trên và ném vào thư mục này.



Bạn đã chạy thử và phím tắt hoạt động mượt mà trên máy chưa? Nếu bạn muốn đóng gói nó thành một file độc lập dạng `.exe` để đem sang máy khác dùng mà không cần cài Python, hãy báo mình để mình hướng dẫn dùng **PyInstaller** nhé!

