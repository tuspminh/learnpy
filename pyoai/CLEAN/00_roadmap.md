Được. Tôi sẽ dạy bạn **Clean Architecture Deep Dive với Python** theo hướng **hiểu bản chất → thiết kế → code → test → refactor → áp dụng vào project thực tế**, không chỉ học thuộc 4 tầng.

Vì bạn đã học qua **OOP, Repository Pattern, SQLite3, MVC, DDD, CLI và đang xây hệ thống crawler**, tôi sẽ lấy những thứ đó làm nền để đi sâu hơn.

# Clean Architecture Deep Dive — Python

## Mục tiêu khóa học

Sau khóa học, bạn có thể tự thiết kế một ứng dụng Python có cấu trúc kiểu:

```text
              ┌──────────────────────┐
              │    Presentation      │
              │ CLI / API / GUI      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │    Application       │
              │ Use Cases            │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │       Domain         │
              │ Entity / Value Obj   │
              │ Business Rules       │
              └──────────┬───────────┘
                         ▲
                         │
              ┌──────────┴───────────┐
              │    Infrastructure    │
              │ SQLite / HTTP / File │
              └──────────────────────┘
```

Điểm quan trọng nhất:

> **Business logic không được phụ thuộc vào database, framework, HTTP, GUI hay CLI.**

---

# Roadmap

## Phần I — Tư duy kiến trúc

### Buổi 1 — Clean Architecture là gì?

* Architecture thực sự giải quyết vấn đề gì?
* Vì sao code chạy được chưa có nghĩa là kiến trúc tốt?
* Dependency
* Coupling
* Cohesion
* Framework-driven architecture
* Database-driven architecture
* UI-driven architecture
* Dependency Rule
* Boundary

### Buổi 2 — Dependency Rule Deep Dive

* Dependency là gì?
* Import dependency
* Runtime dependency
* Conceptual dependency
* Control flow vs dependency direction
* Dependency Inversion
* Vì sao dependency phải hướng vào trong?
* Dependency graph

### Buổi 3 — Separation of Concerns

* Responsibility
* Concern
* Layer
* Module
* Package
* Boundary
* Cohesion vs Coupling
* SRP trong kiến trúc

### Buổi 4 — Architecture vs Design

* Architecture là gì?
* Design là gì?
* Class design
* Module design
* Package design
* Application architecture
* Khi nào một class quá lớn?
* Khi nào abstraction là over-engineering?

---

# Phần II — Domain Layer

### Buổi 5 — Domain Model

* Entity
* Value Object
* Domain Service
* Aggregate
* Domain Rule
* Domain Invariant

### Buổi 6 — Entity Deep Dive

* Identity
* Lifecycle
* Mutable state
* Behavior
* Entity vs DTO
* Entity vs ORM Model

### Buổi 7 — Value Object Deep Dive

* Immutable object
* Equality by value
* Validation
* `dataclass(frozen=True)`
* `Email`
* `Money`
* `URL`
* `StoryTitle`

### Buổi 8 — Domain Invariant

* Invariant là gì?
* Validation vs invariant
* Business rule
* State transition
* Illegal state
* Rich Domain Model

### Buổi 9 — Aggregate

* Aggregate là gì?
* Aggregate Root
* Transaction boundary
* Consistency boundary
* Aggregate quá lớn
* Aggregate quá nhỏ

### Buổi 10 — Domain Service

* Khi nào dùng Domain Service?
* Khi nào không nên dùng?
* Entity behavior vs Domain Service
* Stateless service
* Business logic orchestration

---

# Phần III — Application Layer

### Buổi 11 — Use Case

Đây là phần đặc biệt quan trọng.

* Use Case là gì?
* Application Service
* Command
* Query
* Input Boundary
* Output Boundary
* Use Case vs Service
* Use Case vs Controller

Ví dụ:

```text
CreateStory
UpdateStory
DeleteStory
GetStory
ListStories
StartCrawl
PauseCrawl
ResumeCrawl
```

### Buổi 12 — Use Case Deep Dive

* Input DTO
* Output DTO
* Request Model
* Response Model
* Dependency của Use Case
* Transaction boundary
* Error handling

### Buổi 13 — Repository Pattern

