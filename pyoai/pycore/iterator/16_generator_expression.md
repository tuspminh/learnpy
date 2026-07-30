# Iterator Deep Dive

# Phần III — Generator

# Buổi 16: Generator Expression Deep Dive

Đây là buổi cuối cùng của **Phần III - Generator**.

Đến thời điểm này bạn đã biết:

  * Generator là Iterator 
  * `yield`
  * `yield from`



Hôm nay chúng ta học **Generator Expression** , một trong những cú pháp Python được dùng nhiều nhất trong các thư viện lớn như:

  * Django 
  * FastAPI 
  * SQLAlchemy 
  * Pandas 
  * Requests 
  * BeautifulSoup 
  * AsyncIO 
  * PyTorch 



Sau buổi này bạn sẽ hiểu:

  * Generator Expression là gì 
  * Khác List Comprehension thế nào 
  * Lazy Evaluation thực sự hoạt động ra sao 
  * Khi nào nên dùng Generator Expression 
  * Khi nào không nên dùng 



* * *

# Roadmap

## Phần III - Generator

  * ✅ Buổi 13 — Generator là Iterator 
  * ✅ Buổi 14 — yield 
  * ✅ Buổi 15 — yield from 
  * ✅ **Buổi 16 — Generator Expression**



Tiếp theo

  * 🚀 Phần IV - Iterator nâng cao 



* * *

# Nhắc lại List Comprehension
    
    
    numbers = [x * x for x in range(5)]
    
    print(numbers)

Kết quả
    
    
    [0, 1, 4, 9, 16]

Đây là List.

* * *

# Generator Expression

Chỉ đổi
    
    
    []

thành
    
    
    ()
    
    
    numbers = (x * x for x in range(5))
    
    print(numbers)

Kết quả
    
    
    <generator object ...>

Không phải List.

* * *

# Kiểm tra kiểu dữ liệu
    
    
    numbers = (x*x for x in range(5))
    
    print(type(numbers))

↓
    
    
    <class 'generator'>

Generator Expression tạo ra
    
    
    Generator Object

* * *

# Dùng for
    
    
    numbers = (x*x for x in range(5))
    
    for x in numbers:
        print(x)

↓
    
    
    0
    1
    4
    9
    16

* * *

# next()
    
    
    numbers = (x*x for x in range(5))
    
    print(next(numbers))
    print(next(numbers))
    print(next(numbers))

↓
    
    
    0
    1
    4

Hoàn toàn giống Generator.

* * *

# So sánh

List
    
    
    [x*x for x in range(5)]

↓

Tạo ngay
    
    
    0
    1
    4
    9
    16

* * *

Generator Expression
    
    
    (x*x for x in range(5))

↓

Chưa tạo gì.

* * *

# Minh họa

List
    
    
    range()
    
    ↓
    
    0
    
    1
    
    2
    
    3
    
    4
    
    ↓
    
    RAM

* * *

Generator
    
    
    range()
    
    ↓
    
    0
    
    ↓
    
    next()
    
    ↓
    
    1
    
    ↓
    
    next()
    
    ↓
    
    2

Chỉ sinh khi cần.

* * *

# Ví dụ
    
    
    def square(x):
        print(f"Calculating {x}")
        return x*x

List
    
    
    numbers = [square(i) for i in range(3)]

↓
    
    
    Calculating 0
    
    Calculating 1
    
    Calculating 2

Tính hết ngay.

* * *

Generator Expression
    
    
    numbers = (square(i) for i in range(3))

Không in gì.

* * *

Chỉ khi
    
    
    print(next(numbers))

↓
    
    
    Calculating 0
    
    0

Tiếp
    
    
    print(next(numbers))

↓
    
    
    Calculating 1
    
    1

Đây là Lazy Evaluation.

* * *

# Bộ nhớ

Ví dụ
    
    
    numbers = [x for x in range(100000000)]

Python phải tạo
    
    
    100 triệu object

trước.

* * *

Generator
    
    
    numbers = (x for x in range(100000000))

RAM chỉ chứa
    
    
    1 object

tại một thời điểm.

* * *

# Đo bộ nhớ
    
    
    import sys
    
    lst = [x for x in range(1000)]
    
    gen = (x for x in range(1000))
    
    print(sys.getsizeof(lst))
    print(sys.getsizeof(gen))

