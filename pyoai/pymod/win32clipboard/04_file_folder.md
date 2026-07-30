# Khóa học win32clipboard Deep Dive

# Buổi 4: CF_HDROP - Làm việc với File và Folder trên Windows Clipboard

Đây là một trong những định dạng Clipboard hữu ích nhất nếu bạn phát triển ứng dụng Windows.

Rất nhiều ứng dụng như:

  * File Explorer 
  * Total Commander 
  * Everything 
  * Directory Opus 
  * 7-Zip 
  * WinRAR 
  * Visual Studio Code 



đều sử dụng **CF_HDROP** để trao đổi danh sách file và thư mục.

Sau buổi này, bạn sẽ có thể viết các chương trình như:

  * File Drop Inspector 
  * Batch Rename Tool 
  * File Automation 
  * Clipboard File Manager 
  * Auto Backup Tool 



* * *

# Mục tiêu

Sau buổi học bạn sẽ hiểu:

  * CF_HDROP là gì? 
  * Cấu trúc dữ liệu của File Clipboard 
  * Đọc danh sách file 
  * Đọc danh sách thư mục 
  * Phân biệt Copy và Cut 
  * Preferred DropEffect 
  * Thiết kế `FileClipboardManager`



* * *

# 1\. Khi Copy một file thì Clipboard chứa gì?

Ví dụ:
    
    
    Ctrl + C
    
    example.txt

Nhiều người nghĩ Clipboard chứa:
    
    
    C:\Temp\example.txt

Điều này **không đúng**.

Windows lưu:
    
    
    Clipboard
    
    ├── CF_HDROP
    ├── Preferred DropEffect
    ├── Shell Object Offsets
    ├── ...

Trong đó:

  * `CF_HDROP`: danh sách đường dẫn. 
  * `Preferred DropEffect`: cho biết thao tác là Copy hay Cut. 
  * Các định dạng khác phục vụ Windows Explorer. 



* * *

# 2\. CF_HDROP

Đây là Clipboard Format có ID:
    
    
    15

Trong pywin32:
    
    
    win32clipboard.CF_HDROP

* * *

# 3\. Copy nhiều file

Ví dụ:
    
    
    A.txt
    
    B.txt
    
    C.txt

Clipboard không lưu từng file riêng lẻ.

Nó lưu:
    
    
    [
        "A.txt",
        "B.txt",
        "C.txt"
    ]

* * *

# 4\. Đọc danh sách file

Ví dụ đơn giản:
    
    
    import win32clipboard
    
    win32clipboard.OpenClipboard()
    
    try:
    
        if win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_HDROP):
    
            files = win32clipboard.GetClipboardData(
                win32clipboard.CF_HDROP
            )
    
            print(files)
    
    finally:
    
        win32clipboard.CloseClipboard()

Ví dụ kết quả:
    
    
    (
     'C:\\Temp\\A.txt',
     'C:\\Temp\\B.txt',
     'D:\\Music'
    )

Lưu ý:

`GetClipboardData(CF_HDROP)` trả về **tuple** , không phải list.

* * *

# 5\. Vì sao là tuple?

Windows trả về dữ liệu chỉ đọc (read-only).

Pywin32 chuyển thành:
    
    
    tuple[str, ...]

Nếu cần chỉnh sửa:
    
    
    files = list(files)

* * *

# 6\. Duyệt từng file
    
    
    for path in files:
        print(path)

Ví dụ:
    
    
    C:\Temp\A.txt
    
    C:\Temp\B.txt
    
    D:\Music

* * *

# 7\. File hay Folder?

Sử dụng `pathlib`:
    
    
    from pathlib import Path
    
    for item in files:
    
        p = Path(item)
    
        if p.is_file():
            print("File :", p)
    
        elif p.is_dir():
            print("Folder :", p)

Đây là cách hiện đại và dễ đọc hơn so với `os.path`.

* * *

