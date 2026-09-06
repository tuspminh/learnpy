# Buổi 8 — ChapterStatus + Queue/Worker Boundary

Ở Buổi 7, chúng ta có:

```text
Novel
 ├── Chapters
 └── CrawlState
       └── last_chapter_number
```

Cách này tốt cho **crawler tuần tự**.

Nhưng khi chuyển sang:

```text
Queue
  ↓
Worker 1
Worker 2
Worker 3
Worker 4
```

thì `last_chapter_number` **không còn đủ**.

Hôm nay chúng ta giải quyết vấn đề đó.

---

# 1. Vấn đề của `last_chapter_number`

Giả sử có 5 worker:

```text
Worker 1 → Chapter 101
Worker 2 → Chapter 102
Worker 3 → Chapter 103
Worker 4 → Chapter 104
Worker 5 → Chapter 105
```

Kết quả:

```text
101 ✓
102 ✓
103 ✗
104 ✓
105 ✓
```

Nếu chỉ có:

```text
last_chapter_number = 105
```

ta không biết Chapter 103 thất bại.

Vì vậy:

> Với crawler concurrent, trạng thái phải được quản lý **theo từng Chapter**.

---

# 2. Chapter cần có Status

Ta mở rộng:

```python
from enum import StrEnum


class ChapterStatus(StrEnum):
    PENDING = "pending"
    CRAWLING = "crawling"
    COMPLETED = "completed"
    FAILED = "failed"
```

State machine:

```text
                 ┌─────────┐
                 │ PENDING │
                 └────┬────┘
                      │
                      ▼
                ┌──────────┐
                │ CRAWLING │
                └────┬─────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
         COMPLETED        FAILED
                              │
                              │ retry
                              ▼
                          PENDING
```

---

# 3. Tách `Chapter` và `ChapterCrawlState`

Đây là một quyết định thiết kế quan trọng.

Không nhất thiết phải nhét tất cả vào:

```python
Chapter
```

Ví dụ Chapter:

```python
@dataclass
class Chapter:
    id: int | None
    novel_id: int
    chapter_number: int
    title: str
    content: str
```

Còn trạng thái crawl:

```python
@dataclass
class ChapterCrawlState:
    novel_id: int
    chapter_number: int
    status: ChapterStatus
    retry_count: int = 0
    error_message: str | None = None
```

Tư duy:

```text
Chapter
    ↓
nội dung domain

ChapterCrawlState
    ↓
trạng thái xử lý
```

Đây là separation rất hữu ích.

---

# 4. Database

Ta tạo:

```sql
CREATE TABLE chapter_crawl_states (
    novel_id INTEGER NOT NULL,

    chapter_number INTEGER NOT NULL,

    status TEXT NOT NULL,

    retry_count INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    started_at TEXT,

    finished_at TEXT,

    updated_at TEXT,

    PRIMARY KEY (
        novel_id,
        chapter_number
    ),

    FOREIGN KEY (novel_id)
        REFERENCES novels(id)
        ON DELETE CASCADE
);
```

Khóa chính:

```text
(novel_id, chapter_number)
```

nghĩa là:

```text
Novel 1 + Chapter 10
```

chỉ có một state.

---

# 5. Kiến trúc mới

Bây giờ:

```text
Novel
 │
 ├── Chapter
 │
 └── ChapterCrawlState
```

Infrastructure:

```text
UoW
 ├── novels
 ├── chapters
 ├── crawl_states
 └── chapter_crawl_states
```

---

# 6. Repository Interface

Ta tạo:

```python
class ChapterCrawlStateRepository(ABC):

    @abstractmethod
    def get(
        self,
        novel_id: int,
        chapter_number: int,
    ) -> ChapterCrawlState | None:
        ...

    @abstractmethod
    def create(
        self,
        state: ChapterCrawlState,
    ) -> None:
        ...

    @abstractmethod
    def mark_crawling(
        self,
        novel_id: int,
        chapter_number: int,
    ) -> None:
        ...

    @abstractmethod
    def mark_completed(
        self,
        novel_id: int,
        chapter_number: int,
    ) -> None:
        ...

    @abstractmethod
    def mark_failed(
        self,
        novel_id: int,
        chapter_number: int,
        error: str,
    ) -> None:
        ...
```

---

# 7. Nhưng Repository có một vấn đề

Ta có:

```python
mark_crawling()
mark_completed()
mark_failed()
```

Các method này có vẻ tiện.

Nhưng có một câu hỏi:

> Business rule nằm ở đâu?

Ví dụ:

```text
COMPLETED → CRAWLING
```

có được phép không?

Repository không nên quyết định.

Repository chỉ persistence.

Do đó tốt hơn là:

```text
Domain
   ↓
ChapterCrawlState
   ↓
transition
   ↓
Repository.save()
```

---

# 8. Domain Entity

```python
@dataclass
class ChapterCrawlState:

    novel_id: int
    chapter_number: int

    status: ChapterStatus = (
        ChapterStatus.PENDING
    )

    retry_count: int = 0
    error_message: str | None = None
```

---

# 9. Domain Behavior

## Start

```python
def start(self) -> None:

    if self.status not in {
        ChapterStatus.PENDING,
        ChapterStatus.FAILED,
    }:
        raise ValueError(
            f"Cannot start from {self.status}"
        )

    self.status = ChapterStatus.CRAWLING
    self.error_message = None
```

---

## Complete

```python
def complete(self) -> None:

    if self.status != ChapterStatus.CRAWLING:
        raise ValueError(
            "Chapter is not crawling"
        )

    self.status = ChapterStatus.COMPLETED
```

---

## Fail

```python
def fail(self, error: str) -> None:

    if self.status != ChapterStatus.CRAWLING:
        raise ValueError(
            "Chapter is not crawling"
        )

    self.status = ChapterStatus.FAILED
    self.retry_count += 1
    self.error_message = error
```

---

# 10. Đây là Domain State Machine

Domain object tự bảo vệ invariant:

```text
PENDING
   │
   │ start()
   ▼
CRAWLING
   │
   ├── complete()
   │       ↓
   │   COMPLETED
   │
   └── fail()
           ↓
        FAILED
           │
           │ start()
           ▼
        CRAWLING
```

Repository không biết những rule này.

---

# 11. SQLite Repository

```python
class SQLiteChapterCrawlStateRepository:

    def __init__(self, conn):
        self.conn = conn
```

---

## Save

```python
def save(
    self,
    state: ChapterCrawlState,
) -> None:

    self.conn.execute(
        """
        INSERT INTO chapter_crawl_states (
            novel_id,
            chapter_number,
            status,
            retry_count,
            error_message
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(novel_id, chapter_number)
        DO UPDATE SET
            status = excluded.status,
            retry_count = excluded.retry_count,
            error_message = excluded.error_message,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            state.novel_id,
            state.chapter_number,
            state.status.value,
            state.retry_count,
            state.error_message,
        ),
    )
```

Đây là một pattern rất tốt:

```text
Domain Entity
     ↓
Repository.save()
     ↓
UPSERT
```

---

# 12. `get()`

```python
def get(
    self,
    novel_id: int,
    chapter_number: int,
) -> ChapterCrawlState | None:

    row = self.conn.execute(
        """
        SELECT
            novel_id,
            chapter_number,
            status,
            retry_count,
            error_message
        FROM chapter_crawl_states
        WHERE novel_id = ?
          AND chapter_number = ?
        """,
        (
            novel_id,
            chapter_number,
        ),
    ).fetchone()

    if row is None:
        return None

    return ChapterCrawlState(
        novel_id=row["novel_id"],
        chapter_number=row["chapter_number"],
        status=ChapterStatus(row["status"]),
        retry_count=row["retry_count"],
        error_message=row["error_message"],
    )
```

---

# 13. UoW

UoW bây giờ:

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

        self.chapter_crawl_states = (
            SQLiteChapterCrawlStateRepository(
                self.conn
            )
        )

        return self
```

Ta có:

```text
                  UoW
                   │
       ┌───────────┼────────────┐
       ▼           ▼            ▼
    novels      chapters    crawl_states
                                  │
                                  ▼
                         chapter_crawl_states
```

---

# 14. Queue xuất hiện ở đâu?

Đây là bước chuyển rất quan trọng.

Ta không muốn:

```text
Crawler
   ↓
crawl Chapter 1
crawl Chapter 2
crawl Chapter 3
...
```

Mà:

```text
Crawler
   ↓
Generate Jobs
   ↓
Queue
```

Ví dụ:

```text
Queue
 ├── chapter 101
 ├── chapter 102
 ├── chapter 103
 ├── chapter 104
 └── chapter 105
