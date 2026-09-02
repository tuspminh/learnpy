# Python OOP Master — Buổi 27

# SOLID — Single Responsibility Principle (SRP)

Sau Buổi 24–26, chúng ta đã có:

```text
Composition
      ↓
Aggregation
      ↓
Dependency Injection
      ↓
Loose Coupling
```

Bây giờ bắt đầu **SOLID**.

SOLID là 5 nguyên tắc thiết kế giúp class/module:

* dễ hiểu
* dễ thay đổi
* dễ test
* ít phụ thuộc
* dễ mở rộng

Buổi này tập trung vào chữ đầu tiên:

> **S — Single Responsibility Principle**

---

# 1. SRP là gì?

SRP thường được diễn đạt:

> **Một class chỉ nên có một trách nhiệm và chỉ một lý do để thay đổi.**

Tiếng Anh:

> **A class should have one reason to change.**

Đừng hiểu đơn giản là:

> “Một class chỉ được có một method.”

Không phải.

Một class có thể có 10 method nhưng vẫn chỉ có **một responsibility**.

---

# 2. Ví dụ đơn giản

Giả sử:

```python
class User:
    def save_to_database(self):
        ...

    def send_email(self):
        ...

    def generate_report(self):
        ...
```

Class `User` đang làm quá nhiều việc:

```text
User
 ├── Business data
 ├── Database
 ├── Email
 └── Report
```

Có ít nhất 4 lý do để thay đổi:

```text
Database thay đổi
       ↓
User phải thay đổi

Email provider thay đổi
       ↓
User phải thay đổi

Report format thay đổi
       ↓
User phải thay đổi

Business rule thay đổi
       ↓
User phải thay đổi
```

Đây là vi phạm SRP.

---

# 3. “Một lý do để thay đổi” mới là điểm quan trọng

Ví dụ:

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def change_email(self, email):
        self.email = email

    def rename(self, name):
        self.name = name
```

Class này có nhiều method.

Nhưng các method đều liên quan tới:

```text
User state / User behavior
```

Nên vẫn có thể coi là một responsibility.

---

# 4. Responsibility nghĩa là gì?

**Responsibility** không đơn giản là “method”.

Nó là một nhóm công việc có cùng mục đích.

Ví dụ một `OrderService`:

```text
OrderService
 ├── create_order()
 ├── add_item()
 ├── remove_item()
 └── calculate_total()
```

Nếu tất cả đều liên quan đến **quản lý order**, có thể vẫn hợp lý.

Nhưng:

```text
OrderService
 ├── create_order()
 ├── save_to_sqlite()
 ├── send_email()
 ├── generate_pdf()
 ├── log_to_file()
 └── upload_to_s3()
```

thì bắt đầu có vấn đề.

---

# 5. Một class “God Object”

Một anti-pattern phổ biến là:

> **God Object**

Ví dụ:

```python
class Crawler:
    def crawl(self):
        ...

    def parse_html(self):
        ...

    def save_to_database(self):
        ...

    def send_email(self):
        ...

    def generate_report(self):
        ...

    def write_log(self):
        ...

    def retry_request(self):
        ...
```

Class này đang trở thành trung tâm của cả hệ thống.

```text
Crawler
 ├── HTTP
 ├── Parsing
 ├── Database
 ├── Email
 ├── Report
 ├── Logging
 └── Retry
```

Rất khó bảo trì.

---

# 6. Refactor theo SRP

Ta tách:

```text
Crawler
    ↓
HttpClient

Crawler
    ↓
Parser

Crawler
    ↓
Repository

Crawler
    ↓
Logger
```

Ví dụ:

```python
class HttpClient:
    def get(self, url):
        ...


class StoryParser:
    def parse(self, html):
        ...


class StoryRepository:
    def save(self, story):
        ...


class Logger:
    def info(self, message):
        ...
```

Crawler chỉ orchestration:

```python
class Crawler:

    def __init__(
        self,
        client,
        parser,
        repository,
        logger,
    ):
        self.client = client
        self.parser = parser
        self.repository = repository
        self.logger = logger
```

Đây chính là nơi **SRP + Dependency Injection** kết hợp.

---

# 7. SRP không có nghĩa “class càng nhỏ càng tốt”

Đây là một hiểu lầm nguy hiểm.

Không nên biến:

```python
class User:
    ...
