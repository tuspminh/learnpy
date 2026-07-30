# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 2: Kiểm tra File, Thư mục và lấy thông tin hệ thống (`exists()`, `is_file()`, `is_dir()`, `stat()`...)

> **Mục tiêu**

Sau buổi này bạn sẽ có thể:

  * Kiểm tra file/thư mục có tồn tại hay không. 
  * Phân biệt file, thư mục và symbolic link. 
  * Đọc thông tin chi tiết của file. 
  * Lấy kích thước, thời gian tạo, thời gian sửa. 
  * Hiểu cách `pathlib` tương tác với hệ điều hành. 
  * Áp dụng vào dự án **Crawler + PySide6 + SQLite**. 



* * *

# 1\. Ôn tập buổi trước

Tạo một `Path`:
    
    
    from pathlib import Path
    
    file = Path("downloads/chapter001.txt")

Lưu ý:

  * Chưa kiểm tra file có tồn tại. 
  * Chưa tạo file. 
  * Chỉ tạo một đối tượng `Path`. 



* * *

# 2\. Kiểm tra đường dẫn có tồn tại: `exists()`

Đây là hàm được sử dụng nhiều nhất trong `pathlib`.
    
    
    from pathlib import Path
    
    file = Path("test.txt")
    
    print(file.exists())

Nếu file tồn tại:
    
    
    True

Nếu không tồn tại:
    
    
    False

### Ví dụ
    
    
    from pathlib import Path
    
    paths = [
        Path("README.md"),
        Path("config.json"),
        Path("downloads"),
        Path("abcxyz.txt")
    ]
    
    for p in paths:
        print(f"{p} -> {p.exists()}")

Ví dụ kết quả:
    
    
    README.md -> True
    config.json -> False
    downloads -> True
    abcxyz.txt -> False

* * *

# 3\. `exists()` hoạt động như thế nào?

Giả sử
    
    
    project/
    
    ├── app.py
    ├── downloads/
    ├── logs/
    └── database/

Nếu
    
    
    Path("downloads").exists()

↓

Python hỏi hệ điều hành:

> "Có thư mục downloads không?"

Hệ điều hành trả lời:
    
    
    True

Nếu
    
    
    Path("abc").exists()

↓
    
    
    False

* * *

# 4\. Kiểm tra có phải File không: `is_file()`
    
    
    from pathlib import Path
    
    p = Path("README.md")
    
    print(p.is_file())

Kết quả:
    
    
    True

Nếu
    
    
    Path("downloads")

↓
    
    
    print(Path("downloads").is_file())

Kết quả
    
    
    False

* * *

## Ví dụ
    
    
    project/
    
    README.md
    
    downloads/
    
    config.json
    
    
    from pathlib import Path
    
    items = [
        Path("README.md"),
        Path("downloads"),
        Path("config.json")
    ]
    
    for p in items:
        print(p, p.is_file())

Kết quả
    
    
    README.md True
    
    downloads False
    
    config.json True

* * *

# 5\. Kiểm tra thư mục: `is_dir()`

Ngược lại.
    
    
    Path("downloads").is_dir()

↓
    
    
    True
    
    
    Path("README.md").is_dir()

↓
    
    
    False

* * *

## So sánh

Đường dẫn| exists| is_file| is_dir  
---|---|---|---  
File| ✅| ✅| ❌  
Folder| ✅| ❌| ✅  
Không tồn tại| ❌| ❌| ❌  
  
Đây là bảng rất quan trọng cần nhớ.

* * *

# 6\. Ví dụ thực tế

Không nên
    
    
    if file.exists():
        print("Đọc file")

Vì có thể
    
    
    file

lại là thư mục.

Đúng hơn
    
    
    if file.exists() and file.is_file():
        print("Đọc file")

* * *

# 7\. Kiểm tra Symbolic Link

Trong Linux hoặc macOS
    
    
    shortcut
    ↓
    
    real file

Đây gọi là
    
    
    Symbolic Link

Kiểm tra
    
    
    Path("shortcut").is_symlink()

↓
    
    
    True

