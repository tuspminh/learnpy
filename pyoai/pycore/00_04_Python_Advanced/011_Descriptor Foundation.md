# 🐍 Buổi 11 — Descriptor Foundation

Hôm nay chúng ta bước vào phần **cốt lõi của Python Object Model**:

```text
Part II — Descriptor & Attribute System

08. Attribute Lookup
09. __getattribute__()
10. __getattr__()
11. Descriptor Foundation   ← hôm nay
12. Data Descriptor
13. Non-data Descriptor
14. property
15. Descriptor Practical
16. Descriptor Framework
```

Nếu hiểu Descriptor tốt, bạn sẽ hiểu sâu hơn rất nhiều thứ tưởng như "magic" trong Python:

```text
@property
method binding
classmethod
staticmethod
ORM Field
validation
lazy loading
cached property
dependency injection
framework
```

---

# 1. Descriptor là gì?

Một **descriptor** là một object định nghĩa một hoặc nhiều method đặc biệt:

```python
__get__()
__set__()
__delete__()
```

Khi descriptor được đặt làm **class attribute**, Python có thể chuyển:

```python
obj.name
```

thành logic:

```python
descriptor.__get__(obj, type(obj))
```

Và:

```python
obj.name = value
```

thành:

```python
descriptor.__set__(obj, value)
```

Mental model:

```text
                    User
                     │
                     ▼
             class attribute
                     │
                     ▼
                Descriptor
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
       __get__                __set__
          │                     │
          ▼                     ▼
      obj.name          obj.name = value
```

---

# 2. Descriptor đầu tiên

Hãy viết:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("GET")

    def __set__(self, instance, value):
        print("SET:", value)
```

Sau đó:

```python
class User:
    name = Descriptor()
```

Ta có:

```text
User
 │
 └── name
       │
       ▼
   Descriptor()
```

---

# 3. Khi đọc attribute

```python
user = User()

user.name
```

Python thấy:

```text
user.name
   ↓
User.name
   ↓
Descriptor
   ↓
__get__()
```

Về mặt concept:

```python
Descriptor.__get__(
    descriptor,
    user,
    User
)
```

---

# 4. `instance` và `owner`

Đây là hai tham số cực kỳ quan trọng.

```python
def __get__(self, instance, owner):
```

### `instance`

Object đang truy cập:

```python
user.name
```

thì:

```python
instance == user
```

### `owner`

Class của object:

```python
owner == User
```

Mental model:

```text
user.name
   │
   ├── instance → user
   │
   └── owner    → User
```

---

# 5. Descriptor có thể được truy cập qua class

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("instance =", instance)
        print("owner =", owner)

        return "value"


class User:
    name = Descriptor()
```

Bây giờ:

```python
user = User()

print(user.name)
```

Conceptually:

```text
instance = <User object>
owner    = User
```

---

# 6. Còn `User.name`?

Thử:

```python
print(User.name)
```

Khi descriptor được truy cập qua class, Python gọi:

```python
__get__(
    instance=None,
    owner=User
)
```

Tức là:

```text
user.name

instance = user
owner    = User
```

Trong khi:

```text
User.name

instance = None
owner    = User
```

Đây là pattern cực kỳ quan trọng.

---

# 7. Vì vậy Descriptor thường viết

```python
class Descriptor:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return ...
```

Ví dụ:

```python
class Field:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return "value"
```

Bây giờ:

```python
User.name
```

trả về chính:

```text
Field object
```

còn:

```python
user.name
```

trả về:

```text
"value"
```

---

# 8. Descriptor không lưu value trong chính nó

Đây là một lỗi thiết kế rất phổ biến.

Bạn có thể nghĩ:

```python
class Field:

    def __init__(self):
        self.value = None
```

rồi:

```python
class User:
    name = Field()
```

Nhưng vấn đề:

```python
alice = User()
bob = User()
```

cùng sử dụng:

```text
User.name
    │
    ▼
Field instance
```

Nghĩa là:

```text
alice.name
bob.name
```

đều dùng **cùng một Descriptor object**.

---

# 9. Minh họa vấn đề

Sai:

```python
class Field:

    def __init__(self):
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value
```

```python
class User:
    name = Field()
```

Sau:

```python
alice = User()
bob = User()

alice.name = "Alice"
bob.name = "Bob"
```

Nếu `Field` lưu:

```python
self.value
```

thì:

```text
Field
└── value = "Bob"
```

Alice và Bob sẽ dùng chung value.

**Sai.**

---

# 10. Descriptor phải lưu value theo instance

Ta cần:

```text
Field
 │
 ├── alice → "Alice"
 │
 └── bob   → "Bob"
```

Có nhiều cách.

Cách đơn giản:

```python
class Field:

    def __set__(self, instance, value):
        instance.__dict__["_name"] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__["_name"]
```

---

