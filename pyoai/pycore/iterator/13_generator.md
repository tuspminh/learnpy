# Iterator Deep Dive

# Phần III — Generator

# Buổi 13: Generator chính là Iterator

Đây là **buổi quan trọng nhất của toàn bộ khóa học**.

Nếu trước đây bạn đã tự viết rất nhiều Iterator bằng:
    
    
    class MyIterator:
        def __iter__(self):
            ...
    
        def __next__(self):
            ...

thì từ buổi này trở đi bạn sẽ thấy:

> **Generator chỉ là một cách Python tự động viết Iterator giúp chúng ta.**

Hiểu được điều này, bạn sẽ không còn xem Generator là "một khái niệm mới", mà chỉ là **Iterator được Python sinh tự động**.

* * *

# Roadmap

## Phần I - Iterator Foundation

  * ✅ Buổi 1-6 



## Phần II - Tự xây Iterator

  * ✅ Buổi 7-12 



## Phần III - Generator

  * ✅ **Buổi 13 — Generator là Iterator**
  * Buổi 14 — yield 
  * Buổi 15 — yield from 
  * Buổi 16 — Generator Expression 



* * *

# Bắt đầu bằng một Iterator

Ví dụ quen thuộc.
    
    
    class CounterIterator:
    
        def __init__(self):
            self.value = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            if self.value > 5:
                raise StopIteration
    
            value = self.value
            self.value += 1
            return value

Sử dụng
    
    
    for x in CounterIterator():
        print(x)

Kết quả
    
    
    1
    2
    3
    4
    5

Hoạt động hoàn hảo.

* * *

# Nhưng có vấn đề

Để viết chỉ 5 số

ta phải viết
    
    
    __init__()
    
    ↓
    
    __iter__()
    
    ↓
    
    __next__()
    
    ↓
    
    StopIteration

Rất nhiều mã.

* * *

# Python giải quyết thế nào?

Python giới thiệu
    
    
    Generator

* * *

# Generator đầu tiên
    
    
    def counter():
    
        yield 1
        yield 2
        yield 3
        yield 4
        yield 5

Chỉ vậy thôi.

* * *

Sử dụng
    
    
    for x in counter():
        print(x)

↓
    
    
    1
    2
    3
    4
    5

Kết quả giống hệt Iterator.

* * *

# Điều gì xảy ra?

Nhiều người nghĩ
    
    
    yield

là
    
    
    return

Không.

Đó là hiểu nhầm lớn nhất.

* * *

# Kiểm tra kiểu dữ liệu
    
    
    g = counter()
    
    print(type(g))

↓
    
    
    <class 'generator'>

Generator là một object.

* * *

# Generator có phải Iterator?

Kiểm tra
    
    
    from collections.abc import Iterator
    
    g = counter()
    
    print(isinstance(g, Iterator))

↓
    
    
    True

Generator chính là Iterator.

* * *

# Generator có **next** không?
    
    
    g = counter()
    
    print(hasattr(g, "__next__"))

↓
    
    
    True

* * *

Có `__iter__` không?
    
    
    print(hasattr(g, "__iter__"))

↓
    
    
    True

* * *

Kiểm tra
    
    
    g = counter()
    
    print(iter(g) is g)

↓
    
    
    True

Hoàn toàn giống File Iterator.

* * *

# next()
    
    
    g = counter()
    
    print(next(g))

↓
    
    
    1

Tiếp
    
    
    print(next(g))

↓
    
    
    2

Tiếp
    
    
    print(next(g))

↓
    
    
    3

Generator hoạt động giống Iterator.

* * *

# Khi nào StopIteration?
    
    
    g = counter()
    
    print(next(g))
    print(next(g))
    print(next(g))
    print(next(g))
    print(next(g))
    
    print(next(g))

↓
    
    
    1
    2
    3
    4
    5
    
    StopIteration

Python tự sinh
    
    
    raise StopIteration

Chúng ta không cần viết.

* * *

# So sánh

Iterator
    
    
    class Counter:
    
        def __next__(self):
    
            if ...:
                raise StopIteration
    
            ...

