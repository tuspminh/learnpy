# Dataclass Deep Dive — Buổi 10

# `__post_init__()` Deep Dive

Hôm nay ta quay lại **đúng roadmap**.

Ở các buổi trước, bạn đã biết `__post_init__()` tồn tại. Nhưng từ buổi này chúng ta sẽ nhìn nó dưới góc độ **thiết kế object**, không chỉ là một hook đơn giản.

Roadmap yêu cầu 4 chủ đề:

1. Validation
2. Computed Field
3. Dependency Injection
4. Lazy Initialization

---

# 1. `__post_init__()` thực chất là gì?

Khi dùng:

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

    def __post_init__(self):
        print("POST INIT")
```

Dataclass sinh ra `__init__()` gần giống:

```python
def __init__(self, name: str, age: int):
    self.name = name
    self.age = age
    self.__post_init__()
```

Do đó:

```python
user = User("Alice", 20)
```

luồng thực thi là:

```text
User(...)
   │
   ▼
__init__()
   │
   ├── self.name = ...
   ├── self.age = ...
   │
   ▼
__post_init__()
```

Điểm quan trọng:

> `__post_init__()` chạy **sau khi tất cả field đã được gán**.

---

# 2. `__post_init__()` không phải constructor

Đây là một phân biệt quan trọng.

Bạn có:

```python
@dataclass
class User:

    name: str
    age: int

    def __post_init__(self):
        ...
```

Thì constructor thực sự là:

```python
__init__()
```

Còn:

```python
__post_init__()
```

là **hook sau khởi tạo**.

---

# 3. Vì sao cần `__post_init__()`?

Dataclass rất giỏi trong việc:

```text
nhận dữ liệu
      ↓
gán field
      ↓
tạo object
```

Nhưng đôi khi ta cần:

```text
nhận dữ liệu
      ↓
gán field
      ↓
kiểm tra
      ↓
chuẩn hóa
      ↓
tính toán
      ↓
tạo trạng thái hoàn chỉnh
```

Phần sau đó chính là nơi `__post_init__()` rất hữu ích.

---

# Phần I — Validation

# 4. Validation đơn giản

Ví dụ:

```python
from dataclasses import dataclass

@dataclass
class User:

    name: str
    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("age must be >= 0")
```

Bây giờ:

```python
User("Alice", 20)
```

hợp lệ.

Nhưng:

```python
User("Alice", -10)
```

sẽ:

```text
ValueError: age must be >= 0
```

---

# 5. Validation nhiều field

```python
@dataclass
class User:

    username: str
    age: int
    email: str

    def __post_init__(self):

        if not self.username:
            raise ValueError(
                "username cannot be empty"
            )

        if self.age < 0:
            raise ValueError(
                "age cannot be negative"
            )

        if "@" not in self.email:
            raise ValueError(
                "invalid email"
            )
```

Object chỉ được tạo nếu trạng thái hợp lệ.

Đây là một nguyên tắc rất quan trọng:

> **Không để object tồn tại ở trạng thái không hợp lệ.**

---

# 6. Validation và Type Hint

Một lỗi phổ biến:

```python
@dataclass
class User:
    age: int
```

Nhiều người tưởng Python tự kiểm tra:

```python
User("Alice", "abc")
```

Không.

Type hint:

```python
age: int
```

không tự tạo runtime validation.

Bạn có thể nhận:

```python
User("Alice", "abc")
```

Nếu muốn kiểm tra:

```python
def __post_init__(self):
    if not isinstance(self.age, int):
        raise TypeError("age must be int")
```

---

# 7. Validation nhiều tầng

Một cách tốt hơn:

```python
@dataclass
class User:

    username: str
    age: int

    def __post_init__(self):

        self._validate_username()
        self._validate_age()

    def _validate_username(self):
        if not self.username:
            raise ValueError(
                "username cannot be empty"
            )

    def _validate_age(self):
        if self.age < 0:
            raise ValueError(
                "age cannot be negative"
            )
```

Lợi ích:

* `__post_init__()` ngắn.
* Validation dễ test.
* Logic được tách nhỏ.

---

# 8. Chuẩn hóa dữ liệu

`__post_init__()` không chỉ dùng để reject dữ liệu.

Nó còn có thể **normalize**.

Ví dụ:

```python
@dataclass
class User:

    username: str

    def __post_init__(self):
        self.username = self.username.strip().lower()
