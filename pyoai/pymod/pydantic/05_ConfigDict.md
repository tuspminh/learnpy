# Pydantic v2 — Buổi 5: Model Configuration với `ConfigDict`

Ở Buổi 4 chúng ta đã biết cách xây dựng **Nested Model**. Bây giờ chúng ta học cách **điều khiển hành vi của toàn bộ Pydantic model** bằng `ConfigDict`.

Đây là bài rất quan trọng trước khi đi sang serialization, alias và DTO cho Novel Crawler.

---

# 1. `ConfigDict` là gì?

Ví dụ:

```python
from pydantic import BaseModel, ConfigDict


class NovelDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    title: str
    author: str
```

`model_config` nói cho Pydantic:

> Model này phải hoạt động theo những quy tắc nào?

Có thể hình dung:

```text
                 BaseModel
                    │
                    ▼
              model_config
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      extra       strict    assignment
```

---

# 2. Vì sao cần Configuration?

Giả sử parser trả:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "views": 100000,
    "unknown_field": "abc",
}
```

Model:

```python
class NovelDTO(BaseModel):
    title: str
    author: str
```

Câu hỏi là:

> `unknown_field` phải xử lý thế nào?

Có 3 chiến lược chính:

```text
ignore
forbid
allow
```

Đây chính là công việc của:

```python
ConfigDict(extra=...)
```

---

# 3. `extra="ignore"`

Đây là hành vi mặc định của Pydantic.

```python
from pydantic import BaseModel, ConfigDict


class NovelDTO(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    title: str
    author: str
```

Input:

```python
data = {
    "title": "ABC",
    "author": "XYZ",
    "unknown": "something",
}
```

Validate:

```python
novel = NovelDTO.model_validate(data)
```

`unknown` bị bỏ qua.

```python
print(novel)
```

Chỉ có:

```text
title='ABC' author='XYZ'
```

---

# 4. `extra="forbid"`

Đây là chế độ nghiêm ngặt hơn.

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    title: str
    author: str
```

Input:

```python
data = {
    "title": "ABC",
    "author": "XYZ",
    "unknown": "something",
}
```

Kết quả:

```python
NovelDTO.model_validate(data)
```

→ `ValidationError`.

Pydantic sẽ báo rằng:

```text
unknown
```

không phải field được phép.

---

# 5. `extra="allow"`

Có thể cho phép field ngoài schema:

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )

    title: str
    author: str
```

Input:

```python
data = {
    "title": "ABC",
    "author": "XYZ",
    "source_id": "123",
}
```

Field `source_id` không được khai báo nhưng vẫn được giữ lại như extra data.

---

# 6. So sánh 3 chế độ

| `extra`    | Field lạ |
| ---------- | -------- |
| `"ignore"` | bỏ qua   |
| `"forbid"` | báo lỗi  |
| `"allow"`  | giữ lại  |

Có thể nhớ:

```text
ignore  → bỏ
forbid  → chặn
allow   → giữ
```

---

# 7. Novel Crawler nên dùng gì?

Không có một đáp án duy nhất; phụ thuộc boundary.

Ví dụ parser website:

```text
HTML
 ↓
Parser
 ↓
NovelDTO
```

Website có thể thay đổi HTML và parser có thể vô tình tạo thêm field.

Ở boundary parser, đôi khi:

```python
extra="ignore"
```

rất tiện.

Nhưng với API contract:

```text
Client
 ↓
Request DTO
 ↓
Application
```

ta thường muốn phát hiện dữ liệu ngoài schema:

```python
extra="forbid"
```

Điểm quan trọng là:

> **Configuration nên phản ánh boundary mà model đang bảo vệ.**

---

# 8. `strict=True`

Buổi 3 chúng ta đã nói về strict validation.

Ở cấp model, có thể cấu hình:

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        strict=True
    )

    title: str
    chapter_count: int
```

Khi đó Pydantic sẽ nghiêm ngặt hơn trong việc xử lý kiểu dữ liệu.

Ví dụ:

```python
NovelDTO(
    title="ABC",
    chapter_count="100",
)
```

Trong strict mode, `"100"` không được tự động coi là `100` cho field `int`.

---

# 9. Strict theo model vs strict theo field

