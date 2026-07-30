# Buổi 4: Instance Variable, Class Variable, Shadowing và Mutable Class Attribute

Đây là buổi cực kỳ quan trọng trong OOP Python vì nó giải thích rất nhiều lỗi mà lập trình viên mới thường gặp:

- Vì sao thay đổi thuộc tính của object này không ảnh hưởng object khác?
- Vì sao đôi khi sửa một biến lại làm thay đổi tất cả object?
- Vì sao dùng list trong class có thể gây lỗi?
- Khi nào nên dùng class variable?
- Khi nào phải dùng instance variable?

---

# 1. Hai loại thuộc tính trong Python OOP

Trong Python, thuộc tính của object thường chia thành:

## 1. Instance Variable

Thuộc tính thuộc về **từng object riêng biệt**.

Ví dụ:

```text-x-trilium-auto
class Student:

    def __init__(self, name):
        self.name = name


s1 = Student("An")
s2 = Student("Bình")
```

Bộ nhớ:

```text-x-trilium-auto
Student Class
      |
      |
      +----------------+
                       |
                       |
                 s1 Instance
                 {
                    name: "An"
                 }


                 s2 Instance
                 {
                    name: "Bình"
                 }
```

Mỗi object có dữ liệu riêng.

---

## 2. Class Variable

Thuộc tính thuộc về **class**, được chia sẻ bởi tất cả instance.

Ví dụ:

```text-x-trilium-auto
class Student:

    school = "THPT ABC"


s1 = Student()
s2 = Student()
```

Bộ nhớ:

```text-x-trilium-auto
Student Class

{
    school: "THPT ABC"
}


       |
       |
       +-------- s1
       |
       +-------- s2
```

Cả hai object đều truy cập được.

---

# 2. Tạo Instance Variable

Cách phổ biến nhất:

```text-x-trilium-auto
class Person:

    def __init__(self, name, age):
        self.name = name
        self.age = age
```

Khi:

```text-x-trilium-auto
p = Person("Nam", 20)
```

Python tạo:

```text-x-trilium-auto
p.__dict__
```

Kết quả:

```text-x-trilium-auto
{
    "name": "Nam",
    "age": 20
}
```

---

# 3. Class Variable được lưu ở đâu?

Ví dụ:

```text-x-trilium-auto
class Person:

    country = "Vietnam"
```

Kiểm tra:

```text-x-trilium-auto
print(Person.__dict__)
```

Kết quả:

```text-x-trilium-auto
{
    "country": "Vietnam"
}
```

Nó nằm trong namespace của class.

---

# 4. Attribute Lookup

Nhắc lại kiến thức buổi 2.

Khi viết:

```text-x-trilium-auto
person.country
```

Python tìm:

```text-x-trilium-auto
person.__dict__

       |
       |
       Không có

       ↓

Person.__dict__

       |
       |
       Có

       ↓

Vietnam
```

---

Ví dụ:

```text-x-trilium-auto
class Person:

    country = "Vietnam"


p = Person()

print(p.country)
```

Kết quả:

```text-x-trilium-auto
Vietnam
```

Mặc dù:

```text-x-trilium-auto
p.__dict__
```

là:

```text-x-trilium-auto
{}
```

---

# 5. Shadowing (Che khuất thuộc tính)

Bây giờ:

```text-x-trilium-auto
p.country = "USA"
```

Điều gì xảy ra?

Python tạo một biến mới trong instance:

```text-x-trilium-auto
p.__dict__
```

kết quả:

```text-x-trilium-auto
{
    "country": "USA"
}
```

Bây giờ:

```text-x-trilium-auto
print(p.country)
```

kết quả:

```text-x-trilium-auto
USA
```

Nhưng:

```text-x-trilium-auto
print(Person.country)
```

vẫn:

```text-x-trilium-auto
Vietnam
```

---

Sơ đồ:

Trước:

```text-x-trilium-auto
Person

country
 |
Vietnam


p

{}
```

Sau:

```text-x-trilium-auto
Person

country
 |
Vietnam



p

country
 |
USA
```

Instance đã che class variable.

---

# 6. Ví dụ thực tế

Giả sử làm hệ thống quản lý sinh viên:

```text-x-trilium-auto
class Student:

    school = "ABC School"

    def __init__(self, name):
        self.name = name
```

Tạo:

```text-x-trilium-auto
a = Student("An")
b = Student("Bình")
```

Ta có:

```text-x-trilium-auto
Student

school
 |
ABC School



a

name
 |
An



b

name
 |
Bình
```

---

Truy cập:

```text-x-trilium-auto
print(a.school)
```

Python:

```text-x-trilium-auto
a
 |
không có school

↓

Student

↓

ABC School
```

---

# 7. Thay đổi Class Variable

Ví dụ:

```text-x-trilium-auto
class Student:

    school = "ABC"


a = Student()
b = Student()

Student.school = "XYZ"
```

Bây giờ:

```text-x-trilium-auto
print(a.school)
print(b.school)
```

Kết quả:

```text-x-trilium-auto
XYZ
XYZ
```

Vì cả hai đều đọc từ class.

---

# 8. Nhưng nếu một object tự gán?

```text-x-trilium-auto
a.school = "DEF"
```

Lúc này:

```text-x-trilium-auto
Student

school
 |
XYZ



a

school
 |
DEF



b

(không có)
```

Kết quả:

```text-x-trilium-auto
print(a.school)
```

```text-x-trilium-auto
DEF
```

```text-x-trilium-auto
print(b.school)
```