# 11. Xây Field đầu tiên

```python
class Field:

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            "_field",
            None
        )

    def __set__(self, instance, value):
        instance.__dict__["_field"] = value
```

Sau:

```python
class User:
    name = Field()
```

Ta có:

```python
alice = User()
bob = User()

alice.name = "Alice"
bob.name = "Bob"
```

Conceptually:

```text
alice.__dict__
└── _field → "Alice"

bob.__dict__
└── _field → "Bob"
```

---

# 12. Nhưng `_field` không phải tên tốt

Nếu có:

```python
class User:

    name = Field()
    age = Field()
```

thì cả hai Field đều có thể dùng:

```text
_field
```

→ collision.

Ta cần biết:

```text
name → _name
age  → _age
```

---

# 13. Descriptor cần biết tên attribute

Đây là nơi bắt đầu xuất hiện `__set_name__()`.

Python hỗ trợ:

```python
def __set_name__(self, owner, name):
    ...
```

Ví dụ:

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name
```

Khi:

```python
class User:
    name = Field()
    age = Field()
```

Python sẽ thông báo cho descriptor:

```text
Field(name) → name
Field(age)  → age
```

---

# 14. `__set_name__()` hoạt động thế nào?

Code:

```python
class Field:

    def __set_name__(self, owner, name):
        print(
            "owner =",
            owner,
            "name =",
            name
        )
```

```python
class User:
    name = Field()
    age = Field()
```

Trong quá trình class creation, Python gọi:

```text
Field.__set_name__(User, "name")
Field.__set_name__(User, "age")
```

---

# 15. Xây `Field` tốt hơn

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.storage_name
        )

    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value
```

Bây giờ:

```python
class User:

    name = Field()
    age = Field()
```

---

# 16. Test

```python
alice = User()
bob = User()

alice.name = "Alice"
alice.age = 30

bob.name = "Bob"
bob.age = 25
```

Kết quả:

```python
print(alice.name)
print(alice.age)

print(bob.name)
print(bob.age)
```

```text
Alice
30
Bob
25
```

---

# 17. Object graph

Hãy nhìn cấu trúc:

```text
User class
│
├── name ───────► Field
│                  │
│                  ├── name = "name"
│                  └── storage = "_name"
│
└── age ────────► Field
                   │
                   ├── name = "age"
                   └── storage = "_age"


alice
│
└── __dict__
      ├── _name → "Alice"
      └── _age  → 30


bob
│
└── __dict__
      ├── _name → "Bob"
      └── _age  → 25
```

Đây là kiến trúc rất quan trọng.

---

# 18. Descriptor nằm ở Class

Một descriptor thường được khai báo:

```python
class User:
    name = Field()
```

**Không phải:**

```python
user.name = Field()
```

Descriptor protocol chủ yếu được kích hoạt khi descriptor object được đặt trên **class/MRO**.

Mental model:

```text
              User
               │
        ┌──────┴──────┐
        ▼             ▼
      name            age
        │             │
        ▼             ▼
      Field          Field
        │             │
        └──────┬──────┘
               │
         instance state
               │
          alice / bob
```

---

# 19. Descriptor và `__dict__`

Bạn có thể hỏi:

> Nếu value cuối cùng nằm trong `instance.__dict__`, vậy Descriptor để làm gì?

Câu trả lời:

**Descriptor kiểm soát việc đọc/ghi.**

Ví dụ:

```python
user.name = "Alice"
```

không còn là:

```python
user.__dict__["name"] = "Alice"
```

mà:

```text
user.name = "Alice"
      ↓
Field.__set__()
      ↓
validation
      ↓
normalization
      ↓
storage
```

Khi đọc:

```text
user.name
   ↓
Field.__get__()
   ↓
storage
   ↓
return
```

Descriptor trở thành một **interception layer cho attribute**.

---

# 20. Thêm validation

Bây giờ bắt đầu thấy sức mạnh.

```python
class StringField:

    def __set_name__(self, owner, name):
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.storage_name
        )

    def __set__(self, instance, value):

        if not isinstance(value, str):
            raise TypeError(
                "value must be str"
            )

        instance.__dict__[self.storage_name] = value
```

---

# 21. Sử dụng

```python
class User:

    name = StringField()
```

Đúng:

```python
user = User()

user.name = "Alice"
```

Sai:

```python
user.name = 123
```

→:

```text
TypeError
```

Architecture:

```text
user.name = 123
       ↓
StringField.__set__()
       ↓
isinstance(value, str)?
       ↓
NO
       ↓
TypeError
```

Đây chính là **attribute-level validation**.

---

# 22. IntegerField

Ta có thể tạo:

```python
class IntegerField:

    def __set_name__(self, owner, name):
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.storage_name
        )

    def __set__(self, instance, value):

        if not isinstance(value, int):
            raise TypeError(
                "value must be int"
            )

        instance.__dict__[self.storage_name] = value
```

