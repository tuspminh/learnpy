# Pydantic v2 — Buổi 2: `Field` và Type Annotation

Hôm nay chúng ta học cách **khai báo schema dữ liệu đúng cách** trong Pydantic.

Buổi này rất quan trọng vì từ đây các model của chúng ta sẽ bắt đầu giống **DTO thực tế của Novel Crawler**, thay vì chỉ là các class có vài field đơn giản.

---

# 1. Mục tiêu Buổi 2

Sau bài này bạn sẽ hiểu:

1. Type annotation trong Pydantic
2. Các kiểu dữ liệu cơ bản
3. `list`, `dict`, `tuple`, `set`
4. `Optional` / `None`
5. `Literal`
6. Required field
7. Default value
8. `Field()`
9. `default`
10. `default_factory`
11. Validation cơ bản bằng type annotation
12. Thiết kế DTO cho Novel Crawler

---

# 2. Type Annotation chính là schema

Ví dụ:

```python
from pydantic import BaseModel


class Novel(BaseModel):
    title: str
    author: str
    year: int
```

Ta đang nói với Pydantic:

```text
Novel
 ├── title  : str
 ├── author : str
 └── year   : int
```

Khi tạo:

```python
novel = Novel(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    year=2008,
)
```

Pydantic kiểm tra dữ liệu dựa trên annotation.

---

# 3. Các kiểu dữ liệu cơ bản

## `str`

```python
class Novel(BaseModel):
    title: str
```

```python
novel = Novel(title="Đấu Phá Thương Khung")

print(novel.title)
```

---

## `int`

```python
class Novel(BaseModel):
    chapter_count: int
```

```python
novel = Novel(chapter_count=1200)

print(novel.chapter_count)
```

---

## `float`

```python
class Book(BaseModel):
    rating: float
```

---

## `bool`

```python
class Book(BaseModel):
    completed: bool
```

---

## `None`

Có thể cho phép field nhận `None`:

```python
class Novel(BaseModel):
    description: str | None
```

Ví dụ:

```python
Novel(description=None)
```

---

# 4. `str | None` rất quan trọng

Trong Python hiện đại:

```python
description: str | None
```

có nghĩa:

```text
description có thể là:

str
hoặc
None
```

Tương đương cách viết cũ:

```python
from typing import Optional

description: Optional[str]
```

Hai cách này về ý nghĩa là tương đương.

Tôi khuyên dùng syntax hiện đại:

```python
str | None
```

---

# 5. Nhưng `str | None` không đồng nghĩa với default `None`

Đây là điểm rất dễ nhầm.

Ví dụ:

```python
class Novel(BaseModel):
    description: str | None
```

Field này cho phép `None`, nhưng **không có nghĩa là field tự động có giá trị `None` nếu bạn không truyền vào**.

Nếu muốn optional thật sự:

```python
class Novel(BaseModel):
    description: str | None = None
```

Bây giờ:

```python
novel = Novel()

print(novel.description)
```

Kết quả:

```text
None
```

### Phân biệt

```python
description: str | None
```

→ cho phép `None`, nhưng field vẫn có thể required.

Trong khi:

```python
description: str | None = None
```

→ không bắt buộc truyền field.

Đây là distinction rất quan trọng khi thiết kế DTO.

---

# 6. Collection: `list`

Ví dụ:

```python
class Novel(BaseModel):
    tags: list[str]
```

Dữ liệu:

```python
novel = Novel(
    tags=["Tiên Hiệp", "Huyền Huyễn", "Tu Tiên"]
)

print(novel.tags)
```

Pydantic hiểu:

```text
tags
 ↓
list
 ↓
mỗi phần tử phải là str
```

Ví dụ:

```python
Novel(
    tags=["Tiên Hiệp", 123]
)
```

Pydantic sẽ validation phần tử `123`.

---

# 7. List của model

Đây chính là thứ chúng ta đã bắt đầu dùng ở Buổi 4.

```python
from pydantic import BaseModel


class ChapterDTO(BaseModel):
    number: int
    title: str


class NovelDTO(BaseModel):
    title: str
    chapters: list[ChapterDTO]
```

Input:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "chapters": [
        {
            "number": 1,
            "title": "Tiêu Gia"
        },
        {
            "number": 2,
            "title": "Nạp Khí Đấu Giả"
        }
    ]
}
```

Pydantic tự chuyển:

```text
dict
 ↓
NovelDTO
 ↓
chapters
 ↓
ChapterDTO
ChapterDTO
```

---

# 8. `dict`

Có thể khai báo:

```python
class Novel(BaseModel):
    metadata: dict[str, str]
