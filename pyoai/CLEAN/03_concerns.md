# Buổi 3 — Separation of Concerns, Boundary, Cohesion & Coupling

Buổi 2 chúng ta đã học:

> **Dependency phải hướng về phía abstraction và policy ổn định.**

Buổi 3 sẽ trả lời một câu hỏi sâu hơn:

> **Làm sao biết nên tách hệ thống thành những phần nào?**

Đây chính là vai trò của:

* Separation of Concerns
* Responsibility
* Cohesion
* Coupling
* Boundary
* SRP ở cấp architecture

---

# 1. Separation of Concerns là gì?

**Separation of Concerns — SoC**:

> Mỗi concern khác nhau nên được tách biệt để chúng có thể thay đổi độc lập.

Ví dụ một ứng dụng tạo Story có các concern:

```text
Create Story
├── Business validation
├── Persistence
├── HTTP
├── Logging
├── Authentication
├── CLI
└── UI
```

Một architecture tệ có thể gom tất cả vào:

```python
class StoryService:
    ...
```

Kết quả:

```text
StoryService
 ├── business logic
 ├── SQL
 ├── HTTP
 ├── CLI
 ├── logging
 └── validation
```

Đây là **vi phạm Separation of Concerns**.

---

# 2. Concern không đồng nghĩa với class

Đây là một hiểu lầm phổ biến.

Không phải:

```text
1 concern = 1 class
```

Ví dụ:

```text
Domain
```

là một concern lớn.

Bên trong có thể có:

```text
Entity
Value Object
Domain Service
Aggregate
```

Tương tự:

```text
Infrastructure
```

cũng là một concern lớn:

```text
Database
HTTP
File System
Message Queue
```

Do đó SoC có thể áp dụng ở nhiều cấp:

```text
System
 ↓
Module
 ↓
Package
 ↓
Class
 ↓
Method
```

---

# 3. Responsibility là gì?

Một responsibility không đơn giản là:

> "Class này có một method."

Mà gần hơn với:

> **Một lý do để code phải thay đổi.**

Đây chính là tư duy quan trọng của **Single Responsibility Principle**.

Ví dụ:

```python
class UserService:

    def create_user(self):
        ...

    def send_email(self):
        ...

    def generate_pdf(self):
        ...

    def save_to_database(self):
        ...
```

Nhìn method thì có vẻ bình thường.

Nhưng class có nhiều **reasons to change**:

```text
User requirements
     ↓
create_user()

Email provider thay đổi
     ↓
send_email()

PDF library thay đổi
     ↓
generate_pdf()

Database thay đổi
     ↓
save_to_database()
```

Vậy class có nhiều responsibility.

---

# 4. SRP không chỉ áp dụng cho class

Đây là một trong những điểm quan trọng nhất của khóa học.

Nhiều người hiểu SRP:

> "Một class chỉ nên làm một việc."

Quá đơn giản.

Ở cấp architecture:

```text
Presentation
Application
Domain
Infrastructure
```

cũng phải có responsibility riêng.

Ví dụ:

```text
Presentation
    → giao tiếp với user

Application
    → điều phối use case

Domain
    → business rules

Infrastructure
    → kết nối thế giới bên ngoài
```

Đây là **SRP ở cấp architecture**.

---

# 5. Ví dụ một hệ thống không có Separation

```python
def create_story(title):

    # CLI
    print("Creating story...")

    # validation
    if not title:
        print("Invalid title")
        return

    # business logic
    story = Story(title)

    # database
    conn = sqlite3.connect("story.db")

    # SQL
    conn.execute(
        "INSERT INTO stories(title) VALUES (?)",
        (title,),
    )

    conn.commit()

    # logging
    logging.info("Story created")

    # notification
    requests.post(
        "https://example.com/notify"
    )

    print("Done")
```

Một function đang chứa:

```text
Presentation
Validation
Domain
Database
Logging
HTTP
```

Đây là **architecture smell** rất rõ.

---

# 6. Tách concern

Ta có thể biến thành:

```text
CLI
 ↓
CreateStory
 ↓
Story
 ↓
StoryRepository
 ↓
SQLiteStoryRepository
```

Và:

```text
CreateStory
 ↓
Event
 ↓
NotificationHandler
```

Bây giờ:

```text
CLI
```

chỉ quan tâm presentation.

```text
CreateStory
```

chỉ quan tâm application behavior.

```text
Story
```

chỉ quan tâm domain.

