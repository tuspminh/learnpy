# DDD Deep Dive — Buổi 34

# Domain Event + Transaction

Buổi này cực kỳ quan trọng vì nó trả lời câu hỏi:

> **Khi nào Domain Event được dispatch?**

Ở Buổi 33 ta có:

```text
ChapterAdded
      ↓
Event Handler
      ↓
Search
Notification
Statistics
```

Nhưng nếu Database transaction chưa commit thì sao?

Đây chính là nơi bắt đầu xuất hiện các vấn đề **consistency** trong hệ thống production.

---

# 1. Vấn đề cốt lõi

Giả sử Use Case:

```python
story.add_chapter(chapter)
```

Aggregate tạo:

```text
ChapterAdded
```

Sau đó ta cần:

```text
Database
Search Index
Notification
Statistics
```

Tất cả phải phối hợp với nhau.

Nhưng:

> **Database transaction và Event Handler không mặc nhiên nằm trong cùng một transaction.**

Ví dụ:

```text
SQLite Transaction
       │
       ├── Story
       └── Chapter
       
Event Handler
       │
       ├── Search
       └── Notification
```

SQLite có thể rollback, nhưng Elasticsearch/Email/Telegram không tự rollback theo.

---

# 2. Event timing

Có ba cách tư duy phổ biến:

```text
1. Dispatch trước commit

2. Dispatch sau commit

3. Ghi Event vào Outbox trong cùng transaction
```

Cách 3 là hướng production mà chúng ta sẽ đi tới ở Buổi 35.

---

# 3. Cách 1 — Before Commit

Flow:

```text
BEGIN
  ↓
Aggregate
  ↓
ChapterAdded
  ↓
Dispatch
  ↓
Handlers
  ↓
COMMIT
```

Ví dụ:

```python
with uow:

    story.add_chapter(chapter)

    dispatcher.dispatch(
        event
    )

    uow.commit()
```

---

# 4. Ưu điểm Before Commit

Nếu Handler chỉ thực hiện **domain-local operation** thì có thể hữu ích.

Ví dụ:

```text
Aggregate
 ↓
Domain Event
 ↓
In-memory handler
 ↓
Update một object trong cùng process
```

Tuy nhiên với external system thì rất nguy hiểm.

---

# 5. Vấn đề Before Commit

Giả sử:

```text
BEGIN
 ↓
Story.add_chapter()
 ↓
ChapterAdded
 ↓
NotificationHandler
 ↓
Send notification ✅
 ↓
COMMIT ❌
```

Database rollback.

Nhưng notification đã gửi.

Kết quả:

```text
Database:
Chapter 10 không tồn tại

User:
"Chapter 10 đã được thêm!"
```

❌ Inconsistent.

---

# 6. Ví dụ thực tế

```text
SQLite
   ↓
ROLLBACK

Email
   ↓
SENT
```

Không thể:

```python
email.rollback()
```

Email server không nằm trong SQLite transaction.

---

# 7. Before Commit không phải lúc nào cũng sai

Nếu Handler chỉ làm việc hoàn toàn trong cùng transaction boundary:

```text
SQLite
 ↓
Handler
 ↓
SQLite
```

thì có thể thiết kế transaction chung.

Ví dụ:

```text
ChapterAdded
 ↓
Update local projection
 ↓
COMMIT
```

Nhưng khi Handler gọi:

```text
HTTP
Redis
Email
Search Engine
Telegram
```

thì vấn đề trở nên nghiêm trọng.

---

# 8. Cách 2 — After Commit

Cách trực quan hơn:

```text
BEGIN
  ↓
Aggregate
  ↓
Save
  ↓
COMMIT
  ↓
Dispatch Event
  ↓
Handlers
```

Code:

```python
with uow:

    story.add_chapter(chapter)

    uow.stories.save(story)

    uow.commit()

dispatcher.dispatch(event)
```

---

# 9. Ưu điểm After Commit

Bây giờ:

```text
COMMIT
  ↓
Database chắc chắn đã thay đổi
  ↓
Event Handler
```

Không còn vấn đề:

```text
notification sent
+
database rollback
```

từ trường hợp dispatch trước commit.

---

# 10. Nhưng After Commit có một vấn đề lớn

Giả sử:

```text
COMMIT
   ↓
Process crash
   ↓
dispatcher.dispatch()
```

Process chết trước khi dispatch.

Kết quả:

```text
Database:
Chapter 10 tồn tại ✅

Event:
ChapterAdded mất ❌
```

Ta có:

```text
Database = correct
Side effects = missing
```

Đây là **lost event problem**.

---

# 11. Đây là race window

Khoảng thời gian:

```text
COMMIT
  │
  │  ← process có thể crash ở đây
  │
DISPATCH
```

được gọi là một dạng **failure window**.

Ví dụ:

```text
t1: database commit
t2: process crash
t3: không bao giờ dispatch
```

Không có retry nào giúp được vì event đã biến mất khỏi memory.

---

# 12. So sánh

| Cách          | Ưu điểm                              | Vấn đề                                 |
| ------------- | ------------------------------------ | -------------------------------------- |
| Before commit | Event không bị mất trước transaction | Side effect có thể xảy ra rồi rollback |
| After commit  | DB chắc chắn commit trước handler    | Process crash → event mất              |
| Outbox        | Event nằm cùng transaction           | Cần worker/dispatcher riêng            |

Đây là lý do **Outbox Pattern** tồn tại.

---

# 13. Transactional Consistency

Ta cần đảm bảo:

```text
Business state
+
Event record
```

phải được commit **atomically**.

Mục tiêu:

```text
BEGIN
   │
   ├── Save Story
   ├── Save Chapter
   └── Save Domain Event
           ↓
        COMMIT
```

Hoặc:

```text
ROLLBACK
```

Nếu commit thành công:

```text
Story      ✅
Chapter    ✅
Event      ✅
```

Nếu rollback:

```text
Story      ❌
Chapter    ❌
Event      ❌
```

Đây là điểm mấu chốt của Outbox.

---

# 14. Domain Event vs Event Record

Đây là distinction rất quan trọng.

### Domain Event

Object trong Domain:

```python
ChapterAdded(
    event_id=...,
    story_id=...,
    chapter_id=...,
)
```

### Outbox Event

Persistence representation:

```text
outbox
--------------------------------
id
event_type
payload
occurred_at
processed_at
```

Ta không nhất thiết serialize Domain Event trực tiếp theo một cách duy nhất.

---

# 15. Outbox là gì?

Outbox là một bảng trong database dùng để lưu các Event cần được xử lý.

Ví dụ:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    processed_at TEXT
);
```

---

# 16. Flow

Khi:

```python
story.add_chapter(chapter)
```

Aggregate tạo:

```text
ChapterAdded
```

Application/UoW đưa Event vào Outbox:

```text
SQLite Transaction
       │
       ├── stories
       ├── chapters
       └── outbox
             │
             └── ChapterAdded
```

Sau đó:

```text
COMMIT
```

---

# 17. Nếu Commit thành công

Database chứa:

```text
stories
chapters
outbox
```

Ví dụ:

```text
stories
---------
story-1

chapters
---------
chapter-10

outbox
---------
event-abc | ChapterAdded | ...
```

Process có crash ngay sau đó cũng không sao.

Event vẫn còn trong database.

---

# 18. Worker xử lý Outbox

Worker chạy:

```text
Outbox
   ↓
find pending events
   ↓
publish
   ↓
Handler
```

Ví dụ:

```text
outbox
   ↓
ChapterAdded
   ↓
Event Dispatcher
   ↓
SearchIndexHandler
   ↓
NotificationHandler
```

---

# 19. Đây chính là Architecture

```text
Aggregate
    ↓
Domain Event
    ↓
Outbox
    ↓
Database COMMIT
    ↓
Worker
    ↓
