# DDD Deep Dive — Buổi 4

## Domain Model — Từ ngôn ngữ nghiệp vụ đến mô hình có hành vi

Ở 3 buổi trước, chúng ta đã đi theo chuỗi:

```text
Buổi 1
Domain
   ↓
Business Problem

Buổi 2
Domain Discovery
   ↓
Subdomain

Buổi 3
Ubiquitous Language
   ↓
Business Vocabulary
```

Hôm nay chúng ta bước sang một tầng rất quan trọng:

```text
Ubiquitous Language
        ↓
Domain Model
```

Mục tiêu của Buổi 4 là hiểu sâu:

* Domain Model là gì?
* Model khác database model thế nào?
* Data Model vs Domain Model
* Anemic Domain Model
* Rich Domain Model
* Behavior vs State
* Business Rule
* Invariant
* Encapsulation
* Domain object phải bảo vệ chính nó như thế nào?

---

# 1. Domain Model là gì?

Một định nghĩa thực dụng:

> **Domain Model là mô hình phần mềm biểu diễn các khái niệm, quan hệ, trạng thái và hành vi quan trọng của business.**

Ví dụ domain:

> Hệ thống quản lý và crawl truyện.

Ta có:

```text
Story
Chapter
Source
CrawlerJob
ReadingProgress
```

Nhưng chỉ liệt kê các object chưa đủ.

Ta cần biết:

```text
Story làm gì?
Chapter có rule gì?
CrawlerJob có state gì?
ReadingProgress thay đổi như thế nào?
```

Đó mới là Domain Model.

---

# 2. Domain Model không phải Class Diagram

Đây là một điểm cần phân biệt.

Bạn có thể vẽ:

```text
Story
 ├── id
 ├── title
 └── chapters
```

Đây mới chỉ là **structural model**.

Domain Model phải chứa cả:

```text
State
+
Behavior
+
Rules
+
Relationships
```

Ví dụ:

```text
Story
 ├── title
 ├── status
 ├── add_chapter()
 ├── publish()
 ├── archive()
 └── business rules
```

---

# 3. Model không chỉ là dữ liệu

Một developer mới thường suy nghĩ:

```python
class Story:
    id: int
    title: str
```

Họ coi `Story` là:

> một object chứa dữ liệu.

DDD hỏi câu khác:

> Story có thể làm gì?

Ví dụ:

```python
story.publish()
story.archive()
story.add_chapter(chapter)
```

Đây là chuyển đổi từ:

```text
Data
```

sang:

```text
Data + Behavior
```

---

# 4. State và Behavior

Một Domain Object thường có:

```text
State
+
Behavior
```

Ví dụ:

```python
class CrawlerJob:
    status = RUNNING
```

`status` là state.

Nhưng:

```python
job.pause()
```

là behavior.

Sau khi gọi:

```python
job.pause()
```

state thay đổi:

```text
RUNNING
   ↓
PAUSED
```

Đây chính là domain behavior.

---

# 5. Tại sao behavior quan trọng?

Giả sử chúng ta cho phép:

```python
job.status = CrawlerStatus.PAUSED
```

Bất kỳ code nào cũng có thể làm:

```python
job.status = CrawlerStatus.COMPLETED
job.status = CrawlerStatus.RUNNING
job.status = CrawlerStatus.PAUSED
```

Không có business control.

Trong khi business có rule:

```text
RUNNING → PAUSED
```

nhưng:

```text
COMPLETED → PAUSED
```

không hợp lệ.

Vậy object phải kiểm soát state transition.

---

# 6. Rich Domain Model

Ta muốn:

```python
job.pause()
```

thay vì:

```python
job.status = PAUSED
```

Vì `pause()` thể hiện **ý định nghiệp vụ**.

Ví dụ:

```python
class CrawlerJob:

    def pause(self):
        if self.status != CrawlerStatus.RUNNING:
            raise CrawlerCannotBePaused()

        self.status = CrawlerStatus.PAUSED
```

Bây giờ `CrawlerJob` biết:

> Khi nào tôi được phép pause?

Đó là **Rich Domain Model**.

---

# 7. Anemic Domain Model

Ngược lại:

```python
class CrawlerJob:
    id: int
    status: CrawlerStatus
```

Business logic nằm bên ngoài:

```python
class CrawlerService:

    def pause(self, job):
        if job.status != CrawlerStatus.RUNNING:
            raise ...

        job.status = CrawlerStatus.PAUSED
```

Đây là:

> **Anemic Domain Model**

Object chỉ giữ data.

Service làm gần như toàn bộ business logic.

---

# 8. Tại sao Anemic Model nguy hiểm?

Ban đầu:

```text
CrawlerService
```

chỉ có vài method.

Sau này:

```text
CrawlerService
 ├── start()
 ├── pause()
 ├── resume()
 ├── retry()
 ├── complete()
 ├── fail()
 ├── cancel()
 ├── validate()
 └── ...
```

Nó dần trở thành:

> **God Service**

Trong khi `CrawlerJob` lại rất "ngu":

```text
CrawlerJob
 ├── id
 ├── status
 ├── created_at
 └── ...
```

Business logic nằm sai chỗ.

---

# 9. Rich Domain Model giải quyết thế nào?

Ta đưa behavior về object có trách nhiệm đó.

```python
class CrawlerJob:

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

Application Service chỉ điều phối:

```python
def pause_crawler(job_id):
    job = repository.get(job_id)

    job.pause()

    repository.save(job)
```

Application Service không cần biết chi tiết:

> `RUNNING` có được pause hay không.

`CrawlerJob` biết.

---

# 10. Đây chính là Encapsulation

Encapsulation không chỉ là:

> biến thành private.

Trong DDD, encapsulation có ý nghĩa sâu hơn:

> **Object kiểm soát cách state của nó được thay đổi.**

Không muốn:

```python
job.status = PAUSED
```

thì không expose state mutation tùy tiện.

Thay vào đó:

```python
job.pause()
```

Object tự bảo vệ invariant.

---

# 11. Invariant là gì?

**Invariant** là điều kiện phải luôn đúng đối với một domain object hoặc aggregate.

Ví dụ:

```text
Chapter number > 0
```

là invariant.

```text
Một Story không có hai Chapter cùng number
```

cũng là invariant.

Crawler:

```text
Completed job không thể trở lại Running
```

là invariant.

---

# 12. Invariant cực kỳ quan trọng

Hãy xem:

```python
job.status = CrawlerStatus.COMPLETED
job.status = CrawlerStatus.RUNNING
```

Nếu code cho phép, object có thể rơi vào trạng thái business-invalid.

DDD muốn:

> **Invalid state không nên tồn tại.**

Hay nói cách khác:

```text
Domain Object
     ↓
Protect Invariant
     ↓
Prevent Invalid State
```

---

# 13. Ví dụ `Chapter`

Ta có requirement:

> Chapter number phải lớn hơn 0.

Không nên:

```python
chapter = Chapter(
    number=-100,
    title="ABC",
)
```

Sau đó mới:

```python
if chapter.number <= 0:
    ...
```

Khắp hệ thống.

Ta muốn:

```python
class Chapter:

    def __init__(self, number: int, title: str):
        if number <= 0:
            raise InvalidChapterNumber()

        self.number = number
        self.title = title
```

Ngay khi tạo object:

```text
Invalid
   ↓
Rejected
```

---

# 14. "Make Invalid State Unrepresentable"

Đây là một tư tưởng rất mạnh trong thiết kế domain.

Thay vì:

```text
Object có thể invalid
        ↓
Mọi nơi phải kiểm tra
```

ta muốn:

```text
Object được tạo
        ↓
Invariant được kiểm tra
        ↓
Object hợp lệ
```

Ví dụ:

```python
Chapter(-1, "Hello")
```

không thể tạo thành một Chapter hợp lệ.

---

# 15. Business Rule vs Invariant

Hai khái niệm gần nhau nhưng không hoàn toàn giống nhau.

### Invariant

Một điều kiện phải luôn đúng.

Ví dụ:

```text
Chapter.number > 0
```

### Business Rule

Một quy tắc nghiệp vụ rộng hơn.

Ví dụ:

> Story đã archived thì không được thêm chapter mới.

Có thể biểu diễn:

```python
if self.status == StoryStatus.ARCHIVED:
    raise StoryArchivedError()
