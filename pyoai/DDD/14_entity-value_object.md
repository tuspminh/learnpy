# DDD Deep Dive — Buổi 14

# Entity + Value Object

Đây là buổi **ghép kiến thức của Buổi 11 → 13**.

Chúng ta sẽ xây dựng Domain Model cho hệ thống đọc truyện:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── Status

Chapter
├── ChapterId
├── ChapterNumber
├── Title
└── Content
```

Mục tiêu của buổi này không phải chỉ viết class.

Mục tiêu là hiểu:

> **Entity dùng để biểu diễn "một thứ là ai", còn Value Object biểu diễn "giá trị của thứ đó là gì".**

---

# 1. Nhìn toàn bộ Domain Model

Ta muốn có:

```text
                    Domain
                       │
          ┌────────────┴────────────┐
          │                         │
        Story                     Chapter
       Entity                      Entity
          │                         │
    ┌─────┼─────┐             ┌─────┼──────┐
    ↓     ↓     ↓              ↓     ↓      ↓
 StoryId Title SourceId    ChapterId Number Title
   VO      VO      VO          VO      VO     VO
```

Trong đó:

```text
Story
Chapter
```

là Entity.

Còn:

```text
StoryId
StoryTitle
SourceId
ChapterId
ChapterNumber
ChapterTitle
```

là Value Object.

---

# 2. Tại sao cần thiết kế như vậy?

Cách đơn giản:

```python
class Story:
    id: int
    title: str
    source_id: int
    status: str
```

Nhìn qua có vẻ ổn.

Nhưng Domain không biết:

```text
int này là StoryId?
int này là SourceId?
str này là title?
str này là URL?
```

Primitive không thể hiện đầy đủ **business meaning**.

---

# 3. Sau khi dùng Value Object

Ta có:

```python
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    status: StoryStatus
```

Nhìn signature đã nói được:

```text
id        → StoryId
title     → StoryTitle
source_id → SourceId
status    → StoryStatus
```

Đây là:

> **Domain Model giàu ngữ nghĩa.**

---

# 4. Thiết kế `StoryId`

Trước hết:

```python
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class StoryId:
    value: UUID

    @classmethod
    def generate(cls) -> "StoryId":
        return cls(uuid4())
```

Sử dụng:

```python
story_id = StoryId.generate()
```

---

# 5. Tại sao `StoryId` là Value Object?

Một `StoryId`:

```text
550e8400-e29b-41d4-a716-446655440000
```

được xác định bởi:

```text
value
```

Hai:

```python
StoryId(uuid)
StoryId(uuid)
```

có cùng UUID thì có cùng value.

Do đó:

```text
StoryId
```

là Value Object.

---

# 6. `SourceId`

Tương tự:

```python
@dataclass(frozen=True)
class SourceId:
    value: UUID

    @classmethod
    def generate(cls) -> "SourceId":
        return cls(uuid4())
```

Ta không dùng:

```python
source_id: int
```

một cách mơ hồ.

---

# 7. Tại sao không dùng chung `UUID`?

Có thể viết:

```python
story_id: UUID
source_id: UUID
```

Nhưng:

```python
def load_story(
    story_id: UUID,
):
    ...
```

không thể hiện:

> UUID này là loại identity nào?

Với:

```python
story_id: StoryId
source_id: SourceId
```

Domain rõ ràng hơn.

---

# 8. `StoryTitle`

Từ Buổi 13:

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError(
                "Story title cannot be empty"
            )

        if len(value) > 200:
            raise ValueError(
                "Story title is too long"
            )

        object.__setattr__(
            self,
            "value",
            value,
        )
```

Bây giờ:

```python
title = StoryTitle(" One Piece ")
```

sẽ trở thành:

```text
"One Piece"
```

---

# 9. `StoryStatus`

Status là một trường hợp thú vị.

Ta có thể dùng Enum:

```python
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"
    ARCHIVED = "archived"
```

Đây là một semantic type.

---

# 10. Story Entity

Bây giờ:

```python
from dataclasses import dataclass


@dataclass(eq=False)
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    status: StoryStatus
```

Đây mới chỉ là **state**.

Chúng ta cần thêm **behavior**.

---

# 11. Entity phải bảo vệ lifecycle

Story lifecycle:

```text
DRAFT
  │
  │ publish()
  ↓
PUBLISHED
  │
  │ complete()
  ↓
COMPLETED
  │
  │ archive()
  ↓
ARCHIVED
```

