# OOP Deep Dive — Buổi 25

# `type()` — Class cũng là Object

Đây là buổi mở đầu cho **Phần VII — Metaclass**.

Từ hôm nay chúng ta chuyển từ:

```text
Object
Class
Instance
Descriptor
```

sang tầng sâu hơn:

```text
Class Object
    ↓
type
    ↓
Metaclass
```

Nếu nắm chắc buổi này, các bài **26 → 30 về Dynamic Class Creation và Metaclass** sẽ dễ hiểu hơn rất nhiều.

---

# 1. Nhắc lại mô hình cũ

Ta đã học:

```python
class User:
    pass
```

và:

```python
user = User()
```

Ta thường nghĩ:

```text
User = class
user = object
```

Điều đó đúng, nhưng **chưa đủ sâu**.

Câu hỏi tiếp theo là:

> `User` bản thân nó là gì?

---

# 2. Kiểm tra `type(User)`

```python
class User:
    pass

print(type(User))
```

Kết quả:

```text
<class 'type'>
```

Đây là một trong những dòng code quan trọng nhất của Python OOP.

Nó nói rằng:

```text
User
 ↓
là một object
 ↓
có type là type
```

---

# 3. So sánh `user` và `User`

```python
user = User()

print(type(user))
print(type(User))
```

Kết quả:

```text
<class '__main__.User'>
<class 'type'>
```

Ta có:

```text
user
 ↓
instance của User

User
 ↓
instance của type
```

---

# 4. Đây là mô hình quan trọng

```text
type
 ↑
 │ instance
 │
User
 ↑
 │ instance
 │
user
```

Hay:

```text
user ──instance──> User
User ──instance──> type
```

Đây chính là nền tảng của **Metaclass**.

---

# 5. "Class cũng là object"

Trong Python:

```python
class User:
    pass
```

`User` không phải một thứ gì đó nằm ngoài hệ thống object.

`User` cũng là một object.

Ta có thể:

```python
print(User)
print(id(User))
print(type(User))
```

---

# 6. Class có Identity

Giống mọi object khác:

```python
class User:
    pass

print(id(User))
```

`User` có một identity riêng.

Ví dụ:

```text
User
 ├── identity
 ├── type
 └── value/state
```

---

# 7. Class có Attribute

Ta có:

```python
class User:
    name = "Alice"
```

Có thể:

```python
print(User.name)
```

Tức là class object cũng có attribute.

Thậm chí:

```python
print(User.__dict__)
```

---

# 8. Class có `__dict__`

```python
class User:

    name = "Alice"

    def hello(self):
        print("Hello")
```

Ta có:

```python
print(User.__dict__)
```

Bạn sẽ thấy:

```text
{
    '__module__': ...,
    'name': 'Alice',
    'hello': <function ...>,
    ...
}
```

Đây chính là namespace của class.

---

# 9. Nhưng `User.__dict__` là gì?

Nó là mapping chứa attribute của class.

Ví dụ:

```python
User.__dict__["name"]
```

→

```text
"Alice"
```

và:

```python
User.__dict__["hello"]
```

→ function object.

---

# 10. Class cũng có method

Ví dụ:

```python
User.__dict__
User.__name__
User.__module__
User.__bases__
User.__mro__
```

Những thứ này cho thấy:

> Class object có rất nhiều metadata.

---

# 11. `type()` có hai vai trò

Đây là điểm cực kỳ quan trọng.

`type()` có thể dùng để:

### Vai trò 1 — kiểm tra type

```python
type(obj)
```

Ví dụ:

```python
type(10)
```

→

```text
<class 'int'>
```

---

### Vai trò 2 — tạo class

```python
type(
    name,
    bases,
    namespace
)
```

Đây là phần chúng ta sẽ học sâu hôm nay.

---

# 12. Tạo class bằng `type()`

Thông thường:

```python
class User:
    pass
```

Ta có thể tạo class động:

```python
User = type(
    "User",
    (),
    {}
)
```

Sau đó:

```python
print(User)
```

→

```text
<class '__main__.User'>
```

---

