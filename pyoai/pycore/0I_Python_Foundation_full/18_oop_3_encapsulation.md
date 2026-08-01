# Khóa học Python từ Cơ bản đến Chuyên gia

# Buổi 18: OOP - Phần 3: Đóng gói (Encapsulation), Public, Protected, Private, Property, Getter và Setter

> **Mục tiêu buổi học**
> 
> Sau buổi học này, bạn sẽ:
> 
> - Hiểu bản chất của Encapsulation (Đóng gói).
> - Phân biệt Public, Protected và Private trong Python.
> - Hiểu cơ chế Name Mangling.
> - Thành thạo `@property`, `@setter`, `@deleter`.
> - Biết cách thiết kế Class an toàn và dễ bảo trì.
> - Áp dụng vào các hệ thống thực tế như ngân hàng, thương mại điện tử, quản lý người dùng.

---

# 1. Encapsulation là gì?

Encapsulation (Đóng gói) là một trong **4 trụ cột của OOP**:

1. Encapsulation (Đóng gói)
2. Inheritance (Kế thừa)
3. Polymorphism (Đa hình)
4. Abstraction (Trừu tượng)

Đóng gói có nghĩa là:

> **Ẩn dữ liệu bên trong đối tượng và chỉ cho phép truy cập thông qua các giao diện được kiểm soát.**

Ví dụ ngoài đời:

Một chiếc ATM.

Bạn chỉ thấy:

- Nhập PIN
- Rút tiền
- Chuyển khoản

Bạn **không thể** truy cập trực tiếp vào cơ sở dữ liệu ngân hàng.

Đó chính là Encapsulation.

---

# 2. Vì sao cần Encapsulation?

Giả sử:

```text-x-trilium-auto
class BankAccount:

    def __init__(self):
        self.balance = 1000
```

Người khác có thể:

```text-x-trilium-auto
acc = BankAccount()

acc.balance = -999999999
```

Không hợp lý.

Số dư không thể âm.

Ta cần kiểm soát việc thay đổi dữ liệu.

---

# 3. Public Attribute

Trong Python:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self.name = "An"
```

`name`

là **Public**.

Có thể truy cập từ mọi nơi.

```text-x-trilium-auto
student.name
```

Có thể sửa:

```text-x-trilium-auto
student.name = "Bình"
```

---

# 4. Protected Attribute

Python dùng quy ước:

```text-x-trilium-auto
_name
```

Ví dụ:

```text-x-trilium-auto
class Student:

    def __init__(self):
        self._score = 9
```

Đây là:

Protected.

Có nghĩa:

> **"Đây là dữ liệu nội bộ. Đừng truy cập nếu không thật sự cần."**

Lưu ý:

Đây chỉ là **quy ước**, Python **không cấm** truy cập.

```text-x-trilium-auto
print(student._score)
```

vẫn hoạt động.

---

# 5. Private Attribute

Python dùng:

```text-x-trilium-auto
__balance
```

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    def __init__(self):

        self.__balance = 1000
```

Bây giờ:

```text-x-trilium-auto
acc.__balance
```

Lỗi:

```text-x-trilium-auto
AttributeError
```

---

# 6. Name Mangling

Nhiều người nghĩ:

Python mã hóa dữ liệu.

Không phải.

Python chỉ đổi tên.

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    def __init__(self):

        self.__balance = 1000
```

Thực chất thành:

```text-x-trilium-auto
_BankAccount__balance
```

Có thể xem:

```text-x-trilium-auto
print(acc.__dict__)
```

Kết quả:

```text-x-trilium-auto
{
    '_BankAccount__balance':1000
}
```

Đây gọi là:

**Name Mangling**.

---

# 7. Truy cập Private

Có thể:

```text-x-trilium-auto
print(acc._BankAccount__balance)
```

Nhưng:

> Không nên.

Đây chỉ dành cho:

- Debug
- Testing
- Framework

---

# 8. Getter và Setter

Trong nhiều ngôn ngữ:

```text-x-trilium-auto
getName()

