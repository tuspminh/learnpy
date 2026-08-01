# Python OOP Master – Buổi 4

# Instance Attribute & Class Attribute (Chuyên sâu)

> Đây là một trong những bài học **quan trọng nhất của OOP Python**. Rất nhiều bug trong các project thực tế (Django, Flask, FastAPI, SQLAlchemy, PySide6...) đều xuất phát từ việc **không hiểu rõ sự khác nhau giữa Instance Attribute và Class Attribute**.

Sau buổi này, bạn sẽ hiểu:

* Python lưu attribute ở đâu.
* Khi nào dùng Class Attribute.
* Khi nào dùng Instance Attribute.
* Attribute Lookup Chain hoạt động như thế nào.
* Attribute Shadowing là gì.
* Tại sao mutable Class Attribute rất nguy hiểm.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Instance Attribute.
* Hiểu Class Attribute.
* Hiểu Namespace.
* Hiểu Attribute Lookup.
* Hiểu Shadowing.
* Hiểu Mutable Class Attribute.
* Biết thiết kế class đúng chuẩn.

---

# 1. Attribute là gì?

Attribute là **dữ liệu thuộc về object hoặc class**.

Ví dụ:

```python
class Student:
    school = "OpenAI Academy"

    def __init__(self, name):
        self.name = name
```

Ở đây có hai loại attribute:

```
school
```

là **Class Attribute**

Còn

```
name
```

là **Instance Attribute**

---

# 2. Hai nơi lưu Attribute

Python lưu attribute ở hai nơi.

```
          Student Class
     +---------------------+
     | school="OpenAI"     |
     +---------------------+
              ▲
              │
        lookup nếu không có
              │
     +----------------------+
     | name="Alice"         |
     | age=18               |
     +----------------------+
           Student Object
```

---

# 3. Instance Attribute

Ví dụ

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Tạo object

```python
s1 = Student("Alice")
s2 = Student("Bob")
```

Kiểm tra

```python
print(s1.__dict__)
print(s2.__dict__)
```

Kết quả

```python
{"name": "Alice"}
{"name": "Bob"}
```

Mỗi object có dữ liệu riêng.

---

# 4. Class Attribute

```python
class Student:
    school = "OpenAI Academy"

    def __init__(self, name):
        self.name = name
```

Tạo object

```python
s1 = Student("Alice")
s2 = Student("Bob")
```

```python
print(s1.school)
print(s2.school)
```

Kết quả

```
OpenAI Academy
OpenAI Academy
```

Hai object dùng chung một giá trị.

---

# 5. Namespace

Class có namespace riêng.

Object có namespace riêng.

```
Student Class

{
    school
}
```

Object

```
s1

{
    name
}
```

Object

```
s2

{
    name
}
```

---

# 6. Attribute Lookup

Khi viết

```python
print(s1.school)
```

Python làm gì?

Python tìm theo thứ tự

```
Object Namespace

↓

Class Namespace

↓

Base Class

↓

object
```

Đây gọi là

```
Attribute Lookup Chain
```

---

# Ví dụ

```python
class Student:
    school = "OpenAI"

    def __init__(self, name):
        self.name = name


s = Student("Alice")

print(s.school)
```

Quá trình

```
Object

↓

Không có school

↓

Class

↓

Có school

↓

Trả kết quả
```

---

# 7. Kiểm tra Namespace

```python
class Student:
    school = "OpenAI"

    def __init__(self, name):
        self.name = name


s = Student("Alice")

print(s.__dict__)

print(Student.__dict__)
```

Kết quả

```python
{"name": "Alice"}
```

Trong

```python
Student.__dict__
```

sẽ có

```
school
```

---

# 8. Shadowing (Che khuất)

Đây là phần cực kỳ quan trọng.

```python
class Student:
    school = "OpenAI"


s = Student()

print(s.school)
```

Kết quả

```
OpenAI
```

Bây giờ

```python
s.school = "MIT"
```

In tiếp

```python
print(s.school)
```

Kết quả

