# OOP Deep Dive – Buổi 16

# Descriptor Protocol Deep Dive II – `__set_name__()`, Stateful Descriptor và xây dựng Mini ORM

> Đây là buổi học mà rất nhiều lập trình viên Python chưa từng tiếp cận, dù đã làm việc nhiều năm.

Ở buổi trước, bạn đã biết Descriptor có:

- `__get__()`
- `__set__()`
- `__delete__()`

Nhưng vẫn còn một vấn đề rất lớn.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

- `__set_name__()`
- Stateful Descriptor
- Descriptor Reuse
- Descriptor Storage
- `cached_property`
- Lazy Loading
- Mini ORM bằng Descriptor
- Django Field hoạt động như thế nào

---

# 1. Vấn đề của Descriptor ở buổi trước

Ta có:

```text-x-trilium-auto
class PositiveNumber:

    def __set__(self, instance, value):

        if value <= 0:
            raise ValueError

        instance.__dict__["price"] = value

    def __get__(self, instance, owner):

        return instance.__dict__["price"]
```

Sử dụng:

```text-x-trilium-auto
class Product:

    price = PositiveNumber()
```

Hoạt động.

---

Nhưng...

Nếu thêm:

```text-x-trilium-auto
class Product:

    price = PositiveNumber()

    quantity = PositiveNumber()
```

Thì sao?

---

Bạn sẽ phải sửa Descriptor thành:

```text-x-trilium-auto
instance.__dict__["quantity"]
```

hoặc

```text-x-trilium-auto
instance.__dict__["price"]
```

Descriptor không biết:

> Nó đang quản lý thuộc tính nào.

Đây là lý do Python bổ sung:

# `__set_name__()`

---

# 2. `__set_name__()`

Descriptor có thể định nghĩa:

```text-x-trilium-auto
def __set_name__(

    self,

    owner,

    name

):
```

Python sẽ tự gọi khi class được tạo.

---

# 3. Ví dụ đầu tiên

```text-x-trilium-auto
class Field:

    def __set_name__(

        self,

        owner,

        name
    ):

        print(owner)

        print(name)
```

---

```text-x-trilium-auto
class Person:

    name = Field()

    age = Field()
```

Kết quả

```text-x-trilium-auto
<class Person>

name

<class Person>

age
```

Descriptor biết:

- Owner
- Tên attribute

---

# 4. Lưu tên attribute

```text-x-trilium-auto
class Field:

    def __set_name__(

        self,

        owner,

        name
    ):

        self.name = name
```

Bây giờ

Descriptor nhớ:

```text-x-trilium-auto
price
```

hay

```text-x-trilium-auto
quantity
```

---

# 5. Descriptor tổng quát

```text-x-trilium-auto
class Positive:

    def __set_name__(

        self,

        owner,

        name
    ):

        self.name = name
```

---

```text-x-trilium-auto
    def __set__(

        self,

        instance,

        value
    ):

        if value <= 0:

            raise ValueError

        instance.__dict__[self.name] = value
```

---

```text-x-trilium-auto
    def __get__(

        self,

        instance,

        owner
    ):

        return instance.__dict__[self.name]
```

---

Sử dụng

```text-x-trilium-auto
class Product:

    price = Positive()

    quantity = Positive()
```

Không cần viết riêng cho từng field.

---

# 6. Đây chính là Descriptor Reuse

Một Descriptor

↓

Dùng cho:

- price
- quantity
- stock
- views
- likes

Tái sử dụng rất cao.

---

# 7. Stateful Descriptor

Descriptor cũng là object.

Nó có thể có state.

Ví dụ

```text-x-trilium-auto
class Range:

    def __init__(

        self,

        minimum,

        maximum
    ):

        self.minimum = minimum

        self.maximum = maximum
```

---

```text-x-trilium-auto
    def __set__(

        self,

        instance,

        value
    ):

        if not self.minimum <= value <= self.maximum:

            raise ValueError

        instance.__dict__[self.name] = value
```

---

Sử dụng

```text-x-trilium-auto
class Student:

    score = Range(0,100)
```

---

Hoặc

```text-x-trilium-auto
class Employee:

    age = Range(18,65)
```

Cùng Descriptor

↓

Khác cấu hình.

---

# 8. String Descriptor

```text-x-trilium-auto
class StringField:

    def __init__(

        self,

        max_length
    ):

        self.max_length = max_length
```

---

