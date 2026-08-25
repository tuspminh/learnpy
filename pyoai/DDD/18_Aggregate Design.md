# DDD Deep Dive — Buổi 18

# Aggregate Design

Buổi 16 chúng ta học **Aggregate là gì**.

Buổi 17 học **Aggregate Root và cách Root bảo vệ Aggregate**.

Hôm nay là một bài khó hơn:

> **Làm thế nào quyết định cái gì nằm trong một Aggregate?**

Đây mới là phần thực sự quan trọng của Aggregate Design.

---

# 1. Sai lầm lớn nhất: "gom tất cả vào một Aggregate"

Với hệ thống đọc truyện, ta có:

```text
Story
├── Chapter
├── Comment
├── Rating
├── Bookmark
├── ReadingProgress
├── User
├── CrawlerSource
└── CrawlerJob
```

Người mới học DDD rất dễ thiết kế:

```text
Story Aggregate
│
├── Story
├── Chapter
├── Comment
├── Rating
├── Bookmark
├── ReadingProgress
├── User
├── CrawlerSource
└── CrawlerJob
```

Đây là **God Aggregate**.

Thiết kế này rất nguy hiểm.

---

# 2. Aggregate không phải "mọi thứ liên quan"

Một Aggregate không được thiết kế dựa trên câu hỏi:

> "Object này có liên quan đến Story không?"

Mà phải hỏi:

> **"Những object nào cần được nhất quán cùng nhau để bảo vệ một business invariant?"**

Đây là câu hỏi quan trọng nhất của Buổi 18.

---

# 3. Công thức cơ bản

Khi thiết kế Aggregate:

```text
Business Invariant
        ↓
Ai cần biết invariant này?
        ↓
Những object nào phải thay đổi cùng nhau?
        ↓
Aggregate Boundary
        ↓
Aggregate Root
```

Không đi theo hướng:

```text
Database relationship
        ↓
Aggregate
```

---

# 4. Aggregate quá lớn

Ví dụ:

```text
Story Aggregate
│
├── Story
├── 5000 Chapter
├── 10000 Comment
├── 50000 Rating
├── 1000 Bookmark
└── ReadingProgress
```

Mỗi lần:

```python
story = story_repository.get(story_id)
```

có thể dẫn tới việc phải load rất nhiều dữ liệu.

Đây là dấu hiệu Aggregate quá lớn.

---

# 5. Aggregate quá lớn gây ra vấn đề gì?

### Performance

```text
SELECT ...
JOIN ...
JOIN ...
JOIN ...
```

→ dữ liệu rất lớn.

### Memory

```text
Story
 + thousands of objects
```

→ tốn RAM.

### Transaction

Một thay đổi nhỏ:

```text
rename Story
```

có thể kéo theo Aggregate rất lớn.

### Concurrency

Hai request cùng sửa:

```text
Story
```

có thể tranh chấp trên cùng Aggregate.

---

# 6. Ví dụ concurrency

Giả sử:

```text
Story #100
```

có:

```text
5000 chapters
```

User A:

```text
rename Story
```

User B:

```text
add Chapter
```

Nếu tất cả là một Aggregate lớn:

```text
Story Aggregate #100
```

thì cả hai operation đều đang tác động vào cùng một consistency boundary.

Concurrency trở nên khó hơn.

---

# 7. Aggregate quá nhỏ

Ngược lại, chúng ta có thể tách quá mức:

```text
Story Aggregate
    Story

Chapter Aggregate
    Chapter
```

Giả sử business invariant:

> Một Story không được có hai Chapter cùng `ChapterNumber`.

Bây giờ:

```text
Story Aggregate
```

không biết các Chapter.

`Chapter Aggregate` cũng chỉ biết chính nó.

Không Aggregate nào đủ thông tin để bảo vệ:

```text
unique ChapterNumber within Story
```

---

# 8. Đây là dấu hiệu Aggregate quá nhỏ

Nếu một business invariant yêu cầu:

```text
A + B
```

nhưng:

```text
A → Aggregate A
B → Aggregate B
```

thì bạn phải xem xét:

```text
Có nên đưa A và B vào cùng Aggregate?
```

hoặc:

```text
Có thể thay đổi business rule
để eventual consistency được không?
```

Đây là quyết định thiết kế, không có một câu trả lời tuyệt đối.

---

# 9. Aggregate Design thực chất là trade-off

