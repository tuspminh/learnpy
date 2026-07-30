# Khóa học win32clipboard Deep Dive

# Buổi 2: Ghi dữ liệu vào Clipboard (SetClipboardData) và quản lý định dạng

Ở buổi trước, chúng ta đã học cách **đọc** Clipboard. Hôm nay chúng ta sẽ học cách **ghi** dữ liệu vào Clipboard, đồng thời hiểu sâu cơ chế hoạt động của Windows Clipboard.

* * *

# Mục tiêu buổi học

Sau buổi này bạn sẽ hiểu:

  * Cơ chế ghi dữ liệu vào Clipboard 
  * `EmptyClipboard()`
  * `SetClipboardData()`
  * `CF_TEXT`
  * `CF_UNICODETEXT`
  * Unicode và ANSI 
  * Clipboard Ownership 
  * Tại sao phải `EmptyClipboard()` trước khi ghi 
  * Thiết kế một lớp `ClipboardManager`



* * *

# 1\. Quy trình ghi dữ liệu

Khi ghi Clipboard, Windows yêu cầu thực hiện đúng trình tự:
    
    
    OpenClipboard()
    
    ↓
    
    EmptyClipboard()
    
    ↓
    
    SetClipboardData()
    
    ↓
    
    CloseClipboard()

Không được bỏ qua bước `EmptyClipboard()`.

* * *

# 2\. Ví dụ đầu tiên
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    win32clipboard.EmptyClipboard()
    
    win32clipboard.SetClipboardData(
        win32clipboard.CF_UNICODETEXT,
        "Hello Python"
    )
    
    win32clipboard.CloseClipboard()

Sau khi chạy:
    
    
    Ctrl + V

ở Notepad sẽ được
    
    
    Hello Python

* * *

# 3\. EmptyClipboard()

Nhiều người mới học thường thắc mắc:

"Tại sao phải xóa Clipboard trước?"

Windows Clipboard chỉ có **một Owner**.

Giả sử Clipboard đang chứa
    
    
    Image

Bạn muốn ghi
    
    
    Hello

Windows cần xóa toàn bộ dữ liệu cũ trước.

Cho nên phải
    
    
    EmptyClipboard()

Nếu không...
    
    
    SetClipboardData()

có thể báo lỗi.

* * *

# 4\. EmptyClipboard làm gì?

Giả sử Clipboard đang có:
    
    
    CF_TEXT
    
    CF_UNICODETEXT
    
    CF_BITMAP
    
    CF_HTML
    
    CF_RTF

Sau
    
    
    EmptyClipboard()

Clipboard trở thành
    
    
    (empty)

Sau đó mới ghi dữ liệu mới.

* * *

# 5\. SetClipboardData()

Cú pháp
    
    
    SetClipboardData(format, data)

Ví dụ
    
    
    SetClipboardData(
        CF_UNICODETEXT,
        "Xin chào"
    )

Trong đó
    
    
    format

cho Windows biết kiểu dữ liệu.
    
    
    data

là dữ liệu thật.

* * *

# 6\. CF_TEXT và CF_UNICODETEXT

Đây là điểm rất nhiều lập trình viên nhầm lẫn.

## CF_TEXT
    
    
    ANSI

Ví dụ
    
    
    Hello

Mỗi ký tự
    
    
    1 byte

Không hỗ trợ tiếng Việt đầy đủ.

* * *

## CF_UNICODETEXT
    
    
    Unicode

Ví dụ
    
    
    Xin chào Việt Nam

Windows hiện đại sử dụng định dạng này.

Trong Python, **luôn ưu tiên`CF_UNICODETEXT`**.

* * *

# 7\. Ví dụ Unicode
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    win32clipboard.EmptyClipboard()
    
    win32clipboard.SetClipboardData(
        win32clipboard.CF_UNICODETEXT,
        "Tiếng Việt rất đẹp 😊"
    )
    
    win32clipboard.CloseClipboard()

Dán vào Word:
    
    
    Tiếng Việt rất đẹp 😊

* * *

# 8\. Ví dụ CF_TEXT
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    win32clipboard.EmptyClipboard()
    
    win32clipboard.SetClipboardData(
        win32clipboard.CF_TEXT,
        b"Hello"
    )
    
    win32clipboard.CloseClipboard()

Lưu ý
    
    
    CF_TEXT

phải truyền
    
    
    bytes

không phải
    
    
    str

* * *

# 9\. Sai lầm thường gặp

Sai
    
    
    SetClipboardData(
        CF_TEXT,
        "Hello"
    )

Lỗi
    
    
    TypeError

Đúng
    
    
    SetClipboardData(
        CF_TEXT,
        b"Hello"
    )

* * *

# 10\. Unicode trong Python

Python 3
    
    
    str

=
    
    
    Unicode

Ví dụ
    
    
    text = "Xin chào"

đã là Unicode.

Do đó
    
    
    SetClipboardData(
        CF_UNICODETEXT,
        text
    )

là đúng.

* * *

# 11\. Hàm copy_text()

Ta có thể đóng gói thành hàm:
    
    
    import win32clipboard
    
    
    def copy_text(text: str):
        win32clipboard.OpenClipboard()
    
        try:
            win32clipboard.EmptyClipboard()
    
            win32clipboard.SetClipboardData(
                win32clipboard.CF_UNICODETEXT,
                text
            )
    
        finally:
            win32clipboard.CloseClipboard()

