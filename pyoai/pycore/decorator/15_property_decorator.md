# Decorator Deep Dive — Buổi 15

# `@property` Decorator

Đây là buổi cuối của **Phần III — Decorator nâng cao**.

`@property` đặc biệt quan trọng vì nó cho thấy decorator không chỉ dùng để "bọc function". Nó có thể biến một method thành **attribute có hành vi**.

Ví dụ:

```python
user.full_name
```

nhưng phía sau Python thực hiện logic:

```python
user.get_full_name()
```

Đây chính là sức mạnh của `property`.

---

# 1. Vấn đề cần giải quyết

Giả sử có:

```python
class User:

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

Sử dụng:

```python
user = User("Nguyen", "An")

print(user.full_name())
```

Có một vấn đề về API:

```python
user.full_name()
```

Trong khi về mặt ý nghĩa, `full_name` là **một thuộc tính**, không phải một hành động.

Ta muốn:

```python
user.full_name
```

Đây là lúc `@property` xuất hiện.

---

# 2. `@property` cơ bản

```python
class User:

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

Sử dụng:

```python
user = User("Nguyen", "An")

print(user.full_name)
```

Kết quả:

```text
Nguyen An
```

Không cần:

```python
user.full_name()
```

---

# 3. Python thực sự làm gì?

Khi viết:

```python
@property
def full_name(self):
    ...
```

Python biến function thành một object `property`.

Có thể hình dung:

```python
full_name = property(full_name)
```

Do đó:

```python
user.full_name
```

không đơn giản là đọc một biến.

Python gọi logic getter bên trong `property`.

---

# 4. `property` là Descriptor

Đây là điểm rất quan trọng.

`property` là một **descriptor**.

Mô hình:

```text
user.full_name
       │
       ▼
property object
       │
       ▼
getter
       │
       ▼
return value
```

Đây là lý do `@property` liên quan trực tiếp đến **Descriptor Protocol** mà chúng ta đã nhắc ở buổi 13.

---

# 5. Getter

Getter là phần:

```python
@property
def full_name(self):
    return ...
```

Ví dụ:

```python
class Circle:

    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        return 3.14159 * self.radius ** 2
```

Sử dụng:

```python
circle = Circle(10)

print(circle.area)
```

Kết quả:

```text
314.159
```

`area` không được lưu trực tiếp trong object.

Nó được **tính toán khi truy cập**.

Đây gọi là:

> Computed Property

---

# 6. Property có thể đọc như attribute

```python
circle.area
```

nhưng thực chất:

```text
attribute access
       ↓
property descriptor
       ↓
getter
       ↓
calculation
```

Đây là abstraction rất mạnh.

---

# 7. Property với Validation

Đây là trường hợp sử dụng phổ biến nhất.

Không dùng property:

```python
class User:

    def __init__(self, age):
        self.age = age
```

Người dùng có thể làm:

```python
user.age = -100
```

Không hợp lệ.

Ta có thể dùng property.

```python
class User:

    def __init__(self, age):
        self.age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):

        if value < 0:
            raise ValueError(
                "Age cannot be negative"
            )

        self._age = value
```

---

# 8. `@property` + `@setter`

Cấu trúc:

```python
@property
def age(self):
    return self._age

@age.setter
def age(self, value):
    self._age = value
```

Điều quan trọng:

```python
@age.setter
```

không phải decorator độc lập.

Nó lấy object `property` đã tạo bởi:

```python
@property
```

và tạo ra một property mới có setter.

---

# 9. Đọc và ghi

```python
user = User(20)

print(user.age)
```

Python gọi:

```python
age.getter
```

---

Khi:

```python
user.age = 30
```

Python gọi:

```python
age.setter
```

---

# 10. Ví dụ hoàn chỉnh

```python
class User:

    def __init__(self, age):
        self.age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):

        if not isinstance(value, int):
            raise TypeError(
                "age must be int"
            )

        if value < 0:
            raise ValueError(
                "age must be >= 0"
            )

        self._age = value
```

Sử dụng:

```python
user = User(20)

print(user.age)

user.age = 30

print(user.age)
```

---

# 11. Setter bảo vệ invariant

Một khái niệm rất quan trọng trong OOP là:

> **Invariant**

Tức là điều kiện object luôn phải đảm bảo.

