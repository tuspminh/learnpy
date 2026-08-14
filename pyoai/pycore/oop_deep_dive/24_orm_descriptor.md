# OOP Deep Dive — Buổi 24

# ORM sử dụng Descriptor

Hôm nay chúng ta đi vào một ứng dụng cực kỳ thực tế của Descriptor:

> **ORM — Object Relational Mapping**

Đặc biệt, chúng ta sẽ **tự xây một Mini ORM bằng Python thuần**, chưa dùng SQLAlchemy hay Django ORM.

Mục tiêu cuối buổi:

```python
class User:

    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

sau đó có thể:

```python
user = User()

user.name = "Alice"
user.age = 25

print(user.name)
```

và hiểu chính xác:

```text
user.name
    ↓
StringField.__get__()
    ↓
instance.__dict__
```

cũng như:

```text
user.name = "Alice"
    ↓
StringField.__set__()
    ↓
validation
    ↓
instance.__dict__
```

Đây chính là cách nhiều ORM hiện đại xây dựng API kiểu:

```python
user.name
```

nhưng phía dưới lại có rất nhiều logic.

---

# 1. ORM là gì?

ORM viết tắt:

```text
Object Relational Mapping
```

Có hai thế giới:

### Python

```python
class User:

    id: int
    name: str
    age: int
```

### Database

```sql
CREATE TABLE users (
    id INTEGER,
    name TEXT,
    age INTEGER
);
```

ORM làm nhiệm vụ ánh xạ:

```text
Python Object          Database
─────────────────────────────────
User                   users
id                     id
name                   name
age                    age
```

---

# 2. Vấn đề nếu không có ORM

Không có ORM, bạn có thể phải viết:

```python
user = User()

row = cursor.execute(
    "SELECT id, name, age FROM users"
).fetchone()

user.id = row[0]
user.name = row[1]
user.age = row[2]
```

Rất nhiều boilerplate.

ORM muốn bạn viết:

```python
user = User.get(1)

print(user.name)
```

---

# 3. Descriptor xuất hiện ở đâu?

Hãy nhìn:

```python
class User:

    name = StringField()
```

`StringField` có thể là Descriptor.

Khi:

```python
user.name
```

Python không nhất thiết lấy:

```python
user.__dict__["name"]
```

mà có thể gọi:

```python
StringField.__get__()
```

---

# 4. Tư duy quan trọng

Một ORM Field có thể làm nhiều việc:

```text
name = StringField()
      │
      ├── lưu metadata
      ├── validation
      ├── conversion
      ├── đọc dữ liệu
      ├── ghi dữ liệu
      └── mapping database column
```

Vì vậy Descriptor cực kỳ phù hợp.

---

# 5. ORM Field đầu tiên

Ta bắt đầu rất đơn giản:

```python
class Field:

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
```

Nhưng có vấn đề:

```python
self.name
```

chưa tồn tại.

---

# 6. `__set_name__`

Đây là lúc kiến thức Descriptor của Buổi 21 phát huy tác dụng.

Python cho Descriptor biết tên attribute:

```python
def __set_name__(self, owner, name):
    self.name = name
```

Hoàn chỉnh:

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
```

---

# 7. Sử dụng

```python
class User:

    name = Field()
    age = Field()
```

Python sẽ gọi:

```text
name = Field()
     ↓
__set_name__(User, "name")

age = Field()
    ↓
__set_name__(User, "age")
```

Do đó:

```python
User.name.name
```

sẽ là:

```text
"name"
```

và:

```python
User.age.name
```

là:

```text
"age"
```

---

# 8. Kiểm tra

```python
print(User.__dict__["name"].name)
```

Kết quả:

```text
name
```

---

# 9. `instance is None`

Khi:

```python
User.name
```

Python gọi Descriptor với:

```python
instance = None
```

Ta trả về chính Field:

```python
if instance is None:
    return self
```

Điều này rất quan trọng cho ORM.

Bởi vì:

```python
User.name
```

có thể được dùng để lấy metadata.

---

# 10. Instance Access

Khi:

```python
user = User()
```

và:

```python
user.name
```

Descriptor nhận:

```text
instance = user
owner = User
```

rồi:

```python
return instance.__dict__[self.name]
```

---

# 11. Instance Assignment

Khi:

```python
user.name = "Alice"
```

Python gọi:

```python
Field.__set__(
    user,
    "Alice"
)
```

