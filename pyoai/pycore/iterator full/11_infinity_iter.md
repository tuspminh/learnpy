# Iterator Deep Dive — Buổi 11

# Iterator vô hạn (Infinite Iterator)

Đây là một chủ đề cực kỳ quan trọng vì rất nhiều thư viện Python sử dụng **Iterator vô hạn**.

Ví dụ:

  * `itertools.count()`
  * `itertools.cycle()`
  * `itertools.repeat()`
  * Bộ sinh ID 
  * Đồng hồ thời gian 
  * Stream dữ liệu 
  * Sensor IoT 
  * Message Queue 
  * Event Loop 
  * AI Token Stream 



Sau buổi này bạn sẽ hiểu:

  * Infinite Iterator là gì 
  * Khi nào nên dùng 
  * Làm sao để dừng nó an toàn 
  * Thiết kế Infinite Iterator đúng chuẩn 



* * *

# Roadmap

Đã học

  * ✅ Buổi 1–10 



Hôm nay

  * ✅ Buổi 11 — Infinite Iterator 



Tiếp theo

  * Buổi 12 — Reset Iterator 



* * *

# Iterator thông thường

Ví dụ
    
    
    numbers = iter([1, 2, 3])
    
    print(next(numbers))
    print(next(numbers))
    print(next(numbers))

↓
    
    
    1
    2
    3

Lần tiếp
    
    
    next(numbers)

↓
    
    
    StopIteration

Đây là **Iterator hữu hạn**.

* * *

# Infinite Iterator

Infinite Iterator

↓

không bao giờ
    
    
    StopIteration

Ví dụ
    
    
    1
    
    2
    
    3
    
    4
    
    5
    
    6
    
    7
    
    8
    
    ...

Không có điểm kết thúc.

* * *

# Ví dụ đơn giản
    
    
    class Counter:
    
        def __init__(self):
            self.value = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            value = self.value
            self.value += 1
            return value

* * *

# Thử
    
    
    counter = Counter()
    
    for x in counter:
        print(x)

Điều gì xảy ra?
    
    
    1
    2
    3
    4
    5
    ...

Không bao giờ dừng.

* * *

# Vì sao?

`__next__()`

không có
    
    
    raise StopIteration

* * *

# Minh họa
    
    
    next()
    
    ↓
    
    1
    
    ↓
    
    next()
    
    ↓
    
    2
    
    ↓
    
    next()
    
    ↓
    
    3
    
    ↓
    
    ...
    
    ↓
    
    ∞

* * *

# Dừng như thế nào?

Không dùng
    
    
    for x in counter:

Mà dùng
    
    
    for x in counter:
    
        if x > 10:
            break
    
        print(x)

↓
    
    
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10

* * *

# next()
    
    
    counter = Counter()
    
    print(next(counter))
    print(next(counter))
    print(next(counter))

↓
    
    
    1
    2
    3

Hoàn toàn bình thường.

* * *

# Iterator không biết tương lai

Iterator không biết
    
    
    bao giờ dừng

Nó chỉ biết
    
    
    Lần sau trả gì

Đây là triết lý của Iterator.

* * *

# Infinite Fibonacci
    
    
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

* * *

Kết quả
    
    
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
    ...

Không bao giờ hết.

* * *

# Infinite Even Number
    
    
    class Even:
    
        def __init__(self):
            self.value = 0
    
        def __iter__(self):
            return self
    
        def __next__(self):
            value = self.value
            self.value += 2
            return value

↓
    
    
    0
    2
    4
    6
    8
    10
    ...

* * *

# Infinite Odd
    
    
    class Odd:
    
        def __init__(self):
            self.value = 1
    
        def __iter__(self):
            return self
    
        def __next__(self):
            value = self.value
            self.value += 2
            return value

↓
    
    
    1
    3
    5
    7
    9
    ...

* * *

# Infinite UUID

Giả sử
    
    
    import uuid
    
    class UUIDGenerator:
    
        def __iter__(self):
            return self
    
        def __next__(self):
            return uuid.uuid4()

