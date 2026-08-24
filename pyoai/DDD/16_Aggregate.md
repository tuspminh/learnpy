# DDD Deep Dive — Buổi 16

# Aggregate là gì?

Đây là một trong những bài **quan trọng nhất của Tactical DDD**.

Ở Buổi 15, chúng ta đã học:

```text
Value Object
      ↓
Entity
      ↓
Invariant
```

Nhưng xuất hiện một vấn đề:

```text
Story
  │
  ├── Chapter 1
  ├── Chapter 2
  ├── Chapter 3
  └── Chapter 4
```

Nếu `Story` và `Chapter` cùng liên quan đến một business invariant, thì:

> **Ai chịu trách nhiệm đảm bảo toàn bộ chúng luôn nhất quán?**

Đó chính là vấn đề Aggregate giải quyết.

---

# 1. Aggregate là gì?

Một **Aggregate** là một nhóm các Domain Object được xem như **một đơn vị nhất quán về mặt nghiệp vụ**.

Nó có:

```text
Aggregate
   │
   ├── Aggregate Root
   │
   └── các object bên trong
```

Aggregate có một boundary rõ ràng.

Ví dụ:

```text
┌──────────────────────────────┐
│        Story Aggregate       │
│                              │
│   Story (Root)               │
│      │                       │
│      ├── Chapter             │
│      ├── Chapter             │
│      └── Chapter             │
│                              │
└──────────────────────────────┘
```

`Story` là Aggregate Root.

---

# 2. Aggregate không đơn giản là "object chứa object"

Đây là điểm cực kỳ quan trọng.

Có:

```python
class Story:
    chapters: list[Chapter]
```

**không có nghĩa tự động là Aggregate.**

Aggregate được xác định bởi:

> **Business invariant + consistency boundary**

chứ không phải bởi cấu trúc Python.

---

# 3. Tại sao chúng ta cần Aggregate?

Giả sử hệ thống đọc truyện có rule:

> Một Story không được có hai Chapter cùng số.

Ví dụ hợp lệ:

```text
Story
├── Chapter 1
├── Chapter 2
└── Chapter 3
```

Không hợp lệ:

```text
Story
├── Chapter 1
├── Chapter 2
├── Chapter 2  ← duplicate
└── Chapter 3
```

`ChapterNumber` riêng lẻ không thể biết:

```text
"Chapter 2 đã tồn tại chưa?"
```

Nó chỉ biết:

```python
ChapterNumber(2)
```

là hợp lệ.

---

# 4. Ai có đủ thông tin?

`Story` có:

```text
Story
 ├── Chapter 1
 ├── Chapter 2
 └── Chapter 3
```

Do đó `Story` mới có đủ thông tin để đảm bảo:

```text
ChapterNumber phải unique
```

Đây chính là dấu hiệu mạnh cho thấy:

```text
Story
+
Chapter
```

có thể nằm trong cùng một Aggregate.

---

# 5. Aggregate Root là gì?

Mỗi Aggregate có **một Root**.

Ví dụ:

```text
┌─────────────────────────┐
│ Story Aggregate         │
│                         │
│ Story ← Root            │
│   │                     │
│   ├── Chapter           │
│   ├── Chapter           │
│   └── Chapter           │
└─────────────────────────┘
```

Root là **cổng vào duy nhất** của Aggregate.

Bên ngoài không nên thao tác trực tiếp với các Entity bên trong.

---

# 6. Ví dụ sai

Ta có:

```python
story.chapters.append(chapter)
```

Vấn đề là code bên ngoài đang trực tiếp thay đổi Aggregate.

Nó có thể làm:

```python
story.chapters.append(
    Chapter(number=ChapterNumber(2))
)
```

mặc dù Chapter 2 đã tồn tại.

Invariant bị phá vỡ.

---

# 7. Cách đúng

Thay vì:

```python
story.chapters.append(chapter)
```

dùng:

```python
story.add_chapter(chapter)
```

Sau đó `Story` kiểm tra:

```python
def add_chapter(self, chapter: Chapter):
    if chapter.number in self._chapters:
        raise DuplicateChapterNumber()

    self._chapters.append(chapter)
```