Ví dụ kết quả (phụ thuộc phiên bản Python):
    
    
    8856
    
    200

Generator nhỏ hơn rất nhiều.

* * *

# Nhưng Generator có nhanh hơn không?

Không hẳn.

Nhiều người nghĩ
    
    
    Generator
    
    ↓
    
    Nhanh hơn

Sai.

Thực tế
    
    
    Generator
    
    ↓
    
    Tiết kiệm RAM hơn

Mỗi lần `next()`

↓

Python phải

  * Resume Generator 
  * Chạy code 
  * Pause lại 



Có chi phí.

* * *

# So sánh

List
    
    
    RAM
    
    ↑↑↑
    
    CPU
    
    ↓

Generator
    
    
    RAM
    
    ↓
    
    CPU
    
    ↑

Đánh đổi.

* * *

# Dùng một lần
    
    
    numbers = (x for x in range(5))
    
    for x in numbers:
        print(x)
    
    for x in numbers:
        print(x)

Lần hai

↓

Không có gì.

Generator đã hết.

* * *

List
    
    
    numbers = [x for x in range(5)]

Có thể lặp
    
    
    for x in numbers:
        ...
    
    for x in numbers:
        ...

Bao nhiêu lần cũng được.

* * *

# sum()
    
    
    result = sum(
        x*x
        for x in range(10)
    )

Đây là cú pháp rất phổ biến.

Python không cần
    
    
    [
    ]

* * *

Tương đương
    
    
    result = sum(
        (x*x for x in range(10))
    )

Dấu ngoặc ngoài được lược bỏ khi Generator Expression là đối số duy nhất.

* * *

# max()
    
    
    largest = max(
        len(word)
        for word in ["python","iterator","generator"]
    )
    
    print(largest)

↓
    
    
    9

Không tạo List trung gian.

* * *

# any()
    
    
    numbers = (x > 10 for x in range(20))
    
    print(any(numbers))

↓
    
    
    True

`any()` dừng ngay khi gặp `True` đầu tiên.

* * *

# all()
    
    
    numbers = (x < 100 for x in range(20))
    
    print(all(numbers))

↓
    
    
    True

Không cần duyệt hết nếu gặp `False`.

* * *

# Pipeline
    
    
    numbers = (
        x*x
        for x in range(100)
        if x % 2 == 0
    )

Luồng xử lý
    
    
    range
    
    ↓
    
    lọc
    
    ↓
    
    bình phương
    
    ↓
    
    yield

Không có List trung gian.

* * *

# Nhiều vòng lặp
    
    
    pairs = (
        (x, y)
        for x in range(3)
        for y in range(2)
    )
    
    for pair in pairs:
        print(pair)

↓
    
    
    (0,0)
    
    (0,1)
    
    (1,0)
    
    (1,1)
    
    (2,0)
    
    (2,1)

* * *

# if
    
    
    evens = (
        x
        for x in range(10)
        if x % 2 == 0
    )

↓
    
    
    0
    
    2
    
    4
    
    6
    
    8

* * *

# Lồng nhau
    
    
    matrix = [
        [1,2],
        [3,4]
    ]
    
    numbers = (
        value
        for row in matrix
        for value in row
    )

↓
    
    
    1
    
    2
    
    3
    
    4

* * *

# Với file
    
    
    with open("story.txt") as f:
    
        lines = (
            line.strip()
            for line in f
        )
    
        for line in lines:
            print(line)

Không đọc toàn bộ file vào RAM.

* * *

# Ví dụ crawler
    
    
    chapters = (
        chapter.title
        for chapter in crawl_book()
    )

Nếu chỉ cần lấy từng tiêu đề để xử lý hoặc ghi vào cơ sở dữ liệu, Generator Expression rất phù hợp vì không cần tạo một danh sách lớn trước.

* * *

# Sai lầm phổ biến

## Sai lầm 1
    
    
    gen = (
        x
        for x in range(5)
    )
    
    print(gen[0])

↓
    
    
    TypeError

Generator

↓

không hỗ trợ
    
    
    Index

* * *

## Sai lầm 2
    
    
    len(gen)

↓
    
    
    TypeError

Không có độ dài vì dữ liệu có thể chưa được sinh ra.

* * *

