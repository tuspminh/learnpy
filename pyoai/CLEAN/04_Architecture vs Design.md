# Buổi 4 — Architecture vs Design Deep Dive

Ở 3 buổi đầu, chúng ta đã xây được nền tảng:

```text
Buổi 1
Architecture
    ↓
bảo vệ business rules

Buổi 2
Dependency Rule
    ↓
dependency hướng vào policy ổn định

Buổi 3
Separation of Concerns
    ↓
high cohesion + controlled coupling
```

Hôm nay chúng ta giải quyết một vấn đề rất dễ gây nhầm lẫn:

> **Architecture khác Design như thế nào?**

Đây là một trong những điểm quan trọng nhất nếu bạn muốn từ "biết Clean Architecture" tiến tới **biết thiết kế hệ thống**.

---

# 1. Architecture và Design không phải một thứ

Hãy nhìn một project:

```text
Story Application
```

Architecture quyết định những thứ như:

```text
Domain
Application
Infrastructure
Presentation
```

và:

```text
Dependency direction
Boundary
Policy vs Detail
```

Trong khi Design quyết định:

```text
Story class
Chapter class
Repository method
DTO
Factory
Mapper
Algorithm
```

Nói ngắn gọn:

> **Architecture quyết định cấu trúc và ranh giới lớn.**

> **Design quyết định cách các thành phần bên trong ranh giới đó được xây dựng.**

---

# 2. Ví dụ đời thường

Hãy tưởng tượng xây một ngôi nhà.

### Architecture

Quyết định:

```text
Phòng khách
Phòng ngủ
Bếp
Nhà vệ sinh
Cầu thang
```

và:

```text
Cửa chính
Luồng di chuyển
Khu vực chịu lực
```

### Design

Quyết định:

```text
Bàn đặt ở đâu
Tủ đặt ở đâu
Kích thước cửa
Loại đèn
Cách mở ngăn kéo
```

Bạn có thể đổi:

```text
Bàn
Ghế
Đèn
```

mà không phá architecture.

---

# 3. Trong software cũng vậy

Ví dụ architecture:

```text
Presentation
      ↓
Application
      ↓
Domain
      ↑
Infrastructure
```

Trong Domain:

```text
Story
Chapter
Author
```

Đó là design.

Bạn có thể refactor:

```text
Story
```

thành:

```text
StoryAggregate
```

mà architecture tổng thể có thể vẫn giữ nguyên.

---

# 4. Architectural Decision

Một quyết định là **architectural decision** khi nó ảnh hưởng đến:

* dependency direction
* boundary
* coupling giữa subsystem
* khả năng thay đổi implementation
* deployment
* scalability
* technology independence
* business policy isolation

Ví dụ:

> Application không được phụ thuộc trực tiếp vào SQLite.

Đây là architectural decision.

---

# 5. Design Decision

Ví dụ:

> `Story.title` dùng `str`.

Đây thường là design decision.

Hoặc:

```python
class Story:
    ...
```

dùng:

```python
@dataclass
class Story:
    ...
```

Đây chủ yếu là design.

---

# 6. Nhưng ranh giới không tuyệt đối

Đây là điểm tinh tế.

Một quyết định có thể bắt đầu là design nhưng trở thành architectural khi nó ảnh hưởng lớn đến hệ thống.

Ví dụ:

```text
Repository
```

Nếu chỉ là một class:

```python
class StoryRepository:
    ...
```

thì có thể chỉ là design.

Nhưng nếu quyết định:

> Application chỉ giao tiếp với persistence thông qua repository abstraction.

thì đây là architecture.

---

# 7. Architecture có "scope" lớn hơn

Ta có:

```text
Architecture
    │
    ├── System boundaries
    ├── Dependency direction
    ├── Deployment
    ├── Integration
    └── Technology boundaries
          │
          ▼
       Design
          │
          ├── Class
          ├── Method
          ├── Algorithm
          ├── Data structure
          └── Pattern
```

Architecture và Design liên quan với nhau nhưng không đồng nhất.

---

# 8. Một ví dụ rất quan trọng

Giả sử bạn có:

```python
class StoryService:
    ...
```

Bên trong class thiết kế rất đẹp:

```text
StoryService
 ├── validate()
 ├── create()
 ├── update()
 └── delete()
```

Có:

* type hints
* dataclass
* clean methods
* unit tests
* SOLID

Nhìn rất đẹp.

Nhưng:

```python
import sqlite3
import requests
from PySide6.QtWidgets import QMessageBox
```

nằm trong đó.

Architecture vẫn tệ.

---

# 9. Class design đẹp ≠ Architecture tốt

Đây là một insight cực kỳ quan trọng.

Bạn có thể có:

```text
Excellent OOP
+
Excellent SOLID
+
Excellent naming
```

nhưng:

```text
Bad architecture
```

Ví dụ:

```text
Domain
   ↓
FastAPI
   ↓
SQLite
```

Nếu dependency direction sai thì:

> Class đẹp không cứu được architecture.

---

# 10. Ngược lại

Bạn có thể có architecture tốt nhưng một số class bên trong chưa hoàn hảo.

Ví dụ:

```text
Domain
Application
Infrastructure
```

dependency đúng.

Nhưng:

```python
class Story:
    ...
```

có thể cần refactor.

Điều đó thường ít nguy hiểm hơn.

Vì:

> **Design có thể thay đổi bên trong boundary mà không phá architecture.**

Đây chính là mục tiêu.

---

# 11. Architecture nên ổn định hơn Design

Một nguyên tắc:

```text
Architecture
     ↓
     STABLE

Design
     ↓
     EVOLVING
```

Ví dụ:

Hôm nay:

```text
Story
Chapter
```

Ngày mai:

```text
StoryAggregate
ChapterCollection
```

Không nhất thiết phải thay architecture.

Nhưng nếu hôm nay:

```text
Application → SQLite
```

ngày mai đổi:

```text
Application → Repository → SQLite
```

thì bạn đang sửa architecture.

---

# 12. Architectural Boundary

Một boundary tốt cho phép:

```text
Inside
```

thay đổi mà:

```text
Outside
```

không cần thay đổi.

Ví dụ:

```text
Application
    │
    ▼
StoryRepository
    ▲
    │
Infrastructure
```

Bạn có thể thay:

```text
SQLiteStoryRepository
```

bằng:

```text
PostgresStoryRepository
```

Application không đổi.

Đây là **architectural decoupling**.

---

# 13. Design bên trong Application

Giả sử:

```text
application/
    use_cases/
        create_story.py
```

Ta có thể thiết kế:

```python
class CreateStory:
    ...
```

hoặc:

```python
class CreateStoryUseCase:
    ...
```

hoặc:

```python
class CreateStoryHandler:
    ...
```

Đây chủ yếu là design choice.

Miễn dependency architecture vẫn đúng.

---

# 14. Design bên trong Domain

Ta có:

```text
domain/
    story.py
```

Có thể dùng:

```python
class Story:
    ...
```

hoặc:

```python
@dataclass
class Story:
    ...
```

hoặc:

```python
class Story(AggregateRoot):
    ...
```

Đây là design.

---

# 15. Nhưng Aggregate là architectural hay design?

Câu hỏi hay.

Thông thường:

```text
Aggregate
```

là **domain design**.

Nhưng:

```text
Aggregate boundary
+
transaction boundary
+
consistency boundary
```

có thể ảnh hưởng đến architecture.

Ví dụ:

```text
Story
 ├── Chapter
 ├── Chapter
 └── Chapter
```

Nếu Story là Aggregate Root:

```text
Story
  ↓
Chapter
```

mọi thay đổi Chapter có thể phải đi qua Story.

Điều đó ảnh hưởng đến:

* transaction
* persistence
* concurrency
* performance

Vì vậy ranh giới giữa design và architecture không phải một đường cứng.

---

# 16. Architecture Decision có "cost"

Mọi architectural decision đều có giá.

Ví dụ:

```text
Repository abstraction
```

giúp:

```text
Database independence
Testing
Decoupling
```

nhưng tạo:

```text
Interface
Implementation
DI
Indirection
```

Đây là:

> **Architectural trade-off**

Không có architecture hoàn hảo.

---

# 17. Over-engineering

Một lỗi thường gặp sau khi học Clean Architecture:

```text
"Tôi phải abstraction mọi thứ."
```

