# Khóa học `win32clipboard` Deep Dive

# Buổi 8: Rich Text Format (RTF Clipboard) Deep Dive

> Đây là một trong những định dạng Clipboard quan trọng nhất đối với các ứng dụng văn phòng.

Khi bạn **Ctrl+C** từ:

  * Microsoft Word 
  * WordPad 
  * Outlook 
  * LibreOffice 
  * WPS Office 



Clipboard thường chứa đồng thời:
    
    
    CF_UNICODETEXT
    HTML Format
    Rich Text Format
    CF_LOCALE

Nếu dán vào:

  * Notepad → chỉ lấy `CF_UNICODETEXT`
  * Word → ưu tiên `Rich Text Format`
  * Outlook → có thể ưu tiên HTML hoặc RTF tùy ngữ cảnh 



Đây là lý do vì sao khi dán vào Word, bạn vẫn giữ được:

  * **In đậm**
  * _In nghiêng_
  * Màu chữ 
  * Font chữ 
  * Kích thước 
  * Bảng 
  * Danh sách 
  * Hyperlink 



* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu

  * RTF là gì 
  * Rich Text Format Clipboard 
  * Cấu trúc của RTF 
  * Control Word 
  * Control Symbol 
  * Group 
  * Escape Character 
  * Đọc RTF Clipboard 
  * Ghi RTF Clipboard 
  * Thiết kế RTF Clipboard Manager 



* * *

# 1\. RTF là gì?

RTF

=

**Rich Text Format**

Được Microsoft giới thiệu từ năm 1987.

Mục tiêu:

> Trao đổi tài liệu giữa các chương trình mà vẫn giữ định dạng.

* * *

# 2\. Ví dụ

Bạn tạo trong Word
    
    
    Hello

Trong đó

  * Hello màu đỏ 
  * Bold 
  * Font Arial 
  * Size 18 



Nếu copy

↓

Clipboard

↓

RTF

Không phải:
    
    
    Hello

Mà là
    
    
    {\rtf1
    \b
    \cf1
    \f0
    \fs36
    Hello
    }

* * *

# 3\. Định dạng Clipboard

RTF cũng là

Custom Clipboard Format

Không có
    
    
    CF_RTF

Muốn dùng
    
    
    import win32clipboard
    
    CF_RTF = win32clipboard.RegisterClipboardFormat(
        "Rich Text Format"
    )

* * *

