# Buổi 7 — CrawlStateRepository + Resume / Retry / Checkpoint

Hôm nay chúng ta xây phần rất quan trọng để biến crawler từ:

```text
crawler chạy một lần
```

thành:

```text
crawler production-style
        │
        ├── pause
        ├── resume
        ├── retry
        ├── crash recovery
        └── checkpoint
```

Kiến trúc:

```text
                    Crawler
                       │
                       ▼
                 Application
                       │
                       ▼
                  Crawl UseCase
                       │
                       ▼
                      UoW
              ┌────────┼────────┐
              ▼        ▼        ▼
           Novel    Chapter   CrawlState
           Repo      Repo       Repo
              │        │          │
              └────────┼──────────┘
                       ▼
                     SQLite
```

---

# 1. CrawlState là gì?

Crawler không chỉ cần biết:

```text
Novel có tồn tại hay không?
Chapter có tồn tại hay không?
```

Nó còn cần biết:

```text
Crawler đang làm gì?
Đã crawl tới đâu?
Lần cuối chạy khi nào?
Có lỗi không?
Lỗi gì?
Có cần retry không?
```

Ví dụ:

```text
Novel: Đấu Phá Thương Khung

status:
    crawling

last_chapter:
    523

total_chapters:
    1648

retry_count:
    2
```

Nếu process crash:

```text
Crawler
   ↓
Chapter 523
   ↓
CRASH
```

lần chạy sau có thể biết:

```text
resume_from = 524
```

---

# 2. Database Schema

Ta tạo:

```sql
CREATE TABLE crawl_states (
    novel_id INTEGER PRIMARY KEY,

    status TEXT NOT NULL,

    last_chapter_number INTEGER NOT NULL DEFAULT 0,

    total_chapters INTEGER,

    retry_count INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    started_at TEXT,

    finished_at TEXT,

    updated_at TEXT,

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Quan hệ:

```text
novels
   │
   │ 1
   │
   │ 1
   ▼
crawl_states
```

Một Novel có **một CrawlState**.

---

# 3. State Machine

Không nên để status tùy ý như:

```text
"abc"
"running2"
"hello"
```

Ta định nghĩa state rõ ràng.

```python
from enum import StrEnum


class CrawlStatus(StrEnum):
    PENDING = "pending"
    CRAWLING = "crawling"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

Flow:

```text
                 ┌──────────┐
                 │ PENDING  │
                 └────┬─────┘
                      │
                      ▼
                 ┌──────────┐
                 │ CRAWLING │
                 └────┬─────┘
              ┌───────┼────────┐
              │       │        │
              ▼       ▼        ▼
          COMPLETED  PAUSED   FAILED
                      │         │
                      │         │
                      └────┬────┘
                           ▼
                       CRAWLING
```

---

# 4. Domain Entity

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CrawlState:
    novel_id: int
    status: CrawlStatus

    last_chapter_number: int = 0
    total_chapters: int | None = None

    retry_count: int = 0
    error_message: str | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None
    updated_at: datetime | None = None
```

---

# 5. Tại sao CrawlState là Domain Entity?

Vì nó không đơn thuần là database row.

Nó có behavior:

```text
start()
pause()
resume()
fail()
complete()
checkpoint()
retry()
```

Ví dụ:

```python
state.start()
```

có thể thay đổi:

```text
PENDING
   ↓
CRAWLING
```

Trong khi:

```python
state.complete()
```

thay đổi:

```text
CRAWLING
   ↓
COMPLETED
```

Đây là **domain behavior**.

---

# 6. Đừng cho phép state transition tùy tiện

Ví dụ:

```text
COMPLETED
    ↓
CRAWLING
```

có thể không hợp lệ tùy business rule.

Hoặc:

```text
PENDING
    ↓
COMPLETED
```

không hợp lý nếu chưa crawl chapter nào.

Ta nên đặt invariant.

Ví dụ:

```python
class CrawlState:

    def start(self):
        if self.status not in {
            CrawlStatus.PENDING,
            CrawlStatus.PAUSED,
            CrawlStatus.FAILED,
        }:
            raise ValueError(
                f"Cannot start from {self.status}"
            )

        self.status = CrawlStatus.CRAWLING
```

---

# 7. Checkpoint

Đây là khái niệm cực kỳ quan trọng.

Giả sử:

```text
Chapter 1
Chapter 2
Chapter 3
...
Chapter 500
```

Crawler lưu:

```text
last_chapter_number = 500
```

Đây chính là:

# Checkpoint

Nếu crash:

```text
Chapter 501
   ↓
