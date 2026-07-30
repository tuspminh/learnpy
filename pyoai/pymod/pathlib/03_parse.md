# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 3: Phân tích đường dẫn (`name`, `stem`, `suffix`, `suffixes`, `parent`, `parents`, `parts`)

> **Mục tiêu**

Sau buổi học này, bạn sẽ:

  * Hiểu cấu trúc của một đường dẫn (`Path`) trong Python. 
  * Thành thạo các thuộc tính: 
    * `name`
    * `stem`
    * `suffix`
    * `suffixes`
    * `parent`
    * `parents`
    * `parts`
  * Biết cách xử lý file có nhiều phần mở rộng như `.tar.gz`. 
  * Áp dụng vào dự án **Crawler + PySide6 + SQLite** để quản lý truyện, ảnh và dữ liệu. 



* * *

# 1\. Cấu trúc của một đường dẫn

Giả sử có đường dẫn:
    
    
    downloads/novels/one_piece/chapter001.txt

Ta có thể chia như sau:
    
    
    downloads
        ↓
    novels
        ↓
    one_piece
        ↓
    chapter001.txt
            │
            ├── tên file
            └── phần mở rộng

Trong `pathlib`, mỗi thành phần đều có thể truy cập dễ dàng.

* * *

# 2\. Chuẩn bị
    
    
    from pathlib import Path
    
    p = Path("downloads/novels/one_piece/chapter001.txt")

Toàn bộ các ví dụ bên dưới đều sử dụng biến `p`.

* * *

# 3\. `name`

Đây là thuộc tính được dùng rất nhiều.
    
    
    print(p.name)

Kết quả
    
    
    chapter001.txt

Nó trả về:

> Tên cuối cùng của đường dẫn.

Ví dụ khác
    
    
    Path("images/logo.png").name

↓
    
    
    logo.png

* * *

## Ví dụ
    
    
    files = [
        Path("a.txt"),
        Path("b.py"),
        Path("photo.jpg"),
    ]
    
    for f in files:
        print(f.name)

Kết quả
    
    
    a.txt
    b.py
    photo.jpg

* * *

# 4\. `stem`

Lấy tên file **không có phần mở rộng**.
    
    
    print(p.stem)

↓
    
    
    chapter001

Ví dụ
    
    
    Path("photo.jpg").stem

↓
    
    
    photo

* * *

## Ví dụ thực tế

Crawler tải
    
    
    chapter001.txt
    chapter002.txt
    chapter003.txt

Muốn lấy số chương:
    
    
    print(Path("chapter001.txt").stem)

↓
    
    
    chapter001

* * *

# 5\. `suffix`

Lấy phần mở rộng.
    
    
    print(p.suffix)

↓
    
    
    .txt

Ví dụ
    
    
    Path("photo.jpg").suffix

↓
    
    
    .jpg

* * *

Ví dụ
    
    
    Path("archive.zip").suffix

↓
    
    
    .zip

* * *

# 6\. `suffixes`

Nhiều file có nhiều phần mở rộng.

Ví dụ
    
    
    backup.tar.gz

Ta thử
    
    
    file = Path("backup.tar.gz")
    
    print(file.suffix)

↓
    
    
    .gz

Nhưng
    
    
    print(file.suffixes)

↓
    
    
    ['.tar', '.gz']

Đây là điểm khác biệt rất quan trọng.

* * *

## Ví dụ
    
    
    files = [
        Path("abc.tar.gz"),
        Path("movie.mp4"),
        Path("photo.jpg"),
    ]
    
    for f in files:
        print(f.name)
        print(f.suffix)
        print(f.suffixes)

* * *

# 7\. So sánh `stem` và `suffix`

Ví dụ
    
    
    archive.tar.gz
    
    
    file = Path("archive.tar.gz")

Thuộc tính| Giá trị  
---|---  
name| archive.tar.gz  
stem| archive.tar  
suffix| .gz  
suffixes| ['.tar', '.gz']  
  
Lưu ý:

`stem` chỉ bỏ **đuôi cuối cùng**.

* * *

# 8\. `parent`

Đây là thư mục cha.
    
    
    print(p.parent)

↓
    
    
    downloads/novels/one_piece

* * *

Ví dụ
    
    
    Path("images/logo.png").parent

↓
    
    
    images

* * *

Ví dụ
    
    
    Path("crawler/database.db").parent

↓
    
    
    crawler

* * *

# 9\. `parents`

