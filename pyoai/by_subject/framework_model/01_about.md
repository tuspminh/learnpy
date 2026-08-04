# Model với Metadata, Validation, Computed Property Deep Dive

Đây là một trong những chủ đề quan trọng nhất khi thiết kế framework Python, đặc biệt nếu bạn đang xây dựng:

* Framework cào truyện
* ORM tự viết
* Repository Pattern
* Service Layer
* REST API
* Desktop App (PySide6)
* SQLite Framework

Đây cũng là nền tảng của:

* Django Model
* SQLAlchemy Model
* Pydantic
* attrs
* dataclass
* Marshmallow

---

# Mục tiêu

Sau bài này bạn sẽ biết cách thiết kế model có khả năng:

```
Novel
│
├── metadata
│      field type
│      default
│      nullable
│      max_length
│      unique
│
├── validation
│      validate()
│      before_save()
│      after_load()
│
├── computed property
│      chapter_count
│      slug
│      full_title
│
├── serialization
│
├── dirty tracking
│
└── repository
```

Đây gần như là framework model hoàn chỉnh.

---

# Phần 1. Model là gì?

Thông thường nhiều người viết:

```python
class Novel:
    def __init__(self):
        self.title = ""
        self.author = ""
```

Đây chỉ là object.

Model thực sự còn có:

* schema
* metadata
* validation
* computed field
* serialize
* hooks

Ví dụ:

```
Novel
│
├── id:int
├── title:str
├── author:str
├── created_at
├── updated_at
│
├── validate()
├── to_dict()
├── from_dict()
├── save()
├── delete()
└── computed properties
```

---

# Phần 2. Metadata là gì?

Metadata là dữ liệu mô tả dữ liệu.

Ví dụ:

```
title
```

không chỉ là một chuỗi.

Nó còn có:

```
type = str

nullable = False

max_length = 200

default = ""

index = True

unique = False
```

Đó gọi là metadata.

---

Ví dụ:

```python
Field(type=str, nullable=False, default="", max_length=200)
```

---

Một model thực tế

```python
Novel

title

↓

Field Metadata

type=str

nullable=False

default=""

max_length=200

unique=True
```

---

# Metadata dùng để làm gì?

Ví dụ

```
CREATE TABLE novel

↓

title TEXT NOT NULL

↓

được sinh từ metadata
```

Hoặc

```
UI Form

↓

textbox

↓

metadata quyết định textbox dài bao nhiêu
```

---

# Thiết kế Field

```python
class Field:
    def __init__(
        self, field_type, default=None, nullable=True, max_length=None, unique=False
    ):
        self.field_type = field_type
        self.default = default
        self.nullable = nullable
        self.max_length = max_length
        self.unique = unique
```

---

Tạo model

```python
class Novel:
    title = Field(str, default="", nullable=False, max_length=200)

    author = Field(str, default="")
```

Lúc này class đã mang schema.

---

# Lấy metadata

```python
print(Novel.title.max_length)
```

```
200
```

```
print(Novel.title.nullable)
```

```
False
```

---

# Tự động thu thập metadata

Có thể dùng metaclass hoặc `__init_subclass__`.

Ví dụ đơn giản:

```python
class Model:
    __fields__ = {}

    def __init_subclass__(cls):

        cls.__fields__ = {}

        for name, value in cls.__dict__.items():
            if isinstance(value, Field):
                cls.__fields__[name] = value
```

---

Tạo model

```python
class Novel(Model):
    title = Field(str)

    author = Field(str)
```

---

Kiểm tra

```python
print(Novel.__fields__)
```

```
{
    'title': Field(...),
    'author': Field(...)
}
```

Framework ORM thường hoạt động theo cách này.

---

# Phần 3. Validation

Validation nghĩa là:

Kiểm tra dữ liệu trước khi lưu.

Ví dụ

```
title

↓

không được rỗng
```

---

Ví dụ

```python
title=""

↓

raise ValidationError
```

---

Một validator đơn giản

```python
class ValidationError(Exception):
    pass
```

---

Validator

```python
def validate_title(value):

    if value == "":
        raise ValidationError("Title empty")
```

---

Model

```python
class Novel(Model):
    title = Field(str)

    def validate(self):

        validate_title(self.title)
```

---

Gọi

```python
novel.validate()
```

---

# Validation theo metadata

Ví dụ

```
nullable=False
```

Tự động kiểm tra.

```python
if value is None:
    raise ValidationError
```

---

Kiểm tra kiểu

```python
if not isinstance(value, field.field_type):
    raise ValidationError
```

---

Kiểm tra max_length

```python
if len(value) > field.max_length:
    raise ValidationError
```

---

Framework có thể lặp qua toàn bộ field:

```python
for name, field in self.__fields__.items():
    value = getattr(self, name)

    ...
```

Đây là cách Django, Pydantic và nhiều ORM hoạt động.

---

# Validation tùy chỉnh

Ví dụ

```python
title
```

Không được chứa ký tự HTML.

```python
def validate_title(value):

    if "<" in value:
        raise ValidationError
```

---

Hoặc

```
rating

0-10
```

```python
if value < 0 or value > 10:
    ...
```

---

# Multiple Validator

Một field có thể có nhiều validator.

