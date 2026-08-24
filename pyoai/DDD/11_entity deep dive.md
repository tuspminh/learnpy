# DDD Deep Dive — Buổi 11

# Entity Deep Dive

Hôm nay chúng ta bắt đầu **Phần III — Tactical DDD**.

Sau Buổi 10, bạn đã biết:

```text
DDD
 ├── Strategic DDD
 │   ├── Subdomain
 │   ├── Bounded Context
 │   └── Context Map
 │
 └── Tactical DDD
     ├── Entity        ← Hôm nay
     ├── Value Object
     ├── Aggregate
     ├── Repository
     ├── Domain Service
     └── Domain Event
```

Buổi này tập trung hoàn toàn vào:

```text
Entity
├── Identity
├── Lifecycle
├── Equality
├── Behavior
├── Entity vs DTO
└── Entity vs Database Row
```

---

# 1. Entity là gì?

Trong DDD:

> **Entity là một object được xác định bởi identity của nó, không phải chỉ bởi các giá trị thuộc tính.**

Đây là câu quan trọng nhất của buổi học.

Ví dụ:

```text
Story #100
```

và:

```text
Story #200
```

có thể có:

```text
title = "One Piece"
status = "published"
```

nhưng vẫn là **hai Story khác nhau**.

```text
Story #100 ≠ Story #200
```

vì:

```text
identity khác nhau
```

---

# 2. Identity là gì?

Identity là đặc điểm giúp chúng ta trả lời:

> "Object này là object nào?"

Ví dụ:

```python
story_1 = Story(
    id=1,
    title="One Piece",
)

story_2 = Story(
    id=2,
    title="One Piece",
)
```

Hai object có:

```text
title giống nhau
```

nhưng:

```text
id khác nhau
```

nên:

```python
story_1 != story_2
```

---

# 3. Entity không phải chỉ là "class có id"

Đây là một nuance rất quan trọng.

Nhiều người định nghĩa:

```python
class Story:
    id: int
    title: str
```

rồi kết luận:

> Story có id → Entity.

Chưa đủ.

DDD Entity còn có:

```text
Identity
+
Lifecycle
+
Behavior
+
Business invariants
```

---

# 4. Entity có lifecycle

Entity thường trải qua nhiều trạng thái.

Ví dụ Story:

```text
                ┌───────────┐
                │  DRAFT    │
                └─────┬─────┘
                      │ publish()
                      ↓
                ┌───────────┐
                │ PUBLISHED │
                └─────┬─────┘
                      │ archive()
                      ↓
                ┌───────────┐
                │ ARCHIVED  │
                └───────────┘
```

Story vẫn là **cùng một Entity**.

Identity không thay đổi:

```text
StoryId = 100
```

---

# 5. Entity tồn tại qua thay đổi

Ví dụ:

```python
story = Story(
    id=100,
    title="One Piece",
    status="draft",
)
```

Sau đó:

```python
story.publish()
```

thành:

```text
id = 100
title = "One Piece"
status = "published"
```

Sau đó:

```python
story.rename("One Piece Manga")
```

thành:

```text
id = 100
title = "One Piece Manga"
status = "published"
```

Đây vẫn là:

```text
Story #100
```

---

# 6. Đây chính là điểm khác biệt với Value Object

Entity:

```text
Identity
```

Value Object:

```text
Value
```

Ví dụ:

```text
Story #100
```

là Entity.

Còn:

```text
StoryTitle("One Piece")
```

là Value Object.

---

# 7. Equality của Entity

Đây là phần rất quan trọng.

Giả sử:

```python
story_a = Story(
    id=1,
    title="One Piece",
)

story_b = Story(
    id=1,
    title="One Piece",
)
```

Có thể chúng là:

```text
hai Python object
```

nhưng về mặt Domain:

```text
cùng một Entity
```

vì:

```text
identity = 1
```

---

# 8. Entity equality dựa trên identity

Ta có:

```python
story_a.id == story_b.id
```

nên:

```python
story_a == story_b
```

theo nghĩa Domain.

Ngay cả khi:

```python
story_a.title = "One Piece"
story_b.title = "One Piece - Updated"
```

thì vẫn:

```text
Story #1 == Story #1
```

---

# 9. Entity không equality theo toàn bộ attributes

Sai:

```python
def __eq__(self, other):
    return (
        self.id == other.id
        and self.title == other.title
        and self.status == other.status
    )
```

Vì khi title thay đổi:

```text
Story #1
```

bỗng trở thành:

```text
Story #1 khác
```