Generator
    
    
    def counter():
    
        yield ...

Python tự thêm
    
    
    raise StopIteration

ở cuối hàm.

* * *

# Python thực sự làm gì?

Hãy tưởng tượng.

Bạn viết
    
    
    def counter():
    
        yield 1
        yield 2
        yield 3

Python gần như biến thành
    
    
    class CounterGenerator:
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            ...

Tất nhiên mã nội bộ của CPython phức tạp hơn rất nhiều, nhưng **về ý tưởng** , Generator là một Iterator được Python tạo giúp bạn.

* * *

# Minh họa

Iterator
    
    
    __next__()
    
    ↓
    
    1
    
    ↓
    
    2
    
    ↓
    
    3

Generator
    
    
    yield 1
    
    ↓
    
    yield 2
    
    ↓
    
    yield 3

Giống nhau.

* * *

# Generator không chạy ngay

Ví dụ
    
    
    def hello():
    
        print("Start")
    
        yield 1
    
        print("End")

Ta viết
    
    
    g = hello()
    
    print("Created")

Kết quả
    
    
    Created

Không có
    
    
    Start

* * *

# Vì sao?

Vì
    
    
    g = hello()

không chạy hàm.

Nó chỉ tạo Generator Object.

* * *

# Chỉ chạy khi next()
    
    
    g = hello()
    
    print(next(g))

↓
    
    
    Start
    
    1

Lúc này hàm mới bắt đầu chạy.

* * *

# Sau yield

Tiếp tục
    
    
    print(next(g))

↓
    
    
    End
    
    StopIteration

Điều này cực kỳ quan trọng.

Generator

↓

không chạy từ đầu mỗi lần.

Nó tiếp tục từ nơi dừng.

* * *

# Minh họa
    
    
    yield 1
    
    ↓
    
    PAUSE
    
    ↓
    
    yield 2
    
    ↓
    
    PAUSE
    
    ↓
    
    yield 3
    
    ↓
    
    END

Generator luôn nhớ vị trí.

* * *

# So sánh với return
    
    
    def f():
    
        return 10
    
        print("Hello")

↓

`print`

không bao giờ chạy.

* * *

Generator
    
    
    def g():
    
        yield 10
    
        print("Hello")
    
        yield 20

Hoàn toàn khác.

* * *

# next()

Lần đầu
    
    
    yield 10

↓

Tạm dừng.

* * *

Lần hai

↓
    
    
    Hello
    
    yield 20

* * *

# Ví dụ hoàn chỉnh
    
    
    def demo():
    
        print("A")
        yield 1
    
        print("B")
        yield 2
    
        print("C")
        yield 3
    
        print("D")

Sử dụng
    
    
    g = demo()
    
    print(next(g))
    print(next(g))
    print(next(g))

Kết quả
    
    
    A
    1
    
    B
    2
    
    C
    3

Tiếp
    
    
    next(g)

↓
    
    
    D
    
    StopIteration

* * *

# Trạng thái Generator

Generator có thể ở các trạng thái:
    
    
    Created
    
    ↓
    
    Running
    
    ↓
    
    Suspended
    
    ↓
    
    Running
    
    ↓
    
    Suspended
    
    ↓
    
    Closed

* * *

## Created
    
    
    g = counter()

Chưa chạy.

* * *

## Running

Trong lúc
    
    
    next(g)

Generator đang thực thi.

* * *

## Suspended

Gặp
    
    
    yield

↓

Tạm dừng.

* * *

## Closed

Hết dữ liệu

↓

StopIteration

* * *

# Kiểm tra trạng thái
    
    
    import inspect
    
    g = counter()
    
    print(inspect.getgeneratorstate(g))

↓
    
    
    GEN_CREATED

Sau
    
    
    next(g)

↓
    
    
    GEN_SUSPENDED

Sau khi kết thúc

↓
    
    
    GEN_CLOSED

* * *

# for Loop

Generator cũng dùng
    
    
    for

giống Iterator.
    
    
    for x in counter():
        print(x)

Python làm
    
    
    g = counter()
    
    while True:
    
        try:
            value = next(g)
    
        except StopIteration:
            break
    
        print(value)

