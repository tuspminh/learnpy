# Dataclass Deep Dive - Buổi 10

# Inheritance Deep Dive (Kế thừa với Dataclass)

> Đây là **một trong những chủ đề khó nhất** của `dataclass`.

Nếu hiểu buổi này, bạn có thể thiết kế các hệ thống model lớn như:

```text-x-trilium-auto
BaseEntity
    │
    ├── Novel
    ├── Chapter
    ├── Author
    ├── Category
    ├── Image
    └── CrawlJob
```

Đây cũng là kiểu kiến trúc bạn sẽ sử dụng trong **hệ thống crawler truyện** của mình.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Dataclass kế thừa hoạt động như thế nào.
- Constructor (`__init__`) được sinh ra sao.
- Field của lớp cha và lớp con được kết hợp như thế nào.
- Override field.
- `__post_init__()` và `super()`.
- Kết hợp với `slots`, `frozen`, `kw_only`, `InitVar`.
- Những lỗi thường gặp.

---

# 1. Dataclass có hỗ trợ kế thừa không?

Có.

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Animal:
    name: str

@dataclass class Dog(Animal):
    age: int
```

Khởi tạo:

```text-x-trilium-auto
dog = Dog("Lucky", 3)

print(dog)
```

Kết quả:

```text-x-trilium-auto
Dog(name='Lucky', age=3)
```

---

# 2. Constructor được sinh như thế nào?

Bạn chỉ viết:

```text-x-trilium-auto
Dog("Lucky", 3)
```

Nhưng Python sinh gần giống:

```text-x-trilium-auto
class Dog(Animal):

    def __init__(self, name, age):
        self.name = name
        self.age = age
```

Điều đặc biệt là dataclass **không gọi** `**Animal.__init__()**`.

Nó tự sinh một constructor hoàn chỉnh cho lớp con.

---

# 3. Thứ tự field

Ví dụ

```text-x-trilium-auto
@dataclass class Animal:
    name: str

@dataclass class Dog(Animal):
    age: int
```

Constructor:

```text-x-trilium-auto
Dog(name, age)
```

Field cha luôn đứng trước.

---

Nếu nhiều tầng

```text-x-trilium-auto
@dataclass class A:
    a: int

@dataclass class B(A):
    b: int

@dataclass class C(B):
    c: int
```

Constructor:

```text-x-trilium-auto
C(a, b, c)
```

---

# 4. Override Field

Ví dụ

```text-x-trilium-auto
@dataclass class Animal:
    name: str

@dataclass class Dog(Animal):
    name: str
```

Hoàn toàn hợp lệ.

Field của lớp con sẽ ghi đè field của lớp cha.

---

Ví dụ khác

```text-x-trilium-auto
@dataclass class Animal:
    age: int

@dataclass class Dog(Animal):
    age: float
```

Bây giờ

```text-x-trilium-auto
Dog(3.5)
```

`age`

↓

kiểu

```text-x-trilium-auto
float
```

---

# 5. Thêm default

```text-x-trilium-auto
@dataclass class Animal:
    name: str

@dataclass class Dog(Animal):
    age: int = 1
```

Được.

Constructor

```text-x-trilium-auto
Dog("Lucky")
```

↓

```text-x-trilium-auto
Dog(name='Lucky', age=1)
```

---

# 6. Lỗi thứ tự field

Ví dụ

```text-x-trilium-auto
@dataclass class Animal:
    age: int = 0

@dataclass class Dog(Animal):
    name: str
```

Python báo:

```text-x-trilium-auto
TypeError:
non-default argument follows default argument
```

Vì constructor trở thành:

```text-x-trilium-auto
Dog(age=0, name)
```

Đây là cú pháp không hợp lệ trong Python.

---

## Cách sửa

Đưa field mặc định xuống cuối hoặc dùng `kw_only=True`.

```text-x-trilium-auto
@dataclass class Animal:
    age: int = field(default=0, kw_only=True)
```

---

# 7. `__post_init__()`

Lớp cha

```text-x-trilium-auto
@dataclass class Animal:
    name: str

    def __post_init__(self):
        print("Animal")
```

Lớp con

```text-x-trilium-auto
@dataclass class Dog(Animal):
    age: int

    def __post_init__(self):
        print("Dog")
```

Kết quả

```text-x-trilium-auto
Dog("Lucky", 3)
```

↓

```text-x-trilium-auto
Dog
```

`**Animal.__post_init__()**` **không tự chạy.**

---

# 8. Gọi `super()`

Muốn gọi

↓

```text-x-trilium-auto
@dataclass class Dog(Animal):

    age: int

    def __post_init__(self):

        super().__post_init__()

        print("Dog")