sau đó:

```python
user.__dict__["name"] = "Alice"
```

---

# 12. ORM Field hoàn chỉnh đầu tiên

```python
class Field:

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
```

Dùng:

```python
class User:

    name = Field()
    age = Field()
```

---

# 13. Test

```python
user = User()

user.name = "Alice"
user.age = 25

print(user.name)
print(user.age)
```

Kết quả:

```text
Alice
25
```

---

# 14. Nhưng đây chưa phải ORM

Đây mới là:

```text
Descriptor-based field
```

Để thành ORM, Field cần biết:

```text
Python type
Database type
Column name
Validation
Default value
Nullable
Primary key
```

---

# 15. Tạo `StringField`

```python
class StringField(Field):

    def __set__(self, instance, value):

        if not isinstance(value, str):
            raise TypeError(
                f"{self.name} must be str"
            )

        super().__set__(instance, value)
```

---

# 16. `IntegerField`

```python
class IntegerField(Field):

    def __set__(self, instance, value):

        if not isinstance(value, int):
            raise TypeError(
                f"{self.name} must be int"
            )

        super().__set__(instance, value)
```

---

# 17. Model

```python
class User:

    name = StringField()
    age = IntegerField()
```

Bây giờ:

```python
user = User()

user.name = "Alice"
user.age = 25
```

hoạt động.

Nhưng:

```python
user.age = "25"
```

sẽ:

```text
TypeError
```

---

# 18. Đây là ORM-like behavior

Chúng ta vừa đạt được:

```python
user.age = 25
```

nhưng phía dưới:

```text
IntegerField.__set__()
      ↓
validate
      ↓
instance.__dict__
```

API rất đơn giản nhưng behavior phức tạp.

Đây chính là sức mạnh của Descriptor.

---

# 19. Thêm Database Column

Ta muốn:

```python
class User:

    name = StringField(column="user_name")
```

Nhưng Python attribute là:

```text
name
```

Database column là:

```text
user_name
```

Field cần lưu cả hai.

---

# 20. Field metadata

```python
class Field:

    def __init__(self, column=None):
        self.column = column

    def __set_name__(self, owner, name):
        self.name = name

        if self.column is None:
            self.column = name
```

---

# 21. Sử dụng

```python
class User:

    name = StringField(
        column="user_name"
    )
```

Bây giờ:

```python
User.name.name
```

→

```text
name
```

Còn:

```python
User.name.column
```

→

```text
user_name
```

---

# 22. Đây là metadata

Ta có:

```text
Field
├── name
├── column
└── type
```

ORM có thể dùng metadata này để sinh SQL.

---

# 23. Thêm `python_type`

```python
class Field:

    python_type = object
```

Sau đó:

```python
class StringField(Field):

    python_type = str
```

và:

```python
class IntegerField(Field):

    python_type = int
```

---

# 24. Generic Validation

Ta có thể đưa validation vào Field cha:

```python
class Field:

    python_type = object

    def __init__(self, column=None):
        self.column = column

    def __set_name__(self, owner, name):
        self.name = name

        if self.column is None:
            self.column = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__[self.name]

    def __set__(self, instance, value):

        if not isinstance(
            value,
            self.python_type
        ):
            raise TypeError(
                f"{self.name} "
                f"must be "
                f"{self.python_type.__name__}"
            )

        instance.__dict__[self.name] = value
```

---

# 25. Field con

```python
class StringField(Field):
    python_type = str


class IntegerField(Field):
    python_type = int
```

---

# 26. Model

```python
class User:

    name = StringField()
    age = IntegerField()
```

Test:

```python
user = User()

user.name = "Alice"
user.age = 25
```

OK.

Nhưng:

```python
user.age = "25"
```

→ `TypeError`.

---

# 27. Đây chính là một phần ORM

ORM thường cần:

```text
Field
 ↓
metadata
 ↓
validation
 ↓
conversion
 ↓
SQL mapping
```

Descriptor là lớp nằm giữa:

```text
Python Object
      ↕
 Descriptor
      ↕
 ORM Model
      ↕
 Database
```

---

# 28. Một vấn đề: `__dict__`

Hiện tại ta lưu:

```python
instance.__dict__[self.name]
```

Ví dụ:

```python
user.__dict__
```

sẽ là:

```python
{
    "name": "Alice",
    "age": 25
}
```

Điều này tốt.

