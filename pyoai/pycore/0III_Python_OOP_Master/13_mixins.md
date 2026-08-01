# Python OOP Master – Buổi 13

# Mixins – Thiết kế hành vi tái sử dụng trong Python

> **Mixins** là một trong những kỹ thuật được sử dụng rất nhiều trong Python. Hầu hết các framework lớn như **Django**, **Flask**, **SQLAlchemy**, **Pydantic**, **PySide6**, **FastAPI**... đều sử dụng Mixins để tái sử dụng hành vi mà không làm cây kế thừa trở nên phức tạp.

> Nếu Multiple Inheritance trả lời câu hỏi:
>
> **"Một class có thể kế thừa từ nhiều class không?"**
>
> thì Mixins trả lời câu hỏi:
>
> **"Làm thế nào để tái sử dụng một hành vi nhỏ một cách an toàn?"**

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu Mixins là gì.
* Phân biệt Mixins với Multiple Inheritance.
* Biết cách thiết kế Mixin đúng chuẩn Python.
* Hiểu Cooperative Multiple Inheritance.
* Biết cách dùng `super()` trong Mixins.
* Biết các lỗi thường gặp khi thiết kế Mixins.

---

# 1. Mixins là gì?

Mixin là:

> **Một class nhỏ chỉ bổ sung một hành vi (behavior), không đại diện cho một thực thể nghiệp vụ.**

Ví dụ

```text
SaveMixin

LoggerMixin

TimestampMixin

JsonMixin

CacheMixin
```

Đây **không phải object trong thế giới thực**.

Không ai nói:

```text
Một Logger là một User
```

Hay

```text
Một Json là một Product
```

Mixin chỉ thêm chức năng.

---

# 2. Ví dụ đầu tiên

```python
class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")


class User(LoggerMixin):
    def create(self):
        self.log("Create user")


user = User()

user.create()
```

Kết quả

```text
[LOG] Create user
```

---

# 3. Mixin không phải Base Class

Sai

```python
class Logger: ...
```

Đúng

```python
class LoggerMixin: ...
```

Theo quy ước Python:

```text
TênMixin
```

---

# 4. Mixin không nên đại diện Object

Sai

```text
AnimalMixin
```

Sai

```text
EmployeeMixin
```

Đúng

```text
JsonMixin
```

```text
SerializeMixin
```

```text
PrintableMixin
```

```text
CacheMixin
```

---

# 5. Ví dụ JsonMixin

```python
import json


class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__)
```

Sử dụng

```python
class User(JsonMixin):
    def __init__(self):

        self.name = "Alice"

        self.age = 20


user = User()

print(user.to_json())
```

Kết quả

```text
{"name": "Alice", "age": 20}
```

---

# 6. TimestampMixin

```python
from datetime import datetime


class TimestampMixin:
    def timestamp(self):
        return datetime.now()
```

```python
class Order(TimestampMixin):
    pass
```

```python
order = Order()

print(order.timestamp())
```

---

# 7. Logger + Json

Có thể kết hợp nhiều Mixin.

```python
class LoggerMixin:
    def log(self, msg):
        print(msg)


class JsonMixin:
    def to_json(self):
        return self.__dict__
```

```python
class User(LoggerMixin, JsonMixin):
    def __init__(self):

        self.name = "Bob"
```

```python
user = User()

user.log("Hello")

print(user.to_json())
```

---

# 8. Tại sao Mixins mạnh?

Nếu không dùng Mixins

```text
User

↓

LoggerUser

↓

JsonLoggerUser

↓

CacheJsonLoggerUser
```

Số class sẽ tăng theo cấp số nhân.

Mixins giúp tránh điều này.

---

# 9. Mixins và Multiple Inheritance

Multiple Inheritance

```text
A

↓

B
```

là

```text
IS-A
```

Mixin

```text
LoggerMixin
```

là

```text
HAS-BEHAVIOR
```

Nó chỉ thêm khả năng.

---

# 10. Cooperative Multiple Inheritance

Mixin nên hỗ trợ

```python
super()
```

Ví dụ