Điều này phá vỡ identity.

---

# 10. Identity ổn định, state thay đổi

Hãy ghi nhớ:

```text
Entity
│
├── Identity → ổn định
│
└── State → có thể thay đổi
```

Ví dụ:

```text
StoryId = 100              ← identity

title = "One Piece"        ← state
status = "draft"           ← state
cover = "..."              ← state
```

Sau một thời gian:

```text
StoryId = 100              ← vẫn vậy

title = "One Piece"
status = "published"       ← thay đổi
cover = "new-cover.jpg"    ← thay đổi
```

---

# 11. Entity có Behavior

Đây là điểm quan trọng trong DDD.

Đừng chỉ tạo:

```python
story.status = "published"
```

Nếu `published` có business rule.

Thay vào đó:

```python
story.publish()
```

Entity tự kiểm soát behavior.

---

# 12. Ví dụ Entity đơn giản

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int
    title: str
    status: str = "draft"

    def publish(self) -> None:
        if not self.title.strip():
            raise ValueError("Story title is required")

        if self.status == "published":
            raise ValueError("Story is already published")

        self.status = "published"
```

Bây giờ business rule nằm trong Entity.

---

# 13. Tại sao `story.status = "published"` nguy hiểm?

Nếu cho phép:

```python
story.status = "published"
```

bất kỳ code nào cũng có thể làm:

```text
draft
 ↓
published
```

mà bỏ qua rule.

Ví dụ:

```python
story = Story(
    id=1,
    title="",
)

story.status = "published"
```

Domain object bây giờ:

```text
published
+
title = ""
```

Có thể là trạng thái invalid.

---

# 14. Entity nên bảo vệ state

Tốt hơn:

```python
story.publish()
```

và:

```python
def publish(self):
    if not self.title:
        raise InvalidStoryTitle()

    self.status = StoryStatus.PUBLISHED
```

Entity kiểm soát transition.

---

# 15. Lifecycle của Entity

Một Entity thường có:

```text
Create
 ↓
Active
 ↓
Modified
 ↓
Archived
```

Ví dụ Story:

```text
New
 ↓
Draft
 ↓
Published
 ↓
Completed
 ↓
Archived
```

Identity không thay đổi.

---

# 16. Lifecycle không nhất thiết phải là database lifecycle

Đừng nhầm:

```text
INSERT
UPDATE
DELETE
```

với:

```text
Domain lifecycle
```

Database nói:

```text
row được INSERT
```

Domain nói:

```text
Story được tạo
```

Hai khái niệm liên quan nhưng không đồng nhất.

---

# 17. Entity vs Database Row

Đây là một phần rất quan trọng.

Database:

```text
stories

id | title      | status
---+------------+----------
1  | One Piece  | published
```

Đây là:

> một database row.

DDD:

```python
story = Story(
    id=1,
    title="One Piece",
    status=StoryStatus.PUBLISHED,
)
```

Đây là:

> Domain Entity.

---

# 18. Database Row là data

Database row chủ yếu biểu diễn:

```text
columns
values
```

Entity biểu diễn:

```text
identity
state
behavior
business rules
invariants
```

---

# 19. Database Row không có behavior domain

SQL:

```sql
UPDATE stories
SET status = 'published'
WHERE id = 1;
```

Database không biết:

```text
"Story chỉ được publish khi..."
```

Business rule nằm ở Domain.

---

# 20. Entity có thể tồn tại không cần Database

Ví dụ:

```python
story = Story(
    id=1,
    title="One Piece",
)
```

Bạn có thể:

```python
story.publish()
```

mà không cần:

```text
SQLite
PostgreSQL
MySQL
```

Điều này rất quan trọng.

> **Entity không phải database record.**

---

# 21. Entity vs DTO

DTO:

> Data Transfer Object.

DTO chủ yếu dùng để:

```text
truyền dữ liệu
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class StoryDTO:
    id: int
    title: str
    status: str
```

Nó có thể chỉ là:

```text
data container
```

---

# 22. Entity có behavior

```python
class Story:
    def publish(self):
        ...

    def rename(self, title):
        ...

    def archive(self):
        ...
```

DTO thường:

```python
@dataclass
class StoryDTO:
    id: int
    title: str
    status: str
```

Không có business behavior.

---

# 23. Tại sao cần DTO?

DTO thường xuất hiện ở boundary.

Ví dụ API:

```text
HTTP Request
     ↓
CreateStoryRequest
     ↓
Use Case
     ↓
Story
```

Response:

```text
Story
 ↓
