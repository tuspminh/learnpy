# DDD Deep Dive — Buổi 5

## Event Storming — Khám phá Domain bằng sự kiện

Ở 4 buổi trước, chúng ta đã đi theo chuỗi:

```text
Buổi 1
Domain
   ↓
Business Problem

Buổi 2
Subdomain
   ↓
Core / Supporting / Generic

Buổi 3
Ubiquitous Language
   ↓
Domain Vocabulary

Buổi 4
Domain Model
   ↓
State + Behavior + Invariant
```

Hôm nay chúng ta học một kỹ thuật cực kỳ mạnh để **khám phá Domain trước khi viết code**:

> **Event Storming**

---

# 1. Event Storming là gì?

Event Storming là kỹ thuật dùng **Domain Event** để khám phá cách business thực sự hoạt động.

Thay vì bắt đầu bằng:

```text
Database
   ↓
Table
   ↓
Class
   ↓
CRUD
```

ta bắt đầu bằng:

```text
Business
   ↓
Điều gì xảy ra?
   ↓
Domain Event
   ↓
Command
   ↓
Actor
   ↓
Business Rule
   ↓
Aggregate
```

---

# 2. Tại sao Event Storming quan trọng?

Khi bắt đầu một project, developer thường hỏi:

> "Database có những bảng nào?"

DDD hỏi:

> **"Trong business, những chuyện gì xảy ra?"**

Ví dụ hệ thống truyện:

```text
Crawler bắt đầu
Chapter được phát hiện
Chapter được tải xuống
Chapter được lưu
Crawler hoàn thành
User bắt đầu đọc
User đọc xong chapter
Reading progress được cập nhật
```

Đây chính là business flow.

---

# 3. Domain Event là gì?

Domain Event là:

> **Một sự kiện nghiệp vụ đã xảy ra và có ý nghĩa đối với domain.**

Tên event thường dùng **past tense**.

Ví dụ:

```text
CrawlerStarted
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerCompleted
ReadingStarted
ChapterRead
ReadingProgressUpdated
```

Chú ý:

```text
CrawlerStarted
```

nghĩa là:

> Crawler **đã bắt đầu**.

Không phải:

```text
StartCrawler
```

`StartCrawler` là Command.

---

# 4. Command vs Event

Đây là một trong những thứ phải phân biệt thật chắc.

## Command

Là:

> **Yêu cầu thực hiện một hành động.**

Ví dụ:

```text
StartCrawler
PauseCrawler
ResumeCrawler
AddChapter
MarkChapterAsRead
```

## Event

Là:

> **Thông báo một hành động đã xảy ra.**

Ví dụ:

```text
CrawlerStarted
CrawlerPaused
CrawlerResumed
ChapterAdded
ChapterMarkedAsRead
```

---

# 5. Cặp Command → Event

Ví dụ:

```text
StartCrawler
      ↓
CrawlerStarted
```

```text
PauseCrawler
      ↓
CrawlerPaused
```

```text
ResumeCrawler
      ↓
CrawlerResumed
```

```text
MarkChapterAsRead
      ↓
ChapterMarkedAsRead
```

Nhìn vào đây ta có thể thấy:

```text
Command = intention
Event   = fact
```

---

# 6. Command không đảm bảo thành công

Ví dụ:

```text
PauseCrawler
```

được gửi.

Nhưng crawler đang:

```text
COMPLETED
```

thì command có thể thất bại.

Do đó:

```text
PauseCrawler
       ↓
Business Rule
       ↓
FAILED
```

không có:

```text
CrawlerPaused
```

---

# 7. Event là fact

Một khi:

```text
CrawlerPaused
```

được phát ra, nó có nghĩa:

> Việc pause đã thực sự xảy ra.

Không nên đặt tên event:

```text
PauseCrawler
```

vì đó là intention.

---

# 8. Event Storming bắt đầu từ đâu?

Hãy tưởng tượng chúng ta có một bảng lớn.

Chúng ta viết tất cả những gì xảy ra trong business:

```text
CrawlerStarted
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerCompleted
```

Sau đó sắp xếp theo thời gian:

```text
CrawlerStarted
      ↓
ChapterDiscovered
      ↓
ChapterDownloaded
      ↓
ChapterSaved
      ↓
CrawlerCompleted
```

Đây là **timeline của domain**.

---

# 9. Ví dụ thực tế: Story Crawler

Business requirement:

> Admin yêu cầu hệ thống crawl một Source. Crawler bắt đầu chạy. Trong quá trình crawl, hệ thống phát hiện chapter mới. Chapter được tải xuống và lưu vào Story. Khi không còn chapter mới, crawler hoàn thành.

Ta bắt đầu từ events:

```text
CrawlerStarted

ChapterDiscovered

ChapterDownloaded

ChapterSaved

CrawlerCompleted
```

Đây là bước đầu tiên.

---

# 10. Từ Event tìm Command

Mỗi event thường có một command phía trước.

```text
StartCrawler
    ↓
CrawlerStarted
```

```text
DiscoverChapter
    ↓
ChapterDiscovered
```

```text
DownloadChapter
    ↓
ChapterDownloaded
```

```text
SaveChapter
    ↓
ChapterSaved
```

```text
CompleteCrawler
    ↓
CrawlerCompleted
```

Nhưng cần cẩn thận:

> Không phải mọi Event đều có Command trực tiếp từ user.

Có event được tạo bởi **policy/process**.

---

# 11. Actor là gì?

Actor là người hoặc hệ thống thực hiện command.

Ví dụ:

```text
Admin
   ↓
StartCrawler
```

Hoặc:

```text
Scheduler
   ↓
StartCrawler
```

Hoặc:

```text
Crawler
   ↓
DiscoverChapter
```

---

# 12. Event Storming mở rộng

Ta có:

```text
Actor
  ↓
Command
  ↓
Domain Event
```

Ví dụ:

```text
Admin
  ↓
StartCrawler
  ↓
CrawlerStarted
```

Tiếp:

```text
CrawlerWorker
  ↓
DiscoverChapter
  ↓
ChapterDiscovered
```

---

# 13. Policy

Bây giờ xuất hiện một khái niệm cực kỳ quan trọng:

> **Policy**

Policy mô tả:

> Khi một event xảy ra, business yêu cầu thực hiện hành động tiếp theo.

Ví dụ:

```text
ChapterDiscovered
      ↓
[Policy]
      ↓
DownloadChapter
```

Tức là:

> Khi phát hiện chapter mới, hệ thống phải tải chapter đó xuống.

---

# 14. Event → Policy → Command

Ta có:

```text
ChapterDiscovered
       ↓
   Policy
       ↓
DownloadChapter
       ↓
ChapterDownloaded
```

Đây chính là một business reaction.

---

# 15. Một chuỗi hoàn chỉnh

Hệ thống crawler:

```text
Admin
  ↓
StartCrawler
  ↓
CrawlerStarted
  ↓
[Start Crawling Policy]
  ↓
DiscoverChapter
  ↓
ChapterDiscovered
  ↓
[Download Policy]
  ↓
DownloadChapter
  ↓
ChapterDownloaded
  ↓
[Save Policy]
  ↓
SaveChapter
  ↓
ChapterSaved
```

Sau đó:

```text
NoMoreChapterFound
       ↓
CompleteCrawler
       ↓
CrawlerCompleted
```

---

# 16. Đây chính là Event Storming

Ta đang khám phá:

```text
Actor
Command
Event
Policy
```

mà **chưa cần viết một dòng Python nào**.

Đây là điểm cực kỳ quan trọng.

---

# 17. Tại sao không bắt đầu bằng Entity?

Nếu bắt đầu:

```text
Story
Chapter
Crawler
```

ta rất dễ suy nghĩ theo cấu trúc dữ liệu.

Nhưng nếu bắt đầu bằng:

```text
ChapterDiscovered
ChapterDownloaded
ChapterSaved
```

ta bắt đầu nhìn thấy:

```text
Behavior
Process
Business Flow
```

Sau đó mới suy ra:

> Object nào chịu trách nhiệm?

Đó là cách Event Storming giúp khám phá Aggregate.

---

# 18. Từ Event tìm Aggregate

Ví dụ:

```text
CrawlerStarted
CrawlerPaused
CrawlerResumed
CrawlerCompleted
```

Các event này xoay quanh:

```text
CrawlerJob
```

Có khả năng:

```text
CrawlerJob
```

là Aggregate.

Tương tự:

```text
ChapterAdded
ChapterRemoved
```

có thể liên quan đến:

```text
Story
```

---

# 19. Đừng kết luận Aggregate quá sớm

Đây là một nguyên tắc quan trọng.

Event:

```text
ChapterDiscovered
```

không có nghĩa ngay lập tức:

```text
Chapter = Aggregate
```

Ta phải hỏi:

> Ai chịu trách nhiệm bảo vệ invariant?

Ví dụ:

> Một Story không được có hai chapter cùng số.

Ai có đủ thông tin để bảo vệ rule?

```text
Story
```

Có thể `Story` là Aggregate Root.

---

# 20. Aggregate được phát hiện từ business rule

Ví dụ:

```text
Story
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

Rule:

> Story không thể có hai Chapter cùng number.

Muốn kiểm tra:

```text
Chapter 5
```

có trùng không, cần biết các chapter của Story.

Vậy:

```text
Story
```

có thể cần kiểm soát:

```text
chapters
```

Đây là dấu hiệu Aggregate boundary.

---

# 21. Event Storming và Aggregate

Một cách suy nghĩ:

```text
Domain Event
      ↓
Ai tạo ra event?
      ↓
Ai chịu trách nhiệm?
      ↓
Ai bảo vệ invariant?
      ↓
Aggregate
```

Ví dụ:

```text
AddChapter
     ↓
Story
     ↓
Story.add_chapter()
     ↓
ChapterAdded
```

---

# 22. Ví dụ `Story`

Business:

> Không thể thêm chapter vào Story đã archived.

Ta có:

```text
Command:
AddChapter
```

Aggregate:

```text
Story
```

Behavior:

```python
story.add_chapter(chapter)
```

Event:

```text
ChapterAdded
```

Flow:

```text
AddChapter
    ↓
Story.add_chapter()
    ↓
Business Rule
    ↓
ChapterAdded
```

---

# 23. Event Storming phát hiện Domain Boundary

Giả sử chúng ta có:

```text
CrawlerStarted
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerCompleted
```

và:

```text
ReadingStarted
ChapterRead
ProgressUpdated
BookmarkCreated
```

Nhìn vào event stream, chúng ta bắt đầu thấy hai nhóm:

```text
Crawling
----------------
CrawlerStarted
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerCompleted
```

và:

```text
Reading
----------------
ReadingStarted
ChapterRead
ProgressUpdated
BookmarkCreated
```

Có thể đây là hai **Bounded Context** khác nhau.

---

# 24. Đây là sức mạnh của Event Storming

Thay vì nói:

> "Có bảng `crawler_jobs`, `stories`, `chapters`, `reading_progress`."

Ta nói:

```text
Crawling Context
       ↓
Crawl events

Reading Context
       ↓
Reading events
```

Chúng ta bắt đầu nhìn thấy **business boundary**.

---

# 25. Event Storming không phải Event Sourcing

Hai khái niệm này thường bị nhầm.

### Event Storming

Là:

> Kỹ thuật khám phá và model business.

### Event Sourcing

Là:

> Một chiến lược persistence, lưu state bằng chuỗi events.

Bạn hoàn toàn có thể:

```text
Event Storming
+
SQLite
```

mà không dùng Event Sourcing.

---

# 26. Domain Event không nhất thiết phải là message broker

Ví dụ:

```python
event = ChapterDiscovered(...)
```

Event có thể chỉ tồn tại trong memory.

Không bắt buộc phải có:

```text
Kafka
RabbitMQ
Redis
Celery
```

DDD không đồng nghĩa với microservices.

---

# 27. Domain Event trong Python

Ví dụ:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ChapterDiscovered:
    story_id: int
    chapter_id: int
    occurred_at: datetime
```

Event là một fact.

Thường nên:

```python
@dataclass(frozen=True)
```

để event immutable.

---

# 28. Aggregate phát sinh Event

