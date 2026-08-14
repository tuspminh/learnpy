# OOP Deep Dive — Buổi 22

# `property` thực chất hoạt động như thế nào?

Ở Buổi 21, chúng ta đã học **Descriptor Protocol**:

```python
__get__()
__set__()
__delete__()
__set_name__()
```

Hôm nay ta sẽ giải mã một thứ bạn đã dùng rất nhiều:

```python
@property
```

Mục tiêu không phải chỉ biết dùng `@property`, mà phải hiểu:

```text
@property
    ↓
property object
    ↓
Descriptor
    ↓
__get__()
__set__()
__delete__()
    ↓
attribute access
```

Đây là cầu nối trực tiếp sang **Buổi 23: Method cũng là Descriptor**.

---

# 1. `property` là gì?

Ví dụ quen thuộc:

```python
class User:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
```

Sử dụng:

```python
user = User("Alice")

print(user.name)
```

Ta viết:

```python
user.name
```

chứ không phải:

```python
user.name()
```

---

# 2. `@property` làm gì?

Dòng:

```python
@property
def name(self):
    return self._name
```

không đơn giản có nghĩa:

> "Biến method thành attribute."

Chính xác hơn:

> Python tạo ra một **property object** và gán property object đó vào class.

Có thể hình dung:

```python
class User:

    def name(self):
        return self._name
```

Sau đó decorator:

```python
@property
```

tương đương ý tưởng:

```python
name = property(name)
```

---

# 3. `property` là một object

Ta kiểm tra:

```python
class User:

    @property
    def name(self):
        return "Alice"
```

Sau đó:

```python
print(User.__dict__["name"])
```

Bạn sẽ nhận được một object kiểu:

```text
<property object ...>
```

Vậy:

```python
User.__dict__["name"]
```

không phải function nữa.

Nó là:

```text
property object
```

---

# 4. Và `property` là Descriptor

Đây là điểm quan trọng nhất của bài.

```python
property
```

triển khai Descriptor Protocol.

Về ý tưởng, nó có:

```python
class property:

    def __get__(...):
        ...

    def __set__(...):
        ...

    def __delete__(...):
        ...
```

Vì vậy:

```python
user.name
```

có thể dẫn tới:

```python
property.__get__(...)
```

---

# 5. Phân tích từng bước

Code:

```python
class User:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name
```

Khi class được tạo, về mặt ý tưởng:

```text
User.__dict__

_name?       không

name
 ↓
property object
```

---

# 6. Khi gọi `user.name`

Bạn viết:

```python
user.name
```

Python thực hiện attribute lookup.

Nó tìm:

```python
User.__dict__["name"]
```

và phát hiện:

```text
property object
```

Property là Data Descriptor.

Vì vậy Python gọi:

```python
property.__get__(
    user,
    User
)
```

Property sau đó gọi getter function:

```python
name(self)
```

---

# 7. Luồng đầy đủ

```text
user.name
   │
   ▼
object.__getattribute__()
   │
   ▼
User.__dict__["name"]
   │
   ▼
property object
   │
   ▼
property.__get__(user, User)
   │
   ▼
getter function
   │
   ▼
return user._name
```

Đây là cơ chế thật sự đằng sau:

```python
user.name
```

---

# 8. Tự xây dựng Property đơn giản

Bây giờ ta tự viết.

```python
class MyProperty:

    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return self.getter(instance)
```

---

# 9. Sử dụng

```python
class User:

    def __init__(self, name):
        self._name = name

    name = MyProperty(
        lambda self: self._name
    )
```

Sau đó:

```python
user = User("Alice")

print(user.name)
```

Kết quả:

```text
Alice
```

Ta vừa tạo một phiên bản rất đơn giản của:

```python
@property
```

---

# 10. Không dùng lambda cho dễ hiểu

Viết đầy đủ:

```python
class User:

    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    name = MyProperty(get_name)
```

Bây giờ:

```python
user.name
```

sẽ gọi:

```text
MyProperty.__get__()
    ↓
get_name()
    ↓
self._name
```

---

# 11. Tại sao `instance is None`?

Trong:

```python
User.name
```

không có instance.

Descriptor nhận:

```python
instance = None
```

Vì vậy:

```python
if instance is None:
    return self
```

cho phép:

```python
User.name
```

trả về chính `property object`.

---

# 12. Property có setter

Ta thường viết:

```python
class User:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
```

Sử dụng:

```python
user.name = "Bob"
```

---

# 13. Điều gì xảy ra?

Python thấy:

```python
user.name = "Bob"
```

và `name` là Data Descriptor.

Do đó gọi:

```python
property.__set__(
    user,
    "Bob"
)
```

Property gọi setter:

```python
name(user, "Bob")
```

---

# 14. Luồng setter

```text
user.name = "Bob"
        │
        ▼
object.__setattr__()
        │
        ▼
property object
        │
        ▼
property.__set__()
        │
        ▼
setter function
        │
        ▼
user._name = "Bob"
```

---

# 15. Tự viết setter

Ta mở rộng `MyProperty`:

```python
class MyProperty:

    def __init__(
        self,
        getter=None,
        setter=None
    ):
        self.getter = getter
        self.setter = setter

    def __get__(self, instance, owner):

        if instance is None:
            return self

        if self.getter is None:
            raise AttributeError(
                "unreadable attribute"
            )

        return self.getter(instance)

    def __set__(self, instance, value):

        if self.setter is None:
            raise AttributeError(
                "can't set attribute"
            )

        self.setter(instance, value)
```

---

# 16. Tự tạo property

```python
class User:

    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    name = MyProperty(
        get_name,
        set_name
    )
```

Bây giờ:

```python
user.name
```

↓

```text
get_name()
```

Còn:

```python
user.name = "Bob"
```

↓

```text
set_name()
```

---

# 17. Đây chính là bản chất của property

Có thể hình dung:

```python
@property
def name(self):
    return self._name
```

tạo ra:

```text
property(
    fget=name
)
```

Còn:

```python
@name.setter
def name(self, value):
    self._name = value
```

tạo ra property mới có:

```text
fget
fset
```

---

# 18. Một điều rất quan trọng

Khi viết:

```python
@name.setter
def name(self, value):
    ...
```

Python không sửa function `name` cũ.

Nó tạo ra **một property object mới**.

Có thể hình dung:

```text
property 1
   │
   └── fget

        ↓ setter

property 2
   │
   ├── fget
   └── fset
```

---

# 19. Vì sao phải dùng cùng tên `name`?

Bạn viết:

```python
@property
def name(self):
    ...
```

sau đó:

```python
@name.setter
def name(self, value):
    ...
```

Tên `name` được dùng lại để gán property mới vào class namespace.

---

# 20. Read-only property

Nếu chỉ có:

```python
@property
def name(self):
    return self._name
```

thì:

```python
user.name = "Bob"
```

sẽ gây:

```text
AttributeError
```

Bởi vì property không có setter.

Đây là cách Python tạo **read-only attribute**.

---

# 21. Write-only property?

Có thể tạo property chỉ có setter:

```python
class User:

    def set_password(self, value):
        ...

    password = property(
        fset=set_password
    )
```

Khi:

```python
user.password = "secret"
```

có thể hoạt động.

Nhưng:

```python
user.password
```

sẽ không đọc được.

Trong thiết kế thông thường, kiểu này ít gặp hơn read-only property.

---

# 22. Deleter

Bạn có thể viết:

```python
class User:

    @property
    def name(self):
        return self._name

    @name.deleter
    def name(self):
        del self._name
```

Khi:

```python
del user.name
```

Python gọi:

```python
property.__delete__(
    user
)
```

Sau đó property gọi deleter.

---

# 23. Full Property

Một property có thể có:

```text
fget
fset
fdel
doc
```

Tương ứng:

```python
property(
    fget=...,
    fset=...,
    fdel=...,
    doc=...
)
```

---

# 24. Dùng trực tiếp `property()`

Không dùng decorator cũng được.

```python
class User:

    def __init__(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    name = property(
        get_name,
        set_name
    )
```

Hoàn toàn tương đương về ý tưởng với decorator.

---

# 25. `@property` chỉ là syntax sugar

Điểm này cần nhớ:

```python
@property
def name(self):
    ...
```

về cơ bản tương đương:

```python
def name(self):
    ...

name = property(name)
```

Decorator giúp code đẹp hơn.

---

# 26. Property là Data Descriptor

Đây là lý do property có thể ngăn việc ghi đè từ `instance.__dict__`.

Ví dụ:

```python
class User:

    @property
    def name(self):
        return "Alice"
```

Bạn thử:

```python
user.__dict__["name"] = "Bob"
```

nhưng:

```python
print(user.name)
```

vẫn:

```text
Alice
```

