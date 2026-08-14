# Dataclass Deep Dive — Buổi 18

# Descriptors + `property` + Validator + Custom Field

Buổi 18 là một trong những buổi **quan trọng nhất về internals của Dataclass**.

Từ đây chúng ta bắt đầu chuyển từ:

```text
@dataclass
class User:
    name: str
```

sang việc hiểu sâu:

```text
attribute access
      ↓
descriptor
      ↓
property
      ↓
validation
      ↓
dataclass field
      ↓
custom field
```

Mục tiêu cuối buổi:

* Hiểu Descriptor Protocol.
* Hiểu `__get__`, `__set__`, `__delete__`.
* Hiểu `property` thực chất là descriptor.
* Hiểu tại sao descriptor có thể làm validator.
* Hiểu interaction giữa descriptor và `@dataclass`.
* Tự viết một `ValidatedField`.
* Hiểu giới hạn của custom field.
* Chuẩn bị nền tảng cho **Buổi 19 — Metaclass + Dataclass**.

---

# 1. Attribute access thực sự xảy ra như thế nào?

Khi viết:

```python
user.name
```

ta thường nghĩ:

```text
user
 ↓
name
 ↓
value
```

Nhưng Python thực tế có một cơ chế lookup phức tạp.

Conceptually:

```text
user.name
   │
   ▼
attribute lookup
   │
   ├── data descriptor?
   │
   ├── instance __dict__?
   │
   ├── non-data descriptor?
   │
   └── class attribute
```

Đây chính là nơi Descriptor xuất hiện.

---

# 2. Descriptor là gì?

Một object được xem là descriptor nếu class của nó định nghĩa một hoặc nhiều method:

```python
__get__
__set__
__delete__
```

Ví dụ tối thiểu:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("GET")
```

Sau đó:

```python
class User:

    name = Descriptor()
```

Khi:

```python
user = User()

user.name
```

Python sẽ gọi:

```python
Descriptor.__get__(...)
```

---

# 3. Descriptor nằm ở class

Điểm cực kỳ quan trọng:

```python
class User:

    name = Descriptor()
```

`Descriptor()` không phải value của instance.

Nó nằm trong:

```text
User.__dict__
```

Conceptually:

```text
User
 │
 └── __dict__
       │
       └── name → Descriptor instance
```

Khi truy cập:

```python
user.name
```

Python phát hiện:

```text
User.name
   ↓
Descriptor
```

và kích hoạt descriptor protocol.

---

# 4. `__get__`

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("GET")
        return 123
```

```python
class User:
    age = Descriptor()
```

:

```python
user = User()

print(user.age)
```

Kết quả:

```text
GET
123
```

---

# 5. Ba tham số của `__get__`

```python
def __get__(self, instance, owner):
```

### `self`

Descriptor object.

### `instance`

Instance đang truy cập.

Ví dụ:

```python
user.age
```

thì:

```text
instance = user
```

### `owner`

Class:

```text
owner = User
```

---

# 6. `User.age` khác `user.age`

Điều này cực kỳ quan trọng.

```python
User.age
```

thường gọi:

```python
descriptor.__get__(None, User)
```

Trong khi:

```python
user.age
```

gọi:

```python
descriptor.__get__(user, User)
```

Ta có thể kiểm tra:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("instance =", instance)
        print("owner =", owner)
```

---

# 7. Descriptor lưu dữ liệu ở đâu?

Một descriptor thường cần biết:

```text
giá trị thuộc instance nào?
```

Ví dụ:

```python
class IntegerField:

    def __set_name__(self, owner, name):
        self.name = name
```

Sau đó:

```python
class User:

    age = IntegerField()
```

Python gọi:

```python
__set_name__(User, "age")
```

Descriptor biết:

```text
self.name = "age"
```

---

# 8. `__set_name__`

Python gọi:

```python
descriptor.__set_name__(owner, attribute_name)
```

khi class được tạo.

Ví dụ:

```python
class Field:

    def __set_name__(self, owner, name):
        print(owner)
        print(name)
```

```python
class User:
    age = Field()
```

Output conceptually:

```text
<class '__main__.User'>
age
```

Đây là hook rất quan trọng để xây:

```text
custom field
ORM
validator
framework
```

---

# 9. Descriptor với `__set__`

```python
class Field:

    def __set__(self, instance, value):
        print("SET", value)
```

```python
class User:
    age = Field()