Event Dispatcher
    ↓
Handlers
    ↓
External Systems
```

Đây là kiến trúc chúng ta sẽ implement ở **Buổi 35**.

---

# 20. Vì sao Outbox giải quyết Lost Event?

Không có Outbox:

```text
COMMIT
 ↓
💥 crash
 ↓
EVENT LOST
```

Có Outbox:

```text
BEGIN
 ↓
Save aggregate
 ↓
Save event to outbox
 ↓
COMMIT
 ↓
💥 crash
```

Sau khi process khởi động lại:

```text
outbox
 ↓
pending event
 ↓
worker
 ↓
dispatch
```

Event không mất.

---

# 21. Atomicity

Giả sử:

```text
Story
Chapter
Outbox Event
```

đều nằm trong SQLite.

Ta có:

```sql
BEGIN;

INSERT INTO stories ...;

INSERT INTO chapters ...;

INSERT INTO outbox ...;

COMMIT;
```

SQLite đảm bảo transaction:

```text
ALL
```

hoặc:

```text
NOTHING
```

Nếu lỗi:

```sql
ROLLBACK;
```

thì cả ba thay đổi đều rollback.

---

# 22. Một ví dụ cụ thể

Use Case:

```python
class AddChapterUseCase:

    def execute(self, command):

        with self.uow:

            story = self.uow.stories.get(
                command.story_id
            )

            chapter = Chapter.create(
                ...
            )

            story.add_chapter(chapter)

            self.uow.stories.save(story)

            for event in story.collect_events():
                self.uow.outbox.add(event)

            self.uow.commit()
```

Flow:

```text
story.add_chapter()
       ↓
ChapterAdded
       ↓
uow.outbox.add()
       ↓
COMMIT
```

---

# 23. Điểm rất quan trọng

Ở đây:

```python
uow.outbox.add(event)
```

**chưa dispatch event**.

Nó chỉ:

```text
Domain Event
    ↓
Persistence
```

Sau khi transaction commit:

```text
Outbox Worker
    ↓
Dispatch
```

---

# 24. Tại sao không gọi Handler trong `uow`?

Không nên:

```python
with uow:

    story.add_chapter()

    dispatcher.dispatch(event)

    uow.commit()
```

nếu handler thực hiện external side effect.

Ví dụ:

```text
SQLite transaction
       ↓
HTTP API
       ↓
Email
       ↓
Redis
```

Bạn đang cố ép những hệ thống khác nhau vào một transaction.

Đó là kiến trúc khó kiểm soát.

---

# 25. Distributed Transaction

Giả sử:

```text
SQLite
+
Elasticsearch
+
Email
+
Redis
```

Bạn không thể dễ dàng có:

```text
BEGIN ALL
```

rồi:

```text
COMMIT ALL
```

Một distributed transaction phức tạp hơn rất nhiều.

DDD + Outbox thường chọn cách:

```text
Local Transaction
       ↓
Outbox
       ↓
Asynchronous processing
```

---

# 26. Eventual Consistency

Khi dùng Outbox:

```text
t=0
Database commit

t=1
Worker đọc event

t=2
Search update

t=3
Notification
```

Trong khoảng thời gian ngắn:

```text
Database = updated
Search = old
```

Sau đó:

```text
Database = updated
Search = updated
```

Đây là:

> **Eventual Consistency**

---

# 27. Đây không nhất thiết là bug

Ví dụ hệ thống đọc truyện:

```text
Chapter được lưu
```

Search index cập nhật sau 1–2 giây.

Thông thường hoàn toàn chấp nhận được.

Không nhất thiết phải:

```text
Chapter INSERT
 ↓
Search index
 ↓
Notification
 ↓
Statistics
 ↓
COMMIT
```

tất cả trong một transaction.

---

# 28. Strong vs Eventual Consistency

### Strong consistency

```text
Transaction
 ↓
mọi thứ nhất quán ngay lập tức
```

### Eventual consistency

```text
Transaction
 ↓