Sau:

```python
class User:

    name = StringField()
    age = IntegerField()
```

Ta đã có một mini field system.

---

# 23. Đây chính là nền tảng ORM

Hãy tưởng tượng:

```python
class User(Model):

    id = IntegerField(primary_key=True)

    name = StringField(
        max_length=100
    )

    age = IntegerField(
        min_value=0
    )
```

Syntax rất đẹp:

```python
user.name = "Alice"
user.age = 30
```

Nhưng phía sau:

```text
name
 ↓
StringField
 ↓
validation
 ↓
database mapping


age
 ↓
IntegerField
 ↓
validation
 ↓
database mapping
```

Đây là một trong những lý do Descriptor rất quan trọng trong Python framework design.

---

# 24. `property` thực chất cũng là Descriptor

Bạn đã từng viết:

```python
class User:

    @property
    def name(self):
        return self._name
```

Khi decorator chạy:

```python
@property
```

nó tạo một `property` object.

Conceptually:

```text
name
 ↓
property object
 ↓
__get__()
```

Do đó:

```python
user.name
```

kích hoạt descriptor.

Buổi 14 chúng ta sẽ mổ xẻ `property` từ bên trong.

---

# 25. Function cũng là Descriptor

Như Buổi 8 đã nói:

```python
class User:

    def hello(self):
        return "Hello"
```

`hello` là function object nằm trong class.

Function có:

```python
__get__
```

Do đó:

```python
user.hello
```

có thể biến:

```text
function
```

thành:

```text
bound method
```

Đây là một trong những ví dụ đẹp nhất về Descriptor.

---

# 26. Descriptor không nhất thiết phải có cả `__get__` và `__set__`

Có thể chỉ có:

```python
class Descriptor:

    def __get__(self, instance, owner):
        ...
```

Đây là **non-data descriptor**.

Hoặc:

```python
class Descriptor:

    def __get__(self, instance, owner):
        ...

    def __set__(self, instance, value):
        ...
```

Đây là **data descriptor**.

Buổi 12 và 13 chúng ta sẽ đi sâu vào sự khác biệt này.

---

# 27. `__delete__()`

Descriptor cũng có thể intercept:

```python
del user.name
```

Ví dụ:

```python
class Field:

    def __delete__(self, instance):
        print("DELETE")
```

Sau:

```python
del user.name
```

có thể dẫn tới:

```text
Field.__delete__(user)
```

---

# 28. Một Descriptor hoàn chỉnh cơ bản

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.storage_name
        )

    def __set__(self, instance, value):
        instance.__dict__[self.storage_name] = value

    def __delete__(self, instance):
        instance.__dict__.pop(
            self.storage_name,
            None
        )
```

Sử dụng:

```python
class User:

    name = Field()
```

---

# 29. Test toàn bộ lifecycle

```python
user = User()

user.name = "Alice"

print(user.name)

del user.name

print(user.name)
```

Luồng:

```text
user.name = "Alice"
        ↓
    __set__()
        ↓
    "_name"


user.name
        ↓
    __get__()
        ↓
    "_name"


del user.name
        ↓
    __delete__()
        ↓
    remove "_name"
```

---

# 30. Một chi tiết quan trọng: `owner`

Trong:

```python
def __get__(self, instance, owner):
```

`owner` thường là class dùng để thực hiện lookup.

Ví dụ:

```python
class Animal:
    field = Field()

class Dog(Animal):
    pass
```

Khi:

```python
dog.field
```

descriptor có thể nhận:

```text
instance = dog
owner    = Dog
```

Điều này rất hữu ích khi descriptor cần biết class hiện tại.

---

# 31. Descriptor và inheritance

Ví dụ:

```python
class Base:

    name = Field()


class User(Base):
    pass
```

```python
user = User()

user.name = "Alice"
```

Descriptor được tìm qua:

```text
User
 ↓
Base
 ↓
Field
```

Vì vậy Descriptor kết hợp rất mạnh với:

```text
inheritance
MRO
framework base class
```

---

# 32. Descriptor vs `__getattr__`

Đây là điểm cần phân biệt:

### `__getattr__`

```text
attribute không tồn tại
        ↓
fallback
```

### Descriptor

```text
attribute tồn tại trên class
        ↓
custom behavior
```

Ví dụ:

```python
class User:

    name = Field()

    def __getattr__(self, name):
        ...
```

thì:

```text
user.name
```

→ `Field`

nhưng:

```text
user.unknown
```

→ `__getattr__`

---

# 33. Descriptor vs `__getattribute__`

```text
__getattribute__
        ↓
intercept toàn bộ attribute access
```

Trong khi:

```text
Descriptor
        ↓
intercept một attribute cụ thể
```

Ví dụ:

```python
class User:

    name = Field()
    age = Field()
