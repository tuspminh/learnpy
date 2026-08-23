# Buổi 21 — Domain Model Deep Dive

Hôm nay chúng ta đi sâu vào **Domain Layer** của Story Crawler System.

Nếu Buổi 20 là dựng bộ khung:

```text
CLI
 ↓
Application
 ↓
Domain
 ↑
Infrastructure
```

thì hôm nay chúng ta tập trung vào:

```text
Domain
│
├── Story
├── Chapter
├── Value Object
├── Entity
├── Domain Rule
├── Invariant
└── Domain Service
```

Mục tiêu quan trọng nhất:

> **Domain phải mô tả nghiệp vụ "truyện" mà không biết hệ thống lưu bằng SQLite, crawl bằng requests hay giao diện bằng CLI/PySide6.**

---

# 1. Domain Model là gì?

Một cách hiểu đơn giản:

```text
Domain Model
=
mô hình hóa những khái niệm và quy tắc
của bài toán
```

Trong Story Crawler:

```text
Story
Chapter
Source
URL
Chapter Number
Story Status
```

là các khái niệm domain.

Ví dụ:

```python
@dataclass
class Story:
    title: str
    source: str
    url: str
```

Đây là domain model rất đơn giản.

Nhưng nó chưa thật sự mạnh.

---

# 2. Primitive Obsession

Một vấn đề phổ biến:

```python
@dataclass
class Story:
    title: str
    source: str
    url: str
```

Mọi thứ đều là:

```text
str
```

Ta có:

```python
story.title
story.source
story.url
```

Python cho phép:

```python
story.url = ""
story.title = ""
story.source = ""
```

Domain không tự bảo vệ được.

Đây là một dạng:

> **Primitive Obsession**

---

# 3. URL nên là gì?

Thay vì:

```python
url: str
```

ta có thể tạo:

```python
@dataclass(frozen=True)
class Url:

    value: str
```

Nhưng chưa đủ.

Ta muốn:

```python
Url("")
```

bị reject.

---

# 4. Value Object đầu tiên

```python
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Url:

    value: str

    def __post_init__(self):

        parsed = urlparse(self.value)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use HTTP or HTTPS"
            )

        if not parsed.netloc:
            raise ValueError(
                "URL must have a host"
            )
```

Bây giờ:

```python
url = Url(
    "https://source-a.com/story/1"
)
```

hợp lệ.

Nhưng:

```python
Url("")
```

sẽ lỗi.

---

# 5. Vì sao đây là Value Object?

`Url` không có identity riêng.

Hai object:

```python
Url(
    "https://example.com"
)
```

và:

```python
Url(
    "https://example.com"
)
```

có cùng giá trị.

```python
a == b
```

là `True`.

Đây là đặc trưng của Value Object:

> **Identity không quan trọng; value quan trọng.**

---

# 6. `dataclass(frozen=True)`

Ta dùng:

```python
@dataclass(frozen=True)
```

để Value Object immutable.

Không muốn:

```python
url.value = "..."
```

sau khi tạo.

Điều này giúp domain invariant dễ bảo vệ hơn.

---

# 7. Source cũng có thể là Value Object

Hiện tại:

```python
source: str
```

Ta có thể:

```python
@dataclass(frozen=True)
class Source:

    name: str

    def __post_init__(self):

        if not self.name.strip():
            raise ValueError(
                "Source cannot be empty"
            )
```

Sau đó:

```python
Source("source_a")
```

---

# 8. Story Entity

Bây giờ Story:

```python
from dataclasses import dataclass


@dataclass
class Story:

    title: str
    source: Source
    url: Url
```

Ví dụ:

```python
story = Story(
    title="Đấu Phá Thương Khung",
    source=Source("source_a"),
    url=Url(
        "https://source-a.com/story/1"
    ),
)
```

Domain model đã mạnh hơn.

---

# 9. Entity khác Value Object thế nào?

Đây là phần cực kỳ quan trọng trong DDD.

### Value Object

```text
Url
Source
ChapterNumber
```

Quan trọng:

```text
value
```

### Entity

```text
Story
Chapter
```

Quan trọng:

```text
identity
```

Ví dụ hai chapter:

```text
Chapter ID = 101
title = "Khởi đầu"
```

và:

```text
Chapter ID = 102
title = "Khởi đầu"
```

có thể có cùng title nhưng vẫn là **hai Entity khác nhau**.

---

# 10. Story cần Identity

Thay vì:

```python
@dataclass
class Story:
    title: str
    source: Source
    url: Url
```

ta có:

```python
from dataclasses import dataclass


@dataclass
class Story:

    id: int | None
    title: str
    source: Source
    url: Url
```

Nhưng có một vấn đề:

> Có nên để `id` là database ID?

Chưa chắc.

---

# 11. Database Identity vs Domain Identity

Đây là distinction rất quan trọng.

Database:

```text
id = 123
```

là:

> persistence identity.

Domain có thể cần:

```text
source + canonical URL
```

làm business identity.

Ví dụ:

```text
source_a
https://source-a.com/story/123
```

xác định một Story.

Do đó:

```python
@dataclass
class Story:

    source: Source
    url: Url
    title: str
```

có thể đủ trong domain.

SQLite tự có:

```text
INTEGER PRIMARY KEY
```

ở Infrastructure.

---

# 12. Canonical URL

Crawler thường gặp:

```text
https://source-a.com/story/123
https://source-a.com/story/123/
https://source-a.com/story/123?ref=home
```

Có thể chúng đều chỉ cùng một Story.

Đây là **domain rule**.

Ta có thể tạo:

```python
@dataclass(frozen=True)
class StoryUrl:

    value: str

    def __post_init__(self):
        ...
```

và canonicalize.

Ví dụ:

```python
from urllib.parse import urlparse


def canonicalize(url: str) -> str:

    parsed = urlparse(url)

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"{parsed.path.rstrip('/')}"
    )
```

---

# 13. Không nên nhét mọi thứ vào Value Object

Đây là chỗ cần cẩn thận.

Không phải:

```text
str
 ↓
class StringValueObject
```

Tất cả đều phải thành class.

Chỉ tạo Value Object khi nó có:

* validation
* invariant
* behavior
* domain meaning

Ví dụ:

```python
Url
Source
ChapterNumber
```

hợp lý.

Nhưng:

```python
Title
```

có thể chưa cần.

---

# 14. Chapter Number

Giả sử chapter phải có số:

```text
1
2
3
4
...
```

Không được:

```text
0
-1
```

Tạo:

```python
@dataclass(frozen=True)
class ChapterNumber:

    value: int

    def __post_init__(self):

        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )
```

Bây giờ:

```python
ChapterNumber(1)
```

OK.

```python
ChapterNumber(0)
```

Error.

---

# 15. Chapter Entity

```python
@dataclass
class Chapter:

    number: ChapterNumber
    title: str
    url: Url
    content: str
```

Ta đang có:

```text
Story
│
├── Source
├── StoryUrl
│
└── Chapter
      ├── ChapterNumber
      ├── title
      ├── Url
      └── content
```

---

# 16. Story Aggregate

Đây là bước quan trọng.

Một Story có:

```text
Story
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 └── ...
```

Ta có thể coi:

```text
Story
```

là Aggregate Root.

---

# 17. Aggregate Root là gì?

Aggregate là:

> Một cụm Entity/Value Object được quản lý như một đơn vị nhất quán.

Root:

```text
Story
```

bên trong:

```text
Chapter
```

Không nên để mọi nơi tự ý sửa Chapter.

Thay vì:

```python
story.chapters.append(...)
```

ta có behavior:

```python
story.add_chapter(chapter)
```

---

# 18. Story Aggregate

```python
@dataclass
class Story:

    title: str
    source: Source
    url: Url

    _chapters: list[Chapter] = field(
        default_factory=list,
        repr=False,
    )

    @property
    def chapters(self):
        return tuple(self._chapters)

    def add_chapter(
        self,
        chapter: Chapter,
    ) -> None:

        if any(
            item.number == chapter.number
            for item in self._chapters
        ):
            raise ValueError(
                "Chapter already exists"
            )

        self._chapters.append(
            chapter
        )
```

---

# 19. Đây là Domain Behavior

Ta không chỉ có:

```python
story.title
story.url
```

mà Story có behavior:

```python
story.add_chapter(...)
```

Đây là điểm rất quan trọng khi học DDD.

Một Domain Model tốt không phải chỉ là:

```text
data container
```

mà còn chứa:

```text
business behavior
```

---

# 20. Domain Invariant

Ta vừa tạo invariant:

> Một Story không được có hai Chapter cùng number.

Ví dụ:

```python
story.add_chapter(
    Chapter(
        number=ChapterNumber(1),
        ...
    )
)

story.add_chapter(
    Chapter(
        number=ChapterNumber(1),
        ...
    )
)
```

Phải fail.

Đây là:

> **Domain Invariant**

---

# 21. Tại sao không kiểm tra ở Repository?

Một thiết kế không tốt:

```python
repository.save_chapter(...)
```

rồi mới:

```python
if duplicate:
    raise ...
```

Nếu invariant thuộc domain:

```text
Story không có chapter trùng number
```

thì domain nên bảo vệ nó.

Database constraint vẫn có thể tồn tại như lớp bảo vệ thứ hai.

