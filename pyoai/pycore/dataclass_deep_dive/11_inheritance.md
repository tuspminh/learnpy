# Dataclass Deep Dive — Buổi 11

# Dataclass Inheritance — Kế thừa Dataclass

Hôm nay chúng ta bắt đầu **Phần II — Advanced**, đúng roadmap:

> **Buổi 11. Inheritance — Dataclass kế thừa**

Đây là phần rất quan trọng vì `dataclass` + inheritance có nhiều quy tắc dễ gây nhầm, đặc biệt liên quan đến:

* field inheritance
* field override
* thứ tự field
* `__init__()`
* `__post_init__()`
* `default`
* `default_factory`
* `InitVar`
* `frozen`
* `slots`

---

# 1. Dataclass có thể kế thừa không?

Có.

Ví dụ class thông thường:

```python
class User:
    def __init__(self, name):
        self.name = name


class Admin(User):
    def __init__(self, name, permissions):
        super().__init__(name)
        self.permissions = permissions
```

Với dataclass:

```python
from dataclasses import dataclass


@dataclass
class User:
    name: str


@dataclass
class Admin(User):
    permissions: list[str]
```

Python sẽ tạo `Admin` dựa trên **cả field của `User` và `Admin`**.

```python
admin = Admin(
    name="Alice",
    permissions=["read", "write"]
)
```

---

# 2. Field được kế thừa như thế nào?

Ta có:

```python
@dataclass
class User:
    name: str
    age: int


@dataclass
class Admin(User):
    permissions: list[str]
    level: int
```

Có thể hình dung:

```text
User
│
├── name
└── age

        ↓ inheritance

Admin
│
├── name
├── age
├── permissions
└── level
```

`Admin` có toàn bộ field của `User`.

---

# 3. `__init__()` được sinh cho class con

Python tạo `Admin.__init__()` tương đương về mặt ý tưởng với:

```python
def __init__(
    self,
    name: str,
    age: int,
    permissions: list[str],
    level: int
):
    self.name = name
    self.age = age
    self.permissions = permissions
    self.level = level
```

Bạn **không cần**:

```python
super().__init__(...)
```

chỉ để gán các dataclass field của base class.

Đây là điểm rất quan trọng.

---

# 4. Dataclass không đơn giản gọi `Base.__init__()`

Ví dụ:

```python
@dataclass
class Base:
    name: str

    def __init__(self, name):
        print("Base init")
        self.name = name
```

```python
@dataclass
class Child(Base):
    age: int
```

Khi:

```python
Child("Alice", 20)
```

không nên giả định rằng:

```text
Child.__init__()
      ↓
Base.__init__()
```

Dataclass-generated `__init__()` của `Child` được sinh để khởi tạo các field của toàn bộ dataclass hierarchy.

Đây là lý do `__post_init__()` đặc biệt quan trọng khi inheritance.

---

# 5. `__post_init__()` trong inheritance

Base:

```python
@dataclass
class User:

    name: str

    def __post_init__(self):
        print("User post init")
```

Child:

```python
@dataclass
class Admin(User):

    permissions: list[str]

    def __post_init__(self):
        print("Admin post init")
```

```python
Admin(
    "Alice",
    ["read"]
)
```

Kết quả:

```text
Admin post init
```

Không phải:

```text
User post init
Admin post init
```

---

# 6. Vì sao?

Dataclass-generated `__init__()` của `Admin` sẽ gọi:

```python
self.__post_init__()
```

Theo dynamic dispatch, `self.__post_init__()` trỏ tới method của `Admin`.

Nó **không tự động gọi toàn bộ chuỗi `__post_init__()` của parent**.

---

# 7. Muốn chạy `Base.__post_init__()`

Ta phải chủ động:

```python
@dataclass
class Admin(User):

    permissions: list[str]

    def __post_init__(self):
        super().__post_init__()

        print("Admin post init")
```

Bây giờ:

```python
Admin(
    "Alice",
    ["read"]
)
```

Kết quả:

```text
User post init
Admin post init
```

Đây là pattern rất quan trọng.

---

# 8. `__post_init__()` + validation

Base:

```python
@dataclass
class User:

    name: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError(
                "name cannot be empty"
            )
```

Child:

```python
@dataclass
class Admin(User):

    level: int

    def __post_init__(self):
        super().__post_init__()

        if self.level < 1:
            raise ValueError(
                "level must be >= 1"
            )
```

Luồng:

```text
Admin(...)
    │
    ▼
User validation
    │
    ▼
Admin validation
    │
    ▼
Valid Admin
```

Đây là cách rất tốt để xây dựng validation theo tầng.

---

# 9. Field override

Base:

```python
@dataclass
class User:

    name: str
    age: int
```

Child:

```python
@dataclass
class Admin(User):

    age: int = 18
```

