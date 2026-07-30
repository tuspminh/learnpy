# Khóa học win32clipboard Deep Dive

# Buổi 3: Multiple Clipboard Formats, Enumeration và Clipboard Lock

Đây là một trong những buổi quan trọng nhất của khóa học.

Đến đây chúng ta sẽ bắt đầu hiểu **Windows Clipboard thực sự hoạt động như thế nào** , chứ không chỉ biết dùng `GetClipboardData()` và `SetClipboardData()`.

Rất nhiều lập trình viên Python chỉ biết:
    
    
    GetClipboardData()

nhưng không biết rằng Clipboard có thể chứa **hàng chục định dạng cùng một lúc**.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu

  * Multiple Clipboard Formats 
  * Clipboard Format Table 
  * EnumClipboardFormats() 
  * CountClipboardFormats() 
  * GetPriorityClipboardFormat() 
  * IsClipboardFormatAvailable() 
  * Clipboard Lock 
  * Retry khi Clipboard đang bị khóa 
  * Xây dựng Clipboard Inspector 



* * *

# 1\. Clipboard không chỉ chứa một dữ liệu

Đa số mọi người nghĩ
    
    
    Clipboard
    │
    └── Hello

Thực tế Windows lưu như sau
    
    
    Clipboard
    
    ├── CF_TEXT
    
    ├── CF_UNICODETEXT
    
    ├── CF_LOCALE
    
    ├── HTML Format
    
    ├── Rich Text Format
    
    ├── CSV
    
    └── ...

Tức là **một lần Copy có thể sinh ra nhiều định dạng khác nhau**.

* * *

# 2\. Ví dụ

Copy dòng sau từ Microsoft Word
    
    
    Xin chào Python

Clipboard có thể chứa
    
    
    CF_TEXT
    
    CF_UNICODETEXT
    
    CF_LOCALE
    
    Rich Text Format
    
    HTML Format
    
    Object Descriptor
    
    Embedded Object

Nếu paste vào

Notepad

↓

Windows chọn
    
    
    CF_UNICODETEXT

Nếu paste vào Word

↓

Windows chọn
    
    
    Rich Text

Nếu paste vào Outlook

↓

Windows chọn
    
    
    HTML

Đây là lý do vì sao cùng một thao tác **Ctrl+C** , nhưng khi dán vào các ứng dụng khác nhau lại giữ được hoặc mất định dạng.

* * *

# 3\. Đếm số Format

Windows có hàm
    
    
    CountClipboardFormats()

Ví dụ
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    count = win32clipboard.CountClipboardFormats()
    
    print(count)
    
    win32clipboard.CloseClipboard()

Ví dụ kết quả
    
    
    7

Nghĩa là Clipboard hiện có 7 định dạng dữ liệu.

* * *

# 4\. Liệt kê Format

Windows cung cấp
    
    
    EnumClipboardFormats()

Nguyên lý
    
    
    0
    
    ↓
    
    Format1
    
    ↓
    
    Format2
    
    ↓
    
    Format3
    
    ↓
    
    0

* * *

Ví dụ
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    fmt = 0
    
    while True:
    
        fmt = win32clipboard.EnumClipboardFormats(fmt)
    
        if fmt == 0:
            break
    
        print(fmt)
    
    win32clipboard.CloseClipboard()

Ví dụ
    
    
    13
    
    16
    
    49320
    
    49452
    
    1
    
    7

Đây là các Format ID.

* * *

# 5\. Tên Format

Số
    
    
    13

khó hiểu.

Windows có
    
    
    GetClipboardFormatName()

Nhưng chỉ áp dụng cho **Custom Format**.

Ví dụ
    
    
    try:
        print(win32clipboard.GetClipboardFormatName(fmt))
    except:
        print("Standard Format")

* * *

# 6\. Standard Format

Các Format nhỏ hơn 0xC000 thường là chuẩn.

Ví dụ

ID| Tên  
---|---  
1| CF_TEXT  
2| CF_BITMAP  
7| CF_OEMTEXT  
8| CF_DIB  
13| CF_UNICODETEXT  
15| CF_HDROP  
16| CF_LOCALE  
17| CF_DIBV5  
  
