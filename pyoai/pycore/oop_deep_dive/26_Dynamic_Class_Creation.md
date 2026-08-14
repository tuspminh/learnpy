# OOP Deep Dive — Buổi 26

# Dynamic Class Creation

Hôm trước chúng ta học:

```python
type(name, bases, namespace)
```

và hiểu rằng:

```text
type
  ↓ tạo
Class Object
  ↓ tạo
Instance
```

Hôm nay chúng ta đi một bước sâu hơn:

> **Làm thế nào để chương trình tự tạo class trong runtime?**

Đây là nền tảng của:

* ORM
* Plugin system
* Serializer
* Validation framework
* Dependency Injection
* Mocking
* GUI framework
* Model factory
* Dynamic API
* Metaclass

---

# 1. Dynamic Class Creation là gì?

Bình thường ta viết:

```python
class User:
    pass
```

Class được xác định ngay trong source code.

Dynamic Class Creation nghĩa là:

> Class được tạo ra **bằng code trong runtime**.

Ví dụ:

```python
User = type(
    "User",
    (),
    {}
)
```

Không cần viết:

```python
class User:
    pass
```

---

# 2. Tại sao cần tạo class động?

Hãy tưởng tượng một ORM nhận schema từ database:

```python
schema = {
    "User": {
        "id": int,
        "name": str,
        "age": int,
    },
    "Book": {
        "id": int,
        "title": str,
    },
}
```

Ta không muốn tự viết:

```python
class User:
    ...

class Book:
    ...
```

Framework có thể tự tạo:

```text
schema
  ↓
class factory
  ↓
User
Book
```

---

# 3. Cách đơn giản nhất

```python
User = type(
    "User",
    (),
    {}
)
```

Kiểm tra:

```python
print(User)
print(type(User))
```

Kết quả:

```text
<class '__main__.User'>
<class 'type'>
```

---

# 4. Dynamic class có instance bình thường

```python
User = type(
    "User",
    (),
    {}
)

user = User()

print(user)
print(type(user))
```

Không có gì khác biệt so với:

```python
class User:
    pass

user = User()
```

---

# 5. Thêm class attribute

Namespace chính là dictionary:

```python
User = type(
    "User",
    (),
    {
        "species": "human"
    }
)
```

Sau đó:

```python
print(User.species)
```

→

```text
human
```

Instance cũng truy cập được:

```python
user = User()

print(user.species)
```

---

# 6. Thêm nhiều attribute

```python
User = type(
    "User",
    (),
    {
        "species": "human",
        "country": "Vietnam",
        "active": True,
    }
)
```

Tương đương:

```python
class User:

    species = "human"
    country = "Vietnam"
    active = True
```

---

# 7. Thêm method

Đầu tiên tạo function:

```python
def hello(self):
    return "Hello"
```

Sau đó:

```python
User = type(
    "User",
    (),
    {
        "hello": hello
    }
)
```

Dùng:

```python
user = User()

print(user.hello())
```

Kết quả:

```text
Hello
```

---

# 8. Vì sao function trở thành method?

Điều này liên quan trực tiếp đến **Buổi 23 — Method là Descriptor**.

Trong class:

```python
class User:

    def hello(self):
        ...
```

function:

```python
hello
```

được đặt vào class namespace.

Khi:

```python
user.hello()
```

Python thực hiện descriptor lookup.

Với dynamic class cũng vậy:

```text
function
   ↓
namespace
   ↓
type()
   ↓
User
   ↓
attribute lookup
   ↓
bound method
```

---

# 9. Dynamic method với dữ liệu

```python
def greet(self):
    return f"Hello {self.name}"


User = type(
    "User",
    (),
    {
        "name": "Alice",
        "greet": greet,
    }
)
```

Dùng:

```python
user = User()

print(user.greet())
```

→

```text
Hello Alice
```

---

# 10. Dynamic `__init__`

Ta có thể tạo constructor động:

```python
def __init__(self, name, age):
    self.name = name
    self.age = age
```

Sau đó:

```python
User = type(
    "User",
    (),
    {
        "__init__": __init__
    }
)
```

Dùng:

```python
user = User("Alice", 25)

print(user.name)
print(user.age)
```

---

# 11. Đây là điểm rất quan trọng

`type()` không chỉ tạo:

```python
class User:
    pass
```

Nó có thể tạo class với:

```text
__init__
methods
properties
descriptors
class attributes
special methods
metadata
```

---

# 12. Dynamic class với `__repr__`

```python
def __repr__(self):
    return f"User(name={self.name!r})"


User = type(
    "User",
    (),
    {
        "__repr__": __repr__
    }
)
```

---

# 13. Dynamic class hoàn chỉnh

```python
def __init__(self, name, age):
    self.name = name
    self.age = age


def __repr__(self):
    return (
        f"User("
        f"name={self.name!r}, "
        f"age={self.age}"
        f")"
    )


User = type(
    "User",
    (),
    {
        "__init__": __init__,
        "__repr__": __repr__,
    }
)
```

Dùng:

```python
user = User("Alice", 25)

print(user)
```

Kết quả:

```text
User(name='Alice', age=25)
```

---

# 14. Tạo class factory

Bây giờ ta không muốn viết:

```python
User = type(...)
Book = type(...)
Product = type(...)
```

Ta viết:

```python
def create_class(name):

    return type(
        name,
        (),
        {}
    )
```

Dùng:

```python
User = create_class("User")
Book = create_class("Book")
```

---

# 15. Class Factory là gì?

Một function trả về class:

```python
def create_class(name):
    return type(name, (), {})
```

được gọi là:

> **Class Factory**

Ta có:

```text
create_class()
     ↓
   type()
     ↓
  Class
```

---

# 16. Factory có thể nhận attributes

```python
def create_class(name, attributes):

    return type(
        name,
        (),
        attributes
    )
```

Dùng:

```python
User = create_class(
    "User",
    {
        "species": "human",
    }
)
```

---

# 17. Factory có thể nhận methods

```python
def create_class(
    name,
    attributes=None,
    methods=None,
):

    namespace = {}

    if attributes:
        namespace.update(attributes)

    if methods:
        namespace.update(methods)

    return type(
        name,
        (),
        namespace
    )
```

---

# 18. Sử dụng

```python
def hello(self):
    return "Hello"


User = create_class(
    "User",
    attributes={
        "name": "Alice",
    },
    methods={
        "hello": hello,
    },
)
```

---

# 19. Dynamic inheritance

Nhớ cú pháp:

```python
type(
    name,
    bases,
    namespace
)
```

`bases` là tuple.

Ví dụ:

```python
class Animal:

    def speak(self):
        return "sound"
```

Tạo:

```python
Dog = type(
    "Dog",
    (Animal,),
    {}
)
```

---

# 20. Kiểm tra inheritance

```python
dog = Dog()

print(dog.speak())
```

→

```text
sound
```

và:

```python
print(issubclass(Dog, Animal))
```

→

```text
True
```

---

# 21. Dynamic multiple inheritance

Ta có:

```python
class Logger:

    def log(self):
        return "log"


class Serializer:

    def serialize(self):
        return "serialize"
```

Tạo:

```python
Model = type(
    "Model",
    (Logger, Serializer),
    {}
)
```

Sau đó:

```python
model = Model()

print(model.log())
print(model.serialize())
```

---

# 22. Dynamic class + MRO

```python
print(Model.__mro__)
```

Có dạng:

```text
Model
Logger
Serializer
object
```

Điều này cho thấy:

> Dynamic Class Creation vẫn tuân theo toàn bộ cơ chế inheritance và MRO của Python.

---

# 23. Dynamic class + Descriptor

Đây là phần cực kỳ quan trọng đối với kiến thức chúng ta vừa học.

Ta tạo:

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
```

Sau đó:

```python
User = type(
    "User",
    (),
    {
        "name": Field(),
        "age": Field(),
    }
)
```

---

# 24. Vấn đề `__set_name__`

Đây là điểm rất đáng chú ý.

Khi Descriptor được tạo trong:

```python
class User:

    name = Field()
```

Python class creation machinery sẽ gọi:

```python
Field.__set_name__(
    User,
    "name"
)
```

Nhưng khi ta sử dụng:

```python
type(
    "User",
    (),
    {
        "name": Field()
    }
)
```

việc `__set_name__` cần được hiểu rõ trong quá trình tạo class.

Python's class construction machinery hỗ trợ việc gọi `__set_name__` cho descriptors trong namespace class. Đây là một trong những lý do không nên xem `type()` đơn thuần là một dictionary-to-class converter; nó đi qua class creation machinery của Python.

Ta có thể kiểm tra:

```python
class Field:

    def __set_name__(self, owner, name):
        print(
            f"{owner.__name__}.{name}"
        )