Field `age` của child **override** field `age` của base.

Kết quả:

```python
admin = Admin(
    name="Alice"
)

print(admin.age)
```

```text
18
```

---

# 10. Override type

Có thể override cả type annotation:

```python
@dataclass
class Base:

    value: object
```

```python
@dataclass
class Child(Base):

    value: str
```

Child khai báo:

```python
value: str
```

thay cho:

```python
value: object
```

Tuy nhiên, việc thay đổi type cần đảm bảo thiết kế vẫn hợp lý về mặt substitutability và typing.

---

# 11. Override default

Base:

```python
@dataclass
class User:

    name: str
    age: int = 18
```

Child:

```python
@dataclass
class Admin(User):

    age: int = 30
```

```python
Admin("Alice")
```

Kết quả:

```python
Admin(
    name="Alice",
    age=30
)
```

---

# 12. Một vấn đề cực kỳ quan trọng: field ordering

Xét:

```python
@dataclass
class Base:

    name: str
    age: int = 18
```

Child:

```python
@dataclass
class Admin(Base):

    permissions: list[str]
```

Bạn có thể nghĩ constructor là:

```python
Admin(
    name,
    age=18,
    permissions
)
```

Nhưng Python không cho:

```text
non-default argument
after default argument
```

Do đó inheritance có thể tạo ra lỗi:

```text
TypeError
```

---

# 13. Tại sao?

Dataclass merge field theo thứ tự inheritance.

Conceptually:

```text
Base:

name
age = 18

+

Admin:

permissions
```

↓

```text
name
age = 18
permissions
```

Nhưng Python function không cho:

```python
def __init__(
    name,
    age=18,
    permissions
):
    ...
```

Đây là một trong những lỗi phổ biến nhất của dataclass inheritance.

---

# 14. Giải pháp `kw_only=True`

Một giải pháp rất đẹp:

```python
@dataclass
class Base:

    name: str
    age: int = 18
```

```python
@dataclass(kw_only=True)
class Admin(Base):

    permissions: list[str]
```

Bây giờ:

```python
admin = Admin(
    "Alice",
    permissions=["read"]
)
```

Hoặc rõ ràng hơn:

```python
admin = Admin(
    name="Alice",
    permissions=["read"]
)
```

Keyword-only giúp tránh rất nhiều vấn đề về thứ tự constructor.

---

# 15. Giải pháp `kw_only` cho field

Bạn cũng có thể:

```python
from dataclasses import field


@dataclass
class Admin(Base):

    permissions: list[str] = field(
        kw_only=True
    )
```

Khi đó:

```python
Admin(
    "Alice",
    permissions=["read"]
)
```

---

# 16. `default_factory` trong inheritance

Base:

```python
@dataclass
class User:

    name: str

    tags: list[str] = field(
        default_factory=list
    )
```

Child:

```python
@dataclass
class Admin(User):

    permissions: list[str] = field(
        default_factory=list
    )
```

Mỗi object vẫn có list riêng.

```python
a = Admin("Alice")
b = Admin("Bob")

a.tags.append("admin")

print(b.tags)
```

Kết quả:

```python
[]
```

Không bị shared mutable state.

---

# 17. Inheritance và `InitVar`

Base:

```python
@dataclass
class User:

    name: str

    raw_password: InitVar[str]

    password_hash: str = field(
        init=False
    )

    def __post_init__(self, raw_password):
        self.password_hash = hash(
            raw_password
        )
```

Child:

```python
@dataclass
class Admin(User):

    level: int

    def __post_init__(
        self,
        raw_password
    ):
        super().__post_init__(
            raw_password
        )

        if self.level < 1:
            raise ValueError(
                "invalid level"
            )
```

Điểm quan trọng:

`InitVar` cũng tham gia vào constructor của dataclass hierarchy.

---

# 18. Thứ tự `InitVar`

Đây là lý do cần đặc biệt cẩn thận khi inheritance.

Base:

```python
@dataclass
class Base:

    name: str

    config: InitVar[dict]
```

Child:

```python
@dataclass
class Child(Base):

    age: int

    parser: InitVar[object]
```

Constructor conceptually sẽ có:

```text
name
config
age
parser
```

và `__post_init__()` của child phải nhận đúng các InitVar tương ứng theo thứ tự.

Đây là một trong những phần phức tạp hơn của dataclass inheritance.

---

# 19. `frozen=True` inheritance

Base:

```python
@dataclass(frozen=True)
class User:

    name: str
```

Child:

```python
@dataclass(frozen=True)
class Admin(User):

    level: int
```

Hợp lệ.

Child cũng immutable:

```python
admin = Admin(
    "Alice",
    1
)

admin.level = 2
```

sẽ gây lỗi.

---

