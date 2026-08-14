# Dataclass Deep Dive — Buổi 12

# Multiple Inheritance + MRO

Hôm nay chúng ta đi vào một phần **khó nhưng cực kỳ quan trọng** của Dataclass:

> **Multiple Inheritance + MRO**

Nếu Buổi 11 là:

```text
Base
  ↓
Child
```

thì hôm nay là:

```text
        A
       / \
      B   C
       \ /
        D
```

Đặc biệt, ta sẽ kết hợp 3 cơ chế:

```text
Dataclass
    +
Multiple Inheritance
    +
Python MRO
```

---

# 1. Multiple Inheritance là gì?

Python cho phép một class kế thừa nhiều class:

```python
class A:
    pass


class B:
    pass


class C(A, B):
    pass
```

`C` có hai parent:

```text
A ──┐
    ├──> C
B ──┘
```

Với dataclass:

```python
from dataclasses import dataclass


@dataclass
class A:
    a: int


@dataclass
class B:
    b: int


@dataclass
class C(A, B):
    c: int
```

---

# 2. Field của nhiều Base được merge

Ta có:

```python
@dataclass
class A:
    a: int


@dataclass
class B:
    b: int


@dataclass
class C(A, B):
    c: int
```

`C` conceptually có:

```text
a
b
c
```

Constructor:

```python
C(
    a=1,
    b=2,
    c=3
)
```

---

# 3. Nhưng thứ tự không đơn giản là A → B → C

Đây là điểm rất quan trọng.

Python không đơn giản:

```text
A
↓
B
↓
C
```

mà sử dụng:

> **MRO — Method Resolution Order**

Kiểm tra:

```python
print(C.__mro__)
```

Có thể nhận:

```text
C
A
B
object
```

tức:

```text
C → A → B → object
```

---

# 4. MRO là gì?

MRO xác định:

> Khi Python tìm một method/attribute, nó tìm class nào trước?

Ví dụ:

```python
class A:
    def hello(self):
        print("A")


class B:
    def hello(self):
        print("B")


class C(A, B):
    pass
```

Khi:

```python
c = C()
c.hello()
```

Python tìm:

```text
C
 ↓
A  ← tìm thấy hello()
 ↓
B
 ↓
object
```

Kết quả:

```text
A
```

---

# 5. `__mro__`

Bạn có thể xem trực tiếp:

```python
print(C.__mro__)
```

hoặc:

```python
print(C.mro())
```

Ví dụ:

```python
(
    C,
    A,
    B,
    object
)
```

---

# 6. Tại sao Dataclass cần MRO?

Bởi vì khi có:

```python
class C(A, B):
```

Python phải quyết định:

* field nào trước?
* method nào trước?
* `__post_init__()` nào?
* `super()` gọi ai?
* nếu A và B cùng có field?
* nếu A và B cùng có default?

Đây chính là nơi MRO trở thành nền tảng.

---

# 7. Ví dụ Multiple Dataclass đơn giản

```python
from dataclasses import dataclass


@dataclass
class TimestampMixin:
    created_at: int


@dataclass
class IdentityMixin:
    id: int


@dataclass
class User(
    TimestampMixin,
    IdentityMixin
):
    name: str
```

`User` kế thừa:

```text
TimestampMixin
IdentityMixin
```

và thêm:

```text
name
```

---

# 8. Kiểm tra field

```python
from dataclasses import fields

for field in fields(User):
    print(field.name)
```

Bạn sẽ thấy field được tổng hợp từ hierarchy.

Đây là một điểm rất đáng nhớ:

> Dataclass không chỉ nhìn `__annotations__` của class hiện tại.

Nó xử lý toàn bộ dataclass hierarchy theo quy tắc inheritance.

---

# 9. Field conflict

Đây mới là phần thú vị.

```python
@dataclass
class A:
    value: int


@dataclass
class B:
    value: int


@dataclass
class C(A, B):
    pass
```