```

Khi:

```python
user.age = 20
```

Python gọi:

```python
Field.__set__(
    descriptor,
    user,
    20,
)
```

---

# 10. Descriptor với `__delete__`

Ta cũng có:

```python
class Field:

    def __delete__(self, instance):
        print("DELETE")
```

Khi:

```python
del user.age
```

Python gọi:

```python
__delete__
```

---

# 11. Descriptor hoàn chỉnh

Ta có:

```python
class Field:

    def __get__(self, instance, owner):
        ...

    def __set__(self, instance, value):
        ...

    def __delete__(self, instance):
        ...
```

Đây được gọi là:

```text
full descriptor
```

---

# 12. Data Descriptor vs Non-Data Descriptor

Đây là một phần cực kỳ quan trọng.

### Data descriptor

Có:

```python
__set__
```

hoặc:

```python
__delete__
```

### Non-data descriptor

Chỉ có:

```python
__get__
```

Ví dụ:

```python
class A:
    def __get__(self, instance, owner):
        ...
```

là non-data descriptor.

---

# 13. Tại sao phân biệt?

Bởi vì thứ tự lookup khác nhau.

Data descriptor có ưu tiên cao hơn:

```text
instance.__dict__
```

Ví dụ:

```python
class Field:

    def __get__(self, instance, owner):
        return "descriptor"

    def __set__(self, instance, value):
        instance.__dict__["x"] = value
```

---

# 14. `property` chính là Descriptor

Một revelation quan trọng:

```python
@property
def name(self):
    ...
```

không phải magic.

`property` là một descriptor built-in.

Ví dụ:

```python
class User:

    @property
    def name(self):
        return "Alice"
```

Conceptually:

```text
User.name
     ↓
property object
     ↓
descriptor protocol
```

---

# 15. Property getter

```python
class User:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
```

Khi:

```python
user.name
```

Python gọi getter.

---

# 16. Property setter

```python
class User:

    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("name is empty")

        self._name = value
```

Bây giờ:

```python
user.name = ""
```

sẽ fail.

Đây chính là validation thông qua descriptor.

---

# 17. Dataclass + Property

Ta có thể viết:

```python
from dataclasses import dataclass


@dataclass
class User:
    _name: str

    @property
    def name(self) -> str:
        return self._name
```

Nhưng chú ý:

```python
User(
    _name="Alice"
)
```

chứ không phải:

```python
User(
    name="Alice"
)
```

vì dataclass nhìn thấy:

```text
_name
```

là field.

---

# 18. Dataclass field không phải Descriptor

Đây là điểm quan trọng.

Khi viết:

```python
@dataclass
class User:
    name: str
```

`name` không trở thành một descriptor giống `property`.

Dataclass chủ yếu sử dụng:

```python
__annotations__
```

để xác định field.

Sau đó decorator generate:

```python
__init__
__repr__
__eq__
...
```

---

# 19. `field()` là gì?

Khi viết:

```python
from dataclasses import dataclass, field


@dataclass
class User:
    name: str = field()
```

`field()` trả về một:

```python
dataclasses.Field
```

object.

Dataclass decorator sau đó xử lý object này.

Nó không phải descriptor theo nghĩa thông thường.

---

# 20. Descriptor + Dataclass

Bây giờ đến phần khó.

Ta có:

```python
class PositiveInteger:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError("must be positive")

        instance.__dict__[self.name] = value
```

Sau đó:

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

Đây là nơi interaction giữa:

```text
dataclass
+
descriptor
```

trở nên thú vị.

---

# 21. Vấn đề `__init__`

Dataclass tạo:

```python
def __init__(self, age):
    self.age = age
```

Nếu `age` là descriptor có `__set__`, assignment:

```python
self.age = age
```

sẽ kích hoạt:

```python
PositiveInteger.__set__()
```

Vậy validation xảy ra ngay trong initialization.

---

# 22. Đây là một dạng validation

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

Sau đó:

```python
User(age=20)
```

hợp lệ.

Nhưng:

```python
User(age=-10)
```

sẽ gọi:

```text
__set__
   ↓
validation
   ↓
ValueError
```

---

# 23. Viết `PositiveInteger` tốt hơn

Ta không nên hard-code key `"age"`.

Dùng:

```python
class PositiveInteger:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(
                f"{self.name} must be int"
            )

        if value <= 0:
            raise ValueError(
                f"{self.name} must be positive"
            )

        instance.__dict__[self.name] = value
