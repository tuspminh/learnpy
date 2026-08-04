# Python OOP Master – Buổi 7

# Getter, Setter và `@property` (Phần 1)

> Đây là một trong những đặc điểm làm cho Python khác biệt so với Java và C++. Python **không khuyến khích** viết hàng loạt `get_name()`, `set_name()`. Thay vào đó, Python cung cấp **Property** để vừa giữ cú pháp đơn giản, vừa có thể kiểm soát dữ liệu.

Sau buổi này, bạn sẽ hiểu:

* Getter và Setter là gì.
* Vì sao Python không thích Getter/Setter kiểu Java.
* Khi nào cần kiểm soát dữ liệu.
* `property()` hoạt động như thế nào.
* `@property` giải quyết vấn đề gì.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Getter và Setter.
* Hiểu vấn đề của Public Attribute.
* Hiểu lý do ra đời của Property.
* Biết cách dùng `property()` và `@property`.
* Biết khi nào nên dùng Property.

---

# 1. Vấn đề của Public Attribute

Ví dụ

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

Có thể

```python
student = Student("Alice", 18)

student.age = -100
```

Không có lỗi.

Object rơi vào trạng thái không hợp lệ.

---

# 2. Cách Java giải quyết

Trong Java thường viết

```java
private int age;

public int getAge() {
    return age;
}

public void setAge(int age){
    this.age = age;
}
```

Sau đó

```java
student.setAge(20);
```

Không cho phép

```java
student.age = 20;
```

---

# 3. Nếu áp dụng vào Python?

Có thể viết

```python
class Student:
    def __init__(self, age):
        self.__age = age

    def get_age(self):
        return self.__age

    def set_age(self, value):
        if value < 0:
            raise ValueError("Age must be >= 0")

        self.__age = value
```

Sử dụng

```python
student = Student(18)

print(student.get_age())

student.set_age(20)
```

Hoạt động bình thường.

---

# 4. Nhưng đây không phải phong cách Python

Python khuyến khích

```python
student.age
```

thay vì

```python
student.get_age()
```

và

```python
student.age = 20
```

thay vì

```python
student.set_age(20)
```

Điều này làm code ngắn gọn, tự nhiên và dễ đọc.

---

# 5. Vấn đề khi API thay đổi

Ban đầu bạn viết

```python
class Student:
    def __init__(self):
        self.age = 18
```

Hàng nghìn dòng code sử dụng

```python
student.age
```

Một ngày bạn muốn kiểm tra dữ liệu.

Nếu đổi thành

```python
student.get_age()
```

Bạn phải sửa toàn bộ project.

Python giải quyết bằng **Property**.

---

# 6. `property()` là gì?

Python có hàm dựng sẵn:

```python
property(fget, fset, fdel, doc)
```

Trong đó:

* `fget`: hàm đọc giá trị.
* `fset`: hàm ghi giá trị.
* `fdel`: hàm xóa thuộc tính.
* `doc`: chuỗi mô tả.

Thông thường, ta dùng cú pháp `@property` thay vì gọi trực tiếp `property()`.

---

# 7. Ví dụ với `property()`

```python
class Student:
    def __init__(self, age):
        self.__age = age

    def get_age(self):
        return self.__age

    def set_age(self, value):
        if value < 0:
            raise ValueError("Age must be >= 0")

        self.__age = value

    age = property(get_age, set_age)
```

Sử dụng

```python
student = Student(18)

print(student.age)

student.age = 20

print(student.age)
```

Kết quả

```text
18
20
```

Đặc biệt:

```python
student.age = -5
```

Sẽ báo:

```text
ValueError
```

---

# 8. `@property`

Python cung cấp cú pháp đẹp hơn.

```python
class Student:
    def __init__(self, age):
        self.__age = age

    @property
    def age(self):
        return self.__age
```

Đọc

```python
student = Student(18)

print(student.age)
```

Kết quả

```text
18
```

---

# 9. Property chỉ đọc (Read-only)

Nếu chỉ có

```python
@property
```

thì

```python
student.age = 20
```

Sẽ lỗi

```text
AttributeError:
can't set attribute
```

Đây là cách tạo **Read-only Property**.

Ví dụ:

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius


circle = Circle(10)

print(circle.radius)

circle.radius = 20
```

Kết quả:

```text
10

AttributeError
```

---

# 10. Property có Setter

Muốn ghi được

```python
class Student:
    def __init__(self, age):
        self.__age = age

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, value):

        if value < 0:
            raise ValueError("Age must be >= 0")

        self.__age = value
```

Sử dụng

```python
student = Student(18)

student.age = 20

print(student.age)
```

Kết quả

```text
20
```

---

# 11. Luồng hoạt động

Khi đọc

```python
print(student.age)
```

Python thực hiện

```text
student.age

↓

@property

↓

age()

↓

return __age
```

---

Khi ghi

```python
student.age = 30
```

Python thực hiện

```text
student.age = 30

↓

@age.setter

↓

age(value)

↓

__age = value
```

---

# 12. Kiểm tra dữ liệu

Ví dụ

```python
class Temperature:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):

        if new_value < -273.15:
            raise ValueError("Temperature below absolute zero.")

        self._value = new_value
```

Sử dụng

```python
t = Temperature(25)

