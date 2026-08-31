# DDD Deep Dive — Buổi 28

# Use Case Design

Buổi này chúng ta sẽ đi sâu vào **thiết kế Use Case/Application Service**.

Nếu Buổi 27 trả lời:

> Application Service làm gì?

thì Buổi 28 trả lời:

> **Một Use Case nên nhận input, xử lý và trả output như thế nào?**

Đặc biệt, ta sẽ thiết kế sao cho cùng một Use Case có thể được gọi từ:

```text
PySide6
CLI
REST API
Crawler Worker
Test
```

mà **Domain không cần biết caller là ai**.

---

# 1. Use Case là gì?

Use Case biểu diễn **một hành động mà hệ thống cung cấp cho Actor**.

Ví dụ hệ thống đọc truyện:

```text
CreateStory
AddChapter
PublishStory
StartCrawler
CompleteCrawlerJob
UpdateReadingProgress
```

Mỗi cái là một Use Case.

Ta có thể hình dung:

```text
Actor
  │
  ▼
Use Case
  │
  ▼
Domain
```

Ví dụ:

```text
User
 ↓
AddChapterUseCase
 ↓
Story.add_chapter()
```

---

# 2. Một Use Case có 3 phần chính

```text
Input
  ↓
Use Case
  ↓
Output
```

Ví dụ:

```text
AddChapterCommand
        ↓
AddChapterUseCase
        ↓
ChapterResult
```

Đây là nền tảng của bài hôm nay.

---

# 3. Không nên truyền UI object vào Use Case

Ví dụ PySide6:

```python
def on_add_clicked(self):
    title = self.title_input.text()
    content = self.content_input.toPlainText()

    self.use_case.execute(
        self.title_input,
        self.content_input,
    )
```

❌ Không tốt.

Application Layer bắt đầu phụ thuộc UI.

Use Case không nên biết:

```text
QLineEdit
QTextEdit
QComboBox
QMessageBox
```

---

# 4. Hãy truyền dữ liệu thuần

Ví dụ:

```python
self.use_case.execute(
    title=title,
    content=content,
)
```

Tốt hơn nữa:

```python
command = AddChapterCommand(
    story_id=story_id,
    chapter_number=10,
    title=title,
    content=content,
)

self.use_case.execute(command)
```

---

# 5. Input DTO

DTO = **Data Transfer Object**.

Input DTO mô tả dữ liệu mà Use Case cần.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AddChapterCommand:
    story_id: str
    chapter_number: int
    title: str
    content: str
```

Ta có:

```text
PySide6
   ↓
AddChapterCommand
   ↓
AddChapterUseCase
```

---

# 6. Tại sao dùng DTO?

Thay vì:

```python
use_case.execute(
    story_id,
    chapter_number,
    title,
    content,
)
```

ta có:

```python
use_case.execute(
    AddChapterCommand(
        story_id=story_id,
        chapter_number=chapter_number,
        title=title,
        content=content,
    )
)
```

Ưu điểm:

* dễ đọc
* khó truyền nhầm argument
* dễ mở rộng
* dễ test
* caller không cần biết internal implementation

---

# 7. Command là gì?

Trong Use Case Architecture:

```text
Command
=
request to perform an action
```

Ví dụ:

```python
@dataclass(frozen=True)
class CreateStoryCommand:
    title: str
    source_id: str
```

Nó nói:

> "Hãy tạo Story với những dữ liệu này."

---

# 8. Command không phải Domain Entity

Đây là điểm rất quan trọng.

```python
CreateStoryCommand
```

không phải:

```python
Story
```

Command chỉ là:

```text
Application input
```

Trong khi:

```text
Story
```

là:

```text
Domain Entity
```

---

# 9. Flow đầy đủ

```text
PySide6
   │
   │  CreateStoryCommand
   ▼
Application
   │
   │  Create Story
   ▼
Domain
   │
   │  Story(...)
   ▼
Repository
   │
   ▼
SQLite
```

---

# 10. Output DTO

Tương tự Input DTO, Use Case có thể trả Output DTO.

Ví dụ:

```python
@dataclass(frozen=True)
class StoryResult:
    id: str
    title: str
    status: str
```

Use Case:

```python
class CreateStoryUseCase:

    def execute(
        self,
        command: CreateStoryCommand,
    ) -> StoryResult:

        ...