fetch
   ↓
parse
   ↓
CRASH
```

checkpoint vẫn:

```text
500
```

Lần sau:

```text
resume from 501
```

---

# 8. Nhưng checkpoint phải cập nhật lúc nào?

Đây là câu hỏi rất quan trọng.

Không nên:

```text
fetch chapter
   ↓
checkpoint = chapter number
   ↓
save chapter
```

Vì:

```text
checkpoint = 501
save chapter 501 = FAILED
```

Database sẽ nói:

```text
đã crawl tới 501
```

nhưng Chapter 501 thực tế chưa tồn tại.

Sai.

---

# 9. Quy tắc đúng

Phải:

```text
Fetch
  ↓
Parse
  ↓
Validate
  ↓
Save Chapter
  ↓
Checkpoint
```

và hai operation cuối nằm trong **cùng transaction**.

```text
BEGIN

INSERT/UPSERT Chapter 501

UPDATE CrawlState
SET last_chapter_number = 501

COMMIT
```

Nếu Chapter fail:

```text
BEGIN

INSERT Chapter 501
      ↓
      ERROR

ROLLBACK
```

CrawlState vẫn:

```text
last_chapter_number = 500
```

Đây là thiết kế rất quan trọng.

---

# 10. CrawlStateRepository

Interface:

```python
from abc import ABC, abstractmethod


class CrawlStateRepository(ABC):

    @abstractmethod
    def get_by_novel(
        self,
        novel_id: int,
    ) -> CrawlState | None:
        ...

    @abstractmethod
    def save(
        self,
        state: CrawlState,
    ) -> None:
        ...

    @abstractmethod
    def update_checkpoint(
        self,
        novel_id: int,
        chapter_number: int,
    ) -> None:
        ...
```

---

# 11. SQLite implementation

```python
class SQLiteCrawlStateRepository:

    def __init__(self, conn):
        self.conn = conn
```

---

## get()

```python
def get_by_novel(
    self,
    novel_id: int,
) -> CrawlState | None:

    row = self.conn.execute(
        """
        SELECT
            novel_id,
            status,
            last_chapter_number,
            total_chapters,
            retry_count,
            error_message,
            started_at,
            finished_at,
            updated_at
        FROM crawl_states
        WHERE novel_id = ?
        """,
        (novel_id,),
    ).fetchone()

    if row is None:
        return None

    return CrawlState(
        novel_id=row["novel_id"],
        status=CrawlStatus(row["status"]),
        last_chapter_number=row[
            "last_chapter_number"
        ],
        total_chapters=row["total_chapters"],
        retry_count=row["retry_count"],
        error_message=row["error_message"],
    )
```

---

# 12. Tạo CrawlState

Có thể dùng UPSERT:

```sql
INSERT INTO crawl_states (
    novel_id,
    status,
    last_chapter_number
)
VALUES (?, ?, 0)

ON CONFLICT(novel_id)
DO NOTHING;
```

Repository:

```python
def create_if_not_exists(
    self,
    novel_id: int,
) -> None:

    self.conn.execute(
        """
        INSERT INTO crawl_states (
            novel_id,
            status,
            last_chapter_number
        )
        VALUES (?, ?, 0)

        ON CONFLICT(novel_id)
        DO NOTHING
        """,
        (
            novel_id,
            CrawlStatus.PENDING.value,
        ),
    )
```

---

# 13. Update checkpoint

```python
def update_checkpoint(
    self,
    novel_id: int,
    chapter_number: int,
) -> None:

    self.conn.execute(
        """
        UPDATE crawl_states
        SET
            last_chapter_number = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE novel_id = ?
        """,
        (
            chapter_number,
            novel_id,
        ),
    )
```

Nhớ:

```text
Repository UPDATE
        ↓
KHÔNG COMMIT
```

UoW sẽ commit.

---

# 14. Thêm CrawlState vào UoW

UoW hiện tại:

```text
UoW
 ├── novels
 ├── chapters
 └── crawl_states
```

Code:

```python
class SQLiteUnitOfWork:

    def __enter__(self):

        self.conn = (
            self.connection_manager.connect()
        )

        self.novels = SQLiteNovelRepository(
            self.conn
        )

        self.chapters = SQLiteChapterRepository(
            self.conn
        )

        self.crawl_states = (
            SQLiteCrawlStateRepository(
                self.conn
            )
        )

        return self
