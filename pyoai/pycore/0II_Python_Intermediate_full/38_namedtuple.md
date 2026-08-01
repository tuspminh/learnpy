# Buổi 38. NamedTuple trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu NamedTuple là gì.
> * Biết vì sao cần NamedTuple.
> * Phân biệt Tuple thường và NamedTuple.
> * Sử dụng `collections.namedtuple`.
> * Sử dụng `typing.NamedTuple`.
> * Hiểu tính bất biến (immutable).
> * Biết khi nào nên dùng NamedTuple thay Dataclass.
> * So sánh:
>
>   * Tuple
>   * NamedTuple
>   * Dataclass
>   * Class thường
> * Ứng dụng NamedTuple trong thiết kế dữ liệu nhẹ.

---

# 1. Vấn đề của Tuple thông thường

Tuple:

```python
point = (10, 20)
```

Truy cập:

```python
x = point[0]

y = point[1]
```

Vấn đề:

```python
point[0]
```

không nói lên ý nghĩa.

Người đọc phải nhớ:

```text
index 0 = x

index 1 = y
```

Với dữ liệu lớn hơn:

```python
user = (1, "Alice", 20, "admin")
```

Rất khó đọc:

```python
user[3]
```

Là gì?

* role?
* email?
* password?

---

# 2. NamedTuple là gì?

NamedTuple là một loại tuple đặc biệt:

* Có tên cho từng trường.
* Có thể truy cập bằng thuộc tính.
* Vẫn giữ đặc tính của tuple:

  * immutable.
  * nhẹ.
  * nhanh.

Ví dụ:

```python
from typing import NamedTuple


class Point(NamedTuple):
    x: int
    y: int
```

Sử dụng:

```python
p = Point(10, 20)

print(p.x)

print(p.y)
```

Output:

```text
10
20
```

---

# 3. NamedTuple kế thừa tuple

Kiểm tra:

```python
print(isinstance(p, tuple))
```

Kết quả:

```text
True
```

Nó vẫn là tuple.

---

# 4. Tính Immutable

NamedTuple không thể thay đổi.

Ví dụ:

```python
p.x = 100
```

Kết quả:

```text
AttributeError
```

---

Điều này khác Dataclass:

```python
@dataclass
class Point:
    x: int
    y: int
```

Dataclass có thể thay đổi.

---

# 5. Tạo NamedTuple bằng `typing.NamedTuple`

Cách hiện đại:

```python
from typing import NamedTuple


class User(NamedTuple):
    id: int
    name: str
    age: int
```

Sử dụng:

```python
user = User(1, "Alice", 20)
```

Truy cập:

```python
print(user.name)
```

---

# 6. Default Value

Có thể đặt giá trị mặc định:

```python
class User(NamedTuple):
    name: str
    age: int = 18
```

Sử dụng:

```python
u = User("Alice")

print(u)
```

Output:

```text
User(name='Alice', age=18)
```

---

# 7. NamedTuple bằng `collections.namedtuple`

Cách cũ:

```python
from collections import namedtuple


Point = namedtuple("Point", ["x", "y"])
```

Sử dụng:

```python
p = Point(10, 20)

print(p.x)
```

---

So sánh:

|                 | typing.NamedTuple | collections.namedtuple |
| --------------- | ----------------- | ---------------------- |
| Type Hint       | ✔                 | ✖                      |
| IDE hỗ trợ      | ✔                 | Ít                     |
| Python hiện đại | ✔                 | Cũ hơn                 |
| Khuyến nghị     | ✔                 | Chỉ dùng khi cần       |

---

# 8. NamedTuple với Type Hint

Ví dụ:

```python
class Product(NamedTuple):
    id: int
    name: str
    price: float
```

IDE hiểu:

```python
product.price
```

là:

```text
float
```

---

# 9. Chuyển NamedTuple sang tuple

```python
p = Point(10, 20)

print(tuple(p))
```

Kết quả:

```text
(10,20)
```

---