```text-x-trilium-auto
    def __set__(

        self,

        instance,

        value
    ):

        if len(value)>self.max_length:

            raise ValueError

        instance.__dict__[self.name]=value
```

---

Sử dụng

```text-x-trilium-auto
class Book:

    title = StringField(200)

    author = StringField(100)
```

---

# 9. Descriptor và Validation

Thay vì

```text-x-trilium-auto
if len(title)>200:
```

ở khắp nơi

↓

Validation nằm trong Descriptor.

Đây là nguyên lý:

> Encapsulation

---

# 10. Lazy Loading

Ví dụ

```text-x-trilium-auto
class Lazy:

    def __get__(

        self,

        instance,

        owner
    ):

        print("Load data...")

        return 123
```

---

```text-x-trilium-auto
class Test:

    value = Lazy()
```

Chỉ khi

```text-x-trilium-auto
obj.value
```

↓

Mới load.

Đây gọi là:

Lazy Loading.

---

# 11. cached_property

Python có:

```text-x-trilium-auto
from functools import cached_property
```

Ví dụ

```text-x-trilium-auto
class Book:

    @cached_property

    def chapters(self):

        print("Loading...")

        return load()
```

Lần đầu

```text-x-trilium-auto
book.chapters
```

↓

Load.

---

Lần sau

↓

Không load nữa.

Đây là Descriptor.

---

# 12. Tự viết cached_property

Ý tưởng

```text-x-trilium-auto
class Cached:

    def __init__(self,func):

        self.func=func
```

---

```text-x-trilium-auto
    def __get__(

        self,

        instance,

        owner
    ):

        if self.func.__name__ not in instance.__dict__:

            instance.__dict__[self.func.__name__]=self.func(instance)

        return instance.__dict__[self.func.__name__]
```

---

Sử dụng

```text-x-trilium-auto
class Demo:

    @Cached

    def data(self):

        print("Load")

        return [1,2,3]
```

---

Lần đầu

↓

```text-x-trilium-auto
Load
```

---

Lần hai

↓

Không in nữa.

---

# 13. Mini ORM

Giả sử

```text-x-trilium-auto
class IntegerField:

    ...
```

```text-x-trilium-auto
class StringField:

    ...
```

Model

```text-x-trilium-auto
class Book:

    id = IntegerField()

    title = StringField()
```

Có giống:

Django?

Có.

---

# 14. Django ORM

```text-x-trilium-auto
class Book(Model):

    title=models.CharField(...)
```

`CharField`

↓

Descriptor.

---

# 15. SQLAlchemy

```text-x-trilium-auto
class Book:

    title=Column(String)
```

Column

↓

Descriptor.

---

# 16. Pydantic

```text-x-trilium-auto
class User(BaseModel):

    age:int
```

Có validation.

Ý tưởng rất giống:

Descriptor.

(Mặc dù Pydantic còn sử dụng metaclass và nhiều kỹ thuật khác.)

---

# 17. Descriptor và Logging

```text-x-trilium-auto
class Logged:

    def __set__(

        self,

        instance,

        value
    ):

        print("SET",value)

        instance.__dict__[self.name]=value
```

Mỗi lần

```text-x-trilium-auto
user.name="ABC"
```

↓

Log.

Không cần sửa class.

---

# 18. Descriptor và Security

Ví dụ

```text-x-trilium-auto
class Password:
```

---

```text-x-trilium-auto
def __set__(...):

    hash_password()
```

Mọi lần gán

↓

Hash.

Không ai quên.

---

# 19. Áp dụng vào dự án crawler

Ta có

```text-x-trilium-auto
class UrlField:

    ...
```

```text-x-trilium-auto
class ChapterCount:

    ...
```

```text-x-trilium-auto
class StatusField:

    ...
```

Model

```text-x-trilium-auto
class Novel:

    title = StringField(200)

    url = UrlField()

    chapter_count = Positive()

    status = StatusField()
```

Validation

↓

Tự động.

---

# 20. Xây dựng Mini Model

```text-x-trilium-auto
class Model:

    def to_dict(self):

        return self.__dict__
```

---

```text-x-trilium-auto
book=Book()

book.title="Python"

print(book.to_dict())
```

↓

```text-x-trilium-auto
{
 "title":"Python"
}
```

Bắt đầu giống ORM.

---

# 21. Descriptor không lưu dữ liệu ở đâu?

Đây là câu hỏi rất quan trọng.

Nhiều người nghĩ:

```text-x-trilium-auto
Descriptor

↓

Lưu value
```

Sai.