# 13. Ba tham số của `type()`

Cú pháp:

```python
type(
    name,
    bases,
    namespace
)
```

Ví dụ:

```python
User = type(
    "User",
    (),
    {}
)
```

Có:

```text
name
 ↓
"User"

bases
 ↓
()

namespace
 ↓
{}
```

---

# 14. `name`

```python
"User"
```

là tên class.

Tương đương:

```python
class User:
    ...
```

---

# 15. `bases`

```python
()
```

là tuple chứa các base class.

Ví dụ:

```python
class User(Person):
    pass
```

có thể biểu diễn:

```python
User = type(
    "User",
    (Person,),
    {}
)
```

---

# 16. `namespace`

Đây là dictionary chứa nội dung class.

Ví dụ:

```python
{
    "name": "Alice"
}
```

tạo:

```python
User.name
```

---

# 17. Ví dụ

```python
User = type(
    "User",
    (),
    {
        "name": "Alice"
    }
)
```

Bây giờ:

```python
print(User.name)
```

→

```text
Alice
```

---

# 18. Thêm method

Ta có:

```python
def hello(self):
    print("Hello")
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

Tạo object:

```python
user = User()
```

và:

```python
user.hello()
```

→

```text
Hello
```

---

# 19. Điều gì vừa xảy ra?

Ta tạo:

```python
def hello(self):
    ...
```

Function object.

Sau đó đặt function vào namespace:

```python
{
    "hello": hello
}
```

rồi `type()` tạo class.

Khi gọi:

```python
user.hello()
```

function lại hoạt động như Descriptor.

Vậy kiến thức Buổi 23 tiếp tục được sử dụng.

---

# 20. Sơ đồ

```text
namespace
   │
   ├── name
   ├── hello
   └── ...
        │
        ▼
      type()
        │
        ▼
      User
        │
        ▼
      user
```

---

# 21. `type()` thực chất đang làm gì?

Về mặt tư duy:

```python
User = type(
    "User",
    (),
    {
        "name": "Alice"
    }
)
```

có nghĩa:

> Hãy tạo một class object tên `User`, không có base class bổ sung, với namespace chứa `name = "Alice"`.

---

# 22. So sánh hai cách

## Cách thông thường

```python
class User:

    name = "Alice"

    def hello(self):
        print(self.name)
```

## Dynamic

```python
def hello(self):
    print(self.name)


User = type(
    "User",
    (),
    {
        "name": "Alice",
        "hello": hello,
    }
)
```

Về kết quả cơ bản, chúng tương đương.

---

# 23. Class Statement không đơn giản là `type()`

Cần tránh một hiểu lầm:

> `class User:` chỉ đơn giản là gọi `type()`.

Không hoàn toàn.

Class statement còn có các bước như:

```text
class body execution
namespace preparation
metaclass selection
class creation
__set_name__
__init_subclass__
```

Trong những bài sau chúng ta sẽ mổ xẻ từng bước.

Nhưng:

```python
type(name, bases, namespace)
```

là cách rất tốt để hiểu **class object được tạo ra như thế nào**.

---

# 24. `type` bản thân nó là object

Kiểm tra:

```python
print(type(type))
```

Kết quả:

```text
<class 'type'>
```

Đây là một điểm khá "xoắn não".

Ta có:

```text
type(User) == type
```

và:

```text
type(type) == type
```

---

# 25. Tại sao `type` là instance của chính nó?

Đây là một phần của thiết kế object model của Python.

Mô hình:

```text
              type
             ↗    ↖
          instance
           /        \
        User        int
         ↑           ↑
      instance     instance
        /              \
      user              10
```

Cụ thể:

```python
type(user) is User
```

```python
type(User) is type
```

```python
type(int) is type
```

```python
type(type) is type
```

---

# 26. `object` cũng là class

Kiểm tra:

```python
print(type(object))
```

Kết quả:

```text
<class 'type'>
```

Nghĩa là:

```text
object
 ↓
