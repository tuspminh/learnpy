# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 7: Duyệt thư mục và tìm kiếm File (`iterdir()`, `glob()`, `rglob()`, `match()`)

> **Mục tiêu**

Sau buổi học này, bạn sẽ:

  * Thành thạo duyệt thư mục bằng `iterdir()`. 
  * Hiểu cơ chế Pattern Matching (Wildcard). 
  * Thành thạo `glob()` và `rglob()`. 
  * Biết cách lọc file theo phần mở rộng. 
  * Áp dụng để xây dựng **Thư viện truyện** , **Dashboard** , **Trình đọc truyện** và **Crawler Manager**. 



Đây là một trong những buổi quan trọng nhất của `pathlib`.

* * *

# 1\. Chuẩn bị cấu trúc thư mục

Giả sử dự án của chúng ta có:
    
    
    downloads/
    │
    ├── Naruto/
    │   ├── cover.jpg
    │   ├── info.json
    │   ├── chapter001.txt
    │   ├── chapter002.txt
    │   └── chapter003.txt
    │
    ├── One Piece/
    │   ├── cover.jpg
    │   ├── info.json
    │   ├── chapter001.txt
    │   └── chapter002.txt
    │
    ├── Conan/
    │   ├── cover.jpg
    │   ├── info.json
    │   └── chapter001.txt
    │
    └── cache/
        ├── index.json
        └── temp.html

Chúng ta sẽ dùng cấu trúc này trong toàn bộ buổi học.

* * *

# 2\. `iterdir()`

Đây là hàm đơn giản nhất.
    
    
    from pathlib import Path
    
    folder = Path("downloads")
    
    for item in folder.iterdir():
        print(item)

Ví dụ kết quả
    
    
    downloads/Naruto
    downloads/One Piece
    downloads/Conan
    downloads/cache

Lưu ý:

**Chỉ duyệt cấp đầu tiên.**

* * *

# 3\. `iterdir()` trả về gì?

Không phải List.
    
    
    print(type(Path("downloads").iterdir()))

↓
    
    
    <class 'generator'>

Nó sinh dữ liệu từng phần.

Ưu điểm

  * Nhanh 
  * Tiết kiệm RAM 
  * Phù hợp thư mục hàng trăm nghìn file 



* * *

# 4\. Chỉ lấy thư mục
    
    
    from pathlib import Path
    
    root = Path("downloads")
    
    for item in root.iterdir():
    
        if item.is_dir():
            print(item.name)

↓
    
    
    Naruto
    
    One Piece
    
    Conan
    
    cache

* * *

# 5\. Chỉ lấy file
    
    
    for item in root.iterdir():
    
        if item.is_file():
            print(item.name)

Ví dụ
    
    
    readme.txt
    
    config.json

* * *

# 6\. `glob()`

Đây là hàm mạnh hơn.

Ví dụ
    
    
    folder = Path("downloads/Naruto")
    
    for file in folder.glob("*.txt"):
        print(file.name)

↓
    
    
    chapter001.txt
    
    chapter002.txt
    
    chapter003.txt

* * *

# 7\. Wildcard là gì?

`glob()` sử dụng Pattern.

Các ký tự đặc biệt:

Pattern| Ý nghĩa  
---|---  
*| mọi ký tự  
?| đúng 1 ký tự  
[]| tập ký tự  
**| đệ quy toàn bộ cây  
  
* * *

Ví dụ
    
    
    *.txt

↓
    
    
    chapter001.txt
    
    chapter010.txt
    
    abc.txt

* * *

# 8\. Tìm ảnh
    
    
    folder = Path("downloads/Naruto")
    
    for img in folder.glob("*.jpg"):
        print(img)

↓
    
    
    cover.jpg

* * *

# 9\. Tìm JSON
    
    
    for file in folder.glob("*.json"):
        print(file)

↓
    
    
    info.json

* * *

# 10\. Tìm nhiều loại

Ví dụ
    
    
    patterns = [
        "*.jpg",
        "*.png",
        "*.webp"
    ]
    
    for p in patterns:
    
        for img in folder.glob(p):
            print(img)

* * *

# 11\. `rglob()`

Đây là phiên bản đệ quy.

Ví dụ
    
    
    root = Path("downloads")
    
    for file in root.rglob("*.txt"):
        print(file)

↓
    
    
    downloads/Naruto/chapter001.txt
    
    downloads/Naruto/chapter002.txt
    
    downloads/One Piece/chapter001.txt
    
    downloads/Conan/chapter001.txt

Nó tìm trong toàn bộ cây thư mục.

* * *

# 12\. `glob("**/*.txt")`

Thực chất
    
    
    root.glob("**/*.txt")

