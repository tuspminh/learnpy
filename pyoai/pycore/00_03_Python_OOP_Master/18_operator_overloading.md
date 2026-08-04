# Python OOP Master – Buổi 18

# Operator Overloading – Nạp chồng toán tử trong Python

> Đây là một trong những tính năng mạnh nhất của Magic Methods.
>
> Sau buổi học này, bạn sẽ hiểu vì sao có thể viết:
>
> ```python
> money1 + money2
> vector1 + vector2
> point1 == point2
> matrix * matrix
> ```
>
> trong khi `Money`, `Vector`, `Point` đều là class do chính bạn tạo.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Operator Overloading là gì.
* Biết Python ánh xạ toán tử sang Magic Method.
* Cài đặt các toán tử số học và so sánh.
* Hiểu `NotImplemented`.
* Biết cách viết class giống kiểu dữ liệu chuẩn của Python.
* Áp dụng vào dự án quản lý truyện.

---

# 1. Operator Overloading là gì?

Operator Overloading (nạp chồng toán tử) là khả năng định nghĩa ý nghĩa của các toán tử (`+`, `-`, `*`, `==`, `<`...) cho class của bạn.

Ví dụ:

```python
1 + 2
```

Python thực chất gọi:

```python
(1).__add__(2)
```

Tương tự:

```python
a + b
```

↓

```python
a.__add__(b)
```

---

# 2. Bảng ánh xạ toán tử

| Toán tử | Magic Method     |
| ------- | ---------------- |
| `+`     | `__add__()`      |
| `-`     | `__sub__()`      |
| `*`     | `__mul__()`      |
| `/`     | `__truediv__()`  |
| `//`    | `__floordiv__()` |
| `%`     | `__mod__()`      |
| `**`    | `__pow__()`      |
| `==`    | `__eq__()`       |
| `!=`    | `__ne__()`       |
| `<`     | `__lt__()`       |
| `<=`    | `__le__()`       |
| `>`     | `__gt__()`       |
| `>=`    | `__ge__()`       |

---

# 3. Ví dụ đầu tiên

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __repr__(self):
        return f"Money({self.amount})"


m1 = Money(100)
m2 = Money(250)

print(m1 + m2)
```

Kết quả

```text
Money(350)
```

---

# 4. Python làm gì?

Khi viết

```python
m1 + m2
```

Python thực hiện

```python
m1.__add__(m2)
```

Nếu không có

```python
__add__()
```

↓

```text
TypeError
```

---

# 5. `__sub__()`

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __sub__(self, other):
        return Money(self.amount - other.amount)

    def __repr__(self):
        return f"Money({self.amount})"


print(Money(500) - Money(200))
```

↓

```text
Money(300)
```

---

# 6. `__mul__()`

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __mul__(self, n):
        return Money(self.amount * n)

    def __repr__(self):
        return f"Money({self.amount})"


print(Money(100) * 5)
```

↓

```text
Money(500)
```

---

# 7. `__truediv__()`

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __truediv__(self, n):
        return Money(self.amount / n)

    def __repr__(self):
        return f"Money({self.amount})"


print(Money(1000) / 4)
```

↓

```text
Money(250.0)
```

---

# 8. So sánh bằng

```python
class User:
    def __init__(self, username):
        self.username = username

    def __eq__(self, other):
        return self.username == other.username
```

```python
u1 = User("alice")
u2 = User("alice")
u3 = User("bob")

print(u1 == u2)

print(u1 == u3)
```

↓

```text
True
False
```

---

# 9. Nếu không có `__eq__()`

```python
class User:
    def __init__(self, username):
        self.username = username
```

```python
User("alice") == User("alice")
```

↓

```text
False
```

Python mặc định so sánh **địa chỉ object**, không phải dữ liệu.

---

# 10. `__lt__()`

```python
class Student:
    def __init__(self, score):
        self.score = score

    def __lt__(self, other):
        return self.score < other.score
```