Giống hệt Iterator.

* * *

# Memory

Generator
    
    
    yield

không tạo toàn bộ dữ liệu.

Ví dụ
    
    
    def numbers():
    
        for i in range(1000000000):
            yield i

Không có
    
    
    1 tỷ số

trong RAM.

Chỉ có
    
    
    1 số

được sinh mỗi lần `next()`.

* * *

# Khi nào dùng Iterator?

Nếu bạn cần:

  * Điều khiển hoàn toàn `__next__()`
  * Có nhiều trạng thái phức tạp 
  * Muốn tạo nhiều kiểu Iterator khác nhau trên cùng Collection (DFS, BFS, Reverse...) 



→ Dùng **Iterator Class**.

* * *

# Khi nào dùng Generator?

Nếu chỉ cần:

  * Sinh dữ liệu tuần tự 
  * Mã ngắn gọn 
  * Lazy Evaluation 



→ Dùng **Generator**.

Trong thực tế, Generator thường là lựa chọn đầu tiên vì dễ viết và dễ đọc.

* * *

# So sánh

Iterator Class| Generator  
---|---  
Phải viết `__iter__`| Không  
Phải viết `__next__`| Không  
Tự `raise StopIteration`| Python tự làm  
Nhiều mã| Rất ngắn  
Linh hoạt cao| Viết nhanh hơn  
Phù hợp cấu trúc dữ liệu phức tạp| Phù hợp sinh dữ liệu tuần tự  
  
* * *

# Ví dụ: Iterator chuyển sang Generator

Iterator
    
    
    class RangeIterator:
    
        def __init__(self, start, stop):
            self.current = start
            self.stop = stop
    
        def __iter__(self):
            return self
    
        def __next__(self):
            if self.current >= self.stop:
                raise StopIteration
    
            value = self.current
            self.current += 1
            return value

Generator
    
    
    def range_generator(start, stop):
    
        current = start
    
        while current < stop:
            yield current
            current += 1

Hai đoạn mã cho kết quả giống nhau, nhưng phiên bản Generator ngắn gọn và dễ hiểu hơn.

* * *

# Tổng kết buổi 13

Bạn cần nhớ:

  1. **Generator là một Iterator.**
  2. Hàm chứa `yield` **không chạy ngay** khi được gọi; nó trả về một Generator Object. 
  3. Generator tuân thủ đầy đủ **Iterator Protocol** (`__iter__`, `__next__`). 
  4. Mỗi lần `next()` sẽ chạy cho đến `yield` tiếp theo rồi tạm dừng. 
  5. Khi hàm kết thúc, Python tự phát sinh `StopIteration`. 
  6. Generator giúp viết Iterator ngắn gọn hơn rất nhiều nhưng vẫn giữ được đặc tính **lazy**. 



* * *

# Bài tập

## Bài 1

Viết Generator:
    
    
    def countdown(n):
        ...

Kết quả:
    
    
    for x in countdown(5):
        print(x)

↓
    
    
    5
    4
    3
    2
    1

* * *

## Bài 2

Chuyển `LinkedListIterator` ở Buổi 10 thành một Generator:
    
    
    def iterate_linked_list(head):
        ...

không sử dụng lớp `LinkedListIterator`.

* * *

## Bài 3

Viết Generator:
    
    
    def read_chunks(text, size):
        ...

Ví dụ:
    
    
    for chunk in read_chunks("HelloPythonGenerator", 4):
        print(chunk)

Kết quả:
    
    
    Hell
    oPyt
    honG
    ener
    ator

Đây là một ví dụ điển hình của **Lazy Generator** , rất giống cách Python đọc file theo từng dòng hoặc từng khối dữ liệu.

* * *

Ở **Buổi 14** , chúng ta sẽ đi sâu vào **`yield`** : không chỉ là "trả về một giá trị", mà còn là một **điểm tạm dừng (suspension point)** lưu toàn bộ trạng thái của hàm (biến cục bộ, vị trí thực thi, khối lệnh đang chạy). Đây là chìa khóa để hiểu sức mạnh thực sự của Generator.

