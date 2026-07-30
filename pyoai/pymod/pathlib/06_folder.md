# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 6: Quản lý File và Thư mục (`mkdir()`, `touch()`, `unlink()`, `rename()`, `replace()`, `rmdir()`)

> **Mục tiêu**

Sau buổi học này, bạn sẽ:

  * Thành thạo tạo và xóa file, thư mục. 
  * Hiểu sự khác nhau giữa `rename()` và `replace()`. 
  * Biết cách tạo cây thư mục tự động. 
  * Hiểu khi nào dùng `touch()`. 
  * Áp dụng để xây dựng hệ thống lưu trữ cho dự án **Crawler + PySide6 + SQLite**. 



* * *

# 1\. Tạo thư mục - `mkdir()`

Đây là hàm được dùng rất nhiều.
    
    
    from pathlib import Path
    
    Path("downloads").mkdir()

Nếu chưa có thư mục:
    
    
    downloads/

sẽ được tạo.

* * *

# 2\. Nếu thư mục đã tồn tại?
    
    
    Path("downloads").mkdir()

↓
    
    
    FileExistsError

Đây là lỗi rất nhiều người mới gặp.

* * *

# 3\. `exist_ok=True`

Cách chuyên nghiệp:
    
    
    Path("downloads").mkdir(exist_ok=True)

Nếu thư mục đã tồn tại:

→ Không báo lỗi.

Đây là cách nên sử dụng trong hầu hết dự án.

* * *

# 4\. `parents=True`

Giả sử muốn tạo
    
    
    downloads/
        novels/
            One Piece/

Nếu chỉ viết
    
    
    Path("downloads/novels/One Piece").mkdir()

↓

Lỗi
    
    
    FileNotFoundError

vì
    
    
    downloads

chưa tồn tại.

* * *

