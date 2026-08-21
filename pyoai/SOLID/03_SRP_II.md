# SOLID Deep Dive — Buổi 3

# SRP Deep Dive: Actor → Responsibility → Boundary → Refactoring

Buổi 2 chúng ta đã hiểu:

> **SRP không phải “mỗi class chỉ làm một việc”.**

Cách hiểu chính xác hơn là:

> **Một module/class nên tập trung vào một nhóm trách nhiệm có cùng lý do thay đổi.**

Hôm nay ta sẽ đi sâu hơn và làm một bài **refactoring thực chiến**.

---

# 1. Vấn đề lớn nhất của SRP: “Responsibility” quá mơ hồ

Xét:

```python
class StoryService:

    def crawl(self, url):
        ...
```

Ta có thể nói:

> “Responsibility của nó là crawl story.”

Nghe hợp lý.

Nhưng bên trong:

```python
def crawl(self, url):
    response = requests.get(url)

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    title = soup.select_one("h1").text
    content = soup.select_one(".content").text

    connection = sqlite3.connect("stories.db")

    connection.execute(
        "INSERT INTO stories(title, content) VALUES (?, ?)",
        (title, content),
    )

    connection.commit()

    send_email(f"Crawled: {title}")
```

thực tế có:

```text
HTTP
HTML parsing
Business data
Database
Notification
```

Do đó câu:

> “Class này crawl story”

chưa đủ để đánh giá SRP.

---

# 2. Actor là công cụ rất mạnh

Một cách phân tích SRP là tìm **actor**.

Actor ở đây hiểu đơn giản là:

> Người/nhóm/requirement có thể yêu cầu behavior đó thay đổi.

Ví dụ:

```text
StoryFetcher
    ↓
Crawler/Network requirement

StoryParser
    ↓
Website structure requirement

StoryRepository
    ↓
Database requirement

NotificationService
    ↓
Notification requirement
```

Nếu các actor khác nhau có thể yêu cầu thay đổi các phần khác nhau của class, đó là dấu hiệu mạnh rằng class đang có nhiều responsibility.

---

# 3. Phân tích `StoryService`

Code:

```python
class StoryService:

    def crawl(self, url):
        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = soup.select_one("h1").text
        content = soup.select_one(".content").text

        connection = sqlite3.connect("stories.db")

        connection.execute(
            "INSERT INTO stories(title, content) VALUES (?, ?)",
            (title, content),
        )

        connection.commit()

        send_email(f"Crawled: {title}")
```

Ta phân loại:

| Code             | Responsibility    |
| ---------------- | ----------------- |
| `requests.get()` | HTTP              |
| `BeautifulSoup`  | Parsing           |
| CSS selector     | Website structure |
| `sqlite3`        | Persistence       |
| SQL              | Database          |
| `send_email()`   | Notification      |
| `crawl()`        | Orchestration     |

Đây là một class có **quá nhiều lý do thay đổi**.

---

# 4. Tìm boundary

Ta có thể chia:

```text
StoryService
│
├── Fetching
├── Parsing
├── Domain
├── Persistence
└── Notification
```

Một thiết kế hợp lý hơn:

```text
StoryFetcher
StoryParser
StoryRepository
NotificationService
Story
CrawlStoryUseCase
```

---

# 5. `Story` — Domain

Đầu tiên ta xác định business concept.

```python
from dataclasses import dataclass


@dataclass
class Story:
    title: str
    content: str
```

Đây là domain object.

Nó không biết:

```text
requests
sqlite3
BeautifulSoup
email
```

Đây là một nguyên tắc rất quan trọng:

> **Domain object không nên biết infrastructure nếu infrastructure không phải business rule.**

---

# 6. `StoryFetcher`

Tách HTTP:

```python
import requests


class StoryFetcher:

    def fetch(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()

        return response.text
```

Responsibility:

```text
Fetch HTML
```

Nó không:

```text
parse
save
email
```

---

# 7. `StoryParser`

```python
from bs4 import BeautifulSoup


class StoryParser:

    def parse(self, html: str) -> Story:
        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1").get_text(strip=True)
        content = soup.select_one(".content").get_text(
            "\n",
            strip=True,
        )

        return Story(
            title=title,
            content=content,
        )
```

Responsibility:

```text
HTML → Story
```

Đây là một boundary rất đẹp:

```text
HTML
 ↓
StoryParser
 ↓
Story
```

---

# 8. `StoryRepository`

Không để domain/use case biết SQLite.

```python
import sqlite3


class StoryRepository:

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def save(self, story: Story) -> None:
        self.connection.execute(
            """
            INSERT INTO stories(title, content)
            VALUES (?, ?)
            """,
            (story.title, story.content),
        )

        self.connection.commit()
```

Responsibility:

```text
Story → Database
```

---

# 9. `NotificationService`

```python
class NotificationService:

    def send(self, message: str) -> None:
        send_email(message)
```

Responsibility:

```text
Notification
```

---

# 10. Bây giờ cần một orchestrator

Ta không muốn:

```text
Fetcher
    tự gọi Parser
Parser
    tự gọi Repository
Repository
    tự gọi Email
```

Thay vào đó có một application service/use case:

```python
class CrawlStoryUseCase:

    def __init__(
        self,
        fetcher,
        parser,
        repository,
        notifier,
    ):
        self.fetcher = fetcher
        self.parser = parser
        self.repository = repository
        self.notifier = notifier

    def execute(self, url: str) -> Story:
        html = self.fetcher.fetch(url)

        story = self.parser.parse(html)

        self.repository.save(story)

        self.notifier.send(
            f"Crawled: {story.title}"
        )

        return story
```

Bây giờ flow rất rõ:

```text
URL
 ↓
Fetcher
 ↓
HTML
 ↓
Parser
 ↓
Story
 ↓
Repository
 ↓
Database

Story
 ↓
Notifier
 ↓
Email
```

---

# 11. Một điều rất quan trọng: SRP không cấm orchestration

Có người học SOLID rồi nghĩ:

> “Một class gọi 4 dependency → chắc chắn vi phạm SRP.”

Không đúng.

`CrawlStoryUseCase` có responsibility:

> **Điều phối use case “crawl một story”.**

Việc nó gọi:

```text
Fetcher
Parser
Repository
Notifier
```

không có nghĩa nó có 4 responsibility.

Nó có **một responsibility ở cấp application**:

```text
Execute Crawl Story use case
```

Đây là distinction cực kỳ quan trọng.

---

# 12. Responsibility phụ thuộc abstraction level

Ví dụ:

```python
class Order:
    def calculate_total(self):
        ...
```

Responsibility:

```text
Domain behavior
```

Trong khi:

```python
class CreateOrderUseCase:
    def execute(self):
        ...
```

Responsibility:

```text
Application workflow
```

Và:

```python
class SqliteOrderRepository:
    def save(self, order):
        ...
```

Responsibility:

```text
Persistence
```

Ba class đều có thể có method tên `save`, `calculate`, `execute`..., nhưng responsibility nằm ở **boundary**, không nằm ở tên method.

---

# 13. Refactoring từ God Service

Hãy nhìn code ban đầu:

```python
class StoryService:

    def crawl(self, url):
        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = soup.select_one("h1").text
        content = soup.select_one(".content").text

        connection = sqlite3.connect("stories.db")

        connection.execute(
            "INSERT INTO stories(title, content) VALUES (?, ?)",
            (title, content),
        )

        connection.commit()

        send_email(f"Crawled: {title}")
```

Ta refactor theo từng bước.

---

## Step 1 — Extract fetching

```text
StoryService
    ↓
StoryFetcher
```

---

## Step 2 — Extract parsing

```text
StoryService
    ↓
StoryFetcher
StoryParser
```

---

## Step 3 — Extract persistence

```text
StoryService
    ↓
StoryFetcher
StoryParser
StoryRepository
```

---

## Step 4 — Extract notification

```text
StoryService
    ↓
StoryFetcher
StoryParser
StoryRepository
NotificationService
```

---

## Step 5 — Rename orchestration

`StoryService` trở thành:

```text
CrawlStoryUseCase
```

vì nó thực hiện một **use case**, không phải một “service” mơ hồ.

---

# 14. Tại sao `Service` là một cái tên nguy hiểm?

Ví dụ:

```text
UserService
StoryService
OrderService
FileService
DataService
AppService
```

Không có gì sai với chữ `Service`.

Nhưng nó thường che giấu câu hỏi:

> Service này chịu trách nhiệm chính xác về cái gì?

Ví dụ:

```python
class StoryService:
    ...
```

khó biết.

Trong khi:

```python
class CrawlStoryUseCase:
    ...
```

rõ hơn rất nhiều.

Hoặc:

```python
class StoryRepository:
    ...
```

rõ responsibility.

Hoặc:

```python
class StoryParser:
    ...
```

rõ responsibility.

**Tên tốt thường phản ánh boundary tốt.**

---

# 15. SRP và Composition

Sau refactoring:

```python
use_case = CrawlStoryUseCase(
    fetcher=StoryFetcher(),
    parser=StoryParser(),
    repository=repository,
    notifier=NotificationService(),
)
```

Ta đang dùng **composition**.

Thay vì:

```text
StoryService
    ↓
tự tạo mọi thứ
```

ta có:

```text
Application
    ↓
compose objects
```

Đây là bước chuẩn bị cho **DIP** mà chúng ta sẽ học sau.

