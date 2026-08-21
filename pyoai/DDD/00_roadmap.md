Được. Với **Domain-Driven Design (DDD)**, tôi sẽ dạy theo hướng **Python chuyên nghiệp + thực chiến**, không chỉ học khái niệm mà sẽ xây dần một kiến trúc có thể áp dụng vào dự án thật.

Đặc biệt, tôi sẽ lấy **ứng dụng cào truyện và đọc truyện** mà bạn đang xây dựng làm case study xuyên suốt, vì nó rất phù hợp để học DDD.

# Domain-Driven Design Deep Dive — Python

## Mục tiêu khóa học

Sau khóa học, bạn có thể:

* Phân tích domain trước khi viết code.
* Phân biệt **Domain / Application / Infrastructure / Interface**.
* Thiết kế Entity, Value Object, Aggregate.
* Hiểu Aggregate Root và transaction boundary.
* Thiết kế Repository đúng tinh thần DDD.
* Hiểu Domain Service.
* Hiểu Application Service / Use Case.
* Domain Event.
* Command / Query.
* Bounded Context.
* Context Mapping.
* Anti-Corruption Layer.
* Domain model vs database model.
* DDD với SQLite.
* DDD với Python.
* DDD trong hệ thống crawler/worker.
* Thiết kế test cho Domain.
* Refactor từ code CRUD sang Domain Model.
* Kết hợp DDD với Clean Architecture.

---

# Phần I — Tư duy Domain

### Buổi 1 — DDD là gì?

* Domain là gì?
* Business problem vs technical problem
* Vì sao CRUD không đủ cho hệ thống phức tạp
* Domain Model là gì?
* DDD giải quyết vấn đề gì?
* Strategic DDD vs Tactical DDD
* Khi nào **không nên dùng DDD**
* DDD không phải là framework

### Buổi 2 — Domain Discovery

* Business domain
* Subdomain
* Core Domain
* Supporting Subdomain
* Generic Subdomain
* Domain complexity
* Phân tích domain ứng dụng cào truyện

### Buổi 3 — Ubiquitous Language

* Ubiquitous Language
* Business terminology
* Từ ngữ trong code phải phản ánh domain
* Tránh `data`, `manager`, `handler`, `utils`
* Xây dựng glossary
* Ví dụ:

  * `Story`
  * `Chapter`
  * `Source`
  * `Crawler`
  * `CrawlerJob`
  * `ReadingProgress`

### Buổi 4 — Domain Model

* Domain Model là gì?
* Anemic Domain Model
* Rich Domain Model
* Behavior vs data
* Business invariant
* Domain rule
* Model hóa behavior

### Buổi 5 — Event Storming

* Event Storming là gì?
* Domain Event
* Command
* Actor
* Aggregate
* Policy
* Read Model
* Dùng Event Storming để khám phá domain crawler.

---

# Phần II — Strategic DDD

### Buổi 6 — Subdomain

* Core
* Supporting
* Generic
* Cách phân chia domain
* Ví dụ hệ thống đọc truyện

### Buổi 7 — Bounded Context

* Bounded Context là gì?
* Context boundary
* Một từ có thể có nhiều meaning
* `Story` trong các context khác nhau
* Context cho:

  * Crawling
  * Catalog
  * Reading
  * User
  * Notification

### Buổi 8 — Context Mapping

* Context Map
* Partnership
* Shared Kernel
* Customer/Supplier
* Conformist
* Anti-Corruption Layer
* Open Host Service
* Published Language

### Buổi 9 — Domain Architecture

* Domain Layer
* Application Layer
* Infrastructure Layer
* Interface Layer
* Dependency direction
* Dependency Inversion

### Buổi 10 — DDD + Clean Architecture

* DDD và Clean Architecture khác nhau thế nào?
* DDD nằm ở đâu trong Clean Architecture?
* Ports & Adapters
* Dependency Rule
* Thiết kế project Python.

---

# Phần III — Tactical DDD: Entity & Value Object

### Buổi 11 — Entity Deep Dive

* Entity là gì?
* Identity
* Lifecycle
* Equality
* Entity vs DTO
* Entity vs database row

### Buổi 12 — Value Object

* Value Object là gì?
* Identity vs value
* Immutable object
* Equality
* Validation
* `StoryTitle`
* `ChapterNumber`
* `SourceUrl`

### Buổi 13 — Value Object nâng cao

* Composite Value Object
* Normalization
* Canonical representation
* Factory
* Invalid state
* Python implementation

### Buổi 14 — Entity + Value Object

Thiết kế:

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

### Buổi 15 — Domain Invariant

* Invariant là gì?
* Business rule
* Structural rule
* Validation vs invariant
* Invariant phải nằm ở đâu?
* Không cho domain object rơi vào trạng thái invalid.

---

# Phần IV — Aggregate

