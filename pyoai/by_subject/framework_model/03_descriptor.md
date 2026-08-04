# Buổi 3 — Descriptor & Field Deep Dive

> Đây là buổi quan trọng nhất của toàn bộ series xây dựng Model Framework. Sau buổi này bạn sẽ hiểu vì sao chỉ cần viết:

```python
class Novel(Model):
    title = StringField(max_length=200)
```

là có thể dùng:

```python
novel.title = "Đấu Phá Thương Khung"
```

mà Field vẫn tự động:

* validate
* kiểm tra kiểu dữ liệu
* lưu dữ liệu
* theo dõi thay đổi (dirty tracking)
* gọi hook

Đó chính là sức mạnh của **Descriptor Protocol** trong Python.

---

# Mục tiêu

Sau buổi này bạn sẽ hiểu và tự xây dựng được:

```text
Novel.title
        │
        ▼
Descriptor(Field)
        │
 ├── __get__()
 ├── __set__()
 ├── __delete__()
 └── __set_name__()
        │
        ▼
instance.__dict__
        │
        ▼
Validation
        │
        ▼
Dirty Tracking
```

Đây là nền tảng của:

* Django ORM
* SQLAlchemy ORM
* attrs
* dataclasses (một phần)
* Pydantic (phiên bản đầu)
* rất nhiều framework Python khác.

---

# Phần 1. Descriptor là gì?

Thông thường:

```python
class Person:
    pass


p = Person()
p.name = "Alice"
```

Python làm việc như sau:

```text
p.name = "Alice"

↓

p.__dict__["name"] = "Alice"
```

Không có bất kỳ kiểm tra nào.

---

Nếu muốn:

```python
p.age = -10
```

phải báo lỗi.

Ta cần chặn việc gán.

Descriptor sinh ra để làm điều đó.

---

# Descriptor Protocol

Một descriptor là object có một hoặc nhiều phương thức sau:

```python
__get__()

__set__()

__delete__()

__set_name__()
```

Ví dụ:

```python
class Field:
    def __get__(self, instance, owner): ...

    def __set__(self, instance, value): ...
```

---

# Descriptor hoạt động thế nào?

Ví dụ

```python
class User:
    name = Field()
```

Khi viết:

```python
u.name = "Alice"
```

Python KHÔNG gán trực tiếp.

Python thực hiện:

```python
Field.__set__(u, "Alice")
```

---

Khi đọc

```python
print(u.name)
```

Python gọi

```python
Field.__get__(u, User)
```

Không hề truy cập thẳng vào `u.__dict__`.

---

# Ví dụ đầu tiên

```python
class Field:
    def __get__(self, instance, owner):
        print("GET")

    def __set__(self, instance, value):
        print("SET", value)
```

---

Model

```python
class User:
    name = Field()
```

---

Thử

```python
u = User()

u.name = "Alice"

print(u.name)
```

Kết quả

```text
SET Alice

GET
```

---

# Phần 2. Lưu dữ liệu ở đâu?

Nếu chỉ in ra:

```python
SET Alice
```

thì dữ liệu mất.

Descriptor phải tự lưu.

---

Sai

```python
class Field:
    def __set__(self, instance, value):

        self.value = value
```

---

Vì

```python
u1.name = "Alice"

u2.name = "Bob"
```

thì:

```text
Field.value

↓

Bob
```

Hai object dùng chung một Field.

---

Đúng

Lưu vào instance.

```python
instance.__dict__
```

---

Ví dụ

```python
class Field:
    def __set__(self, instance, value):

        instance.__dict__["name"] = value

    def __get__(self, instance, owner):

        return instance.__dict__["name"]
```

---

Thử

```python
u1.name = "Alice"

u2.name = "Bob"
```

Kết quả

```text
u1

↓

Alice

u2

↓

Bob
```

---

# Phần 3. **set_name**()

Nhưng:

```python
instance.__dict__["name"]
```

đang hard-code.

Nếu Field là

```python
title
```

thì sao?

---

Python giải quyết bằng:

```python
__set_name__()
```

---

Ví dụ

```python
class Field:
    def __set_name__(self, owner, name):

        self.name = name
```

---

Model

```python
class Novel:
    title = Field()

    author = Field()
```

Python tự động gọi

```python
Field.__set_name__(Novel, "title")

Field.__set_name__(Novel, "author")
```

---

Lúc này

```python
self.name
```

đã biết:

```text
"title"

hoặc

"author"
```

---

Descriptor

```python
class Field:
    def __set_name__(self, owner, name):

        self.name = name

    def __set__(self, instance, value):

        instance.__dict__[self.name] = value

    def __get__(self, instance, owner):

        return instance.__dict__.get(self.name)
```

Không còn hard-code nữa.

---

# Phần 4. Validation

Bây giờ có thể validate ngay khi gán.

```python
class StringField(Field):
    def __set__(self, instance, value):

        if not isinstance(value, str):
            raise TypeError

        instance.__dict__[self.name] = value
```

---

Ví dụ

```python
novel.title = 123
```

↓

```text
TypeError
```

---

Giới hạn độ dài

```python
class StringField(Field):
    def __init__(self, max_length):

        self.max_length = max_length
```

---

Validation

```python
if len(value) > self.max_length:
    raise ValueError
```

---

Ví dụ

```python
title = StringField(max_length=10)
```

---

```python
novel.title = "abcdefghijk"
```

↓

```text
ValueError
```

---

# Phần 5. Dirty Tracking

Muốn biết field nào đã thay đổi.

Ví dụ

```python
novel.title = "AAA"

novel.author = "BBB"
```

Repository chỉ UPDATE đúng 2 field.

---

Descriptor

```python
instance.__dirty__.add(self.name)
```

---

Ví dụ

```python
class Field:
    def __set__(self, instance, value):

        instance.__dict__[self.name] = value

        instance.__dirty__.add(self.name)
```

---

Kết quả

```python
print(novel.__dirty__)
```

↓

```text
{
    'title',
    'author'
}
```

---

# Phần 6. Read Only Field

Ví dụ

```text
created_at
```

Không cho sửa.

---

```python
class ReadOnlyField(Field):
    def __set__(self, instance, value):

        if self.name in instance.__dict__:
            raise AttributeError

        instance.__dict__[self.name] = value
```

---

Thử

```python
obj.created_at = ...

obj.created_at = ...
```

↓

```text
AttributeError
```

---

# Phần 7. Lazy Loading

Giả sử

```text
Novel

↓

chapters
```

Có 5000 chapter.

Không muốn load ngay.

---

Descriptor

```python
novel.chapters
```

↓

lần đầu

↓

query database

↓

cache

↓

trả về.

---

Ví dụ

```python
class LazyField(Field):
    def __get__(self, instance, owner):

        if self.name not in instance.__dict__:
            print("Loading...")

            instance.__dict__[self.name] = []

        return instance.__dict__[self.name]
```

---

Lần đầu

```text
Loading...
```

Lần sau

Không load nữa.

---

# Phần 8. Computed Descriptor

Không lưu dữ liệu.

Ví dụ

```text
slug
```

---

Descriptor

```python
class SlugField:
    def __get__(self, instance, owner):

        return instance.title.lower().replace(" ", "-")
```

---

Model

```python
class Novel:
    title = StringField()

    slug = SlugField()
```

---

Kết quả

```python
print(novel.slug)
```

↓

```text
dau-pha-thuong-khung
```

Không cần `@property`.

---

# Phần 9. Một Field hoàn chỉnh

```python
class Field:
    def __init__(self, default=None):
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):

        if instance is None:
            return self

        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):

        instance.__dict__[self.name] = value

        instance.__dirty__.add(self.name)

    def __delete__(self, instance):

        instance.__dict__.pop(self.name, None)
```

Đây là nền tảng cho mọi Field sau này.

---

# Data Descriptor và Non-data Descriptor

Python chia descriptor thành hai loại:

| Loại                | Có `__get__` | Có `__set__` | Độ ưu tiên                   |
| ------------------- | ------------ | ------------ | ---------------------------- |
| Data Descriptor     | ✔            | ✔            | Cao hơn `instance.__dict__`  |
| Non-data Descriptor | ✔            | ✘            | Thấp hơn `instance.__dict__` |

Ví dụ:

```python
class ReadOnly:
    def __get__(self, instance, owner):
        return 42
```

Đây là **non-data descriptor**.

Nếu:

```python
obj.__dict__["value"] = 100
```

thì:

```python
print(obj.value)
```

sẽ in:

```text
100
```

Ngược lại, nếu descriptor có cả `__set__`, Python sẽ ưu tiên descriptor thay vì giá trị trong `__dict__`.

---

# Thứ tự tra cứu thuộc tính (Attribute Lookup)

Khi bạn viết:

```python
value = obj.title
```

Python tra cứu theo thứ tự:

```text
1. Data Descriptor
        │
        ▼
2. instance.__dict__
        │
        ▼
3. Non-data Descriptor
        │
        ▼
4. Class Attribute
        │
        ▼
5. __getattr__()
```

Hiểu đúng thứ tự này giúp bạn giải thích được hầu hết hành vi của descriptor.

---

# Kiến trúc của Field

```text
               User.title
                    │
                    ▼
           Descriptor Protocol
      ┌──────────┼──────────┐
      ▼          ▼          ▼
   __get__    __set__    __delete__
      │          │
      ▼          ▼
 instance.__dict__
      │
      ▼
 Validation
      │
      ▼
 Dirty Tracking
      │
      ▼
 Repository
```

---

# So sánh @property và Descriptor

| Tiêu chí                | `@property`   | Descriptor  |
| ----------------------- | ------------- | ----------- |
| Áp dụng cho nhiều field | ✘             | ✔           |
| Tái sử dụng             | Thấp          | Cao         |
| Có metadata             | ✘             | ✔           |
| Validation chung        | Khó           | Dễ          |
| Dirty Tracking          | Khó           | Dễ          |
| ORM Framework           | Không phù hợp | Rất phù hợp |

Vì vậy, các ORM lớn đều xây dựng Field dựa trên **descriptor** thay vì chỉ dùng `@property`.

---

# Bài tập thực hành

## Bài 1

Viết `Field` hỗ trợ:

* `__set_name__`
* `__get__`
* `__set__`
* `__delete__`

Lưu dữ liệu vào `instance.__dict__`.

---

## Bài 2

Viết `StringField`:

* Kiểm tra kiểu `str`
* Hỗ trợ `max_length`
* Hỗ trợ `nullable`

---

## Bài 3

Viết `IntegerField`:

* Chỉ chấp nhận `int`
* Có `min_value`
* Có `max_value`

---

## Bài 4

Thêm **dirty tracking**:

```python
novel.title = "A"
novel.author = "B"

print(novel.__dirty__)
```

Kết quả:

```text
{'title', 'author'}
```

---

## Bài 5

Viết `ReadOnlyField` cho `created_at`.

---

## Bài 6

Viết `LazyField` mô phỏng việc tải danh sách chapter chỉ khi truy cập lần đầu.

---

## Buổi tiếp theo

**Buổi 4 — Metaclass & Model Registry Deep Dive**

Đây là buổi chúng ta sẽ kết hợp tất cả kiến thức đã học để xây dựng một **mini ORM framework**. Nội dung gồm:

* `type` và cách Python tạo class
* Xây dựng `ModelMeta`
* Tự động thu thập toàn bộ `Field`
* Kế thừa metadata từ lớp cha
* Đăng ký (registry) tất cả model trong hệ thống
* Tự động sinh schema từ metadata
* Chuẩn bị nền tảng cho `Repository` và `DatabaseManager`

Sau buổi này, bạn sẽ hiểu cơ chế mà Django ORM, SQLAlchemy và nhiều framework Python sử dụng để tạo và quản lý các model một cách tự động.
