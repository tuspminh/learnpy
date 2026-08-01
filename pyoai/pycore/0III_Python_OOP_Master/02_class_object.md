# Python OOP Master – Buổi 2

# Class và Object (Chuyên sâu)

> Đây là một trong những bài quan trọng nhất của toàn bộ khóa học OOP. Sau buổi này, bạn sẽ hiểu chính xác **Class**, **Object**, **Instance**, **Attribute**, **Method**, **Namespace**, **Identity**, **Reference**, và cách Python tạo một object trong bộ nhớ.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu chính xác Class là gì.
* Hiểu Object được tạo như thế nào.
* Phân biệt Class và Instance.
* Hiểu namespace của class và object.
* Hiểu object nằm ở đâu trong RAM.
* Hiểu biến trong Python chỉ là **tham chiếu (Reference)**.
* Biết cách tạo nhiều object đúng chuẩn.

---

# 1. Class là gì?

Class là **bản thiết kế (Blueprint)**.

Ví dụ ngoài đời:

```
Bản thiết kế ngôi nhà
        │
        ▼
 Nhà A
 Nhà B
 Nhà C
```

Một bản thiết kế có thể tạo ra rất nhiều ngôi nhà.

Trong Python cũng vậy.

```
Person
   │
   ├── Alice
   ├── Bob
   └── Charlie
```

Class chỉ mô tả.

Object mới là thứ tồn tại.

---

# Ví dụ đầu tiên

```python
class Person:
    pass
```

Class trên chưa có gì.

Nhưng ta có thể tạo object.

```python
class Person:
    pass


p1 = Person()
p2 = Person()

print(type(p1))
print(type(p2))
```

Kết quả

```
<class '__main__.Person'>
<class '__main__.Person'>
```

---

# 2. Object là gì?

Object là một thực thể được tạo từ class.

Ví dụ

```
Class

Person

↓

Object

Alice

Bob

Charlie
```

Mỗi object có dữ liệu riêng.

Ví dụ:

```
Person

↓

Alice
age=18

↓

Bob
age=22
```

---

# 3. Một Class có thể tạo vô số Object

```python
class Dog:
    pass


dogs = []

for i in range(5):
    dogs.append(Dog())

for dog in dogs:
    print(dog)
```

Ví dụ kết quả

```
<__main__.Dog object at 0x21A5D9B0>
<__main__.Dog object at 0x21A5DA30>
<__main__.Dog object at 0x21A5DB10>
...
```

---

# 4. Vì sao địa chỉ khác nhau?

Mỗi object được lưu ở một vùng nhớ khác nhau.

```
RAM

+--------------------+
| Dog object #1      |
+--------------------+

+--------------------+
| Dog object #2      |
+--------------------+

+--------------------+
| Dog object #3      |
+--------------------+
```

Python tạo object trong Heap Memory.

---

# 5. id() là gì?

Python cung cấp hàm:

```python
id(obj)
```

Trả về Identity của object.

Ví dụ

```python
class Cat:
    pass


c1 = Cat()
c2 = Cat()

print(id(c1))
print(id(c2))
```

Ví dụ

```
2458382042880
2458382043312
```

Hai object khác nhau nên id khác nhau.

---

# 6. identity khác equality

Ví dụ

```python
a = [1, 2]
b = [1, 2]

print(a == b)
print(a is b)
```

Kết quả

```
True
False
```

Giải thích

```
==

So sánh giá trị

is

So sánh object
```

---

Ví dụ

```
a ─────► Object A

b ─────► Object B
```

Giá trị giống nhau

Nhưng object khác nhau.

---

# 7. Reference (Tham chiếu)

Đây là phần rất nhiều người mới học hiểu sai.

Ví dụ

```python
x = Person()
```

Nhiều người nghĩ

```
x chứa object
```

Thực tế

```
x

↓

Object
```

Biến chỉ giữ địa chỉ.

Hay nói đúng hơn

```
Reference
```

---

Ví dụ

```python
class Dog:
    pass


d1 = Dog()
d2 = d1

print(d1 is d2)
```

Kết quả

```
True
```

Sơ đồ

```
d1 ─────┐
         │
         ▼
      Dog Object
         ▲
         │
d2 ──────┘
```

Không có object mới được tạo.

---

# 8. Thử thay đổi object

```python
class Dog:
    pass


d1 = Dog()
d2 = d1

d1.name = "Lucky"

print(d2.name)
```

Kết quả

```
Lucky
```

Vì cả hai cùng trỏ đến một object.

---

# 9. Tạo object mới

```python
class Dog:
    pass


d1 = Dog()
d2 = Dog()

d1.name = "Lucky"
d2.name = "Tom"

print(d1.name)
print(d2.name)
```

```
Lucky
Tom
```

---

# 10. Namespace của Object

Mỗi object có một vùng dữ liệu riêng.

Ví dụ

```python
class Student:
    pass


s1 = Student()
s2 = Student()

s1.name = "Alice"
s2.name = "Bob"

print(s1.__dict__)
print(s2.__dict__)
```

Kết quả

```
{'name': 'Alice'}

{'name': 'Bob'}
```

---

`__dict__`

Là dictionary chứa attribute.

```
Student Object

{
   "name":"Alice"
}
```

---

# 11. Namespace của Class

```python
class Student:
    school = "ABC School"
```

Xem namespace

```python
print(Student.__dict__)
```

Sẽ thấy rất nhiều thông tin.

Ví dụ