Ta có:

```text
Aggregate quá lớn
        ↓
Consistency mạnh
nhưng
Performance kém
Concurrency kém
```

và:

```text
Aggregate quá nhỏ
        ↓
Performance tốt
Concurrency tốt
nhưng
Consistency phức tạp
```

Mục tiêu:

```text
       ┌─────────────────────┐
       │     JUST ENOUGH     │
       │     CONSISTENCY     │
       └─────────────────────┘
```

---

# 10. Nguyên tắc quan trọng

> **Model true invariants, not relationships.**

Đừng nhìn:

```text
Story 1 ─── N Chapter
```

rồi kết luận:

```text
Story Aggregate
└── Chapter
```

Database relationship:

```text
Story 1:N Chapter
```

không tự động quyết định Aggregate boundary.

---

# 11. Database relationship ≠ Aggregate relationship

Ví dụ database:

```text
stories
   │
   └── chapters
```

có thể là:

```text
Story Aggregate
```

nhưng cũng có thể là:

```text
Story Aggregate
Chapter Aggregate
```

với:

```text
chapter.story_id
```

Điểm quyết định là:

```text
Business consistency
```

không phải:

```text
Foreign key
```

---

# 12. Khi nào Story và Chapter cùng Aggregate?

Giả sử business yêu cầu:

```text
ChapterNumber phải unique trong Story
```

và:

```text
Story.add_chapter()
```

phải kiểm tra uniqueness ngay lập tức.

Khi đó:

```text
┌─────────────────────────┐
│ Story Aggregate         │
│                         │
│ Story ← Root            │
│   ├── Chapter           │
│   ├── Chapter           │
│   └── Chapter           │
└─────────────────────────┘
```

có thể hợp lý.

---

# 13. Nhưng hãy thay đổi business rule

Giả sử hệ thống crawler có hàng trăm nghìn chapter.

Business nói:

> Chapter number chỉ cần unique theo `(story_id, chapter_number)` ở database.

Không có business operation nào yêu cầu load toàn bộ Story để thêm Chapter.

Ta có thể thiết kế:

```text
Story Aggregate
    Story

Chapter Aggregate
    Chapter
    story_id
```

và database:

```sql
UNIQUE(story_id, chapter_number)
```

Bây giờ hai Aggregate có thể tồn tại độc lập.

---

# 14. Đây là một insight rất quan trọng

Có những invariant:

```text
Domain invariant
```

và có những constraint:

```text
Data integrity constraint
```

Ví dụ:

```sql
UNIQUE(story_id, chapter_number)
```

có thể đảm bảo database không chứa duplicate.

Nhưng nếu business behavior cần:

```text
Story.add_chapter()
```

quyết định nhiều thứ liên quan tới Chapter, thì database constraint không thay thế được Aggregate.

---

# 15. Aggregate không phải nơi duy nhất có constraint

Một hệ thống tốt có thể có:

```text
Domain
    ↓
Business invariant

Database
    ↓
Data integrity
```

Ví dụ:

```text
Domain:
ChapterNumber > 0

Database:
CHECK(chapter_number > 0)
```

và:

```text
Domain:
Story không cho phép duplicate chapter

Database:
UNIQUE(story_id, chapter_number)
```

Hai lớp bảo vệ có thể cùng tồn tại.

---

# 16. Khi nào tách Aggregate?

Có một số dấu hiệu rất mạnh.

### Dấu hiệu 1

Hai object không cần thay đổi trong cùng transaction.

```text
A
B
```

có thể tách.

---

### Dấu hiệu 2

Chúng có lifecycle độc lập.

Ví dụ:

```text
Story
```

có lifecycle:

```text
DRAFT → PUBLISHED → ARCHIVED
```

Trong khi:

```text
CrawlerJob
```

có lifecycle:

```text
QUEUED → RUNNING → COMPLETED
```

Hai lifecycle độc lập.

Không có lý do mặc định để chúng cùng Aggregate.

---

# 17. Dấu hiệu 3 — Concurrency khác nhau

Ví dụ:

```text
Story
```

được chỉnh sửa ít.

Nhưng:

```text
ReadingProgress
```

được cập nhật hàng nghìn lần mỗi phút.

Nếu:

```text
Story + ReadingProgress
```

cùng Aggregate:

```text
Story Aggregate
```

sẽ trở thành concurrency hotspot.

