# OOP Deep Dive – Buổi 19

# Object Lifecycle Deep Dive – `__new__()`, `__init__()`, `__del__()` và Vòng đời của Object

> Nếu Metaclass giúp bạn hiểu **class được tạo như thế nào**, thì buổi hôm nay sẽ giúp bạn hiểu **object được tạo như thế nào**.

Rất nhiều lập trình viên Python chỉ biết:

```text-x-trilium-auto
obj = MyClass()
```

Nhưng phía sau một dòng lệnh đơn giản đó là cả một chuỗi sự kiện.

Sau buổi này, bạn sẽ hiểu:

- Vì sao `__new__()` chạy trước `__init__()`.
- Khi nào `__init__()` **không được gọi**.
- `__del__()` có đáng tin cậy không.
- Cách Python cấp phát bộ nhớ cho object.
- Cách xây dựng `Singleton`, `Flyweight`, `Object Pool`.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Object Lifecycle
- `__new__()`
- `__init__()`
- `__del__()`
- Immutable Objects
- Singleton
- Flyweight
- Object Pool
- Garbage Collection (ở mức tổng quan)

---

# 1. Điều gì xảy ra khi gọi `Person()`?

Giả sử:

```text-x-trilium-auto
class Person:
    pass

p = Person()
```

Bạn nghĩ Python làm gì?

Thực tế:

```text-x-trilium-auto
Person()

↓

__new__()

↓

Tạo object

↓

__init__()

↓

Khởi tạo object

↓

Trả về object
```

Đây là quy trình chuẩn.

---

# 2. `__new__()` là gì?

`__new__()` chịu trách nhiệm:

> **Tạo object**

Nó chạy trước `__init__()`.

Ví dụ:

```text-x-trilium-auto
class Person:

    def __new__(cls):
        print("__new__")
        return super().__new__(cls)

    def __init__(self):
        print("__init__")
```

Kết quả:

```text-x-trilium-auto
__new__
__init__
```

---

# 3. Khác nhau giữa `__new__()` và `__init__()`

## `__new__()`

- tạo object
- trả về object

## `__init__()`

- nhận object đã tạo
- khởi tạo dữ liệu

---

Sơ đồ

```text-x-trilium-auto
Memory

↓

__new__()

↓

Object

↓

__init__()

↓

Ready
```

---

# 4. `__new__()` phải return gì?

Ví dụ đúng

```text-x-trilium-auto
class Person:

    def __new__(cls):

        obj = super().__new__(cls)

        return obj
```

---

Ví dụ sai

```text-x-trilium-auto
class Person:

    def __new__(cls):

        return 123
```

Thử

```text-x-trilium-auto
p = Person()
```

Kết quả

```text-x-trilium-auto
print(type(p))
```

↓

```text-x-trilium-auto
<class 'int'>
```

`__init__()` không chạy.

---

# 5. Tại sao?

Python chỉ gọi `__init__()` nếu:

```text-x-trilium-auto
__new__()

↓

Trả về

↓

Instance của class
```

Nếu trả về object khác

↓

`__init__()` bị bỏ qua.

---

# 6. Thử nghiệm

```text-x-trilium-auto
class Demo:

    def __new__(cls):

        print("new")

        return object()

    def __init__(self):

        print("init")
```

Kết quả

```text-x-trilium-auto
new
```

Không có:

```text-x-trilium-auto
init
```

---

# 7. Immutable Object

Các kiểu:

```text-x-trilium-auto
int

str

tuple

frozenset
```

là immutable.

Việc khởi tạo giá trị của chúng diễn ra chủ yếu trong `__new__()`, vì sau khi tạo xong chúng không thể thay đổi.

Ví dụ:

```text-x-trilium-auto
class PositiveInt(int):

    def __new__(cls, value):

        if value < 0:

            value = 0

        return super().__new__(cls, value)
```

---

```text-x-trilium-auto
print(PositiveInt(-5))
```

↓

```text-x-trilium-auto
0
```

Không cần `__init__()`.

---

# 8. Tại sao?

`int`

không cho sửa giá trị.

Nên:

```text-x-trilium-auto
__new__()

↓

Quyết định giá trị

↓

Tạo object
```

---

# 9. Singleton Pattern

Ý tưởng:

```text-x-trilium-auto
Chỉ có

1 object
```

---

```text-x-trilium-auto
class Singleton:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

        return cls._instance
```

---

```text-x-trilium-auto
a = Singleton()

b = Singleton()
```

↓

```text-x-trilium-auto
print(a is b)
```

↓

```text-x-trilium-auto
True
```

---

# 10. `__init__()` vẫn chạy

Đây là điều nhiều người bất ngờ.

```text-x-trilium-auto
class Singleton:

    _instance = None

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        print("init")
```

```text-x-trilium-auto
Singleton()

Singleton()
```

↓

```text-x-trilium-auto
init

init
```

Mặc dù chỉ có một object.

Vì `__init__()` được gọi sau mỗi lần gọi `Singleton()` nếu `__new__()` trả về một instance hợp lệ.

---

# 11. Singleton đúng hơn

Thường thêm cờ:

```text-x-trilium-auto
class Singleton:

    _instance = None

    _initialized = False

    def __new__(cls):

        if cls._instance is None:

            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if self._initialized:

            return

        print("Initialize")

        self._initialized = True
```

---

# 12. Flyweight Pattern

Ý tưởng

Nếu hai object giống hệt nhau

↓

Dùng chung.

Ví dụ

```text-x-trilium-auto
class Color:

    _cache = {}

    def __new__(cls, name):

        if name not in cls._cache:

            cls._cache[name] = super().__new__(cls)

        return cls._cache[name]
```

---

```text-x-trilium-auto
a = Color("red")

b = Color("red")
```

↓

```text-x-trilium-auto
a is b
```

↓

```text-x-trilium-auto
True
```

---

# 13. Object Pool

Ý tưởng

```text-x-trilium-auto
Tạo sẵn

10 object

↓

Lấy ra dùng

↓

Trả lại pool
```

Thường dùng cho:

- Database Connection
- HTTP Connection
- Thread
- Worker

---

# 14. `__del__()`

Có:

```text-x-trilium-auto
class Demo:

    def __del__(self):

        print("Destroy")
```

---

```text-x-trilium-auto
obj = Demo()

del obj
```

Có thể in:

```text-x-trilium-auto
Destroy
```

---

# 15. Có nên dùng `__del__()`?

Không nên dựa vào `__del__()` để giải phóng tài nguyên quan trọng.

Lý do:

- Thời điểm được gọi phụ thuộc vào Garbage Collector.
- Không đảm bảo sẽ chạy khi chương trình kết thúc.
- Có thể không chạy nếu có vòng tham chiếu (ở một số trường hợp).

Nên dùng:

```text-x-trilium-auto
with ...
```

hoặc

```text-x-trilium-auto
try:
    ...
finally:
    resource.close()
```

---

# 16. Garbage Collection

Python dùng:

- Reference Counting
- Cyclic Garbage Collector

Khi không còn reference

↓

Object có thể bị thu hồi.

---

# 17. `id()`

Ví dụ

```text-x-trilium-auto
a = Person()

print(id(a))
```

↓

```text-x-trilium-auto
140543827...
```

Đây là định danh của object trong suốt vòng đời của nó.

Lưu ý: Sau khi object bị hủy, Python **có thể** tái sử dụng giá trị `id()` đó cho object mới.

---

# 18. `is`

```text-x-trilium-auto
a = Person()

b = a
```

↓

```text-x-trilium-auto
a is b
```

↓

```text-x-trilium-auto
True
```

Vì:

Hai biến

↓

Cùng object.

---

# 19. `==`

```text-x-trilium-auto
a == b
```

↓

Mặc định

↓

So sánh identity (do `object.__eq__`).

Nếu bạn cài `__eq__()`

↓

So sánh giá trị.

---

# 20. `copy`

```text-x-trilium-auto
import copy
```

```text-x-trilium-auto
a = Person()

b = copy.copy(a)
```

↓

Object mới.

---

```text-x-trilium-auto
copy.deepcopy()
```

↓