# 10. Unpacking

Vì là tuple:

```python
x, y = p
```

Kết quả:

```python
x = 10

y = 20
```

---

# 11. `_fields`

Xem danh sách trường:

```python
print(Point._fields)
```

Output:

```text
('x', 'y')
```

---

# 12. `_asdict()`

Chuyển sang dictionary:

```python
print(p._asdict())
```

Output:

```python
{"x": 10, "y": 20}
```

---

# 13. `_replace()`

Tạo bản sao mới.

```python
p2 = p._replace(x=100)
```

Kết quả:

```text
p

(10,20)


p2

(100,20)
```

Đối tượng cũ không đổi.

---

# 14. NamedTuple có phương thức không?

Có.

Ví dụ:

```python
class Point(NamedTuple):
    x: int
    y: int

    def distance(self):
        return (self.x**2 + self.y**2) ** 0.5
```

Sử dụng:

```python
p = Point(3, 4)

print(p.distance())
```

Kết quả:

```text
5.0
```

---

# 15. NamedTuple trong API Response

Ví dụ:

API trả:

```json
{
    "id":1,
    "name":"Alice",
    "active":true
}
```

Model:

```python
class UserResponse(NamedTuple):
    id: int
    name: str
    active: bool
```

---

# 16. NamedTuple trong cấu hình

Ví dụ:

```python
class DatabaseConfig(NamedTuple):
    host: str
    port: int
```

Sử dụng:

```python
config = DatabaseConfig("localhost", 3306)
```

Vì config không nên bị thay đổi.

---

# 17. NamedTuple trong Return Multiple Values

Python thường:

```python
def get_user():

    return (1, "Alice")
```

Khó đọc.

Dùng:

```python
class UserInfo(NamedTuple):
    id: int
    name: str
```

```python
def get_user():

    return UserInfo(1, "Alice")
```

Rõ ràng hơn.

---

# 18. So sánh Tuple và NamedTuple

|               | Tuple | NamedTuple |
| ------------- | ----- | ---------- |
| Immutable     | ✔     | ✔          |
| Nhẹ           | ✔     | ✔          |
| Có tên trường | ✖     | ✔          |
| Type Hint     | ✖     | ✔          |
| Dễ đọc        | Thấp  | Cao        |

---

# 19. So sánh NamedTuple và Dataclass

|                  | NamedTuple    | Dataclass |
| ---------------- | ------------- | --------- |
| Mutable          | ✖             | ✔         |
| Immutable        | ✔             | tùy chọn  |
| Bộ nhớ           | Nhỏ hơn       | Lớn hơn   |
| Method           | Có            | Có        |
| default_factory  | ✖             | ✔         |
| Validation       | Khó           | Dễ        |
| Dữ liệu phức tạp | Không phù hợp | Phù hợp   |

---

# 20. Khi nào dùng NamedTuple?

Dùng NamedTuple khi:

## ✔ Dữ liệu nhỏ

Ví dụ:

```text
Point
Coordinate
Color
Version
Range
```

---

## ✔ Dữ liệu bất biến

Ví dụ:

```text
Configuration
API Response
Database Result
```

---

## ✔ Cần hiệu năng

NamedTuple nhẹ hơn object thông thường.

---

# 21. Khi nào không nên dùng?

Không dùng cho:

* Entity có trạng thái thay đổi.
* Object nghiệp vụ phức tạp.
* Model cần validation nhiều.

Ví dụ:

```text
Order
User Account
Shopping Cart
```

Nên dùng:

* Dataclass.
* Class.

---

# 22. NamedTuple và Enum

Kết hợp:

```python
from enum import Enum
from typing import NamedTuple


class Status(Enum):
    OK = 1
    ERROR = 2


class Response(NamedTuple):
    status: Status
    message: str
```

---

# 23. NamedTuple và Pattern Matching

Python 3.10:

```python
match point:
    case Point(x, y):
        print(x, y)
```

---

# 24. Mini Project - Vector