Cả A và B đều có:

```text
value
```

Vậy `C` dùng cái nào?

---

# 10. Dataclass xử lý field override qua hierarchy

Dataclass thu thập field theo thứ tự reverse MRO, sau đó field ở class phía sau trong quá trình xử lý có thể override field cùng tên.

Với:

```python
C(A, B)
```

cần hiểu rằng **field merge không đơn giản đồng nhất với method lookup MRO**.

Đây là điểm rất quan trọng:

> **Field resolution của dataclass và method resolution của Python là hai cơ chế liên quan nhưng không phải cùng một thuật toán.**

---

# 11. Tại sao phải hiểu điều này?

Bạn có thể thấy:

```python
C.__mro__
```

là:

```text
C
A
B
object
```

nhưng thứ tự field không nên suy ra bằng cách:

```text
C
→ A
→ B
```

một cách máy móc.

Dataclass xây dựng ordered mapping các field bằng cách duyệt base dataclass theo hierarchy rồi áp dụng field của class hiện tại.

---

# 12. Diamond Inheritance

Đây là mô hình kinh điển:

```text
       A
      / \
     B   C
      \ /
       D
```

Ví dụ:

```python
@dataclass
class A:
    x: int


@dataclass
class B(A):
    b: int


@dataclass
class C(A):
    c: int


@dataclass
class D(B, C):
    d: int
```

Đây gọi là:

> Diamond inheritance.

---

# 13. MRO của Diamond

Python tạo MRO kiểu:

```text
D
B
C
A
object
```

Bạn có thể kiểm tra:

```python
print(D.__mro__)
```

Conceptually:

```text
D
 ↓
B
 ↓
C
 ↓
A
 ↓
object
```

Điểm quan trọng:

> `A` chỉ xuất hiện **một lần** trong MRO.

---

# 14. C3 Linearization

MRO của Python không phải chọn ngẫu nhiên.

Python sử dụng:

> **C3 Linearization**

Mục tiêu là đảm bảo:

### Local precedence

Nếu:

```python
class D(B, C):
```

thì:

```text
B
```

phải đứng trước:

```text
C
```

---

### Monotonicity

Thứ tự MRO của parent phải được giữ nhất quán trong child.

---

### Không duplicate class

`A` không xuất hiện hai lần.

---

# 15. `super()` thực sự là gì?

Một hiểu lầm phổ biến:

```python
super()
```

không có nghĩa đơn giản là:

> "gọi parent trực tiếp".

Thực tế:

> `super()` tiếp tục tìm method theo **MRO**, bắt đầu sau class hiện tại.

Đây là cực kỳ quan trọng với multiple inheritance.

---

# 16. Ví dụ

```python
class A:

    def hello(self):
        print("A")


class B(A):

    def hello(self):
        print("B")
        super().hello()


class C(A):

    def hello(self):
        print("C")
        super().hello()


class D(B, C):

    def hello(self):
        print("D")
        super().hello()
```

MRO:

```text
D
B
C
A
object
```

Khi:

```python
D().hello()
```

kết quả:

```text
D
B
C
A
```

---

# 17. Đây chính là sức mạnh của Cooperative Multiple Inheritance

Mỗi class không gọi:

```python
A.hello(self)
```

một cách hard-code.

Mà gọi:

```python
super().hello()
```

Mỗi class nói:

> "Tôi làm phần của tôi, sau đó chuyển quyền cho class tiếp theo trong MRO."

Đây gọi là:

> **Cooperative inheritance**

---

# 18. Dataclass + `__post_init__()` + MRO

Bây giờ kết hợp mọi thứ.

```python
@dataclass
class A:

    def __post_init__(self):
        print("A")
```

```python
@dataclass
class B(A):

    def __post_init__(self):
        print("B")
        super().__post_init__()
```

```python
@dataclass
class C(A):

    def __post_init__(self):
        print("C")
        super().__post_init__()
```

