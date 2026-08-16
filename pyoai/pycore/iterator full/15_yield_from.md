# Iterator Deep Dive

# Phần III — Generator

# Buổi 15: `yield from` Deep Dive — Ủy quyền Generator

Đây là một trong những chủ đề **nâng cao nhất của Generator**.

Rất nhiều người nghĩ:

> "`yield from` chỉ là cách viết ngắn hơn của `for ... yield`."

Điều đó **đúng nhưng chưa đủ**.

`yield from` còn thực hiện:

  * Ủy quyền (`delegation`) 
  * Chuyển tiếp `next()`
  * Chuyển tiếp `send()`
  * Chuyển tiếp `throw()`
  * Chuyển tiếp `close()`
  * Nhận giá trị `return` của Generator con 



Đó là lý do `yield from` từng là nền tảng của nhiều framework bất đồng bộ trước khi `async/await` xuất hiện.

* * *

# Roadmap

## Phần III – Generator

  * ✅ Buổi 13 — Generator là Iterator 
  * ✅ Buổi 14 — `yield`
  * ✅ **Buổi 15 —`yield from`**
  * Buổi 16 — Generator Expression 



* * *

# Bài toán

Giả sử có Generator
    
    
    def numbers():
    
        yield 1
        yield 2
        yield 3

Ta muốn tạo
    
    
    def all_numbers():
    
        ...

để trả về
    
    
    1
    2
    3

* * *

# Cách 1
    
    
    def all_numbers():
    
        for x in numbers():
            yield x

Đây là cách mọi người thường viết.

* * *

# Kết quả
    
    
    for x in all_numbers():
        print(x)

↓
    
    
    1
    2
    3

* * *

# Python có cách ngắn hơn
    
    
    def all_numbers():
    
        yield from numbers()

Hoạt động giống hệt.

* * *

# So sánh

Viết tay
    
    
    for item in iterable:
        yield item

Viết bằng
    
    
    yield from iterable

Nếu chỉ xét `next()`, hai cách gần như tương đương.

* * *

# Minh họa

Không dùng `yield from`
    
    
    Generator A
    
    ↓
    
    for
    
    ↓
    
    Generator B
    
    ↓
    
    yield

* * *

Có `yield from`
    
    
    Generator A
    
    ↓
    
    yield from
    
    ↓
    
    Generator B

Python chuyển tiếp trực tiếp.

* * *

# Ví dụ
    
    
    def letters():
    
        yield "A"
        yield "B"
    
    
    def numbers():
    
        yield 1
        yield 2

Ghép
    
    
    def everything():
    
        yield from letters()
    
        yield from numbers()

* * *

Kết quả
    
    
    for x in everything():
        print(x)

↓
    
    
    A
    B
    1
    2

* * *

# yield from List

Không nhất thiết phải là Generator.
    
    
    def demo():
    
        yield from [10,20,30]

↓
    
    
    10
    20
    30

* * *

# yield from Tuple
    
    
    def demo():
    
        yield from (1,2,3)

↓
    
    
    1
    2
    3

* * *

# yield from String
    
    
    def demo():
    
        yield from "Python"

↓
    
    
    P
    y
    t
    h
    o
    n

Vì String cũng là Iterable.

* * *

# yield from Dictionary
    
    
    def demo():
    
        yield from {
            "a":1,
            "b":2
        }

↓
    
    
    a
    b

Giống
    
    
    for k in dict:

* * *

# yield from File
    
    
    def read_file(path):
    
        with open(path) as f:
    
            yield from f

Toàn bộ file trở thành Generator.

* * *

# Ví dụ thực tế

Crawler
    
    
    def crawl_page(page):
    
        yield f"Chapter {page}-1"
    
        yield f"Chapter {page}-2"

Muốn crawl nhiều page
    
    
    def crawl():
    
        for page in range(1,4):
    
            yield from crawl_page(page)

Kết quả
    
    
    Chapter 1-1
    
    Chapter 1-2
    
    Chapter 2-1
    
    Chapter 2-2
    
    Chapter 3-1
    
    Chapter 3-2

Đây là mẫu rất phổ biến trong các ứng dụng crawler.

* * *

