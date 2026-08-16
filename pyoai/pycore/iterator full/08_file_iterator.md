# Iterator Deep Dive — Buổi 8

# File Iterator & Lazy Loading

Đây là một trong những ứng dụng quan trọng nhất của Iterator trong Python.

Sau buổi này, bạn sẽ hiểu vì sao các thư viện như:

  * `open()`
  * `pathlib`
  * `csv`
  * `json`
  * `sqlite3`
  * `requests`
  * `BeautifulSoup`
  * `pandas`
  * Django ORM 



đều sử dụng Iterator để xử lý dữ liệu lớn.

* * *

# Roadmap

Đã học

  * ✅ Buổi 1 — Iterator 
  * ✅ Buổi 2 — Iterable 
  * ✅ Buổi 3 — Iterator Protocol 
  * ✅ Buổi 4 — for hoạt động thế nào 
  * ✅ Buổi 5 — iter() 
  * ✅ Buổi 6 — next() 
  * ✅ Buổi 7 — Thiết kế Iterator 



Hôm nay

  * ✅ Buổi 8 — File Iterator & Lazy Loading 



Tiếp theo

  * Buổi 9 — Linked List Iterator 



* * *

# Một câu hỏi

Giả sử có file
    
    
    story.txt
    
    Line 1
    Line 2
    Line 3
    ...
    Line 10,000,000

Bạn viết
    
    
    with open("story.txt", encoding="utf8") as f:
        for line in f:
            print(line)

Có phải Python đọc toàn bộ file vào RAM không?

**Không.**

* * *

# Python làm gì?

Khi mở file
    
    
    f = open("story.txt")

`f` là một object.

Kiểm tra
    
    
    from collections.abc import Iterator
    
    print(isinstance(f, Iterator))

↓
    
    
    True

Điều đó có nghĩa
    
    
    File Object
    
    ↓
    
    Iterator

* * *

# Chứng minh
    
    
    with open("story.txt", encoding="utf8") as f:
    
        print(iter(f) is f)

↓
    
    
    True

File vừa là

  * Iterable 
  * Iterator 



* * *

# File nhớ vị trí

Giả sử file
    
    
    A
    B
    C
    D

Ta viết
    
    
    with open("story.txt", encoding="utf8") as f:
    
        print(next(f))
        print(next(f))

↓
    
    
    A
    
    B

File đang nhớ
    
    
    đã đọc tới dòng thứ 2

* * *

Tiếp tục
    
    
    print(next(f))

↓
    
    
    C

Không quay lại đầu.

* * *

# Bên trong File Iterator

Bạn có thể hình dung:
    
    
    story.txt
    
    ↓
    
    File Object
    
    ↓
    
    current_position
    
    ↓
    
    0

Sau lần đọc đầu
    
    
    current_position
    
    ↓
    
    10 bytes

Sau lần hai
    
    
    current_position
    
    ↓
    
    20 bytes

Nó chỉ lưu **offset** hiện tại trong file.

* * *

# Vì sao cần Iterator?

Giả sử file
    
    
    100 GB

Nếu Python đọc toàn bộ

↓

RAM sẽ không đủ.

* * *

Iterator chỉ đọc
    
    
    Một dòng
    
    ↓
    
    Xử lý
    
    ↓
    
    Đọc dòng tiếp
    
    ↓
    
    Xử lý

Đây gọi là

# Lazy Loading

* * *

# Lazy Loading là gì?

Lazy = trì hoãn.

Thay vì
    
    
    Đọc toàn bộ file
    
    ↓
    
    Sau đó xử lý

Python làm
    
    
    Đọc 1 dòng
    
    ↓
    
    Xử lý
    
    ↓
    
    Đọc dòng kế
    
    ↓
    
    Xử lý

* * *

# Minh họa

## Eager Loading
    
    
    File
    
    ↓
    
    RAM
    
    ↓
    
    Toàn bộ dữ liệu

* * *

## Lazy Loading
    
    
    File
    
    ↓
    
    Line 1
    
    ↓
    
    Process
    
    ↓
    
    Line 2
    
    ↓
    
    Process
    
    ↓
    
    Line 3

* * *

# next(file)

Ví dụ
    
    
    with open("story.txt", encoding="utf8") as f:
    
        print(next(f))
        print(next(f))

↓
    
    
    Line1
    
    Line2

* * *

# for hoạt động

