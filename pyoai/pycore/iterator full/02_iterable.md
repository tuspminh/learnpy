# Iterator Deep Dive — Buổi 2

# Iterable là gì? Phân biệt Iterable và Iterator

Ở buổi trước, chúng ta đã biết:
    
    
    numbers = [10, 20, 30]
    
    it = iter(numbers)
    
    print(next(it))
    print(next(it))

`it` là **Iterator**.

Nhưng có một câu hỏi quan trọng:

> **Tại sao list lại tạo được Iterator?**

Câu trả lời là:

> Vì **list là một Iterable**.

Đây là khái niệm cực kỳ quan trọng.

* * *

# Roadmap

Đã học

  * ✅ Buổi 1: Iterator là gì? 



Hôm nay

  * ✅ Buổi 2: Iterable 



Sắp tới

  * Buổi 3: Iterator Protocol 
  * Buổi 4: Bên trong vòng lặp for 
  * Buổi 5: iter() 
  * Buổi 6: next() 



* * *

# Iterable là gì?

Định nghĩa đơn giản nhất:

> **Iterable là đối tượng có thể tạo ra Iterator.**

Hay nói cách khác:
    
    
    Iterable
        │
    iter()
        │
        ▼
    Iterator
        │
    next()
        │
        ▼
    Phần tử

* * *

# Ví dụ đầu tiên
    
    
    numbers = [1, 2, 3]

Đây là
    
    
    Iterable

vì ta có thể
    
    
    it = iter(numbers)

* * *

Sau đó
    
    
    print(next(it))

mới lấy được dữ liệu.

Điều này rất quan trọng.

List KHÔNG tự lấy dữ liệu.

Iterator mới lấy dữ liệu.

* * *

# Một ví dụ dễ hình dung

Hãy tưởng tượng:
    
    
    Thư viện

là
    
    
    Iterable

Còn
    
    
    Người đọc sách

là
    
    
    Iterator

Người đọc có thể:

  * mở sách 
  * đọc từng trang 
  * nhớ đang ở trang nào 



Trong khi thư viện chỉ chứa sách.

* * *

# Quan hệ giữa Iterable và Iterator
    
    
    List
    
    ↓
    
    Iterable
    
    ↓
    
    iter()
    
    ↓
    
    Iterator
    
    ↓
    
    next()
    
    ↓
    
    1
    
    ↓
    
    2
    
    ↓
    
    3

* * *

# Ví dụ
    
    
    numbers = [10, 20, 30]
    
    print(numbers)

Kết quả
    
    
    [10, 20, 30]

Đây chỉ là dữ liệu.

* * *

Muốn duyệt
    
    
    it = iter(numbers)

Bây giờ
    
    
    print(next(it))

↓
    
    
    10

* * *

# Kiểm tra bằng isinstance()

Python có module
    
    
    collections.abc

định nghĩa các giao diện (ABC) như `Iterable` và `Iterator`.

Ví dụ:
    
    
    from collections.abc import Iterable
    
    numbers = [1, 2, 3]
    
    print(isinstance(numbers, Iterable))

Kết quả
    
    
    True

* * *

Tuple
    
    
    from collections.abc import Iterable
    
    data = (1, 2, 3)
    
    print(isinstance(data, Iterable))

↓
    
    
    True

* * *

String
    
    
    from collections.abc import Iterable
    
    text = "Python"
    
    print(isinstance(text, Iterable))

↓
    
    
    True

* * *

Dictionary
    
    
    from collections.abc import Iterable
    
    d = {"a": 1, "b": 2}
    
    print(isinstance(d, Iterable))

↓
    
    
    True

* * *

Set
    
    
    from collections.abc import Iterable
    
    s = {1, 2, 3}
    
    print(isinstance(s, Iterable))

↓
    
    
    True

* * *

# Những gì là Iterable

Hầu như mọi collection trong Python đều là Iterable.
    
    
    []
    ()
    {}
    set()
    
    str
    bytes
    bytearray
    
    range()
    
    deque()
    
    dict_keys
    
    dict_values
    
    dict_items
    
    file

* * *

# range cũng là Iterable
    
    
    r = range(5)
    
    print(r)

↓
    
    
    range(0, 5)

Muốn lấy dữ liệu
    
    
    it = iter(r)
    
    print(next(it))

↓
    
    
    0

* * *

# File cũng là Iterable
    
    
    with open("data.txt", encoding="utf-8") as f:
        print(isinstance(f, Iterable))

↓
    
    
    True

Do đó ta có thể
    
    
    for line in f:
        print(line)

* * *

# dict cũng là Iterable

Đây là điều nhiều người mới học không để ý.
    
    
    d = {
        "name": "Alice",
        "age": 20
    }
    
    for x in d:
        print(x)

Kết quả
    
    
    name
    age

Tại sao?

Vì Iterator mặc định của dict trả về **key**.

* * *

Nếu muốn value
    
    
    for x in d.values():
        print(x)

↓
    
    
    Alice
    20

* * *

# Iterable KHÔNG nhất thiết phải là Iterator

Đây là phần quan trọng nhất buổi học.

Ví dụ
    
    
    numbers = [1, 2, 3]

Kiểm tra
    
    
    from collections.abc import Iterator
    
    print(isinstance(numbers, Iterator))

↓
    
    
    False

List KHÔNG phải Iterator.

* * *

Nhưng
    
    
    it = iter(numbers)
    
    print(isinstance(it, Iterator))

↓
    
    
    True

* * *

Bảng so sánh