```

Worker lấy job:

```text
Worker
   │
   ▼
Job
   │
   ▼
Fetch Chapter
   │
   ▼
Parse
   │
   ▼
Save
```

---

# 15. Job Object

Đừng truyền một đống dictionary:

```python
{
    "novel_id": 10,
    "chapter": 101,
    "url": "...",
}
```

Ta có thể tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlChapterJob:
    novel_id: int
    chapter_number: int
    url: str
```

Job là immutable:

```python
@dataclass(frozen=True)
```

Worker chỉ nhận:

```text
CrawlChapterJob
```

---

# 16. Worker Boundary

Worker:

```python
class ChapterWorker:

    def __init__(
        self,
        crawler,
        save_chapter,
    ):
        self.crawler = crawler
        self.save_chapter = save_chapter

    def process(
        self,
        job: CrawlChapterJob,
    ):
        chapter = self.crawler.fetch(
            job
        )

        self.save_chapter.execute(
            chapter
        )
```

Chú ý:

Worker không biết:

```text
sqlite3
SQL
commit
rollback
```

Worker chỉ biết:

```text
Job
 ↓
Crawler
 ↓
Use Case
```

---

# 17. Worker + Chapter State

Ta cần cập nhật:

```text
PENDING
   ↓
CRAWLING
   ↓
COMPLETED
```

Có thể làm Use Case:

```python
class StartChapterCrawl:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        novel_id: int,
        chapter_number: int,
    ):

        with self.uow:

            state = (
                self.uow.chapter_crawl_states
                .get(
                    novel_id,
                    chapter_number,
                )
            )

            if state is None:
                state = ChapterCrawlState(
                    novel_id=novel_id,
                    chapter_number=chapter_number,
                )

            state.start()

            self.uow.chapter_crawl_states.save(
                state
            )
```

---

# 18. Nhưng có Race Condition

Đây là phần cực kỳ quan trọng khi chúng ta bắt đầu concurrency.

Giả sử:

```text
Worker A
    ↓
get state = PENDING

Worker B
    ↓
get state = PENDING
```

Cả hai đều thấy:

```text
PENDING
```

Worker A:

```text
PENDING → CRAWLING
```

Worker B:

```text
PENDING → CRAWLING
```

Kết quả:

```text
Worker A → crawl Chapter 100
Worker B → crawl Chapter 100
```

Một chapter bị crawl hai lần.

---

# 19. Đây gọi là Race Condition

```text
          DB
           │
      state=PENDING
        /       \
       /         \
 Worker A       Worker B
   read            read
    │               │
 PENDING         PENDING
    │               │
 CRAWLING        CRAWLING
```

Đây là một vấn đề mà:

> `get() -> modify() -> save()` đơn thuần không giải quyết được.

---

# 20. Cần Atomic Claim

Thay vì:

```text
SELECT
   ↓
UPDATE
```

ta cần một operation atomic:

```text
UPDATE ... WHERE status = 'pending'
```

Ví dụ:

```sql
UPDATE chapter_crawl_states
SET
    status = 'crawling',
    started_at = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE novel_id = ?
  AND chapter_number = ?
  AND status = 'pending';
```

Sau đó kiểm tra:

```python
cursor.rowcount
```

Nếu:

```text
1
```

→ Worker claim thành công.

Nếu:

```text
0
```

→ Worker khác đã claim hoặc state không còn pending.

---

# 21. Đây là khái niệm `Claim`

Queue worker thực tế thường có:

```text
PENDING
   ↓
CLAIM
   ↓
PROCESSING
```

Không phải:

```text
SELECT
UPDATE
```

một cách tùy tiện.

---

# 22. Repository method

Ta có thể thêm:

```python
def claim(
    self,
    novel_id: int,
    chapter_number: int,
) -> bool:

    cursor = self.conn.execute(
        """
        UPDATE chapter_crawl_states
        SET
            status = ?,
            started_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE novel_id = ?
          AND chapter_number = ?
          AND status = ?
        """,
        (
            ChapterStatus.CRAWLING.value,
            novel_id,
            chapter_number,
            ChapterStatus.PENDING.value,
        ),
    )

    return cursor.rowcount == 1
```

Đây là một operation rất mạnh.

---

# 23. Worker Flow

Bây giờ:

```text
Job
 │
 ▼
claim()
 │
 ├── False → bỏ qua
 │
 └── True
      │
      ▼
    fetch
      │
      ▼
    parse
      │
      ▼
    save
```

Nếu Worker A claim:

```text
PENDING
   ↓
CRAWLING
```

Worker B:

```text
PENDING?
   ↓
NO
   ↓
skip
```

---

# 24. Khi hoàn thành

Ta cần transaction:

```text
BEGIN

save chapter
   +
mark chapter state = COMPLETED

COMMIT
```

Use Case:

```python
class CompleteChapterCrawl:

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

            state = (
                self.uow.chapter_crawl_states
                .get(
                    chapter.novel_id,
                    chapter.chapter_number,
                )
            )

            if state is None:
                raise RuntimeError(
                    "Crawl state not found"
                )

            state.complete()

            self.uow.chapter_crawl_states.save(
                state
            )
```

---

# 25. Nếu save Chapter thành công nhưng state update thất bại?

Ví dụ:

```text
BEGIN

Chapter UPSERT ✓

State UPDATE ✗

ROLLBACK
```

Kết quả:

```text
Chapter không commit
State không commit
```

Sau đó retry:

```text
Chapter UPSERT
```

vẫn an toàn vì chúng ta đã thiết kế **idempotent UPSERT**.

Đây là lúc các bài học:

```text
Buổi 6
UPSERT

Buổi 7
Checkpoint

Buổi 8
Chapter State
```

bắt đầu kết nối với nhau.

---

# 26. Failed

Nếu crawler lỗi:

```python
class FailChapterCrawl:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        novel_id: int,
        chapter_number: int,
        error: str,
    ):

        with self.uow:

            state = (
                self.uow.chapter_crawl_states
                .get(
                    novel_id,
                    chapter_number,
                )
            )

            if state is None:
                raise RuntimeError(
                    "State not found"
                )

            state.fail(error)

            self.uow.chapter_crawl_states.save(
                state
            )
```

Database:

```text
chapter 103

status:
    failed

retry_count:
    1

error:
    timeout
```

---

# 27. Retry

Ta có:

```text
FAILED
  │
  │ retry
  ▼
PENDING
```

Domain:

```python
def retry(self):

    if self.status != ChapterStatus.FAILED:
        raise ValueError(
            "Only failed chapter can retry"
        )

    self.status = ChapterStatus.PENDING
    self.error_message = None
```

Sau đó worker có thể claim lại.

---

# 28. Retry limit

Ví dụ:

```python
MAX_RETRIES = 3
```

Logic:

```text
retry_count = 0
     ↓
attempt
     ↓
FAILED
     ↓
retry_count = 1
     ↓
attempt
     ↓
FAILED
     ↓
retry_count = 2
     ↓
attempt
     ↓
FAILED
     ↓
retry_count = 3
     ↓
STOP
```

Đừng retry vô hạn.

---

# 29. Queue không nên biết Domain

Một queue đơn giản:

```python
queue.put(job)
```

không cần biết:

```text
Novel
Chapter
SQLite
Repository
UoW
```

Nó chỉ vận chuyển:

```text
Job
```

Đây là boundary:

```text
Queue
   │
   │ Job
   ▼
Worker
   │
   ▼
Application
```

---

# 30. Kiến trúc tổng thể

Chúng ta hiện có:

```text
                       Queue
                         │
                         ▼
                      Worker
                         │
                         ▼
                 CrawlChapterJob
                         │
                         ▼
                  Crawl Application
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
          Start/Claim         Save Chapter
               │                   │
               └─────────┬─────────┘
                         ▼
                        UoW
             ┌───────────┼─────────────┐
             ▼           ▼             ▼
          Chapter     Chapter       Crawl
           Repo       State Repo    State Repo
             │           │             │
             └───────────┼─────────────┘
                         ▼
                       SQLite
```

---

# 31. Một điểm rất quan trọng: Queue ≠ Database

Không nên nhầm:

```text
Queue
```

với:

```text
Persistence
```

Queue trả lời:

> "Việc gì cần làm?"

Database trả lời:

> "Dữ liệu hiện tại là gì?"

Ví dụ:

```text
Queue:

crawl chapter 501
crawl chapter 502
crawl chapter 503
```

Database:

```text
501 → completed
502 → failed
503 → crawling
```

Hai khái niệm khác nhau.

---

