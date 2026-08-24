# DDD Deep Dive — Buổi 17

# Aggregate Root

Ở Buổi 16, chúng ta đã biết:

```text
Aggregate
    │
    ├── Aggregate Root
    │
    └── Internal Entities / Value Objects
```

Hôm nay chúng ta tập trung vào câu hỏi:

> **Aggregate Root thực sự chịu trách nhiệm gì?**

Đây là bài rất quan trọng vì nếu hiểu sai Root, Aggregate sẽ chỉ trở thành một class "to hơn bình thường".

---

# 1. Aggregate Root là gì?

**Aggregate Root là Entity đứng ở biên của Aggregate và là cổng truy cập chính vào Aggregate.**

Ví dụ:

```text
┌──────────────────────────────────┐
│        Story Aggregate           │
│                                  │
│   Story ← Aggregate Root         │
│      │                           │
│      ├── Chapter                 │
│      ├── Chapter                 │
│      └── Chapter                 │
│                                  │
└──────────────────────────────────┘
```

Bên ngoài chỉ nên giao tiếp với:

```text
Story
```

chứ không trực tiếp thao tác với:

```text
Chapter
```

nếu `Chapter` là internal entity của Aggregate.

---

# 2. Root giống như cửa chính

Hãy tưởng tượng Aggregate là một ngôi nhà:

```text
                 Aggregate
        ┌──────────────────────┐
        │                      │
        │   Story ← cửa chính  │
        │      │               │
        │      ├─ Chapter      │
        │      ├─ Chapter      │
        │      └─ Chapter      │
        │                      │
        └──────────────────────┘
```

Không nên:

```text
External
   ↓
Chapter
```

mà:

```text
External
   ↓
Story
   ↓
Chapter
```

---

# 3. Tại sao phải có Root?

Vì chúng ta cần một nơi kiểm soát:

```text
business invariant
mutation
lifecycle
access
transaction
```

Ví dụ:

```text
Story
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

Business rule:

> Không được có hai chapter cùng số.

Nếu bên ngoài có thể:

```python
story.chapters.append(chapter)
```

thì rule này có thể bị phá vỡ.

---

# 4. Thiết kế sai

```python
@dataclass
class Story:
    chapters: list[Chapter]
```

Sau đó:

```python
story.chapters.append(chapter)
```

Code chạy bình thường.

Nhưng:

```text
Story
├── Chapter 1
├── Chapter 2
└── Chapter 2   ❌
```

Domain invariant đã bị phá vỡ.

---

# 5. Thiết kế đúng

Ta giữ collection bên trong:

```python
class Story:
    def __init__(self):
        self._chapters: list[Chapter] = []
```

và cung cấp behavior:

```python
def add_chapter(self, chapter: Chapter) -> None:
    ...
```

Bây giờ:

```text
External
    ↓
story.add_chapter()
    ↓
check invariant
    ↓
modify _chapters
```

---

# 6. Root không phải "manager"

Một lỗi rất phổ biến:

```python
class Story:
    def add_chapter(...)
    def remove_chapter(...)
    def rename_chapter(...)
    def publish(...)
    def archive(...)
    def send_email(...)
    def crawl(...)
    def save_to_database(...)
```

Đây là:

> **God Object**

Aggregate Root không có nghĩa là:

> "Mọi logic liên quan đến Story đều nhét vào Story."

Root chỉ chịu trách nhiệm những behavior cần thiết để bảo vệ Domain invariant và trạng thái của Aggregate.

---

# 7. Root sở hữu Aggregate Boundary

Ví dụ:

```text
Story Aggregate
│
├── Story
│
├── Chapter
│
└── Chapter
```

Root:

```text
Story
```

chịu trách nhiệm:

```text
"Chapter nào được thêm?"
"Chapter nào được xóa?"
"Chapter nào được thay đổi?"
```

nếu những operation đó ảnh hưởng invariant của Aggregate.

---

# 8. `story.add_chapter()`

Ví dụ:

```python
def add_chapter(self, chapter: Chapter) -> None:
    if any(
        item.number == chapter.number
        for item in self._chapters
    ):
        raise DuplicateChapterNumber(
            chapter.number
        )

    self._chapters.append(chapter)
