# Buổi 4 — Metaclass & Model Registry Deep Dive

> Đây là một trong những buổi quan trọng nhất của toàn bộ series **Model Framework Deep Dive**. Sau buổi này bạn sẽ hiểu cách Python tạo class và cách Django ORM, SQLAlchemy, Pydantic... tự động thu thập các `Field`, xây dựng metadata và đăng ký (registry) toàn bộ model.

---

# Mục tiêu

Sau buổi này bạn sẽ xây dựng được:

```text
                    class Novel(Model)

                           │
                           ▼
                    ModelMeta.__new__()

                           │
         ┌─────────────────┼──────────────────┐
         ▼                 ▼                  ▼
    Thu thập Field    Kế thừa Field     Đăng ký Model
         │                 │                  │
         └─────────────────┼──────────────────┘
                           ▼
                     __fields__
                           │
                           ▼
                     Model Registry
                           │
                           ▼
             Repository / DatabaseManager
```

Đây chính là trái tim của mọi ORM.

---

# Phần 1. Python tạo class như thế nào?

Nhiều người nghĩ:

```python
class Novel(Model):
    title = StringField()
```

Python chỉ tạo class.

Thực tế:

```text
Đọc class body

↓

Tạo dictionary

↓

Gọi metaclass

↓

Sinh object class

↓

Novel được tạo
```

Class trong Python cũng là một object.

---

Ví dụ

```python
class User:
    pass


print(type(User))
```

Kết quả

```text
<class 'type'>
```

Điều đó có nghĩa:

```python
type
```

chính là metaclass mặc định.

---

# Class được tạo bằng type()

Ví dụ:

```python
User = type("User", (), {"name": "anonymous"})
```

Hoàn toàn tương đương:

```python
class User:
    name = "anonymous"
```

---

Kiểm tra

```python
print(User.name)
```

```text
anonymous
```

---

# Muốn can thiệp khi tạo class?

Không sửa được `type`.

Ta kế thừa nó.

```python
class ModelMeta(type):
    pass
```

Đây chính là metaclass.

---

# Metaclass được gọi khi nào?

Ví dụ

```python
class Model(metaclass=ModelMeta):
    pass
```

Sau đó

```python
class Novel(Model):
    pass
```

Python sẽ gọi:

```text
ModelMeta.__new__()
```

Tự động.

---

# Phần 2. **new** của Metaclass

Ví dụ

```python
class ModelMeta(type):
    def __new__(mcls, name, bases, namespace):

        print(name)

        return super().__new__(mcls, name, bases, namespace)
```

---

Tạo

```python
class Novel(Model):
    pass
```

Kết quả

```text
Novel
```

Metaclass chạy đúng lúc class được tạo.

---

# namespace là gì?

Giả sử

```python
class Novel(Model):
    title = StringField()

    author = StringField()
```

namespace chính là

```python
{"title": StringField(...), "author": StringField(...)}
```

Đây là nơi ta lấy toàn bộ Field.

---

# Phần 3. Thu thập Field

Ví dụ

```python
class ModelMeta(type):

    def __new__(...):

        fields = {}

        for key, value in namespace.items():

            if isinstance(value, Field):

                fields[key] = value
```

---

Sau đó

```python
cls = super().__new__(...)
```

---

Gắn vào class

```python
cls.__fields__ = fields
```

---

Kiểm tra

```python
print(Novel.__fields__)
```

↓

```text
{
    "title": ...,

    "author": ...
}
```

Không cần tự khai báo nữa.

---

# Phần 4. Kế thừa Field

Ví dụ

```python
class BaseEntity(Model):
    id = IntegerField()
```

---

```python
class Novel(BaseEntity):
    title = StringField()
```

Muốn

```text
Novel

↓

id

title
```

---

Metaclass

```python
fields = {}

for base in bases:
    if hasattr(base, "__fields__"):
        fields.update(base.__fields__)
```

Sau đó

```python
fields.update(current_fields)
```

---

Kết quả

```python
Novel.__fields__
```

↓

```text
id

title
```

---

# Override Field

Ví dụ

```python
class Base:
    name = StringField(max_length=50)
```

---

Con

```python
class User(Base):
    name = StringField(max_length=200)
```

---

Do:

```python
fields.update()
```

Field mới sẽ ghi đè field cũ.

Đây cũng là cách Django ORM hoạt động.

---

# Phần 5. Model Registry

Framework cần biết có những model nào.

Ví dụ

```text
Novel

Chapter

Author

Category
```

---

Tạo registry

```python
MODEL_REGISTRY = {}
```

---

Metaclass

```python
MODEL_REGISTRY[name] = cls
```

---

Kết quả

```python
print(MODEL_REGISTRY)
```

↓

```text
Novel

Chapter

Author
```

---

# Registry dùng để làm gì?

Ví dụ

```text
DatabaseManager

↓

Load tất cả model

↓

CREATE TABLE
```

Không cần import thủ công.

---

Hoặc

```text
Migration

↓

Registry

↓

Generate SQL
```

---

# Phần 6. Sinh Schema

Field

```python
title = StringField(max_length=200, nullable=False)
```

↓

Schema

```text
title

TEXT

NOT NULL
```

---

Field

```python
IntegerField()
```

↓

```text
INTEGER
```

---

Field

```python
BooleanField()
```

↓

```text
INTEGER
```

(SQLite không có kiểu BOOLEAN thực sự.)

---

Ví dụ

```python
for field in cls.__fields__.values():
    print(field.name)
```

↓

```text
id

title

author
```

---

# Field biết SQL Type