```
MIT
```

Có phải Class Attribute bị thay đổi không?

Không.

---

Kiểm tra

```python
print(Student.school)
```

Kết quả

```
OpenAI
```

---

Giải thích

Object đã tạo ra một Instance Attribute mới.

```
Student Class

school = OpenAI

↑

Object

school = MIT
```

Python luôn tìm object trước.

Cho nên

```
MIT
```

được trả về.

Đây gọi là

```
Attribute Shadowing
```

---

# 9. Minh họa Shadowing

Ban đầu

```
Class

school

↓

ABC School
```

Object

```
name=Alice
```

Sau khi

```python
s.school = "MIT"
```

Bộ nhớ

```
Class

school

↓

ABC School
```

Object

```
name

school

↓

MIT
```

---

# 10. Thay đổi Class Attribute

```python
class Student:
    school = "ABC"


Student.school = "OpenAI"

print(Student.school)
```

```
OpenAI
```

Các object chưa shadow sẽ nhìn thấy giá trị mới.

```python
s1 = Student()
s2 = Student()

print(s1.school)
print(s2.school)
```

```
OpenAI
OpenAI
```

---

# 11. Mutable Class Attribute (Lỗi kinh điển)

Ví dụ

```python
class Team:
    members = []
```

Tạo object

```python
t1 = Team()
t2 = Team()

t1.members.append("Alice")

print(t2.members)
```

Kết quả

```
['Alice']
```

Tại sao?

---

Bộ nhớ

```
Class

members

↓

[]
```

Object

```
t1
```

Object

```
t2
```

Cả hai cùng dùng chung list.

---

# 12. Thử tiếp

```python
t2.members.append("Bob")

print(t1.members)
```

Kết quả

```
['Alice', 'Bob']
```

Đây là lỗi rất nhiều người gặp.

---

# 13. Cách đúng

```python
class Team:
    def __init__(self):
        self.members = []
```

Bây giờ

```
t1

↓

[]
```

```
t2

↓

[]
```

Hai list khác nhau.

---

# 14. Khi nào dùng Class Attribute?

Nên dùng cho dữ liệu dùng chung.

Ví dụ

```python
class Config:
    APP_NAME = "Library"

    VERSION = "1.0"

    MAX_BOOK = 100
```

Hoặc

```python
class Student:
    school = "OpenAI Academy"
```

Hoặc

```python
class Math:
    PI = 3.1415926
```

---

# 15. Khi nào dùng Instance Attribute?

Dữ liệu riêng.

Ví dụ

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

Mỗi object khác nhau.

---

# 16. Ví dụ thực tế

```python
class User:
    website = "https://example.com"

    def __init__(self, username):
        self.username = username


u1 = User("alice")
u2 = User("bob")

print(u1.website)
print(u2.website)

print(u1.username)
print(u2.username)
```

Kết quả

```
https://example.com
https://example.com

alice
bob
```

---

# 17. Ví dụ hoàn chỉnh

```python
class Employee:
    company = "OpenAI"

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def display(self):
        print(f"Company : {self.company}")
        print(f"Name    : {self.name}")
        print(f"Salary  : {self.salary}")
        print("-" * 30)


e1 = Employee("Alice", 1000)
e2 = Employee("Bob", 2000)

e2.company = "Microsoft"

e1.display()
e2.display()

print("Object Namespace")
print(e1.__dict__)
print(e2.__dict__)

print()

print("Class Namespace")
print(Employee.__dict__["company"])
```

Kết quả

```
Company : OpenAI
Name    : Alice
Salary  : 1000
------------------------------

Company : Microsoft
Name    : Bob
Salary  : 2000
------------------------------

Object Namespace
{'name': 'Alice', 'salary': 1000}

{'name': 'Bob',
 'salary': 2000,
 'company': 'Microsoft'}

Class Namespace
OpenAI
```

Lưu ý:

* `e1.company` lấy từ **Class Attribute**.
* `e2.company` là **Instance Attribute** mới được tạo, che khuất (`shadow`) giá trị của class.
* `Employee.company` vẫn giữ nguyên là `"OpenAI"`.

