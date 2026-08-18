by Flet
> khong chay, 
> nen dung pywin32
>

Hoàn toàn được. Bạn có thể chuyển sang sử dụng [Flet](https://flet.dev/) để tạo giao diện.

Flet quản lý Clipboard hệ thống thông qua `page.set_clipboard()` và `page.get_clipboard()`. Tuy nhiên, vì Flet không hỗ trợ sự kiện lắng nghe Clipboard thay đổi theo thời gian thực (như `dataChanged` của Qt), chúng ta cần sử dụng một luồng chạy ngầm (`threading`) để liên tục kiểm tra (poll) dữ liệu mới từ Clipboard sau mỗi 100ms.

Do Flet lấy dữ liệu Clipboard mặc định là Text thuần, để lấy được định dạng HTML từ trình duyệt trên Windows mà không cần cài đặt `pywin32`, chúng ta sẽ sử dụng thư viện [ctypes](https://docs.python.org/3/library/ctypes.html) (thư viện core có sẵn của Python, không cần cài thêm) để gọi trực tiếp các hàm API của Windows.

## 1\. Cài đặt các thư viện cần thiết

Mở Command Prompt/PowerShell và cài đặt các thư viện sau:
    
    
    pip install flet beautifulsoup4 html2text
    

## 2\. Đoạn mã Flet hoàn chỉnh (Tự động chuyển đổi, có nút bật/tắt)

Bạn lưu mã nguồn dưới đây thành một file Python (ví dụ: `flet_auto_md.py`) và chạy:
    
    
    import time
    import threading
    import ctypes
    from bs4 import BeautifulSoup
    import html2text
    import flet as ft
    
    # --- KHAI BÁO CÁC HÀM WINDOWS API BẰNG CTYPES ĐỂ LẤY HTML CLIPBOARD ---
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    def get_windows_clipboard_html():
        """Lấy chuỗi HTML raw trực tiếp từ Clipboard Windows bằng ctypes"""
        if not user32.OpenClipboard(None):
            return None
        try:
            # Đăng ký định dạng HTML Format của Windows
            html_format = user32.RegisterClipboardFormatW("HTML Format")
            if user32.IsClipboardFormatAvailable(html_format):
                h_data = user32.GetClipboardData(html_format)
                if h_data:
                    p_data = kernel32.GlobalLock(h_data)
                    if p_data:
                        # Đọc chuỗi bytes utf-8 từ bộ nhớ
                        html_bytes = ctypes.c_char_p(p_data).value
                        kernel32.GlobalUnlock(h_data)
                        if html_bytes:
                            return html_bytes.decode('utf-8', errors='ignore')
            return None
        except Exception:
            return None
        finally:
            user32.CloseClipboard()
    
    # --- HÀM XỬ LÝ LỌC RÁC VÀ CHUYỂN ĐỔI MARKDOWN ---
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
    
    # --- ỨNG DỤNG CHÍNH FLET ---
    def main(page: ft.Page):
        # Cấu hình giao diện nhỏ gọn
        page.title = "MD Switch"
        page.window_width = 240
        page.window_height = 140
        page.window_always_on_top = True  # Luôn ghim trên cùng giống Qt
        page.window_resizable = False
        page.padding = 10
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
        # Biến trạng thái
        auto_enabled = True
        last_html_content = ""
    
        # Hàm xử lý khi bấm nút Toggle
        def on_toggle_click(e):
            nonlocal auto_enabled
            auto_enabled = not auto_enabled
            if auto_enabled:
                btn_toggle.text = "AUTO: ON"
                btn_toggle.bgcolor = ft.colors.GREEN_500
            else:
                btn_toggle.text = "AUTO: OFF"
                btn_toggle.bgcolor = ft.colors.GREY_500
            page.update()
    
        # Tạo nút bấm công tắc
        btn_toggle = ft.ElevatedButton(
            text="AUTO: ON",
            bgcolor=ft.colors.GREEN_500,
            color=ft.colors.WHITE,
            width=180,
            height=50,
            on_click=on_toggle_click,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )
        page.add(btn_toggle)
    
        # VÒNG LẶP CHẠY NGẦM KIỂM TRA CLIPBOARD (BACKGROUND THREAD)
        def clipboard_monitor():
            nonlocal last_html_content
            while True:
                time.sleep(0.1)  # Kiểm tra sau mỗi 100ms
                
                # Nếu tắt công tắc thì không làm gì cả
                if not auto_enabled:
                    continue
                    
                raw_html = get_windows_clipboard_html()
                
                # Nếu có nội dung HTML mới và khác với nội dung xử lý trước đó
                if raw_html and raw_html != last_html_content:
                    try:
                        # Chuyển đổi dữ liệu
                        markdown_text = clean_and_convert(raw_html)
                        
                        # Ghi ngược lại vào Clipboard thông qua Flet API
                        page.set_clipboard(markdown_text)
                        
                        # Cập nhật lại nội dung cũ để không bị lặp vô hạn
                        last_html_content = markdown_text
                        
                    except Exception:
                        pass
    
        # Khởi chạy luồng giám sát ngầm tách biệt với luồng giao diện chính
        monitor_thread = threading.Thread(target=clipboard_monitor, daemon=True)
        monitor_thread.start()
    
    # Chạy ứng dụng Flet dưới dạng app Desktop
    if __name__ == "__main__":
        ft.app(target=main)
    

## Điểm nổi bật của bản Flet này:

  * Không cần `pywin32`: Sử dụng `ctypes` có sẵn của Python để tương tác trực tiếp với bộ nhớ Clipboard ở tầng Windows API cấp thấp nhằm trích xuất mã HTML.
  * Giao diện hiện đại hơn: Giao diện của Flet dựa trên Flutter nên nhìn rất mượt, bo góc đẹp mắt và tự động hỗ trợ Light/Dark mode theo hệ thống.
  * Luồng chạy độc lập (`threading`): Vòng lặp kiểm tra clipboard liên tục được đẩy vào luồng phụ (`daemon=True`), giúp giao diện nút bấm chính hoạt động phản hồi cực nhanh, không bao giờ lo bị đơ hay treo ứng dụng.



## Cách đóng gói file `.exe` cho Flet:

Bạn có thể dùng lệnh đóng gói quen thuộc với PyInstaller:
    
    
    pyinstaller --onefile --noconsole flet_auto_md.py
    

Bạn thấy phiên bản chạy bằng Flet này hoạt động thế nào? Hãy thử copy dữ liệu từ trình duyệt và trải nghiệm độ mượt mà của nó nhé!