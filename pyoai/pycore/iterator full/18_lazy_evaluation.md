# Iterator Deep Dive

# Phần IV — Iterator nâng cao

# Buổi 18: Lazy Evaluation Deep Dive

Đây là **một trong những buổi quan trọng nhất của toàn bộ khóa học**.

Rất nhiều lập trình viên biết:

  * Iterator 
  * Generator 
  * `yield`



nhưng lại **không hiểu triết lý Lazy Evaluation**.

Trong khi đó, Lazy Evaluation chính là nền tảng của:

  * `itertools`
  * `map`
  * `filter`
  * `zip`
  * `enumerate`
  * `reversed`
  * File Iterator 
  * Database Cursor 
  * `pathlib.Path.glob()`
  * `os.scandir()`
  * `csv.reader`
  * `sqlite3.Cursor`
  * Async Generator 
  * Streaming API 



Sau buổi này, bạn sẽ nhìn Python theo một cách hoàn toàn khác.

* * *

# Roadmap

## Phần IV

  * ✅ Buổi 17 — itertools 
  * ✅ **Buổi 18 — Lazy Evaluation**
  * Buổi 19 — Infinite Iterator 
  * Buổi 20 — Async Iterator 
  * Buổi 21 — Performance 
  * Buổi 22 — Thiết kế thư viện sử dụng Iterator 
  * Buổi 23 — Dự án thực tế 



* * *

# 1\. Lazy Evaluation là gì?

Có hai cách xử lý dữ liệu.

## Eager (Háo hức)

Làm tất cả ngay lập tức.
    
    
    Input
    
    ↓
    
    Xử lý toàn bộ
    
    ↓
    
    Lưu toàn bộ
    
    ↓
    
    Output

Ví dụ
    
    
    numbers = [x * x for x in range(5)]
    
    print(numbers)

Python tính ngay
    
    
    0
    1
    4
    9
    16

* * *

## Lazy (Lười)

Chỉ làm khi có người yêu cầu.
    
    
    Input
    
    ↓
    
    Chờ
    
    ↓
    
    next()
    
    ↓
    
    Sinh 1 giá trị
    
    ↓
    
    Chờ
    
    ↓
    
    next()

* * *

# Ví dụ
    
    
    def numbers():
    
        print("Create 1")
        yield 1
    
        print("Create 2")
        yield 2
    
        print("Create 3")
        yield 3

Tạo
    
    
    g = numbers()

↓

Không in gì.

* * *

Lần đầu
    
    
    next(g)

↓
    
    
    Create 1
    1

* * *

Lần hai

↓
    
    
    Create 2
    2

Đây chính là Lazy.

* * *

# Minh họa

Eager
    
    
    1
    2
    3
    4
    5
    
    ↓
    
    RAM

* * *

Lazy
    
    
    1
    
    ↓
    
    next()
    
    ↓
    
    2
    
    ↓
    
    next()
    
    ↓
    
    3

* * *

# 2\. Vì sao cần Lazy?

Giả sử có
    
    
    range(1_000_000_000)

Nếu Eager

↓

Python phải tạo
    
    
    1 tỷ số

Nếu Lazy

↓

Chỉ tạo
    
    
    1 số

mỗi lần.

* * *

# 3\. List vs Generator

List
    
    
    numbers = [x*x for x in range(5)]

↓
    
    
    0
    1
    4
    9
    16

được tạo ngay.

* * *

Generator
    
    
    numbers = (x*x for x in range(5))

↓

Không tạo gì.

* * *

# Ví dụ trực quan
    
    
    def square(x):
        print(f"Calculating {x}")
        return x*x

List
    
    
    result = [
        square(i)
        for i in range(3)
    ]

↓
    
    
    Calculating 0
    
    Calculating 1
    
    Calculating 2

* * *

Generator
    
    
    result = (
        square(i)
        for i in range(3)
    )

↓

Không in.

* * *

Khi
    
    
    next(result)

