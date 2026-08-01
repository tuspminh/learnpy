# Python OOP Master – Buổi 8

# Property nâng cao – Descriptor, `@deleter`, Validation và Cơ chế hoạt động

> Đây là buổi học cực kỳ quan trọng. Sau buổi này, bạn sẽ hiểu rằng **`@property` không phải là một cú pháp đặc biệt**, mà thực chất là một **Descriptor**. Hiểu Descriptor sẽ giúp bạn đọc được source code của Django ORM, SQLAlchemy, Pydantic, attrs, dataclasses và nhiều framework Python khác.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu đầy đủ `property()`.
* Hiểu `@property`, `@setter`, `@deleter`.
* Hiểu Descriptor là gì.
* Hiểu Data Descriptor và Non-data Descriptor.
* Hiểu thứ tự Python lookup attribute.
* Biết viết Descriptor đơn giản.
* Hiểu vì sao Django ORM hoạt động.

---

# 1. Ôn tập Property

Buổi trước chúng ta đã học

```python
class Student:
    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value
```

Khi gọi

```python
student.age
```

Python thực chất gọi

```python
student.age.__get__()
```

Khi ghi

```python
student.age = 18
```

Python gọi

```python
student.age.__set__()
```

Nhưng ai có các method này?

Đó là **Descriptor**.

---

# 2. property() đầy đủ

Thực chất

```python
@property
```

chỉ là cách viết ngắn của

```python
age = property(fget, fset, fdel, doc)
```

Trong đó

```text
fget
```

là getter

```text
fset
```

là setter

```text
fdel
```

là deleter

```text
doc
```

là docstring.

---

# Ví dụ

```python
class Student:
    def __init__(self):
        self._age = 18

    def get_age(self):
        return self._age

    def set_age(self, value):
        self._age = value

    def del_age(self):
        print("Deleting age")
        del self._age

    age = property(get_age, set_age, del_age, "Student age")
```

---

# 3. @deleter

Python hỗ trợ

```python
@property
```

```python
@age.setter
```

và

```python
@age.deleter
```

Ví dụ

```python
class Student:
    def __init__(self):
        self._age = 18

    @property
    def age(self):
        return self._age

    @age.deleter
    def age(self):
        print("Delete age")
        del self._age
```

Sử dụng

```python
student = Student()

del student.age
```

Kết quả

```text
Delete age
```

---

# 4. Descriptor là gì?

Descriptor là object có ít nhất một trong các method

```python
__get__()

__set__()

__delete__()
```

Python sẽ tự động gọi các method này khi truy cập attribute.

---

# 5. Descriptor đầu tiên

```python
class AgeDescriptor:
    def __get__(self, instance, owner):
        print("GET")
        return 18
```

Sử dụng

```python
class Student:
    age = AgeDescriptor()


student = Student()

print(student.age)
```

Kết quả

```text
GET
18
```

Không hề có

```python
@property
```

---

# 6. **get**()

```python
def __get__(
    self,
    instance,
    owner
)
```

Ý nghĩa

```text
instance

↓

Object hiện tại
```

```text
owner

↓

Class
```

Ví dụ

```python
class Age:
    def __get__(self, instance, owner):
        print(instance)
        print(owner)
        return 100
```

---

# 7. **set**()

```python
class Age:
    def __get__(self, instance, owner):
        return instance._age

    def __set__(self, instance, value):

        if value < 0:
            raise ValueError

        instance._age = value
```

Sử dụng

```python
class Student:
    age = Age()

    def __init__(self):
        self._age = 18
```

```python
student = Student()

student.age = 30

print(student.age)
```

---

# 8. **delete**()

```python
class Age:
    def __delete__(self, instance):
        print("Delete")
        del instance._age
```

Khi

```python
del student.age
```

Python gọi

```python
__delete__()
```

---

# 9. Property thực chất là Descriptor

Có thể hình dung