Có thể strict toàn model:

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        strict=True
    )

    title: str
    chapter_count: int
```

Hoặc chỉ strict một field:

```python
from pydantic import Field


class NovelDTO(BaseModel):
    title: str

    chapter_count: int = Field(
        strict=True
    )
```

Khi đó:

```text
Model
 ├── title          → bình thường
 └── chapter_count  → strict
```

Điều này rất hữu ích khi chỉ một số dữ liệu cần kiểm soát chặt.

---

# 10. `validate_assignment`

Một vấn đề thú vị:

```python
class NovelDTO(BaseModel):
    title: str
    chapter_count: int
```

Tạo object:

```python
novel = NovelDTO(
    title="ABC",
    chapter_count=100,
)
```

Sau đó:

```python
novel.chapter_count = "hello"
```

Nếu không bật `validate_assignment`, việc assignment này không được validation theo cách bạn có thể mong đợi.

Ta có thể bật:

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True
    )

    title: str
    chapter_count: int
```

Bây giờ:

```python
novel.chapter_count = "hello"
```

sẽ gây `ValidationError`.

---

# 11. Tại sao `validate_assignment` quan trọng?

Hãy tưởng tượng:

```text
DTO được tạo
   ↓
VALID
   ↓
application sửa dữ liệu
   ↓
INVALID
```

Nếu DTO có thể bị sửa trực tiếp, validation lúc khởi tạo chưa đủ.

Với:

```python
validate_assignment=True
```

ta có:

```text
CREATE
  ↓
validate
  ↓
VALID
  ↓
ASSIGN
  ↓
validate
  ↓
VALID
```

---

# 12. Test `validate_assignment`

```python
from pydantic import BaseModel, ConfigDict


class ChapterDTO(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True
    )

    number: int
    title: str
```

Tạo:

```python
chapter = ChapterDTO(
    number=1,
    title="Chapter 1",
)
```

Assignment hợp lệ:

```python
chapter.number = 2

print(chapter.number)
```

Kết quả:

```text
2
```

Assignment sai:

```python
chapter.number = "hello"
```

→ `ValidationError`.

---

# 13. `frozen=True`

Có thể làm model immutable theo nghĩa Pydantic:

```python
class NovelDTO(BaseModel):
    model_config = ConfigDict(
        frozen=True
    )

    title: str
    author: str
```

Sau khi tạo:

```python
novel = NovelDTO(
    title="ABC",
    author="XYZ",
)
```

Không thể:

```python
novel.title = "DEF"
```

Pydantic sẽ báo lỗi.

---

# 14. Khi nào dùng `frozen=True`?

Rất hữu ích cho các object mang tính:

```text
Value Object
Configuration
Immutable DTO
Request snapshot
```

Ví dụ:

```python
class CrawlRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True
    )

    url: str
    retry: int
```

Sau khi tạo request:

```text
CrawlRequest
      │
      ▼
Không thay đổi
      │
      ▼
Worker
```

Điều này giúp giảm khả năng một phần code khác vô tình thay đổi request.

---

# 15. `populate_by_name`

Phần này sẽ trở nên rất quan trọng khi học **Alias**.

Ví dụ model:

```python
from pydantic import BaseModel, ConfigDict, Field


class NovelDTO(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True
    )

    title: str = Field(
        alias="book_title"
    )
```

Có alias:

```text
Python field:
title

External field:
book_title
```

Với `populate_by_name=True`, model có thể chấp nhận tên field Python trong các trường hợp phù hợp với alias configuration.

Đến Buổi 8 chúng ta sẽ học alias một cách đầy đủ, nên ở đây chỉ cần nhớ:

```text
populate_by_name
        ↓
liên quan đến alias
```

---

# 16. Configuration có thể kết hợp

Ví dụ DTO của crawler:

```python
from pydantic import BaseModel, ConfigDict


class NovelDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        strict=True,
    )

    title: str
    author: str
    chapter_count: int
```

Model này có 3 quy tắc:

```text
extra="forbid"
        ↓
Không cho field lạ

strict=True
        ↓
Không coercion kiểu dữ liệu dễ dàng

validate_assignment=True
        ↓
Assignment cũng phải validate
```

---

# 17. Nhưng đừng bật mọi thứ một cách máy móc

Đây là tư duy kiến trúc quan trọng.