↓
    
    
    Calculating 0
    
    0

* * *

# 4\. map()

Ít người biết.

`map()`

cũng Lazy.
    
    
    def double(x):
        print(x)
        return x*2
    
    
    m = map(
        double,
        [1,2,3]
    )

↓

Không in gì.

* * *

Chỉ khi
    
    
    next(m)

↓
    
    
    1
    2

Lần sau

↓
    
    
    2
    4

* * *

# map() trả về gì?
    
    
    m = map(str, [1,2,3])
    
    print(type(m))

↓
    
    
    <class 'map'>

Đây là một Iterator.

* * *

# 5\. filter()
    
    
    def even(x):
    
        print(f"Check {x}")
    
        return x % 2 == 0
    
    
    f = filter(
        even,
        range(5)
    )

Không chạy.

* * *

Lần đầu
    
    
    next(f)

↓
    
    
    Check 0
    
    0

* * *

Lần hai

↓
    
    
    Check 1
    
    Check 2
    
    2

`filter` chỉ chạy đủ để tìm phần tử kế tiếp thỏa điều kiện.

* * *

# 6\. zip()
    
    
    names = [
        "An",
        "Bình",
        "Lan"
    ]
    
    ages = [
        20,
        21,
        22
    ]
    
    z = zip(names, ages)

↓

Không tạo
    
    
    [
    ("An",20),
    ...
    ]

* * *

Lần đầu
    
    
    next(z)

↓
    
    
    ("An",20)

* * *

# 7\. enumerate()
    
    
    e = enumerate(
        ["A","B","C"]
    )

↓

Không tạo.

* * *
    
    
    next(e)

↓
    
    
    (0,"A")

* * *

# 8\. reversed()
    
    
    r = reversed(
        [1,2,3]
    )

Không tạo List mới.

↓
    
    
    next(r)

↓
    
    
    3

* * *

# 9\. dict_keys
    
    
    data = {
        "a":1,
        "b":2
    }
    
    keys = data.keys()

Không phải List.
    
    
    print(type(keys))

↓
    
    
    dict_keys

Đây là một **view** phản ánh trực tiếp nội dung của từ điển.

* * *

## View là Lazy
    
    
    data = {
        "a":1
    }
    
    keys = data.keys()
    
    print(keys)
    
    data["b"] = 2
    
    print(keys)

↓
    
    
    dict_keys(['a'])
    
    dict_keys(['a','b'])

Không tạo bản sao.

* * *

# 10\. File Iterator
    
    
    with open("story.txt") as f:
    
        for line in f:
            ...

Không đọc toàn bộ file.

↓

Mỗi lần
    
    
    next()

↓

Đọc
    
    
    1 dòng

* * *

Nếu file
    
    
    100 GB

vẫn chạy được.

* * *

# 11\. pathlib
    
    
    from pathlib import Path
    
    files = Path(".").glob("*.py")

↓

Không duyệt thư mục ngay.

* * *

Khi
    
    
    for f in files:
        ...

↓

Mới tìm từng tệp.

* * *

# 12\. os.scandir()
    
    
    import os
    
    entries = os.scandir(".")

↓

Iterator.

Không tạo danh sách tất cả tệp.

* * *

# 13\. sqlite3 Cursor
    
    
    cursor.execute(
        "SELECT * FROM users"
    )
    
    for row in cursor:
        ...

Cursor trả từng bản ghi một, thay vì tải toàn bộ bảng vào RAM.

* * *

# 14\. csv.reader
    
    
    import csv
    
    with open("users.csv") as f:
    
        reader = csv.reader(f)
    
        for row in reader:
            ...

↓

Từng dòng.

* * *

# 15\. Pipeline

Đây là triết lý quan trọng nhất.

Ví dụ
    
    
    numbers = range(100)

Pipeline
    
    
    result = map(
        lambda x:x*x,
        filter(
            lambda x:x%2==0,
            numbers
        )
    )

Không có List.

