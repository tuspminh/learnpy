# Iterator Deep Dive — Buổi 4

# Bên trong vòng lặp `for` hoạt động như thế nào?

Đây là buổi học quan trọng nhất sau **Iterator Protocol**.

Rất nhiều lập trình viên dùng `for` hàng chục năm nhưng chưa bao giờ hiểu **Python thực sự làm gì khi gặp câu lệnh`for`**.

Sau buổi này bạn sẽ hiểu:

  * `for` không biết `list`, `tuple`, `set` là gì. 
  * `for` không dùng chỉ số (`index`). 
  * `for` không gọi `len()`. 
  * `for` chỉ biết **Iterator Protocol**. 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1: Iterator 
  * ✅ Buổi 2: Iterable 
  * ✅ Buổi 3: Iterator Protocol 



Hôm nay

  * ✅ Buổi 4: Cơ chế hoạt động của `for`



Sắp tới

  * Buổi 5: `iter()`
  * Buổi 6: `next()`



* * *

# Ví dụ quen thuộc
    
    
    numbers = [10, 20, 30]
    
    for x in numbers:
        print(x)

Ai cũng viết được đoạn này.

Nhưng Python làm gì?

* * *

# Bước 1

Python gặp
    
    
    for x in numbers:

Việc đầu tiên KHÔNG phải là lấy phần tử.

Nó gọi
    
    
    iter(numbers)

Hay nói cách khác
    
    
    numbers.__iter__()

Kết quả
    
    
    list_iterator

* * *

## Minh họa
    
    
    numbers
    
    ↓
    
    iter()
    
    ↓
    
    list_iterator

* * *

# Bước 2

Python gọi
    
    
    next(iterator)

↓
    
    
    10

Biến
    
    
    x

nhận giá trị
    
    
    10

Sau đó chạy thân vòng lặp
    
    
    print(x)

* * *

# Bước 3

Lặp lại
    
    
    next(iterator)

↓
    
    
    20

↓
    
    
    print(x)

* * *

# Bước 4
    
    
    next(iterator)

↓
    
    
    30

↓
    
    
    print(x)

* * *

# Bước cuối

Python gọi
    
    
    next(iterator)

↓
    
    
    StopIteration

Lúc này
    
    
    for kết thúc

* * *

# Sơ đồ hoàn chỉnh
    
    
    numbers
    
    ↓
    
    iter()
    
    ↓
    
    iterator
    
    ↓
    
    next()
    
    ↓
    
    10
    
    ↓
    
    print()
    
    ↓
    
    next()
    
    ↓
    
    20
    
    ↓
    
    print()
    
    ↓
    
    next()
    
    ↓
    
    30
    
    ↓
    
    print()
    
    ↓
    
    next()
    
    ↓
    
    StopIteration
    
    ↓
    
    kết thúc

* * *

# Mã giả của Python

Đoạn này
    
    
    for item in numbers:
        print(item)

gần tương đương với:
    
    
    iterator = iter(numbers)
    
    while True:
        try:
            item = next(iterator)
        except StopIteration:
            break
    
        print(item)

Đây là điều quan trọng nhất của buổi học.

**`for` chỉ là cú pháp đẹp hơn của đoạn `while` phía trên.**

* * *

# Thử chứng minh

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    iterator = iter(numbers)
    
    while True:
        try:
            x = next(iterator)
            print(x)
        except StopIteration:
            break

Kết quả
    
    
    1
    2
    3

Hoàn toàn giống
    
    
    for x in numbers:
        print(x)

* * *

# `for` không dùng chỉ số

Nhiều người nghĩ
    
    
    for x in numbers:

thực chất là
    
    
    for i in range(len(numbers)):
        print(numbers[i])

Điều này **không đúng**.

* * *

# Vì sao?

Ví dụ
    
    
    s = {10, 20, 30}
    
    for x in s:
        print(x)

Set

  * không có index 
  * không có `s[0]`