```
{
'__module__',
'__dict__',
'__weakref__',
'school'
...
}
```

---

# 12. Object tìm attribute như thế nào?

Ví dụ

```python
class Student:
    school = "ABC"


s = Student()

print(s.school)
```

Object không có school.

Python sẽ tìm theo thứ tự:

```
Object Namespace

↓

Class Namespace

↓

Base Class

↓

object
```

Đây được gọi là **Attribute Lookup Chain**.

---

# 13. Minh họa

```
Student Class

school="ABC"

↑

Object s

name="Alice"
```

Khi gọi

```python
print(s.name)
```

Python tìm

```
Object

↓

name

Tìm thấy
```

Khi gọi

```python
print(s.school)
```

Python tìm

```
Object

↓

Không có

↓

Class

↓

Có
```

---

# 14. dir()

Có thể xem mọi attribute

```python
class Student:
    school = "ABC"


s = Student()

print(dir(s))
```

Ví dụ

```
[
'__class__',
'__dict__',
'__repr__',
...
'school'
]
```

---

# 15. type()

```python
class Student:
    pass


s = Student()

print(type(s))
```

```
<class '__main__.Student'>
```

---

# 16. isinstance()

```python
class Animal:
    pass


dog = Animal()

print(isinstance(dog, Animal))
```

```
True
```

---

# 17. Ví dụ hoàn chỉnh

```python
class Student:
    school = "ABC School"


s1 = Student()
s2 = Student()

s1.name = "Alice"
s1.age = 18

s2.name = "Bob"
s2.age = 20

print("== Student 1 ==")
print(s1.name)
print(s1.age)
print(s1.school)

print()

print("== Student 2 ==")
print(s2.name)
print(s2.age)
print(s2.school)

print()

print("Object namespace:")
print(s1.__dict__)
print(s2.__dict__)

print()

print("Class namespace:")
print(Student.__dict__.keys())
```

Kết quả (rút gọn)

```
== Student 1 ==
Alice
18
ABC School

== Student 2 ==
Bob
20
ABC School

Object namespace:
{'name': 'Alice', 'age': 18}
{'name': 'Bob', 'age': 20}

Class namespace:
dict_keys([
'__module__',
'school',
'__dict__',
'__weakref__',
'__doc__'
])
```

---

# Best Practices

* Không nên thêm thuộc tính động (`s.name = ...`) trong các dự án lớn; hãy khởi tạo chúng trong `__init__` (sẽ học ở buổi 3).
* Dùng `is` để so sánh danh tính đối tượng (ví dụ `x is None`), không dùng để so sánh giá trị thông thường.
* Hiểu rõ sự khác nhau giữa **biến**, **đối tượng** và **tham chiếu** để tránh lỗi khi làm việc với danh sách, từ điển và các object.

---

# Những lỗi người mới thường gặp

### 1. Nhầm `=` là sao chép object

```python
a = Dog()
b = a
```

`b` không phải bản sao của `a`, mà chỉ là một tham chiếu khác đến cùng object.

### 2. Nhầm `==` và `is`

```python
a = [1, 2]
b = [1, 2]

print(a == b)  # True
print(a is b)  # False
```

### 3. Cho rằng mọi thuộc tính đều thuộc object

Nếu một thuộc tính chỉ tồn tại ở class, object vẫn có thể truy cập nhờ **Attribute Lookup Chain**, nhưng thuộc tính đó không nằm trong `object.__dict__`.

---

# Bài tập

### Bài 1

Tạo class `Book`.

Sinh ra 5 object và in:

* `id()`
* `type()`

---

### Bài 2

Tạo hai object `Car`.

Thêm thuộc tính:

```text
brand
color
year
```

In `__dict__` của từng object.

---

### Bài 3

Viết chương trình chứng minh:

```python
a = []
b = a
```

và

```python
a = []
b = []
```

khác nhau như thế nào bằng cách sử dụng `id()`, `is` và `==`.

---

### Bài 4

Tạo class `Employee` có class attribute:

```python
company = "OpenAI"
```

Tạo 3 object và chứng minh rằng:

* `company` nằm trong namespace của class.
* Không nằm trong namespace của từng object.
* Mọi object đều truy cập được `company`.

---

### Bài 5 (Nâng cao)

Tự xây dựng sơ đồ bộ nhớ (memory diagram) cho đoạn mã sau và dự đoán kết quả trước khi chạy:

```python
class Person:
    pass


p1 = Person()
p2 = Person()
p3 = p1

p1.name = "Alice"
p2.name = "Bob"

print(p1 is p2)
print(p1 is p3)
print(p3.name)
print(p1.__dict__)
print(p2.__dict__)
```

---

## Tóm tắt buổi học

* **Class** là bản thiết kế, **Object** là thực thể được tạo từ class.
* Mỗi object có **identity** riêng (`id()`), vùng nhớ riêng và namespace riêng (`__dict__`).
* Biến trong Python **không chứa object**, mà chứa **tham chiếu (reference)** đến object.
* Python tra cứu thuộc tính theo **Attribute Lookup Chain**: `Object → Class → Base Class → object`.
* Phân biệt rõ `==` (so sánh giá trị) và `is` (so sánh danh tính đối tượng).

> **Buổi 3** chúng ta sẽ học **Constructor (`__init__`)**, cơ chế khởi tạo object, vòng đời của object và cách thiết kế class đúng chuẩn thay vì thêm thuộc tính động sau khi tạo đối tượng.