```

Bây giờ:

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

---

# 24. Nhưng có một vấn đề lớn

Tên field:

```python
age
```

và storage:

```python
instance.__dict__["age"]
```

đang trùng nhau.

Điều này có thể tạo recursion trong một số thiết kế descriptor.

Một pattern an toàn hơn là dùng private storage:

```python
class PositiveInteger:

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(
                f"{self.public_name} must be int"
            )

        if value <= 0:
            raise ValueError(
                f"{self.public_name} must be positive"
            )

        setattr(
            instance,
            self.private_name,
            value,
        )
```

---

# 25. Dataclass + Descriptor Pattern

Ta có:

```python
class PositiveInteger:

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, int):
            raise TypeError(
                f"{self.public_name} must be int"
            )

        if value <= 0:
            raise ValueError(
                f"{self.public_name} must be positive"
            )

        setattr(instance, self.private_name, value)
```

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

Đây là:

```text
dataclass
    +
descriptor
    ↓
validated attribute
```

---

# 26. Descriptor có thể validate mọi assignment

Không chỉ initialization.

```python
user = User(age=20)
```

Sau đó:

```python
user.age = 30
```

descriptor vẫn kiểm tra.

Nhưng:

```python
user.age = -5
```

sẽ fail.

Đây là khác biệt lớn với:

```python
__post_init__
```

---

# 27. `__post_init__` vs Descriptor

### `__post_init__`

Validation:

```text
chỉ sau initialization
```

Ví dụ:

```python
@dataclass
class User:
    age: int

    def __post_init__(self):
        validate(self.age)
```

Sau đó:

```python
user.age = -10
```

không tự động validate.

---

### Descriptor

Validation:

```text
mọi assignment
```

```python
user.age = -10
```

descriptor bắt được.

---

# 28. Khi nào dùng `__post_init__`?

Dùng khi:

```text
initialization validation
cross-field validation
computed state
normalization
```

Ví dụ:

```python
@dataclass
class User:
    first_name: str
    last_name: str

    def __post_init__(self):
        self.full_name = (
            f"{self.first_name} {self.last_name}"
        )
```

---

# 29. Khi nào Descriptor tốt hơn?

Khi invariant phải giữ trong **suốt lifetime object**.

Ví dụ:

```text
age > 0
price >= 0
status chỉ nhận enum hợp lệ
email phải valid
```

Nếu object mutable:

```python
user.age = -100
```

ta muốn ngăn ngay.

Descriptor phù hợp.

---

# 30. Custom Validator Descriptor

Ta có thể tổng quát hóa.

```python
class ValidatedField:

    def __init__(self, validator):
        self.validator = validator

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        self.validator(value)

        setattr(
            instance,
            self.private_name,
            value,
        )
```

---

# 31. Sử dụng

```python
def positive(value):
    if value <= 0:
        raise ValueError(
            "value must be positive"
        )
```

Dataclass:

```python
@dataclass
class Product:
    price: float = ValidatedField(positive)
```

Bây giờ:

```python
Product(price=100)
```

OK.

```python
Product(price=-10)
```

fail.

---

# 32. Nhưng có vấn đề với typing

Ở đây:

```python
price: float = ValidatedField(positive)
```

type checker có thể hiểu:

```text
price: float
```

nhưng runtime class attribute thực chất là:

```text
ValidatedField
```

Dataclass cũng phải xử lý descriptor.

Đây là một trong những lý do custom descriptor field không đơn giản như:

```python
field(...)
```

---

# 33. Descriptor cần hỗ trợ `instance=None`

Luôn nhớ:

```python
def __get__(self, instance, owner):
```

Khi:

```python
Product.price
```

thì:

```text
instance = None
```

Nên thường:

```python
if instance is None:
    return self
```

Nếu không:

```text
class-level introspection
```

có thể bị lỗi.

---

# 34. `__set_name__` được gọi khi nào?

Khi class được tạo:

```python
class User:
    age = PositiveInteger()
```

Python conceptually:

```text
create class
     ↓
find descriptors
     ↓
call __set_name__
```

Do đó:

```python
self.name
```

được biết sau khi class được tạo.

---

# 35. Descriptor có state riêng

Ví dụ:

```python
class Field:

    def __init__(self, validator):
        self.validator = validator
```

Descriptor object tồn tại ở class:

```text
User
 │
 └── age → Field(...)