```

Bây giờ cả ba repository dùng:

```text
        SAME CONNECTION
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Novel  Chapter  State
```

---

# 15. Use Case Crawl Chapter

Bây giờ hãy thiết kế một Use Case:

```python
class SaveChapter:
    def __init__(self, uow):
        self.uow = uow
```

Flow:

```text
Save Chapter
     │
     ▼
BEGIN
     │
     ├── UPSERT Chapter
     │
     ├── UPDATE checkpoint
     │
     ▼
  COMMIT
```

Code:

```python
class SaveChapter:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        chapter: Chapter,
    ):

        with self.uow:

            self.uow.chapters.upsert(
                chapter
            )

            self.uow.crawl_states.update_checkpoint(
                chapter.novel_id,
                chapter.chapter_number,
            )
```

---

# 16. Vì sao đây là thiết kế tốt?

Giả sử:

```text
Chapter 501
```

save thành công:

```text
chapters
    ↓
501 exists

crawl_states
    ↓
last_chapter = 501
```

Cả hai commit cùng nhau.

Không thể xảy ra:

```text
chapter = 501
checkpoint = 500
```

nếu transaction thành công.

Và cũng không xảy ra:

```text
chapter = missing
checkpoint = 501
```

nếu transaction rollback đúng.

---

# 17. Resume Use Case

Ta cần:

```python
class GetResumePoint:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        novel_id: int,
    ) -> int:

        with self.uow:

            state = (
                self.uow.crawl_states
                .get_by_novel(novel_id)
            )

            if state is None:
                return 1

            return (
                state.last_chapter_number + 1
            )
```

Nếu:

```text
last_chapter_number = 500
```

thì:

```python
resume_from = 501
```

---

# 18. Nhưng `with self.uow` ở đây có commit

Đây là điểm tinh tế.

Use Case chỉ đọc:

```python
state = repo.get(...)
```

nhưng:

```python
with self.uow:
```

theo implementation hiện tại:

```python
__exit__()
    ↓
commit()
```

Không sai nghiêm trọng, nhưng không tối ưu về mặt semantics.

Trong hệ thống lớn, ta có thể tách:

```text
UnitOfWork
    ↓
transactional work

Read Repository
    ↓
read-only query
```

hoặc vẫn dùng UoW cho đơn giản.

Sau này khi học **CQRS / Read Model**, vấn đề này sẽ được giải quyết đẹp hơn.

---

# 19. Retry

Giả sử HTTP request:

```text
GET chapter 501
```

thất bại:

```text
Timeout
```

Ta không nên ngay lập tức:

```text
FAILED forever
```

Ta có:

```text
retry_count
```

Ví dụ policy:

```text
retry 1
retry 2
retry 3
→ FAILED
```

---

# 20. Retry policy nên nằm ở đâu?

Không nên:

```text
Repository
    ↓
retry HTTP
```

Repository chỉ biết database.

Cũng không nên nhét toàn bộ retry vào Entity.

Có thể thiết kế:

```text
Application
    ↓
RetryPolicy
```

Ví dụ:

```python
class RetryPolicy:

    def __init__(
        self,
        max_retries: int = 3,
    ):
        self.max_retries = max_retries

    def should_retry(
        self,
        retry_count: int,
    ) -> bool:

        return retry_count < self.max_retries
```

---

# 21. CrawlState có thể có `fail()`

```python
def fail(self, message: str):

    self.status = CrawlStatus.FAILED
    self.error_message = message
    self.retry_count += 1
```

Sau đó application quyết định:

```python
if policy.should_retry(state.retry_count):
    state.start()
else:
    state.fail(error)
```

Tách:

```text
Domain
   ↓
state transition

Application
   ↓
retry orchestration

Infrastructure
   ↓
SQLite persistence
```

rất sạch.

---

# 22. Pause / Resume

Ta muốn CLI:

```bash
novel crawl start 123
novel crawl pause 123
novel crawl resume 123
novel crawl status 123
```

Flow pause:

```text
CLI
 ↓
PauseCrawl
 ↓
UoW
 ↓
CrawlState
 ↓
PAUSED
```

Domain:

```python
def pause(self):

    if self.status != CrawlStatus.CRAWLING:
        raise ValueError(
            "Only crawling state can be paused"
        )

    self.status = CrawlStatus.PAUSED