* Repository thực sự là gì?
* Repository interface
* Repository implementation
* Repository vs DAO
* Repository vs ORM
* Repository nằm ở đâu?

### Buổi 14 — Dependency Inversion trong Python

* `ABC`
* `Protocol`
* Dependency Injection
* Constructor Injection
* Function Injection
* Composition Root

### Buổi 15 — Application Transaction

* Transaction boundary
* Unit of Work
* Commit / Rollback
* Atomicity
* Use Case và transaction

---

# Phần IV — Infrastructure

### Buổi 16 — Database Adapter

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

* SQLite
* PostgreSQL
* Repository implementation
* Mapping Domain ↔ Database
* ORM model ≠ Domain Entity

### Buổi 17 — Persistence Mapping

Ví dụ:

```text
Story Entity
     ↓
StoryRecord
     ↓
SQLite row
```

* Mapper
* Persistence Model
* Domain Model
* Anti-Corruption Layer

### Buổi 18 — External Service

* HTTP API
* File system
* Redis
* Message Queue
* Web scraper

Ví dụ:

```python
class StorySource(Protocol):
    def fetch_story(self, url: str) -> str:
        ...
```

Domain/Application không cần biết implementation là:

```text
Requests
HTTPX
aiohttp
Playwright
```

### Buổi 19 — Framework Independence

* FastAPI
* Flask
* PySide6
* Flet
* Typer
* Click

Framework chỉ nên nằm ở **outer layer**.

---

# Phần V — Presentation

### Buổi 20 — Controller

```text
HTTP Request
     ↓
Controller
     ↓
Use Case
     ↓
Domain
```

* Controller
* Request parsing
* Response mapping
* Validation boundary

### Buổi 21 — CLI Architecture

Áp dụng với:

```bash
story crawl
story list
story read
story pause
```

Thiết kế:

```text
CLI
 ↓
Controller
 ↓
Use Case
 ↓
Repository
```

### Buổi 22 — GUI Architecture

Áp dụng vào PySide6/Flet:

```text
UI
 ↓
Controller
 ↓
Use Case
 ↓
Domain
```

UI **không được chứa business logic**.

---

# Phần VI — Cross-Cutting Concerns

### Buổi 23 — Error Architecture

* Domain Exception
* Application Exception
* Infrastructure Exception
* Exception translation
* Error boundary

### Buổi 24 — Logging

* Logging boundary
* Structured logging
* Domain có nên `logger.info()`?
* Application logging
* Infrastructure logging

### Buổi 25 — Configuration

* Environment
* Settings
* Dependency Injection
* Configuration boundary

### Buổi 26 — Event & Domain Event

```text
StoryCreated
StoryUpdated
CrawlStarted
CrawlFinished
```

* Domain Event
* Event Handler
* Event Dispatcher
* In-process event

---

# Phần VII — Testing

### Buổi 27 — Unit Testing Domain

Test:

```text
Entity
Value Object
Aggregate
Domain Service
```

Không cần:

```text
SQLite
HTTP
Framework
```

### Buổi 28 — Use Case Testing

```text
Use Case
   ↓
Fake Repository
```

* Fake
* Stub
* Mock
* Spy
* Dependency injection

### Buổi 29 — Integration Testing

* Repository + SQLite
* HTTP adapter
* Database
* External service

### Buổi 30 — Architecture Testing

Kiểm tra:

```text
domain
  ❌ không import infrastructure

application
  ❌ không import PySide6

domain
  ❌ không import FastAPI
```

Đây là một chủ đề rất quan trọng nhưng thường bị bỏ qua.

---

# Phần VIII — Advanced Architecture

### Buổi 31 — Composition Root

Tất cả implementation được nối với nhau ở một nơi:

```text
main.py
   │
   ├── Repository
   ├── Service
   ├── Use Case
   └── Controller
```

### Buổi 32 — Dependency Injection Container

* Manual DI
* Container
* Factory
* Khi nào cần DI framework?
* Khi nào không cần?

### Buổi 33 — CQRS

```text
Command → thay đổi state

Query → đọc state
```

* Command
* Query
* Read Model
* Write Model

### Buổi 34 — Ports & Adapters