* * *

Luồng
    
    
    100
    
    ↓
    
    filter
    
    ↓
    
    50
    
    ↓
    
    map
    
    ↓
    
    Iterator
    
    ↓
    
    next()

Không tạo dữ liệu trung gian.

* * *

# Ví dụ Generator Pipeline
    
    
    numbers = (
        x
        for x in range(100)
    )
    
    evens = (
        x
        for x in numbers
        if x % 2 == 0
    )
    
    squares = (
        x*x
        for x in evens
    )

Không có List nào.

* * *

# Minh họa
    
    
    Generator
    
    ↓
    
    Filter
    
    ↓
    
    Map
    
    ↓
    
    Save

Mỗi bước chỉ xử lý **một phần tử**.

* * *

# Ví dụ crawler
    
    
    urls = generate_urls()

↓
    
    
    htmls = (
        download(url)
        for url in urls
    )

↓
    
    
    books = (
        parse(html)
        for html in htmls
    )

↓
    
    
    titles = (
        book.title
        for book in books
    )

↓
    
    
    for title in titles:
        save(title)

Không có bước nào cần giữ toàn bộ dữ liệu.

* * *

# Ví dụ ETL
    
    
    CSV
    
    ↓
    
    Read
    
    ↓
    
    Validate
    
    ↓
    
    Transform
    
    ↓
    
    Save

Toàn bộ đều là Iterator.

* * *

# Ví dụ Log Processing
    
    
    Log File
    
    ↓
    
    Read Line
    
    ↓
    
    Parse
    
    ↓
    
    Filter ERROR
    
    ↓
    
    Count

* * *

# Khi nào không nên Lazy?

Không phải lúc nào Lazy cũng tốt.

Ví dụ
    
    
    users = (
        load_user(i)
        for i in range(10)
    )

Nếu cần
    
    
    len(users)

↓

Không được.

* * *

Nếu cần
    
    
    users[5]

↓

Không được.

* * *

Nếu cần
    
    
    for u in users:
        ...
    
    for u in users:
        ...

↓

Lần hai

không còn gì.

* * *

# Khi nào nên Eager?

Nếu:

  * Dữ liệu nhỏ. 
  * Truy cập nhiều lần. 
  * Cần truy cập ngẫu nhiên. 
  * Cần `len()`. 
  * Cần sắp xếp nhiều lần. 



→ Dùng `list`, `tuple` hoặc các cấu trúc dữ liệu eager khác.

* * *

# Khi nào nên Lazy?

Nếu:

  * File lớn. 
  * Dữ liệu vô hạn. 
  * Crawler. 
  * ETL. 
  * Streaming. 
  * Database Cursor. 
  * API Streaming. 
  * AI Streaming. 
  * Socket. 



* * *

# Sai lầm phổ biến

## Sai lầm 1
    
    
    gen = (
        x
        for x in range(5)
    )
    
    print(list(gen))
    print(list(gen))

↓
    
    
    [0,1,2,3,4]
    
    []

Generator đã bị tiêu thụ.

* * *

## Sai lầm 2

Biến đổi qua `list()` quá sớm:
    
    
    result = list(filter(...))

Bạn đã phá vỡ pipeline lazy và buộc Python tạo toàn bộ dữ liệu trong bộ nhớ.

* * *

## Sai lầm 3

Dùng lazy cho dữ liệu rất nhỏ rồi nghĩ rằng luôn nhanh hơn.

Lazy chủ yếu giúp **tiết kiệm bộ nhớ** và hỗ trợ xử lý theo luồng; với dữ liệu nhỏ, chi phí quản lý Iterator đôi khi còn cao hơn việc dùng `list`.

* * *

# Thiết kế pipeline cho ứng dụng crawler

Đây là mô hình rất phù hợp với dự án crawler truyện của bạn:
    
    
    Source Plugin
          │
          ▼
    Generate URLs
          │
          ▼
    Download HTML
          │
          ▼
    Parse HTML
          │
          ▼
    Extract Chapters
          │
          ▼
    Normalize Data
          │
          ▼
    Repository.save()

