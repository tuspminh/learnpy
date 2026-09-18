# Pydantic v2 — Buổi 4: Nested Models

> **Foundation — Buổi 4/50**

Buổi này chúng ta học một trong những khả năng quan trọng nhất của Pydantic: **mô hình hóa dữ liệu có cấu trúc lồng nhau**.

Đây là bước rất quan trọng trước khi chúng ta xây `NovelDTO`, `ChapterDTO`, `ParserResult` cho Novel Crawler.

---

# 1. Nested Model là gì?

Ở các bài trước, ta có model đơn giản:

```python
from pydantic import BaseModel


class Novel(BaseModel):
    title: str
    author: str
```

Nhưng dữ liệu thực tế thường phức tạp hơn.

Ví dụ:

```python
novel = {
    "title": "Đấu Phá Thương Khung",
    "author": {
        "name": "Thiên Tằm Thổ Đậu",
        "country": "China",
    },
}
```

Ở đây:

```text
Novel
 ├── title
 └── author
      ├── name
      └── country
```

Ta có thể biểu diễn trực tiếp bằng Pydantic.

---

# 2. Model lồng trong Model

```python
from pydantic import BaseModel


class Author(BaseModel):
    name: str
    country: str


class Novel(BaseModel):
    title: str
    author: Author
```

Sử dụng:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "author": {
        "name": "Thiên Tằm Thổ Đậu",
        "country": "China",
    },
}

novel = Novel.model_validate(data)

print(novel)
```

Kết quả:

```text
title='Đấu Phá Thương Khung'
author=Author(name='Thiên Tằm Thổ Đậu', country='China')
```

---

# 3. Truy cập Nested Model

Ta có:

```python
print(novel.title)
```

Kết quả:

```text
Đấu Phá Thương Khung
```

Và:

```python
print(novel.author)
```

Kết quả:

```text
name='Thiên Tằm Thổ Đậu' country='China'
```

Muốn lấy tên tác giả:

```python
print(novel.author.name)
```

Kết quả:

```text
Thiên Tằm Thổ Đậu
```

---

# 4. Điều gì đã xảy ra?

Input:

```text
dict
 │
 ▼
Novel.model_validate()
 │
 ├── title → str
 │
 └── author → Author
                  │
                  ├── name → str
                  └── country → str
```

Pydantic không chỉ validate `Novel`.

Nó **đệ quy validate toàn bộ cây dữ liệu**.

---

# 5. Nested Validation

Đây là điểm rất mạnh.

Ví dụ:

```python
data = {
    "title": "ĐPTK",
    "author": {
        "name": 123,
        "country": True,
    },
}
```

Pydantic sẽ validate cả:

```text
Novel.title
Novel.author.name
Novel.author.country
```

---

# 6. Nested Validation Error

Ví dụ:

```python
from pydantic import BaseModel, ValidationError


class Author(BaseModel):
    name: str
    country: str


class Novel(BaseModel):
    title: str
    author: Author


data = {
    "title": "ĐPTK",
    "author": {
        "name": 123,
        "country": True,
    },
}

try:
    novel = Novel.model_validate(data)

except ValidationError as e:
    for error in e.errors():
        print(error)
```

`loc` sẽ cho biết vị trí field.

Có thể thấy dạng:

```python
{
    "loc": ("author", "name"),
    ...
}
```

và:

```python
{
    "loc": ("author", "country"),
    ...
}
```

Đọc:

```text
author.name
author.country
```

---

# 7. Nested sâu hơn

Không giới hạn chỉ một tầng.

```python
class Publisher(BaseModel):
    name: str


class Author(BaseModel):
    name: str
    publisher: Publisher


class Novel(BaseModel):
    title: str
    author: Author
```

Dữ liệu:

```python
data = {
    "title": "ĐPTK",
    "author": {
        "name": "Thiên Tằm Thổ Đậu",
        "publisher": {
            "name": "Example Publisher"
        }
    }
}
```

Pydantic xử lý:

```text
Novel
 └── author
      ├── name
      └── publisher
           └── name
