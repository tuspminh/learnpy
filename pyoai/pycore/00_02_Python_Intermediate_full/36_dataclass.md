# Buổi 36. Dataclass trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu vì sao cần `@dataclass`.
> * Thành thạo cách sử dụng `@dataclass`.
> * Hiểu các tham số: `init`, `repr`, `eq`, `order`, `frozen`, `slots`.
> * Biết sử dụng `field()`.
> * Thành thạo `default_factory`.
> * Hiểu `__post_init__()`.
> * Biết dùng `asdict()`, `astuple()`, `replace()`.
> * So sánh Dataclass với Class thường và NamedTuple.
> * Áp dụng Dataclass trong các dự án Python.

---

# 1. Dataclass là gì?

`dataclass` là module giúp tạo các lớp **chủ yếu dùng để chứa dữ liệu** (data container) mà không phải viết nhiều mã lặp.

Ví dụ, thay vì:

```python
class Student:
    def __init__(self, id, name, score):
        self.id = id
        self.name = name
        self.score = score

    def __repr__(self):
        return f"Student(id={self.id}, name={self.name}, score={self.score})"

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.name == other.name
            and self.score == other.score
        )
```

Ta chỉ cần:

```python
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    score: float
```

Python sẽ tự sinh:

* `__init__()`
* `__repr__()`
* `__eq__()`

---

# 2. Dataclass hoạt động như thế nào?

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str
    age: int
```

Sử dụng:

```python
u = User("Alice", 20)

print(u)
```

Output:

```text
User(name='Alice', age=20)
```

Không cần tự viết `__repr__()`.

---

# 3. Các phương thức được tạo tự động

Mặc định:

```python
@dataclass
class User: ...
```

Python tạo:

```text
✔ __init__()

✔ __repr__()

✔ __eq__()
```

Nếu yêu cầu thêm:

```python
@dataclass(order=True)
```

Python còn tạo:

```text
__lt__()

__le__()

__gt__()

__ge__()
```

---

# 4. `repr=False`

```python
from dataclasses import dataclass


@dataclass(repr=False)
class User:
    name: str
```

Khi đó:

```python
print(User("Alice"))
```

↓

```text
<__main__.User object at ...>
```

---

# 5. `eq=False`

```python
@dataclass(eq=False)
class User:
    name: str
```

So sánh:

```python
User("A") == User("A")
```

↓

```text
False
```

Vì quay về so sánh theo địa chỉ bộ nhớ.

---

# 6. `order=True`

```python
from dataclasses import dataclass


@dataclass(order=True)
class Product:
    price: float
```

```python
a = Product(100)

b = Product(200)

print(a < b)
```

↓

```text
True
```

Thứ tự so sánh dựa trên **thứ tự khai báo các trường**.

---

# 7. `frozen=True`

Đối tượng trở thành **bất biến**.

```python
@dataclass(frozen=True)
class Config:
    host: str
```

```python
cfg = Config("localhost")

cfg.host = "127.0.0.1"
```

↓

```text
FrozenInstanceError
```

---

# 8. `slots=True`

```python
@dataclass(slots=True)
class User:
    name: str
    age: int
```

Ưu điểm:

* Giảm bộ nhớ.
* Truy cập thuộc tính nhanh hơn.
* Không cho phép thêm thuộc tính mới ngoài những trường đã khai báo.

Ví dụ:

```python
u = User("Alice", 20)

u.email = "a@example.com"
```

↓

```text
AttributeError
```

---

# 9. Giá trị mặc định

```python
@dataclass
class User:
    name: str
    age: int = 18
```

```python
User("Alice")
```

↓

```text
User(name='Alice', age=18)
```

---

# 10. `field()`

```python
from dataclasses import field


@dataclass
class User:
    name: str
    age: int = field(default=18)
```

`field()` dùng để cấu hình chi tiết từng trường.

---

# 11. `default_factory`

Sai:

```python
@dataclass
class Student:
    scores: list[int] = []
```

Lỗi:

```text
ValueError
mutable default ...
```

Đúng:

```python
from dataclasses import field


@dataclass
class Student:
    scores: list[int] = field(default_factory=list)
```

Mỗi đối tượng sẽ có một danh sách riêng.

---

# 12. Vì sao cần `default_factory`?

Nếu dùng:

```python
scores = []
```

Tất cả đối tượng sẽ dùng chung một danh sách.

```text
Student A
        │
        ├────► []
        │
Student B
```

`default_factory` tạo danh sách mới cho mỗi đối tượng.

---

# 13. `__post_init__()`

Được gọi ngay sau `__init__()`.

```python
from dataclasses import dataclass


@dataclass
class Rectangle:
    width: float
    height: float

    def __post_init__(self):
        self.area = self.width * self.height
```

```python
r = Rectangle(3, 4)

print(r.area)
```

↓

```text
12
```

---

# 14. Kiểm tra dữ liệu

```python
@dataclass
class Student:
    score: float

    def __post_init__(self):

        if not 0 <= self.score <= 10:
            raise ValueError("Invalid score")
```

---

# 15. `asdict()`

```python
from dataclasses import asdict

u = User("Alice", 20)

print(asdict(u))
```

↓

```text
{
    'name': 'Alice',
    'age': 20
}
```

Rất hữu ích khi chuyển sang JSON.

---

# 16. `astuple()`

```python
from dataclasses import astuple

u = User("Alice", 20)

print(astuple(u))
```

↓

```text
('Alice', 20)
```

---

# 17. `replace()`

```python
from dataclasses import replace

u1 = User("Alice", 20)