StoryResponse
 ↓
JSON
```

DTO giúp:

```text
Domain
```

không bị phụ thuộc vào:

```text
HTTP / JSON / UI
```

---

# 24. Ví dụ API DTO

```python
@dataclass
class CreateStoryRequest:
    title: str
    source_url: str
```

Use Case:

```python
class CreateStory:

    def execute(self, request: CreateStoryRequest):
        story = Story.create(
            title=request.title,
            source_url=request.source_url,
        )

        ...
```

DTO chỉ truyền dữ liệu.

---

# 25. Entity vs DTO

|                    | Entity          | DTO              |
| ------------------ | --------------- | ---------------- |
| Identity           | Có              | Có thể có        |
| Business behavior  | Có              | Không            |
| Business invariant | Có              | Thường không     |
| Mutable state      | Có thể          | Thường đơn giản  |
| Domain concept     | Có              | Không nhất thiết |
| Transport          | Không           | Có               |
| API boundary       | Không trực tiếp | Rất phổ biến     |

Điểm quan trọng:

> **Có `id` không biến DTO thành Entity.**

---

# 26. Một DTO có thể có `id`

Ví dụ:

```python
@dataclass
class StoryResponse:
    id: int
    title: str
    status: str
```

Nó vẫn là DTO.

Vì mục đích của nó là:

```text
transport data
```

không phải:

```text
domain identity + behavior
```

---

# 27. Entity có thể mutable

Đây là khác biệt quan trọng với Value Object.

Ví dụ:

```python
story.rename("One Piece New")
```

Entity thay đổi state.

Nhưng identity vẫn:

```text
StoryId = 1
```

---

# 28. Một Entity tốt

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class Story:
    id: int
    title: str
    status: str = "draft"

    def rename(self, title: str) -> None:
        title = title.strip()

        if not title:
            raise ValueError("Title cannot be empty")

        self.title = title

    def publish(self) -> None:
        if self.status == "published":
            raise ValueError("Story already published")

        if not self.title.strip():
            raise ValueError("Title cannot be empty")

        self.status = "published"

    def archive(self) -> None:
        if self.status != "published":
            raise ValueError(
                "Only published story can be archived"
            )

        self.status = "archived"
```

Entity này có:

```text
Identity
Behavior
State
Lifecycle
Invariant
```

---

# 29. Nhưng `dataclass` có vấn đề

Nếu dùng:

```python
@dataclass
class Story:
    id: int
    title: str
```

Python mặc định tạo:

```python
__eq__()
```

dựa trên **toàn bộ fields**.

Điều này không phù hợp với Entity nếu Domain equality dựa trên identity.

Ví dụ:

```python
a = Story(1, "One Piece")
b = Story(1, "Naruto")
```

Dataclass mặc định:

```python
a != b
```

Nhưng Domain có thể muốn:

```text
a == b
```

vì cùng:

```text
StoryId = 1
```

---

# 30. Cách 1 — `eq=False`

```python
from dataclasses import dataclass


@dataclass(eq=False)
class Story:
    id: int
    title: str
```

Sau đó tự implement:

```python
def __eq__(self, other):
    if not isinstance(other, Story):
        return NotImplemented

    return self.id == other.id
```

---

# 31. Nhưng còn hash?

Nếu Entity mutable:

```python
story.title = "New title"
```

thì không nên tùy tiện dùng Entity làm dictionary key.

Ví dụ:

```python
set_of_stories = {story}
```

có thể dẫn tới vấn đề nếu hash/equality thiết kế không cẩn thận.

Một nguyên tắc thực tế:

> **Entity mutable thường không nên được thiết kế như immutable hashable object.**

---

# 32. Identity có thể là UUID

Không nhất thiết:

```python
id: int
```

Có thể:

```python
from uuid import UUID


class Story:
    id: UUID
```

Ví dụ:

```text
550e8400-e29b-41d4-a716-446655440000
```

DDD không yêu cầu loại identity cụ thể.

Quan trọng là:

```text
identity phải xác định Entity.
```

---

# 33. Và đây là nơi Value Object sẽ xuất hiện

Thay vì:

```python
class Story:
    id: int
```

ta có thể:

```python
class Story:
    id: StoryId
```

Trong đó:

```python
@dataclass(frozen=True)
class StoryId:
    value: UUID
```

Đây sẽ là nội dung Buổi 12.

---

# 34. Entity Factory

Entity có thể được tạo qua:

```python
Story.create(...)
```

thay vì constructor trực tiếp.

Ví dụ:

```python
@dataclass(eq=False)
class Story:
    id: int
    title: str
    status: str

    @classmethod
    def create(cls, id: int, title: str):
        title = title.strip()

        if not title:
            raise ValueError("Title cannot be empty")

        return cls(
            id=id,
            title=title,
            status="draft",
        )
```

---

# 35. Tại sao `create()` hữu ích?

Nó biểu diễn:

> **Domain creation rule.**

Ví dụ:

```python
story = Story.create(
    id=1,
    title="One Piece",
)
```

thay vì:

```python
story = Story(
    id=1,
    title="",
    status="published",
)
```

Nếu constructor public cho phép mọi trạng thái, rất dễ tạo object invalid.

Buổi 15 chúng ta sẽ đào sâu vấn đề này khi học **Domain Invariant**.

---

# 36. Entity có thể có private state

Python không có private tuyệt đối như Java/C++.

Nhưng có thể dùng:

```python
@dataclass(eq=False)
class Story:
    _id: int
    _title: str
    _status: str
```

và expose behavior:

```python
@property
def title(self):
    return self._title
```

thay vì cho phép:

```python
story._status = "published"
```

khắp nơi.

---

# 37. Tuy nhiên đừng cực đoan

DDD không có quy tắc:

> "Tất cả field phải private."

Mục tiêu là:

> **Domain Entity phải kiểm soát những state transition quan trọng.**

Ví dụ:

```python
story.publish()
```

tốt hơn:

```python
story.status = "published"
```

nếu publish có business rule.

---

# 38. Entity và Identity qua Repository

Giả sử:

```python
story = repository.get(1)
```

Sau đó:

```python
story.rename("New Title")
repository.save(story)
```

Repository đang duy trì:

```text
StoryId = 1
```

Entity vẫn là:

```text
Story #1
```

---

# 39. Entity lifecycle và persistence

Có thể có:

```text
Transient
    ↓
Persisted
    ↓
Modified
    ↓
Persisted
    ↓
Archived
```

Nhưng Domain Entity không nhất thiết phải biết:

```text
"tôi đang ở database"
```

Nó chỉ biết:

```text
"tôi đang là Story"
```

---

# 40. Một sai lầm phổ biến

```python
class Story:

    def save(self):
        sqlite.execute(...)
```

Đây là:

```text
Domain → Infrastructure
```

và vi phạm dependency direction.

Entity không nên tự save.

Thay vào đó:

```python
story.publish()

repository.save(story)
```

---

# 41. Entity không phải Active Record

Active Record thường có kiểu:

```python
story.save()
story.delete()
story.find(...)
```

DDD + Clean Architecture thường ưu tiên:

```python
story.publish()

repository.save(story)
```

vì:

```text
Entity
```

và:

```text
Persistence
```

được tách biệt.

Không phải Active Record luôn sai, nhưng nó thường tạo coupling mạnh giữa Domain và Persistence.

---

# 42. Entity vs ORM Model

ORM:

```python
class StoryModel(Base):
    id = ...
    title = ...
```

Domain:

```python
class Story:
    id: StoryId
    title: StoryTitle

    def publish(self):
        ...
```

ORM Model:

```text
Database representation
```

Domain Entity:

```text
Business representation
```

---

# 43. Một Entity tốt trả lời được câu hỏi

Ví dụ:

```python
story.publish()
```

Người đọc code có thể hiểu:

> Story được publish.

Trong khi:

```python
story.status = 2
```

phải đi tìm:

```text
2 nghĩa là gì?
Có được phép không?
Có điều kiện gì?
```

DDD khuyến khích **behavior-rich model**.

---

# 44. Ubiquitous Language

Nếu domain expert nói:

> "Story chỉ được archive sau khi published."

Code nên phản ánh:

```python
story.archive()
```

và:

```python
if self.status != StoryStatus.PUBLISHED:
    raise StoryCannotBeArchived()
```

Thay vì:

```python
story.state = 3
```

Đây chính là:

> **Ubiquitous Language trong code.**

---

# 45. Entity trong hệ thống đọc truyện

Theo roadmap của chúng ta, sắp tới:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
└── status
```

và:

```text
Chapter
├── ChapterId
├── ChapterNumber
├── Title
└── Content
```

Trong đó:

```text
Story
```

là Entity.

```text
Chapter
```

cũng có thể là Entity.

Nhưng:

```text
StoryTitle
ChapterNumber
SourceUrl
```

có xu hướng là Value Object.

Đây sẽ là trọng tâm của Buổi 12.

---

# 46. Có phải mọi object có ID đều là Entity?

**Không.**

Ví dụ:

```python
@dataclass
class StoryResponse:
    id: int
    title: str