Tách ra thường hợp lý hơn:

```text
Story Aggregate

ReadingProgress Aggregate
```

---

# 18. Dấu hiệu 4 — Kích thước khác nhau

Ví dụ:

```text
Story
```

nhỏ.

Nhưng:

```text
Comments
```

có thể lên tới:

```text
100,000
```

Không nên:

```text
Story
 └── 100,000 Comments
```

chỉ vì:

```text
Comment.story_id
```

---

# 19. Dấu hiệu 5 — Access pattern khác nhau

Story được đọc:

```text
GET /stories/123
```

Chapter được đọc:

```text
GET /stories/123/chapters/500
```

ReadingProgress:

```text
GET /users/1/reading-progress/123
```

Nếu mỗi loại được truy cập độc lập rất nhiều:

```text
Aggregate boundaries
```

nên phản ánh cách hệ thống thực sự hoạt động.

---

# 20. Reference by ID

Đây là nguyên tắc cực kỳ quan trọng.

Nếu hai Aggregate khác nhau:

```text
Story Aggregate
```

và:

```text
User Aggregate
```

không nên:

```python
class Story:
    user: User
```

thường nên:

```python
class Story:
    user_id: UserId
```

---

# 21. Tại sao reference bằng ID?

Vì:

```text
Story Aggregate
```

không cần sở hữu:

```text
User Aggregate
```

Ta chỉ nói:

```text
Story.author_id = UserId(...)
```

Quan hệ:

```text
Story
  │
  └── author_id ─────────→ User
```

là một **reference**, không phải object embedding.

---

# 22. Tránh Aggregate graph

Thiết kế nguy hiểm:

```text
Story
 └── User
      └── ReadingProgress
           └── Story
                └── User
                     └── ...
```

Đây là object graph khổng lồ.

Thiết kế DDD tốt hơn:

```text
Story
 └── author_id

User
 └── UserId

ReadingProgress
 ├── user_id
 └── story_id
```

Mỗi Aggregate có boundary rõ ràng.

---

# 23. Reference by ID không có nghĩa là không có relationship

Ta vẫn có:

```python
story.author_id
```

và:

```python
reading_progress.story_id
```

Quan hệ vẫn tồn tại.

Chỉ là:

```text
Domain ownership
```

không bị trộn với:

```text
reference
```

---

# 24. Một Aggregate không nên nhúng Aggregate khác

Ví dụ:

```python
class Story:
    author: User
```

nếu `User` là Aggregate Root riêng.

Thường không nên.

Thay bằng:

```python
class Story:
    author_id: UserId
```

Tương tự:

```python
class ReadingProgress:
    user_id: UserId
    story_id: StoryId
```

---

# 25. Nhưng có ngoại lệ?

Có thể có những **Value Object** hoặc snapshot data được nhúng.

Ví dụ:

```python
class Story:
    author_name: AuthorName
```

nếu đây chỉ là:

```text
snapshot
```

và không phải `User Aggregate`.

Điều quan trọng là phân biệt:

```text
Entity/Aggregate reference
```

với:

```text
Value Object / snapshot
```

---

# 26. Aggregate không phải object graph

Đây là mental model rất quan trọng:

### Object graph

```text
Story
 ├── User
 │    └── ...
 ├── Chapter
 │    └── ...
 └── Rating
      └── User
```

### Aggregate graph

```text
Story Aggregate ──author_id──→ User Aggregate

Story Aggregate ←story_id── ReadingProgress Aggregate

Chapter Aggregate ──story_id──→ Story Aggregate
```

Aggregate graph thường:

```text
loose coupling
```

hơn.

---

# 27. Một ví dụ với hệ thống đọc truyện

Ban đầu:

```text
Story
├── Chapter
├── User
├── ReadingProgress
├── CrawlerJob
└── CrawlerSource
```

Thiết kế tốt hơn có thể là:

```text
Story Aggregate
    Story

Chapter Aggregate
    Chapter
    story_id

User Aggregate
    User

ReadingProgress Aggregate
    ReadingProgress
    user_id
    story_id

CrawlerSource Aggregate
    CrawlerSource

CrawlerJob Aggregate
    CrawlerJob
    source_id
```

Đây là **một khả năng**.

Không phải đáp án duy nhất.

---

# 28. Tại sao Chapter có thể là Aggregate riêng?

Hãy xem use case:

```text
Crawler
    ↓
crawl chapter
    ↓
save Chapter
```

Crawler không cần:

```text
load Story Aggregate
```

rồi:

```python
story.add_chapter(chapter)
```

cho mỗi chapter.

Nếu crawler xử lý:

```text
100,000 chapters
```

việc load Story Aggregate khổng lồ sẽ rất tệ.

---

# 29. Reference by ID giúp crawler

Thay vì:

```python
story = story_repository.get(story_id)

story.add_chapter(chapter)

story_repository.save(story)
```

có thể:

```python
chapter = Chapter.create(
    story_id=story_id,
    number=number,
    ...
)

chapter_repository.save(chapter)
```

Database:

```sql
INSERT INTO chapters (...)
```

và:

```sql
UNIQUE(story_id, chapter_number)
```

bảo vệ data integrity.

---

# 30. Nhưng có một câu hỏi

Nếu Chapter là Aggregate riêng:

> Ai đảm bảo business rule "Story phải có ít nhất một Chapter trước khi publish"?

Bây giờ:

```text
Story Aggregate
```

không sở hữu Chapters.

Đây là vấn đề thực sự.

Có vài cách.

---

# 31. Cách 1 — Đưa Chapter vào Story Aggregate

Nếu invariant rất quan trọng và phải synchronous:

```text
Story
 ├── Chapter
 └── Chapter
```

đây có thể là thiết kế phù hợp.

---

# 32. Cách 2 — Domain Service / Application orchestration

Nếu business cho phép:

```text
Story
```

được publish sau khi hệ thống kiểm tra:

```text
Chapter count > 0
```

Application có thể phối hợp:

```text
Story
   ↓
ChapterRepository
   ↓
check
   ↓
story.publish()
```

Nhưng cần cẩn thận về race conditions và transaction boundary.

---

# 33. Cách 3 — Eventual Consistency

Nếu business cho phép:

```text
Story Published
```

rồi sau đó hệ thống cập nhật một read model hoặc workflow khác:

```text
StoryPublished
       ↓
check chapter availability
       ↓
...
```

thì có thể tách Aggregate.

Nhưng lúc này business semantics thay đổi:

```text
strong consistency
```

thành:

```text
eventual consistency
```

---

# 34. Không có Aggregate Design "đúng tuyệt đối"

Đây là điểm bạn cần nhớ.

DDD không nói:

> Story và Chapter **phải** cùng Aggregate.

DDD hỏi:

> **Business invariant nào cần strong consistency?**

Từ đó mới quyết định boundary.

---

# 35. Aggregate quá lớn thường xuất hiện vì database thinking

Ví dụ database:

```text
stories
chapters
comments
ratings
```

có foreign keys:

```text
chapters.story_id
comments.story_id
ratings.story_id
```

Người thiết kế nghĩ:

```text
FK → thuộc Story
```

rồi:

```text
Story Aggregate
 ├── Chapter
 ├── Comment
 └── Rating
```

Đây là suy luận sai.

---

# 36. DDD thinking

Thay vì:

```text
Database relationship
        ↓
Aggregate
```

hãy làm:

```text
Business invariant
        ↓
Consistency requirement
        ↓
Transaction requirement
        ↓
Aggregate
```

---

# 37. Aggregate size heuristic

Không có quy tắc:

```text
Aggregate <= 5 objects
```

hoặc:

```text
Aggregate <= 1MB
```

Không có con số cố định.

Nhưng một heuristic tốt:

> **Aggregate nên đủ nhỏ để transaction và concurrency manageable.**

---

# 38. "Small Aggregate" không có nghĩa "ít field"

Ví dụ:

```python
class User:
    id
    username
    email
    password_hash
    status
    preferences
```

có thể có nhiều field nhưng vẫn là Aggregate nhỏ.

Trong khi:

```python
class Story:
    chapters: list[Chapter]
```

có thể chỉ vài field nhưng 100,000 Chapter.

Độ lớn không chỉ là số property.

---

# 39. Aggregate size còn phụ thuộc cardinality

Ví dụ:

```text
Story
 └── Chapter × 10
```

khác hoàn toàn:

```text
Story
 └── Chapter × 100,000
```

Business model giống nhau nhưng operational characteristics khác nhau.

---

# 40. Một Aggregate có thể thay đổi theo thời gian

Ban đầu:

```text
Story
 └── Chapter
```

là hợp lý.