---

# 22. Domain Rule vs Database Rule

Ví dụ:

```text
Domain:
Chapter number không được trùng
```

Database:

```sql
UNIQUE(story_id, chapter_number)
```

Hai cái **không loại trừ nhau**.

Domain bảo vệ business correctness.

Database bảo vệ persistence integrity.

---

# 23. Một Domain Model tốt

Không phải:

```python
@dataclass
class Story:
    id: int
    title: str
    source: str
    url: str
    chapters: list
```

rồi mọi nơi muốn sửa gì thì sửa.

Mà:

```text
Story
│
├── invariant
│
├── behavior
│
└── controlled state changes
```

Ví dụ:

```python
story.add_chapter(...)
```

thay vì:

```python
story.chapters.append(...)
```

---

# 24. Immutability của Value Object

```python
url = Url(
    "https://source-a.com"
)
```

Không cho:

```python
url.value = "..."
```

Trong khi Entity:

```python
story.title = "Tên mới"
```

có thể mutable.

Đây là khác biệt thường gặp:

```text
Value Object
→ immutable

Entity
→ thường mutable
```

Không phải quy tắc tuyệt đối, nhưng là lựa chọn rất phổ biến.

---

# 25. Domain Service

Có những logic không thuộc tự nhiên vào một Entity nào.

Ví dụ:

> Xác định Story URL có phải thuộc Source nào không?

Ta có thể có:

```python
class StorySourceResolver:
    ...
```

Nhưng phải cẩn thận.

Nếu logic chỉ đơn giản:

```python
source.can_handle(url)
```

thì không cần Domain Service.

---

# 26. Khi nào cần Domain Service?

Ví dụ nghiệp vụ:

```text
Story recommendation
```

phụ thuộc:

```text
Story
Author
Category
ReadingHistory
```

và không tự nhiên thuộc một Entity duy nhất.

Lúc đó:

```python
class StoryRecommendationService:
    ...
```

có thể hợp lý.

Nhưng:

> Đừng tạo Domain Service chỉ vì "DDD có Domain Service".

---

# 27. Domain Layer hoàn chỉnh hơn

Sau Buổi 21, ta có thể hướng tới:

```text
domain/
│
├── story.py
├── chapter.py
│
├── value_objects/
│   ├── url.py
│   ├── source.py
│   └── chapter_number.py
│
├── crawler.py
│
└── repository.py
```

---

# 28. Dependency của Domain

Một Domain tốt:

```text
domain
│
├── dataclasses
├── typing
├── urllib.parse
│
└── business logic
```

Không:

```text
domain
├── sqlite3       ❌
├── requests      ❌
├── bs4           ❌
├── typer         ❌
└── PySide6       ❌
```

---

# 29. Một câu hỏi rất quan trọng

Tại sao chúng ta không viết:

```python
class Story:

    def save(self):
        sqlite3...
```

?

Vì lúc đó:

```text
Story
 ↓
SQLite
```

Domain phụ thuộc Infrastructure.

Nếu sau này:

```text
SQLite
 ↓
PostgreSQL
```

Domain phải thay đổi.

Đây là vi phạm DIP và Dependency Rule.

---

# 30. Domain Model vs ORM Model

Đừng nhầm:

```text
Domain Entity
```

với:

```text
ORM Model
```

Ví dụ domain:

```python
@dataclass
class Story:

    title: str
    source: Source
    url: Url
```

Database model có thể:

```text
stories
----------------
id
title
source
url
created_at
updated_at
```

Hai model phục vụ **hai mục đích khác nhau**.

---

# 31. Mapping

Infrastructure chịu trách nhiệm mapping:

```text
Domain Story
     ↓
SQLite row
```

và:

```text
SQLite row
     ↓
Domain Story
```

Ví dụ:

```python
def to_row(story: Story):
    return (
        story.title,
        story.source.name,
        story.url.value,
    )
```

Repository là boundary.

---

# 32. Domain không biết database schema

Domain không cần biết:

```sql
CREATE TABLE stories (...)
```

Database schema là concern của Infrastructure.

Đây chính là Separation of Concerns.

---

# 33. Một nguyên tắc DDD rất đáng nhớ

> **Không thiết kế Domain theo Database trước.**

Sai:

```text
Database table
 ↓
ORM model
 ↓
Domain
```

Tốt hơn:

```text
Business concept
 ↓
Domain model
 ↓
Repository abstraction
 ↓
Persistence implementation
```

---

# 34. Áp dụng vào Story Crawler

Business nghĩ:

```text
Story
Chapter
Chapter Number
Source
```

Không nghĩ:

```text
story_table
chapter_table
story_id
foreign_key
sqlite_row
```

