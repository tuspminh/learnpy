# Buổi 5 — Domain Model Deep Dive

Từ buổi 1–4, chúng ta đã hiểu:

```text
Clean Architecture
        ↓
bảo vệ Business Rules
        ↓
Business Rules nằm ở Core
        ↓
Core không phụ thuộc Framework / DB / UI
```

Hôm nay chúng ta đi vào **trái tim của Clean Architecture**:

> **Domain Model**

Đây cũng là điểm giao nhau rất mạnh giữa **Clean Architecture và DDD**.

---

# 1. Domain là gì?

Đầu tiên, đừng hiểu Domain là:

```text
domain/
    models.py
```

Domain không phải là một folder.

Domain là:

> **Lĩnh vực nghiệp vụ mà phần mềm đang giải quyết.**

Ví dụ ứng dụng đọc truyện:

```text
Domain
├── Story
├── Chapter
├── Author
├── Genre
├── ReadingProgress
├── CrawlJob
└── Publication
```

Đây là các khái niệm nghiệp vụ.

---

# 2. Domain không phải Database

Đây là một lỗi rất phổ biến.

Ví dụ database:

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author_id INTEGER,
    status TEXT,
    created_at TEXT
);
```

Bạn không nên kết luận:

```text
Story = database row
```

Không.

Database model trả lời:

> **Dữ liệu được lưu như thế nào?**

Domain model trả lời:

> **Business hoạt động như thế nào?**

---

# 3. Domain Model vs ORM Model

Ví dụ ORM:

```python
class StoryModel:
    id: int
    title: str
    status: str
```

Domain:

```python
class Story:
    ...
```

Hai thứ có thể trông giống nhau.

Nhưng mục đích khác nhau.

---

# 4. Database Model là Data Structure

Ví dụ:

```python
@dataclass
class StoryRow:
    id: int
    title: str
    status: str
```

Nó có thể chỉ là:

```text
id
title
status
```

Không nhất thiết có business behavior.

---

# 5. Domain Model có Behavior

Ví dụ:

```python
class Story:

    def publish(self):
        if not self.chapters:
            raise CannotPublishEmptyStory()

        self.status = StoryStatus.PUBLISHED
```

Đây mới là domain logic.

`Story` không chỉ chứa:

```text
data
```

mà còn chứa:

```text
behavior
+
invariants
```

---

# 6. Entity là gì?

Trong DDD:

> **Entity là object được xác định bởi identity của nó.**

Ví dụ:

```python
story_1 = Story(id=1, title="ABC")
story_2 = Story(id=1, title="XYZ")
```

Dù title khác nhau:

```text
id = 1
```

chúng có thể vẫn là **cùng một Story** dưới góc nhìn identity.

---

# 7. Identity

Entity có identity:

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

Identity có thể là:

```text
UUID
Integer
String
Composite key
```

Nhưng quan trọng không phải loại ID.

Quan trọng là:

> **Identity có ý nghĩa nghiệp vụ.**

---

# 8. Entity không đồng nghĩa Database ID

Ví dụ:

```python
Story(id=123)
```

`123` có thể là database ID.

Nhưng Domain có thể dùng:

```python
StoryId
```

```python
@dataclass(frozen=True)
class StoryId:
    value: UUID
```

Database có thể map:

```text
StoryId
   ↓
INTEGER / TEXT / UUID
```

Domain không cần biết database lưu thế nào.

---

# 9. Entity có lifecycle

Một Entity thường có lifecycle:

```text
Created
   ↓
Draft
   ↓
Published
   ↓
Archived
```

Ví dụ:

```python
story.publish()
```

thay đổi state.

Đây là điểm quan trọng:

> Entity thường có **behavior theo thời gian**.

---

# 10. Value Object

Bây giờ đến khái niệm cực kỳ quan trọng:

> **Value Object được xác định bởi value, không phải identity.**

Ví dụ:

```python
Money(100_000, "VND")
```

Hai object:

```python
Money(100_000, "VND")
Money(100_000, "VND")
```

có thể được xem là bằng nhau.

Không cần:

```text
money_id
```

---

# 11. Ví dụ Email

Thay vì:

```python
class User:
    email: str