---

# 16. Nhưng SRP chưa giải quyết hết vấn đề

Hiện tại:

```python
class CrawlStoryUseCase:

    def __init__(
        self,
        fetcher,
        parser,
        repository,
        notifier,
    ):
        ...
```

đã tốt hơn.

Nhưng:

```python
StoryFetcher
```

vẫn phụ thuộc:

```python
requests
```

và:

```python
StoryRepository
```

vẫn phụ thuộc:

```python
sqlite3
```

Điều đó **không nhất thiết vi phạm SRP**.

Đây là một distinction rất quan trọng.

Ta có thể có:

```text
SRP tốt
+
DIP chưa tốt
```

SOLID không phải:

```text
Nếu class tốt
→ tất cả SOLID đều được áp dụng
```

Mỗi principle giải quyết một dimension khác nhau.

---

# 17. SRP và DIP phối hợp như thế nào?

Hiện tại:

```text
CrawlStoryUseCase
       ↓
StoryRepository
       ↓
SQLite
```

Sau khi học DIP:

```text
CrawlStoryUseCase
       ↓
StoryRepository interface
       ↑
       │
SQLiteStoryRepository
```

Tương tự:

```text
CrawlStoryUseCase
       ↓
StoryFetcher interface
       ↑
       │
RequestsStoryFetcher
```

Đây là bước từ:

```text
SRP
```

sang:

```text
DIP
```

---

# 18. Một sai lầm rất phổ biến: “SRP = nhiều class hơn”

Không.

Mục tiêu không phải:

```text
1 class
 ↓
10 classes
```

Mục tiêu là:

```text
Low cohesion
     ↓
identify boundaries
     ↓
High cohesion
```

Ví dụ ban đầu:

```text
StoryService
 ├── HTTP
 ├── Parsing
 ├── DB
 └── Email
```

Sau:

```text
StoryFetcher
StoryParser
StoryRepository
NotificationService
```

Số class tăng.

Nhưng điều quan trọng là:

```text
coupling giảm
cohesion tăng
reason to change rõ hơn
testability tăng
```

---

# 19. Một ví dụ về over-engineering

Không nên làm:

```text
StoryTitleExtractor
StoryContentExtractor
StoryUrlExtractor
StoryMetadataExtractor
StoryDatabaseSaver
StoryDatabaseConnectionManager
StoryNotificationFormatter
StoryNotificationSender
```

cho một parser 30 dòng.

Nếu website đơn giản:

```python
class StoryParser:
    def parse(self, html):
        ...
```

hoàn toàn hợp lý.

**SRP không yêu cầu abstraction tối đa.**

---

# 20. Quy tắc thực chiến

Khi refactor một class lớn, hãy đi theo thứ tự:

```text
Step 1
↓
Đọc toàn bộ class

Step 2
↓
Nhóm behavior theo cohesion

Step 3
↓
Tìm actor

Step 4
↓
Tìm reason to change

Step 5
↓
Xác định boundary

Step 6
↓
Extract component

Step 7
↓
Kiểm tra coupling

Step 8
↓
Kiểm tra testability

Step 9
↓
Chỉ tạo abstraction khi cần
```

---

# 21. SRP và Testing

Đây là một lợi ích cực lớn.

Class ban đầu:

```python
class StoryService:

    def crawl(self, url):
        requests.get(...)
        sqlite3.connect(...)
        send_email(...)
```

Muốn test parsing:

```text
phải mock HTTP
phải mock database
phải mock email
```

Rất khó.

Sau refactoring:

```python
class StoryParser:

    def parse(self, html):
        ...
```

Test cực đơn giản:

```python
def test_parse_story():
    html = """
    <h1>Hello</h1>
    <div class="content">
        World
    </div>
    """

    parser = StoryParser()

    story = parser.parse(html)

    assert story.title == "Hello"
    assert story.content == "World"
```

Không cần:

```text
HTTP
SQLite
Email
Internet
```

Đây chính là:

> **SRP → better testability**

---

# 22. SRP và Mock

Use case:

```python
class CrawlStoryUseCase:

    def __init__(
        self,
        fetcher,
        parser,
        repository,
        notifier,
    ):
        ...
```

Ta có thể test bằng fake:

```python
class FakeFetcher:

    def fetch(self, url):
        return "<h1>Hello</h1>"
```

```python
class FakeRepository:

    def __init__(self):
        self.saved = []

    def save(self, story):
        self.saved.append(story)
```

Không cần SQLite thật.

Đây chính là nền tảng để sau này học:

```text
Dependency Injection
DIP
Ports & Adapters
Clean Architecture
```

---

# 23. SRP trong architecture lớn

Với project crawler của bạn, ta có thể bắt đầu suy nghĩ:

```text
src/
│
├── domain/
│   └── story.py
│
├── application/
│   └── crawl_story.py
│
├── infrastructure/
│   ├── http/
│   ├── parser/
│   ├── sqlite/
│   └── notification/
│
└── presentation/
    └── cli/
```

Điều này chưa phải toàn bộ Clean Architecture.

Nhưng nó cho thấy một tư duy:

```text
Business responsibility
        ≠
Infrastructure responsibility
        ≠
Application orchestration
        ≠
Presentation
```

---

# 24. Một mental model cực kỳ quan trọng

Hãy nhớ 4 tầng responsibility:

```text
┌─────────────────────────┐
│ Presentation             │
│ CLI / GUI / API          │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Application              │
│ Use Cases                │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Domain                   │
│ Business Rules            │
└─────────────────────────┘

        ↑
        │
┌───────┴─────────────────┐
│ Infrastructure            │
│ SQLite / HTTP / Email    │
└─────────────────────────┘
```

SRP giúp ta nhận ra:

> **Các loại responsibility khác nhau nên có boundary rõ ràng.**

---

# 25. Bài tập thực chiến

Hãy refactor class này:

```python
class StoryManager:

    def crawl(self, url):
        response = requests.get(url)

        if response.status_code != 200:
            raise RuntimeError("Request failed")

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = soup.select_one("h1").get_text(
            strip=True
        )

        content = soup.select_one(
            ".content"
        ).get_text(
            "\n",
            strip=True,
        )

        if not title:
            raise ValueError("Missing title")

        if not content:
            raise ValueError("Missing content")

        connection = sqlite3.connect(
            "stories.db"
        )

        connection.execute(
            """
            INSERT INTO stories(title, content)
            VALUES (?, ?)
            """,
            (title, content),
        )

        connection.commit()

        with open("crawler.log", "a") as f:
            f.write(
                f"Crawled: {url}\n"
            )

        send_email(
            subject="Crawler",
            body=f"Story {title} crawled",
        )

        return {
            "title": title,
            "content": content,
        }
```

Hãy thử thiết kế thành:

```text
domain/
    Story

application/
    CrawlStoryUseCase

infrastructure/
    HttpStoryFetcher
    BeautifulSoupStoryParser
    SqliteStoryRepository
    FileLogger
    EmailNotifier
```

Chưa cần viết code hoàn chỉnh.

Trước tiên hãy vẽ dependency:

```text
???
```

và xác định:

```text
Actor
Responsibility
Reason to change
Boundary
```

---

# 26. Thử thách nâng cao

Có một câu hỏi khó hơn:

Giả sử:

```python
class StoryParser:

    def parse(self, html):
        ...
```

Parser có 300 dòng vì website rất phức tạp.

Bạn có nên tách thành:

```text
TitleParser
ContentParser
AuthorParser
ChapterParser
ImageParser
MetadataParser
```

không?

**Không nhất thiết.**

Hãy xem chúng có cùng reason to change hay không.

Nếu tất cả đều thay đổi khi:

```text
website HTML structure thay đổi
```

thì chúng có thể vẫn thuộc cùng một responsibility:

```text
Story parsing
```

Do đó:

> **300 dòng không tự động có nghĩa là vi phạm SRP.**

Đây là một insight rất quan trọng.

---

# 27. Bài học sâu nhất của Buổi 3

Đừng hỏi:

> “Class này có bao nhiêu method?”

Hãy hỏi:

> **“Nếu một requirement thay đổi, tại sao class này phải thay đổi?”**

Nếu câu trả lời là:

```text
Database thay đổi
→ class phải sửa

Email provider thay đổi
→ class phải sửa

HTML structure thay đổi
→ class phải sửa

Business rule thay đổi
→ class phải sửa
```

thì bạn đang nhìn thấy nhiều **reason to change**.

Khi đó mới bắt đầu refactoring.

---

## Tóm tắt Buổi 3

```text
SRP
│
├── Responsibility
│
├── Actor
│
├── Reason to Change
│
├── Cohesion
│
├── Boundary
│
└── Refactoring
```

Mental model:

```text
                 CLASS
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
      Actor      Reason     Behavior
        │          │          │
        └──────────┼──────────┘
                   ↓
              Responsibility
                   ↓
                Boundary
```

Và một câu rất đáng nhớ:

> **SRP không nhằm tạo ra nhiều class hơn; SRP nhằm tạo ra những boundary có ý nghĩa.**

**Buổi 4** chúng ta sẽ chuyển sang **OCP — Open/Closed Principle**, bắt đầu từ một vấn đề cực phổ biến trong Python: `if/elif` ngày càng dài, rồi dùng **Strategy + Polymorphism + Registry** để mở rộng hệ thống mà không phải liên tục sửa code cũ.