```text
@property

↓

Descriptor

↓

__get__

↓

__set__

↓

__delete__
```

Cho nên

```python
student.age
```

không phải đọc trực tiếp attribute.

---

# 10. Data Descriptor

Nếu Descriptor có

```python
__set__
```

hoặc

```python
__delete__
```

thì gọi là

```text
Data Descriptor
```

Ví dụ

```python
class Age:

    def __get__(...):
        ...

    def __set__(...):
        ...
```

---

# 11. Non-data Descriptor

Nếu chỉ có

```python
__get__
```

thì gọi là

```text
Non-data Descriptor
```

Ví dụ

```python
class Age:

    def __get__(...):
        ...
```

---

# 12. Thứ tự Lookup

Python tìm attribute theo thứ tự

```text
Data Descriptor

↓

Object Namespace

↓

Non-data Descriptor

↓

Class Attribute

↓

Base Class
```

Đây là một trong những quy tắc quan trọng nhất của OOP trong Python.

---

# 13. Minh họa

```python
class Demo:
    value = AgeDescriptor()


obj = Demo()
```

Khi

```python
obj.value
```

Python

```text
↓

Descriptor

↓

__get__()
```

Không đọc

```python
obj.__dict__
```

nếu là Data Descriptor.

---

# 14. Validation bằng Descriptor

Ví dụ

```python
class PositiveNumber:
    def __get__(self, instance, owner):
        return instance._value

    def __set__(self, instance, value):

        if value <= 0:
            raise ValueError("Must be positive.")

        instance._value = value
```

Sử dụng

```python
class Product:
    price = PositiveNumber()

    def __init__(self, price):
        self.price = price
```

```python
product = Product(100)

print(product.price)

product.price = -1
```

Kết quả

```text
ValueError
```

---

# 15. Descriptor dùng lại được

Một Property

```python
@property
```

chỉ dùng cho một attribute.

Descriptor

```python
PositiveNumber
```

có thể dùng cho rất nhiều class.

Ví dụ

```python
class Product:
    price = PositiveNumber()
```

```python
class Employee:
    salary = PositiveNumber()
```

```python
class Loan:
    amount = PositiveNumber()
```

Đây là một ưu điểm lớn của Descriptor.

---

# 16. Ví dụ hoàn chỉnh

```python
class Positive:
    def __set_name__(self, owner, name):
        self.storage_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("Value must be >= 0")
        setattr(instance, self.storage_name, value)


class Employee:
    salary = Positive()
    bonus = Positive()

    def __init__(self, salary, bonus):
        self.salary = salary
        self.bonus = bonus

    @property
    def total_income(self):
        return self.salary + self.bonus


employee = Employee(1500, 300)

print(employee.salary)
print(employee.bonus)
print(employee.total_income)

employee.salary = 2000

print(employee.total_income)
```

Kết quả

```text
1500
300
1800
2300
```

**Giải thích:**

* `__set_name__` được Python gọi khi tạo class để descriptor biết tên thuộc tính (`salary`, `bonus`).
* `salary` và `bonus` đều dùng chung descriptor `Positive`.
* Giá trị thực được lưu trong `_salary` và `_bonus` của từng object.

---

# 17. Descriptor trong các Framework

Rất nhiều thư viện nổi tiếng sử dụng Descriptor.

## Django ORM

```python
class Book(Model):
    title = CharField(max_length=200)
```

`CharField` là một descriptor quản lý việc đọc/ghi dữ liệu của thuộc tính `title`.

---

## SQLAlchemy

```python
class User(Base):
    name = Column(String)
```

`Column` hoạt động thông qua descriptor để kiểm soát truy cập thuộc tính.

---

## Pydantic

```python
class User(BaseModel):
    age: int
```

Khi gán giá trị, Pydantic thực hiện kiểm tra kiểu và xác thực dữ liệu bằng các cơ chế tương tự descriptor và metaclass.

---

# Best Practices

