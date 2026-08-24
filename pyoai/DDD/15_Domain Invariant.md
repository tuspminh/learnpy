# DDD Deep Dive — Buổi 15

# Domain Invariant

Đây là một trong những buổi **quan trọng nhất của Tactical DDD**.

Sau Buổi 14, chúng ta đã có:

```text
Entity
├── Identity
├── State
└── Behavior

Value Object
├── Value
├── Validation
└── Immutability
```

Nhưng vẫn còn một câu hỏi lớn:

> **Làm thế nào đảm bảo Domain Model không bao giờ rơi vào trạng thái mà business không cho phép?**

Câu trả lời là:

# Domain Invariant

---

# 1. Invariant là gì?

**Invariant** là một điều kiện phải luôn đúng trong Domain.

Ví dụ hệ thống đọc truyện:

```text
ChapterNumber > 0
```

Đây là invariant.

Hoặc:

```text
Story phải có title
```

Cũng có thể là invariant.

Hoặc:

```text
Story đã ARCHIVED
không thể quay lại DRAFT
```

Đây cũng là invariant.

Có thể hiểu đơn giản:

```text
Invariant = Điều kiện Domain không được phép bị phá vỡ
```

---

# 2. Ví dụ đời thường

Một tài khoản ngân hàng:

```text
balance >= 0
```

nếu business không cho phép overdraft.

Ta không muốn:

```python
account.balance = -100_000
```

Nếu điều đó xảy ra:

```text
Domain Model
    ↓
INVALID
```

Invariant chính là hàng rào bảo vệ.

---

# 3. Validation và Invariant không giống nhau

Đây là điểm rất dễ nhầm.

Ví dụ:

```python
title = StoryTitle("")
```

và:

```python
story.publish()
```

có thể đều phát sinh exception.

Nhưng bản chất khác nhau.

---

## Validation

Validation hỏi:

> Input này có hợp lệ không?

Ví dụ:

```python
StoryTitle("")
```

→ invalid.

---

## Invariant

Invariant hỏi:

> Object/Domain có đang ở trạng thái hợp lệ không?

Ví dụ:

```text
Story
status = ARCHIVED
```

không được phép:

```python
story.publish()
```

---

# 4. Nhìn theo pipeline

```text
Raw Input
    ↓
Validation
    ↓
Value Object
    ↓
Entity
    ↓
Domain Behavior
    ↓
Invariant
```

Ví dụ:

```text
"   One Piece   "
       ↓
normalize
       ↓
"One Piece"
       ↓
StoryTitle
       ↓
Story
```

---

# 5. Structural Rule

Một loại invariant là **structural invariant**.

Nó mô tả cấu trúc phải luôn hợp lệ.

Ví dụ:

```text
Story.title != None
Story.id != None
Chapter.number > 0
```

---

# 6. Business Rule

Business rule thường thể hiện hành vi Domain.

Ví dụ:

```text
Chỉ Story PUBLISHED mới được COMPLETE.
```

Ta có:

```python
def complete(self):
    if self.status != StoryStatus.PUBLISHED:
        raise InvalidStoryTransition(...)
```

Đây là business invariant/rule của lifecycle.

---

# 7. Hai loại rule có thể trông giống nhau

Ví dụ:

```text
ChapterNumber > 0
```

và:

```text
Chỉ chapter đã được publish mới có thể đọc.
```

Cả hai đều là Domain rule.

Nhưng:

```text
ChapterNumber > 0
```

gắn với **giá trị của object**.

Còn:

```text
publish → read
```

gắn với **lifecycle/behavior**.

---

# 8. Tại sao invariant quan trọng?

Hãy tưởng tượng Domain không có invariant.

Ta có:

```python
story.status = StoryStatus.ARCHIVED
```

Sau đó:

```python
story.status = StoryStatus.DRAFT
```

Rồi:

```python
story.publish()
```

Code vẫn chạy.

