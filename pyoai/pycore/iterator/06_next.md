# Iterator Deep Dive — Buổi 6

# `next()` Deep Dive

Đây là buổi cuối cùng của phần nền tảng Iterator.

Sau buổi này, bạn sẽ hiểu:

  * `next()` thực chất làm gì 
  * Tại sao `StopIteration` tồn tại 
  * `next(iterator, default)`
  * Khi nào nên dùng `next()`
  * Những lỗi rất thường gặp trong thực tế 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1 — Iterator 
  * ✅ Buổi 2 — Iterable 
  * ✅ Buổi 3 — Iterator Protocol 
  * ✅ Buổi 4 — Cơ chế hoạt động của `for`
  * ✅ Buổi 5 — `iter()`



Hôm nay

  * ✅ Buổi 6 — `next()`



Tiếp theo

  * Buổi 7 — Tự xây Iterator đầu tiên 



* * *

# next() là gì?

Định nghĩa đơn giản:

> **`next()` lấy phần tử tiếp theo từ một Iterator.**

Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(next(it))

↓
    
    
    10

* * *

# next() gọi gì?

Giống như
    
    
    iter(obj)

thực chất gọi
    
    
    obj.__iter__()

thì
    
    
    next(it)

thực chất gọi
    
    
    it.__next__()

Ví dụ
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    print(next(it))
    print(it.__next__())

↓
    
    
    1
    2

Hai cách hoàn toàn giống nhau.

* * *

# Quá trình hoạt động

Ví dụ
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)

Lần đầu
    
    
    next(it)

↓
    
    
    10

Iterator nhớ
    
    
    đã đọc tới vị trí 0

* * *

Lần hai
    
    
    next(it)

↓
    
    
    20

Iterator nhớ
    
    
    đã đọc tới vị trí 1

* * *

Lần ba
    
    
    next(it)

↓
    
    
    30

* * *

Lần bốn
    
    
    next(it)

↓
    
    
    StopIteration

* * *

# Minh họa
    
    
    Iterator
    
    ↓
    
    10
    
    ↓
    
    20
    
    ↓
    
    30
    
    ↓
    
    StopIteration

* * *

# next() chỉ dùng với Iterator

Sai
    
    
    numbers = [1, 2, 3]
    
    next(numbers)

↓
    
    
    TypeError
    
    'list' object is not an iterator

Đúng
    
    
    it = iter(numbers)
    
    next(it)

* * *

# next() và Iterator Protocol

Nhớ buổi trước
    
    
    class Counter:
    
        def __iter__(self):
            return self
    
        def __next__(self):
            ...

`next(counter)` sẽ gọi
    
    
    counter.__next__()

* * *

# Ví dụ
    
    
    class Counter:
    
        def __init__(self):
            self.value = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            if self.value > 3:
                raise StopIteration
    
            result = self.value
            self.value += 1
            return result

Sử dụng
    
    
    counter = Counter()
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    1
    2
    3

* * *

# Điều gì xảy ra sau đó?
    
    
    print(next(counter))

↓
    
    
    StopIteration

* * *

# next() có tham số thứ hai

Đây là tính năng nhiều người chưa biết.

Cú pháp
    
    
    next(iterator, default)

Nếu Iterator hết dữ liệu

↓

không phát sinh lỗi

↓

mà trả về
    
    
    default

* * *

# Ví dụ
    
    
    numbers = [1, 2]
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))
    print(next(it, "Hết"))
    print(next(it, "Hết luôn"))

↓
    
    
    1
    2
    Hết
    Hết luôn

Không có `StopIteration`.

* * *

# So sánh

## Không có default
    
    
    next(it)

↓
    
    
    StopIteration

* * *

## Có default
    
    
    next(it, None)

↓
    
    
    None

* * *

# Ứng dụng thực tế

Ví dụ
    
    
    users = iter(["Alice", "Bob"])
    
    user = next(users, None)
    
    if user is None:
        print("Không còn user")
    else:
        print(user)

Không cần
    
    
    try:
        ...
    except StopIteration:
        ...

* * *

# next() trong while

Đây là mẫu rất phổ biến.
    
    
    numbers = iter([10, 20, 30])
    
    while True:
    
        value = next(numbers, None)
    
        if value is None:
            break
    
        print(value)

↓
    
    
    10
    20
    30

* * *

# So sánh với try/except

### Cách 1
    
    
    while True:
        try:
            print(next(it))
        except StopIteration:
            break

* * *

### Cách 2
    
    
    while True:
    
        value = next(it, None)
    
        if value is None:
            break
    
        print(value)

Ngắn hơn.

**Lưu ý:** Chỉ dùng cách này khi `None` không thể là dữ liệu hợp lệ.

* * *

# Cẩn thận với default

Ví dụ
    
    
    data = [1, None, 3]
    
    it = iter(data)
    
    while True:
    
        value = next(it, None)
    
        if value is None:
            break
    
        print(value)

Kết quả
    
    
    1

Sai.

Vì
    
    
    None

là dữ liệu thật.

* * *

# Giải pháp

Dùng một object đặc biệt làm giá trị đánh dấu (sentinel).
    
    
    _sentinel = object()
    
    it = iter([1, None, 3])
    
    while True:
        value = next(it, _sentinel)
        if value is _sentinel:
            break
    
        print(value)

↓
    
    
    1
    None
    3

Đây là kỹ thuật rất phổ biến trong thư viện Python.

* * *

# next() với Generator
    
    
    def numbers():
        yield 10
        yield 20
        yield 30
    
    
    g = numbers()
    
    print(next(g))
    print(next(g))
    print(next(g))