```

Điểm quan trọng không phải method tên `add_chapter`.

Điểm quan trọng là:

```text
Root
 ↓
protect invariant
```

---

# 9. Root kiểm soát mutation

Có một nguyên tắc:

> **External code không được tự ý mutate internal state của Aggregate.**

Ví dụ không tốt:

```python
story.chapters.append(...)
story.chapters.remove(...)
story.chapters[0].title = ...
```

Thiết kế tốt hơn:

```python
story.add_chapter(...)
story.remove_chapter(...)
story.rename_chapter(...)
```

---

# 10. Nhưng `tuple` chưa đủ

Ở Buổi 16 ta dùng:

```python
@property
def chapters(self):
    return tuple(self._chapters)
```

Điều này ngăn:

```python
story.chapters.append(...)
```

Nhưng vẫn còn vấn đề:

```python
chapter = story.chapters[0]

chapter.title = "..."
```

Nếu `Chapter` mutable, caller vẫn có thể thay đổi internal entity.

---

# 11. Đây mới là vấn đề thực sự

Ví dụ:

```python
chapters = story.chapters

chapter = chapters[0]

chapter.title = ""
```

Collection không bị mutate.

Nhưng Entity bên trong đã bị mutate.

Nếu:

```text
Chapter.title != ""
```

là invariant:

```text
INVALID
```

---

# 12. Root phải kiểm soát cả Entity con

Có một nguyên tắc mạnh hơn:

> **Không chỉ bảo vệ collection; phải bảo vệ mutation của các object bên trong nếu mutation đó ảnh hưởng Aggregate invariant.**

Ví dụ:

```python
story.rename_chapter(
    chapter_id,
    StoryTitle(...)
)
```

Root tìm Chapter:

```text
Story
 ↓
find Chapter
 ↓
validate
 ↓
Chapter.rename()
```

---

# 13. Internal Entity không nhất thiết phải public

Ta có:

```python
class Story:
    def __init__(self):
        self._chapters = {}
```

Thay vì:

```python
list
```

có thể dùng:

```python
dict[ChapterId, Chapter]
```

Ví dụ:

```python
def add_chapter(self, chapter: Chapter) -> None:
    if chapter.id in self._chapters:
        raise DuplicateChapter(...)

    if any(
        c.number == chapter.number
        for c in self._chapters.values()
    ):
        raise DuplicateChapterNumber(...)

    self._chapters[chapter.id] = chapter
```

---

# 14. Tại sao `dict` có thể tốt hơn?

Nếu thường xuyên cần:

```python
story.get_chapter(chapter_id)
```

thì:

```python
dict
```

phù hợp hơn:

```python
list
```

Ta có:

```python
def get_chapter(
    self,
    chapter_id: ChapterId,
) -> Chapter:
    try:
        return self._chapters[chapter_id]
    except KeyError:
        raise ChapterNotFound(chapter_id)
```

---

# 15. Nhưng hãy cẩn thận

Nếu:

```python
def get_chapter(...) -> Chapter:
    return self._chapters[id]
```

thì caller nhận được object mutable.

Caller có thể:

```python
chapter = story.get_chapter(id)
chapter.title = ""
```

và bypass Root.

---

# 16. Một số cách xử lý

Có nhiều chiến lược.

### Cách 1

`Chapter` tự bảo vệ invariant của chính nó.

Ví dụ:

```python
chapter.rename(new_title)
```

thay vì:

```python
chapter.title = new_title
```

---

### Cách 2

Mutation xuyên Aggregate phải đi qua Root.

Ví dụ:

```python
story.rename_chapter(
    chapter_id,
    new_title,
)
```

---

### Cách 3

Không expose Entity con nếu không cần.

Thay vì:

```python
story.get_chapter()
```

có thể cung cấp:

```python
story.chapter_title(chapter_id)
```

hoặc DTO/read model riêng.

---

# 17. Command vs Query

Một cách tư duy rất hữu ích:

```text
Command
    ↓
thay đổi state
    ↓
Root
```

Ví dụ:

```python
story.add_chapter(...)
story.remove_chapter(...)
story.rename_chapter(...)
```

Còn:

```text
Query
    ↓