# 20. Không thể tùy tiện bỏ `frozen`

Nếu base là:

```python
@dataclass(frozen=True)
class Base:
    name: str
```

mà child:

```python
@dataclass
class Child(Base):
    age: int
```

sẽ gặp lỗi thiết kế vì frozen và non-frozen dataclass inheritance không thể trộn tùy ý.

Nguyên tắc thực tế:

> Nếu base là frozen, hãy giữ child là frozen.

---

# 21. `slots=True` inheritance

Base:

```python
@dataclass(slots=True)
class User:

    name: str
```

Child:

```python
@dataclass(slots=True)
class Admin(User):

    level: int
```

Child cũng sử dụng slots cho field của mình.

Conceptually:

```text
User
└── __slots__ = ("name",)

Admin
└── __slots__ = ("level",)
```

Không nên nghĩ rằng `Admin.__slots__` nhất thiết chứa lại toàn bộ field của parent.

Inheritance hierarchy cùng tham gia vào layout.

---

# 22. `slots` và `__dict__`

Với:

```python
@dataclass(slots=True)
class User:
    name: str
```

thường:

```python
user.__dict__
```

không tồn tại.

Điều này giúp giảm overhead của mỗi instance.

Nhưng inheritance với các class không dùng slots cần được thiết kế cẩn thận, vì một base class có `__dict__` vẫn có thể khiến instance hierarchy có dictionary.

---

# 23. Dataclass inheritance không đồng nghĩa OOP inheritance luôn tốt

Đây là vấn đề thiết kế.

Ví dụ:

```text
BaseModel
   │
   ├── Novel
   ├── Chapter
   ├── Author
   ├── Image
   ├── Category
   ├── Task
   └── Config
```

Không nên ép tất cả thành inheritance chỉ vì có thể.

Nếu quan hệ là:

```text
Novel HAS Author
Novel HAS Chapter
```

thì đó là:

> Composition

không phải inheritance.

Phần này sẽ học sâu ở **Buổi 13**.

---

# 24. Inheritance vs Composition

Inheritance:

```text
Admin
   IS-A
User
```

Composition:

```text
Novel
   HAS-A
Author
```

Ví dụ:

```python
@dataclass
class Author:
    name: str
```

```python
@dataclass
class Novel:
    title: str
    author: Author
```

Đây là composition.

---

# 25. `super()` trong Dataclass

Có hai chỗ cần phân biệt.

### Constructor

Thông thường **không cần** tự gọi:

```python
super().__init__()
```

nếu cả base và child đều là dataclass.

### `__post_init__()`

Nếu child override:

```python
def __post_init__(self):
```

thì cần cân nhắc:

```python
super().__post_init__()
```

để chạy logic của base.

Đây là khác biệt rất quan trọng.

---

# 26. Một ví dụ hoàn chỉnh

```python
from dataclasses import dataclass, field


@dataclass(slots=True)
class User:

    name: str
    age: int

    def __post_init__(self):

        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "name cannot be empty"
            )

        if self.age < 0:
            raise ValueError(
                "age cannot be negative"
            )


@dataclass(slots=True)
class Admin(User):

    permissions: list[str] = field(
        default_factory=list,
        kw_only=True
    )

    def __post_init__(self):

        super().__post_init__()

        if not self.permissions:
            raise ValueError(
                "Admin needs permissions"
            )
```

Sử dụng:

```python
admin = Admin(
    name=" Alice ",
    age=30,
    permissions=["read", "write"]
)
```

Sau đó:

```python
print(admin)
```

Có thể nhận được:

```text
Admin(
    name='Alice',
    age=30,
    permissions=['read', 'write']
)
```

---

# 27. Luồng khởi tạo

Khi chạy:

```python
Admin(
    name=" Alice ",
    age=30,
    permissions=["read"]
)
```

conceptually:

```text
Admin.__init__()
        │
        ├── self.name = " Alice "
        ├── self.age = 30
        ├── self.permissions = ["read"]
        │
        ▼
Admin.__post_init__()
        │
        ▼
User.__post_init__()
        │
        ├── normalize name
        ├── validate name
        └── validate age
        │
        ▼
Admin validation
        │
        ▼
Valid Admin
```

---

# 28. Một pattern rất tốt

Ta có thể xây hierarchy:

```text
BaseEntity
    │
    ├── normalize ID
    └── validate ID
          │
          ▼
Novel
    │
    └── validate novel data
          │
          ▼
SpecialNovel
    │
    └── validate special rules
```

Mỗi tầng chịu trách nhiệm cho invariant của chính mình.

---

# 29. Nhưng đừng tạo inheritance quá sâu

Ví dụ:

```text
Base
 ↓
Entity
 ↓
Content
 ↓
Story
 ↓
Novel
 ↓
PublishedNovel
 ↓
FeaturedNovel
 ↓
PremiumFeaturedNovel
```