Sao chép toàn bộ object graph.

---

# 21. Áp dụng vào hệ thống crawler

Ví dụ:

```text-x-trilium-auto
HttpClient

↓

Singleton
```

Toàn bộ hệ thống dùng chung:

- Session
- Connection Pool
- Cookie

Thay vì mỗi service tạo một client mới.

---

# 22. SQLite

```text-x-trilium-auto
Database

↓

Connection Pool

↓

Reuse
```

Thay vì:

```text-x-trilium-auto
Open

↓

Close

↓

Open

↓

Close
```

Mỗi lần truy vấn.

(Lưu ý: Với SQLite, việc dùng pool thường không cần thiết như PostgreSQL/MySQL, nhưng ý tưởng này rất quan trọng với các CSDL client-server.)

---

# 23. Crawler Worker

```text-x-trilium-auto
Worker

↓

Object Pool

↓

Reuse
```

Tiết kiệm thời gian tạo object.

---

# 24. Vòng đời Object

```text-x-trilium-auto
Person()

      │

      ▼

 __new__()

      │

      ▼

 Allocate Memory

      │

      ▼

 __init__()

      │

      ▼

 Use Object

      │

      ▼

 Garbage Collection

      │

      ▼

 __del__()
```

Lưu ý: `__del__()` **không được đảm bảo** sẽ chạy ngay trước khi bộ nhớ được giải phóng.

---

# 25. Tổng kết

```text-x-trilium-auto
           Object Lifecycle

                │

      ┌─────────┼─────────┐

      ▼         ▼         ▼

   __new__   __init__   __del__

      │

      ▼

Memory Allocation

      │

      ▼

 Initialization

      │

      ▼

 Object Ready
```

---

# Điều quan trọng nhất cần nhớ

| Method | Vai trò |
| --- | --- |
| `__new__()` | Tạo object và trả về object |
| `__init__()` | Khởi tạo object đã được tạo |
| `__del__()` | Dọn dẹp khi object bị hủy (không nên phụ thuộc) |

Một nguyên tắc rất quan trọng:

> **Nếu cần thay đổi cách object được tạo, hãy dùng** `**__new__()**`**. Nếu chỉ cần gán thuộc tính ban đầu, hãy dùng** `**__init__()**`**.**

---

# Bài tập thực hành

## Bài 1

Viết lớp `PositiveFloat(float)`:

- Kế thừa `float`.
- Override `__new__()`.
- Nếu giá trị < 0 thì chuyển thành `0.0`.

---

## Bài 2

Viết một `Singleton`:

- Chỉ tạo một instance.
- Đảm bảo logic trong `__init__()` chỉ chạy một lần.

---

## Bài 3

Viết `Color` theo Flyweight Pattern:

```text-x-trilium-auto
red1 = Color("red")
red2 = Color("red")
blue = Color("blue")
```

Kiểm tra:

```text-x-trilium-auto
red1 is red2 red1 is blue
```

Giải thích kết quả.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế:

- `HttpClient` theo Singleton.
- `WorkerPool` quản lý các `CrawlerWorker`.
- `NovelCache` theo Flyweight (cùng URL thì dùng chung một object `Novel`).

Vẽ sơ đồ mối quan hệ giữa ba thành phần này và giải thích lợi ích về hiệu năng, bộ nhớ và khả năng quản lý tài nguyên.

---

# Chuẩn bị cho Buổi 20

Buổi tiếp theo chúng ta sẽ khám phá một chủ đề được sử dụng liên tục trong các thư viện Python:

# Magic Methods (Special Methods) Deep Dive

Chúng ta sẽ tìm hiểu:

- `__repr__()`
- `__str__()`
- `__bytes__()`
- `__format__()`
- `__bool__()`
- `__len__()`
- `__iter__()`
- `__next__()`
- `__contains__()`

Sau buổi này, bạn sẽ biết cách tạo ra những class có cách sử dụng tự nhiên như các kiểu dữ liệu tích hợp sẵn của Python (`list`, `dict`, `str`,...). Đây là một trong những kỹ năng quan trọng để viết API Python "đẹp" và chuyên nghiệp.