```

---

# 8. List các Model

Đây mới là phần cực kỳ quan trọng đối với crawler.

Giả sử Novel có nhiều chapter:

```python
class Chapter(BaseModel):
    number: int
    title: str


class Novel(BaseModel):
    title: str
    chapters: list[Chapter]
```

Dữ liệu:

```python
data = {
    "title": "Đấu Phá Thương Khung",
    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
        },
        {
            "number": 2,
            "title": "Chương 2",
        },
        {
            "number": 3,
            "title": "Chương 3",
        },
    ],
}
```

Validate:

```python
novel = Novel.model_validate(data)
```

---

# 9. Kết quả

```python
print(novel)
```

Ta có:

```text
title='Đấu Phá Thương Khung'
chapters=[
    Chapter(number=1, title='Chương 1'),
    Chapter(number=2, title='Chương 2'),
    Chapter(number=3, title='Chương 3')
]
```

Quan trọng nhất:

```python
print(type(novel.chapters))
```

→

```text
<class 'list'>
```

Còn:

```python
print(type(novel.chapters[0]))
```

→

```text
<class '__main__.Chapter'>
```

Tức là:

```text
list[dict]
```

đã biến thành:

```text
list[Chapter]
```

---

# 10. Truy cập từng Chapter

```python
for chapter in novel.chapters:
    print(chapter.number, chapter.title)
```

Kết quả:

```text
1 Chương 1
2 Chương 2
3 Chương 3
```

Và:

```python
chapter = novel.chapters[0]

print(chapter.number)
print(chapter.title)
```

---

# 11. Pydantic validate từng phần tử

Giả sử:

```python
data = {
    "title": "ĐPTK",
    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
        },
        {
            "number": "abc",
            "title": "Chương 2",
        },
    ],
}
```

Pydantic sẽ phát hiện:

```text
chapters[1].number
```

Thông tin `loc` sẽ có dạng tương tự:

```python
("chapters", 1, "number")
```

Đọc là:

```text
Novel
 └── chapters
      └── index 1
           └── number
```

---

# 12. `dict[str, Model]`

Pydantic cũng hỗ trợ dictionary chứa model.

Ví dụ:

```python
class Chapter(BaseModel):
    number: int
    title: str


class Novel(BaseModel):
    title: str
    chapters: dict[str, Chapter]
```

Dữ liệu:

```python
data = {
    "title": "ĐPTK",
    "chapters": {
        "chapter-1": {
            "number": 1,
            "title": "Chương 1",
        },
        "chapter-2": {
            "number": 2,
            "title": "Chương 2",
        },
    },
}
```

Pydantic sẽ tạo:

```text
dict[str, Chapter]
```

---

# 13. Truy cập

```python
novel = Novel.model_validate(data)

chapter = novel.chapters["chapter-1"]

print(chapter)
```

Kết quả:

```text
number=1 title='Chương 1'
```

---

# 14. List lồng trong List

Pydantic có thể biểu diễn cấu trúc phức tạp.

Ví dụ:

```python
class Page(BaseModel):
    number: int
    content: str


class Chapter(BaseModel):
    number: int
    title: str
    pages: list[Page]


class Novel(BaseModel):
    title: str
    chapters: list[Chapter]
```

Cấu trúc:

```text
Novel
 │
 └── chapters: list[Chapter]
                    │
                    └── pages: list[Page]
```

Dữ liệu:

```python
data = {
    "title": "ĐPTK",
    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
            "pages": [
                {
                    "number": 1,
                    "content": "Nội dung trang 1"
                },
                {
                    "number": 2,
                    "content": "Nội dung trang 2"
                }
            ]
        }
    ]
}
```

Pydantic có thể validate toàn bộ cây.

---

# 15. Nested Model trong Novel Crawler

Đây là lúc kiến thức bắt đầu kết nối với project của bạn.

Thay vì:

```python
novel = {
    "title": "...",
    "author": "...",
    "chapters": [...]
}
```

ta có thể thiết kế:

```python
class AuthorDTO(BaseModel):
    name: str