```

ta có:

```python
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email")
```

Bây giờ:

```python
Email("abc@example.com")
```

không chỉ là string.

Nó là:

> **một giá trị có business meaning.**

---

# 12. Primitive Obsession

Code kiểu này:

```python
class User:
    email: str
    phone: str
    country_code: str
```

dễ dẫn tới:

```python
user.email = "hello"
user.phone = "abc"
```

Không có protection.

Đây gọi là:

> **Primitive Obsession**

Ta có thể model:

```python
Email
PhoneNumber
CountryCode
```

---

# 13. Value Object bảo vệ invariant

Ví dụ:

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
ChapterNumber(10)
```

hợp lệ.

Nhưng:

```python
ChapterNumber(-5)
```

không thể tồn tại.

Đây là một ý tưởng rất mạnh:

> **Invalid state should be hard to represent.**

---

# 14. Entity + Value Object

Ví dụ:

```python
@dataclass
class Chapter:

    id: ChapterId
    number: ChapterNumber
    title: ChapterTitle
```

Ta tránh:

```python
id: int
number: int
title: str
```

nếu những value đó có business rules.

---

# 15. Domain Invariant

Đây là từ khóa cực kỳ quan trọng.

> **Invariant là điều kiện phải luôn đúng trong domain.**

Ví dụ:

```text
Chapter number > 0
```

hoặc:

```text
Story không thể Published nếu không có Chapter
```

hoặc:

```text
Published Story không thể bị sửa nội dung
```

Invariant phải được bảo vệ.

---

# 16. Invariant không nên chỉ nằm ở UI

Sai:

```python
def on_publish_clicked():
    if len(chapters) == 0:
        QMessageBox.warning(...)
        return
```

Vấn đề:

CLI có thể bypass:

```bash
story publish 123
```

API cũng bypass.

Test cũng có thể bypass.

Business rule không được phụ thuộc UI.

---

# 17. Domain bảo vệ Invariant

Ví dụ:

```python
class Story:

    def publish(self):

        if not self.chapters:
            raise CannotPublishStory(
                "Story must contain at least one chapter"
            )

        self.status = StoryStatus.PUBLISHED
```

Bây giờ:

```text
PySide6 ──┐
FastAPI ──┼──> Story.publish()
CLI ──────┘
```

Rule chỉ tồn tại một nơi.

---

# 18. Domain Service

Không phải business logic nào cũng thuộc một Entity.

Ví dụ:

```text
TransferMoney
```

có:

```text
Account A
Account B
Money
```

Logic liên quan nhiều Entity.

Ta có:

```python
class TransferMoney:

    def execute(
        self,
        source: Account,
        target: Account,
        amount: Money,
    ):
        ...
```

Đây có thể là **Domain Service**.

---

# 19. Domain Service không phải Application Service

Hai khái niệm này rất dễ nhầm.

### Domain Service

Chứa:

> **Domain logic**

Ví dụ:

```python
class PricingService:
    def calculate_price(...):
        ...
```

### Application Service / Use Case

Chứa:

> **Workflow / orchestration**

Ví dụ:

```python
class PublishStory:

    def execute(self, story_id):
        story = self.repository.get(story_id)

        story.publish()

        self.repository.save(story)
```

Application Service điều phối.

Domain Service giải quyết business rule.

---

# 20. So sánh

```text
Domain Entity
    ↓
Business behavior của chính Entity

Domain Service
    ↓
Business logic liên quan nhiều domain object

Application Service
    ↓
Điều phối Use Case
```

Đây là distinction cực kỳ quan trọng.

---

# 21. Ví dụ

```python
class Story:

    def publish(self):
        ...
```

Nếu logic chỉ cần Story:

→ Entity.

Nhưng:

```python
class StoryPublicationPolicy:

    def can_publish(
        self,
        story,
        author,
        subscription,
    ):
        ...
```

Nếu business rule liên quan nhiều object:

→ Domain Service/Policy.

Còn:

```python
class PublishStory:

    def execute(self, story_id):
        story = repository.get(story_id)
        ...
        repository.save(story)
```

→ Application Service.

---

# 22. Domain Event

