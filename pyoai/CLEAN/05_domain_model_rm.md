Đúng. Roadmap bạn đưa ra là **roadmap chuẩn của Phần II — Domain Layer**, và buổi 5 trước tôi đã đi hơi rộng, có chạm sang Domain Event/DTO nhưng **chưa bám sát cấu trúc bạn định nghĩa**.

Từ đây tôi sẽ **bám đúng roadmap này**, không tự ý nhảy bài.

## Phần II — Domain Layer

| Buổi   | Chủ đề                 | Trọng tâm                                                                                |
| ------ | ---------------------- | ---------------------------------------------------------------------------------------- |
| **5**  | Domain Model           | Entity, Value Object, Domain Service, Aggregate, Domain Rule, Domain Invariant           |
| **6**  | Entity Deep Dive       | Identity, Lifecycle, Mutable state, Behavior, Entity vs DTO, Entity vs ORM               |
| **7**  | Value Object Deep Dive | Immutable, Equality, Validation, `dataclass(frozen=True)`, Email, Money, URL, StoryTitle |
| **8**  | Domain Invariant       | Invariant, Validation, Business Rule, State Transition, Illegal State, Rich Domain Model |
| **9**  | Aggregate              | Aggregate, Aggregate Root, Transaction Boundary, Consistency Boundary, quá lớn/quá nhỏ   |
| **10** | Domain Service         | Khi nào dùng, khi nào không, Entity vs Service, Stateless Service, orchestration         |

### Một điểm tôi sẽ điều chỉnh

Ở **Buổi 5**, chúng ta chỉ cần xây **bản đồ tổng thể của Domain Model**:

```text
                    Domain Model
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Entity         Value Object    Domain Service
        │                │
        └────────┬───────┘
                 │
              Aggregate
                 │
          ┌──────┴──────┐
          │             │
     Domain Rule    Invariant
```

Sau đó:

```text
Buổi 6 → đào sâu Entity
Buổi 7 → đào sâu Value Object
Buổi 8 → đào sâu Invariant
Buổi 9 → đào sâu Aggregate
Buổi 10 → đào sâu Domain Service
```

Như vậy sẽ tránh việc **Buổi 5 học luôn quá nhiều kiến thức của Buổi 6–10**.

---

# Bây giờ chúng ta reset lại Buổi 5

## Buổi 5 — Domain Model

### Mục tiêu

Sau buổi này, bạn phải trả lời được:

> Domain Model là gì?

> Entity khác Value Object như thế nào?

> Domain Service dùng để làm gì?

> Aggregate là gì?

> Domain Rule và Domain Invariant khác nhau thế nào?

Và quan trọng nhất:

> **Business logic nên được đặt ở đâu?**

---

# 1. Domain Model là gì?

Domain Model là mô hình biểu diễn:

```text
Business Concepts
+
Business Behavior
+
Business Rules
+
Business Constraints
```

Ví dụ ứng dụng đọc truyện:

```text
Story
Chapter
Author
CrawlerJob
ReadingProgress
```

không chỉ là database tables.

Chúng là **business concepts**.

---

# 2. Domain Model không phải Database Model

Database:

```text
stories
chapters
authors
```

Domain:

```text
Story
Chapter
Author
```

Có vẻ giống nhau.

Nhưng mục đích khác nhau.

Database hỏi:

> Dữ liệu được lưu thế nào?

Domain hỏi:

> Business hoạt động thế nào?

---

# 3. Ví dụ

Database:

```sql
stories
-------
id
title
status
```

Domain:

```python
class Story:

    def publish(self):
        ...

    def archive(self):
        ...

    def add_chapter(self):
        ...
```

Database chứa:

```text
data
```

Domain chứa:

```text
data
+
behavior
+
rules
```

---

# 4. Domain Model gồm những gì?

Trong roadmap của chúng ta:

```text
Domain Model
│
├── Entity
│
├── Value Object
│
├── Domain Service
│
├── Aggregate
│
├── Domain Rule
│
└── Domain Invariant
```

Hãy xem từng thành phần.

---

# 5. Entity

Entity là object có:

> **Identity**

Ví dụ:

```python
story = Story(
    id=StoryId(100),
    title="One Piece",
)
```

Story có identity:

```text
StoryId(100)
```

Nếu title thay đổi:

```text
One Piece
    ↓
One Piece Manga
```

thì vẫn là cùng Story.

```text
Identity không đổi
Value có thể đổi
```

Đây là điểm cốt lõi của Entity.

---

# 6. Value Object

Value Object không có identity riêng.

Nó được xác định bởi giá trị.

Ví dụ:

```python
Money(100_000, "VND")
```

Hai object:

```python
Money(100_000, "VND")
Money(100_000, "VND")
```

được xem là cùng giá trị.

Ta quan tâm:

```text
value
```

không quan tâm:

```text
object identity
```

---

# 7. So sánh

