# Python OOP Master – Buổi 22

# `@classmethod` – Phương thức lớp và Alternative Constructor

> Đây là một trong những tính năng OOP được sử dụng rất nhiều trong thư viện chuẩn của Python.
>
> Nếu bạn từng thấy:
>
> ```python
> datetime.fromtimestamp(...)
> pathlib.Path.cwd()
> dict.fromkeys(...)
> ```
>
> thì bạn đã sử dụng **Class Method**.

---

# Mục tiêu

Sau buổi học này bạn sẽ:

* Hiểu `@classmethod` là gì.
* Hiểu tham số `cls`.
* Phân biệt `self`, `cls` và `staticmethod`.
* Biết Alternative Constructor là gì.
* Hiểu vì sao Factory Pattern dựa trên `@classmethod`.
* Áp dụng vào framework cào truyện.

---

# 1. Ôn lại ba loại Method

| Loại            | Tham số đầu tiên | Đại diện                         |
| --------------- | ---------------- | -------------------------------- |
| Instance Method | `self`           | Object hiện tại                  |
| Class Method    | `cls`            | Chính class                      |
| Static Method   | Không có         | Không phụ thuộc object hay class |

Ví dụ

```python
class Demo:
    def instance(self): ...

    @classmethod
    def from_data(cls): ...

    @staticmethod
    def helper(): ...
```

---

# 2. Class Method là gì?

Instance Method

```python
user.save()
```

↓

Python gọi

```python
User.save(user)
```

---

Class Method

```python
User.create()
```

↓

Python gọi

```python
User.create(User)
```

Tham số đầu tiên là

```python
cls
```

chính là class.

---

# 3. Ví dụ đầu tiên

```python
class User:
    count = 0

    @classmethod
    def show_count(cls):

        print(cls.count)
```

```python
User.show_count()
```

↓

```text
0
```

---

# 4. `cls` là gì?

Ví dụ

```python
class User:
    @classmethod
    def info(cls):

        print(cls)
```

↓

```python
User.info()
```

Kết quả

```text
<class '__main__.User'>
```

`cls`

↓

là

```python
User
```

---

# 5. Thay đổi thuộc tính class

```python
class User:
    count = 0

    @classmethod
    def increase(cls):

        cls.count += 1
```

```python
User.increase()

User.increase()

print(User.count)
```

↓

```text
2
```

---

# 6. Alternative Constructor

Đây là ứng dụng quan trọng nhất.

Ví dụ

```python
class User:
    def __init__(self, name, age):

        self.name = name

        self.age = age
```

Thông thường

```python
user = User("Alice", 20)
```

Nhưng nếu dữ liệu đến từ

```text
Alice,20
```

thì sao?

---

# 7. `from_string()`

```python
class User:
    def __init__(self, name, age):

        self.name = name

        self.age = age

    @classmethod
    def from_string(cls, text):

        name, age = text.split(",")

        return cls(name, int(age))
```

Sử dụng

```python
user = User.from_string("Alice,20")

print(user.name)

print(user.age)
```

↓

```text
Alice

20
```

---

# 8. Vì sao dùng `cls()` thay vì `User()`?

Sai

```python
return User(...)
```

Đúng

```python
return cls(...)
```

Lý do?

↓

Hỗ trợ kế thừa.

---

# 9. Ví dụ kế thừa

```python
class User:
    def __init__(self, name):
        self.name = name

    @classmethod
    def create(cls):

        return cls("Unknown")
```

```python
class Admin(User):
    pass
```

```python
admin = Admin.create()

print(type(admin))
```

↓

```text
<class '__main__.Admin'>
```

Nếu dùng

```python
return User(...)
```

↓

sẽ tạo

```text
User
```

không phải

```text
Admin
```

---

# 10. Ví dụ JSON

```python
import json


class Book:
    def __init__(self, title, price):

        self.title = title

        self.price = price

    @classmethod
    def from_json(cls, text):

        data = json.loads(text)

        return cls(**data)
```

```python
book = Book.from_json('{"title":"Python","price":50}')
```

---

# 11. Ví dụ Dictionary

```python
class Book:
    def __init__(self, title, price):

        self.title = title

        self.price = price

    @classmethod
    def from_dict(cls, data):

        return cls(**data)
```

---

# 12. Ví dụ File

```python
class Config:
    def __init__(self, host, port):

        self.host = host

        self.port = port

    @classmethod
    def from_file(cls, filename):

        with open(filename) as f:
            host = f.readline().strip()

            port = int(f.readline())

        return cls(host, port)
```

---

# 13. Ví dụ trong framework cào truyện

```python
class Chapter:
    def __init__(self, id, title):

        self.id = id

        self.title = title

    @classmethod
    def from_row(cls, row):

        return cls(row["id"], row["title"])
```

Repository

```python
chapter = Chapter.from_row(row)
```

Thay vì

```python
chapter = Chapter(row["id"], row["title"])
```

Mã nguồn rõ ràng và dễ bảo trì hơn.

---

# 14. Ví dụ `sqlite3`

```python
class Book:
    @classmethod
    def from_sqlite(cls, row):

        return cls(row["id"], row["title"], row["author"])
```

Repository

```python
cursor.execute(...)

row = cursor.fetchone()

book = Book.from_sqlite(row)
```

Đây là cách rất phổ biến trong ORM và Repository Pattern.

---

# 15. Ví dụ Path

```python
from pathlib import Path

path = Path.cwd()
```