```text
SQLiteStoryRepository
```

chỉ quan tâm persistence.

---

# 7. Cohesion

Bây giờ đến khái niệm cực kỳ quan trọng:

> **Cohesion đo mức độ các thành phần bên trong một module/class có liên quan với nhau.**

Ví dụ tốt:

```python
class Money:
    ...
```

Các method:

```text
add
subtract
multiply
compare
```

đều liên quan tới Money.

→ **High cohesion**

---

# 8. Low Cohesion

Ví dụ:

```python
class Utils:

    def resize_image(self):
        ...

    def validate_email(self):
        ...

    def connect_database(self):
        ...

    def crawl_website(self):
        ...

    def calculate_salary(self):
        ...
```

Những thứ này không có lý do tồn tại chung.

```text
Utils
 ├── Image
 ├── Email
 ├── Database
 ├── Web
 └── Salary
```

→ **Low cohesion**

---

# 9. High Cohesion không có nghĩa class nhỏ

Một class 500 dòng **có thể** có cohesion cao.

Ví dụ parser phức tạp:

```text
HTMLParser
```

có 500 dòng nhưng toàn bộ code đều liên quan đến parsing HTML.

Trong khi:

```python
utils.py
```

chỉ 100 dòng nhưng chứa 20 loại chức năng khác nhau.

Vậy:

```text
500 lines + high cohesion
```

có thể tốt hơn:

```text
100 lines + low cohesion
```

Đừng đánh giá architecture chỉ bằng số dòng.

---

# 10. Coupling

Nhắc lại:

> **Coupling là mức độ một component phụ thuộc vào component khác.**

Ví dụ:

```text
CreateStory
    ↓
SQLite
```

coupling cao.

Nếu:

```text
CreateStory
    ↓
StoryRepository
```

thì coupling thấp hơn.

---

# 11. Nhưng coupling không phải lúc nào cũng xấu

Đây là điểm tinh tế.

Một hệ thống không thể:

```text
0 coupling
```

Không thể.

Ví dụ:

```text
CreateStory
    ↓
Story
```

`CreateStory` rõ ràng cần `Story`.

Đó là coupling.

Vấn đề là:

> **Couple với cái gì?**

---

# 12. Stable coupling vs unstable coupling

Ví dụ:

```text
CreateStory
    ↓
Story
```

Nếu `Story` là domain model ổn định:

```text
HIGH COHESION
+
STABLE DEPENDENCY
```

thì coupling này thường chấp nhận được.

Nhưng:

```text
CreateStory
    ↓
PySide6
```

rất nguy hiểm.

Vì PySide6 là detail dễ thay đổi.

---

# 13. Architectural goal

Ta không cố:

```text
eliminate coupling
```

Mà:

> **Control coupling.**

Đặc biệt:

```text
Stable Policy
    ↑
    │
should be protected
    │
Volatile Detail
```

---

# 14. Boundary

Boundary là nơi chúng ta **kiểm soát dependency**.

Ví dụ:

```text
┌───────────────────────────────┐
│         Application           │
│                               │
│     CreateStory               │
│          │                    │
│          ▼                    │
│   StoryRepository             │
│                               │
└──────────────┬────────────────┘
               │
               │ Boundary
               │
┌──────────────▼────────────────┐
│       Infrastructure          │
│                               │
│ SQLiteStoryRepository         │
│                               │
└───────────────────────────────┘
```

Boundary nói:

> "Application chỉ biết contract. Infrastructure chịu trách nhiệm implementation."

---

# 15. Boundary không nhất thiết là file

Boundary có thể là:

### Module boundary

```text
application/
infrastructure/
```

### Package boundary

```text
domain/
application/
```

### Interface boundary

```python
class StoryRepository(Protocol):
    ...
```

### Process boundary

```text
Application
    ↓
Redis Queue
    ↓
Crawler Worker
```

### Network boundary

```text
Application
    ↓ HTTP
External API
```

---

# 16. Boundary là nơi thay đổi xảy ra

Đây là một insight quan trọng.

Hãy tưởng tượng:

```text
Application
      │
      │ Repository
      │
      ▼
Database
```

Database có thể thay đổi:

```text
SQLite
 ↓
PostgreSQL
 ↓
MariaDB
```

Nếu boundary tốt:

```text
Application
    │
    │ không đổi
    ▼
Repository
    ▲
    │
    ├── SQLite
    ├── PostgreSQL
    └── MariaDB
```

Thay đổi được **đẩy ra ngoài boundary**.

