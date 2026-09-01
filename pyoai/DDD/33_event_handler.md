# DDD Deep Dive — Buổi 33

# Event Handler

Ở Buổi 32, ta đã xây:

```text
Domain Event
      ↓
Event Dispatcher
      ↓
Event Handler
```

Hôm nay tập trung hoàn toàn vào **Event Handler**.

Đây là nơi Domain Event biến thành **reaction của hệ thống**.

---

# 1. Event Handler là gì?

Event Handler là thành phần nhận một Domain Event và thực hiện một hành động phản ứng với event đó.

Ví dụ:

```text
ChapterAdded
      ↓
SearchIndexHandler
```

Handler có thể:

```text
ChapterAdded
    ↓
Update search index
```

hoặc:

```text
ChapterAdded
    ↓
Update statistics
```

hoặc:

```text
ChapterAdded
    ↓
Send notification
```

---

# 2. Event Handler không phải Domain Service

Đây là distinction quan trọng.

### Domain Service

Chứa **business logic**:

```text
"Story có được phép publish hay không?"
```

### Event Handler

Phản ứng với một **business fact**:

```text
"Story đã được publish."
→ gửi notification
```

Ví dụ:

```text
Domain Service
    ↓
quyết định

Event Handler
    ↓
phản ứng
```

---

# 3. Event Handler không quyết định business rule chính

Ví dụ:

```python
story.add_chapter(chapter)
```

Aggregate quyết định:

```text
Chapter đã tồn tại?
Chapter number hợp lệ?
Story có trạng thái cho phép thêm chapter?
```

Handler không nên quyết định những invariant này.

```text
Story
 ↓
Business decision
 ↓
ChapterAdded
 ↓
Handler
```

---

# 4. Ví dụ hệ thống đọc truyện

Giả sử:

```text
ChapterAdded
```

Có 3 handler:

```text
                 ChapterAdded
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Search      Statistics  Notification
```

Mỗi handler có một responsibility riêng.

---

# 5. SearchIndexHandler

```python
class SearchIndexHandler:

    def __init__(self, search_index):
        self._search_index = search_index

    def handle(self, event: ChapterAdded) -> None:
        self._search_index.index_chapter(
            story_id=event.story_id,
            chapter_id=event.chapter_id,
        )
```

Handler không biết:

```text
SQLite
Aggregate
Use Case
CLI
PySide6
```

Nó chỉ cần:

```text
ChapterAdded
+
SearchIndex
```

---

# 6. StatisticsHandler

```python
class StatisticsHandler:

    def __init__(self, statistics):
        self._statistics = statistics

    def handle(self, event: ChapterAdded) -> None:
        self._statistics.chapter_added(
            story_id=event.story_id,
        )
```

---

# 7. NotificationHandler

```python
class NotificationHandler:

    def __init__(self, notifier):
        self._notifier = notifier

    def handle(self, event: ChapterAdded) -> None:
        self._notifier.notify_new_chapter(
            story_id=event.story_id,
            chapter_number=event.chapter_number,
        )
```

---

# 8. Một Event → nhiều Handler

Đây là mô hình phổ biến:

```text
ChapterAdded
      │
      ├── SearchIndexHandler
      │
      ├── StatisticsHandler
      │
      └── NotificationHandler
```

Dispatcher:

```python
dispatcher.register(
    ChapterAdded,
    SearchIndexHandler(search_index),
)

dispatcher.register(
    ChapterAdded,
    StatisticsHandler(statistics),
)

dispatcher.register(
    ChapterAdded,
    NotificationHandler(notifier),
)
```

---

# 9. Handler nên có một responsibility

Không nên:

```python
class ChapterAddedHandler:

    def handle(self, event):

        update_search()

        update_statistics()

        send_notification()

        update_cache()

        send_email()
```

Handler này đang làm quá nhiều việc.

Tốt hơn:

```text
ChapterAdded
   │
   ├── SearchIndexHandler
   ├── StatisticsHandler
   ├── NotificationHandler
   └── CacheHandler
```