```

Sau đó:

```python
User = type(
    "User",
    (),
    {
        "name": Field()
    }
)
```

Bạn sẽ thấy:

```text
User.name
```

---

# 25. Đây là sự kết nối rất đẹp

```text
Dynamic Class Creation
        ↓
       type()
        ↓
   class creation
        ↓
    Descriptor
        ↓
 __set_name__()
```

---

# 26. Dynamic ORM Model

Bây giờ kết hợp với Buổi 24.

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.name
        )

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
```

Tạo:

```python
User = type(
    "User",
    (),
    {
        "id": Field(),
        "name": Field(),
        "age": Field(),
    }
)
```

---

# 27. Sử dụng

```python
user = User()

user.id = 1
user.name = "Alice"
user.age = 25

print(user.name)
```

→

```text
Alice
```

---

# 28. Đây chính là bước đầu của Dynamic ORM

Ta có:

```text
Schema
  ↓
Class Factory
  ↓
type()
  ↓
Dynamic Model
  ↓
Descriptor Fields
  ↓
Instance
```

Ví dụ schema:

```python
schema = {
    "id": int,
    "name": str,
    "age": int,
}
```

có thể trở thành:

```python
User
```

runtime.

---

# 29. Tạo Field tự động từ schema

Ta có:

```python
class IntegerField(Field):
    pass


class StringField(Field):
    pass
```

Sau đó:

```python
TYPE_TO_FIELD = {
    int: IntegerField,
    str: StringField,
}
```

Viết factory:

```python
def create_model(name, schema):

    namespace = {}

    for field_name, field_type in schema.items():

        field_class = TYPE_TO_FIELD[field_type]

        namespace[field_name] = field_class()

    return type(
        name,
        (),
        namespace
    )
```

---

# 30. Sử dụng

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
        "age": int,
    }
)
```

Bây giờ:

```python
user = User()

user.id = 1
user.name = "Alice"
user.age = 25
```

Ta vừa xây một **Dynamic Model Generator** rất nhỏ.

---

# 31. Thêm validation

Ta cải tiến:

```python
class Field:

    python_type = object

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.name
        )

    def __set__(self, instance, value):

        if not isinstance(
            value,
            self.python_type
        ):
            raise TypeError(
                f"{self.name} "
                f"must be "
                f"{self.python_type.__name__}"
            )

        instance.__dict__[self.name] = value
```

---

# 32. Field con

```python
class IntegerField(Field):
    python_type = int


class StringField(Field):
    python_type = str
```

---

# 33. Dynamic model

```python
TYPE_TO_FIELD = {
    int: IntegerField,
    str: StringField,
}


def create_model(name, schema):

    namespace = {}

    for field_name, field_type in schema.items():

        field_class = TYPE_TO_FIELD[field_type]

        namespace[field_name] = field_class()

    return type(
        name,
        (),
        namespace
    )
```

---

# 34. Test

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
        "age": int,
    }
)
```

Sau đó:

```python
user = User()

user.id = 1
user.name = "Alice"
user.age = 25
```

Nhưng:

```python
user.age = "twenty five"
```

sẽ:

```text
TypeError
```

---

# 35. Đây đã rất gần Framework

Ta đã có:

```text
Schema
   ↓
Factory
   ↓
Dynamic Class
   ↓
Descriptor
   ↓
Validation
```

Thêm database:

```text
Schema
   ↓
Dynamic Model
   ↓
ORM
   ↓
Database
```

---

# 36. Dynamic Class có thể thêm `__init__`

Hiện tại:

```python
user = User()
```

sau đó phải:

```python
user.id = 1
user.name = "Alice"
```

Ta muốn:

```python
user = User(
    id=1,
    name="Alice",
    age=25,
)
```

Ta có thể tạo `__init__` động.

---

# 37. Tạo `__init__` factory

```python
def create_init(fields):

    def __init__(self, **kwargs):

        for name in fields:

            if name in kwargs:
                setattr(
                    self,
                    name,
                    kwargs[name]
                )

    return __init__
```