đọc state
```

có thể dùng:

```python
story.get_chapter(...)
story.chapters
```

Nhưng query không nên cho phép mutation.

---

# 18. Root là Business API

Một Aggregate Root tốt thường có API rất rõ:

```python
story.publish()
story.complete()
story.add_chapter(...)
story.remove_chapter(...)
```

Thay vì:

```python
story.status = ...
story.chapters.append(...)
story.chapters.remove(...)
```

Nhìn API ta có thể đọc được business language.

Đây chính là **Ubiquitous Language**.

---

# 19. So sánh

### Data-centric

```python
story.status = PUBLISHED
story.chapters.append(chapter)
```

### Domain-centric

```python
story.publish()
story.add_chapter(chapter)
```

Cách thứ hai diễn đạt:

```text
business intent
```

thay vì:

```text
data manipulation
```

---

# 20. Đây là điểm cực kỳ quan trọng

DDD không chỉ muốn:

```text
object có data
```

DDD muốn:

```text
object biểu diễn business concept
```

Ví dụ:

```python
story.publish()
```

có nghĩa nghiệp vụ.

Trong khi:

```python
story.status = StoryStatus.PUBLISHED
```

chỉ là thay đổi dữ liệu.

---

# 21. Root và lifecycle

Ví dụ Story:

```text
DRAFT
  ↓
PUBLISHED
  ↓
COMPLETED
  ↓
ARCHIVED
```

Root kiểm soát transition:

```python
def publish(self):
    if self._status != StoryStatus.DRAFT:
        raise InvalidStoryTransition()

    self._status = StoryStatus.PUBLISHED
```

Không cho:

```python
story.status = COMPLETED
```

từ bên ngoài.

---

# 22. Root và invariant của Chapter

Giả sử:

```text
Chapter number phải unique
```

Root:

```python
def add_chapter(self, chapter):
    if self._has_number(chapter.number):
        raise DuplicateChapterNumber()

    self._chapters[chapter.id] = chapter
```

Như vậy invariant:

```text
unique(ChapterNumber)
```

được bảo vệ tại:

```text
Story Aggregate Root
```

---

# 23. Root và invariant xuyên Entity

Đây là lý do Aggregate Root tồn tại.

Ví dụ:

```text
Chapter A
number = 1

Chapter B
number = 1
```

Mỗi Chapter riêng lẻ:

```text
VALID
```

Nhưng:

```text
Story
├── Chapter A (1)
└── Chapter B (1)
```

→ INVALID.

Root có visibility:

```text
Chapter A
Chapter B
```

nên Root có thể bảo vệ rule.

---

# 24. Root và transaction

Giả sử:

```python
story.add_chapter(chapter)
```

Operation này có thể dẫn tới:

```text
INSERT chapter
UPDATE story
```

Application Layer có thể:

```text
BEGIN
   ↓
story.add_chapter()
   ↓
repository.save(story)
   ↓
COMMIT
```

Root không tự mở SQLite transaction.

Đây là distinction quan trọng.

---

# 25. Root không nên biết Infrastructure

Sai:

```python
class Story:
    def save_to_sqlite(self):
        ...
```

hoặc:

```python
class Story:
    def __init__(self, connection):
        ...
```

Aggregate Root thuộc:

```text
Domain Layer
```

nó không nên phụ thuộc:

```text
SQLite
SQLAlchemy
HTTP
PySide6
filesystem
```

---

# 26. Application Layer điều phối

Kiến trúc:

```text
CLI / GUI / API
       ↓
Application
       ↓
StoryRepository
       ↓
Story Aggregate
       ↓
Domain behavior
```

Ví dụ:

```python
def add_chapter(
    story_id: StoryId,
    chapter: Chapter,
):
    story = story_repository.get(story_id)

    story.add_chapter(chapter)

    story_repository.save(story)
```

Application:

```text
orchestration
```

Domain:

```text
business rule
```

---

# 27. Root không gọi Repository

Tránh:

```python
class Story:
    def add_chapter(self):
        chapter_repository.save(...)
```

Vì:

```text
Domain
 ↓
Repository implementation
```

làm sai dependency direction.

Root chỉ biết:

```text
Domain objects
```

---

# 28. Aggregate Root và Repository

Một Repository thường đại diện cho Aggregate:

```python
class StoryRepository(Protocol):

    def get(self, story_id: StoryId) -> Story:
        ...

    def save(self, story: Story) -> None:
        ...
