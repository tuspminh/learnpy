# Iterator Deep Dive

# Phần IV — Iterator nâng cao

# Buổi 17: `itertools` Deep Dive (Phần 1)

Đây là buổi mở đầu của phần Iterator nâng cao.

Nếu Generator giúp bạn **tự tạo Iterator** , thì `itertools` giúp bạn **kết hợp (compose)** nhiều Iterator thành các **pipeline xử lý dữ liệu** hiệu quả.

Có thể xem `itertools` là một **"hộp công cụ Lego"** cho Iterator.

Nhiều thư viện lớn như:

  * Pandas 
  * SQLAlchemy 
  * Django 
  * FastAPI 
  * Requests 
  * BeautifulSoup 
  * asyncio 



đều sử dụng các ý tưởng tương tự `itertools`.

* * *

# Roadmap

## Phần IV – Iterator nâng cao

  * ✅ Buổi 17 — `itertools` (Phần 1) 
  * Buổi 18 — Lazy Evaluation 
  * Buổi 19 — Infinite Iterator 
  * Buổi 20 — Async Iterator 
  * Buổi 21 — Performance 
  * Buổi 22 — Thiết kế thư viện sử dụng Iterator 
  * Buổi 23 — Dự án thực tế 



* * *

# 1\. itertools là gì?
    
    
    import itertools

`itertools` là module chuẩn của Python.

Nó không tạo ra kiểu dữ liệu mới.

Nó tạo ra:
    
    
    Iterator
    
    ↓
    
    Iterator
    
    ↓
    
    Iterator

Mọi hàm trong `itertools` đều trả về **Iterator**.

* * *

# Triết lý của itertools

Không viết
    
    
    result = []
    
    for x in data:
        if condition(x):
            result.append(transform(x))

Mà viết
    
    
    result = map(
        transform,
        filter(condition, data)
    )

Hoặc
    
    
    from itertools import islice
    
    result = islice(
        filter(condition, data),
        10
    )

Đây gọi là

> **Iterator Pipeline**

* * *

# Sơ đồ
    
    
    File
    
    ↓
    
    filter()
    
    ↓
    
    map()
    
    ↓
    
    islice()
    
    ↓
    
    Database

Không có List trung gian.

* * *

# 2\. count()

Đây là Iterator vô hạn.
    
    
    from itertools import count
    
    counter = count()
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    0
    1
    2

* * *

Có thể bắt đầu từ số khác
    
    
    counter = count(100)

↓
    
    
    100
    101
    102

* * *

Có thể tăng theo bước
    
    
    counter = count(10, 5)
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    10
    15
    20

* * *

## Ứng dụng

Sinh ID
    
    
    from itertools import count
    
    ids = count(1)
    
    for _ in range(5):
        print(next(ids))

↓
    
    
    1
    2
    3
    4
    5

* * *

# 3\. cycle()

Lặp vô hạn.
    
    
    from itertools import cycle
    
    colors = cycle([
        "red",
        "green",
        "blue"
    ])
    
    for _ in range(8):
        print(next(colors))

↓
    
    
    red
    green
    blue
    red
    green
    blue
    red
    green

* * *

## Ứng dụng

Round Robin
    
    
    Worker1
    
    ↓
    
    Worker2
    
    ↓
    
    Worker3
    
    ↓
    
    Worker1

* * *

Ví dụ
    
    
    from itertools import cycle
    
    workers = cycle([
        "A",
        "B",
        "C"
    ])
    
    jobs = [
        "Job1",
        "Job2",
        "Job3",
        "Job4",
        "Job5"
    ]
    
    for job in jobs:
        print(next(workers), job)

↓
    
    
    A Job1
    B Job2
    C Job3
    A Job4
    B Job5

* * *

# 4\. repeat()

Lặp một giá trị.
    
    
    from itertools import repeat
    
    r = repeat("Python", 3)
    
    for x in r:
        print(x)

↓
    
    
    Python
    Python
    Python

* * *

Không giới hạn
    
    
    repeat(0)

↓
    
    
    0
    0
    0
    0
    ...