```python
print(Student(70) < Student(80))
```

↓

```text
True
```

---

# 11. Sắp xếp

```python
students = [
    Student(90),
    Student(60),
    Student(75),
]
```

```python
students.sort()
```

Python sẽ dùng

```python
__lt__()
```

---

# 12. `NotImplemented`

Đây là điểm rất quan trọng.

Sai

```python
def __add__(self, other):

    return None
```

Đúng

```python
def __add__(self, other):

    if not isinstance(other, Money):
        return NotImplemented

    return Money(self.amount + other.amount)
```

`NotImplemented` cho Python biết:

> "Tôi không biết xử lý kiểu này, hãy thử cách khác."

---

# 13. Reverse Operator

Ví dụ

```python
5 + Money(10)
```

Python sẽ thử

```python
int.__add__()
```

Nếu thất bại

↓

Python gọi

```python
Money.__radd__()
```

Ví dụ

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __radd__(self, value):
        return Money(value + self.amount)

    def __repr__(self):
        return f"Money({self.amount})"


print(5 + Money(10))
```

↓

```text
Money(15)
```

---

# 14. In-place Operator

```python
+=
```

↓

```python
__iadd__()
```

Ví dụ

```python
class Counter:
    def __init__(self, value):
        self.value = value

    def __iadd__(self, n):
        self.value += n
        return self

    def __repr__(self):
        return str(self.value)
```

```python
counter = Counter(10)

counter += 5

print(counter)
```

↓

```text
15
```

---

# 15. Ví dụ Vector

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"({self.x}, {self.y})"
```

```python
v1 = Vector(2, 3)
v2 = Vector(5, 8)

print(v1 + v2)
```

↓

```text
(7, 11)
```

---

# 16. Ví dụ trong dự án cào truyện

```python
class Chapter:
    def __init__(self, number):
        self.number = number

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):
        return f"Chapter({self.number})"
```

```python
chapters = [
    Chapter(5),
    Chapter(2),
    Chapter(10),
]

chapters.sort()

print(chapters)
```

↓

```text
[
 Chapter(2),
 Chapter(5),
 Chapter(10)
]
```

---

# 17. `functools.total_ordering`

Nếu đã có:

```python
__eq__()
```

và

```python
__lt__()
```

Python có thể tự sinh:

* `<=`
* `>`
* `>=`

Ví dụ

```python
from functools import total_ordering


@total_ordering
class Student:
    def __init__(self, score):
        self.score = score

    def __eq__(self, other):
        return self.score == other.score

    def __lt__(self, other):
        return self.score < other.score
```

---

# 18. Ví dụ hoàn chỉnh

```python
class Book:
    def __init__(self, title, price):
        self.title = title
        self.price = price

    def __lt__(self, other):
        return self.price < other.price

    def __eq__(self, other):
        return self.title == other.title and self.price == other.price

    def __repr__(self):
        return f"Book({self.title!r}, {self.price})"


books = [
    Book("Python", 50),
    Book("C++", 20),
    Book("Java", 35),
]

books.sort()

print(books)
```

---

# 19. Những Magic Methods liên quan

| Method         | Ý nghĩa                                 |
| -------------- | --------------------------------------- |
| `__add__`      | `+`                                     |
| `__sub__`      | `-`                                     |
| `__mul__`      | `*`                                     |
| `__truediv__`  | `/`                                     |
| `__floordiv__` | `//`                                    |
| `__mod__`      | `%`                                     |
| `__pow__`      | `**`                                    |
| `__eq__`       | `==`                                    |
| `__ne__`       | `!=`                                    |
| `__lt__`       | `<`                                     |
| `__le__`       | `<=`                                    |
| `__gt__`       | `>`                                     |
| `__ge__`       | `>=`                                    |
| `__radd__`     | Toán hạng bên trái không xử lý được `+` |
| `__iadd__`     | `+=`                                    |

---

# Best Practices