Ví dụ:

```text
age >= 0
```

Property giúp đảm bảo invariant:

```python
@age.setter
def age(self, value):

    if value < 0:
        raise ValueError

    self._age = value
```

Bất cứ nơi nào thay đổi `age` đều phải đi qua validation.

---

# 12. Property chỉ đọc

Nếu chỉ viết:

```python
@property
def username(self):
    return self._username
```

mà không có setter:

```python
@username.setter
```

thì:

```python
user.username = "Bob"
```

sẽ gây:

```text
AttributeError
```

Đây là:

> Read-only property

---

# 13. Ví dụ Read-only

```python
class Account:

    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance
```

Có thể:

```python
account = Account(1000)

print(account.balance)
```

Nhưng:

```python
account.balance = 5000
```

sẽ lỗi.

Điều này rất hữu ích với những giá trị không muốn cho code bên ngoài thay đổi trực tiếp.

---

# 14. `@deleter`

Property còn có:

```python
@x.deleter
```

Ví dụ:

```python
class User:

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        print("Deleting name")
        del self._name
```

Sử dụng:

```python
user = User("Alice")

del user.name
```

Python gọi:

```python
name.deleter
```

---

# 15. Ba thành phần

Một property có thể có:

```text
getter
setter
deleter
```

Mô hình:

```text
@property
    │
    ├── getter
    │
    ├── setter
    │
    └── deleter
```

Không bắt buộc phải có cả ba.

---

# 16. Ví dụ đầy đủ

```python
class Temperature:

    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):

        if value < -273.15:
            raise ValueError(
                "Temperature below absolute zero"
            )

        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32
```

Sử dụng:

```python
temperature = Temperature(25)

print(temperature.celsius)
print(temperature.fahrenheit)
```

Kết quả:

```text
25
77.0
```

`fahrenheit` là **computed property**.

---

# 17. Property và Encapsulation

Ví dụ:

```python
class BankAccount:

    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balance
```

Code bên ngoài:

```python
account.balance
```

có thể đọc.

Nhưng:

```python
account.balance = -1000
```

không được phép nếu không có setter.

Đây là một dạng **encapsulation**.

---

# 18. Property không nhất thiết cần `_name`

Một property có thể tính toán hoàn toàn:

```python
class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

    @property
    def perimeter(self):
        return 2 * (
            self.width + self.height
        )
```

Không có:

```python
self._area
```

vì `area` được tính động.

---

# 19. Property vs Method

### Method

```python
user.get_full_name()
```

Phù hợp khi đây là:

> hành động

### Property

```python
user.full_name
```

Phù hợp khi đây là:

> trạng thái / thuộc tính / giá trị

Ví dụ:

```python
user.is_active
user.full_name
user.age
order.total
cart.item_count
rectangle.area
```

rất phù hợp với property.

---

# 20. Không nên biến mọi method thành property

Không nên:

```python
user.send_email
```

nếu `send_email` thực hiện một hành động.

Nên:

```python
user.send_email()
```

Property phù hợp với **giá trị**, không phải **command/action**.

---

# 21. Lazy Property

Một ứng dụng nâng cao là tính toán khi cần.

```python
class Data:

    def __init__(self):
        self._result = None

    @property
    def result(self):

        if self._result is None:
            print("Calculating...")
            self._result = self.calculate()

        return self._result

    def calculate(self):
        return sum(range(1_000_000))
```

Lần đầu:

```python
data.result
```

sẽ tính.

Lần sau:

```python
data.result
```

sử dụng kết quả đã lưu.

---

# 22. `functools.cached_property`

Python có sẵn một công cụ cho pattern này:

```python
from functools import cached_property
```

Ví dụ:

```python
from functools import cached_property


class Data:

    @cached_property
    def result(self):
        print("Calculating...")
        return sum(range(1_000_000))
```

Sử dụng:

```python
data = Data()

print(data.result)
print(data.result)
```

`Calculating...` chỉ xuất hiện lần đầu.

---

# 23. `property` vs `cached_property`

|                  | `property`       | `cached_property`     |
| ---------------- | ---------------- | --------------------- |
| Tính toán        | Mỗi lần truy cập | Một lần               |
| Cache            | Không            | Có                    |
| Dữ liệu thay đổi | Luôn cập nhật    | Có thể bị stale       |
| Phù hợp          | Computed value   | Expensive computation |