Không phải transition nào cũng hợp lệ.

---

# 12. `publish()`

```python
def publish(self) -> None:
    if self.status != StoryStatus.DRAFT:
        raise ValueError(
            "Only draft story can be published"
        )

    self.status = StoryStatus.PUBLISHED
```

Entity tự kiểm soát transition.

---

# 13. `complete()`

```python
def complete(self) -> None:
    if self.status != StoryStatus.PUBLISHED:
        raise ValueError(
            "Only published story can be completed"
        )

    self.status = StoryStatus.COMPLETED
```

---

# 14. `archive()`

```python
def archive(self) -> None:
    if self.status != StoryStatus.COMPLETED:
        raise ValueError(
            "Only completed story can be archived"
        )

    self.status = StoryStatus.ARCHIVED
```

---

# 15. `rename()`

```python
def rename(self, title: StoryTitle) -> None:
    self.title = title
```

Nếu API nhận `str`:

```python
def rename(self, title: str) -> None:
    self.title = StoryTitle(title)
```

Tôi thường thích Domain API dùng:

```python
StoryTitle
```

để boundary conversion rõ ràng.

---

# 16. Equality của Story

Vì:

```python
@dataclass(eq=False)
```

ta tự định nghĩa:

```python
def __eq__(self, other):
    if not isinstance(other, Story):
        return NotImplemented

    return self.id == other.id
```

Entity equality dựa trên:

```text
StoryId
```

không dựa trên:

```text
title
status
source_id
```

---

# 17. Hoàn chỉnh `Story`

```python
from dataclasses import dataclass
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass(eq=False)
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    status: StoryStatus = StoryStatus.DRAFT

    def __eq__(self, other):
        if not isinstance(other, Story):
            return NotImplemented

        return self.id == other.id

    def rename(self, title: StoryTitle) -> None:
        self.title = title

    def publish(self) -> None:
        if self.status != StoryStatus.DRAFT:
            raise ValueError(
                "Only draft story can be published"
            )

        self.status = StoryStatus.PUBLISHED

    def complete(self) -> None:
        if self.status != StoryStatus.PUBLISHED:
            raise ValueError(
                "Only published story can be completed"
            )

        self.status = StoryStatus.COMPLETED

    def archive(self) -> None:
        if self.status != StoryStatus.COMPLETED:
            raise ValueError(
                "Only completed story can be archived"
            )

        self.status = StoryStatus.ARCHIVED
```

---

# 18. Chú ý một điều rất quan trọng

`Story` là mutable:

```python
story.publish()
```

làm:

```text
DRAFT
 ↓
PUBLISHED
```

Nhưng:

```python
story.id
```

không thay đổi.

Do đó:

```text
Identity
    ↓
stable

State
    ↓
mutable
```

---

# 19. Bây giờ tới `Chapter`

Chapter:

```text
Chapter
├── ChapterId
├── ChapterNumber
├── Title
└── Content
```

Ta có thể thiết kế:

```python
@dataclass(eq=False)
class Chapter:
    id: ChapterId
    number: ChapterNumber
    title: ChapterTitle
    content: ChapterContent
```

---

# 20. `ChapterId`

```python
@dataclass(frozen=True)
class ChapterId:
    value: UUID

    @classmethod
    def generate(cls) -> "ChapterId":
        return cls(uuid4())
```

---

# 21. `ChapterNumber`

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )

    def next(self) -> "ChapterNumber":
        return ChapterNumber(self.value + 1)
```

---

# 22. `ChapterTitle`

Có thể dùng:

```python
@dataclass(frozen=True)
class ChapterTitle:
    value: str

    def __post_init__(self):
        value = self.value.strip()

        if not value:
            raise ValueError(
                "Chapter title cannot be empty"
            )

        object.__setattr__(
            self,
            "value",
            value,
        )
```

---

# 23. `ChapterContent`

Đây là trường hợp thú vị.

Có nhất thiết phải tạo:

```python
ChapterContent
```

không?

Không nhất thiết.

Nếu content chỉ là:

```text
str
```

không có domain rule:

```python
content: str
```

có thể hoàn toàn hợp lý.

---

# 24. Nhưng nếu Content có business rule?

Ví dụ:

```text
content không được rỗng
content phải có tối thiểu 100 ký tự
content không chứa HTML script
```

thì có thể tạo:

```python
@dataclass(frozen=True)
class ChapterContent:
    value: str