```

thành:

```text
UserNameValidator
UserEmailValidator
UserAgeValidator
UserNameGetter
UserNameSetter
UserCreator
UserUpdater
...
```

chỉ để nói rằng:

> “Tôi đang dùng SRP.”

SRP không phải:

> **One class = one method**

Mà là:

> **Một abstraction nên có một responsibility rõ ràng.**

---

# 8. Ví dụ Order

Code ban đầu:

```python
class Order:

    def calculate_total(self):
        ...

    def save(self):
        ...

    def send_confirmation_email(self):
        ...

    def generate_invoice(self):
        ...
```

Có nhiều responsibility:

```text
Order
 ├── Business logic
 ├── Persistence
 ├── Notification
 └── Presentation
```

Refactor:

```text
Order
    ↓
OrderRepository

Order
    ↓
OrderNotification

Order
    ↓
InvoiceGenerator
```

---

# 9. Thiết kế tốt hơn

```python
class Order:

    def __init__(self, items):
        self.items = items

    def calculate_total(self):
        return sum(
            item.price
            for item in self.items
        )
```

Repository:

```python
class OrderRepository:

    def save(self, order):
        print("Saving order")
```

Notification:

```python
class OrderNotifier:

    def send_confirmation(self, order):
        print("Sending confirmation")
```

Invoice:

```python
class InvoiceGenerator:

    def generate(self, order):
        print("Generating invoice")
```

Bây giờ:

```text
Order
 └── Order business logic

OrderRepository
 └── Persistence

OrderNotifier
 └── Notification

InvoiceGenerator
 └── Invoice generation
```

Mỗi abstraction có responsibility rõ ràng.

---

# 10. “Reason to change” — ví dụ thực tế

Giả sử:

```python
class Invoice:
    ...
```

Invoice thay đổi khi:

```text
Business rule về Invoice thay đổi
```

Đó là một nhóm lý do.

Nhưng nếu `Invoice` đồng thời chứa:

```python
def save_to_database(self):
    ...

def send_email(self):
    ...

def export_pdf(self):
    ...
```

thì:

```text
Database thay đổi
       → Invoice thay đổi

Email provider thay đổi
       → Invoice thay đổi

PDF library thay đổi
       → Invoice thay đổi
```

Có quá nhiều reason to change.

---

# 11. SRP trong Crawler

Đây là ví dụ rất sát với project của bạn.

Một crawler thực tế có thể cần:

```text
HTTP request
HTML parsing
Data validation
Persistence
Retry
Logging
Scheduling
```

Không nên:

```python
class Crawler:

    def request(self):
        ...

    def parse(self):
        ...

    def validate(self):
        ...

    def save(self):
        ...

    def retry(self):
        ...

    def log(self):
        ...
```

Tất nhiên một class có thể điều phối chúng, nhưng implementation của từng responsibility nên được tách.

Ví dụ:

```text
Crawler
 │
 ├── HttpClient
 ├── Parser
 ├── Validator
 ├── Repository
 ├── RetryPolicy
 └── Logger
```

---

# 12. Crawler chỉ orchestration

Ví dụ:

```python
class Crawler:

    def __init__(
        self,
        client,
        parser,
        validator,
        repository,
        logger,
    ):
        self.client = client
        self.parser = parser
        self.validator = validator
        self.repository = repository
        self.logger = logger

    def crawl(self, url):
        self.logger.info(
            f"Crawling {url}"
        )

        response = self.client.get(url)

        data = self.parser.parse(
            response.text
        )

        if not self.validator.is_valid(data):
            return

        self.repository.save(data)
```

Crawler không cần biết:

```text
HTTP hoạt động thế nào
Parser hoạt động thế nào
SQLite hoạt động thế nào
Logging hoạt động thế nào
```

Nó chỉ **điều phối**.

---

# 13. SRP + DI

Đây là kiến trúc rất đẹp:

```text
                 Composition Root
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   HttpClient        Parser          Repository
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                     Crawler
```

Các dependency được inject:

```python
crawler = Crawler(
    client=HttpClient(),
    parser=StoryParser(),
    validator=StoryValidator(),
    repository=SQLiteStoryRepository(),
    logger=Logger(),
)
```

Crawler chỉ sử dụng chúng.

---

# 14. SRP và Testing

Thiết kế SRP giúp test từng phần.

Ví dụ test parser:

```python
parser = StoryParser()

story = parser.parse(html)