Sau này hệ thống có:

```text
1 million stories
100 million chapters
```

và crawler scale lớn.

Bạn có thể refactor thành:

```text
Story Aggregate
Chapter Aggregate
```

mà không nhất thiết thay đổi toàn bộ domain concept.

Aggregate boundary là một **design decision**, không phải chân lý bất biến.

---

# 41. Aggregate và concurrency

Giả sử:

```text
Story Aggregate
```

có:

```text
Chapter count
Current reading chapter
Rating
Comments
```

User A:

```text
update rating
```

User B:

```text
update reading progress
```

User C:

```text
add comment
```

Nếu tất cả là một Aggregate:

```text
same consistency boundary
```

thì concurrency rất cao.

Tách:

```text
Story
Rating
ReadingProgress
Comment
```

có thể giảm contention.

---

# 42. Aggregate và transaction

Nếu:

```text
A + B
```

phải commit atomically:

```text
A
+
B
```

có thể cùng Aggregate.

Nếu:

```text
A
```

và:

```text
B
```

không cần atomic:

```text
tách Aggregate
```

thường có lợi.

---

# 43. Một heuristic rất mạnh

Hãy hỏi:

> **"Nếu A thay đổi, B có bắt buộc phải thay đổi trong cùng một transaction không?"**

Nếu:

```text
YES
```

→ có lý do để xem xét cùng Aggregate.

Nếu:

```text
NO
```

→ có lý do để tách.

Không phải quy tắc tuyệt đối, nhưng rất hữu ích.

---

# 44. Một heuristic khác

Hỏi:

> **"Nếu A được load, có thực sự cần B để thực hiện business behavior không?"**

Nếu:

```text
Story.publish()
```

không cần toàn bộ Chapters:

```text
Chapter
```

có thể không cần nằm trong Story Aggregate.

Nhưng nếu:

```text
Story.publish()
```

phải kiểm tra:

```text
has_at_least_one_chapter
```

thì relationship trở nên quan trọng hơn.

---

# 45. Reference by ID — Python

Ví dụ:

```python
@dataclass(frozen=True)
class StoryId:
    value: UUID
```

và:

```python
@dataclass
class ReadingProgress:
    user_id: UserId
    story_id: StoryId
    chapter_id: ChapterId
```

Không cần:

```python
user: User
story: Story
chapter: Chapter
```

---

# 46. Tại sao cách này rất hợp với Python?

Python rất dễ tạo object graph:

```python
story.user.progress.story...
```

Nhưng chính sự tiện lợi này có thể khiến Domain Model bị coupling.

Reference bằng ID buộc chúng ta suy nghĩ rõ:

```text
Aggregate boundary
```

---

# 47. Repository cũng phản ánh Aggregate Boundary

Nếu:

```text
Story Aggregate
```

và:

```text
Chapter Aggregate
```

thì:

```python
class StoryRepository:
    ...

class ChapterRepository:
    ...
```

là hợp lý.

Nếu:

```text
Story + Chapter
```

cùng Aggregate:

```python
class StoryRepository:
    ...
```

có thể đủ.

---

# 48. Đây là cách Aggregate ảnh hưởng persistence

### Một Aggregate:

```text
Story
 └── Chapter
```

Repository:

```text
StoryRepository
```

### Hai Aggregate:

```text
Story

Chapter
```

Repositories:

```text
StoryRepository
ChapterRepository
```

Database có thể vẫn là:

```text
stories
chapters
```

Nhưng Domain boundary khác nhau.

---

# 49. Aggregate không quyết định database schema một cách máy móc

Ví dụ:

```text
Story Aggregate
Story
Chapter
```

có thể lưu:

```text
stories
chapters
```

hoặc:

```text
story_document
```

hoặc nhiều bảng.

Persistence model:

```text
Infrastructure concern
```

Aggregate:

```text
Domain concern
```

Chúng liên quan nhưng không đồng nhất.

---

# 50. Một ví dụ về User

Giả sử:

```text
User
```

có:

```text
username
email
status
```

và:

```text
ReadingProgress
```

có:

```text
user_id
story_id
chapter_id
```

Không nên:

```text
User Aggregate
├── ReadingProgress × 5000
```

chỉ vì ReadingProgress thuộc User.

Tại sao?

```text
ReadingProgress
```

có lifecycle và access pattern riêng.

---

# 51. ReadingProgress thường là Aggregate riêng

