# Dataclass Deep Dive — Buổi 19

# Metaclass + Dataclass

Buổi này chúng ta đi vào một trong những tầng sâu nhất của Python:

```text
class definition
      ↓
Metaclass
      ↓
Class object được tạo
      ↓
Decorator
      ↓
@dataclass
      ↓
Generated methods
```

Nếu Buổi 18 giúp bạn hiểu:

```text
attribute
    ↓
descriptor
```

thì Buổi 19 giúp bạn hiểu:

```text
class
    ↓
metaclass
```

Đây là nền tảng cực kỳ quan trọng nếu sau này bạn muốn tự xây:

* ORM
* Validation framework
* Plugin framework
* Dependency Injection
* Mini framework
* Mini ORM
* `@my_dataclass`

---

# 1. Class trong Python thực chất là gì?

Ta thường viết:

```python
class User:
    name: str
```

và nghĩ:

```text
User = class
```

Nhưng chính xác hơn:

> `User` là một **object**.

Kiểm tra:

```python
print(type(User))
```

Kết quả thông thường:

```text
<class 'type'>
```

Tức là:

```text
User
 ↓
object
 ↓
type
```

---

# 2. `type` là gì?

`type` chính là metaclass mặc định của phần lớn class Python.

Ví dụ:

```python
class User:
    pass
```

Python conceptually tạo:

```python
User = type(
    "User",
    (),
    {}
)
```

Tức là:

```text
class User:
    pass
```

về mặt concept có thể hình dung như:

```text
type("User", bases, namespace)
```

---

# 3. Metaclass là gì?

Nếu:

```text
class
```

là object được tạo ra bởi:

```text
metaclass
```

thì:

```text
metaclass
```

là:

> class của class.

Ví dụ:

```python
class User:
    pass
```

Ta có:

```text
User
  │
  ▼
type
```

Do đó:

```python
type(User)
```

là:

```text
type
```

---

# 4. Tại sao cần Metaclass?

Metaclass cho phép bạn can thiệp vào:

```text
quá trình tạo class
```

Ví dụ:

```python
class User:
    name: str
```

Bạn có thể:

```text
phát hiện fields
validate class
đăng ký class
thêm method
sửa namespace
tạo metadata
```

ngay khi `User` được tạo.

---

# 5. Class Creation Pipeline

Đây là phần quan trọng nhất của Buổi 19.

Khi Python gặp:

```python
class User:
    name: str
```

conceptually:

```text
① Xác định metaclass
        ↓
② __prepare__()
        ↓
③ thực thi class body
        ↓
④ tạo namespace
        ↓
⑤ metaclass.__new__()
        ↓
⑥ metaclass.__init__()
        ↓
⑦ class object hoàn thành
        ↓
⑧ decorator được áp dụng
```

Đặc biệt:

```text
@dataclass
```

là **decorator**, không phải metaclass.

---

# 6. Một ví dụ Metaclass tối thiểu

```python
class Meta(type):

    def __new__(mcls, name, bases, namespace):
        print("Creating:", name)

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
class User(metaclass=Meta):
    pass
```

Output:

```text
Creating: User
```

---

# 7. `Meta` là class

Ta có:

```python
class Meta(type):
    ...
```

Nghĩa là:

```text
Meta
 ↓
type
```

Còn:

```python
class User(metaclass=Meta):
```

thì:

```text
User
 ↓
Meta
```

Sơ đồ:

```text
          type
           ↑
           │
          Meta
           ↑
           │
          User
```

---

# 8. `__new__` của Metaclass

```python
class Meta(type):

    def __new__(
        mcls,
        name,
        bases,
        namespace,
    ):
        ...
```

Các tham số:

### `mcls`

Metaclass:

```text
Meta
```

### `name`

Tên class:

```text
"User"
```

### `bases`

Base classes:

```python
()
```

hoặc:

```python
(Base,)
```

### `namespace`

Dictionary chứa class body:

```python
{
    "__module__": ...,
    "__qualname__": ...,
    ...
}
```

---

# 9. Inspect Namespace