Cách đúng
    
    
    Path(
        "downloads/novels/One Piece"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

Python sẽ tạo toàn bộ cây thư mục.

* * *

# 5\. Minh họa

Trước
    
    
    project/

Sau
    
    
    Path(
        "downloads/comics/Naruto"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

Kết quả
    
    
    project/
    
        downloads/
    
            comics/
    
                Naruto/

* * *

# 6\. `touch()`

Dùng để tạo file rỗng.
    
    
    from pathlib import Path
    
    Path("log.txt").touch()

Kết quả
    
    
    log.txt

↓

Dung lượng
    
    
    0 byte

* * *

## Ví dụ
    
    
    Path(
        "database.db"
    ).touch()

↓
    
    
    database.db

* * *

# 7\. Nếu file đã tồn tại?
    
    
    Path("log.txt").touch()

↓

Không có lỗi.

File vẫn giữ nguyên.

* * *

# 8\. `touch(exist_ok=False)`
    
    
    Path("log.txt").touch(
        exist_ok=False
    )

Nếu file tồn tại

↓
    
    
    FileExistsError

* * *

# 9\. `unlink()`

Xóa file.
    
    
    Path("hello.txt").unlink()

↓
    
    
    hello.txt

đã bị xóa.

* * *

## Nếu file không tồn tại
    
    
    Path("abc.txt").unlink()

↓
    
    
    FileNotFoundError

* * *

## Python 3.8+

Có thể dùng
    
    
    Path("abc.txt").unlink(
        missing_ok=True
    )

↓

Không báo lỗi.

* * *

# 10\. Không dùng `unlink()` để xóa thư mục

Sai
    
    
    Path("downloads").unlink()

↓
    
    
    IsADirectoryError

`unlink()` chỉ dùng cho file hoặc symbolic link.

* * *

# 11\. `rmdir()`

Xóa thư mục.
    
    
    Path("downloads").rmdir()

Điều kiện:

Thư mục phải rỗng.

* * *

Ví dụ
    
    
    downloads/

↓

OK

* * *

Nhưng
    
    
    downloads/
    
        chapter001.txt

↓
    
    
    OSError

vì thư mục không rỗng.

* * *

# 12\. Xóa cả cây thư mục

`pathlib` không có hàm riêng.

Dùng `shutil`.
    
    
    import shutil
    
    shutil.rmtree("downloads")

Chúng ta sẽ học chi tiết ở buổi sau.

* * *

# 13\. `rename()`

Đổi tên.
    
    
    Path("old.txt").rename(
        "new.txt"
    )

↓
    
    
    old.txt
    
    ↓
    
    new.txt

* * *

Đổi tên thư mục
    
    
    Path("Novel").rename(
        "One Piece"
    )

↓
    
    
    Novel/
    
    ↓
    
    One Piece/

* * *

# 14\. Di chuyển file
    
    
    Path(
        "chapter001.txt"
    ).rename(
        "downloads/chapter001.txt"
    )

↓

File sẽ được di chuyển.

* * *

# 15\. `replace()`

Rất giống `rename()`.

Điểm khác biệt:

Nếu đích đã tồn tại
    
    
    source.replace(target)

↓

File đích sẽ bị ghi đè.

* * *

Ví dụ
    
    
    A.txt
    
    B.txt
    
    
    Path("A.txt").replace(
        "B.txt"
    )

↓
    
    
    B.txt

chứa nội dung của `A.txt`.

* * *

# 16\. So sánh

Hàm| Ghi đè file đích  
---|---  
rename()| Phụ thuộc hệ điều hành  
replace()| Luôn ghi đè  
  
Trong các dự án đồng bộ dữ liệu hoặc crawler, nếu bạn muốn chắc chắn file đích được thay thế thì nên dùng `replace()`.

* * *

# 17\. Ví dụ thực tế

Crawler tải
    
    
    chapter001.tmp

Sau khi tải hoàn tất

↓
    
    
    tmp = Path("chapter001.tmp")
    
    tmp.replace("chapter001.txt")

Nếu chương cũ tồn tại

↓

Sẽ được thay thế.

Đây là kỹ thuật thường dùng để tránh tạo ra file chưa tải xong nếu chương trình bị dừng giữa chừng.

* * *

# 18\. Tạo môi trường dự án
    
    
    from pathlib import Path
    
    folders = [
        "downloads",
        "cache",
        "logs",
        "database",
        "assets"
    ]
    
    for folder in folders:
        Path(folder).mkdir(
            exist_ok=True
        )

* * *

# 19\. Tạo cây thư mục
    
    
    novels = [
        "Naruto",
        "One Piece",
        "Conan"
    ]
    
    for novel in novels:
        (
            Path("downloads")
            / novel
        ).mkdir(
            parents=True,
            exist_ok=True
        )

Kết quả
    
    
    downloads/
    
        Naruto/
    
        One Piece/
    
        Conan/

* * *

# 20\. Tạo log
    
    
    log = Path("logs/crawler.log")
    
    log.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    log.touch()

Nếu:
    
    
    logs/

chưa có

↓

Python sẽ tạo trước.

* * *

# 21\. Tạo SQLite Database
    
    
    db = Path("database/crawler.db")
    
    db.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    db.touch()

Trong thực tế, khi kết nối SQLite bằng `sqlite3.connect()`, file cơ sở dữ liệu sẽ tự được tạo nếu chưa tồn tại. Tuy nhiên, việc chủ động tạo thư mục cha trước vẫn là rất cần thiết.

* * *

# 22\. Ví dụ hoàn chỉnh
    
    
    from pathlib import Path
    
    BASE = Path.cwd()
    
    DOWNLOAD = BASE / "downloads"
    CACHE = BASE / "cache"
    LOG = BASE / "logs"
    DB = BASE / "database"
    
    for folder in [
        DOWNLOAD,
        CACHE,
        LOG,
        DB
    ]:
        folder.mkdir(
            parents=True,
            exist_ok=True
        )
    
    (LOG / "crawler.log").touch()
    
    (DB / "crawler.db").touch()

* * *

# 23\. Thiết kế lớp Environment
    
    
    from pathlib import Path
    
    class Environment:
    
        def __init__(self, root):
            self.root = Path(root)
    
            self.download = self.root / "downloads"
            self.cache = self.root / "cache"
            self.logs = self.root / "logs"
            self.database = self.root / "database"
    
        def initialize(self):
            for folder in [
                self.download,
                self.cache,
                self.logs,
                self.database
            ]:
                folder.mkdir(
                    parents=True,
                    exist_ok=True
                )
    
            (self.logs / "crawler.log").touch()
    
            (self.database / "crawler.db").touch()

Sử dụng
    
    
    env = Environment(".")
    
    env.initialize()

* * *

# 24\. Ứng dụng trong hệ thống Crawler

Giả sử crawler tải chương:
    
    
    downloads/
    
        One Piece/
    
            chapter001.tmp

Sau khi tải xong:
    
    
    tmp = (
        Path("downloads")
        / "One Piece"
        / "chapter001.tmp"
    )
    
    txt = tmp.with_suffix(".txt")
    
    tmp.replace(txt)

Nếu tải thất bại:
    
    
    tmp.unlink(missing_ok=True)

Đây là quy trình rất phổ biến trong các chương trình tải file chuyên nghiệp.

* * *

# Những lỗi thường gặp

## 1\. Quên `parents=True`

Sai:
    
    
    Path("a/b/c").mkdir()

Nếu `a` hoặc `b` chưa tồn tại sẽ báo lỗi.

Đúng:
    
    
    Path("a/b/c").mkdir(
        parents=True,
        exist_ok=True
    )

* * *

## 2\. Dùng `unlink()` để xóa thư mục

Sai:
    
    
    Path("downloads").unlink()

Đúng:
    
    
    Path("downloads").rmdir()

Nếu thư mục rỗng.

* * *

## 3\. Dùng `rmdir()` với thư mục có dữ liệu
    
    
    downloads/
    
        chapter001.txt

↓
    
    
    Path("downloads").rmdir()

↓
    
    
    OSError

Muốn xóa toàn bộ cây thư mục, hãy dùng `shutil.rmtree()` (sẽ học ở buổi sau).

* * *

## 4\. Đổi tên sang thư mục chưa tồn tại

Sai:
    
    
    Path("chapter001.txt").rename(
        "downloads/One Piece/chapter001.txt"
    )

Nếu thư mục `downloads/One Piece` chưa tồn tại, thao tác sẽ thất bại.

Đúng:
    
    
    target = Path("downloads/One Piece")
    target.mkdir(parents=True, exist_ok=True)
    
    Path("chapter001.txt").rename(
        target / "chapter001.txt"
    )

* * *

# Bài tập thực hành

## Bài 1

Tạo cấu trúc:
    
    
    project/
    
        downloads/
    
        cache/
    
        logs/
    
        database/
    
        assets/

Sử dụng `mkdir()`.

* * *

## Bài 2

Tạo:
    
    
    logs/error.log
    
    logs/access.log

Bằng `touch()`.

* * *

## Bài 3

Đổi:
    
    
    chapter001.txt

↓
    
    
    chapter002.txt

Bằng:

  * `rename()`
  * `replace()`



Quan sát sự khác biệt nếu file đích đã tồn tại.

* * *

## Bài 4

Viết chương trình:

  * Tạo file `temp.tmp`. 
  * Ghi nội dung vào file. 
  * Đổi thành `chapter001.txt`. 
  * Xóa file sau khi kiểm tra xong. 



* * *

## Bài 5 (Dự án thực tế)

Xây dựng lớp `ProjectInitializer`:

  * Tạo toàn bộ thư mục của dự án. 
  * Tạo các file: 
    * `crawler.db`
    * `crawler.log`
    * `config.json`
  * Có phương thức: 
    * `initialize()`
    * `reset_logs()`
    * `create_novel_folder(name)`
    * `remove_empty_folder(path)`



Hãy thiết kế lớp này để có thể tái sử dụng cho mọi dự án crawler hoặc ứng dụng PySide6.

* * *

# Tổng kết buổi 6

Trong buổi học này, bạn đã học cách quản lý vòng đời của file và thư mục bằng `pathlib`:

  * `mkdir()` để tạo thư mục, kết hợp `parents=True` và `exist_ok=True`. 
  * `touch()` để tạo file rỗng. 
  * `unlink()` để xóa file. 
  * `rmdir()` để xóa thư mục rỗng. 
  * `rename()` và `replace()` để đổi tên hoặc di chuyển file/thư mục. 
  * Xây dựng cấu trúc thư mục và môi trường dự án một cách tự động. 



Đến đây, bạn đã nắm gần như đầy đủ các thao tác cơ bản với file và thư mục trong `pathlib`. Ở **Buổi 7** , chúng ta sẽ học cách **duyệt thư mục và tìm kiếm file** với `iterdir()`, `glob()`, `rglob()` và `match()`. Đây là những công cụ cực kỳ quan trọng để xây dựng trình đọc truyện, quét thư viện sách, thống kê dữ liệu và quản lý hàng nghìn file trong hệ thống crawler của bạn.

