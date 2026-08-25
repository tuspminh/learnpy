# DDD Deep Dive — Buổi 20

# Aggregate Design Workshop

Hôm nay chúng ta sẽ **thiết kế Aggregate thực tế** cho hệ thống đọc truyện mà bạn đang xây dựng.

Đây là buổi rất quan trọng vì từ đây chúng ta không chỉ học định nghĩa nữa, mà phải biết trả lời:

> **"Object nào thuộc Aggregate nào, Root là gì, boundary nằm ở đâu và transaction nên bao phủ đến đâu?"**

---

# 1. Bài toán

Giả sử hệ thống có các đối tượng:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

Hệ thống có các chức năng:

```text
Crawler
    ↓
Crawl Story
    ↓
Save Story
    ↓
Save Chapter

User
    ↓
Read Story
    ↓
Update Reading Progress

Admin
    ↓
Create Crawler Job
    ↓
Pause / Resume / Cancel Job
```

Mục tiêu hôm nay:

```text
Object
  ↓
Aggregate
  ↓
Aggregate Root
  ↓
Boundary
  ↓
Transaction
  ↓
Repository
```

---

# 2. Đừng bắt đầu bằng Database

Đây là nguyên tắc cực kỳ quan trọng.

Không bắt đầu bằng:

```text
stories table
chapters table
crawler_jobs table
```

mà bắt đầu bằng:

```text
Business behavior
Business invariant
Consistency requirement
Lifecycle
```

Sau đó mới thiết kế persistence.

---

# 3. Story

Hãy bắt đầu với:

```text
Story
```

Story có:

```text
StoryId
StoryTitle
SourceId
Status
```

Ví dụ:

```python
story = Story(
    id=StoryId("story-1"),
    title=StoryTitle("One Piece"),
    source_id=SourceId("nettruyen"),
)
```

Story có behavior:

```python
story.rename(...)
story.publish()
story.archive()
```

Đây rõ ràng là một Entity.

---

# 4. Story có phải Aggregate Root?

Có.

Ta có:

```text
Story Aggregate
```

và:

```text
Story
  ↑
Aggregate Root
```

Boundary ban đầu:

```text
┌─────────────────────────┐
│ Story Aggregate          │
│                          │
│ Story                    │
│                          │
└─────────────────────────┘
```

---

# 5. Chapter thì sao?

Đây là câu hỏi khó nhất.

Ta có hai khả năng.

### Option A

```text
Story Aggregate
│
└── Chapter
```

### Option B

```text
Story Aggregate

Chapter Aggregate
```

Không được quyết định chỉ vì:

```text
Story có nhiều Chapter
```

Quan hệ 1:N **không đủ để quyết định Aggregate**.

---

# 6. Hãy tìm invariant

Giả sử business rule:

> Một Story không được có hai Chapter cùng số.

Ví dụ:

```text
Story 1
├── Chapter 1
├── Chapter 2
├── Chapter 3
```

Không được:

```text
Story 1
├── Chapter 1
├── Chapter 1  ← invalid
```

Câu hỏi:

> Invariant này có cần được kiểm tra trong cùng một transaction không?

Nếu:

```text
YES
```

thì có lý do để:

```text
Story
└── Chapter
```

cùng Aggregate.

---

# 7. Nhưng hệ thống của chúng ta có vấn đề lớn

Hãy tưởng tượng một truyện:

```text
1000 chapters
```

hoặc:

```text
5000 chapters
```

Nếu Story Aggregate chứa toàn bộ:

```text
Story
├── Chapter 1
├── Chapter 2
├── ...
└── Chapter 5000
```

mỗi lần:

```python
story.add_chapter(...)
```

ta có nguy cơ phải load một Aggregate rất lớn.

Đặc biệt crawler sẽ liên tục thêm chapter.

---

# 8. Crawler làm thay đổi quyết định

Hệ thống của chúng ta có:

```text
Crawler
    ↓
Chapter 1
Chapter 2
Chapter 3
...
```

Crawler có thể chạy hàng nghìn lần.

Nếu:

```text
Chapter ∈ Story Aggregate
```

thì mỗi lần thêm chapter có thể tác động đến Story Aggregate.

Điều này tạo:

```text
Large Aggregate
       +
High write frequency
       +
Concurrency
```

Không tốt.

---

# 9. Vì vậy chọn Option B

Trong hệ thống đọc truyện của chúng ta, tôi khuyến nghị:

```text
Story Aggregate

Chapter Aggregate
```

Thay vì:

```text
Story
└── Chapter
```

---

# 10. Thiết kế Story Aggregate

```text
┌──────────────────────────────┐
│ Story Aggregate              │
│                              │
│ Story                        │
│  ├── StoryId                 │
│  ├── StoryTitle              │
│  ├── SourceId                │
│  └── StoryStatus             │
│                              │
└──────────────────────────────┘
```

Root:

```text
Story
```

Repository:

```python
StoryRepository
```

---

# 11. Chapter Aggregate

```text
┌──────────────────────────────┐
│ Chapter Aggregate            │
│                              │
│ Chapter                      │
│  ├── ChapterId               │
│  ├── StoryId                 │
│  ├── ChapterNumber           │
│  ├── ChapterTitle            │
│  └── Content                 │
│                              │
└──────────────────────────────┘
```

Root:

```text
Chapter
```

Chapter giữ:

```python
story_id: StoryId
```

chứ không giữ:

```python
story: Story
```

---

# 12. Đây chính là Reference by ID

Không:

```python
class Chapter:
    story: Story
```

Mà:

```python
class Chapter:
    story_id: StoryId
```

Quan hệ:

```text
Chapter
   │
   └── story_id
          ↓
       Story
```

Aggregate không nhúng Aggregate khác.

---

# 13. Aggregate boundary

Ta có:

```text
┌───────────────┐
│ Story         │
│ Aggregate     │
│               │
│ Story Root    │
└───────────────┘


┌───────────────┐
│ Chapter       │
│ Aggregate     │
│               │
│ Chapter Root  │
└───────────────┘
```

Hai Aggregate độc lập.

---

# 14. Nhưng invariant Chapter Number thì sao?

Database có thể bảo vệ:

```sql
UNIQUE(story_id, chapter_number)
```

Ví dụ:

```sql
CREATE TABLE chapters (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL,
    chapter_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,

    UNIQUE(story_id, chapter_number)
);
```

Đây là một ví dụ rất quan trọng:

> **Domain invariant không nhất thiết phải được bảo vệ bằng cách nhét tất cả object vào cùng Aggregate.**

Ta có thể kết hợp:

```text
Domain rule
+
Database constraint
```

---

# 15. Tiếp theo: CrawlerSource

```text
CrawlerSource
```

Ví dụ:

```text
NetTruyen
TruyenFull
TruyenYY
```

CrawlerSource có:

```text
SourceId
Name
BaseUrl
Enabled
```

Behavior:

```python
source.enable()
source.disable()
source.change_base_url(...)
```

---

# 16. CrawlerSource là Aggregate

```text
CrawlerSource Aggregate
└── CrawlerSource
```

Root:

```text
CrawlerSource
```

Repository:

```python
CrawlerSourceRepository
```

---

# 17. CrawlerJob

CrawlerJob đại diện cho một lần crawl.

Ví dụ:

```text
CrawlerJob
├── JobId
├── SourceId
├── StoryId
├── Status
├── StartedAt
└── FinishedAt
```

Status:

```text
PENDING
RUNNING
PAUSED
COMPLETED
FAILED
CANCELLED
```

Behavior:

```python
job.start()
job.pause()
job.resume()
job.complete()
job.fail()
job.cancel()
```

---