---

# 17. Change Amplification

Một architectural smell rất quan trọng:

> Một thay đổi nhỏ nhưng phải sửa rất nhiều nơi.

Ví dụ database đổi từ SQLite sang PostgreSQL.

Architecture xấu:

```text
SQLite change
 ↓
Domain
 ↓
Service
 ↓
Controller
 ↓
CLI
 ↓
Tests
 ↓
GUI
```

Một thay đổi:

```text
1 requirement
```

dẫn đến:

```text
20 files changed
```

Đó là **change amplification**.

---

# 18. Architecture tốt

Database đổi:

```text
SQLite
  ↓
PostgreSQL
```

chủ yếu:

```text
infrastructure/database/
```

thay đổi.

Application:

```text
CreateStory
```

không đổi.

Domain:

```text
Story
```

không đổi.

Đây là một mục tiêu rất quan trọng của architecture.

---

# 19. Volatility

Ta có thể vẽ:

```text
                Stable
                  ↑
                  │
               Domain
                  │
             Application
                  │
          ───── Boundary ─────
                  │
            Infrastructure
                  │
         Highly Volatile
```

Các thứ thường volatile:

```text
UI
Database
Framework
External API
Network
Filesystem
```

Clean Architecture đẩy những thứ volatile ra ngoài.

---

# 20. Một ví dụ thực tế với PySide6

Sai:

```python
class StoryWindow(QMainWindow):

    def save_story(self):
        title = self.title_input.text()

        if len(title) < 3:
            QMessageBox.warning(...)
            return

        conn = sqlite3.connect(...)
        conn.execute(...)

        if title == "...":
            ...
```

Widget đang biết:

```text
PySide6
Validation
Business Rule
SQLite
SQL
```

Cohesion thấp.

Coupling cao.

---

# 21. Thiết kế lại

UI:

```python
class StoryWindow:

    def save_story(self):
        title = self.title_input.text()

        self.create_story.execute(title)
```

Application:

```python
class CreateStory:

    def execute(self, title):
        story = Story(title)
        self.repository.save(story)
```

Domain:

```python
class Story:

    def __init__(self, title):
        if not title.strip():
            raise ValueError("Invalid title")

        self.title = title
```

Infrastructure:

```python
class SQLiteStoryRepository:

    def save(self, story):
        ...
```

Ta có:

```text
PySide6
   ↓
Controller
   ↓
CreateStory
   ↓
Story
   ↓
Repository
   ↓
SQLite
```

Mỗi phần có concern rõ hơn.

---

# 22. Một điểm tinh tế: Validation nằm ở đâu?

Đây là câu hỏi thường gây tranh luận.

Ví dụ:

```python
if not title:
    raise ValueError(...)
```

Có thể nằm ở:

```text
UI
Application
Domain
```

Nhưng phải phân biệt **loại validation**.

### Presentation validation

Ví dụ:

```text
Input có phải string?
Form field có bị bỏ trống?
```

Có thể xử lý ở UI.

### Application validation

Ví dụ:

```text
Request có đủ field?
User có quyền gọi Use Case?
```

Application có thể xử lý.

### Domain invariant

Ví dụ:

```text
Story không thể tồn tại nếu title invalid.
```

Nên nằm trong Domain.

Đây chính là Separation of Concerns.

---

# 23. Một rule rất hữu ích

Hỏi:

> "Nếu UI biến mất, rule này còn tồn tại không?"

Nếu **còn**:

```text
Domain/Application
```

Nếu **không**:

```text
Presentation
```

Ví dụ:

```text
Button phải disable khi loading
```

→ UI concern.

Nhưng:

```text
Không được publish Story chưa có Chapter
```

→ Business rule.

Dù bạn dùng:

```text
CLI
API
GUI
```

rule vẫn phải tồn tại.

→ Domain/Application.

---

# 24. SRP ở nhiều cấp

Hãy xem:

```text
System
```

có:

```text
Presentation
Application
Domain
Infrastructure
```

Đây là separation.

Trong Application:

```text
CreateStory
UpdateStory
DeleteStory
PublishStory
```

Mỗi Use Case có responsibility riêng.

Trong Domain:

```text
Story
Chapter
Author
```

Mỗi entity có responsibility riêng.

Trong Infrastructure:

```text
SQLiteStoryRepository
HttpStorySource
RedisQueue
```

mỗi adapter có concern riêng.

Ta có:

```text
Architecture
    ↓
Package
    ↓
Module
    ↓
Class
    ↓
Method
```

SRP và SoC có thể áp dụng ở **mọi cấp**.

---

# 25. Một sai lầm phổ biến: tách quá mức

Ví dụ:

```python
class CreateStoryValidator:
    ...

class CreateStoryMapper:
    ...

class CreateStoryFactory:
    ...

class CreateStoryBuilder:
    ...

class CreateStoryLogger:
    ...

class CreateStoryExecutor:
    ...

class CreateStoryService:
    ...
```

Bạn có thể đạt:

```text
LOW COUPLING
```

nhưng lại tạo:

```text
LOW COHESION
+
HIGH COMPLEXITY
```

và cuối cùng:

```text
Architecture ≠ Maintainability
```

Clean Architecture không có nghĩa:

> "Càng nhiều abstraction càng tốt."

---

# 26. Abstraction Tax

Mỗi abstraction đều có chi phí:

```text
Interface
Factory
Adapter
Mapper
DTO
Dependency Injection
```

Chúng tạo thêm:

```text
Code
Cognitive load
Indirection
Testing complexity
```

Do đó phải có lý do.

Một boundary tốt đáng để trả abstraction tax.

Một boundary giả tạo thì không.

---

# 27. Rule thực dụng

Khi muốn tạo abstraction, hãy hỏi:

```text
1. Có volatility không?

2. Có nhiều implementation không?

3. Có boundary thực sự không?

4. Có testability benefit không?

5. Có business policy cần được bảo vệ không?

6. Nếu không tạo abstraction thì thay đổi có lan rộng không?
```

Nếu tất cả đều "không":

> Có thể bạn không cần abstraction.

---

# 28. Coupling Matrix

Hãy tưởng tượng:

```text
                 Domain Application Infrastructure UI

Domain               -       ✓          ✗          ✗

Application          ✓       -          ✗          ✗

Infrastructure       ✓       ✓          -          ✗

UI                   ✓       ✓          ✓          -
```

Trong Clean Architecture, dependency hợp lệ phải được kiểm soát.

Một dependency kiểu:

```text
Domain → Infrastructure
```

là dấu hiệu nguy hiểm.

Ví dụ:

```python
# domain/story.py

import sqlite3
```

🚨 Architecture violation.

---

# 29. "Import direction" là một dấu hiệu rất hữu ích

Trong Python:

```python
from infrastructure.database import SQLiteStoryRepository
```

nếu xuất hiện trong:

```text
domain/
```

hãy lập tức cảnh giác.

Ngược lại:

```python
from application.ports import StoryRepository
```

trong infrastructure:

```text
infrastructure/database/sqlite.py
```

thường hợp lý.

Ta muốn:

```text
infrastructure
      ↓
application
      ↓
domain
```

---

# 30. Dependency không chỉ một chiều về runtime

Hãy xem:

```text
CLI
 ↓
Use Case
 ↓
Repository
 ↓
SQLite
```

Runtime flow:

```text
OUT → IN → OUT
```

Nhưng source-code dependency:

```text
CLI
 ↓
Application
 ↓
Domain

Infrastructure
 ↓
Application
 ↓
Domain
```

Đây chính là lý do Clean Architecture có vẻ "ngược đời" lúc mới học.

---

# 31. Một bài toán thực tế

Hãy xem crawler system:

```text
CLI
 ↓
CrawlerService
 ↓
Playwright
 ↓
Website
```

Nếu:

```python
class CrawlerService:

    def crawl(self, url):
        browser = playwright.chromium.launch()
        ...
```

thì:

```text
CrawlerService
     ↓
Playwright
```

Coupling cao.

Thay Playwright bằng:

```text
HTTPX
Requests
Selenium
```

sẽ ảnh hưởng service.

---

# 32. Tách boundary

Ta thiết kế:

```python
class PageFetcher(Protocol):

    def fetch(self, url: str) -> str:
        ...
```

Application:

```python
class CrawlChapter:

    def __init__(self, fetcher: PageFetcher):
        self.fetcher = fetcher

    def execute(self, url):
        html = self.fetcher.fetch(url)
        ...
```

Infrastructure:

```python
class PlaywrightPageFetcher:

    def fetch(self, url):
        ...
```

Bây giờ:

```text
CrawlChapter
      ↓
 PageFetcher
      ↑
      │
PlaywrightPageFetcher
```

---

# 33. Đây chính là "Protected Variation"