Đối tượng| Iterable| Iterator  
---|---|---  
list| ✅| ❌  
tuple| ✅| ❌  
string| ✅| ❌  
dict| ✅| ❌  
set| ✅| ❌  
file| ✅| ✅  
list_iterator| ✅| ✅  
generator| ✅| ✅  
  
Lưu ý:

  * Một **Iterator luôn là một Iterable** , vì nó có thể trả về chính nó khi gọi `iter()`. 
  * Nhưng **không phải Iterable nào cũng là Iterator**. 



* * *

# Vì sao phải tách thành hai loại?

Nếu List là Iterator luôn thì sẽ có vấn đề.

Ví dụ:
    
    
    numbers = [1, 2, 3]
    
    for x in numbers:
        print(x)
    
    for x in numbers:
        print(x)

Kết quả
    
    
    1
    2
    3
    1
    2
    3

List có thể lặp lại nhiều lần.

* * *

Nếu List chính là Iterator
    
    
    1
    2
    3

thì lần thứ hai sẽ:
    
    
    không còn dữ liệu

Điều này sẽ rất bất tiện.

Vì vậy Python thiết kế:
    
    
    List

chỉ là
    
    
    Iterable

Mỗi lần cần lặp sẽ sinh ra
    
    
    Iterator mới

* * *

# Chứng minh
    
    
    numbers = [1, 2, 3]
    
    it1 = iter(numbers)
    it2 = iter(numbers)
    
    print(next(it1))
    print(next(it1))
    
    print(next(it2))

Kết quả
    
    
    1
    2
    1

Hai Iterator hoàn toàn độc lập.

* * *

# Sơ đồ bộ nhớ
    
    
    numbers
    
    +----------------+
    |1|2|3|
    +----------------+
    
          ▲
          │
    
    it1
    
          ▲
          │
    
    it2

Sau hai lần `next(it1)`:
    
    
    numbers
    
    +----------------+
    |1|2|3|
    +----------------+
    
              ▲
              │
    
    it1
    
          ▲
          │
    
    it2

`numbers` không thay đổi, chỉ có trạng thái của từng Iterator thay đổi.

* * *

# Ví dụ hoàn chỉnh
    
    
    from collections.abc import Iterable, Iterator
    
    data = ["A", "B", "C"]
    
    print("data là Iterable:", isinstance(data, Iterable))
    print("data là Iterator:", isinstance(data, Iterator))
    
    it = iter(data)
    
    print("it là Iterable:", isinstance(it, Iterable))
    print("it là Iterator:", isinstance(it, Iterator))
    
    print(next(it))
    print(next(it))
    
    print("Tạo iterator mới...")
    
    it2 = iter(data)
    
    for item in it2:
        print(item)

**Kết quả**
    
    
    data là Iterable: True
    data là Iterator: False
    it là Iterable: True
    it là Iterator: True
    A
    B
    Tạo iterator mới...
    A
    B
    C

* * *

# Những lỗi phổ biến

## Lỗi 1: Nhầm Iterable với Iterator

Sai:
    
    
    numbers = [1, 2, 3]
    
    next(numbers)

Lỗi:
    
    
    TypeError: 'list' object is not an iterator

Đúng:
    
    
    numbers = [1, 2, 3]
    
    it = iter(numbers)
    
    print(next(it))

* * *

## Lỗi 2: Cho rằng `for` gọi `next()` trực tiếp trên list

Nhiều người tưởng:
    
    
    for x in numbers:

tương đương:
    
    
    next(numbers)

Điều này **không đúng**.

Thực tế:
    
    
    it = iter(numbers)
    
    while True:
        try:
            x = next(it)
        except StopIteration:
            break
    
        print(x)

`for` luôn gọi `iter()` trước rồi mới dùng `next()`.

* * *

# Tổng kết buổi 2

Bạn cần ghi nhớ 5 ý quan trọng:

  1. **Iterable** là đối tượng có thể tạo ra Iterator thông qua `iter()`. 
  2. Các kiểu dữ liệu như `list`, `tuple`, `dict`, `set`, `str`, `range` đều là Iterable. 
  3. **Iterator** là đối tượng thực hiện việc duyệt từng phần tử bằng `next()`. 
  4. Mỗi lần gọi `iter(iterable)` thường sẽ tạo một Iterator mới với trạng thái độc lập. 
  5. `for` không lặp trực tiếp trên Iterable; nó luôn lấy một Iterator trước rồi mới gọi `next()` liên tục. 



* * *

# Bài tập

### Bài 1

Cho các đối tượng sau:
    
    
    data = [
        [1, 2, 3],
        (4, 5, 6),
        {7, 8, 9},
        {"a": 1, "b": 2},
        "Python",
        range(5),
    ]

Hãy kiểm tra từng đối tượng có phải là `Iterable` hay không bằng `isinstance()`.

* * *

### Bài 2

Với mỗi đối tượng ở bài 1:

  * Tạo `Iterator` bằng `iter()`. 
  * In ra hai phần tử đầu tiên bằng `next()`. 



* * *

### Bài 3

Tạo hai `Iterator` từ cùng một `list` và chứng minh rằng chúng hoạt động độc lập bằng cách gọi `next()` xen kẽ trên từng `Iterator`.

Ở **Buổi 3** , chúng ta sẽ đi sâu vào **Iterator Protocol** (`__iter__()` và `__next__()`), nền tảng giúp bạn tự xây dựng các Iterator của riêng mình và hiểu cách Python hỗ trợ mọi kiểu dữ liệu có thể lặp.