Đoạn này
    
    
    for line in f:
        print(line)

tương đương
    
    
    while True:
    
        try:
            line = next(f)
    
        except StopIteration:
            break
    
        print(line)

Giống hệt các Iterator khác.

* * *

# readline()

Nhiều người nhầm
    
    
    f.readline()

và
    
    
    next(f)

Thực tế:
    
    
    line = next(f)

gần như tương đương
    
    
    line = f.readline()
    
    if line == "":
        raise StopIteration

* * *

# Ví dụ
    
    
    with open("story.txt", encoding="utf8") as f:
    
        while True:
    
            line = f.readline()
    
            if line == "":
                break
    
            print(line)

Có thể viết ngắn hơn
    
    
    with open("story.txt", encoding="utf8") as f:
    
        for line in f:
            print(line)

* * *

# File chỉ đọc một lần
    
    
    with open("story.txt", encoding="utf8") as f:
    
        for line in f:
            print(line)
    
        print("Lần hai")
    
        for line in f:
            print(line)

↓
    
    
    Line1
    Line2
    Line3
    
    Lần hai

Không còn gì.

* * *

# Vì sao?

Vì File chính là Iterator.

Không giống List.

* * *

# Muốn đọc lại

Có hai cách.

## Cách 1

Mở file lại
    
    
    with open("story.txt") as f:
        ...

* * *

## Cách 2

Dùng
    
    
    f.seek(0)

Ví dụ
    
    
    with open("story.txt") as f:
    
        print(next(f))
    
        f.seek(0)
    
        print(next(f))

↓
    
    
    Line1
    
    Line1

`seek(0)` đưa con trỏ file về đầu file.

* * *

# Đọc từng khối (Chunk)

Không phải lúc nào cũng đọc từng dòng.

Ví dụ đọc ảnh
    
    
    with open("image.jpg", "rb") as f:
    
        while True:
    
            chunk = f.read(1024)
    
            if not chunk:
                break
    
            print(len(chunk))

↓
    
    
    1024
    1024
    1024
    ...
    530

* * *

# Dùng iter(callable, sentinel)

Đây là cách chuyên nghiệp hơn.
    
    
    from functools import partial
    
    with open("image.jpg", "rb") as f:
    
        for chunk in iter(partial(f.read, 1024), b""):
            print(len(chunk))

Bạn đã học `iter(callable, sentinel)` ở buổi trước.

Ở đây:
    
    
    partial(f.read, 1024)
    
    ↓
    
    Callable
    
    ↓
    
    1024 bytes
    
    ↓
    
    ...
    
    ↓
    
    b""
    
    ↓
    
    StopIteration

* * *

# Tự xây File Iterator

Giả sử ta muốn đọc từng dòng từ một nguồn dữ liệu giả lập.
    
    
    class TextFileIterator:
    
        def __init__(self, lines):
            self.lines = lines
            self.index = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.index >= len(self.lines):
                raise StopIteration
    
            line = self.lines[self.index]
            self.index += 1
    
            return line

Sử dụng
    
    
    data = [
        "Hello",
        "Python",
        "Iterator"
    ]
    
    it = TextFileIterator(data)
    
    for line in it:
        print(line)

↓
    
    
    Hello
    Python
    Iterator

* * *

# Thiết kế chuẩn hơn

Như buổi trước, ta tách thành:
    
    
    TextFile
    
    ↓
    
    TextFileIterator
    
    
    class TextFile:
    
        def __init__(self, lines):
            self.lines = lines
    
        def __iter__(self):
            return TextFileIterator(self.lines)

Lúc này có thể lặp nhiều lần.

* * *

# Lazy Database

Ý tưởng này cũng được dùng trong database.

Ví dụ:
    
    
    cursor.execute("""
    SELECT *
    FROM users
    """)
    
    for row in cursor:
        print(row)

Python không lấy toàn bộ bảng.

Cursor thường lấy từng bản ghi hoặc từng lô (batch) từ cơ sở dữ liệu.

* * *

# Lazy Web Crawler

Giả sử bạn đang viết app cào truyện (đúng với dự án bạn đang học).

Thay vì:
    
    
    chapters = crawl_all_chapters()
    
    for chapter in chapters:
        ...

có thể thiết kế:
    
    
    for chapter in crawler:
        process(chapter)