Bây giờ:

```text
External code
      │
      ↓
story.add_chapter()
      │
      ↓
check invariant
      │
      ↓
modify state
```

---

# 8. Aggregate chính là boundary của invariant

Hãy nhớ câu này:

> **Aggregate boundary xác định phạm vi mà Domain phải giữ consistency.**

Ví dụ:

```text
Story Aggregate
│
├── Story
├── Chapter 1
├── Chapter 2
└── Chapter 3
```

Invariant:

```text
Chapter number unique
```

được đảm bảo bên trong boundary này.

---

# 9. Consistency Boundary

Aggregate thường được xem là:

> **Consistency Boundary**

Có nghĩa:

```text
Trong cùng Aggregate
        ↓
phải đảm bảo consistency
```

Ví dụ:

```text
Story
+
Chapters
```

cùng Aggregate.

Khi:

```python
story.add_chapter(...)
```

hoàn thành thành công:

```text
Story + Chapters
```

phải ở trạng thái hợp lệ.

---

# 10. Transaction Boundary

Aggregate còn thường đóng vai trò:

> **Transaction Boundary**

Ví dụ:

```text
BEGIN TRANSACTION

update Story
insert Chapter
insert Chapter

COMMIT
```

Nếu tất cả thuộc cùng Aggregate và một operation cần cập nhật tất cả:

```text
tất cả thành công
    hoặc
tất cả rollback
```

Đây là atomicity.

---

# 11. Aggregate nối Domain với Database

Ta có:

```text
Domain
   │
   │ Aggregate
   ↓
Transaction
   │
   ↓
Database
```

Ví dụ:

```text
Story Aggregate
      ↓
Repository
      ↓
SQLite transaction
      ↓
COMMIT
```

Đây là lý do Aggregate không chỉ là khái niệm OOP.

Nó ảnh hưởng trực tiếp đến:

```text
database
transaction
concurrency
performance
```

---

# 12. Một Aggregate không nhất thiết là một bảng

Đừng nghĩ:

```text
Aggregate = Database table
```

Không đúng.

Một Aggregate:

```text
Story
├── Story
└── Chapters
```

có thể được lưu bằng:

```text
stories
chapters
```

hai bảng.

Nhưng về Domain:

```text
Story Aggregate
```

là một consistency boundary.

---

# 13. Một Aggregate cũng có thể chỉ có một Entity

Ví dụ:

```text
┌─────────────────┐
│ User Aggregate  │
│                 │
│ User ← Root     │
└─────────────────┘
```

Không phải Aggregate nào cũng phải có:

```text
Root
 ├── Entity
 ├── Entity
 └── Entity
```

Có Aggregate chỉ có:

```text
Root
```

---

# 14. Aggregate không phải Collection

Ví dụ:

```python
class Story:
    chapters: list[Chapter]
```

Nếu chỉ vì có list mà gọi:

```text
Story Aggregate
```

thì chưa đủ.

Cần hỏi:

> Story có thực sự chịu trách nhiệm đảm bảo consistency của Chapter không?

Nếu:

```text
Có
```

→ Aggregate có thể phù hợp.

Nếu:

```text
Không
```

→ có thể nên tách.

---

# 15. Ví dụ Story + Chapter

Ta thiết kế:

```python
class Story:
    def __init__(
        self,
        id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
    ):
        self._id = id
        self._title = title
        self._source_id = source_id
        self._chapters = []
```

---

# 16. Không expose list trực tiếp

Sai:

```python
@property
def chapters(self):
    return self._chapters
```

vì bên ngoài có thể:

```python
story.chapters.append(chapter)
```

và bypass invariant.

---

# 17. Trả về immutable view

Ví dụ đơn giản:

```python
@property
def chapters(self) -> tuple[Chapter, ...]:
    return tuple(self._chapters)
```

Bây giờ:

```python
story.chapters
```

trả:

```text
tuple
```

Không thể:

```python
story.chapters.append(...)
```

---

# 18. Mutation thông qua Root

Thay vào đó:

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

Root kiểm soát mutation.

---

# 19. Aggregate Root giống như "API"

Hãy hình dung:

```text
┌────────────────────────────┐
│       Story Aggregate      │
│                            │
│   ┌────────────────────┐   │
│   │ Story Root         │   │
│   │                    │   │
│   │ add_chapter()      │   │
│   │ remove_chapter()   │   │
│   │ publish()          │   │
│   └────────────────────┘   │
│                            │
│      Chapter               │
│      Chapter               │
└────────────────────────────┘
```

Bên ngoài chỉ gọi:

```text
Story API
```

không chọc trực tiếp vào internal objects.

---

# 20. Đây chính là Encapsulation

OOP truyền thống nói:

> Encapsulation = che giấu implementation details.

DDD đi xa hơn:

> Aggregate Root encapsulates **business invariant**.

Ví dụ:

```python
story.add_chapter(chapter)
```

không chỉ là method tiện lợi.

Nó bảo vệ:

```text
business rule
```

---

# 21. Một câu cực kỳ quan trọng

> **Nếu bên ngoài có thể thay đổi Entity bên trong Aggregate mà không thông qua Root, Aggregate boundary đang bị phá vỡ.**

Ví dụ nguy hiểm:

```python
chapter.title = ...
```

nếu `chapter` là internal entity.

Tốt hơn:

```python
story.rename_chapter(
    chapter_id,
    new_title,
)
```

hoặc:

```python
chapter.rename(...)
```

nhưng chỉ khi `chapter` được kiểm soát đúng trong Aggregate boundary.

---

# 22. Root có cần chứa tất cả behavior không?

Không.

Ví dụ:

```python
chapter.rename(...)
```

có thể hoàn toàn hợp lý.

Nhưng việc:

```text
Story
+
Chapter
```

phải giữ một invariant chung thì Root phải kiểm soát.

Ví dụ:

```text
Chapter.rename()
```

có thể tự thay đổi title.

Nhưng:

```text
Story.add_chapter()
```

phải do Root kiểm soát.

---

# 23. Phân biệt Local Invariant và Aggregate Invariant

Ví dụ:

### Chapter

```text
Chapter.title != empty
```

Đây là invariant của Chapter.

### Story

```text
Story.title != empty
```

Đây là invariant của Story.

### Story + Chapters

```text
Không duplicate chapter number
```

Đây là Aggregate invariant.

---

# 24. Đây là cách phân chia

```text
Value Object
    ↓
local value invariant

Entity
    ↓
entity invariant

Aggregate
    ↓
cross-entity invariant
```

Đây là một trong những tư duy quan trọng nhất của Tactical DDD.

---

# 25. Aggregate Boundary không phải lúc nào cũng giống Object Graph

Giả sử:

```text
Story
 ├── Author
 ├── Genre
 ├── Chapter
 ├── Comment
 ├── Rating
 ├── Bookmark
 └── ReadingProgress
```

Không nên kết luận:

```text
Tất cả → Story Aggregate
```

Nếu làm vậy Aggregate trở thành:

```text
God Aggregate
```

và cực kỳ khó scale.

---

# 26. Aggregate quá lớn

Ví dụ:

```text
Story Aggregate
├── Story
├── 5000 Chapters
├── 10000 Comments
├── 50000 Ratings
├── ReadingProgress
└── Bookmarks
```

Mỗi lần sửa:

```text
Story
```

có thể phải load:

```text
5000 chapters
10000 comments
...
```

Đây là thiết kế tệ.

---

# 27. Aggregate nên nhỏ đến mức có thể

Một heuristic rất hữu ích:

> **Design Aggregate nhỏ nhất có thể nhưng vẫn đủ để bảo vệ invariant.**

Ví dụ:

```text
Story
+
Chapter
```

nếu cần consistency.

Nhưng:

```text
Story
+
10000 Comments
```

không cần thiết nếu Comment không có invariant phụ thuộc toàn bộ Story.

---

# 28. Aggregate quá nhỏ cũng có vấn đề

Giả sử:

```text
Story Aggregate
    ↓
Story

Chapter Aggregate
    ↓
Chapter
```

Nếu business rule:

```text
ChapterNumber unique trong Story
```

thì mỗi Aggregate chỉ thấy:

```text
Story
```

hoặc:

```text
Chapter
```