```python
class LoggerMixin:
    def save(self):

        print("Logging")

        super().save()
```

---

# 11. Ví dụ

```python
class SaveMixin:
    def save(self):

        print("Saving")

        super().save()
```

```python
class ValidateMixin:
    def save(self):

        print("Validate")

        super().save()
```

```python
class Base:
    def save(self):

        print("Database")
```

```python
class User(LoggerMixin, ValidateMixin, Base):
    pass
```

Kết quả

```python
user = User()

user.save()
```

```text
Logging
Validate
Database
```

---

# 12. Kiểm tra MRO

```python
print(User.mro())
```

Ví dụ

```text
[
 User,
 LoggerMixin,
 ValidateMixin,
 Base,
 object
]
```

---

# 13. Ví dụ hoàn chỉnh

```python
class LoggerMixin:
    def process(self):

        print("Logger")

        super().process()


class CacheMixin:
    def process(self):

        print("Cache")

        super().process()


class ValidationMixin:
    def process(self):

        print("Validation")

        super().process()


class Service:
    def process(self):

        print("Service")


class UserService(LoggerMixin, CacheMixin, ValidationMixin, Service):
    pass


service = UserService()

service.process()
```

Kết quả

```text
Logger
Cache
Validation
Service
```

---

# 14. Mixin không nên có constructor phức tạp

Không nên

```python
class LoggerMixin:
    def __init__(self):

        self.filename = "log.txt"
```

Vì sẽ dễ gây xung đột với các class khác.

Nếu cần constructor:

```python
class LoggerMixin:
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.logs = []
```

Đây là cách viết **cooperative constructor**.

---

# 15. Mixin nên độc lập

Sai

```python
class LoggerMixin:
    def log(self):

        print(self.database.connection)
```

Mixin đang phụ thuộc vào cấu trúc cụ thể của class khác.

Đúng

```python
class LoggerMixin:
    def log(self, message):

        print(message)
```

Mixin nên có ít phụ thuộc nhất có thể.

---

# 16. Mixins trong Django

Ví dụ:

```python
class LoginRequiredMixin: ...
```

```python
class PermissionRequiredMixin: ...
```

```python
class FormMixin: ...
```

```python
class TemplateResponseMixin: ...
```

Có thể kết hợp:

```python
class UserView(
    LoginRequiredMixin, PermissionRequiredMixin, TemplateResponseMixin, View
): ...
```

Mỗi Mixin thêm một khả năng riêng.

---

# 17. Mixins trong SQLAlchemy

```python
class TimestampMixin:
    created_at = ...

    updated_at = ...
```

```python
class User(TimestampMixin, Base): ...
```

Mọi model đều có:

```text
created_at
updated_at
```

mà không cần lặp lại mã.

---

# 18. Ví dụ thực tế

```python
import json
from datetime import datetime


class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__)


class TimestampMixin:
    def created_time(self):
        return datetime.now()


class LoggerMixin:
    def log(self, message):
        print(f"[LOG] {message}")


class User(JsonMixin, TimestampMixin, LoggerMixin):
    def __init__(self):

        self.name = "Alice"

        self.age = 25


user = User()

user.log("Created")

print(user.created_time())

print(user.to_json())
```

---

# 19. Khi nào nên dùng Mixin?

Rất phù hợp cho:

* Logging
* Cache
* Serialize
* Export CSV
* Export JSON
* Timestamp
* Audit
* Permission
* Validation
* Retry
* Pagination

Những chức năng này có thể tái sử dụng ở nhiều class.

---

# 20. Khi nào không nên dùng Mixin?

Không nên dùng Mixin cho:

* `User`
* `Animal`
* `Employee`
* `Car`

Đây là các thực thể nghiệp vụ, không phải hành vi.

---

# 21. Mixin vs Composition

## Mixin

```python
class User(LoggerMixin): ...
```

Hành vi được thêm thông qua kế thừa.

## Composition

```python
class User:
    def __init__(self):

        self.logger = Logger()
```

Hành vi được thêm thông qua một đối tượng thành viên.

### So sánh

