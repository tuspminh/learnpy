# Pydantic v2 — Buổi 7: Parsing & `model_validate*()`

Ở Buổi 6, chúng ta học chiều:

```text
Pydantic Model
      ↓
model_dump()
      ↓
dict
```

Hôm nay học chiều ngược lại:

```text
dict / JSON / string data
          ↓
       Pydantic
          ↓
       DTO hợp lệ
```

Đây chính là phần kết nối trực tiếp với **Parser của Novel Crawler**.

---

# 1. Parsing trong Pydantic là gì?

Giả sử parser HTML của crawler lấy được:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
}
```

Ta muốn biến nó thành:

```python
NovelDTO(...)
```

Thay vì:

```python
novel = NovelDTO(
    title=data["title"],
    author=data["author"],
)
```

Pydantic cung cấp:

```python
novel = NovelDTO.model_validate(data)
```

Luồng:

```text
HTML
 ↓
Parser
 ↓
dict
 ↓
model_validate()
 ↓
NovelDTO
```

---

# 2. `model_validate()`

Đây là API quan trọng nhất của bài.

```python
from pydantic import BaseModel


class NovelDTO(BaseModel):
    title: str
    author: str
```

Có dữ liệu:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
}
```

Validate:

```python
novel = NovelDTO.model_validate(data)
```

Sau đó:

```python
print(novel.title)
print(novel.author)
```

Kết quả:

```text
Đấu Phá Thương Khung
Thiên Tằm Thổ Đậu
```

---

# 3. Tại sao không gọi trực tiếp `NovelDTO(**data)`?

Cách này hoàn toàn hợp lệ:

```python
novel = NovelDTO(**data)
```

Nhưng:

```python
NovelDTO.model_validate(data)
```

thể hiện rõ ý nghĩa:

> "Hãy validate dữ liệu này theo schema của NovelDTO."

Đặc biệt khi làm application lớn, `model_validate()` rất dễ đọc trong các boundary.

Ví dụ:

```python
novel_dto = NovelDTO.model_validate(
    parser.parse(page)
)
```

Ta nhìn vào code là hiểu ngay:

```text
parser output
     ↓
validation
     ↓
DTO
```

---

# 4. `model_validate()` không chỉ nhận dict

Ví dụ:

```python
class AuthorDTO(BaseModel):
    name: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
```

Input:

```python
data = {
    "title": "ABC",
    "author": {
        "name": "XYZ"
    }
}
```

Có thể:

```python
novel = NovelDTO.model_validate(data)
```

Pydantic tự xây:

```text
dict
 │
 ▼
NovelDTO
 │
 └── AuthorDTO
```

---

# 5. Validation nested

Ví dụ dữ liệu lỗi:

```python
data = {
    "title": "ABC",
    "author": {
        "name": 123
    }
}
```

Pydantic sẽ validation cả nested model.

Ta có thể xem:

```python
from pydantic import ValidationError

try:
    NovelDTO.model_validate(data)
except ValidationError as exc:
    for error in exc.errors():
        print(error)
```

---

# 6. `model_validate_json()`

Bây giờ dữ liệu không còn là `dict`.

Giả sử API trả JSON:

```python
json_data = """
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu"
}
"""
```

Ta có thể:

```python
novel = NovelDTO.model_validate_json(
    json_data
)
```

Kết quả:

```python
print(novel)
```

---

# 7. `model_validate()` vs `model_validate_json()`

Đây là điểm cần nhớ:

```text
model_validate()
        ↓
Python object
        ↓
dict / mapping
```

Trong khi:

```text
model_validate_json()
        ↓
JSON data
        ↓
str / bytes
```

Ví dụ:

```python
data = {
    "title": "ABC",
    "author": "XYZ",
}

NovelDTO.model_validate(data)
```

Còn:

```python
json_data = '{"title":"ABC","author":"XYZ"}'

NovelDTO.model_validate_json(json_data)
```

---

# 8. Không nên dùng `json.loads()` nếu không cần

Có người viết:

```python
import json

data = json.loads(json_data)

novel = NovelDTO.model_validate(data)
```

Cách này có thể dùng.

Nhưng nếu nguồn đã là JSON:

```python
NovelDTO.model_validate_json(json_data)
```

ngắn gọn và thể hiện đúng ý định hơn.

---

# 9. JSON bytes

`model_validate_json()` cũng hữu ích khi dữ liệu ở dạng bytes.

Ví dụ:

```python
json_data = b'''
{
    "title": "ABC",
    "author": "XYZ"
}
'''
```

Có thể:

```python
novel = NovelDTO.model_validate_json(
    json_data
)
```

