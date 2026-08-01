Tuyệt vời. Đây là phần quan trọng nhất của Python. Nếu nắm vững OOP, bạn sẽ có thể đọc và phát triển các framework lớn như Django, Flask, FastAPI, Celery, Scrapy, SQLAlchemy, PySide6, cũng như tự thiết kế framework riêng.

---

# Python OOP Master (2026 Edition)

## Mục tiêu

Sau khóa học này bạn sẽ:

* Hiểu OOP từ bản chất, không học thuộc lòng.
* Biết khi nào nên dùng class.
* Thiết kế được project lớn.
* Đọc được source code thư viện Python.
* Áp dụng SOLID.
* Áp dụng Design Pattern.
* Viết code clean và dễ mở rộng.

---

# Roadmap đầy đủ

## Phần I — Nền tảng OOP

**Buổi 1. OOP là gì? Vì sao cần OOP**

> Objects trong đời thực

**Buổi 2. Class và Object**

> Tạo class đầu tiên

**Buổi 3. Constructor (`__init__`)**

> Khởi tạo object

**Buổi 4. Thuộc tính (Attributes)**

* Instance Attribute
* Class Attribute

**Buổi 5. Method**

* Instance Method
* self

---

## Phần II — Đóng gói dữ liệu

**Buổi 6. Encapsulation**

* public
* protected
* private

**Buổi 7. Getter Setter**

**Buổi 8. Property**

@property

---

## Phần III — Kế thừa

**Buổi 9. Inheritance**

**Buổi 10. super()**

**Buổi 11. Overriding**

**Buổi 12. Multiple Inheritance**

**Buổi 13. Mixins**

---

## Phần IV — Đa hình

**Buổi 14. Polymorphism**

**Buổi 15. Duck Typing**

**Buổi 16. Abstract Base Class**

---

## Phần V — Magic Method

**Buổi 17. Magic Method cơ bản**

```
__str__
__repr__
```

**Buổi 18. Operator Overloading**

```
__add__
__sub__
__eq__
```

**Buổi 19. Container Magic**

```
__len__
__iter__
__getitem__
```

**Buổi 20. Callable Object**

```
__call__
```

---

## Phần VI — Static và Class Method

**Buổi 21. Static Method**

**Buổi 22. Class Method**

**Buổi 23. Factory Pattern**

---

## Phần VII — Thiết kế Class

**Buổi 24. Composition**

**Buổi 25. Aggregation**

**Buổi 26. Dependency Injection**

---

## Phần VIII — SOLID

**Buổi 27. Single Responsibility**

**Buổi 28. Open Closed**

**Buổi 29. Liskov**

**Buổi 30. Interface Segregation**

**Buổi 31. Dependency Inversion**

---

## Phần IX — Design Pattern

**Buổi 32. Singleton**

**Buổi 33. Factory**

**Buổi 34. Builder**

**Buổi 35. Strategy**

**Buổi 36. Observer**

**Buổi 37. Command**

**Buổi 38. Repository Pattern**

---

## Phần X — Project

**Buổi 39–40**

Project:

```
Library Management System
```

Sử dụng

* OOP
* SOLID
* Design Pattern
* Package
* Logging
* Exception
* Unit Test

---

Project thứ hai

```
Sales Management
```

Bao gồm

* Customer
* Product
* Invoice
* Inventory
* Report

---

# Phương pháp học

Mỗi buổi sẽ gồm 8 phần:

1. Lý thuyết
2. Minh họa trực quan
3. Ví dụ nhỏ
4. Ví dụ thực tế
5. Những lỗi người mới
6. Best Practice
7. Bài tập
8. Mini Project

---

# Buổi 1 — OOP là gì? Vì sao cần OOP?

## Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu bản chất của OOP.
* Biết vì sao lập trình hướng đối tượng ra đời.
* Phân biệt Procedural Programming và OOP.
* Biết khi nào nên sử dụng OOP.
* Hiểu 4 trụ cột của OOP ở mức khái quát.

---

# 1. Lập trình thủ tục (Procedural Programming)

Khi mới học Python, bạn thường viết chương trình như sau:

```python
name = "Alice"
age = 20


def introduce():
    print(f"My name is {name}")
    print(f"I'm {age} years old.")


introduce()
```

Chương trình nhỏ thì không có vấn đề.

Nhưng nếu quản lý nhiều người:

```python
name1 = "Alice"
age1 = 20

name2 = "Bob"
age2 = 25

name3 = "Charlie"
age3 = 18
```

Bạn sẽ phải tạo rất nhiều biến và hàm riêng lẻ.

---

# 2. Vấn đề của lập trình thủ tục

Giả sử quản lý 10.000 sinh viên.

Bạn sẽ có:

```
name1
name2
...
name10000

age1
age2
...
age10000
```

Các vấn đề:

* Khó quản lý dữ liệu.
* Dữ liệu và hành vi tách rời.
* Khó tái sử dụng.
* Khó mở rộng.
* Dễ phát sinh lỗi.

---

# 3. Ý tưởng của OOP

Trong đời thực, mọi thứ đều là **đối tượng (Object)**.

Ví dụ:

```
Con người

Tên
Tuổi
Chiều cao
Cân nặng

Có thể

Đi
Chạy
Ăn
Ngủ
```

OOP gom **dữ liệu** và **hành vi** vào cùng một thực thể.

---

# 4. Object là gì?

Ví dụ:

```
Xe ô tô

Thuộc tính

Màu
Hãng
Biển số

Hành vi

Chạy
Rẽ
Phanh
Đỗ
```

Trong OOP:

```
Object
=
Data
+
Behavior
```