# 8\. Thông tin file
    
    
    from pathlib import Path
    
    for item in files:
    
        p = Path(item)
    
        print("Name :", p.name)
    
        print("Stem :", p.stem)
    
        print("Suffix :", p.suffix)
    
        print("Parent :", p.parent)

Ví dụ:
    
    
    Name:
    story.pdf
    
    Stem:
    story
    
    Suffix:
    .pdf
    
    Parent:
    C:\Books

* * *

# 9\. Lọc theo Extension
    
    
    for item in files:
    
        p = Path(item)
    
        if p.suffix.lower() == ".pdf":
    
            print(p)

Hoặc:
    
    
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    
    for item in files:
        p = Path(item)
        if p.suffix.lower() in IMAGE_EXTENSIONS:
            print("Ảnh:", p)

* * *

# 10\. Chỉ lấy Folder
    
    
    folders = []
    
    for item in files:
    
        p = Path(item)
    
        if p.is_dir():
    
            folders.append(p)

* * *

# 11\. Chỉ lấy File
    
    
    real_files = []
    
    for item in files:
    
        p = Path(item)
    
        if p.is_file():
    
            real_files.append(p)

* * *

# 12\. File Clipboard Manager

Thiết kế OOP:
    
    
    from pathlib import Path
    
    import win32clipboard
    
    
    class FileClipboard:
    
        @staticmethod
        def files():
    
            win32clipboard.OpenClipboard()
    
            try:
    
                if not win32clipboard.IsClipboardFormatAvailable(
                        win32clipboard.CF_HDROP):
    
                    return []
    
                return [
                    Path(f)
                    for f in win32clipboard.GetClipboardData(
                        win32clipboard.CF_HDROP
                    )
                ]
    
            finally:
    
                win32clipboard.CloseClipboard()

Sử dụng:
    
    
    for f in FileClipboard.files():
    
        print(f)

* * *

# 13\. Thêm các phương thức tiện ích
    
    
    class FileClipboard:
    
        ...
    
        @classmethod
        def file_count(cls):
    
            return len(cls.files())
    
        @classmethod
        def folders(cls):
    
            return [
                p
                for p in cls.files()
                if p.is_dir()
            ]
    
        @classmethod
        def regular_files(cls):
    
            return [
                p
                for p in cls.files()
                if p.is_file()
            ]

Sử dụng:
    
    
    print(FileClipboard.file_count())
    
    print(FileClipboard.folders())
    
    print(FileClipboard.regular_files())

* * *

# 14\. Copy hay Cut?

Đây là phần thú vị.

Bạn:
    
    
    Ctrl + C

và
    
    
    Ctrl + X

đều tạo ra:
    
    
    CF_HDROP

Vậy Windows phân biệt thế nào?

Nó dùng:
    
    
    Preferred DropEffect

Đây là **Custom Clipboard Format**.

Không phải:
    
    
    CF_HDROP

* * *

# 15\. Preferred DropEffect

Windows Explorer thêm:
    
    
    Preferred DropEffect

Giá trị:
    
    
    1

=
    
    
    Copy

Giá trị:
    
    
    2

=
    
    
    Move

Định dạng này không có hằng số dựng sẵn trong `win32clipboard`; cần đăng ký/tìm ID bằng `RegisterClipboardFormat("Preferred DropEffect")` rồi đọc dữ liệu thô. Chúng ta sẽ thực hành chi tiết ở buổi nâng cao.

* * *

# 16\. Kiểm tra có File không
    
    
    def has_files():
    
        win32clipboard.OpenClipboard()
    
        try:
    
            return win32clipboard.IsClipboardFormatAvailable(
                win32clipboard.CF_HDROP
            )
    
        finally:
    
            win32clipboard.CloseClipboard()

* * *

# 17\. Clipboard Inspector phiên bản nâng cấp
    
    
    if has_files():
    
        for item in FileClipboard.files():
    
            print(item)