Sử dụng
    
    
    copy_text("Python Deep Dive")

* * *

# 12\. Hàm paste_text()
    
    
    import win32clipboard
    
    
    def paste_text():
    
        win32clipboard.OpenClipboard()
    
        try:
    
            if win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_UNICODETEXT
            ):
    
                return win32clipboard.GetClipboardData(
                    win32clipboard.CF_UNICODETEXT
                )
    
            return None
    
        finally:
    
            win32clipboard.CloseClipboard()

* * *

# 13\. Clipboard Ownership

Đây là khái niệm rất quan trọng.

Khi gọi
    
    
    EmptyClipboard()

Windows gán chương trình hiện tại làm **Clipboard Owner**.
    
    
    Explorer
    
    ↓
    
    Python
    
    ↓
    
    Word

Mỗi lần có chương trình khác ghi Clipboard:
    
    
    Owner

sẽ thay đổi.

Điều này giải thích vì sao nhiều ứng dụng có thể lần lượt thay thế nội dung Clipboard của nhau.

* * *

# 14\. Thử nghiệm
    
    
    copy_text("One")
    
    input()

Trong lúc chương trình đang chờ:

  * mở Notepad 
  * nhấn Ctrl+V 



Bạn sẽ thấy
    
    
    One

Sau đó
    
    
    Ctrl+C

một đoạn khác.

Lúc này
    
    
    Owner

đã đổi sang Notepad (thực chất là tiến trình của ứng dụng đã ghi Clipboard).

* * *

# 15\. Thiết kế ClipboardManager

Thay vì các hàm rời rạc, ta có thể thiết kế lớp:
    
    
    import win32clipboard
    
    
    class ClipboardManager:
    
        @staticmethod
        def copy(text: str):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                win32clipboard.EmptyClipboard()
    
                win32clipboard.SetClipboardData(
                    win32clipboard.CF_UNICODETEXT,
                    text
                )
    
            finally:
    
                win32clipboard.CloseClipboard()
    
        @staticmethod
        def paste():
    
            win32clipboard.OpenClipboard()
    
            try:
    
                if win32clipboard.IsClipboardFormatAvailable(
                    win32clipboard.CF_UNICODETEXT
                ):
    
                    return win32clipboard.GetClipboardData(
                        win32clipboard.CF_UNICODETEXT
                    )
    
                return None
    
            finally:
    
                win32clipboard.CloseClipboard()

Sử dụng
    
    
    ClipboardManager.copy("Hello")
    
    print(ClipboardManager.paste())

* * *

# 16\. Những lỗi thường gặp

## Quên OpenClipboard
    
    
    SetClipboardData(...)

→ lỗi.

* * *

## Quên EmptyClipboard
    
    
    SetClipboardData(...)

→ có thể lỗi hoặc ghi không thành công.

* * *

## Quên CloseClipboard

Các chương trình khác có thể không truy cập được Clipboard ngay lập tức, hoặc chương trình của bạn có thể gặp lỗi ở lần truy cập tiếp theo.

* * *

## Dùng sai Format
    
    
    CF_TEXT

nhưng truyền
    
    
    str

→ lỗi kiểu dữ liệu.

* * *

## Không xử lý ngoại lệ

Nếu `OpenClipboard()` thất bại (ví dụ Clipboard đang bị ứng dụng khác sử dụng), chương trình sẽ dừng đột ngột nếu không bắt ngoại lệ.

* * *

# 17\. Thực hành

### Bài 1

Viết
    
    
    copy_text(text)

* * *

### Bài 2

Viết
    
    
    paste_text()

* * *

### Bài 3

Viết chương trình:
    
    
    Nhập:
    
    Xin chào ChatGPT

Sau đó:
    
    
    Ctrl + V

ở bất kỳ ứng dụng nào sẽ được
    
    
    Xin chào ChatGPT

* * *

### Bài 4

Viết menu:
    
    
    1. Copy
    
    2. Paste
    
    3. Exit

Trong đó:

  * Chọn `1`: nhập văn bản và sao chép vào Clipboard. 
  * Chọn `2`: hiển thị nội dung hiện có trong Clipboard (nếu là văn bản Unicode). 
  * Chọn `3`: thoát chương trình. 



* * *

# Tổng kết

Ở buổi này, bạn đã học được:

  * Quy trình chuẩn để ghi dữ liệu vào Clipboard (`OpenClipboard` → `EmptyClipboard` → `SetClipboardData` → `CloseClipboard`). 
  * Sự khác nhau giữa `CF_TEXT` (ANSI, `bytes`) và `CF_UNICODETEXT` (Unicode, `str`). 
  * Vai trò của `EmptyClipboard()` và khái niệm **Clipboard Ownership**. 
  * Cách xây dựng các hàm tiện ích và lớp `ClipboardManager`. 



**Buổi 3** sẽ đi sâu vào một chủ đề rất quan trọng của Win32 Clipboard: **quản lý nhiều định dạng dữ liệu (multiple clipboard formats)** , cơ chế **Clipboard Lock** , **EnumClipboardFormats()** , **CountClipboardFormats()** , và cách đọc các định dạng khác nhau như `CF_HDROP` (danh sách file), `CF_BITMAP`, cùng những kỹ thuật mà các ứng dụng chuyên nghiệp như Microsoft Office hay Photoshop sử dụng để làm việc với Clipboard.

