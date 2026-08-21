# SOLID Deep Dive — Buổi 2

# Single Responsibility Principle — SRP

Hôm nay chúng ta đi sâu vào chữ **S** trong SOLID.

> **SRP — Single Responsibility Principle**

Đây là principle đầu tiên nhưng cũng là một trong những principle **dễ hiểu sai nhất**.

---

# 1. Định nghĩa kinh điển

Robert C. Martin thường diễn đạt SRP theo ý:

> **A class should have one reason to change.**

Dịch:

> **Một class nên có một lý do để thay đổi.**

Điểm quan trọng nhất ở đây là:

**Không phải:**

> Một class chỉ được có một method.

**Không phải:**

> Một class chỉ làm một việc nhỏ.

Mà là:

> **Một class nên phục vụ một nhóm trách nhiệm thuộc cùng một nguồn thay đổi.**

---

# 2. “Responsibility” thực sự là gì?

Đây là phần quan trọng nhất của buổi hôm nay.

Ví dụ:

```python
class User:
    def change_password(self):
        ...

    def change_email(self):
        ...

    def activate(self):
        ...
```

Có phải class này vi phạm SRP vì có 3 method?

**Không.**

Ba method đều liên quan đến:

```text
User
```

và có thể thuộc cùng một responsibility:

```text
Quản lý trạng thái và hành vi của User
```

Ngược lại:

```python
class User:
    def change_password(self):
        ...

    def save_to_database(self):
        ...

    def send_email(self):
        ...

    def generate_pdf(self):
        ...
```

Ở đây có nhiều responsibility:

```text
User domain behavior
        +
Persistence
        +
Notification
        +
Document generation
```

Đây mới là vấn đề.

---

# 3. Reason to Change

Hãy tập trung vào câu hỏi:

> **“Ai hoặc cái gì có thể khiến class này phải thay đổi?”**

Ví dụ:

```python
class UserService:

    def create_user(self):
        ...

    def save_to_database(self):
        ...

    def send_email(self):
        ...
```

Có thể có 3 nguồn thay đổi:

```text
Business rule
     ↓
create_user()

Database requirement
     ↓
save_to_database()

Email requirement
     ↓
send_email()
```

Ta có:

```text
UserService
 ├── Business rules
 ├── Database
 └── Email
```

Nếu ba phần này thay đổi độc lập, class có **nhiều reason to change**.

---

# 4. Ví dụ thực tế

Xét code:

```python
class OrderService:

    def create_order(self, items):
        total = sum(item.price for item in items)

        order = {
            "items": items,
            "total": total,
        }

        self.save_to_database(order)
        self.send_email(order)
        self.generate_invoice(order)

        return order

    def save_to_database(self, order):
        ...

    def send_email(self, order):
        ...

    def generate_invoice(self, order):
        ...
```

Nhìn qua rất tiện.

Một class làm toàn bộ workflow.

Nhưng hãy hỏi:

### Nếu database thay đổi?

```text
SQLite
→ PostgreSQL
```

`OrderService` thay đổi.

### Nếu email provider thay đổi?

```text
SMTP
→ SendGrid
```

`OrderService` thay đổi.

### Nếu invoice thay đổi?

```text
PDF
→ HTML
```

`OrderService` thay đổi.

### Nếu business rule tính giá thay đổi?

`OrderService` cũng thay đổi.

Như vậy:

```text
OrderService
       │
       ├── Business
       ├── Persistence
       ├── Notification
       └── Invoice
```

Đây là dấu hiệu SRP violation.

---

# 5. Refactoring theo SRP

Ta tách:

```text
OrderService
OrderRepository
EmailService
InvoiceGenerator
```

Ví dụ:

```python
class OrderService:

    def __init__(
        self,
        repository,
        email_service,
        invoice_generator,
    ):
        self.repository = repository
        self.email_service = email_service
        self.invoice_generator = invoice_generator

    def create_order(self, items):
        total = sum(item.price for item in items)

        order = {
            "items": items,
            "total": total,
        }

        self.repository.save(order)
        self.email_service.send(order)
        self.invoice_generator.generate(order)

        return order
```

