# Khóa học `win32clipboard` Deep Dive

# Buổi 7: HTML Clipboard Deep Dive (CF_HTML)

> Đây là một chủ đề cực kỳ thú vị và cũng là một trong những định dạng Clipboard ít được biết đến nhất.

Hầu hết mọi người nghĩ rằng khi nhấn **Ctrl+C** trên một trang web thì Clipboard chỉ chứa văn bản.

Thực tế hoàn toàn khác.

Nếu bạn copy từ:

  * Chrome 
  * Edge 
  * Firefox 
  * Microsoft Word 
  * Outlook 
  * VS Code 
  * Notion 
  * ChatGPT (Web) 



Clipboard thường sẽ chứa đồng thời:
    
    
    CF_UNICODETEXT
    HTML Format
    Rich Text Format
    CF_LOCALE
    ...

Đây chính là lý do khi bạn dán vào Word, định dạng (màu sắc, in đậm, bảng, liên kết...) vẫn được giữ nguyên.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * HTML Clipboard Format là gì 
  * Cấu trúc chuẩn của `CF_HTML`
  * Header của HTML Clipboard 
  * `StartHTML`
  * `EndHTML`
  * `StartFragment`
  * `EndFragment`
  * Tạo HTML Clipboard bằng Python 
  * Đọc HTML Clipboard 
  * Viết HTML Clipboard Manager 



* * *

# 1\. HTML Clipboard là gì?

Windows **không có** hằng số:
    
    
    CF_HTML

Đây là **Custom Clipboard Format**.

Muốn sử dụng phải đăng ký:
    
    
    import win32clipboard
    
    CF_HTML = win32clipboard.RegisterClipboardFormat(
        "HTML Format"
    )
    
    print(CF_HTML)

Ví dụ:
    
    
    49345

Mỗi máy có thể trả về ID khác nhau, vì đây là định dạng tùy chỉnh được đăng ký lúc chạy.

* * *