# 18. CrawlerJob là Aggregate

```text
┌─────────────────────────────┐
│ CrawlerJob Aggregate        │
│                             │
│ CrawlerJob                  │
│   ├── JobId                 │
│   ├── SourceId              │
│   ├── StoryId               │
│   └── Status                │
│                             │
└─────────────────────────────┘
```

Root:

```text
CrawlerJob
```

---

# 19. Không làm thế này

Không nên:

```python
class CrawlerJob:
    source: CrawlerSource
    story: Story
```

Mà:

```python
class CrawlerJob:
    source_id: SourceId
    story_id: StoryId
```

Ta có:

```text
CrawlerJob
    │
    ├── source_id ──→ CrawlerSource
    │
    └── story_id ───→ Story
```

---

# 20. Vì sao?

CrawlerJob không cần:

```text
CrawlerSource Aggregate
```

nằm bên trong nó.

CrawlerJob chỉ cần biết:

```text
source_id
```

Đây là:

> Reference by Identity.

---

# 21. ReadingProgress

Đây là một Aggregate rất thú vị.

Ví dụ:

```text
ReadingProgress
├── UserId
├── StoryId
├── ChapterId
├── UpdatedAt
└── status
```

Behavior:

```python
progress.move_to(chapter_id)
progress.mark_completed()
```

---

# 22. ReadingProgress có nên nằm trong User?

Không nhất thiết.

Không:

```text
User
├── ReadingProgress 1
├── ReadingProgress 2
├── ReadingProgress 3
├── ...
└── ReadingProgress 1000
```

Một user có thể đọc:

```text
100
1000
10000
```

truyện.

User Aggregate sẽ trở nên rất lớn.

---

# 23. Tách ReadingProgress

Ta thiết kế:

```text
User Aggregate

ReadingProgress Aggregate
```

ReadingProgress:

```text
┌─────────────────────────────┐
│ ReadingProgress             │
│                             │
│ UserId                      │
│ StoryId                     │
│ ChapterId                   │
│ UpdatedAt                   │
│                             │
└─────────────────────────────┘
```

---

# 24. ReadingProgress reference

```python
class ReadingProgress:
    user_id: UserId
    story_id: StoryId
    chapter_id: ChapterId
```

Không:

```python
user: User
story: Story
chapter: Chapter
```

---

# 25. User Aggregate

User có:

```text
UserId
Username
Status
```

Behavior:

```python
user.activate()
user.deactivate()
user.change_username(...)
```

Aggregate:

```text
┌─────────────────────┐
│ User Aggregate      │
│                     │
│ User                │
│                     │
└─────────────────────┘
```

Không chứa:

```text
ReadingProgress
```

---

# 26. Tổng kết Aggregate

Chúng ta có:

```text
Story
    ↓
Story Aggregate


Chapter
    ↓
Chapter Aggregate


CrawlerSource
    ↓
CrawlerSource Aggregate


CrawlerJob
    ↓
CrawlerJob Aggregate


User
    ↓
User Aggregate


ReadingProgress
    ↓
ReadingProgress Aggregate
```

Tức là **6 Aggregate**.

---

# 27. Bức tranh tổng thể

```text
┌───────────────────┐
│ Story             │
│ Aggregate         │
└───────────────────┘
        ↑
     story_id
        │
┌───────────────────┐
│ Chapter           │
│ Aggregate         │
└───────────────────┘


┌───────────────────┐
│ CrawlerSource     │
│ Aggregate         │
└───────────────────┘
        ↑
    source_id
        │
┌───────────────────┐
│ CrawlerJob        │
│ Aggregate         │
└───────────────────┘


┌───────────────────┐
│ User              │
│ Aggregate         │
└───────────────────┘
        ↑
      user_id
        │
┌───────────────────┐
│ ReadingProgress   │
│ Aggregate         │
└───────────────────┘
```

---