Ví dụ:

```python
class Story:

    def __init__(self):
        self._events = []

    def add_chapter(self, chapter):
        # validate invariant

        self._chapters.append(chapter)

        self._events.append(
            ChapterAdded(
                story_id=self.id,
                chapter_id=chapter.id,
            )
        )
```

Đây mới chỉ là ví dụ đơn giản.

Sau này chúng ta sẽ thiết kế Domain Event đúng hơn.

---

# 29. Event không nên chứa logic

Sai:

```python
class ChapterAdded:

    def save_to_database(self):
        ...
```

Event chỉ mô tả:

> Điều gì đã xảy ra?

Ví dụ:

```python
@dataclass(frozen=True)
class ChapterAdded:
    story_id: int
    chapter_id: int
```

Persistence hoặc reaction nằm bên ngoài.

---

# 30. Domain Event vs Integration Event

Đây là distinction quan trọng.

### Domain Event

Dùng bên trong domain/application boundary:

```text
ChapterAdded
```

### Integration Event

Dùng để giao tiếp với hệ thống khác:

```text
ChapterAddedToCatalog
```

hoặc một message contract cụ thể.

Không nên vội biến mọi Domain Event thành Kafka/RabbitMQ message.

---

# 31. Event Storming và Use Case

Event Storming cũng giúp phát hiện Use Case.

Ví dụ:

```text
Admin
  ↓
StartCrawler
```

Có thể trở thành:

```python
StartCrawlerUseCase
```

Tiếp:

```text
Admin
  ↓
PauseCrawler
```

→

```python
PauseCrawlerUseCase
```

Và:

```text
User
  ↓
MarkChapterAsRead
```

→

```python
MarkChapterAsReadUseCase
```

---

# 32. Nhìn toàn hệ thống

Ta có thể dựng một bản đồ như sau:

```text
                 ┌──────────────┐
                 │    Admin     │
                 └──────┬───────┘
                        │
                 StartCrawler
                        │
                        ▼
                CrawlerStarted
                        │
                        ▼
                DiscoverChapter
                        │
                        ▼
               ChapterDiscovered
                        │
                        ▼
                 DownloadChapter
                        │
                        ▼
               ChapterDownloaded
                        │
                        ▼
                   SaveChapter
                        │
                        ▼
                 ChapterSaved
                        │
                        ▼
                CrawlerCompleted
```

Đây chính là **business process**.

---

# 33. Một kỹ thuật rất hữu ích: Past Tense

Khi tìm Domain Event, hãy hỏi:

> "Điều gì đã xảy ra?"

Ví dụ:

```text
StoryCreated
ChapterAdded
ChapterPublished
CrawlerStarted
CrawlerCompleted
UserRegistered
OrderPaid
PaymentFailed
```

Nếu tên nghe giống command:

```text
CreateStory
AddChapter
StartCrawler
```

thì có khả năng bạn đang viết Command thay vì Event.

---

# 34. Event Storming Workshop

Trong một team thực tế, Event Storming thường có sự tham gia của:

```text
Domain Expert
Product Owner
Developer
Tester
Architect
Business Analyst
```

Mục tiêu:

> Không phải để architect một mình quyết định model.

Mà để **business knowledge được đưa vào model**.

---

# 35. Developer không nên tự đoán domain

Ví dụ business nói:

> "Khi truyện hoàn thành."

Developer hỏi:

> "Hoàn thành nghĩa là gì?"

Có thể:

```text
Đã crawl hết chapter?
```

hoặc:

```text
Đã được admin đánh dấu hoàn thành?
```

hoặc:

```text
Tác giả đã kết thúc truyện?
```

Ba khái niệm hoàn toàn khác nhau.

Đây chính là lý do Event Storming rất hữu ích.

---

# 36. Domain Event giúp phát hiện ambiguity

Ví dụ business nói:

> "Chapter được cập nhật."

Hỏi:

> Updated cái gì?

Có thể:

```text
ChapterContentUpdated
ChapterTitleUpdated
ChapterMetadataUpdated
ChapterNumberChanged
```

Một từ mơ hồ:

```text
Updated
```

có thể che giấu nhiều business concept.