```

---

# 11. Tại sao không trả Entity?

Có thể trả:

```python
return story
```

nhưng thường không muốn Application consumer phụ thuộc trực tiếp vào Domain Entity.

Ví dụ PySide6 không nên phải biết:

```python
story._status
story._title
story._source_id
```

Thay vào đó:

```python
result.status
result.title
```

---

# 12. Domain Entity vs Output DTO

```text
Story
```

có:

```text
behavior
invariant
identity
domain state
```

Trong khi:

```text
StoryResult
```

chỉ có:

```text
data
```

Ví dụ:

```python
@dataclass(frozen=True)
class StoryResult:
    id: str
    title: str
    status: str
```

Không có:

```python
def publish()
def add_chapter()
```

---

# 13. Một Use Case hoàn chỉnh

Ta xây `CreateStoryUseCase`.

## Command

```python
@dataclass(frozen=True)
class CreateStoryCommand:
    title: str
    source_id: str
```

## Result

```python
@dataclass(frozen=True)
class CreateStoryResult:
    story_id: str
```

---

# 14. Use Case

```python
class CreateStoryUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        command: CreateStoryCommand,
    ) -> CreateStoryResult:

        with self.uow:

            story = Story.create(
                title=command.title,
                source_id=command.source_id,
            )

            self.uow.stories.add(story)

            self.uow.commit()

            return CreateStoryResult(
                story_id=str(story.id)
            )
```

Đây là Application Service rất sạch.

---

# 15. Phân tích trách nhiệm

```python
Story.create(...)
```

→ Domain.

```python
uow.stories.add(...)
```

→ Repository.

```python
uow.commit()
```

→ Transaction.

```python
CreateStoryCommand
```

→ Application input.

```python
CreateStoryResult
```

→ Application output.

```python
CreateStoryUseCase
```

→ Orchestration.

---

# 16. Command không nên chứa business logic

Sai:

```python
@dataclass
class CreateStoryCommand:

    title: str

    def validate_business_rule(self):
        ...
```

Đừng biến Command thành Domain Object.

Command chủ yếu là:

```text
data
```

---

# 17. Nhưng DTO có validation không?

Có thể có **structural/input validation**, tùy kiến trúc.

Ví dụ:

```python
if not isinstance(command.title, str):
    raise TypeError(...)
```

Nhưng business invariant như:

> Story title không được rỗng.

thường nên được bảo vệ ở Domain:

```python
StoryTitle(...)
```

hoặc:

```python
Story.create(...)
```

Điều này đảm bảo Domain không thể bị bypass nếu nó được tạo từ nơi khác.

---

# 18. Application validation vs Domain invariant

Đây là ranh giới quan trọng.

### Application validation

```text
request có đủ field không?
type có đúng không?
format input có đúng không?
```

### Domain invariant

```text
business state có hợp lệ không?
```

Ví dụ:

```text
chapter_number
```

không được:

```text
<= 0
```

→ `ChapterNumber` có thể bảo vệ.

---

# 19. Result Pattern

Không phải Use Case nào cũng chỉ:

```python
return result
```

hoặc:

```python
raise Exception
```

Ta có thể thiết kế:

```text
Result
 ├── Success
 └── Failure
```

Ví dụ:

```python
@dataclass(frozen=True)
class Result:
    success: bool
    value: object | None = None
    error: str | None = None
```

---

# 20. Nhưng đừng lạm dụng Result

Trong Python, exception là cơ chế tự nhiên.

Ví dụ:

```python
story = repo.get(story_id)

if story is None:
    raise StoryNotFound(story_id)
```

Đây hoàn toàn hợp lý.

Không nhất thiết phải biến mọi thứ thành:

```python
Result[Story, Error]
```

DDD không yêu cầu Result Pattern.

---

# 21. Domain Exception

Ta có thể định nghĩa:

```python
class DomainError(Exception):
    pass


class StoryNotFound(DomainError):
    pass


class StoryCannotBePublished(DomainError):
    pass
```

Nhưng cần phân biệt:

```text
Not Found
```

có thể là application/repository concern,

trong khi:

```text
Cannot Publish
```

rõ ràng là domain business error.

---

# 22. Một cấu trúc exception tốt

```text
DomainError
   │
   ├── InvalidStory
   ├── StoryCannotBePublished
   ├── ChapterAlreadyExists
   └── InvalidChapterNumber
```

Application layer có thể bắt và chuyển thành:

```text
CLI error
GUI message
HTTP response
```

---

# 23. Use Case không nên hiển thị lỗi

Sai:

```python
class PublishStoryUseCase:

    def execute(...):

        try:
            ...
        except StoryCannotBePublished:
            QMessageBox.warning(
                None,
                "Error",
                "Cannot publish",
            )
```

❌

Use Case không biết PySide6.

---

# 24. UI xử lý lỗi

Ví dụ:

```python
try:
    result = use_case.execute(command)