t.value = -300
```

Kết quả

```text
ValueError
```

---

# 13. Property tính toán

Property không nhất thiết phải lưu dữ liệu.

Ví dụ

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height
```

Sử dụng

```python
r = Rectangle(5, 10)

print(r.area)
```

Kết quả

```text
50
```

Không cần

```python
r.area()
```

Đây là một ưu điểm lớn của Property.

---

# 14. So sánh Method và Property

Method

```python
rectangle.area()
```

Property

```python
rectangle.area
```

Nếu giá trị chỉ là "đặc tính" của object (ví dụ: diện tích, chu vi, tuổi...), dùng Property sẽ tự nhiên hơn.

---

# 15. Ví dụ hoàn chỉnh

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self._salary = salary

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):

        if value < 0:
            raise ValueError("Salary must be >= 0")

        self._salary = value

    @property
    def yearly_salary(self):
        return self._salary * 12


employee = Employee("Alice", 1500)

print(employee.salary)
print(employee.yearly_salary)

employee.salary = 2000

print(employee.salary)
print(employee.yearly_salary)
```

Kết quả

```text
1500
18000
2000
24000
```

---

# 16. Vì sao Property quan trọng?

Giả sử phiên bản đầu tiên:

```python
student.age
```

Sau vài tháng, cần kiểm tra dữ liệu.

Nếu dùng Property:

Không cần sửa code bên ngoài.

```python
student.age
```

vẫn giữ nguyên.

Đây gọi là:

```text
Backward Compatibility
```

Một trong những lý do khiến rất nhiều thư viện Python sử dụng Property.

---

# Best Practices

✅ Dùng Public Attribute nếu không cần kiểm tra dữ liệu.

```python
self.name
```

✅ Dùng Property khi:

* cần kiểm tra dữ liệu;
* cần tính toán động;
* cần chuyển đổi định dạng;
* muốn giữ API ổn định.

✅ Dùng tên thuộc tính nội bộ với `_` hoặc `__` để tránh đệ quy trong setter.

Ví dụ:

```python
self._salary
```

thay vì:

```python
self.salary
```

bên trong setter.

---

# Những lỗi người mới thường gặp

## Lỗi 1: Đệ quy vô hạn

Sai:

```python
class Student:
    @property
    def age(self):
        return self.age
```

`self.age` sẽ lại gọi chính property `age`, dẫn đến `RecursionError`.

Đúng:

```python
return self._age
```

---

## Lỗi 2: Setter tự gọi lại chính nó

Sai:

```python
@age.setter
def age(self, value):
    self.age = value
```

Điều này lại gọi setter một lần nữa và gây đệ quy vô hạn.

Đúng:

```python
self._age = value
```

---

## Lỗi 3: Viết Getter/Setter kiểu Java

Không nên:

```python
student.get_name()
student.set_name("Alice")
```

Trong Python, nếu không có lý do đặc biệt, hãy dùng Property để giữ cú pháp:

```python
student.name
student.name = "Alice"
```

---

# Bài tập

## Bài 1

Viết class `Person`:

* `_age`

Tạo Property:

* `age`

Yêu cầu:

* tuổi ≥ 0;
* in thử trước và sau khi thay đổi.

---

## Bài 2

Viết class `BankAccount`

* `_balance`

Property:

* `balance`

Không cho phép số dư âm.

---

## Bài 3

Viết class `Square`

Thuộc tính:

* `side`

Property:

* `area`

`area` là **read-only property**.

---

## Bài 4

Viết class `Circle`

Thuộc tính:

* `_radius`

Property:

* `radius`
* `diameter`
* `area`

Trong đó:

* `radius` có getter và setter.
* `diameter` và `area` chỉ đọc.

---

## Bài 5 (Nâng cao)

Thiết kế class `Employee`

Thuộc tính nội bộ:

```text
_name
_salary
_tax_rate
```

Yêu cầu:

Property:

* `salary`
* `tax`
* `net_salary`

Trong đó:

* `salary` có getter và setter (không cho phép âm).
* `tax` chỉ đọc (`salary * tax_rate`).
* `net_salary` chỉ đọc (`salary - tax`).

Kiểm tra rằng sau khi thay đổi `salary`, cả `tax` và `net_salary` đều cập nhật tự động.

---

# Tóm tắt buổi học

* Getter và Setter giúp kiểm soát việc đọc/ghi dữ liệu, nhưng Python ưu tiên dùng **Property** thay vì các phương thức `get_*`/`set_*`.
* `@property` cho phép truy cập bằng cú pháp thuộc tính (`obj.attr`) trong khi vẫn thực thi logic phía sau.
* `@<property>.setter` cho phép kiểm tra và xác thực dữ liệu trước khi cập nhật.
* Property có thể là **read-only** hoặc **computed property**, rất hữu ích để giữ API ổn định và hỗ trợ tương thích ngược.
* Luôn lưu dữ liệu thật trong thuộc tính nội bộ (`_name`, `_salary`, ...) để tránh đệ quy vô hạn.

> **Buổi 8** chúng ta sẽ đi sâu vào **Property nâng cao**: `@deleter`, `property()` đầy đủ, cơ chế **Descriptor** phía sau `property`, cached property, validation phức tạp và cách các framework như Django, SQLAlchemy, Pydantic tận dụng descriptor để xây dựng API mạnh mẽ.