---

# 37. Event Storming và Ubiquitous Language

Hai buổi này liên kết trực tiếp:

```text
Ubiquitous Language
        ↓
Event names
        ↓
Commands
        ↓
Business Rules
        ↓
Aggregates
```

Nếu vocabulary không rõ:

```text
Event Storming
```

cũng sẽ rất khó.

---

# 38. Thực hành với hệ thống của chúng ta

Hãy lấy domain:

> App crawl và đọc truyện.

## Actor

```text
Admin
User
Scheduler
CrawlerWorker
```

## Commands

```text
StartCrawler
PauseCrawler
ResumeCrawler
AddSource
DiscoverChapter
DownloadChapter
MarkChapterAsRead
CreateBookmark
```

## Events

```text
CrawlerStarted
CrawlerPaused
CrawlerResumed
SourceAdded
ChapterDiscovered
ChapterDownloaded
ChapterSaved
ChapterRead
BookmarkCreated
```

---

# 39. Dựng timeline

```text
Admin
 ↓
StartCrawler
 ↓
CrawlerStarted
 ↓
CrawlerWorker
 ↓
DiscoverChapter
 ↓
ChapterDiscovered
 ↓
DownloadChapter
 ↓
ChapterDownloaded
 ↓
SaveChapter
 ↓
ChapterSaved
```

Sau đó:

```text
User
 ↓
MarkChapterAsRead
 ↓
ChapterRead
 ↓
ReadingProgressUpdated
```

---

# 40. Tìm Policy

Ví dụ:

```text
ChapterDiscovered
       ↓
[Download discovered chapter]
       ↓
DownloadChapter
```

```text
ChapterDownloaded
       ↓
[Persist downloaded chapter]
       ↓
SaveChapter
```

```text
CrawlerCompleted
       ↓
[Notify admin]
       ↓
CrawlerCompletionNotificationSent
```

Policy thường có dạng:

```text
WHEN event X happens
THEN perform command Y
```

---

# 41. Tìm Aggregate

Từ những event trên, thử gom:

### CrawlerJob

```text
CrawlerStarted
CrawlerPaused
CrawlerResumed
CrawlerCompleted
```

### Story

```text
ChapterAdded
ChapterRemoved
StoryPublished
StoryArchived
```

### ReadingProgress

```text
ChapterRead
ProgressUpdated
```

Ta bắt đầu có candidate aggregates.

---

# 42. Nhưng hãy đặt câu hỏi "Consistency Boundary"

Ví dụ:

```text
Story
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── ...
```

Nếu một Story có 10.000 chapter, có nên load tất cả vào một Aggregate không?

Không nhất thiết.

Đây là lúc chúng ta phải suy nghĩ về:

> **Aggregate boundary**

và:

> **Consistency boundary**

Đây sẽ là chủ đề rất quan trọng của các buổi sau.

---

# 43. Event Storming không nhằm tạo một sơ đồ hoàn hảo

Đây là điểm rất quan trọng.

Event Storming là công cụ **khám phá**.

Model ban đầu có thể:

```text
Story
```

sau đó thay đổi thành:

```text
StoryCatalog
Chapter
```

hoặc:

```text
CatalogEntry
```

Không sao.

DDD là quá trình:

```text
Discover
   ↓
Model
   ↓
Implement
   ↓
Learn
   ↓
Refactor Model
```

---

# 44. Anti-pattern: Event Storming thành CRUD Storming

Ví dụ:

```text
CreateStory
UpdateStory
DeleteStory
CreateChapter
UpdateChapter
DeleteChapter
```

Đây không phải business event tốt.

Chúng ta cần hỏi:

> Business thực sự quan tâm chuyện gì xảy ra?

Ví dụ:

```text
StoryPublished
ChapterDiscovered
CrawlerCompleted
ChapterRead
```

thường có nhiều business meaning hơn.

---

# 45. CRUD vs Domain Event

### CRUD thinking

```text
INSERT story
UPDATE story
DELETE story
```

### Domain thinking

```text
StoryCreated
StoryPublished
StoryArchived
```

Database nói:

> Row thay đổi.

Domain nói:

> Business event xảy ra.