Một khái niệm tiếp theo:

> **Domain Event biểu diễn một điều có ý nghĩa nghiệp vụ đã xảy ra.**

Ví dụ:

```text
StoryPublished
ChapterDownloaded
StoryCompleted
```

Ví dụ:

```python
@dataclass(frozen=True)
class StoryPublished:
    story_id: StoryId
```

Domain nói:

> Story đã được publish.

Nó không cần biết:

```text
email
Redis
HTTP
notification
```

---

# 23. Event giúp giảm coupling

Không có event:

```text
PublishStory
    ↓
EmailService
    ↓
Notification
    ↓
Redis
```

Use case biết quá nhiều.

Có event:

```text
Story
  ↓
StoryPublished
  ↓
Event Handler
  ├── SendEmail
  ├── UpdateSearchIndex
  └── PublishNotification
```

Domain không biết các detail.

---

# 24. Entity không nên gọi Infrastructure

Sai:

```python
class Story:

    def publish(self):
        requests.post(...)
        sqlite3.connect(...)
```

Domain entity đang biết:

```text
HTTP
SQLite
```

🚨 Vi phạm dependency rule.

Đúng:

```python
class Story:

    def publish(self):
        self.status = StoryStatus.PUBLISHED
```

Sau đó Application xử lý persistence/event.

---

# 25. Domain Model không phải CRUD Model

CRUD mindset:

```text
Create
Read
Update
Delete
```

Domain mindset:

```text
Publish
Archive
AddChapter
Complete
StartCrawl
PauseCrawl
ResumeCrawl
```

Đây là sự khác biệt rất lớn.

---

# 26. Anemic Domain Model

Một model kiểu:

```python
@dataclass
class Story:
    id: int
    title: str
    status: str
```

và tất cả logic:

```python
class StoryService:

    def publish(self, story):
        if ...:
            ...
```

có thể trở thành:

> **Anemic Domain Model**

Entity chỉ chứa data.

Business logic nằm hết bên ngoài.

---

# 27. Rich Domain Model

Thay vào đó:

```python
class Story:

    def publish(self):
        if not self.can_publish():
            raise CannotPublishStory()

        self.status = StoryStatus.PUBLISHED

    def add_chapter(self, chapter):
        if self.status is StoryStatus.PUBLISHED:
            raise StoryAlreadyPublished()

        self.chapters.append(chapter)
```

Entity có:

```text
state
+
behavior
+
invariants
```

Đây là Rich Domain Model.

---

# 28. Nhưng không phải lúc nào cũng cần Rich Model

Nếu domain rất đơn giản:

```text
Simple CRUD
```

thì:

```python
@dataclass
class User:
    id: int
    name: str
```

hoàn toàn có thể đủ.

Không nên ép:

```text
Entity
Value Object
Aggregate
Domain Service
Domain Event
Factory
Repository
```

vào mọi project.

---

# 29. Domain Model nên phản ánh ngôn ngữ nghiệp vụ

Ví dụ crawler.

Code CRUD:

```python
story.status = "done"
```

Domain model tốt hơn:

```python
story.complete()
```

Hoặc:

```python
crawl_job.pause()
crawl_job.resume()
crawl_job.retry()
```

Business language trở thành code.

Đây chính là **Ubiquitous Language** của DDD.

---

# 30. Enum cho Domain State

Đừng lạm dụng string:

```python
status = "published"
```

Có thể dùng:

```python
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

Sau đó:

```python
if self.status is StoryStatus.PUBLISHED:
    ...
```

Giảm typo và làm domain rõ hơn.

---

# 31. Ví dụ Domain Model hoàn chỉnh

```python
from dataclasses import dataclass
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class StoryId:
    value: int


@dataclass
class Chapter:

    id: int
    title: str


class Story:

    def __init__(
        self,
        story_id: StoryId,
        title: str,
    ):
        if not title.strip():
            raise ValueError("Title is required")

        self.id = story_id
        self.title = title
        self.chapters: list[Chapter] = []
        self.status = StoryStatus.DRAFT

    def add_chapter(self, chapter: Chapter):

        if self.status is StoryStatus.PUBLISHED:
            raise RuntimeError(
                "Cannot modify published story"
            )

        self.chapters.append(chapter)

    def publish(self):

        if not self.chapters:
            raise RuntimeError(
                "Story must have at least one chapter"
            )

        self.status = StoryStatus.PUBLISHED
