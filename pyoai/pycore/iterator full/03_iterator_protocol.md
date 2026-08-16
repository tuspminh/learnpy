# Iterator Deep Dive — Buổi 3

# Iterator Protocol (`__iter__()` và `__next__()`)

Đây là **buổi quan trọng nhất** trong toàn bộ khóa học Iterator.

Nếu hiểu buổi này, bạn sẽ hiểu:

  * Vì sao `for` hoạt động. 
  * Vì sao `list` có thể lặp. 
  * Vì sao `generator` hoạt động. 
  * Vì sao `yield` hoạt động. 
  * Cách tự tạo Collection của riêng mình. 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1 — Iterator là gì? 
  * ✅ Buổi 2 — Iterable là gì? 



Hôm nay

  * ✅ Buổi 3 — Iterator Protocol 



Sắp tới

  * Buổi 4 — Bên trong `for`
  * Buổi 5 — `iter()`
  * Buổi 6 — `next()`



* * *

# Protocol là gì?

Trong Python, **Protocol** là một "giao ước".

Ví dụ:

Nếu một object có:
    
    
    __len__()

thì:
    
    
    len(obj)

sẽ hoạt động.

Nếu object có:
    
    
    __getitem__()

thì:
    
    
    obj[0]

sẽ hoạt động.

Tương tự,

nếu object có:
    
    
    __iter__()

và
    
    
    __next__()

thì Python coi nó là **Iterator**.

Đó gọi là

> **Iterator Protocol**

* * *

# Iterator Protocol gồm hai hàm
    
    
    __iter__()

và
    
    
    __next__()

* * *

## `__iter__()`

Nhiệm vụ:

> Trả về một Iterator.

Ví dụ
    
    
    it = iter(numbers)

Python thực chất gọi
    
    
    numbers.__iter__()

* * *

## `__next__()`

Nhiệm vụ:

> Trả về phần tử tiếp theo.

Ví dụ
    
    
    next(it)

Python thực chất gọi
    
    
    it.__next__()

* * *

# Sơ đồ
    
    
    Iterable
    
          │
    
     __iter__()
    
          │
    
          ▼
    
    Iterator
    
          │
    
     __next__()
    
          │
    
          ▼
    
    Item

* * *

# Thử gọi trực tiếp

Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = numbers.__iter__()
    
    print(it.__next__())
    print(it.__next__())
    print(it.__next__())

Kết quả
    
    
    10
    20
    30

Hoàn toàn giống
    
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))
    print(next(it))

* * *

# Điều gì xảy ra khi hết dữ liệu?
    
    
    numbers = [1]
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))

↓
    
    
    1
    
    StopIteration

Nghĩa là
    
    
    __next__()

phải có khả năng
    
    
    raise StopIteration

* * *

# Tự viết Iterator đầu tiên

Chúng ta sẽ **không dùng list**.

Viết một Iterator từ đầu.
    
    
    class Counter:
    
        def __init__(self):
            self.current = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            if self.current > 5:
                raise StopIteration
    
            value = self.current
            self.current += 1
            return value

* * *

Sử dụng
    
    
    counter = Counter()
    
    for x in counter:
        print(x)

Kết quả
    
    
    1
    2
    3
    4
    5

Chúng ta vừa tạo thành công một Iterator.

* * *

# Phân tích từng dòng

## Constructor
    
    
    self.current = 1

Lưu trạng thái.

* * *

## `__iter__`
    
    
    def __iter__(self):
        return self

Tại sao trả về `self`?

Vì object này **chính là Iterator**.

* * *

## `__next__`
    
    
    if self.current > 5:

Nếu vượt giới hạn

↓
    
    
    raise StopIteration

* * *

Nếu chưa
    
    
    value = self.current

↓
    
    
    self.current += 1

↓
    
    
    return value

* * *

# Minh họa

Ban đầu
    
    
    current = 1

Lần 1
    
    
    return 1
    
    current = 2

Lần 2
    
    
    return 2
    
    current = 3

...

Lần cuối
    
    
    return 5
    
    current = 6

Lần sau
    
    
    StopIteration

* * *

# Chứng minh `for` dùng Protocol

Đoạn này
    
    
    for x in Counter():
        print(x)

Python thực hiện gần như sau:
    
    
    obj = Counter()
    
    it = obj.__iter__()
    
    while True:
    
        try:
            value = it.__next__()
    
        except StopIteration:
            break
    
        print(value)

Không có phép màu nào cả.

* * *

# Một Iterator luôn trả về chính nó

Ví dụ
    
    
    counter = Counter()
    
    print(iter(counter) is counter)

↓
    
    
    True

Đây là quy tắc rất quan trọng.

Nếu object là Iterator thì
    
    
    iter(iterator)

phải trả về
    
    
    chính nó

* * *

# Iterable thì khác

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    print(iter(numbers) is numbers)

↓
    
    
    False

Vì List không phải Iterator.

* * *

# So sánh

## List
    
    
    List
    
    ↓
    
    Iterator A
    
    ↓
    
    1
    
    2
    
    3