```python
@dataclass
class D(B, C):

    def __post_init__(self):
        print("D")
        super().__post_init__()
```

MRO:

```text
D → B → C → A → object
```

---

# 19. Kết quả

```python
D()
```

sẽ conceptually:

```text
D
B
C
A
```

Đây là pattern cực kỳ quan trọng.

Không phải:

```text
D
B
A
C
A
```

và cũng không phải:

```text
D
B
C
```

---

# 20. Vì sao `A` chỉ chạy một lần?

Vì:

```python
super()
```

không có nghĩa:

```text
gọi parent của class hiện tại
```

mà là:

```text
tiếp tục từ vị trí hiện tại trong MRO
```

MRO:

```text
D
 ↓
B
 ↓
C
 ↓
A
```

Luồng:

```text
D.super()
   ↓
B

B.super()
   ↓
C

C.super()
   ↓
A
```

---

# 21. Đây là lý do không nên hard-code parent

Không tốt:

```python
def __post_init__(self):
    B.__post_init__(self)
```

hoặc:

```python
A.__post_init__(self)
```

Trong multiple inheritance, cách này phá vỡ cooperative chain.

Nên:

```python
def __post_init__(self):
    super().__post_init__()
```

---

# 22. Nhưng có một vấn đề với Dataclass

Giả sử:

```python
@dataclass
class A:
    x: int

    def __post_init__(self):
        print("A")
```

```python
@dataclass
class B(A):
    y: int

    def __post_init__(self):
        print("B")
        super().__post_init__()
```

```python
@dataclass
class C(A):
    z: int

    def __post_init__(self):
        print("C")
        super().__post_init__()
```

```python
@dataclass
class D(B, C):
    w: int
```

`D` **không tự động sinh `__post_init__()` gọi cả chain theo kiểu bạn mong muốn nếu không có method thích hợp ở D?**

Điều cần nhớ là dataclass-generated `__init__()` chỉ gọi:

```python
self.__post_init__()
```

nếu `__post_init__` được phát hiện trong class hierarchy.

Nếu method được resolve tới `B.__post_init__`, chain cooperative của B → C → A có thể chạy.

---

# 23. Cooperative pattern

Một pattern tốt:

```python
@dataclass
class Base:

    def __post_init__(self):
        pass
```

Sau đó:

```python
@dataclass
class A(Base):

    def __post_init__(self):
        print("A")
        super().__post_init__()
```

```python
@dataclass
class B(Base):

    def __post_init__(self):
        print("B")
        super().__post_init__()
```

và:

```python
@dataclass
class C(A, B):

    def __post_init__(self):
        print("C")
        super().__post_init__()
```

MRO:

```text
C
A
B
Base
object
```

Kết quả:

```text
C
A
B
```

---

# 24. Tại sao cần Base no-op?

Đây là một kỹ thuật thiết kế.

Nếu:

```python
Base.__post_init__
```

không tồn tại, một class cuối cùng gọi:

```python
super().__post_init__()
```

có thể gặp:

```text
AttributeError
```

Một base cooperative có thể cung cấp:

```python
def __post_init__(self):
    pass
```

để kết thúc chain an toàn.

---

# 25. Nhưng đừng lạm dụng Mixin

Một pattern phổ biến:

```python
@dataclass
class TimestampMixin:
    created_at: datetime


@dataclass
class IDMixin:
    id: int


@dataclass
class Entity(
    TimestampMixin,
    IDMixin
):
    name: str
```

Đây có thể là thiết kế tốt nếu các mixin:

* nhỏ,
* độc lập,
* có trách nhiệm rõ ràng.

---

# 26. Mixin là gì?

Mixin thường không đại diện cho một entity hoàn chỉnh.

Ví dụ:

```text
TimestampMixin
IDMixin
SerializableMixin
ValidationMixin
```

Chúng cung cấp một capability.

Ví dụ:

```text
User
 ├── IDMixin
 ├── TimestampMixin
 └── SerializableMixin
```