u2 = replace(u1, age=21)
```

`u1` không thay đổi.

`u2` là đối tượng mới.

---

# 18. `compare=False`

```python
from dataclasses import field


@dataclass
class User:
    id: int
    cache: dict = field(default_factory=dict, compare=False)
```

`cache` sẽ không được dùng khi so sánh hai đối tượng.

---

# 19. `repr=False`

Ẩn thông tin nhạy cảm.

```python
@dataclass
class Account:
    username: str
    password: str = field(repr=False)
```

```python
print(Account("admin", "123"))
```

↓

```text
Account(username='admin')
```

---

# 20. Kế thừa Dataclass

```python
from dataclasses import dataclass


@dataclass
class Person:
    name: str


@dataclass
class Student(Person):
    score: float
```

```python
s = Student("Alice", 9.5)
```

---

# 21. Dataclass và Class thường

Class thường:

```python
class User: ...
```

Bạn phải tự viết:

* `__init__`
* `__repr__`
* `__eq__`

Dataclass:

```python
@dataclass
class User: ...
```

Python sinh tự động.

---

# 22. Dataclass và NamedTuple

| Dataclass                | NamedTuple        |
| ------------------------ | ----------------- |
| Có thể thay đổi          | Mặc định bất biến |
| Hỗ trợ `__post_init__()` | Không             |
| Hỗ trợ `default_factory` | Không             |
| Dễ mở rộng               | Ít linh hoạt      |

Nếu đối tượng cần thay đổi trạng thái, Dataclass thường phù hợp hơn.

---

# 23. Best Practices

## ✔ Dùng Dataclass cho Model dữ liệu

Ví dụ:

* User
* Book
* Student
* Product
* Config
* DTO

---

## ✔ Dùng `slots=True`

Khi tạo nhiều đối tượng để tiết kiệm bộ nhớ.

---

## ✔ Dùng `frozen=True`

Cho:

* Config
* Value Object
* Dữ liệu bất biến

---

## ✔ Dùng `default_factory`

Cho:

* `list`
* `dict`
* `set`

Không dùng trực tiếp giá trị mặc định có thể thay đổi.

---

## ✔ Dùng `__post_init__()`

Để:

* kiểm tra dữ liệu,
* tính toán thuộc tính phụ,
* chuẩn hóa dữ liệu.

---

# 24. Mini Project - Book Model

```python
from dataclasses import dataclass


@dataclass(slots=True)
class Book:
    id: int
    title: str
    author: str
    price: float
```

Sử dụng:

```python
book = Book(1, "Python", "David", 25.5)

print(book)
```

---

# 25. Mini Project - Configuration

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Config:
    host: str
    port: int
```

```python
cfg = Config("localhost", 3306)
```

Đối tượng này phù hợp để lưu cấu hình vì không thể bị sửa đổi sau khi tạo.

---

# Tổng kết

Sau buổi học này, bạn đã nắm được:

* `@dataclass`.
* `field()`.
* `default_factory`.
* `__post_init__()`.
* `repr`, `eq`, `order`, `frozen`, `slots`.
* `asdict()`.
* `astuple()`.
* `replace()`.
* Kế thừa Dataclass.
* So sánh Dataclass với Class thường và NamedTuple.

---

# Sơ đồ Dataclass

```text
                 @dataclass
                      │
      ┌───────────────┼───────────────┐
      │               │               │
   __init__()     __repr__()      __eq__()
      │
      ├───────────────┐
      │               │
 default_factory   __post_init__()
      │               │
      └───────────────┘
              │
      asdict() / astuple()
              │
          replace()
```

---

# Bài tập thực hành

### Bài 1

Tạo `Employee` bằng `@dataclass` gồm:

* `id`
* `name`
* `salary`

In đối tượng để kiểm tra `__repr__()` được sinh tự động.

---

### Bài 2

Viết `Student` có:

```python
scores: list[float]
```

Sử dụng `default_factory=list`.

---

### Bài 3

Tạo `Rectangle` với:

* `width`
* `height`

Dùng `__post_init__()` để tính thuộc tính `area`.

---

### Bài 4

Tạo `Config` với:

```python
@dataclass(frozen=True, slots=True)
```

Thử thay đổi thuộc tính sau khi tạo và quan sát ngoại lệ.

---

### Bài 5

Dùng `replace()` để tạo bản sao của một `Book` với giá mới mà không làm thay đổi đối tượng ban đầu.

---

### Bài 6 (Thử thách)

Xây dựng mô hình cho một ứng dụng quản lý thư viện:

* `Author`
* `Book`
* `Category`
* `BorrowRecord`

Yêu cầu:

* Sử dụng `@dataclass`.
* Có `default_factory` cho các trường kiểu danh sách.
* Có `__post_init__()` để kiểm tra dữ liệu (ví dụ: giá sách không âm, tên không rỗng).
* Dùng `slots=True` cho các lớp tạo nhiều đối tượng.
* Dùng `frozen=True` cho các lớp bất biến như `Category` nếu phù hợp.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 37**, chúng ta sẽ học **Enum** trong Python Intermediate, bao gồm:

* Vì sao cần `Enum`.
* `Enum`, `IntEnum`, `StrEnum` (Python 3.11+).
* `auto()`.
* So sánh Enum với hằng số thông thường.
* Enum trong `match-case`.
* Thuộc tính `name`, `value`.
* Tùy biến Enum với phương thức và thuộc tính.
* Ứng dụng trong trạng thái (State), quyền (Role), loại dữ liệu (Type) và cấu hình.
