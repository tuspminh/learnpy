# Pydantic v2 — Buổi 6: Serialization với `model_dump()` và `model_dump_json()`

Hôm nay chúng ta học **Serialization** — tức là chuyển một Pydantic model thành dữ liệu có thể:

* lưu SQLite/JSON
* gửi qua HTTP API
* ghi log
* truyền giữa các layer
* lưu cache
* export dữ liệu crawler

Đây là phần rất quan trọng với kiến trúc Novel Crawler của bạn.

---

# 1. Serialization là gì?

Giả sử có:

```python
from pydantic import BaseModel


class NovelDTO(BaseModel):
    title: str
    author: str
```

Tạo model:

```python
novel = NovelDTO(
    title="Đấu Phá Thương Khung",
    author="Thiên Tằm Thổ Đậu",
)
```

Trong Python:

```text
NovelDTO object
      │
      │ serialization
      ▼
   dict / JSON
```

Ví dụ:

```python
novel.model_dump()
```

→ `dict`

Hoặc:

```python
novel.model_dump_json()
```

→ JSON string.

---

# 2. `model_dump()`

Đây là API serialization quan trọng nhất.

```python
data = novel.model_dump()

print(data)
```

Kết quả:

```python
{
    "title": "Đấu Phá Thương Khung",
    "author": "Thiên Tằm Thổ Đậu"
}
```

Kiểu dữ liệu:

```python
print(type(data))
```

Kết quả:

```text
<class 'dict'>
```

---

# 3. `model_dump()` không trả về JSON

Điểm này rất quan trọng.

```python
data = novel.model_dump()
```

là:

```text
Pydantic Model
      ↓
Python dict
```

Không phải:

```text
Pydantic Model
      ↓
JSON
```

Nếu cần JSON:

```python
json_data = novel.model_dump_json()
```

---

# 4. `model_dump_json()`

Ví dụ:

```python
json_data = novel.model_dump_json()

print(json_data)
```

Kết quả dạng:

```json
{"title":"Đấu Phá Thương Khung","author":"Thiên Tằm Thổ Đậu"}
```

Kiểu:

```python
print(type(json_data))
```

→

```text
<class 'str'>
```

Nhớ:

```text
model_dump()
      ↓
dict

model_dump_json()
      ↓
JSON string
```

---

# 5. Khi nào dùng cái nào?

### `model_dump()`

Dùng khi cần Python object:

```text
Repository
Database
Application layer
Mapper
Logic Python
```

Ví dụ:

```python
data = novel.model_dump()

repository.save(data)
```

---

### `model_dump_json()`

Dùng khi cần JSON:

```text
HTTP
API
JSON file
Cache
Message queue
Logging
```

Ví dụ:

```python
json_text = novel.model_dump_json()
```

---

# 6. Nested Model

Đây là trường hợp quan trọng với crawler.

```python
from pydantic import BaseModel


class AuthorDTO(BaseModel):
    name: str


class ChapterDTO(BaseModel):
    number: int
    title: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
    chapters: list[ChapterDTO]
```

Tạo:

```python
novel = NovelDTO(
    title="Đấu Phá Thương Khung",

    author={
        "name": "Thiên Tằm Thổ Đậu"
    },

    chapters=[
        {
            "number": 1,
            "title": "Tiêu Gia",
        },
        {
            "number": 2,
            "title": "Nạp Khí",
        },
    ],
)
```

---

# 7. Dump nested model

```python
data = novel.model_dump()

print(data)
```

Kết quả:

```python
{
    "title": "Đấu Phá Thương Khung",

    "author": {
        "name": "Thiên Tằm Thổ Đậu"
    },

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
```

Pydantic tự serialize toàn bộ cây model:

```text
NovelDTO
 │
 ├── AuthorDTO
 │
 └── list[ChapterDTO]
          │
          ├── ChapterDTO
          └── ChapterDTO
```

→

```text
dict
 │
 ├── dict
 │
 └── list[dict]
```

---

# 8. `model_dump_json()`

```python
print(novel.model_dump_json())
```

Kết quả:

```json
{
  "title": "Đấu Phá Thương Khung",
  "author": {
    "name": "Thiên Tằm Thổ Đậu"
  },
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
```