Đây là toàn bộ cây thư mục cha.
    
    
    print(p.parents)

Kết quả
    
    
    <PosixPath.parents>

Muốn truy cập:
    
    
    print(p.parents[0])

↓
    
    
    downloads/novels/one_piece

* * *
    
    
    print(p.parents[1])

↓
    
    
    downloads/novels

* * *
    
    
    print(p.parents[2])

↓
    
    
    downloads

* * *
    
    
    print(p.parents[3])

↓
    
    
    .

* * *

## Duyệt toàn bộ
    
    
    for parent in p.parents:
        print(parent)

Kết quả
    
    
    downloads/novels/one_piece
    
    downloads/novels
    
    downloads
    
    .

* * *

# 10\. `parts`

Đây là thuộc tính mình sử dụng rất nhiều.
    
    
    print(p.parts)

↓
    
    
    ('downloads',
     'novels',
     'one_piece',
     'chapter001.txt')

Kiểu dữ liệu
    
    
    tuple

* * *

Có thể truy cập
    
    
    print(p.parts[0])

↓
    
    
    downloads

* * *
    
    
    print(p.parts[1])

↓
    
    
    novels

* * *
    
    
    print(p.parts[-1])

↓
    
    
    chapter001.txt

* * *

# 11\. Ví dụ minh họa
    
    
    downloads/
        novels/
            one_piece/
                chapter001.txt
    
    
    from pathlib import Path
    
    p = Path(
        "downloads/novels/one_piece/chapter001.txt"
    )
    
    print("name:", p.name)
    print("stem:", p.stem)
    print("suffix:", p.suffix)
    print("parent:", p.parent)
    print("parts:", p.parts)

Kết quả
    
    
    name: chapter001.txt
    
    stem: chapter001
    
    suffix: .txt
    
    parent: downloads/novels/one_piece
    
    parts:
    ('downloads',
    'novels',
    'one_piece',
    'chapter001.txt')

* * *

# 12\. Ví dụ trong dự án Crawler

Giả sử
    
    
    downloads/
        Naruto/
            chapter001.txt

Ta có
    
    
    chapter = Path(
        "downloads/Naruto/chapter001.txt"
    )
    
    print(chapter.parent.name)

↓
    
    
    Naruto

Lấy tên truyện rất nhanh.

* * *

Muốn lấy tên chương
    
    
    print(chapter.stem)

↓
    
    
    chapter001

* * *

# 13\. Lấy loại file
    
    
    file = Path("cover.webp")
    
    if file.suffix == ".jpg":
        print("JPEG")
    
    elif file.suffix == ".png":
        print("PNG")
    
    elif file.suffix == ".webp":
        print("WEBP")

* * *

# 14\. Đổi phần mở rộng

`pathlib` không thay đổi trực tiếp `suffix`, nhưng có thể tạo một `Path` mới bằng `with_suffix()`.
    
    
    from pathlib import Path
    
    file = Path("cover.jpg")
    new_file = file.with_suffix(".png")
    
    print(new_file)

Kết quả:
    
    
    cover.png

> Chúng ta sẽ học chi tiết `with_suffix()` ở buổi sau.

* * *

# 15\. Phân tích cấu trúc dự án
    
    
    crawler/
    
        config/
    
        downloads/
    
            novels/
    
                one_piece/
    
                    chapter001.txt
    
        database/
    
            crawler.db
    
    
    db = Path("database/crawler.db")
    
    print(db.name)
    print(db.parent)
    print(db.stem)
    print(db.suffix)

Kết quả
    
    
    crawler.db
    
    database
    
    crawler
    
    .db

* * *

# 16\. Ví dụ tổng hợp
    
    
    from pathlib import Path
    
    file = Path("downloads/novels/one_piece/chapter001.txt")
    
    print("=" * 40)
    
    print("Đường dẫn:", file)
    print("Tên:", file.name)
    print("Tên không đuôi:", file.stem)
    print("Đuôi:", file.suffix)
    print("Các đuôi:", file.suffixes)
    print("Thư mục cha:", file.parent)
    
    print("Các thư mục cha:")
    
    for p in file.parents:
        print("  ", p)
    
    print("Các thành phần:")
    
    for item in file.parts:
        print(item)

* * *

# 17\. Những lỗi thường gặp

## Lỗi 1: Nhầm `stem` với tên đầy đủ
    
    
    Path("image.png").stem

↓
    
    
    image

Không phải
    
    
    image.png