```

Ví dụ:

```python
novel = Novel(
    metadata={
        "source": "truyenfull",
        "category": "tien-hiep",
    }
)
```

Schema:

```text
metadata
   │
   ├── key   : str
   └── value : str
```

---

# 9. Dict với model

Ví dụ crawler có:

```text
chapter_number -> ChapterDTO
```

Ta có thể viết:

```python
class ChapterDTO(BaseModel):
    number: int
    title: str


class NovelDTO(BaseModel):
    chapters: dict[int, ChapterDTO]
```

Input:

```python
data = {
    "chapters": {
        1: {
            "number": 1,
            "title": "Chương 1"
        },
        2: {
            "number": 2,
            "title": "Chương 2"
        }
    }
}
```

Sau validation:

```python
novel = NovelDTO.model_validate(data)

print(novel.chapters[1])
```

---

# 10. `tuple`

Có thể khai báo:

```python
class Point(BaseModel):
    position: tuple[int, int]
```

```python
point = Point(position=(100, 200))

print(point.position)
```

Schema:

```text
position
 ├── int
 └── int
```

---

# 11. `set`

```python
class Novel(BaseModel):
    tags: set[str]
```

Input:

```python
novel = Novel(
    tags=[
        "Tiên Hiệp",
        "Huyền Huyễn",
        "Tiên Hiệp",
    ]
)

print(novel.tags)
```

Set sẽ loại duplicate.

Kết quả về mặt dữ liệu sẽ chỉ còn các giá trị duy nhất.

---

# 12. `Literal`

`Literal` dùng khi một field **chỉ được phép nhận một số giá trị cố định**.

Ví dụ:

```python
from typing import Literal


class Novel(BaseModel):
    status: Literal["ongoing", "completed"]
```

Hợp lệ:

```python
Novel(status="ongoing")

Novel(status="completed")
```

Không hợp lệ:

```python
Novel(status="unknown")
```

Đây rất hữu ích cho crawler.

Ví dụ:

```python
class CrawlResult(BaseModel):
    status: Literal[
        "success",
        "failed",
        "skipped",
    ]
```

Ta đang biến:

```text
status = bất kỳ string nào
```

thành:

```text
status ∈ {
    success,
    failed,
    skipped
}
```

---

# 13. Khi nào dùng `Literal`?

Dùng khi tập giá trị **nhỏ và cố định**.

Ví dụ:

```python
method: Literal["GET", "POST"]
```

```python
environment: Literal[
    "development",
    "testing",
    "production",
]
```

Nhưng nếu tập giá trị lớn hoặc là một concept domain quan trọng, sau này chúng ta sẽ học `Enum`.

---

# 14. Required field

Ví dụ:

```python
class Novel(BaseModel):
    title: str
    author: str
```

Cả hai đều required.

Không được:

```python
Novel()
```

Không được:

```python
Novel(title="ABC")
```

Phải:

```python
Novel(
    title="ABC",
    author="XYZ",
)
```

---

# 15. Default value

Ta có thể đặt default:

```python
class Novel(BaseModel):
    title: str
    status: str = "ongoing"
```

Bây giờ:

```python
novel = Novel(title="ABC")

print(novel.status)
```

Kết quả:

```text
ongoing
```

Schema:

```text
title
required

