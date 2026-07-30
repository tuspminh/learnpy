# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 1: Giới thiệu `pathlib` \- Quản lý đường dẫn hiện đại trong Python

> **Mục tiêu buổi học**

Sau buổi này bạn sẽ:

  * Hiểu vì sao `pathlib` được tạo ra. 
  * Biết sự khác nhau giữa `os.path` và `pathlib`. 
  * Thành thạo lớp `Path`. 
  * Biết cách tạo, nối và chuẩn hóa đường dẫn. 
  * Hiểu sự khác nhau giữa đường dẫn Windows và Linux. 
  * Viết được các đoạn code sạch, hiện đại bằng `pathlib`. 



* * *

# 1\. Vì sao `pathlib` ra đời?

Trước Python 3.4, việc thao tác với file thường sử dụng:
    
    
    import os
    
    path = os.path.join("downloads", "novel", "chapter1.txt")
    
    if os.path.exists(path):
        print(path)

Hoặc
    
    
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    extension = os.path.splitext(path)

Có rất nhiều hàm:

  * dirname() 
  * basename() 
  * split() 
  * splitext() 
  * exists() 
  * isdir() 
  * isfile() 



Mỗi chức năng là một hàm riêng.

Code nhanh trở nên dài và khó đọc.

Ví dụ:
    
    
    os.path.dirname(
        os.path.abspath(
            os.path.expanduser("~/Downloads")
        )
    )

Khá khó hiểu.

* * *

## pathlib giải quyết điều gì?

Ý tưởng rất đơn giản:

> "Đường dẫn cũng là một đối tượng."

Thay vì:
    
    
    os.path.exists(path)

Ta viết
    
    
    path.exists()

Thay vì
    
    
    os.path.basename(path)

Ta viết
    
    
    path.name

Code trở nên tự nhiên hơn rất nhiều.

* * *

# 2\. pathlib là gì?

`pathlib` là thư viện chuẩn (Standard Library).

Không cần cài đặt.

Chỉ cần:
    
    
    from pathlib import Path

Lớp quan trọng nhất là:
    
    
    Path

Gần như toàn bộ thư viện xoay quanh lớp này.

* * *

# 3\. Đối tượng Path

Ví dụ
    
    
    from pathlib import Path
    
    p = Path("downloads")

Lúc này
    
    
    print(type(p))

Kết quả
    
    
    <class 'pathlib.PosixPath'>

Trên Windows
    
    
    <class 'pathlib.WindowsPath'>

Nghĩa là:

`Path` không phải chuỗi (`str`).

Mà là một object.

Ví dụ
    
    
    from pathlib import Path
    
    p = Path("abc.txt")
    
    print(p)

Kết quả
    
    
    abc.txt

* * *

# 4\. Path hoạt động như một object

Ví dụ
    
    
    from pathlib import Path
    
    file = Path("image.png")
    
    print(file.name)

Kết quả
    
    
    image.png

Không cần
    
    
    os.path.basename(...)

* * *

# 5\. Tạo Path

## Ví dụ 1
    
    
    from pathlib import Path
    
    p = Path("data")

Kết quả
    
    
    data

* * *

## Ví dụ 2
    
    
    p = Path("data/books")

* * *

## Ví dụ 3
    
    
    p = Path("data/books/chapter1.txt")

* * *

## Ví dụ 4

Đường dẫn tuyệt đối

Windows
    
    
    Path(r"C:\Users\Admin\Desktop")

Linux
    
    
    Path("/home/admin/Desktop")

* * *

# 6\. Path không kiểm tra sự tồn tại

Nhiều người mới học nghĩ:
    
    
    Path("hello.txt")

Nếu file không tồn tại sẽ lỗi.

Không.

Nó chỉ tạo một đối tượng.

Ví dụ
    
    
    from pathlib import Path
    
    p = Path("abcxyz.txt")
    
    print(p)

Kết quả
    
    
    abcxyz.txt

Không hề báo lỗi.

* * *

# 7\. Đường dẫn tương đối (Relative Path)
    
    
    Path("images/logo.png")

Nó được hiểu là
    
    
    Thư mục hiện tại/images/logo.png

Ví dụ

Giả sử chương trình đang chạy ở
    
    
    C:/Project

thì
    
    
    Path("images/logo.png")

sẽ trỏ tới
    
    
    C:/Project/images/logo.png

* * *

# 8\. Đường dẫn tuyệt đối (Absolute Path)

Ví dụ
    
    
    Path("/home/user/data.txt")

Hoặc
    
    
    Path(r"C:\Python\data.txt")

Không phụ thuộc thư mục hiện tại.

* * *

# 9\. Lấy thư mục hiện tại
    
    
    from pathlib import Path
    
    print(Path.cwd())

Ví dụ
    
    
    D:\Crawler

Đây là thư mục chương trình đang chạy.

Ví dụ thực tế
    
    
    Crawler/
    
        app.py
    
        downloads/
    
        logs/

Nếu chạy
    
    
    print(Path.cwd())

Kết quả
    
    
    Crawler

* * *

# 10\. Thư mục Home
    
    
    from pathlib import Path
    
    print(Path.home())

Windows
    
    
    C:\Users\Admin

Linux
    
    
    /home/admin

Mac
    
    
    /Users/admin

* * *