### Buổi 16 — Aggregate là gì?

Đây là một trong những bài quan trọng nhất.

* Aggregate
* Aggregate Root
* Boundary
* Consistency boundary
* Transaction boundary

### Buổi 17 — Aggregate Root

* Root chịu trách nhiệm gì?
* Không truy cập entity con trực tiếp
* Encapsulation
* Business behavior

Ví dụ:

```python
story.add_chapter(...)
```

thay vì:

```python
story.chapters.append(...)
```

### Buổi 18 — Aggregate Design

* Aggregate quá lớn
* Aggregate quá nhỏ
* Khi nào tách Aggregate?
* Reference by ID
* Không nhúng Aggregate khác

### Buổi 19 — Aggregate + Transaction

* Transaction boundary
* Atomicity
* Consistency
* Concurrency
* SQLite transaction
* Aggregate ảnh hưởng database transaction thế nào?

### Buổi 20 — Aggregate Design Workshop

Thiết kế Aggregate cho hệ thống:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

---

# Phần V — Repository

### Buổi 21 — Repository Pattern

* Repository là gì?
* Repository không phải DAO
* Collection abstraction
* Persistence ignorance

### Buổi 22 — Repository Interface

```python
class StoryRepository(ABC):
    ...
```

* Domain không biết SQLite
* Interface thuộc về domain/application
* Dependency inversion

### Buổi 23 — SQLite Repository

Implement:

```text
SQLiteStoryRepository
SQLiteChapterRepository
```

### Buổi 24 — Unit of Work

* Unit of Work
* Transaction
* Commit
* Rollback
* Repository coordination

### Buổi 25 — Repository + Unit of Work

Thiết kế:

```python
with uow:
    story = story_repo.get(story_id)
    story.add_chapter(chapter)
    uow.commit()
```

---

# Phần VI — Domain Service & Application Service

### Buổi 26 — Domain Service

* Khi nào logic không thuộc Entity?
* Stateless service
* Domain Service vs Utility
* Domain Service vs Application Service

### Buổi 27 — Application Service

* Use Case
* Application Service
* Orchestration
* Transaction management

Ví dụ:

```python
CreateStoryUseCase
AddChapterUseCase
StartCrawlerUseCase
CompleteCrawlerJobUseCase
```

### Buổi 28 — Use Case Design

* Input DTO
* Output DTO
* Command
* Result
* Error handling

### Buổi 29 — Domain Service vs Application Service

So sánh trực tiếp:

```text
Entity
Domain Service
Application Service
Repository
Infrastructure Service
```

### Buổi 30 — Use Case Architecture

Xây dựng hoàn chỉnh:

```text
CLI
 ↓
Use Case
 ↓
Domain
 ↓
Repository
 ↓
SQLite
```

---

# Phần VII — Domain Event

### Buổi 31 — Domain Event

* Domain Event là gì?
* Event vs Command
* Event immutable
* Past tense

Ví dụ:

```text
StoryCreated
ChapterAdded
CrawlerStarted
CrawlerCompleted
```

### Buổi 32 — Event Dispatching

* Event Dispatcher
* Handler
* In-process event bus
* Event registration

### Buổi 33 — Event Handler

Ví dụ:

```text
ChapterAdded
   ↓
Update search index
   ↓
Send notification
   ↓
Update statistics
```

### Buổi 34 — Domain Event + Transaction

* Event timing
* Before commit
* After commit
* Transactional consistency
* Outbox pattern

### Buổi 35 — Outbox Pattern

Đây là bước chuyển từ DDD đơn giản sang kiến trúc production.

```text
Aggregate
   ↓
Domain Event
   ↓
Outbox
   ↓
Worker
   ↓
External system
```

---

# Phần VIII — CQRS

### Buổi 36 — CQRS

* Command
* Query
* Write Model
* Read Model
* Vì sao CQRS phù hợp với domain phức tạp?

### Buổi 37 — Command Model

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
```

### Buổi 38 — Query Model

```text
StoryList
ChapterList
CrawlerDashboard
ReadingPage
```

### Buổi 39 — CQRS với SQLite

Thiết kế:

```text
domain/
application/
infrastructure/
read_model/
```

### Buổi 40 — CQRS thực chiến

Xây dashboard crawler bằng Read Model riêng.

---

# Phần IX — Advanced DDD

### Buổi 41 — Specification Pattern

* Specification
* Business predicates
* Composite specification
* AND / OR / NOT

### Buổi 42 — Policy

* Business Policy
* Policy Object
* Policy vs Specification

### Buổi 43 — Domain Factory

* Factory Method
* Factory Object
* Creation invariant
* Khi nào dùng Factory?

### Buổi 44 — Anti-Corruption Layer

Đặc biệt quan trọng khi crawler lấy dữ liệu từ nhiều website.

```text
Website A
    ↓