instance của type
```

---

# 27. Quan hệ `type` và `object`

Đây là phần rất quan trọng:

```python
print(type(object))
```

→

```text
type
```

Nhưng:

```python
print(object.__class__)
```

→

```text
type
```

Trong khi:

```python
print(type.__base__)
```

→ tùy implementation, nhưng trong CPython thường là:

```text
object
```

Ta có một quan hệ:

```text
type
 ↓
base
object
```

---

# 28. Hai quan hệ khác nhau

Đừng nhầm:

### Instance relationship

```text
User → type
```

nghĩa:

> User là instance của type.

### Inheritance relationship

```text
User → object
```

nghĩa:

> User kế thừa object.

Ví dụ:

```python
class User:
    pass
```

thực chất có:

```python
User.__bases__
```

→

```python
(object,)
```

---

# 29. Có hai graph

Đây là cách tư duy rất mạnh.

### Inheritance graph

```text
object
  ↑
 User
```

### Instance graph

```text
type
 ↑
User
```

Và:

```text
User
 ↑
user
```

---

# 30. Sơ đồ đầy đủ

```text
              type
               ↑
               │ instance
               │
             User
               ↑
               │ instance
               │
              user


object
  ↑
  │ inheritance
 User
```

Tức:

```text
user is instance of User
User is instance of type
User inherits from object
```

---

# 31. Kiểm tra bằng `isinstance`

```python
class User:
    pass

user = User()

print(isinstance(user, User))
```

→

```text
True
```

Và:

```python
print(isinstance(User, type))
```

→

```text
True
```

---

# 32. `issubclass`

```python
print(issubclass(User, object))
```

→

```text
True
```

Nhưng:

```python
print(issubclass(User, type))
```

thường:

```text
False
```

Đây là điểm nhiều người mới học Metaclass nhầm.

`User` là:

```text
instance của type
```

không có nghĩa:

```text
User là subclass của type
```

---

# 33. Đây là khác biệt cực kỳ quan trọng

```python
isinstance(User, type)
```

hỏi:

> User có phải instance của type không?

Còn:

```python
issubclass(User, type)
```

hỏi:

> User có kế thừa từ type không?

Hai câu hỏi hoàn toàn khác nhau.

---

# 34. Class object có thể được truyền như biến

Vì class là object:

```python
class User:
    pass
```

ta có thể:

```python
cls = User
```

Sau đó:

```python
user = cls()
```

hoạt động.

---

# 35. Class có thể nằm trong list

```python
classes = [
    User,
    str,
    int,
]
```

Ta có thể:

```python
for cls in classes:
    print(cls)
```

Đây là nền tảng cho nhiều cơ chế:

```text
Plugin registry
Dependency Injection
Factory
ORM
Serializer
Framework
```

---

# 36. Class có thể làm dictionary key

```python
registry = {}

registry[User] = "user handler"
registry[str] = "string handler"
```

Vì class là object và có identity/hash.

---

# 37. Class có thể được truyền vào function

```python
def create(cls):
    return cls()
```

Sau đó:

```python
user = create(User)
```

Đây chính là một dạng Factory rất đơn giản.

---

# 38. Dynamic Class Creation

Ví dụ:

```python
def create_model(name):

    return type(
        name,
        (),
        {}
    )
```

Sau đó:

```python
User = create_model("User")
Book = create_model("Book")
```

Ta vừa tạo class lúc runtime.

---

# 39. Tạo nhiều class động

```python
models = {}

for name in ["User", "Book", "Author"]:

    models[name] = type(
        name,
        (),
        {}
    )
```

Bây giờ:

```python
models["User"]
models["Book"]
models["Author"]
```

đều là class object.

---

# 40. Đây là lý do `type()` quan trọng với Framework

Framework có thể nhận configuration:

```python
config = {
    "User": {...},
    "Book": {...},
}
```

rồi tự tạo class:

```text
configuration
      ↓
type()
      ↓
dynamic classes
```

Không cần developer viết từng class thủ công.

---

# 41. Dynamic class có inheritance

Ví dụ:

```python
class Model:
    def save(self):
        print("save")