```text
┌──────────────────────────┐
│ ReadingProgress          │
│                          │
│ ReadingProgress ← Root   │
│ user_id                  │
│ story_id                 │
│ chapter_id               │
└──────────────────────────┘
```

Một operation:

```python
progress.move_to(chapter_id)
```

không cần load:

```text
User
Story
Chapter 1...N
```

---

# 52. CrawlerJob cũng rất phù hợp làm Aggregate riêng

Ví dụ:

```text
CrawlerJob
```

có lifecycle:

```text
QUEUED
   ↓
RUNNING
   ↓
COMPLETED
```

hoặc:

```text
RUNNING
   ↓
FAILED
```

Root:

```text
CrawlerJob
```

bảo vệ transition.

Không cần:

```text
Story Aggregate
```

sở hữu Job.

---

# 53. CrawlerSource

Có thể:

```text
CrawlerSource Aggregate
```

với:

```text
source_id
name
base_url
status
configuration
```

và:

```text
CrawlerJob
    source_id
```

reference bằng ID.

Không:

```python
job.source = crawler_source
```

nếu `CrawlerSource` là Aggregate khác.

---

# 54. Aggregate Graph cho hệ thống của chúng ta

Một mô hình có thể là:

```text
                   ┌───────────────┐
                   │ User          │
                   │ Aggregate     │
                   └───────┬───────┘
                           │ user_id
                           ↓
┌──────────────┐    ┌──────────────────┐
│ Story        │    │ ReadingProgress  │
│ Aggregate    │←───│ Aggregate        │
└──────┬───────┘    └──────────────────┘
       │
       │ story_id
       ↓
┌──────────────┐
│ Chapter      │
│ Aggregate    │
└──────────────┘


┌──────────────────┐
│ CrawlerSource    │
│ Aggregate        │
└────────┬─────────┘
         │ source_id
         ↓
┌──────────────────┐
│ CrawlerJob       │
│ Aggregate        │
└──────────────────┘
```

Đây là **một thiết kế có thể có**.

---

# 55. Một Aggregate không nên biết quá nhiều Aggregate khác

Ví dụ tệ:

```python
class Story:
    user: User
    crawler_source: CrawlerSource
    crawler_job: CrawlerJob
    reading_progress: ReadingProgress
```

Story trở thành trung tâm của toàn hệ thống.

Đó là:

```text
high coupling
```

Thiết kế tốt hơn:

```python
class Story:
    author_id: UserId
```

và:

```python
class ReadingProgress:
    user_id: UserId
    story_id: StoryId
```

---

# 56. Root có thể reference ID của Aggregate khác

Đây là điều hoàn toàn bình thường:

```python
@dataclass
class Story:
    id: StoryId
    author_id: UserId
```

hoặc:

```python
@dataclass
class CrawlerJob:
    id: CrawlerJobId
    source_id: CrawlerSourceId
```

Đây là:

> **Reference by identity**

không phải:

> **Object embedding**

---

# 57. Khi nào không nên tách?

Nếu bạn thấy mình phải liên tục làm:

```text
load Aggregate A
load Aggregate B
load Aggregate C
validate A+B+C
save A
save B
save C
```

cho **mọi operation**, có thể Aggregate đang bị tách quá nhỏ.

Ví dụ:

```text
Story
Chapter
```

tách ra nhưng 90% command đều cần:

```text
Story + Chapter
```

và phải giữ strong consistency.

Có thể boundary đang sai.

---

# 58. "Smallest useful aggregate"

Một cách diễn đạt rất hay:

> **Aggregate should be as small as possible, but as large as necessary to enforce invariants.**

Tiếng Việt:

> **Aggregate nên nhỏ nhất có thể, nhưng đủ lớn để bảo vệ các invariant cần strong consistency.**

Hãy nhớ câu này.

---

# 59. Quy trình thiết kế Aggregate

Khi gặp một Domain mới, làm theo:

### Bước 1

Liệt kê:

```text
Entities
Value Objects
```

### Bước 2

Liệt kê:

```text
Business invariants
```

### Bước 3

Với mỗi invariant:

```text
Ai cần biết?
```

### Bước 4

Xác định:

```text
Object nào cần thay đổi atomic?
```

### Bước 5

Tạo:

```text
Aggregate Boundary
```

### Bước 6

Chọn:

```text
Aggregate Root
```

