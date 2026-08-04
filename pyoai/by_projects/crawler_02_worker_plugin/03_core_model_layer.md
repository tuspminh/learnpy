# Buổi 3 — Xây dựng Core Model Layer

## Mục tiêu

Sau buổi này, framework sẽ có một **Model Layer** hoàn chỉnh, là nền tảng cho toàn bộ hệ thống:

* Thiết kế BaseModel
* Thiết kế Entity Model
* Validation
* Serialization
* Metadata
* Dirty Tracking
* Copy
* Hash
* Equality
* Có thể test hoàn toàn bằng CLI

> **Mục tiêu thiết kế:** Model không phụ thuộc vào SQLite, Repository, Worker hay Plugin. Đây là lớp Domain thuần (Pure Domain Model).

---

# 1. Kiến trúc Model Layer

```text
crawler/
│
├── core/
│
│   ├── models/
│   │
│   ├── base.py
│   ├── metadata.py
│   ├── fields.py
│   ├── validators.py
│   ├── exceptions.py
│   │
│   ├── book.py
│   ├── chapter.py
│   ├── author.py
│   ├── image.py
│   ├── category.py
│   └── tag.py
```

Mỗi model chỉ chứa dữ liệu và quy tắc nghiệp vụ liên quan đến chính nó.

---

# 2. Vì sao không dùng dict?

Đừng làm:

```python
book = {
    "title": "...",
    "author": "...",
    "cover": "..."
}
```

Vì:

* Không có autocomplete.
* Không validate.
* Không type hint.
* Không IDE support.
* Sai key rất khó phát hiện.

Thay vào đó:

```python
book.title
book.author
book.cover
```

---

# 3. BaseModel

Tạo:

```text
core/models/base.py
```

```python
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(slots=True)
class BaseModel:

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
```

Đây là nền tảng cho mọi model.

---

# 4. Book Model

```python
from dataclasses import dataclass

from .base import BaseModel


@dataclass(slots=True)
class Book(BaseModel):

    id: int | None = None

    title: str = ""

    author: str = ""

    description: str = ""

    cover: str = ""

    source: str = ""

    source_book_id: str = ""
```

Sử dụng:

```python
book = Book(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu"
)

print(book.title)
```

---

# 5. Chapter Model

```python
from dataclasses import dataclass

from .base import BaseModel


@dataclass(slots=True)
class Chapter(BaseModel):

    id: int |None = None

    book_id: int | None = None

    order: int = 0

    title: str = ""

    content: str = ""

    source_url: str = ""
```

---

# 6. Image Model

```python
@dataclass(slots=True)
class Image(BaseModel):

    id: int | None = None

    chapter_id: int | None = None

    url: str = ""

    local_path: str = ""
```

---

# 7. Metadata

Mỗi model nên có metadata.

Ví dụ:

```python
from dataclasses import field


title: str = field(
    default="",
    metadata={
        "required": True,
        "max_length": 300
    }
)
```

Sau này validator sẽ đọc metadata.

---

# 8. Validation

Ví dụ:

```python
from dataclasses import fields


def validate(model):

    for f in fields(model):

        value = getattr(model, f.name)

        required = f.metadata.get("required", False)

        if required and value == "":

            raise ValueError(
                f"{f.name} is required."
            )
```

Thử:

```python
book = Book()

validate(book)
```

Kết quả:

```
ValueError:

title is required
```

---

# 9. Serialization

Có:

```python
book.to_dict()
```

Trả về:

```python
{
    "id":None,
    "title":"abc",
    "author":"xyz"
}
```

Ngược lại:

```python
Book.from_dict(data)
```

---

# 10. Equality

Dataclass hỗ trợ:

```python
book1 == book2
```

Ví dụ:

```python
Book(title="A")

Book(title="A")
```

Kết quả

```
True
```

---

# 11. Copy

```python
from copy import deepcopy

book2 = deepcopy(book1)
```

Không ảnh hưởng object cũ.

---

# 12. Dirty Tracking (phiên bản đơn giản)

Trong nhiều ORM, cần biết object có thay đổi hay không.

Ví dụ:

```python
book.title = "ABC"
```

Đánh dấu:

```
dirty=True
```

Phiên bản đầu:

```python
class BaseModel:

    _dirty=False

    def mark_dirty(self):

        self._dirty=True
```

Sau này (buổi nâng cao) sẽ tự động theo dõi mọi thay đổi bằng `__setattr__`.

---

# 13. CLI Test

Tạo command:

```
crawler model
```

Ví dụ:

```bash
python -m crawler model create-book
```

Output:

```
Book

title : Demo

author : Unknown
```

---

Command:

```bash
python -m crawler model validate
```

Output:

```
Validation OK
```

---

Command:

```bash
python -m crawler model serialize
```

Output:

```json
{
  "title":"Demo",
  "author":"Unknown"
}
```

---

# 14. Test Unit

```
tests/

test_models.py
```

Ví dụ:

```python
from crawler.core.models.book import Book


def test_book():

    book = Book(title="ABC")

    assert book.title == "ABC"
```

---

# 15. Cấu trúc sau buổi 3

```text
core/
│
├── models/
│
│   ├── base.py
│   ├── book.py
│   ├── chapter.py
│   ├── image.py
│   ├── author.py
│   ├── category.py
│   └── tag.py
│
├── validators.py
├── metadata.py
└── exceptions.py
```

---

# Kết quả cuối buổi

Framework đã có:

* ✅ BaseModel
* ✅ Book Model
* ✅ Chapter Model
* ✅ Image Model
* ✅ Validation cơ bản
* ✅ Metadata
* ✅ Serialization (`to_dict`, `from_dict`)
* ✅ Dirty Tracking (bản đơn giản)
* ✅ Unit Test
* ✅ CLI để tạo, validate và serialize model

Đây là nền tảng để các tầng **Repository**, **Plugin** và **Worker** làm việc với cùng một kiểu dữ liệu, không phụ thuộc vào cách dữ liệu được lấy hay lưu.

---

# Bài tập

1. Cài đặt `BaseModel` với `to_dict()` và `from_dict()`.
2. Tạo các model `Book`, `Chapter`, `Image`.
3. Thêm metadata `required` cho các trường bắt buộc như `title`.
4. Viết hàm `validate()` đọc metadata và kiểm tra dữ liệu.
5. Thêm các lệnh CLI:

   * `model create-book`
   * `model validate`
   * `model serialize`
6. Viết ít nhất 5 unit test kiểm tra:

   * Khởi tạo model
   * `to_dict()`
   * `from_dict()`
   * Validation thành công
   * Validation thất bại

## Buổi 4

Ở buổi tiếp theo, chúng ta sẽ xây dựng **Plugin Interface Layer**, bao gồm:

* Thiết kế `CrawlerPlugin` bằng `abc.ABC`
* Định nghĩa lifecycle của plugin
* Capability (book/chapter/search...)
* Plugin metadata
* Plugin registry
* Mock plugin để kiểm thử hoàn toàn bằng CLI trước khi kết nối tới website thật.