# 28. Nhưng bây giờ xuất hiện câu hỏi quan trọng

Nếu:

```text
Chapter
```

là Aggregate riêng thì làm sao biết:

```text
Story có tồn tại không?
```

Ví dụ:

```python
Chapter.create(
    story_id=StoryId("abc")
)
```

nhưng Story `abc` không tồn tại.

---

# 29. Đừng vội load Story

Một sai lầm là:

```python
story = story_repository.get(story_id)

chapter = Chapter(...)
```

cho mọi Chapter creation.

Điều này tạo coupling:

```text
Chapter
   ↓
Story Repository
```

và làm transaction lớn hơn.

---

# 30. Có thể dùng Application Layer

Application kiểm tra:

```python
story = story_repo.get(story_id)

if story is None:
    raise StoryNotFound()

chapter = Chapter.create(
    story_id=story.id,
    ...
)
```

Sau đó:

```text
Chapter
```

vẫn độc lập.

---

# 31. Nhưng còn concurrency?

Giữa:

```text
check Story
```

và:

```text
insert Chapter
```

Story có thể bị xóa.

Đây là lý do database foreign key rất hữu ích.

```sql
FOREIGN KEY(story_id)
REFERENCES stories(id)
```

Khi đó:

```text
Domain
+
Application
+
Database constraint
```

phối hợp với nhau.

---

# 32. Aggregate không có nghĩa "mọi invariant phải nằm trong code"

Một hệ thống thực tế có nhiều lớp bảo vệ:

```text
Domain
   ↓
Application
   ↓
Database
```

Ví dụ:

```text
Chapter.number > 0
```

Domain:

```python
if number <= 0:
    raise ValueError(...)
```

Database:

```sql
CHECK(chapter_number > 0)
```

Hai lớp bảo vệ khác nhau.

---

# 33. Transaction cho Add Chapter

Với Chapter Aggregate riêng:

```text
BEGIN
    INSERT chapter
COMMIT
```

Nếu Story tồn tại đã được kiểm tra trước đó, database FK đảm bảo referential integrity.

Đây là transaction rất nhỏ.

---

# 34. Transaction cho Update Reading Progress

```text
BEGIN
    UPDATE reading_progress
    SET chapter_id = ?
COMMIT
```

Không cần:

```text
UPDATE user
UPDATE story
UPDATE chapter
```

Nếu business không yêu cầu.

---

# 35. Transaction cho CrawlerJob

```text
BEGIN
    UPDATE crawler_jobs
    SET status = 'RUNNING'
COMMIT
```

Sau đó crawler chạy:

```text
Network
   ↓
Parse
   ↓
Save chapters
```

Không giữ transaction của Job trong suốt quá trình crawl.

---

# 36. Đây là điểm cực kỳ quan trọng với Crawler

**Sai:**

```text
BEGIN
 ↓
Crawler HTTP request
 ↓
Parse
 ↓
Save chapter
 ↓
HTTP request
 ↓
Parse
 ↓
Save chapter
 ↓
COMMIT
```

**Đúng:**

```text
Crawler HTTP
     ↓
Parse
     ↓
Short transaction
     ↓
Save Chapter
     ↓
COMMIT

Crawler HTTP
     ↓
Parse
     ↓
Short transaction
     ↓
Save Chapter
     ↓
COMMIT
```

---

# 37. CrawlerJob và Chapter không phải cùng Aggregate

Có thể một job crawl:

```text
100 chapters
```

Nếu nhét Chapter vào Job:

```text
CrawlerJob
└── Chapter × 100
```

thì Aggregate rất lớn.

Không nên.

Thay vào đó:

```text
CrawlerJob
```

chỉ quản lý:

```text
status
progress
lifecycle
```

Còn:

```text
Chapter
```

quản lý nội dung chapter.

---

# 38. Đây là Separation of Responsibility