Descriptor chịu trách nhiệm behavior, còn instance giữ state.

---

# 29. Tại sao không lưu dữ liệu trong Field?

Sai lầm:

```python
class BadField:

    def __set__(self, instance, value):
        self.value = value
```

Vì:

```python
user1.name = "Alice"
user2.name = "Bob"
```

cả hai instance dùng chung:

```python
User.name
```

Field object.

Kết quả sẽ bị ghi đè.

---

# 30. Descriptor là class-level

Đây là insight cực kỳ quan trọng:

```text
User
 │
 └── name
      ↓
   StringField
```

Chỉ có **một Field object**.

Nhưng:

```text
user1
user2
user3
```

có state riêng.

Do đó Field phải lưu:

```text
metadata
```

chứ không lưu:

```text
instance state
```

---

# 31. Kiến trúc đúng

```text
                 User.name
                    │
                    ▼
              StringField
              ┌──────────┐
              │ metadata │
              │ name     │
              │ column   │
              │ type     │
              └──────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
      user1                   user2
   __dict__                 __dict__
      │                       │
 name=Alice                 name=Bob
```

---

# 32. Đây là nguyên tắc cực kỳ quan trọng

> **Descriptor nên giữ metadata, instance nên giữ state.**

Đây là một nguyên tắc thiết kế rất quan trọng khi tự xây framework.

---

# 33. Thêm `ModelMeta`

Bây giờ chúng ta muốn:

```python
class User:
    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

Framework tự động biết:

```text
id
name
age
```

Ta có thể sử dụng metaclass.

```python
class ModelMeta(type):

    def __new__(
        cls,
        name,
        bases,
        namespace
    ):
        fields = {}

        for key, value in namespace.items():

            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields

        return super().__new__(
            cls,
            name,
            bases,
            namespace
        )
```

---

# 34. Model Base

```python
class Model(
    metaclass=ModelMeta
):
    pass
```

Sau đó:

```python
class User(Model):

    id = IntegerField()
    name = StringField()
    age = IntegerField()
```

---

# 35. Kiểm tra

```python
print(User._fields)
```

Có thể nhận:

```text
{
    "id": <IntegerField ...>,
    "name": <StringField ...>,
    "age": <IntegerField ...>
}
```

---

# 36. Bây giờ Framework đã biết Model Schema

```text
User
 │
 ├── id
 │    └── IntegerField
 │
 ├── name
 │    └── StringField
 │
 └── age
      └── IntegerField
```

Đây là bước đầu tiên của ORM.

---

# 37. Sinh SQL

Ta có thể viết:

```python
def create_table_sql(model):

    columns = []

    for name, field in model._fields.items():

        sql_type = {
            int: "INTEGER",
            str: "TEXT",
        }[field.python_type]

        columns.append(
            f"{field.column} {sql_type}"
        )

    return (
        f"CREATE TABLE "
        f"{model.__name__.lower()} "
        f"({', '.join(columns)})"
    )
```

---

# 38. Test

```python
print(create_table_sql(User))
```

Có thể tạo:

```sql
CREATE TABLE user (
    id INTEGER,
    name TEXT,
    age INTEGER
)
```

Ta vừa bắt đầu biến:

```python
class User(...)
```

thành:

```sql
CREATE TABLE ...
```

---

# 39. Đây là Object → Relational Mapping

```text
Python
────────────────
User
id
name
age
        │
        │ ORM
        ▼
SQL
────────────────
user
id INTEGER
name TEXT
age INTEGER
```

---

# 40. Thêm `table_name`

Ta không nên lấy trực tiếp:

```python
model.__name__.lower()
```

Ta có:

```python
class ModelMeta(type):

    def __new__(
        cls,
        name,
        bases,
        namespace
    ):
        fields = {}

        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields
        namespace["_table"] = name.lower()

        return super().__new__(
            cls,
            name,
            bases,
            namespace
        )
```

Sau đó:

```python
class User(Model):
    ...
```

có:

```python
User._table
```

→

```text
user
```

---

# 41. Nhưng ORM thật còn phức tạp hơn

ORM cần xử lý:

```text
Field
Type
Nullable
Default
Primary Key
Foreign Key
Index
Unique
Relationship
Lazy Loading
Query
Transaction
Identity Map
Unit of Work
```

Nhưng tất cả có thể bắt đầu từ:

```text
Descriptor
```

---

# 42. Descriptor + Lazy Loading

Một ứng dụng rất mạnh:

```python
class User:

    @property
    def posts(self):
        return load_posts(self.id)
