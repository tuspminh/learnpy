# Metaclass Deep Dive I – `type`, Class Creation và Cơ chế tạo Class trong Python

> Đây là một trong những chủ đề khó nhất nhưng cũng thú vị nhất của Python.

Có một câu nói nổi tiếng của Tim Peters (một trong những tác giả của Python):

> **"Metaclasses are deeper magic than 99% of users should ever worry about."**

Điều đó không có nghĩa là metaclass không quan trọng.

Ngược lại, nếu muốn xây dựng:

- Framework
- ORM
- Plugin System
- Dependency Injection
- Serialization Framework
- GUI Framework

thì metaclass là kiến thức gần như bắt buộc.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- Class là object
- `type`
- `object`
- Mối quan hệ giữa `type` và `object`
- Class Creation
- Metaclass là gì
- Vì sao class cũng là object

---

# 1. Một câu hỏi

Giả sử:

```text-x-trilium-auto
class Person:
    pass
```

Câu hỏi:

`Person` là gì?

Nhiều người trả lời:

> Là class.

Đúng.

Nhưng chưa đủ.

---

# 2. Class cũng là Object

Thử:

```text-x-trilium-auto
class Person:
    pass

print(type(Person))
```

Kết quả

```text-x-trilium-auto
<class 'type'>
```

Điều này có nghĩa:

```text-x-trilium-auto
Person

↓

Object

↓

Được tạo bởi

↓

type
```

---

# 3. Instance

```text-x-trilium-auto
p = Person()

print(type(p))
```

↓

```text-x-trilium-auto
<class '__main__.Person'>
```

Quan sát:

```text-x-trilium-auto
Person

↓

tạo

↓

Person object
```

---

Trong khi:

```text-x-trilium-auto
type

↓

tạo

↓

Person class
```

---

# 4. Sơ đồ

```text-x-trilium-auto
                type

                 │

      tạo class Person

                 │

                 ▼

              Person

                 │

      tạo instance p

                 │

                 ▼

                 p
```

Đây là mô hình của Python.

---

# 5. `type()` có hai vai trò

Bạn đã dùng:

```text-x-trilium-auto
type(obj)
```

Để xem kiểu.

Nhưng còn vai trò thứ hai.

Nó tạo class.

---

# 6. Tạo class bằng `type`

Ví dụ

```text-x-trilium-auto
class Person:
    pass
```

Thực ra tương đương

```text-x-trilium-auto
Person = type(
    "Person",
    (),
    {}
)
```

Kết quả

```text-x-trilium-auto
print(Person)
```

↓

```text-x-trilium-auto
<class '__main__.Person'>
```

Không khác gì class bình thường.

---

# 7. Thêm attribute

```text-x-trilium-auto
Person = type(

    "Person",

    (),

    {

        "name":"Unknown"

    }

)
```

Thử

```text-x-trilium-auto
print(Person.name)
```

↓

```text-x-trilium-auto
Unknown
```

---

# 8. Thêm method

```text-x-trilium-auto
def hello(self):

    print("Hello")
```

---

```text-x-trilium-auto
Person = type(

    "Person",

    (),

    {

        "hello":hello

    }

)
```

---

```text-x-trilium-auto
p = Person()

p.hello()
```

↓

```text-x-trilium-auto
Hello
```

Bạn vừa tạo class bằng code.

---

# 9. Thêm kế thừa

```text-x-trilium-auto
class Animal:
    pass
```

---

```text-x-trilium-auto
Dog = type(

    "Dog",

    (Animal,),

    {}

)
```

Dog kế thừa Animal.

---

# 10. Class là object

Thử

```text-x-trilium-auto
class Person:
    pass
```

---

```text-x-trilium-auto
Person.age = 20
```

Được.

Vì:

```text-x-trilium-auto
Person

↓

Object
```

Object thì có thể gán attribute.

---

# 11. Thêm method sau khi tạo

```text-x-trilium-auto
def hello(self):

    print("Hi")
```

---

```text-x-trilium-auto
Person.hello = hello
```

