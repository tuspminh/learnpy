# Buổi 37. Enum trong Python (Python Intermediate)

> **Mục tiêu buổi học**
>
> Sau buổi này bạn sẽ:
>
> * Hiểu Enum là gì và tại sao cần dùng Enum.
> * Biết sự khác nhau giữa Constant và Enum.
> * Thành thạo `Enum`.
> * Hiểu `name`, `value`.
> * Sử dụng `auto()`.
> * Biết `IntEnum`, `StrEnum`.
> * Kết hợp Enum với `match-case`.
> * Tạo Enum có phương thức và thuộc tính.
> * Ứng dụng Enum trong thiết kế phần mềm thực tế.

---

# 1. Enum là gì?

`Enum` (Enumeration) là kiểu dữ liệu đại diện cho một tập hợp **các giá trị cố định**.

Ví dụ:

Một đơn hàng có trạng thái:

```text
PENDING
PROCESSING
SHIPPED
COMPLETED
CANCELLED
```

Các giá trị này không nên thay đổi.

Enum giúp biểu diễn chúng một cách an toàn.

---

# 2. Vấn đề với Constant thông thường

Cách truyền thống:

```python
PENDING = 1
PROCESSING = 2
DONE = 3
```

Sử dụng:

```python
status = 1
```

Vấn đề:

```python
status = 1000
```

Python không biết:

* 1000 có hợp lệ không?
* Đây là trạng thái gì?

---

# 3. Enum giải quyết vấn đề

```python
from enum import Enum


class Status(Enum):
    PENDING = 1
    PROCESSING = 2
    DONE = 3
```

Sử dụng:

```python
status = Status.PENDING
```

Bây giờ:

```python
print(status)
```

Output:

```text
Status.PENDING
```

---

# 4. Enum Member

Mỗi thành phần Enum là một object.

Ví dụ:

```python
Status.PENDING
```

gọi là:

```text
Enum Member
```

---

# 5. `name` và `value`

```python
status = Status.PENDING
```

Tên:

```python
print(status.name)
```

Output:

```text
PENDING
```

Giá trị:

```python
print(status.value)
```

Output:

```text
1
```

---

# 6. So sánh Enum

```python
Status.PENDING == Status.PENDING
```

Kết quả:

```text
True
```

---

Nhưng:

```python
Status.PENDING == 1
```

Kết quả:

```text
False
```

Đây là điểm khác biệt quan trọng.

---

# 7. Duyệt Enum

```python
for status in Status:
    print(status)
```

Output:

```text
Status.PENDING
Status.PROCESSING
Status.DONE
```

---

# 8. Lấy Enum từ value

```python
status = Status(1)

print(status)
```

Output:

```text
Status.PENDING
```

---

Nếu sai:

```python
Status(100)
```

Python báo:

```text
ValueError
```

---

# 9. `auto()`

Không muốn tự đánh số:

```python
from enum import Enum, auto


class Color(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()
```

Python tự tạo:

```text
RED = 1
GREEN = 2
BLUE = 3
```

---

# 10. Tùy chỉnh giá trị Enum

```python
class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
```

Sử dụng:

```python
Role.ADMIN.value
```

Kết quả:

```text
admin
```

---

# 11. `IntEnum`

`IntEnum` hoạt động giống số nguyên.

```python
from enum import IntEnum


class Permission(IntEnum):
    READ = 1
    WRITE = 2
    DELETE = 3
```

So sánh:

```python
Permission.READ == 1
```

Kết quả:

```text
True
```

---

## Khi nào dùng IntEnum?

Khi cần tương thích với:

* Database.
* API cũ.
* Hệ thống dùng mã số.

Ví dụ:

```text
1 = Success
2 = Failed
3 = Pending
```

---

# 12. `StrEnum`

Python 3.11+

```python
from enum import StrEnum


class Environment(StrEnum):
    DEV = "development"
    PROD = "production"
```

Có thể dùng như string.

---

# 13. Enum với `match-case`

Python 3.10:

```python
def process(status):

    match status:
        case Status.PENDING:
            print("Waiting")

        case Status.DONE:
            print("Finished")
```

Sạch hơn:

```python
if status == 1:
```

---

# 14. Enum trong State Machine

Ví dụ:

```python
from enum import Enum


class OrderState(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPING = "shipping"
    DONE = "done"
```

Model:

```python
class Order:
    def __init__(self):
        self.state = OrderState.CREATED
```

Chuyển trạng thái:

```python
order.state = OrderState.PAID
```

---

# 15. Enum có phương thức

Enum không chỉ chứa dữ liệu.

Ví dụ:

```python
from enum import Enum


class Level(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def description(self):

        if self == Level.LOW:
            return "Low priority"

        if self == Level.HIGH:
            return "High priority"
```

Sử dụng:

```python
print(Level.HIGH.description())
```

Output:

```text
High priority
```

---

# 16. Enum với thuộc tính

```python
from enum import Enum


class HttpStatus(Enum):
    OK = (200, "Success")
    NOT_FOUND = (404, "Missing")

    def __init__(self, code, message):
        self.code = code
        self.message = message
```

Sử dụng:

```python
print(HttpStatus.OK.code)

print(HttpStatus.OK.message)
```

Output:

```text
200
Success
```

---

# 17. Enum trong Dataclass

Kết hợp rất phổ biến.