Repository:

```python
class OrderRepository:

    def save(self, order):
        ...
```

Email:

```python
class EmailService:

    def send(self, order):
        ...
```

Invoice:

```python
class InvoiceGenerator:

    def generate(self, order):
        ...
```

Bây giờ:

```text
OrderService
    │
    ├── OrderRepository
    ├── EmailService
    └── InvoiceGenerator
```

Mỗi thành phần có một responsibility rõ hơn.

---

# 6. Nhưng có một vấn đề quan trọng

Đừng hiểu SRP thành:

> “Cứ thấy class dài là phải tách.”

Ví dụ:

```python
class Order:
    def add_item(self, item):
        ...

    def remove_item(self, item):
        ...

    def calculate_total(self):
        ...

    def is_empty(self):
        ...
```

Class này có 4 method.

Nhưng tất cả đều liên quan đến:

```text
Order domain behavior
```

Không cần tách thành:

```text
OrderItemAdder
OrderItemRemover
OrderCalculator
OrderValidator
```

Nếu làm như vậy, bạn đang **over-engineering**.

---

# 7. SRP không phải “One Method”

Một anti-pattern phổ biến:

```python
class UserCreator:
    def create(self):
        ...


class UserUpdater:
    def update(self):
        ...


class UserDeleter:
    def delete(self):
        ...
```

Có vẻ rất SOLID.

Nhưng nếu hệ thống đơn giản:

```text
UserService
 ├── create()
 ├── update()
 └── delete()
```

hoàn toàn có thể tốt hơn.

SRP không đo bằng:

```text
Số method
```

mà bằng:

```text
Mức độ liên quan giữa các behavior
+
Nguồn thay đổi
```

---

# 8. Cohesion và SRP

SRP liên quan rất mạnh đến **cohesion**.

Cohesion cao:

```python
class Order:
    def add_item(self):
        ...

    def remove_item(self):
        ...

    def calculate_total(self):
        ...
```

Các behavior cùng xoay quanh:

```text
Order
```

Cohesion thấp:

```python
class OrderService:
    def create_order(self):
        ...

    def send_email(self):
        ...

    def resize_image(self):
        ...

    def generate_pdf(self):
        ...

    def backup_database(self):
        ...
```

Các behavior không có mối quan hệ chặt chẽ.

---

# 9. Một kỹ thuật rất hữu ích: Actor

Một cách phân tích SRP tốt là hỏi:

> **Ai là người quan tâm đến behavior này?**

Ví dụ:

```python
class Employee:

    def calculate_salary(self):
        ...

    def save(self):
        ...

    def print_report(self):
        ...
```

Ba behavior có thể phục vụ ba actor:

```text
calculate_salary()
       ↓
Payroll department

save()
       ↓
Database / infrastructure

print_report()
       ↓
Reporting department
```

Do đó có thể tách:

```text
Employee
EmployeeRepository
EmployeeReport
PayrollService
```

---

# 10. SRP và Domain Model

Đây là chỗ rất quan trọng khi bạn học DDD.

Ví dụ:

```python
class Order:

    def add_item(self, item):
        ...

    def remove_item(self, item):
        ...

    def calculate_total(self):
        ...
```

Đây là **domain responsibility**.

Nhưng:

```python
class Order:

    def save_to_sqlite(self):
        ...
```

thì không còn là domain responsibility.

Database là infrastructure concern.

Do đó:

```text
Domain

Order
  ↓
business behavior
```

còn:

```text
Infrastructure

OrderRepository
  ↓
SQLite
```

Đây là một trong những lý do SRP thường xuất hiện cùng:

* DDD
* Clean Architecture
* Hexagonal Architecture

---

# 11. SRP trong Python

Python khiến việc áp dụng SRP khá thú vị vì Python không bắt bạn phải sử dụng class.

Ví dụ hoàn toàn có thể dùng function:

```python
def calculate_total(items):
    return sum(item.price for item in items)
```

và:

```python
def save_order(order, repository):
    repository.save(order)
```

SRP **không phải nguyên tắc dành riêng cho class**.

Nó có thể áp dụng ở nhiều cấp độ:

```text
Function
   ↓
Class
   ↓
Module
   ↓
Package
   ↓
Application
```

---

# 12. SRP ở cấp module

Ví dụ file:

```text
order.py
```

chứa:

```python
class Order:
    ...


class OrderRepository:
    ...


class EmailService:
    ...


class PDFGenerator:
    ...


def send_email():
    ...


def connect_database():
    ...
```

Mặc dù mỗi class riêng lẻ có thể tương đối ổn, module vẫn có thể có cohesion thấp.

Có thể tổ chức:

```text
orders/
    domain.py
    repository.py
    email.py
    invoice.py
```

Hoặc trong architecture lớn hơn:

```text
orders/
    domain/
    application/
    infrastructure/
```

---

# 13. SRP ở cấp package

Ví dụ:

```text
app/
    user/
    order/
    crawler/
    database/
    email/
```

Mỗi package có boundary riêng.

SRP lúc này không chỉ là:

```text
Class → một responsibility
```

mà là:

```text
Package → một nhóm responsibility có cohesion cao
```

Đây là cách tư duy rất quan trọng khi thiết kế hệ thống lớn.

---

# 14. SRP và “Manager” class

Một code smell rất phổ biến trong Python:

```python
class ApplicationManager:
    ...
```

Sau một thời gian:

```python
class ApplicationManager:

    def create_user(self):
        ...

    def delete_user(self):
        ...

    def crawl_story(self):
        ...

    def download_image(self):
        ...

    def convert_audio(self):
        ...

    def backup_database(self):
        ...

    def send_notification(self):
        ...
```

Đây là **God Object**.

Tên như:

```text
Manager
Service
Helper
Utility
Handler
Processor
Controller
```

không tự động là xấu.

Nhưng chúng thường là nơi responsibility bị dồn vào.

---

# 15. Một heuristic rất mạnh

Khi nhìn một class, hãy hỏi:

```text
Nếu requirement A thay đổi
→ class này có phải sửa?

Nếu requirement B thay đổi
→ class này có phải sửa?

Nếu requirement C thay đổi
→ class này có phải sửa?
```

Nếu:

```text
A → sửa
B → sửa
C → sửa
```

và A/B/C là các concern độc lập:

**SRP violation rất có khả năng xảy ra.**

---

# 16. SRP không có nghĩa là tách tất cả

Đây là điểm tôi muốn bạn đặc biệt nhớ.

### Sai:

```text
Một class có 10 method
        ↓
SRP violation
        ↓
tách thành 10 class
```

### Đúng:

```text
Class có nhiều behavior
        ↓
Phân tích cohesion
        ↓
Tìm reason to change
        ↓
Xác định boundary
        ↓
Chỉ tách khi có lý do
```

---

# 17. Một ví dụ khó hơn

Giả sử:

```python
class StoryCrawler:

    def crawl(self, url):
        html = requests.get(url).text

        soup = BeautifulSoup(html, "html.parser")

        title = soup.select_one("h1").text

        connection = sqlite3.connect("story.db")

        connection.execute(
            "INSERT INTO stories(title) VALUES (?)",
            (title,)
        )

        connection.commit()

        send_notification(
            f"Crawled: {title}"
        )
```

Có rất nhiều concern:

```text
HTTP
HTML parsing
Domain extraction
Database
Notification
```

Nếu tất cả nằm trong `StoryCrawler`, việc thay đổi một concern sẽ ảnh hưởng crawler.

Một thiết kế tốt hơn:

```text
Crawler
   ↓
Fetcher
   ↓
Parser
   ↓
Story
   ↓
Repository
   ↓
Notification
```

Ví dụ:

```python
class StoryFetcher:
    def fetch(self, url):
        ...


class StoryParser:
    def parse(self, html):
        ...


class StoryRepository:
    def save(self, story):
        ...


class NotificationService:
    def notify(self, message):
        ...
```