class ChapterDTO(BaseModel):
    number: int
    title: str
    url: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
    chapters: list[ChapterDTO]
```

---

# 16. Ví dụ hoàn chỉnh

```python
from pydantic import BaseModel


class AuthorDTO(BaseModel):
    name: str


class ChapterDTO(BaseModel):
    number: int
    title: str
    url: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
    chapters: list[ChapterDTO]


data = {
    "title": "Đấu Phá Thương Khung",

    "author": {
        "name": "Thiên Tằm Thổ Đậu",
    },

    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
            "url": "/chuong-1",
        },
        {
            "number": 2,
            "title": "Chương 2",
            "url": "/chuong-2",
        },
        {
            "number": 3,
            "title": "Chương 3",
            "url": "/chuong-3",
        },
    ],
}


novel = NovelDTO.model_validate(data)


print("Novel:", novel.title)
print("Author:", novel.author.name)

for chapter in novel.chapters:
    print(
        chapter.number,
        chapter.title,
        chapter.url,
    )
```

Output:

```text
Novel: Đấu Phá Thương Khung
Author: Thiên Tằm Thổ Đậu
1 Chương 1 /chuong-1
2 Chương 2 /chuong-2
3 Chương 3 /chuong-3
```

---

# 17. Nested Model không nhất thiết phải nhận dict

Ví dụ:

```python
author = AuthorDTO(
    name="Thiên Tằm Thổ Đậu"
)

chapter = ChapterDTO(
    number=1,
    title="Chương 1",
    url="/chuong-1"
)
```

Sau đó:

```python
novel = NovelDTO(
    title="ĐPTK",
    author=author,
    chapters=[chapter],
)
```

Điều này hoàn toàn hợp lệ.

Pydantic nhận object model đã được validate.

---

# 18. Model có thể được tạo trực tiếp

```python
novel = NovelDTO(
    title="ĐPTK",
    author={
        "name": "Thiên Tằm Thổ Đậu"
    },
    chapters=[
        {
            "number": 1,
            "title": "Chương 1",
            "url": "/chuong-1"
        }
    ]
)
```

Pydantic tự tạo:

```text
author → AuthorDTO
chapters[0] → ChapterDTO
```

---

# 19. `model_dump()` với Nested Model

Sau khi đã có:

```python
novel = NovelDTO.model_validate(data)
```

ta có thể:

```python
result = novel.model_dump()

print(result)
```

Kết quả là dictionary:

```python
{
    "title": "Đấu Phá Thương Khung",
    "author": {
        "name": "Thiên Tằm Thổ Đậu"
    },
    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
            "url": "/chuong-1"
        }
    ]
}
```

Chú ý:

```text
Pydantic Model
      ↓
model_dump()
      ↓
dict
```

---

# 20. `model_dump_json()`

Nếu cần JSON:

```python
json_data = novel.model_dump_json()

print(json_data)
```

Kết quả dạng:

```json
{
  "title": "Đấu Phá Thương Khung",
  "author": {
    "name": "Thiên Tằm Thổ Đậu"
  },
  "chapters": [
    {
      "number": 1,
      "title": "Chương 1",
      "url": "/chuong-1"
    }
  ]
}
```

---

# 21. Một lỗi thiết kế cần tránh

Giả sử bạn có:

```python
class NovelDTO(BaseModel):
    title: str
    chapters: list[ChapterDTO]
```

Không nên biến `ChapterDTO` thành một object chứa:

```python
def save_to_database():
    ...
    
def download():
    ...
    
def crawl():
    ...
```

DTO chỉ nên biểu diễn **data contract**.

Ví dụ tốt:

```text
ChapterDTO
    ↓
Mapper
    ↓
Chapter Entity
    ↓