```text
Entity
────────────────────
Identity quan trọng
Lifecycle
Có thể mutable
Có behavior


Value Object
────────────────────
Value quan trọng
Không cần identity
Thường immutable
Có validation
```

Ví dụ:

```text
Entity
    Story
    Chapter
    Author

Value Object
    Email
    Money
    URL
    StoryTitle
    ChapterNumber
```

---

# 8. Domain Service

Không phải business logic nào cũng thuộc Entity.

Ví dụ:

```text
Story
Author
Subscription
```

và business rule:

> Author chỉ được publish Story nếu subscription còn hiệu lực.

Logic này liên quan nhiều object.

Không tự nhiên thuộc:

```text
Story
```

hay:

```text
Author
```

Ta có thể dùng:

```python
class StoryPublishingPolicy:

    def can_publish(
        self,
        story,
        author,
        subscription,
    ):
        ...
```

Đây là Domain Service/Domain Policy.

**Buổi 10** chúng ta sẽ đào sâu phần này.

---

# 9. Aggregate

Aggregate là:

> **Một nhóm domain objects được xem như một đơn vị consistency.**

Ví dụ:

```text
Story
├── Chapter
├── Chapter
└── Chapter
```

Có thể thiết kế:

```text
Story
  ↓
Aggregate Root

Chapter
Chapter
Chapter
  ↓
Aggregate members
```

Bên ngoài không trực tiếp sửa Chapter.

Ví dụ:

```python
story.add_chapter(chapter)
```

thay vì:

```python
story.chapters.append(chapter)
```

Aggregate sẽ được đào sâu ở **Buổi 9**.

---

# 10. Domain Rule

Domain Rule là quy tắc nghiệp vụ.

Ví dụ:

> Story phải có ít nhất một Chapter mới được publish.

Hoặc:

> Chapter number phải lớn hơn 0.

Hoặc:

> Story đã archived không được publish.

Rule mô tả:

```text
Business says:
"Điều này phải như vậy."
```

---

# 11. Domain Invariant

Invariant là một loại constraint đặc biệt:

> **Điều kiện phải luôn đúng đối với trạng thái hợp lệ của domain object/aggregate.**

Ví dụ:

```text
Chapter.number > 0
```

Nếu Chapter tồn tại với:

```text
number = -1
```

domain đang ở trạng thái illegal.

Hoặc:

```text
Published Story
    ⇒
must have at least one Chapter
```

Invariant phải được bảo vệ.

Buổi 8 chúng ta sẽ đào cực sâu phần này.

---

# 12. Domain Rule vs Domain Invariant

Ở mức đơn giản:

```text
Domain Rule
    ↓
Business requirement

Domain Invariant
    ↓
Condition that must remain true
```

Ví dụ:

### Rule

> Story không được publish nếu chưa có chapter.

### Invariant

```text
status == PUBLISHED
    ⇒
len(chapters) > 0
```

Invariant biểu diễn rule dưới dạng **điều kiện trạng thái**.

---

# 13. Một Domain Model nhỏ

Ví dụ:

```python
class Story:

    def __init__(self, title):
        self.title = title
        self.chapters = []
        self.status = "draft"

    def add_chapter(self, chapter):
        self.chapters.append(chapter)

    def publish(self):
        if not self.chapters:
            raise ValueError(
                "Story must have a chapter"
            )

        self.status = "published"
```

Ở đây:

```text
Story
```

là Entity.

```text
publish()
add_chapter()
```

là behavior.

```text
must have chapter before publish
```

là Domain Rule.

Và:

```text
published ⇒ chapters > 0
```

là Invariant.

---

# 14. Tư duy quan trọng: Domain Model phải có behavior

Đừng chỉ viết:

```python
@dataclass
class Story:
    id: int
    title: str
    status: str
```

rồi:

```python
class StoryService:

    def publish(self, story):
        ...
```

Nếu business behavior thuộc về Story, hãy cân nhắc:

```python
story.publish()
```

Thay vì:

```python
service.publish(story)
```

Chúng ta sẽ phân tích sâu vấn đề này ở Buổi 6 và Buổi 10.

---

# 15. Domain Model và Clean Architecture

Clean Architecture:

```text
Presentation
      ↓
Application
      ↓
Domain
      ↑
Infrastructure
```

Domain nằm ở trung tâm.

Domain không nên biết:

```text
FastAPI
PySide6
Flet
SQLite
PostgreSQL
Redis
Playwright
```

Domain chỉ biết:

```text
Business
```

---

# 16. Ví dụ với hệ thống crawler

### Domain

```text
Story
Chapter
CrawlerJob
ReadingProgress
```

### Infrastructure

```text
SQLite
Redis
Playwright
HTTPX
```

### Presentation

```text
CLI
PySide6
FastAPI
```

Domain không được biến thành:

```python
class Story:

    def save_to_sqlite(self):
        ...

    def crawl_with_playwright(self):
        ...

    def show_qmessagebox(self):
        ...
```

