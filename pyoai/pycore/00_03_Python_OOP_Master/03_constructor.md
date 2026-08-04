# Python OOP Master – Buổi 3

# Constructor (`__init__`) – Khởi tạo Object chuyên sâu

> Đây là một trong những buổi quan trọng nhất của OOP. Sau buổi này, bạn sẽ hiểu **chính xác điều gì xảy ra khi tạo một object**, vai trò của `__new__`, `__init__`, `self`, và cách thiết kế constructor theo chuẩn của các thư viện Python chuyên nghiệp.

---

# Mục tiêu

Sau buổi học này, bạn sẽ:

* Hiểu Constructor là gì.
* Hiểu vòng đời của object khi gọi `Class()`.
* Phân biệt `__new__()` và `__init__()`.
* Hiểu bản chất của `self`.
* Biết cách thiết kế constructor linh hoạt.
* Biết khi nào nên và không nên đặt logic trong `__init__`.
* Áp dụng type hints và giá trị mặc định đúng cách.

---

# 1. Constructor là gì?

Trong OOP, **constructor** là phương thức được gọi ngay sau khi object được tạo, dùng để khởi tạo trạng thái ban đầu của object.

Trong Python, constructor thông thường là:

```python
__init__()
```

Ví dụ:

```python
class Student:
    def __init__(self):
        print("Student được khởi tạo")


s = Student()
```

Kết quả:

```text
Student được khởi tạo
```

---

# 2. Điều gì xảy ra khi gọi `Student()`?

Khi viết:

```python
s = Student()
```

Nhiều người nghĩ Python chỉ gọi `__init__()`.

Thực tế không phải vậy.

Python thực hiện theo trình tự:

```text
Student()

↓

__new__()

↓

Tạo object

↓

__init__()

↓

Trả object về biến s
```

Hay chi tiết hơn:

```text
            Student()

                │

                ▼

      __new__(Student)

                │

      Cấp phát vùng nhớ

                │

                ▼

        Object mới sinh ra

                │

                ▼

   __init__(self, ...)

                │

      Khởi tạo dữ liệu

                │

                ▼

     Trả object cho biến
```

> `__new__()` tạo object.
> `__init__()` chỉ khởi tạo object đã được tạo.

---

# 3. Constructor đầu tiên

```python
class Dog:
    def __init__(self):
        self.name = "Lucky"
        self.age = 2


dog = Dog()

print(dog.name)
print(dog.age)
```

Kết quả:

```text
Lucky
2
```

Không cần:

```python
dog.name = "Lucky"
dog.age = 2
```

như ở Buổi 2.

---

# 4. Constructor có tham số

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age


s1 = Student("Alice", 18)
s2 = Student("Bob", 20)

print(s1.name)
print(s2.name)
```

Kết quả:

```text
Alice
Bob
```

---

# 5. `self` là gì?

Đây là phần khiến người mới học dễ nhầm lẫn.

Ví dụ:

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Nhiều người nghĩ:

```text
self là từ khóa
```

❌ Sai.

`self` **không phải từ khóa**.

Bạn có thể viết:

```python
class Student:
    def __init__(this, name):
        this.name = name
```

Vẫn chạy.

Nhưng theo quy ước của Python (**PEP 8**), luôn dùng `self`.

---

# 6. Python truyền `self` như thế nào?

Khi bạn viết:

```python
s = Student("Alice")
```

Python thực chất gọi:

```python
Student.__init__(s, "Alice")
```

Tức là object vừa tạo sẽ được truyền vào tham số đầu tiên.

Minh họa:

```text
Student()

↓

Tạo object

↓

self = object vừa tạo

↓

__init__(self)
```

---

# 7. Gán thuộc tính bằng `self`

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Sơ đồ bộ nhớ:

```text
self

↓

Student Object

{
    "name": "Alice"
}
```

Nếu không dùng `self`:

```python
class Student:
    def __init__(self, name):
        name = name
```

thì chỉ là biến cục bộ trong hàm.

Sau khi `__init__` kết thúc:

```text
name

↓

Biến bị hủy
```

Object không có thuộc tính `name`.

---

# 8. Giá trị mặc định

```python
class Student:
    def __init__(self, name, age=18):
        self.name = name
        self.age = age


s1 = Student("Alice")
s2 = Student("Bob", 20)

print(s1.age)
print(s2.age)
```

Kết quả:

```text
18
20
```

---

# 9. Type Hints

Nên viết:

```python
class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
```

Thay vì:

```python
def __init__(self, name, age):
```

Ưu điểm:

* IDE hỗ trợ tốt hơn.
* Dễ đọc.
* Dễ bảo trì.
* Thuận tiện cho kiểm tra kiểu bằng các công cụ như `mypy`.

---

# 10. Constructor với nhiều tham số

```python
class Employee:
    def __init__(
        self,
        employee_id: int,
        name: str,
        department: str,
        salary: float,
        active: bool = True,
    ):
        self.employee_id = employee_id
        self.name = name
        self.department = department
        self.salary = salary
        self.active = active


employee = Employee(
    1,
    "Alice",
    "IT",
    1500,
)

print(employee.__dict__)
```

Kết quả:

```text
{
 'employee_id': 1,
 'name': 'Alice',
 'department': 'IT',
 'salary': 1500,
 'active': True
}
```

---

# 11. Keyword Arguments

Nên ưu tiên:

```python
employee = Employee(
    employee_id=1,
    name="Alice",
    department="IT",
    salary=1500,
)
```

Thay vì:

```python
Employee(
    1,
    "Alice",
    "IT",
    1500,
)
```

Vì:

* Dễ đọc.
* Ít nhầm vị trí tham số.
* Thuận tiện khi bổ sung tham số mới.

---

# 12. Constructor không nên làm gì?

Không nên:

```python
class Database:
    def __init__(self):
        self.connect_to_database()
        self.download_everything()
        self.process_all_data()