≈
    
    
    root.rglob("*.txt")

Hai cách gần như tương đương.

* * *

# 13\. `match()`

Kiểm tra một đường dẫn có khớp Pattern không.
    
    
    from pathlib import Path
    
    file = Path("chapter001.txt")
    
    print(file.match("*.txt"))

↓
    
    
    True

* * *

Ví dụ
    
    
    file.match("*.jpg")

↓
    
    
    False

* * *

# 14\. Kiểm tra chương truyện
    
    
    chapter = Path("chapter001.txt")
    
    if chapter.match("chapter*.txt"):
        print("Đây là file chương")

↓
    
    
    Đây là file chương

* * *

# 15\. Duyệt toàn bộ truyện
    
    
    root = Path("downloads")
    
    for novel in root.iterdir():
    
        if novel.is_dir():
    
            print(novel.name)
    
            for chapter in novel.glob("chapter*.txt"):
                print("   ", chapter.name)

↓
    
    
    Naruto
    
        chapter001.txt
    
        chapter002.txt
    
    One Piece
    
        chapter001.txt

* * *

# 16\. Đếm số chương
    
    
    folder = Path("downloads/Naruto")
    
    count = len(
        list(
            folder.glob("chapter*.txt")
        )
    )
    
    print(count)

↓
    
    
    3

* * *

# 17\. Tìm toàn bộ ảnh bìa
    
    
    root = Path("downloads")
    
    covers = list(
        root.rglob("cover.*")
    )
    
    for cover in covers:
        print(cover)

↓
    
    
    downloads/Naruto/cover.jpg
    
    downloads/Conan/cover.jpg
    
    downloads/One Piece/cover.jpg

* * *

# 18\. Tìm toàn bộ Database
    
    
    for db in Path(".").rglob("*.db"):
        print(db)

↓
    
    
    database/crawler.db

* * *

# 19\. Ví dụ Dashboard

Danh sách truyện.
    
    
    from pathlib import Path
    
    DOWNLOAD = Path("downloads")
    
    novels = [
        folder
        for folder in DOWNLOAD.iterdir()
        if folder.is_dir()
    ]
    
    for novel in novels:
        print(novel.name)

↓
    
    
    Naruto
    
    One Piece
    
    Conan

Đây chính là dữ liệu để đưa vào `QTreeWidget`, `QListView` hoặc `QTableView` trong PySide6.

* * *

# 20\. Tìm chương mới nhất
    
    
    chapters = sorted(
        Path("downloads/Naruto").glob(
            "chapter*.txt"
        )
    )
    
    print(chapters[-1])

↓
    
    
    chapter003.txt

> **Lưu ý:** `sorted()` sắp xếp theo tên file. Nếu số chương không được đệm số (`chapter1`, `chapter10`, `chapter2`), kết quả sẽ không đúng. Vì vậy hãy luôn dùng định dạng như `chapter001`, `chapter002`, ...

* * *

# 21\. Lọc theo nhiều điều kiện
    
    
    for file in Path("downloads").rglob("*"):
    
        if file.is_file():
    
            if file.suffix == ".txt":
    
                print(file)

* * *

# 22\. Tìm file lớn hơn 1 MB
    
    
    for file in Path(".").rglob("*"):
    
        if file.is_file():
    
            if file.stat().st_size > 1024 * 1024:
    
                print(file)

* * *

# 23\. Ví dụ hoàn chỉnh
    
    
    from pathlib import Path
    
    DOWNLOAD = Path("downloads")
    
    for novel in DOWNLOAD.iterdir():
    
        if not novel.is_dir():
            continue
    
        print("=" * 40)
        print("Tên truyện:", novel.name)
    
        chapters = sorted(
            novel.glob("chapter*.txt")
        )
    
        print("Số chương:", len(chapters))
    
        for chapter in chapters:
    
            print("   ", chapter.name)

* * *

# 24\. Thiết kế lớp `LibraryScanner`
    
    
    from pathlib import Path
    
    class LibraryScanner:
    
        def __init__(self, root):
            self.root = Path(root)
    
        def novels(self):
            return [
                d
                for d in self.root.iterdir()
                if d.is_dir()
            ]
    
        def chapters(self, novel):
    
            return sorted(
                novel.glob("chapter*.txt")
            )
    
        def covers(self):
    
            return list(
                self.root.rglob("cover.*")
            )

Sử dụng
    
    
    scanner = LibraryScanner("downloads")
    
    for novel in scanner.novels():
    
        print(novel.name)
    
        for chapter in scanner.chapters(novel):
    
            print(chapter.name)

* * *

# 25\. Những lỗi thường gặp