# 11\. Toán tử `/`

Đây là điểm mình rất thích ở `pathlib`.

Ví dụ
    
    
    from pathlib import Path
    
    p = Path("downloads") / "novels"

Kết quả
    
    
    downloads/novels

Tiếp tục
    
    
    p = p / "chapter001.txt"

Kết quả
    
    
    downloads/novels/chapter001.txt

Không cần
    
    
    os.path.join(...)

* * *

Ví dụ dài
    
    
    from pathlib import Path
    
    file = (
        Path("downloads")
        / "novels"
        / "one_piece"
        / "chapter001.txt"
    )
    
    print(file)

Đọc rất tự nhiên.

* * *

# 12\. Path tự xử lý dấu phân cách

Bạn không cần quan tâm:

Windows
    
    
    \

Linux
    
    
    /

Ví dụ
    
    
    Path("downloads") / "books"

Windows
    
    
    downloads\books

Linux
    
    
    downloads/books

Python tự xử lý.

* * *

# 13\. Chuyển sang chuỗi

Đôi khi thư viện khác cần `str`.

Ví dụ
    
    
    path = Path("logs/log.txt")
    
    print(str(path))

Kết quả
    
    
    logs/log.txt

* * *

# 14\. Ví dụ thực tế

Giả sử bạn làm crawler.

Thay vì
    
    
    import os
    
    save_dir = os.path.join(
        "downloads",
        "novel",
        "one_piece"
    )
    
    filename = os.path.join(
        save_dir,
        "chapter001.txt"
    )

Bạn chỉ cần
    
    
    from pathlib import Path
    
    filename = (
        Path("downloads")
        / "novel"
        / "one_piece"
        / "chapter001.txt"
    )
    
    print(filename)

Code ngắn hơn rất nhiều.

* * *

# 15\. Áp dụng cho dự án cào truyện

Một cấu trúc thư mục điển hình:
    
    
    crawler/
    
    │
    
    ├── app.py
    
    ├── config/
    
    ├── downloads/
    
    │      ├── novels/
    
    │      ├── comics/
    
    │      └── images/
    
    ├── cache/
    
    ├── logs/
    
    ├── database/
    
    └── assets/

Ta có thể định nghĩa các đường dẫn:
    
    
    from pathlib import Path
    
    BASE_DIR = Path.cwd()
    
    CONFIG_DIR = BASE_DIR / "config"
    
    DOWNLOAD_DIR = BASE_DIR / "downloads"
    
    CACHE_DIR = BASE_DIR / "cache"
    
    LOG_DIR = BASE_DIR / "logs"
    
    DATABASE_DIR = BASE_DIR / "database"
    
    ASSET_DIR = BASE_DIR / "assets"

Sau này chỉ cần dùng:
    
    
    cover = DOWNLOAD_DIR / "images" / "cover.jpg"
    
    chapter = DOWNLOAD_DIR / "novels" / "chapter001.txt"
    
    log = LOG_DIR / "crawler.log"

Nếu sau này thay đổi vị trí dự án, bạn chỉ cần cập nhật `BASE_DIR`, toàn bộ đường dẫn còn lại sẽ tự động thay đổi theo.

* * *

# 16\. Bài tập thực hành

## Bài 1

Tạo các đối tượng `Path` sau:

  * `downloads`
  * `downloads/images`
  * `downloads/images/cover.jpg`



In ra màn hình.

* * *

## Bài 2

In ra:

  * `Path.cwd()`
  * `Path.home()`



* * *

## Bài 3

Sử dụng toán tử `/` để tạo đường dẫn:
    
    
    project/
        logs/
            crawler.log

* * *

## Bài 4

Tạo cấu hình đường dẫn cho dự án:
    
    
    project/
    
    config/
    
    downloads/
    
    cache/
    
    logs/
    
    database/
    
    assets/

Sử dụng biến:
    
    
    BASE_DIR
    CONFIG_DIR
    DOWNLOAD_DIR
    CACHE_DIR
    LOG_DIR
    DATABASE_DIR
    ASSET_DIR

* * *

## Bài 5 (Thực tế)

Viết chương trình in ra các đường dẫn sau bằng `pathlib`:
    
    
    downloads/novels/one_piece/chapter001.txt
    
    downloads/images/cover.jpg
    
    logs/error.log
    
    database/crawler.db

* * *

# Tổng kết buổi 1

Bạn đã nắm được những nền tảng quan trọng của `pathlib`:

  * Hiểu vai trò của `pathlib` và lý do thay thế `os.path`. 
  * Tạo và sử dụng đối tượng `Path`. 
  * Phân biệt đường dẫn tương đối và tuyệt đối. 
  * Sử dụng `Path.cwd()` và `Path.home()`. 
  * Ghép đường dẫn bằng toán tử `/`, giúp mã nguồn gọn gàng và đa nền tảng. 
  * Xây dựng các hằng số đường dẫn cho một dự án thực tế. 



Ở **Buổi 2** , chúng ta sẽ đi sâu vào cách **kiểm tra sự tồn tại của file/thư mục và đọc thông tin hệ thống file** , bao gồm `exists()`, `is_file()`, `is_dir()`, `is_symlink()`, `stat()` và nhiều ví dụ thực tế liên quan đến hệ thống cào truyện.