* * *

## Ứng dụng

Ghép dữ liệu
    
    
    from itertools import repeat
    
    names = [
        "An",
        "Bình",
        "Cường"
    ]
    
    ages = repeat(18)
    
    for item in zip(names, ages):
        print(item)

↓
    
    
    ('An',18)
    
    ('Bình',18)
    
    ('Cường',18)

* * *

# 5\. chain()

Ghép nhiều Iterator.
    
    
    from itertools import chain
    
    a = [1,2]
    
    b = [3,4]
    
    c = [5,6]
    
    for x in chain(a,b,c):
        print(x)

↓
    
    
    1
    2
    3
    4
    5
    6

* * *

Không cần
    
    
    a+b+c

nên không tạo List mới.

* * *

## chain.from_iterable()
    
    
    from itertools import chain
    
    matrix = [
        [1,2],
        [3,4],
        [5,6]
    ]
    
    for x in chain.from_iterable(matrix):
        print(x)

↓
    
    
    1
    2
    3
    4
    5
    6

Đây là cách "làm phẳng" (flatten) một cấp rất hiệu quả.

* * *

# 6\. islice()

Cắt Iterator.

Iterator không hỗ trợ
    
    
    iterator[5:10]

Ta dùng
    
    
    from itertools import islice
    
    numbers = count()
    
    for x in islice(numbers, 5):
        print(x)

↓
    
    
    0
    1
    2
    3
    4

* * *

Bắt đầu từ vị trí
    
    
    numbers = count()
    
    for x in islice(numbers, 10, 15):
        print(x)

↓
    
    
    10
    11
    12
    13
    14

* * *

Bước nhảy
    
    
    numbers = count()
    
    for x in islice(numbers, 0, 10, 2):
        print(x)

↓
    
    
    0
    2
    4
    6
    8

* * *

# Ứng dụng

Crawler
    
    
    pages = crawl_all_pages()
    
    first10 = islice(
        pages,
        10
    )
    
    for page in first10:
        save(page)

Không cần crawl toàn bộ website.

* * *

# 7\. pairwise()

Python 3.10+
    
    
    from itertools import pairwise
    
    for pair in pairwise([
        1,
        2,
        3,
        4
    ]):
        print(pair)

↓
    
    
    (1,2)
    
    (2,3)
    
    (3,4)

* * *

## Ứng dụng

Tính khoảng cách
    
    
    points = [
        (0,0),
        (1,1),
        (2,5)
    ]

Duyệt
    
    
    (0,0)
    
    ↓
    
    (1,1)

rồi
    
    
    (1,1)
    
    ↓
    
    (2,5)

* * *

# 8\. batched()

Python 3.12+

Chia thành nhóm.
    
    
    from itertools import batched
    
    for group in batched(
        range(10),
        3
    ):
        print(group)

↓
    
    
    (0,1,2)
    
    (3,4,5)
    
    (6,7,8)
    
    (9,)

* * *

## Ứng dụng

Batch Insert
    
    
    records = range(1000000)
    
    for batch in batched(
        records,
        1000
    ):
        save_database(batch)

Không cần giữ toàn bộ dữ liệu trong RAM.

* * *

# Ví dụ tổng hợp

Giả sử có dữ liệu
    
    
    numbers = range(100)

Ta muốn:

  * bình phương 
  * chỉ lấy số chẵn 
  * lấy 5 phần tử đầu 


    
    
    from itertools import islice
    
    pipeline = islice(
        (
            x*x
            for x in numbers
            if x % 2 == 0
        ),
        5
    )
    
    for x in pipeline:
        print(x)

↓
    
    
    0
    4
    16
    36
    64

Không tạo bất kỳ danh sách trung gian nào.

* * *

# Ứng dụng trong dự án crawler

Giả sử bạn có:
    
    
    books = crawl_books()

Mỗi `book` có nhiều chapter.

Ta có thể tạo pipeline:
    
    
    from itertools import chain
    
    chapters = chain.from_iterable(
        book.chapters
        for book in books
    )
    
    for chapter in islice(chapters, 100):
        print(chapter.title)