* * *

## Lỗi 2: Nhầm `parent` là chuỗi
    
    
    print(type(p.parent))

↓
    
    
    <class 'pathlib.Path'>

`parent` vẫn là một đối tượng `Path`, vì vậy bạn có thể tiếp tục gọi:
    
    
    print(p.parent.parent)

hoặc:
    
    
    print(p.parent.name)

* * *

## Lỗi 3: Quên file nhiều đuôi
    
    
    Path("backup.tar.gz").suffix

↓
    
    
    .gz

Nếu cần toàn bộ phần mở rộng, hãy dùng:
    
    
    Path("backup.tar.gz").suffixes

* * *

# 18\. Ứng dụng trong hệ thống cào truyện

Giả sử crawler tải:
    
    
    downloads/
    
        One Piece/
    
            chapter001.txt
    
            chapter002.txt
    
            chapter003.txt

Ta có thể:
    
    
    from pathlib import Path
    
    chapter = Path(
        "downloads/One Piece/chapter003.txt"
    )
    
    novel_name = chapter.parent.name
    chapter_name = chapter.stem
    extension = chapter.suffix
    
    print(novel_name)
    print(chapter_name)
    print(extension)

Kết quả:
    
    
    One Piece
    chapter003
    .txt

Đây là cách rất gọn để lấy thông tin từ đường dẫn mà không cần cắt chuỗi (`split("/")`, `split(".")`), giúp mã nguồn rõ ràng và ít lỗi hơn.

* * *

# Bài tập thực hành

## Bài 1

Cho đường dẫn:
    
    
    downloads/comics/one_piece/chapter010.txt

In ra:

  * `name`
  * `stem`
  * `suffix`
  * `parent`
  * `parts`



* * *

## Bài 2

Cho các file:
    
    
    photo.jpg
    archive.tar.gz
    video.mp4
    book.pdf

In:

  * tên file 
  * phần mở rộng 
  * danh sách các phần mở rộng (`suffixes`) 



* * *

## Bài 3

Viết hàm:
    
    
    def analyze_path(path: str):
        ...

Hiển thị:

  * Tên file 
  * Tên không đuôi 
  * Đuôi file 
  * Thư mục cha 
  * Các thành phần của đường dẫn 



* * *

## Bài 4

Cho danh sách:
    
    
    downloads/
        Naruto/
            chapter001.txt
    
    downloads/
        Conan/
            chapter010.txt
    
    downloads/
        Doraemon/
            chapter005.txt

Viết chương trình in:
    
    
    Truyện: Naruto - Chương: chapter001
    
    Truyện: Conan - Chương: chapter010
    
    Truyện: Doraemon - Chương: chapter005

* * *

## Bài 5 (Thực tế)

Xây dựng lớp `NovelPathAnalyzer`:
    
    
    from pathlib import Path
    
    class NovelPathAnalyzer:
        def __init__(self, chapter_path: Path):
            self.path = chapter_path
    
        @property
        def novel_name(self):
            return self.path.parent.name
    
        @property
        def chapter_name(self):
            return self.path.stem
    
        @property
        def extension(self):
            return self.path.suffix

Đây sẽ là một thành phần hữu ích trong dự án crawler của bạn, giúp giao diện PySide6 hoặc dashboard hiển thị thông tin truyện và chương trực tiếp từ đường dẫn mà không cần truy vấn cơ sở dữ liệu cho những thông tin cơ bản.

* * *

# Tổng kết buổi 3

Trong buổi học này, bạn đã học cách "giải phẫu" một đường dẫn bằng các thuộc tính mạnh mẽ của `Path`:

  * `name`: tên file hoặc thư mục cuối cùng. 
  * `stem`: tên file không có phần mở rộng cuối. 
  * `suffix` và `suffixes`: lấy một hoặc nhiều phần mở rộng. 
  * `parent` và `parents`: truy cập thư mục cha ở nhiều cấp. 
  * `parts`: tách đường dẫn thành từng thành phần. 



Đây là nền tảng quan trọng để xử lý đường dẫn một cách an toàn, rõ ràng và đa nền tảng. Ở **Buổi 4** , chúng ta sẽ học **biến đổi và xây dựng đường dẫn** với các phương thức như `joinpath()`, `relative_to()`, `with_name()`, `with_suffix()`, `with_stem()` và `resolve()`, giúp bạn tạo ra các đường dẫn mới mà không cần thao tác trên chuỗi.

