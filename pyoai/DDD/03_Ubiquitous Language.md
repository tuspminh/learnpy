# DDD Deep Dive — Buổi 3

## Ubiquitous Language — Xây dựng ngôn ngữ chung của Domain

Buổi 2 chúng ta đã học:

```text
Domain
   ↓
Business Capability
   ↓
Subdomain
   ↓
Core / Supporting / Generic
```

Hôm nay chúng ta đi sâu vào một nền tảng cực kỳ quan trọng của DDD:

> **Ubiquitous Language — Ngôn ngữ chung của Domain.**

Đây là thứ giúp **developer, domain expert, tester, product owner và codebase nói cùng một ngôn ngữ**.

---

# 1. Ubiquitous Language là gì?

Có thể hiểu đơn giản:

> **Ubiquitous Language là một ngôn ngữ chung được cả team sử dụng để mô tả domain, và ngôn ngữ đó phải xuất hiện nhất quán trong code.**

Ví dụ domain của chúng ta:

```text
Story
Chapter
Source
Crawler
CrawlerJob
ReadingProgress
```

Nếu business gọi:

> "Nguồn truyện"

thì code không nên gọi:

```python
WebsiteProvider
```

ở chỗ này, rồi:

```python
Site
```

ở chỗ khác, rồi:

```python
Source
```

ở chỗ khác.

Ta cần thống nhất:

```text
Source
```

---

# 2. Tại sao ngôn ngữ lại quan trọng?

Hãy tưởng tượng Product Owner nói:

> "Khi crawler phát hiện một chương mới, hệ thống phải thêm chương đó vào truyện."

Developer hiểu:

```text
new chapter
```

Tester hiểu:

```text
new content
```

Database designer hiểu:

```text
new row
```

Crawler developer hiểu:

```text
crawl result
```

Mọi người đang nói về cùng một business event nhưng dùng những khái niệm khác nhau.

Đây là nguồn gốc của rất nhiều bug.

---

# 3. Ubiquitous Language giải quyết vấn đề này

Ta thống nhất:

```text
Chapter Discovered
```

có nghĩa chính xác:

> Crawler đã xác định được một Chapter mới từ Source.

Sau đó:

```text
ChapterDiscovered
```

xuất hiện trong code.

Ví dụ:

```python
class ChapterDiscovered:
    ...
```

Tester:

```text
Given a ChapterDiscovered event...
```

Document:

```text
When ChapterDiscovered occurs...
```

Business:

> "Khi Chapter Discovered..."

Mọi người đang nói cùng một ngôn ngữ.

---

# 4. Ubiquitous Language không chỉ là đặt tên class

Đây là hiểu lầm phổ biến.

Nó không đơn giản là:

```python
class Story:
    ...
```

Ubiquitous Language bao phủ:

```text
Entity
Value Object
Command
Event
State
Business Rule
Use Case
Error
API
Database concept
Documentation
Test
```

Ví dụ:

```text
Command:
StartCrawler

Event:
CrawlerStarted

State:
Running

Exception:
CrawlerAlreadyRunning
```

Tất cả đều phải xuất phát từ domain language.

---

# 5. Ví dụ rất dễ thấy

Giả sử business nói:

> "Crawler có thể tạm dừng."

Bạn có thể viết:

```python
crawler.pause()
```

Nhưng developer khác viết:

```python
crawler.stop_temporarily()
```

Developer khác:

```python
crawler.hold()
```

Developer khác:

```python
crawler.suspend()
```

Nếu business thực sự dùng từ:

> Pause

thì nên thống nhất:

```python
crawler.pause()
```

---

# 6. Từ ngữ trong Domain phải có meaning

Ví dụ:

```text
Story
```

có nghĩa gì?

Có phải:

> Một truyện hoàn chỉnh được hệ thống quản lý?

Hay:

> Một record trong bảng `stories`?

Hai thứ này không nhất thiết giống nhau.

DDD yêu cầu chúng ta xác định:

> **Domain concept thực sự là gì?**

---

# 7. Ví dụ `Source`

Trong hệ thống crawler:

```text
Source
```

có thể có nghĩa:

> Một nguồn nội dung mà hệ thống có thể crawl.

Ví dụ:

```text
Source
 ├── name
 ├── base_url
 ├── enabled
 └── crawler_plugin
```