Tạo:

```python
class Vector(NamedTuple):
    x: float
    y: float
```

Thêm:

```python
def length(self):
```

Tính độ dài vector.

Ví dụ:

```python
v = Vector(3, 4)

print(v.length())
```

Kết quả:

```text
5.0
```

---

# 25. Mini Project - Database Result

Giả lập:

```python
class UserRow(NamedTuple):
    id: int
    username: str
    email: str
```

Repository:

```python
def find_user(id: int) -> UserRow | None: ...
```

Lợi ích:

* Có type rõ ràng.
* Không thể sửa dữ liệu trả về.
* Nhẹ hơn class.

---

# 26. Mini Project - Configuration

Thiết kế:

```python
class AppConfig(NamedTuple):
    debug: bool
    host: str
    port: int
```

Yêu cầu:

* Không cho phép thay đổi config sau khi tạo.
* Có method:

```python
url()
```

Trả về:

```text
http://host:port
```

---

# Best Practices

## ✔ Dùng NamedTuple cho Value Object nhỏ

Ví dụ:

```text
Point
Money
Coordinate
Version
```

---

## ✔ Dùng Dataclass cho Domain Model

Ví dụ:

```text
User
Order
Product
Invoice
```

---

## ✔ Dùng Frozen Dataclass nếu cần immutable nhưng nhiều logic

Ví dụ:

```python
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str
```

---

## ✔ Ưu tiên `typing.NamedTuple`

Code hiện đại:

```python
class User(NamedTuple):
```

Không nên:

```python
namedtuple(...)
```

trong dự án mới.

---

# Tổng kết

Sau buổi học này bạn đã hiểu:

* NamedTuple là gì.
* NamedTuple kế thừa tuple.
* Immutable object.
* `typing.NamedTuple`.
* `collections.namedtuple`.
* Default value.
* `_fields`.
* `_asdict()`.
* `_replace()`.
* Method trong NamedTuple.
* Ứng dụng:

  * API Response.
  * Database Result.
  * Configuration.
  * Value Object.

---

# Sơ đồ lựa chọn Data Object

```
                 Data Object
                     |
        ┌────────────┼────────────┐
        │            │            │
      Tuple     NamedTuple    Dataclass
        │            │            │
    đơn giản     nhẹ + rõ    mạnh + linh hoạt
        │            │            │
    (1,2)       Point(x,y)   User(...)
```

---

# Bài tập thực hành

## Bài 1

Tạo:

```python
class Coordinate(NamedTuple):
```

gồm:

```python
x: int
y: int
z: int
```

---

## Bài 2

Tạo:

```python
class RGB(NamedTuple):
```

gồm:

```python
red
green
blue
```

Thêm method:

```python
hex()
```

Trả về:

```text
#FFFFFF
```

---

## Bài 3

Tạo:

```python
class Money(NamedTuple):
```

gồm:

```python
amount
currency
```

Thêm:

```python
format()
```

Ví dụ:

```text
100 USD
```

---

## Bài 4

So sánh cùng một mô hình:

`User`

viết bằng:

1. Tuple
2. NamedTuple
3. Dataclass
4. Class thường

Đánh giá:

* khả năng đọc.
* khả năng thay đổi.
* độ linh hoạt.

---

## Bài 5 (Thử thách)

Thiết kế một lớp `QueryResult` bằng NamedTuple:

```python
QueryResult(rows, count, execution_time)
```

Dùng để trả kết quả từ Database Repository.

Yêu cầu:

* immutable.
* có method `is_empty()`.
* có method `summary()`.

---

# Chuẩn bị cho buổi sau

Ở **Buổi 39**, chúng ta sẽ học **Pathlib**:

* Vì sao không nên lạm dụng `os.path`.
* `Path` object.
* Tạo, đọc, ghi file.
* Duyệt thư mục.
* Tìm file bằng `glob`.
* Xử lý đường dẫn đa nền tảng.
* Ứng dụng Pathlib trong project thực tế.