## Sai lầm 3
    
    
    sorted(gen)

Hoạt động.

Nhưng

↓

Generator bị tiêu thụ.

* * *

## Sai lầm 4
    
    
    list(gen)
    
    list(gen)

Lần hai

↓
    
    
    []

Generator đã hết.

* * *

# Khi nào dùng List?

Nên dùng khi:

  * Cần truy cập theo chỉ số (`data[10]`). 
  * Cần duyệt nhiều lần. 
  * Cần `len()`. 
  * Dữ liệu nhỏ và cần truy cập ngẫu nhiên. 



* * *

# Khi nào dùng Generator Expression?

Nên dùng khi:

  * Dữ liệu rất lớn. 
  * Chỉ duyệt một lần. 
  * Muốn tiết kiệm RAM. 
  * Xây dựng pipeline xử lý. 
  * Làm việc với file, socket, crawler, stream. 



* * *

# Ví dụ thực tế

Giả sử crawler lấy 5 triệu chapter.

Không nên
    
    
    titles = [
        chapter.title
        for chapter in crawler()
    ]

Nên
    
    
    titles = (
        chapter.title
        for chapter in crawler()
    )
    
    for title in titles:
        database.save(title)

Ưu điểm:

  * Không cần giữ 5 triệu tiêu đề trong RAM. 
  * Có thể xử lý từng tiêu đề ngay khi lấy được. 



* * *

# So sánh tổng hợp

Đặc điểm| List Comprehension| Generator Expression  
---|---|---  
Ký hiệu| `[]`| `()`  
Kết quả| `list`| `generator`  
Lazy| ❌| ✅  
Tốn RAM| Cao hơn| Thấp  
Hỗ trợ `len()`| ✅| ❌  
Truy cập chỉ số| ✅| ❌  
Lặp nhiều lần| ✅| ❌ (sau khi tiêu thụ)  
Phù hợp dữ liệu lớn| ⚠️| ✅  
  
* * *

# Tổng kết Phần III – Generator

Qua 4 buổi (13–16), bạn đã học:

  * Generator là Iterator. 
  * `yield` là điểm tạm dừng và lưu toàn bộ trạng thái. 
  * `yield from` dùng để ủy quyền cho Generator hoặc Iterable khác. 
  * Generator Expression giúp tạo các pipeline xử lý dữ liệu theo kiểu **lazy** với cú pháp ngắn gọn. 



Đến đây, bạn đã có đầy đủ nền tảng để sử dụng Generator thành thạo trong các dự án Python thực tế.

* * *

# Bài tập

## Bài 1

Viết Generator Expression trả về:
    
    
    1
    8
    27
    64
    125
    ...

(các lập phương từ `1` đến `10`), sau đó dùng `sum()` để tính tổng mà **không tạo List**.

* * *

## Bài 2

Cho danh sách:
    
    
    files = [
        "a.txt",
        "b.jpg",
        "c.txt",
        "d.png"
    ]

Viết Generator Expression chỉ sinh ra các tệp có phần mở rộng `.txt`, sau đó duyệt và in từng tên tệp.

* * *

## Bài 3

Mô phỏng một pipeline crawler:
    
    
    pages = range(1, 6)

Tạo ba Generator Expression nối tiếp:

  1. Sinh URL: 


    
    
    https://example.com/page/1

  2. Sinh HTML giả lập từ URL: 


    
    
    <html>https://example.com/page/1</html>

  3. Trích xuất tiêu đề giả lập: 


    
    
    Title of https://example.com/page/1

In kết quả cuối cùng và quan sát rằng mỗi bước chỉ xử lý **một phần tử tại một thời điểm** , không tạo danh sách trung gian.

* * *

# Chuẩn bị sang Phần IV – Iterator nâng cao

Từ **Buổi 17** , chúng ta sẽ bắt đầu **Iterator nâng cao** , tập trung vào thư viện `itertools` của Python.

Đây là một trong những module mạnh nhất trong thư viện chuẩn, cung cấp các "khối Lego" để xây dựng các pipeline xử lý dữ liệu hiệu quả. Bạn sẽ học cách kết hợp các Iterator thay vì tự viết vòng lặp, giúp mã ngắn gọn, nhanh và tận dụng tối đa cơ chế lazy mà bạn đã nắm vững trong các buổi trước.

