# OOP Deep Dive — Buổi 21

# Descriptor Protocol Deep Dive

Hôm nay chúng ta bước vào một phần **rất quan trọng của Python OOP**: **Descriptor**.

Nếu hiểu Descriptor thật sự, bạn sẽ hiểu sâu hơn rất nhiều về:

* `property`
* method
* `classmethod`
* `staticmethod`
* ORM
* lazy loading
* validation
* framework internals

Đặc biệt, Descriptor là một trong những cơ chế khiến Python có khả năng **thay đổi hành vi của việc truy cập attribute**.

---

# 1. Descriptor là gì?

Nói đơn giản:

> **Descriptor là một object định nghĩa một hoặc nhiều method đặc biệt `__get__()`, `__set__()`, `__delete__()` để điều khiển việc truy cập attribute.**

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("GET")

    def __set__(self, instance, value):
        print("SET")

    def __delete__(self, instance):
        print("DELETE")
```

Object `Descriptor` có thể kiểm soát:

```python
obj.attribute
obj.attribute = value
del obj.attribute
```

---

# 2. Descriptor không nằm trong instance

Đây là điểm cực kỳ quan trọng.

Ví dụ:

```python
class User:

    name = Descriptor()
```

Ta có:

```text
User
 │
 ├── name ───────→ Descriptor object
 │
 └── __dict__
```

Khi:

```python
user = User()
```

thì `user.__dict__` **không nhất thiết chứa `name`**.

Descriptor nằm trong:

```python
User.__dict__
```

---

# 3. Ví dụ đầu tiên

```python
class Descriptor:

    def __get__(self, instance, owner):
        print("__get__")
        return "Hello"


class User:

    name = Descriptor()
```

Bây giờ:

```python
user = User()

print(user.name)
```

Kết quả:

```text
__get__
Hello
```

---

# 4. Điều gì đã xảy ra?

Bạn viết:

```python
user.name
```

Python không đơn giản làm:

```python
user.__dict__["name"]
```

Mà cơ chế attribute lookup sẽ kiểm tra class.

Nó phát hiện:

```python
User.__dict__["name"]
```

là một Descriptor.

Sau đó gọi:

```python
descriptor.__get__(
    user,
    User
)
```

---

# 5. `__get__()` có hai tham số quan trọng

```python
def __get__(self, instance, owner):
```

Trong đó:

```text
instance
```

là object đang truy cập.

Ví dụ:

```python
user.name
```

thì:

```python
instance == user
```

Còn:

```text
owner
```

là class.

```python
owner == User
```

---

# 6. Kiểm tra

```python
class Descriptor:

    def __get__(self, instance, owner):

        print("instance:", instance)
        print("owner:", owner)

        return "value"


class User:

    name = Descriptor()
```

```python
user = User()

user.name
```

Có thể thấy:

```text
instance: <User object ...>
owner: <class 'User'>
```

---

# 7. Nhưng nếu truy cập từ class?

```python
User.name
```

thì sao?

Kết quả:

```text
instance: None
owner: <class 'User'>
```

Đây là lý do Descriptor thường viết:

```python
if instance is None:
    return self
```

---

# 8. Pattern quan trọng

```python
class Descriptor:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return ...
```

Pattern này xuất hiện rất nhiều trong Descriptor thực tế.

---

# 9. Descriptor đơn giản lưu dữ liệu

Ta có thể viết:

```python
class Field:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__["value"]

    def __set__(self, instance, value):

        instance.__dict__["value"] = value
```

---

Sau đó:

```python
class User:

    name = Field()
```

```python
user = User()

user.name = "Alice"

print(user.name)
```

Kết quả:

```text
Alice
```

---

# 10. Nhưng có vấn đề

Nếu có:

```python
class User:

    name = Field()
    age = Field()