assert story.title == "Python"
```

Không cần:

```text
HTTP
SQLite
Crawler
```

Test repository:

```python
repository.save(story)
```

Test validator:

```python
assert validator.is_valid(story)
```

Test crawler:

```python
crawler = Crawler(
    client=FakeClient(),
    parser=FakeParser(),
    validator=FakeValidator(),
    repository=FakeRepository(),
    logger=FakeLogger(),
)
```

Đây chính là lợi ích của việc tách responsibility.

---

# 15. SRP và Module

SRP không chỉ áp dụng cho class.

Nó cũng áp dụng cho module/package.

Ví dụ không nên:

```text
utils.py
```

chứa:

```text
HTTP
SQLite
Parsing
Date
File
Email
Logging
Validation
```

Một file `utils.py` khổng lồ cũng là dấu hiệu thiết kế kém.

Có thể tách:

```text
utils/
    ├── text.py
    ├── date.py
    ├── file.py
    └── url.py
```

---

# 16. SRP và Package

Trong project crawler:

```text
src/
└── crawler/
    ├── domain/
    │   ├── story.py
    │   └── chapter.py
    │
    ├── application/
    │   └── crawl_story.py
    │
    ├── infrastructure/
    │   ├── http/
    │   ├── parser/
    │   ├── repository/
    │   └── logging/
    │
    └── cli/
        └── commands.py
```

Mỗi khu vực có responsibility tương đối rõ.

Đây là SRP ở cấp độ architecture.

---

# 17. Dấu hiệu class vi phạm SRP

Hãy cảnh giác khi một class có:

### 1. Quá nhiều dependency

```python
def __init__(
    self,
    db,
    logger,
    email,
    pdf,
    http,
    cache,
    parser,
):
```

Không phải lúc nào cũng sai, nhưng là dấu hiệu cần kiểm tra.

---

### 2. Nhiều loại công việc

```text
Database
Network
File
UI
Business Logic
Email
```

trong cùng một class.

---

### 3. Class thay đổi thường xuyên

Nếu Git history cho thấy:

```text
Monday → database change
Tuesday → email change
Wednesday → UI change
Thursday → business rule change
```

đều sửa cùng một class, đó là dấu hiệu mạnh của SRP violation.

---

### 4. Test class quá khó

Nếu test một class cần:

```text
Database
Network
Filesystem
Environment variables
External API
```

thì có thể class đang làm quá nhiều.

---

# 18. SRP không phải “tách mọi thứ”

Ví dụ:

```python
class ShoppingCart:

    def add_item(self, item):
        ...

    def remove_item(self, item):
        ...

    def total(self):
        ...
```

Hoàn toàn hợp lý.

Đừng tách thành:

```text
AddItemService
RemoveItemService
TotalService
```

chỉ vì mỗi method là một hành động.

Tất cả đều thuộc responsibility:

> **Quản lý trạng thái và hành vi của ShoppingCart.**

---

# 19. Một nguyên tắc thực tế

Khi gặp một class lớn, hãy hỏi:

> “Nếu requirement X thay đổi, class này có phải thay đổi không?”

Ví dụ:

```text
Database schema thay đổi?
Email provider thay đổi?
PDF library thay đổi?
Business rule thay đổi?
HTTP library thay đổi?
```

Nếu câu trả lời là **tất cả đều phải sửa class này**, class đó có khả năng vi phạm SRP.

---

# 20. Refactoring từng bước

Đừng refactor bằng cách viết lại toàn bộ.

Giả sử:

```python
class ReportService:

    def generate(self):
        data = self.load_data()
        data = self.process(data)
        self.save_pdf(data)
        self.send_email()
```

Bước 1:

```text
ReportService
    ↓
DataLoader
```

Bước 2:

```text
ReportService
    ↓
DataProcessor
```

Bước 3:

```text
ReportService
    ↓
PdfGenerator
```

Bước 4:

```text
ReportService
    ↓
EmailSender
```

Cuối cùng:

```python
class ReportService:

    def __init__(
        self,
        loader,
        processor,
        pdf_generator,
        email_sender,
    ):
        self.loader = loader
        self.processor = processor
        self.pdf_generator = pdf_generator
        self.email_sender = email_sender
```

Service chỉ điều phối workflow.

---

# 21. Một ví dụ hoàn chỉnh

## Trước SRP

```python
class StoryManager:

    def crawl(self, url):
        ...

    def parse(self, html):
        ...

    def save_to_sqlite(self, story):
        ...

    def send_notification(self, story):
        ...

    def export_markdown(self, story):
        ...
```

Có thể có:

```text
5 responsibilities
```

---

## Sau SRP

```text
StoryCrawler
    ↓
HttpClient

StoryParser
    ↓
HTML → Story

StoryRepository
    ↓
Story → SQLite

StoryNotifier
    ↓
Notification

MarkdownExporter
    ↓