Đây thường là dấu hiệu thiết kế có vấn đề.

Càng sâu:

* MRO phức tạp hơn.
* `super()` khó theo dõi.
* field ordering khó kiểm soát.
* validation khó debug.
* thay đổi base class ảnh hưởng nhiều child.

Trong domain model thực tế, thường ưu tiên:

```text
Composition
+
small focused dataclasses
```

hơn là inheritance quá sâu.

---

# 30. Quy tắc vàng

Khi thiết kế dataclass inheritance:

### Rule 1

Base chứa những field thực sự chung.

### Rule 2

Child chỉ thêm dữ liệu hoặc behavior thật sự đặc thù.

### Rule 3

Nếu override `__post_init__()`, cân nhắc `super()`.

### Rule 4

Cẩn thận default field ở base.

### Rule 5

`kw_only=True` rất hữu ích khi hierarchy có nhiều default.

### Rule 6

Frozen hierarchy nên nhất quán.

### Rule 7

Không dùng inheritance để biểu diễn quan hệ `HAS-A`.

---

# 31. Bài tập 1 — Basic Inheritance

Tạo:

```python
@dataclass
class Person:
    name: str
    age: int
```

và:

```python
@dataclass
class Student(Person):
    school: str
```

Kiểm tra:

```python
Student(
    "Alice",
    20,
    "ABC School"
)
```

Sau đó kiểm tra:

```python
Student.__dataclass_fields__
```

---

# 32. Bài tập 2 — Field Override

Tạo:

```python
@dataclass
class User:
    name: str
    role: str = "user"
```

Child:

```python
@dataclass
class Admin(User):
    role: str = "admin"
```

Kiểm tra:

```python
Admin("Alice")
```

---

# 33. Bài tập 3 — `__post_init__()` chain

Tạo:

```python
@dataclass
class Base:
    value: int

    def __post_init__(self):
        print("Base")
```

Child:

```python
@dataclass
class Child(Base):
    name: str

    def __post_init__(self):
        super().__post_init__()
        print("Child")
```

Dự đoán output trước khi chạy.

---

# 34. Bài tập 4 — Default Ordering

Thử:

```python
@dataclass
class Base:
    name: str
    age: int = 18


@dataclass
class Child(Base):
    level: int
```

Quan sát lỗi.

Sau đó sửa bằng:

```python
kw_only=True
```

và giải thích tại sao nó giải quyết được vấn đề.

---

# 35. Bài tập 5 — Crawler Framework

Thiết kế:

```text
BaseModel
    │
    ├── id
    └── source
         │
         ├── Novel
         ├── Chapter
         └── Author
```

Yêu cầu:

### `BaseModel`

```python
id: int
source: str
```

### `Novel`

```python
title: str
author: str
```

### `Chapter`

```python
novel_id: int
index: int
title: str
url: str
```

Trong `BaseModel.__post_init__()`:

* validate `id > 0`
* validate `source != ""`

Trong child:

* gọi `super().__post_init__()`
* thêm validation riêng.

Đây là bài tập rất sát với kiến trúc crawler của bạn.

---

# 36. Tóm tắt Buổi 11

Mô hình tư duy quan trọng nhất:

```text
                 Base Dataclass
                       │
                inherited fields
                       │
                       ▼
                Child Dataclass
                       │
                merged fields
                       │
                       ▼
                 generated init
                       │
                       ▼
              child __post_init__
                       │
                       ▼
              super().__post_init__
                       │
                       ▼
               base validation
```

Điểm cần nhớ nhất:

```text
Dataclass inheritance
        ≠
class inheritance đơn giản
```

Dataclass phải xử lý thêm:

* field collection
* field overriding
* field ordering
* default
* generated `__init__`
* `InitVar`
* `__post_init__`
* frozen
* slots
* keyword-only

Và đây chính là lý do **Buổi 12 — Multiple Inheritance + MRO** sẽ thú vị hơn rất nhiều.

---

# Buổi 12

Theo đúng roadmap của bạn:

## Multiple Inheritance + MRO

Chúng ta sẽ đi sâu vào:

```text
A
├── B
└── C
     │
     ▼
     D
```

và tìm hiểu:

* Multiple inheritance với dataclass.
* Python merge field như thế nào.
* MRO là gì.
* C3 Linearization.
* `super()` thực sự chạy theo MRO ra sao.
* Diamond inheritance.
* `__post_init__()` trong diamond.
* Field conflict.
* Override field giữa nhiều parent.
* `default` conflict.
* `InitVar` + MRO.
* `frozen` + multiple inheritance.
* `slots` + multiple inheritance.
* Khi nào multiple inheritance là thiết kế tốt và khi nào nên chuyển sang composition.
