# Khóa học: Làm chủ `pathlib` và `urllib`

# Buổi 5: Đọc và ghi File (`read_text()`, `write_text()`, `read_bytes()`, `write_bytes()`)

> **Mục tiêu**

Sau buổi học này, bạn sẽ:

  * Thành thạo đọc và ghi file bằng `pathlib`. 
  * Hiểu sự khác nhau giữa **Text Mode** và **Binary Mode**. 
  * Hiểu rõ về **Encoding** (UTF-8, UTF-8 BOM, UTF-16...). 
  * Biết khi nào dùng `read_text()` và khi nào dùng `read_bytes()`. 
  * Áp dụng vào dự án **Crawler + PySide6 + SQLite** để lưu truyện, cache và ảnh. 



* * *

# 1\. Hai loại dữ liệu trong file

Mọi file trên máy tính đều thuộc một trong hai nhóm:

## Text File

Ví dụ:
    
    
    chapter001.txt
    README.md
    config.json
    index.html
    style.css
    script.js
    robots.txt

Đọc bằng chuỗi (`str`).

* * *

## Binary File

Ví dụ:
    
    
    cover.jpg
    image.webp
    movie.mp4
    music.mp3
    ebook.pdf
    database.db

Đọc bằng `bytes`.

* * *

Đây là điều cực kỳ quan trọng.

Loại| Kiểu dữ liệu  
---|---  
Text| str  
Binary| bytes  
  
* * *

# 2\. `read_text()`

Đây là cách đơn giản nhất để đọc file văn bản.

Giả sử có:
    
    
    chapter001.txt

Nội dung
    
    
    Chương 1
    
    Luffy bắt đầu hành trình...

Đọc:
    
    
    from pathlib import Path
    
    file = Path("chapter001.txt")
    
    text = file.read_text()
    
    print(text)

Kết quả
    
    
    Chương 1
    
    Luffy bắt đầu hành trình...

* * *

# 3\. `encoding`

Đây là tham số rất quan trọng.

Luôn nên ghi rõ:
    
    
    text = file.read_text(
        encoding="utf-8"
    )

Thay vì
    
    
    text = file.read_text()

Lý do:

  * Windows có thể dùng `cp1252`, `cp1258` hoặc encoding khác. 
  * Linux/macOS thường mặc định là UTF-8. 
  * Ghi rõ encoding giúp mã chạy ổn định trên mọi hệ điều hành. 



* * *

# 4\. Ví dụ
    
    
    from pathlib import Path
    
    config = Path("config.json")
    
    print(
        config.read_text(
            encoding="utf-8"
        )
    )

* * *

# 5\. `write_text()`

Ghi file.
    
    
    from pathlib import Path
    
    file = Path("hello.txt")
    
    file.write_text(
        "Xin chào Python",
        encoding="utf-8"
    )

Kết quả
    
    
    hello.txt

Nội dung
    
    
    Xin chào Python

* * *

# 6\. Nếu file chưa tồn tại?

`write_text()` sẽ tự tạo file.

Ví dụ
    
    
    Path("abc.txt").write_text(
        "ABC",
        encoding="utf-8"
    )

↓

Nếu chưa có
    
    
    abc.txt

Python sẽ tạo.

* * *

# 7\. Nếu file đã tồn tại?

Nội dung cũ sẽ bị **ghi đè hoàn toàn**.

Ví dụ

File
    
    
    hello.txt
    
    ABC

Sau
    
    
    file.write_text("XYZ")

↓
    
    
    hello.txt
    
    XYZ

Không còn `ABC`.

* * *

# 8\. Ghi nhiều dòng
    
    
    text = """Chương 1
    
    Luffy
    
    Zoro
    
    Nami
    """
    
    Path("chapter.txt").write_text(
        text,
        encoding="utf-8"
    )

* * *

# 9\. Đọc Binary

Ví dụ
    
    
    cover.jpg

Không dùng
    
    
    read_text()

Mà dùng
    
    
    data = Path("cover.jpg").read_bytes()

Kiểu dữ liệu
    
    
    print(type(data))

↓
    
    
    <class 'bytes'>

* * *

# 10\. `write_bytes()`

Ví dụ
    
    
    img = Path("cover.jpg").read_bytes()
    
    Path("copy.jpg").write_bytes(img)

↓

Đã copy xong ảnh.

* * *

# 11\. Copy file bằng pathlib
    
    
    from pathlib import Path
    
    source = Path("cover.jpg")
    
    target = Path("cover_copy.jpg")
    
    target.write_bytes(
        source.read_bytes()
    )

Không cần `shutil.copy()` trong trường hợp đơn giản.

* * *

