# OOP Deep Dive – Buổi 15

# Descriptor Protocol – Trái tim của OOP Python

> **Đây là một trong những buổi quan trọng nhất của toàn bộ khóa học.**

Nếu bạn hỏi:

> **"Cơ chế OOP mạnh nhất của Python là gì?"**

Câu trả lời gần như luôn là:

# Descriptor Protocol

Rất nhiều người dùng Python 10 năm vẫn chưa thực sự hiểu Descriptor.

Nhưng khi hiểu rồi, bạn sẽ hiểu được:

- `@property`
- method
- bound method
- `classmethod`
- `staticmethod`
- `cached_property`
- ORM (SQLAlchemy)
- Django Model
- Pydantic
- dataclass (một phần)
- attrs
- PySide6 Property

đều được xây dựng trên cùng một cơ chế.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Descriptor Protocol
- `__get__`
- `__set__`
- `__delete__`
- Attribute Lookup
- Data Descriptor
- Non-data Descriptor
- Vì sao method cũng là descriptor

---

# 1. Mọi chuyện bắt đầu từ Attribute Lookup

Giả sử

```text-x-trilium-auto
class Person:

    def __init__(self):
        self.name = "Alice"

p = Person()

print(p.name)
```

Câu hỏi:

Python lấy `"Alice"` ở đâu?

Có phải chỉ đơn giản:

```text-x-trilium-auto
object

↓

dictionary

↓

return
```

Không.

Python làm nhiều việc hơn rất nhiều.

---

# 2. Object có `__dict__`

Ví dụ

```text-x-trilium-auto
class Person:

    def __init__(self):

        self.name = "Alice"

        self.age = 20
```

```text-x-trilium-auto
p = Person()

print(p.__dict__)
```

Kết quả

```text-x-trilium-auto
{
    'name': 'Alice',
    'age': 20
}
```

Đây là nơi lưu attribute của object.

---

# 3. Class cũng có `__dict__`

```text-x-trilium-auto
class Person:

    species = "Human"
```

```text-x-trilium-auto
print(Person.__dict__)
```

Kết quả

```text-x-trilium-auto
mappingproxy(...)
```

Trong đó có:

```text-x-trilium-auto
species
```

---

# 4. Khi đọc thuộc tính

Ví dụ

```text-x-trilium-auto
print(p.name)
```

Python **không** đọc ngay `__dict__`.

Nó thực hiện một quy trình gọi là:

> **Attribute Lookup**

---

# 5. Lookup đơn giản

```text-x-trilium-auto
Instance

↓

__dict__

↓

Có?

↓

Return

↓

Không

↓

Class

↓

Base Class

↓

object
```

Nhưng...

Đây **vẫn chưa đầy đủ**.

---

# 6. Descriptor chen vào giữa

Thực tế:

```text-x-trilium-auto
Instance

↓

Descriptor ?

↓

Có

↓

Descriptor xử lý

↓

Không

↓

Instance __dict__

↓

Class

↓

...
```

Descriptor có quyền **can thiệp** vào việc đọc ghi xóa attribute.

---

# 7. Descriptor là gì?

Một object có một trong các method:

```text-x-trilium-auto
__get__()

__set__()

__delete__()
```

được gọi là:

Descriptor.

---

# 8. Descriptor đơn giản nhất

```text-x-trilium-auto
class NameDescriptor:

    def __get__(self, instance, owner):

        print("GET")

        return "Alice"
```

Sử dụng

```text-x-trilium-auto
class Person:

    name = NameDescriptor()
```

---

# 9. Thử chạy

```text-x-trilium-auto
p = Person()

print(p.name)
```

Kết quả

```text-x-trilium-auto
GET

Alice
```

Không hề có:

```text-x-trilium-auto
self.name
```

Nhưng vẫn hoạt động.

---

# 10. `__get__()` nhận gì?

```text-x-trilium-auto
def __get__(

    self,

    instance,

    owner
):
```

Có ba tham số.

---

## self

Chính descriptor.

---

## instance

Object đang truy cập.

Ví dụ

```text-x-trilium-auto
p.name
```

instance là:

```text-x-trilium-auto
p
```