---

# 27. Mixin + Dataclass

Ví dụ:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimestampMixin:

    created_at: datetime
```

```python
@dataclass
class IdentifiableMixin:

    id: int
```

```python
@dataclass
class User(
    IdentifiableMixin,
    TimestampMixin
):

    name: str
```

User có:

```text
id
created_at
name
```

---

# 28. Vấn đề default trong Multiple Inheritance

Đây là vùng dễ xảy ra lỗi.

Ví dụ:

```python
@dataclass
class A:
    x: int = 10
```

```python
@dataclass
class B:
    y: int
```

```python
@dataclass
class C(A, B):
    z: int
```

Bạn có thể gặp lỗi liên quan đến:

```text
non-default argument
after default argument
```

Bởi vì field từ nhiều base được merge thành constructor.

---

# 29. Cách an toàn: Keyword-only

Một chiến lược tốt cho mixin:

```python
@dataclass
class TimestampMixin:

    created_at: datetime = field(
        kw_only=True
    )
```

hoặc:

```python
@dataclass(kw_only=True)
class TimestampMixin:
    created_at: datetime
```

Điều này giảm coupling giữa thứ tự field của các parent.

---

# 30. Multiple inheritance + `frozen`

Giả sử:

```python
@dataclass(frozen=True)
class A:
    x: int
```

và:

```python
@dataclass(frozen=True)
class B:
    y: int
```

thì:

```python
@dataclass(frozen=True)
class C(A, B):
    z: int
```

là một hierarchy immutable nhất quán.

Nhưng:

```python
A frozen
B non-frozen
C frozen/non-frozen
```

cần cực kỳ cẩn thận vì các quy tắc frozen inheritance hạn chế việc trộn trạng thái mutable/immutable.

Nguyên tắc thực tế:

> **Trong một hierarchy cooperative, nên giữ policy `frozen` nhất quán.**

---

# 31. Multiple inheritance + `slots`

Ví dụ:

```python
@dataclass(slots=True)
class A:
    x: int
```

```python
@dataclass(slots=True)
class B:
    y: int
```

```python
@dataclass(slots=True)
class C(A, B):
    z: int
```

Đây là nơi cần đặc biệt cẩn thận.

Multiple inheritance + `__slots__` có những giới hạn của Python object layout.

Không phải mọi combination của:

```text
slots
+
multiple inheritance
```

đều hợp lệ.

Có thể gặp:

```text
TypeError
```

liên quan tới layout conflict.

---

# 32. Vì vậy đừng mặc định dùng nhiều mixin slots

Nếu hệ thống phức tạp:

```text
A(slots=True)
B(slots=True)
C(A, B, slots=True)
```

hãy kiểm tra thực tế.

Đặc biệt nếu các base có layout khác nhau hoặc có `__dict__`/`__weakref__`.

---

# 33. `InitVar` + Multiple Inheritance

Đây là phần nâng cao.

Ví dụ:

```python
@dataclass
class A:

    config: InitVar[dict]

    def __post_init__(self, config):
        ...
```

và:

```python
@dataclass
class B:

    parser: InitVar[object]

    def __post_init__(self, parser):
        ...
```

Nếu:

```python
@dataclass
class C(A, B):
    ...
```

thì `__post_init__()` phải xử lý các InitVar theo constructor/field ordering của hierarchy.

Đây là lý do:

> **Multiple inheritance + InitVar rất dễ trở thành API khó bảo trì.**

Trong thiết kế thực tế, nếu có quá nhiều `InitVar`, nên xem xét composition hoặc explicit factory.

---

# 34. Multiple Inheritance và field override

Ví dụ:

```python
@dataclass
class A:
    value: int
```

```python
@dataclass
class B:
    value: float
```

```python
@dataclass
class C(A, B):
    pass
```

Đây là thiết kế đáng nghi.

Tại sao?

Vì:

```text
A nói:
value là int