Đây là một sự thay đổi tư duy rất lớn.

---

# 46. Bài tập 1 — Event Storming cơ bản

Với hệ thống:

> Admin quản lý crawler.

Hãy tìm:

### Actor

```text
?
```

### Commands

```text
?
```

### Events

```text
?
```

### Policies

```text
?
```

### Aggregate candidates

```text
?
```

---

# 47. Bài tập 2 — Phân biệt Command/Event

Cho các từ:

```text
StartCrawler
CrawlerStarted

PauseCrawler
CrawlerPaused

DownloadChapter
ChapterDownloaded

MarkChapterAsRead
ChapterRead
```

Hãy phân loại:

```text
Command
Event
```

và giải thích **tại sao**.

---

# 48. Bài tập 3 — Phát hiện Event sai

Các event sau có vấn đề gì?

```text
CrawlerProcessUpdated
DataChanged
SomethingHappened
DatabaseUpdated
ChapterActionPerformed
```

Hãy refactor chúng thành các Domain Event có meaning.

Ví dụ:

```text
DataChanged
```

có thể cần xác định:

```text
ChapterContentUpdated
```

hoặc:

```text
ChapterMetadataUpdated
```

---

# 49. Bài tập 4 — Vẽ Event Flow

Hãy vẽ:

```text
Admin
   ↓
StartCrawler
   ↓
CrawlerStarted
   ↓
?
   ↓
ChapterDiscovered
   ↓
?
   ↓
ChapterDownloaded
   ↓
?
   ↓
ChapterSaved
```

Điền các Command/Policy còn thiếu.

---

# 50. Bài tập 5 — Tìm Aggregate

Từ các Event:

```text
CrawlerStarted
CrawlerPaused
CrawlerResumed
CrawlerCompleted

ChapterAdded
ChapterRemoved
StoryPublished
StoryArchived

ChapterRead
ReadingProgressUpdated
BookmarkCreated
```

Hãy nhóm thành các Aggregate candidate.

---

# 51. Bài tập 6 — Event Storming thực chiến

Hãy viết business process của hệ thống:

> User mở một Story, chọn Chapter, bắt đầu đọc, đọc đến một vị trí, đánh dấu chapter đã đọc và tạo bookmark.

Từ đó tìm:

```text
Actor
Command
Event
Policy
Aggregate
```

---

# 52. Checklist Buổi 5

Bạn cần hiểu chắc:

```text
☑ Domain Event
☑ Command
☑ Actor
☑ Policy
☑ Event timeline
☑ Event vs Command
☑ Event Storming
☑ Aggregate candidate
☑ Business process
☑ Domain Event ≠ Event Sourcing
```

Và đặc biệt phải nhớ:

> **Command là điều ai đó yêu cầu hệ thống làm.**

> **Event là điều domain xác nhận đã xảy ra.**

---

# 53. Bức tranh DDD hiện tại

Sau 5 buổi:

```text
                    DDD
                     │
          ┌──────────┴──────────┐
          │                     │
    Strategic DDD         Tactical DDD
          │
     ┌────┴────┐
     │         │
  Domain   Subdomain
     │
     ↓
Ubiquitous Language
     │
     ↓
 Event Storming
     │
     ↓
Domain Model
```

Chúng ta đã bắt đầu chuyển từ **"hiểu business"** sang **"thiết kế model"**.

---

## Buổi 6 — Entity Deep Dive

Buổi tiếp theo chúng ta sẽ đi rất sâu vào:

```text
Entity
 │
 ├── Identity
 ├── Equality
 ├── Lifecycle
 ├── Mutable State
 ├── Behavior
 ├── Identity vs Attribute
 ├── Entity vs DTO
 ├── Entity vs ORM Model
 └── Entity vs Database Row
```

Đặc biệt, chúng ta sẽ giải quyết một câu hỏi rất quan trọng:

> **Tại sao hai object có toàn bộ dữ liệu giống hệt nhau nhưng vẫn có thể là hai Entity khác nhau?**

Sau đó chúng ta sẽ tự xây `Story`, `Chapter` và `CrawlerJob` bằng Python theo đúng tư duy DDD.