```

---

# 23. Resume

```python
def resume(self):

    if self.status != CrawlStatus.PAUSED:
        raise ValueError(
            "Only paused crawl can resume"
        )

    self.status = CrawlStatus.CRAWLING
```

Đây là ví dụ điển hình của:

> **Domain invariant**

Không phải mọi trạng thái đều chuyển sang mọi trạng thái.

---

# 24. Full state machine

Ta có:

```text
                  ┌─────────┐
                  │ PENDING │
                  └────┬────┘
                       │ start
                       ▼
                 ┌──────────┐
          ┌─────►│ CRAWLING │◄─────┐
          │      └────┬─────┘      │
          │           │            │
       resume         │            │ retry
          │           │            │
          │      ┌────┴────┐   ┌───┴────┐
          │      ▼         ▼   ▼        │
       ┌──────┐ PAUSED  FAILED──────────┘
       └──────┘
                       │
                       │ success
                       ▼
                  ┌───────────┐
                  │ COMPLETED │
                  └───────────┘
```

Đây chính là một **state machine** đơn giản.

---

# 25. Crash Recovery

Đây là mục tiêu lớn nhất.

Giả sử:

```text
last_checkpoint = 500
```

Crawler:

```text
fetch 501
save 501
checkpoint 501
COMMIT
```

sau đó:

```text
fetch 502
CRASH
```

Database:

```text
last_checkpoint = 501
```

Process khởi động lại:

```text
resume_from = 502
```

Không cần crawl lại 1 → 501.

---

# 26. Nếu crash giữa transaction?

Giả sử:

```text
BEGIN

save Chapter 502 ✓

update checkpoint 502 ✓

CRASH

COMMIT chưa chạy
```

SQLite transaction chưa commit.

Khi connection/process kết thúc:

```text
ROLLBACK
```

Kết quả:

```text
Chapter 502     → không tồn tại
checkpoint      → 501
```

Lần sau:

```text
resume = 502
```

Đây là lý do:

> **Checkpoint phải nằm trong cùng transaction với dữ liệu mà checkpoint đại diện.**

---

# 27. Đây là pattern rất quan trọng

```text
             Transaction
┌─────────────────────────────────┐
│                                 │
│  Save Chapter                    │
│        │                        │
│        ▼                        │
│  Update Checkpoint               │
│                                 │
└──────────────┬──────────────────┘
               │
            COMMIT
```

Không được:

```text
Save Chapter
     ↓
COMMIT

Update checkpoint
     ↓
COMMIT
```

vì giữa hai commit có thể crash.

---

# 28. Một vấn đề tinh tế: checkpoint không nhất thiết là max chapter

Giả sử crawler chạy song song:

```text
worker A → chapter 100
worker B → chapter 101
```

Worker B hoàn thành trước:

```text
checkpoint = 101
```

Worker A sau đó hoàn thành:

```text
checkpoint = 100
```

Nếu update trực tiếp:

```sql
last_chapter_number = 100
```

checkpoint bị lùi.

Do đó với crawler concurrent, ta nên dùng:

```sql
UPDATE crawl_states
SET last_chapter_number = MAX(
    last_chapter_number,
    ?
)
WHERE novel_id = ?
```

Ví dụ:

```python
def update_checkpoint(
    self,
    novel_id: int,
    chapter_number: int,
) -> None:

    self.conn.execute(
        """
        UPDATE crawl_states
        SET
            last_chapter_number =
                MAX(last_chapter_number, ?),
            updated_at = CURRENT_TIMESTAMP
        WHERE novel_id = ?
        """,
        (
            chapter_number,
            novel_id,
        ),
    )
```

Đây là một chi tiết cực kỳ đáng nhớ khi sau này chúng ta học:

```text
Thread
Worker
Queue
Asyncio
Parallel crawling
```

---

# 29. Nhưng concurrent crawler còn phức tạp hơn

`last_chapter_number` chỉ an toàn nếu chapter được crawl tuần tự hoặc chúng ta chỉ quan tâm tới **highest completed chapter**.

Ví dụ:

```text
100 ✓
101 ✓
102 ✗
103 ✓
```

Nếu checkpoint:

```text
103
```

thì không thể hiểu:

```text
100 → 103 đều hoàn thành
```

vì Chapter 102 mất.

Do đó:

### Sequential crawler

Có thể dùng:

```text
last_chapter_number
```

### Concurrent crawler

Có thể cần:

```text
ChapterStatus
```

cho từng chapter:

```text
pending
crawling
completed
failed
```

Đây là kiến trúc chúng ta sẽ xây tiếp.

---

# 30. Kiến trúc hiện tại

Sau Buổi 7:

```text
                    Application
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         CrawlNovel             ResumeCrawl
              │                     │
              └──────────┬──────────┘
                         ▼
                        UoW
             ┌───────────┼────────────┐
             ▼           ▼            ▼
          novels      chapters    crawl_states
             │           │            │
             └───────────┼────────────┘
                         ▼
                      SQLite