setName()
```

Python có cách hiện đại hơn.

---

# 9. `@property`

Ví dụ:

```text-x-trilium-auto
class BankAccount:

    def __init__(self):

        self.__balance = 1000

    @property
    def balance(self):
        return self.__balance
```

Sử dụng:

```text-x-trilium-auto
acc = BankAccount()

print(acc.balance)
```

Không cần:

```text-x-trilium-auto
acc.get_balance()
```

Đây là phong cách Pythonic.

---

# 10. Setter

```text-x-trilium-auto
class BankAccount:

    def __init__(self):
        self.__balance = 0

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):

        if value < 0:
            raise ValueError("Số dư không được âm.")

        self.__balance = value
```

Sử dụng:

```text-x-trilium-auto
acc.balance = 1000
```

Nếu:

```text-x-trilium-auto
acc.balance = -100
```

Kết quả:

```text-x-trilium-auto
ValueError
```

---

# 11. Deleter

Có thể:

```text-x-trilium-auto
class Student:

    @property
    def name(self):
        return self._name

    @name.deleter
    def name(self):
        print("Đã xóa tên")
        del self._name
```

Sử dụng:

```text-x-trilium-auto
del student.name
```

---

# 12. Ví dụ thực tế: Tài khoản ngân hàng

```text-x-trilium-auto
class BankAccount:

    def __init__(self, owner, balance=0):

        self.owner = owner

        self.__balance = balance

    @property
    def balance(self):

        return self.__balance

    def deposit(self, amount):

        if amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0.")

        self.__balance += amount

    def withdraw(self, amount):

        if amount > self.__balance:
            raise ValueError("Không đủ tiền.")

        self.__balance -= amount
```

Sử dụng:

```text-x-trilium-auto
acc = BankAccount("An", 1000)

acc.deposit(500)

print(acc.balance)
```

Lập trình viên khác **không thể** tự ý sửa `__balance`.

---

# 13. Property chỉ đọc (Read-only)

```text-x-trilium-auto
class Circle:

    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):

        return 3.14159 * self.radius**2
```

Sử dụng:

```text-x-trilium-auto
circle.area
```

Không thể:

```text-x-trilium-auto
circle.area = 100
```

Rất hữu ích cho các giá trị được tính toán.

---

# 14. Property tính toán

```text-x-trilium-auto
class Rectangle:

    def __init__(self, width, height):

        self.width = width

        self.height = height

    @property
    def area(self):

        return self.width * self.height
```

Không cần:

```text-x-trilium-auto
rectangle.get_area()
```

---

# 15. Validation bằng Property

```text-x-trilium-auto
class Employee:

    def __init__(self, salary):

        self.salary = salary

    @property
    def salary(self):

        return self.__salary

    @salary.setter
    def salary(self, value):

        if value < 0:

            raise ValueError("Salary không hợp lệ.")

        self.__salary = value
```

---

# 16. Những lỗi phổ biến

## Lỗi 1

Setter gọi chính nó.

Sai:

```text-x-trilium-auto
self.balance = value
```

Trong setter.

Đúng:

```text-x-trilium-auto
self.__balance = value
```

Hoặc:

```text-x-trilium-auto
self._balance = value
```

---

## Lỗi 2

Quên dùng Property.

Viết:

```text-x-trilium-auto
student.age = -100
```

Không kiểm tra.

---

## Lỗi 3

Dùng Private quá nhiều.

Sai:

```text-x-trilium-auto
__name

__age

__phone

__email
```

Không phải thuộc tính nào cũng cần Private.

Thông thường:

- Public nếu dữ liệu không nhạy cảm.
- Protected nếu dành cho nội bộ hoặc lớp kế thừa.
- Private khi cần bảo vệ dữ liệu hoặc tránh ghi đè ngoài ý muốn.

---

# 17. Ví dụ hiện đại

## User

```text-x-trilium-auto
class User:

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}"
```

---

## Product

```text-x-trilium-auto
@property
def final_price(self):
```

Tính:

```text-x-trilium-auto
Giá

↓

Thuế

↓