Mỗi khối:

  * Nhận vào một `Iterable`. 
  * Trả về một `Iterator` hoặc `Generator`. 
  * Không biết bước trước hay bước sau hoạt động thế nào. 



Ví dụ:
    
    
    def generate_urls():
        for page in range(1, 1001):
            yield f"https://example.com/page/{page}"
    
    
    def download(urls):
        for url in urls:
            yield f"<html>{url}</html>"
    
    
    def parse(htmls):
        for html in htmls:
            yield {"title": html[6:-7]}
    
    
    def save(items):
        for item in items:
            print(f"Saved: {item['title']}")

Ghép pipeline:
    
    
    urls = generate_urls()
    htmls = download(urls)
    books = parse(htmls)
    
    save(books)

Đây là cách xây dựng các pipeline dữ liệu lớn mà **không cần giữ toàn bộ dữ liệu trong RAM**.

* * *

# Tổng kết buổi 18

Bạn cần ghi nhớ 10 ý quan trọng:

  1. **Lazy Evaluation** nghĩa là chỉ tính toán khi thực sự cần. 
  2. Iterator và Generator là hai công cụ cốt lõi để hiện thực Lazy Evaluation trong Python. 
  3. `map()`, `filter()`, `zip()`, `enumerate()`, `reversed()` đều hoạt động theo cơ chế lazy. 
  4. Các `dict` view (`keys()`, `values()`, `items()`) phản ánh dữ liệu hiện tại, không tạo bản sao. 
  5. File, `csv.reader`, `sqlite3.Cursor`, `Path.glob()`, `os.scandir()` đều tận dụng lazy để xử lý dữ liệu lớn. 
  6. Pipeline lazy giúp loại bỏ các danh sách trung gian. 
  7. Mỗi phần tử đi qua toàn bộ pipeline trước khi phần tử tiếp theo được tạo. 
  8. Lazy giúp tiết kiệm bộ nhớ, đặc biệt với dữ liệu lớn hoặc vô hạn. 
  9. Lazy không phải lúc nào cũng nhanh hơn; nó là một sự đánh đổi giữa CPU và bộ nhớ. 
  10. Thiết kế các hàm nhận và trả về `Iterable`/`Iterator` giúp mã nguồn linh hoạt và dễ kết hợp. 



* * *

# Bài tập

## Bài 1

Xây dựng pipeline gồm 3 Generator:
    
    
    generate_numbers()
            ↓
    filter_even()
            ↓
    square()

Cuối cùng chỉ in 10 kết quả đầu tiên bằng `itertools.islice()`.

* * *

## Bài 2

Viết một `LazyFileReader`:
    
    
    class LazyFileReader:
        ...

Yêu cầu:

  * Nhận đường dẫn tệp. 
  * Mỗi lần lặp chỉ đọc đúng **một dòng**. 
  * Có thể dùng trong: 


    
    
    for line in LazyFileReader("log.txt"):
        ...

* * *

## Bài 3

Thiết kế một pipeline crawler hoàn chỉnh:
    
    
    PageGenerator
          ↓
    Downloader
          ↓
    Parser
          ↓
    ChapterExtractor
          ↓
    Repository

Mỗi thành phần là một Generator hoặc Iterator độc lập, chỉ xử lý **một phần tử tại một thời điểm**. Đây là mô hình kiến trúc rất gần với các hệ thống crawler và ETL chuyên nghiệp.

* * *

Ở **Buổi 19** , chúng ta sẽ nghiên cứu **Infinite Iterator** : cách thiết kế các luồng dữ liệu vô hạn (Fibonacci, số nguyên tố, cảm biến, event stream...), cách dừng chúng an toàn bằng `islice()`, `takewhile()`, và cách áp dụng vào các hệ thống xử lý dữ liệu thời gian thực.

