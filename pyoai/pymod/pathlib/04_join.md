# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 4: Biến đổi và xây dựng đường dẫn (`joinpath()`, `relative_to()`, `with_name()`, `with_suffix()`, `with_stem()`, `resolve()`)

> **Mục tiêu**

Sau buổi học này, bạn sẽ:

  * Thành thạo việc tạo đường dẫn mới từ một `Path`. 
  * Hiểu sự khác nhau giữa `/` và `joinpath()`. 
  * Đổi tên file, đổi phần mở rộng mà không cần xử lý chuỗi. 
  * Lấy đường dẫn tương đối và tuyệt đối. 
  * Hiểu rõ tính **bất biến (immutable)** của `Path`. 
  * Áp dụng vào hệ thống **Crawler + PySide6 + SQLite**. 



* * *

# 1\. `Path` là immutable

Đây là điều rất quan trọng.

Giả sử:
    
    
    from pathlib import Path
    
    p = Path("downloads/chapter001.txt")

Đổi phần mở rộng:
    
    
    new_p = p.with_suffix(".html")

Kết quả:
    
    
    print(p)
    
    
    downloads/chapter001.txt
    
    
    print(new_p)
    
    
    downloads/chapter001.html

**`p` không hề thay đổi.**

Mọi phương thức của `Path` đều tạo **một đối tượng mới**.

* * *

# 2\. Toán tử `/`

Đây là cách phổ biến nhất.
    
    
    from pathlib import Path
    
    p = Path("downloads") / "novels" / "chapter001.txt"
    
    print(p)

Kết quả
    
    
    downloads/novels/chapter001.txt

Đây là cú pháp được khuyến nghị.

* * *

# 3\. `joinpath()`

Hoàn toàn tương đương với `/`.
    
    
    from pathlib import Path
    
    p = Path("downloads").joinpath("novels")
    
    print(p)

↓
    
    
    downloads/novels

Có thể nối nhiều thành phần:
    
    
    p = Path("downloads").joinpath(
        "novels",
        "One Piece",
        "chapter001.txt"
    )
    
    print(p)

↓
    
    
    downloads/novels/One Piece/chapter001.txt

* * *

## `/` hay `joinpath()`?

### `/`
    
    
    Path("downloads") / "novels" / "chapter001.txt"

Đẹp, ngắn gọn.

* * *

### `joinpath()`
    
    
    Path("downloads").joinpath(
        folder,
        filename
    )

Phù hợp khi số lượng thành phần thay đổi theo chương trình.

Ví dụ:
    
    
    parts = ["novels", "One Piece", "chapter001.txt"]
    
    p = Path("downloads").joinpath(*parts)

↓
    
    
    downloads/novels/One Piece/chapter001.txt

Dấu `*` giúp giải nén danh sách thành các đối số.

* * *

# 4\. `with_name()`

Đổi tên file.

Ví dụ
    
    
    from pathlib import Path
    
    file = Path("chapter001.txt")
    
    new_file = file.with_name("chapter002.txt")
    
    print(new_file)

↓
    
    
    chapter002.txt

File gốc vẫn giữ nguyên.

* * *

## Ví dụ
    
    
    downloads/
    
        chapter001.txt

↓
    
    
    new = file.with_name("chapter005.txt")

↓
    
    
    downloads/
    
        chapter005.txt

* * *

# 5\. `with_suffix()`

Đổi phần mở rộng.
    
    
    from pathlib import Path
    
    file = Path("cover.jpg")
    
    print(file.with_suffix(".png"))

↓
    
    
    cover.png

* * *

Ví dụ
    
    
    Path("chapter001.txt").with_suffix(".html")

↓
    
    
    chapter001.html

* * *

Ví dụ
    
    
    Path("movie.mp4").with_suffix(".mkv")

↓
    
    
    movie.mkv

* * *

# 6\. `with_stem()`

Đổi tên file nhưng giữ nguyên phần mở rộng.
    
    
    from pathlib import Path
    
    file = Path("cover.jpg")
    
    new = file.with_stem("thumbnail")
    
    print(new)

↓
    
    
    thumbnail.jpg

* * *

Ví dụ
    
    
    chapter001.txt

↓
    
    
    chapter.with_stem("chapter010")

↓
    
    
    chapter010.txt

* * *

# 7\. Kết hợp
    
    
    from pathlib import Path
    
    file = Path("chapter001.txt")
    
    new = (
        file
        .with_stem("chapter002")
        .with_suffix(".html")
    )
    
    print(new)