state chính xác
 ↓
event processing
 ↓
eventually mọi projection/side effect cập nhật
```

DDD Event-driven architecture thường chấp nhận eventual consistency ở các boundary phù hợp.

---

# 29. Domain Invariant vẫn phải Strongly Consistent

Đây là điểm cực kỳ quan trọng.

Ví dụ:

```text
Story
```

Invariant:

```text
Không được có 2 chapter cùng chapter_number.
```

Điều này phải được bảo vệ ngay trong transaction/aggregate/database phù hợp.

Không thể nói:

```text
"Eventually chapter number sẽ hợp lệ."
```

❌

Business invariant quan trọng phải được đảm bảo ở consistency boundary thích hợp.

---

# 30. Side Effect có thể Eventually Consistent

Ví dụ:

```text
ChapterAdded
 ↓
Search index
```

Có thể:

```text
delay 500ms
```

hoặc:

```text
delay 5s
```

tùy yêu cầu.

Tương tự:

```text
Notification
Statistics
Recommendation
```

thường có thể xử lý asynchronous.

---

# 31. Transaction Boundary và Aggregate

Ở Buổi 16–20 ta đã học:

```text
Aggregate
    ↓
Consistency Boundary
    ↓
Transaction Boundary
```

Giờ kết nối với Event:

```text
Aggregate
   │
   ├── state changes
   │
   └── Domain Events
          ↓
       Outbox
```

Aggregate quyết định:

```text
business state
```

Transaction đảm bảo:

```text
state + event record
```

được lưu atomically.

---

# 32. UoW trở nên rất quan trọng

Trước đây:

```text
UnitOfWork
 ├── StoryRepository
 └── ChapterRepository
```

Bây giờ:

```text
UnitOfWork
 ├── StoryRepository
 ├── ChapterRepository
 └── OutboxRepository
```

Ví dụ:

```python
class UnitOfWork(ABC):

    stories: StoryRepository
    chapters: ChapterRepository
    outbox: OutboxRepository

    def commit(self) -> None:
        ...
```

---

# 33. SQLite Transaction

Ví dụ đơn giản:

```python
conn.execute("BEGIN")

try:
    # save aggregate
    # save outbox events

    conn.commit()

except Exception:
    conn.rollback()
    raise
```

Mục tiêu:

```text
Aggregate
+
Outbox
```

cùng transaction.

---

# 34. SQLite Schema

Có thể có:

```sql
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
```

và:

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    processed_at TEXT
);
```

---

# 35. Pending Event

Worker cần tìm:

```sql
SELECT
    id,
    event_type,
    payload
FROM outbox
WHERE processed_at IS NULL
ORDER BY occurred_at;
```

Ví dụ:

```text
event-001
ChapterAdded
pending

event-002
CrawlerCompleted
pending
```

---

# 36. Worker

Worker có logic:

```text
while True:

    events = get_pending_events()

    for event in events:

        dispatch(event)

        mark_processed(event)
```

Nhưng:

> **Đây mới là phiên bản đơn giản hóa.**

Production cần xử lý:

```text
retry
concurrency
locking
crash
duplicate delivery
poison message
dead letter
```

Chúng ta sẽ đi sâu ở Buổi 35.

---

# 37. Một vấn đề mới: Crash sau Handler

Giả sử:

```text
Worker
 ↓
read event
 ↓
SearchHandler
 ↓
SUCCESS
 ↓
💥 crash
 ↓
mark_processed() chưa chạy
```

Khi worker restart:

```text
event vẫn pending
 ↓
SearchHandler chạy lần nữa
```

Do đó:

> **Outbox thường cung cấp at-least-once processing, không mặc nhiên exactly-once.**

Vì vậy Handler phải quan tâm đến **idempotency**.

---

# 38. At-Least-Once

Ví dụ:

```text
Event #123
```

có thể:

```text
process
process again
```

nhưng mục tiêu là:

```text
event không bị mất
```

thay vì:

```text
event chỉ chạy chính xác một lần
```

Exactly-once rất khó trong distributed systems.

---

# 39. Outbox không giải quyết mọi thứ

Outbox giải quyết rất tốt:

```text
Database commit
+
Event persistence
```

và:

```text
Lost event
```

Nhưng vẫn cần giải quyết:

```text
duplicate processing
retry
external API failure
worker crash
concurrency
```

Đó là lý do Outbox + Idempotent Handler thường đi cùng nhau.

---

# 40. Một kiến trúc production thực tế

```text
                   Application
                       │
                       ▼
                 ┌───────────┐
                 │ Aggregate │
                 └─────┬─────┘
                       │
                 Domain Event
                       │
                       ▼
              ┌────────────────┐
              │ Unit of Work   │
              │                │
              │ Aggregate      │
              │ +              │
              │ Outbox         │
              └───────┬────────┘
                      │
                   COMMIT
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      Database                Outbox
                                  │
                                  ▼
                                Worker
                                  │
                                  ▼
                              Dispatcher
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 Search       Statistics    Notification
```

---

# 41. So sánh ba kiến trúc

## A. Before Commit

```text
Aggregate
 ↓
Event
 ↓
Handler
 ↓
Commit
```

Nguy cơ:

```text
Handler success
Commit failure
```

---

## B. After Commit

```text
Aggregate
 ↓
Commit
 ↓
Event
 ↓
Handler
```

Nguy cơ:

```text
Commit success
 ↓
Process crash
 ↓
Event lost
```

---

## C. Outbox

```text
Aggregate
 ↓
Event
 ↓
Outbox
 ↓
COMMIT
 ↓
Worker
 ↓
Handler
```

Nếu crash:

```text
Outbox vẫn còn event
```

Worker có thể retry.

Đây là hướng production.

---

# 42. Outbox không phải Message Broker

Outbox:

```text
SQLite
 └── outbox table
```

Message Broker:

```text
Redis
RabbitMQ
Kafka
...
```

Outbox là **reliable persistence mechanism**.

Broker là **messaging infrastructure**.

Có thể kết hợp:

```text
SQLite
 ↓
Outbox
 ↓
Worker
 ↓
Redis
 ↓
Consumers
```

---

# 43. Trong hệ thống đọc truyện của bạn

Ta có thể thiết kế:

```text
Crawler
   ↓
CrawlerCompleted
   ↓
Outbox
```

Worker:

```text
Outbox Worker
     ↓
CrawlerCompleted
     │
     ├── Update statistics
     ├── Update dashboard
     ├── Notify user
     └── Schedule next crawl
```

Hoặc:

```text
ChapterAdded
     │
     ├── Search index
     ├── Reading statistics
     └── Notification
```

Crawler core không cần biết những hệ thống này.

---

# 44. Một nguyên tắc cực kỳ quan trọng

> **Transaction bảo vệ state; Outbox bảo vệ việc phát hành event.**

Có thể nhớ:

```text
Aggregate
   ↓
Business State
   +
Domain Event
   ↓
Same Transaction
   ↓
COMMIT
```

Sau đó:

```text
Outbox
   ↓
Reliable Delivery
```

---

# 45. Domain Event không nhất thiết là integration event

Một nuance quan trọng.

### Domain Event

Mô tả:

```text
"Điều gì đã xảy ra trong domain?"
```

Ví dụ:

```text
ChapterAdded
```

### Integration Event

Mô tả:

```text
"Thông tin gì cần gửi sang hệ thống khác?"
```

Ví dụ:

```text
ChapterAddedIntegrationEvent
```

Không nhất thiết phải serialize Domain Event trực tiếp thành message public.

Trong hệ thống lớn:

```text
Domain Event
     ↓
Application
     ↓
Integration Event
     ↓
Broker
```

---

# 46. Điều cần tránh

Đừng làm:

```text
Aggregate
 ↓
HTTP API
 ↓
Redis
 ↓
Email
```