Nhưng đừng vội biến nó thành database schema.

Trước tiên hãy xác định business meaning.

---

# 8. Source khác Website

Giả sử:

```text
https://example.com
```

Có phải `Website` không?

Trong business của chúng ta, có thể gọi là:

```text
Source
```

vì business quan tâm:

> "Nguồn này cung cấp truyện."

Không nhất thiết quan tâm:

> "Đây là một website theo nghĩa kỹ thuật."

Đây chính là DDD:

**business language > technical terminology.**

---

# 9. `Crawler` và `CrawlerJob` có giống nhau không?

Không nhất thiết.

Đây là ví dụ rất hay về việc phải làm rõ language.

### Crawler

Có thể là:

> Component chịu trách nhiệm thực hiện quá trình crawl.

### CrawlerJob

Có thể là:

> Một lần chạy cụ thể của crawler.

Ví dụ:

```text
Crawler
   |
   +--- Job #1001
   +--- Job #1002
   +--- Job #1003
```

Vậy:

```text
Crawler ≠ CrawlerJob
```

Nếu không xác định rõ từ đầu, sau này code sẽ rất dễ lẫn.

---

# 10. Một Domain có thể có nhiều meaning cho cùng một từ

Đây là điểm cực kỳ quan trọng.

Ví dụ:

```text
Chapter
```

Trong **Catalog Context**:

> Chapter là metadata của một chương.

Có thể:

```text
Chapter
 ├── number
 ├── title
 ├── published_at
 └── url
```

Trong **Reading Context**:

> Chapter là nội dung mà user đang đọc.

Có thể:

```text
Chapter
 ├── content
 ├── position
 └── reading_state
```

Hai model không nhất thiết phải giống nhau.

---

# 11. Đây là dấu hiệu của Bounded Context

Nếu một từ bắt đầu có meaning khác nhau trong những vùng khác nhau:

```text
Catalog:
Chapter = catalog metadata

Reading:
Chapter = readable content
```

thì đây là dấu hiệu:

> Có thể chúng ta cần **Bounded Context**.

Buổi 7 chúng ta sẽ học sâu về chuyện này.

---

# 12. Đừng cố tạo một "Universal Model"

Một lỗi phổ biến:

> "Story chỉ nên có một class duy nhất trong toàn bộ hệ thống."

Ví dụ:

```python
class Story:
    id
    title
    chapters
    reading_progress
    crawler_status
    search_score
    user_bookmarks
    ...
```

Đây là một **God Model**.

Nó cố gắng đại diện cho mọi khía cạnh của business.

Kết quả:

```text
Story
 ├── Catalog logic
 ├── Reading logic
 ├── Crawler logic
 ├── Search logic
 └── User logic
```

Rất nguy hiểm.

---

# 13. Cùng một business concept có thể có nhiều model

Ví dụ `Story`.

### Catalog

```text
Story
 ├── title
 ├── author
 ├── genres
 └── publication_status
```

### Reading

```text
Story
 ├── chapters
 └── reading_order
```

### Search

```text
Story
 ├── searchable_title
 ├── tokens
 └── ranking
```

Không cần ép cả ba thành một object.

---

# 14. Ubiquitous Language phải xuất hiện trong code

Ví dụ business nói:

> "Chapter đã được phát hiện."

Không nên:

```python
class NewContentRecord:
    ...
```

nếu business không dùng khái niệm `NewContentRecord`.

Nên:

```python
class ChapterDiscovered:
    ...
```

---

# 15. Command cũng phải dùng Domain Language

Ví dụ:

```text
StartCrawler
PauseCrawler
ResumeCrawler
CompleteCrawler
```

Không nên:

```text
ExecuteCrawlerProcess
SuspendCrawlerExecution
ContinueCrawlerExecution
```

nếu business thực sự dùng:

```text
start
pause
resume
complete
```

Code càng gần ngôn ngữ business càng tốt.

---

# 16. Event cũng phải dùng Domain Language

Ví dụ:

```python
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerStarted
CrawlerPaused
CrawlerCompleted
CrawlerFailed
```

Có thể nhìn vào event name là hiểu business đang diễn ra chuyện gì.

---

# 17. Business Rule cũng phải viết bằng Domain Language

Ví dụ business rule:

> Không thể pause một crawler chưa chạy.

Không nên chỉ có:

```python
if status != 2:
    raise Exception()
```

Hãy model bằng language:

```python
if self.status != CrawlerStatus.RUNNING:
    raise CrawlerCannotBePaused()
```

Code trở nên dễ đọc hơn rất nhiều.

---

# 18. State cũng thuộc Ubiquitous Language

Crawler:

```text
Pending
Running
Paused
Completed
Failed
```

Đừng tùy tiện dùng:

```text
0
1
2
3
4
```

Domain code nên nói:

```python
CrawlerStatus.RUNNING
```

thay vì:

```python
status == 2
```

Vì:

```python
CrawlerStatus.RUNNING
```

mang business meaning.

---

# 19. Exception cũng là Domain Language

Ví dụ:

```python
class CrawlerAlreadyRunning(DomainError):
    pass
```

hoặc:

```python
class ChapterAlreadyExists(DomainError):
    pass
```

Thay vì:

```python
raise ValueError("invalid state")
```

Một exception tốt có thể diễn đạt business rule.

---

# 20. Ví dụ trước và sau

### Trước

```python
def update_status(job, status):
    if status == 3:
        ...
```

Rất khó hiểu.

### Sau

```python
job.complete()
```

hoặc:

```python
job.pause()
```

Business intent trở nên rõ ràng.

---

# 21. Ubiquitous Language giúp code "đọc như business"

Ví dụ:

```python
crawler.start()

chapter = crawler.discover_chapter()

story.add_chapter(chapter)

reading_progress.mark_read(chapter)
```

Đọc code ta có thể hình dung ngay business flow:

```text
Crawler start
    ↓
Discover chapter
    ↓
Add chapter to story
    ↓
Mark chapter as read
```

Đó là một dấu hiệu tốt của Domain Model.

---

# 22. Nhưng đừng lạm dụng tự nhiên hóa code

Không phải cứ business language là code phải giống tiếng người 100%.

Ví dụ không cần:

```python
crawler.perform_the_action_of_starting_the_crawler_process()
```

DDD không yêu cầu code dài.

Tốt nhất:

```python
crawler.start()
```

Ngắn nhưng rõ business meaning.

---

# 23. Ubiquitous Language và database

Database cũng nên phản ánh language **khi phù hợp**.

Ví dụ:

```text
crawler_jobs
crawler_status
chapter_number
reading_progress
```

tốt hơn:

```text
tbl_01
status_code
data_type
obj_ref
```

Nhưng nhớ:

> Database không phải Domain Model.

Ta chỉ muốn tránh những tên kỹ thuật vô nghĩa.

---

# 24. Ubiquitous Language và API

API:

```http
POST /crawler-jobs/{id}/pause
```

rõ ràng.

Thay vì:

```http
POST /jobs/{id}/action/3
```

API cũng đang thể hiện domain language.

---

# 25. Ubiquitous Language và test

Đây là nơi cực kỳ hữu ích.

Test:

```python
def test_running_crawler_can_be_paused():
    ...
```

Người đọc hiểu business ngay.

Hoặc:

```python
def test_cannot_add_duplicate_chapter():
    ...
```

Không cần đọc implementation vẫn hiểu requirement.

---

# 26. Một kỹ thuật rất mạnh: Glossary

Ta nên tạo một **Domain Glossary**.

Ví dụ:

| Term             | Meaning                              |
| ---------------- | ------------------------------------ |
| Story            | Một tác phẩm được hệ thống quản lý   |
| Chapter          | Một chương thuộc Story               |
| Source           | Nguồn cung cấp nội dung              |
| Crawler          | Thành phần thực hiện quá trình crawl |
| Crawler Job      | Một lần thực thi crawler             |
| Reading Progress | Trạng thái tiến độ đọc của user      |
| Bookmark         | Vị trí/nội dung user đánh dấu        |

Glossary này sẽ trở thành "từ điển" của team.

---

# 27. Glossary phải ghi cả những từ KHÔNG được dùng

Đây là kỹ thuật rất tốt.

Ví dụ:

```text
Preferred:
Source

Avoid:
Website
Site
Provider
Publisher
```

Nếu business thực sự thống nhất `Source`, hãy cố định nó.

---

# 28. Synonym Problem

Ví dụ team có:

```text
Crawler
Spider
Scraper
CrawlerWorker
CrawlerService
CrawlerEngine
```