Tại sao?

Bởi vì:

```text
property
```

là **Data Descriptor**.

Nó có `__set__()`.

---

# 27. Đây là điểm liên hệ trực tiếp với Buổi 21

Ta đã học:

```text
Data Descriptor
    >
instance.__dict__
```

`property` chính là một ví dụ cực kỳ quan trọng của quy tắc này.

---

# 28. Property + Validation

Đây là cách sử dụng rất phổ biến.

```python
class User:

    def __init__(self, age):
        self.age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):

        if value < 0:
            raise ValueError(
                "age must be >= 0"
            )

        self._age = value
```

---

# 29. Tại sao trong `__init__` dùng `self.age`?

```python
self.age = age
```

chứ không:

```python
self._age = age
```

Vì ta muốn validation chạy ngay.

Luồng:

```text
__init__
   │
   ▼
self.age = age
   │
   ▼
property.__set__()
   │
   ▼
validation
   │
   ▼
self._age
```

---

# 30. Property + Computed Attribute

Ví dụ:

```python
class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height
```

Sử dụng:

```python
rect.area
```

Không cần:

```python
rect.area()
```

---

# 31. Vì sao `area` nên là property?

Bởi vì:

```python
area
```

mang ý nghĩa **dữ liệu**.

Còn:

```python
calculate_area()
```

mang ý nghĩa **hành động**.

Đây là vấn đề thiết kế API.

---

# 32. Property không nhất thiết phải lưu dữ liệu

Ví dụ:

```python
class User:

    @property
    def full_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )
```

`full_name` không cần nằm trong:

```python
__dict__
```

Nó được tính khi truy cập.

---

# 33. Property + Lazy Computation

Ví dụ:

```python
class Report:

    @property
    def summary(self):

        print("Computing...")

        return expensive_calculation()
```

Mỗi lần:

```python
report.summary
```

sẽ tính lại.

Nếu muốn cache thì cần kỹ thuật khác.

---

# 34. Property + Cache

Có thể kết hợp:

```python
class Report:

    @property
    def summary(self):

        if "_summary" not in self.__dict__:
            self._summary = expensive_calculation()

        return self._summary
```

Luồng:

```text
Lần 1
summary
 ↓
calculate
 ↓
cache

Lần 2
summary
 ↓
cache
```

Đây chính là nền tảng của **lazy cached property**.

Python cũng có:

```python
functools.cached_property
```

cho trường hợp phổ biến này.

---

# 35. Property không phải magic

Đây là mindset quan trọng.

Khi bạn thấy:

```python
user.name
```

đừng nghĩ:

> "Python somehow biết phải gọi getter."

Hãy nghĩ:

```text
user.name
   ↓
attribute lookup
   ↓
property descriptor
   ↓
property.__get__()
   ↓
getter
```

---

# 36. So sánh 3 cách

### Cách 1 — Public attribute

```python
user.name
```

Dữ liệu trực tiếp.

---

### Cách 2 — Method

```python
user.get_name()
```

Hành động rõ ràng.

---

### Cách 3 — Property

```python
user.name
```

nhưng phía sau có logic.

Property cho phép bạn **giữ API giống attribute trong khi thay đổi implementation phía dưới**.

Đây là giá trị lớn nhất của `property`.

---

# 37. Ví dụ rất quan trọng về API Evolution

Ban đầu:

```python
class User:

    def __init__(self, name):
        self.name = name
```

Code bên ngoài:

```python
user.name
```

Sau này bạn muốn validation.

Nếu vẫn giữ:

```python
user.name
```

thì có thể chuyển thành:

```python
class User:

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        validate(value)
        self._name = value
```

Code phía client **không cần thay đổi**.

Đây là một lý do property cực kỳ hữu ích trong API design.

---

# 38. Property và Encapsulation

Property giúp kiểm soát:

```text
Read
Write
Delete
```

Ví dụ:

```python
@property
def balance(self):
    return self._balance

@balance.setter
def balance(self, value):
    if value < 0:
        raise ValueError(...)
    self._balance = value
```

Object có thể đảm bảo invariant:

```text
balance >= 0
```

---

# 39. Property và Descriptor

Ta có thể xây dựng hierarchy tư duy:

```text
Attribute Access
       │
       ▼
Descriptor Protocol
       │
       ▼
property
       │
       ├── getter
       ├── setter
       └── deleter
```

Vì vậy học `property` sau Descriptor là hoàn toàn hợp lý.