# 4\. Kiểm tra
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        print(
            win32clipboard.IsClipboardFormatAvailable(
                CF_RTF
            )
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

* * *

# 5\. Đọc RTF
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        rtf = win32clipboard.GetClipboardData(
            CF_RTF
        )
    
    finally:
    
        win32clipboard.CloseClipboard()
    
    print(rtf)

Ví dụ
    
    
    {\rtf1\ansi
    
    \b Hello\b0
    
    }

* * *

# 6\. Cấu trúc RTF

RTF là

Text

Không phải Binary.

Ví dụ
    
    
    {\rtf1
    
    ...
    
    }

Trong đó
    
    
    {
    
    }

là

Group.

* * *

# 7\. Group

Ví dụ
    
    
    {
    
    \b
    
    Hello
    
    }

↓

Một Group.

Có thể lồng nhau
    
    
    {
    
    \fonttbl
    
    {
    
    \f0 Arial;
    
    }
    
    }

↓

Group trong Group.

* * *

# 8\. Control Word

Ví dụ
    
    
    \b

↓

Bold

* * *
    
    
    \i

↓

Italic

* * *
    
    
    \ul

↓

Underline

* * *
    
    
    \par

↓

New Paragraph

* * *
    
    
    \cf1

↓

Color số 1

* * *
    
    
    \f0

↓

Font số 0

* * *
    
    
    \fs24

↓

Font size

24 half-points

=

12pt

* * *

# 9\. Ví dụ
    
    
    {\rtf1
    
    \b
    
    Hello
    
    \b0
    
    }

↓

Bold

* * *
    
    
    \b0

↓

Tắt Bold.

* * *

# 10\. Font Table

Ví dụ
    
    
    {
    
    \fonttbl
    
    {
    
    \f0 Arial;
    
    }
    
    {
    
    \f1 Times New Roman;
    
    }
    
    }

↓

Định nghĩa Font.

* * *

Sau đó
    
    
    \f1

↓

Dùng

Times New Roman.

* * *

# 11\. Color Table
    
    
    {
    
    \colortbl
    
    ;
    
    \red255\green0\blue0;
    
    \red0\green255\blue0;
    
    }

↓

Color

1

↓

Red

* * *
    
    
    \cf1

↓

Dùng màu đỏ.

* * *

# 12\. Paragraph
    
    
    Hello
    
    \par
    
    Python

↓

Hiển thị
    
    
    Hello
    
    Python

* * *

# 13\. Unicode

RTF hỗ trợ Unicode.

Ví dụ
    
    
    \u27231?

↓

Một ký tự Unicode.

Hoặc trong nhiều tài liệu hiện đại, RTF có thể chứa trực tiếp ký tự Unicode tùy theo bộ sinh tài liệu và bảng mã.

* * *

# 14\. Đọc Plain Text từ RTF

RTF
    
    
    {\rtf1
    
    \b
    
    Hello
    
    \b0
    
    }

↓

Plain Text
    
    
    Hello

Ý tưởng
    
    
    import re
    
    text = re.sub(
        r'\\[a-z]+[0-9]* ?',
        '',
        rtf
    )
    
    text = text.replace("{", "")
    text = text.replace("}", "")
    
    print(text)

> Đây chỉ là **minh họa đơn giản**. Một parser RTF đầy đủ phức tạp hơn nhiều vì phải xử lý group lồng nhau, escape và Unicode.

* * *

# 15\. Ghi RTF

Ví dụ
    
    
    {\rtf1
    
    \b
    
    Hello Python
    
    \b0
    
    }

↓

Clipboard
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        win32clipboard.EmptyClipboard()
    
        win32clipboard.SetClipboardData(
            CF_RTF,
            rtf
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

* * *

# 16\. RTF Manager
    
    
    import win32clipboard
    
    
    class RtfClipboard:
    
        FORMAT = win32clipboard.RegisterClipboardFormat(
            "Rich Text Format"
        )
    
        @classmethod
        def has_rtf(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.IsClipboardFormatAvailable(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()
    
        @classmethod
        def get_rtf(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.GetClipboardData(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()

* * *

# 17\. Chuyển đổi

Clipboard

↓

RTF

↓

Plain Text

↓

Markdown

↓

HTML

↓

SQLite

Đây là quy trình mà nhiều ứng dụng ghi chú và hệ thống quản lý tri thức sử dụng.

* * *

# 18\. So sánh

Định dạng| Giữ định dạng| Có hình ảnh| Dễ đọc  
---|---|---|---  
Plain Text| ❌| ❌| ⭐⭐⭐⭐⭐  
RTF| ✅| ✅ (có thể nhúng)| ⭐⭐⭐  
HTML| ✅| ✅| ⭐⭐⭐⭐  
DOCX| ✅| ✅| ⭐⭐  
  
* * *

# 19\. Kiến trúc
    
    
    clipboard/
    
    rtf/
    
    ├── parser.py
    ├── tokenizer.py
    ├── reader.py
    ├── writer.py
    ├── manager.py
    ├── converter.py
    └── constants.py

Ví dụ
    
    
    parser.py

↓
    
    
    parse_groups()
    
    parse_control_words()
    
    parse_fonts()

* * *

# 20\. Dự án thực tế

Ví dụ
    
    
    Word
    
    ↓
    
    Copy
    
    ↓
    
    Clipboard
    
    ↓
    
    RTF
    
    ↓
    
    Python
    
    ↓
    
    Markdown
    
    ↓
    
    SQLite

Hoặc
    
    
    Outlook
    
    ↓
    
    Copy
    
    ↓
    
    RTF
    
    ↓
    
    HTML
    
    ↓
    
    Email Viewer

Hoặc
    
    
    RTF
    
    ↓
    
    Plain Text
    
    ↓
    
    LLM
    
    ↓
    
    AI Summary

* * *

# Bài tập

## Bài 1

Viết
    
    
    has_rtf()

* * *

## Bài 2

Viết
    
    
    get_rtf()

* * *

## Bài 3

Viết
    
    
    save_rtf(path)

Ví dụ
    
    
    save_rtf("note.rtf")

* * *

## Bài 4

Viết
    
    
    rtf_to_text(rtf)

Yêu cầu:

  * Loại bỏ các control word cơ bản. 
  * Loại bỏ dấu `{}`. 
  * Trả về văn bản thuần. 



> Chấp nhận đây là phiên bản đơn giản, chưa cần hỗ trợ đầy đủ chuẩn RTF.

* * *

## Bài 5

Viết
    
    
    ClipboardInspector

Hiển thị
    
    
    Có Plain Text : YES
    
    Có HTML : YES
    
    Có RTF : YES
    
    Có Image : NO
    
    Có File : NO

* * *

# Mini Project

Viết chương trình
    
    
    Clipboard Rich Text Viewer
    
    ===========================
    
    Có RTF : YES
    
    ----------------------------
    
    {\rtf1
    
    ...
    
    }
    
    ----------------------------
    
    Save? (y/n)

Nếu
    
    
    y

↓
    
    
    clipboard.rtf

* * *

# Tổng kết

Trong buổi này bạn đã học:

  * Kiến trúc của **Rich Text Format (RTF)**. 
  * Cách đăng ký và sử dụng định dạng `"Rich Text Format"` trên Clipboard. 
  * Khái niệm **Group** , **Control Word** , **Font Table** , **Color Table**. 
  * Đọc và ghi dữ liệu RTF bằng `win32clipboard`. 
  * Thiết kế lớp `RtfClipboard` và cách chuyển đổi RTF sang văn bản thuần ở mức cơ bản. 



* * *

# Chuẩn bị cho Buổi 9

Ở **Buổi 9** , chúng ta sẽ xây dựng một **Clipboard Inspector Pro** – một công cụ chuyên nghiệp có khả năng:

  * Liệt kê **tất cả** các định dạng hiện có trên Clipboard. 
  * Hiển thị tên định dạng chuẩn và định dạng tùy chỉnh. 
  * Xem trước nội dung của từng định dạng (Text, HTML, RTF, File, Image...). 
  * Xuất toàn bộ nội dung Clipboard ra thư mục để phục vụ debug hoặc phân tích. 



Đây sẽ là bước kết hợp toàn bộ kiến thức từ các buổi 1–8 thành một công cụ có giá trị sử dụng thực tế.