```

---

# 16. Business Rule nên nằm ở đâu?

Đây là câu hỏi trung tâm của DDD.

Không có câu trả lời:

> "Luôn luôn nằm trong Entity."

Mà phải hỏi:

> **Object nào có đủ thông tin và trách nhiệm để bảo vệ rule này?**

Ví dụ:

```text
Story archived
+
Add chapter
```

Rule thuộc về `Story`:

```python
story.add_chapter(chapter)
```

vì Story biết:

```text
status
chapters
```

---

# 17. Ví dụ rule sai chỗ

Giả sử:

```python
class StoryService:

    def add_chapter(self, story, chapter):
        if story.status == "archived":
            raise ...

        if chapter.number in story.chapters:
            raise ...

        story.chapters.append(chapter)
```

Service đang biết quá nhiều về nội bộ `Story`.

Tốt hơn:

```python
story.add_chapter(chapter)
```

và:

```python
class Story:

    def add_chapter(self, chapter):
        ...
```

---

# 18. Nhưng không phải mọi logic đều thuộc Entity

Đây là điểm cần đặc biệt nhớ.

Ví dụ:

> Tính phí vận chuyển dựa trên khoảng cách, trọng lượng và chính sách vận chuyển.

Không nhất thiết thuộc:

```text
Order
```

hay:

```text
Product
```

Có thể cần:

```text
ShippingCostCalculator
```

Đây sẽ dẫn chúng ta đến **Domain Service** ở các buổi sau.

---

# 19. Domain Model phải thể hiện Intent

So sánh:

```python
order.status = "cancelled"
```

với:

```python
order.cancel()
```

Cái thứ hai nói rõ:

> Tôi muốn hủy Order.

Đây gọi là:

> **Intention-revealing interface**

Interface của domain nên diễn đạt **ý định nghiệp vụ**.

---

# 20. Một ví dụ tốt hơn

Không:

```python
story.status = "published"
```

Mà:

```python
story.publish()
```

Không:

```python
crawler.status = "paused"
```

Mà:

```python
crawler.pause()
```

Không:

```python
progress.position = 100
```

Mà:

```python
progress.move_to(100)
```

Không:

```python
chapter.read = True
```

Mà:

```python
progress.mark_as_read()
```

---

# 21. Domain Model kể được câu chuyện

Một đoạn code tốt:

```python
job.start()

chapter = job.discover_chapter()

story.add_chapter(chapter)

job.complete()
```

Có thể đọc gần giống business language:

> Job bắt đầu → phát hiện chapter → thêm chapter vào story → hoàn thành.

Đây là một Domain Model tốt hơn:

```python
repository.update_status(...)
repository.insert(...)
repository.update(...)
```

vì code không còn thể hiện business intent.

---

# 22. Domain Model và database model

Đây là chỗ developer thường nhầm nhất.

Database:

```text
crawler_jobs
-------------------------
id
status
created_at
updated_at
```

Domain:

```python
class CrawlerJob:

    def start(self):
        ...

    def pause(self):
        ...

    def resume(self):
        ...

    def complete(self):
        ...
```

Database chỉ lưu state.

Domain định nghĩa:

> State nào hợp lệ và state thay đổi thế nào.

---

# 23. Domain Model không cần biết persistence

Domain không nên:

```python
class Story:

    def save(self):
        connection.execute(...)
```

Vì:

```text
Story
```

không phải database adapter.

Domain chỉ quan tâm:

```python
story.add_chapter(chapter)
```

Sau đó Application/Infrastructure xử lý persistence.

---

# 24. Một Domain Model đơn giản

Ta bắt đầu xây:

```python
from enum import Enum


class StoryStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
```

Entity:

```python
class Story:

    def __init__(self, title: str):
        if not title.strip():
            raise ValueError("Title cannot be empty")

        self.title = title
        self.status = StoryStatus.DRAFT
        self._chapters = []
```

Behavior:

```python
def publish(self):
    if not self._chapters:
        raise ValueError(
            "Story must have at least one chapter"
        )

    self.status = StoryStatus.PUBLISHED
```

---

# 25. Encapsulation collection

Không nên:

```python
story.chapters.append(chapter)
```

Nếu public:

```python
self.chapters = []
```

thì bất kỳ code nào cũng có thể phá invariant.

Thay vào đó:

```python
self._chapters = []
```

và:

```python
def add_chapter(self, chapter):
    ...
```

---

# 26. Không nên trả list mutable trực tiếp

Ví dụ:

```python
@property
def chapters(self):
    return self._chapters