---

```text-x-trilium-auto
Person().hello()
```

↓

Hoạt động.

---

# 12. `object`

Python có:

```text-x-trilium-auto
object
```

Đây là:

Root class.

Mọi class đều kế thừa.

Ví dụ

```text-x-trilium-auto
class Person:
    pass
```

Thực tế

```text-x-trilium-auto
class Person(object):
    pass
```

---

# 13. Quan hệ kỳ lạ

Thử

```text-x-trilium-auto
print(type(object))
```

↓

```text-x-trilium-auto
<class 'type'>
```

---

Thử

```text-x-trilium-auto
print(type(type))
```

↓

```text-x-trilium-auto
<class 'type'>
```

???

---

# 14. Quan hệ giữa object và type

Đây là sơ đồ nổi tiếng.

```text-x-trilium-auto
              object

                 ▲

                 │

              type

                 ▲

                 │

            Person class

                 ▲

                 │

             Person()
```

Nhưng còn:

```text-x-trilium-auto
type

↓

là instance của

↓

type
```

Tức là:

```text-x-trilium-auto
type(type)
```

↓

```text-x-trilium-auto
type
```

Nghe rất kỳ lạ.

Nhưng đúng.

---

# 15. Kiểm tra

```text-x-trilium-auto
print(isinstance(Person,type))
```

↓

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
print(isinstance(type,type))
```

↓

```text-x-trilium-auto
True
```

---

```text-x-trilium-auto
print(isinstance(object,type))
```

↓

```text-x-trilium-auto
True
```

---

# 16. MRO

Thử

```text-x-trilium-auto
print(Person.__mro__)
```

↓

```text-x-trilium-auto
(
 Person,

 object
)
```

Nếu

```text-x-trilium-auto
class Dog(Animal):
```

↓

```text-x-trilium-auto
Dog

↓

Animal

↓

object
```

---

# 17. Tự tạo Metaclass

```text-x-trilium-auto
class MyMeta(type):
    pass
```

Đây là:

Metaclass.

---

# 18. Sử dụng

```text-x-trilium-auto
class Person(

    metaclass=MyMeta

):
    pass
```

Python sẽ dùng:

```text-x-trilium-auto
MyMeta
```

để tạo class.

Không dùng:

```text-x-trilium-auto
type
```

nữa.

---

# 19. Điều gì xảy ra?

Thông thường

```text-x-trilium-auto
type

↓

Person
```

Bây giờ

```text-x-trilium-auto
MyMeta

↓

Person
```

Metaclass thay thế `type`.

---

# 20. Thử in

```text-x-trilium-auto
class MyMeta(type):

    def __new__(

        cls,

        name,

        bases,

        attrs
    ):

        print(name)

        return super().__new__(

            cls,

            name,

            bases,

            attrs
        )
```

---

```text-x-trilium-auto
class Person(

    metaclass=MyMeta
):
    pass
```

Kết quả

```text-x-trilium-auto
Person
```

Bạn vừa can thiệp vào quá trình tạo class.

---

# 21. Class Creation

Python tạo class theo các bước:

```text-x-trilium-auto
Đọc class

↓

Tạo namespace

↓

Thu thập method

↓

Gọi metaclass

↓

Sinh class object

↓

Class sẵn sàng
```

Metaclass nằm ở bước gần cuối.

---

# 22. Ví dụ thực tế

Giả sử bạn muốn:

Mọi class đều có

```text-x-trilium-auto
id = None
```

Metaclass

```text-x-trilium-auto
class MyMeta(type):

    def __new__(

        cls,

        name,

        bases,

        attrs
    ):

        attrs["id"]=None

        return super().__new__(

            cls,

            name,

            bases,

            attrs
        )
```

---

```text-x-trilium-auto
class User(

    metaclass=MyMeta
):
    pass
```

↓

```text-x-trilium-auto
print(User.id)
```

↓

```text-x-trilium-auto
None
```

Không cần viết trong class.

---

# 23. Django ORM

Bạn viết

```text-x-trilium-auto
class Book(Model):

    title = CharField()