```

Nhưng ORM có thể biến:

```python
user.posts
```

thành:

```text
Relationship Descriptor
        ↓
check cache
        ↓
query database
        ↓
load Posts
        ↓
cache
        ↓
return
```

Người dùng chỉ thấy:

```python
user.posts
```

---

# 43. Đây là lý do ORM trông như magic

Bạn viết:

```python
user.name
```

nhưng framework có thể:

```text
attribute lookup
      ↓
descriptor
      ↓
field
      ↓
type conversion
      ↓
validation
      ↓
database state
```

API bên ngoài cực kỳ đơn giản.

Implementation bên trong rất phức tạp.

---

# 44. Một ORM Field tốt

Về thiết kế, Field nên chứa:

```python
class Field:

    name
    column
    python_type
    nullable
    default
    primary_key
    unique
```

Ví dụ:

```python
id = IntegerField(
    primary_key=True
)

name = StringField(
    nullable=False,
    unique=True
)
```

---

# 45. Model cuối cùng

Ta hướng tới API:

```python
class User(Model):

    id = IntegerField(
        primary_key=True
    )

    name = StringField(
        nullable=False
    )

    age = IntegerField(
        nullable=False
    )
```

Sau đó:

```python
user = User()

user.name = "Alice"
user.age = 25
```

Framework có thể biết:

```text
User
 │
 ├── id
 │   ├── INTEGER
 │   └── PRIMARY KEY
 │
 ├── name
 │   ├── TEXT
 │   └── NOT NULL
 │
 └── age
     ├── INTEGER
     └── NOT NULL
```

---

# 46. Điểm kết nối với Metaclass

Ở đây chúng ta bắt đầu thấy một kiến trúc rất thú vị:

```text
                 Class Creation
                       │
                       ▼
                  ModelMeta
                       │
                       ▼
                 inspect Fields
                       │
                       ▼
                  Model Schema
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
      Descriptor                 SQL
          │                         │
          ▼                         ▼
     object access             database
```

Đây chính là cầu nối sang:

> **Phần VII — Metaclass**

---

# 47. Descriptor và Metaclass có vai trò khác nhau

Đừng nhầm hai thứ.

### Descriptor

Xử lý:

```text
instance attribute access
```

Ví dụ:

```python
user.name
user.name = "Alice"
```

### Metaclass

Xử lý:

```text
class creation
```

Ví dụ:

```python
class User(Model):
    ...
```

---

# 48. Một ORM thường dùng cả hai

```text
               ORM
                │
       ┌────────┴────────┐
       ▼                 ▼
 Descriptor          Metaclass
       │                 │
       ▼                 ▼
instance access     class creation
       │                 │
       └────────┬────────┘
                ▼
             Model
                │
                ▼
            Database
```

Đây là kiến thức rất quan trọng cho phần Framework Design mà bạn đang học.

---

# 49. Code Mini ORM hoàn chỉnh

Đây là phiên bản nhỏ nhưng đã thể hiện đúng tư tưởng:

```python
class Field:

    python_type = object

    def __init__(
        self,
        column=None,
        nullable=True,
        primary_key=False,
    ):
        self.column = column
        self.nullable = nullable
        self.primary_key = primary_key

    def __set_name__(self, owner, name):
        self.name = name

        if self.column is None:
            self.column = name

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return instance.__dict__.get(
            self.name
        )

    def __set__(self, instance, value):

        if value is None:

            if not self.nullable:
                raise ValueError(
                    f"{self.name} "
                    "cannot be None"
                )

        elif not isinstance(
            value,
            self.python_type
        ):
            raise TypeError(
                f"{self.name} must be "
                f"{self.python_type.__name__}"
            )

        instance.__dict__[self.name] = value


class StringField(Field):

    python_type = str


class IntegerField(Field):

    python_type = int
```

---

# 50. ModelMeta

```python
class ModelMeta(type):

    def __new__(
        cls,
        name,
        bases,
        namespace,
    ):

        fields = {}

        for key, value in namespace.items():

            if isinstance(value, Field):
                fields[key] = value

        namespace["_fields"] = fields
        namespace["_table"] = name.lower()

        return super().__new__(
            cls,
            name,
            bases,
            namespace,
        )