Ví dụ project:

```text
convert_image.py
```

Bạn tạo:

```text
ImageConverter
ImageConverterProtocol
ImageConverterFactory
ImageConverterService
ImageConverterAdapter
ImageConverterDTO
ImageConverterMapper
```

Trong khi logic chỉ:

```python
image.save(pdf)
```

Đây là over-engineering.

---

# 18. Architecture không phải càng nhiều layer càng tốt

Sai lầm:

```text
Clean Architecture
=
nhiều folder
+
nhiều interface
+
nhiều class
```

Không.

Clean Architecture là:

```text
Good boundaries
+
Good dependency direction
+
Protected business rules
```

Có thể project nhỏ chỉ cần:

```text
domain.py
application.py
infrastructure.py
main.py
```

và vẫn có architecture tốt.

---

# 19. Một câu hỏi rất hữu ích

Trước khi tạo abstraction, hỏi:

> **"Tôi đang bảo vệ cái gì?"**

Ví dụ:

```text
Protocol StoryRepository
```

Bảo vệ:

```text
Application
```

khỏi:

```text
Database implementation
```

Rất hợp lý.

Nhưng:

```text
Protocol StoryTitleFormatter
```

nếu chỉ có một implementation và không có variation đáng kể?

Có thể không cần.

---

# 20. Indirection

Clean Architecture thường tạo nhiều indirection.

Ví dụ bạn gọi:

```python
repository.save(story)
```

thực tế có thể đi:

```text
CreateStory
   ↓
StoryRepository
   ↓
SQLiteStoryRepository
   ↓
SQLite
```

Có thêm bước.

Đây là **indirection**.

Indirection không phải xấu.

Nó có giá trị nếu giúp:

```text
isolate change
```

---

# 21. Indirection không có mục đích

Nếu:

```text
CreateStory
 ↓
StoryRepository
 ↓
StoryRepositoryAdapter
 ↓
StoryRepositoryWrapper
 ↓
SQLiteRepository
```

mà tất cả chỉ chuyển tiếp:

```python
return self.repository.save(story)
```

thì bạn có thể đang tạo **accidental complexity**.

---

# 22. Essential Complexity vs Accidental Complexity

Một khái niệm rất quan trọng.

### Essential complexity

Độ phức tạp bản thân bài toán.

Ví dụ crawler phải xử lý:

```text
pagination
retry
rate limit
chapter parsing
anti-bot
```

Đó là complexity thật.

### Accidental complexity

Độ phức tạp do cách chúng ta thiết kế code.

Ví dụ:

```text
5 tầng wrapper
10 interface
15 factory
20 DTO
```

chỉ để:

```text
save()
```

Đó là complexity do kiến trúc/design.

Mục tiêu:

> **Không làm mất essential complexity, nhưng giảm accidental complexity.**

---

# 23. Architecture Decision Records

Khi project lớn, các quyết định architecture nên được ghi lại.

Ví dụ:

```text
ADR-001

Decision:
Application không phụ thuộc trực tiếp vào database.

Reason:
Cho phép thay đổi persistence và test use case
không cần database.

Consequences:
Repository abstraction được đưa vào Application.
```

Đây là một thói quen rất tốt khi làm project production.

---

# 24. Architecture vs Framework

Đây là một bài test rất tốt.

Nếu architecture của bạn là:

```text
FastAPI
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

thì bạn đang mô tả **technology stack**.

Không phải Clean Architecture.

Một architecture tốt hơn:

```text
FastAPI
   ↓
Controller
   ↓
Use Case
   ↓
Domain
   ↑
Repository
   ↑
SQLAlchemy
```

Bây giờ:

```text
FastAPI
SQLAlchemy
PostgreSQL
```

trở thành details.

---

# 25. Framework should be a plugin

Một tư duy rất đẹp:

> **Framework nên giống plugin của application, không phải application là plugin của framework.**

Sai:

```text
FastAPI
 ├── business logic
 ├── database
 ├── validation
 └── domain
```

Đúng hơn:

```text
                 Application
                      │
             ┌────────┴────────┐
             │                 │
          FastAPI           PySide6
          adapter            adapter
```

FastAPI chỉ là một cách đưa request vào application.

---

# 26. Database should be a plugin

Tương tự:

```text
Application
    │
    ▼