```

Đây là một domain model có behavior.

---

# 32. Điều gì không nên nằm trong Domain?

Ví dụ:

```python
class Story:

    def save_to_sqlite(self):
        ...

    def send_http_request(self):
        ...

    def show_message_box(self):
        ...

    def serialize_to_json(self):
        ...
```

Đây đều là dấu hiệu domain đang chứa infrastructure/presentation concerns.

---

# 33. Domain Model vs DTO

DTO:

```python
@dataclass
class CreateStoryRequest:
    title: str
```

DTO dùng để:

```text
Transport data
```

Domain Entity:

```python
Story(...)
```

dùng để:

```text
Business behavior
```

Không nên mặc định:

```text
DTO == Domain Entity
```

---

# 34. Ví dụ FastAPI

Request:

```python
class CreateStoryRequest(BaseModel):
    title: str
```

Use Case:

```python
class CreateStory:

    def execute(self, request):
        story = Story(
            story_id=self.id_generator.next(),
            title=request.title,
        )

        self.repository.save(story)

        return story
```

Response:

```python
class StoryResponse(BaseModel):
    id: int
    title: str
```

Ta có:

```text
HTTP DTO
   ↓
Use Case
   ↓
Domain
   ↓
Repository
```

---

# 35. Mapping

Nếu DTO và Domain khác nhau:

```text
CreateStoryRequest
        ↓
      Mapper
        ↓
      Story
```

và:

```text
Story
  ↓
Mapper
  ↓
StoryResponse
```

Điều này giúp Domain không bị framework contamination.

---

# 36. ORM mapping

Database:

```text
stories
```

Domain:

```text
Story
```

Infrastructure mapper:

```python
def to_domain(row) -> Story:
    ...
```

và:

```python
def to_row(story: Story):
    ...
```

Ta có:

```text
Database
    ↓
ORM / Row
    ↓
Mapper
    ↓
Domain Entity
```

Domain không cần biết SQLite.

---

# 37. Tại sao đây là Clean Architecture?

Bởi vì:

```text
          ┌───────────────┐
          │    Domain     │
          │               │
          │ Story         │
          │ Chapter       │
          │ Value Object  │
          └───────▲───────┘
                  │
          Application
                  │
        ──────────┼──────────
                  │
          Infrastructure
                  │
        SQLite / Redis / HTTP
```

Domain ở trung tâm.

---

# 38. Một nguyên tắc rất quan trọng

> **Domain model không nên được thiết kế dựa trên database schema.**

Sai:

```text
Database
   ↓
ORM
   ↓
Domain
```

Nếu database thay đổi:

```text
Domain thay đổi
```

Đúng:

```text
Business
   ↓
Domain Model
   ↓
Persistence Mapping
   ↓
Database
```

Database thích nghi với domain.

---

# 39. Nhưng có một nuance

Không phải lúc nào Domain phải hoàn toàn độc lập với persistence.

Ví dụ:

```text
performance
query optimization
transaction
aggregate persistence
```

có thể ảnh hưởng domain design.

Nhưng dependency vẫn phải được kiểm soát.

Clean Architecture không nói:

> "Database không được ảnh hưởng bất kỳ quyết định nào."

Nó nói:

> **Database không được trở thành chủ sở hữu của business rules.**

---

# 40. Mental Model quan trọng nhất của Buổi 5

Khi nhìn một object, hãy hỏi:

### Câu 1

```text
Object này có identity không?
```

Có:

→ Entity.

Không:

→ có thể là Value Object.

---

### Câu 2

```text
Object này có business behavior không?
```

Có:

→ Domain Model candidate.

---

### Câu 3

```text
Object này bảo vệ invariant nào?
```

Nếu không có:

→ có thể chỉ là DTO/data structure.

---

### Câu 4

```text
Object này có biết SQLite / HTTP / GUI không?
```

Nếu có:

→ rất có khả năng không thuộc Domain.

---

# 41. Bài tập Buổi 5

## Bài 1 — Entity hay Value Object?

Phân loại:

```text
Story
StoryId
Chapter
Email
Money
Author
ISBN
Address
ReadingProgress
```

và giải thích lý do.

---

# 42. Bài 2 — Anemic hay Rich?

Code:

```python
@dataclass
class Story:
    id: int
    title: str
    chapters: list
    status: str