Mỗi handler một responsibility.

Đây cũng chính là **SRP**.

---

# 10. Handler và Dependency Injection

Một Handler thường có dependency.

Ví dụ:

```python
class NotificationHandler:

    def __init__(self, notifier):
        self._notifier = notifier
```

Không nên:

```python
class NotificationHandler:

    def __init__(self):
        self._notifier = EmailNotifier()
```

Vì lúc đó Handler tự quyết định infrastructure implementation.

---

# 11. Ports & Adapters

Thiết kế tốt:

```text
Event Handler
      ↓
Notifier Interface
      ↓
EmailNotifier
```

Ví dụ:

```python
from typing import Protocol


class Notifier(Protocol):

    def notify_new_chapter(
        self,
        story_id,
        chapter_number,
    ) -> None:
        ...
```

Infrastructure:

```python
class EmailNotifier:

    def notify_new_chapter(
        self,
        story_id,
        chapter_number,
    ):
        ...
```

Handler:

```python
class NotificationHandler:

    def __init__(self, notifier: Notifier):
        self._notifier = notifier

    def handle(self, event: ChapterAdded):
        self._notifier.notify_new_chapter(
            event.story_id,
            event.chapter_number,
        )
```

---

# 12. Handler nằm ở đâu?

Một cách tổ chức:

```text
src/
└── story_app/

    ├── domain/
    │   └── story/
    │       ├── entities.py
    │       └── events.py
    │
    ├── application/
    │   └── event_handlers/
    │       ├── search.py
    │       ├── statistics.py
    │       └── notification.py
    │
    └── infrastructure/
        ├── search/
        └── notification/
```

Điểm quan trọng:

> **Domain Event thuộc Domain. Handler thường thuộc Application Layer.**

---

# 13. Tại sao Handler thường thuộc Application?

Vì Handler thường **orchestrate interaction với bên ngoài**.

Ví dụ:

```text
ChapterAdded
     ↓
NotificationHandler
     ↓
Notifier Port
     ↓
Email / Push / Telegram
```

Domain không cần biết Telegram tồn tại.

---

# 14. Handler có thể gọi Repository

Ví dụ:

```python
class NotificationHandler:

    def __init__(
        self,
        stories,
        notifier,
    ):
        self._stories = stories
        self._notifier = notifier

    def handle(self, event):

        story = self._stories.get(
            event.story_id
        )

        self._notifier.notify(
            story_id=story.id,
            title=story.title,
        )
```

Điều này có thể hợp lý.

Nhưng cần cẩn thận:

```text
Event Handler
    ↓
Repository
    ↓
Database
```

có thể tạo thêm transaction boundary.

Ta sẽ quay lại vấn đề này ở **Buổi 34**.

---

# 15. Handler có nên sửa Aggregate?

Có thể, nhưng phải cực kỳ cẩn thận.

Ví dụ:

```text
ChapterAdded
    ↓
Update Story Statistics
```

Có thể:

```python
story.update_statistics(...)
```

Nhưng nếu Handler làm:

```text
Event
 ↓
Load Aggregate
 ↓
Modify Aggregate
 ↓
Save Aggregate
 ↓
Generate another Event
 ↓
Handler
 ↓
...
```

ta có nguy cơ tạo **event chain rất phức tạp**.

---

# 16. Event Chain

Ví dụ:

```text
ChapterAdded
     ↓
UpdateStatistics
     ↓
StatisticsUpdated
     ↓
UpdateDashboard
     ↓
DashboardUpdated
```

Có thể hợp lệ.

Nhưng nếu không kiểm soát:

```text
Event A
 ↓
Event B
 ↓
Event C
 ↓
Event A
```

→ vòng lặp.

---

# 17. Event Handler không nên gọi ngược Event một cách tùy tiện

Ví dụ nguy hiểm:

```text
ChapterAdded
    ↓
Handler
    ↓
Story.update()
    ↓
StoryUpdated
    ↓
Handler
    ↓
Story.add_chapter()
    ↓
ChapterAdded
```

Ta có:

```text
A → B → A → B → ...
```

Vì vậy event flow phải được thiết kế rõ ràng.

---

# 18. Handler có thể phát Event mới?

**Có thể.**

Ví dụ:

```text
CrawlerCompleted
       ↓
CrawlerCompletedHandler
       ↓
PublishStory
       ↓
StoryPublished
```

Nhưng đây là một workflow có chủ ý.

Không nên để event chain phát sinh ngẫu nhiên.

---

# 19. Handler synchronous

Event Dispatcher đơn giản:

```python
for handler in handlers:
    handler.handle(event)
```

Có nghĩa:

```text
ChapterAdded
   ↓
SearchHandler
   ↓
xong
   ↓
StatisticsHandler
   ↓
xong
   ↓
NotificationHandler
```

Đây là **synchronous dispatching**.

---

# 20. Vấn đề của synchronous handler

Giả sử:

```text
NotificationHandler
```

gọi API:

```text
Telegram
```

API mất:

```text
5 giây
```

thì:

```text
ChapterAdded
 ↓
Search        10ms
 ↓
Statistics    5ms
 ↓
Notification  5000ms
```

Toàn bộ flow bị chậm.

---

# 21. Async handler

Có thể dùng:

```python
async def handle(
    self,
    event: ChapterAdded,
):
    await self._notifier.notify(...)
```

Dispatcher trở thành:

```python
async def dispatch(self, event):

    for handler in handlers:
        await handler.handle(event)
```

Nhưng đây mới chỉ là **async**, chưa phải background processing.

---

# 22. Async ≠ Background Worker

Đây là distinction rất quan trọng.

```text
async handler
```

vẫn có thể chạy trong cùng process:

```text
Python Process
   ↓
Event Bus
   ↓
async handler
```

Trong khi Worker:

```text
Process A
   ↓
Queue
   ↓
Process B
```

Worker phù hợp với:

```text
email
notification
search indexing
heavy processing
retry
```

---

# 23. Khi nào Handler nên chạy background?

Ví dụ:

```text
ChapterAdded
```

Search indexing:

```text
có thể background
```

Notification:

```text
có thể background
```

Statistics:

```text
tùy trường hợp
```

Nhưng invariant của Aggregate:

```text
Story
 ↓
ChapterAdded
```

phải hoàn tất trong transaction chính.

---

# 24. Handler và Transaction

Đây là vấn đề cực kỳ quan trọng.

Giả sử:

```text
BEGIN
 ↓
Story.add_chapter()
 ↓
ChapterAdded
 ↓
SearchHandler
 ↓
COMMIT
```

Search đã update nhưng DB commit có thể fail.

Không tốt.

Ngược lại:

```text
BEGIN
 ↓
Story.add_chapter()
 ↓
COMMIT
 ↓
SearchHandler
```

Nếu process crash sau commit:

```text
Database = updated
Search = not updated
```

Event có thể bị mất.

Đây chính là vấn đề của:

> **Buổi 34 — Domain Event + Transaction**

---

# 25. Handler phải chịu được retry

Giả sử:

```text
ChapterAdded
```

được gửi:

```text
lần 1 → handler fail
lần 2 → thành công
```

Đây là bình thường trong hệ thống production.

Handler cần có khả năng xử lý:

```text
same event
```

nhiều lần một cách an toàn.

---

# 26. Idempotency

Ví dụ:

```python
class SearchIndexHandler:

    def handle(self, event):

        self.search.index_chapter(
            event.chapter_id
        )
```

Nếu index operation là upsert:

```text
chapter_id = 123
```

thì chạy 2 lần:

```text
index(123)
index(123)
```

vẫn an toàn.

Đây là một dạng idempotency.

---

# 27. Notification khó hơn

Ví dụ:

```text
ChapterAdded
 ↓
SendEmail
```

Nếu chạy hai lần:

```text
Email
Email
```

User nhận 2 email.

Ta có thể cần:

```text
processed_events
```

Ví dụ:

```text
event_id
---------
abc123
```

Handler kiểm tra:

```text
abc123 đã xử lý?
    │
    ├── yes → skip
    └── no  → process
```

---

# 28. Idempotency Store

Một bảng đơn giản:

```sql
CREATE TABLE processed_events (
    event_id TEXT PRIMARY KEY,
    processed_at TEXT NOT NULL
);
```

Handler:

```text
event
 ↓
check event_id
 ↓
đã tồn tại?
 ├── yes → return
 └── no
      ↓
   process
      ↓
   record event_id
```

Nhưng transaction của phần này phải được thiết kế cẩn thận.

---

# 29. Error Handling

Giả sử:

```text
ChapterAdded
```

và:

```text
SearchHandler      ✅
StatisticsHandler  ❌
NotificationHandler ?
```

Có nhiều policy.

### Policy 1 — Stop

```text
Search      ✅
Statistics  ❌
Notification không chạy
```

### Policy 2 — Continue

```text
Search       ✅
Statistics   ❌
Notification ✅
```

### Policy 3 — Retry

```text
Statistics
   ↓
retry
   ↓
retry
   ↓
dead letter
```

Production system thường cần policy rõ ràng.

---

# 30. Đừng catch Exception rồi bỏ qua

Sai:

```python
def handle(event):

    try:
        ...
    except Exception:
        pass
```

❌

Bạn vừa biến:

```text
failure
```

thành:

```text
invisible failure
```

Tốt hơn:

```python
try:
    ...
except Exception:
    logger.exception(
        "Handler failed"
    )
    raise
```

Sau đó dispatcher/worker quyết định retry.

---

# 31. Handler phải observable

Production Handler nên có:

```text
logging
metrics
tracing
event_id
```

Ví dụ log:

```text
event=ChapterAdded
event_id=abc123
handler=SearchIndexHandler
status=success
```

Nếu fail:

```text
event=ChapterAdded
event_id=abc123
handler=SearchIndexHandler
status=failed
```

Điều này cực kỳ hữu ích khi debug crawler.

---

# 32. Ví dụ thực tế với crawler

Giả sử crawler hoàn thành:

```text
CrawlerCompleted
```

Handler 1:

```text
UpdateCrawlerStatistics
```

Handler 2:

```text
NotifyCrawlerCompleted
```

Handler 3:

```text
ScheduleNextCrawl
```

Handler 4:

```text
UpdateDashboard
```

Flow:

```text
Crawler
   ↓
CrawlerCompleted
   ↓
Event Bus
   │
   ├── Statistics
   ├── Notification
   ├── Scheduler
   └── Dashboard
```

Crawler không cần biết các thành phần đó.

---

# 33. Đây chính là Loose Coupling

Không có Event:

```text
Crawler
 ├── Dashboard
 ├── Notification
 ├── Statistics
 ├── Scheduler
 └── ...
```

Crawler biết quá nhiều.

Có Event:

```text
Crawler
   ↓
CrawlerCompleted
```

Các consumer:

```text
CrawlerCompleted
 ├── DashboardHandler
 ├── NotificationHandler
 ├── StatisticsHandler
 └── SchedulerHandler
```

Crawler chỉ cần biết Domain Event.

---

# 34. Open/Closed Principle

Giả sử hiện tại:

```text
ChapterAdded
 ├── Search
 └── Statistics
```

Sau này muốn thêm:

```text
Recommendation
```

Ta chỉ thêm:

```text
RecommendationHandler
```

và register:

```python
dispatcher.register(
    ChapterAdded,
    RecommendationHandler(...),
)
```

Không cần sửa:

```text
Story
ChapterAdded
SearchHandler
StatisticsHandler
```

Đây là lợi ích lớn của Event-driven design.

---

# 35. Nhưng đừng lạm dụng Event

Sai lầm phổ biến:

```text
mọi method
    ↓
Event
```

Ví dụ:

```text
StoryTitleChanged
StoryDescriptionChanged
StoryAuthorChanged
StoryUpdated
StoryFieldChanged
StorySomethingChanged
```

Nếu không có consumer thực sự cần chúng, event chỉ tạo complexity.

Nguyên tắc:

> **Event phải có business meaning hoặc architectural value.**

---

# 36. Một Handler không nhất thiết phải tương ứng 1 Event

Có thể:

```text
Handler
   ← Event A
   ← Event B
   ← Event C
```

Ví dụ:

```python
class SearchIndexHandler:

    def handle_story_created(self, event):
        ...

    def handle_chapter_added(self, event):
        ...

    def handle_story_title_changed(self, event):
        ...
```

Nhưng trong hệ thống lớn, thường thích tách rõ handler theo event để dễ test và monitoring.

---

# 37. Một pattern tốt

```text
One Event
    ↓
One Handler class
    ↓
One responsibility
```

Ví dụ:

```text
ChapterAdded
    ↓
IndexChapterHandler

ChapterAdded
    ↓
UpdateStatisticsHandler

ChapterAdded
    ↓
NotifySubscribersHandler
```

Không phải quy tắc bắt buộc, nhưng rất dễ quản lý.

---

# 38. Test Handler

Handler rất dễ unit test.

Ví dụ:

```python
def test_chapter_added_updates_search():

    search = FakeSearchIndex()

    handler = SearchIndexHandler(search)

    event = ChapterAdded(
        event_id=uuid4(),
        occurred_at=datetime.now(),
        story_id=story_id,
        chapter_id=chapter_id,
        chapter_number=10,
    )

    handler.handle(event)

    assert search.indexed == [
        chapter_id
    ]
```

Không cần:

```text
SQLite
HTTP
Redis
real search engine
```

---

# 39. Fake Dependency

Ví dụ:

```python
class FakeNotifier:

    def __init__(self):
        self.messages = []

    def notify_new_chapter(
        self,
        story_id,
        chapter_number,
    ):
        self.messages.append(
            (story_id, chapter_number)
        )
```

Test:

```python
def test_notification_handler():

    notifier = FakeNotifier()

    handler = NotificationHandler(
        notifier
    )

    handler.handle(event)

    assert notifier.messages == [
        (story_id, 10)
    ]
```

Đây là một trong những lợi ích lớn nhất của Dependency Inversion.

---

# 40. Handler Test ≠ Integration Test

Unit test:

```text
Handler
 ↓
Fake dependency
```

Integration test:

```text
Handler
 ↓
Real repository
 ↓
SQLite
```

End-to-end:

```text
CLI
 ↓
Use Case
 ↓
Aggregate
 ↓
UoW
 ↓
Event
 ↓
Dispatcher
 ↓
Handler
 ↓
Infrastructure
```

Nên có nhiều tầng test.

---

# 41. Handler có thể gọi Use Case không?

Thường:

```text
Handler
   ↓
Use Case
```

có thể tạo circular/complex flow.

Ví dụ:

```text
Event A
 ↓
Handler
 ↓
Use Case
 ↓
Aggregate
 ↓
Event B
```

Điều này không phải luôn sai, nhưng cần có chủ đích.

Thông thường Handler nên orchestration trực tiếp qua application ports/services khi logic đơn giản.

---

# 42. Handler vs Application Service

### Application Service

Được gọi bởi một request/command:

```text
User
 ↓
Command
 ↓
Use Case
```

### Event Handler

Được kích hoạt bởi Event:

```text
Event
 ↓
Handler
```

Cả hai đều có thể nằm Application Layer.

---

# 43. So sánh

| Thành phần             | Trigger             | Mục đích          |
| ---------------------- | ------------------- | ----------------- |
| Entity                 | Method call         | Business behavior |
| Domain Service         | Domain operation    | Business logic    |
| Application Service    | Command/request     | Orchestration     |
| Event Handler          | Domain Event        | Reaction          |
| Repository             | Persistence request | Load/save         |
| Infrastructure Service | External operation  | Technical concern |