Repository
    ▲
    │
 ┌──┴──────┐
SQLite   PostgreSQL
```

Database là detail.

---

# 27. CLI cũng là plugin

Ví dụ:

```bash
story create "One Piece"
```

CLI chỉ làm:

```text
parse arguments
      ↓
create request
      ↓
call use case
      ↓
format output
```

Nó không nên quyết định business rule.

---

# 28. GUI cũng vậy

PySide6:

```text
Button
  ↓
Controller
  ↓
Use Case
```

Không:

```text
Button
  ↓
SQL
```

---

# 29. Một hệ quả rất mạnh

Nếu architecture đúng:

```text
                Application
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      CLI        FastAPI       PySide6
```

Ba interface có thể cùng gọi:

```text
CreateStory
UpdateStory
DeleteStory
```

Business logic không cần copy.

---

# 30. Đây là lý do tôi muốn bạn học Architecture sau OOP/SOLID

Bạn đã học SOLID.

Nhưng cần phân biệt:

```text
OOP
 ↓
Class design

SOLID
 ↓
Object/module design

Clean Architecture
 ↓
System boundaries + dependency direction
```

Ba tầng tư duy khác nhau.

---

# 31. Ví dụ tổng hợp

Architecture:

```text
┌──────────────────────────────────────┐
│            Presentation              │
│                                      │
│ CLI │ FastAPI │ PySide6 │ Flet       │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│             Application              │
│                                      │
│ CreateStory                          │
│ UpdateStory                          │
│ PublishStory                         │
└──────────────────┬───────────────────┘
                   ↓
┌──────────────────────────────────────┐
│                Domain                │
│                                      │
│ Story │ Chapter │ Value Objects      │
└──────────────────────────────────────┘
                   ▲
                   │
┌──────────────────────────────────────┐
│           Infrastructure             │
│                                      │
│ SQLite │ HTTP │ Redis │ Playwright   │
└──────────────────────────────────────┘
```

Đây là architecture.

---

# 32. Design bên trong

Ví dụ:

```text
CreateStory
```

có thể được design:

```python
class CreateStory:

    def __init__(
        self,
        repository: StoryRepository,
        clock: Clock,
        id_generator: IdGenerator,
    ):
        ...
```

Đây là **design decision**.

Nhưng quyết định:

```text
Application không import SQLite
```

là **architectural decision**.

---

# 33. Architecture Stability Principle

Một nguyên tắc quan trọng:

> **Architecture nên bảo vệ những quyết định khó thay đổi và để những quyết định dễ thay đổi ở ngoài.**

Ví dụ:

```text
Hard to change:
Business rules
Core domain
Core workflows
```

Nên ở trong.

```text
Easy to change:
UI
Database
HTTP library
Framework
```

Nên ở ngoài.

---

# 34. Một bài test cực hay

Khi nhìn một dependency, hỏi:

> **"Nếu tôi đổi X, tại sao Y phải biết?"**

Ví dụ:

```text
CreateStory → SQLite
```

Hỏi:

> Nếu đổi SQLite thành PostgreSQL, tại sao `CreateStory` phải biết?

Câu trả lời:

> Không có lý do.

→ Boundary đang sai.

---

# 35. Một bài test khác

Hỏi:

> **"Nếu tôi bỏ UI hoàn toàn, business rule có biến mất không?"**

Nếu:

```text
PySide6 button
```

quyết định:

```text
Story cannot be published without chapters
```

thì business rule đang ở sai nơi.

Nếu bỏ PySide6 mà rule vẫn tồn tại:

```text
Domain
```

thì đúng.

---

# 36. Architecture Decision Tree

Khi gặp một đoạn code mới, hãy suy nghĩ:

```text
                Đây là gì?
                    │
          ┌─────────┴─────────┐
          │                   │
       Policy               Detail
          │                   │
          ▼                   ▼
       Core                Outer
          │                   │
      Stable              Volatile
          │                   │
          └────────┬──────────┘
                   │
                Boundary
                   │
             Abstraction