↓
    
    
    chapter002.html

* * *

# 8\. `relative_to()`

Lấy đường dẫn tương đối.

Ví dụ
    
    
    from pathlib import Path
    
    full = Path(
        "/home/admin/project/downloads/chapter001.txt"
    )
    
    base = Path("/home/admin/project")
    
    print(full.relative_to(base))

↓
    
    
    downloads/chapter001.txt

* * *

## Ví dụ Windows
    
    
    full = Path(
        r"C:\Crawler\downloads\cover.jpg"
    )
    
    base = Path(r"C:\Crawler")
    
    print(full.relative_to(base))

↓
    
    
    downloads\cover.jpg

* * *

## Khi không cùng gốc
    
    
    Path("/data/file.txt").relative_to("/tmp")

↓
    
    
    ValueError

Vì `/tmp` không phải cha của `/data/file.txt`.

* * *

# 9\. `resolve()`

Lấy đường dẫn tuyệt đối.
    
    
    from pathlib import Path
    
    p = Path("downloads/chapter001.txt")
    
    print(p.resolve())

Ví dụ
    
    
    D:\Crawler\downloads\chapter001.txt

* * *

`resolve()` rất hữu ích khi:

  * Ghi log 
  * Debug 
  * Lưu vào database 
  * Hiển thị trên giao diện 



* * *

# 10\. `absolute()`

Một số tài liệu cũ có nhắc đến `absolute()`, nhưng trong thực tế bạn nên ưu tiên:
    
    
    p.resolve()

Vì `resolve()` còn chuẩn hóa đường dẫn và xử lý tốt hơn trong nhiều trường hợp.

* * *

# 11\. Ví dụ thực tế

Giả sử:
    
    
    crawler/
    
        downloads/
    
            Naruto/
    
                chapter001.txt
    
    
    from pathlib import Path
    
    base = Path.cwd()
    
    chapter = (
        base
        / "downloads"
        / "Naruto"
        / "chapter001.txt"
    )
    
    print(chapter.resolve())

↓
    
    
    D:\Crawler\downloads\Naruto\chapter001.txt

* * *

# 12\. Ứng dụng trong Crawler

Crawler tải:
    
    
    chapter001.html

Muốn lưu thành
    
    
    chapter001.txt
    
    
    html = Path("chapter001.html")
    
    txt = html.with_suffix(".txt")

* * *

Tải ảnh
    
    
    cover.webp

Muốn chuyển sang
    
    
    cover.jpg
    
    
    cover = Path("cover.webp")
    
    jpg = cover.with_suffix(".jpg")

* * *

# 13\. Đổi tên chương
    
    
    chapter = Path("chapter001.txt")
    
    next_chapter = chapter.with_stem("chapter002")
    
    print(next_chapter)

↓
    
    
    chapter002.txt

* * *

# 14\. Tạo đường dẫn động
    
    
    from pathlib import Path
    
    novel = "One Piece"
    
    chapter = 25
    
    path = (
        Path("downloads")
        / novel
        / f"chapter{chapter:03}.txt"
    )
    
    print(path)

↓
    
    
    downloads/One Piece/chapter025.txt

`{chapter:03}` sẽ đệm số 0 ở bên trái.

* * *

# 15\. Ví dụ tổng hợp
    
    
    from pathlib import Path
    
    file = Path("downloads/One Piece/chapter001.txt")
    
    print("Gốc:", file)
    
    print("Đổi tên:",
          file.with_name("chapter010.txt"))
    
    print("Đổi đuôi:",
          file.with_suffix(".html"))
    
    print("Đổi stem:",
          file.with_stem("chapter100"))
    
    print("Cha:",
          file.parent)
    
    print("Tuyệt đối:",
          file.resolve())

* * *

# 16\. Thiết kế lớp quản lý đường dẫn
    
    
    from pathlib import Path
    
    class NovelPaths:
    
        def __init__(self, root):
            self.root = Path(root)
    
        def chapter(self, novel, number):
            return (
                self.root
                / "downloads"
                / novel
                / f"chapter{number:03}.txt"
            )
    
        def cover(self, novel):
            return (
                self.root
                / "downloads"
                / novel
                / "cover.jpg"
            )

Sử dụng:
    
    
    paths = NovelPaths(".")
    
    print(paths.chapter("Naruto", 15))

↓
    
    
    downloads/Naruto/chapter015.txt

* * *