So sánh:

```text
Clean Architecture
Hexagonal Architecture
Onion Architecture
Layered Architecture
```

### Buổi 35 — Clean Architecture + DDD

Kết hợp hai tư duy:

```text
DDD
 ↓
Domain Model

Clean Architecture
 ↓
Dependency direction
```

### Buổi 36 — Anti-Corruption Layer

Đặc biệt quan trọng khi tích hợp:

```text
Crawler Source
External API
Legacy System
Database
```

---

# Phần IX — Refactoring

### Buổi 37 — Nhận diện Architecture Smell

Ví dụ:

```python
def create_story():
    db.execute(...)
    requests.get(...)
    validate(...)
    send_email(...)
```

Tại sao đây là vấn đề?

### Buổi 38 — Refactor God Service

Từ:

```text
StoryService 1000 lines
```

thành:

```text
Use Cases
Domain
Repository
Adapters
```

### Buổi 39 — Refactor Legacy Project

Chúng ta sẽ lấy một project "xấu":

```text
app.py
 ├── SQLite
 ├── requests
 ├── business logic
 ├── CLI
 └── validation
```

và từng bước refactor.

---

# Phần X — Project thực tế

### Buổi 40–45 — Story Management System

Tôi đề xuất dùng chính loại project gần với những gì bạn đang xây:

```text
Story Reading System
```

Architecture:

```text
story_app/
│
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── services/
│   ├── events/
│   └── repositories/
│
├── application/
│   ├── commands/
│   ├── queries/
│   ├── dto/
│   └── use_cases/
│
├── infrastructure/
│   ├── database/
│   ├── repositories/
│   ├── http/
│   ├── scraper/
│   └── filesystem/
│
├── presentation/
│   ├── cli/
│   ├── api/
│   └── gui/
│
└── bootstrap/
    └── container.py
```

Sau đó chúng ta có thể chạy **cùng một application core** bằng:

```text
CLI
 │
 ├──────────────┐
 │              │
PySide6       FastAPI
 │              │
 └──────┬───────┘
        ↓
   Application
        ↓
      Domain
```

Đây mới là mục tiêu thực sự của Clean Architecture.

---

# Một nguyên tắc tôi muốn bạn nhớ ngay từ đầu

Đừng học Clean Architecture như:

> "Có 4 folder: domain/application/infrastructure/presentation."

Đó chỉ là **cấu trúc thư mục**.

Cốt lõi là:

```text
                DETAIL
                  │
                  │
                  ▼
        ┌──────────────────┐
        │ Infrastructure   │
        │ SQLite / HTTP    │
        │ PySide6 / FastAPI│
        └────────┬─────────┘
                 │
                 │ depends on
                 ▼
        ┌──────────────────┐
        │   Application    │
        │    Use Cases     │
        └────────┬─────────┘
                 │
                 │ depends on
                 ▼
        ┌──────────────────┐
        │     Domain       │
        │ Business Rules   │
        └──────────────────┘
                 ▲
                 │
              STABLE
```

**Domain càng ổn định thì kiến trúc càng tốt.**

Nếu ngày mai bạn đổi:

```text
SQLite → PostgreSQL
requests → httpx
CLI → FastAPI
PySide6 → Flet
```

thì **business rules gần như không cần thay đổi**.

Đó chính là sức mạnh mà chúng ta sẽ đào sâu trong khóa này.

---

## Cách tôi sẽ dạy mỗi buổi

Mỗi buổi sẽ theo format:

1. **Concept** — hiểu bản chất.
2. **Problem** — xem kiến trúc tệ.
3. **Why** — tại sao nó tệ.
4. **Design** — thiết kế lại.
5. **Python implementation** — code.
6. **Testing** — test.
7. **Refactoring** — cải thiện.
8. **Architecture reasoning** — giải thích tại sao thiết kế đó đúng.
9. **Bài tập** — bạn tự thiết kế/code.
10. **Review** — tôi review code của bạn như code production.

Và tôi sẽ **không nhảy ngay vào framework**. Chúng ta sẽ xây một Clean Architecture thuần Python trước, sau đó mới đưa **SQLite, HTTP, CLI, PySide6/Flet, crawler** vào.