```

Tạo:

```python
User = type(
    "User",
    (Model,),
    {}
)
```

Bây giờ:

```python
user = User()
user.save()
```

hoạt động.

---

# 42. Kiểm tra

```python
print(User.__bases__)
```

→

```python
(Model,)
```

và:

```python
print(User.__mro__)
```

sẽ có:

```text
User
Model
object
```

---

# 43. Dynamic class + Descriptor

Đây là chỗ kết nối trực tiếp với Buổi 24.

Ta có:

```python
class Field:

    def __get__(
        self,
        instance,
        owner
    ):
        ...
```

Sau đó:

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

`User` được tạo động nhưng vẫn có Descriptor.

---

# 44. Dynamic ORM Model

Ví dụ:

```python
User = type(
    "User",
    (Model,),
    {
        "id": IntegerField(),
        "name": StringField(),
    }
)
```

Ta có:

```python
user = User()

user.name = "Alice"

print(user.name)
```

Descriptor vẫn hoạt động bình thường.

---

# 45. Điều này dẫn đến Metaclass

Hãy tưởng tượng framework muốn tự động:

```text
class User(Model):
    ...
```

→

```text
collect fields
→
register model
→
validate schema
→
generate metadata
```

Ai làm việc này?

> **Metaclass.**

Và metaclass mặc định của class thông thường chính là:

```python
type
```

---

# 46. `type` chính là một metaclass

Một cách hiểu:

> Metaclass là class dùng để tạo class.

Ví dụ:

```text
type
 ↓ creates
User
 ↓ creates
user
```

Tức:

```text
type
   │
   │ creates
   ▼
 User
   │
   │ creates
   ▼
 user
```

---

# 47. Đây là tầng abstraction

Thông thường:

```text
Class
 ↓
Instance
```

Nhưng bây giờ:

```text
Metaclass
 ↓
Class
 ↓
Instance
```

Ví dụ:

```text
type
 ↓
User
 ↓
user
```

---

# 48. `type()` tạo class

Khi viết:

```python
User = type(
    "User",
    (),
    {}
)
```

ta đang trực tiếp sử dụng metaclass:

```text
type
```

để tạo:

```text
User
```

---

# 49. Tự định nghĩa metaclass

Ta có thể:

```python
class MyMeta(type):
    pass
```

Sau đó:

```python
class User(metaclass=MyMeta):
    pass
```

Bây giờ:

```python
type(User)
```

là:

```text
MyMeta
```

thay vì:

```text
type
```

Đây chính là bước đầu tiên vào **Metaclass**.

---

# 50. Nhưng hôm nay chưa đi sâu `MyMeta`

Theo roadmap:

```text
25. type()
26. Dynamic Class Creation
27. Metaclass
28. __new__ của metaclass
29. __prepare__
    __init_subclass__
30. Ứng dụng Metaclass
```

Nên hôm nay chúng ta chỉ cần hiểu thật chắc:

```text
type()
Class Object
Class cũng là object
```

---

# 51. Thí nghiệm quan trọng

Chạy nguyên đoạn này:

```python
class User:
    pass

user = User()

print(type(user))
print(type(User))

print(isinstance(user, User))
print(isinstance(User, type))

print(issubclass(User, object))
print(issubclass(User, type))
```

Hãy tự dự đoán kết quả trước khi chạy.

---

# 52. Thí nghiệm `type()` tạo class

```python
User = type(
    "User",
    (),
    {}
)

user = User()

print(user)
print(type(user))
print(type(User))
```

Dự đoán:

```text
type(user)
    ↓
User

type(User)
    ↓
type
```

---

# 53. Thí nghiệm namespace

```python
def hello(self):
    return "Hello"


User = type(
    "User",
    (),
    {
        "hello": hello,
    }
)

user = User()

print(user.hello())
```

Hãy quan sát:

```text
function
 ↓
namespace
 ↓
type()
 ↓
class
 ↓
descriptor
 ↓
bound method
```

Đây là một chuỗi kiến thức rất đẹp:

```text
Buổi 23 → Buổi 25
```

---

# 54. Thí nghiệm inheritance

```python
class Animal:

    def speak(self):
        return "sound"


