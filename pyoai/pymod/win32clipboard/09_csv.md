# Khóa học `win32clipboard` Deep Dive

# Buổi 9: CSV Clipboard Deep Dive

> **Lưu ý quan trọng trước khi bắt đầu**

Đây là một điểm mà rất nhiều tài liệu trên Internet giải thích chưa chính xác.

**Windows KHÔNG có một Clipboard Format chuẩn tên là`CF_CSV`.**

CSV trên Clipboard thường xuất hiện dưới **Custom Clipboard Format** , và tên định dạng phụ thuộc vào ứng dụng.

Ví dụ:

  * Microsoft Excel 
  * LibreOffice Calc 
  * WPS Spreadsheet 
  * Google Sheets (qua trình duyệt) 



có thể cung cấp:
    
    
    CF_UNICODETEXT
    HTML Format
    Rich Text Format
    CSV
    CSV Format
    text/csv
    Biff8
    XML Spreadsheet
    ...

Tùy từng ứng dụng, có thể **không có CSV** , mà chỉ có HTML + Unicode Text.

Đây là lý do khi lập trình Clipboard bạn **không nên giả định luôn tồn tại CSV**.

* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu

  * CSV trên Clipboard hoạt động như thế nào 
  * Excel copy dữ liệu như thế nào 
  * Tại sao CSV không phải Standard Format 
  * Đọc CSV Clipboard 
  * Ghi CSV Clipboard 
  * Parse CSV 
  * Export sang SQLite 
  * Thiết kế `CsvClipboard`



* * *

# 1\. Copy từ Excel

Ví dụ
    
    
    Tên      Tuổi
    
    An       20
    
    Bình     25

Bạn nhấn
    
    
    Ctrl+C

Clipboard có thể chứa
    
    
    CF_UNICODETEXT
    
    HTML Format
    
    CSV
    
    Biff8
    
    ...

* * *

# 2\. Unicode Text

Nếu lấy
    
    
    GetClipboardData(
        CF_UNICODETEXT
    )

ta có
    
    
    Tên    Tuổi
    
    An     20
    
    Bình   25

Trong thực tế, dữ liệu thường được phân tách bằng **Tab (`\t`)** giữa các cột và **CRLF (`\r\n`)** giữa các hàng:
    
    
    Tên\tTuổi\r\nAn\t20\r\nBình\t25\r\n

Đó là định dạng mà nhiều ứng dụng bảng tính sử dụng.

* * *

# 3\. HTML

Nếu lấy
    
    
    HTML Format

↓
    
    
    <table>
    
    <tr>
    
    <td>An</td>
    
    <td>20</td>
    
    </tr>
    
    </table>

↓

Giữ

  * màu 
  * border 
  * merge cell 



* * *

# 4\. CSV

Một số chương trình còn thêm
    
    
    CSV

↓
    
    
    Tên,Tuổi
    
    An,20
    
    Bình,25

Đây chỉ là **một lựa chọn bổ sung** , không phải quy định bắt buộc của Windows.

* * *

# 5\. Đăng ký Format

Ví dụ
    
    
    import win32clipboard
    
    CF_CSV = win32clipboard.RegisterClipboardFormat(
        "CSV"
    )

Hoặc với một số ứng dụng khác:
    
    
    CF_TEXT_CSV = win32clipboard.RegisterClipboardFormat(
        "text/csv"
    )

Nếu ứng dụng không đăng ký định dạng này thì việc đăng ký vẫn thành công, nhưng `IsClipboardFormatAvailable()` sẽ trả về `False`.

* * *