Domain logic
```

---

# 22. DTO và Domain Entity

Đây là kiến trúc chúng ta sẽ tiếp tục xây:

```text
                Parser
                  │
                  ▼
             raw dict
                  │
                  ▼
        ┌──────────────────┐
        │   NovelDTO       │
        │   Pydantic       │
        └────────┬─────────┘
                 │
               Mapper
                 │
                 ▼
        ┌──────────────────┐
        │   Novel Entity   │
        │     Domain       │
        └────────┬─────────┘
                 │
                 ▼
             Use Case
                 │
                 ▼
            Repository
```

Nested DTO:

```text
NovelDTO
 ├── AuthorDTO
 └── list[ChapterDTO]
```

Domain:

```text
Novel
 ├── Author
 └── list[Chapter]
```

Hai bên có thể có cấu trúc tương tự nhưng **không nhất thiết là cùng một class**.

---

# 23. Nested Model và `ValidationError`

Hãy thử một dữ liệu lỗi:

```python
data = {
    "title": "ĐPTK",
    "author": {
        "name": "Thiên Tằm"
    },
    "chapters": [
        {
            "number": 1,
            "title": "Chương 1",
            "url": "/1"
        },
        {
            "number": "abc",
            "title": "Chương 2",
            "url": "/2"
        }
    ]
}
```

Validation:

```python
from pydantic import ValidationError

try:
    novel = NovelDTO.model_validate(data)

except ValidationError as e:
    for error in e.errors():
        print(error)
```

Bạn sẽ thấy vị trí lỗi nằm trong:

```text
chapters
   ↓
index 1
   ↓
number
```

Tức:

```python
("chapters", 1, "number")
```

Đây là một trong những lý do Pydantic rất hữu ích cho parser.

---

# 24. Một pattern rất hữu ích

Trong parser:

```python
raw_data = parser.parse()
```

Kết quả:

```python
{
    "title": "...",
    "author": {...},
    "chapters": [...]
}
```

Sau đó:

```python
dto = NovelDTO.model_validate(raw_data)
```

Từ thời điểm đó trở đi:

```text
dto.title
dto.author.name
dto.chapters[0].title
```

đều có type rõ ràng.

IDE cũng hiểu:

```text
dto
 ├── title: str
 ├── author: AuthorDTO
 │      └── name: str
 │
 └── chapters: list[ChapterDTO]
              ├── number: int
              ├── title: str
              └── url: str
```

Đây chính là lợi ích rất lớn so với việc truyền `dict` xuyên suốt application.

---

# 25. Ví dụ thực tế hơn cho Novel Crawler

Ta có thể thiết kế bước đầu:

```python
from pydantic import BaseModel


class ChapterDTO(BaseModel):
    number: int
    title: str
    url: str


class NovelDTO(BaseModel):
    title: str
    author: str
    url: str
    cover: str | None = None
    description: str | None = None
    chapters: list[ChapterDTO] = []
```

**Nhưng có một vấn đề ở đây:** viết:

```python
chapters: list[ChapterDTO] = []
```

không phải cách chúng ta muốn dùng cho mọi trường hợp.

Ở các bài sau khi học sâu hơn về default values và `Field`, chúng ta sẽ xử lý cấu trúc này đúng cách, thường bằng `default_factory`.

Ví dụ:

```python
from pydantic import BaseModel, Field


class NovelDTO(BaseModel):
    title: str
    chapters: list[ChapterDTO] = Field(default_factory=list)
```

Điểm này chúng ta sẽ đào sâu sau.

---

# 26. Nested Model với Optional

Ví dụ novel chưa có thông tin tác giả:

```python
class AuthorDTO(BaseModel):
    name: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO | None = None
```

Có thể:

```python
novel = NovelDTO(
    title="ĐPTK"
)
```

Sau đó:

```python
print(novel.author)
```

→

```text
None
```

Nhưng nếu có:

```python
novel = NovelDTO(
    title="ĐPTK",
    author={
        "name": "Thiên Tằm"
    }
)
```

Pydantic tạo:

```text
AuthorDTO(name='Thiên Tằm')
```

---

# 27. Mô hình hóa JSON thực tế

Giả sử API trả:

```json
{
    "data": {
        "novel": {
            "title": "ĐPTK",
            "author": {
                "name": "Thiên Tằm"
            }
        }
    }
}
```

Ta có thể mô hình hóa:

```python
class Author(BaseModel):
    name: str