# 12\. UTF-8 là gì?

Ví dụ
    
    
    Xin chào

Máy tính không hiểu chữ.

Máy chỉ hiểu
    
    
    01001100...

Encoding là quy tắc chuyển:
    
    
    Chữ
    
    ↓
    
    Byte
    
    ↓
    
    Lưu vào ổ cứng

* * *

# 13\. UTF-8

Đây là encoding phổ biến nhất.

Ưu điểm

  * Hỗ trợ tiếng Việt 
  * Hỗ trợ Unicode 
  * Hỗ trợ Emoji 😊 
  * Đa nền tảng 



Luôn ưu tiên
    
    
    encoding="utf-8"

* * *

# 14\. UTF-8 BOM

Một số file của Notepad hoặc Excel có BOM.

Đọc bằng
    
    
    encoding="utf-8-sig"

Ví dụ
    
    
    text = file.read_text(
        encoding="utf-8-sig"
    )

* * *

# 15\. UTF-16

Một số phần mềm Windows tạo file UTF-16.
    
    
    text = file.read_text(
        encoding="utf-16"
    )

* * *

# 16\. Lỗi thường gặp
    
    
    UnicodeDecodeError

Ví dụ
    
    
    Path("abc.txt").read_text(
        encoding="utf-8"
    )

Nếu file thật sự là UTF-16

↓
    
    
    UnicodeDecodeError

* * *

# 17\. Xử lý lỗi
    
    
    from pathlib import Path
    
    file = Path("abc.txt")
    
    try:
        text = file.read_text(
            encoding="utf-8"
        )
    
    except UnicodeDecodeError:
        text = file.read_text(
            encoding="utf-16"
        )

* * *

# 18\. Đọc file JSON

Ví dụ
    
    
    config.json
    
    
    {
        "host":"localhost",
        "port":8000
    }
    
    
    import json
    from pathlib import Path
    
    config = json.loads(
        Path("config.json").read_text(
            encoding="utf-8"
        )
    )
    
    print(config)

* * *