---

# 24. Property và `__dict__`

Ví dụ:

```python
class User:

    def __init__(self, name):
        self.name = name

    @property
    def upper_name(self):
        return self.name.upper()
```

Sau:

```python
user = User("alice")
```

`__dict__`:

```python
print(user.__dict__)
```

Kết quả:

```python
{
    "name": "alice"
}
```

Không có:

```text
upper_name
```

vì nó không phải dữ liệu được lưu trong instance.

Nó được tính khi truy cập.

---

# 25. Property là một object

Ta có thể kiểm tra:

```python
class User:

    @property
    def name(self):
        return self._name
```

```python
print(User.__dict__["name"])
```

Kết quả đại loại:

```text
<property object>
```

Tức là:

```text
User.name
```

không phải function nữa.

Nó là:

```text
property object
```

---

# 26. `property()` không cần decorator

Cú pháp decorator:

```python
class User:

    @property
    def name(self):
        return self._name
```

Tương đương về ý tưởng:

```python
class User:

    def get_name(self):
        return self._name

    name = property(get_name)
```

---

# 27. Property với setter bằng cú pháp cổ điển

Có thể viết:

```python
class User:

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    name = property(
        get_name,
        set_name
    )
```

Nhưng cách hiện đại dễ đọc hơn:

```python
@property
def name(self):
    ...

@name.setter
def name(self, value):
    ...
```

---

# 28. Ví dụ Model chuyên nghiệp

Đây là pattern rất gần với những model bạn sẽ gặp trong ứng dụng thực tế:

```python
class User:

    def __init__(
        self,
        first_name,
        last_name,
        age
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

    @property
    def full_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )

    @property
    def is_adult(self):
        return self.age >= 18

    @property
    def display_name(self):
        return self.full_name.title()
```

Sử dụng:

```python
user = User(
    "nguyen",
    "an",
    20
)

print(user.full_name)
print(user.is_adult)
print(user.display_name)
```

Kết quả:

```text
nguyen an
True
Nguyen An
```

---

# 29. Property kết hợp Validation + Computed Property

```python
class Product:

    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):

        if value < 0:
            raise ValueError(
                "price must be >= 0"
            )

        self._price = value

    @property
    def total(self):
        return self.price * self.quantity
```

Sử dụng:

```python
product = Product(100, 5)

print(product.total)
```

Kết quả:

```text
500
```

Đây là pattern rất phổ biến trong domain model.

---

# 30. Một lỗi rất phổ biến

Không được viết:

```python
class User:

    @property
    def name(self):
        return self.name
```

Điều này tạo recursion:

```text
name
 ↓
self.name
 ↓
name
 ↓
self.name
 ↓
...
```

Cuối cùng:

```text
RecursionError
```

Phải dùng một attribute backing:

```python
return self._name
```

---

# 31. Setter cũng có lỗi tương tự

Sai:

```python
@name.setter
def name(self, value):
    self.name = value
```

Lại gọi setter:

```text
name.setter
   ↓
self.name
   ↓
name.setter
   ↓
...
```

Đúng:

```python
@name.setter
def name(self, value):
    self._name = value
```

---

# 32. Property và Invariant

Ví dụ tài khoản ngân hàng:

```python
class Account:

    def __init__(self, balance):
        self.balance = balance

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):

        if value < 0:
            raise ValueError(
                "Balance cannot be negative"
            )

        self._balance = value
```

Invariant:

```text
balance >= 0
```

Property là một "cổng" bảo vệ invariant.

---

# 33. Khi nào nên dùng `@property`?

Nên dùng khi:

### 1. Computed value

```python
user.full_name
```

### 2. Validation

```python
user.age = 20
```

### 3. Read-only attribute

```python
account.balance
```

### 4. Encapsulation

```python
object.value
```

nhưng bên trong:

```python
self._value
```

### 5. Giữ API ổn định

Ban đầu:

```python
user.name
```

sau này bạn có thể thêm validation mà code sử dụng bên ngoài vẫn giữ:

```python
user.name
```

Không cần đổi thành:

```python
user.get_name()
```

---

# 34. Một lợi ích thiết kế rất quan trọng

Ban đầu bạn có:

```python
class User:

    def __init__(self, age):
        self.age = age
```

Code bên ngoài:

```python
user.age
```

Sau này cần validation.

Bạn có thể chuyển thành:

```python
class User:

    def __init__(self, age):
        self.age = age

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError
        self._age = value
```

Code bên ngoài vẫn:

```python
user.age
```

Đây là một trong những lý do `property` rất quan trọng trong thiết kế API Python.

---

# 35. `property` và Decorator

Đây là điều bạn cần kết nối với toàn bộ khóa học Decorator:

```text
Decorator
    │
    ├── Function Decorator
    │
    ├── Class-based Decorator
    │
    ├── Class Decorator
    │
    └── property
            │
            ▼
        Descriptor
```

`@property` là một ví dụ rất đẹp cho việc decorator có thể thay đổi **vai trò của function**.

Ban đầu:

```python
def name(self):
    ...
```

Sau:

```python
@property
def name(self):
    ...
```

`name` trở thành một `property object`.

---

# 36. Ví dụ cuối — Model hoàn chỉnh

```python
from functools import cached_property


class Order:

    def __init__(self, items):

        self.items = items

    @property
    def item_count(self):
        return len(self.items)

    @property
    def subtotal(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self.items
        )

    @property
    def tax(self):
        return self.subtotal * 0.1

    @property
    def total(self):
        return self.subtotal + self.tax

    @cached_property
    def summary(self):
        print("Building summary...")

        return {
            "item_count": self.item_count,
            "subtotal": self.subtotal,
            "tax": self.tax,
            "total": self.total,
        }
```

Sử dụng:

```python
order = Order([
    {
        "price": 100,
        "quantity": 2,
    },
    {
        "price": 50,
        "quantity": 3,
    },
])

print(order.item_count)
print(order.subtotal)
print(order.tax)
print(order.total)

print(order.summary)
print(order.summary)
```

Bạn có thể thấy `Order` có một API rất tự nhiên:

```python
order.item_count
order.subtotal
order.tax
order.total
```

thay vì:

```python
order.get_item_count()
order.calculate_subtotal()
order.calculate_tax()
order.calculate_total()
```

---

# Bài tập

### Bài 1 — Temperature

Tạo class:

```python
class Temperature:
    ...
```

Có:

```python
temperature.celsius
temperature.fahrenheit
```

Yêu cầu:

* `celsius` có getter + setter.
* Không cho phép thấp hơn `-273.15`.
* `fahrenheit` là computed property.

---

### Bài 2 — BankAccount

Tạo:

```python
class BankAccount:
    ...
```

Có:

```python
account.balance
```

Yêu cầu:

* `balance` chỉ đọc.
* Có `deposit(amount)`.
* Có `withdraw(amount)`.
* Không cho phép balance âm.

---

### Bài 3 — Product

Tạo:

```python
class Product:
    ...
```

Có:

```python
product.price
product.quantity
product.subtotal
product.discount
product.total
```

Yêu cầu:

```text
subtotal = price × quantity
total = subtotal - discount
```

Validation:

```text
price >= 0
quantity >= 0
discount >= 0
discount <= subtotal
```

---

### Bài 4 — Lazy Property

Tạo class:

```python
class Data:
    ...
```

Có property:

```python
data.result
```

Yêu cầu:

* Lần đầu truy cập mới thực hiện phép tính nặng.
* Những lần sau sử dụng kết quả đã cache.
* Không sử dụng `functools.cached_property`; tự triển khai bằng `@property`.

---

# Tổng kết Phần III

Bạn đã hoàn thành:

| Buổi | Nội dung                   |
| ---- | -------------------------- |
| 11   | Class-based Decorator      |
| 12   | Decorator Factory nâng cao |
| 13   | Method Decorator           |
| 14   | Class Decorator            |
| 15   | Property Decorator         |

Đến đây bạn đã nắm được phần lớn các dạng decorator quan trọng trong Python.

**Bước tiếp theo nên chuyển sang Phần IV — Decorator thực chiến**, nơi chúng ta không chỉ học cú pháp mà bắt đầu xây dựng các decorator giống thư viện/framework thực tế: `retry`, `cache`, `authentication`, `authorization`, `logging`, `rate_limit`, `transaction`, `validation`, decorator async và decorator có type hint.