# 17\. Ứng dụng vào dự án PySide6

Trong Dashboard:
    
    
    Danh sách truyện
    
    ↓
    
    One Piece
    
    ↓
    
    chapter001.txt

Khi người dùng chọn truyện:
    
    
    novel = "One Piece"
    
    cover = (
        DOWNLOAD_DIR
        / novel
        / "cover.jpg"
    )

Đọc nội dung chương:
    
    
    chapter = (
        DOWNLOAD_DIR
        / novel
        / "chapter001.txt"
    )

Không cần ghép chuỗi bằng `+` hay `os.path.join()`.

* * *

# Những lỗi thường gặp

## 1\. Quên gán kết quả

Sai:
    
    
    p = Path("cover.jpg")
    
    p.with_suffix(".png")
    
    print(p)

↓
    
    
    cover.jpg

Đúng:
    
    
    p = p.with_suffix(".png")

* * *

## 2\. Thiếu dấu `.` ở `with_suffix()`

Sai:
    
    
    p.with_suffix("png")

Đúng:
    
    
    p.with_suffix(".png")

* * *

## 3\. `relative_to()` với đường dẫn không cùng gốc
    
    
    Path("/data/test.txt").relative_to("/tmp")

↓
    
    
    ValueError

Hãy đảm bảo đường dẫn cơ sở (`base`) là thư mục cha của đường dẫn cần chuyển đổi.

* * *

# Bài tập thực hành

## Bài 1

Tạo đường dẫn:
    
    
    downloads/Naruto/chapter001.txt

Bằng:

  * Toán tử `/`
  * `joinpath()`



* * *

## Bài 2

Đổi:
    
    
    chapter001.txt

thành:
    
    
    chapter050.txt

sử dụng:

  * `with_name()`
  * `with_stem()`



và so sánh hai cách.

* * *

## Bài 3

Đổi các file sau sang `.txt`:
    
    
    chapter001.html
    chapter002.md
    chapter003.xhtml

bằng `with_suffix()`.

* * *

## Bài 4

Viết hàm:
    
    
    from pathlib import Path
    
    def build_chapter_path(base: Path, novel: str, chapter: int) -> Path:
        """Trả về đường dẫn tới file chương theo định dạng chapterXXX.txt"""
        ...

Ví dụ:
    
    
    build_chapter_path(Path("."), "Conan", 7)

Kết quả mong muốn:
    
    
    downloads/Conan/chapter007.txt

* * *

## Bài 5 (Dự án thực tế)

Xây dựng lớp `CrawlerPathManager`:

  * Quản lý thư mục `downloads`, `cache`, `logs`, `database`. 
  * Có các phương thức: 
    * `novel_dir(novel_name)`
    * `chapter_path(novel_name, chapter_number)`
    * `cover_path(novel_name)`
    * `log_path(date)`
    * `cache_path(filename)`



Hãy sử dụng toàn bộ kiến thức từ 4 buổi đầu (`/`, `joinpath()`, `with_name()`, `with_suffix()`, `resolve()`) để thiết kế lớp này. Đây sẽ là nền móng cho hệ thống cào truyện và dashboard PySide6 mà bạn đang xây dựng.

* * *

# Tổng kết buổi 4

Trong buổi học này, bạn đã học cách **xây dựng và biến đổi đường dẫn** một cách linh hoạt với `pathlib`:

  * Dùng toán tử `/` và `joinpath()` để ghép đường dẫn. 
  * Đổi tên file bằng `with_name()`. 
  * Đổi phần mở rộng bằng `with_suffix()`. 
  * Đổi tên file nhưng giữ nguyên phần mở rộng bằng `with_stem()`. 
  * Chuyển giữa đường dẫn tuyệt đối và tương đối với `resolve()` và `relative_to()`. 
  * Hiểu rằng `Path` là **immutable** , mọi phép biến đổi đều trả về một đối tượng mới. 



Đến thời điểm này, bạn đã có nền tảng rất vững về cách biểu diễn và thao tác với đường dẫn trong Python. Ở **Buổi 5** , chúng ta sẽ chuyển sang một nhóm chức năng rất quan trọng: **đọc và ghi file** với `read_text()`, `write_text()`, `read_bytes()` và `write_bytes()`, đồng thời tìm hiểu về mã hóa ký tự (UTF-8, UTF-8 BOM, UTF-16...) và các lưu ý khi xử lý văn bản tiếng Việt trong các dự án thực tế.