✅ Dùng `@property` khi logic chỉ áp dụng cho một thuộc tính của một class.

✅ Dùng **Descriptor** khi muốn tái sử dụng cùng một logic (validation, logging, chuyển đổi dữ liệu...) cho nhiều thuộc tính hoặc nhiều class.

✅ Luôn xử lý trường hợp:

```python
instance is None
```

trong `__get__`, vì khi truy cập qua class (`Employee.salary`), `instance` sẽ là `None`.

---

# Những lỗi người mới thường gặp

### Lỗi 1: Không xử lý `instance is None`

Sai:

```python
def __get__(self, instance, owner):
    return instance._value
```

Khi gọi:

```python
Employee.salary
```

sẽ lỗi vì `instance` là `None`.

---

### Lỗi 2: Lưu dữ liệu trong descriptor

Sai:

```python
class Positive:
    def __init__(self):
        self.value = 0
```

Descriptor được chia sẻ giữa mọi object của class, nên nếu lưu dữ liệu trực tiếp trong descriptor thì tất cả object sẽ dùng chung một giá trị.

Đúng: lưu dữ liệu trong `instance`.

---

### Lỗi 3: Không dùng `__set_name__`

Nếu tự ghép tên thuộc tính bằng tay:

```python
instance._value
```

descriptor sẽ khó tái sử dụng.

`__set_name__` giúp descriptor biết chính xác tên thuộc tính mà nó quản lý.

---

# Bài tập

## Bài 1

Viết class `PositiveNumber` dưới dạng descriptor.

Áp dụng cho:

```python
class Product:
    price = PositiveNumber()
```

Không cho phép giá trị âm.

---

## Bài 2

Viết class `NonEmptyString` descriptor.

Áp dụng cho:

```python
class User:
    username = NonEmptyString()
```

Điều kiện:

* Không được là chuỗi rỗng.
* Tự loại bỏ khoảng trắng đầu và cuối bằng `strip()` trước khi lưu.

---

## Bài 3

Viết class `Rectangle`

* `width`
* `height`

Dùng cùng một descriptor `PositiveNumber`.

Thêm property:

* `area`

---

## Bài 4

Tạo property `full_name` trong class `Person`:

* Getter trả về `"first_name last_name"`.
* Setter nhận một chuỗi `"Tên Họ"` và tự tách thành `first_name`, `last_name`.
* Thêm `@full_name.deleter` để xóa cả hai thuộc tính.

---

## Bài 5 (Nâng cao)

Viết descriptor `RangeNumber(min_value, max_value)`.

Ví dụ:

```python
class Student:
    score = RangeNumber(0, 100)
```

Yêu cầu:

* Chỉ cho phép điểm trong khoảng từ 0 đến 100.
* Tái sử dụng được cho nhiều class khác nhau.
* Sử dụng `__set_name__` để tự động xác định tên thuộc tính lưu trữ.

---

# Tóm tắt buổi học

* `@property` thực chất được xây dựng trên **Descriptor Protocol**.
* Descriptor là object cài đặt một hoặc nhiều phương thức `__get__`, `__set__`, `__delete__`.
* Có hai loại descriptor:

  * **Data Descriptor**: có `__set__` hoặc `__delete__`.
  * **Non-data Descriptor**: chỉ có `__get__`.
* Thứ tự tra cứu thuộc tính của Python ưu tiên **Data Descriptor** trước `object.__dict__`.
* Descriptor là nền tảng của rất nhiều framework Python hiện đại như Django ORM, SQLAlchemy và nhiều thư viện khác.

> **Buổi 9** chúng ta sẽ bắt đầu **Inheritance (Kế thừa)**: tìm hiểu cách Python kế thừa class, cơ chế tra cứu phương thức (**Method Resolution Order – MRO**), `super()`, ghi đè phương thức (overriding) và cách thiết kế hệ thống class dễ mở rộng. Đây là nền tảng cho đa hình và nhiều design pattern sau này.