JSON serialization cũng xử lý nested model.

---

# 9. `exclude_none`

Đây là option rất hay dùng.

Ví dụ:

```python
class NovelDTO(BaseModel):
    title: str
    description: str | None = None
    cover: str | None = None
```

Tạo:

```python
novel = NovelDTO(
    title="ABC"
)
```

Dump bình thường:

```python
print(novel.model_dump())
```

Kết quả:

```python
{
    "title": "ABC",
    "description": None,
    "cover": None
}
```

---

# 10. `exclude_none=True`

```python
data = novel.model_dump(
    exclude_none=True
)
```

Kết quả:

```python
{
    "title": "ABC"
}
```

Các field:

```text
description = None
cover = None
```

bị loại bỏ.

---

# 11. Rất hữu ích cho API

Ví dụ response:

```python
response = novel.model_dump(
    exclude_none=True
)
```

Thay vì:

```json
{
    "title": "ABC",
    "description": null,
    "cover": null
}
```

có thể trả:

```json
{
    "title": "ABC"
}
```

Tuy nhiên việc có nên bỏ `null` hay không phụ thuộc API contract.

---

# 12. `exclude_defaults`

Ví dụ:

```python
from pydantic import BaseModel


class CrawlConfig(BaseModel):
    retry: int = 3
    timeout: int = 30
    verify_ssl: bool = True
```

Tạo:

```python
config = CrawlConfig(
    retry=3,
    timeout=30,
    verify_ssl=True,
)
```

Dump bình thường:

```python
config.model_dump()
```

→

```python
{
    "retry": 3,
    "timeout": 30,
    "verify_ssl": True
}
```

---

# 13. `exclude_defaults=True`

```python
config.model_dump(
    exclude_defaults=True
)
```

Nếu mọi giá trị vẫn là default:

```python
{}
```

Tức là:

> Loại bỏ các field đang có giá trị bằng default.

---

# 14. `exclude_unset`

Đây là một option rất quan trọng nhưng dễ nhầm.

```python
class NovelDTO(BaseModel):
    title: str
    description: str | None = None
    status: str = "ongoing"
```

Tạo:

```python
novel = NovelDTO(
    title="ABC"
)
```

`description` và `status` không được truyền vào.

Nếu:

```python
novel.model_dump()
```

thì vẫn có:

```python
{
    "title": "ABC",
    "description": None,
    "status": "ongoing"
}
```

---

# 15. `exclude_unset=True`

```python
novel.model_dump(
    exclude_unset=True
)
```

Kết quả:

```python
{
    "title": "ABC"
}
```

Vì chỉ `title` được user/input truyền vào.

---

# 16. `exclude_unset` khác `exclude_defaults`

Đây là phần cần nhớ.

### `exclude_unset`

> Field có được set khi tạo model hay không?

### `exclude_defaults`

> Giá trị hiện tại có bằng default hay không?

Ví dụ:

```python
class Config(BaseModel):
    retry: int = 3
```

Trường hợp:

```python
config = Config()
```

`retry`:

```text
unset
default = 3
```

---

Nếu:

```python
config = Config(retry=3)
```

thì:

```text
retry
set
value = default
```

Do đó hai option có thể cho kết quả khác nhau.

---

# 17. Bảng so sánh

| Option                  | Ý nghĩa                        |
| ----------------------- | ------------------------------ |
| `exclude_none=True`     | bỏ field có value `None`       |
| `exclude_defaults=True` | bỏ field có value bằng default |
| `exclude_unset=True`    | bỏ field chưa được set         |
| không option            | giữ tất cả                     |

Đây là 3 option serialization bạn nên thuộc.

---

# 18. `include`

Có thể chỉ lấy một số field.

```python
data = novel.model_dump(
    include={
        "title",
        "author",
    }
)
```

Kết quả:

```python
{
    "title": "ABC",
    "author": "XYZ"
}
```

---

# 19. `exclude`

Ngược lại:

```python
data = novel.model_dump(
    exclude={
        "chapters"
    }
)
```

Kết quả sẽ không có:

```text
chapters
```

---

# 20. `include` và `exclude`

Hãy nhớ:

```text
include
   ↓
chỉ lấy những gì chỉ định

exclude
   ↓
lấy tất cả trừ những gì chỉ định
```

---

# 21. Nested include/exclude

Đây là phần rất hữu ích.

Ví dụ:

```python
class AuthorDTO(BaseModel):
    name: str
    country: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
```

Ta chỉ muốn:

```text
title
author.name
```

Có thể sử dụng nested include.

Ý tưởng:

```python
novel.model_dump(
    include={
        "title",
        "author": {"name"},
    }
)
```

Kết quả:

```python
{
    "title": "ABC",
    "author": {
        "name": "XYZ"
    }
}
```

---

# 22. Nested exclude

Ví dụ:

```python
novel.model_dump(
    exclude={
        "author": {"country"}
    }
)
```

Kết quả:

```python
{
    "title": "ABC",
    "author": {
        "name": "XYZ"
    }
}
```

---

# 23. List nested model

Với list:

```python
class NovelDTO(BaseModel):
    chapters: list[ChapterDTO]
```

Có thể áp dụng exclude/include tới nested data.

Đây là lúc cú pháp của Pydantic bắt đầu mạnh nhưng cũng phức tạp hơn.

Trong application thực tế, nếu mapping quá phức tạp, đôi khi **viết mapper riêng sẽ dễ đọc hơn** thay vì nhồi quá nhiều logic vào `model_dump()`.

Đây là điểm phù hợp với cách chúng ta đang thiết kế Clean Architecture.

---

# 24. `model_dump(mode="json")`

Có một điểm rất quan trọng:

```python
novel.model_dump()
```

mặc định trả Python representation.

Ta cũng có thể yêu cầu JSON-compatible representation:

```python
novel.model_dump(
    mode="json"
)
```

Điều này hữu ích với các kiểu đặc biệt như:

```text
datetime
UUID
URL
Decimal
Enum
```

Ví dụ sau này chúng ta sẽ gặp:

```python
from datetime import datetime

from pydantic import BaseModel


class ChapterDTO(BaseModel):
    published_at: datetime
```

Khi:

```python
chapter.model_dump(mode="json")
```

Pydantic sẽ tạo representation phù hợp để đưa vào JSON.

---

# 25. `model_dump_json()` thực chất là bước tiếp theo

Có thể hình dung:

```text
Pydantic Model
      │
      ▼
model_dump(mode="json")
      │
      ▼
JSON-compatible Python data
      │
      ▼
JSON serialization
      │
      ▼
model_dump_json()
```

Không cần hiểu implementation nội bộ ở mức này; chỉ cần nhớ API sử dụng.

---

# 26. Serialization trong Novel Crawler

Đây là phần quan trọng nhất đối với project của bạn.

Giả sử:

```python
class NovelDTO(BaseModel):
    title: str
    author: str
    description: str | None = None
    chapters: list[ChapterDTO] = []
```

Sau parser:

```text
HTML
 ↓
Parser
 ↓
NovelDTO
```

Nếu cần database:

```python
data = novel.model_dump()
```

Sau đó mapper/repository xử lý:

```text
NovelDTO
   ↓
model_dump()
   ↓
dict
   ↓
Repository
   ↓
SQLite
```

---

# 27. Nhưng đừng đưa `model_dump()` thẳng vào SQLite

Ví dụ:

```python
repository.save(
    novel.model_dump()
)
```

có thể hoạt động trong một số thiết kế, nhưng về kiến trúc lâu dài không nên để Repository phụ thuộc vào cấu trúc Pydantic DTO.

Tốt hơn:

```text
Pydantic DTO
      ↓
   Mapper
      ↓
Domain Entity
      ↓
Repository
```

Ví dụ:

```python
novel_entity = mapper.to_domain(novel_dto)

repository.save(novel_entity)
```

Serialization phục vụ **boundary**, không nên trở thành cách né tránh Domain Model.

---

# 28. DTO → JSON

Trường hợp này hợp lý:

```python
json_text = novel_dto.model_dump_json()
```

Ví dụ API hoặc cache:

```text
NovelDTO
   ↓
model_dump_json()
   ↓
JSON
   ↓
HTTP / Cache / File
```

