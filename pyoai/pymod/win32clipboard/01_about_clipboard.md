# Buổi 1

# 1\. Clipboard là gì?

Clipboard là vùng nhớ tạm do Windows quản lý.

Ví dụ
    
    
    Ctrl + C

↓
    
    
    Windows Clipboard

↓
    
    
    Ctrl + V

Clipboard không thuộc chương trình nào.

Nó là tài nguyên chung của hệ điều hành.

Ví dụ
    
    
    Notepad
         │
    Word
         │
    VSCode
         │
    Chrome
         │
    Python

đều dùng chung Clipboard.

* * *

# 2\. Clipboard API của Windows

Windows cung cấp hàng chục hàm.

Ví dụ
    
    
    OpenClipboard()
    
    CloseClipboard()
    
    GetClipboardData()
    
    SetClipboardData()
    
    EmptyClipboard()
    
    CountClipboardFormats()
    
    EnumClipboardFormats()
    
    RegisterClipboardFormat()

`pywin32` chỉ là lớp bọc (wrapper) để gọi các hàm Win32 này từ Python.

* * *

# 3\. Cài đặt
    
    
    pip install pywin32

Kiểm tra
    
    
    import win32clipboard
    
    print("OK")

* * *

# 4\. Luôn phải OpenClipboard()

Không thể đọc Clipboard ngay.

Sai
    
    
    import win32clipboard
    
    text = win32clipboard.GetClipboardData()

Lỗi
    
    
    pywintypes.error:
    OpenClipboard Failed

Đúng
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    text = win32clipboard.GetClipboardData()
    
    win32clipboard.CloseClipboard()

* * *

# 5\. Luôn phải CloseClipboard()

Clipboard chỉ cho một tiến trình truy cập tại một thời điểm.

Nếu quên
    
    
    OpenClipboard()

mà không
    
    
    CloseClipboard()

thì:

  * chương trình khác không thể truy cập Clipboard, 
  * có thể phát sinh lỗi hoặc khiến thao tác sao chép/dán của các ứng dụng khác bị ảnh hưởng. 



Vì vậy nên dùng `try...finally` hoặc Context Manager.

* * *

# 6\. Ví dụ đầu tiên
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    text = win32clipboard.GetClipboardData()
    
    win32clipboard.CloseClipboard()
    
    print(text)

Nếu Clipboard chứa
    
    
    Hello Python

Kết quả
    
    
    Hello Python

* * *

# 7\. Nếu Clipboard không phải Text

Ví dụ bạn copy

  * ảnh 
  * file 
  * Excel 
  * HTML 



thì
    
    
    GetClipboardData()

có thể phát sinh lỗi hoặc trả về dữ liệu không như mong đợi.

Nên kiểm tra định dạng trước.
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_UNICODETEXT):
        text = win32clipboard.GetClipboardData()
        print(text)
    
    win32clipboard.CloseClipboard()

* * *

# 8\. Clipboard Format

Mỗi dữ liệu có một số hiệu (format ID).

Ví dụ

Format| Ý nghĩa  
---|---  
CF_TEXT| ANSI Text  
CF_UNICODETEXT| Unicode  
CF_BITMAP| Bitmap  
CF_DIB| Device Independent Bitmap  
CF_HDROP| Danh sách file được copy trong Explorer  
CF_OEMTEXT| OEM Text  
CF_LOCALE| Thông tin locale  
CF_DIBV5| Bitmap mở rộng  
  
Buổi sau chúng ta sẽ tìm hiểu chi tiết từng định dạng và cách đọc/ghi chúng.

* * *

# 9\. Ví dụ đọc Unicode
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    if win32clipboard.IsClipboardFormatAvailable(
            win32clipboard.CF_UNICODETEXT):
    
        text = win32clipboard.GetClipboardData(
            win32clipboard.CF_UNICODETEXT)
    
        print(text)
    
    win32clipboard.CloseClipboard()

* * *

# 10\. Xử lý ngoại lệ

Clipboard có thể đang bị ứng dụng khác sử dụng.
    
    
    import win32clipboard
    
    try:
        win32clipboard.OpenClipboard()
    
        text = win32clipboard.GetClipboardData()
    
        print(text)
    
    finally:
        win32clipboard.CloseClipboard()

Một phiên bản an toàn hơn:
    
    
    import win32clipboard
    import pywintypes
    
    opened = False
    
    try:
        win32clipboard.OpenClipboard()
        opened = True
    
        if win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_UNICODETEXT):
            text = win32clipboard.GetClipboardData(
                win32clipboard.CF_UNICODETEXT)
            print(text)
        else:
            print("Clipboard không chứa văn bản Unicode.")
    
    except pywintypes.error as e:
        print(f"Lỗi khi truy cập Clipboard: {e}")
    
    finally:
        if opened:
            win32clipboard.CloseClipboard()

Đoạn mã này tránh gọi `CloseClipboard()` khi `OpenClipboard()` thất bại.

* * *

# Tổng kết Buổi 1

Bạn đã nắm được:

  * Kiến trúc Clipboard của Windows. 
  * Vai trò của `win32clipboard` trong `pywin32`. 
  * Cách mở và đóng Clipboard. 
  * Đọc dữ liệu văn bản Unicode. 
  * Kiểm tra định dạng dữ liệu trước khi đọc. 
  * Xử lý lỗi khi Clipboard đang bị ứng dụng khác chiếm dụng. 



* * *

# Bài tập

### Bài 1

Viết chương trình in toàn bộ nội dung text trong Clipboard.

* * *

### Bài 2

Nếu Clipboard không chứa text thì in:
    
    
    Clipboard is not text.

* * *

### Bài 3

Viết hàm:
    
    
    def get_clipboard_text() -> str | None:
        ...

Yêu cầu:

  * Trả về chuỗi nếu Clipboard chứa `CF_UNICODETEXT`. 
  * Trả về `None` nếu không có văn bản hoặc không thể truy cập Clipboard. 



* * *

### Bài 4

Thử:

  * Copy một đoạn văn bản từ Notepad. 
  * Copy một hình ảnh. 
  * Copy một tệp trong File Explorer. 



Sau mỗi lần, chạy chương trình và quan sát kết quả. Ghi nhận sự khác biệt giữa các định dạng dữ liệu trên Clipboard.

* * *

Ở **Buổi 2** , chúng ta sẽ đi sâu vào **SetClipboardData()** , **EmptyClipboard()** , cơ chế ghi dữ liệu lên Clipboard, Unicode/ANSI, và cách sao chép văn bản bằng Python để thay thế hoặc bổ sung cho các thư viện như `pyperclip`.

