# Dataclass Deep Dive - Buổi 5

# Frozen Dataclass Deep Dive (Immutable Objects)

> Đây là một trong những tính năng mạnh nhất của `dataclass`.

Rất nhiều framework lớn như **Pydantic**, **attrs**, **SQLAlchemy**, **TensorFlow**, **PyTorch**, **LangChain**... đều có khái niệm **immutable object**.

Nếu hiểu rõ `frozen=True`, bạn sẽ hiểu:

- Value Object trong Domain Driven Design (DDD)
- Thread-safe object
- Cache key
- Functional Programming
- Hashable Object

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Immutable là gì?
- `frozen=True` hoạt động như thế nào?
- Python ngăn sửa dữ liệu bằng cách nào?
- `object.__setattr__()` là gì?
- `dataclasses.replace()`
- Quan hệ giữa `frozen` và `__hash__`
- Khi nào nên dùng và không nên dùng

---

# 1. Mutable và Immutable

Trong Python có hai nhóm đối tượng.

## Mutable (có thể thay đổi)

Ví dụ

```text-x-trilium-auto
numbers = [1, 2, 3]

numbers.append(4)

print(numbers)
```

Kết quả

```text-x-trilium-auto
[1, 2, 3, 4]
```

List thay đổi được.

---

Dictionary

```text-x-trilium-auto
config = {
    "host": "localhost"
}

config["host"] = "127.0.0.1"
```

---

Set

```text-x-trilium-auto
tags = {"python"}

tags.add("sqlite")
```

---

## Immutable (không thay đổi)

Ví dụ

```text-x-trilium-auto
name = "Python"

name += "3"
```

Thực tế Python **không sửa chuỗi cũ**.

Nó tạo chuỗi mới.

---

Tuple

```text-x-trilium-auto
point = (10,20)
```

Không sửa được

```text-x-trilium-auto
point[0] = 5
```

Lỗi.

---

# 2. Mutable Object có vấn đề gì?

Ví dụ

```text-x-trilium-auto
class Config:

    def __init__(self):

        self.host = "localhost"
```

Ở đâu đó

```text-x-trilium-auto
config.host = "abc"
```

Có thể vô tình làm hỏng toàn bộ chương trình.

Trong hệ thống lớn

```text-x-trilium-auto
Database

↓

Config

↓

100 module cùng dùng
```

Nếu một module sửa Config

↓

99 module còn lại bị ảnh hưởng.

---

# 3. Ý tưởng của Frozen Dataclass

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:

    host: str

    port: int
```

Tạo

```text-x-trilium-auto
config = Config("localhost",3306)
```

---

Muốn sửa

```text-x-trilium-auto
config.host = "abc"
```

Kết quả

```text-x-trilium-auto
FrozenInstanceError:
cannot assign to field 'host'
```

Object trở thành **bất biến (immutable)** sau khi khởi tạo.

---

# 4. Frozen hoạt động như thế nào?

Nhiều người nghĩ

Python khóa bộ nhớ.

Không.

Dataclass chỉ sinh thêm

```text-x-trilium-auto
__setattr__()

__delattr__()
```

---

Bình thường

```text-x-trilium-auto
student.name = "Tom"
```

Python gọi

```text-x-trilium-auto
student.__setattr__(
    "name",
    "Tom"
)
```

---

Frozen Dataclass sinh gần giống

```text-x-trilium-auto
def __setattr__(self, name, value):

    raise FrozenInstanceError(...)
```

Thế là không sửa được.

---

# 5. Thử nghiệm

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(frozen=True)
class User:

    name: str
```

```text-x-trilium-auto
u = User("Alice")

u.name = "Bob"
```

Kết quả

```text-x-trilium-auto
FrozenInstanceError
```

---

Ngay cả xóa

```text-x-trilium-auto
del u.name
```

cũng lỗi.

---

# 6. Nhưng **init** vẫn gán được?

Đây là câu hỏi rất hay.

Nếu