### Bước 7

Kiểm tra:

```text
Aggregate có quá lớn?
```

### Bước 8

Kiểm tra:

```text
Có Aggregate nào đang bị nhúng không?
```

---

# 60. Áp dụng quy trình vào Story

### Bước 1

Entities:

```text
Story
Chapter
```

### Bước 2

Invariant:

```text
ChapterNumber unique trong Story
```

### Bước 3

Ai cần biết?

```text
Story
```

### Bước 4

Cần atomic?

```text
Add Chapter
+
check uniqueness
```

### Bước 5

Boundary:

```text
Story + Chapter
```

### Bước 6

Root:

```text
Story
```

Kết quả:

```text
Story Aggregate
└── Story
    └── Chapters
```

---

# 61. Nhưng nếu có 1 triệu Chapter?

Quay lại bước 7:

```text
Aggregate quá lớn?
```

Có.

Tiếp tục hỏi:

```text
Chapter có lifecycle độc lập?
```

Có.

```text
Chapter có được crawler cập nhật độc lập?
```

Có.

```text
Story cần load toàn bộ Chapter?
```

Không.

→ Có lý do mạnh để tách:

```text
Story Aggregate
Chapter Aggregate
```

và:

```text
Chapter.story_id
```

---

# 62. Đây là DDD thực sự

DDD không phải:

```text
Entity
Value Object
Aggregate
Repository
```

rồi áp dụng mechanical.

DDD là:

```text
Business
   ↓
Invariants
   ↓
Consistency
   ↓
Boundaries
   ↓
Model
```

Đó mới là tư duy cần luyện.

---

# 63. Checklist cuối Buổi 18

Trước khi tạo Aggregate, hãy hỏi 10 câu:

```text
1. Business invariant là gì?

2. Object nào bảo vệ invariant?

3. Những object nào cần thay đổi atomic?

4. Có cần strong consistency không?

5. Có cần cùng transaction không?

6. Aggregate có quá lớn không?

7. Aggregate có quá nhỏ không?

8. Object này có lifecycle độc lập không?

9. Có thể reference Aggregate khác bằng ID không?

10. Repository boundary có khớp Aggregate boundary không?
```

Nếu bạn trả lời được 10 câu này, bạn đã bắt đầu **thực sự thiết kế Aggregate**, thay vì chỉ học thuộc định nghĩa.

---

# 64. Bài tập Buổi 18

Với hệ thống:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

hãy phân tích 4 trường hợp sau.

### Case A

```text
Story + Chapter
```

Rule:

```text
ChapterNumber phải unique trong Story.
```

→ Một Aggregate hay hai?

---

### Case B

```text
User + ReadingProgress
```

Rule:

```text
User có thể đọc hàng nghìn Story.
ReadingProgress được cập nhật rất thường xuyên.
```

→ Có nên nhúng `ReadingProgress` vào `User` không?

---

### Case C

```text
CrawlerSource + CrawlerJob
```

Rule:

```text
CrawlerSource có thể có hàng triệu CrawlerJob.
CrawlerJob có lifecycle riêng.
```

→ Một Aggregate hay hai?

---

### Case D

```text
Story + User
```

Story chỉ cần:

```text
author_id
```

→ Có cần nhúng `User` vào Story Aggregate không?

---

## Bài code

Hãy thử thiết kế:

```text
Story Aggregate
```

và:

```text
Chapter Aggregate
```

theo **hai phiên bản**.

### Version A

```text
Story
└── Chapter
```

### Version B

```text
Story

Chapter
└── story_id
```

Sau đó viết ra:

```text
- invariant nào Version A bảo vệ dễ hơn?
- invariant nào Version B khó bảo vệ hơn?
- transaction nào thay đổi?
- crawler nào dễ implement hơn?
- concurrency nào tốt hơn?
- repository thay đổi thế nào?
```

Đây là bài tập rất quan trọng trước khi sang **Buổi 19 — Aggregate + Transaction**, nơi chúng ta sẽ nối trực tiếp:

```text
Aggregate
    ↓
Consistency Boundary
    ↓
Transaction Boundary
    ↓
SQLite BEGIN / COMMIT / ROLLBACK
    ↓
Concurrency
```

và lúc đó bạn sẽ thấy **Aggregate Design ảnh hưởng trực tiếp đến cách thiết kế Repository và SQLite transaction như thế nào**.