```

Không nhất thiết:

```python
class ChapterRepository:
    ...
```

nếu Chapter là internal Entity.

---

# 29. Vì sao Repository Root-centric?

Giả sử có:

```text
Story Aggregate
    Story
    Chapter
```

Nếu Application làm:

```python
chapter_repository.save(chapter)
```

thì nó có thể bypass:

```text
Story.add_chapter()
```

và phá invariant.

Root-centric Repository giúp:

```text
Application
    ↓
StoryRepository
    ↓
Story Root
    ↓
Chapter
```

---

# 30. Một Aggregate Root không phải Singleton

Đừng nhầm:

```text
Aggregate Root
```

với:

```text
Singleton
```

Ví dụ hệ thống có:

```text
Story #1
Story #2
Story #3
```

Mỗi Story là một Aggregate riêng:

```text
Aggregate 1 → Story #1
Aggregate 2 → Story #2
Aggregate 3 → Story #3
```

Mỗi cái có Root riêng.

---

# 31. Root và identity

Root là Entity nên có Identity:

```python
story.id: StoryId
```

Chapter cũng có:

```python
chapter.id: ChapterId
```

nhưng external identity chính của Aggregate là:

```text
StoryId
```

Ví dụ:

```python
story_repository.get(story_id)
```

---

# 32. Aggregate Root và child identity

Có thể có:

```text
StoryId = 100
ChapterId = 500
```

Chapter vẫn có identity riêng.

Nhưng:

```text
Chapter 500
```

không nên được truy cập độc lập như một Aggregate nếu nó là internal Entity.

Nó có ý nghĩa trong:

```text
Story Aggregate
```

---

# 33. Root và Domain Event

Một Aggregate có thể tạo Domain Event:

```python
class Story:
    def publish(self):
        ...
        self._events.append(
            StoryPublished(self._id)
        )
```

Sau đó Application/Infrastructure xử lý event.

Ví dụ:

```text
Story.publish()
       ↓
StoryPublished
       ↓
Notification
       ↓
Search Index
```

Điểm quan trọng:

```text
Story
```

không trực tiếp gọi:

```text
NotificationService
SearchService
```

---

# 34. Root có thể giữ Domain Events

Ví dụ:

```python
class Story:
    def __init__(...):
        self._events = []

    def publish(self):
        ...
        self._events.append(
            StoryPublished(self.id)
        )

    def pull_events(self):
        events = tuple(self._events)
        self._events.clear()
        return events
```

Application Layer có thể lấy:

```python
events = story.pull_events()
```

và dispatch.

Chúng ta sẽ đào sâu Domain Event ở phần sau.

---

# 35. Một thiết kế Python hoàn chỉnh hơn

```python
class Story:
    def __init__(
        self,
        story_id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
    ):
        self._id = story_id
        self._title = title
        self._source_id = source_id
        self._status = StoryStatus.DRAFT
        self._chapters: dict[ChapterId, Chapter] = {}

    @property
    def id(self) -> StoryId:
        return self._id

    @property
    def title(self) -> StoryTitle:
        return self._title

    @property
    def status(self) -> StoryStatus:
        return self._status

    def add_chapter(self, chapter: Chapter) -> None:
        if any(
            item.number == chapter.number
            for item in self._chapters.values()
        ):
            raise DuplicateChapterNumber(
                chapter.number
            )

        self._chapters[chapter.id] = chapter
```

---

# 36. Thêm behavior

```python
def publish(self) -> None:
    if self._status != StoryStatus.DRAFT:
        raise InvalidStoryTransition(
            "Only draft story can be published"
        )

    self._status = StoryStatus.PUBLISHED
```

và:

```python
def complete(self) -> None:
    if self._status != StoryStatus.PUBLISHED:
        raise InvalidStoryTransition(
            "Only published story can be completed"
        )

    self._status = StoryStatus.COMPLETED
```

---

# 37. Xóa Chapter

```python
def remove_chapter(
    self,
    chapter_id: ChapterId,
) -> None:
    if chapter_id not in self._chapters:
        raise ChapterNotFound(chapter_id)

    del self._chapters[chapter_id]
