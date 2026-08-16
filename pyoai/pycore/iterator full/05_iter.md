# Iterator Deep Dive — Buổi 5

# Hàm `iter()` Deep Dive

Đến buổi này, chúng ta đã biết:

  * `for` luôn gọi `iter()`
  * `iter()` tạo ra Iterator 
  * `next()` lấy phần tử tiếp theo 



Nhưng:

> **`iter()` thực chất làm gì?**

Buổi học này sẽ đi sâu vào toàn bộ cơ chế của `iter()`.

* * *

# Roadmap

Đã học

  * ✅ Buổi 1 — Iterator 
  * ✅ Buổi 2 — Iterable 
  * ✅ Buổi 3 — Iterator Protocol 
  * ✅ Buổi 4 — Bên trong `for`



Hôm nay

  * ✅ Buổi 5 — `iter()`



Sắp tới

  * Buổi 6 — `next()`
  * Buổi 7 — Tự xây Iterator 



* * *

# iter() là gì?

Định nghĩa ngắn gọn:

> **`iter(obj)` trả về một Iterator của `obj`.**

Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(it)

Kết quả
    
    
    <list_iterator object at 0x...>

* * *

# iter() không trả về list

Sai
    
    
    iter(list)
    
    ↓
    
    list

Đúng
    
    
    list
    
    ↓
    
    iter()
    
    ↓
    
    list_iterator

* * *

# Thử kiểm tra kiểu
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    print(type(numbers))
    print(type(it))

↓
    
    
    <class 'list'>
    <class 'list_iterator'>

Hai object hoàn toàn khác nhau.

* * *

# iter() gọi gì?

Khi viết
    
    
    iter(numbers)

Python thực chất gọi
    
    
    numbers.__iter__()

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    a = iter(numbers)
    
    b = numbers.__iter__()
    
    print(next(a))
    print(next(b))

↓
    
    
    1
    1

Hai Iterator độc lập.

* * *

# iter() trên nhiều kiểu dữ liệu

## List
    
    
    it = iter([1, 2, 3])

↓
    
    
    list_iterator

* * *

## Tuple
    
    
    it = iter((1, 2, 3))

↓
    
    
    tuple_iterator

* * *

## String
    
    
    it = iter("Python")

↓
    
    
    str_iterator

* * *

## Dict
    
    
    it = iter({"a": 1, "b": 2})

↓
    
    
    dict_keyiterator

Mặc định duyệt theo key.

* * *

## Set
    
    
    it = iter({1, 2, 3})

↓
    
    
    set_iterator

* * *

## Range
    
    
    it = iter(range(5))

↓
    
    
    range_iterator

* * *

# iter() với Iterator

Đây là điều cực kỳ quan trọng.
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    print(iter(it) is it)

↓
    
    
    True

Tại sao?

Vì quy tắc của Iterator là
    
    
    iterator.__iter__()

phải trả về
    
    
    self

* * *

# So sánh

## Iterable
    
    
    numbers = [1, 2, 3]
    
    print(iter(numbers) is numbers)

↓
    
    
    False

* * *

## Iterator
    
    
    it = iter(numbers)
    
    print(iter(it) is it)

↓
    
    
    True

* * *

# Chứng minh
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(next(it))
    
    it2 = iter(it)
    
    print(it is it2)
    
    print(next(it2))

↓
    
    
    10
    True
    20

Không tạo Iterator mới.

* * *

# iter() không reset Iterator

Đây là lỗi rất nhiều người mắc.
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    next(it)
    
    it = iter(it)
    
    print(next(it))

Kết quả
    
    
    2

Không phải
    
    
    1

* * *

# Vì sao?

Vì
    
    
    iter(iterator)

chỉ trả về
    
    
    iterator

* * *

# Muốn reset

Phải tạo Iterator mới
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    next(it)
    
    it = iter(numbers)
    
    print(next(it))

↓
    
    
    1

* * *

# iter() và Generator
    
    
    def numbers():
        yield 1
        yield 2
        yield 3
    
    
    g = numbers()
    
    print(iter(g) is g)

↓
    
    
    True

Generator cũng là Iterator.

* * *

# iter() với File
    
    
    with open("data.txt", encoding="utf8") as f:
        print(iter(f) is f)

↓
    
    
    True

File object cũng là Iterator.

* * *

# iter() có hai dạng

Đây là phần rất nhiều lập trình viên Python chưa từng sử dụng.

## Dạng 1
    
    
    iter(iterable)

Đây là dạng quen thuộc.

* * *

## Dạng 2
    
    
    iter(callable, sentinel)

Đây là một tính năng rất mạnh và ít người biết.

* * *

# iter(callable, sentinel)

Cú pháp
    
    
    iter(function, stop_value)

Python sẽ

  * gọi `function()`
  * lấy kết quả 
  * nếu khác `stop_value`



↓

trả về kết quả.

Nếu bằng
    
    
    stop_value

↓

phát sinh
    
    
    StopIteration

* * *

# Ví dụ đơn giản
    
    
    class Counter:
    
        def __init__(self):
            self.value = 0
    
        def __call__(self):
            self.value += 1
            return self.value
    
    
    counter = Counter()
    
    it = iter(counter, 5)
    
    for x in it:
        print(x)

Kết quả
    
    
    1
    2
    3
    4