* * *

# 7\. Hàm chuyển ID sang tên

Đây là hàm rất hữu ích.
    
    
    STANDARD_FORMATS = {
        1: "CF_TEXT",
        2: "CF_BITMAP",
        3: "CF_METAFILEPICT",
        4: "CF_SYLK",
        5: "CF_DIF",
        6: "CF_TIFF",
        7: "CF_OEMTEXT",
        8: "CF_DIB",
        9: "CF_PALETTE",
        10: "CF_PENDATA",
        11: "CF_RIFF",
        12: "CF_WAVE",
        13: "CF_UNICODETEXT",
        14: "CF_ENHMETAFILE",
        15: "CF_HDROP",
        16: "CF_LOCALE",
        17: "CF_DIBV5"
    }
    
    
    def format_name(fmt):
    
        if fmt in STANDARD_FORMATS:
            return STANDARD_FORMATS[fmt]
    
        try:
            return win32clipboard.GetClipboardFormatName(fmt)
        except:
            return f"Unknown({fmt})"

* * *

# 8\. Clipboard Inspector

Kết hợp tất cả
    
    
    import win32clipboard
    
    STANDARD_FORMATS = {
        1: "CF_TEXT",
        2: "CF_BITMAP",
        7: "CF_OEMTEXT",
        8: "CF_DIB",
        13: "CF_UNICODETEXT",
        15: "CF_HDROP",
        16: "CF_LOCALE",
        17: "CF_DIBV5",
    }
    
    
    def format_name(fmt):
    
        if fmt in STANDARD_FORMATS:
            return STANDARD_FORMATS[fmt]
    
        try:
            return win32clipboard.GetClipboardFormatName(fmt)
        except:
            return f"Unknown({fmt})"
    
    
    win32clipboard.OpenClipboard()
    
    fmt = 0
    
    while True:
    
        fmt = win32clipboard.EnumClipboardFormats(fmt)
    
        if fmt == 0:
            break
    
        print(fmt, format_name(fmt))
    
    win32clipboard.CloseClipboard()

Ví dụ
    
    
    13 CF_UNICODETEXT
    
    16 CF_LOCALE
    
    49423 HTML Format
    
    49328 Rich Text Format

Đây là công cụ đầu tiên mà các lập trình viên Win32 thường tự viết để "nhìn" vào Clipboard.

* * *

# 9\. IsClipboardFormatAvailable()

Đây là hàm quan trọng.
    
    
    if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_HDROP):
        ...

hoặc
    
    
    if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_BITMAP):
        ...

hoặc
    
    
    if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_UNICODETEXT):
        ...

Nó giúp tránh lỗi khi đọc sai định dạng.

* * *

# 10\. GetPriorityClipboardFormat()

Windows cho phép hỏi:

> "Trong danh sách này, định dạng nào đang có và nên ưu tiên?"

Ví dụ
    
    
    formats = [
        win32clipboard.CF_UNICODETEXT,
        win32clipboard.CF_TEXT,
    ]
    
    
    fmt = win32clipboard.GetPriorityClipboardFormat(formats)
    
    print(fmt)

Nếu có Unicode

↓

trả về
    
    
    13

Nếu chỉ có ANSI

↓

trả về
    
    
    1

Điều này rất hữu ích khi ứng dụng của bạn có thể xử lý nhiều định dạng.

* * *

# 11\. Clipboard Lock

Đây là lỗi mà mọi lập trình viên Windows đều gặp.

Ví dụ

Chrome đang ghi Clipboard.

Python cũng ghi.

Word cũng ghi.

Chỉ **một tiến trình** được mở Clipboard tại một thời điểm.

Nếu không mở được
    
    
    OpenClipboard()

sẽ báo
    
    
    pywintypes.error
    
    OpenClipboard Failed

* * *

# 12\. Retry

Thay vì báo lỗi ngay

Ta thử lại
    
    
    import time
    import pywintypes
    import win32clipboard
    
    
    def open_clipboard(retry=10, delay=0.05):
    
        for _ in range(retry):
    
            try:
    
                win32clipboard.OpenClipboard()
                return
    
            except pywintypes.error:
    
                time.sleep(delay)
    
        raise RuntimeError("Cannot open clipboard.")