```

Nhưng cần hỏi business:

> Có được xóa Chapter khi Story đã Published không?

Nếu không:

```python
def remove_chapter(self, chapter_id):
    if self._status != StoryStatus.DRAFT:
        raise InvalidStoryOperation(
            "Cannot remove chapter"
        )

    ...
```

Đây mới thực sự là DDD.

---

# 38. Behavior phải xuất phát từ Domain

Đừng nghĩ:

```text
"CRUD Story"
```

rồi tạo:

```text
create_story()
update_story()
delete_story()
```

một cách máy móc.

Hãy hỏi:

```text
Business muốn làm gì?
```

Ví dụ:

```text
publish story
archive story
add chapter
complete story
rename story
```

Đây là:

> **Domain behavior**

---

# 39. Command-oriented API

Aggregate API thường có dạng:

```text
publish()
complete()
archive()
add_chapter()
remove_chapter()
rename()
```

thay vì:

```text
set_status()
set_title()
set_chapters()
```

Tại sao?

Vì command diễn tả:

```text
intent
```

chứ không chỉ:

```text
state mutation
```

---

# 40. Một quy tắc rất mạnh

> **Nếu một operation có business meaning, hãy biểu diễn nó bằng method có business meaning.**

Ví dụ:

Không:

```python
story.status = PUBLISHED
```

Mà:

```python
story.publish()
```

Không:

```python
story.chapters.append(chapter)
```

Mà:

```python
story.add_chapter(chapter)
```

Không:

```python
story.status = ARCHIVED
```

Mà:

```python
story.archive()
```

---

# 41. Root không nhất thiết phải expose mọi child

Đây là điểm nâng cao.

Nếu UI chỉ cần:

```text
chapter count
```

không cần:

```python
story.chapters
```

có thể:

```python
@property
def chapter_count(self) -> int:
    return len(self._chapters)
```

Nếu cần đọc chapter:

```python
def get_chapter_summary(...)
```

hoặc Query/Read Model riêng.

---

# 42. CQRS bắt đầu xuất hiện ở đây

Đây là nơi tư duy DDD có thể kết nối với CQRS:

```text
Command
    ↓
Aggregate Root
    ↓
Domain behavior
```

Trong khi:

```text
Query
    ↓
Read Model
    ↓
Database query
```

Không nhất thiết phải load toàn bộ Aggregate chỉ để:

```text
"Hiển thị danh sách 100 chapter"
```

---

# 43. Aggregate không phải API cho mọi query

Ví dụ:

```text
User mở trang Story
```

cần:

```text
Story title
Author name
Chapter count
Last chapter
Rating
Reading progress
```

Không nên nhất thiết:

```text
load Story Aggregate
load User Aggregate
load 1000 Chapter Entities
load ReadingProgress
...
```

Chỉ để render UI.

Read side có thể có query riêng.

---

# 44. Đây là lý do Domain Model ≠ Read Model

Domain Model:

```text
Story Aggregate
```

tối ưu cho:

```text
business behavior
invariant
consistency
```

Read Model:

```text
StoryDetailView
```

tối ưu cho:

```text
query
display
performance
```

Đây là một insight rất quan trọng khi hệ thống lớn.

---

# 45. Aggregate Root và Encapsulation — công thức

Hãy nhớ:

```text
Private state
      ↓
Business behavior
      ↓
Invariant
      ↓
Valid state
```

Ví dụ:

```text
_story._chapters
       ↓
story.add_chapter()
       ↓
check duplicate
       ↓