except StoryCannotBePublished as exc:
    QMessageBox.warning(
        self,
        "Cannot publish",
        str(exc),
    )
```

Flow:

```text
Domain Exception
       ↓
Application
       ↓
UI
```

UI quyết định cách hiển thị.

---

# 25. CLI cũng có thể dùng cùng Use Case

```python
try:
    result = use_case.execute(command)

except StoryCannotBePublished as exc:
    print(f"Error: {exc}")
```

Cùng Use Case.

Khác Interface.

```text
PySide6 ─┐
         ├── PublishStoryUseCase
CLI ─────┘
```

Đây là lợi ích cực lớn.

---

# 26. REST API cũng có thể dùng

Ví dụ:

```text
POST /stories/{id}/publish
```

Controller:

```python
try:
    result = publish_story.execute(
        PublishStoryCommand(
            story_id=story_id
        )
    )

except StoryCannotBePublished:
    return 409
```

Use Case vẫn không biết HTTP.

---

# 27. Một Use Case — nhiều Interface

```text
                 ┌── PySide6
                 │
                 ├── CLI
                 │
                 ├── REST API
                 │
                 └── Worker
                       │
                       ▼
               Application Use Case
                       │
                       ▼
                    Domain
```

Đây là một trong những mục tiêu quan trọng của Clean Architecture.

---

# 28. Input DTO có nên dùng Domain Value Object?

Có hai lựa chọn.

### Cách 1

```python
@dataclass(frozen=True)
class AddChapterCommand:
    story_id: str
    chapter_number: int
    title: str
    content: str
```

Application chuyển đổi:

```python
chapter_number = ChapterNumber(
    command.chapter_number
)
```

### Cách 2

```python
@dataclass(frozen=True)
class AddChapterCommand:
    story_id: StoryId
    chapter_number: ChapterNumber
    title: StoryTitle
```

Cách này làm Application API domain-oriented hơn.

Không có một quy tắc tuyệt đối.

---

# 29. Với project của bạn, tôi khuyên

Ở boundary:

```text
CLI / GUI
```

dùng primitive hoặc DTO:

```python
@dataclass(frozen=True)
class AddChapterCommand:
    story_id: str
    chapter_number: int
    title: str
    content: str
```

Sau đó Application chuyển thành Domain types:

```python
story_id = StoryId(command.story_id)

number = ChapterNumber(
    command.chapter_number
)

title = ChapterTitle(
    command.title
)
```

Flow:

```text
External Input
     ↓
Command
     ↓
Domain Value Objects
     ↓
Aggregate
```

---

# 30. Tại sao cách này tốt?

Giả sử CLI nhận:

```text
chapter_number = "10"
```

Application có thể convert:

```python
number = int(command.chapter_number)
```

Sau đó:

```python
ChapterNumber(number)
```

Domain đảm bảo invariant.

---

# 31. Command cho AddChapter

```python
@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    chapter_number: int
    title: str
    content: str
```

Result:

```python
@dataclass(frozen=True)
class AddChapterResult:

    chapter_id: str
    story_id: str
```

---

# 32. Use Case

```python
class AddChapterUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        command: AddChapterCommand,
    ) -> AddChapterResult:

        with self.uow:

            story = self.uow.stories.get(
                StoryId(command.story_id)
            )

            if story is None:
                raise StoryNotFound(
                    command.story_id
                )

            chapter = Chapter.create(
                number=ChapterNumber(
                    command.chapter_number
                ),
                title=ChapterTitle(
                    command.title
                ),
                content=command.content,
            )

            story.add_chapter(chapter)

            self.uow.stories.save(story)

            self.uow.commit()

            return AddChapterResult(
                chapter_id=str(chapter.id),
                story_id=str(story.id),
            )
```

Đây là một ví dụ rất sát với project đọc truyện của bạn.

---

# 33. Notice điều quan trọng

Application Service không làm:

```python
if command.chapter_number <= 0:
    ...
```

Mà:

```python
ChapterNumber(
    command.chapter_number
)
```

Domain Value Object chịu trách nhiệm invariant.

---

# 34. Application Service cũng không làm:

```python
if story.status == "published":
    ...
```

Nếu đó là business rule:

```python
story.add_chapter(chapter)
```

để Aggregate xử lý.

---

# 35. Command ≠ Event

Hai khái niệm rất dễ nhầm.

### Command

```text
"Please do this."
```

Ví dụ:

```text
AddChapterCommand
```

### Event

```text
"This already happened."
```

Ví dụ:

```text
ChapterAdded
```

Command:

```text
Input
```

Event:

```text
Fact
```

Ta sẽ gặp Domain Event ở phần sau.

---

# 36. Command ≠ Query

Trong CQRS:

```text
Command
→ thay đổi state