Nếu không phải
    
    
    False

Trong các dự án crawler trên Windows, bạn sẽ ít dùng nhưng khi triển khai trên Linux server thì rất hữu ích.

* * *

# 8\. Lấy thông tin File: `stat()`

Đây là hàm cực kỳ mạnh.
    
    
    from pathlib import Path
    
    file = Path("README.md")
    
    info = file.stat()
    
    print(info)

Ví dụ
    
    
    os.stat_result(
        st_mode=33206,
        st_size=10240,
        st_atime=...
        st_mtime=...
    )

* * *

# 9\. `stat()` trả về gì?

Một đối tượng
    
    
    os.stat_result

Có rất nhiều thuộc tính.

Quan trọng nhất là:
    
    
    st_size
    
    st_mtime
    
    st_ctime
    
    st_atime
    
    st_mode

* * *

# 10\. Kích thước File
    
    
    from pathlib import Path
    
    file = Path("movie.mp4")
    
    print(file.stat().st_size)

Ví dụ
    
    
    10485760

Đơn vị
    
    
    Byte

* * *

## Đổi sang KB
    
    
    size = file.stat().st_size / 1024
    
    print(size)

* * *

## MB
    
    
    size = file.stat().st_size / (1024 * 1024)
    
    print(size)

* * *

## GB
    
    
    size = file.stat().st_size / (1024**3)
    
    print(size)

* * *

# 11\. Thời gian sửa cuối
    
    
    file.stat().st_mtime

Kết quả
    
    
    1719922222.52

Đây là Unix Timestamp.

Chuyển thành ngày
    
    
    from datetime import datetime
    
    t = file.stat().st_mtime
    
    print(datetime.fromtimestamp(t))

Ví dụ
    
    
    2026-07-13 09:15:23

* * *

# 12\. Thời gian truy cập
    
    
    file.stat().st_atime

* * *

# 13\. Thời gian tạo
    
    
    file.stat().st_ctime

Lưu ý:

  * Trên Windows thường là thời gian tạo. 
  * Trên Linux có thể là thời gian thay đổi metadata, không phải lúc tạo file. 



Không nên viết chương trình phụ thuộc vào ý nghĩa của `st_ctime` nếu cần chạy đa nền tảng.

* * *

# 14\. Quyền truy cập (`st_mode`)
    
    
    mode = file.stat().st_mode
    
    print(mode)

Có thể dùng với module `stat` để kiểm tra quyền đọc/ghi/thực thi.

Chúng ta sẽ học kỹ hơn ở buổi về quyền truy cập và `chmod()`.

* * *

# 15\. Ví dụ: Liệt kê thông tin file
    
    
    from pathlib import Path
    from datetime import datetime
    
    file = Path("README.md")
    
    if file.exists() and file.is_file():
        info = file.stat()
    
        print("Tên:", file.name)
        print("Kích thước:", info.st_size, "bytes")
        print("Sửa lần cuối:", datetime.fromtimestamp(info.st_mtime))

* * *

# 16\. Hàm tiện ích: Hiển thị kích thước dễ đọc
    
    
    from pathlib import Path
    
    def format_size(size):
        units = ["B", "KB", "MB", "GB", "TB"]
    
        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
    
        return f"{size:.2f} PB"
    
    
    file = Path("movie.mp4")
    
    if file.exists():
        print(format_size(file.stat().st_size))

Ví dụ
    
    
    2.34 GB

* * *

# 17\. Ứng dụng trong dự án Crawler

Giả sử cấu trúc:
    
    
    downloads/
    
        One Piece/
    
            chapter001.txt
    
            chapter002.txt
    
    images/
    
    cache/
    
    logs/

Trước khi tải chương mới:
    
    
    chapter = Path(
        "downloads/One Piece/chapter001.txt"
    )
    
    if chapter.exists():
        print("Đã tải, bỏ qua")
    else:
        print("Tiến hành tải")

* * *

## Kiểm tra cache
    
    
    cache = Path("cache/index.json")
    
    if cache.exists():
        print("Đọc cache")
    else:
        print("Tạo cache")