```

```python
user = User("  Alice  ")
```

Kết quả:

```python
user.username
```

```text
alice
```

---

# 9. Validation + Normalization

Một model tốt thường:

```text
Input
  │
  ▼
Normalize
  │
  ▼
Validate
  │
  ▼
Valid Object
```

Ví dụ:

```python
@dataclass
class Chapter:

    title: str
    url: str

    def __post_init__(self):
        self.title = self.title.strip()
        self.url = self.url.strip()

        if not self.title:
            raise ValueError(
                "title cannot be empty"
            )

        if not self.url.startswith("http"):
            raise ValueError(
                "invalid URL"
            )
```

---

# Phần II — Computed Field

# 10. Computed Field là gì?

Đây là field được **tính từ các field khác**.

Ví dụ:

```text
first_name
last_name

      ↓

full_name
```

---

# 11. Ví dụ

```python
from dataclasses import dataclass, field

@dataclass
class User:

    first_name: str
    last_name: str

    full_name: str = field(init=False)

    def __post_init__(self):
        self.full_name = (
            f"{self.first_name} "
            f"{self.last_name}"
        )
```

Sử dụng:

```python
user = User(
    "John",
    "Smith"
)
```

Kết quả:

```python
user.full_name
```

```text
John Smith
```

---

# 12. Tại sao `init=False`?

Nếu không có:

```python
init=False
```

dataclass sẽ đưa `full_name` vào constructor.

Không mong muốn:

```python
User(
    "John",
    "Smith",
    "John Smith"
)
```

Ta muốn:

```python
User(
    "John",
    "Smith"
)
```

Sau đó:

```text
__post_init__()
      ↓
full_name được tính
```

---

# 13. Computed Field trong crawler

Ví dụ:

```python
@dataclass
class Chapter:

    novel_id: int
    index: int
    title: str

    chapter_key: str = field(init=False)

    def __post_init__(self):
        self.chapter_key = (
            f"{self.novel_id}:{self.index}"
        )
```

Ví dụ:

```python
chapter = Chapter(
    novel_id=100,
    index=5,
    title="Chương 5"
)
```

Tự động có:

```text
chapter_key = "100:5"
```

---

# 14. Computed Field có thể phụ thuộc nhiều field

```python
@dataclass
class Product:

    price: float
    quantity: int

    total: float = field(init=False)

    def __post_init__(self):
        self.total = (
            self.price * self.quantity
        )
```

```python
product = Product(100, 3)

print(product.total)
```

```text
300
```

---

# 15. Computed Field và `repr`

Mặc định:

```python
@dataclass
class Product:
    ...
```

`total` vẫn xuất hiện trong `repr()`.

Nếu không muốn:

```python
total: float = field(
    init=False,
    repr=False
)
```

---

# 16. Computed Field và `compare`

Đôi khi computed field không nên tham gia equality.

Ví dụ:

```python
total: float = field(
    init=False,
    compare=False
)
```

Lúc này:

```python
Product(100, 2)
```

và một object khác có cùng:

```text
price
quantity
```

vẫn được xem xét equality mà không phụ thuộc `total`.

---

# Phần III — Dependency Injection

# 17. Dependency Injection là gì?

Giả sử:

```python
Chapter
```

cần một parser.

Một cách không tốt:

```python
@dataclass
class Chapter:

    title: str

    def parse(self):
        parser = MyParser()
        ...
```

`Chapter` tự tạo dependency.

Điều này làm object:

* khó test,
* phụ thuộc cứng,
* khó thay thế implementation.

---

# 18. Dependency Injection

Thay vì:

```text
Chapter
   │
   └── tự tạo Parser
```

ta làm:

```text
Parser
   │
   ▼
Chapter
```

Dependency được **inject từ bên ngoài**.

---

# 19. Dùng `InitVar`

Đây là nơi `InitVar` của Buổi 9 kết hợp với `__post_init__()`.

```python
from dataclasses import dataclass, InitVar

@dataclass
class Chapter:

    title: str

    parser: InitVar[object]

    content: str = ""

    def __post_init__(self, parser):
        self.content = parser.parse(
            self.title
        )