append
```

---

# 46. Sai lầm #1

```python
story.chapters.append(chapter)
```

→ bypass Root.

---

# 47. Sai lầm #2

```python
story.status = StoryStatus.PUBLISHED
```

→ bypass lifecycle.

---

# 48. Sai lầm #3

```python
chapter = story.chapters[0]
chapter.title = ""
```

→ bypass child invariant.

---

# 49. Sai lầm #4

```python
story.save_to_database()
```

→ Domain phụ thuộc Infrastructure.

---

# 50. Sai lầm #5

```python
story.send_notification()
```

→ Root trở thành integration service.

---

# 51. Sai lầm #6

```python
story.user = User(...)
```

nếu `User` là Aggregate khác.

→ Aggregate coupling quá mạnh.

Thường nên:

```python
story.user_id = user_id
```

---

# 52. Root nên nhỏ và rõ

Một Root tốt thường có API:

```text
Story
│
├── publish()
├── complete()
├── archive()
├── rename()
├── add_chapter()
├── remove_chapter()
└── rename_chapter()
```

Mỗi method đều có:

```text
business meaning
```

và:

```text
invariant protection
```

---

# 53. Checklist thiết kế Aggregate Root

Khi thiết kế Root, hãy hỏi:

### 1.

```text
Root là Entity nào?
```

### 2.

```text
Invariant nào Root phải bảo vệ?
```

### 3.

```text
Entity con nào thuộc boundary?
```

### 4.

```text
Mutation nào phải đi qua Root?
```

### 5.

```text
Có expose mutable collection không?
```

### 6.

```text
Repository có làm việc với Root không?
```

### 7.

```text
Aggregate có quá lớn không?
```

### 8.

```text
Có Aggregate khác bị nhúng trực tiếp không?
```

---

# 54. Áp dụng vào hệ thống đọc truyện

Một thiết kế ban đầu:

```text
┌─────────────────────────────┐
│       Story Aggregate       │
│                             │
│ Story ← Root                │
│   │                         │
│   ├── Chapter               │
│   ├── Chapter               │
│   └── Chapter               │
│                             │
│ Operations:                 │
│   add_chapter()             │
│   remove_chapter()          │
│   rename_chapter()          │
│   publish()                 │
│   complete()                │
│   archive()                 │
└─────────────────────────────┘
```

Bên ngoài:

```text
Application
    ↓
StoryRepository
    ↓
Story
    ↓
Chapter
```

Không:

```text
Application
    ↓
ChapterRepository
    ↓
Chapter
```

nếu Chapter là internal Entity.

---

# 55. Một nuance rất quan trọng

Câu:

> "Không truy cập Entity con trực tiếp"

không có nghĩa:

> "Không bao giờ được đọc Chapter."

Ý chính là:

> **Không được bypass Aggregate boundary để thực hiện mutation/business operation.**

Ví dụ read:

```python
story.chapter_count
```

hoàn toàn bình thường.

Hoặc:

```python
story.find_chapter(chapter_id)
```

cũng có thể hợp lý.

Vấn đề là:

```python
chapter.title = ""
```

làm thay đổi Domain state mà không qua cơ chế bảo vệ.

---

# 56. Tổng kết Buổi 17

Hãy nhớ mô hình:

```text
                  Aggregate
                      │
                      ▼
             ┌────────────────┐
             │ Aggregate Root │
             └───────┬────────┘
                     │
             Business API
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
      publish() add_chapter() archive()
                     │
                     ↓
              Internal State
                     │
                     ↓
                 Invariant
```

Và 5 nguyên tắc cốt lõi:

1. **Aggregate có một Root.**
2. **Root là cổng vào của Aggregate.**
3. **Mutation business phải được kiểm soát bởi Root/Domain behavior.**
4. **Không expose mutable internal state.**
5. **Repository thường làm việc với Aggregate Root.**

---

## Bài tập Buổi 17

Hãy tự thiết kế `Story Aggregate` với:

```text
Story
├── StoryId
├── StoryTitle
├── SourceId
├── Status
└── Chapters
```

và các operation:

```python
story.publish()

story.complete()

story.archive()

story.add_chapter(chapter)

story.remove_chapter(chapter_id)

story.rename_chapter(
    chapter_id,
    new_title,
)
```

Bắt buộc bảo vệ:

```text
1. Story phải bắt đầu ở DRAFT
2. DRAFT → PUBLISHED
3. PUBLISHED → COMPLETED
4. COMPLETED → ARCHIVED
5. Không duplicate ChapterNumber
6. Không expose mutable chapters
7. Không cho code bên ngoài tự ý thay đổi status
```

**Bài 18** chúng ta sẽ đi vào một vấn đề khó hơn nhiều: **Aggregate Design** — khi nào Aggregate quá lớn, khi nào quá nhỏ, tại sao phải *reference by ID*, và đặc biệt là cách quyết định `Story + Chapter` nên là **một Aggregate hay hai Aggregate**.