Điều này khá phù hợp với dữ liệu nhận từ HTTP.

---

# 10. `model_validate_strings()`

Đây là API thú vị hơn.

Giả sử ta có:

```python
data = {
    "title": "ABC",
    "chapter_count": "123",
}
```

Tất cả dữ liệu đều là string.

Model:

```python
class NovelDTO(BaseModel):
    title: str
    chapter_count: int
```

Có thể:

```python
novel = NovelDTO.model_validate_strings(data)
```

Pydantic sẽ xử lý dữ liệu string theo schema.

Kết quả:

```python
print(novel.chapter_count)
print(type(novel.chapter_count))
```

→

```text
123
<class 'int'>
```

---

# 11. Tại sao `model_validate_strings()` hữu ích?

Có rất nhiều nguồn dữ liệu mà mọi thứ đều là string:

```text
HTML
HTML form
environment variables
query parameters
CSV
CLI arguments
configuration
```

Ví dụ:

```python
data = {
    "title": "ABC",
    "chapter_count": "123",
}
```

Nếu model yêu cầu:

```python
chapter_count: int
```

Pydantic có thể chuyển đổi phù hợp.

---

# 12. So sánh 3 API

Hãy nhớ bảng này:

| API                        | Input chính          |
| -------------------------- | -------------------- |
| `model_validate()`         | Python object / dict |
| `model_validate_json()`    | JSON string/bytes    |
| `model_validate_strings()` | dữ liệu dạng string  |

Mental model:

```text
dict
 │
 └── model_validate()
          ↓
        Model


JSON
 │
 └── model_validate_json()
          ↓
        Model


string values
 │
 └── model_validate_strings()
          ↓
        Model
```

---

# 13. `model_validate()` và type coercion

Ví dụ:

```python
class ChapterDTO(BaseModel):
    number: int
    title: str
```

Input:

```python
data = {
    "number": "123",
    "title": "Chapter 123",
}
```

Trong configuration mặc định, Pydantic có thể chuyển:

```text
"123"
 ↓
123
```

nên:

```python
chapter = ChapterDTO.model_validate(data)

print(chapter.number)
print(type(chapter.number))
```

Kết quả:

```text
123
<class 'int'>
```

---

# 14. Nhưng strict mode thay đổi điều này

Nếu:

```python
from pydantic import BaseModel, ConfigDict


class ChapterDTO(BaseModel):
    model_config = ConfigDict(
        strict=True
    )

    number: int
    title: str
```

thì:

```python
data = {
    "number": "123",
    "title": "Chapter 123",
}
```

có thể bị reject vì:

```text
"123" != int
```

Đây chính là mối liên hệ giữa:

```text
Buổi 3
Strict Mode
     ↓
Buổi 5
ConfigDict
     ↓
Buổi 7
model_validate()
```

---

# 15. Parsing không có nghĩa là Business Validation

Điểm này rất quan trọng trong kiến trúc.

Ví dụ:

```python
class ChapterDTO(BaseModel):
    number: int
    title: str
```

Pydantic kiểm tra:

```text
number có phải int?
title có phải str?
```

Nhưng giả sử domain có rule:

```text
chapter number phải lớn hơn chapter trước
```

Đây không nhất thiết là trách nhiệm của Pydantic DTO.

Luồng:

```text
Raw Data
   ↓
Pydantic Validation
   ↓
DTO hợp lệ về mặt dữ liệu
   ↓
Domain Validation
   ↓
Business Rule
```

---

# 16. Pipeline thực tế của Novel Crawler

Đây là phần bạn nên đặc biệt chú ý.

Giả sử parser:

```python
class NovelParser:
    def parse(self, html: str) -> dict:
        return {
            "title": "...",
            "author": "...",
            "description": "...",
        }
```

Parser **không cần biết Pydantic**.

Sau đó application layer:

```python
raw_data = parser.parse(html)

novel_dto = NovelDTO.model_validate(
    raw_data
)
```

Ta có:

```text
                 Infrastructure
                       │
HTML ──→ Parser ──→ dict
                       │
                       ▼
                model_validate()
                       │
                       ▼
                   NovelDTO
                       │
                       ▼
                    Mapper
                       │
                       ▼
                 Domain Entity
```

Đây là separation rất đẹp.

---

# 17. Parser không nên tự "nhồi" validation

Ví dụ không nên biến parser thành:

```python
def parse(html):
    ...
    if not title:
        raise ...
    if not author:
        raise ...
    if not ...
```

rồi tất cả validation nằm trong parser.

Parser nên tập trung vào:

```text
HTML
 ↓
Extract data
 ↓
dict
```

Pydantic boundary:

```text
dict
 ↓
Validate structure/type
 ↓
DTO
```

Domain:

```text
DTO
 ↓
Business rules
 ↓
Entity
```

---

# 18. Ví dụ đầy đủ

```python
from pydantic import BaseModel, Field, ValidationError


class ChapterDTO(BaseModel):
    number: int = Field(ge=1)
    title: str


class NovelDTO(BaseModel):
    title: str
    author: str
    description: str | None = None
    chapters: list[ChapterDTO] = []


raw_data = {
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "chapters": [
        {
            "number": 1,
            "title": "Tiêu Gia",
        },
        {
            "number": 2,
            "title": "Nạp Khí",
        },
    ],
}


try:
    novel = NovelDTO.model_validate(raw_data)

    print("VALID")
    print(novel)
    print(novel.chapters[0])

except ValidationError as exc:
    print("INVALID")

    for error in exc.errors():
        print(error)
```

---

# 19. Parsing JSON hoàn chỉnh

```python
json_data = """
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu",
    "chapters": [
        {
            "number": 1,
            "title": "Tiêu Gia"
        },
        {
            "number": 2,
            "title": "Nạp Khí"
        }
    ]
}
"""
```

Validate:

```python
novel = NovelDTO.model_validate_json(
    json_data
)
```

Sau đó:

```python
print(novel.title)
print(novel.chapters[1].title)
```

---

# 20. Parsing dữ liệu toàn string

Model:

```python
class CrawlRequest(BaseModel):
    url: str
    retry: int
    timeout: float
```

Data:

```python
data = {
    "url": "https://example.com",
    "retry": "3",
    "timeout": "10.5",
}
```

Dùng:

```python
request = CrawlRequest.model_validate_strings(
    data
)
```

Sau đó:

```python
print(request.retry)
print(type(request.retry))

print(request.timeout)
print(type(request.timeout))
```

Kết quả:

```text
3
<class 'int'>

10.5
<class 'float'>
```

---

# 21. Một lỗi thường gặp

Đừng làm:

```python
data = NovelDTO.model_validate_json(
    raw_dict
)
```

nếu `raw_dict` là:

```python
dict
```

`model_validate_json()` dành cho JSON data.

Nếu có:

```python
dict
```

thì:

```python
NovelDTO.model_validate(data)
```

Nếu có:

```python
JSON string
```

thì:

```python
NovelDTO.model_validate_json(json_data)
```

---

# 22. Một lỗi khác: JSON string vs Python string

Ví dụ:

```python
data = {
    "title": "ABC"
}
```

Đây là Python dict.

Còn:

```python
data = '{"title": "ABC"}'
```

đây là JSON string.

Do đó:

```text
dict
 ↓
model_validate()


JSON string
 ↓
model_validate_json()
```

---

# 23. `model_validate()` với object

Pydantic còn có khả năng validation từ object attributes khi cấu hình thích hợp.

Ví dụ:

```python
class NovelRecord:
    def __init__(self):
        self.title = "ABC"
        self.author = "XYZ"
```

DTO:

```python
from pydantic import BaseModel, ConfigDict


class NovelDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    title: str
    author: str
```

Sau đó:

```python
record = NovelRecord()

novel = NovelDTO.model_validate(
    record
)
```

Pydantic có thể đọc:

```text
record.title
record.author
```

thay vì chỉ đọc:

```text
data["title"]
data["author"]
```

---

# 24. `from_attributes=True` rất quan trọng cho ORM/Domain

Điều này sẽ hữu ích khi chúng ta học:

```text
DTO
 ↕
Mapper
 ↕
Domain Entity
```

hoặc:

```text
Database Record
 ↓
DTO
```

Ví dụ:

```text
SQLite row / ORM object
          ↓
     attributes
          ↓
   Pydantic DTO
```

Nhưng với kiến trúc Clean Architecture, tôi vẫn khuyến nghị **Mapper rõ ràng** khi domain object có ý nghĩa nghiệp vụ, thay vì để Pydantic âm thầm trở thành mapper của toàn hệ thống.

---

# 25. `model_validate()` là boundary

Đây là mental model quan trọng nhất của Buổi 7:

```text
          UNTRUSTED DATA
                │
                ▼
       model_validate()
                │
                ▼
          TRUSTED DTO
                │
                ▼
          Application
```

Ví dụ crawler:

```text
Website
   │
   ▼
HTML
   │
   ▼
selectolax Parser
   │
   ▼
dict
   │
   ▼
NovelDTO.model_validate()
   │
   ▼
Validated DTO
   │
   ▼
Mapper
   │
   ▼
Domain
```

Pydantic nằm **ở boundary**, không phải toàn bộ application.