không ai có đủ information để bảo vệ rule.

Đây là dấu hiệu Aggregate đang **quá nhỏ**.

---

# 29. Vì vậy Aggregate Design là bài toán cân bằng

```text
Aggregate quá lớn
       ↓
performance kém
transaction lớn
concurrency thấp
lock nhiều

Aggregate quá nhỏ
       ↓
invariant khó bảo vệ
nhiều distributed consistency
logic phức tạp
```

Mục tiêu:

```text
          vừa đủ
             ↓
      Aggregate Boundary
```

---

# 30. Aggregate và Repository

Một nguyên tắc quan trọng:

> **Repository thường được thiết kế cho Aggregate Root.**

Ví dụ:

```python
class StoryRepository(Protocol):

    def get(self, id: StoryId) -> Story:
        ...

    def save(self, story: Story) -> None:
        ...
```

Không nhất thiết tạo:

```python
ChapterRepository
```

nếu `Chapter` là Entity bên trong `Story Aggregate`.

---

# 31. Tại sao?

Nếu:

```python
chapter_repository.save(chapter)
```

cho phép code bên ngoài sửa Chapter độc lập:

```text
Story Aggregate
      ↑
     bị bypass
```

Root không còn kiểm soát consistency.

---

# 32. Repository của Aggregate

Thay vào đó:

```text
Application
    ↓
StoryRepository
    ↓
Story Aggregate
    ↓
Story + Chapters
```

Repository làm việc với:

```text
Aggregate Root
```

---

# 33. Đây là một nguyên tắc DDD rất đáng nhớ

```text
External world
      ↓
Aggregate Root
      ↓
Entities / Value Objects
```

Không phải:

```text
External world
   ├── Story
   ├── Chapter
   ├── Chapter
   └── Chapter
```

---

# 34. Aggregate và ID

Một Aggregate Root có identity:

```text
StoryId
```

Entity bên trong cũng có thể có identity:

```text
ChapterId
```

Nhưng từ bên ngoài:

```text
StoryId
```

là identity quan trọng để truy cập Aggregate.

Ví dụ:

```python
story_repository.get(story_id)
```

thay vì:

```python
chapter_repository.get(chapter_id)
```

nếu Chapter là internal Entity.

---

# 35. Aggregate khác Aggregate chỉ nên reference bằng ID

Giả sử có:

```text
Story Aggregate
```

và:

```text
User Aggregate
```

Không nên:

```python
class Story:
    author: User
```

nếu `User` là một Aggregate khác.

Thường tốt hơn:

```python
class Story:
    author_id: UserId
```

Tức:

```text
Story
  │
  └── author_id ─────→ User Aggregate
```

---

# 36. Tại sao reference bằng ID?

Vì:

```text
Story Aggregate
```

không cần load toàn bộ:

```text
User Aggregate
```

để hoạt động.

Ta giảm:

```text
coupling
```

và tránh:

```text
giữa hai Aggregate
```

trở thành một object graph khổng lồ.

---

# 37. Ví dụ

```python
@dataclass
class Story:
    id: StoryId
    title: StoryTitle
    author_id: UserId
```

Không:

```python
@dataclass
class Story:
    id: StoryId
    title: StoryTitle
    author: User
```

nếu `User` là Aggregate Root riêng.

---

# 38. Aggregate Boundary và Transaction Boundary

Giả sử:

```text
Story Aggregate
```

cần:

```text
Story
+
Chapter
```

được cập nhật atomic.

Ta có:

```text
BEGIN
   ↓
UPDATE story
   ↓
INSERT chapter
   ↓
COMMIT
```

Một transaction có thể bao phủ Aggregate.

---

# 39. Nhưng không nên mặc định transaction toàn hệ thống

Ví dụ:

```text
Story
User
Notification
CrawlerJob
ReadingProgress
```

không nên:

```text
BEGIN TRANSACTION

update Story
update User
insert Notification
update ReadingProgress
update CrawlerJob

COMMIT
```

chỉ vì tất cả liên quan đến một use case.

Điều đó tạo coupling cực lớn.

---

# 40. Aggregate giúp chia transaction

Ví dụ:

```text
Story Aggregate
      ↓
Transaction A

User Aggregate
      ↓
Transaction B

ReadingProgress Aggregate
      ↓
Transaction C
```

Nếu chúng không cần consistency tức thời với nhau:

```text
không cần cùng transaction
```

---

# 41. Đây là lý do Aggregate liên quan đến Eventual Consistency

Ví dụ:

```text
User đọc Chapter
```

có thể:

```text
ReadingProgress Aggregate
        ↓
save
        ↓
event
        ↓
Notification
```

Không nhất thiết:

```text
ReadingProgress
+
Notification
+
Story
+
User
```

phải commit trong cùng một transaction.

---

# 42. Aggregate và Event

Sau này ta sẽ học:

```text
Domain Event
```

Ví dụ:

```text
ChapterCompleted
```

Aggregate có thể phát event:

```text
Story
   ↓
complete_chapter()
   ↓
ChapterCompleted
```

Application layer xử lý:

```text
ChapterCompleted
   ├── update ReadingProgress
   └── notify User
```

Đây là cách các Aggregate giao tiếp mà không cần nằm chung boundary.

---

# 43. Nhưng hôm nay chỉ cần nhớ

```text
Aggregate
   ↓
Consistency boundary
   ↓
Transaction boundary
   ↓
Root controls access
```

Đây là 4 từ khóa của Buổi 16.

---

# 44. Ví dụ hoàn chỉnh cho Story Aggregate

Một model ban đầu:

```python
class Story:
    def __init__(
        self,
        id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
    ):
        self._id = id
        self._title = title
        self._source_id = source_id
        self._chapters: list[Chapter] = []

    @property
    def chapters(self) -> tuple[Chapter, ...]:
        return tuple(self._chapters)

    def add_chapter(self, chapter: Chapter) -> None:
        if any(
            c.number == chapter.number
            for c in self._chapters
        ):
            raise DuplicateChapterNumber(
                chapter.number
            )

        self._chapters.append(chapter)
```

Ở đây:

```text
Story
```

là:

# Aggregate Root

và:

```text
Chapter
```

là:

# Internal Entity

---

# 45. Nhưng có một câu hỏi sâu hơn

Nếu Story có:

```text
5000 chapters
```

thì:

```python
story.chapters
```

có hợp lý không?

Có thể **không**.

Đây là lúc ta phải xem xét:

```text
Aggregate size
Loading strategy
Consistency requirement
Query requirement
Transaction requirement
```

DDD không nói:

> "Nếu Chapter thuộc Story thì Story phải load tất cả Chapter."

Không.

---

# 46. Aggregate là business boundary, không phải navigation convenience

Đừng thiết kế:

```text
Story
 └── chapters
```

chỉ vì UI muốn:

```text
story.chapters
```

Hãy thiết kế dựa trên:

```text
business invariant
```

---

# 47. Một cách suy nghĩ rất mạnh

Thay vì hỏi:

> "Entity nào chứa Entity nào?"

Hãy hỏi:

> **"Business rule nào cần được bảo vệ atomically?"**

Ví dụ:

```text
Rule:
Chapter number phải unique trong Story
```

→ Story cần kiểm soát Chapters.

Nhưng:

```text
Rule:
User có thể đánh dấu Chapter là đã đọc
```

không nhất thiết cần Story.

Có thể:

```text
ReadingProgress Aggregate
```

riêng.

---

# 48. Ví dụ hệ thống đọc truyện

Ta có:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

Một thiết kế ban đầu có thể là:

```text
Story Aggregate
    Story
    Chapter

CrawlerSource Aggregate
    CrawlerSource

CrawlerJob Aggregate
    CrawlerJob

ReadingProgress Aggregate
    ReadingProgress

User Aggregate
    User
```

Đây **chưa phải thiết kế cuối cùng**.

Buổi 20 chúng ta sẽ workshop lại từng cái.

---

# 49. Một lỗi cực phổ biến khi học DDD

Người mới thường nghĩ:

```text
Aggregate = object lớn nhất
```

Không đúng.

Aggregate là:

```text
boundary của consistency
```

Chứ không phải:

```text
boundary của tất cả dữ liệu liên quan
```