Sau này chúng ta sẽ tái sử dụng hàm này trong mọi project.

* * *

# 13\. Context Manager

Thay vì
    
    
    OpenClipboard()
    
    ...
    
    CloseClipboard()

ta có
    
    
    from contextlib import contextmanager
    import time
    import pywintypes
    import win32clipboard
    
    
    @contextmanager
    def clipboard(retry=10, delay=0.05):
        opened = False
        try:
            for _ in range(retry):
                try:
                    win32clipboard.OpenClipboard()
                    opened = True
                    break
                except pywintypes.error:
                    time.sleep(delay)
    
            if not opened:
                raise RuntimeError("Không thể mở Clipboard.")
    
            yield
    
        finally:
            if opened:
                win32clipboard.CloseClipboard()

Sử dụng
    
    
    with clipboard():
        if win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_UNICODETEXT):
            print(
                win32clipboard.GetClipboardData(
                    win32clipboard.CF_UNICODETEXT
                )
            )

Đây là một cách thiết kế rất "Pythonic", giúp đảm bảo `CloseClipboard()` luôn được gọi.

* * *

# 14\. Kiến trúc chuyên nghiệp

Thay vì gọi trực tiếp `win32clipboard` khắp nơi, hãy đóng gói:
    
    
    clipboard/
    │
    ├── __init__.py
    ├── manager.py
    ├── formats.py
    ├── retry.py
    ├── inspector.py
    ├── context.py
    └── exceptions.py

Ví dụ:

  * `manager.py`: đọc/ghi dữ liệu. 
  * `formats.py`: ánh xạ ID ↔ tên định dạng. 
  * `retry.py`: mở Clipboard có retry. 
  * `context.py`: Context Manager. 
  * `inspector.py`: công cụ liệt kê định dạng. 



Cách tổ chức này giúp mã dễ kiểm thử, tái sử dụng và mở rộng.

* * *

# Bài tập

### Bài 1

Viết chương trình
    
    
    Clipboard Inspector

In ra
    
    
    13 CF_UNICODETEXT
    
    16 CF_LOCALE
    
    49423 HTML Format
    
    49328 Rich Text Format

với cả ID và tên định dạng.

* * *

### Bài 2

Viết
    
    
    has_text()
    
    has_bitmap()
    
    has_file()

sử dụng `IsClipboardFormatAvailable()`.

* * *

### Bài 3

Viết
    
    
    list_formats()

trả về
    
    
    [
        "CF_UNICODETEXT",
        "CF_LOCALE",
        "HTML Format",
        "Rich Text Format",
    ]

* * *

### Bài 4

Viết `ClipboardManager` phiên bản nâng cấp:
    
    
    manager = ClipboardManager()
    
    print(manager.formats())
    
    if manager.has_text():
        print(manager.text())

* * *

# Tổng kết

Buổi này bạn đã nắm được:

  * Clipboard có thể chứa **nhiều định dạng cùng lúc** , không chỉ một chuỗi văn bản. 
  * Cách dùng `CountClipboardFormats()`, `EnumClipboardFormats()`, `GetClipboardFormatName()` và `GetPriorityClipboardFormat()`. 
  * Cách kiểm tra sự tồn tại của định dạng bằng `IsClipboardFormatAvailable()`. 
  * Nguyên nhân gây ra **Clipboard Lock** và cách xử lý bằng cơ chế retry. 
  * Cách xây dựng `Clipboard Inspector` và tổ chức mã theo hướng chuyên nghiệp. 



Ở **Buổi 4** , chúng ta sẽ chuyển sang một chủ đề rất thực tế: **`CF_HDROP`** \- đọc và ghi **danh sách file/thư mục** trên Clipboard. Bạn sẽ học cách lấy các tệp mà người dùng **Ctrl+C** trong File Explorer, mô phỏng thao tác copy file, và xây dựng các tiện ích tự động hóa làm việc với tệp trên Windows. Đây là một trong những định dạng được dùng nhiều trong các công cụ quản lý file và ứng dụng desktop.

