> html2md , set to clipboard again

Version:0.9 StartHTML:00000097 EndHTML:00092561 StartFragment:00000131 EndFragment:00092525 

Để tự động nạp ngược đoạn Markdown vừa chuyển đổi vào lại Clipboard, bạn cần dùng lại chính thư viện `win32clipboard` để ghi đè dữ liệu.

Tuy nhiên, vì mục tiêu là dán sang các ứng dụng hỗ trợ Markdown (như Notion, Obsidian, GitHub, hay VS Code), chúng ta sẽ nạp dữ liệu này dưới dạng **Text thuần** (`CF_UNICODETEXT`). Như vậy, khi bạn nhấn `Ctrl + V`, ứng dụng sẽ nhận ngay đoạn code Markdown chuẩn.

Dưới đây là mã nguồn hoàn chỉnh đã tích hợp tính năng **Đọc HTML ➔ Chuyển Markdown ➔ Ghi đè vào Clipboard** :

python
    
    
    import win32clipboard
    from bs4 import BeautifulSoup
    import html2text
    
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
            print(f"Lỗi đọc clipboard: {e}")
            return None
        finally:
            win32clipboard.CloseClipboard()
    
    def set_clipboard_text(text):
        """Ghi đè đoạn Markdown (Text thuần) vào Windows Clipboard"""
        win32clipboard.OpenClipboard()
        try:
            # Xóa toàn bộ dữ liệu cũ đang có trong clipboard
            win32clipboard.EmptyClipboard()
            # Nạp dữ liệu mới dưới dạng Text thuần Unicode
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            print("➔ Đã nạp thành công đoạn Markdown vào Clipboard!")
        except Exception as e:
            print(f"Lỗi ghi clipboard: {e}")
        finally:
            win32clipboard.CloseClipboard()
    
    def html_to_markdown(html_raw):
        """Lọc header Windows và chuyển đổi nội dung sang Markdown"""
        soup = BeautifulSoup(html_raw, 'html.parser')
        
        # Cấu hình html2text
        converter = html2text.HTML2Text()
        converter.bypass_tables = False   # Giữ lại bảng dữ liệu
        converter.ignore_links = False    # Giữ lại link
        converter.ignore_emphasis = False  # Giữ lại chữ đậm/nghiêng
        converter.body_width = 0          # Không tự động xuống dòng ngắt quãng
    
        return converter.handle(str(soup)).strip()
    
    if __name__ == "__main__":
        # Bước 1: Đọc dữ liệu HTML từ clipboard (khi bạn vừa copy trên web)
        raw_html = get_clipboard_html()
        
        if raw_html:
            # Bước 2: Chuyển đổi sang Markdown
            markdown_text = html_to_markdown(raw_html)
            
            print("\n--- NỘI DUNG MARKDOWN ĐÃ CHUYỂN ĐỔI ---")
            print(markdown_text)
            print("---------------------------------------\n")
            
            # Bước 3: Ghi ngược dữ liệu Markdown vào clipboard
            set_clipboard_text(markdown_text)
            print("Bây giờ bạn có thể nhấn Ctrl + V để dán Markdown vào Notion/Obsidian/VS Code.")
        else:
            print("Không tìm thấy dữ liệu HTML. Hãy bôi đen và copy lại từ trình duyệt!")
    

Hãy thận trọng khi sử dụng mã.

Quy trình sử dụng sau khi chạy code:

  1. Bạn vào trình duyệt, bôi đen đoạn văn bản có tiêu đề, link hoặc code rồi bấm `Ctrl + C`.
  2. Chạy file Python này.
  3. Vào ứng dụng ghi chú của bạn (Obsidian, Notion, Notion, Slack...) và bấm `Ctrl + V` là xong.



Bạn có cần mình đóng gói đoạn code này thành một công cụ chạy ngầm (ví dụ: nhấn một phím tắt `Ctrl + Alt + M` là tự động chuyển đổi luôn mà không cần mở app Python để chạy thủ công) không?