```

Nó không phải:

```text
User instance
```

Do đó:

> Không nên lưu dữ liệu instance-specific trực tiếp trong descriptor.

Sai:

```python
class Field:

    def __init__(self):
        self.value = None
```

vì tất cả instances sẽ dùng chung:

```text
Field.value
```

---

# 36. Storage phải thuộc instance

Đúng:

```python
instance.__dict__[private_name] = value
```

hoặc:

```python
setattr(instance, private_name, value)
```

Concept:

```text
Class
 │
 └── Descriptor
       │
       └── validator

Instance A
 │
 └── _age = 20

Instance B
 │
 └── _age = 30
```

Descriptor dùng chung.

Data không dùng chung.

---

# 37. Descriptor + `slots=True`

Đây là phần khó.

Nếu:

```python
@dataclass(slots=True)
class User:
    age: int = PositiveInteger()
```

thì instance không có:

```python
__dict__
```

Do đó descriptor code:

```python
instance.__dict__
```

có thể fail.

Đây là một lý do descriptor phải được thiết kế tương thích với storage strategy.

---

# 38. Descriptor + Slots

Có thể lưu qua một slot khác hoặc thiết kế descriptor phù hợp.

Ví dụ conceptually:

```text
User
 ├── age
 └── _age
```

Nhưng dataclass `slots=True` cần khai báo slot tương ứng.

Đây là nơi:

```text
slots
+
descriptor
```

trở nên khá phức tạp.

Không nên viết custom descriptor mà không hiểu memory layout.

---

# 39. Property cũng có vấn đề tương tự về setter

Ví dụ:

```python
@dataclass
class User:

    _age: int

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value <= 0:
            raise ValueError

        self._age = value
```

Dataclass constructor vẫn nhận:

```python
_age
```

không phải:

```python
age
```

Nếu muốn API:

```python
User(age=20)
```

thì thiết kế sẽ phức tạp hơn.

---

# 40. `field()` vs Descriptor

Đây là distinction quan trọng.

### `field()`

Dùng để cấu hình dataclass:

```python
field(
    default=...,
    default_factory=...,
    init=...,
    repr=...,
    compare=...,
    hash=...,
    metadata=...,
    kw_only=...,
)
```

Nó nói với:

```text
@dataclass
```

> "Hãy generate class theo cách này."

---

### Descriptor

Kiểm soát:

```text
attribute access
assignment
deletion
```

Nó nói với:

```text
Python runtime
```

> "Khi ai đó truy cập attribute này, hãy chạy logic của tôi."

---

# 41. Đây là hai tầng khác nhau

```text
             Dataclass
                │
                ▼
        class generation
                │
                ▼
        __init__/repr/eq
                │
                │
        Descriptor Protocol
                │
                ▼
      runtime attribute access
```

Đừng nhầm:

```text
Field
```

với:

```text
Descriptor
```

---

# 42. Custom Field Framework

Bây giờ ta có thể bắt đầu xây framework.

Ví dụ:

```python
class Field:

    def __init__(self, validator=None):
        self.validator = validator

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(
            instance,
            self.storage_name,
        )

    def __set__(self, instance, value):
        if self.validator:
            self.validator(value)

        setattr(
            instance,
            self.storage_name,
            value,
        )
```

---

# 43. Validator function

```python
def positive(value):
    if value <= 0:
        raise ValueError(
            "must be positive"
        )
```

Sử dụng:

```python
@dataclass
class Product:

    price: float = Field(
        validator=positive
    )
```

Ta vừa xây:

```text
mini validation framework
```

---

# 44. Type Validator

Có thể mở rộng:

```python
class Field:

    def __init__(
        self,
        expected_type=None,
        validator=None,
    ):
        self.expected_type = expected_type
        self.validator = validator

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(
            instance,
            self.storage_name,
        )

    def __set__(self, instance, value):

        if (
            self.expected_type is not None
            and not isinstance(value, self.expected_type)
        ):
            raise TypeError(
                f"{self.name} must be "
                f"{self.expected_type.__name__}"
            )

        if self.validator:
            self.validator(value)

        setattr(
            instance,
            self.storage_name,
            value,
        )
```

---

# 45. Sử dụng

```python
@dataclass
class User:

    age: int = Field(
        expected_type=int,
        validator=positive,
    )