Luồng dữ liệu:
    
    
    Crawler
    
    ↓
    
    Book Generator
    
    ↓
    
    Chapter Generator
    
    ↓
    
    chain.from_iterable()
    
    ↓
    
    islice()
    
    ↓
    
    Database

Đây là phong cách xử lý rất phổ biến trong các hệ thống crawler và ETL.

* * *

# Những sai lầm phổ biến

## Sai lầm 1
    
    
    list(chain(a, b))

Nếu dữ liệu rất lớn, bạn lại mất lợi ích của Iterator vì đã chuyển toàn bộ sang `list`.

* * *

## Sai lầm 2
    
    
    count()

rồi dùng trực tiếp trong
    
    
    for x in count():
        ...

mà không có điều kiện dừng.

Đây là Iterator vô hạn.

* * *

## Sai lầm 3
    
    
    cycle(big_list)

`cycle()` phải lưu lại toàn bộ phần tử để lặp lại, nên nếu `big_list` rất lớn hoặc là một Iterator vô hạn thì không phù hợp.

* * *

## Sai lầm 4

Dùng `chain(a, b)` khi chỉ cần:
    
    
    for x in a:
        ...
    
    for x in b:
        ...

`chain()` phát huy sức mạnh nhất khi xây dựng **pipeline** , không phải lúc nào cũng cần thay thế vòng lặp.

* * *

# Tổng kết buổi 17

Bạn cần nhớ:

  1. `itertools` là thư viện chuẩn chuyên về Iterator. 
  2. Hầu hết các hàm trong `itertools` đều trả về **Iterator**. 
  3. `count()`, `cycle()`, `repeat()` tạo Iterator (nhiều trường hợp là vô hạn). 
  4. `chain()` và `chain.from_iterable()` dùng để ghép hoặc làm phẳng nhiều Iterable. 
  5. `islice()` cắt Iterator mà không cần tạo danh sách. 
  6. `pairwise()` giúp duyệt theo từng cặp liên tiếp. 
  7. `batched()` chia dữ liệu thành các lô (batch), rất hữu ích khi xử lý dữ liệu lớn. 
  8. Kết hợp `itertools` với Generator giúp xây dựng các **pipeline lazy** , tiết kiệm bộ nhớ và dễ mở rộng. 



* * *

# Bài tập

## Bài 1

Viết một hàm sinh URL vô hạn bằng `count()`:
    
    
    from itertools import count
    
    def page_urls():
        ...

Kết quả:
    
    
    https://example.com/page/1
    https://example.com/page/2
    https://example.com/page/3
    ...

Sau đó dùng `islice()` chỉ lấy 10 URL đầu tiên.

* * *

## Bài 2

Cho dữ liệu:
    
    
    books = [
        ["C1", "C2"],
        ["C3"],
        ["C4", "C5", "C6"]
    ]

Sử dụng `chain.from_iterable()` để duyệt và in:
    
    
    C1
    C2
    C3
    C4
    C5
    C6

Không dùng hai vòng `for` lồng nhau.

* * *

## Bài 3

Mô phỏng hệ thống lưu cơ sở dữ liệu:

  * Sinh 10.000 bản ghi bằng Generator. 
  * Dùng `batched()` để chia thành các nhóm 500 bản ghi. 
  * Với mỗi nhóm, in: 


    
    
    Saving batch 1 (500 records)
    Saving batch 2 (500 records)
    ...

Đây là mô hình rất phổ biến khi ghi dữ liệu từ crawler hoặc ETL vào cơ sở dữ liệu, giúp tránh tiêu tốn quá nhiều bộ nhớ và giảm số lần ghi xuống database.

Ở **Buổi 18** , chúng ta sẽ đi sâu vào **Lazy Evaluation** : không chỉ trong Generator mà còn trong `map()`, `filter()`, `zip()`, `enumerate()`, `reversed()`, `dict_keys`, `dict_values`, cũng như cách thiết kế các **pipeline xử lý dữ liệu** hoàn toàn lazy như trong các thư viện chuyên nghiệp.