```

Code bên ngoài có thể:

```python
story.chapters.clear()
```

Invariant bị phá.

Tốt hơn:

```python
@property
def chapters(self):
    return tuple(self._chapters)
```

Hoặc trả một immutable view tùy nhu cầu.

---

# 27. Domain Model và mutation

Một nguyên tắc tốt:

> **State mutation nên đi qua behavior có ý nghĩa nghiệp vụ.**

Không:

```python
story.status = ...
story.chapters.append(...)
```

Mà:

```python
story.publish()
story.add_chapter(...)
```

Điều này tạo một "cổng kiểm soát" cho business rules.

---

# 28. Primitive Obsession

Một vấn đề khác bắt đầu xuất hiện khi thiết kế Domain Model:

```python
story_id: int
chapter_number: int
source_url: str
```

Các kiểu primitive có thể không đủ thể hiện business meaning.

Ví dụ:

```python
source_url = ""
```

hoặc:

```python
chapter_number = -10
```

Ta sẽ dần chuyển sang:

```text
StoryId
ChapterNumber
SourceUrl
```

Đây chính là tiền đề của **Value Object**, sẽ học ở Buổi 12–13.

---

# 29. Entity chưa phải trọng tâm hôm nay

Bạn sẽ thấy:

```text
Story
Chapter
CrawlerJob
```

có vẻ là Entity.

Đúng, rất có thể.

Nhưng hôm nay chưa cần quyết định hoàn toàn.

Trước tiên phải hiểu:

```text
Business concept
     ↓
Behavior
     ↓
Invariant
```

Sau đó mới hỏi:

> Object này là Entity hay Value Object?

---

# 30. Một Domain Model tốt phải trả lời được 4 câu hỏi

Khi nhìn vào object:

### 1. Nó là gì?

```text
CrawlerJob
= một lần thực thi crawler
```

### 2. Nó đang ở trạng thái nào?

```text
Pending
Running
Paused
Completed
Failed
```

### 3. Nó có thể làm gì?

```text
start()
pause()
resume()
complete()
fail()
```

### 4. Nó không được phép làm gì?

```text
Completed → Running
Pending → Resume
Failed → Complete
```

Nếu model trả lời rõ 4 câu này, chúng ta đang tiến gần Rich Domain Model.

---

# 31. Ví dụ hoàn chỉnh: CrawlerJob

```python
from enum import Enum


class CrawlerJobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class CrawlerJob:

    def __init__(self):
        self.status = CrawlerJobStatus.PENDING

    def start(self):
        if self.status != CrawlerJobStatus.PENDING:
            raise RuntimeError(
                "Only pending job can be started"
            )

        self.status = CrawlerJobStatus.RUNNING

    def pause(self):
        if self.status != CrawlerJobStatus.RUNNING:
            raise RuntimeError(
                "Only running job can be paused"
            )

        self.status = CrawlerJobStatus.PAUSED

    def resume(self):
        if self.status != CrawlerJobStatus.PAUSED:
            raise RuntimeError(
                "Only paused job can be resumed"
            )

        self.status = CrawlerJobStatus.RUNNING

    def complete(self):
        if self.status != CrawlerJobStatus.RUNNING:
            raise RuntimeError(
                "Only running job can be completed"
            )

        self.status = CrawlerJobStatus.COMPLETED
```

Đây là một Domain Model đơn giản nhưng đã có:

```text
State
+
Behavior
+
Invariant
+
Encapsulation
```

---

# 32. Business flow

Ta có:

```python
job = CrawlerJob()

job.start()
job.pause()
job.resume()
job.complete()
```

State:

```text
PENDING
   ↓
RUNNING
   ↓
PAUSED
   ↓
RUNNING
   ↓
COMPLETED
```

Nhưng:

```python
job.complete()
```

ngay từ đầu sẽ fail.

Và:

```python
job.resume()
```

sau `COMPLETED` cũng fail.

Domain object tự bảo vệ business rule.

---

# 33. Đây là điểm khác biệt rất lớn

### Anemic

```text
CrawlerJob
     ↓
data

CrawlerService
     ↓
business rules
```

### Rich

```text
CrawlerJob
 ├── state
 ├── behavior
 └── invariants