```

Có ID nhưng vẫn là DTO.

Hoặc:

```python
@dataclass
class DatabaseRow:
    id: int
    title: str
```

có ID nhưng vẫn chỉ là persistence data.

Câu hỏi đúng là:

> **Object này có identity mang ý nghĩa business và có lifecycle/behavior trong domain không?**

---

# 47. Checklist nhận diện Entity

Khi gặp một object, hãy hỏi:

### 1.

```text
Nó có identity không?
```

### 2.

```text
Identity có ý nghĩa business không?
```

### 3.

```text
Object có tồn tại qua thời gian không?
```

### 4.

```text
State có thay đổi không?
```

### 5.

```text
Nó có lifecycle không?
```

### 6.

```text
Business logic có gắn với nó không?
```

Nếu đa số câu trả lời là **có**, rất có khả năng đó là Entity.

---

# 48. Entity hay Value Object?

Một cách phân biệt nhanh:

### Entity

```text
"Đây là object nào?"
```

### Value Object

```text
"Giá trị của nó là gì?"
```

Ví dụ:

```text
Story #100
```

→ Entity.

```text
"One Piece"
```

→ Value Object có thể là `StoryTitle`.

---

# 49. Entity hay DTO?

### Entity

```text
"Object này là gì trong business?"
```

### DTO

```text
"Ta cần truyền dữ liệu gì qua boundary?"
```

---

# 50. Entity hay Database Row?

### Entity

```text
Business object
```

### Database Row

```text
Persistence representation
```

Đây là ba khái niệm cần tách:

```text
              Story Entity
                   │
             Business Model
                   │
          ┌────────┴────────┐
          ↓                 ↓
      DTO/API          ORM/DB Model
     Transport        Persistence
```

---

# 51. Tổng kết Buổi 11

Bạn cần nhớ 6 ý:

### ① Entity được xác định bởi Identity

```text
Story #1
```

không phải bởi:

```text
title/status
```

### ② Identity ổn định

```text
id = 1
```

state có thể thay đổi.

### ③ Entity có lifecycle

```text
Draft → Published → Archived
```

### ④ Entity nên chứa behavior

```python
story.publish()
```

thay vì thao tác state trực tiếp khắp nơi.

### ⑤ Entity ≠ DTO

DTO truyền data.

Entity biểu diễn business concept.

### ⑥ Entity ≠ Database Row

Database lưu persistence representation.

Entity biểu diễn domain behavior và business identity.

---

# 52. Bài tập Buổi 11

## Bài 1 — Phân loại

Hãy phân loại:

```text
Story
StoryDTO
StoryModel(SQLAlchemy)
StoryId
Chapter
ChapterResponse
```

vào:

```text
Entity
Value Object
DTO
ORM Model
```

---

## Bài 2 — Equality

Cho:

```python
story_a = Story(
    id=1,
    title="One Piece",
)

story_b = Story(
    id=1,
    title="Naruto",
)
```

Theo DDD Entity equality, `story_a` và `story_b` có phải cùng Entity không?

Giải thích.

---

## Bài 3 — Refactoring

Đoạn code:

```python
story.status = "published"
```

hãy refactor thành:

```python
story.publish()
```

và đặt business rule thích hợp vào Entity.

---

## Bài 4 — Lifecycle

Thiết kế lifecycle cho:

```text
Story
```

với các trạng thái:

```text
DRAFT
PUBLISHED
COMPLETED
ARCHIVED
```

Xác định transition nào được phép:

```text
DRAFT → ?
PUBLISHED → ?
COMPLETED → ?
ARCHIVED → ?
```

---

# 53. Bài tập quan trọng nhất

Thiết kế `Story` Entity **không dùng ORM**:

```text
Story
├── id
├── title
├── status
│
├── rename()
├── publish()
├── complete()
└── archive()
```

Yêu cầu:

```text
1. Equality dựa trên identity.
2. Không cho publish Story không có title.
3. Không publish Story đã published.
4. Chỉ published mới được complete.
5. Chỉ completed mới được archive.
6. Identity không thay đổi trong lifecycle.
```

Đây là bài tập rất tốt để chuẩn bị cho:

> **Buổi 12 — Value Object**, nơi chúng ta sẽ thay `id` và `title` primitive bằng `StoryId` và `StoryTitle`, đồng thời đi sâu vào **immutability, equality, validation và semantic type**.