`cwd()`

↓

chính là một **Class Method**.

Nó tạo object từ một nguồn dữ liệu đặc biệt (thư mục hiện tại).

---

# 16. Ví dụ `dict.fromkeys()`

```python
d = dict.fromkeys(["a", "b", "c"], 0)

print(d)
```

↓

```text
{
    "a":0,
    "b":0,
    "c":0
}
```

`fromkeys()`

↓

là **Class Method**.

---

# 17. Ví dụ hoàn chỉnh

```python
class User:
    def __init__(self, name, age):

        self.name = name

        self.age = age

    @classmethod
    def from_string(cls, text):

        name, age = text.split(",")

        return cls(name, int(age))

    def __repr__(self):

        return f"User({self.name}, {self.age})"


u = User.from_string("Alice,20")

print(u)
```

↓

```text
User(Alice,20)
```

---

# 18. So sánh ba loại Method

```python
class Demo:
    value = 10

    def instance(self):

        return self.value

    @classmethod
    def cls_method(cls):

        return cls.value

    @staticmethod
    def static():

        return 100
```

| Method   | `self` | `cls` | Tạo object     | Truy cập class |
| -------- | ------ | ----- | -------------- | -------------- |
| Instance | ✅      | ❌     | ❌              | ✅              |
| Class    | ❌      | ✅     | ✅ (`cls(...)`) | ✅              |
| Static   | ❌      | ❌     | ❌              | Không tự động  |

---

# 19. Khi nào dùng Class Method?

Rất phù hợp cho:

* Alternative Constructor
* Factory Method
* Load từ file
* Load từ JSON
* Load từ Database
* Load từ API
* Parse HTML
* Parse XML

Ví dụ

```python
Book.from_json()

Book.from_dict()

Book.from_sqlite()

Book.from_api()
```

---

# 20. Best Practices

✅ Dùng `cls(...)` thay vì ghi cứng tên lớp:

```python
return cls(...)
```

Điều này giúp code hoạt động đúng khi kế thừa.

---

✅ Đặt tên rõ ràng cho các alternative constructor:

```python
from_json()

from_dict()

from_row()

from_sqlite()

from_api()

from_string()
```

---

✅ Không dùng `@classmethod` nếu phương thức chỉ thao tác với dữ liệu của một object cụ thể. Khi đó hãy dùng instance method.

---

# Những lỗi người mới thường gặp

## Lỗi 1

Ghi cứng tên class

Sai

```python
return User(...)
```

Đúng

```python
return cls(...)
```

---

## Lỗi 2

Nhầm lẫn giữa `@staticmethod` và `@classmethod`

Ví dụ:

```python
@staticmethod
def from_json():
```

Nếu cần tạo object bằng `cls(...)`, đây phải là `@classmethod`.

---

## Lỗi 3

Lạm dụng `@classmethod`

Không phải mọi phương thức đều nên là class method.

Ví dụ:

```python
user.rename("Bob")
```

Đây là hành vi của một object cụ thể ⇒ dùng instance method.

---

## Lỗi 4

Đặt tên constructor không rõ ràng

Kém:

```python
create()

build()

new()
```

Tốt hơn:

```python
from_json()

from_file()

from_row()

from_dict()
```

Tên phương thức nên mô tả **nguồn dữ liệu**.

---

# Bài tập

## Bài 1

Viết class `Student`:

* `__init__(name, age)`
* `from_string("Alice,20")`

---

## Bài 2

Viết class `Book`:

* `from_dict()`
* `from_json()`

---

## Bài 3

Viết class `CrawlerConfig`:

* `from_file()`
* `from_dict()`

---

## Bài 4

Trong framework cào truyện, thiết kế class `Chapter`:

Yêu cầu:

* `from_row(row)`
* `from_dict(data)`
* `from_json(text)`

Mỗi phương thức đều trả về một đối tượng `Chapter`.

---

## Bài 5 (Nâng cao)

Thiết kế class `DatabaseConnection`:

```python
conn = DatabaseConnection.from_config(config)

conn = DatabaseConnection.from_file("db.ini")

conn = DatabaseConnection.from_env()
```

Mỗi phương thức là một **alternative constructor**, chuẩn bị cho việc xây dựng `DatabaseManager` và **Factory Pattern** ở buổi sau.

---

# Tổng kết buổi học

* `@classmethod` nhận tham số đầu tiên là `cls`, đại diện cho chính lớp đang được gọi.
* Ứng dụng quan trọng nhất của `@classmethod` là xây dựng **Alternative Constructor**, cho phép tạo object từ nhiều nguồn dữ liệu như chuỗi, `dict`, JSON, file, cơ sở dữ liệu hay API.
* Luôn sử dụng `cls(...)` thay vì ghi cứng tên lớp để hỗ trợ kế thừa và mở rộng.
* `@classmethod` là nền tảng cho nhiều kỹ thuật thiết kế hướng đối tượng, đặc biệt là **Factory Method** và các ORM.

> **Buổi 23** chúng ta sẽ học **Factory Pattern**. Bạn sẽ kết hợp `@classmethod`, tính đa hình (Polymorphism) và OOP để xây dựng các đối tượng theo cấu hình hoặc kiểu dữ liệu đầu vào. Đây là mẫu thiết kế được sử dụng rất nhiều trong SQLAlchemy, Requests, logging, `pathlib`, cũng như trong hệ thống plugin của framework cào truyện mà bạn đang xây dựng.