```python
class Meta(type):

    def __new__(mcls, name, bases, namespace):

        print(name)
        print(bases)
        print(namespace)

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

```python
class User(metaclass=Meta):

    name: str

    def hello(self):
        return "hello"
```

Namespace sẽ chứa conceptually:

```text
{
    "__module__": ...,
    "__qualname__": "User",
    "__annotations__": {
        "name": str
    },
    "hello": <function ...>
}
```

---

# 10. Đây chính là điều Dataclass quan tâm

Khi bạn viết:

```python
@dataclass
class User:
    name: str
    age: int
```

class namespace có:

```python
__annotations__
```

conceptually:

```python
{
    "name": str,
    "age": int,
}
```

Dataclass sử dụng thông tin này để xác định fields.

---

# 11. Decorator vs Metaclass

Đây là distinction cực kỳ quan trọng.

### Metaclass

Can thiệp khi:

```text
class object đang được tạo
```

### Decorator

Nhận:

```text
class object đã được tạo
```

rồi:

```text
biến đổi / trả về class
```

Ví dụ:

```python
@dataclass
class User:
    name: str
```

conceptually:

```python
class User:
    name: str

User = dataclass(User)
```

---

# 12. Thứ tự thực tế

Hãy nhớ:

```text
class User:
    ...
```

trước tiên class phải được tạo.

Sau đó:

```text
@dataclass
```

mới nhận class.

Conceptually:

```text
class body
   ↓
metaclass
   ↓
User class object
   ↓
dataclass(User)
   ↓
modified User
```

Đây là điểm rất dễ nhầm.

---

# 13. Metaclass + Dataclass

Ta thử:

```python
from dataclasses import dataclass


class Meta(type):

    def __new__(mcls, name, bases, namespace):

        print(
            "annotations:",
            namespace.get("__annotations__")
        )

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )


@dataclass
class User(metaclass=Meta):

    name: str
    age: int
```

Metaclass nhìn thấy:

```python
{
    "name": str,
    "age": int,
}
```

Nhưng lúc `Meta.__new__()` chạy:

```python
__init__
```

do dataclass generate **chưa tồn tại**.

Đây là một insight quan trọng.

---

# 14. Kiểm tra

Trong metaclass:

```python
class Meta(type):

    def __new__(mcls, name, bases, namespace):

        print("__init__ =", namespace.get("__init__"))

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Với:

```python
@dataclass
class User(metaclass=Meta):
    name: str
```

Metaclass thường thấy:

```text
__init__ = None
```

hoặc không có generated dataclass initializer.

Sau đó decorator mới generate.

---

# 15. Điều này dẫn tới một lỗi thiết kế phổ biến

Bạn có thể nghĩ:

```python
class Meta(type):

    def __new__(...):
        inspect(User.__init__)
```

để lấy generated dataclass constructor.

Nhưng:

> Metaclass chạy trước `@dataclass`.

Vì vậy nó không nên giả định dataclass đã generate methods.

---

# 16. Nếu cần inspect sau Dataclass

Có thể dùng decorator khác:

```python
def inspect_dataclass(cls):

    print(cls.__init__)

    return cls
```

```python
@inspect_dataclass
@dataclass
class User:
    name: str
```

Decorator gần class chạy trước.

Thứ tự decorator:

```python
@A
@B
class User:
    ...
```

tương đương:

```python
User = A(B(User))
```

Vì vậy:

```text
class
 ↓
B
 ↓
A
```

---

# 17. Metaclass có thể đăng ký class

Đây là ứng dụng cực kỳ phổ biến.

```python
registry = {}
```

Metaclass:

```python
class PluginMeta(type):

    def __new__(mcls, name, bases, namespace):

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )

        registry[name] = cls

        return cls
```

Plugin:

```python
class NovelPlugin(metaclass=PluginMeta):
    pass
```

Registry:

```python
print(registry)
```

Concept:

```text
NovelPlugin
     ↓
PluginMeta
     ↓
registry
```

---

# 18. Dataclass Plugin

Ta có thể kết hợp:

```python
from dataclasses import dataclass


registry = {}


class PluginMeta(type):

    def __new__(mcls, name, bases, namespace):

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )

        registry[name] = cls

        return cls


@dataclass
class NovelPlugin(
    metaclass=PluginMeta
):
    name: str
```

Bây giờ:

```text
PluginMeta
    ↓
tạo NovelPlugin
    ↓
dataclass decorator
    ↓
generate __init__
```

Registry chứa class.

---

# 19. Nhưng Registry không biết Dataclass fields

Tại thời điểm:

```python
PluginMeta.__new__
```

ta có:

```python
__annotations__
```

nhưng chưa chắc có:

```python
dataclasses.fields(cls)
```

vì `@dataclass` chưa chạy.

Do đó:

```text
Metaclass
 ↓
class registration
```

và:

```text
Dataclass
 ↓
field transformation
```

là hai phase khác nhau.

---

# 20. `__prepare__`

Một metaclass còn có:

```python
def __prepare__(
    mcls,
    name,
    bases,
):
    ...
```

Nó được gọi trước khi class body chạy.

Concept:

```text
metaclass
   ↓
__prepare__()
   ↓
namespace
   ↓
execute class body
   ↓
__new__()
```

---

# 21. Ví dụ

```python
class Meta(type):

    @classmethod
    def __prepare__(mcls, name, bases):
        print("PREPARE")

        return {}
```

```python
class User(metaclass=Meta):
    print("BODY")
```

Thứ tự:

```text
PREPARE
BODY
```

sau đó mới đến:

```text
__new__
```

---

# 22. Vì sao `__prepare__` quan trọng?

Nó cho phép metaclass kiểm soát namespace được sử dụng trong class body.

Framework có thể dùng để:

```text
capture declaration order
collect fields
register commands
collect routes
collect ORM columns
```

---

# 23. Dataclass và Declaration Order

Dataclass rất quan tâm thứ tự field:

```python
@dataclass
class User:
    name: str
    age: int
    email: str
```

Constructor:

```python
User(
    name,
    age,
    email,
)
```

Thứ tự này phải được giữ.

Python hiện đại đảm bảo class namespace có thứ tự insertion.

Do đó:

```python
__annotations__
```

giữ:

```text
name
age
email
```

theo thứ tự khai báo.

---

# 24. `__init_subclass__`

Có một cơ chế khác cần biết:

```python
class Base:

    def __init_subclass__(cls):
        print("Subclass:", cls.__name__)
```

```python
class User(Base):
    pass
```

Output:

```text
Subclass: User
```

Nó chạy khi subclass được tạo.

---

# 25. `__init_subclass__` vs Metaclass

Có thể hình dung:

```text
__init_subclass__
    ↓
hook cho subclass

Metaclass
    ↓
kiểm soát class creation
```

Nếu chỉ cần:

```text
register subclass
validate subclass
configure subclass
```

thì `__init_subclass__` thường đơn giản hơn metaclass.

---

# 26. Một nguyên tắc quan trọng

> **Không dùng Metaclass nếu Decorator hoặc `__init_subclass__` đã giải quyết được vấn đề.**

Metaclass là công cụ mạnh nhưng dễ làm framework khó hiểu.

---

# 27. Dataclass + `__init_subclass__`

Ví dụ:

```python
class Entity:

    def __init_subclass__(cls):
        print(
            "Created:",
            cls.__name__,
        )
```

```python
@dataclass
class User(Entity):
    name: str
```

`__init_subclass__` chạy trong quá trình class creation.

Sau đó:

```text
@dataclass
```

mới transform class.

---

# 28. Một vấn đề với `slots=True`

Đây là một chi tiết rất thú vị.

Khi:

```python
@dataclass(slots=True)
class User:
    name: str
```

dataclass không chỉ đơn giản "thêm `__slots__`".

Nó có thể tạo/trả về một class phù hợp với slots transformation.

Điều này có nghĩa:

```text
Decorator transformation
```

có thể ảnh hưởng tới interaction với:

```text
Metaclass
__init_subclass__
```