↓
    
    
    3a...
    
    c9...
    
    12...
    
    ...

Không bao giờ hết.

Ứng dụng:

  * Session ID 
  * Request ID 
  * Transaction ID 



* * *

# Infinite Timestamp
    
    
    from datetime import datetime
    
    class Clock:
    
        def __iter__(self):
            return self
    
        def __next__(self):
            return datetime.now()

Mỗi lần
    
    
    next(clock)

↓
    
    
    2026-07-26 ...
    
    2026-07-26 ...

* * *

# Infinite Random
    
    
    import random
    
    class RandomNumber:
    
        def __iter__(self):
            return self
    
        def __next__(self):
            return random.randint(1, 100)

↓
    
    
    51
    
    2
    
    88
    
    13
    
    ...

* * *

# Stream dữ liệu

Giả sử cảm biến nhiệt độ.
    
    
    25.1
    
    25.2
    
    25.4
    
    25.6
    
    25.5
    
    ...

Sensor không bao giờ "hết dữ liệu".

Đó chính là Infinite Iterator.

* * *

# Log Stream

Server liên tục sinh log.
    
    
    INFO
    
    INFO
    
    ERROR
    
    WARNING
    
    ...

Không biết khi nào kết thúc.

* * *

# Chat Stream

Ví dụ AI trả token.
    
    
    Xin
    
    chào
    
    bạn
    
    ...

Mỗi token được sinh ra theo thời gian.

Iterator vô hạn rất phù hợp với kiểu dữ liệu này.

* * *

# itertools.count()

Python có sẵn.
    
    
    import itertools
    
    counter = itertools.count()
    
    for x in counter:
    
        if x > 5:
            break
    
        print(x)

↓
    
    
    0
    1
    2
    3
    4
    5

* * *

# count(start)
    
    
    counter = itertools.count(100)

↓
    
    
    100
    
    101
    
    102
    
    ...

* * *

# count(step)
    
    
    counter = itertools.count(0, 5)

↓
    
    
    0
    
    5
    
    10
    
    15

* * *

# itertools.cycle()
    
    
    import itertools
    
    colors = itertools.cycle([
        "red",
        "green",
        "blue"
    ])
    
    for i, color in enumerate(colors):
    
        if i == 10:
            break
    
        print(color)

↓
    
    
    red
    green
    blue
    red
    green
    blue
    ...

* * *

# cycle hoạt động
    
    
    red
    
    ↓
    
    green
    
    ↓
    
    blue
    
    ↓
    
    red
    
    ↓
    
    green

Không bao giờ hết.

* * *

# itertools.repeat()
    
    
    import itertools
    
    it = itertools.repeat("Python")

↓
    
    
    Python
    
    Python
    
    Python
    
    ...

* * *

# Infinite không có nghĩa là tốn RAM

Đây là hiểu lầm rất phổ biến.

Sai
    
    
    ∞
    
    ↓
    
    RAM vô hạn

Đúng
    
    
    1 object
    
    ↓
    
    Sinh từng phần tử
    
    ↓
    
    Bỏ phần tử cũ
    
    ↓
    
    Sinh phần tử mới

RAM gần như không đổi.

* * *

# So sánh

Iterator hữu hạn
    
    
    1
    
    2
    
    3
    
    StopIteration

* * *

Iterator vô hạn
    
    
    1
    
    2
    
    3
    
    4
    
    5
    
    ...
    
    ∞

* * *

# Sai lầm
    
    
    numbers = Counter()
    
    print(list(numbers))

Điều gì xảy ra?

`list()` sẽ cố đọc
    
    
    đến khi StopIteration

Nhưng
    
    
    không bao giờ có

↓

Chương trình sẽ chạy mãi (hoặc cạn bộ nhớ).

* * *

# Sai lầm khác
    
    
    tuple(counter)

↓

Không bao giờ xong.

* * *

# Cách an toàn