```python
Field(str, validators=[validate_not_empty, validate_length, validate_html])
```

---

Framework

```python
for validator in field.validators:
    validator(value)
```

---

# Cross Field Validation

Có những validation cần nhiều field.

Ví dụ

```
start_date

end_date
```

Phải:

```
start < end
```

---

Ví dụ

```python
def validate(self):

    if self.start_date > self.end_date:
        raise ValidationError
```

---

# Phần 4. Computed Property

Đây là phần cực kỳ quan trọng.

Giả sử

```
Novel

chapters
```

Muốn

```
chapter_count
```

Nhưng không lưu database.

---

Không nên:

```python
self.chapter_count = len(self.chapters)
```

Vì dễ sai khi dữ liệu thay đổi.

---

Dùng property

```python
@property
def chapter_count(self):

    return len(self.chapters)
```

---

Ví dụ

```python
novel.chapter_count
```

```
152
```

Không cần lưu database.

---

# Computed Slug

```python
@property
def slug(self):

    return self.title.lower().replace(" ", "-")
```

---

Ví dụ

```
Đấu Phá Thương Khung
```

↓

```
đấu-phá-thương-khung
```

---

# Computed Full Name

```python
@property
def full_name(self):

    return f"{self.title} - {self.author}"
```

---

# Cached Property

Nếu tính toán tốn thời gian:

```python
from functools import cached_property


class Novel:
    @cached_property
    def statistics(self):

        print("calculating...")

        return heavy_calculation()
```

Lần đầu:

```
calculating...
```

Lần sau:

Không tính lại.

> Lưu ý: nếu dữ liệu gốc thay đổi sau khi cache, bạn cần xóa thuộc tính đã cache (`del obj.statistics`) hoặc xây dựng cơ chế tự làm mới.

---

# Computed Database Field

Một số hệ thống vẫn lưu giá trị đã tính sẵn để tối ưu truy vấn.

Ví dụ:

```
chapter_count
```

Database có cột:

```
chapter_count INTEGER
```

Nhưng khi thêm chapter:

```
Repository

↓

update chapter_count
```

Đây là chiến lược **denormalization** để tăng hiệu năng đọc, đổi lại phải đảm bảo cập nhật nhất quán.

---

# Metadata + Validation + Property kết hợp

```python
class Novel(Model):
    title = Field(str, nullable=False, max_length=200)

    author = Field(str, default="")

    @property
    def slug(self):
        return self.title.lower().replace(" ", "-")
```

Model này đã có:

* Metadata
* Schema
* Validation (dựa trên metadata)
* Computed Property

Đây là nền tảng cho một framework model hiện đại.

---

# Kiến trúc hoàn chỉnh

```text
                   Model
                     │
     ┌───────────────┼────────────────┐
     │               │                │
 Metadata        Validation      Computed Property
     │               │                │
  Field()      validate()       @property
     │               │                │
     └───────────────┼────────────────┘
                     │
             Serialization
                     │
                Dirty Tracking
                     │
               Repository Layer
                     │
                  SQLite ORM
```

---

# So sánh các thành phần

| Thành phần        | Vai trò                      | Ví dụ                              |
| ----------------- | ---------------------------- | ---------------------------------- |
| Metadata          | Mô tả schema                 | `max_length=200`, `nullable=False` |
| Validation        | Kiểm tra dữ liệu             | Không cho tiêu đề rỗng             |
| Computed Property | Giá trị tính toán            | `chapter_count`, `slug`            |
| Cached Property   | Cache kết quả tính toán      | Thống kê truyện                    |
| Serialization     | Chuyển đổi model ↔ dict/JSON | `to_dict()`, `from_dict()`         |
| Dirty Tracking    | Theo dõi thay đổi            | Biết trường nào cần cập nhật       |
| Repository        | Đọc/ghi cơ sở dữ liệu        | `NovelRepository.save()`           |

---

# Bài tập thực hành

1. Xây dựng lớp `Field` hỗ trợ:

   * `field_type`
   * `default`
   * `nullable`
   * `max_length`
   * `unique`
   * `validators`

2. Xây dựng `Model` cơ sở tự động thu thập các `Field` bằng `__init_subclass__`.

3. Cài đặt `Model.validate()` để:

   * Kiểm tra `nullable`
   * Kiểm tra kiểu dữ liệu
   * Kiểm tra `max_length`
   * Chạy toàn bộ validator tùy chỉnh của từng trường

4. Tạo model `Novel` gồm:

   * `title`
   * `author`
   * `description`
   * `created_at`

5. Thêm các computed property:

   * `slug`
   * `short_description` (100 ký tự đầu)
   * `display_title` (`"{title} - {author}"`)

6. Thử tạo các trường hợp dữ liệu hợp lệ và không hợp lệ để kiểm chứng cơ chế validation.

---

## Buổi tiếp theo

**Model Lifecycle & Hooks Deep Dive**

Chúng ta sẽ xây dựng vòng đời đầy đủ của model với các hook như:

* `before_validate()`
* `after_validate()`
* `before_save()`
* `after_save()`
* `before_delete()`
* `after_delete()`
* `before_load()`
* `after_load()`

Đây là nền tảng để tạo nên một framework ORM hoàn chỉnh với khả năng mở rộng và tùy biến cao.