Ví dụ crawler lấy dữ liệu từ HTML:

```python
data = {
    "chapter_count": "123"
}
```

Nếu parser luôn trả string từ HTML:

```text
HTML
 ↓
Parser
 ↓
"123"
```

thì:

```python
strict=True
```

có thể khiến boundary trở nên khó dùng.

Trong trường hợp này coercion:

```text
"123"
 ↓
123
```

có thể là hành vi mong muốn.

Ngược lại API contract:

```text
JSON
 ↓
Request DTO
```

thường cần contract rõ ràng hơn.

Vì vậy:

> **Config không phải “càng strict càng tốt”.**

Mà là:

> **Strictness phải phù hợp với nguồn dữ liệu và boundary.**

---

# 18. Configuration ở Base Model

Nếu project có rất nhiều DTO, không nên lặp:

```python
extra="forbid"
validate_assignment=True
```

ở hàng chục class.

Có thể tạo base DTO:

```python
from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
```

Sau đó:

```python
class NovelDTO(BaseDTO):
    title: str
    author: str
```

và:

```python
class ChapterDTO(BaseDTO):
    number: int
    title: str
```

Tất cả đều kế thừa configuration.

---

# 19. Đây là cách rất phù hợp với project lớn

Ví dụ:

```text
application/
    dto/
        base.py
        novel.py
        chapter.py
        author.py
        crawl.py
```

`base.py`:

```python
from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )
```

`novel.py`:

```python
from .base import BaseDTO


class NovelDTO(BaseDTO):
    title: str
    author: str
```

`chapter.py`:

```python
from .base import BaseDTO


class ChapterDTO(BaseDTO):
    number: int
    title: str
```

Kiến trúc sẽ sạch hơn.

---

# 20. Một lưu ý quan trọng về kế thừa config

Config của model con có thể bổ sung hoặc ghi đè config của model cha.

Ví dụ:

```python
class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )
```

Model con:

```python
class ExternalDTO(BaseDTO):
    model_config = ConfigDict(
        extra="ignore"
    )

    title: str
```

Model con có thể thay đổi hành vi `extra`.

Vì vậy cần thiết kế:

```text
BaseDTO
   ↓
default policy
   ↓
DTO cụ thể
   ↓
override nếu thật sự cần
```

---

# 21. `ConfigDict` và Domain Model

Trong kiến trúc chúng ta đang học:

```text
Parser
   ↓
Pydantic DTO
   ↓
Mapper
   ↓
Domain Entity
```

`ConfigDict` thuộc về **Pydantic/data boundary**.

Không nên biến Domain Entity thành một Pydantic model chỉ vì Pydantic có configuration tiện lợi.

Ví dụ:

```text
                    Infrastructure
                         │
HTML ──→ Parser ──→ NovelDTO
                         │
                         ▼
                      Mapper
                         │
                         ▼
                   Novel Entity
                         │
                         ▼
                    Use Case
```

`ConfigDict` chủ yếu nằm ở:

```text
NovelDTO
```

chứ không phải toàn bộ domain.

---

# 22. Mini Project — DTO cho Novel Crawler

Ta tạo:

```python
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseDTO(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class AuthorDTO(BaseDTO):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class ChapterDTO(BaseDTO):
    number: int = Field(
        ge=1,
    )

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    url: str


class NovelDTO(BaseDTO):
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

# 23. Test hợp lệ

```python
data = {
    "title": "Đấu Phá Thương Khung",

    "author": {
        "name": "Thiên Tằm Thổ Đậu"
    },

    "status": "ongoing",

    "chapters": [
        {
            "number": 1,
            "title": "Tiêu Gia",
            "url": "https://example.com/1",
        }
    ],
}

novel = NovelDTO.model_validate(data)

print(novel)
```

---

# 24. Test `extra="forbid"`

Thêm:

```python
data = {
    "title": "ABC",
    "author": {
        "name": "XYZ"
    },
    "unknown_field": "hello",
}
```

Chạy:

```python
NovelDTO.model_validate(data)
```

→ `ValidationError`.

Đặc biệt, vì `AuthorDTO` cũng kế thừa `BaseDTO`, extra field bên trong author cũng bị chặn:

```python
data = {
    "title": "ABC",
    "author": {
        "name": "XYZ",
        "age": 100,
    },
}
```

`age` cũng bị reject.

---

# 25. Test `validate_assignment`

```python
novel = NovelDTO(
    title="ABC",
    author={
        "name": "XYZ"
    },
)