status
optional
default = "ongoing"
```

---

# 16. `Field()`

Đây là phần quan trọng nhất của buổi hôm nay.

Import:

```python
from pydantic import BaseModel, Field
```

Ví dụ:

```python
class Novel(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
```

Ở đây:

```python
title: str
```

xác định **kiểu dữ liệu**.

Còn:

```python
Field(
    min_length=1,
    max_length=200,
)
```

bổ sung **metadata + constraints**.

---

# 17. `Field` không thay thế type annotation

Không nên nghĩ:

```python
Field(str)
```

Thay vào đó:

```python
title: str = Field(...)
```

Có hai phần:

```text
title: str
   │
   └── type


Field(...)
   │
   └── constraints / metadata / default
```

---

# 18. `Field` với description

```python
class Novel(BaseModel):
    title: str = Field(
        description="Tên truyện"
    )
```

Field này có:

```text
type:
str

description:
Tên truyện
```

Description đặc biệt hữu ích khi tạo JSON Schema hoặc API documentation.

---

# 19. `Field` với default

```python
class Novel(BaseModel):
    status: str = Field(
        default="ongoing"
    )
```

Tương đương:

```python
status: str = "ongoing"
```

Nhưng `Field()` cho phép thêm nhiều metadata/constraint.

Ví dụ:

```python
class Novel(BaseModel):
    status: str = Field(
        default="ongoing",
        description="Trạng thái truyện",
    )
```

---

# 20. `Field(...)` — Required field

Bạn có thể thấy:

```python
class Novel(BaseModel):
    title: str = Field(...)
```

`...` nghĩa là:

> field này required.

Ví dụ:

```python
class Novel(BaseModel):
    title: str = Field(...)
```

Phải truyền:

```python
Novel(title="ABC")
```

---

# 21. `default_factory`

Đây là phần cực kỳ quan trọng khi làm DTO có collection.

Ví dụ:

```python
class Novel(BaseModel):
    chapters: list[str] = Field(
        default_factory=list
    )
```

Bây giờ:

```python
novel = Novel()

print(novel.chapters)
```

Kết quả:

```text
[]
```

---

# 22. Vì sao dùng `default_factory`?

Thay vì cố gắng tạo một list mặc định dùng chung, ta nói:

```python
default_factory=list
```

nghĩa là:

> Mỗi instance hãy tạo một list mới.

Ví dụ:

```python
class Novel(BaseModel):
    chapters: list[str] = Field(
        default_factory=list
    )


novel1 = Novel()
novel2 = Novel()

novel1.chapters.append("Chapter 1")

print(novel1.chapters)
print(novel2.chapters)
```

Kết quả:

```text
['Chapter 1']
[]
```

Hai object có list độc lập.

---

# 23. Đây rất phù hợp với Novel Crawler

Ví dụ:

```python
class NovelDTO(BaseModel):
    title: str
    author: str
    chapters: list[str] = Field(
        default_factory=list
    )
```

Khi parser mới chỉ lấy được thông tin novel:

```python
novel = NovelDTO(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
)
```

Ta vẫn có:

```python
novel.chapters == []
```

Sau đó application layer có thể bổ sung chapters.

---

# 24. Constraint cho số

`Field()` cũng có thể giới hạn số.

```python
class Chapter(BaseModel):
    number: int = Field(
        ge=1
    )
```

`ge`:

```text
greater than or equal
```

Tức:

```text
number >= 1
```

---

Ví dụ:

```python
Chapter(number=1)
```

hợp lệ.

```python
Chapter(number=0)
```

sẽ validation error.

---

# 25. Một số constraint quan trọng

### Số

```python
Field(
    gt=0,
    ge=0,
    lt=100,
    le=100,
    multiple_of=5,
)
```

Ý nghĩa:

| Constraint    | Ý nghĩa |
| ------------- | ------- |
| `gt`          | >       |
| `ge`          | >=      |
| `lt`          | <       |
| `le`          | <=      |
| `multiple_of` | bội số  |

---

### String

```python
Field(
    min_length=1,
    max_length=200,
)
```

---

### Collection

```python
Field(
    min_length=1,
    max_length=1000,
)
```

Có thể dùng để giới hạn kích thước collection.

---

# 26. Ví dụ hoàn chỉnh

Bây giờ kết hợp tất cả:

```python
from typing import Literal

from pydantic import BaseModel, Field


class AuthorDTO(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Tên tác giả",
    )


class ChapterDTO(BaseModel):
    number: int = Field(
        ge=1,
        description="Số chương",
    )

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    url: str


class NovelDTO(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    author: AuthorDTO

    description: str | None = None

    status: Literal[
        "ongoing",
        "completed",
    ] = "ongoing"

    chapters: list[ChapterDTO] = Field(
        default_factory=list
    )
```

---

# 27. Test model

```python
data = {
    "title": "Đấu Phá Thương Khung",

    "author": {
        "name": "Thiên Tằm Thổ Đậu"
    },

    "description": "Một câu chuyện tu luyện.",

    "status": "ongoing",

    "chapters": [
        {
            "number": 1,
            "title": "Tiêu Gia",
            "url": "https://example.com/chapter-1",
        },
        {
            "number": 2,
            "title": "Nạp Khí",
            "url": "https://example.com/chapter-2",
        },
    ],
}
```

Validate:

```python
novel = NovelDTO.model_validate(data)
```

Sau đó:

```python
print(novel.title)
print(novel.author.name)
print(novel.chapters[0].title)
```

---

# 28. Test lỗi

Thử:

```python
data = {
    "title": "",
    "author": {
        "name": ""
    },
    "status": "invalid",
    "chapters": [
        {
            "number": 0,
            "title": "",
            "url": "abc",
        }
    ],
}
```

Pydantic sẽ phát hiện nhiều lỗi:

```text
title
author.name
status
chapters[0].number
chapters[0].title
```

Đây chính là ưu điểm rất lớn của Pydantic:

```text
Raw Data
   ↓
Validation
   ↓
Valid DTO
```

hoặc:

```text
Raw Data
   ↓
Validation Error
   ↓
Không cho dữ liệu bẩn đi tiếp
```

---

# 29. Type annotation + Field tạo thành Schema

Có thể hình dung:

```python
class ChapterDTO(BaseModel):
    number: int = Field(ge=1)

    title: str = Field(
        min_length=1,
        max_length=300,
    )
```

Không chỉ nói:

```text
number là int
title là str
```

mà còn nói:

```text
number >= 1

1 <= len(title) <= 300
```

Do đó Pydantic model ngày càng giống một **data contract**.

---

# 30. Áp dụng vào kiến trúc Novel Crawler

Trong crawler của bạn, parser có thể trả:

```python
raw_data = {
    "title": "...",
    "author": "...",
    "status": "...",
    "chapters": [...]
}
```

Sau đó:

```python
novel_dto = NovelDTO.model_validate(raw_data)
```

Luồng:

```text
Website HTML
     │
     ▼
   Parser
     │
     ▼
   dict
     │
     ▼
 Pydantic DTO
     │
     │ validation
     ▼
 Valid Data
     │
     ▼
   Mapper
     │
     ▼
 Domain Entity
     │
     ▼
 Repository
```

Điểm quan trọng:

> **Pydantic DTO bảo vệ boundary của application; nó không phải domain entity.**

Đây là hướng chúng ta sẽ tiếp tục giữ khi đi tới phần DDD/Clean Architecture.

---

# 31. Một model thực tế hơn cho crawler

Ví dụ:

```python
from typing import Literal

from pydantic import BaseModel, Field


class NovelDTO(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    author: str = Field(
        min_length=1,
        max_length=100,
    )

    url: str

    cover: str | None = None

    description: str | None = None

    status: Literal[
        "ongoing",
        "completed",
    ] = "ongoing"

    chapters: list[str] = Field(
        default_factory=list
    )
```

Test:

```python
novel = NovelDTO(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
    url="https://example.com/dau-pha-thuong-khung",
)

print(novel)
```

---

# 32. `model_dump()`

Sau khi có model:

```python
print(novel.model_dump())
```

Ví dụ:

```python
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "url": "https://example.com/dau-pha-thuong-khung",
    "cover": None,
    "description": None,
    "status": "ongoing",
    "chapters": [],
}
```

Đây là lúc DTO có thể truyền sang application layer.

---

# 33. `Field` còn có nhiều tính năng hơn

Trong các bài sau chúng ta sẽ lần lượt học:

```python
Field(...)
```

kết hợp với:

* alias
* validation constraints
* serialization
* JSON Schema
* metadata
* strict mode
* validation
* serialization

Đặc biệt:

```text
Buổi 2
   ↓
Field
   ↓
Buổi 3
Validation
   ↓
Buổi 4
Nested Models
   ↓
Buổi 5
ConfigDict
```

---

# 34. Những điều cần nhớ sau Buổi 2

Bạn chỉ cần nắm chắc 7 điểm này trước khi sang bài tiếp:

### ① Type annotation

```python
title: str
```

xác định kiểu dữ liệu.

### ② `| None`

```python
description: str | None
```

cho phép `None`.

### ③ Default

```python
status: str = "ongoing"
```

field có giá trị mặc định.

### ④ `Literal`

```python
status: Literal["ongoing", "completed"]
```

chỉ cho phép tập giá trị xác định.

### ⑤ `Field`

```python
title: str = Field(
    min_length=1,
    max_length=200,
)
```

bổ sung constraints/metadata.

### ⑥ `default_factory`

```python
chapters: list[str] = Field(
    default_factory=list
)
```

tạo collection mới cho mỗi instance.

### ⑦ Nested type

```python
chapters: list[ChapterDTO]
```

cho phép tạo schema dữ liệu nhiều tầng.

---

## Bài tập Buổi 2

Hãy tự viết:

```text
AuthorDTO
ChapterDTO
NovelDTO
```

với yêu cầu:

```text
AuthorDTO
- name: str, 1–100 ký tự

ChapterDTO
- number: int >= 1
- title: str, 1–300 ký tự
- url: str

NovelDTO
- title: str, 1–200 ký tự
- author: AuthorDTO
- description: str | None
- status: "ongoing" | "completed"
- chapters: list[ChapterDTO], mặc định []
```

Sau đó test **3 trường hợp**:

```text
1. Dữ liệu hợp lệ
2. Thiếu field required
3. Dữ liệu sai constraint
```

Ở **Buổi 3**, chúng ta sẽ đi sâu vào **Validation, Type Coercion, Strict Mode và `ValidationError`**; đây là phần biến Pydantic từ một class khai báo dữ liệu thành một hệ thống validation thực sự.