```

Domain:

```text
Novel
Chapter
CrawlState
```

Infrastructure:

```text
SQLiteNovelRepository
SQLiteChapterRepository
SQLiteCrawlStateRepository
SQLiteUnitOfWork
SQLiteConnectionManager
```

---

# 31. Flow hoàn chỉnh

Một chapter được crawl:

```text
HTTP
 ↓
Parser
 ↓
Chapter
 ↓
SaveChapter UseCase
 ↓
UoW
 ├── ChapterRepository.upsert()
 │
 └── CrawlStateRepository.update_checkpoint()
 ↓
COMMIT
```

Nếu lỗi:

```text
HTTP
 ↓
Parser
 ↓
Chapter
 ↓
SaveChapter
 ↓
Chapter INSERT
 ↓
ERROR
 ↓
ROLLBACK
```

Checkpoint không bị cập nhật sai.

---

# 32. Bài tập Buổi 7

### Bài 1 — Domain

Implement:

```python
CrawlState.start()
CrawlState.pause()
CrawlState.resume()
CrawlState.fail()
CrawlState.complete()
```

và đảm bảo transition không hợp lệ phải raise exception.

---

### Bài 2 — Repository

Implement:

```python
SQLiteCrawlStateRepository
```

có:

```text
get_by_novel()
create_if_not_exists()
update_checkpoint()
save()
```

---

### Bài 3 — UoW

Thêm:

```python
self.crawl_states
```

vào:

```python
SQLiteUnitOfWork
```

---

### Bài 4 — Transaction

Viết:

```python
SaveChapter
```

đảm bảo:

```text
UPSERT chapter
        +
UPDATE checkpoint
        ↓
     COMMIT
```

---

### Bài 5 — Crash simulation

Cố tình tạo lỗi:

```python
with uow:

    uow.chapters.upsert(chapter)

    raise RuntimeError("CRASH")

    uow.crawl_states.update_checkpoint(
        novel_id,
        chapter.chapter_number,
    )
```

Sau đó kiểm tra:

```text
Chapter không tồn tại
Checkpoint không thay đổi
```

---

# 33. Bài tập quan trọng nhất

Hãy mô phỏng:

```text
last_chapter = 100
```

Crawler xử lý:

```text
101 ✓
102 ✓
103 ✓
104 ✗
```

Sau rollback:

```text
last_chapter = ?
```

**Đáp án phải là:**

```text
100
```

Lần chạy tiếp:

```text
resume_from = 101
```

Nếu 101–103 đã commit riêng từng chapter trước đó thì:

```text
UPSERT
```

sẽ giúp crawler xử lý lại an toàn.

---

# 34. Tư duy kiến trúc cần nhớ

Buổi 6:

```text
Novel + Chapter
       ↓
Repository + UoW
       ↓
Atomic transaction
```

Buổi 7:

```text
Chapter
   +
Checkpoint
   ↓
Atomic transaction
   ↓
Crash recovery
```

Và nguyên tắc quan trọng nhất:

> **Checkpoint phải đại diện cho dữ liệu đã thực sự commit.**

Từ đây crawler của chúng ta đã có nền tảng cho:

```text
       CRAWLER
          │
          ├── Repository
          ├── Unit of Work
          ├── Transaction
          ├── UPSERT
          ├── Idempotency
          ├── Checkpoint
          ├── Resume
          ├── Retry
          └── Crash Recovery
```

**Buổi 8** hợp lý nhất sẽ là **ChapterStatus + Queue/Worker boundary**: thay vì chỉ lưu `last_chapter_number`, ta quản lý trạng thái **từng chapter** (`pending / crawling / completed / failed`), từ đó chuẩn bị trực tiếp cho **Queue + Worker + concurrent crawler**.