```

Django sẽ:

- tìm tất cả `Field`
- lưu metadata
- tạo SQL
- tạo Descriptor

Ai làm?

↓

Metaclass.

---

# 24. Enum

```text-x-trilium-auto
from enum import Enum

class Color(Enum):

    RED = 1

    BLUE = 2
```

Enum dùng:

Metaclass.

---

# 25. Pydantic

```text-x-trilium-auto
class User(BaseModel):

    age:int
```

Pydantic dùng metaclass (và các hook khác) để:

- thu thập type hints
- tạo validator
- tạo serializer

---

# 26. Áp dụng vào dự án crawler

Giả sử

```text-x-trilium-auto
class TruyenFull(

    BaseSource
):
```

Metaclass có thể:

- tự đăng ký plugin
- kiểm tra plugin hợp lệ
- tạo registry

Không cần:

```text-x-trilium-auto
register(...)
```

---

# 27. Registry

Ví dụ

```text-x-trilium-auto
Registry

↓

TruyenFull

↓

TangThuVien

↓

NovelBin
```

Metaclass có thể tự thêm plugin vào registry ngay khi class được định nghĩa.

---

# 28. Tổng kết

```text-x-trilium-auto
                type

                  │

        tạo mọi class

                  │

                  ▼

            Metaclass

                  │

        can thiệp tạo class

                  │

                  ▼

           Class Object

                  │

                  ▼

            Instance
```

---

# Điều quan trọng nhất cần nhớ

Có **hai giai đoạn khác nhau**:

1. **Tạo class**

```text-x-trilium-auto
type / metaclass

↓

Person
```

2. **Tạo object**

```text-x-trilium-auto
Person

↓

Person()
```

Đừng nhầm lẫn hai quá trình này.

Metaclass **không tạo instance**.

Metaclass tạo **class**.

---

# Bài tập thực hành

## Bài 1

Tạo class bằng `type()`:

```text-x-trilium-auto
Person = type(
    "Person",
    (),
    {
        "name": "Unknown",
    }
)
```

Sau đó:

- thêm `hello()`
- tạo object
- gọi `hello()`.

---

## Bài 2

Viết `MyMeta`.

Trong `__new__()`:

- in tên class.
- in danh sách method.
- tạo class.

Tạo:

```text-x-trilium-auto
class Book(metaclass=MyMeta):
    ...
```

Quan sát kết quả.

---

## Bài 3

Sửa `MyMeta`.

Mỗi class đều tự động có:

```text-x-trilium-auto
created = True
```

Kiểm tra:

```text-x-trilium-auto
Book.created
```

---

## Bài 4 (Áp dụng dự án crawler)

Thiết kế:

```text-x-trilium-auto
class SourceMeta(type):
    ...
```

Mỗi khi có:

```text-x-trilium-auto
class TruyenFull(BaseSource, metaclass=SourceMeta):
    ...
```

`SourceMeta` sẽ tự động:

- lấy tên class.
- thêm vào một `registry` dạng dictionary:

```text-x-trilium-auto
{
    "TruyenFull": TruyenFull,
    "TangThuVien": TangThuVien,
    ...
}
```

Đây là nền tảng để xây dựng **Plugin Manager** tự động phát hiện nguồn truyện mà không cần đăng ký thủ công.

---

# Chuẩn bị cho Buổi 18

Buổi tiếp theo chúng ta sẽ đi sâu hơn vào Metaclass với các chủ đề:

- `__prepare__()`
- `__new__()`
- `__init__()` của Metaclass.
- Sự khác biệt giữa `__new__` và `__init__` trong metaclass.
- Tự xây dựng **Plugin Framework**.
- Tự xây dựng **Mini ORM** sử dụng **Descriptor + Metaclass**.

Đây sẽ là buổi kết nối toàn bộ kiến thức từ:

- Descriptor
- ABC
- Protocol
- Metaclass

để tạo ra một framework Python hoàn chỉnh theo phong cách của Django hoặc SQLAlchemy.