↓
    
    
    10
    20
    30

Generator chính là Iterator.

* * *

# next() với File
    
    
    with open("data.txt", encoding="utf8") as f:
    
        print(next(f))
        print(next(f))

↓
    
    
    Dòng đầu
    
    Dòng hai

Mỗi lần
    
    
    next(f)

↓

đọc một dòng.

* * *

# next() và for

Ví dụ
    
    
    it = iter([1, 2, 3])
    
    print(next(it))
    
    for x in it:
        print(x)

↓
    
    
    1
    2
    3

Vì Iterator đã đọc mất
    
    
    1

nên `for` chỉ đọc phần còn lại.

* * *

# Chứng minh
    
    
    it = iter([10, 20, 30])
    
    print(next(it))
    print(next(it))
    
    for x in it:
        print(x)

↓
    
    
    10
    20
    30

* * *

# next() không quay lại

Sai
    
    
    it = iter([1, 2, 3])
    
    next(it)
    
    next(it)
    
    next(it)

Nhiều người nghĩ
    
    
    1
    
    2
    
    3
    
    1

Đúng là
    
    
    1
    
    2
    
    3
    
    StopIteration

Iterator chỉ đi tới.

* * *

# next() và itertools

Ví dụ
    
    
    import itertools
    
    counter = itertools.count()
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    0
    1
    2

Không bao giờ có
    
    
    StopIteration

vì đây là **Iterator vô hạn**.

* * *

# next() với enumerate()
    
    
    e = enumerate(["A", "B", "C"])
    
    print(next(e))
    print(next(e))

↓
    
    
    (0, 'A')
    (1, 'B')

`enumerate()` trả về một Iterator.

* * *

# next() với zip()
    
    
    z = zip([1, 2], ["A", "B"])
    
    print(next(z))
    print(next(z))

↓
    
    
    (1, 'A')
    (2, 'B')

* * *

# Ví dụ hoàn chỉnh
    
    
    class Fibonacci:
    
        def __init__(self):
            self.a = 0
            self.b = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            value = self.a
            self.a, self.b = self.b, self.a + self.b
            return value
    
    
    fib = Fibonacci()
    
    for _ in range(10):
        print(next(fib))

↓
    
    
    0
    1
    1
    2
    3
    5
    8
    13
    21
    34

Đây là ví dụ của một **Iterator vô hạn**.

* * *

# Sơ đồ toàn bộ quá trình
    
    
    Iterator
    
    ↓
    
    next()
    
    ↓
    
    __next__()
    
    ↓
    
    value
    
    ↓
    
    next()
    
    ↓
    
    __next__()
    
    ↓
    
    value
    
    ↓
    
    ...
    
    ↓
    
    StopIteration

* * *

# Những lỗi phổ biến

## Lỗi 1
    
    
    next([1, 2, 3])

Sai.

Phải dùng
    
    
    next(iter([1, 2, 3]))

* * *

## Lỗi 2

Dùng `None` làm `default` khi `None` là dữ liệu hợp lệ.

Giải pháp:
    
    
    _marker = object()
    value = next(it, _marker)

* * *

## Lỗi 3

Quên rằng `next()` làm thay đổi trạng thái Iterator.
    
    
    print(next(it))
    print(next(it))

Lần gọi thứ hai luôn lấy **phần tử kế tiếp** , không phải phần tử cũ.

* * *

# Tổng kết Buổi 6

Bạn cần ghi nhớ:

  1. `next(iterator)` gọi `iterator.__next__()`. 
  2. `next()` chỉ làm việc với **Iterator** , không phải mọi Iterable. 
  3. Khi hết dữ liệu, `__next__()` phải phát sinh `StopIteration`. 
  4. `next(iterator, default)` giúp tránh phải dùng `try/except`, nhưng hãy chọn `default` cẩn thận. 
  5. Mỗi lần gọi `next()` sẽ **tiêu thụ** (consume) một phần tử và làm thay đổi trạng thái của Iterator. 
  6. `for` cũng chỉ là việc gọi `next()` liên tục cho đến khi gặp `StopIteration`. 



* * *

# Bài tập

## Bài 1

Viết lớp `AlphabetIterator` sinh các chữ cái từ `'A'` đến `'Z'` bằng cách cài đặt `__iter__()` và `__next__()`. Sau đó dùng `next()` để lấy 5 chữ cái đầu tiên.

* * *

## Bài 2

Tạo một `generator` sinh các số từ `1` đến `5`, rồi:

  * Gọi `next()` hai lần. 
  * Dùng `for` để in các giá trị còn lại. 
  * Giải thích vì sao `for` không in lại hai số đầu tiên. 



* * *

## Bài 3

Viết hàm:
    
    
    def first_even(iterable):
        ...

Yêu cầu:

  * Tìm số chẵn đầu tiên trong một Iterable. 
  * Không chuyển Iterable thành `list`. 
  * Sử dụng `iter()` và `next()` để duyệt. 
  * Trả về `None` nếu không có số chẵn. 



Ví dụ:
    
    
    print(first_even([1, 3, 5, 8, 9]))
    # 8
    
    print(first_even([1, 3, 5]))
    # None

* * *

Ở **Buổi 7** , chúng ta sẽ bắt đầu phần thực hành với **tự xây dựng Iterator đầu tiên** , phân biệt rõ **Iterable Object** và **Iterator Object** theo đúng cách mà các thư viện Python chuyên nghiệp (pandas, Django ORM, `pathlib`, `itertools`, ...) thiết kế. Đây là bước chuyển từ "hiểu" sang "tự thiết kế" Iterator.