Story → Markdown
```

Workflow:

```python
class StoryService:

    def __init__(
        self,
        crawler,
        parser,
        repository,
        notifier,
        exporter,
    ):
        self.crawler = crawler
        self.parser = parser
        self.repository = repository
        self.notifier = notifier
        self.exporter = exporter

    def process(self, url):
        html = self.crawler.fetch(url)

        story = self.parser.parse(html)

        self.repository.save(story)

        self.notifier.notify(story)

        self.exporter.export(story)
```

Đây là một thiết kế rất gần với hệ thống crawler/reading mà bạn đang xây.

---

# 22. SRP kết hợp với các bài trước

Chúng ta đã đi qua một chuỗi rất quan trọng:

```text
Buổi 24
Composition
      ↓
Buổi 25
Aggregation
      ↓
Buổi 26
Dependency Injection
      ↓
Buổi 27
Single Responsibility
```

Chúng không phải những kiến thức rời rạc.

Chúng kết hợp với nhau:

```text
SRP
 ↓
Tách responsibility
 ↓
Composition
 ↓
Inject dependency
 ↓
Loose coupling
 ↓
Testable
```

---

# 23. Một architecture mẫu

```text
                    Application
                         │
                         ▼
                  StoryService
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      Repository       Parser        Crawler
          │              │              │
          ▼              ▼              ▼
       SQLite        Selectolax       HTTPX
```

Mỗi thành phần có một responsibility chính.

Đây là tư duy bạn sẽ tiếp tục sử dụng khi học:

```text
OCP
LSP
ISP
DIP
```

---

# 24. Bài tập Buổi 27

## Bài 1 — Phát hiện SRP

Class sau có những responsibility nào?

```python
class UserManager:

    def create_user(self):
        ...

    def validate_email(self):
        ...

    def save_to_database(self):
        ...

    def send_welcome_email(self):
        ...

    def export_csv(self):
        ...

    def log(self):
        ...
```

Hãy xác định ít nhất **5 responsibility**.

---

## Bài 2 — Refactor

Refactor:

```python
class OrderManager:

    def create_order(self):
        ...

    def save_order(self):
        ...

    def send_email(self):
        ...

    def generate_pdf(self):
        ...
```

thành:

```text
Order
OrderRepository
OrderNotifier
InvoiceGenerator
OrderService
```

---

# 25. Bài tập nâng cao — Crawler

Hãy thiết kế:

```text
Crawler
 ├── HttpClient
 ├── Parser
 ├── Validator
 ├── Repository
 └── Logger
```

Yêu cầu:

### `HttpClient`

Chỉ phụ trách:

```text
HTTP request
```

### `Parser`

Chỉ phụ trách:

```text
HTML → Story
```

### `Validator`

Chỉ phụ trách:

```text
validate Story
```

### `Repository`

Chỉ phụ trách:

```text
Persistence
```

### `Logger`

Chỉ phụ trách:

```text
Logging
```

### `Crawler`

Chỉ phụ trách:

```text
orchestration
```

Dependency phải được inject:

```python
crawler = Crawler(
    client=client,
    parser=parser,
    validator=validator,
    repository=repository,
    logger=logger,
)
```

---

# 26. Tư duy quan trọng nhất hôm nay

Đừng nhìn SRP như một quy tắc:

```text
❌ Một class chỉ có một method
```

Hãy nhìn nó như:

```text
                 Class
                   │
                   ▼
             Responsibility
                   │
                   ▼
          Một nhóm hành vi liên quan
                   │
                   ▼
             Một reason to change
```

Ví dụ:

```text
Order
  ↓
Order business rules

Repository
  ↓
Persistence

Parser
  ↓
Parsing

Notifier
  ↓
Notification
```

---

# 27. Tóm tắt

**SRP — Single Responsibility Principle:**

> Một class/module nên có **một trách nhiệm rõ ràng** và **một lý do chính để thay đổi**.

### Dấu hiệu vi phạm:

```text
❌ Class quá lớn
❌ Nhiều loại dependency
❌ Database + HTTP + UI + Email cùng một class
❌ Khó test
❌ Thay đổi một thứ kéo theo sửa nhiều thứ
```

### Thiết kế tốt:

```text
SRP
 ↓
Small cohesive components
 ↓
Composition
 ↓
Dependency Injection
 ↓
Loose Coupling
 ↓
Easy Testing
```

**Buổi 28 — Open/Closed Principle (OCP)** sẽ giải quyết câu hỏi tiếp theo:

> **Sau khi đã tách class theo SRP, làm thế nào để thêm tính năng mới mà không phải sửa code cũ?**

Đặc biệt chúng ta sẽ dùng chính ví dụ **Parser Site A / Site B / Site C** của crawler để thấy OCP hoạt động như thế nào.