Parser
    ↓
ACL
    ↓
Domain Model
```

### Buổi 45 — External System Integration

* API
* Scraper
* External model
* Mapping
* DTO → Domain

---

# Phần X — DDD với Python

### Buổi 46 — Pythonic Domain Model

* Dataclass
* Frozen dataclass
* Enum
* Protocol
* ABC
* Type hints
* Generic Repository

### Buổi 47 — Domain Exceptions

Thiết kế:

```text
DomainError
├── InvalidStoryTitle
├── InvalidChapterNumber
├── ChapterAlreadyExists
└── InvalidStoryState
```

### Buổi 48 — Domain Testing

* Unit test Entity
* Unit test Value Object
* Aggregate test
* Invariant test
* Không cần database

### Buổi 49 — Application Testing

* Use Case test
* Fake Repository
* Fake Unit of Work
* Mock vs Fake

### Buổi 50 — Infrastructure Testing

* SQLite integration test
* Repository test
* Transaction test
* Migration test

---

# Phần XI — Production DDD

### Buổi 51 — DDD Project Structure

Thiết kế project Python production:

```text
src/
└── app/
    ├── domain/
    │   ├── story/
    │   ├── crawler/
    │   └── reading/
    │
    ├── application/
    │   ├── commands/
    │   ├── queries/
    │   └── services/
    │
    ├── infrastructure/
    │   ├── persistence/
    │   ├── crawler/
    │   └── messaging/
    │
    └── interfaces/
        ├── cli/
        └── api/
```

### Buổi 52 — DDD + SQLite

* Database schema
* Mapping domain → relational model
* Repository implementation
* Transaction

### Buổi 53 — DDD + Worker

Kết hợp với kiến trúc crawler-worker của bạn:

```text
Crawler
   ↓
Queue
   ↓
Worker
   ↓
Application Service
   ↓
Domain
   ↓
Repository
```

### Buổi 54 — DDD + Plugin Architecture

Thiết kế:

```text
CrawlerPlugin
 ├── SourceAPlugin
 ├── SourceBPlugin
 └── SourceCPlugin
```

nhưng **plugin không được làm ô nhiễm Domain Model**.

### Buổi 55 — DDD + CLI

Mọi Use Case đều có thể test bằng CLI:

```bash
app story create
app story add-chapter
app crawler start
app crawler pause
app crawler resume
```

---

# Phần XII — Dự án cuối khóa

### Buổi 56 — Phân tích Domain

Event Storming toàn bộ hệ thống.

### Buổi 57 — Bounded Context

Thiết kế:

```text
Catalog Context
Crawler Context
Reading Context
User Context
```

### Buổi 58 — Domain Model

Thiết kế Entity + Value Object + Aggregate.

### Buổi 59 — Repository + Unit of Work

SQLite implementation.

### Buổi 60 — Use Case

Xây Application Layer.

### Buổi 61 — Domain Event

Event Bus + Event Handler.

### Buổi 62 — Crawler Worker

Kết nối Queue Server.

### Buổi 63 — Plugin

Crawler Plugin Architecture.

### Buổi 64 — CQRS

Read Model cho dashboard và reading page.

### Buổi 65 — Testing

Unit + Integration + Application tests.

### Buổi 66 — Refactoring

Phân tích các vấn đề:

* God Aggregate
* Anemic Domain Model
* Fat Service
* Leaky Repository
* Infrastructure leakage
* Primitive obsession
* Wrong bounded context

### Buổi 67 — Production Architecture

Hoàn thiện kiến trúc.

### Buổi 68 — DDD Code Review

Review toàn bộ project theo tiêu chuẩn production.

### Buổi 69 — DDD Anti-patterns

Các lỗi thường gặp khi áp dụng DDD.

### Buổi 70 — Final Project

Hoàn thiện **Story Crawling & Reading Platform**.

---

## Một nguyên tắc quan trọng

Trong khóa này tôi sẽ **không bắt đầu bằng `class Entity`, `Repository`, `Service`**.

Ta sẽ đi theo thứ tự:

```text
Business Problem
       ↓
Domain
       ↓
Subdomain
       ↓
Ubiquitous Language
       ↓
Bounded Context
       ↓
Domain Model
       ↓
Entity / Value Object
       ↓
Aggregate
       ↓
Domain Service
       ↓
Repository
       ↓
Use Case
       ↓
Domain Event
       ↓
Infrastructure
```

Đây chính là điểm khác biệt giữa **học DDD** và chỉ học một đống Design Pattern mang tên DDD.

Nếu bắt đầu, **Buổi 1 sẽ là “DDD là gì và tại sao CRUD bắt đầu thất bại khi domain trở nên phức tạp?”**, sau đó tôi sẽ dùng chính ví dụ **ứng dụng cào và đọc truyện** để phân tích từng bước.