```

thì cả hai đều lưu vào:

```python
instance.__dict__["value"]
```

Vậy:

```python
user.name = "Alice"
user.age = 20
```

sẽ ghi đè nhau.

Cần một cách để Descriptor biết tên attribute của nó.

Đây chính là lúc `__set_name__()` trở nên quan trọng.

---

# 11. `__set_name__()`

Python cung cấp:

```python
def __set_name__(self, owner, name):
```

Nó được gọi khi class được tạo.

Ví dụ:

```python
class Field:

    def __set_name__(self, owner, name):

        print(owner)
        print(name)
```

---

```python
class User:

    name = Field()
    age = Field()
```

Khi class được tạo, Python gọi:

```text
Field.__set_name__(User, "name")
Field.__set_name__(User, "age")
```

---

# 12. Lưu tên attribute

Ta viết:

```python
class Field:

    def __set_name__(self, owner, name):

        self.name = name
```

Bây giờ:

```python
class User:

    name = Field()
    age = Field()
```

Descriptor `name` biết:

```python
self.name == "name"
```

Descriptor `age` biết:

```python
self.name == "age"
```

---

# 13. Hoàn thiện `Field`

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

---

Bây giờ:

```python
class User:

    name = Field()
    age = Field()
```

---

```python
user = User()

user.name = "Alice"
user.age = 20
```

---

```python
print(user.name)
print(user.age)
```

Kết quả:

```text
Alice
20
```

---

# 14. Đây chính là một ORM primitive

Chúng ta vừa xây dựng một phiên bản cực kỳ đơn giản của:

```python
class User:

    name = Field()
    age = Field()
```

Thay vì:

```python
user.__dict__["name"]
```

ta có:

```python
user.name
```

Descriptor đứng giữa:

```text
user.name

   ↓

Field.__get__()

   ↓

user.__dict__["name"]
```

---

# 15. Data Descriptor

Descriptor có:

```python
__set__()
```

hoặc:

```python
__delete__()
```

được gọi là **Data Descriptor**.

Ví dụ:

```python
class Field:

    def __get__(...):
        ...

    def __set__(...):
        ...
```

Đây là Data Descriptor.

---

# 16. Non-data Descriptor

Nếu Descriptor chỉ có:

```python
__get__()
```

thì nó là:

> Non-data Descriptor

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "hello"
```

Không có:

```python
__set__
```

---

# 17. Tại sao Data và Non-data quan trọng?

Bởi vì Python có **thứ tự ưu tiên attribute lookup**.

Đây là phần cực kỳ quan trọng.

Giả sử:

```python
class User:

    name = Descriptor()
```

và:

```python
user.__dict__["name"] = "Alice"
```

Python phải quyết định:

```text
Descriptor

hay

instance.__dict__
```

---

# 18. Data Descriptor thắng `instance.__dict__`

Nếu `name` là Data Descriptor:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "Descriptor"

    def __set__(self, instance, value):
        pass
```

và:

```python
user.__dict__["name"] = "Alice"
```

thì:

```python
user.name
```

vẫn trả về:

```text
Descriptor
```

---

# 19. Tại sao?

Thứ tự lookup đơn giản hóa:

```text
obj.attr

   ↓

Data Descriptor?

   ↓ yes

descriptor.__get__()

   ↓ no

instance.__dict__?

   ↓ yes

value

   ↓ no

Non-data Descriptor / class attribute

   ↓

__getattr__()
```

Đây là một trong những sơ đồ quan trọng nhất của Python OOP.

---

# 20. Non-data Descriptor có thể bị shadow

Ví dụ:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "Descriptor"
```

---

```python
class User:

    name = Descriptor()
```

Sau đó:

```python
user = User()

user.__dict__["name"] = "Alice"
```

Bây giờ:

```python
print(user.name)
```

↓

```text
Alice
```

Instance attribute đã **shadow** Non-data Descriptor.

---

# 21. Đây chính là lý do method hoạt động như vậy

Bạn đã học:

```python
class User:

    def hello(self):
        print("Hello")
```

Khi:

```python
user.hello
```

Python tìm:

```python
User.__dict__["hello"]
```

Đó là một function object.

Function object có:

```python
__get__()
```

Do đó function là một **Non-data Descriptor**.

---

# 22. Descriptor và Method

Ta sẽ học kỹ ở **Buổi 23**, nhưng có thể hình dung:

```python
user.hello
```

được biến đổi thành một bound method tương đương về mặt ý tưởng:

```python
User.hello.__get__(user, User)
```

Đây là cơ chế khiến:

```python
user.hello()
```

tự động có:

```python
self == user
```

---

# 23. Descriptor có thể validation

Ví dụ:

```python
class PositiveNumber:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):

        if value < 0:
            raise ValueError(
                f"{self.name} must be >= 0"
            )

        instance.__dict__[self.name] = value
```

---

Sử dụng:

```python
class Product:

    price = PositiveNumber()
    stock = PositiveNumber()
```

---

```python
product = Product()

product.price = 100
product.stock = 20
```

Hoạt động.

Nhưng:

```python
product.price = -10
```

↓

```text
ValueError
```

---

# 24. Descriptor có thể type validation

```python
class StringField:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):

        if not isinstance(value, str):
            raise TypeError(
                f"{self.name} must be str"
            )

        instance.__dict__[self.name] = value
```

---

Sử dụng:

```python
class User:

    name = StringField()
```

```python
user.name = "Alice"
```

OK.

Nhưng:

```python
user.name = 123
```

↓

```text
TypeError
```

---

# 25. Descriptor có thể Lazy Loading

Đây là kỹ thuật cực kỳ quan trọng.

Ví dụ:

```python
class LazyField:

    def __init__(self, loader):

        self.loader = loader
```

Khi:

```python
user.profile
```

lần đầu:

```text
Database

↓

Load Profile

↓

Cache vào instance
```

Lần sau:

```text
user.profile

↓

Cache

↓

Không query DB
```

Đây chính là nền tảng của **Lazy Loading** trong nhiều ORM/framework.

---

# 26. Descriptor có thể Proxy

Ví dụ:

```python
user.name
```

không nhất thiết phải đọc từ:

```python
user.__dict__
```

Nó có thể:

```text
user.name
    ↓
Descriptor
    ↓
Remote API
    ↓
Database
    ↓
Cache
```

Người sử dụng vẫn chỉ thấy:

```python
user.name
```

---

# 27. Descriptor có thể quản lý computed field

Ví dụ:

```python
class FullName:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return (
            f"{instance.first_name} "
            f"{instance.last_name}"
        )
```

---

```python
class User:

    full_name = FullName()

    def __init__(self, first, last):

        self.first_name = first
        self.last_name = last
```

---

```python
user = User("John", "Doe")

print(user.full_name)
```

↓

```text
John Doe
```

`full_name` không cần lưu trong `__dict__`.

---

# 28. Descriptor và `property`

Bạn có thể nghĩ:

```python
@property
def name(self):
    ...
```

là một cơ chế đặc biệt.

Thực tế:

> `property` chính là một **Descriptor được Python cung cấp sẵn**.

Buổi 22 chúng ta sẽ mổ xẻ chính xác điều này.

---

# 29. Attribute Lookup — mô hình tổng quát

Khi Python gặp:

```python
obj.attr
```

ta có thể hình dung:

```text
                obj.attr
                   │
                   ▼
       object.__getattribute__()
                   │
                   ▼
        Tìm trong class/MRO
                   │
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
   Data Descriptor?       Không
          │                 │
          ▼                 ▼
     __get__()       instance.__dict__
                            │
                      ┌─────┴─────┐
                      │           │
                     Có          Không
                      │           │
                      ▼           ▼
                    value    Non-data Descriptor
                                      │
                                      ▼
                                  __get__()
                                      │
                                      ▼
                                Class attribute
                                      │
                                      ▼
                                 __getattr__()
```