Dùng `itertools.islice()`.
    
    
    import itertools
    
    counter = Counter()
    
    for x in itertools.islice(counter, 10):
        print(x)

↓
    
    
    1
    2
    3
    ...
    10

`islice()` là công cụ rất quan trọng khi làm việc với Infinite Iterator.

* * *

# Ví dụ hoàn chỉnh
    
    
    import itertools
    
    
    class PrimeCandidate:
    
        def __init__(self):
            self.value = 2
    
        def __iter__(self):
            return self
    
        def __next__(self):
    
            value = self.value
    
            self.value += 1
    
            return value
    
    
    numbers = PrimeCandidate()
    
    for n in itertools.islice(numbers, 20):
        print(n)

Kết quả
    
    
    2
    3
    4
    5
    6
    ...
    21

(Lưu ý: ví dụ này sinh **ứng viên số nguyên** , chưa phải bộ sinh số nguyên tố.)

* * *

# Khi nào nên dùng Infinite Iterator?

Rất phù hợp khi dữ liệu:

  * Không có điểm kết thúc rõ ràng. 
  * Được sinh theo thời gian. 
  * Không thể hoặc không nên tải toàn bộ vào bộ nhớ. 



Ví dụ:

  * Log server. 
  * Dữ liệu cảm biến. 
  * Đồng hồ. 
  * Luồng token AI. 
  * Queue xử lý tác vụ. 
  * Event stream. 



* * *

# Thiết kế Collection hay Iterator?

Infinite Iterator thường **không cần** tách thành Collection + Iterator.

Ví dụ:
    
    
    counter = Counter()

vừa là

  * Iterator 
  * Iterable 



Giống:

  * `itertools.count()`
  * Generator 
  * File object 
  * `enumerate()`
  * `zip()`



Bởi vì nó đại diện cho **một luồng dữ liệu** , không phải một tập dữ liệu có thể lặp lại nhiều lần.

* * *

# Tổng kết buổi 11

Bạn cần nhớ:

  1. Infinite Iterator **không bao giờ** phát sinh `StopIteration`. 
  2. Không nên chuyển Infinite Iterator thành `list()`, `tuple()`, hoặc `set()`. 
  3. Hãy giới hạn số phần tử bằng: 
     * `break`
     * `itertools.islice()`
  4. Infinite Iterator chỉ sinh từng phần tử khi được yêu cầu, nên rất tiết kiệm bộ nhớ. 
  5. Đây là nền tảng của nhiều hệ thống xử lý dữ liệu theo luồng (stream processing). 



* * *

# Bài tập

## Bài 1

Viết lớp:
    
    
    class SquareNumbers:

Sinh vô hạn:
    
    
    1
    4
    9
    16
    25
    ...

Sau đó dùng `itertools.islice()` để in 15 số đầu tiên.

* * *

## Bài 2

Viết lớp:
    
    
    class RandomPassword:

Mỗi lần `next()` trả về một mật khẩu ngẫu nhiên dài 8 ký tự (chữ và số). Dùng `islice()` để lấy 10 mật khẩu đầu tiên.

* * *

## Bài 3

Viết lớp:
    
    
    class Sensor:

Mỗi lần `next()` trả về:
    
    
    {
        "temperature": ...,
        "humidity": ...,
        "timestamp": ...
    }

Trong đó:

  * Nhiệt độ ngẫu nhiên từ `20`–`35`. 
  * Độ ẩm ngẫu nhiên từ `40`–`90`. 
  * `timestamp` là thời điểm hiện tại. 



Sau đó dùng `itertools.islice(sensor, 5)` để mô phỏng việc đọc 5 bản ghi đầu tiên từ một cảm biến IoT.

* * *

Ở **Buổi 12** , chúng ta sẽ học **Reset Iterator** : vì sao hầu hết Iterator trong Python **không thể reset** , các chiến lược để "quay lại từ đầu", và cách thiết kế các Iterator có thể khởi động lại khi xây dựng thư viện hoặc framework.