# 2\. Kiểm tra HTML
    
    
    import win32clipboard
    
    CF_HTML = win32clipboard.RegisterClipboardFormat(
        "HTML Format"
    )
    
    win32clipboard.OpenClipboard()
    
    try:
    
        print(
            win32clipboard.IsClipboardFormatAvailable(
                CF_HTML
            )
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

Nếu vừa copy từ Chrome:
    
    
    True

* * *

# 3\. Đọc HTML
    
    
    import win32clipboard
    
    CF_HTML = win32clipboard.RegisterClipboardFormat(
        "HTML Format"
    )
    
    win32clipboard.OpenClipboard()
    
    try:
    
        html = win32clipboard.GetClipboardData(
            CF_HTML
        )
    
    finally:
    
        win32clipboard.CloseClipboard()
    
    print(html)

Kết quả thường là một chuỗi văn bản rất dài, bao gồm cả phần header và HTML.

* * *

# 4\. Nội dung thực tế

Ví dụ:
    
    
    Version:1.0
    StartHTML:00000097
    EndHTML:00000231
    StartFragment:00000131
    EndFragment:00000193
    
    <html>
    <body>
    
    <!--StartFragment-->
    
    <b>Hello</b>
    
    <!--EndFragment-->
    
    </body>
    </html>

Đây là **định dạng chuẩn CF_HTML** do Microsoft mô tả.

* * *

# 5\. Header

Header luôn nằm đầu dữ liệu.

Ví dụ:
    
    
    Version:1.0
    
    StartHTML:00000097
    
    EndHTML:00000231
    
    StartFragment:00000131
    
    EndFragment:00000193

Các số này là **offset theo byte** tính từ đầu toàn bộ chuỗi.

* * *

# 6\. Ý nghĩa

## StartHTML
    
    
    97

↓

HTML bắt đầu ở byte 97.

* * *

## EndHTML
    
    
    231

↓

HTML kết thúc ở byte 231.

* * *

## StartFragment
    
    
    131

↓

Đoạn cần dán bắt đầu.

* * *

## EndFragment
    
    
    193

↓

Đoạn cần dán kết thúc.

* * *

# 7\. Fragment là gì?

Ví dụ
    
    
    <html>
    
    <body>
    
    <p>Hello</p>
    
    <b>Python</b>
    
    </body>
    
    </html>

Bạn chỉ copy
    
    
    <b>Python</b>

thì
    
    
    <!--StartFragment-->
    
    <b>Python</b>
    
    <!--EndFragment-->

chính là nội dung thực sự được dán.

* * *

# 8\. Vì sao cần Fragment?

Giả sử
    
    
    <html>
    
    <head>
    
    <style>
    
    ...
    
    </style>
    
    </head>
    
    <body>
    
    <h1>Hello</h1>
    
    </body>
    
    </html>

Không phải lúc nào cũng muốn dán cả tài liệu HTML.

Windows chỉ lấy:
    
    
    <h1>Hello</h1>

* * *

# 9\. Phân tích Header

Ví dụ:
    
    
    import re
    
    header = """
    Version:1.0
    StartHTML:00000097
    EndHTML:00000231
    StartFragment:00000131
    EndFragment:00000193
    """
    
    print(
        re.findall(
            r'(\w+):([0-9.]+)',
            header
        )
    )

Kết quả:
    
    
    [
        ('Version', '1.0'),
        ('StartHTML', '00000097'),
        ('EndHTML', '00000231'),
        ('StartFragment', '00000131'),
        ('EndFragment', '00000193')
    ]

* * *

# 10\. Dataclass
    
    
    from dataclasses import dataclass
    
    
    @dataclass(slots=True)
    class HtmlClipboardHeader:
    
        version: str
    
        start_html: int
    
        end_html: int
    
        start_fragment: int
    
        end_fragment: int

* * *

# 11\. Parse Header
    
    
    import re
    
    
    def parse_header(text: str):
    
        d = dict(
            re.findall(
                r'(\w+):([0-9.]+)',
                text
            )
        )
    
        return HtmlClipboardHeader(
    
            version=d["Version"],
    
            start_html=int(d["StartHTML"]),
    
            end_html=int(d["EndHTML"]),
    
            start_fragment=int(d["StartFragment"]),
    
            end_fragment=int(d["EndFragment"])
        )

* * *

# 12\. Lấy Fragment
    
    
    header = parse_header(html)
    
    fragment = html[
        header.start_fragment:
        header.end_fragment
    ]
    
    print(fragment)

Ví dụ:
    
    
    <b>Hello Python</b>

* * *

# 13\. Tạo HTML Clipboard

Giả sử muốn copy:
    
    
    <b>Hello</b>

Không thể chỉ:
    
    
    SetClipboardData(
        CF_HTML,
        "<b>Hello</b>"
    )

Điều này **không đúng chuẩn CF_HTML**.

* * *

# 14\. HTML Clipboard Builder

Ý tưởng:
    
    
    Header
    
    ↓
    
    HTML
    
    ↓
    
    Fragment
    
    ↓
    
    Offset

* * *

Ví dụ:
    
    
    <html>
    
    <body>
    
    <!--StartFragment-->
    
    <b>Hello</b>
    
    <!--EndFragment-->
    
    </body>
    
    </html>

Sau đó tính chính xác:

  * StartHTML 
  * EndHTML 
  * StartFragment 
  * EndFragment 



rồi điền vào header.

Đây là phần khó nhất khi tự tạo dữ liệu CF_HTML.

* * *

# 15\. Hàm Builder

Một cách đơn giản:
    
    
    def build_html(fragment: str):
    
        html = f"""<html>
    <body>
    <!--StartFragment-->{fragment}<!--EndFragment-->
    </body>
    </html>
    """
    
        # Sau này sẽ tính offset
    
        return html

Trong thực tế, bạn cần tính các offset theo **số byte** (không phải số ký tự) của chuỗi đã mã hóa, thường là UTF-8.

* * *

# 16\. HTML Clipboard Manager
    
    
    class HtmlClipboard:
    
        FORMAT = win32clipboard.RegisterClipboardFormat(
            "HTML Format"
        )
    
        @classmethod
        def has_html(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.IsClipboardFormatAvailable(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()
    
        @classmethod
        def html(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.GetClipboardData(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()

* * *

# 17\. Ứng dụng thực tế

Ví dụ

Copy
    
    
    Wikipedia

↓

Python

↓

Đọc
    
    
    <a href="...">
    
    Wikipedia
    
    </a>

↓

Lưu Database

↓

Hiển thị GUI

* * *

Hoặc
    
    
    Chrome
    
    ↓
    
    Clipboard
    
    ↓
    
    HTML
    
    ↓
    
    BeautifulSoup
    
    ↓
    
    Markdown
    
    ↓
    
    SQLite

Đây là quy trình rất hữu ích khi xây dựng các công cụ thu thập nội dung web hoặc ghi chú.

* * *

# 18\. Kiến trúc
    
    
    clipboard/
    
    html/
    
    ├── parser.py
    ├── builder.py
    ├── header.py
    ├── fragment.py
    ├── manager.py
    └── constants.py

Ví dụ
    
    
    parser.py
    
    
    parse_header()
    
    parse_fragment()
    
    parse_html()
    
    
    builder.py
    
    
    build()
    
    calculate_offset()
    
    write_clipboard()

Việc tách riêng parser và builder giúp dễ kiểm thử và tái sử dụng.

* * *

# Bài tập

## Bài 1

Viết
    
    
    has_html()

* * *

## Bài 2

Viết
    
    
    get_html()

* * *

## Bài 3

Viết
    
    
    get_fragment()

* * *

## Bài 4

Viết dataclass
    
    
    HtmlClipboardHeader

* * *

## Bài 5

Viết
    
    
    HtmlClipboardInspector

Cho kết quả
    
    
    Version : 1.0
    
    StartHTML : 97
    
    EndHTML : 231
    
    StartFragment : 131
    
    EndFragment : 193

* * *

# Mini Project

Viết chương trình:
    
    
    Clipboard HTML Viewer
    
    ====================
    
    Có HTML : YES
    
    Fragment
    
    -----------------
    
    <h2>Hello</h2>
    
    <b>Python</b>
    
    -----------------
    
    Save HTML? (y/n)

Nếu chọn:
    
    
    y

↓
    
    
    clipboard.html

* * *

# Tổng kết

Trong buổi này, bạn đã học:

  * Cơ chế hoạt động của **HTML Clipboard (`CF_HTML`)**. 
  * Cách đăng ký và sử dụng định dạng `"HTML Format"` bằng `RegisterClipboardFormat()`. 
  * Cấu trúc chuẩn của dữ liệu `CF_HTML` với các trường `StartHTML`, `EndHTML`, `StartFragment`, `EndFragment`. 
  * Cách phân tích header và trích xuất phần HTML thực sự được dán. 
  * Thiết kế nền tảng cho một `HtmlClipboardManager`. 



## Buổi tiếp theo

Ở **Buổi 8** , chúng ta sẽ học về **Rich Text Format (RTF Clipboard)** :

  * Cấu trúc của dữ liệu RTF. 
  * Định dạng `"Rich Text Format"` trên Clipboard. 
  * Đọc và ghi RTF. 
  * Chuyển đổi giữa **RTF ↔ HTML ↔ Plain Text**. 
  * Xây dựng một **Clipboard Format Converter** có thể chuyển đổi linh hoạt giữa nhiều định dạng văn bản 