```text-x-trilium-auto
__setattr__()
```

bị khóa

thì

```text-x-trilium-auto
__init__()
```

làm sao gán

```text-x-trilium-auto
self.name = ...
```

được?

---

Đáp án:

Dataclass sinh constructor như sau (giản lược):

```text-x-trilium-auto
def __init__(self, name):

    object.__setattr__(
        self,
        "name",
        name
    )
```

Không dùng

```text-x-trilium-auto
self.name = name
```

mà dùng

```text-x-trilium-auto
object.__setattr__()
```

để bỏ qua phiên bản `__setattr__` đã bị ghi đè.

---

# 7. object.**setattr**()

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(frozen=True)
class User:

    name: str
```

```text-x-trilium-auto
u = User("Alice")
```

Có thể "phá khóa"

```text-x-trilium-auto
object.__setattr__(
    u,
    "name",
    "Bob"
)

print(u)
```

Kết quả

```text-x-trilium-auto
User(name='Bob')
```

Đây là lý do `frozen=True` **không phải là cơ chế bảo mật**, mà là cơ chế giúp tránh sửa đổi ngoài ý muốn.

---

# 8. replace()

Giả sử

```text-x-trilium-auto
config = Config(
    "localhost",
    3306
)
```

Muốn đổi port.

Không sửa được.

Cách đúng

```text-x-trilium-auto
from dataclasses import replace

new_config = replace(
    config,
    port=5432
)
```

Kết quả

```text-x-trilium-auto
Config(host='localhost', port=5432)
```

Object cũ vẫn giữ nguyên.

---

Minh họa

```text-x-trilium-auto
config
 │
 ▼
(host=localhost,3306)

replace()

        ↓

new_config
 │
 ▼
(host=localhost,5432)
```

---

# 9. Vì sao replace() quan trọng?

Trong Functional Programming

không sửa object

↓

luôn tạo object mới.

Ưu điểm

- dễ debug
- undo/redo
- thread-safe
- không có side effect

---

# 10. Frozen và Hash

Ví dụ

```text-x-trilium-auto
@dataclass(frozen=True)
class User:

    id:int

    name:str
```

Ta có thể

```text-x-trilium-auto
users = {
    User(1,"Alice")
}
```

Hoặc

```text-x-trilium-auto
cache = {

User(1,"Alice"):100

}
```

Được.

---

Nếu object thay đổi được

```text-x-trilium-auto
user.id = 999
```

thì hash sẽ thay đổi.

Dictionary sẽ hỏng.

Vì vậy Python chỉ tự sinh `__hash__` khi đối tượng phù hợp để dùng làm khóa.

---

# 11. Value Object

DDD

Ví dụ

```text-x-trilium-auto
Money
```

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:

    amount:int

    currency:str
```

100 USD

không nên đổi thành

500 USD

sau khi tạo.

Muốn thay đổi

↓

tạo object mới.

---

Địa chỉ

```text-x-trilium-auto
Address
```

```text-x-trilium-auto
@dataclass(frozen=True)
class Address:

    city:str

    street:str
```

Một địa chỉ cụ thể nên là giá trị bất biến.

---

# 12. Config Object

Đây là ứng dụng phổ biến nhất.

```text-x-trilium-auto
@dataclass(frozen=True)
class DatabaseConfig:

    host:str

    port:int

    username:str

    password:str
```

Khởi động chương trình

↓

không ai được sửa config.

---

# 13. Thread-safe

Ví dụ

```text-x-trilium-auto
Thread A

↓

Config

↑

Thread B
```

Nếu Config thay đổi

↓

race condition.

Nếu Frozen

↓

không ai sửa được.

Đọc đồng thời an toàn hơn vì không có trạng thái bị thay đổi.

---

# 14. Crawler Project

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(frozen=True)
class CrawlRequest:

    novel_url:str

    chapter:int

    force:bool=False