Tất cả đều có thể đang chỉ một thứ.

Đây là dấu hiệu vocabulary đang hỗn loạn.

Hãy hỏi:

> Business thực sự gọi nó là gì?

Nếu chọn:

```text
Crawler
```

thì dùng nhất quán.

---

# 29. Nhưng synonym đôi khi lại là tín hiệu tốt

Ví dụ:

```text
Crawler
CrawlerJob
CrawlerWorker
```

Nếu phân tích kỹ:

```text
Crawler
= business capability

CrawlerJob
= một execution

CrawlerWorker
= infrastructure component
```

Vậy chúng **không phải synonym**.

Đây là một phát hiện rất quan trọng.

---

# 30. Domain Language giúp phát hiện abstraction sai

Giả sử bạn có:

```python
class Manager:
    def execute(self):
        ...
```

Đây là abstraction rất nghèo meaning.

Manager làm gì?

```text
StoryManager?
CrawlerManager?
ChapterManager?
```

DDD buộc bạn hỏi:

> "Business thực sự có khái niệm Manager không?"

Nếu không:

> Có lẽ abstraction này xuất phát từ technical thinking.

---

# 31. Code smell: `Manager`, `Helper`, `Utils`

Không phải lúc nào cũng sai.

Nhưng nếu bạn thấy:

```text
StoryManager
CrawlerManager
ChapterManager
DataHelper
CommonUtils
```

hãy đặt câu hỏi:

> Đây có phải business concept không?

Nếu không, có thể architecture đang che giấu domain logic.

---

# 32. Ví dụ refactor

Thay vì:

```python
crawler_manager.start_crawler(job)
```

có thể domain model là:

```python
job.start()
```

Application layer:

```python
job = repository.get(job_id)

job.start()

repository.save(job)
```

Sự khác biệt:

```text
Manager
```

là technical abstraction.

Trong khi:

```text
CrawlerJob.start()
```

là domain behavior.

---

# 33. Ubiquitous Language không chỉ dành cho Developer

Nó phải được dùng trong:

```text
Product specification
Documentation
User story
Ticket
Test
Code
API
Event
Log
Monitoring
```

Ví dụ:

Business:

> Khi crawler phát hiện chapter mới...

Specification:

> `ChapterDiscovered` được phát sinh...

Code:

```python
ChapterDiscovered(...)
```

Test:

```python
assert ChapterDiscovered in events
```

Tất cả nói cùng một thứ.

---

# 34. Một ví dụ xuyên suốt

Business requirement:

> Khi một crawler đang chạy, admin có thể pause crawler. Crawler đang paused có thể resume. Khi crawler hoàn thành, nó chuyển sang trạng thái completed và không thể resume lại.

Ta chuyển thành Ubiquitous Language:

### Terms

```text
Crawler
CrawlerJob
Admin
Running
Paused
Completed
```

### Commands

```text
PauseCrawler
ResumeCrawler
CompleteCrawler
```

### Events

```text
CrawlerPaused
CrawlerResumed
CrawlerCompleted
```

### Rules

```text
Running → Paused
Paused → Running
Running → Completed
Completed → không thể Resume
```

### Exceptions

```text
CrawlerCannotBePaused
CrawlerCannotBeResumed
CrawlerAlreadyCompleted
```

Đây chính là cách DDD biến **business conversation → model → code**.

---

# 35. Từ ngôn ngữ đến code

Sau khi có vocabulary:

```text
CrawlerJob
```

ta có thể bắt đầu:

```python
class CrawlerJob:
    ...
```

Sau khi xác định state:

```python
from enum import Enum


class CrawlerJobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

Sau đó behavior:

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

Lúc này code bắt đầu kể được câu chuyện business.

---

# 36. Một nguyên tắc cực kỳ quan trọng

> **Nếu bạn không thể giải thích một class bằng ngôn ngữ business, hãy nghi ngờ class đó.**

Ví dụ:

```python
class CrawlerJob:
```

Bạn giải thích được:

> Một lần thực thi crawler.

Tốt.

Nhưng:

```python
class DataProcessorManager:
```

Bạn giải thích:

> Nó xử lý data.

Câu này quá mơ hồ.

Hãy hỏi:

> Business thực sự gọi "Data Processor Manager" là gì?

Có thể phát hiện abstraction sai.

---

# 37. Ubiquitous Language và bounded context

Một điều tinh tế hơn:

> **Ubiquitous Language không nhất thiết giống nhau trên toàn hệ thống.**

Ví dụ:

### Catalog Context

```text
Story
Chapter
Publication
Source
```

### Reading Context

```text
Book
Chapter
ReadingSession
Progress
```

### Crawling Context

```text
Source
CrawlTarget
CrawlerJob
DiscoveredChapter
```

Không nên cố tạo một vocabulary toàn hệ thống nếu các context có business meaning khác nhau.

Đây là lý do chúng ta sẽ học **Bounded Context** sau này.

---

# 38. Nguyên tắc "One word, one meaning — within a context"

Trong một Bounded Context:

> Một term nên có meaning rõ ràng.

Ví dụ trong Catalog:

```text
Chapter
```

phải có meaning ổn định.

Nếu trong cùng context lúc thì:

```text
Chapter = metadata
```

lúc:

```text
Chapter = HTML content
```

thì model bắt đầu có vấn đề.

---

# 39. Bài tập Buổi 3

Đây là bài tập quan trọng hơn việc viết code.

## Bài 1 — Domain Glossary

Tạo glossary cho app:

```text
Story
Chapter
Source
Crawler
CrawlerJob
CrawlerWorker
ReadingProgress
Bookmark
```

Với mỗi term, viết:

```text
Term
Meaning
```

---

## Bài 2 — Synonym

Tìm các từ đang có thể bị dùng lẫn:

```text
Crawler
Spider
Scraper
```

```text
Source
Website
Site
Provider
```

```text
Chapter
Episode
Part
```

Sau đó chọn **một vocabulary chuẩn**.

---

## Bài 3 — Command

Tìm 10 commands.

Ví dụ:

```text
StartCrawler
PauseCrawler
ResumeCrawler
...
```

---

## Bài 4 — Domain Event

Tìm 10 events.

Ví dụ:

```text
CrawlerStarted
CrawlerPaused
ChapterDiscovered
...
```

---

## Bài 5 — Business State

Xác định state của:

```text
CrawlerJob
Story
Chapter
ReadingProgress
```

---

## Bài 6 — Business Rule

Viết rule bằng ngôn ngữ business, **chưa code**.

Ví dụ:

```text
A Running CrawlerJob can be paused.
A Paused CrawlerJob can be resumed.
A Completed CrawlerJob cannot be resumed.
```

---

# 40. Bài tập quan trọng nhất

Hãy thử viết câu này:

> "Khi ________, hệ thống sẽ ________."

Ví dụ:

```text
Khi CrawlerJob bắt đầu,
hệ thống phát sinh CrawlerStarted.
```

```text
Khi crawler phát hiện một chapter chưa tồn tại,
hệ thống phát sinh ChapterDiscovered.
```

```text
Khi user đọc xong chapter,
ReadingProgress được cập nhật.
```

Nếu bạn có thể viết **20–30 câu** kiểu này, bạn đang bắt đầu nhìn hệ thống bằng tư duy domain thay vì tư duy database.

---

# 41. Tổng kết Buổi 3

Bạn cần nắm chắc:

```text
Ubiquitous Language
        ↓
Business terminology
        ↓
Domain Model
        ↓
Code
```

Các nguyên tắc quan trọng:

1. **Business và developer phải nói cùng một ngôn ngữ.**
2. Tên class, method, event, command nên xuất phát từ domain.
3. Tránh vocabulary mơ hồ như `Manager`, `Helper`, `Utils` khi chúng che giấu business concept.
4. Một từ có thể có meaning khác nhau ở các Bounded Context khác nhau.
5. Không ép toàn hệ thống dùng một model duy nhất.
6. Domain Event và Command cũng là một phần của Ubiquitous Language.
7. **Ngôn ngữ tốt giúp phát hiện model sai trước khi viết code.**

### Tiếp theo: Buổi 4 — Domain Model

Chúng ta sẽ bắt đầu đi từ **language → model**:

```text
Business concept
       ↓
Behavior
       ↓
Invariant
       ↓
Domain Model
       ↓
Entity / Value Object
```

Và tôi sẽ giải thích rất kỹ **Anemic Domain Model vs Rich Domain Model**, vì đây là nền móng trực tiếp trước khi chúng ta bước vào **Entity và Value Object**.