```

Kết quả

```text-x-trilium-auto
Animal
Dog
```

Đây là cách đúng khi có logic ở cả lớp cha và lớp con.

---

# 9. Ví dụ BaseEntity

```text-x-trilium-auto
from dataclasses import dataclass from datetime import datetime

@dataclass class BaseEntity:

    created_at: datetime

    def __post_init__(self):
        print("Entity created")
```

---

```text-x-trilium-auto
@dataclass class Novel(BaseEntity):

    title: str

    def __post_init__(self):

        super().__post_init__()

        print("Novel created")
```

---

Kết quả

```text-x-trilium-auto
Entity created
Novel created
```

---

# 10. Kết hợp InitVar

```text-x-trilium-auto
from dataclasses import dataclass from dataclasses import InitVar

@dataclass class Animal:

    config: InitVar[dict]

    def __post_init__(self, config):

        print(config)
```

---

```text-x-trilium-auto
@dataclass class Dog(Animal):

    age: int

    def __post_init__(self, config):

        super().__post_init__(config)
```

Lưu ý:

Các `InitVar` phải được truyền tiếp cho `super().__post_init__()` nếu lớp cha cần dùng.

---

# 11. Kết hợp Frozen

```text-x-trilium-auto
@dataclass(
    frozen=True
)
class Animal:

    name: str
```

↓

```text-x-trilium-auto
@dataclass(
    frozen=True
)
class Dog(Animal):

    age: int
```

Được.

---

Sai

```text-x-trilium-auto
@dataclass(
    frozen=True
)
class Animal:
    ...

@dataclass class Dog(Animal):
    ...
```

Python báo lỗi vì lớp con không được "giảm" mức bất biến của lớp cha.

Tương tự, lớp con `frozen=True` cũng không thể kế thừa từ lớp cha không `frozen`.

---

# 12. Kết hợp Slots

```text-x-trilium-auto
@dataclass(
    slots=True
)
class Animal:

    name: str
```

↓

```text-x-trilium-auto
@dataclass(
    slots=True
)
class Dog(Animal):

    age: int
```

Được.

Python sẽ hợp nhất các slot.

---

# 13. Kết hợp kw_only

```text-x-trilium-auto
@dataclass class Animal:

    name: str

    age: int = field(
        kw_only=True
    )
```

↓

```text-x-trilium-auto
Dog(
    "Lucky",
    age=3
)
```

Hoạt động bình thường.

---

# 14. Kế thừa nhiều tầng

```text-x-trilium-auto
A

↓

B

↓

C

↓

D
```

Dataclass sẽ thu thập field theo thứ tự MRO (Method Resolution Order), sau đó sinh một constructor thống nhất.

Ví dụ:

```text-x-trilium-auto
@dataclass class A:
    a: int

@dataclass class B(A):
    b: int

@dataclass class C(B):
    c: int
```

↓

```text-x-trilium-auto
C(1, 2, 3)
```

---

# 15. Multiple Inheritance

Ví dụ

```text-x-trilium-auto
@dataclass class A:
    a: int

@dataclass class B:
    b: int

@dataclass class C(A, B):
    c: int
```

Python **có hỗ trợ**, nhưng việc kết hợp field theo MRO khá phức tạp và dễ gây nhầm lẫn.

Trong thực tế:

> **Không nên dùng Multiple Inheritance với dataclass**, trừ khi bạn hiểu rất rõ MRO và cách dataclass thu thập field.

Thay vào đó, ưu tiên:

- Composition
- Mixins không chứa field

---

# 16. Ví dụ thực tế của crawler

```text-x-trilium-auto
from dataclasses import dataclass from datetime import datetime

@dataclass(slots=True)
class BaseModel:

    id: int

    created_at: datetime
```

---

```text-x-trilium-auto
@dataclass(slots=True)
class Chapter(BaseModel):

    novel_id: int

    title: str

    url: str
```

---

```text-x-trilium-auto
chapter = Chapter(

1,

datetime.now(),

100,

"Chương 1",

"https://..."
)
```

---

# 17. BaseAuditModel

Một thiết kế rất phổ biến:

```text-x-trilium-auto
@dataclass class BaseAuditModel:

    created_at: datetime

    updated_at: datetime
```

---

```text-x-trilium-auto
@dataclass class Novel(BaseAuditModel):

    title: str
```

---

```text-x-trilium-auto
@dataclass class Chapter(BaseAuditModel):

    title: str