# 6\. Kiểm tra
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        print(
            win32clipboard.IsClipboardFormatAvailable(
                CF_CSV
            )
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

* * *

# 7\. Đọc CSV
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        csv_text = win32clipboard.GetClipboardData(
            CF_CSV
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

Nếu không có định dạng CSV, bạn nên fallback sang `CF_UNICODETEXT` rồi phân tích dữ liệu dạng tab.

* * *

# 8\. Parse CSV

Python có thư viện chuẩn
    
    
    csv

Ví dụ
    
    
    import csv
    import io
    
    reader = csv.reader(
        io.StringIO(csv_text)
    )
    
    for row in reader:
    
        print(row)

↓
    
    
    ['Tên', 'Tuổi']
    
    ['An', '20']
    
    ['Bình', '25']

* * *

# 9\. DictReader
    
    
    reader = csv.DictReader(
        io.StringIO(csv_text)
    )
    
    for row in reader:
    
        print(row)

↓
    
    
    {
    'Tên':'An',
    
    'Tuổi':'20'
    }

Đây là cách rất tiện nếu hàng đầu tiên là tiêu đề cột.

* * *

# 10\. Ghi CSV
    
    
    import csv
    import io
    
    buffer = io.StringIO()
    
    writer = csv.writer(buffer)
    
    writer.writerow(
        ["Tên", "Tuổi"]
    )
    
    writer.writerow(
        ["An", 20]
    )
    
    csv_text = buffer.getvalue()

↓
    
    
    Tên,Tuổi
    
    An,20

* * *

# 11\. Ghi Clipboard
    
    
    win32clipboard.OpenClipboard()
    
    try:
    
        win32clipboard.EmptyClipboard()
    
        win32clipboard.SetClipboardData(
            CF_CSV,
            csv_text
        )
    
    finally:
    
        win32clipboard.CloseClipboard()

Trong thực tế, để các ứng dụng tương thích tốt hơn, bạn thường sẽ ghi **đồng thời** :

  * `CF_UNICODETEXT`
  * và định dạng CSV (nếu cần) 



* * *

# 12\. CsvClipboard
    
    
    import win32clipboard
    
    
    class CsvClipboard:
    
        FORMAT = win32clipboard.RegisterClipboardFormat(
            "CSV"
        )
    
        @classmethod
        def has_csv(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.IsClipboardFormatAvailable(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()
    
        @classmethod
        def csv(cls):
    
            win32clipboard.OpenClipboard()
    
            try:
    
                return win32clipboard.GetClipboardData(
                    cls.FORMAT
                )
    
            finally:
    
                win32clipboard.CloseClipboard()

* * *

# 13\. Chuyển SQLite

Ví dụ
    
    
    Clipboard
    
    ↓
    
    CSV
    
    ↓
    
    csv.reader
    
    ↓
    
    SQLite
    
    ↓
    
    Repository

Đây là cách rất tiện để nhập dữ liệu từ bảng tính vào cơ sở dữ liệu.

* * *

# 14\. Pandas

Có thể dùng
    
    
    import pandas as pd
    
    df = pd.read_csv(
        io.StringIO(csv_text)
    )
    
    print(df)

↓
    
    
    Tên   Tuổi
    
    An    20
    
    Bình  25

Rất hữu ích cho xử lý dữ liệu lớn.

* * *

# 15\. Kiến trúc
    
    
    clipboard/
    
    csv/
    
    ├── manager.py
    ├── parser.py
    ├── writer.py
    ├── dataframe.py
    ├── sqlite.py
    └── constants.py

* * *

# 16\. Ứng dụng thực tế

Excel

↓

Copy

↓

Clipboard

↓

CSV

↓

Python

↓

SQLite

↓

Dashboard

* * *

Hoặc

Google Sheets

↓

Clipboard

↓

CSV / Unicode Text

↓

Pandas

↓

Excel

* * *

Hoặc

CSV

↓

Clipboard

↓

Repository

↓

ORM

↓

Database

* * *

# 17\. Một Clipboard Manager thông minh

Thay vì:
    
    
    if has_csv():

Ta nên:
    
    
    Clipboard
    
    ↓
    
    CSV ?
    
    ↓
    
    YES
    
    ↓
    
    csv.reader()
    
    ↓
    
    NO
    
    ↓
    
    Unicode ?
    
    ↓
    
    YES
    
    ↓
    
    Parse Tab
    
    ↓
    
    NO
    
    ↓
    
    HTML ?
    
    ↓
    
    Parse Table

Đây là chiến lược mà nhiều ứng dụng chuyên nghiệp sử dụng để tăng khả năng tương thích.

* * *

# Bài tập

## Bài 1

Viết
    
    
    has_csv()

* * *

## Bài 2

Viết
    
    
    get_csv()

* * *

## Bài 3

Viết
    
    
    csv_to_list()

↓
    
    
    [
    ["Tên","Tuổi"],
    
    ["An","20"],
    
    ["Bình","25"]
    ]

* * *

## Bài 4

Viết
    
    
    csv_to_dict()

↓
    
    
    [
    {
    "Tên":"An",
    
    "Tuổi":"20"
    }
    ]

* * *

## Bài 5

Viết
    
    
    ClipboardTable

Có thể:

  * `load()`
  * `rows()`
  * `columns()`
  * `to_dataframe()`
  * `to_sqlite()`



* * *

# Mini Project

Viết chương trình
    
    
    Clipboard CSV Viewer
    
    =========================
    
    Rows : 2
    
    Columns : 2
    
    -------------------------
    
    Tên    Tuổi
    
    An      20
    
    Bình    25
    
    -------------------------
    
    Export SQLite ? (y/n)

* * *

# Tổng kết

Trong buổi này bạn đã học:

  * Windows **không có`CF_CSV` chuẩn**; CSV là **Custom Clipboard Format** nếu ứng dụng hỗ trợ. 
  * Cách đăng ký và kiểm tra định dạng CSV bằng `RegisterClipboardFormat()`. 
  * Cách đọc và ghi dữ liệu CSV trên Clipboard. 
  * Sử dụng module `csv` và `pandas` để phân tích dữ liệu. 
  * Chiến lược fallback sang `CF_UNICODETEXT` hoặc `HTML Format` khi CSV không có. 



* * *

# Chuẩn bị cho Buổi 10

Ở **Buổi 10** , chúng ta sẽ học về **Custom Clipboard Format** một cách chuyên sâu:

  * Cơ chế hoạt động của `RegisterClipboardFormat()`. 
  * Cách hai ứng dụng trao đổi dữ liệu bằng định dạng riêng. 
  * Thiết kế định dạng Clipboard cho chính ứng dụng của bạn (ví dụ: `StoryCrawler/Novel`, `MyApp/Bookmark`). 
  * Ghi và đọc các đối tượng Python (sau khi tuần tự hóa) thông qua Clipboard. 



Đây là bước giúp bạn xây dựng các ứng dụng Windows có khả năng trao đổi dữ liệu chuyên nghiệp và mở rộng vượt xa các định dạng chuẩn như Text, HTML hay RTF.