```

Nếu các thao tác này mất nhiều thời gian hoặc có thể thất bại, việc tạo object sẽ trở nên chậm và khó kiểm thử.

Nên tách riêng:

```python
class Database:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
```

---

# 13. Constructor gọi method khác

```python
class User:
    def __init__(self, name):
        self.name = name
        self.display()

    def display(self):
        print(f"Xin chào {self.name}")


user = User("Alice")
```

Điều này hợp lệ, nhưng cần cẩn thận nếu `display()` phụ thuộc vào những thuộc tính chưa được khởi tạo.

---

# 14. Constructor và Mutable Default Argument

Đây là một lỗi rất phổ biến.

❌ Sai:

```python
class Team:
    def __init__(self, members=[]):
        self.members = members
```

Vì danh sách mặc định được tạo **một lần** khi định nghĩa hàm và được dùng chung giữa các lần gọi.

Ví dụ:

```python
team1 = Team()
team2 = Team()

team1.members.append("Alice")

print(team2.members)
```

Kết quả:

```text
['Alice']
```

`team2` cũng bị ảnh hưởng.

---

## Cách đúng

```python
class Team:
    def __init__(self, members=None):
        if members is None:
            members = []

        self.members = members
```

Bây giờ:

```python
team1 = Team()
team2 = Team()

team1.members.append("Alice")

print(team1.members)
print(team2.members)
```

Kết quả:

```text
['Alice']
[]
```

Mỗi object có danh sách riêng.

---

# 15. Ví dụ hoàn chỉnh

```python
class Book:
    def __init__(
        self,
        title: str,
        author: str,
        price: float,
        quantity: int = 0,
    ):
        self.title = title
        self.author = author
        self.price = price
        self.quantity = quantity

    def display(self):
        print("=== Book ===")
        print(f"Title    : {self.title}")
        print(f"Author   : {self.author}")
        print(f"Price    : {self.price}")
        print(f"Quantity : {self.quantity}")


book1 = Book(
    title="Clean Code",
    author="Robert C. Martin",
    price=45.5,
    quantity=10,
)

book2 = Book(
    title="Python Cookbook",
    author="David Beazley",
    price=50,
)

book1.display()
print()
book2.display()
```

Kết quả:

```text
=== Book ===
Title    : Clean Code
Author   : Robert C. Martin
Price    : 45.5
Quantity : 10

=== Book ===
Title    : Python Cookbook
Author   : David Beazley
Price    : 50
Quantity : 0
```

---

# Best Practices

* Luôn khởi tạo đầy đủ các thuộc tính trong `__init__`.
* Dùng type hints cho mọi tham số.
* Ưu tiên keyword arguments khi tạo object có nhiều tham số.
* Không thực hiện tác vụ nặng (I/O, tải dữ liệu, kết nối mạng...) trong `__init__`.
* Tránh dùng mutable object (`[]`, `{}`, `set()`) làm giá trị mặc định cho tham số.

---

# Những lỗi người mới thường gặp

1. Quên dùng `self` khi gán thuộc tính.
2. Nghĩ `self` là từ khóa của Python.
3. Thêm thuộc tính ở nhiều nơi thay vì khởi tạo trong `__init__`.
4. Dùng danh sách hoặc từ điển làm giá trị mặc định của tham số.
5. Viết quá nhiều logic trong constructor khiến việc tạo object trở nên phức tạp.

---

# Bài tập

### Bài 1

Viết class `Car` với các thuộc tính:

* brand
* model
* year
* color

Khởi tạo bằng constructor và viết phương thức `display()`.

---

### Bài 2

Viết class `BankAccount`:

* account_number
* owner
* balance (mặc định bằng `0`)

Viết phương thức `display()`.

---

### Bài 3

Chứng minh lỗi của mutable default argument bằng một ví dụ với class `ShoppingCart`, sau đó sửa lại bằng cách dùng `None`.

---

### Bài 4

Viết class `Rectangle` nhận:

* width
* height

Viết thêm phương thức:

* `area()`
* `perimeter()`

Tạo 3 object với các kích thước khác nhau và in kết quả.

---

### Bài 5 (Nâng cao)

Viết class `Student`:

* student_id
* name
* scores (danh sách điểm, mặc định rỗng nhưng không dùng `[]` trực tiếp)

Thêm phương thức:

* `add_score(score)`
* `average_score()`

Kiểm tra rằng mỗi object có danh sách điểm độc lập.

---

# Tóm tắt buổi học

* `__init__()` là phương thức khởi tạo trạng thái ban đầu của object, không phải nơi tạo object.
* `__new__()` chịu trách nhiệm tạo object, sau đó `__init__()` khởi tạo dữ liệu cho object đó.
* `self` là tham chiếu đến chính object hiện tại và được Python truyền tự động.
* Luôn khởi tạo đầy đủ thuộc tính trong `__init__` để tránh trạng thái không nhất quán.
* Tránh `mutable default argument`; hãy dùng `None` và tạo đối tượng mới bên trong `__init__`.
* Thiết kế constructor gọn gàng, chỉ thực hiện việc khởi tạo, không chứa các thao tác nặng hoặc dễ thất bại.

> **Buổi 4** chúng ta sẽ đi sâu vào **Instance Attribute và Class Attribute**, cơ chế tra cứu thuộc tính (attribute lookup), hiện tượng *attribute shadowing*, chia sẻ dữ liệu giữa các object và những lỗi rất thường gặp khi sử dụng class attribute với kiểu dữ liệu mutable.