Nhưng Domain đã trở nên vô nghĩa.

---

# 9. Mục tiêu của Domain Model

Một mục tiêu rất quan trọng:

> **Không cho phép invalid state tồn tại.**

Ví dụ:

```text
BAD

Story
├── id = None
├── title = ""
└── status = "abc"
```

Model tốt:

```text
GOOD

Story
├── StoryId
├── StoryTitle
└── StoryStatus
```

Từng thành phần đã có constraint.

---

# 10. Value Object bảo vệ invariant nhỏ

Ví dụ:

```python
@dataclass(frozen=True)
class ChapterNumber:
    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError(
                "Chapter number must be positive"
            )
```

Invariant:

```text
ChapterNumber.value > 0
```

Từ đây trở đi:

```python
number: ChapterNumber
```

ta có thể tin:

```text
number.value > 0
```

---

# 11. Entity bảo vệ invariant lớn hơn

Ví dụ Story:

```python
class Story:
    status: StoryStatus
```

Invariant:

```text
DRAFT
 → PUBLISHED
 → COMPLETED
 → ARCHIVED
```

Không được:

```text
DRAFT → COMPLETED
DRAFT → ARCHIVED
PUBLISHED → DRAFT
COMPLETED → DRAFT
ARCHIVED → PUBLISHED
```

Entity phải bảo vệ lifecycle này.

---

# 12. Đừng expose state tùy tiện

Một thiết kế nguy hiểm:

```python
@dataclass
class Story:
    status: StoryStatus
```

Code bên ngoài có thể:

```python
story.status = StoryStatus.ARCHIVED
```

và bỏ qua business rules.

---

# 13. Encapsulation

Thay vì:

```python
story.status = StoryStatus.COMPLETED
```

hãy:

```python
story.complete()
```

Tại sao?

Vì:

```text
story.complete()
```

có thể kiểm tra invariant.

---

# 14. Ví dụ

```python
def complete(self):
    if self.status != StoryStatus.PUBLISHED:
        raise InvalidStoryTransition(
            "Only published story can be completed"
        )

    self.status = StoryStatus.COMPLETED
```

Bây giờ:

```text
PUBLISHED
    ↓
complete()
    ↓
COMPLETED
```

là transition được kiểm soát.

---

# 15. Nhưng có một vấn đề

Python không có:

```text
private field
```

theo nghĩa tuyệt đối.

Ta có thể dùng convention:

```python
self._status
```

và property:

```python
@property
def status(self):
    return self._status
```

---

# 16. Thiết kế tốt hơn

```python
class Story:
    def __init__(self, ...):
        self._status = StoryStatus.DRAFT

    @property
    def status(self) -> StoryStatus:
        return self._status

    def publish(self):
        ...
```

Code bên ngoài:

```python
story.status
```

để đọc.

Nhưng không nên:

```python
story.status = ...
```

---

# 17. Tuy nhiên `dataclass` vẫn rất hữu ích

Ta có thể:

```python
@dataclass(eq=False)
class Story:
    id: StoryId
    title: StoryTitle
    source_id: SourceId
    _status: StoryStatus = StoryStatus.DRAFT

    @property
    def status(self):
        return self._status
```

Đây là một pattern Python khá thực dụng.

---

# 18. Invariant phải nằm ở đâu?

Đây là câu hỏi quan trọng.

Giả sử:

```text
UI
Application
Domain
Repository
Database
```

Invariant nên nằm ở:

# Domain

Không phải:

```text
UI
```

và không nên chỉ dựa vào:

```text
Database
```

---

# 19. Vì sao không để UI?

Ví dụ PySide6:

```python
if title_edit.text():
    ...
```

Đây chỉ là UX validation.

Một CLI cũng có thể gọi Domain:

```text
CLI
 ↓
Application
 ↓
Domain
```

Nếu invariant chỉ nằm trong UI:

```text
CLI → bypass
```