```

Application Service:

```text
orchestration
```

Infrastructure:

```text
persistence
```

Đây là separation of responsibility rất quan trọng.

---

# 34. Tuy nhiên, đừng biến Entity thành "God Object"

Rich Domain Model không có nghĩa:

```python
class Story:
    # 2,000 lines
```

và:

```text
database
http
filesystem
redis
email
logging
```

tất cả nằm trong `Story`.

Entity chỉ nên chứa **logic thuộc về chính domain concept đó**.

Ví dụ tốt:

```python
story.add_chapter()
story.publish()
story.archive()
```

Không tốt:

```python
story.send_email()
story.save_to_sqlite()
story.call_api()
story.write_file()
```

---

# 35. Domain Model và Separation of Concerns

Ta muốn:

```text
Domain
    ↓
Business rules
```

```text
Application
    ↓
Use case orchestration
```

```text
Infrastructure
    ↓
SQLite / Redis / HTTP / filesystem
```

Ví dụ:

```text
PauseCrawlerUseCase
        ↓
repository.get()
        ↓
job.pause()
        ↓
repository.save()
```

Application Service biết **workflow**.

Domain Object biết **business rule**.

---

# 36. Một cách phân biệt cực kỳ hữu ích

Hãy hỏi:

> "Nếu bỏ SQLite đi, business rule này còn tồn tại không?"

Nếu câu trả lời là **có**:

```text
job.pause()
```

đó là Domain.

Nếu:

```text
UPDATE crawler_jobs
SET status = ?
```

thì đó là Infrastructure.

---

# 37. Domain Model không nhất thiết phải phức tạp

Đừng nghĩ:

```text
DDD
=
nhiều class
+
nhiều abstraction
```

Không.

Một domain model tốt có thể rất nhỏ:

```python
class Money:
    ...

class Order:
    ...

class OrderItem:
    ...
```

Nếu business đơn giản, model cũng đơn giản.

DDD quan trọng ở:

> **đúng model**, không phải **nhiều model**.

---

# 38. Bài tập Buổi 4

## Bài 1 — Chuyển Data thành Behavior

Cho:

```python
class CrawlerJob:
    status
```

Hãy thiết kế:

```text
start()
pause()
resume()
complete()
fail()
```

và xác định transition hợp lệ.

---

## Bài 2 — Invariant

Tìm ít nhất 10 invariant cho:

```text
Story
Chapter
CrawlerJob
ReadingProgress
```

Ví dụ:

```text
Chapter number > 0
```

---

## Bài 3 — Anemic hay Rich?

Phân tích:

```python
class Story:
    title: str
    status: str
    chapters: list
```

và:

```python
class StoryService:

    def add_chapter(self, story, chapter):
        ...
```

Tại sao đây là Anemic Domain Model?

Sau đó refactor thành Rich Domain Model.

---

# 39. Bài tập quan trọng nhất

Hãy thiết kế `Story` bằng tư duy:

```text
State
Behavior
Invariant
```

Không cần Repository.

Không cần SQLite.

Không cần API.

Không cần GUI.

Chỉ:

```text
Story
```

Hãy trả lời:

### State

```text
Story có những trạng thái nào?
```

### Behavior

```text
Story có thể làm gì?
```

### Invariant

```text
Điều gì không bao giờ được phép xảy ra?
```

Ví dụ:

```text
DRAFT
PUBLISHED
ARCHIVED
```

và:

```text
publish()
archive()
add_chapter()
```

---

# 40. Tư duy cốt lõi của Buổi 4

Hãy ghi nhớ chuỗi này:

```text
Business Language
       ↓
Domain Concept
       ↓
State
       ↓
Behavior
       ↓
Business Rule
       ↓
Invariant
       ↓
Domain Model
```

Và nguyên tắc quan trọng nhất:

> **Đừng thiết kế Entity như một cái túi chứa dữ liệu. Hãy thiết kế nó như một đối tượng có trách nhiệm bảo vệ các quy tắc của domain.**

Buổi 5 sẽ là **Event Storming Deep Dive**. Chúng ta sẽ lấy chính hệ thống **crawler + story + reading** và từ các câu mô tả business, dựng thành:

```text
Actor
  ↓
Command
  ↓
Domain Event
  ↓
Aggregate
  ↓
Policy
  ↓
Read Model
```

Đây sẽ là cầu nối cực kỳ quan trọng từ **Strategic DDD** sang **Tactical DDD**.