```

Đây là một trong những mental models quan trọng nhất của khóa học.

---

# 37. Bài tập Buổi 4

## Bài 1 — Phân loại

Hãy phân loại các quyết định sau thành:

```text
Architecture
Design
```

### A

> Application không import `sqlite3`.

### B

> Dùng `dataclass(frozen=True)` cho `Email`.

### C

> Repository implementation nằm trong Infrastructure.

### D

> `Story.title` dùng `str`.

### E

> CLI và FastAPI cùng sử dụng một Use Case.

### F

> Dùng `Protocol` cho `StoryRepository`.

### G

> Dùng SQLite thay vì PostgreSQL.

Không phải câu nào cũng chỉ có một đáp án tuyệt đối. Hãy giải thích **lý do**.

---

# 38. Bài 2 — Phát hiện architecture violation

Cho:

```python
class PublishStory:

    def execute(self, story):

        if not story.chapters:
            raise ValueError(
                "Cannot publish empty story"
            )

        QMessageBox.information(
            None,
            "Success",
            "Story published"
        )

        conn = sqlite3.connect("story.db")

        conn.execute(
            "UPDATE stories SET published = 1 WHERE id = ?",
            (story.id,),
        )

        conn.commit()
```

Hãy tìm tất cả vấn đề.

Tôi muốn bạn phân loại chúng thành:

```text
Domain problem
Application problem
Infrastructure problem
Presentation problem
Dependency problem
```

---

# 39. Bài 3 — Thiết kế boundary

Bạn có:

```text
DownloadChapter
```

Có thể sử dụng:

```text
requests
httpx
aiohttp
Playwright
```

Hãy thiết kế:

```text
Application
     ↓
     ???
     ↑
     ???
```

Sau đó viết `Protocol`.

---

# 40. Bài 4 — Architecture hay Design?

Một developer nói:

> "Tôi đã dùng Factory Pattern nên project của tôi có Clean Architecture."

Bạn có đồng ý không?

Hãy giải thích.

---

# 41. Bài 5 — Project thực tế

Hãy thiết kế architecture cho:

```text
Novel Reader
```

Chức năng:

```text
Create Story
Add Chapter
Read Chapter
Download Chapter
Publish Story
Start Crawl
Pause Crawl
Resume Crawl
```

Technology:

```text
PySide6
FastAPI
Typer
SQLite
Redis
Playwright
```

Hãy xác định:

### Stable

```text
?
```

### Volatile

```text
?
```

### Domain

```text
?
```

### Application

```text
?
```

### Infrastructure

```text
?
```

### Presentation

```text
?
```

### Boundaries

```text
?
```

---

# 42. Tổng kết Buổi 4

Bạn cần phân biệt thật rõ:

```text
                 SOFTWARE DESIGN
                       │
          ┌────────────┴────────────┐
          │                         │
       ARCHITECTURE              DESIGN
          │                         │
          │                    Class
          │                    Method
          │                    DTO
          │                    Algorithm
          │                    Pattern
          │
     Boundary
     Dependency
     Policy
     Detail
     Deployment
```

Và nhớ 5 nguyên tắc:

> **1. Architecture bảo vệ những thứ ổn định.**

> **2. Details nên nằm ngoài boundary.**

> **3. Design có thể thay đổi mà architecture không nhất thiết thay đổi.**

> **4. Không phải abstraction nào cũng có giá trị.**

> **5. Clean Architecture không phải nhiều layer; nó là kiểm soát dependency và bảo vệ business rules.**

---

## Mental model của 4 buổi đầu

Bạn đã đi qua:

```text
BUỔI 1
Architecture
     ↓
Protect Business Rules

BUỔI 2
Dependency Rule
     ↓
Dependencies Point Inward

BUỔI 3
Separation of Concerns
     ↓
High Cohesion
Low Coupling
Good Boundaries

BUỔI 4
Architecture vs Design
     ↓
Stable Policy
        protected by
Good Boundaries
        from
Volatile Details
```

**Buổi 5** chúng ta sẽ bắt đầu bước vào phần Domain thực sự: **Domain Model Deep Dive — Entity, Value Object, Domain Service, Business Rule, Domain Invariant**, và đặc biệt phân biệt **Domain Model với ORM Model/Database Model**. Đây sẽ là bước nối trực tiếp Clean Architecture với **DDD** mà bạn đã học.
