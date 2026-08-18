Để loại bỏ các thành phần không mong muốn như quảng cáo, menu điều hướng, hoặc các nút "Copy" rác thường chèn vào giữa bài viết trước khi dịch sang Markdown, chúng ta **bắt buộc phải mang BeautifulSoup quay trở lại**.

`html2text` không có khả năng phân biệt đâu là nội dung bài viết, đâu là quảng cáo. Nó sẽ dịch tất cả. Nhưng `BeautifulSoup` thì làm được điều đó nhờ vào việc quét các thuộc tính như `class`, `id`, hoặc các thẻ (`<aside>`, `<nav>`, `<script>`).

Dưới đây là đoạn code hoàn chỉnh sử dụng `BeautifulSoup` để **chủ động "bóc" và xóa sạch quảng cáo** trước khi truyền phần HTML sạch vào cho `html2text`:

python
    
    
    import win32clipboard
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
        # 1. Khởi tạo BeautifulSoup để phân tích cú pháp HTML
        soup = BeautifulSoup(html_raw, 'html.parser')
        
        # 2. ĐỊNH NGHĨA BỘ LỌC QUẢNG CÁO VÀ RÁC
        # Danh sách các thẻ thường chứa quảng cáo hoặc nội dung thừa trên các trang web
        tags_to_remove = ['script', 'style', 'noscript', 'iframe', 'aside', 'nav', 'footer', 'header']
        
        # Danh sách các từ khóa thường nằm trong tên Class hoặc ID của quảng cáo, nút bấm thừa
        bad_keywords = ['ads', 'advertisement', 'banner', 'sidebar', 'share', 'social', 'copy-btn', 'popup']
    
        # 3. TIẾN HÀNH XÓA BỎ BẰNG BEAUTIFULSOUP
        # Xóa theo tên thẻ
        for tag in soup.find_all(tags_to_remove):
            tag.decompose()  # Lệnh decompose() sẽ xóa hoàn toàn thẻ đó khỏi cây HTML
    
        # Xóa theo Class hoặc ID có chứa từ khóa quảng cáo
        for element in soup.find_all(True):  # Duyệt qua tất cả các thẻ
            # Kiểm tra class của thẻ
            if element.get('class'):
                class_str = " ".join(element.get('class')).lower()
                if any(keyword in class_str for keyword in bad_keywords):
                    element.decompose()
                    continue  # Bỏ qua không cần check ID nếu đã xóa bằng Class
                    
            # Kiểm tra ID của thẻ
            if element.get('id'):
                id_str = element.get('id').lower()
                if any(keyword in id_str for keyword in bad_keywords):
                    element.decompose()
    
        # 4. CHUYỂN ĐỔI SANG MARKDOWN
        # Lúc này soup đã hoàn toàn sạch bóng quảng cáo, ta lấy chuỗi HTML còn lại đưa vào html2text
        converter = html2text.HTML2Text()
        converter.bypass_tables = False
        converter.ignore_links = False
        converter.ignore_emphasis = False
        converter.body_width = 0
        
        return converter.handle(str(soup)).strip()
    
    def process_clipboard():
        time.sleep(0.1)
        raw_html = get_clipboard_html()
        
        if raw_html:
            # Gọi hàm dọn rác và chuyển đổi
            markdown_text = clean_and_convert(raw_html)
            set_clipboard_text(markdown_text)
            print("➔ Đã lọc sạch quảng cáo và chuyển đổi sang Markdown!")
        else:
            print("➔ Không tìm thấy dữ liệu HTML.")
    
    if __name__ == "__main__":
        keyboard.add_hotkey('ctrl+alt+m', process_clipboard)
        print("Công cụ chặn quảng cáo đang chạy... Nhấn Ctrl + Alt + M để xử lý.")
        keyboard.wait()
    

Hãy thận trọng khi sử dụng mã.

Giải thích cơ chế lọc của BeautifulSoup:

  * **`tag.decompose()`** : Đây là vũ khí chính. Khi phát hiện ra một thẻ `<div class="ads-banner">`, câu lệnh này sẽ nhổ tận gốc toàn bộ thẻ đó và các thẻ con nằm bên trong nó ra khỏi dữ liệu.
  * **`bad_keywords`** : Bạn có thể tự do thêm các từ khóa khác vào danh sách này nếu bạn phát hiện ra một trang web cụ thể nào đó hay chèn các đoạn text thừa (ví dụ nếu trang web hay có nút `Sao chép`, bạn có thể thêm từ `'copy'` hoặc `'btn'` vào để xóa sạch các nút bấm đó trước khi đổi sang Markdown).



Bạn có muốn bổ sung thêm tính năng **phát âm thanh (Tiếng Bíp nhẹ)** của Windows mỗi khi bấm phím tắt thành công để biết chương trình đã xử lý xong mà không cần nhìn màn hình không?

