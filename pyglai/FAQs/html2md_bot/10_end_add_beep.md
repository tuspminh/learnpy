Để thêm tiếng bíp báo hiệu khi chương trình xử lý thành công, chúng ta sẽ sử dụng hàm `MessageBeep` từ thư viện `win32api` (đi kèm sẵn trong gói `pywin32` mà bạn đã cài đặt).

Hàm này sẽ gọi âm thanh thông báo chuẩn của hệ thống Windows (tiếng bíp nhẹ), giúp bạn nhận biết ngay khi clipboard đã được chuyển đổi xong mà không cần phải mở bất kỳ cửa sổ nào để kiểm tra.

Dưới đây là mã nguồn hoàn chỉnh cuối cùng, sẵn sàng để bạn chạy thử hoặc đóng gói thành file `.exe`:

python
    
    
    import win32clipboard
    import win32api
    import win32con
    from bs4 import BeautifulSoup
    import html2text
    import keyboard
    import time
    
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
        # 1. LOẠI BỎ ĐOẠN META CỦA WINDOWS CLIPBOARD
        lower_html = html_raw.lower()
        start_idx = lower_html.find("<html")
        
        if start_idx == -1:
            fragment_idx = lower_html.find("endfragment:")
            if fragment_idx != -1:
                start_idx = html_raw.find("<", fragment_idx)
                
        if start_idx != -1:
            html_raw = html_raw[start_idx:]
    
        # 2. LỌC QUẢNG CÁO VÀ RÁC BẰNG BEAUTIFULSOUP
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
    
        # 3. CHUYỂN ĐỔI SANG MARKDOWN
        converter = html2text.HTML2Text()
        converter.bypass_tables = False
        converter.ignore_links = False
        converter.ignore_emphasis = False
        converter.body_width = 0
        
        return converter.handle(str(soup)).strip()
    
    def process_clipboard():
        # Chờ nhẹ để tránh xung đột phím bấm hệ thống
        time.sleep(0.1)
        raw_html = get_clipboard_html()
        
        if raw_html:
            markdown_text = clean_and_convert(raw_html)
            set_clipboard_text(markdown_text)
            print("➔ Đã chuyển đổi sang Markdown thành công!")
            
            # PHÁT TIẾNG BÍP THÔNG BÁO CỦA WINDOWS
            # MB_OK là âm thanh thông báo chuẩn mặc định của Windows
            win32api.MessageBeep(win32con.MB_OK)
        else:
            print("➔ Không tìm thấy dữ liệu HTML.")
            # Nếu lỗi hoặc không có dữ liệu, phát âm thanh cảnh báo (tiếng bíp trầm hơn)
            win32api.MessageBeep(win32con.MB_ICONERROR)
    
    if __name__ == "__main__":
        keyboard.add_hotkey('ctrl+alt+m', process_clipboard)
        print("Công cụ hoàn chỉnh đang chạy... Nhấn Ctrl + Alt + M để thực hiện.")
        keyboard.wait()
    

Hãy thận trọng khi sử dụng mã.

Hướng dẫn đóng gói lại lần cuối:

Bây giờ bạn có thể mở CMD và chạy lại lệnh đóng gói để cập nhật file `.exe` mới nhất có cả tính năng dọn meta và phát tiếng bíp:

bash
    
    
    pyinstaller --onefile --noconsole --uac-admin ten_file_cua_ban.py
    

Hãy thận trọng khi sử dụng mã.

Khi công cụ này chạy ẩn, quy trình dùng sẽ cực kỳ tiện lợi: **Bôi đen copy trên web ➔ Nhấn`Ctrl + Alt + M` ➔ Nghe tiếng "Ting" nhẹ từ máy tính ➔ Nhấn `Ctrl + V` vào Notion/Obsidian.**

Nếu bạn muốn thay đổi tổ hợp phím tắt khác (ví dụ: đổi sang phím dễ bấm hơn) hoặc gặp bất kỳ lỗi nào khi chạy ngầm, hãy cho mình biết nhé!