# 19\. Ghi JSON
    
    
    import json
    from pathlib import Path
    
    config = {
        "host":"localhost",
        "port":8000
    }
    
    Path("config.json").write_text(
        json.dumps(
            config,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

Kết quả
    
    
    {
        "host": "localhost",
        "port": 8000
    }

* * *

# 20\. Đọc HTML

Crawler tải
    
    
    chapter001.html
    
    
    html = Path(
        "chapter001.html"
    ).read_text(
        encoding="utf-8"
    )

* * *

# 21\. Lưu chương truyện
    
    
    chapter = """
    Chương 1
    
    Ngày hôm đó...
    """
    
    Path(
        "downloads/chapter001.txt"
    ).write_text(
        chapter,
        encoding="utf-8"
    )

* * *

# 22\. Lưu Cache
    
    
    cache = {
        "page":12,
        "updated":"2026-07-13"
    }
    
    
    import json
    
    Path("cache/index.json").write_text(
        json.dumps(
            cache,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

* * *

# 23\. Lưu Log
    
    
    from pathlib import Path
    from datetime import datetime
    
    log = Path("logs/crawler.log")
    
    message = (
        f"[{datetime.now()}] "
        "Đã tải chapter001\n"
    )
    
    # Ghi nối tiếp (append) cần dùng open()
    with log.open("a", encoding="utf-8") as f:
        f.write(message)

> **Lưu ý:** `write_text()` luôn ghi đè nội dung. Muốn **ghi nối tiếp (append)** , hãy dùng `Path.open()` với chế độ `"a"`.

* * *

# 24\. So sánh `read_text()` và `open()`

## `read_text()`
    
    
    text = file.read_text(
        encoding="utf-8"
    )

Ưu điểm:

  * Ngắn gọn. 
  * Dễ đọc. 
  * Phù hợp với file nhỏ và vừa. 



* * *

## `open()`
    
    
    with file.open(
        "r",
        encoding="utf-8"
    ) as f:
        text = f.read()

Ưu điểm:

  * Linh hoạt hơn. 
  * Đọc từng dòng. 
  * Đọc từng phần (streaming). 
  * Ghi nối tiếp (append). 
  * Xử lý file lớn. 



* * *

# 25\. Ứng dụng trong hệ thống Crawler
    
    
    downloads/
    
        One Piece/
    
            chapter001.txt
    
            chapter002.txt
    
    images/
    
    cache/
    
    logs/
    
    database/

Đọc chương truyện:
    
    
    chapter = (
        DOWNLOAD_DIR
        / "One Piece"
        / "chapter001.txt"
    )
    
    content = chapter.read_text(
        encoding="utf-8"
    )

Lưu chương:
    
    
    chapter.write_text(
        content,
        encoding="utf-8"
    )

Lưu ảnh:
    
    
    cover.write_bytes(image_data)

Lưu cache:
    
    
    cache.write_text(
        json.dumps(data, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )

* * *

# 26\. Ví dụ hoàn chỉnh
    
    
    from pathlib import Path
    import json
    
    class NovelStorage:
    
        def __init__(self, root):
            self.root = Path(root)
    
        def save_chapter(self, novel, chapter, text):
            path = (
                self.root
                / "downloads"
                / novel
                / f"chapter{chapter:03}.txt"
            )
    
            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )
    
            path.write_text(
                text,
                encoding="utf-8"
            )
    
        def load_chapter(self, novel, chapter):
            path = (
                self.root
                / "downloads"
                / novel
                / f"chapter{chapter:03}.txt"
            )
    
            return path.read_text(
                encoding="utf-8"
            )

Đây là một nền tảng rất tốt cho dự án cào truyện.

* * *

# Những lỗi thường gặp

### 1\. Quên chỉ định `encoding`
    
    
    file.read_text()

Có thể chạy trên máy bạn nhưng lỗi trên máy khác.

Nên dùng:
    
    
    file.read_text(encoding="utf-8")

* * *

### 2\. Dùng `read_text()` để đọc ảnh

Sai:
    
    
    Path("cover.jpg").read_text()

Đúng:
    
    
    Path("cover.jpg").read_bytes()

* * *

### 3\. Dùng `write_text()` để ghi dữ liệu nhị phân

Sai:
    
    
    Path("cover.jpg").write_text(image_bytes)

Đúng:
    
    
    Path("cover.jpg").write_bytes(image_bytes)

* * *

### 4\. Mong `write_text()` ghi nối tiếp

Sai:
    
    
    log.write_text("Dòng mới")

`write_text()` sẽ xóa nội dung cũ.

Đúng:
    
    
    with log.open("a", encoding="utf-8") as f:
        f.write("Dòng mới\n")

* * *

# Bài tập thực hành

## Bài 1

Tạo file:
    
    
    hello.txt

Ghi nội dung:
    
    
    Xin chào pathlib

Sau đó đọc lại và in ra màn hình.

* * *

## Bài 2

Tạo file JSON:
    
    
    {
        "name":"Naruto",
        "chapters":700
    }

Đọc bằng `json.loads()` và in:
    
    
    Naruto
    
    700

* * *

## Bài 3

Viết chương trình sao chép một ảnh bằng:

  * `read_bytes()`
  * `write_bytes()`



* * *

## Bài 4

Viết lớp:
    
    
    class TextFileManager:
        ...

Có các phương thức:

  * `read()`
  * `write()`
  * `append()`
  * `exists()`



Sử dụng hoàn toàn `pathlib`.

* * *

## Bài 5 (Dự án thực tế)

Xây dựng lớp `CrawlerStorage` với các chức năng:

  * Lưu chương truyện (`save_chapter()`). 
  * Đọc chương truyện (`load_chapter()`). 
  * Lưu ảnh bìa (`save_cover()`). 
  * Lưu cache JSON (`save_cache()`). 
  * Đọc cache JSON (`load_cache()`). 
  * Ghi log theo chế độ nối tiếp (`append_log()`). 



Thiết kế lớp sao cho mọi thao tác đường dẫn đều sử dụng `Path` và mọi file văn bản đều sử dụng `UTF-8`.

* * *

# Tổng kết buổi 5

Bạn đã học được nhóm phương thức quan trọng nhất để làm việc với nội dung file:

  * `read_text()` và `write_text()` cho file văn bản. 
  * `read_bytes()` và `write_bytes()` cho dữ liệu nhị phân. 
  * Tầm quan trọng của `encoding`, đặc biệt là `UTF-8`. 
  * Cách xử lý `UnicodeDecodeError`. 
  * Đọc và ghi JSON kết hợp với `json`. 
  * Khi nào nên dùng `read_text()` và khi nào nên chuyển sang `Path.open()`. 



Đến thời điểm này, bạn đã có thể xây dựng một lớp lưu trữ dữ liệu hoàn chỉnh cho dự án crawler của mình. Ở **Buổi 6** , chúng ta sẽ học cách **tạo, xóa, đổi tên và di chuyển file/thư mục** với `mkdir()`, `touch()`, `unlink()`, `rename()`, `replace()`, cùng các kỹ thuật tạo cấu trúc thư mục tự động trước khi lưu dữ liệu. Đây là bước rất quan trọng để xây dựng hệ thống lưu trữ ổn định và chuyên nghiệp.