Tại sao không có
    
    
    5

Vì
    
    
    5

là
    
    
    sentinel

Khi callable trả về `5`, Iterator kết thúc và giá trị `5` **không được trả về**.

* * *

# Minh họa
    
    
    Counter()
    
    ↓
    
    1
    
    ↓
    
    2
    
    ↓
    
    3
    
    ↓
    
    4
    
    ↓
    
    5
    
    ↓
    
    StopIteration

* * *

# Ví dụ đọc dữ liệu theo khối

Một ứng dụng thực tế của `iter(callable, sentinel)` là đọc file theo từng block cho đến khi hết dữ liệu.
    
    
    from functools import partial
    
    with open("image.jpg", "rb") as f:
        for block in iter(partial(f.read, 1024), b""):
            print(len(block))

Giải thích:

  * `partial(f.read, 1024)` tạo một hàm không tham số, mỗi lần gọi sẽ đọc 1024 byte. 
  * Khi `f.read(1024)` trả về `b""` (chuỗi byte rỗng), tức là đã đến cuối file. 
  * `iter()` tự động phát sinh `StopIteration`. 



Tương đương với:
    
    
    while True:
        block = f.read(1024)
        if block == b"":
            break
    
        print(len(block))

* * *

# Tự viết Iterable
    
    
    class MyNumbers:
    
        def __iter__(self):
            return iter([10, 20, 30])

Sử dụng
    
    
    obj = MyNumbers()
    
    it = iter(obj)
    
    print(next(it))

↓
    
    
    10

* * *

# Điều gì xảy ra nếu không có `__iter__()`?
    
    
    class Person:
        pass
    
    p = Person()
    
    iter(p)

↓
    
    
    TypeError:
    'Person' object is not iterable

Đây là cơ chế Python xác định một đối tượng có phải Iterable hay không.

* * *

# Sơ đồ hoạt động của `iter()`
    
    
    iter(obj)
    
    ↓
    
    obj có __iter__ ?
    
    ↓
    
    Có
    
    ↓
    
    gọi obj.__iter__()
    
    ↓
    
    Iterator
    
    ↓
    
    next()
    
    ↓
    
    Item

Nếu không có `__iter__()` (và cũng không hỗ trợ cơ chế lặp cũ dựa trên `__getitem__()`), Python sẽ phát sinh `TypeError`.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections.abc import Iterable, Iterator
    
    data = ["Python", "Java", "Go"]
    
    print(isinstance(data, Iterable))
    
    it = iter(data)
    
    print(isinstance(it, Iterator))
    
    print(iter(it) is it)
    
    for item in it:
        print(item)

Kết quả
    
    
    True
    True
    True
    Python
    Java
    Go

* * *

# Những hiểu lầm phổ biến

## Hiểu lầm 1

> `iter()` tạo bản sao dữ liệu.

Sai.
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)

Iterator chỉ giữ tham chiếu đến dữ liệu và trạng thái duyệt.

* * *

## Hiểu lầm 2

> `iter(iterator)` sẽ tạo Iterator mới.

Sai.

Nó trả về chính Iterator đó.

* * *

## Hiểu lầm 3

> `iter()` chỉ dùng với `list`.

Sai.

Mọi Iterable đều có thể truyền vào `iter()`, bao gồm:

  * `tuple`
  * `str`
  * `dict`
  * `set`
  * `range`
  * `file`
  * `generator`
  * các lớp do bạn tự xây dựng. 



* * *

# Tổng kết buổi 5

Những điểm cần ghi nhớ:

  1. `iter(obj)` gọi `obj.__iter__()`. 
  2. `iter()` luôn trả về một Iterator. 
  3. Nếu đối tượng đã là Iterator thì `iter(obj)` trả về chính đối tượng đó. 
  4. `iter()` **không reset** Iterator. 
  5. `iter(callable, sentinel)` tạo một Iterator từ một hàm được gọi lặp đi lặp lại cho đến khi hàm trả về giá trị `sentinel`. 
  6. Nếu một đối tượng không hỗ trợ giao thức lặp, `iter(obj)` sẽ phát sinh `TypeError`. 



* * *

# Bài tập

## Bài 1

Viết lớp `Alphabet` có `__iter__()` trả về Iterator sinh các ký tự từ `'A'` đến `'F'`.

* * *

## Bài 2

Tạo một Iterator từ `range(100)`, đọc 5 số đầu tiên bằng `next()`, sau đó gọi `iter()` lên chính Iterator và chứng minh rằng trạng thái không bị reset.

* * *

## Bài 3

Viết lớp sau:
    
    
    class RandomNumber:
        ...

  * Mỗi lần đối tượng được gọi (`__call__()`), trả về một số nguyên ngẫu nhiên từ `1` đến `10`. 
  * Dùng `iter(random_number, 7)` để tạo Iterator. 
  * In ra các số sinh được cho đến khi hàm trả về `7` (không in `7`), rồi giải thích vai trò của `sentinel`. 



Ở **Buổi 6** , chúng ta sẽ đi sâu vào **`next()`** , phân tích cách `next()` hoạt động ở mức giao thức, tham số mặc định `next(iterator, default)`, cách xử lý `StopIteration`, và các mẫu sử dụng an toàn trong các chương trình Python thực tế.