```

---

# 51. Model

```python
class Model(
    metaclass=ModelMeta
):
    pass
```

---

# 52. User

```python
class User(Model):

    id = IntegerField(
        primary_key=True
    )

    name = StringField(
        nullable=False
    )

    age = IntegerField(
        nullable=False
    )
```

---

# 53. Sử dụng

```python
user = User()

user.id = 1
user.name = "Alice"
user.age = 25
```

Đọc:

```python
print(user.name)
```

Kết quả:

```text
Alice
```

---

# 54. Metadata

```python
print(User._fields)
```

Ta có schema của Model.

Ví dụ:

```python
for name, field in User._fields.items():

    print(
        name,
        field.column,
        field.python_type,
        field.primary_key,
        field.nullable,
    )
```

---

# 55. Đây chính là "magic" của ORM

Ta viết:

```python
class User(Model):
    ...
```

nhưng framework thu được:

```text
Model Schema
     │
     ├── Fields
     ├── Types
     ├── Columns
     ├── Constraints
     └── Metadata
```

Sau đó có thể:

```text
Schema
  ↓
CREATE TABLE
  ↓
INSERT
  ↓
SELECT
  ↓
UPDATE
  ↓
DELETE
```

---

# 56. Kiến thức cần nhớ

## 1.

Field là Descriptor:

```python
class StringField(Field):
    ...
```

## 2.

Field nằm trên class:

```python
User.__dict__["name"]
```

## 3.

Dữ liệu nằm trên instance:

```python
user.__dict__["name"]
```

## 4.

`__set_name__()` giúp Field biết tên attribute.

## 5.

`__get__()` xử lý:

```python
user.name
```

## 6.

`__set__()` xử lý:

```python
user.name = "Alice"
```

## 7.

Metaclass xử lý class creation.

---

# 57. Bức tranh toàn bộ 21 → 24

Đây là phần bạn nên ghi nhớ nhất:

```text
Buổi 21
Descriptor
   │
   ├── __get__
   ├── __set__
   └── __delete__
        │
        ▼
Buổi 22
property
        │
        ▼
Buổi 23
method
        │
        ▼
Buổi 24
ORM Field
        │
        ▼
┌─────────────────────────┐
│ StringField             │
│ IntegerField            │
│ RelationshipField       │
│ ForeignKey              │
│ QueryField              │
└─────────────────────────┘
        │
        ▼
     ORM
```

Bạn có thể thấy **Descriptor không phải kiến thức lý thuyết riêng lẻ**. Nó là một trong những cơ chế nền tảng giúp Python xây dựng API kiểu ORM rất mạnh.

---

# 58. Bài tập thực hành

### Bài 1 — `Field`

Tự viết lại:

```python
Field
StringField
IntegerField
```

phải hỗ trợ:

```python
user.name
user.name = "Alice"
```

---

### Bài 2 — Validation

Thêm:

```python
nullable=False
```

Sao cho:

```python
user.name = None
```

ném:

```text
ValueError
```

---

### Bài 3 — Metadata

Thêm:

```python
column="user_name"
```

để:

```python
User.name.column
```

trả về:

```text
user_name
```

---

### Bài 4 — Mini Schema

Viết:

```python
User.schema()
```

trả về:

```python
{
    "id": {
        "type": "INTEGER",
        "primary_key": True,
    },
    "name": {
        "type": "TEXT",
        "nullable": False,
    },
}
```

---

### Bài 5 — Deep Dive

Giải thích chính xác:

```python
user.name = "Alice"
```

theo chuỗi:

```text
1. Python bắt đầu attribute assignment
2. tìm User.name
3. phát hiện Data Descriptor
4. gọi Field.__set__()
5. validation
6. ghi vào user.__dict__
```

---

# Tiếp theo — Buổi 25

Theo **đúng roadmap ban đầu**, sau Descriptor/ORM chúng ta chuyển sang:

# **Phần VII — Metaclass**

### Buổi 25 — `type()`

Chúng ta sẽ giải mã:

```python
class User:
    pass
```

thực chất liên quan đến:

```python
User = type(
    "User",
    (),
    {}
)
```

và tìm hiểu sâu:

```text
object
  ↑
type
  ↑
User
```

Đặc biệt:

> **Class cũng là object.**

Sau bài này, ta sẽ bắt đầu đi sâu vào **Class Object → `type` → Dynamic Class Creation → Metaclass**, đúng theo roadmap 25–30.