---

# Best Practices

✅ Dùng **Instance Attribute** cho dữ liệu thay đổi theo từng object.

```python
self.name
self.age
self.salary
```

✅ Dùng **Class Attribute** cho dữ liệu dùng chung.

```python
VERSION
PI
MAX_CONNECTION
```

❌ Không dùng mutable object làm Class Attribute nếu object có thể thay đổi.

Sai:

```python
class Team:
    members = []
```

Đúng:

```python
class Team:
    def __init__(self):
        self.members = []
```

---

# Những lỗi người mới thường gặp

### Lỗi 1: Nhầm lẫn giữa Class Attribute và Instance Attribute

```python
class User:
    role = "Guest"


u = User()
u.role = "Admin"
```

`User.role` vẫn là `"Guest"`.

---

### Lỗi 2: Mutable Class Attribute

```python
class Cart:
    items = []
```

Tất cả object dùng chung một danh sách.

---

### Lỗi 3: Nghĩ rằng `object.attribute = ...` sẽ thay đổi Class Attribute

Thực tế, nếu attribute chưa tồn tại trong object, Python sẽ tạo **Instance Attribute mới**, không sửa Class Attribute.

---

# Bài tập

## Bài 1

Viết class `Book`

Có:

```text
library_name
```

là Class Attribute.

Có:

```text
title
price
```

là Instance Attribute.

Tạo 3 object và in `__dict__` của từng object cùng với `Book.__dict__`.

---

## Bài 2

Tạo class `Company`

Có:

```text
country = "Vietnam"
```

Tạo 2 object.

Cho object thứ hai đổi:

```python
country = "Japan"
```

Dự đoán và kiểm tra:

* `Company.country`
* `obj1.country`
* `obj2.country`

Giải thích vì sao.

---

## Bài 3

Tạo class `Classroom`

**Phiên bản sai:**

```python
students = []
```

Thêm học sinh vào hai object khác nhau và quan sát kết quả.

Sau đó sửa bằng cách chuyển `students` thành Instance Attribute trong `__init__`.

---

## Bài 4

Viết class `Product`

* Class Attribute:

  * `currency = "VND"`
* Instance Attribute:

  * `name`
  * `price`

Viết phương thức `display()` để in đầy đủ thông tin và thử thay đổi `currency` ở:

* Cấp class (`Product.currency = "USD"`).
* Một object cụ thể (`p1.currency = "EUR"`).

Quan sát sự khác biệt.

---

## Bài 5 (Nâng cao)

Cho đoạn mã:

```python
class A:
    x = 10


a1 = A()
a2 = A()

a1.x = 20
A.x = 30

print(a1.x)
print(a2.x)
print(A.x)

print(a1.__dict__)
print(a2.__dict__)
```

1. Dự đoán kết quả trước khi chạy.
2. Vẽ sơ đồ bộ nhớ (memory diagram).
3. Giải thích từng bước Python tìm thuộc tính `x`.

---

# Tóm tắt buổi học

* **Instance Attribute** thuộc về từng object và được lưu trong `object.__dict__`.
* **Class Attribute** thuộc về class và được lưu trong `Class.__dict__`.
* Python tìm thuộc tính theo **Attribute Lookup Chain**: `Object → Class → Base Class → object`.
* Gán `obj.attribute = value` có thể tạo **Instance Attribute** mới và **che khuất (shadow)** Class Attribute.
* Tránh sử dụng **mutable Class Attribute** (`list`, `dict`, `set`) cho dữ liệu riêng của từng object.

> **Buổi 5** chúng ta sẽ học **Method trong Python OOP**, bao gồm cách hoạt động của `self`, cơ chế **bound method**, cách Python gọi phương thức phía sau hậu trường, và sự khác biệt giữa **Instance Method**, **Function** và **Method**. Đây là nền tảng để hiểu sâu `@staticmethod` và `@classmethod` ở các buổi sau.