---

## owner

Lớp sở hữu descriptor.

Ở đây

```text-x-trilium-auto
Person
```

---

# 11. Ví dụ

```text-x-trilium-auto
class Name:

    def __get__(self, instance, owner):

        print(instance)

        print(owner)

        return "ABC"
```

Kết quả

```text-x-trilium-auto
<Person object>

<class Person>
```

---

# 12. Descriptor ghi dữ liệu

```text-x-trilium-auto
class Age:

    def __set__(

        self,

        instance,

        value
    ):

        print(value)
```

---

```text-x-trilium-auto
class Person:

    age = Age()
```

Thử

```text-x-trilium-auto
p = Person()

p.age = 20
```

Kết quả

```text-x-trilium-auto
20
```

---

# 13. Descriptor đọc + ghi

```text-x-trilium-auto
class Age:

    def __get__(self, instance, owner):

        return instance.__dict__["_age"]


    def __set__(

        self,

        instance,

        value
    ):

        instance.__dict__["_age"] = value
```

---

Sử dụng

```text-x-trilium-auto
class Person:

    age = Age()
```

```text-x-trilium-auto
p = Person()

p.age = 30

print(p.age)
```

Hoạt động như property.

---

# 14. Descriptor Validation

```text-x-trilium-auto
class Positive:

    def __set__(

        self,

        instance,

        value
    ):

        if value < 0:

            raise ValueError

        instance.__dict__["_value"] = value
```

---

```text-x-trilium-auto
class Product:

    price = Positive()
```

Bây giờ

```text-x-trilium-auto
p.price = -10
```

↓

```text-x-trilium-auto
ValueError
```

---

# 15. Descriptor Delete

```text-x-trilium-auto
class Age:

    def __delete__(

        self,

        instance
    ):

        del instance.__dict__["_age"]
```

---

```text-x-trilium-auto
del p.age
```

↓

Descriptor chạy.

---

# 16. Property thực chất là Descriptor

Bạn nghĩ

```text-x-trilium-auto
@property
```

là cú pháp đặc biệt?

Không.

Thực tế

```text-x-trilium-auto
@property

↓

Tạo Descriptor Object
```

`property` là một class trong Python, cài đặt sẵn `__get__()`, `__set__()` và `__delete__()`.

---

# 17. Tự viết Property

Ý tưởng đơn giản:

```text-x-trilium-auto
class MyProperty:

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(instance)
```

Sử dụng

```text-x-trilium-auto
class Person:

    @MyProperty

    def name(self):

        return "Alice"
```

Đây mới chỉ là phiên bản tối giản. `property` thật trong Python còn hỗ trợ setter, deleter và nhiều chi tiết khác.

---

# 18. Method cũng là Descriptor

Ví dụ

```text-x-trilium-auto
class Person:

    def hello(self):

        print("Hello")
```

Khi

```text-x-trilium-auto
p.hello
```

Bạn nghĩ:

```text-x-trilium-auto
Function
```

Sai.

Python trả về:

```text-x-trilium-auto
Bound Method
```

---

# 19. Bound Method

```text-x-trilium-auto
p.hello
```

↓

```text-x-trilium-auto
Function

+

self
```

Đây cũng là Descriptor.

Function object có:

```text-x-trilium-auto
__get__()
```

---

# 20. Thử

```text-x-trilium-auto
print(type(Person.hello))
```

↓

```text-x-trilium-auto
function
```

---

```text-x-trilium-auto
print(type(p.hello))
```

↓

```text-x-trilium-auto
method
```

Tại sao?

Descriptor.

---

# 21. Data Descriptor

Descriptor có:

```text-x-trilium-auto
__set__
```

hoặc

```text-x-trilium-auto
__delete__
```

↓

Data Descriptor

Ví dụ

```text-x-trilium-auto
@property
```

---

# 22. Non-data Descriptor

Chỉ có

```text-x-trilium-auto
__get__
```

↓

Non-data Descriptor

Ví dụ

Function

Method

`staticmethod` (ở dạng đơn giản)

---

# 23. Lookup đầy đủ

Đây là sơ đồ rất quan trọng.