---

# 38. Đưa vào class namespace

```python
def create_model(name, schema):

    namespace = {}

    for field_name, field_type in schema.items():

        field_class = TYPE_TO_FIELD[field_type]

        namespace[field_name] = field_class()

    namespace["__init__"] = create_init(
        schema
    )

    return type(
        name,
        (),
        namespace
    )
```

---

# 39. Sử dụng

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
        "age": int,
    }
)
```

Sau đó:

```python
user = User(
    id=1,
    name="Alice",
    age=25,
)
```

---

# 40. Kiểm tra

```python
print(user.id)
print(user.name)
print(user.age)
```

Kết quả:

```text
1
Alice
25
```

---

# 41. Một insight rất quan trọng

Ta vừa tạo function:

```python
create_init()
```

trả về:

```python
__init__
```

sau đó đưa function vào:

```python
namespace
```

rồi:

```python
type()
```

tạo class.

Nghĩa là:

```text
function factory
      ↓
function
      ↓
class namespace
      ↓
type()
      ↓
class
```

---

# 42. Dynamic class không có nghĩa là "eval"

Một số người mới học dynamic class nghĩ đến:

```python
exec(...)
```

Ví dụ:

```python
code = """
class User:
    pass
"""

exec(code)
```

Cách này có thể chạy, nhưng thường **không phải lựa chọn tốt**.

---

# 43. `type()` vs `exec()`

### `type()`

```python
type(
    "User",
    bases,
    namespace
)
```

Ưu điểm:

* rõ ràng
* có cấu trúc
* an toàn hơn
* dễ kiểm soát
* phù hợp framework

### `exec()`

```python
exec(code)
```

Ưu điểm:

* cực kỳ linh hoạt

Nhược điểm:

* khó kiểm soát
* khó debug
* dễ tạo vấn đề security
* code generation phức tạp

Trong phần lớn trường hợp tạo class động:

> Ưu tiên `type()` hoặc class/metaclass machinery thay vì `exec()`.

---

# 44. Dynamic class và Plugin Architecture

Đây là một ứng dụng rất gần với những gì bạn đang học về Plugin Architecture.

Ví dụ plugin config:

```python
plugins = {
    "NovelPlugin": {
        "source": "example.com",
    },
    "BookPlugin": {
        "source": "books.com",
    },
}
```

Framework có thể tạo các class runtime.

```text
plugin config
     ↓
factory
     ↓
dynamic class
     ↓
plugin registry
```

Tất nhiên plugin thật thường dùng class/module import động thay vì tạo mọi class từ `type()`, nhưng tư tưởng object model là tương tự.

---

# 45. Dynamic class và Serialization

Giả sử JSON:

```json
{
    "name": "Alice",
    "age": 25
}
```

Framework có thể sinh model:

```text
JSON schema
    ↓
fields
    ↓
dynamic class
    ↓
User
```

Sau đó:

```python
user.name
user.age
```

Đây là ý tưởng phía sau nhiều hệ thống schema/model generation.

---

# 46. Dynamic class và ORM

Ví dụ database metadata:

```text
users
 ├── id INTEGER
 ├── name TEXT
 └── age INTEGER
```

Framework có thể tạo:

```text
User
 ├── id = IntegerField()
 ├── name = StringField()
 └── age = IntegerField()
```

Sau đó:

```python
user.name
```

được xử lý bởi Descriptor.

Đây là sự kết hợp:

```text
Dynamic Class Creation
+
Descriptor
+
Metadata
```

---

# 47. Một kiến trúc nhỏ

Ta có:

```text
                Schema
                  │
                  ▼
            create_model()
                  │
                  ▼
                type()
                  │
                  ▼
             Model Class
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Field     Method    Metadata
        │
        ▼
    Descriptor
        │
        ▼
     Instance
```

Đây là kiến trúc rất quan trọng cần ghi nhớ.

---

# 48. Một điểm sâu: Class Creation có lifecycle

Khi framework tạo class, về tư duy có thể hình dung:

```text
1. Chuẩn bị namespace
        ↓
2. Đặt attributes vào namespace
        ↓
3. Chọn metaclass
        ↓
4. Tạo class object
        ↓
5. Gọi __set_name__
        ↓
6. Gọi __init_subclass__
        ↓