class Novel(BaseModel):
    title: str
    author: Author


class Data(BaseModel):
    novel: Novel


class Response(BaseModel):
    data: Data
```

Sau đó:

```python
response = Response.model_validate(json_data)
```

Truy cập:

```python
response.data.novel.title
```

---

# 28. Tư duy quan trọng

Khi gặp JSON/dict phức tạp, hãy nhìn nó như **cây dữ liệu**.

Ví dụ:

```text
Response
 │
 └── data
      │
      └── novel
           ├── title
           ├── author
           │    └── name
           │
           └── chapters
                │
                ├── Chapter
                ├── Chapter
                └── Chapter
```

Sau đó chuyển từng node thành Model.

Đừng cố nhồi toàn bộ thành một model khổng lồ.

---

# 29. Mini Project Buổi 4

Hãy xây:

```text
NovelResponse
 └── novel
      ├── title
      ├── author
      │    ├── name
      │    └── url
      │
      └── chapters
           ├── ChapterDTO
           ├── ChapterDTO
           └── ChapterDTO
```

Code khung:

```python
from pydantic import BaseModel


class AuthorDTO(BaseModel):
    name: str
    url: str


class ChapterDTO(BaseModel):
    number: int
    title: str
    url: str


class NovelDTO(BaseModel):
    title: str
    author: AuthorDTO
    chapters: list[ChapterDTO]


class NovelResponse(BaseModel):
    novel: NovelDTO
```

Test bằng:

```python
data = {
    "novel": {
        "title": "Đấu Phá Thương Khung",
        "author": {
            "name": "Thiên Tằm Thổ Đậu",
            "url": "/author/thien-tam-tho-dau",
        },
        "chapters": [
            {
                "number": "1",
                "title": "Chương 1",
                "url": "/chuong-1",
            },
            {
                "number": "2",
                "title": "Chương 2",
                "url": "/chuong-2",
            },
        ],
    }
}
```

Sau đó:

```python
response = NovelResponse.model_validate(data)
```

Test:

```python
print(response.novel.title)
print(response.novel.author.name)

for chapter in response.novel.chapters:
    print(chapter.number, chapter.title)
```

Đặc biệt kiểm tra:

```python
print(type(response.novel.author))
print(type(response.novel.chapters))
print(type(response.novel.chapters[0]))
print(type(response.novel.chapters[0].number))
```

Bạn sẽ thấy:

```text
AuthorDTO
list
ChapterDTO
int
```

---

# 30. Những gì cần nhớ sau Buổi 4

```text
Nested Model
│
├── Model trong Model
│
├── list[Model]
│
├── dict[str, Model]
│
├── Nested Validation
│
├── Nested ValidationError
│
├── model_dump()
│
└── model_dump_json()
```

Quan trọng nhất:

```python
class Novel(BaseModel):
    author: Author
    chapters: list[Chapter]
```

Pydantic hiểu rằng:

```text
author
    ↓
Author model

chapters
    ↓
list
    ↓
Chapter model
```

và tự động validate toàn bộ cấu trúc.

---

## Sơ đồ kiến trúc cần nhớ

```text
                    raw dict / JSON
                          │
                          ▼
                  NovelResponse
                       Pydantic
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
             NovelDTO          metadata
                 │
          ┌──────┴──────┐
          ▼             ▼
      AuthorDTO    list[ChapterDTO]
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Chapter       Chapter      Chapter
```

**Buổi 5** chúng ta sẽ học **Model Configuration với `ConfigDict`** — một phần rất quan trọng của Pydantic v2: `extra`, `strict`, `validate_assignment`, `frozen`, `populate_by_name`, và cách quyết định model của bạn nên **linh hoạt hay nghiêm ngặt**.