* * *

## Kiểm tra database
    
    
    db = Path("database/crawler.db")
    
    if not db.exists():
        print("Khởi tạo SQLite")

* * *

# 18\. Ví dụ tổng hợp
    
    
    from pathlib import Path
    from datetime import datetime
    
    path = Path("downloads/chapter001.txt")
    
    if not path.exists():
        print("Không tồn tại")
    
    elif path.is_dir():
        print("Là thư mục")
    
    elif path.is_file():
        info = path.stat()
    
        print("Tên:", path.name)
        print("Dung lượng:", info.st_size)
        print(
            "Sửa:",
            datetime.fromtimestamp(info.st_mtime)
        )

* * *

# 19\. Những lỗi thường gặp

### Sai
    
    
    Path("abc.txt").stat()

Nếu file không tồn tại:
    
    
    FileNotFoundError

Đúng:
    
    
    p = Path("abc.txt")
    
    if p.exists():
        print(p.stat())

Hoặc xử lý ngoại lệ:
    
    
    from pathlib import Path
    
    try:
        info = Path("abc.txt").stat()
        print(info)
    except FileNotFoundError:
        print("File không tồn tại.")

* * *

# 20\. Bài tập thực hành

## Bài 1

Tạo thư mục thử nghiệm:
    
    
    practice/
    
        data/
    
        images/
    
        logs/

Kiểm tra với:

  * `exists()`
  * `is_file()`
  * `is_dir()`



* * *

## Bài 2

Tạo file:
    
    
    hello.txt

In:

  * tên file 
  * kích thước 
  * thời gian sửa cuối 



* * *

## Bài 3

Viết hàm:
    
    
    def file_info(path):
        ...

Hiển thị:

  * tồn tại? 
  * file hay thư mục? 
  * dung lượng 
  * thời gian sửa 



* * *

## Bài 4

Trong thư mục `downloads`, duyệt qua tất cả các mục và in:
    
    
    Tên
    
    Loại (FILE/FOLDER)
    
    Dung lượng (nếu là file)

* * *

## Bài 5 (Dự án thực tế)

Viết một lớp `StorageManager` để quản lý các đường dẫn của hệ thống cào truyện:
    
    
    from pathlib import Path
    
    class StorageManager:
        def __init__(self, base_dir: Path):
            self.base_dir = base_dir
            self.downloads = base_dir / "downloads"
            self.cache = base_dir / "cache"
            self.logs = base_dir / "logs"
            self.database = base_dir / "database"
    
        def check_environment(self):
            """Kiểm tra các thư mục cần thiết đã tồn tại hay chưa."""
            for path in [self.downloads, self.cache, self.logs, self.database]:
                print(f"{path}: {'OK' if path.exists() else 'Thiếu'}")

Đây sẽ là nền tảng để sau này tích hợp với PySide6, SQLite và hệ thống giám sát crawler của bạn.

* * *

# Tổng kết buổi 2

Trong buổi học này, bạn đã nắm được các phương thức quan trọng nhất để làm việc với hệ thống file:

  * `exists()` để kiểm tra đường dẫn có tồn tại. 
  * `is_file()` và `is_dir()` để phân biệt file và thư mục. 
  * `is_symlink()` để nhận biết symbolic link. 
  * `stat()` để lấy thông tin chi tiết như kích thước, thời gian truy cập, thời gian sửa và quyền truy cập. 
  * Chuyển đổi `st_mtime` từ Unix timestamp sang `datetime`. 
  * Áp dụng các kiến thức này vào kiểm tra môi trường và quản lý dữ liệu cho một dự án crawler. 



Ở **Buổi 3** , chúng ta sẽ tìm hiểu nhóm thuộc tính giúp **phân tích cấu trúc đường dẫn** , bao gồm `name`, `stem`, `suffix`, `suffixes`, `parent`, `parents` và `parts`. Đây là những công cụ rất quan trọng khi xử lý tên file, đổi đuôi file, tổ chức thư mục và xây dựng các công cụ tải truyện hoặc quản lý tài nguyên.

