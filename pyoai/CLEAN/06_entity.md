# Buổi 6 — Entity Deep Dive

Hôm nay chúng ta chỉ tập trung vào **Entity**, đúng roadmap:

```text
Buổi 6 — Entity Deep Dive

✓ Identity
✓ Lifecycle
✓ Mutable state
✓ Behavior
✓ Entity vs DTO
✓ Entity vs ORM Model
```

Mục tiêu không phải chỉ biết định nghĩa Entity, mà phải hiểu:

> **Tại sao một object cần trở thành Entity, identity thực sự có ý nghĩa gì, state thay đổi thế nào, và business behavior nên nằm ở đâu.**

---

# 1. Entity là gì?

Trong Domain-Driven Design:

> **Entity là một domain object được nhận diện bởi identity liên tục theo thời gian.**

Có 3 ý quan trọng:

```text
Entity
 │
 ├── Identity
 │
 ├── Lifecycle
 │
 └── Behavior + State
```

Ví dụ:

```python
story = Story(
    id=StoryId(100),
    title="One Piece",
)
```

`Story` là Entity.

Tại sao?

Vì chúng ta quan tâm:

```text
Story #100
```

chứ không chỉ:

```text
title = "One Piece"
```

---

# 2. Identity là trái tim của Entity

Giả sử:

```python
story_a = Story(
    id=1,
    title="One Piece",
)
```

Sau đó title thay đổi:

```python
story_a.title = "One Piece Manga"
```

Nó vẫn là:

```text
Story #1
```

Identity không đổi.

```text
┌─────────────────────┐
│ Story               │
│                     │
│ id = 1              │ ← Identity
│ title = "One Piece" │ ← State
└─────────────────────┘

            ↓ update

┌──────────────────────────┐
│ Story                    │
│                          │
│ id = 1                   │ ← Same identity
│ title = "One Piece Manga"│ ← Changed state
└──────────────────────────┘
```

Đây chính là điểm khác biệt với Value Object.

---

# 3. Entity không được xác định bởi toàn bộ state

Giả sử:

```python
story_a = Story(
    id=1,
    title="One Piece",
)

story_b = Story(
    id=2,
    title="One Piece",
)
```

Hai Story có cùng:

```text
title
```

nhưng:

```text
id khác nhau
```

→ hai Entity khác nhau.

Ngược lại:

```python
story = Story(
    id=1,
    title="One Piece",
)
```

sau đó:

```python
story.title = "One Piece Manga"
```

→ vẫn là cùng Entity.

---

# 4. Entity Equality

Đây là một vấn đề rất quan trọng khi implement Entity.

Không nên mặc định:

```python
story_a == story_b
```

dựa trên toàn bộ field.

Thông thường identity là yếu tố chính:

```python
story_a.id == story_b.id
```

Ví dụ:

```python
class Story:

    def __init__(self, story_id, title):
        self.id = story_id
        self.title = title

    def __eq__(self, other):
        if not isinstance(other, Story):
            return NotImplemented

        return self.id == other.id
```

Bây giờ:

```python
a = Story(1, "One Piece")
b = Story(1, "One Piece Manga")

print(a == b)
```

Kết quả:

```text
True
```

vì:

```text
identity giống nhau
```

---

# 5. Nhưng hãy cẩn thận với `id`

Không phải cứ có:

```python
id: int
```

thì object là Entity.

Ví dụ:

```python
@dataclass(frozen=True)
class UserId:
    value: int
```

`UserId` không phải Entity.

Nó là **Value Object** đại diện cho identity.

Ta có:

```text
User
 ↓
Entity

UserId
 ↓
Value Object
```

Đây là một thiết kế rất tốt trong Domain Model.

---

# 6. Identity nên có type riêng

Thay vì:

```python
class Story:
    id: int
```

có thể:

```python
@dataclass(frozen=True)
class StoryId:
    value: int
```

Sau đó:

```python
class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: str,
    ):
        self.id = story_id
        self.title = title
```

Lợi ích:

```python
story.id
```

không còn đơn giản là một `int`.

Nó có domain meaning:

```text
StoryId
```

---

# 7. Tránh Primitive Confusion

Code:

```python
story_id = 10
author_id = 10
chapter_id = 10
```

Python đều thấy:

```text
int
```