Đây là mô hình tư duy cực kỳ quan trọng.

---

# 30. Descriptor nằm ở đâu?

Thông thường:

```python
class User:

    name = Field()
```

thì:

```python
User.__dict__["name"]
```

là:

```text
Field object
```

Còn:

```python
user.__dict__
```

có thể là:

```python
{
    "name": "Alice"
}
```

---

# 31. Hai object khác nhau

Đây là điểm cần ghi nhớ.

```python
User.name
```

và:

```python
user.name
```

không nhất thiết trả về cùng thứ.

Ví dụ:

```python
class Field:

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__[self.name]
```

Khi:

```python
User.name
```

↓

Descriptor object.

Khi:

```python
user.name
```

↓

Giá trị `"Alice"`.

---

# 32. Descriptor Protocol

Có ba method chính:

```python
__get__()
__set__()
__delete__()
```

Ngoài ra còn có:

```python
__set_name__()
```

để descriptor biết mình được gán cho attribute nào.

---

# 33. Bảng tổng kết

| Method         | Vai trò                               |
| -------------- | ------------------------------------- |
| `__get__`      | Đọc attribute                         |
| `__set__`      | Gán attribute                         |
| `__delete__`   | Xóa attribute                         |
| `__set_name__` | Nhận tên attribute khi class được tạo |

---

# 34. Data vs Non-data Descriptor

| Loại     | `__get__` | `__set__` / `__delete__` |
| -------- | --------: | -----------------------: |
| Non-data |         ✅ |                        ❌ |
| Data     |         ✅ |                        ✅ |

Quy tắc quan trọng:

```text
Data Descriptor
    >
instance.__dict__
    >
Non-data Descriptor
    >
class attribute
```

Đây là simplified lookup order; MRO và `__getattr__()` còn tham gia vào toàn bộ cơ chế.

---

# 35. Một Descriptor hoàn chỉnh

Hãy viết lại:

```python
class Field:

    def __init__(self, default=None):

        self.default = default

    def __set_name__(self, owner, name):

        self.name = name

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__.get(
            self.name,
            self.default
        )

    def __set__(self, instance, value):

        instance.__dict__[self.name] = value

    def __delete__(self, instance):

        instance.__dict__.pop(
            self.name,
            None
        )
```

---

Sử dụng:

```python
class User:

    name = Field()
    age = Field(18)
```

---

```python
user = User()

print(user.age)
```

↓

```text
18
```

---

```python
user.age = 25

print(user.age)
```

↓

```text
25
```

---

```python
del user.age
```

Sau đó:

```python
print(user.age)
```

↓

```text
18
```

---

# 36. Đây là nền tảng của ORM

Hãy tưởng tượng:

```python
class User:

    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

Sau này ta có thể biến:

```python
user.name
```

thành:

```text
Descriptor
      ↓
Field metadata
      ↓
ORM
      ↓
Database
```

Ví dụ:

```python
user.name
```

có thể tương ứng với:

```sql
SELECT name FROM users WHERE id = ?
```

Đây là ý tưởng nền tảng để chúng ta xây dựng ORM mini ở **Buổi 24**.

---

# 37. Liên hệ với project crawler của bạn

Giả sử model:

```python
class Novel:

    id = IntegerField()
    title = StringField()
    author = StringField()
    status = StringField()
```

Ta có:

```python
novel.title
```

hoặc:

```python
novel.author
```

Nhưng phía dưới có thể là:

```text
Novel
  │
  ├── title → Descriptor
  ├── author → Descriptor
  ├── status → Descriptor
  │
  ▼
Model metadata
  │
  ▼
Repository
  │
  ▼
SQLite
```

Đây chính là hướng chúng ta sẽ đi tới ở Buổi 24.

---

# 38. Những lỗi rất thường gặp

### Lỗi 1 — Lưu dữ liệu vào Descriptor

Không nên:

```python
class Field:

    def __set__(self, instance, value):

        self.value = value