```

Bây giờ:

```python
User(age=20)
```

OK.

```python
User(age=-1)
```

ValueError.

```python
User(age="20")
```

TypeError.

---

# 46. Một vấn đề thiết kế lớn

Ta đang viết:

```python
age: int = Field(...)
```

Trong dataclass.

Nhưng dataclass có thể coi `Field` object là default value.

Đây là điểm cần nghiên cứu rất kỹ khi xây custom framework.

Có nhiều cách thiết kế:

```text
1. Descriptor trực tiếp
2. field(metadata=...)
3. custom decorator
4. post-processing class
5. metaclass
```

Và đây chính là cầu nối tới:

> **Buổi 19 — Metaclass + Dataclass**

---

# 47. Một thiết kế thường tốt hơn

Thay vì:

```python
age: int = Field(...)
```

ta có thể dùng:

```python
age: int = field(
    metadata={
        "validator": positive
    }
)
```

Sau đó framework đọc:

```python
dataclasses.fields(User)
```

và lấy:

```python
field.metadata
```

Đây là hướng khác:

```text
Dataclass
   ↓
metadata
   ↓
validation framework
```

không cần descriptor.

---

# 48. Descriptor vs Metadata

### Descriptor

```text
runtime enforcement
```

### Metadata

```text
declarative configuration
```

Ví dụ:

```python
@dataclass
class User:

    age: int = field(
        metadata={
            "min": 0,
            "max": 150,
        }
    )
```

Framework có thể đọc metadata.

Nhưng:

```python
user.age = -10
```

vẫn không tự động fail.

---

# 49. Ba chiến lược Validation

Trong Dataclass ecosystem:

```text
                 Validation
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
 __post_init__   Descriptor     Metadata
       │             │             │
   init-time      runtime      framework
```

### `__post_init__`

Đơn giản.

### Descriptor

Mạnh nhưng phức tạp.

### Metadata

Linh hoạt cho framework.

---

# 50. Khi nào nên dùng cái nào?

| Cách            | Dùng khi                      |
| --------------- | ----------------------------- |
| `__post_init__` | Validate lúc tạo object       |
| `property`      | Computed/controlled attribute |
| Descriptor      | Invariant trong suốt lifetime |
| `metadata`      | Framework/configuration       |
| Pydantic        | Validation/data parsing lớn   |
| `attrs`         | Data model nâng cao           |

---

# 51. Ví dụ Domain Model

Với crawler của bạn:

```python
@dataclass
class Chapter:
    number: int
    title: str
    content: str
```

Validation cơ bản:

```python
def __post_init__(self):
    if self.number <= 0:
        raise ValueError

    if not self.title:
        raise ValueError

    if not self.content:
        raise ValueError
```

Đây thường là lựa chọn tốt hơn descriptor.

Không nên over-engineer.

---

# 52. Descriptor phù hợp hơn khi nào?

Ví dụ:

```python
@dataclass
class DownloadTask:

    progress: int
```

Ta muốn invariant:

```text
0 <= progress <= 100
```

và task mutable:

```python
task.progress = 50
task.progress = 80
```

Nếu muốn ngăn:

```python
task.progress = 200
```

descriptor có thể hợp lý.

---

# 53. Một Descriptor Range

```python
class Range:

    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):

        if not (
            self.minimum
            <= value
            <= self.maximum
        ):
            raise ValueError(
                f"{self.name} must be between "
                f"{self.minimum} and {self.maximum}"
            )

        setattr(
            instance,
            self.storage_name,
            value,
        )
```

---

# 54. Dùng cho Task

```python
@dataclass
class DownloadTask:

    progress: int = Range(0, 100)
```

Sau đó:

```python
task = DownloadTask(
    progress=50
)
```

OK.

```python
task.progress = 80
```

OK.

```python
task.progress = 120
```

fail.

---

# 55. Đây là một invariant

Ta đang bảo vệ:

```text
DownloadTask.progress
        ↓
0 <= progress <= 100
```

bất kể assignment xảy ra lúc nào.

Đây là một use case rất phù hợp của descriptor.

---

# 56. Nhưng đừng lạm dụng Descriptor

Nếu bạn chỉ cần:

```python
@dataclass
class User:

    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError
```

thì descriptor là quá mức cần thiết.

Nguyên tắc:

> **Dùng cơ chế đơn giản nhất đủ để bảo vệ invariant.**

---

# 57. Connection tới ORM

Nếu bạn từng thấy:

```python
class User(Base):
    name = Column(String)