Khuyến mãi
```

---

## API

```text-x-trilium-auto
@property
def is_success(self):
```

Trả:

```text-x-trilium-auto
status==200
```

---

# 18. Khi nào dùng Property?

Dùng khi:

- Cần kiểm tra dữ liệu trước khi gán.
- Giá trị được tính toán từ các thuộc tính khác.
- Muốn giữ giao diện truy cập đơn giản (`obj.attr`) nhưng vẫn có thể thay đổi cách cài đặt bên trong mà không ảnh hưởng đến mã đang sử dụng.

---

# 19. Bài tập thực hành

## Bài 1

Viết Class:

```text-x-trilium-auto
Person
```

Có:

- `name`
- `age`

Không cho phép:

```text-x-trilium-auto
age < 0
```

Sử dụng `@property`.

---

## Bài 2

Viết Class:

```text-x-trilium-auto
BankAccount
```

Có:

- deposit()
- withdraw()

Số dư luôn ≥ 0.

---

## Bài 3

Viết Class:

```text-x-trilium-auto
Circle
```

Có:

```text-x-trilium-auto
area
```

là Read-only Property.

---

## Bài 4

Viết Class:

```text-x-trilium-auto
Employee
```

Salary:

- không âm.
- không vượt quá một mức tối đa do bạn tự đặt.

---

## Bài 5

Viết Class:

```text-x-trilium-auto
Product
```

Property:

```text-x-trilium-auto
final_price
```

Tính:

```text-x-trilium-auto
price

↓

discount

↓

VAT
```

---

## Bài 6

Xây dựng Class:

```text-x-trilium-auto
LibraryBook
```

Yêu cầu:

- Thuộc tính `title`, `author`, `isbn`.
- `isbn` chỉ được đọc (Read-only Property) sau khi khởi tạo.
- `quantity` không được âm.

---

# Mini Project: Hệ thống Ví điện tử

Thiết kế lớp:

```text-x-trilium-auto
Wallet
```

Thuộc tính:

- owner
- balance (Private)

Phương thức:

- deposit()
- withdraw()
- transfer()
- show_balance()

Yêu cầu:

- Không cho phép số dư âm.
- Không cho phép nạp hoặc chuyển số tiền ≤ 0.
- `balance` chỉ được đọc thông qua Property.

**Mở rộng:**

- Ghi lại lịch sử giao dịch trong một danh sách.
- Tạo Property `transaction_count` để trả về số giao dịch đã thực hiện.

---

# Tổng kết buổi 18

Bạn đã học:

- ✅ Encapsulation.
- ✅ Public.
- ✅ Protected.
- ✅ Private.
- ✅ Name Mangling.
- ✅ `@property`.
- ✅ `@setter`.
- ✅ `@deleter`.
- ✅ Read-only Property.
- ✅ Validation bằng Property.

---

# Góc lập trình viên chuyên nghiệp

Trong các framework như:

- **Django ORM**
- **SQLAlchemy**
- **Pydantic**
- **PySide6**
- **Flet**

bạn sẽ thường thấy việc dùng Property để:

- Kiểm tra dữ liệu.
- Tính toán thuộc tính động.
- Che giấu chi tiết cài đặt.
- Cung cấp giao diện truy cập đơn giản nhưng an toàn.

Đây là một trong những kỹ thuật giúp mã nguồn **dễ bảo trì**, **dễ mở rộng** và giảm lỗi khi dự án ngày càng lớn.

---

# Chuẩn bị cho Buổi 19

Ở **Buổi 19**, chúng ta sẽ học trụ cột thứ hai của OOP:

# **Kế thừa (Inheritance)**

Nội dung sẽ bao gồm:

- Khái niệm kế thừa.
- Lớp cha (Base Class) và lớp con (Derived Class).
- Ghi đè phương thức (Method Overriding).
- Hàm `super()`.
- Kế thừa nhiều cấp (Multilevel Inheritance).
- Đa kế thừa (Multiple Inheritance).
- MRO (Method Resolution Order).
- Thiết kế hệ thống quản lý nhân sự và động vật bằng kế thừa.

Sau buổi này, bạn sẽ biết cách **tái sử dụng mã nguồn**, giảm lặp code và xây dựng các hệ thống hướng đối tượng có cấu trúc tốt theo chuẩn Python hiện đại.