class StoryService:

    def publish(self, story):

        if not story.chapters:
            raise ValueError()

        story.status = "published"
```

Hãy:

1. Chỉ ra vấn đề.
2. Refactor thành Rich Domain Model.
3. Xác định invariant.

---

# 43. Bài 3 — Domain vs Application

Phân loại:

```text
CreateStory
PublishStory
Story.publish()
Story.add_chapter()
CalculateStoryPrice
StoryRepository
SQLiteStoryRepository
SendStoryPublishedEmail
```

thành:

```text
Domain Entity
Domain Service
Application Use Case
Repository Port
Infrastructure Adapter
Event Handler
```

---

# 44. Bài 4 — Domain Invariant

Thiết kế `Story` với các rule:

```text
1. Title không được rỗng.

2. Chapter number > 0.

3. Story phải có ít nhất một Chapter
   mới được publish.

4. Story đã publish không được thêm Chapter.

5. Story đã archived không được publish lại.
```

Hãy viết domain model Python.

**Không dùng SQLite.
Không dùng FastAPI.
Không dùng PySide6.**

---

# 45. Bài 5 — Domain Model vs Database Model

Database:

```sql
stories
-------
id
title
status

chapters
--------
id
story_id
number
title
```

Hãy thiết kế:

```text
Domain
    Story
    Chapter
    StoryId
    ChapterNumber
    StoryStatus
```

và:

```text
Infrastructure
    SQLiteStoryRepository
    StoryMapper
```

Mục tiêu là:

```text
SQLite schema
       ≠
Domain model
```

---

# 46. Bài tập lớn

Thiết kế Domain Model cho hệ thống **cào và đọc truyện** của bạn.

Tối thiểu:

```text
Story
Chapter
Author
CrawlerJob
ReadingProgress
```

Xác định:

```text
Entity
Value Object
Invariant
Behavior
Domain Service
Domain Event
```

Đặc biệt hãy suy nghĩ:

```text
CrawlerJob
```

có state:

```text
PENDING
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
```

và các behavior:

```python
job.start()
job.pause()
job.resume()
job.fail()
job.complete()
job.cancel()
```

Đây sẽ là ví dụ rất tốt để chúng ta tiếp tục xây Clean Architecture thực tế.

---

# 47. Tổng kết Buổi 5

Hãy nhớ mô hình:

```text
                 DOMAIN
                   │
        ┌──────────┼──────────┐
        │          │          │
     Entity     Value       Domain
                Object      Service
        │          │          │
        └──────────┼──────────┘
                   │
              Invariants
                   │
                Behavior
```

Trong đó:

```text
Entity
→ identity + lifecycle + behavior

Value Object
→ value + invariant + immutable thường dùng

Domain Service
→ business logic không tự nhiên thuộc một Entity

Domain Event
→ business fact đã xảy ra

Domain Invariant
→ điều kiện domain luôn phải bảo vệ
```

Và nguyên tắc quan trọng nhất:

> **Domain Model mô hình hóa business, không mô hình hóa database.**

---

## Chuỗi kiến thức hiện tại

```text
Buổi 1
Clean Architecture
        ↓
Buổi 2
Dependency Rule
        ↓
Buổi 3
Boundary / Cohesion / Coupling
        ↓
Buổi 4
Architecture vs Design
        ↓
Buổi 5
Domain Model
        ↓
Entity
Value Object
Domain Service
Invariant
Domain Event
```

**Buổi 6** chúng ta sẽ đi sâu vào **Application Layer & Use Case**: Use Case thực sự là gì, Application Service khác Domain Service ra sao, Input/Output Boundary, Request/Response Model, DTO, Command/Query, orchestration và cách viết một Use Case **không phụ thuộc FastAPI/PySide6/SQLite**.