Rất dễ truyền nhầm:

```python
get_story(author_id)
```

Trong khi:

```python
StoryId
AuthorId
ChapterId
```

sẽ rõ hơn.

```python
@dataclass(frozen=True)
class StoryId:
    value: int


@dataclass(frozen=True)
class AuthorId:
    value: int
```

Bây giờ type system giúp chúng ta thể hiện domain rõ hơn.

---

# 8. Identity phải ổn định

Một Entity không nên tùy tiện đổi identity.

Không nên:

```python
story.id = 999
```

sau khi Entity đã tồn tại.

Bởi vì:

```text
Story #1
```

không nên đột nhiên trở thành:

```text
Story #999
```

Đó không phải là update state thông thường.

Nó gần như tạo ra một Entity khác.

---

# 9. Identity và Lifecycle

Entity có lifecycle.

Ví dụ Story:

```text
                 create
                   │
                   ▼
                DRAFT
                   │
                publish
                   │
                   ▼
              PUBLISHED
                   │
                archive
                   │
                   ▼
              ARCHIVED
```

Entity tồn tại qua nhiều state.

Điều quan trọng:

```text
Identity
   ↓
không đổi

State
   ↓
thay đổi
```

---

# 10. Lifecycle là gì?

Lifecycle mô tả:

> **Entity được tạo ra, thay đổi và kết thúc như thế nào.**

Ví dụ `CrawlerJob`:

```text
PENDING
   │
 start
   ▼
RUNNING
   │
 ┌─┴───────────┐
 │             │
pause         fail
 │             │
 ▼             ▼
PAUSED       FAILED
 │
resume
 │
 ▼
RUNNING
 │
complete
 ▼
COMPLETED
```

Đây chính là lifecycle.

---

# 11. Không phải mọi state transition đều hợp lệ

Ví dụ:

```text
COMPLETED
```

không nên:

```text
resume()
```

hoặc:

```text
start()
```

Nếu business không cho phép.

Do đó Entity không chỉ lưu:

```text
status
```

mà phải bảo vệ:

```text
valid state transitions
```

---

# 12. Sai lầm: public mutable state

Ví dụ:

```python
class CrawlerJob:

    def __init__(self):
        self.status = "pending"
```

Code bên ngoài có thể:

```python
job.status = "completed"
```

Mà không thực sự chạy job.

Đây là vấn đề.

Ta muốn:

```python
job.complete()
```

thay vì:

```python
job.status = "completed"
```

---

# 13. Entity nên kiểm soát state

Ví dụ:

```python
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

Entity:

```python
class CrawlerJob:

    def __init__(self, job_id):
        self.id = job_id
        self.status = JobStatus.PENDING

    def start(self):
        if self.status is not JobStatus.PENDING:
            raise RuntimeError(
                "Only pending job can start"
            )

        self.status = JobStatus.RUNNING

    def pause(self):
        if self.status is not JobStatus.RUNNING:
            raise RuntimeError(
                "Only running job can pause"
            )

        self.status = JobStatus.PAUSED

    def resume(self):
        if self.status is not JobStatus.PAUSED:
            raise RuntimeError(
                "Only paused job can resume"
            )

        self.status = JobStatus.RUNNING
```

Bây giờ:

```text
State transition
```

được kiểm soát bởi Entity.

---

# 14. Mutable State

Entity thường có mutable state.

Ví dụ:

```python
story.title = ...
story.status = ...
```

hoặc thông qua behavior:

```python
story.rename(...)
story.publish()
story.archive()
```

Điểm quan trọng:

> **Mutable không có nghĩa là public mutable.**

Đây là hai chuyện khác nhau.

---

# 15. Public Mutable State vs Controlled Mutation

### Không tốt

```python
story.status = "published"
```

### Tốt hơn

```python
story.publish()
```

Bởi vì:

```text
publish()
```

có thể kiểm tra invariant:

```python
def publish(self):

    if not self.chapters:
        raise CannotPublishStory()

    self.status = StoryStatus.PUBLISHED
```

---

# 16. Entity Behavior

Entity không nên chỉ là:

```text
data container
```

Một Entity tốt thường có:

```text
State
+
Behavior
+
Invariant
```

Ví dụ:

```python
class Story:

    def add_chapter(self, chapter):
        ...

    def publish(self):
        ...

    def archive(self):
        ...