Aggregate không nên biết infrastructure.

Đúng hơn:

```text
Aggregate
 ↓
Domain Event
 ↓
Outbox
 ↓
Worker
 ↓
Infrastructure
```

---

# 47. Mental Model

Hãy nhớ 4 câu:

### 1.

**Before commit:**

```text
"Event có thể chạy nhưng transaction chưa chắc thành công."
```

### 2.

**After commit:**

```text
"Transaction chắc chắn thành công nhưng event có thể bị mất."
```

### 3.

**Outbox:**

```text
"State và event record commit cùng nhau."
```

### 4.

**Worker:**

```text
"Event được xử lý bên ngoài transaction chính."
```

---

# 48. Bài tập Buổi 34

Hãy phân tích flow sau:

```text
AddChapterUseCase
        ↓
Story.add_chapter()
        ↓
ChapterAdded
        ↓
Save Story
        ↓
COMMIT
        ↓
Dispatch
        ↓
Notification
```

Trả lời:

### Câu 1

Process crash ở:

```text
COMMIT
 ↓
💥
 ↓
Dispatch
```

Điều gì xảy ra?

---

### Câu 2

Đổi thành:

```text
Dispatch
 ↓
Notification
 ↓
COMMIT
```

Nếu `COMMIT` fail thì chuyện gì xảy ra?

---

### Câu 3

Thiết kế lại:

```text
Story
 ↓
ChapterAdded
 ↓
Outbox
 ↓
COMMIT
```

Tại sao cách này tốt hơn?

---

### Câu 4

Nếu Worker:

```text
dispatch(event)
 ↓
SUCCESS
 ↓
💥 crash
 ↓
mark_processed()
```

thì khi worker chạy lại điều gì xảy ra?

Gợi ý:

```text
event → có thể được xử lý lần 2
```

Và từ đây dẫn tới:

> **Idempotent Event Handler**

---

# 49. Bài tập code

Hãy xây một `SQLiteUnitOfWork` có:

```python
with uow:

    story = uow.stories.get(story_id)

    story.add_chapter(chapter)

    uow.stories.save(story)

    for event in story.collect_events():
        uow.outbox.add(event)

    uow.commit()
```

Database phải đảm bảo:

```text
┌──────────────────────┐
│ SQLite Transaction   │
│                      │
│ Story                │
│ Chapter              │
│ Outbox Event         │
│                      │
└──────────┬───────────┘
           │
         COMMIT
```

**Không dispatch Handler bên trong transaction.**

---

# 50. Tổng kết Buổi 34

Ta đã đi từ:

```text
Buổi 31
Domain Event
```

→

```text
Buổi 32
Event Dispatcher
```

→

```text
Buổi 33
Event Handler
```

→ hôm nay:

```text
Buổi 34
Event + Transaction
```

và cuối cùng:

```text
                    ┌─────────────┐
                    │  Aggregate  │
                    └──────┬──────┘
                           │
                           ▼
                    Domain Event
                           │
                           ▼
                  ┌─────────────────┐
                  │ Unit of Work    │
                  │                 │
                  │ Aggregate       │
                  │ Outbox Event    │
                  └────────┬────────┘
                           │
                         COMMIT
                           │
                           ▼
                        Outbox
                           │
                           ▼
                         Worker
                           │
                           ▼
                     Event Handler
                           │
                ┌──────────┼──────────┐
                ▼          ▼          ▼
             Search     Notify     Statistics
```

**Điểm cốt lõi của Buổi 34:**

> **Không cố đưa external side effects vào cùng transaction với Aggregate. Hãy đảm bảo Aggregate state và Event record được commit atomically; sau đó xử lý Event từ Outbox.**

Ở **Buổi 35 — Outbox Pattern**, chúng ta sẽ triển khai thật bằng **Python + SQLite**, gồm `outbox` table, serialization Domain Event, polling worker, retry, trạng thái `pending/processing/processed/failed`, idempotency và xử lý crash/concurrency.