Đó là trộn concerns.

---

# 17. Một mental model rất quan trọng

Khi nhìn một yêu cầu nghiệp vụ:

> "Story không được publish nếu chưa có chapter."

Đừng bắt đầu bằng:

```text
SQL?
FastAPI?
PySide6?
```

Hãy bắt đầu:

```text
Business rule
       ↓
Domain model
       ↓
Invariant
       ↓
Behavior
```

Sau đó mới nghĩ:

```text
Persistence
API
UI
```

---

# 18. Domain Model không cần biết Use Case

Domain:

```python
story.publish()
```

không cần biết:

```text
PublishStoryUseCase
```

Domain không biết user đang:

```text
click button
gọi API
gõ CLI
```

Nó chỉ biết:

> Business action `publish`.

---

# 19. Domain Model không phải toàn bộ Domain Layer

Một Domain Layer có thể có:

```text
domain/
├── entities/
├── value_objects/
├── services/
├── aggregates/
├── rules/
└── exceptions/
```

Nhưng đừng hiểu rằng phải có đầy đủ tất cả folder.

Nếu domain đơn giản:

```text
domain/
    story.py
```

cũng có thể đủ.

**Architecture phục vụ domain, không phải ngược lại.**

---

# 20. Sai lầm lớn nhất khi học Clean Architecture

Người mới thường nghĩ:

```text
Clean Architecture
=
Folder structure
```

Ví dụ:

```text
domain/
application/
infrastructure/
presentation/
```

rồi nghĩ đã xong.

Không.

Folder chỉ là **physical organization**.

Điều quan trọng là:

```text
Dependency
Boundary
Business rules
```

---

# 21. Một câu hỏi kiểm tra

Nếu tôi xóa:

```text
PySide6
```

Domain có thay đổi không?

**Không.**

Nếu tôi đổi:

```text
SQLite → PostgreSQL
```

Domain có thay đổi không?

**Không nên.**

Nếu business thay đổi:

> Story không được publish nếu chưa có Chapter.

Domain phải thay đổi.

Đây chính là:

```text
Domain = business
Details = outside
```

---

# 22. Bài tập Buổi 5 — bản chuẩn theo roadmap

### Bài 1

Phân loại:

```text
Story
StoryId
Email
Money
Chapter
StoryRepository
StoryPublishingPolicy
SQLiteStoryRepository
```

thành:

```text
Entity
Value Object
Domain Service
Repository
Infrastructure
```

---

### Bài 2

Cho business rules:

```text
1. Story phải có title.

2. Chapter number > 0.

3. Story phải có Chapter mới được publish.

4. Story đã archived không được publish.

5. Published Story không được thêm Chapter.
```

Xác định:

```text
Domain Rule
Domain Invariant
```

---

### Bài 3

Giải thích tại sao:

```python
story.publish()
```

có thể tốt hơn:

```python
story_service.publish(story)
```

trong trường hợp business behavior thuộc về `Story`.

---

### Bài 4

Cho:

```python
class Story:

    def save_to_database(self):
        ...

    def publish(self):
        ...

    def send_email(self):
        ...

    def add_chapter(self):
        ...
```

Hãy xác định method nào:

```text
Domain
Infrastructure
Application
```

và giải thích dependency violation.

---

### Bài 5 — Thiết kế Domain Model

Thiết kế sơ bộ cho:

```text
Novel Reader
```

với:

```text
Story
Chapter
Author
ReadingProgress
CrawlerJob
```

Xác định:

```text
Entity
Value Object
Domain Service
Aggregate
Domain Rule
Domain Invariant
```

**Chưa cần code hoàn chỉnh.**

---

## Roadmap từ đây

Chúng ta sẽ đi đúng thứ tự:

```text
                 PHẦN II
               DOMAIN LAYER

Buổi 5 ── Domain Model
             │
             ├─ Entity
             ├─ Value Object
             ├─ Domain Service
             ├─ Aggregate
             ├─ Domain Rule
             └─ Domain Invariant
                    │
                    ▼
Buổi 6 ── Entity Deep Dive
             │
             ├─ Identity
             ├─ Lifecycle
             ├─ Mutable State
             ├─ Behavior
             ├─ Entity vs DTO
             └─ Entity vs ORM
                    │
                    ▼
Buổi 7 ── Value Object Deep Dive
                    │
                    ▼
Buổi 8 ── Domain Invariant
                    │
                    ▼
Buổi 9 ── Aggregate
                    │
                    ▼
Buổi 10 ─ Domain Service
```

Từ **Buổi 6 trở đi**, tôi sẽ không đưa sâu nội dung của các buổi sau vào bài hiện tại nữa; mỗi buổi sẽ đào đúng một chủ đề, có **lý thuyết → mental model → Python implementation → anti-pattern → refactoring → bài tập → áp dụng vào hệ thống cào/đọc truyện**.