Đây là bảng rất đáng nhớ.

---

# 44. Kiến trúc hoàn chỉnh hiện tại

Ta đã đi từ:

```text
CLI
 ↓
Use Case
 ↓
Aggregate
 ↓
Repository
 ↓
Unit of Work
```

và thêm:

```text
Aggregate
 ↓
Domain Event
 ↓
Event Dispatcher
 ↓
Event Handler
 ↓
Infrastructure
```

Tổng thể:

```text
                     ┌───────────────┐
                     │      CLI      │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │    Use Case   │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │   Aggregate   │
                     └───────┬───────┘
                             │
                    records Event
                             │
                             ▼
                     ┌───────────────┐
                     │ Domain Event  │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │ Event Bus     │
                     └───────┬───────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          Search          Stats       Notification
          Handler         Handler        Handler
              │              │              │
              ▼              ▼              ▼
       Infrastructure   Infrastructure  Infrastructure
```

---

# 45. Ba nguyên tắc quan trọng nhất của Buổi 33

### Nguyên tắc 1

**Handler phản ứng với Event, không quyết định invariant của Aggregate.**

```text
Aggregate
→ business decision

Handler
→ reaction
```

### Nguyên tắc 2

**Handler nhận dependency từ bên ngoài.**

```text
Handler
 ↓
Port
 ↓
Infrastructure
```

Không tự tạo infrastructure.

### Nguyên tắc 3

**Handler phải được thiết kế để có thể retry/idempotent khi hệ thống cần.**

Đặc biệt quan trọng khi chuyển sang:

```text
Outbox
 ↓
Worker
 ↓
Redis/RQ/Celery/etc.
```

---

# 46. Bài tập Buổi 33

Với hệ thống đọc truyện, hãy thiết kế:

```text
ChapterAdded
```

và 3 Handler:

```text
1. SearchIndexHandler
2. StatisticsHandler
3. NotificationHandler
```

Kiến trúc:

```text
ChapterAdded
      │
      ├── SearchIndexHandler
      │
      ├── StatisticsHandler
      │
      └── NotificationHandler
```

Mỗi Handler phải:

* nhận dependency qua constructor;
* không biết SQLite cụ thể;
* không tạo infrastructure object bên trong;
* chỉ có một responsibility;
* có thể unit test bằng Fake dependency.

---

# 47. Bài tập nâng cao

Thiết kế:

```text
CrawlerCompleted
```

với:

```text
CrawlerCompleted
       │
       ├── UpdateCrawlerStatisticsHandler
       ├── NotifyCrawlerCompletedHandler
       ├── UpdateDashboardHandler
       └── ScheduleNextCrawlHandler
```

Sau đó suy nghĩ:

> Nếu `NotifyCrawlerCompletedHandler` gọi API bên ngoài và API thất bại, ta có muốn rollback transaction tạo `CrawlerCompleted` không?

**Đây là câu hỏi rất quan trọng.**

Trong nhiều kiến trúc production, câu trả lời là **không đơn giản như "có" hoặc "không"**. Nó phụ thuộc vào việc event là **domain state change** hay **side effect**, thời điểm dispatch, retry và transaction boundary.

Đó chính là nội dung của **Buổi 34 — Domain Event + Transaction**:

```text
Aggregate
    ↓
Domain Event
    ↓
Before Commit?
    │
    ├── ❌ External side effect?
    │
    ▼
Commit
    ↓
After Commit?
    │
    └── ❌ Process crash → Event mất?
```

Sau đó **Buổi 35 — Outbox Pattern** sẽ giải quyết bài toán:

```text
Aggregate
    ↓
Domain Event
    ↓
Outbox Table
    ↓
Worker
    ↓
Handler
    ↓
External System
```

Đây là bước đưa Domain Event từ **in-process architecture** sang **production-style reliable event processing**.