```text
CrawlerJob
    ↓
"Job đang ở trạng thái nào?"

Chapter
    ↓
"Chapter có dữ liệu gì?"

Story
    ↓
"Story có trạng thái gì?"

ReadingProgress
    ↓
"User đang đọc đến đâu?"

User
    ↓
"User đang ở trạng thái nào?"
```

Mỗi Aggregate có một responsibility rõ ràng.

---

# 39. Aggregate không phải Entity Group tùy ý

Đừng nghĩ:

```text
Story + Chapter + User + Progress
```

là Aggregate vì chúng "có liên quan".

Aggregate phải được thiết kế dựa trên:

```text
Consistency
Invariant
Transaction
Lifecycle
Concurrency
```

---

# 40. Một cách rất hay để tìm Aggregate

Với mỗi Entity, hỏi 6 câu:

### 1.

> Nó có business behavior gì?

### 2.

> Nó có invariant gì?

### 3.

> Entity nào phải thay đổi cùng nó?

### 4.

> Thay đổi nào phải atomic?

### 5.

> Nó có lifecycle độc lập không?

### 6.

> Nó có được truy cập độc lập không?

Nếu câu trả lời cho 5 và 6 là:

```text
YES
```

thì rất có khả năng nó nên là Aggregate riêng.

---

# 41. Áp dụng vào Chapter

### Behavior

```text
update_content()
change_title()
```

### Invariant

```text
number > 0
```

### Lifecycle

```text
created
updated
deleted
```

### Access

Crawler có thể truy cập Chapter trực tiếp.

### Concurrency

Nhiều worker có thể update Chapter.

Kết luận:

```text
Chapter = Aggregate Root
```

---

# 42. Áp dụng vào ReadingProgress

### Behavior

```text
move_to()
mark_completed()
```

### Invariant

```text
chapter thuộc story
```

### Lifecycle

```text
created
updated
```

### Access

Reading UI truy cập trực tiếp.

Kết luận:

```text
ReadingProgress = Aggregate Root
```

---

# 43. Aggregate Design cuối cùng

Tôi sẽ chọn:

```text
┌────────────────────┐
│ Story              │
│ Aggregate Root     │
└────────────────────┘

┌────────────────────┐
│ Chapter            │
│ Aggregate Root     │
└────────────────────┘

┌────────────────────┐
│ CrawlerSource      │
│ Aggregate Root     │
└────────────────────┘

┌────────────────────┐
│ CrawlerJob         │
│ Aggregate Root     │
└────────────────────┘

┌────────────────────┐
│ User               │
│ Aggregate Root     │
└────────────────────┘

┌────────────────────┐
│ ReadingProgress    │
│ Aggregate Root     │
└────────────────────┘
```

Đây là một thiết kế khá **small Aggregate**.

---

# 44. Repository tương ứng

Ta có:

```python
class StoryRepository:
    ...


class ChapterRepository:
    ...


class CrawlerSourceRepository:
    ...


class CrawlerJobRepository:
    ...


class UserRepository:
    ...


class ReadingProgressRepository:
    ...
```

Một Aggregate Root thường có Repository riêng.

---

# 45. Không tạo Repository cho Value Object

Ví dụ:

```text
StoryTitle
ChapterNumber
SourceUrl
```

không nên có:

```python
StoryTitleRepository
ChapterNumberRepository
SourceUrlRepository
```

Vì chúng không có lifecycle độc lập.

Chúng sống bên trong Aggregate.

---

# 46. Ví dụ Domain Model

```python
class Story:
    def __init__(
        self,
        story_id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
    ):
        self.id = story_id
        self.title = title
        self.source_id = source_id
        self.status = StoryStatus.DRAFT

    def publish(self):
        if self.status == StoryStatus.ARCHIVED:
            raise DomainError(
                "Archived story cannot be published"
            )

        self.status = StoryStatus.PUBLISHED
```

---

# 47. Chapter