```text-x-trilium-auto
XYZ
```

---

# 9. Lỗi nguy hiểm: Mutable Class Variable

Đây là lỗi rất phổ biến.

Ví dụ:

```text-x-trilium-auto
class Team:

    members = []


a = Team()
b = Team()

a.members.append("An")

print(b.members)
```

Kết quả:

```text-x-trilium-auto
['An']
```

Tại sao?

Vì list nằm ở class.

Sơ đồ:

```text-x-trilium-auto
Team

members
 |
[]
 |
 +---- a
 |
 +---- b
```

Cả hai cùng dùng một list.

---

# 10. Đây là lỗi cực kỳ nguy hiểm

Ví dụ:

```text-x-trilium-auto
class ShoppingCart:

    items = []


cart1 = ShoppingCart()
cart2 = ShoppingCart()

cart1.items.append("Laptop")

print(cart2.items)
```

Bạn mong:

```text-x-trilium-auto
[]
```

Nhưng nhận:

```text-x-trilium-auto
['Laptop']
```

Vì:

```text-x-trilium-auto
cart1.items
       |
       |
       v
    Team.items
       |
       v
      []
```

---

# 11. Cách sửa đúng

Đưa list vào instance:

```text-x-trilium-auto
class ShoppingCart:

    def __init__(self):
        self.items = []
```

Bây giờ:

```text-x-trilium-auto
cart1 = ShoppingCart()
cart2 = ShoppingCart()

cart1.items.append("Laptop")

print(cart2.items)
```

Kết quả:

```text-x-trilium-auto
[]
```

Bộ nhớ:

```text-x-trilium-auto
cart1

items
 |
["Laptop"]



cart2

items
 |
[]
```

---

# 12. Khi nào dùng Class Variable?

Dùng khi dữ liệu:

- Chung cho mọi object.
- Không thay đổi thường xuyên.
- Mang tính cấu hình.

Ví dụ:

```text-x-trilium-auto
class Database:

    host = "localhost"
    port = 3306
```

---

Ví dụ trong game:

```text-x-trilium-auto
class Player:

    max_health = 100
```

Mọi player đều có:

```text-x-trilium-auto
100 HP
```

---

# 13. Khi nào dùng Instance Variable?

Khi dữ liệu:

- Mỗi object khác nhau.
- Có trạng thái riêng.

Ví dụ:

```text-x-trilium-auto
class Player:

    def __init__(self, name):
        self.name = name
        self.health = 100
```

Mỗi player:

```text-x-trilium-auto
Player A

name
health



Player B

name
health
```

---

# 14. Class Variable kết hợp với Constructor

Ví dụ:

```text-x-trilium-auto
class User:

    count = 0

    def __init__(self, name):

        self.name = name

        User.count += 1
```

Dùng:

```text-x-trilium-auto
a = User("An")
b = User("Bình")

print(User.count)
```

Kết quả:

```text-x-trilium-auto
2
```

Đây là cách thường dùng để đếm số object.

---

# 15. Sai lầm phổ biến

## Sai:

```text-x-trilium-auto
class Config:

    options = {}
```

Nếu:

```text-x-trilium-auto
a = Config()
b = Config()

a.options["debug"] = True
```

Thì:

```text-x-trilium-auto
b.options
```

cũng có:

```text-x-trilium-auto
{
 "debug": True
}
```

---

## Đúng:

```text-x-trilium-auto
class Config:

    def __init__(self):
        self.options = {}
```

---

# 16. Bài tập thực hành

## Bài 1

Tạo class:

```text-x-trilium-auto
class Employee:
```

Có:

Class variable:

```text-x-trilium-auto
company = "ABC"
```

Instance variable:

```text-x-trilium-auto
name salary
```

Tạo 3 nhân viên.

In:

- `Employee.__dict__`
- từng object `__dict__`

---

# Bài 2

Dự đoán kết quả:

```text-x-trilium-auto
class A:
    x = 10


a = A()
b = A()

a.x = 20

print(a.x)
print(b.x)
print(A.x)
```

Giải thích vì sao.

---

# Bài 3

Tìm lỗi:

```text-x-trilium-auto
class Database:

    connections = []


db1 = Database()
db2 = Database()

db1.connections.append("MySQL")
```

Sửa lại để mỗi database có danh sách riêng.

---

# Bài 4 (Thực tế)

Thiết kế class:

```text-x-trilium-auto
Book
```

Yêu cầu:

Class variable:

```text-x-trilium-auto
publisher
total_books
```

Instance variable:

```text-x-trilium-auto
title
author
price
```

Mỗi khi tạo sách tăng `total_books`.

---

# Kiến thức cần nhớ sau buổi 4

| Thành phần | Nơi lưu |
| --- | --- |
| Instance variable | `object.__dict__` |
| Class variable | `Class.__dict__` |
| Method | Class namespace |
| `self.x = ...` | tạo instance variable |
| `Class.x = ...` | thay đổi class variable |
| Mutable class variable | dễ gây bug |

---

## Chuẩn bị cho Buổi 5

Buổi tiếp theo chúng ta sẽ đi sâu vào:

# Method trong Python OOP

- Function trong class thực chất là gì?
- Vì sao phải có `self`?
- Bound method hoạt động thế nào?
- Python tự truyền `self` ra sao?
- Vì sao `obj.method()` khác `Class.method(obj)`?
- Method object được tạo khi nào?
- Descriptor liên quan gì đến method?

Đây là nền tảng để hiểu sâu `@classmethod`, `@staticmethod`, decorator và framework như Django/PySide6.