```python
from dataclasses import dataclass


class Role(Enum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    name: str
    role: Role
```

Sử dụng:

```python
user = User("Alice", Role.ADMIN)
```

---

# 18. Enum và JSON

Vấn đề:

```python
import json

json.dumps(Status.PENDING)
```

Không chạy như mong muốn.

Cần:

```python
json.dumps(Status.PENDING.value)
```

Kết quả:

```json
1
```

---

# 19. Enum với API

Ví dụ API trả:

```json
{
    "status": "success"
}
```

Model:

```python
from enum import StrEnum


class ResponseStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
```

---

# 20. Enum với Database

Ví dụ:

Database:

```
orders

id | status
------------
1  | paid
2  | done
```

Python:

```python
class OrderStatus(StrEnum):
    PAID = "paid"
    DONE = "done"
```

Tránh dùng:

```python
if status == "paid":
```

nhiều nơi trong code.

---

# 21. Enum Alias

```python
class Color(Enum):
    RED = 1
    ERROR = 1
```

Ở đây:

```python
Color.ERROR
```

là alias của:

```python
Color.RED
```

---

# 22. So sánh Enum và Constant

|                     | Constant | Enum        |
| ------------------- | -------- | ----------- |
| An toàn kiểu        | ❌        | ✔           |
| IDE hỗ trợ          | Ít       | Tốt         |
| Không trùng giá trị | ❌        | ✔           |
| Có phương thức      | ❌        | ✔           |
| Dùng trong state    | Khó      | Rất phù hợp |

---

# 23. Best Practices

## ✔ Dùng Enum cho tập giá trị cố định

Ví dụ:

* Status.
* Role.
* Permission.
* Type.
* Category.

---

## ✔ Không dùng Enum cho dữ liệu thay đổi

Sai:

```text
Danh sách user
Danh sách sản phẩm
```

Đây là dữ liệu động.

---

## ✔ Dùng StrEnum cho API

Ví dụ:

```python
class Status(StrEnum):
    ACTIVE = "active"
```

Dễ serialize JSON.

---

## ✔ Dùng IntEnum khi làm việc với hệ thống cũ

Ví dụ:

* Legacy database.
* Protocol.
* Hardware code.

---

# 24. Mini Project - Order System

Thiết kế:

```text
order/

├── status.py
├── order.py
└── main.py
```

---

## status.py

```python
from enum import StrEnum


class OrderStatus(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    DONE = "done"
```

---

## order.py

```python
from dataclasses import dataclass
from status import OrderStatus


@dataclass
class Order:
    id: int
    status: OrderStatus
```

---

## main.py

```python
order = Order(1, OrderStatus.NEW)


print(order)
```

---

# 25. Mini Project - Permission System

Yêu cầu:

Tạo:

```python
class Permission(Enum):
```

Có:

```
READ
WRITE
DELETE
```

Tạo:

```python
class User:
```

Có:

```python
permissions: set[Permission]
```

Kiểm tra:

```python
if Permission.DELETE in user.permissions:
    ...
```

---

# Tổng kết

Sau buổi học này bạn đã hiểu:

* Enum là gì.
* Vì sao dùng Enum.
* Enum Member.
* `name`, `value`.
* `auto()`.
* `IntEnum`.
* `StrEnum`.
* Enum với `match-case`.
* Enum có phương thức.
* Enum có thuộc tính.
* Enum trong Dataclass.
* Enum trong API, Database, State Machine.

---

# Sơ đồ Enum

```
              Enum
                |
    ┌───────────┼───────────┐
    │           │           │
 Constant    Behavior    Safety
    │           │           │
 value      method       type check
    │
 ┌──┴─────┐
 │        │
IntEnum  StrEnum
```

---

# Bài tập thực hành

## Bài 1

Tạo:

```python
class WeekDay(Enum)
```

gồm:

```
MONDAY
TUESDAY
...
SUNDAY
```

Dùng `auto()`.

---

## Bài 2

Tạo:

```python
class UserRole(StrEnum)
```

gồm:

```
ADMIN
EDITOR
VIEWER
```

---

## Bài 3

Tạo:

```python
class PaymentStatus(Enum)
```

có:

```
PENDING
SUCCESS
FAILED
```

Thêm method:

```python
is_finished()
```

---

## Bài 4

Tạo HTTP Status Enum:

```python
OK = (200, "OK")

NOT_FOUND = (404, "Not Found")
```

Có:

```python
.code

.message
```

---

## Bài 5

Xây dựng State Machine cho đơn hàng:

Trạng thái:

```
CREATED
PAID
SHIPPED
COMPLETED
CANCELLED
```

Chỉ cho phép chuyển:

```
CREATED
    |
    v
PAID
    |
    v
SHIPPED
    |
    v
COMPLETED
```

Không cho:

```
COMPLETED -> PAID
```

---

# Chuẩn bị cho buổi sau

Ở **Buổi 38**, chúng ta sẽ học **NamedTuple**:

* NamedTuple là gì.
* Khác nhau giữa tuple thường và NamedTuple.
* `typing.NamedTuple`.
* Immutable Data Object.
* Khi nào dùng NamedTuple thay Dataclass.
* NamedTuple trong API, cấu trúc dữ liệu nhẹ.
* So sánh:

  * Tuple
  * NamedTuple
  * Dataclass
  * Class thường.