| Tiêu chí                              | Mixin | Composition |
| ------------------------------------- | ----- | ----------- |
| Thêm hành vi qua kế thừa              | ✅     | ❌           |
| Có thể thay thế đối tượng lúc chạy    | ❌     | ✅           |
| Tái sử dụng code                      | ✅     | ✅           |
| Phụ thuộc MRO                         | ✅     | ❌           |
| Linh hoạt khi thay đổi implementation | ❌     | ✅           |

Trong nhiều hệ thống lớn, **Composition thường được ưu tiên hơn** khi hành vi có thể thay đổi trong quá trình chạy.

---

# Best Practices

✅ Mỗi Mixin chỉ nên có **một trách nhiệm**.

✅ Đặt tên theo quy ước:

```text
*Mixin
```

✅ Nếu ghi đè phương thức, hãy gọi:

```python
super().method()
```

để hỗ trợ Cooperative Multiple Inheritance.

✅ Nếu có `__init__()`, hãy viết:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
```

---

# Những lỗi người mới thường gặp

## Lỗi 1: Mixin quá lớn

Sai

```python
class EverythingMixin:
```

Chứa:

* Logging
* Cache
* Validate
* Database
* Export

Mixin nên nhỏ và tập trung.

---

## Lỗi 2: Không gọi `super()`

```python
class LoggerMixin:
    def save(self):

        print("Log")
```

Nếu quên:

```python
super().save()
```

chuỗi MRO sẽ bị cắt.

---

## Lỗi 3: Mixin phụ thuộc vào class cụ thể

Ví dụ:

```python
self.database.cursor.execute(...)
```

Mixin sẽ không còn tái sử dụng được.

---

# Bài tập

## Bài 1

Viết `LoggerMixin`:

```python
class LoggerMixin:
    def log(self, message): ...
```

Áp dụng cho:

```python
class User(LoggerMixin): ...
```

---

## Bài 2

Viết `JsonMixin` có:

```python
to_json()
```

Trả về chuỗi JSON từ `self.__dict__`.

---

## Bài 3

Viết:

* `LoggerMixin`
* `CacheMixin`
* `ValidationMixin`

Mỗi class có:

```python
process()
```

gọi `super().process()`.

Sau đó tạo:

```python
class Service(LoggerMixin, CacheMixin, ValidationMixin, BaseService): ...
```

Quan sát MRO và thứ tự thực thi.

---

## Bài 4

Viết `TimestampMixin`:

* `created_at()`
* `updated_at()`

Áp dụng cho:

* `User`
* `Product`
* `Order`

Không lặp lại mã.

---

## Bài 5 (Nâng cao)

Xây dựng hệ thống:

```text
Repository
```

Kết hợp các Mixins:

* `LoggerMixin`
* `RetryMixin`
* `CacheMixin`
* `ValidationMixin`

Mỗi Mixin ghi đè:

```python
save()
```

và gọi `super().save()`.

In `Repository.mro()` và giải thích thứ tự thực thi.

---

# Tóm tắt buổi học

* **Mixin** là một lớp nhỏ dùng để bổ sung **một hành vi** cho nhiều class khác nhau.
* Mixins khác với Multiple Inheritance thông thường ở chỗ chúng **không đại diện cho thực thể nghiệp vụ**, mà chỉ cung cấp chức năng tái sử dụng.
* Khi kết hợp nhiều Mixins, cần tuân theo **Cooperative Multiple Inheritance** bằng cách sử dụng `super()`.
* Mỗi Mixin nên có **một trách nhiệm duy nhất**, ít phụ thuộc và dễ tái sử dụng.
* Mixins được sử dụng rất phổ biến trong các framework Python hiện đại như Django, SQLAlchemy và nhiều thư viện khác.

> **Buổi 14** chúng ta sẽ bắt đầu **Phần IV – Đa hình (Polymorphism)**, tìm hiểu cách Python thực hiện đa hình thông qua **Dynamic Dispatch**, cách viết mã mở rộng mà không cần `if/elif`, và xây dựng các hệ thống linh hoạt theo nguyên tắc **"program to an interface, not an implementation"**.