```

Worker chỉ đọc.

Không sửa request.

Rất an toàn.

---

# 15. Khi nào không nên dùng Frozen?

Ví dụ

```text-x-trilium-auto
@dataclass class DownloadTask:

    progress:int

    status:str
```

Progress

```text-x-trilium-auto
0%

↓

10%

↓

50%

↓

100%
```

Luôn thay đổi.

Không nên Frozen.

---

User Session

```text-x-trilium-auto
last_login

token

expire
```

Luôn cập nhật.

Không Frozen.

---

# 16. So sánh Mutable và Frozen

```text-x-trilium-auto
@dataclass class User:

    name:str
```

```text-x-trilium-auto
u.name="Bob"
```

Được.

---

```text-x-trilium-auto
@dataclass(frozen=True)
class User:

    name:str
```

```text-x-trilium-auto
u.name="Bob"
```

Lỗi.

---

# 17. replace() trong thực tế

```text-x-trilium-auto
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Chapter:

    id:int

    title:str

    downloaded:bool=False
```

Ban đầu

```text-x-trilium-auto
chapter = Chapter(
    1,
    "Chương 1"
)
```

Sau khi tải xong

```text-x-trilium-auto
chapter2 = replace(
    chapter,
    downloaded=True
)
```

Ta có

```text-x-trilium-auto
chapter

↓

downloaded=False

-------------------

chapter2

↓

downloaded=True
```

Không làm thay đổi đối tượng ban đầu.

---

# Tổng kết

| Tính năng | Ý nghĩa |
| --- | --- |
| `frozen=True` | Đối tượng bất biến sau khi khởi tạo |
| `FrozenInstanceError` | Lỗi khi cố sửa field |
| `object.__setattr__()` | Cách dataclass khởi tạo field và cũng có thể bỏ qua cơ chế khóa |
| `replace()` | Tạo bản sao với một số field thay đổi |
| `__hash__` | Thường được tự sinh khi đối tượng là immutable và có thể dùng làm khóa |
| Thread-safe | Đọc đồng thời an toàn hơn |
| Value Object | Rất phù hợp với `frozen=True` |

---

# Bài tập thực hành

## Bài 1

Tạo dataclass:

```text-x-trilium-auto
@dataclass(frozen=True)
class Point:
    x: int
    y: int
```

- Tạo một đối tượng.
- Thử sửa `x`.
- Quan sát lỗi.

---

## Bài 2

Dùng `replace()`:

```text-x-trilium-auto
Point(10,20)
```

Tạo một đối tượng mới có:

```text-x-trilium-auto
x = 100
```

Giữ nguyên `y`.

---

## Bài 3

Thiết kế Value Object cho dự án crawler:

```text-x-trilium-auto
@dataclass(frozen=True)
class NovelId:
    source: str
    novel_id: str
```

Ví dụ:

```text-x-trilium-auto
NovelId(
    source="truyenfull",
    novel_id="tien-nghich"
)
```

Thử:

- Đưa `NovelId` vào `set`.
- Dùng `NovelId` làm key của `dict`.
- Tạo một `NovelId` khác có cùng dữ liệu và kiểm tra xem chúng có được coi là cùng một khóa hay không.

---

# Chuẩn bị cho Buổi 6

Buổi tiếp theo chúng ta sẽ học **Ordering Deep Dive (**`**order=True**`**)**.

Đây là chủ đề giúp dataclass tự sinh các toán tử:

- `__lt__` (`<`)
- `__le__` (`<=`)
- `__gt__` (`>`)
- `__ge__` (`>=`)

Chúng ta sẽ tìm hiểu:

- Python sinh các phép so sánh theo quy tắc nào.
- So sánh theo thứ tự field ra sao.
- Kết hợp `compare=False`.
- Sắp xếp (`sorted`, `list.sort`) danh sách dataclass.
- Khi nào **không nên** dùng `order=True` và nên tự định nghĩa quy tắc sắp xếp. Đây là kiến thức rất hữu ích khi làm việc với danh sách model trong các ứng dụng thực tế.