Nhưng vẫn lặp được.

* * *

Ví dụ khác
    
    
    text = "Python"
    
    for ch in text:
        print(ch)

String cũng không dùng `range(len())`.

Nó dùng Iterator.

* * *

# File
    
    
    with open("data.txt", encoding="utf8") as f:
        for line in f:
            print(line)

File có index không?

Không.

Vậy `for` làm sao biết dòng tiếp theo?

Đơn giản:
    
    
    next(file_iterator)

* * *

# Generator
    
    
    def numbers():
        yield 1
        yield 2
        yield 3
    
    for x in numbers():
        print(x)

Generator không có
    
    
    obj[0]

Nhưng vẫn lặp.

Lý do:

Generator là Iterator.

* * *

# Chính vì vậy

`for` có thể làm việc với
    
    
    list
    
    tuple
    
    set
    
    dict
    
    file
    
    generator
    
    range
    
    deque
    
    bytes
    
    bytearray
    
    ...

Bởi vì tất cả đều cung cấp Iterator.

* * *

# Thử viết Collection riêng
    
    
    class MyNumbers:
    
        def __iter__(self):
            return iter([10, 20, 30])

Sử dụng
    
    
    obj = MyNumbers()
    
    for x in obj:
        print(x)

Kết quả
    
    
    10
    20
    30

Python không quan tâm đây là lớp do bạn viết.

Nó chỉ hỏi:

> Có `__iter__()` không?

* * *

# Một ví dụ thú vị
    
    
    class Hello:
    
        def __iter__(self):
            return iter("Python")
    
    
    for ch in Hello():
        print(ch)

↓
    
    
    P
    y
    t
    h
    o
    n

* * *

# `break` hoạt động thế nào?

Ví dụ
    
    
    for x in [1, 2, 3, 4]:
        if x == 3:
            break
    
        print(x)

Kết quả
    
    
    1
    2

Điều gì xảy ra?

Python KHÔNG đọc tiếp Iterator nữa.

Iterator vẫn còn
    
    
    4

nhưng vòng lặp dừng.

* * *

Ví dụ
    
    
    numbers = iter([1, 2, 3, 4])
    
    for x in numbers:
        print(x)
    
        if x == 2:
            break

Lúc này
    
    
    print(next(numbers))

↓
    
    
    3

Tại sao?

Iterator vẫn còn sống.

Chỉ có vòng lặp kết thúc.

* * *

# Chứng minh
    
    
    it = iter([10, 20, 30, 40])
    
    for x in it:
        print(x)
    
        if x == 20:
            break
    
    print(next(it))

Kết quả
    
    
    10
    20
    30

Giải thích
    
    
    10 → đã đọc
    
    20 → đã đọc
    
    break
    
    Iterator đang đứng trước 30

* * *

# `continue`
    
    
    for x in [1, 2, 3]:
        if x == 2:
            continue
    
        print(x)

Kết quả
    
    
    1
    3

`continue`

không làm Iterator quay lại.

Nó chỉ bỏ qua phần còn lại của thân vòng lặp.

Lần tiếp theo Python vẫn gọi
    
    
    next(iterator)

* * *

# `else` trong `for`

Ít người biết Python có:
    
    
    for x in [1, 2, 3]:
        print(x)
    else:
        print("Hoàn thành")

↓
    
    
    1
    2
    3
    Hoàn thành

`else` chỉ chạy khi vòng lặp kết thúc **tự nhiên** do `StopIteration`.

Nếu có
    
    
    break

thì
    
    
    else

không chạy.

Ví dụ
    
    
    for x in [1, 2, 3]:
        if x == 2:
            break
    else:
        print("Done")

↓

Không in gì.

* * *

# `enumerate()` cũng dùng Iterator
    
    
    for index, value in enumerate(["A", "B", "C"]):
        print(index, value)