---

# 40. Property có thể có docstring

Ví dụ:

```python
class User:

    @property
    def name(self):
        """Tên người dùng."""
        return self._name
```

Sau đó:

```python
print(User.name.__doc__)
```

có thể lấy documentation của property.

---

# 41. Một ví dụ hoàn chỉnh

```python
class Product:

    def __init__(self, name, price):

        self.name = name
        self.price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):

        if not isinstance(value, (int, float)):
            raise TypeError(
                "price must be a number"
            )

        if value < 0:
            raise ValueError(
                "price must be >= 0"
            )

        self._price = value

    @property
    def display_price(self):

        return f"${self.price:.2f}"
```

---

Sử dụng:

```python
product = Product(
    "Book",
    100
)

print(product.price)
print(product.display_price)
```

---

Nếu:

```python
product.price = -10
```

↓

```text
ValueError
```

Nếu:

```python
product.price = "100"
```

↓

```text
TypeError
```

---

# 42. Bài tập 1 — Tự viết `MyProperty`

Viết class:

```python
class MyProperty:
    ...
```

hỗ trợ:

```python
class User:

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    name = MyProperty(
        get_name,
        set_name
    )
```

Phải hoạt động:

```python
user.name
```

và:

```python
user.name = "Alice"
```

---

# 43. Bài tập 2 — Validation

Viết:

```python
class Product:

    price = ...
```

Yêu cầu:

```python
product.price = 100
```

OK.

```python
product.price = -1
```

→ `ValueError`

```python
product.price = "100"
```

→ `TypeError`

---

# 44. Bài tập 3 — Computed Property

Viết:

```python
class Rectangle:

    @property
    def area(self):
        ...
```

và:

```python
@property
def perimeter(self):
    ...
```

Sử dụng:

```python
rect.area
rect.perimeter
```

Không được dùng:

```python
rect.area()
```

---

# 45. Bài tập 4 — Lazy Property

Viết:

```python
class Data:

    @property
    def result(self):
        ...
```

Yêu cầu:

```text
Lần đầu:
calculate

Lần sau:
dùng cache
```

Không được tính toán lại.

---

# 46. Bài tập Deep Dive

Hãy giải thích chính xác từng bước của:

```python
class User:

    def __init__(self):
        self._name = "Alice"

    @property
    def name(self):
        return self._name
```

khi chạy:

```python
user = User()

print(user.name)
```

Bạn cần mô tả:

```text
1. Class creation
2. function name được tạo
3. @property chạy
4. property object được tạo
5. property được đặt vào User.__dict__
6. User() tạo instance
7. user.name bắt đầu attribute lookup
8. property.__get__()
9. getter chạy
10. self._name được trả về
```

Nếu bạn hiểu được chuỗi này thì bạn đã thực sự hiểu `property`, thay vì chỉ biết cú pháp.

---

# 47. Kiến thức cốt lõi của Buổi 22

Hãy ghi nhớ:

```python
@property
def name(self):
    ...
```

về bản chất:

```python
def name(self):
    ...

name = property(name)
```

Và:

```text
property
   ↓
Descriptor
   ↓
__get__
__set__
__delete__
```

Do đó:

```python
user.name
```

không nhất thiết đọc trực tiếp từ:

```python
user.__dict__
```

mà có thể đi qua:

```text
property.__get__()
```

---

# Roadmap tiếp theo — Buổi 23

Theo **đúng roadmap gốc của bạn**, buổi sau là:

# **Buổi 23 — Method cũng là Descriptor**

Đây là bài rất quan trọng vì chúng ta sẽ giải thích tận gốc câu hỏi:

> Tại sao khi viết:

```python
user.say_hello()
```

Python tự động truyền:

```python
self = user
```

trong khi function ban đầu chỉ là:

```python
def say_hello(self):
    ...
```

Chúng ta sẽ mổ xẻ:

```python
User.__dict__["say_hello"]
```

→ `function object`

→ `function.__get__()`

→ `bound method`

→ `self`

→ tại sao:

```python
user.say_hello
```

khác:

```python
User.say_hello
```

và từ đó nối toàn bộ kiến thức:

```text
Buổi 5
Function Object
      ↓
Buổi 21
Descriptor
      ↓
Buổi 22
property
      ↓
Buổi 23
Method = Descriptor
```

Đây sẽ là một trong những buổi quan trọng nhất của toàn bộ phần Descriptor.