✅ Chỉ overload toán tử khi **ý nghĩa tự nhiên**.

Ví dụ:

* Vector + Vector
* Money + Money
* Matrix × Matrix

---

✅ Trả về object mới thay vì sửa object hiện tại (trừ các toán tử in-place như `+=`).

---

✅ Kiểm tra kiểu dữ liệu và trả về `NotImplemented` nếu không hỗ trợ.

---

✅ Giữ ý nghĩa của toán tử nhất quán với trực giác của người dùng.

---

# Những lỗi người mới thường gặp

## Lỗi 1

Không kiểm tra kiểu

```python
def __add__(self, other):
    return Money(self.amount + other.amount)
```

Nếu:

```python
Money(10) + 5
```

↓

```text
AttributeError
```

---

## Lỗi 2

Trả về kiểu sai

Sai

```python
def __add__(self, other):

    return self.amount + other.amount
```

Nên

```python
return Money(...)
```

để giữ tính nhất quán.

---

## Lỗi 3

Lạm dụng Operator Overloading

Ví dụ

```python
user1 + user2
```

Nghĩa là gì?

Không rõ ràng.

Trong trường hợp này nên dùng

```python
user.merge(user2)
```

---

## Lỗi 4

Quên `__repr__()`

Khi debug sẽ thấy

```text
<User object at ...>
```

thay vì thông tin hữu ích.

---

# Bài tập

## Bài 1

Viết class `Money` hỗ trợ:

* `+`
* `-`
* `*`
* `/`

và `__repr__()`.

---

## Bài 2

Viết class `Vector2D` hỗ trợ:

* cộng hai vector
* trừ hai vector
* so sánh bằng

Ví dụ:

```python
Vector2D(1, 2) + Vector2D(3, 4)
```

---

## Bài 3

Viết class `Book` với:

* `title`
* `price`

Cài đặt:

* `__lt__()`
* `__eq__()`

Sau đó sắp xếp danh sách sách theo giá.

---

## Bài 4

Trong dự án cào truyện, viết class `Chapter`:

* `number`
* `title`

Cài đặt `__lt__()` để có thể:

```python
chapters.sort()
```

---

## Bài 5 (Nâng cao)

Thiết kế class `CrawlerStats`:

Thuộc tính:

* `success`
* `failed`

Yêu cầu:

* `stats1 + stats2` cộng số liệu.
* `stats1 == stats2` so sánh.
* `stats += stats2`.
* Hỗ trợ:

```python
sum(list_of_stats)
```

(*Gợi ý:* cần triển khai thêm `__radd__()` để `sum()` hoạt động tốt.)

---

# Tổng kết buổi học

* **Operator Overloading** cho phép định nghĩa ý nghĩa của các toán tử trên class tự tạo thông qua các Magic Methods.
* Các toán tử như `+`, `-`, `*`, `==`, `<`... đều được Python ánh xạ sang các phương thức đặc biệt như `__add__()`, `__sub__()`, `__eq__()`, `__lt__()`.
* Hãy trả về `NotImplemented` khi không hỗ trợ kiểu dữ liệu, thay vì tự gây lỗi hoặc trả về giá trị không phù hợp.
* Chỉ nên overload toán tử khi hành vi của nó **tự nhiên và trực quan**, tránh làm mã nguồn khó hiểu.
* Trong các hệ thống thực tế như framework cào truyện, việc overload các toán tử so sánh giúp sắp xếp chapter, so sánh phiên bản hoặc cộng dồn thống kê một cách tự nhiên.

> **Buổi 19** chúng ta sẽ học **Container Magic Methods**: `__len__()`, `__getitem__()`, `__setitem__()`, `__contains__()`, `__iter__()`, `__next__()`... Đây là nhóm Magic Methods giúp class của bạn hoạt động như `list`, `dict` hoặc các container chuẩn của Python. Chúng là nền tảng để xây dựng các Repository, Collection và Model Manager chuyên nghiệp.