---

# 20. Vì sao không chỉ để Database?

Database có thể có:

```sql
CHECK (...)
```

rất tốt.

Nhưng Domain vẫn cần bảo vệ invariant.

Vì Domain có thể được gọi bởi:

```text
CLI
API
GUI
Worker
Crawler
Test
Message Handler
```

Tất cả đều phải chịu cùng business rules.

---

# 21. Defense in depth

Thiết kế tốt có thể là:

```text
UI
 ↓
UX Validation
 ↓
Application
 ↓
Domain
 ↓
Database Constraint
```

Mỗi layer có vai trò riêng.

---

# 22. Phân biệt 3 loại validation

## UI Validation

Mục tiêu:

```text
User experience
```

Ví dụ:

```text
"Title cannot be empty"
```

hiển thị ngay trên form.

---

## Domain Validation

Mục tiêu:

```text
Business correctness
```

Ví dụ:

```python
StoryTitle("")
```

→ exception.

---

## Database Constraint

Mục tiêu:

```text
Data integrity
```

Ví dụ:

```sql
CHECK (chapter_number > 0)
```

---

# 23. Một invariant quan trọng của Story

Giả sử:

```text
Story
```

phải có ít nhất một chapter trước khi publish.

Đây là một invariant phức tạp hơn.

Ta không thể chỉ kiểm tra:

```python
StoryTitle
```

mà phải kiểm tra relationship:

```text
Story
   ↓
Chapters
   ↓
len(chapters) > 0
```

---

# 24. Đây là lúc Aggregate xuất hiện

Nếu:

```text
Story
```

phải bảo vệ:

```text
Story + Chapters
```

thì chúng ta bắt đầu có câu hỏi:

> Ai chịu trách nhiệm bảo vệ invariant giữa nhiều Entity?

Đó chính là một trong những lý do Aggregate tồn tại.

Buổi này chỉ cần nhớ:

```text
Invariant xuyên nhiều object
        ↓
Aggregate boundary rất quan trọng
```

---

# 25. Ví dụ invariant đơn giản

Giả sử:

```text
Chapter number phải unique trong Story
```

Không thể có:

```text
Story
├── Chapter 1
├── Chapter 2
├── Chapter 2   ← invalid
└── Chapter 3
```

Đây không còn là invariant của `ChapterNumber` riêng lẻ.

Vì:

```python
ChapterNumber(2)
```

hoàn toàn hợp lệ.

Vấn đề nằm ở:

```text
Story + collection of Chapters
```

---

# 26. Đây là distinction cực kỳ quan trọng

```text
ChapterNumber(2)
```

→ hợp lệ.

Nhưng:

```text
Story
├── Chapter(2)
└── Chapter(2)
```

→ có thể không hợp lệ.

Do đó:

```text
Value Object invariant
        ≠
Entity invariant
        ≠
Aggregate invariant
```

---

# 27. Invariant của Value Object

Ví dụ:

```python
ChapterNumber(0)
```

invalid.

Invariant:

```text
value > 0
```

Nằm trong:

```text
ChapterNumber
```

---

# 28. Invariant của Entity

Ví dụ:

```text
Story
```

không thể:

```text
ARCHIVED → PUBLISHED
```

Invariant/lifecycle rule nằm trong:

```text
Story
```

---

# 29. Invariant của Aggregate

Ví dụ:

```text
Story
```

không được có hai Chapter cùng number.

Rule nằm ở:

```text
Story Aggregate
```

chứ không nằm trong:

```text
ChapterNumber
```

---

# 30. Một lỗi thiết kế phổ biến

Đưa tất cả validation vào Entity:

```python
class Story:
    def validate(self):
        ...
```

và:

```python
if not story.validate():
    ...
```

Cách này dễ dẫn đến:

```text
Object invalid
    ↓
validate()
    ↓
phát hiện invalid
```

Trong Domain mạnh hơn:

```text
Create/Change
    ↓
check invariant
    ↓
Invalid operation → exception
```

---

# 31. Fail Fast

Ví dụ:

```python
story.rename(StoryTitle(""))
```

Không nên để:

```text
Story
 ↓
invalid title
 ↓
repository.save()
 ↓
database error
```

Mà nên:

```text
Story.rename()
 ↓
StoryTitle validation
 ↓
exception
```

Ngay tại Domain boundary.

---

# 32. Domain Exception

Nên tạo exception riêng:

```python
class DomainError(Exception):
    pass


class InvalidStoryTransition(DomainError):
    pass


class InvalidStoryTitle(DomainError):
    pass


class InvalidChapterNumber(DomainError):
    pass
```

Sau này Application Layer có thể:

```python
try:
    ...
except DomainError as exc:
    ...
```

---

# 33. Một hierarchy đơn giản

```text
Exception
   │
   └── DomainError
         ├── InvalidStoryTitle
         ├── InvalidChapterNumber
         └── InvalidStoryTransition
```

Điều này rất hữu ích khi xây Application Layer.

---

# 34. Invariant và constructor

Constructor nên đảm bảo:

```text
Story mới
    ↓
valid
```

Ví dụ:

```python
Story(
    id=...,
    title=...,
    source_id=...,
    status=StoryStatus.ARCHIVED,
)
```

Nếu Domain không cho phép tạo Archived Story thì constructor không nên cho phép tùy ý.

---

# 35. Factory giải quyết vấn đề này

```python
@classmethod
def create(
    cls,
    id: StoryId,
    title: StoryTitle,
    source_id: SourceId,
) -> "Story":

    return cls(
        id=id,
        title=title,
        source_id=source_id,
        _status=StoryStatus.DRAFT,
    )
```

Bây giờ:

```text
Story.create()
```

luôn bắt đầu:

```text
DRAFT
```

---

# 36. Nhưng Repository cần load Story

Đây là vấn đề sâu hơn.

Database có thể chứa:

```text
status = completed
```

Repository phải tạo lại Entity:

```python
Story.reconstitute(...)
```

không nên dùng:

```python
Story.create(...)
```

vì `create()` dành cho **new entity**.

---

# 37. `create()` vs `reconstitute()`

Đây là pattern rất hữu ích.

```python
@classmethod
def create(...):
    ...
```

dành cho:

```text
New Domain Entity
```

Còn:

```python
@classmethod
def reconstitute(...):
    ...
```

dành cho:

```text
Database → Domain
```

Ví dụ:

```python
@classmethod
def reconstitute(
    cls,
    id: StoryId,
    title: StoryTitle,
    source_id: SourceId,
    status: StoryStatus,
) -> "Story":
    return cls(
        id=id,
        title=title,
        source_id=source_id,
        _status=status,
    )
```

---

# 38. Vì sao điều này quan trọng?

Khi load từ DB:

```text
SQLite
 ↓
Repository
 ↓
Story.reconstitute()
 ↓
Story Entity
```

Entity không cần:

```text
UI
ORM
SQLite
```

để tồn tại.

Domain độc lập.

---

# 39. Invariant trong reconstitution

Đây là câu hỏi khó:

> Nếu database chứa dữ liệu invalid thì sao?

Ví dụ:

```text
status = "WHAT?"
```

Repository không được silently tạo Entity invalid.

Có thể:

```python
StoryStatus(status)
```

và fail.

Hoặc Domain factory/reconstitution kiểm tra invariant.

---

# 40. Domain phải tin chính mình

Một khi:

```python
story = Story.reconstitute(...)
```

trả về thành công:

ta muốn có guarantee:

```text
story là valid Domain Entity
```

Không nên có:

```text
"Entity này có thể invalid nhưng database chắc chắn đúng."
```

Đó là thiết kế nguy hiểm.

---

# 41. Invariant và Setter

Tránh:

```python
@property
def status(self):
    return self._status

@status.setter
def status(self, value):
    self._status = value
```

vì:

```python
story.status = StoryStatus.ARCHIVED
```

bypass lifecycle.

Thay bằng:

```python
story.publish()
story.complete()
story.archive()
```

Behavior method chính là nơi bảo vệ invariant.

---

# 42. Đây là nguyên tắc rất quan trọng

> **Không expose mutation nếu mutation đó có business rule.**

Ví dụ:

```text
title thay đổi
```

có thể:

```python
story.rename(...)
```

thay vì:

```python
story.title = ...
```

---

# 43. Anemic Domain Model

Một model kiểu:

```python
@dataclass
class Story:
    id: StoryId
    title: StoryTitle
    status: StoryStatus
```

và tất cả logic nằm ngoài:

```python
publish_story(story)
complete_story(story)
archive_story(story)
```

có nguy cơ trở thành:

> **Anemic Domain Model**

Entity chỉ chứa data, không chứa behavior.

---

# 44. Rich Domain Model

Thay vào đó:

```python
story.publish()
story.complete()
story.archive()
story.rename(...)
```

Behavior nằm gần state và invariant.

Đây thường là hướng phù hợp với DDD.

---

# 45. Nhưng không phải mọi logic đều nằm Entity

Ví dụ:

```text
Tính ranking của 10.000 stories
```

không nhất thiết đặt trong:

```python
Story.calculate_global_ranking()
```

Nếu logic liên quan nhiều Entity và không tự nhiên thuộc về một Entity cụ thể, có thể dùng:

```text
Domain Service
```

Chúng ta sẽ học kỹ hơn sau.

---

# 46. Invariant và Domain Service

Ví dụ:

```text
Story recommendation
```

dựa trên:

```text
Story
User
ReadingHistory
Genre
```

Đây có thể không thuộc riêng `Story`.

Khi đó:

```text
Domain Service
```

có thể phù hợp.

Nhưng Service vẫn phải **bảo vệ Domain rules**, không biến thành "God Service".

---

# 47. Một ví dụ hoàn chỉnh

```python
class Story:
    def __init__(
        self,
        id: StoryId,
        title: StoryTitle,
        source_id: SourceId,
        status: StoryStatus,
    ):
        self._id = id
        self._title = title
        self._source_id = source_id
        self._status = status

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def source_id(self):
        return self._source_id

    @property
    def status(self):
        return self._status

    def rename(self, title: StoryTitle):
        self._title = title

    def publish(self):
        if self._status != StoryStatus.DRAFT:
            raise InvalidStoryTransition(
                "Story must be draft"
            )

        self._status = StoryStatus.PUBLISHED

    def complete(self):
        if self._status != StoryStatus.PUBLISHED:
            raise InvalidStoryTransition(
                "Story must be published"
            )

        self._status = StoryStatus.COMPLETED

    def archive(self):
        if self._status != StoryStatus.COMPLETED:
            raise InvalidStoryTransition(
                "Story must be completed"
            )

        self._status = StoryStatus.ARCHIVED
```

Đây là một **rich Entity**.

---

# 48. Invariant map

Hãy hình dung Domain Model của chúng ta như sau:

```text
StoryTitle
   │
   └── invariant:
       title != ""

ChapterNumber
   │
   └── invariant:
       number > 0

Story
   │
   ├── invariant:
   │   identity tồn tại
   │
   └── lifecycle:
       DRAFT
        ↓
       PUBLISHED
        ↓
       COMPLETED
        ↓
       ARCHIVED
```

Sau này:

```text
Story Aggregate
   │
   └── invariant:
       chapter numbers unique
```

---

# 49. Invariant phải được bảo vệ ở mọi mutation path

Đây là điểm cực kỳ quan trọng.

Giả sử có:

```python
story.rename(...)
```

và:

```python
story.set_title(...)
```

và:

```python
story.title = ...
```

thì có quá nhiều mutation path.

Thiết kế tốt:

```text
Change title
     ↓
rename()
     ↓
one controlled path
```

---

# 50. "One source of truth"

Nếu rule:

```text
Story chỉ được publish từ DRAFT
```

thì rule đó phải nằm ở một nơi rõ ràng:

```python
def publish(self):
    ...
```

Không nên copy:

```text
UI check
Application check
Repository check
Domain check
```

mỗi nơi một phiên bản khác nhau.

UI có thể pre-check.

Application có thể orchestrate.

Nhưng **Domain là authority cuối cùng về business rule**.

---

# 51. Invariant không nhất thiết là validation

Một invariant có thể được đảm bảo bằng behavior.

Ví dụ:

```text
balance >= 0
```

Không nhất thiết có:

```python
validate_balance()
```

Mà:

```python
def withdraw(self, amount):
    if self.balance - amount < 0:
        raise InsufficientFunds()
```

Behavior không cho invariant bị phá vỡ.

---

# 52. Đây là tư duy quan trọng nhất của buổi học

Đừng nghĩ:

```text
"Validation ở đâu?"
```

Hãy nghĩ:

> **"Domain nào chịu trách nhiệm đảm bảo điều này luôn đúng?"**

Ví dụ:

```text
title không rỗng
        ↓
StoryTitle

chapter number > 0
        ↓
ChapterNumber

Story lifecycle
        ↓
Story

chapter number unique trong Story
        ↓
Aggregate
```

Đây chính là cách tư duy Domain Modeling.

---

# 53. Tổng kết Buổi 15

Bạn cần phân biệt rõ:

| Khái niệm              | Ý nghĩa                     |
| ---------------------- | --------------------------- |
| Validation             | Kiểm tra input              |
| Value Object invariant | Giá trị luôn hợp lệ         |
| Entity invariant       | Entity luôn hợp lệ          |
| Business Rule          | Quy tắc nghiệp vụ           |
| Aggregate invariant    | Nhiều object phải nhất quán |
| UI validation          | Hỗ trợ UX                   |
| DB constraint          | Bảo vệ data integrity       |

---

# 54. Công thức tư duy

Khi gặp một business rule, hãy hỏi:

```text
Rule này thuộc về ai?
       │
       ├── Một Value Object?
       │
       ├── Một Entity?
       │
       ├── Nhiều Entity?
       │      ↓
       │   Aggregate?
       │
       └── Không thuộc Entity nào?
              ↓
          Domain Service?
```

Đây là kỹ năng quan trọng hơn việc thuộc lòng định nghĩa DDD.

---

# 55. Bài tập Buổi 15

Hãy thiết kế invariant cho hệ thống đọc truyện:

### Story

```text
1. title không rỗng
2. status chỉ được transition theo:
   DRAFT → PUBLISHED → COMPLETED → ARCHIVED
3. ARCHIVED không được sửa title
```

### Chapter

```text
1. number > 0
2. title không rỗng
3. content không được null
```

### Story + Chapter

Giả sử business rule:

```text
4. Không được có hai chapter
   cùng ChapterNumber trong một Story.
```

Hãy xác định:

```text
Rule 1 → ?
Rule 2 → ?
Rule 3 → ?
Rule 4 → ?
```

**Đặc biệt Rule 4:** đừng vội nhét nó vào `ChapterNumber`. Hãy suy nghĩ xem **object nào thực sự có đủ thông tin để bảo vệ rule này**.

---

## Sau Buổi 15

Phần Tactical DDD tiếp theo nên đi vào:

```text
Buổi 16 — Aggregate
    ↓
Aggregate là gì?
Aggregate Root
Boundary
Consistency Boundary
Invariant Boundary
Story + Chapter
```

Đây là bước rất tự nhiên sau khi bạn đã hiểu **Entity + Value Object + Domain Invariant**.