```

Business language trở thành method.

---

# 17. Behavior nên đặt ở đâu?

Một câu hỏi quan trọng:

> Behavior có thuộc về Entity không?

Hãy hỏi:

> **"Ai chịu trách nhiệm về hành vi này?"**

Ví dụ:

```text
Story.publish()
```

rất tự nhiên.

Vì:

```text
Story
```

là object thay đổi trạng thái publication.

---

# 18. Nhưng không phải mọi logic đều đặt vào Entity

Ví dụ:

```text
CalculateRoyalty
```

có thể cần:

```text
Story
Author
Contract
Sales
```

Không nên ép:

```python
story.calculate_royalty(...)
```

nếu logic không thực sự thuộc Story.

Có thể dùng:

```python
class RoyaltyCalculator:
    ...
```

Đây sẽ dẫn tới Domain Service ở Buổi 10.

---

# 19. Entity vs DTO

Đây là phần rất quan trọng trong Clean Architecture.

DTO:

> **Data Transfer Object**

Nó tồn tại để chuyển dữ liệu giữa boundary.

Ví dụ API request:

```python
from dataclasses import dataclass


@dataclass
class CreateStoryRequest:
    title: str
    author_id: int
```

Nó không nhất thiết có business behavior.

---

# 20. Entity

Entity:

```python
class Story:

    def publish(self):
        ...

    def add_chapter(self, chapter):
        ...

    def archive(self):
        ...
```

Nó đại diện cho:

```text
Business concept
```

DTO đại diện cho:

```text
Data crossing a boundary
```

---

# 21. DTO có thể thay đổi theo API

API version 1:

```python
@dataclass
class CreateStoryRequest:
    title: str
```

API version 2:

```python
@dataclass
class CreateStoryRequest:
    title: str
    author_name: str
    source_url: str
```

Domain Entity không nhất thiết phải thay đổi theo DTO.

Đây chính là lý do tách chúng.

---

# 22. Đừng làm DTO = Entity

Một anti-pattern:

```python
class StoryRequest(Story):
    ...
```

hoặc dùng cùng một object:

```text
FastAPI Pydantic Model
        =
Domain Entity
        =