Ví dụ:
    
    
    D:\Movies
    
    D:\Books
    
    C:\Temp\a.txt

* * *

# 18\. Ứng dụng thực tế

Bạn có thể tạo:

## Auto Rename
    
    
    Ctrl+C File
    
    ↓
    
    Python
    
    ↓
    
    Rename
    
    ↓
    
    Xuất danh sách

* * *

## Auto Backup
    
    
    Ctrl+C Folder
    
    ↓
    
    Python
    
    ↓
    
    Zip
    
    ↓
    
    Backup

* * *

## Story Import Tool

Đây là ví dụ sát với dự án **story_crawler** mà chúng ta đang xây dựng.

Người dùng:
    
    
    Ctrl+C

một thư mục:
    
    
    Novel1
    
    Novel2
    
    Novel3

Python:
    
    
    ↓
    
    Đọc CF_HDROP
    
    ↓
    
    Quét thư mục
    
    ↓
    
    Import SQLite
    
    ↓
    
    Hiển thị GUI

Không cần người dùng nhập đường dẫn bằng tay.

* * *

# 19\. Kiến trúc đề xuất
    
    
    clipboard/
    │
    ├── manager.py
    ├── text.py
    ├── files.py
    ├── images.py
    ├── formats.py
    ├── inspector.py
    └── context.py

Trong đó:
    
    
    files.py
    
    
    class FileClipboard
    
    ↓
    
    files()
    
    ↓
    
    folders()
    
    ↓
    
    regular_files()
    
    ↓
    
    file_count()

Các module này tách biệt trách nhiệm, giúp mã dễ bảo trì và mở rộng.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    list_files()

Trả về:
    
    
    list[Path]

* * *

## Bài 2

Viết:
    
    
    list_folders()

* * *

## Bài 3

Viết:
    
    
    list_images()

Chỉ lấy:
    
    
    jpg
    
    png
    
    gif
    
    bmp
    
    jpeg
    
    webp

* * *

## Bài 4

Viết:
    
    
    class FileClipboard

Có đầy đủ:

  * `has_files()`
  * `files()`
  * `folders()`
  * `regular_files()`
  * `file_count()`



* * *

## Bài 5 (Nâng cao)

Viết một chương trình dòng lệnh:
    
    
    ===== Clipboard File Inspector =====
    
    Có file trong Clipboard: Có
    
    Số lượng: 4
    
    1. C:\Book\a.pdf
       Loại: File
    
    2. D:\Novel
       Loại: Folder
    
    3. C:\Image\cover.png
       Loại: File
    
    4. D:\Music
       Loại: Folder

Chương trình nên:

  * Kiểm tra `CF_HDROP`. 
  * Phân loại từng mục là file hay thư mục. 
  * Hiển thị tên, đường dẫn và tổng số lượng. 



* * *

# Tổng kết

Buổi này bạn đã học:

  * Hiểu `CF_HDROP` là định dạng chuẩn để trao đổi danh sách file/thư mục trên Windows Clipboard. 
  * Đọc và xử lý danh sách đường dẫn bằng `GetClipboardData(CF_HDROP)`. 
  * Kết hợp `pathlib.Path` để phân tích và phân loại file/thư mục. 
  * Khái niệm `Preferred DropEffect` để phân biệt **Copy** và **Cut**. 
  * Thiết kế một lớp `FileClipboard` theo hướng OOP để tái sử dụng trong các dự án. 



Ở **Buổi 5** , chúng ta sẽ chuyển sang một chủ đề phức tạp hơn nhiều: **`CF_BITMAP` và `CF_DIB`**. Bạn sẽ học cách đọc ảnh từ Clipboard, chuyển đổi dữ liệu sang `Pillow (PIL.Image)`, lưu ảnh thành PNG/JPEG và xây dựng một **Clipboard Image Manager** giống như các công cụ chụp màn hình chuyên nghiệp.