B nói:
value là float
```

Child:

```text
C
```

phải mang một semantic rõ ràng.

Không nên tạo hierarchy kiểu này chỉ vì Python cho phép.

---

# 35. Multiple inheritance nên dùng khi nào?

Rất phù hợp với:

### Mixins

```text
IdentifiableMixin
TimestampMixin
SerializableMixin
```

### Orthogonal behavior

Các capability độc lập.

Ví dụ:

```text
Entity
+
Timestamp
+
Serialization
```

---

# 36. Khi nào không nên dùng?

Không nên dùng để biểu diễn:

```text
Novel
    ↓
Chapter
```

vì:

```text
Chapter IS-A Novel
```

là sai.

Chapter:

```text
Novel HAS-A Chapter
```

Đây là composition.

---

# 37. Crawler Framework của chúng ta

Trong crawler của bạn, thiết kế tốt hơn có thể là:

```text
                 BaseEntity
                    │
          ┌─────────┴─────────┐
          │                   │
       Novel                Author
          │
       chapters
          │
       Chapter
```

thay vì:

```text
Novel
 ↓
Chapter
 ↓
Author
```

Vì đây là quan hệ domain khác nhau.

---

# 38. Mixin phù hợp hơn

Ví dụ:

```python
@dataclass
class IdentifiableMixin:

    id: int
```

```python
@dataclass
class SourceMixin:

    source: str
```

```python
@dataclass
class Novel(
    IdentifiableMixin,
    SourceMixin
):

    title: str
```

Ở đây:

```text
Novel
 ├── Identifiable
 └── Source
```

có ý nghĩa.

---

# 39. Một ví dụ hoàn chỉnh

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IdentifiableMixin:

    id: int

    def __post_init__(self):
        if self.id <= 0:
            raise ValueError(
                "id must be positive"
            )

        super().__post_init__()
```

```python
@dataclass
class TimestampMixin:

    created_at: datetime

    def __post_init__(self):

        if self.created_at is None:
            raise ValueError(
                "created_at is required"
            )

        super().__post_init__()
```

Base cooperative:

```python
@dataclass
class BaseMixin:

    def __post_init__(self):
        pass
```

Ta có thể thiết kế hierarchy cooperative từ base này.

---

# 40. Nhưng thứ tự Base rất quan trọng

Nếu:

```python
class Novel(
    IdentifiableMixin,
    TimestampMixin,
    BaseMixin
):
    ...
```

MRO:

```text
Novel
IdentifiableMixin
TimestampMixin
BaseMixin
object
```

Nếu đổi:

```python
class Novel(
    TimestampMixin,
    IdentifiableMixin,
    BaseMixin
):
```

MRO trở thành:

```text
Novel
TimestampMixin
IdentifiableMixin
BaseMixin
object
```

Do đó thứ tự base class **có ý nghĩa**.

---

# 41. Đây là lý do `super()` mạnh hơn `Parent.method()`

Nếu dùng:

```python
IdentifiableMixin.__post_init__(self)
```

bạn đang hard-code hierarchy.

Nếu dùng:

```python
super().__post_init__()
```

Python đi theo MRO.

Do đó cooperative multiple inheritance yêu cầu:

```text
Mọi class:
    làm phần mình
    ↓
    super()
```

---

# 42. Mô hình tư duy quan trọng

Hãy nhớ:

```text
class D(B, C)
```

không có nghĩa đơn giản:

```text
D
 ├── B
 └── C
```

Mà Python xây một **linear order**:

```text
D → B → C → A → object
```

Mọi:

```python
super()
```

đều di chuyển dọc theo order đó.

---

# 43. Bài tập 1 — MRO

Viết:

```python
class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass
```

Sau đó:

```python
print(D.__mro__)
```

Tự giải thích tại sao có:

```text
D
B
C
A
object
```

---

# 44. Bài tập 2 — Cooperative `__post_init__`

Tạo:

```python
@dataclass
class A:
    def __post_init__(self):
        print("A")
```

```python
@dataclass
class B(A):
    def __post_init__(self):
        print("B")
        super().__post_init__()
```

```python
@dataclass
class C(A):
    def __post_init__(self):
        print("C")
        super().__post_init__()
```

```python
@dataclass
class D(B, C):
    def __post_init__(self):
        print("D")
        super().__post_init__()
```

Dự đoán:

```text
?
```

trước khi chạy.

---

# 45. Bài tập 3 — Mixin

Thiết kế:

```text
IdentifiableMixin
TimestampMixin
Novel
```

`Novel` phải có:

```python
id
created_at
title
```

Mỗi mixin phải validation phần của mình và dùng:

```python
super().__post_init__()
```

---

# 46. Bài tập 4 — Field conflict

Tạo:

```python
@dataclass
class A:
    value: int = 10
```

```python
@dataclass
class B:
    value: str = "hello"
```

```python
@dataclass
class C(A, B):
    pass
```

Kiểm tra:

```python
C.__dataclass_fields__["value"]
```

và:

```python
C().value
```

Sau đó giải thích **field nào thắng và tại sao**.

---

# 47. Bài tập 5 — Crawler

Thiết kế:

```text
               EntityMixin
              /           \
             /             \
     Identifiable       SourceAware
             \             /
              \           /
                 Novel
```

`Novel` cần:

```text
id
source
title
```

Mỗi mixin:

* validate field của mình
* sử dụng `super().__post_init__()`

Sau đó kiểm tra:

```python
print(Novel.__mro__)
```

và theo dõi thứ tự `__post_init__()`.

---

# 48. Những điều cần nhớ sau Buổi 12

### 1. MRO

```python
Class.__mro__
```

cho biết thứ tự Python tìm method.

---

### 2. `super()`

Không đơn giản là:

```text
parent
```

mà là:

```text
next class in MRO
```

---

### 3. Dataclass field merge

Field inheritance có logic riêng, không nên đồng nhất máy móc với method lookup.

---

### 4. Cooperative inheritance

Pattern:

```python
def __post_init__(self):
    # own logic
    super().__post_init__()
```

là nền tảng cho multiple inheritance.

---

### 5. Diamond

```text
      A
     / \
    B   C
     \ /
      D
```

Python dùng C3 MRO để tạo:

```text
D → B → C → A → object
```

---

### 6. Mixin

Multiple inheritance phù hợp nhất khi các parent là **capability độc lập**, ví dụ:

```text
IdentifiableMixin
TimestampMixin
SerializableMixin
```

---

### 7. Composition

Nếu quan hệ là:

```text
HAS-A
```

hãy ưu tiên composition.

Ví dụ:

```python
@dataclass
class Novel:
    author: Author
```

thay vì inheritance.

---

## Vị trí hiện tại trong roadmap

```text
Phần I — Foundation
...
Buổi 9  InitVar             ✅
Buổi 10 __post_init__       ✅
--------------------------------
Phần II — Advanced
Buổi 11 Inheritance         ✅
Buổi 12 Multiple Inheritance + MRO  ← DONE
Buổi 13 Composition         ← tiếp theo
Buổi 14 Recursive Dataclass
Buổi 15 Generic Dataclass
Buổi 16 Abstract Dataclass
...
```

**Buổi 13 — Composition** sẽ rất quan trọng đối với hướng xây dựng **crawler framework**, vì chúng ta sẽ chuyển từ tư duy:

```text
Inheritance
    ↓
"is-a"
```

sang:

```text
Composition
    ↓
"has-a"
```

và xây các dataclass lồng nhau kiểu:

```text
Novel
 ├── Author
 │    └── Address
 │
 ├── Publisher
 │    └── Address
 │
 └── chapters
      ├── Chapter
      ├── Chapter
      └── Chapter
```

đúng với domain crawler mà bạn đang xây dựng.