Dog = type(
    "Dog",
    (Animal,),
    {}
)
```

Sau đó:

```python
dog = Dog()

print(dog.speak())
```

Kết quả:

```text
sound
```

---

# 55. Dynamic class với attribute

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

và:

```python
user = User()

print(user.species)
```

Đều có thể truy cập được thông qua attribute lookup/inheritance từ class.

---

# 56. Dynamic class với method

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

Sau đó:

```python
user = User()

print(user.greet())
```

→

```text
Hello Alice
```

---

# 57. Điều gì xảy ra phía dưới?

```python
user.greet()
```

Ta đã học:

```text
user.greet
    ↓
User.__dict__["greet"]
    ↓
function descriptor
    ↓
__get__(user, User)
    ↓
bound method
    ↓
greet(user)
```

Nhưng `User` lại được tạo bởi:

```text
type()
```

Vậy:

```text
type
 ↓
User
 ↓
function descriptor
 ↓
bound method
 ↓
user
```

Đây chính là lúc các phần OOP Deep Dive bắt đầu kết nối thành một object model hoàn chỉnh.

---

# 58. Một mô hình cần thuộc

```text
                         type
                          │
                    creates class
                          │
                          ▼
                        User
                          │
                    creates instance
                          │
                          ▼
                         user
```

Trong khi inheritance:

```text
object
   ▲
   │
  User
```

Và method:

```text
User.__dict__["hello"]
          │
          ▼
      function
          │
       __get__
          │
          ▼
    bound method
```

---

# 59. Ba khái niệm không được nhầm

### Object

```python
user
```

### Class Object

```python
User
```

### Metaclass

```python
type
```

Quan hệ:

```text
user
 ↓ instance of
User
 ↓ instance of
type
```

---

# 60. Tư duy quan trọng nhất của Buổi 25

Đừng nghĩ:

```text
class = cú pháp
```

Hãy nghĩ:

```text
class statement
      ↓
class object
```

Ví dụ:

```python
class User:
    pass
```

tạo ra một object:

```text
User
```

object này:

* có identity
* có type
* có namespace
* có attributes
* có bases
* có MRO
* có methods
* có metadata
* có thể được truyền vào function
* có thể được lưu trong biến
* có thể được tạo động

Và:

```python
type(User)
```

cho biết **metaclass của User**.

---

# 61. Bài tập

### Bài 1

Giải thích:

```python
class User:
    pass

user = User()

type(user)
type(User)
```

Tại sao hai kết quả khác nhau?

---

### Bài 2

Viết lại:

```python
class Person:
    species = "human"
```

bằng `type()`.

---

### Bài 3

Viết lại:

```python
class Person:

    def hello(self):
        return "Hello"
```

bằng `type()`.

---

### Bài 4

Tạo:

```python
class Animal:
    def speak(self):
        return "sound"
```

bằng cú pháp bình thường, sau đó tạo:

```python
Dog
```

bằng `type()` sao cho:

```python
issubclass(Dog, Animal)
```

là:

```text
True
```

---

### Bài 5 — Deep Dive

Giải thích toàn bộ chuỗi:

```python
class User:

    def hello(self):
        return "Hello"


user = User()

user.hello()
```

theo các tầng:

```text
class statement
      ↓
class object
      ↓
type
      ↓
function descriptor
      ↓
__get__()
      ↓
bound method
      ↓
user
```

---

# 62. Preview Buổi 26

Theo đúng roadmap:

# **Buổi 26 — Dynamic Class Creation**

Chúng ta sẽ không chỉ dùng:

```python
type("User", (), {})
```

mà sẽ xây một **Class Factory** thực sự:

```python
create_model(
    "User",
    fields={
        "id": int,
        "name": str,
        "age": int,
    }
)
```

để runtime tự tạo:

```python
User
```

với:

* attributes
* methods
* inheritance
* Descriptor
* metadata
* validation

Sau đó chúng ta sẽ nối trực tiếp với **Mini ORM ở Buổi 24**, trước khi bước sang **Metaclass thực sự ở Buổi 27**.