Database chỉ là cách lưu trữ.

---

# 35. SOLID + DDD

Hôm nay chúng ta thấy các nguyên lý kết nối với nhau:

### SRP

`Story` chịu trách nhiệm domain behavior của Story.

### OCP

Crawler plugin có thể mở rộng.

### LSP

Crawler implementation phải thay thế được abstraction.

### ISP

Tách:

```text
StoryCrawler
ChapterCrawler
```

### DIP

Application phụ thuộc:

```text
StoryRepository
```

thay vì:

```text
SQLiteStoryRepository
```

---

# 36. Code Domain phiên bản hiện tại

Một phiên bản đơn giản có thể là:

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass(frozen=True)
class Url:

    value: str

    def __post_init__(self):

        parsed = urlparse(self.value)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "Invalid URL scheme"
            )

        if not parsed.netloc:
            raise ValueError(
                "URL must contain host"
            )


@dataclass(frozen=True)
class Source:

    name: str

    def __post_init__(self):

        if not self.name.strip():
            raise ValueError(
                "Source cannot be empty"
            )


@dataclass(frozen=True)
class ChapterNumber:

    value: int

    def __post_init__(self):

        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )


@dataclass
class Chapter:

    number: ChapterNumber
    title: str
    url: Url
    content: str


@dataclass
class Story:

    title: str
    source: Source
    url: Url

    _chapters: list[Chapter] = field(
        default_factory=list,
        repr=False,
    )

    @property
    def chapters(self):
        return tuple(self._chapters)

    def add_chapter(
        self,
        chapter: Chapter,
    ) -> None:

        if any(
            item.number == chapter.number
            for item in self._chapters
        ):
            raise ValueError(
                "Duplicate chapter number"
            )

        self._chapters.append(
            chapter
        )
```

Đây là **domain model thực sự**, chứ không chỉ là vài `dataclass` chứa dữ liệu.

---

# 37. Bài tập thực hành

## Bài 1 — `Url`

Viết:

```python
Url("https://example.com")
```

hợp lệ.

Các trường hợp sau phải lỗi:

```python
Url("")
Url("abc")
Url("ftp://example.com")
```

---

## Bài 2 — `ChapterNumber`

```python
ChapterNumber(1)
```

OK.

```python
ChapterNumber(0)
ChapterNumber(-1)
```

phải lỗi.

---

## Bài 3 — Story invariant

Viết test:

```python
story.add_chapter(chapter1)
story.add_chapter(chapter2)
```

với:

```text
chapter1.number = 1
chapter2.number = 2
```

→ OK.

Nhưng:

```text
chapter1.number = 1
chapter2.number = 1
```

→ `ValueError`.

---

# 38. Bài tập quan trọng nhất

Hãy trả lời câu hỏi này trước khi code:

> **`Chapter` có nên tồn tại độc lập ngoài `Story` hay không?**

Nếu domain của bạn xác định:

```text
Chapter luôn thuộc Story
```

thì mô hình:

```text
Story
 └── Chapter
```

là hợp lý.

Nếu Chapter có lifecycle độc lập:

```text
Chapter
 ├── có repository riêng
 ├── được crawl riêng
 └── được xử lý độc lập
```

thì có thể cần thiết kế khác.

Đây chính là tư duy **Aggregate Design**.

---

# 39. Bài học quan trọng nhất của Buổi 21

Đừng bắt đầu Domain bằng câu hỏi:

> "Tôi nên tạo class nào?"

Hãy bắt đầu bằng:

```text
Business có những concept nào?
        ↓
Concept nào có identity?
        ↓
Concept nào chỉ có value?
        ↓
Business rule là gì?
        ↓
Invariant là gì?
        ↓
Entity nào sở hữu behavior?
        ↓
Boundary của Aggregate nằm ở đâu?
```

Đây mới là **DDD thinking**.

---

## Roadmap tiếp theo

```text
20 — Architecture Skeleton
          ↓
21 — Domain Model Deep Dive  ← hôm nay
          ↓
22 — Crawler Port + Plugin
          ↓
23 — HTTP Client + Parser
          ↓
24 — SQLite Repository
          ↓
25 — CLI + Dependency Injection
          ↓
26 — Testing Architecture
```

**Buổi 22** chúng ta sẽ quay lại phần crawler và thiết kế thật kỹ:

```text
StoryCrawler
      │
      ├── can_handle()
      └── crawl()
             ↑
       ┌─────┴─────┐
       │           │
   SourceA      SourceB
```

và đặc biệt sẽ giải quyết một vấn đề rất thực tế: **làm thế nào thêm một crawler plugin mới mà không sửa `CrawlStory` — OCP + DIP + LSP + Plugin Architecture cùng lúc.**