Sau đó orchestration:

```python
class StoryCrawler:

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

    def crawl(self, url):
        html = self.fetcher.fetch(url)
        story = self.parser.parse(html)

        self.repository.save(story)

        self.notifier.notify(
            f"Crawled: {story.title}"
        )

        return story
```

Đây là bước đầu tiên tiến tới:

```text
SRP
 ↓
DIP
 ↓
Clean Architecture
```

Nhưng **đừng vội kết luận rằng class trên hoàn hảo**. Buổi sau chúng ta sẽ phân tích sâu hơn về boundary.

---

# 18. SRP và Use Case

Một điều rất quan trọng khi kết hợp với Clean Architecture:

`StoryCrawler` ở trên có thể vẫn đang làm quá nhiều.

Ta có thể chuyển orchestration thành:

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

    def execute(self, url):
        ...
```

Trong khi:

```text
Fetcher
Parser
Repository
Notifier
```

là các dependency.

Lúc này architecture bắt đầu có hình dạng:

```text
             CLI
              ↓
      CrawlStoryUseCase
        ↓    ↓    ↓
   Fetcher Parser Repository
```

Đây sẽ là cầu nối giữa:

```text
SOLID
   ↓
DDD
   ↓
Clean Architecture
```

---

# 19. Checklist phân tích SRP

Khi gặp một class lớn, hãy tự hỏi:

```text
1. Class này làm những việc gì?

2. Những việc đó có cùng mục đích không?

3. Những behavior đó có cùng actor không?

4. Những behavior đó có cùng reason to change không?

5. Database thay đổi thì class có thay đổi không?

6. UI thay đổi thì class có thay đổi không?

7. Business rule thay đổi thì class có thay đổi không?

8. External service thay đổi thì class có thay đổi không?

9. Tôi có thể mô tả responsibility của class bằng một câu rõ ràng không?

10. Nếu tách class, coupling có giảm không?
```

Câu cuối cùng cực kỳ quan trọng.

---

# 20. Bài tập Buổi 2

Hãy phân tích class này:

```python
class StoryService:

    def crawl(self, url):
        response = requests.get(url)

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = soup.select_one("h1").text
        content = soup.select_one(".content").text

        connection = sqlite3.connect("stories.db")

        connection.execute(
            """
            INSERT INTO stories(title, content)
            VALUES (?, ?)
            """,
            (title, content)
        )

        connection.commit()

        with open("crawl.log", "a") as f:
            f.write(f"Crawled: {title}\n")

        send_email(
            f"Story crawled: {title}"
        )

        return {
            "title": title,
            "content": content,
        }
```

### Yêu cầu 1

Liệt kê **tất cả responsibility** bạn phát hiện.

### Yêu cầu 2

Xác định **reason to change** của từng responsibility.

### Yêu cầu 3

Xác định actor của từng responsibility.

### Yêu cầu 4

Thiết kế lại thành các component phù hợp.

Gợi ý:

```text
StoryService
    ↓
???
```

### Yêu cầu 5 — nâng cao

Không chỉ tách class.

Hãy suy nghĩ:

```text
Domain
Application
Infrastructure
```

nên chứa gì?

---

## Kiến thức cần chốt sau Buổi 2

Nếu chỉ nhớ **5 câu**, hãy nhớ:

```text
1. SRP ≠ một class chỉ có một method.

2. SRP = một responsibility / một nhóm reason to change.

3. Responsibility phải được xác định dựa trên behavior và actor.

4. SRP nhằm tăng cohesion và giảm coupling.

5. Không được tách class chỉ vì muốn “trông SOLID”.
```

**Buổi 3** chúng ta sẽ đi vào **SRP Deep Dive + Refactoring thực chiến**: từ một `God Service` khoảng 100 dòng, phân tích **actor → responsibility → reason to change → boundary**, sau đó refactor thành architecture có `Domain / Application / Infrastructure`.