Đây là lý do cần hiểu pipeline thay vì coi `@dataclass` chỉ là một annotation tiện lợi.

---

# 29. Metaclass + `slots`

Nếu metaclass:

```python
class Meta(type):

    def __new__(mcls, name, bases, namespace):
        print("CREATE", name)

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

và:

```python
@dataclass(slots=True)
class User(metaclass=Meta):
    name: str
```

có thể quan sát thấy class creation behavior khác với dataclass thông thường.

Đây là một ví dụ tốt cho việc:

> Decorator có thể tạo/thay thế class sau khi metaclass đã tham gia vào class creation ban đầu.

---

# 30. Metaclass dùng để validate class

Ví dụ:

```python
class ModelMeta(type):

    def __new__(mcls, name, bases, namespace):

        annotations = namespace.get(
            "__annotations__",
            {}
        )

        if "id" not in annotations:
            raise TypeError(
                f"{name} must define id"
            )

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

Sau đó:

```python
@dataclass
class User(metaclass=ModelMeta):
    id: int
    name: str
```

OK.

Nhưng:

```python
@dataclass
class Product(metaclass=ModelMeta):
    name: str
```

fail ngay khi class được tạo.

---

# 31. Đây là Class-level Validation

So sánh:

### Instance validation

```python
@dataclass
class User:

    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError
```

Kiểm tra:

```text
User(age=-1)
```

### Class validation

Metaclass:

```text
class User:
    ...
```

kiểm tra:

```text
id field có tồn tại?
```

Hai tầng:

```text
Class validation
        ↓
Instance validation
```

---

# 32. Metaclass + Dataclass Field Inspection

Nếu muốn inspect field sau khi dataclass hoàn thành, có thể dùng decorator:

```python
from dataclasses import dataclass, fields


def inspect_fields(cls):

    for f in fields(cls):
        print(f.name, f.type)

    return cls
```

Dùng:

```python
@inspect_fields
@dataclass
class User:
    id: int
    name: str
```

Pipeline:

```text
class creation
 ↓
metaclass
 ↓
dataclass
 ↓
inspect_fields
```

Bây giờ `fields(cls)` hoạt động.

---

# 33. Metaclass + Dataclass Framework

Nếu xây framework lớn, có thể có kiến trúc:

```text
                  Python class creation
                          │
                          ▼
                     Metaclass
                          │
               class-level validation
                          │
                          ▼
                    @dataclass
                          │
                  field processing
                          │
                          ▼
                  generated methods
                          │
                          ▼
                    framework hook
```

Đây là kiến trúc framework thực tế.

---

# 34. Mini ORM Concept

Hãy tưởng tượng:

```python
@dataclass
class User(Model):
    id: int
    name: str
```

Framework muốn tự động:

```text
User
 ↓
table name = "user"
 ↓
fields
 ↓
SQL columns
```

Có thể dùng:

```text
Metaclass
+
Dataclass
+
Metadata
+
Descriptor
```

Đây chính là nền tảng của ORM.

---

# 35. Nhưng đừng làm tất cả bằng Metaclass

Một framework tốt có thể chia:

```text
Metaclass
    ↓
class registration

Dataclass
    ↓
data model

Metadata
    ↓
configuration

Descriptor
    ↓
runtime behavior

Repository
    ↓
persistence
```

Mỗi cơ chế có một trách nhiệm.

---

# 36. `type()` và Metaclass

Bạn có thể tạo class trực tiếp:

```python
User = type(
    "User",
    (),
    {
        "hello": lambda self: "hello"
    }
)
```

Với metaclass:

```python
class Meta(type):
    ...
```

thì:

```python
User = Meta(
    "User",
    (),
    namespace,
)
```

Đây là cầu nối trực tiếp tới Buổi 20:

> `make_dataclass()` và Dynamic Dataclass.

---

# 37. `dataclass()` bản chất là function

Điều này rất đáng nhớ:

```python
from dataclasses import dataclass
```

`dataclass` là decorator function.

Conceptually:

```python
User = dataclass(User)
```

Nó nhận class và biến đổi class.

Trong khi:

```python
class Meta(type):
```

là metaclass.

Hai cơ chế:

```text
Metaclass
   ↓
class creation

Decorator
   ↓
class transformation
```

---

# 38. Tự mô phỏng Dataclass

Một decorator đơn giản:

```python
def my_dataclass(cls):

    annotations = cls.__annotations__

    def __init__(self, **kwargs):

        for name in annotations:
            setattr(
                self,
                name,
                kwargs[name],
            )

    cls.__init__ = __init__

    return cls
```

Dùng:

```python
@my_dataclass
class User:
    name: str
    age: int
```

Concept:

```text
annotations
    ↓
generate __init__
    ↓
modify class
```

---

# 39. Nếu thêm Metaclass

Ta có:

```python
class Meta(type):

    def __new__(mcls, name, bases, namespace):

        print(
            "Before decorator:",
            namespace.get(
                "__annotations__"
            )
        )

        return super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )
```

và:

```python
@my_dataclass
class User(metaclass=Meta):
    name: str
    age: int
```

Flow:

```text
Meta
 ↓
User class
 ↓
my_dataclass
 ↓
generated __init__
```

Đây là bản chất của interaction.

---

# 40. Tại sao hiểu điều này quan trọng?

Vì khi gặp framework:

```python
@something
class User(Model):
    ...
```

bạn không còn nghĩ:

> "Python magic."

Bạn có thể phân tích:

```text
Who creates the class?
        ↓
metaclass

Who transforms the class?
        ↓
decorator

Who controls attribute access?
        ↓
descriptor

Who stores configuration?
        ↓
metadata

Who generates methods?
        ↓
decorator/framework
```

Đây chính là tư duy framework engineer.

---

# 41. So sánh 4 cơ chế

| Cơ chế              | Thời điểm                | Vai trò           |
| ------------------- | ------------------------ | ----------------- |
| Metaclass           | Class creation           | Kiểm soát class   |
| `__init_subclass__` | Subclass creation        | Hook subclass     |
| Decorator           | Sau class creation       | Transform class   |
| Descriptor          | Runtime attribute access | Control attribute |

Sơ đồ:

```text
class User:
    │
    ▼
Metaclass
    │
    ▼
Class object
    │
    ▼
Decorator
    │
    ▼
Final class
    │
    ▼
instance
    │
    ▼
Descriptor
```

---

# 42. Một Framework Pattern rất mạnh

```python
class ModelMeta(type):

    def __new__(mcls, name, bases, namespace):
        annotations = namespace.get(
            "__annotations__",
            {}
        )

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
        )

        cls.__model_fields__ = annotations

        return cls
```

Sau đó:

```python
@dataclass
class User(metaclass=ModelMeta):
    id: int
    name: str
```

Framework có:

```python
User.__model_fields__
```

conceptually:

```python
{
    "id": int,
    "name": str,
}
```

---

# 43. Nhưng đây chưa phải Dataclass Fields

Đừng nhầm:

```python
__annotations__
```

với:

```python
dataclasses.fields()
```

`__annotations__` chỉ là type annotations.

Dataclass field còn chứa:

```text
default
default_factory
init
repr
compare
hash
metadata
kw_only
```

Do đó framework thật sự cần hiểu cả:

```text
annotations
+
Field objects
```

---

# 44. Một bài toán quan trọng

Giả sử:

```python
@dataclass
class User(metaclass=Meta):

    id: int

    name: str = "Unknown"
```

Metaclass có thể thấy:

```text
__annotations__
id → int
name → str
```

và namespace có:

```text
name → "Unknown"
```

Nhưng:

```python
dataclasses.fields(User)
```

chỉ có đầy đủ dataclass semantics sau khi decorator chạy.

Đây là lý do framework cần quyết định:

```text
inspect trước dataclass?
hay
inspect sau dataclass?
```

---

# 45. Quy tắc thực chiến

Nếu mục tiêu là:

### Class registration

Dùng:

```text
Metaclass
```

### Subclass registration

Dùng:

```text
__init_subclass__
```

### Transform dataclass

Dùng:

```text
decorator
```