Thực chất
    
    
    enumerate
    
    ↓
    
    Iterator mới
    
    ↓
    
    (0, "A")
    
    ↓
    
    (1, "B")
    
    ↓
    
    (2, "C")

Chúng ta sẽ học chi tiết về `enumerate` ở phần Iterator nâng cao.

* * *

# `zip()` cũng vậy
    
    
    a = [1, 2, 3]
    b = ["A", "B", "C"]
    
    for x, y in zip(a, b):
        print(x, y)

↓
    
    
    1 A
    2 B
    3 C

`zip()` tạo ra một Iterator kết hợp nhiều Iterable.

* * *

# Ví dụ hoàn chỉnh
    
    
    class Squares:
    
        def __init__(self, n):
            self.n = n
    
        def __iter__(self):
            current = 1
    
            while current <= self.n:
                yield current * current
                current += 1
    
    
    squares = Squares(5)
    
    for value in squares:
        print(value)

Kết quả
    
    
    1
    4
    9
    16
    25

Ở đây:

  * `Squares` là **Iterable** (có `__iter__()`). 
  * `__iter__()` sử dụng `yield`, nên Python tự tạo một **Generator Iterator**. 
  * `for` không biết bên trong dùng `yield`; nó chỉ lấy Iterator rồi gọi `next()` liên tục. 



Đây là cách rất phổ biến để xây dựng Iterable trong Python hiện đại.

* * *

# Những hiểu lầm phổ biến

## Hiểu lầm 1

> `for` chỉ dùng được với list.

Sai.

Chỉ cần đối tượng là Iterable.

* * *

## Hiểu lầm 2

> `for` luôn biết số phần tử.

Sai.

Iterator có thể là vô hạn.

Ví dụ:
    
    
    import itertools
    
    for x in itertools.count():
        print(x)

Nếu không có `break`, vòng lặp sẽ chạy mãi vì `itertools.count()` sinh số vô hạn.

* * *

## Hiểu lầm 3

> `for` cần `len()`.

Sai.

Nhiều Iterator không có `len()`.

Ví dụ:
    
    
    it = iter([1, 2, 3])
    
    len(it)

↓
    
    
    TypeError

Nhưng
    
    
    for x in it:
        print(x)

vẫn hoạt động bình thường.

* * *

# Tổng kết buổi 4

Bạn cần nhớ những điểm cốt lõi sau:

  1. `for` luôn bắt đầu bằng cách gọi `iter(obj)`. 
  2. Sau đó `for` gọi `next(iterator)` liên tục. 
  3. Khi `next()` phát sinh `StopIteration`, vòng lặp kết thúc. 
  4. `for` **không dùng** chỉ số (`index`) hay `len()`. 
  5. Mọi đối tượng tuân theo **Iterator Protocol** đều có thể dùng trong `for`. 
  6. `break` chỉ dừng vòng lặp, không hủy Iterator; `continue` chỉ bỏ qua phần còn lại của một lần lặp hiện tại. 



* * *

# Bài tập

### Bài 1

Viết lại đoạn mã sau bằng `while True` và `next()`:
    
    
    for ch in "Iterator":
        print(ch)

* * *

### Bài 2

Tạo một Iterator từ danh sách `[10, 20, 30, 40, 50]`, dùng `for` để đọc đến `30` thì `break`, sau đó gọi `next()` và giải thích vì sao kết quả là `40`.

* * *

### Bài 3

Viết lớp:
    
    
    class Countdown:

trong đó `__iter__()` sử dụng `yield` để sinh các số từ `5` xuống `1`, rồi dùng `for` để in kết quả. Sau đó giải thích chi tiết vì sao `yield` giúp `Countdown` trở thành một Iterable.

Ở **Buổi 5** , chúng ta sẽ đi sâu vào **hàm`iter()`**, khám phá các dạng gọi của `iter()`, cơ chế `iter(callable, sentinel)` ít người biết, và cách Python quyết định một đối tượng có phải là Iterable hay không.