---

# 26. Một pipeline hoàn chỉnh

Ta thử xây gần giống hệ thống crawler thực tế.

```python
from pydantic import BaseModel, Field


class ChapterDTO(BaseModel):
    number: int = Field(ge=1)
    title: str
    url: str


class NovelDTO(BaseModel):
    title: str
    author: str
    description: str | None = None
    chapters: list[ChapterDTO] = []


class NovelParser:
    def parse(self, html: str) -> dict:
        # Sau này thay bằng selectolax
        return {
            "title": "Đấu Phá Thương Khung",
            "author": "Thiên Tằm Thổ Đậu",
            "description": "Một câu chuyện tu luyện.",
            "chapters": [
                {
                    "number": 1,
                    "title": "Tiêu Gia",
                    "url": "/chuong-1",
                },
                {
                    "number": 2,
                    "title": "Nạp Khí",
                    "url": "/chuong-2",
                },
            ],
        }


parser = NovelParser()

raw_data = parser.parse("<html>...</html>")

novel_dto = NovelDTO.model_validate(
    raw_data
)

print(novel_dto)
```

Điểm quan trọng:

```text
Parser
```

không biết:

```text
NovelDTO
```

Parser chỉ trả:

```python
dict
```

Application boundary mới làm:

```python
NovelDTO.model_validate(raw_data)
```

Đây là một thiết kế rất sạch.

---

# 27. `model_validate*()` và `model_dump*()` tạo thành hai chiều

Đến đây chúng ta có:

```text
             deserialize
                 ↓
dict ─────→ Pydantic Model
                 │
                 │
                 ↓
            model_dump()
                 │
                 ▼
                dict
```

Với JSON:

```text
JSON
 │
 ▼
model_validate_json()
 │
 ▼
Model
 │
 ▼
model_dump_json()
 │
 ▼
JSON
```

Có thể nhớ:

```text
IN:
model_validate*

OUT:
model_dump*
```

---

# 28. Cheat Sheet

### Python dict → Model

```python
Model.model_validate(data)
```

### JSON → Model

```python
Model.model_validate_json(json_data)
```

### String values → Model

```python
Model.model_validate_strings(data)
```

### Object attributes → Model

```python
class Model(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )
```

---

# 29. Bài tập thực hành

## Bài 1 — dict

Tạo:

```python
data = {
    "title": "ABC",
    "author": "XYZ",
}
```

và:

```python
NovelDTO.model_validate(data)
```

---

## Bài 2 — JSON

Chuyển dữ liệu thành:

```python
json_data = """
{
    "title": "ABC",
    "author": "XYZ"
}
"""
```

và dùng:

```python
model_validate_json()
```

---

## Bài 3 — strings

Tạo:

```python
class CrawlRequest(BaseModel):
    url: str
    retry: int
    timeout: float
```

Input:

```python
data = {
    "url": "https://example.com",
    "retry": "3",
    "timeout": "10.5",
}
```

Dùng:

```python
model_validate_strings()
```

và kiểm tra:

```python
type(request.retry)
type(request.timeout)
```

---

## Bài 4 — Error

Thử:

```python
data = {
    "title": "ABC",
}
```

với:

```python
class NovelDTO(BaseModel):
    title: str
    author: str
```

Bắt:

```python
ValidationError
```

và in:

```python
error["loc"]
error["msg"]
error["type"]
```

---

# 30. Tổng kết 7 buổi đầu

Chúng ta đã có một pipeline Pydantic khá hoàn chỉnh:

```text
01 BaseModel
       │
       ▼
02 Type Annotation + Field
       │
       ▼
03 Validation
       │
       ▼
04 Nested Model
       │
       ▼
05 ConfigDict
       │
       ▼
06 Serialization
       │
       ▼
07 Parsing
```

Và đối với Novel Crawler:

```text
                    NOVEL CRAWLER

Website
   │
   ▼
HTML
   │
   ▼
Parser / selectolax
   │
   ▼
raw dict
   │
   ▼
model_validate()
   │
   ▼
NovelDTO
   │
   ├──────────────→ model_dump() → Repository/API
   │
   ▼
Mapper
   │
   ▼
Domain Entity
   │
   ▼
Use Case
   │
   ▼
Repository
```

**Buổi 8** sẽ là **Alias**: `alias`, `validation_alias`, `serialization_alias`, `AliasPath`, `AliasChoices`. Phần này đặc biệt hữu ích khi dữ liệu từ website/API có tên field khác với tên thuộc tính Python, ví dụ `book_name → title`, `book_url → url`, hoặc dữ liệu nested kiểu `{"book": {"info": {"title": "..."}}}`.