```

Descriptor chỉ quan tâm:

```text
name
age
```

không nhất thiết can thiệp:

```text
user.email
user.address
user.foo
```

---

# 34. Khi nào dùng Descriptor?

Descriptor phù hợp khi bạn cần:

### Validation

```python
user.age = 100
```

### Conversion

```python
user.age = "30"
```

→ chuyển thành:

```python
30
```

### Lazy loading

```python
user.profile
```

### Computed value

```python
user.total
```

### ORM field

```python
User.name
```

### Dependency injection

```python
service.repository
```

### Caching

```python
obj.expensive_property
```

---

# 35. Khi nào không nên dùng?

Không phải mọi vấn đề đều cần Descriptor.

Nếu chỉ cần:

```python
class User:

    def __init__(self, name):
        self.name = name
```

thì cứ dùng:

```python
self.name
```

Đừng biến thành:

```python
NameDescriptor
StringField
ValidationDescriptor
...
```

nếu không có lý do.

Descriptor đặc biệt hữu ích khi:

> **nhiều class/attribute cần cùng một cơ chế behavior.**

---

# 36. Mental Model quan trọng nhất

Hãy ghi nhớ:

```text
                class User
                    │
                    │
             name = Field()
                    │
                    ▼
                Descriptor
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      __get__      __set__    __delete__
        │           │           │
        ▼           ▼           ▼
   user.name   user.name = x   del user.name
```

Descriptor là một **object đứng giữa attribute access và instance state**.

---

# 🧪 Bài tập

## Bài 1 — Logger Descriptor

Viết:

```python
class LoggedField:
    ...
```

sao cho:

```python
class User:
    name = LoggedField()
```

khi:

```python
user.name = "Alice"
print(user.name)
```

sẽ log:

```text
SET name = Alice
GET name
Alice
```

---

## Bài 2 — StringField

Xây:

```python
class StringField:
    ...
```

Sao cho:

```python
class User:
    name = StringField()
```

chấp nhận:

```python
user.name = "Alice"
```

nhưng từ chối:

```python
user.name = 123
```

---

## Bài 3 — IntegerField

Tạo:

```python
class User:

    name = StringField()
    age = IntegerField()
```

Test:

```python
user.name = "Alice"
user.age = 30
```

và:

```python
user.age = "30"
```

phải raise `TypeError`.

---

## Bài 4 — `__set_name__()`

Tạo:

```python
class Field:

    def __set_name__(self, owner, name):
        print(owner.__name__, name)
```

Sau:

```python
class User:
    name = Field()
    age = Field()
```

Dự đoán output.

---

## Bài 5 — Class access

Với:

```python
class Field:

    def __get__(self, instance, owner):
        print(
            "instance:",
            instance,
            "owner:",
            owner
        )
        return self
```

thử:

```python
User.name
```

và:

```python
user.name
```

Quan sát sự khác nhau của `instance`.

---

# 🎯 Tổng kết Buổi 11

Bạn cần nắm chắc 5 điểm:

### 1. Descriptor là object có:

```python
__get__()
__set__()
__delete__()
```

### 2. Descriptor thường được đặt trên class:

```python
class User:
    name = Field()
```

### 3. Đọc:

```python
user.name
```

có thể dẫn đến:

```python
Field.__get__(
    user,
    User
)
```

### 4. Ghi:

```python
user.name = "Alice"
```

có thể dẫn đến:

```python
Field.__set__(
    user,
    "Alice"
)
```

### 5. `__set_name__()` cho descriptor biết:

```text
owner = User
name  = "name"
```

---

# 🔥 Bức tranh lớn

Chúng ta đã đi từ:

```text
Buổi 8
Attribute Lookup
       ↓
Buổi 9
__getattribute__
       ↓
Buổi 10
__getattr__
       ↓
Buổi 11
Descriptor
```

và bây giờ bắt đầu hiểu được:

```text
                 obj.attr
                    │
                    ▼
            __getattribute__
                    │
                    ▼
             Class / MRO
                    │
                    ▼
              Descriptor
              ┌─────┴─────┐
              ▼           ▼
           __get__      __set__
              │           │
              ▼           ▼
          obj.attr   obj.attr = x
```

## 🚀 Buổi 12 — Data Descriptor

Buổi sau chúng ta sẽ đi vào phần **rất quan trọng**:

```text
Data Descriptor
      vs
Instance __dict__
```

và tự chứng minh tại sao:

```python
class User:
    name = Descriptor()
```

có thể **đánh bại**:

```python
user.__dict__["name"] = "Alice"
```

Sau đó chúng ta sẽ xây một `ValidatedField` có:

```text
type validation
required
default
min/max
normalization
error message
```

Đây sẽ là bước đầu tiên để từ Descriptor cơ bản tiến tới **mini ORM / framework field system**.