```

hoặc các ORM/framework sử dụng:

```python
field = ...
```

thì rất có thể bạn đang nhìn thấy các kỹ thuật tương tự:

```text
Descriptor
Metaclass
Class inspection
Metadata
```

Đây là lý do học Descriptor trước Metaclass rất quan trọng.

---

# 58. Connection tới Pydantic

Pydantic sử dụng một hệ thống model/field/validation phức tạp hơn:

```text
annotation
    ↓
field information
    ↓
validator
    ↓
model construction
```

Dataclass thuần Python không cung cấp toàn bộ hệ thống validation này.

Ta đang tự xây một phần nhỏ để hiểu:

```text
framework design
```

---

# 59. Descriptor và `__dict__`

Với object thông thường:

```python
user.__dict__
```

có thể:

```python
{
    "_age": 20
}
```

Trong khi:

```python
user.age
```

đi qua:

```text
PositiveInteger.__get__()
```

Nghĩa là:

```text
public API
    ↓
age
    ↓
descriptor
    ↓
_age
    ↓
20
```

---

# 60. Mental Model quan trọng nhất

Hãy ghi nhớ pipeline:

```text
user.age
   │
   ▼
Python attribute lookup
   │
   ▼
User.age
   │
   ▼
Descriptor?
   │
   ▼
__get__(user, User)
   │
   ▼
user._age
```

Khi assignment:

```text
user.age = 20
   │
   ▼
__set__(user, 20)
   │
   ▼
validate
   │
   ▼
user._age = 20
```

Đây là bản chất của descriptor.

---

# 61. Dataclass + Descriptor: kiến trúc

```text
                    @dataclass
                        │
                        ▼
                  class generation
                        │
                 ┌──────┴──────┐
                 ▼             ▼
             __init__       metadata
                 │
                 ▼
             self.age = x
                 │
                 ▼
             Descriptor
                 │
                 ▼
              __set__()
                 │
                 ▼
             validation
```

Đây là mental model bạn cần nắm thật chắc.

---

# 62. Bài tập Buổi 18

## Bài 1 — Descriptor cơ bản

Tự viết:

```python
Descriptor
```

hỗ trợ:

```python
__get__
__set__
__set_name__
```

và lưu value vào:

```text
_private_name
```

---

## Bài 2 — PositiveInteger

Viết:

```python
PositiveInteger
```

sao cho:

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

Cho phép:

```python
User(age=20)
```

Không cho:

```python
User(age=-1)
User(age="20")
```

---

## Bài 3 — Range

Viết:

```python
Range(0, 100)
```

cho:

```python
@dataclass
class DownloadTask:
    progress: int = Range(0, 100)
```

Kiểm tra cả:

```python
initialization
assignment
```

---

## Bài 4 — String Validator

Tạo:

```python
NonEmptyString()
```

sử dụng:

```python
@dataclass
class Novel:
    title: str = NonEmptyString()
```

Phải reject:

```python
""
"   "
None
```

---

# 63. Bài tập Deep Dive

Tự giải thích tại sao:

```python
@dataclass
class User:
    age: int = PositiveInteger()
```

có thể hoạt động theo flow:

```text
@dataclass
      ↓
generated __init__
      ↓
self.age = age
      ↓
PositiveInteger.__set__()
      ↓
validation
      ↓
self._age
```

Sau đó trả lời:

> Tại sao `PositiveInteger` không nên lưu `value` trực tiếp trong chính descriptor object?

Nếu hiểu được câu này, bạn đã thực sự hiểu **state của Descriptor vs state của Instance**.

---

# 64. Roadmap

```text
Phần II — Advanced

11. Inheritance                  ✅
12. Multiple Inheritance + MRO   ✅
13. Composition                  ✅
14. Recursive Dataclass          ✅
15. Generic Dataclass            ✅
16. Abstract Dataclass            ✅
17. Protocols                    ✅
18. Descriptors                  ✅ ← hôm nay
19. Metaclass + Dataclass        ← tiếp theo
20. Dynamic Dataclass
```

Buổi 19 sẽ nối trực tiếp từ hôm nay:

```text
Descriptor
    ↓
Class creation
    ↓
__set_name__
    ↓
Metaclass
    ↓
@dataclass
    ↓
Generated methods
```

Chúng ta sẽ **mổ xẻ Metaclass + Dataclass**, bao gồm cách metaclass can thiệp vào quá trình tạo class, `type.__new__`, `__prepare__`, `__new__`, `__init__`, và tại sao thứ tự **Metaclass → Class creation → Decorator → Dataclass transformation** lại quan trọng.