---

# 29. Ví dụ hoàn chỉnh

Tạo file:

```text
lesson_06.py
```

Code:

```python
from pydantic import BaseModel, Field


class AuthorDTO(BaseModel):
    name: str
    country: str | None = None


class ChapterDTO(BaseModel):
    number: int = Field(ge=1)
    title: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
    description: str | None = None
    status: str = "ongoing"
    chapters: list[ChapterDTO] = Field(
        default_factory=list
    )


novel = NovelDTO(
    title="Đấu Phá Thương Khung",

    author={
        "name": "Thiên Tằm Thổ Đậu",
    },

    chapters=[
        {
            "number": 1,
            "title": "Tiêu Gia",
        },
        {
            "number": 2,
            "title": "Nạp Khí",
        },
    ],
)


print("=== MODEL ===")
print(novel)


print("\n=== model_dump ===")
print(novel.model_dump())


print("\n=== model_dump_json ===")
print(novel.model_dump_json())


print("\n=== exclude_none ===")
print(
    novel.model_dump(
        exclude_none=True
    )
)


print("\n=== exclude_defaults ===")
print(
    novel.model_dump(
        exclude_defaults=True
    )
)


print("\n=== exclude_unset ===")
print(
    novel.model_dump(
        exclude_unset=True
    )
)


print("\n=== include ===")
print(
    novel.model_dump(
        include={
            "title",
            "author",
        }
    )
)


print("\n=== exclude ===")
print(
    novel.model_dump(
        exclude={
            "chapters",
        }
    )
)
```

Chạy:

```bash
python lesson_06.py
```

---

# 30. Bài tập thực hành

Từ model trên, hãy thực hiện 5 yêu cầu.

### Bài 1

Chỉ lấy:

```text
title
author
```

---

### Bài 2

Loại bỏ:

```text
description
chapters
```

---

### Bài 3

Loại bỏ tất cả `None`.

---

### Bài 4

Chuyển toàn bộ NovelDTO thành JSON.

---

### Bài 5 — quan trọng

Tạo:

```python
novel = NovelDTO(
    title="ABC",
    author={
        "name": "XYZ"
    }
)
```

So sánh:

```python
novel.model_dump()
```

với:

```python
novel.model_dump(
    exclude_none=True
)
```

và:

```python
novel.model_dump(
    exclude_unset=True
)
```

Quan sát sự khác nhau giữa:

```text
None
default
unset
```

---

# 31. Mental Model của Buổi 6

Hãy nhớ sơ đồ này:

```text
                    Pydantic Model
                          │
              ┌───────────┴───────────┐
              │                       │
       model_dump()          model_dump_json()
              │                       │
              ▼                       ▼
            dict                  JSON str
              │                       │
       Python / DB / Mapper      HTTP / File / API
```

Và:

```text
model_dump()
   │
   ├── include
   ├── exclude
   ├── exclude_none
   ├── exclude_defaults
   ├── exclude_unset
   └── mode="json"
```

---

# 32. Những API cần thuộc lòng

Sau Buổi 6, tối thiểu phải nhớ:

```python
model.model_dump()
```

```python
model.model_dump_json()
```

```python
model.model_dump(
    exclude_none=True
)
```

```python
model.model_dump(
    exclude_defaults=True
)
```

```python
model.model_dump(
    exclude_unset=True
)
```

```python
model.model_dump(
    include={"title"}
)
```

```python
model.model_dump(
    exclude={"chapters"}
)
```

Đây là bộ API serialization nền tảng của Pydantic v2.

---

## Roadmap hiện tại

```text
01  BaseModel + Validation
02  Field + Type Annotation       ✓
03  Validation + Strict           ✓
04  Nested Models                 ✓
05  ConfigDict                    ✓
06  Serialization                 ← hôm nay
07  Parsing
08  Alias
09  field_validator
10  model_validator
```

**Buổi 7** sẽ học **Parsing trong Pydantic v2**: `model_validate()`, `model_validate_json()`, `model_validate_strings()`, cách đưa `dict`, JSON và dữ liệu dạng string vào DTO, và đặc biệt là cách áp dụng nó vào pipeline **HTML Parser → NovelDTO**.