# Generator lồng nhau
    
    
    def level3():
    
        yield 100
    
    
    def level2():
    
        yield from level3()
    
    
    def level1():
    
        yield from level2()

Python sẽ đi xuyên qua nhiều tầng Generator.
    
    
    Level1
    
    ↓
    
    Level2
    
    ↓
    
    Level3
    
    ↓
    
    100

* * *

# Không dùng yield from
    
    
    def level2():
    
        for x in level3():
    
            yield x

Hoạt động được.

Nhưng nếu có 10 tầng Generator

↓

Code sẽ rất dài.

* * *

# return trong Generator

Đây là điều thú vị.
    
    
    def child():
    
        yield 1
    
        return 100

Ta thử
    
    
    g = child()
    
    print(next(g))

↓
    
    
    1

* * *

Tiếp
    
    
    next(g)

↓
    
    
    StopIteration

Nhưng thật ra
    
    
    StopIteration.value = 100

* * *

# Lấy giá trị return

Ví dụ
    
    
    g = child()
    
    try:
    
        while True:
            next(g)
    
    except StopIteration as e:
    
        print(e.value)

↓
    
    
    100

Đây là một tính năng ít người biết.

* * *

# yield from nhận return

Đây mới là sức mạnh thực sự.
    
    
    def child():
    
        yield 1
    
        return 999

* * *

Generator cha
    
    
    def parent():
    
        value = yield from child()
    
        print(value)

* * *

Chạy
    
    
    g = parent()
    
    print(next(g))
    
    try:
        next(g)
    except StopIteration:
        pass

↓
    
    
    1
    
    999

Điều gì xảy ra?

`yield from`

nhận được
    
    
    return 999

của Generator con.

* * *

# Minh họa
    
    
    Child
    
    ↓
    
    yield
    
    ↓
    
    yield
    
    ↓
    
    return 999
    
    ↓
    
    yield from
    
    ↓
    
    value = 999

* * *

# Đây là điều for không làm được
    
    
    for x in child():
    
        yield x

Không lấy được
    
    
    return 999

Chỉ `yield from` mới làm được.

* * *

# send()

Bạn sẽ học kỹ ở phần Generator nâng cao.

Hiện tại chỉ cần biết.

Generator
    
    
    value = yield

có thể nhận dữ liệu.

Nếu dùng
    
    
    yield from child()

thì
    
    
    send()

được chuyển xuống Generator con.

* * *

# throw()

Tương tự
    
    
    generator.throw(...)

↓

`yield from`

↓

Generator con.

* * *

# close()

Đóng Generator cha

↓

Generator con cũng được đóng.

* * *

# Vì sao Python làm vậy?

Để
    
    
    Generator Cha

không cần biết
    
    
    Generator Con

đang hoạt động thế nào.

Nó chỉ
    
    
    Ủy quyền

cho Generator con.

* * *

# Ví dụ Pipeline
    
    
    download()
    
    ↓
    
    parse()
    
    ↓
    
    clean()
    
    ↓
    
    save()

Mỗi bước có thể là một Generator.
    
    
    yield from

kết nối chúng lại.

* * *

# Ví dụ Parser
    
    
    def parse_html():
    
        yield "<html>"
    
        yield "<body>"
    
    
    def parse_document():
    
        yield from parse_html()
    
        yield "<footer>"

↓
    
    
    <html>
    
    <body>
    
    <footer>

* * *

# Ví dụ Tree

Ở Buổi 9

DFS
    
    
    A
    
    ├──B
    
    └──C

Có thể viết
    
    
    def dfs(node):
    
        yield node.value
    
        for child in node.children:
    
            yield from dfs(child)

Đây là cách viết DFS đẹp nhất.

* * *

# Ví dụ hoàn chỉnh
    
    
    class Node:
    
        def __init__(self, value):
            self.value = value
            self.children = []
    
    
    def walk(node):
    
        yield node.value
    
        for child in node.children:
    
            yield from walk(child)
    
    
    root = Node("A")
    
    b = Node("B")
    c = Node("C")
    d = Node("D")
    
    root.children = [b, c]
    b.children = [d]
    
    for x in walk(root):
        print(x)

↓
    
    
    A
    B
    D
    C