```

`parser`:

* được truyền vào constructor,
* được sử dụng trong `__post_init__()`,
* không được lưu thành field.

---

# 20. Test dễ hơn

Ta có:

```python
class FakeParser:

    def parse(self, title):
        return f"CONTENT: {title}"
```

Test:

```python
chapter = Chapter(
    "Chapter 1",
    FakeParser()
)
```

Không cần parser thật.

Đây là một trong những lợi ích lớn nhất của Dependency Injection:

> **Dependency có thể thay thế trong test.**

---

# 21. Nhưng có nên dùng DI trong mọi Dataclass?

Không.

Ví dụ:

```python
@dataclass
class Chapter:
    title: str
    url: str
    content: str
```

Nếu Chapter chỉ là dữ liệu thì không cần parser.

Nên:

```text
Chapter
   ↑
ChapterParser
```

thay vì:

```text
Chapter
   └── Parser
```

Nói cách khác:

> Đừng biến dataclass thành service container.

---

# Phần IV — Lazy Initialization

# 22. Lazy Initialization là gì?

Thay vì tạo dữ liệu ngay:

```text
Object được tạo
      ↓
Tạo resource ngay
```

ta trì hoãn:

```text
Object được tạo
      ↓
Chưa tạo resource
      ↓
Khi cần mới tạo
```

Ví dụ:

* database connection,
* HTTP session,
* cache,
* file,
* expensive computation.

---

# 23. Một ví dụ đơn giản

```python
@dataclass
class User:

    name: str

    _normalized_name: str | None = field(
        init=False,
        default=None
    )

    @property
    def normalized_name(self):
        if self._normalized_name is None:
            self._normalized_name = (
                self.name.strip().lower()
            )

        return self._normalized_name
```

Ban đầu:

```text
_normalized_name = None
```

Khi gọi:

```python
user.normalized_name
```

mới tính.

---

# 24. Đây là Lazy Computation

Luồng:

```text
User(...)
   │
   ▼
_normalized_name = None

...

user.normalized_name
   │
   ▼
compute
   │
   ▼
cache result
```

---

# 25. Lazy Initialization cho crawler

Ví dụ:

```python
@dataclass
class Novel:

    title: str
    url: str

    _chapters: list | None = field(
        init=False,
        default=None
    )

    def load_chapters(self):
        if self._chapters is None:
            self._chapters = []

        return self._chapters
```

Lúc mới tạo:

```python
Novel(
    "My Novel",
    "https://..."
)
```

chưa tạo danh sách chapters.

Khi cần:

```python
novel.load_chapters()
```

mới khởi tạo.

---

# 26. Một cảnh báo quan trọng

Lazy initialization thường là **behavior**.

Do đó nếu dataclass bắt đầu chứa quá nhiều:

```python
load()
save()
fetch()
refresh()
connect()
disconnect()
```

thì có thể class đã không còn phù hợp với vai trò của dataclass nữa.

Đây là dấu hiệu:

> Nên chuyển behavior sang service/repository.

---

# 27. `__post_init__()` với `frozen=True`

Đây là trường hợp rất quan trọng.

```python
@dataclass(frozen=True)
class User:

    name: str

    normalized_name: str = field(
        init=False
    )

    def __post_init__(self):
        self.normalized_name = (
            self.name.lower()
        )
```

Sẽ lỗi.

Vì:

```text
frozen=True
```

không cho phép:

```python
self.normalized_name = ...
```

---

# 28. Dùng `object.__setattr__()`

Trong frozen dataclass:

```python
@dataclass(frozen=True)
class User:

    name: str

    normalized_name: str = field(
        init=False
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "normalized_name",
            self.name.lower()
        )
```

Đây là pattern chuẩn để thiết lập trạng thái ban đầu trong frozen dataclass.

---

# 29. Tại sao làm được?

`frozen=True` chủ yếu ngăn:

```python
user.name = "Bob"
```

thông qua cơ chế `__setattr__()` của dataclass.

Trong quá trình khởi tạo, ta có thể dùng:

```python
object.__setattr__()
```

để thiết lập field.

Nhưng:

> Không nên dùng kỹ thuật này để phá vỡ tính immutable sau khi object đã được tạo.

---

# 30. `__post_init__()` và `InitVar`

Đây là mối quan hệ quan trọng:

```python
@dataclass
class User:

    name: str

    raw_name: InitVar[str]

    def __post_init__(self, raw_name):
        ...