---

# 50. Một lỗi khác

Người mới thường nghĩ:

```text
Story
 └── Chapter
```

thì:

```text
Chapter phải thuộc Story Aggregate
```

Không nhất thiết.

Có thể:

```text
Story Aggregate
```

chỉ chứa:

```text
Story
```

và:

```text
Chapter Aggregate
```

riêng.

Nếu business requirements cho phép.

---

# 51. Quy tắc thiết kế Aggregate

Hãy ghi nhớ 6 câu sau:

### 1.

> **Protect invariants inside the Aggregate.**

### 2.

> **One Aggregate has one Root.**

### 3.

> **External code accesses the Aggregate through the Root.**

### 4.

> **Repository thường làm việc với Aggregate Root.**

### 5.

> **Reference Aggregate khác bằng ID.**

### 6.

> **Thiết kế Aggregate nhỏ nhất có thể nhưng đủ để bảo vệ invariant.**

---

# 52. Mental Model

Khi thiết kế Aggregate, hãy vẽ:

```text
              BUSINESS RULE
                    │
                    ↓
             cần consistency?
                    │
              ┌─────┴─────┐
             YES          NO
              │            │
              ↓            ↓
        cùng Aggregate   có thể tách
              │
              ↓
        Aggregate Root
              │
              ↓
      kiểm soát mutation
              │
              ↓
        transaction
```

Đây là tư duy rất đáng luyện.

---

# 53. Bài tập Buổi 16

Với hệ thống đọc truyện:

```text
Story
Chapter
User
ReadingProgress
CrawlerSource
CrawlerJob
```

hãy trả lời:

### Câu 1

Nếu rule:

```text
Không được có 2 Chapter cùng number trong Story
```

thì:

```text
ChapterNumber
Chapter
Story
```

ai nên bảo vệ invariant?

---

### Câu 2

Nếu:

```text
User đánh dấu Chapter 100 đã đọc
```

có nhất thiết phải load:

```text
Story
Chapter 1 → 99
Chapter 100
```

không?

Tại sao?

---

### Câu 3

Nếu:

```text
Story
```

có 10.000 Chapter, bạn có nên thiết kế:

```python
story.chapters: list[Chapter]
```

và load toàn bộ mỗi lần lấy Story không?

---

### Câu 4

Nếu:

```text
Story
```

cần biết tác giả:

```python
story.author: User
```

hay:

```python
story.author_id: UserId
```

cách nào phù hợp hơn nếu `User` là Aggregate khác?

---

# 54. Bài tập code

Hãy tự implement:

```text
Story Aggregate Root
Chapter Entity
```

với:

```python
story.add_chapter(chapter)
story.remove_chapter(chapter_id)
story.rename_chapter(chapter_id, title)
```

và bảo vệ:

```text
1. Chapter number > 0
2. Chapter title != ""
3. Không duplicate ChapterNumber
4. Không truy cập trực tiếp để mutate collection
```

Đặc biệt hãy làm cho đoạn này **không thể sử dụng được**:

```python
story.chapters.append(chapter)
```

---

# 55. Tóm tắt Buổi 16

Cuối buổi này, bạn cần hình dung:

```text
                    Aggregate
                        │
                ┌───────┴───────┐
                │               │
           Aggregate Root    Internal Objects
                │               │
                │          Entity / VO
                │
          Business Behavior
                │
          Protect Invariant
                │
        ┌───────┴────────┐
        ↓                ↓
Consistency         Transaction
Boundary             Boundary
```

Và với hệ thống đọc truyện:

```text
┌─────────────────────────────┐
│       Story Aggregate       │
│                             │
│  Story ← Aggregate Root     │
│    │                        │
│    ├── Chapter              │
│    ├── Chapter              │
│    └── Chapter              │
│                             │
│  invariant:                 │
│  ChapterNumber unique       │
└─────────────────────────────┘
```

**Buổi 17 — Aggregate Root** sẽ đi sâu hơn vào chính `Story` Root: tại sao `story.add_chapter()` tốt hơn `story.chapters.append()`, cách encapsulation Entity con, cách thiết kế API của Aggregate và cách Repository chỉ làm việc với Root.