---

# 5. Class là gì?

Class là **bản thiết kế (Blueprint)** dùng để tạo ra các Object có cùng cấu trúc và hành vi.

Ví dụ:

```
Class

Car
```

Từ class đó có thể tạo ra nhiều object:

```
Car

↓

Toyota

↓

Honda

↓

BMW
```

Hay:

```
Person

↓

Alice

↓

Bob

↓

Charlie
```

**Ví dụ minh họa:**

```python
class Person:
    pass


p1 = Person()
p2 = Person()

print(type(p1))
print(type(p2))
print(p1 is p2)
```

**Kết quả:**

```
<class '__main__.Person'>
<class '__main__.Person'>
False
```

`p1` và `p2` là hai đối tượng khác nhau được tạo từ cùng một class.

---

# 6. Vì sao cần OOP?

Giả sử xây dựng phần mềm quản lý trường học.

Nếu không dùng OOP:

```
student_name
student_age
student_score

teacher_name
teacher_age
teacher_salary

course_name
course_price
```

Khi chương trình lớn dần, số lượng biến và hàm sẽ tăng rất nhanh.

Với OOP:

```text
School
│
├── Student
├── Teacher
├── Course
├── Classroom
├── Subject
└── Grade
```

Mỗi loại đối tượng quản lý dữ liệu và hành vi của chính nó, giúp mã nguồn rõ ràng và dễ mở rộng.

---

# 7. Bốn trụ cột của OOP

Trong các buổi sau chúng ta sẽ học chi tiết từng phần. Trước mắt, hãy nắm ý nghĩa:

1. **Encapsulation (Đóng gói)**: Gom dữ liệu và các phương thức xử lý dữ liệu vào cùng một class, đồng thời kiểm soát việc truy cập.
2. **Inheritance (Kế thừa)**: Tạo class mới dựa trên class đã có để tái sử dụng và mở rộng chức năng.
3. **Polymorphism (Đa hình)**: Cùng một giao diện nhưng có thể có nhiều cách triển khai khác nhau.
4. **Abstraction (Trừu tượng)**: Chỉ cung cấp những gì cần thiết, che giấu chi tiết triển khai.

---

# 8. Ví dụ hoàn chỉnh

Giả sử quản lý nhân viên.

### Cách làm không dùng OOP

```python
employees = [
    {"name": "Alice", "salary": 1200},
    {"name": "Bob", "salary": 1500},
]


def increase_salary(employee, percent):
    employee["salary"] += employee["salary"] * percent / 100


for employee in employees:
    increase_salary(employee, 10)
    print(employee)
```

Nhược điểm:

* Dữ liệu dạng `dict`, dễ gõ sai khóa (`"salary"` thành `"salery"`).
* Không có kiểm soát kiểu dữ liệu.
* Khó mở rộng khi thêm hành vi mới.

### Cách làm với OOP

```python
class Employee:
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary

    def increase_salary(self, percent: float):
        self.salary += self.salary * percent / 100

    def display(self):
        print(f"Name: {self.name}")
        print(f"Salary: {self.salary:.2f}")


employees = [
    Employee("Alice", 1200),
    Employee("Bob", 1500),
]

for employee in employees:
    employee.increase_salary(10)
    employee.display()
```

**Ưu điểm:**

* Dữ liệu và hành vi được đóng gói trong `Employee`.
* Dễ bổ sung phương thức như `calculate_bonus()`, `promote()`, `transfer_department()`.
* Dễ kiểm thử và tái sử dụng.

---

# Best Practices

* Đặt tên class theo **PascalCase** (`Student`, `EmployeeManager`).
* Một class chỉ nên đại diện cho **một khái niệm**.
* Ưu tiên thiết kế các class có trách nhiệm rõ ràng.
* Chưa cần dùng OOP cho các script rất nhỏ, nhưng với ứng dụng vừa và lớn, OOP giúp mã nguồn dễ bảo trì hơn.

---

# Những lỗi người mới thường gặp

* Nhầm lẫn giữa **Class** và **Object**.
* Coi class như nơi chứa toàn bộ chương trình.
* Tạo quá nhiều class không cần thiết.
* Sử dụng biến toàn cục thay vì thuộc tính của object.
* Thiết kế class có quá nhiều trách nhiệm (sẽ học cách tránh với nguyên lý SOLID).

---

# Bài tập

1. Giải thích sự khác nhau giữa **Class** và **Object**.
2. Viết class `Dog` và tạo 3 object khác nhau.
3. Viết class `Book`, tạo 5 object và in ra kiểu dữ liệu của từng object bằng `type()`.
4. So sánh ưu, nhược điểm giữa cách quản lý dữ liệu bằng `dict` và bằng class.
5. Thiết kế (chưa cần code) các class cho hệ thống quản lý cửa hàng sách: hãy liệt kê ít nhất 6 class và mô tả ngắn gọn trách nhiệm của mỗi class.

---

## Tóm tắt buổi học

* OOP là phương pháp tổ chức chương trình xoay quanh **đối tượng**.
* **Class** là bản thiết kế, **Object** là thể hiện cụ thể của bản thiết kế đó.
* OOP giúp quản lý dữ liệu và hành vi tốt hơn, đặc biệt trong các dự án lớn.
* Bốn trụ cột của OOP là: **Encapsulation**, **Inheritance**, **Polymorphism** và **Abstraction**.

Ở **Buổi 2**, chúng ta sẽ đi sâu vào **Class và Object**, tìm hiểu cách định nghĩa thuộc tính, phương thức, tạo nhiều đối tượng, và khám phá cách Python lưu trữ object trong bộ nhớ.