```

Tất cả model đều dùng chung hai field audit.

---

# 18. Best Practice cho dự án crawler

Mình đề xuất kiến trúc như sau:

```text-x-trilium-auto
BaseEntity
│
├── id
├── created_at
├── updated_at
│
├──────────────┐
│              │
│              │
Novel       Chapter
│              │
│              │
Author      Image
│
Category
```

Hoặc nếu tách rõ:

```text-x-trilium-auto
BaseModel
    │
    ├── BaseAuditModel
    │       │
    │       ├── Novel
    │       ├── Chapter
    │       ├── Author
    │       └── Category
    │
    └── CrawlJob
```

Thiết kế này giúp tránh lặp lại các field dùng chung và dễ mở rộng.

---

# 19. Những lỗi thường gặp

### ❌ Quên gọi `super().__post_init__()`

Nếu lớp cha có logic khởi tạo quan trọng, lớp con phải gọi:

```text-x-trilium-auto
super().__post_init__()
```

---

### ❌ Thứ tự field sai

```text-x-trilium-auto
default

↓

non-default
```

Sẽ gây:

```text-x-trilium-auto
TypeError
```

---

### ❌ Trộn `frozen=True` và `frozen=False`

Không hợp lệ trong kế thừa.

---

### ❌ Lạm dụng Multiple Inheritance

Nên tránh với dataclass có field.

---

# 20. So sánh kế thừa và composition

Kế thừa:

```text-x-trilium-auto
BaseEntity
    │
    └── Chapter
```

Composition:

```text-x-trilium-auto
Chapter
    │
    └── AuditInfo
```

Nếu mối quan hệ là "**is-a**" (Chapter **là** một BaseEntity), kế thừa phù hợp.

Nếu là "**has-a**" (Chapter **có** thông tin audit), composition cũng là một lựa chọn tốt, đặc biệt khi muốn giảm mức độ phụ thuộc giữa các lớp.

---

# Tổng kết

| Chủ đề | Ý nghĩa |
| --- | --- |
| Kế thừa | Dataclass hỗ trợ đầy đủ |
| Constructor | Tự sinh cho toàn bộ cây kế thừa |
| Override field | Được phép |
| `__post_init__()` | Phải gọi `super()` nếu cần |
| `slots` | Có thể kế thừa |
| `frozen` | Cha và con phải nhất quán |
| `InitVar` | Có thể truyền qua `super()` |
| Multiple Inheritance | Hỗ trợ nhưng nên hạn chế |

---

# Bài tập thực hành

## Bài 1

Thiết kế:

```text-x-trilium-auto
@dataclass class BaseEntity:
    id: int
```

↓

```text-x-trilium-auto
@dataclass class User(BaseEntity):
    username: str
```

↓

```text-x-trilium-auto
@dataclass class Admin(User):
    role: str
```

Kiểm tra constructor và `repr()`.

---

## Bài 2

Tạo:

```text-x-trilium-auto
BaseAuditModel
```

gồm:

- `created_at`
- `updated_at`

Sau đó cho:

- `Novel`
- `Chapter`
- `Author`

kế thừa và thêm các field riêng.

---

## Bài 3 (Áp dụng dự án crawler)

Thiết kế cây model:

```text-x-trilium-auto
BaseModel
│
├── BaseContent
│      ├── Novel
│      ├── Chapter
│      └── Author
│
├── BaseMedia
│      └── Image
│
└── CrawlJob
```

Yêu cầu:

- Sử dụng `@dataclass(slots=True)`.
- Thêm `created_at` và `updated_at` ở lớp cơ sở phù hợp.
- Viết `__post_init__()` để tự động ghi log khi tạo đối tượng và dùng `super().__post_init__()` để đảm bảo toàn bộ chuỗi khởi tạo được thực thi đúng.

---

# Chuẩn bị cho Buổi 11

Buổi tiếp theo chúng ta sẽ học **Dataclass Introspection & Utility Functions Deep Dive**.

Đây là chủ đề về các hàm tiện ích quan trọng của `dataclasses`:

- `fields()`
- `asdict()`
- `astuple()`
- `replace()`
- `is_dataclass()`
- `make_dataclass()`

Bạn sẽ học cách:

- Chuyển đổi dataclass thành `dict` hoặc `tuple`.
- Sao chép đối tượng với thay đổi một vài field.
- Kiểm tra một object có phải dataclass hay không.
- Tạo dataclass động tại runtime.
- Xây dựng serializer, mapper và công cụ hỗ trợ cho hệ thống crawler của mình. Đây là nhóm API được sử dụng rất nhiều trong các framework và thư viện Python chuyên nghiệp.