Database Model
```

Khi đó:

```text
API
DB
Domain
```

bị coupling.

---

# 23. Entity vs ORM Model

ORM Model đại diện cho persistence.

Ví dụ:

```python
class StoryModel(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    status = Column(String)
```

Nó phục vụ:

```text
Database
```

Entity:

```python
class Story:
    ...
```

phục vụ:

```text
Domain
```

---

# 24. Vì sao không nên dùng ORM Model làm Domain Entity?

Ví dụ:

```python
class StoryModel(Base):

    id = Column(...)
    title = Column(...)
    status = Column(...)
```

Sau đó business logic:

```python
story.publish()
```

có vẻ rất tiện.

Nhưng bây giờ Domain phụ thuộc:

```text
SQLAlchemy
```

hoặc một ORM khác.

Bạn đã làm:

```text
Domain
  ↓
ORM
  ↓
Database
```

Dependency hướng ra ngoài.

Clean Architecture muốn:

```text
Infrastructure
      ↓
  implements
      ↓
Domain abstraction
```

---

# 25. ORM Model có persistence concerns

ORM có thể có:

```text
lazy loading
relationship
session
transaction
column mapping
indexes
foreign keys
```

Đó đều là persistence concerns.

Domain Entity không nên phải hiểu:

```python
session.commit()
```

---

# 26. Mapping giữa ORM và Entity

Ta có:

```text
Database
    ↓
ORM Model
    ↓
Mapper
    ↓
Domain Entity
```

và chiều ngược lại:

```text
Domain Entity
    ↓
Mapper
    ↓
ORM Model
    ↓
Database
```

Ví dụ:

```python
def to_domain(model: StoryModel) -> Story:
    return Story(
        story_id=StoryId(model.id),
        title=StoryTitle(model.title),
        status=StoryStatus(model.status),
    )
```

---

# 27. Entity hoàn chỉnh hơn

Hãy xây một `Story`.

```python
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class StoryId:
    value: int


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

Entity:

```python
class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: str,
    ):
        self._id = story_id
        self._title = title
        self._status = StoryStatus.DRAFT
        self._chapters = []
```

---

# 28. Encapsulation

Không nên:

```python
story._status = StoryStatus.PUBLISHED
```

Code bên ngoài không nên thao túng internal state.

Ta expose:

```python
@property
def status(self):
    return self._status
```

và behavior:

```python
def publish(self):
    ...
```

---

# 29. Entity API

Một thiết kế tốt:

```python
class Story:

    @property
    def id(self) -> StoryId:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def status(self) -> StoryStatus:
        return self._status

    def rename(self, title: str):
        ...

    def publish(self):
        ...

    def archive(self):
        ...
```

Bên ngoài:

```python
story.publish()
```

thay vì:

```python
story.status = "published"
```

---

# 30. Constructor cũng phải bảo vệ invariant

Không nên:

```python
Story(
    story_id=None,
    title="",
)
```

nếu đó là state không hợp lệ.

Constructor phải đảm bảo:

```text
Entity mới sinh ra
=
Valid state
```

Ví dụ:

```python
class Story:

    def __init__(self, story_id, title):

        if not title.strip():
            raise ValueError(
                "Story title cannot be empty"
            )

        self._id = story_id
        self._title = title
```

---

# 31. Factory Method

Khi constructor phức tạp, có thể dùng factory.

Ví dụ:

```python
class Story:

    @classmethod
    def create(cls, story_id, title):
        return cls(
            story_id=story_id,
            title=title,
        )
```

Hoặc:

```python
Story.create(...)
```

để biểu diễn business intent.

Factory sẽ là chủ đề riêng sau này, nên hiện tại chỉ cần hiểu:

> Constructor/factory phải tạo Entity ở trạng thái hợp lệ.

---

# 32. Entity Persistence Lifecycle

Một Entity thường có hai trạng thái lớn:

```text
Transient
   ↓
Persisted
```

Ví dụ:

```python
story = Story.create(...)
```

chưa lưu DB.

Sau:

```python
repository.save(story)
```

nó trở thành persistent state.

Nhưng domain entity không cần biết:

```text
SQLite
```

đã lưu nó.

---

# 33. Loading Entity

Khi repository đọc:

```python
story = repository.get(story_id)
```

nó phải tạo ra:

```text
Valid Story Entity
```

chứ không phải:

```text
raw database row
```

Ví dụ:

```text
SQLite row
     ↓
Mapper
     ↓
Story Entity
```

---

# 34. Một lỗi phổ biến

Repository:

```python
def get(self, story_id):
    return conn.execute(
        "SELECT * FROM stories WHERE id = ?",
        (story_id,),
    ).fetchone()
```

Application nhận:

```text
sqlite3.Row
```

Đây không phải Domain Entity.

Application bắt đầu biết:

```text
database structure
```

Architecture đang bị leak.

---

# 35. Repository đúng hơn

```python
class StoryRepository(Protocol):

    def get(self, story_id: StoryId) -> Story:
        ...

    def save(self, story: Story) -> None:
        ...
```

Infrastructure:

```python
class SQLiteStoryRepository:

    def get(self, story_id):
        row = ...
        return to_domain(row)
```

Application nhận:

```text
Story
```

không nhận:

```text
sqlite3.Row
```

---

# 36. Entity và ORM có thể trông giống nhau

Đây là một nuance quan trọng.

Không phải:

> "Nếu hai class giống nhau thì chắc chắn nên gộp."

Ví dụ:

```python
class Story:
    id
    title
    status
```

và:

```python
class StoryModel:
    id
    title
    status
```

Có thể giống nhau về fields.

Nhưng chúng có **hai responsibility khác nhau**:

```text
Story
→ Domain

StoryModel
→ Persistence
```

---

# 37. Khi nào có thể dùng chung?

Trong project rất nhỏ:

```text
CRUD application
```

có thể chấp nhận:

```text
ORM Model = Domain Model
```

để giảm complexity.

Nhưng khi:

```text
business rules phức tạp
+
nhiều interface
+
nhiều persistence concerns
```

thì separation trở nên có giá trị.

Đây là trade-off, không phải luật tuyệt đối.

---

# 38. Entity trong hệ thống cào truyện

Hãy xem `CrawlerJob`.

```python
class CrawlerJob:

    def __init__(self, job_id):
        self._id = job_id
        self._status = JobStatus.PENDING
```

Behavior:

```python
def start(self):
    ...

def pause(self):
    ...

def resume(self):
    ...

def complete(self):
    ...

def fail(self):
    ...
```

Đây là Entity rất rõ ràng vì:

```text
CrawlerJob #100
```

có lifecycle.

---

# 39. `CrawlerJob` không phải DTO

DTO:

```python
@dataclass
class StartCrawlerRequest:
    job_id: int
```

Entity:

```python
CrawlerJob
```

Use Case:

```python
class StartCrawler:

    def execute(self, request):
        job = repository.get(request.job_id)
        job.start()
        repository.save(job)
```

Luồng:

```text
DTO
 ↓
Use Case
 ↓
Entity
 ↓
Repository
```

---

# 40. Entity vs DTO vs ORM

Đây là mô hình cần nhớ:

```text
                API
                 │
                 ▼
                DTO
                 │
                 ▼
              Use Case
                 │
                 ▼
              Entity
                 │
                 ▼
              Repository
                 │
                 ▼
             ORM Model
                 │
                 ▼
             Database
```

Mỗi object có một responsibility.

---

# 41. Nhưng đừng biến nó thành ceremony

Không phải project nào cũng cần:

```text
API DTO
→ Application DTO
→ Domain DTO
→ Persistence DTO
→ ORM DTO
→ Database DTO
```

Nếu tất cả chỉ copy:

```text
id
title
status
```

thì có thể bạn đang tạo accidental complexity.

Nguyên tắc:

> **Tách khi boundary có ý nghĩa.**

---

# 42. Entity Design Checklist

Khi thiết kế Entity, hãy hỏi:

### 1. Identity là gì?

```text
StoryId
CrawlerJobId
AuthorId
```

### 2. Lifecycle là gì?

```text
Draft → Published → Archived
```

### 3. State nào mutable?

```text
title
status
chapters
```

### 4. Behavior nào thuộc Entity?

```text
publish()
archive()
add_chapter()
```

### 5. Invariant nào Entity phải bảo vệ?

```text
published story
→ cannot add chapter
```

### 6. Entity có biết infrastructure không?

Nếu có:

```text
SQLite
HTTP
Redis
PySide6
FastAPI
```

→ cần xem lại.

---

# 43. Một Entity tốt

```text
                    Story
                      │
        ┌─────────────┼─────────────┐
        │             │             │
     Identity       State        Behavior
        │             │             │
    StoryId         title        rename()
                    status       publish()
                    chapters    archive()
                                    │
                                    ▼
                              Invariants
```

Đây là mental model của hôm nay.

---

# 44. Anti-pattern: Setter Everywhere

Không nên:

```python
story.set_title(...)
story.set_status(...)
story.set_author(...)
story.set_published(...)
```

và để mọi business rule nằm ở caller.

Tốt hơn:

```python
story.rename(...)
story.publish()
story.assign_author(...)
```

Tên method nên diễn đạt **business intent**.

---

# 45. Anti-pattern: Entity as Dictionary

Ví dụ:

```python
story = {
    "id": 1,
    "title": "One Piece",
    "status": "published",
}
```

Không có:

```text
identity semantics
behavior
invariant
encapsulation
```

Đây chỉ là data structure.

---

# 46. Anti-pattern: God Entity

Ngược lại:

```python
class Story:

    def crawl(self):
        ...

    def parse_html(self):
        ...

    def save_database(self):
        ...

    def send_email(self):
        ...

    def calculate_recommendation(self):
        ...

    def render_html(self):
        ...
```

Entity trở thành God Object.

Entity chỉ nên sở hữu business behavior **thực sự thuộc về nó**.

---

# 47. Thực hành: thiết kế `Story`

Một phiên bản tốt:

```python
class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: StoryTitle,
    ):
        self._id = story_id
        self._title = title
        self._status = StoryStatus.DRAFT
        self._chapters = []

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def status(self):
        return self._status

    def rename(self, title: StoryTitle):
        self._ensure_editable()
        self._title = title

    def publish(self):
        self._ensure_can_publish()
        self._status = StoryStatus.PUBLISHED

    def _ensure_editable(self):
        if self._status is StoryStatus.ARCHIVED:
            raise RuntimeError(
                "Archived story cannot be edited"
            )

    def _ensure_can_publish(self):
        if not self._chapters:
            raise RuntimeError(
                "Story must have at least one chapter"
            )
```

Ở đây:

```text
Identity
→ _id

State
→ _title
→ _status
→ _chapters

Behavior
→ rename()
→ publish()

Invariant
→ _ensure_editable()
→ _ensure_can_publish()
```

---

# 48. Điều quan trọng nhất hôm nay

Đừng định nghĩa Entity là:

> "Một class có ID."

Định nghĩa chính xác hơn:

> **Entity là domain object có identity liên tục theo thời gian, có lifecycle và thường sở hữu behavior để bảo vệ các business invariant liên quan đến state của nó.**

Đây mới là tư duy DDD/Clean Architecture.

---

# 49. Bài tập Buổi 6

## Bài 1 — Identity

Giải thích tại sao:

```python
story_a = Story(1, "A")
story_b = Story(1, "B")
```

có thể được xem là cùng Entity.

Nhưng:

```python
story_a = Story(1, "A")
story_b = Story(2, "A")
```

là hai Entity khác nhau.

---

## Bài 2 — Lifecycle

Thiết kế lifecycle cho:

```text
CrawlerJob
```

với:

```text
PENDING
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
```

Xác định transition hợp lệ:

```text
PENDING → ?
RUNNING → ?
PAUSED → ?
COMPLETED → ?
FAILED → ?
CANCELLED → ?
```

---

## Bài 3 — Refactor Entity

Code hiện tại:

```python
class Story:

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.status = "draft"

    def set_status(self, status):
        self.status = status

    def set_title(self, title):
        self.title = title
```

Refactor thành:

```text
Identity
Encapsulation
Behavior
Invariant
```

với:

```python
story.rename(...)
story.publish()
story.archive()
```

---

## Bài 4 — Entity vs DTO

Cho:

```python
class CreateStoryRequest:
    title: str
    author_id: int
```

và:

```python
class Story:
    ...
```

Giải thích tại sao không nên coi chúng là cùng một object.

---

## Bài 5 — Entity vs ORM

Cho:

```python
class StoryModel:
    id: int
    title: str
    status: str
```

và:

```python
class Story:
    ...
```

Hãy thiết kế:

```text
StoryModel
    ↓
to_domain()
    ↓
Story
```

và:

```text
Story
    ↓
to_model()
    ↓
StoryModel
```

---

## Bài 6 — Bài tập quan trọng nhất

Thiết kế Entity:

```text
CrawlerJob
```

Có:

```text
Identity:
    CrawlerJobId

State:
    status
    source
    created_at
    started_at
    completed_at

Behavior:
    start()
    pause()
    resume()
    complete()
    fail()
    cancel()
```

Yêu cầu:

```text
1. Không cho phép transition bất hợp lệ.

2. Không cho phép Entity ở illegal state.

3. Không có SQLite.

4. Không có Redis.

5. Không có Playwright.

6. Không có FastAPI.

7. Không có PySide6.
```

Mục tiêu là bạn phải cảm nhận được:

```text
             CrawlerJob
                  │
       ┌──────────┼──────────┐
       │          │          │
   Identity     State     Behavior
       │          │          │
 JobId        status      start()
              source      pause()
              dates       resume()
                           │
                           ▼
                     State Machine
                           │
                           ▼
                      Invariants
```

---

## Chuỗi kiến thức

Sau Buổi 6, ta đã có:

```text
Buổi 5
Domain Model
    │
    ├── Entity ──────────┐
    ├── Value Object     │
    ├── Aggregate        │
    ├── Domain Service   │
    ├── Domain Rule      │
    └── Invariant        │
                          ▼
Buổi 6
Entity Deep Dive
    │
    ├── Identity
    ├── Lifecycle
    ├── Mutable State
    ├── Behavior
    ├── Entity vs DTO
    └── Entity vs ORM
```

**Buổi 7 sẽ chỉ tập trung vào Value Object Deep Dive**: vì sao Value Object nên immutable, equality-by-value hoạt động thế nào, `dataclass(frozen=True)`, validation và chúng ta sẽ tự xây lần lượt `Email`, `Money`, `URL`, `StoryTitle` theo hướng domain-driven.