Descriptor thường lưu:

```text-x-trilium-auto
Metadata
```

Ví dụ

```text-x-trilium-auto
max_length

minimum

maximum

validator
```

Còn dữ liệu của từng object được lưu trong:

```text-x-trilium-auto
instance.__dict__
```

Nếu Descriptor tự lưu giá trị trong chính nó, tất cả các instance sẽ dùng chung một giá trị — đây thường là lỗi của người mới học.

---

# 22. Sơ đồ hoạt động

```text-x-trilium-auto
               Product

        price = Positive()

                │

                ▼

          Descriptor Object

                │

        __set_name__()

                │

       biết tên field = "price"

                │

      __set__()

                │

instance.__dict__["price"]=100
```

---

# 23. Sai lầm phổ biến

## Sai

Lưu value trong Descriptor.

↓

Mọi object dùng chung.

---

## Sai

Không dùng `__set_name__()`.

↓

Descriptor không tái sử dụng.

---

## Sai

Validation trong Model.

↓

Lặp code.

Nên chuyển sang Descriptor.

---

# 24. Kiến trúc ORM

```text-x-trilium-auto
                Model

                  │

      ┌───────────┼────────────┐

      ▼           ▼            ▼

 IntegerField StringField FloatField

      │

      ▼

 Descriptor
```

Đây là cách Django ORM và nhiều ORM khác hoạt động ở mức khái niệm.

---

# Tổng kết Buổi 16

```text-x-trilium-auto
                  Descriptor

                      │

        ┌─────────────┼──────────────┐

        ▼             ▼              ▼

   __set_name__   Validation     Lazy Loading

        │

        ▼

 Reusable Field Objects

        │

        ▼

 ORM / Framework
```

---

# Điều quan trọng nhất cần nhớ

`__set_name__()` giúp Descriptor biết:

- mình đang quản lý thuộc tính nào;
- thuộc về lớp nào.

Nhờ đó, bạn có thể viết **một Descriptor duy nhất** để quản lý hàng chục thuộc tính khác nhau.

Đây là nền tảng của:

- Django ORM
- SQLAlchemy
- `cached_property`
- Validation framework
- Field system

---

# Bài tập thực hành

## Bài 1

Viết `PositiveField` sử dụng `__set_name__()`.

Yêu cầu:

- Dùng được cho nhiều thuộc tính.
- Không hard-code tên `"price"` hay `"quantity"`.

---

## Bài 2

Viết `EmailField`:

- Chỉ chấp nhận chuỗi có ký tự `@`.
- Dùng:

```text-x-trilium-auto
class User:
    email = EmailField()
```

---

## Bài 3

Tự cài đặt một `CachedProperty` đơn giản.

Kiểm tra:

- Lần đầu truy cập: tính toán và lưu kết quả.
- Các lần sau: trả về giá trị đã cache.

Thử xóa khóa tương ứng trong `instance.__dict__` rồi truy cập lại để thấy giá trị được tính lại.

---

## Bài 4 (Áp dụng dự án crawler)

Xây dựng một mini framework Model:

- `Field` (Descriptor cơ sở).
- `StringField`.
- `IntegerField`.
- `UrlField`.
- `DateTimeField`.

Sau đó tạo:

```text-x-trilium-auto
class Novel:
    id = IntegerField()
    title = StringField(max_length=255)
    url = UrlField()
    created_at = DateTimeField()
```

Mục tiêu:

- Tất cả validation nằm trong các `Field`.
- `Novel` chỉ khai báo các trường dữ liệu, không chứa mã kiểm tra.
- Thiết kế đủ linh hoạt để sau này có thể mở rộng thành một mini ORM.

---

# Chuẩn bị cho Buổi 17

Buổi tiếp theo sẽ bước sang một chủ đề cực kỳ quan trọng trong việc xây dựng framework Python:

# Metaclass (Siêu lớp)

Chúng ta sẽ tìm hiểu:

- Class được tạo ra như thế nào.
- `type` thực chất là gì.
- Metaclass hoạt động ra sao.
- Cơ chế tạo class trong Python.
- Vì sao Django ORM, SQLAlchemy, Enum, Dataclass, Pydantic đều sử dụng Metaclass hoặc các cơ chế tương tự.

Đây là chủ đề được xem là "đỉnh cao" của OOP trong Python và sẽ giúp bạn hiểu cách các framework lớn tự động tạo hành vi cho các lớp mà bạn chỉ cần khai báo vài dòng mã.