Query
→ đọc data
```

Ví dụ:

```text
AddChapterCommand
PublishStoryCommand
StartCrawlerCommand
```

và:

```text
GetStoryQuery
GetChapterQuery
SearchStoriesQuery
```

Use Case design tốt thường phân biệt rõ hai loại.

---

# 37. Một Use Case nên có interface đơn giản

Ví dụ:

```python
class AddChapterUseCase:

    def execute(
        self,
        command: AddChapterCommand,
    ) -> AddChapterResult:
        ...
```

Caller chỉ cần biết:

```text
command → execute → result
```

Không cần biết:

```text
SQLite
SQL
transaction
Entity internals
```

---

# 38. Testing trở nên rất dễ

Test:

```python
def test_add_chapter():

    uow = FakeUnitOfWork()

    use_case = AddChapterUseCase(
        uow
    )

    result = use_case.execute(
        AddChapterCommand(
            story_id="story-1",
            chapter_number=1,
            title="Chapter 1",
            content="Hello",
        )
    )

    assert result.chapter_id
```

Ta không cần PySide6.

Không cần CLI.

Không cần HTTP.

---

# 39. Test business failure

```python
def test_add_duplicate_chapter():

    ...

    with pytest.raises(
        ChapterAlreadyExists
    ):
        use_case.execute(
            AddChapterCommand(
                story_id="story-1",
                chapter_number=1,
                title="Duplicate",
                content="...",
            )
        )
```

Đây là test rất giá trị.

---

# 40. Test transaction

```python
def test_commit_after_success():

    ...

    use_case.execute(command)

    assert uow.committed is True
```

Và:

```python
def test_rollback_after_failure():

    ...

    with pytest.raises(...):
        use_case.execute(command)

    assert uow.rolled_back is True
```

---

# 41. Use Case có nên có `__call__`?

Có thể.

Thay vì:

```python
use_case.execute(command)
```

ta có:

```python
use_case(command)
```

Ví dụ:

```python
class AddChapterUseCase:

    def __call__(
        self,
        command: AddChapterCommand,
    ) -> AddChapterResult:
        ...
```

Nhưng:

```python
execute()
```

thường dễ đọc hơn với người mới.

Tôi khuyên bạn dùng:

```python
execute()
```

ở giai đoạn hiện tại.

---

# 42. Use Case có nên là ABC không?

Không nhất thiết.

Không cần tạo:

```python
class UseCase(ABC):
    ...
```

chỉ vì "DDD phải abstraction".

Nếu không có polymorphism thực sự, class bình thường là đủ:

```python
class AddChapterUseCase:
    ...
```

DDD không đồng nghĩa với việc tạo thật nhiều interface.

---

# 43. Một sai lầm phổ biến

Tạo:

```text
BaseUseCase
BaseCommand
BaseResult
BaseRepository
BaseService
BaseEntity
BaseManager
```

rồi mọi thứ kế thừa chúng.

Kết quả:

```text
Abstract Architecture
```

nhưng business model lại không rõ.

DDD nên bắt đầu từ:

```text
Business
```

không phải từ:

```text
class hierarchy
```

---

# 44. Một Use Case lý tưởng

```text
CreateStoryUseCase
```

có thể nhìn như:

```python
def execute(command):

    validate_input()

    with uow:

        source = load_source()

        story = Story.create(...)

        repository.add(story)

        uow.commit()

        return result
```

Người đọc nhìn vào là hiểu workflow.

---

# 45. Nhưng business logic phải được đẩy xuống

Ví dụ:

```python
story.create(...)
```

Domain xử lý:

```text
Story invariant
StoryTitle
SourceId
status
```

Domain Service xử lý:

```text
cross-entity business rule
```

Application Service chỉ:

```text
orchestrate
```

---

# 46. Kiến trúc Use Case chuẩn

```text
                 Interface
              ┌─────┼─────┐
              │     │     │
             CLI  PySide  API
              │     │     │
              └─────┼─────┘
                    ▼
              Input Command
                    │
                    ▼
             Application Service
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Repository  Entity  Domain Service
          │         │
          └────┬────┘
               ▼
              UoW
               │
               ▼
             SQLite