```

Đây là quyết định **theo Domain**, không phải quy tắc "DDD bắt buộc mọi primitive phải thành VO".

---

# 25. Đây là một nguyên tắc quan trọng

Đừng làm:

```text
str
 ↓
Value Object
```

một cách máy móc.

Hãy hỏi:

> "Content có business meaning và business rule riêng không?"

Nếu:

```text
Không
```

→ `str`.

Nếu:

```text
Có
```

→ `ChapterContent`.

---

# 26. Chapter Entity

```python
@dataclass(eq=False)
class Chapter:
    id: ChapterId
    number: ChapterNumber
    title: ChapterTitle
    content: str

    def __eq__(self, other):
        if not isinstance(other, Chapter):
            return NotImplemented

        return self.id == other.id

    def rename(self, title: ChapterTitle) -> None:
        self.title = title

    def update_content(self, content: str) -> None:
        self.content = content
```

---

# 27. Một câu hỏi rất quan trọng

`Chapter` có phải Entity không?

Có thể là **có**.

Tại sao?

Vì:

```text
ChapterId
```

xác định một chapter cụ thể.

Ví dụ:

```text
Chapter #100
```

có thể thay đổi:

```text
title
content
```

nhưng vẫn là:

```text
Chapter #100
```

---

# 28. Story và Chapter có relationship

Ta có:

```text
Story
 │
 ├── StoryId
 ├── StoryTitle
 └── ...
 │
 └──── Chapters
          │
          ├── Chapter
          ├── Chapter
          └── Chapter
```

Nhưng đây dẫn chúng ta đến một khái niệm cực kỳ quan trọng:

> **Aggregate**

Chúng ta chưa học ngay.

---

# 29. Đừng vội biến `Story` thành list Chapter

Sai lầm phổ biến:

```python
@dataclass
class Story:
    ...
    chapters: list[Chapter]
```

rồi mọi thứ:

```python
story.chapters.append(...)
```

Có thể dẫn tới một model rất khó kiểm soát.

Trước tiên cần xác định:

```text
Story
```

và:

```text
Chapter
```

có thuộc cùng Aggregate hay không.

Đây sẽ là chủ đề của các buổi Aggregate sau.

---

# 30. Entity + Value Object + Domain behavior

Bây giờ Domain model của chúng ta:

```text
                 Story Entity
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
   StoryId       StoryTitle     SourceId
      VO             VO             VO
                     │
                     ↓
                StoryStatus
```

và:

```text
               Chapter Entity
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
    ChapterId   ChapterNumber  ChapterTitle
       VO            VO             VO
```

---

# 31. So sánh với model primitive

## Primitive model

```python
@dataclass
class Story:
    id: int
    title: str
    source_id: int
    status: str
```

## DDD model

```python
@dataclass(eq=False)
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    status: StoryStatus
```

DDD model dài hơn.

Nhưng đổi lại:

```text
type safety
+
business meaning
+
validation
+
behavior
+
invariant
```

---

# 32. Đây chính là trade-off

DDD không làm code:

```text
ít code hơn
```

Thường ngược lại:

```text
Primitive model
    ↓
ít class
ít code

DDD model
    ↓
nhiều concept
nhiều type
nhiều code
```

Nhưng với domain phức tạp:

```text
nhiều business rule
nhiều lifecycle
nhiều invariant
```

DDD giúp:

```text
complexity giảm
```

---

# 33. Factory cho Story

Không nên để:

```python
Story(
    id=...,
    title=...,
    source_id=...,
    status=StoryStatus.ARCHIVED,
)
```

nếu Domain không cho phép tạo trực tiếp Archived Story.

Ta có:

```python
@classmethod
def create(
    cls,
    id: StoryId,
    title: StoryTitle,
    source_id: SourceId,
) -> "Story":
    return cls(
        id=id,
        title=title,
        source_id=source_id,
        status=StoryStatus.DRAFT,
    )
```

---

# 34. Story creation

```python
story = Story.create(
    id=StoryId.generate(),
    title=StoryTitle("One Piece"),
    source_id=SourceId.generate(),
)
```

Kết quả:

```text
Story
status = DRAFT
```

Không thể tùy ý tạo:

```text
status = ARCHIVED
```

qua factory.

---

# 35. Factory + Invariant

Đây là bước chuyển từ:

```text
Object
```

sang:

```text
Domain Object
```

Factory đảm bảo:

```text
Story mới
    ↓