```

Luồng:

```text
User(raw_name)
      │
      ▼
__init__()
      │
      ├── self.name = ...
      │
      ▼
__post_init__(raw_name)
      │
      ▼
raw_name không được lưu
```

---

# 31. `__post_init__()` và inheritance

Điều này sẽ trở nên rất quan trọng ở **Buổi 11**.

Ví dụ:

```python
@dataclass
class Base:

    name: str

    def __post_init__(self):
        print("Base")
```

```python
@dataclass
class User(Base):

    age: int

    def __post_init__(self):
        super().__post_init__()
        print("User")
```

Kết quả:

```text
Base
User
```

Nếu lớp con không gọi:

```python
super().__post_init__()
```

thì logic của lớp cha không tự chạy.

Phần này chúng ta sẽ đào sâu ở Buổi 11.

---

# 32. Một thiết kế thực tế

Hãy xây dựng:

```python
@dataclass(
    slots=True
)
class Chapter:

    title: str
    url: str

    content: str = field(
        init=False,
        default=""
    )

    def __post_init__(self):
        self.title = self.title.strip()
        self.url = self.url.strip()

        if not self.title:
            raise ValueError(
                "title cannot be empty"
            )

        if not self.url.startswith(
            ("http://", "https://")
        ):
            raise ValueError(
                "invalid URL"
            )
```

Ở đây `__post_init__()` làm hai việc:

```text
Normalization
      +
Validation
```

---

# 33. Một nguyên tắc thiết kế quan trọng

`__post_init__()` nên tập trung vào:

```text
✓ Normalize
✓ Validate
✓ Initialize derived state
✓ Establish invariants
```

Không nên biến nó thành:

```text
✗ HTTP request
✗ Database query
✗ File download
✗ Business workflow
✗ Crawl entire website
```

Ví dụ này không tốt:

```python
@dataclass
class Novel:

    url: str

    def __post_init__(self):
        html = requests.get(self.url)
        self.parse(html)
        self.save_database()
```

Vì việc tạo object giờ có side effect rất lớn.

```python
Novel(url)
```

mà lại:

```text
HTTP request
+
Parser
+
Database
```

Đây là thiết kế khó test và khó kiểm soát.

---

# 34. Invariant

Đây là khái niệm quan trọng.

**Invariant** là điều kiện phải luôn đúng đối với object.

Ví dụ:

```python
@dataclass
class Chapter:

    index: int
    title: str

    def __post_init__(self):
        if self.index < 1:
            raise ValueError(
                "index must be >= 1"
            )

        if not self.title.strip():
            raise ValueError(
                "title cannot be empty"
            )
```

Sau khi:

```python
chapter = Chapter(...)
```

ta có thể tin rằng:

```text
chapter.index >= 1
chapter.title != ""
```

Đây chính là giá trị lớn của validation trong `__post_init__()`.

---

# 35. `__post_init__()` như một Boundary

Có thể hình dung:

```text
External Data
      │
      ▼
┌───────────────────┐
│   __post_init__   │
│                   │
│ Normalize         │
│ Validate          │
│ Compute           │
│ Initialize        │
└───────────────────┘
      │
      ▼
Valid Object
```

Dataclass trở thành một **boundary giữa dữ liệu bên ngoài và trạng thái hợp lệ bên trong**.

---

# 36. Pattern hoàn chỉnh

Một dataclass có thể có:

```python
@dataclass(slots=True)
class Product:

    price: float
    quantity: int

    total: float = field(
        init=False
    )

    def __post_init__(self):

        # 1. Normalize
        ...

        # 2. Validate
        ...

        # 3. Computed field
        self.total = (
            self.price * self.quantity
        )
```

Đây là pattern rất đáng nhớ.

---

# 37. Khi nào không dùng `__post_init__()`?

Nếu không có logic sau khởi tạo:

```python
@dataclass
class Point:
    x: float
    y: float
```

thì không cần:

```python
def __post_init__(self):
    pass
```

Không có lý do để viết hook nếu hook không làm gì.

---

# 38. Những lỗi thường gặp

### Lỗi 1 — Quên `self`

Sai:

```python
def __post_init__():
    ...
```

Đúng:

```python
def __post_init__(self):
    ...