Code này ngắn gọn hơn rất nhiều so với việc tự quản lý một ngăn xếp (stack).

* * *

# yield from và Lazy Evaluation

Giả sử
    
    
    def huge():
    
        for i in range(1000000000):
    
            yield i

Tiếp
    
    
    def wrapper():
    
        yield from huge()

Không tạo
    
    
    1 tỷ số

trong RAM.

Mỗi lần `next()`:
    
    
    wrapper
    
    ↓
    
    huge
    
    ↓
    
    1 số

Được sinh ra.

Vẫn là Lazy.

* * *

# So sánh

Không dùng
    
    
    for item in child():
        yield item

Ưu điểm:

  * Dễ hiểu. 
  * Chủ động xử lý từng phần tử. 



Nhược điểm:

  * Không chuyển tiếp `send()`, `throw()`, `close()`. 
  * Không lấy được giá trị `return`. 



* * *

Dùng
    
    
    yield from child()

Ưu điểm:

  * Ngắn gọn. 
  * Chuyển tiếp đầy đủ giao thức Generator. 
  * Nhận được `return` từ Generator con. 
  * Phù hợp cho Generator lồng nhau và pipeline. 



* * *

# Ứng dụng thực tế

Trong dự án crawler truyện của bạn, có thể thiết kế như sau:
    
    
    crawl_site()
    
    ↓
    
    yield from crawl_category()
    
    ↓
    
    yield from crawl_book()
    
    ↓
    
    yield from crawl_chapters()
    
    ↓
    
    yield from crawl_images()

Mỗi Generator chỉ tập trung vào **một nhiệm vụ** , còn `yield from` giúp ghép chúng thành một luồng dữ liệu thống nhất.

Đây là cách tổ chức mã rất rõ ràng và dễ mở rộng.

* * *

# Tổng kết buổi 15

Bạn cần nhớ 10 ý quan trọng:

  1. `yield from` dùng để **ủy quyền** cho một Iterable hoặc Generator khác. 
  2. Có thể dùng với mọi **Iterable** (`list`, `tuple`, `set`, `dict`, `str`, `file`, Generator...). 
  3. Với `next()`, `yield from iterable` gần giống `for item in iterable: yield item`. 
  4. `yield from` hỗ trợ Generator lồng nhau rất tự nhiên. 
  5. `yield from` chuyển tiếp `send()`, `throw()`, `close()`. 
  6. `yield from` nhận được giá trị `return` của Generator con. 
  7. Đây là công cụ rất mạnh để xây dựng pipeline xử lý dữ liệu. 
  8. DFS đệ quy là một ví dụ điển hình của `yield from`. 
  9. `yield from` vẫn giữ nguyên đặc tính **Lazy Evaluation**. 
  10. Khi chỉ cần "phát lại" toàn bộ dữ liệu từ một Generator khác, `yield from` gần như luôn là lựa chọn tốt nhất. 



* * *

# Bài tập

## Bài 1

Viết ba Generator:
    
    
    def vowels():
        ...
    
    
    def consonants():
        ...
    
    
    def alphabet():
        ...

Trong đó `alphabet()` sử dụng `yield from` để kết hợp hai Generator còn lại.

* * *

## Bài 2

Viết Generator duyệt một cây thư mục giả lập:
    
    
    class Folder:
        ...

Viết:
    
    
    def walk(folder):
        ...

Sử dụng `yield from` để duyệt đệ quy tất cả thư mục và tệp.

* * *

## Bài 3

Xây dựng một pipeline Generator cho ứng dụng crawler:
    
    
    fetch_pages()
    
    ↓
    
    yield from extract_books()
    
    ↓
    
    yield from extract_chapters()
    
    ↓
    
    yield from download_images()

Mỗi Generator chỉ xử lý một bước và trả dữ liệu cho bước tiếp theo thông qua `yield from`. Đây là bài tập rất sát với kiến trúc của một ứng dụng crawler thực tế.

* * *

Ở **Buổi 16** , chúng ta sẽ học **Generator Expression** (`(...)`) và so sánh chi tiết với **List Comprehension** (`[...]`), bao gồm cơ chế lazy, hiệu năng, mức sử dụng bộ nhớ, và các tình huống nên chọn loại nào trong các dự án Python lớn.