DRAFT
```

Entity đảm bảo:

```text
DRAFT
 ↓ publish()
PUBLISHED
```

---

# 36. Entity method không nên trả primitive nếu Domain cần VO

Ví dụ:

```python
story.title
```

nên trả:

```text
StoryTitle
```

không nhất thiết:

```text
str
```

Boundary mapper mới làm:

```python
story.title.value
```

---

# 37. Domain model và UI

UI:

```text
QLineEdit
```

trả:

```python
str
```

Application layer:

```text
str
 ↓
StoryTitle
```

Domain:

```text
StoryTitle
```

Đừng để:

```text
QLineEdit
```

xuất hiện trong Domain.

---

# 38. Domain model và database

Database:

```text
story_id
title
source_id
status
```

Repository mapper:

```text
DB values
   ↓
Value Objects
   ↓
Entity
```

Khi save:

```text
Entity
   ↓
Value Objects
   ↓
primitive
   ↓
SQL
```

---

# 39. Đây là kiến trúc chúng ta đang hướng tới

```text
                Interface
                    │
                    ↓
             Application
                    │
                    ↓
                Domain
          ┌─────────┴─────────┐
          ↓                   ↓
       Story               Chapter
       Entity               Entity
          │                   │
      Value Objects       Value Objects
          │                   │
          └─────────┬─────────┘
                    ↓
              Repository
                    ↓
             Infrastructure
                    ↓
                 SQLite
```

Đây chính là cầu nối giữa:

```text
DDD
```

và:

```text
Clean Architecture
```

mà chúng ta đã học ở Phần II.

---

# 40. Test Entity

Entity test:

```python
def test_story_can_be_published():
    story = Story.create(
        id=StoryId.generate(),
        title=StoryTitle("One Piece"),
        source_id=SourceId.generate(),
    )

    story.publish()

    assert story.status == StoryStatus.PUBLISHED
```

---

# 41. Test lifecycle

```python
def test_story_lifecycle():
    story = Story.create(
        id=StoryId.generate(),
        title=StoryTitle("One Piece"),
        source_id=SourceId.generate(),
    )

    assert story.status == StoryStatus.DRAFT

    story.publish()

    assert story.status == StoryStatus.PUBLISHED

    story.complete()

    assert story.status == StoryStatus.COMPLETED

    story.archive()

    assert story.status == StoryStatus.ARCHIVED
```

---

# 42. Test invalid transition

```python
def test_cannot_archive_draft_story():
    story = Story.create(
        id=StoryId.generate(),
        title=StoryTitle("One Piece"),
        source_id=SourceId.generate(),
    )

    with pytest.raises(ValueError):
        story.archive()
```

Đây là test **Domain behavior**, không phải test database.

---

# 43. Test Entity equality

```python
def test_story_equality_uses_identity():
    story_id = StoryId.generate()

    a = Story.create(
        id=story_id,
        title=StoryTitle("One Piece"),
        source_id=SourceId.generate(),
    )

    b = Story.create(
        id=story_id,
        title=StoryTitle("Naruto"),
        source_id=SourceId.generate(),
    )

    assert a == b
```

Điểm quan trọng:

```text
title khác
source_id khác
status giống
identity giống

→ cùng Entity
```

---

# 44. Test Value Object equality

```python
def test_title_equality():
    a = StoryTitle("One Piece")
    b = StoryTitle("One Piece")

    assert a == b
```

Khác với Entity:

```text
Entity → identity
VO     → value
```

---

# 45. Một sai lầm lớn

Đừng viết:

```python
if story.title == "One Piece":
```

nếu `story.title` là:

```text
StoryTitle
```

thay vào đó:

```python
if story.title == StoryTitle("One Piece"):
```

hoặc:

```python
if story.title.value == "One Piece":
```

Cách nào tốt hơn phụ thuộc vào Domain.

Nếu việc so sánh title là business behavior, có thể đưa vào `StoryTitle`.

---

# 46. Ví dụ behavior của Value Object

```python
@dataclass(frozen=True)
class StoryTitle:
    value: str

    ...

    def same_as(self, other: "StoryTitle") -> bool:
        return self.value.casefold() == other.value.casefold()
```

Bây giờ:

```python
a = StoryTitle("One Piece")
b = StoryTitle("ONE PIECE")