```

---

### Lỗi 2 — Tưởng type hint tự validate

```python
age: int
```

không có nghĩa runtime tự kiểm tra.

---

### Lỗi 3 — Gọi HTTP trong `__post_init__()`

Làm constructor có side effect.

---

### Lỗi 4 — Quên `super().__post_init__()`

Đặc biệt nguy hiểm khi inheritance.

---

### Lỗi 5 — Dùng `self.field = ...` trong frozen dataclass

Phải dùng:

```python
object.__setattr__()
```

khi đang thiết lập trạng thái ban đầu.

---

# 39. Bài tập 1 — Validation

Viết:

```python
@dataclass
class User:

    username: str
    age: int
    email: str
```

`__post_init__()` phải đảm bảo:

```text
username != ""
age >= 0
email chứa "@"
```

Nếu không hợp lệ:

```python
ValueError
```

---

# 40. Bài tập 2 — Computed Field

Viết:

```python
@dataclass
class Rectangle:

    width: float
    height: float

    area: float = field(
        init=False
    )
```

Trong `__post_init__()`:

```text
area = width × height
```

Đồng thời validate:

```text
width > 0
height > 0
```

---

# 41. Bài tập 3 — Frozen

Viết:

```python
@dataclass(frozen=True)
class User:

    first_name: str
    last_name: str

    full_name: str = field(
        init=False
    )
```

Trong `__post_init__()` sử dụng:

```python
object.__setattr__()
```

để tạo `full_name`.

Sau đó thử:

```python
user.first_name = "Bob"
```

và quan sát kết quả.

---

# 42. Bài tập 4 — Dependency Injection

Tạo:

```python
class Parser:

    def parse(self, text):
        return text.upper()
```

Sau đó:

```python
@dataclass
class Document:

    text: str

    parser: InitVar[Parser]

    content: str = field(
        init=False
    )
```

Trong `__post_init__()`:

```text
parser.parse(text)
       ↓
content
```

Kiểm tra rằng:

```python
document.parser
```

không tồn tại.

---

# 43. Bài tập 5 — Crawler Model

Thiết kế:

```python
@dataclass(slots=True)
class Chapter:

    novel_id: int
    index: int
    title: str
    url: str

    chapter_key: str = field(
        init=False
    )
```

`__post_init__()` phải:

1. `title.strip()`
2. `url.strip()`
3. Validate `novel_id > 0`
4. Validate `index > 0`
5. Validate URL bắt đầu bằng `http://` hoặc `https://`
6. Tạo:

```text
chapter_key = "{novel_id}:{index}"
```

Ví dụ:

```python
Chapter(
    novel_id=100,
    index=5,
    title="  Chương 5  ",
    url=" https://example.com/chapter-5 "
)
```

Sau khi tạo:

```text
title
→ "Chương 5"

url
→ "https://example.com/chapter-5"

chapter_key
→ "100:5"
```

---

# Tổng kết Buổi 10

`__post_init__()` không đơn giản chỉ là:

```python
print("created")
```

Nó là nơi rất phù hợp để thiết lập **invariant** của object.

4 vai trò chính theo roadmap:

```text
                __post_init__()
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   Validation    Computed       Initialization
                     Field
                       │
                Dependency /
                Lazy setup
```

Nguyên tắc quan trọng nhất:

> **Sau khi `__post_init__()` hoàn thành, object nên ở trạng thái hợp lệ và nhất quán.**

Và cần nhớ:

```text
@dataclass
      │
      ▼
__init__()
      │
      ▼
__post_init__()
      │
      ▼
Valid Object
```

---

## Buổi tiếp theo — Buổi 11

Theo roadmap chính xác của bạn:

# **Buổi 11 — Dataclass Inheritance**

Chúng ta sẽ đi sâu vào:

* Dataclass kế thừa thực sự hoạt động thế nào.
* Field của Base + Child được merge ra sao.
* Field override.
* Default field và vấn đề thứ tự.
* `__init__()` trong inheritance.
* `__post_init__()` + `super()`.
* `InitVar` trong inheritance.
* `frozen` inheritance.
* `slots` inheritance.
* `kw_only` inheritance.
* MRO và cách dataclass sử dụng MRO.

Sau đó **Buổi 12 mới là Multiple Inheritance + MRO**, đúng như roadmap bạn đưa.