## 1\. Quên kiểm tra `is_dir()`

Sai:
    
    
    for novel in Path("downloads").iterdir():
    
        for chapter in novel.glob("*.txt"):
            ...

Nếu `novel` là file, đoạn mã sẽ không hoạt động như mong đợi.

Đúng:
    
    
    if novel.is_dir():
        ...

* * *

## 2\. `glob()` không tìm thư mục con
    
    
    Path("downloads").glob("*.txt")

↓

Không tìm thấy
    
    
    downloads/Naruto/chapter001.txt

Vì `glob()` chỉ tìm ở cấp hiện tại.

Muốn tìm tất cả:
    
    
    Path("downloads").rglob("*.txt")

* * *

## 3\. `iterdir()` không duyệt đệ quy

Nhiều người nghĩ:
    
    
    Path("downloads").iterdir()

sẽ duyệt toàn bộ cây.

Không.

Nó chỉ duyệt **một cấp**.

* * *

# 26\. Ứng dụng trong hệ thống Crawler

Giả sử mỗi truyện có cấu trúc:
    
    
    downloads/
    └── One Piece/
        ├── cover.jpg
        ├── info.json
        ├── chapter001.txt
        ├── chapter002.txt
        └── chapter003.txt

Bạn có thể:

  * Hiển thị danh sách truyện bằng `iterdir()`. 
  * Đếm số chương bằng `glob("chapter*.txt")`. 
  * Tìm tất cả ảnh bìa bằng `rglob("cover.*")`. 
  * Kiểm tra một file có phải là chương truyện bằng `match("chapter*.txt")`. 
  * Xây dựng thư viện truyện mà không cần lưu danh sách file trong cơ sở dữ liệu. 



* * *

# Bài tập thực hành

## Bài 1

Tạo cấu trúc:
    
    
    downloads/
    ├── Naruto/
    ├── Conan/
    ├── Doraemon/
    └── One Piece/

Viết chương trình in tên tất cả thư mục truyện.

* * *

## Bài 2

Trong mỗi thư mục truyện, tạo các file:
    
    
    chapter001.txt
    chapter002.txt
    cover.jpg
    info.json

Viết chương trình:

  * Chỉ in các file `.txt`. 
  * Chỉ in các file `.jpg`. 
  * Chỉ in các file `.json`. 



* * *

## Bài 3

Viết hàm:
    
    
    from pathlib import Path
    
    def count_chapters(novel_dir: Path) -> int:
        """Đếm số file chapter*.txt trong thư mục truyện."""
        ...

* * *

## Bài 4

Viết chương trình quét toàn bộ thư mục `downloads` và hiển thị:
    
    
    Naruto        : 120 chương
    Conan         : 1050 chương
    One Piece     : 1135 chương

* * *

## Bài 5 (Dự án thực tế)

Xây dựng lớp `NovelLibrary` với các phương thức:

  * `scan_novels()` → trả về danh sách thư mục truyện. 
  * `scan_chapters(novel_name)` → trả về danh sách chương. 
  * `find_cover(novel_name)` → tìm ảnh bìa. 
  * `search_files(pattern)` → tìm mọi file theo mẫu (`*.txt`, `*.json`, ...). 
  * `latest_chapter(novel_name)` → trả về chương mới nhất. 



Hãy thiết kế lớp sao cho có thể tích hợp trực tiếp với giao diện **PySide6** , nơi danh sách truyện được hiển thị ở panel bên trái và danh sách chương ở panel bên phải.

* * *

# Tổng kết buổi 7

Trong buổi học này, bạn đã làm chủ nhóm công cụ tìm kiếm và duyệt thư mục của `pathlib`:

  * `iterdir()` để duyệt nội dung một cấp. 
  * `glob()` để tìm file theo mẫu trong thư mục hiện tại. 
  * `rglob()` để tìm kiếm đệ quy trên toàn bộ cây thư mục. 
  * `match()` để kiểm tra đường dẫn có khớp một mẫu hay không. 
  * Kết hợp với `is_file()`, `is_dir()` và `stat()` để xây dựng các công cụ quét dữ liệu mạnh mẽ. 



Đây là nền tảng để xây dựng các ứng dụng như **trình quản lý file** , **thư viện sách** , **trình đọc truyện** , **dashboard giám sát crawler** và **hệ thống lập chỉ mục dữ liệu**. Ở **Buổi 8** , chúng ta sẽ tiếp tục với các thao tác **sao chép, di chuyển và đồng bộ dữ liệu** bằng cách kết hợp `pathlib` với `shutil`, đồng thời xây dựng một **FileManager** chuyên nghiệp có khả năng copy, move, backup và đồng bộ cây thư mục.