# 32. Queue có thể mất Job

Giả sử:

```text
Queue
   ↓
Worker
   ↓
claim Chapter 502
   ↓
CRASH
```

Queue có thể:

```text
job mất
```

nhưng database:

```text
chapter 502 = crawling
```

Bây giờ Chapter 502 bị "kẹt".

Đây chính là lý do chúng ta cần sau này:

```text
stale job recovery
```

Ví dụ:

```text
status = crawling
started_at = 10:00

current time = 11:00

→ worker chết
→ reset về pending
```

Đây sẽ là một chủ đề rất quan trọng khi xây queue server.

---

# 33. Stale Processing

Ta có thể tìm:

```sql
SELECT *
FROM chapter_crawl_states
WHERE status = 'crawling'
AND started_at < ?;
```

Ví dụ:

```text
crawling > 30 phút
```

→ coi là stale.

Sau đó:

```text
CRAWLING
    ↓
PENDING
```

để worker khác xử lý lại.

---

# 34. Idempotency + Claim + Transaction

Ba thứ này tạo thành nền tảng của crawler concurrent:

```text
             Concurrent Crawler
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   Idempotency     Claim      Transaction
       │            │            │
       ▼            ▼            ▼
    UPSERT      Atomic      Chapter +
                UPDATE      State
```

Nếu thiếu một:

### Không có Idempotency

Retry → duplicate.

### Không có Claim

2 worker → cùng crawl 1 chapter.

### Không có Transaction

Chapter và state có thể không đồng bộ.

---

# 35. Bài tập Buổi 8

## Bài 1 — Domain

Implement:

```python
ChapterCrawlState.start()
ChapterCrawlState.complete()
ChapterCrawlState.fail()
ChapterCrawlState.retry()
```

Test:

```text
PENDING → CRAWLING ✓
CRAWLING → COMPLETED ✓
CRAWLING → FAILED ✓
FAILED → PENDING ✓
COMPLETED → CRAWLING ✗
PENDING → COMPLETED ✗
```

---

## Bài 2 — Repository

Implement:

```python
get()
save()
claim()
```

đặc biệt:

```python
claim() -> bool
```

phải dùng atomic SQL:

```sql
WHERE status = 'pending'
```

---

## Bài 3 — Race Condition

Mô phỏng:

```text
Worker A
Worker B
```

cùng claim:

```text
Chapter 100
```

Kết quả mong muốn:

```text
Worker A → True
Worker B → False
```

hoặc ngược lại.

**Không được:**

```text
True
True
```

---

# 36. Bài tập 4 — Crash Recovery

Mô phỏng:

```text
PENDING
   ↓
CLAIM
   ↓
CRAWLING
   ↓
process crash
```

Database:

```text
CRAWLING
started_at = old timestamp
```

Viết query tìm:

```text
stale crawling chapters
```

và chuyển chúng về:

```text
PENDING
```

---

# 37. Bài tập 5 — Full flow

Xây:

```text
Job
 ↓
Worker
 ↓
Claim
 ↓
Fetch
 ↓
Parse
 ↓
Save Chapter
 ↓
Complete
```

Nếu Fetch lỗi:

```text
Claim
 ↓
Fetch ✗
 ↓
Fail
```

Nếu process crash:

```text
CRAWLING
 ↓
stale
 ↓
PENDING
 ↓
retry
```

---

# 38. Sau Buổi 8, hệ thống đã tiến thêm một bước lớn

Ta không còn chỉ có:

```text
Crawler → SQLite
```

mà đã có:

```text
                   Queue
                     │
                     ▼
                   Worker
                     │
                     ▼
                    Job
                     │
                     ▼
                 Application
                     │
                     ▼
                    UoW
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Novel      Chapter    CrawlState
       Repo        Repo        Repo
                     │
                     ▼
               ChapterState
                     │
                     ▼
                   SQLite
```

Và 4 khái niệm quan trọng nhất hiện tại là:

```text
1. UPSERT
2. Idempotency
3. Atomic Claim
4. Transaction
```

Chúng chính là nền móng để bước sang **Buổi 9 — Queue + Worker Architecture**: thiết kế `Job`, `Queue`, `Worker`, `Retry`, `Ack`, `Failure`, `Dead Letter Queue` và cách nối chúng với `UnitOfWork` mà không làm Application Layer phụ thuộc vào Redis/RQ/Celery.