```

---

# 47. Thiết kế folder

Với project đọc truyện, ta có thể bắt đầu:

```text
src/
└── story_app/
    │
    ├── domain/
    │   ├── story/
    │   ├── chapter/
    │   ├── crawler/
    │   └── user/
    │
    ├── application/
    │   ├── stories/
    │   │   ├── create_story.py
    │   │   ├── publish_story.py
    │   │   └── add_chapter.py
    │   │
    │   ├── crawler/
    │   │   ├── start_crawler.py
    │   │   └── complete_job.py
    │   │
    │   └── reading/
    │       └── update_progress.py
    │
    ├── infrastructure/
    │   └── persistence/
    │
    └── interfaces/
        ├── cli/
        └── pyside6/
```

Điều quan trọng:

```text
interfaces
     ↓
application
     ↓
domain
```

Không đi ngược.

---

# 48. Một Use Case không nên phụ thuộc PySide6

```text
application
    X
    ↓
PySide6
```

Không.

Mà:

```text
PySide6
   ↓
application
```

---

# 49. Một Use Case không nên phụ thuộc SQLite implementation

Không:

```python
class AddChapterUseCase:

    def __init__(self):
        self.connection = sqlite3.connect(...)
```

❌

Mà:

```python
class AddChapterUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

---

# 50. Tổng kết toàn bộ Buổi 28

Ta có:

```text
COMMAND
   ↓
Use Case
   ↓
Domain
   ↓
RESULT
```

Chi tiết:

```text
Input DTO
   ↓
Application Service
   │
   ├── Repository
   ├── Aggregate
   ├── Domain Service
   └── Unit of Work
   │
   ▼
Output DTO
```

---

# 51. Mental Model cần nhớ

Hãy nhớ 5 câu:

### ① Command

> **Tôi muốn hệ thống làm gì?**

```text
AddChapterCommand
```

### ② Use Case

> **Để làm việc đó cần orchestrate những bước nào?**

```text
AddChapterUseCase
```

### ③ Entity/Aggregate

> **Business rule cho phép hay không?**

```python
story.add_chapter(...)
```

### ④ Domain Service

> **Business rule liên quan nhiều domain object nhưng không thuộc tự nhiên một object.**

### ⑤ Result

> **Kết quả của Use Case là gì?**

```text
AddChapterResult
```

---

# 52. Bài tập thực hành

Hãy tự thiết kế 3 Use Case sau:

### Bài 1 — CreateStory

```text
CreateStoryCommand
CreateStoryResult
CreateStoryUseCase
```

Input:

```text
title
source_id
```

Output:

```text
story_id
```

---

### Bài 2 — AddChapter

```text
AddChapterCommand
AddChapterResult
AddChapterUseCase
```

Input:

```text
story_id
chapter_number
title
content
```

Output:

```text
chapter_id
story_id
```

---

### Bài 3 — StartCrawler

```text
StartCrawlerCommand
StartCrawlerResult
StartCrawlerUseCase
```

Input:

```text
source_id
```

Output:

```text
job_id
```

Flow:

```text
source_id
   ↓
load CrawlerSource
   ↓
CrawlerJob.start()
   ↓
repository.add()
   ↓
commit
   ↓
job_id
```

---

# 53. Bài tập nâng cao

Thiết kế:

```text
PublishStoryCommand
PublishStoryResult
PublishStoryUseCase
```

Use Case phải:

```text
1. Load Story
2. Nếu không tồn tại → StoryNotFound
3. Gọi StoryPublicationPolicy
4. Nếu không được publish → StoryCannotBePublished
5. story.publish()
6. save
7. commit
8. trả StoryResult
```

Sau đó trả lời:

> **Trong 8 bước trên, bước nào là Application logic, bước nào là Domain logic?**

Đây là bài tập quan trọng nhất của Buổi 28.

---

## Sơ đồ cuối cùng

```text
                    ┌─────────────┐
                    │   PySide6   │
                    └──────┬──────┘
                           │
                    Command / DTO
                           │
                           ▼
                ┌────────────────────┐
                │ Application Layer  │
                │                    │
                │   Use Case         │
                └─────────┬──────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         Repository    Entity    Domain Service
              │           │           │
              └───────────┼───────────┘
                          ▼
                    Unit of Work
                          │
                          ▼
                        SQLite
                          │
                          ▼
                     Result DTO
                          │
                          ▼
                    PySide6 / CLI
```

**Điểm cốt lõi của Buổi 28:** đừng thiết kế Use Case như một "class chứa nghiệp vụ". Hãy thiết kế nó như **một cổng vào Application Layer**, nhận `Command`, orchestrate Domain, quản lý transaction và trả `Result`; còn **business rules vẫn phải được bảo vệ bởi Domain Model**.