```python
class Chapter:
    def __init__(
        self,
        chapter_id: ChapterId,
        story_id: StoryId,
        number: ChapterNumber,
        title: StoryTitle,
        content: str,
    ):
        self.id = chapter_id
        self.story_id = story_id
        self.number = number
        self.title = title
        self.content = content
```

Notice:

```python
story_id: StoryId
```

chứ không phải:

```python
story: Story
```

---

# 48. CrawlerJob

```python
class CrawlerJob:
    def __init__(
        self,
        job_id: JobId,
        source_id: SourceId,
        story_id: StoryId,
    ):
        self.id = job_id
        self.source_id = source_id
        self.story_id = story_id
        self.status = JobStatus.PENDING

    def start(self):
        if self.status != JobStatus.PENDING:
            raise DomainError(
                "Job cannot start"
            )

        self.status = JobStatus.RUNNING
```

---

# 49. ReadingProgress

```python
class ReadingProgress:
    def __init__(
        self,
        user_id: UserId,
        story_id: StoryId,
        chapter_id: ChapterId,
    ):
        self.user_id = user_id
        self.story_id = story_id
        self.chapter_id = chapter_id

    def move_to(self, chapter_id):
        self.chapter_id = chapter_id
```

Sau này ta sẽ làm invariant:

```text
chapter.story_id == progress.story_id
```

đúng cách ở Application/Domain tùy yêu cầu consistency.

---

# 50. Một insight quan trọng

Bạn có thể nhận ra:

```text
Entity
```

không đồng nghĩa:

```text
Aggregate Root
```

Ví dụ nếu chúng ta thiết kế:

```text
Order
├── OrderItem
└── Address
```

thì:

```text
Order = Aggregate Root
OrderItem = Entity bên trong Aggregate
Address = Value Object
```

Trong workshop hôm nay:

```text
Chapter
```

được chọn làm:

```text
Aggregate Root
```

vì nó có lifecycle và consistency riêng.

---

# 51. Aggregate Root là cổng vào

Với Aggregate:

```text
Story
```

client gọi:

```python
story.publish()
```

chứ không nên:

```python
story.status = "PUBLISHED"
```

Với Aggregate:

```text
CrawlerJob
```

gọi:

```python
job.pause()
```

chứ không:

```python
job.status = "PAUSED"
```

Với:

```text
ReadingProgress
```

gọi:

```python
progress.move_to(chapter_id)
```

thay vì tùy ý sửa:

```python
progress.chapter_id = ...
```

---

# 52. Đây chính là Encapsulation

Aggregate Root kiểm soát:

```text
state
+
behavior
+
invariant
```

Do đó:

```text
Aggregate Root
       ↓
Controlled mutation
```

thay vì:

```text
public mutable data
```

---

# 53. Bản thiết kế kiến trúc

Toàn bộ hệ thống:

```text
                    Application
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
   Story UseCase    Crawl UseCase    Reading UseCase
       │                 │                 │
       ↓                 ↓                 ↓
    Story Repo      CrawlerJob Repo   Progress Repo
       │                 │                 │
       ↓                 ↓                 ↓
   Story Aggregate  Job Aggregate   Progress Aggregate


   Chapter Aggregate
          ↑
     Chapter Repo


   CrawlerSource Aggregate
          ↑
     Source Repo


   User Aggregate
          ↑
      User Repo
```

---

# 54. Database có thể tương ứng

```text
stories
chapters
crawler_sources
crawler_jobs
users
reading_progress
```

Nhưng nhớ:

> **Database table không phải Aggregate.**

Hai thứ có thể trùng nhau về cấu trúc, nhưng concept khác nhau.

---

# 55. Transaction Map

Ta có thể thiết kế transaction như sau:

```text
Create Story
    ↓
Story Transaction


Add Chapter
    ↓
Chapter Transaction


Start CrawlerJob
    ↓
CrawlerJob Transaction


Save ReadingProgress
    ↓
ReadingProgress Transaction


Update User
    ↓
User Transaction
```