novel.title = "DEF"

print(novel.title)
```

Hợp lệ.

Nhưng:

```python
novel.title = 123
```

sẽ được kiểm tra lại bởi `validate_assignment`.

---

# 26. Một nuance quan trọng

`validate_assignment=True` không có nghĩa:

> mọi object lồng bên trong tự động được kiểm tra khi chúng tự thay đổi.

Ví dụ:

```python
novel.author.name = ...
```

là một vấn đề khác với:

```python
novel.author = ...
```

Nếu cần immutable/validation sâu, chúng ta phải thiết kế model lồng nhau và configuration phù hợp.

Đừng hiểu `validate_assignment` là một hệ thống "deep freeze/deep validation".

---

# 27. Bảng tổng kết Buổi 5

| Config                     | Tác dụng                                       |
| -------------------------- | ---------------------------------------------- |
| `extra="ignore"`           | bỏ field lạ                                    |
| `extra="forbid"`           | reject field lạ                                |
| `extra="allow"`            | giữ field lạ                                   |
| `strict=True`              | validation kiểu nghiêm ngặt                    |
| `validate_assignment=True` | validate khi assignment                        |
| `frozen=True`              | không cho thay đổi field                       |
| `populate_by_name=True`    | hỗ trợ populate theo field name khi dùng alias |

---

# 28. Mental Model

Đừng học thuộc từng option riêng lẻ. Hãy nghĩ:

```text
              Pydantic Model
                    │
             ┌──────┴──────┐
             │ ConfigDict  │
             └──────┬──────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Input         Runtime      Output
       │            │            │
     extra        assignment   alias
     strict       frozen       serialization
```

`ConfigDict` chính là **policy của model**.

---

# 29. Liên hệ trực tiếp với Novel Crawler

Ta có thể chia configuration theo boundary:

```text
HTML Parser DTO
    │
    └── extra="ignore"
        có thể phù hợp nếu parser có dữ liệu phụ

API Request DTO
    │
    └── extra="forbid"
        contract chặt

Immutable Request
    │
    └── frozen=True

DTO cần chỉnh sửa trong application
    │
    └── validate_assignment=True
```

Không nhất thiết toàn project phải dùng một configuration duy nhất.

Đây là cách tiếp cận phù hợp với DDD/Clean Architecture: **policy của DTO phụ thuộc vào boundary mà DTO đại diện.**

---

# 30. Bài tập Buổi 5

Hãy viết một `BaseDTO`:

```python
class BaseDTO(BaseModel):
    ...
```

yêu cầu:

```text
extra field       → reject
assignment        → validate
```

Sau đó:

```python
class ChapterDTO(BaseDTO):
    number: int
    title: str
```

Test:

### Test 1

```python
ChapterDTO(
    number=1,
    title="Chapter 1",
)
```

### Test 2

```python
ChapterDTO(
    number=1,
    title="Chapter 1",
    author="ABC",
)
```

### Test 3

```python
chapter = ChapterDTO(
    number=1,
    title="Chapter 1",
)

chapter.number = "hello"
```

### Test 4

Thử tạo:

```python
class ImmutableChapterDTO(BaseDTO):
    model_config = ConfigDict(
        frozen=True
    )

    number: int
    title: str
```

rồi:

```python
chapter.number = 2
```

và quan sát lỗi.

---

## Roadmap hiện tại

```text
01 Pydantic + BaseModel
02 Field + Type Annotation          ← đã học
03 Validation + Strict              ← đã học
04 Nested Models                    ← đã học
05 ConfigDict                       ← hôm nay
06 Serialization
07 Parsing / model_validate
08 Alias
09 field_validator
10 model_validator
...
```

**Buổi 6** chúng ta sẽ học **Serialization chuyên sâu**: `model_dump()`, `model_dump_json()`, `include`, `exclude`, `exclude_none`, `exclude_defaults`, nested serialization — phần này đặc biệt quan trọng khi DTO phải truyền dữ liệu giữa **Parser → Application → Repository/API**.