7. Trả về class
```

Ở buổi 26, chúng ta mới đang kiểm soát phần:

```text
namespace
   ↓
type()
```

Đến Buổi 27, chúng ta sẽ bắt đầu **can thiệp trực tiếp vào class creation bằng Metaclass**.

---

# 49. So sánh 3 tầng

### Tầng 1 — Instance

```python
user = User()
```

### Tầng 2 — Class

```python
User
```

### Tầng 3 — Metaclass

```python
type
```

Dynamic class creation:

```text
type(...)
  ↓
User
  ↓
User(...)
  ↓
user
```

---

# 50. Liên hệ với Buổi 25

Buổi 25:

```python
type(User)
```

cho ta:

```text
type
```

Buổi 26:

```python
type(
    "User",
    (),
    {}
)
```

cho ta:

```text
User
```

Vậy:

```text
Buổi 25
"Class là object"

        ↓

Buổi 26
"Class có thể được tạo động"

        ↓

Buổi 27
"Ta có thể kiểm soát việc tạo Class"
```

Và đó chính là **Metaclass**.

---

# 51. Mini Project cuối buổi

Hãy tự xây:

```python
User = create_model(
    "User",
    {
        "id": int,
        "name": str,
        "age": int,
    }
)
```

Yêu cầu:

### 1. Có Descriptor

```python
user.name
```

### 2. Có validation

```python
user.age = "abc"
```

phải lỗi.

### 3. Có constructor

```python
user = User(
    id=1,
    name="Alice",
    age=25,
)
```

### 4. Có `__repr__`

Kết quả:

```text
User(id=1, name='Alice', age=25)
```

### 5. Có metadata

```python
User._fields
```

phải chứa:

```text
id
name
age
```

---

# 52. Bài tập Deep Dive

## Bài 1

Tạo class:

```python
Person
```

bằng:

```python
type()
```

với:

```python
name = "Alice"
age = 25
```

---

## Bài 2

Thêm method:

```python
def introduce(self):
    return f"{self.name} - {self.age}"
```

---

## Bài 3

Tạo:

```python
Student
```

kế thừa:

```python
Person
```

bằng `type()`.

---

## Bài 4

Tạo class factory:

```python
create_model(
    name,
    fields
)
```

với:

```python
fields = {
    "name": str,
    "age": int,
}
```

---

## Bài 5 — Quan trọng

Giải thích:

```python
User = type(
    "User",
    (Model,),
    {
        "name": StringField(),
        "age": IntegerField(),
    }
)
```

theo thứ tự:

```text
name
↓
bases
↓
namespace
↓
type
↓
class object
↓
Descriptor
↓
instance
```

---

# 53. Tổng kết Buổi 26

Hôm nay bạn cần nắm chắc 8 ý:

```text
1. Class là object.

2. type() có thể tạo class.

3. type(name, bases, namespace).

4. namespace chứa attributes/methods/descriptors.

5. bases quyết định inheritance.

6. Class Factory có thể tạo class runtime.

7. Dynamic class vẫn sử dụng đầy đủ
   Descriptor, MRO, inheritance, method binding.

8. Dynamic Class Creation là nền tảng để hiểu
   Metaclass.
```

Đặc biệt hãy nhớ mô hình:

```text
                 type
                  │
             type(...)
                  │
                  ▼
              User class
                  │
               User()
                  │
                  ▼
               user
```

và:

```text
Schema
  ↓
Factory
  ↓
type()
  ↓
Dynamic Class
  ↓
Descriptor / Method / Metadata
  ↓
Instance
```

---

# Buổi 27 — Metaclass

Theo đúng roadmap ban đầu, bài tiếp theo sẽ đi vào **Metaclass thực sự**:

```python
class ModelMeta(type):

    def __new__(...):
        ...
```

Chúng ta sẽ trả lời các câu hỏi quan trọng:

* Metaclass chính xác là gì?
* `class User(metaclass=ModelMeta)` hoạt động thế nào?
* Vì sao `type` là metaclass mặc định?
* Metaclass khác class bình thường ở đâu?
* `type(User)` và `User.__class__` liên quan thế nào?
* Metaclass có thể intercept class creation ra sao?
* Tự xây `ModelMeta` cho Mini ORM như thế nào?
* Tại sao Django/ORM/framework thường sử dụng metaclass?