Các transaction nhỏ.

---

# 56. Cross-Aggregate operation

Ví dụ:

```text
Crawler hoàn thành
```

Có thể:

```text
CrawlerJob
    ↓
complete()
    ↓
commit
    ↓
ChapterCreated events
    ↓
Chapter persistence
```

Hoặc tùy thiết kế:

```text
CrawlerJob
    ↓
complete()
+
save chapters
```

trong cùng Application workflow nhưng **không nhất thiết** phải cùng Aggregate.

---

# 57. Một Use Case có thể chạm nhiều Aggregate

Đây là điểm rất quan trọng.

DDD **không cấm**:

```text
Use Case
   ↓
Story
   ↓
Chapter
   ↓
ReadingProgress
```

Nhưng:

```text
Use Case
```

là nơi orchestration xảy ra.

Không biến các Aggregate thành object graph khổng lồ.

---

# 58. Aggregate chỉ nên bảo vệ invariant của chính nó

Ví dụ:

```text
Story
```

chịu trách nhiệm:

```text
StoryStatus
StoryTitle
```

Chapter:

```text
ChapterNumber
ChapterContent
```

ReadingProgress:

```text
CurrentChapter
```

CrawlerJob:

```text
JobStatus
```

Không để:

```text
Story
```

quản lý:

```text
CrawlerJob
ReadingProgress
User
```

chỉ vì chúng có quan hệ.

---

# 59. Aggregate Design Checklist

Trước khi tạo Aggregate, hãy hỏi:

```text
□ Root là gì?
□ Business behavior là gì?
□ Invariant là gì?
□ Entity nào phải thay đổi cùng Root?
□ Có cần atomicity không?
□ Transaction có lớn không?
□ Aggregate có load thường xuyên không?
□ Có concurrency cao không?
□ Lifecycle có độc lập không?
□ Có thể reference bằng ID không?
```

Nếu bạn dùng checklist này thường xuyên, Aggregate Design sẽ tiến bộ rất nhanh.

---

# 60. Kết luận Phần IV

Sau Buổi 20, bạn đã đi qua toàn bộ:

```text
Buổi 16
Aggregate
    ↓
Boundary
    ↓
Consistency
    ↓
Transaction


Buổi 17
Aggregate Root
    ↓
Encapsulation
    ↓
Behavior


Buổi 18
Aggregate Design
    ↓
Large vs Small
    ↓
Reference by ID


Buổi 19
Aggregate + Transaction
    ↓
Atomicity
    ↓
Concurrency
    ↓
Unit of Work


Buổi 20
Aggregate Workshop
    ↓
Real-world design
```

Với hệ thống đọc truyện, mô hình hiện tại là:

```text
┌──────────────────┐
│ Story            │
│ Aggregate        │
└──────────────────┘

┌──────────────────┐
│ Chapter          │
│ Aggregate        │
└──────────────────┘

┌──────────────────┐
│ CrawlerSource    │
│ Aggregate        │
└──────────────────┘

┌──────────────────┐
│ CrawlerJob       │
│ Aggregate        │
└──────────────────┘

┌──────────────────┐
│ User             │
│ Aggregate        │
└──────────────────┘

┌──────────────────┐
│ ReadingProgress  │
│ Aggregate        │
└──────────────────┘
```

**Insight quan trọng nhất của Buổi 20:**

> **Aggregate không được thiết kế dựa trên quan hệ giữa các bảng; Aggregate được thiết kế dựa trên business invariant và consistency boundary.**

Và một nguyên tắc bạn nên thuộc lòng:

```text
Don't ask:
"Objects nào có quan hệ với nhau?"

Ask:
"Objects nào phải nhất quán với nhau trong cùng một transaction?"
```

Đó mới là tư duy **DDD Aggregate Design**.
