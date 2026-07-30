# Buổi 7: `@property`, Getter, Setter, Deleter và nền tảng Descriptor

Đây là một trong những buổi quan trọng nhất của OOP Python.

Sau buổi này bạn sẽ hiểu:

- Vì sao Python **không khuyến khích** viết getter/setter như Java.
- `@property` thực chất là gì.
- Vì sao có thể viết:

```text-x-trilium-auto
print(person.age)
```

thay vì

```text-x-trilium-auto
print(person.get_age())
```

- `property` hoạt động bên trong như thế nào.
- Tại sao SQLAlchemy, Django ORM, PySide6... đều dựa trên Descriptor.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu được:

- Getter
- Setter
- Deleter
- Property Object
- Read Only Property
- Validation
- Computed Property
- Property Chain

---

# 1. Vấn đề khi dùng Public Attribute

Ví dụ:

```text-x-trilium-auto
class Person:

    def __init__(self, age):
        self.age = age
```

Sử dụng:

```text-x-trilium-auto
p = Person(20)

p.age = -100
```

Python vẫn chấp nhận.

Kết quả:

```text-x-trilium-auto
print(p.age)
```

```text-x-trilium-auto
-100
```

Điều này không hợp lý.

Ta muốn:

```text-x-trilium-auto
Tuổi phải >= 0
```

---

# 2. Cách làm trong Java

Java thường viết:

```text-x-trilium-auto
person.setAge(20);

person.getAge();
```

Python không thích cách này.

Python muốn:

```text-x-trilium-auto
person.age = 20

print(person.age)
```

vẫn đẹp như dùng biến.

---

# 3. Getter truyền thống

Ví dụ:

```text-x-trilium-auto
class Person:

    def __init__(self):
        self._age = 0

    def get_age(self):
        return self._age
```

Dùng:

```text-x-trilium-auto
p = Person()

print(p.get_age())
```

Hoạt động.

Nhưng Pythonic không thích.

---

# 4. Setter truyền thống

```text-x-trilium-auto
class Person:

    def __init__(self):
        self._age = 0

    def set_age(self, value):

        if value < 0:
            raise ValueError

        self._age = value
```

Dùng:

```text-x-trilium-auto
p.set_age(20)
```

Nhìn giống Java.

---

# 5. Pythonic Solution

Python tạo ra:

```text-x-trilium-auto
@property
```

Ví dụ:

```text-x-trilium-auto
class Person:

    def __init__(self):
        self._age = 0

    @property
    def age(self):
        return self._age
```

Bây giờ:

```text-x-trilium-auto
p = Person()

print(p.age)
```

Không cần:

```text-x-trilium-auto
p.get_age()
```

---

# 6. Điều kỳ diệu xảy ra

Bạn tưởng:

```text-x-trilium-auto
p.age
```

đang đọc biến.

Thực tế:

Python gọi:

```text-x-trilium-auto
Person.age.__get__(p)
```

Sau đó:

```text-x-trilium-auto
age(self)
```

được thực thi.

Nghĩa là:

```text-x-trilium-auto
p.age

↓

property object

↓

getter()

↓

return value
```

---

# 7. Getter với @property

Ví dụ:

```text-x-trilium-auto
class Person:

    def __init__(self,name):
        self._name = name

    @property
    def name(self):
        print("Getter được gọi")
        return self._name
```

Thử:

```text-x-trilium-auto
p = Person("An")

print(p.name)
```

Kết quả:

```text-x-trilium-auto
Getter được gọi

An
```

---

# 8. Setter

Ta thêm:

```text-x-trilium-auto
class Person:

    def __init__(self):
        self._age = 0

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self,value):

        if value < 0:
            raise ValueError(
                "Age must >=0"
            )

        self._age = value
```

Sử dụng:

```text-x-trilium-auto
p = Person()

p.age = 20
```

Python thực hiện:

```text-x-trilium-auto
Person.age.__set__(p,20)
```

---

# 9. Validation

Ví dụ:

```text-x-trilium-auto
p.age = -5
```

Kết quả:

```text-x-trilium-auto
ValueError
```

Đây là lợi ích lớn nhất của property.

---

# 10. Read Only Property

Ví dụ:

```text-x-trilium-auto
class Circle:

    def __init__(self,r):
        self.radius = r

    @property
    def area(self):
        return 3.14 * self.radius **2
```

Dùng:

```text-x-trilium-auto
c = Circle(10)

print(c.area)
```

Kết quả:

```text-x-trilium-auto
314
```

Nhưng:

```text-x-trilium-auto
c.area = 500
```

Kết quả:

```text-x-trilium-auto
AttributeError
```

Vì không có setter.

---

# 11. Computed Property

Property không cần lưu dữ liệu.

Ví dụ:

```text-x-trilium-auto
class Rectangle:

    def __init__(self,w,h):
        self.width = w
        self.height = h

    @property
    def area(self):
        return self.width * self.height
```

Không hề có:

```text-x-trilium-auto
self.area
```

Mỗi lần:

```text-x-trilium-auto
rect.area
```

Python tính lại.

---

# 12. Setter không nhất thiết lưu nguyên giá trị

Ví dụ:

```text-x-trilium-auto
class Temperature:

    def __init__(self):
        self._c = 0

    @property
    def celsius(self):
        return self._c

    @celsius.setter
    def celsius(self,v):

        self._c = round(v,1)
```

Dùng:

```text-x-trilium-auto
t = Temperature()

t.celsius = 20.5678

print(t.celsius)
```

Kết quả:

```text-x-trilium-auto
20.6
```

Setter có thể xử lý dữ liệu trước khi lưu.

---

# 13. Deleter

Có thể:

```text-x-trilium-auto
class Person:

    def __init__(self):
        self._name = "An"

    @property
    def name(self):
        return self._name

    @name.deleter
    def name(self):
        print("Delete")

        del self._name
```

Dùng:

```text-x-trilium-auto
del p.name
```

Python gọi:

```text-x-trilium-auto
Person.name.__delete__(p)
```

---

# 14. Property Object

Xem:

```text-x-trilium-auto
print(Person.__dict__["age"])
```

Kết quả:

```text-x-trilium-auto
<property object at ...>
```

Không còn là function.

Sơ đồ:

```text-x-trilium-auto
Class

age

↓

property object

↓

getter

setter

deleter
```

---

# 15. Property bên trong

Thực chất:

```text-x-trilium-auto
@property def age(self):
    ...
```

gần giống:

```text-x-trilium-auto
age = property(age)
```

Sau đó:

```text-x-trilium-auto
age = age.setter(set_age)
```

Nên:

```text-x-trilium-auto
Person.age
```

không còn là function.

Mà là:

```text-x-trilium-auto
property object
```

---

# 16. Ví dụ đầy đủ

```text-x-trilium-auto
class Employee:

    def __init__(self,name,salary):

        self.name = name
        self._salary = salary

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self,value):

        if value <0:
            raise ValueError(
                "Salary >0"
            )

        self._salary = value
```

Sử dụng:

```text-x-trilium-auto
e = Employee("An",1000)

print(e.salary)

e.salary = 2000

print(e.salary)
```

---

# 17. Property trong dự án lớn

Ví dụ Model Book:

```text-x-trilium-auto
class Book:

    def __init__(self,title):

        self._title = title

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self,v):

        if not v.strip():
            raise ValueError

        self._title = v
```

UI:

```text-x-trilium-auto
book.title = input_title
```

Không cần biết bên trong đang validate.

---

# 18. Property là Descriptor

Đây là điều quan trọng.

Khi:

```text-x-trilium-auto
obj.age
```

Python làm:

```text-x-trilium-auto
obj.age

↓

property

↓

__get__()

↓

getter()
```

Khi:

```text-x-trilium-auto
obj.age = 10
```

Python làm:

```text-x-trilium-auto
property

↓

__set__()

↓

setter()
```

Đây chính là **Descriptor Protocol**.

Chúng ta sẽ học rất sâu ở phần Descriptor (Buổi 21–24), nhưng ngay từ bây giờ bạn đã thấy rằng `property` không phải là "phép màu", mà là một object đặc biệt tham gia vào quá trình tra cứu thuộc tính.

---

# 19. Sai lầm phổ biến

## Sai

```text-x-trilium-auto
@property def age(self):
    return self.age
```

Điều này gây:

```text-x-trilium-auto
RecursionError
```

Vì `self.age` lại gọi getter của `age`, tạo vòng lặp vô hạn.

Đúng:

```text-x-trilium-auto
@property def age(self):
    return self._age
```

---

## Sai

Trong setter:

```text-x-trilium-auto
@age.setter def age(self,v):

    self.age = v
```

Lại gọi chính setter.

Đúng:

```text-x-trilium-auto
self._age = v
```

---

# 20. Tổng kết

| Thành phần | Vai trò |
| --- | --- |
| `@property` | Biến method thành thuộc tính |
| Getter | Đọc dữ liệu |
| Setter | Ghi và kiểm tra dữ liệu |
| Deleter | Xóa dữ liệu |
| Read-only property | Chỉ có getter |
| Computed property | Giá trị được tính toán khi truy cập |
| `property` | Một descriptor đặc biệt |

---

# Bài tập thực hành

## Bài 1

Viết lớp `Student`:

- `_name`
- `_score`

Yêu cầu:

- `name` không được rỗng.
- `score` chỉ nhận giá trị từ `0` đến `10`.

Sử dụng `@property` và `@setter`.

---

## Bài 2

Viết lớp `Circle`:

- `radius`

Property:

```text-x-trilium-auto
area
```

chỉ đọc (read-only), tự tính diện tích theo công thức:

```text-x-trilium-auto
π × r²
```

Không được lưu `area` trong `__init__`.

---

## Bài 3

Viết lớp `Temperature`:

Lưu:

```text-x-trilium-auto
_celsius
```

Tạo hai property:

```text-x-trilium-auto
celsius fahrenheit
```

Yêu cầu:

- Gán `celsius` thì `fahrenheit` thay đổi theo.
- Gán `fahrenheit` thì `celsius` thay đổi theo.
- Không lưu trùng hai giá trị, chỉ lưu `_celsius`.

Đây là một ví dụ điển hình của **computed property**.

---

## Bài 4 (Áp dụng vào dự án crawler)

Thiết kế lớp:

```text-x-trilium-auto
class CrawlJob:
```

Có các thuộc tính:

- `_url`
- `_status`
- `_progress`

Yêu cầu:

- `url`: không được rỗng.
- `progress`: chỉ nhận giá trị từ `0` đến `100`.
- `status`: chỉ cho phép `"pending"`, `"running"`, `"paused"`, `"finished"` hoặc `"error"`.

Sử dụng `@property` để đảm bảo mọi thay đổi đều được kiểm tra trước khi lưu.

---

# Chuẩn bị cho Buổi 8

Buổi tiếp theo chúng ta sẽ tiếp tục với **Property nâng cao**, bao gồm:

- Lazy Property (chỉ tính toán khi cần).
- Cached Property (lưu kết quả để tăng hiệu năng).
- Validation Pattern.
- Property kết hợp với `dataclass`.
- Thiết kế API Pythonic bằng property.
- Các lỗi hiệu năng và cách tối ưu khi dùng property trong các dự án lớn.

Đây là bước đệm trước khi chúng ta chuyển sang **Inheritance (Kế thừa)** ở các buổi tiếp theo.