Mỗi lần `next(crawler)`:
    
    
    HTTP Request
    
    ↓
    
    Parse HTML
    
    ↓
    
    Trả về Chapter
    
    ↓
    
    Request tiếp

Ưu điểm:

  * Không cần lưu hàng nghìn chapter trong RAM. 
  * Có thể dừng giữa chừng. 
  * Có thể tiếp tục xử lý ngay khi tải xong một chapter. 



Đây là một ví dụ điển hình của **Lazy Loading** trong các ứng dụng crawler.

* * *

# Lazy CSV Reader

Thư viện `csv` cũng hoạt động tương tự.
    
    
    import csv
    
    with open("users.csv", newline="", encoding="utf8") as f:
    
        reader = csv.reader(f)
    
        for row in reader:
            print(row)

`csv.reader()` trả về một Iterator, mỗi lần lặp sẽ phân tích (parse) đúng một dòng CSV.

* * *

# So sánh Eager và Lazy

Eager Loading| Lazy Loading  
---|---  
Đọc toàn bộ dữ liệu| Đọc từng phần  
Tốn RAM| Ít RAM  
Chậm lúc bắt đầu| Bắt đầu nhanh  
Phù hợp dữ liệu nhỏ| Phù hợp dữ liệu lớn  
Có thể truy cập ngẫu nhiên dễ dàng| Chủ yếu truy cập tuần tự  
  
* * *

# Ví dụ hoàn chỉnh
    
    
    class LogFile:
    
        def __init__(self, filename):
            self.filename = filename
    
        def __iter__(self):
            return open(self.filename, encoding="utf8")
    
    
    for line in LogFile("server.log"):
        if "ERROR" in line:
            print(line.rstrip())

Ý tưởng:

  * `LogFile` là một **Iterable**. 
  * `open()` trả về một **File Iterator**. 
  * Vòng lặp xử lý từng dòng ngay khi đọc được, không cần nạp toàn bộ file vào bộ nhớ. 



Trong thực tế, bạn nên kết hợp với context manager (`with`) để đảm bảo file luôn được đóng đúng cách. Ví dụ trên nhằm minh họa mối quan hệ giữa `Iterable` và `Iterator`.

* * *

# Tổng kết buổi 8

Bạn cần ghi nhớ:

  1. File object trong Python là một **Iterator**. 
  2. `for line in file` thực chất là gọi `next(file)` liên tục. 
  3. File chỉ được duyệt một lần, trừ khi dùng `seek()` hoặc mở lại file. 
  4. Lazy Loading giúp xử lý các file rất lớn mà không tốn nhiều RAM. 
  5. `iter(callable, sentinel)` là cách rất hiệu quả để đọc dữ liệu theo từng khối. 
  6. Ý tưởng Lazy Loading được áp dụng rộng rãi trong: 
     * File I/O 
     * CSV 
     * Database Cursor 
     * ORM 
     * Web Crawler 
     * API phân trang (pagination) 



* * *

# Bài tập

## Bài 1

Viết lớp:
    
    
    class ChunkReader:

Yêu cầu:

  * Nhận vào một chuỗi (`str`) và kích thước khối (`chunk_size`). 
  * Khi lặp, trả về từng đoạn có độ dài `chunk_size`. 



Ví dụ:
    
    
    reader = ChunkReader("HelloPython", 5)
    
    for chunk in reader:
        print(chunk)

Kết quả:
    
    
    Hello
    Pytho
    n

* * *

## Bài 2

Viết `LineIterator` và `LineCollection` (không dùng `open()`), trong đó:

  * `LineCollection` chứa danh sách các dòng. 
  * Mỗi lần `iter(collection)` tạo một `LineIterator` mới. 
  * Chứng minh có thể lặp hai lần liên tiếp mà vẫn nhận đủ dữ liệu. 



* * *

## Bài 3 (gần với dự án crawler của bạn)

Thiết kế:
    
    
    class ChapterCrawler:

Yêu cầu:

  * Giả lập danh sách URL các chương. 
  * Mỗi lần `next()` chỉ "tải" một chương (có thể dùng `print("Downloading:", url)` để mô phỏng). 
  * Trả về nội dung của chương đó. 
  * Không tải tất cả chương ngay từ đầu. 



Đây là một ví dụ điển hình về **Lazy Iterator** mà bạn sẽ gặp khi xây dựng các ứng dụng crawler hoặc xử lý dữ liệu quy mô lớn.