Một khái niệm rất đáng nhớ:

> **Bao bọc phần có khả năng thay đổi bằng abstraction.**

Ví dụ:

```text
Possible variation:

Database
HTTP library
GUI
Queue
External API
```

Ta đặt boundary:

```text
Application
     │
     ▼
 abstraction
     ▲
     │
implementation
```

Thay đổi xảy ra phía ngoài.

Core được bảo vệ.

---

# 34. Bốn câu hỏi kiến trúc

Khi thiết kế bất kỳ feature nào, hãy hỏi:

### 1. What changes?

```text
Cái gì có khả năng thay đổi?
```

### 2. What stays stable?

```text
Cái gì là business rule ổn định?
```

### 3. Where is the boundary?

```text
Ranh giới giữa chúng nằm đâu?
```

### 4. Which direction should dependency point?

```text
Dependency nên hướng về đâu?
```

Đây là cách tư duy Clean Architecture thực tế.

---

# 35. Bài tập Buổi 3

## Bài 1 — Phân tích SRP

Cho:

```python
class OrderService:

    def create_order(self, data):
        self.validate(data)
        self.calculate_total(data)
        self.save_to_database(data)
        self.send_email(data)
        self.write_log(data)
        self.generate_invoice(data)
```

Hãy xác định **6 reasons to change**.

Sau đó phân loại:

```text
Domain
Application
Infrastructure
Presentation
```

---

# 36. Bài 2 — Cohesion

Class sau:

```python
class StoryManager:

    def create_story(self):
        ...

    def delete_story(self):
        ...

    def parse_html(self):
        ...

    def connect_database(self):
        ...

    def send_notification(self):
        ...

    def export_pdf(self):
        ...
```

Hãy:

1. Đánh giá cohesion.
2. Tách thành các nhóm responsibility.
3. Đề xuất package structure.

---

# 37. Bài 3 — Coupling

Cho:

```python
class PublishStory:

    def __init__(self):
        self.db = SQLiteDatabase()
        self.mailer = GmailMailer()
        self.logger = FileLogger()
```

Hãy xác định:

```text
Policy
Detail
Dependency
Boundary
```

Sau đó thiết kế lại bằng `Protocol`.

---

# 38. Bài 4 — Quan trọng

Bạn có business rule:

> Một Chapter chỉ được publish nếu Story đã hoàn thành.

Có ba UI:

```text
CLI
PySide6
FastAPI
```

Hãy trả lời:

**Rule này nên nằm ở đâu?**

Và giải thích tại sao không nên đặt nó trong:

```python
def on_publish_button_clicked():
    ...
```

---

# 39. Bài 5 — Architecture của hệ thống crawler

Thiết kế các boundary cho:

```text
StoryCrawler
```

Có:

```text
Business:
    Story
    Chapter
    CrawlChapter
    PublishChapter

Infrastructure:
    Playwright
    SQLite
    Redis

Presentation:
    CLI
    PySide6
```

Hãy vẽ:

```text
Domain
Application
Infrastructure
Presentation
```

và chỉ ra dependency nào được phép.

---

# 40. Tổng kết Buổi 3

Bạn cần nắm chắc chuỗi tư duy:

```text
Separation of Concerns
        ↓
Separate responsibilities
        ↓
High Cohesion
        ↓
Low Coupling
        ↓
Create boundaries
        ↓
Protect stable policy
        ↓
Isolate volatile details
```

Và một câu cực kỳ quan trọng:

> **SRP không phải là "mỗi class chỉ có một method". SRP là tổ chức code sao cho một loại thay đổi chỉ ảnh hưởng đến một phần phù hợp của hệ thống.**

Cuối cùng, hãy ghi nhớ mô hình này:

```text
                 STABLE
                   ▲
                   │
              ┌─────────┐
              │ DOMAIN  │
              └────▲────┘
                   │
              ┌────┴────┐
              │  APP    │
              │ USECASE │
              └────▲────┘
                   │
              ═════════════
                BOUNDARY
              ═════════════
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    SQLite       HTTP         GUI
       │           │           │
       └───────────┴───────────┘
                 DETAILS
                VOLATILE
```

**Buổi 4** sẽ chuyển sang một vấn đề rất quan trọng: **Architecture vs Design** — phân biệt architectural decision với class/module design, học cách nhận biết khi nào nên tạo abstraction, khi nào không, và đặc biệt là **làm thế nào một hệ thống có class design đẹp nhưng architecture vẫn sai**.