```python
class StringField(Field):
    sql_type = "TEXT"
```

---

```python
class IntegerField(Field):
    sql_type = "INTEGER"
```

---

Sinh schema

```python
for field in fields.values():
    print(field.sql_type)
```

↓

```text
TEXT

INTEGER
```

---

# Phần 7. Table Name

Thông thường

```python
class Novel(Model):
```

↓

```text
novel
```

---

Hoặc

```python
novel_info
```

---

Metaclass

```python
cls.__table_name__ = name.lower()
```

---

Có thể cho phép ghi đè

```python
class Novel(Model):
    __table_name__ = "novels"
```

---

Metaclass

```python
table = namespace.get("__table_name__", name.lower())
```

---

# Phần 8. Primary Key

Ví dụ

```python
id = IntegerField(primary_key=True)
```

---

Metaclass

```python
for field in fields.values():
    if field.primary_key:
        cls.__primary_key__ = field
```

---

Kiểm tra

```python
Novel.__primary_key__
```

↓

```text
id
```

---

# Phần 9. Index

Ví dụ

```python
title = StringField(index=True)
```

---

Metaclass

```python
indexes = []

for field in fields.values():
    if field.index:
        indexes.append(field)
```

---

Kết quả

```python
Novel.__indexes__
```

↓

```text
title

author
```

---

# Phần 10. Một ModelMeta hoàn chỉnh

```python
class ModelMeta(type):
    registry = {}

    def __new__(mcls, name, bases, namespace):

        fields = {}

        for base in bases:
            if hasattr(base, "__fields__"):
                fields.update(base.__fields__)

        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value

        cls = super().__new__(mcls, name, bases, namespace)

        cls.__fields__ = fields

        cls.__table_name__ = namespace.get("__table_name__", name.lower())

        ModelMeta.registry[name] = cls

        return cls
```

Đây là phiên bản mini của metaclass trong các ORM.

---

# Tại sao không dùng `__init_subclass__`?

Ở các buổi trước, chúng ta dùng:

```python
class Model:
    def __init_subclass__(cls): ...
```

Cách này đủ tốt cho các framework nhỏ.

So sánh:

| Tiêu chí                     | `__init_subclass__` | Metaclass |
| ---------------------------- | ------------------- | --------- |
| Dễ học                       | ✔                   | ✘         |
| Thu thập Field               | ✔                   | ✔         |
| Thay đổi quá trình tạo class | ✘                   | ✔         |
| Tạo registry                 | ✔                   | ✔         |
| ORM lớn sử dụng              | Ít                  | ✔         |
| Kiểm soát toàn bộ class      | ✘                   | ✔         |

Nếu bạn muốn xây dựng một framework ORM hoàn chỉnh, metaclass là lựa chọn mạnh mẽ hơn.

---

# Kiến trúc sau Buổi 4

```text
                 class Novel

                     │
                     ▼
              ModelMeta.__new__()
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   Collect       Inheritance   Registry
   Fields           Fields
        │            │
        └──────┬─────┘
               ▼
          __fields__
               │
        ┌──────┼─────────────┐
        ▼      ▼             ▼
  __table__  __pk__    __indexes__
               │
               ▼
        Repository Layer
               │
               ▼
          SQLite Builder
```

---

# Dự án Framework Cào Truyện

Sau buổi này, bạn đã có thể định nghĩa model như sau:

```python
class Novel(Model):
    id = IntegerField(primary_key=True)
    title = StringField(max_length=200, index=True)
    slug = StringField(max_length=200, unique=True)
    author = StringField(max_length=100)
```

Framework sẽ tự động biết:

* Bảng: `novel`
* Primary key: `id`
* Có 4 field
* `title` cần tạo index
* `slug` là unique
* Có thể sinh câu lệnh `CREATE TABLE` mà không cần viết SQL thủ công.

---

# Bài tập thực hành

## Bài 1

Viết `ModelMeta` tự động:

* Thu thập `Field`
* Gán vào `__fields__`

---

## Bài 2

Hỗ trợ kế thừa `Field` từ lớp cha và ghi đè field cùng tên ở lớp con.

---

## Bài 3

Tạo `ModelMeta.registry` và tự động đăng ký tất cả model (trừ `Model` cơ sở nếu muốn).

---

## Bài 4

Tự động tạo:

* `__table_name__`
* `__primary_key__`
* `__indexes__`

---

## Bài 5

Viết phương thức:

```python
Novel.describe()
```

In ra:

```text
Model: Novel
Table : novel

Fields:
-----------------------------------------
id         INTEGER   PK
title      TEXT      INDEX
slug       TEXT      UNIQUE
author     TEXT
```

Điều này sẽ giúp kiểm tra metadata trước khi sinh SQL.

---

# Buổi tiếp theo

**Buổi 5 — SQL Schema Builder Deep Dive**

Đây là buổi bắt đầu kết nối Model với SQLite. Chúng ta sẽ xây dựng một **Schema Builder** có khả năng tự động sinh SQL từ metadata của model, bao gồm:

* Chuyển `Field` → kiểu dữ liệu SQLite
* Sinh `CREATE TABLE`
* Sinh `PRIMARY KEY`
* Sinh `UNIQUE`
* Sinh `NOT NULL`
* Sinh `DEFAULT`
* Sinh `CREATE INDEX`
* Hỗ trợ `AUTOINCREMENT`
* Chuẩn bị nền tảng cho `DatabaseManager` và `Migration Engine`

Sau buổi này, framework của bạn sẽ có thể tạo toàn bộ cấu trúc cơ sở dữ liệu từ các model mà không cần viết SQL bằng tay.