### Attribute validation

Dùng:

```text
Descriptor
```

### Declarative configuration

Dùng:

```text
field(metadata=...)
```

Không gom tất cả vào metaclass.

---

# 46. Bài tập Buổi 19

## Bài 1 — Trace class creation

Viết:

```python
class Meta(type):

    def __prepare__(...):
        ...

    def __new__(...):
        ...

    def __init__(...):
        ...
```

Sau đó:

```python
class User(metaclass=Meta):
    name: str
```

In ra thứ tự:

```text
PREPARE
BODY
NEW
INIT
```

---

# 47. Bài 2 — Dataclass pipeline

Viết:

```python
class Meta(type):
    ...
```

và:

```python
@dataclass
class User(metaclass=Meta):
    name: str
```

Kiểm tra trong metaclass:

```python
__annotations__
__init__
__repr__
```

Sau đó kiểm tra lại **sau khi `@dataclass` chạy**.

Mục tiêu:

> Tự chứng minh generated methods của dataclass chưa tồn tại ở thời điểm metaclass xử lý class body.

---

# 48. Bài 3 — Model Registry

Viết:

```python
registry = {}
```

và:

```python
class ModelMeta(type):
    ...
```

Tất cả:

```python
@dataclass
class User(metaclass=ModelMeta):
    id: int
```

```python
@dataclass
class Novel(metaclass=ModelMeta):
    id: int
    title: str
```

đều phải tự động đăng ký.

Kết quả:

```text
registry
 ├── User
 └── Novel
```

---

# 49. Bài 4 — Class Validation

Viết metaclass bắt buộc mọi model phải có:

```python
id: int
```

Ví dụ hợp lệ:

```python
@dataclass
class User(metaclass=ModelMeta):
    id: int
    name: str
```

Không hợp lệ:

```python
@dataclass
class User(metaclass=ModelMeta):
    name: str
```

Phải raise:

```python
TypeError
```

**ngay khi class được định nghĩa**, không phải khi tạo instance.

---

# 50. Bài 5 — Mini Dataclass Framework

Kết hợp:

```text
Metaclass
+
Dataclass
+
Descriptor
+
Metadata
```

Thiết kế:

```python
@dataclass
class User(metaclass=ModelMeta):

    id: int

    name: str = field(
        metadata={
            "required": True
        }
    )
```

Framework phải có khả năng:

```text
1. Register Model
2. Discover fields
3. Read metadata
4. Validate class
5. Validate instance
```

Đây chính là bài tập chuẩn bị cho **Buổi 20 và Phần III**.

---

# 51. Mental Model cuối buổi

Hãy ghi nhớ chính xác pipeline này:

```text
                class User
                    │
                    ▼
             determine metaclass
                    │
                    ▼
             Meta.__prepare__
                    │
                    ▼
              execute body
                    │
                    ▼
              Meta.__new__
                    │
                    ▼
              Meta.__init__
                    │
                    ▼
             User class object
                    │
                    ▼
               @dataclass
                    │
                    ▼
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
    __init__      __repr__       __eq__
                    │
                    ▼
               final class
                    │
                    ▼
                User(...)
                    │
                    ▼
              Descriptor access
```

Đây là **bức tranh tổng thể** của những gì chúng ta đã học từ Buổi 1 → 19.

---

# 52. Roadmap

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ✅
16. Abstract Dataclass            ✅
17. Protocols                    ✅
18. Descriptors                  ✅
19. Metaclass + Dataclass        ✅ ← hôm nay
20. Dynamic Dataclass            ← tiếp theo
```

**Buổi 20** sẽ đi vào `make_dataclass()` và Dynamic Dataclass: tạo dataclass **hoàn toàn tại runtime**, tự xây fields từ schema/dictionary/database metadata, rồi tiến tới việc hiểu cách xây một hệ thống kiểu:

```text
Database Schema
      ↓
Field Definitions
      ↓
make_dataclass()
      ↓
Runtime Model
      ↓
Repository
```

Đây sẽ là cầu nối trực tiếp sang **Phần III — Serialization**.