a.same_as(b)
```

→ `True`.

Đây là behavior có ý nghĩa Domain.

---

# 47. Đừng lạm dụng Value Object

Nếu viết:

```text
StoryTitle
StoryDescription
StorySlug
StoryAuthorName
StoryAuthorNickname
StoryCoverPath
StoryMetadata
StoryShortDescription
...
```

chỉ vì mỗi `str` đều là "domain concept", model sẽ trở nên nặng nề.

Hãy ưu tiên những primitive có:

```text
meaning + rules + behavior
```

---

# 48. Một heuristic rất hữu ích

Khi nhìn vào:

```python
title: str
```

hãy hỏi:

> Nếu tôi để `str`, liệu business rule nào sẽ bị phân tán khắp codebase?

Nếu:

```text
Không có
```

→ giữ `str`.

Nếu:

```text
Có
```

→ Value Object rất có khả năng phù hợp.

---

# 49. Domain Model cuối buổi

Ta có:

```text
domain/
│
├── story/
│   ├── entities/
│   │   └── story.py
│   │
│   ├── value_objects/
│   │   ├── story_id.py
│   │   ├── story_title.py
│   │   └── source_id.py
│   │
│   └── enums/
│       └── story_status.py
│
└── chapter/
    ├── entities/
    │   └── chapter.py
    │
    └── value_objects/
        ├── chapter_id.py
        ├── chapter_number.py
        └── chapter_title.py
```

Đây là một cách tổ chức.

Không phải duy nhất.

---

# 50. Một cách tổ chức đơn giản hơn

Với project nhỏ, không nhất thiết phải:

```text
entities/
value_objects/
enums/
```

quá sâu.

Có thể:

```text
domain/
├── story.py
├── story_id.py
├── story_title.py
├── story_status.py
├── chapter.py
├── chapter_id.py
├── chapter_number.py
└── chapter_title.py
```

DDD quan trọng ở **model và boundary**, không phải số lượng folder.

---

# 51. Những gì bạn cần nhớ sau Buổi 14

### Entity

```text
Story
Chapter
```

có:

```text
Identity
Lifecycle
Mutable State
Behavior
```

---

### Value Object

```text
StoryId
StoryTitle
SourceId
ChapterId
ChapterNumber
ChapterTitle
```

có:

```text
Value
Equality
Validation
Immutability
Semantic Meaning
```

---

### Entity chứa Value Object

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── StoryStatus
```

Đây là pattern rất quan trọng:

```text
Entity
   ↓
Value Objects
   ↓
Rich Domain Model
```

---

# 52. Bài tập Buổi 14

Hãy tự xây dựng Domain Model sau:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── StoryStatus

Chapter
├── ChapterId
├── ChapterNumber
├── ChapterTitle
└── Content
```

Yêu cầu:

### Story

```text
create()
rename()
publish()
complete()
archive()
```

Lifecycle:

```text
DRAFT
 ↓
PUBLISHED
 ↓
COMPLETED
 ↓
ARCHIVED
```

Không cho phép skip trạng thái.

### Chapter

```text
create()
rename()
update_content()
```

`ChapterNumber` phải:

```text
> 0
```

### Entity

Equality:

```text
Story → StoryId
Chapter → ChapterId
```

### Value Object

Tất cả phải:

```text
immutable
validated
equality by value
```

---

# 53. Bài tập nâng cao

Viết test cho toàn bộ Domain mà **không sử dụng SQLite, ORM, PySide6 hay HTTP**.

Chỉ được test:

```text
Story
Chapter
StoryId
StoryTitle
SourceId
ChapterId
ChapterNumber
ChapterTitle
StoryStatus
```

Nếu toàn bộ test chạy độc lập mà không cần database/UI thì bạn đã bắt đầu có một **Domain Model đúng hướng**.

---

## Bước tiếp theo

**Buổi 15 — Domain Invariant** sẽ đi sâu vào vấn đề quan trọng nhất còn thiếu:

```text
Invariant là gì?
       ↓
Business Rule
       ↓
Structural Rule
       ↓
Validation vs Invariant
       ↓
Invariant nằm ở đâu?
       ↓
Làm sao ngăn Entity rơi vào invalid state?
```

Và chúng ta sẽ bắt đầu phân biệt rất rõ:

```text
Input validation
       ≠
Domain invariant
       ≠
Database constraint
```