```text-x-trilium-auto
instance.attr

        │

        ▼

Data Descriptor ?

        │

     Có ▼ Không

 Descriptor

        │

        ▼

Instance __dict__

        │

        ▼

Non-data Descriptor

        │

        ▼

Class Attribute

        │

        ▼

Base Class
```

Đây là quy trình Python thực hiện mỗi lần bạn truy cập thuộc tính.

---

# 24. SQLAlchemy

ORM

```text-x-trilium-auto
class Book:

    title = Column(String)
```

`Column`

không phải string.

Nó là:

Descriptor.

---

Khi

```text-x-trilium-auto
book.title = "ABC"
```

Descriptor xử lý.

---

# 25. Django ORM

```text-x-trilium-auto
class Book(Model):

    title = models.CharField(...)
```

`CharField`

↓

Descriptor.

---

# 26. PySide6

Qt Property

↓

Descriptor.

---

# 27. Áp dụng vào hệ thống crawler

Ví dụ

```text-x-trilium-auto
class Url:

    def __set__(

        self,

        instance,

        value
    ):

        if not value.startswith("https://"):

            raise ValueError

        instance.__dict__["url"] = value
```

---

```text-x-trilium-auto
class Novel:

    url = Url()
```

Mỗi lần

```text-x-trilium-auto
novel.url = ...
```

Descriptor sẽ kiểm tra URL hợp lệ.

---

# 28. Tổng kết

```text-x-trilium-auto
                 Descriptor

                      │

      ┌───────────────┼───────────────┐

      ▼               ▼               ▼

   __get__        __set__       __delete__

      │

      ▼

 Attribute Lookup

      │

      ▼

property / method / ORM / cached_property
```

---

# Điều quan trọng nhất cần nhớ

Descriptor là **cơ chế nền tảng** của Python để kiểm soát việc truy cập thuộc tính.

Rất nhiều tính năng "cao cấp" thực chất chỉ là các descriptor được viết sẵn.

Nếu hiểu Descriptor, bạn sẽ hiểu cách Python xây dựng:

- `property`
- method
- ORM
- validation
- lazy loading
- cache

---

# Bài tập thực hành

## Bài 1

Viết một descriptor `PositiveNumber`:

- Chỉ cho phép giá trị > 0.
- Dùng cho:

```text-x-trilium-auto
class Product:
    price = PositiveNumber()
```

Thử gán:

```text-x-trilium-auto
product.price = -5
```

và quan sát kết quả.

---

## Bài 2

Viết descriptor `UpperCaseString`:

- Khi gán:

```text-x-trilium-auto
user.name = "garden dau"
```

tự động lưu thành:

```text-x-trilium-auto
GARDEN DAU
```

---

## Bài 3

Tự viết một phiên bản rút gọn của `property`:

- Hỗ trợ `__get__`.
- Sau đó mở rộng để hỗ trợ `setter`.

Mục tiêu là hiểu cách `@property` hoạt động bên trong.

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế các descriptor:

- `UrlField` (kiểm tra URL hợp lệ).
- `PositiveIntField` (kiểm tra số dương).
- `NonEmptyStringField` (không cho phép chuỗi rỗng).

Áp dụng vào:

```text-x-trilium-auto
class Novel:
    url = UrlField()
    title = NonEmptyStringField()
    chapter_count = PositiveIntField()
```

Hãy để mọi kiểm tra dữ liệu diễn ra tự động khi gán thuộc tính, thay vì phải viết `if` trong nhiều nơi của chương trình.

---

# Chuẩn bị cho Buổi 16

Buổi tiếp theo sẽ tiếp tục đào sâu Descriptor với các chủ đề nâng cao:

- `__set_name__()` (PEP 487).
- Descriptor tái sử dụng cho nhiều thuộc tính.
- Descriptor có trạng thái (stateful descriptors).
- `cached_property` được cài đặt như thế nào.
- Xây dựng một mini ORM bằng Descriptor.
- Cơ chế Field của Django ORM và SQLAlchemy từ góc nhìn Descriptor.

Đây sẽ là bước đưa bạn từ **người sử dụng Descriptor** sang **người có thể tự xây dựng framework** bằng Descriptor.