Lần nữa
    
    
    List
    
    ↓
    
    Iterator B
    
    ↓
    
    1
    
    2
    
    3

Iterator mới.

* * *

## Counter
    
    
    Counter
    
    ↓
    
    chính nó
    
    ↓
    
    1
    
    2
    
    3
    
    4
    
    5

Không tạo object mới.

* * *

# Kiểm tra bằng isinstance()
    
    
    from collections.abc import Iterator
    
    counter = Counter()
    
    print(isinstance(counter, Iterator))

↓
    
    
    True

* * *

# Thử dùng next()
    
    
    counter = Counter()
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    1
    2
    3

Không cần `for`.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections.abc import Iterator
    
    
    class Counter:
    
        def __init__(self, start, end):
            self.current = start
            self.end = end
    
        def __iter__(self):
            return self
    
        def __next__(self):
            if self.current > self.end:
                raise StopIteration
    
            value = self.current
            self.current += 1
            return value
    
    
    counter = Counter(5, 10)
    
    print(isinstance(counter, Iterator))
    
    for x in counter:
        print(x)

Kết quả
    
    
    True
    
    5
    6
    7
    8
    9
    10

* * *

# Một lỗi phổ biến

Nhiều người viết:
    
    
    class BadCounter:
    
        def __iter__(self):
            pass
    
        def __next__(self):
            ...

Sau đó
    
    
    for x in BadCounter():
        ...

Lỗi
    
    
    TypeError

Vì
    
    
    __iter__()

không trả về Iterator hợp lệ.

* * *

# Lỗi khác
    
    
    class BadCounter:
    
        def __iter__(self):
            return self
    
        def __next__(self):
            return 1

Điều gì xảy ra?
    
    
    for x in BadCounter():
        print(x)

Kết quả:
    
    
    1
    1
    1
    1
    1
    1
    ...

**Vòng lặp vô hạn.**

Vì bạn không bao giờ:
    
    
    raise StopIteration

Đây là lỗi rất hay gặp khi tự xây Iterator.

* * *

# Quy trình đầy đủ của Iterator Protocol
    
    
    for item in obj:
    
    ↓
    
    iter(obj)
    
    ↓
    
    obj.__iter__()
    
    ↓
    
    Iterator
    
    ↓
    
    next(iterator)
    
    ↓
    
    iterator.__next__()
    
    ↓
    
    return value
    
    ↓
    
    next()
    
    ↓
    
    return value
    
    ↓
    
    ...
    
    ↓
    
    StopIteration
    
    ↓
    
    for kết thúc

* * *

# Khi nào nên tự viết Iterator?

Trong thực tế, bạn sẽ tự viết Iterator khi xây dựng các cấu trúc dữ liệu hoặc nguồn dữ liệu riêng, chẳng hạn:

  * Cây (Tree) 
  * Danh sách liên kết (Linked List) 
  * Đồ thị (Graph) 
  * Bộ đọc file hoặc log tùy chỉnh 
  * Bộ đọc dữ liệu từ API theo từng trang 
  * Cursor cơ sở dữ liệu 
  * Bộ đọc dữ liệu cảm biến (stream) 



Nếu chỉ cần sinh một chuỗi giá trị đơn giản, **Generator (`yield`)** thường ngắn gọn và dễ bảo trì hơn. Chúng ta sẽ học kỹ ở phần sau của khóa học.

* * *

# Tổng kết buổi 3

Bạn cần nhớ những điểm cốt lõi sau:

  * **Iterator Protocol** gồm hai phương thức: 
    * `__iter__()`
    * `__next__()`
  * `iter(obj)` thực chất gọi `obj.__iter__()`. 
  * `next(obj)` thực chất gọi `obj.__next__()`. 
  * `__next__()` phải phát sinh `StopIteration` khi không còn dữ liệu. 
  * Một **Iterator** phải trả về chính nó trong `__iter__()`. 
  * `for` hoạt động hoàn toàn dựa trên Iterator Protocol. 



* * *

# Bài tập

## Bài 1

Viết lớp `EvenNumbers` sinh các số chẵn từ `2` đến `20` bằng cách cài đặt đầy đủ `__iter__()` và `__next__()`.

Kết quả mong muốn:
    
    
    2
    4
    6
    8
    10
    12
    14
    16
    18
    20

* * *

## Bài 2

Viết lớp `Countdown` đếm ngược từ `10` xuống `1`, sau đó kết thúc bằng `StopIteration`.

* * *

## Bài 3

Thử sửa lớp `Counter` bằng cách **bỏ dòng** :
    
    
    raise StopIteration

và quan sát điều gì xảy ra khi dùng trong vòng lặp `for`. Giải thích vì sao vòng lặp không kết thúc.

Ở **Buổi 4** , chúng ta sẽ mổ xẻ **toàn bộ cơ chế hoạt động của vòng lặp`for`**, từ mã Python đến cách Python nội bộ gọi `iter()` và `next()`, giúp bạn hiểu vì sao hầu hết mọi kiểu dữ liệu có thể lặp đều hoạt động thống nhất.