```

Vì:

```python
user1.name = "Alice"
user2.name = "Bob"
```

sẽ làm hai instance dùng chung:

```python
Field.value
```

---

### Lỗi 2 — Quên `instance is None`

Nên có:

```python
if instance is None:
    return self
```

để:

```python
User.name
```

không bị lỗi.

---

### Lỗi 3 — Không hiểu Data Descriptor

Đây là lỗi nguy hiểm nhất.

Nếu bạn không hiểu:

```text
Data Descriptor
>
instance.__dict__
>
Non-data Descriptor
```

thì rất khó hiểu:

* `property`
* method
* ORM
* lazy loading
* framework internals.

---

# 39. Bài tập

## Bài 1 — `StringField`

Viết:

```python
class StringField:
    ...
```

Yêu cầu:

```python
class User:

    name = StringField()
```

Phải:

```python
user.name = "Alice"
```

nhưng:

```python
user.name = 123
```

phải ném `TypeError`.

---

## Bài 2 — `PositiveIntegerField`

```python
class Product:

    stock = PositiveIntegerField()
```

Cho phép:

```python
product.stock = 100
```

Không cho:

```python
product.stock = -1
```

và:

```python
product.stock = "100"
```

---

## Bài 3 — `DefaultField`

```python
class User:

    name = Field("Anonymous")
    age = Field(18)
```

Khi:

```python
user = User()
```

phải có:

```python
user.name == "Anonymous"
user.age == 18
```

---

## Bài 4 — Phân tích sâu

Không chạy code, hãy dự đoán kết quả:

```python
class Descriptor:

    def __get__(self, instance, owner):
        return "descriptor"

    def __set__(self, instance, value):
        instance.__dict__["x"] = value


class A:

    x = Descriptor()


a = A()

a.__dict__["x"] = "instance"

print(a.x)
```

**Câu hỏi:** Vì sao kết quả không phải `"instance"`?

---

# 40. Bài tập quan trọng nhất

Tự viết một `Field` có:

```python
class Field:

    def __init__(
        self,
        field_type,
        default=None
    ):
        ...
```

Cho phép:

```python
class User:

    name = Field(str)
    age = Field(int)
```

Sau đó:

```python
user.name = "Alice"
user.age = 20
```

hợp lệ.

Nhưng:

```python
user.age = "20"
```

phải:

```text
TypeError
```

---

# Tổng kết Buổi 21

Hôm nay bạn cần nắm chắc 5 ý:

### 1. Descriptor là object điều khiển attribute access

```python
obj.attr
```

có thể dẫn đến:

```python
descriptor.__get__(...)
```

### 2. Descriptor nằm trên class

```python
class User:

    name = Field()
```

### 3. Data Descriptor có độ ưu tiên cao hơn `instance.__dict__`

```text
Data Descriptor
>
instance.__dict__
>
Non-data Descriptor
```

### 4. `__set_name__()` giúp Descriptor biết tên field

```python
name = Field()

↓

__set_name__(User, "name")
```

### 5. Descriptor là nền tảng của rất nhiều cơ chế Python

```text
Descriptor
    │
    ├── property
    ├── method
    ├── classmethod
    ├── staticmethod
    ├── ORM
    ├── validation
    └── lazy loading
```

---

## Roadmap tiếp theo

Chúng ta giữ **đúng roadmap gốc**:

**Buổi 22 — `property` thực chất hoạt động ra sao**

Ta sẽ không chỉ học cách dùng:

```python
@property
```

mà sẽ **tự xây dựng một phiên bản `property` bằng Descriptor**, rồi giải thích chính xác:

```python
user.name
```

→ `property.__get__()`

và:

```python
user.name = "Alice"
```

→ `property.__set__()`

Từ đó bạn sẽ thấy `@property` không phải là "phép thuật" của Python, mà chỉ là một ứng dụng rất đẹp của **Descriptor Protocol**.
