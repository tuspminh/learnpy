# DDD Deep Dive — Buổi 37

# Command Model

Ở Buổi 36, ta đã phân biệt:

```text
Command → thay đổi hệ thống
Query   → đọc dữ liệu
```

Hôm nay đi sâu vào **Command Model** và đặc biệt là mối quan hệ:

```text
Command
   ↓
Command Handler / Use Case
   ↓
Aggregate
   ↓
Repository
   ↓
Unit of Work
   ↓
Domain Event
   ↓
Outbox
```

---

# 1. Command Model là gì?

Command Model là phần của application chịu trách nhiệm xử lý **ý định thay đổi state**.

Ví dụ hệ thống đọc truyện:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
```

Ta có:

```text
                  COMMAND MODEL

CreateStory ───────┐
AddChapter ────────┤
StartCrawler ──────┤
PauseCrawler ──────┤
ResumeCrawler ─────┘
         │
         ▼
      Use Case
         │
         ▼
       Domain
```

---

# 2. Command không phải Entity

Ví dụ:

```python
CreateStory(
    title="Đấu Phá Thương Khung"
)
```

Đây **không phải Story**.

Nó chỉ là:

> "Tôi muốn tạo một Story."

Trong khi:

```python
Story(...)
```

là Domain Entity/Aggregate.

Phân biệt:

```text
CreateStory
    = intention

Story
    = domain state
```

---

# 3. Command thường là immutable DTO

Python:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class CreateStoryCommand:

    title: str
    source_id: str
```

Sử dụng:

```python
command = CreateStoryCommand(
    title="Đấu Phá Thương Khung",
    source_id="truyen-abc",
)
```

`frozen=True` phù hợp vì Command là một **message**.

Sau khi tạo:

```python
command.title = "abc"
```

sẽ không được phép.

---

# 4. Command nên chứa gì?

Command chứa **dữ liệu cần thiết để thực hiện một hành động**.

Ví dụ:

```python
@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    number: int
    title: str
    content: str
```

Không nên nhét:

```python
story: Story
repository: StoryRepository
database_connection: sqlite3.Connection
```

Command không nên chứa infrastructure dependency.

---

# 5. Command không nên chứa business logic

Sai:

```python
@dataclass
class AddChapterCommand:

    story_id: str
    number: int

    def execute(self):
        ...
```

Command nên là:

```text
data/message
```

Còn logic thuộc:

```text
Use Case
Domain
Aggregate
```

---

# 6. Command Handler là gì?

Command Handler nhận Command và thực hiện nó.

Ví dụ:

```python
class CreateStoryHandler:

    def handle(
        self,
        command: CreateStoryCommand,
    ):
        ...
```

Flow:

```text
CreateStoryCommand
        ↓
CreateStoryHandler
        ↓
Story
```

Tuy nhiên trong kiến trúc DDD chúng ta đang học, **Use Case/Application Service** thường chính là nơi đóng vai trò Command Handler.

Do đó có thể viết:

```python
class CreateStoryUseCase:

    def execute(
        self,
        command: CreateStoryCommand,
    ):
        ...
```

---

# 7. Command vs Use Case

Đây là điểm cực kỳ quan trọng.

```text
Command
    = WHAT

Use Case
    = HOW
```

Ví dụ:

```text
AddChapterCommand
```

nói:

> Tôi muốn thêm chapter.

Còn:

```text
AddChapterUseCase
```

biết:

```text
1. Load Story
2. Create Chapter
3. story.add_chapter()
4. Save
5. Collect Event
6. Save Outbox
7. Commit
```

---

# 8. Command Model hoàn chỉnh

```text
CLI
 ↓
AddChapterCommand
 ↓
AddChapterUseCase
 ↓
StoryRepository
 ↓
Story Aggregate
 ↓
Domain Event
 ↓
OutboxRepository
 ↓
UnitOfWork
 ↓
COMMIT
```

Đây là flow chúng ta sẽ sử dụng xuyên suốt phần CQRS.

---

# 9. CreateStory

Bắt đầu với Command:

```python
@dataclass(frozen=True)
class CreateStoryCommand:

    title: str
    source_id: str
```

Use Case:

```python
class CreateStoryUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, command):

        story = Story.create(
            title=command.title,
            source_id=command.source_id,
        )

        self.uow.stories.add(story)

        for event in story.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()

        return story.id
```

---

# 10. Chú ý Boundary

CLI không nên:

```python
story = Story(...)
repository.save(story)
```

CLI chỉ nên:

```python
command = CreateStoryCommand(
    title=title,
    source_id=source_id,
)

use_case.execute(command)
```

Architecture:

```text
CLI
 ↓
Command
 ↓
Use Case
 ↓
Domain
```

CLI không cần biết Domain internals.

---

# 11. AddChapter

Command:

```python
@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    number: int
    title: str
    content: str
```

Use Case:

```python
class AddChapterUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, command):

        story = self.uow.stories.get(
            command.story_id
        )

        chapter = Chapter.create(
            number=command.number,
            title=command.title,
            content=command.content,
        )

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        for event in story.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()

        return chapter.id
```

---

# 12. Business Rule nằm ở đâu?

Ví dụ không cho:

```text
Chapter 10
```

xuất hiện hai lần.

Không nên:

```python
if repository.exists(...):
    raise ...
```

trong CLI.

Cũng không nên để Command chứa rule.

Business rule thuộc Domain:

```python
class Story:

    def add_chapter(self, chapter):

        if chapter.number in self._chapter_numbers:
            raise DuplicateChapterError()

        self._chapters.append(chapter)
```

---

# 13. Đây là nguyên tắc quan trọng

Command:

```text
WHAT
```

Application:

```text
ORCHESTRATION
```

Domain:

```text
BUSINESS RULE
```

Repository:

```text
PERSISTENCE
```

Infrastructure:

```text
TECHNICAL IMPLEMENTATION
```

---

# 14. StartCrawler

Command:

```python
@dataclass(frozen=True)
class StartCrawlerCommand:

    source_id: str
```

Use Case:

```python
class StartCrawlerUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, command):

        source = self.uow.sources.get(
            command.source_id
        )

        job = CrawlerJob.start(
            source_id=source.id
        )

        self.uow.jobs.add(job)

        for event in job.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()

        return job.id
```

---

# 15. PauseCrawler

```python
@dataclass(frozen=True)
class PauseCrawlerCommand:

    job_id: str
```

Use Case:

```python
class PauseCrawlerUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(self, command):

        job = self.uow.jobs.get(
            command.job_id
        )

        job.pause()

        self.uow.jobs.save(job)

        for event in job.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()
```

Domain:

```python
job.pause()
```

mới là nơi quyết định:

```text
Running → Paused
```

có hợp lệ hay không.

---

# 16. ResumeCrawler

Command:

```python
@dataclass(frozen=True)
class ResumeCrawlerCommand:

    job_id: str
```

Flow:

```text
ResumeCrawlerCommand
        ↓
ResumeCrawlerUseCase
        ↓
CrawlerJob
        ↓
job.resume()
        ↓
CrawlerResumed
        ↓
Outbox
        ↓
Commit
```

---

# 17. Command không phải HTTP Request

Ví dụ HTTP:

```text
POST /stories
```

không nhất thiết chính là Command.

HTTP là **transport**.

Command là **application message**.

Có thể:

```text
HTTP
 ↓
CreateStoryCommand
 ↓
Use Case
```

Nhưng cũng có:

```text
CLI
 ↓
CreateStoryCommand
```

hoặc:

```text
Worker
 ↓
CreateStoryCommand
```

Command giúp application không phụ thuộc transport.

---

# 18. CLI + Command

Ví dụ Typer:

```python
@app.command()
def create_story(
    title: str,
    source_id: str,
):

    command = CreateStoryCommand(
        title=title,
        source_id=source_id,
    )

    result = create_story.execute(
        command
    )

    print(result)
```

CLI chỉ làm:

```text
parse input
     ↓
create command
     ↓
call use case
     ↓
display result
```

---

# 19. Command Bus

Khi số lượng Command tăng:

```text
CreateStory
AddChapter
StartCrawler
PauseCrawler
ResumeCrawler
CompleteCrawler
...
```

ta có thể dùng:

```text
CommandBus
```

Architecture:

```text
Command
   ↓
CommandBus
   ↓
Handler
```

Ví dụ:

```python
class CommandBus:

    def __init__(self):
        self._handlers = {}

    def register(self, command_type, handler):
        self._handlers[command_type] = handler

    def dispatch(self, command):

        handler = self._handlers[
            type(command)
        ]

        return handler.execute(command)
```

---

# 20. Registration

```python
bus.register(
    CreateStoryCommand,
    create_story_use_case,
)

bus.register(
    AddChapterCommand,
    add_chapter_use_case,
)
```

Sau đó:

```python
bus.dispatch(
    CreateStoryCommand(...)
)
```

CommandBus tìm:

```text
CreateStoryCommand
        ↓
CreateStoryUseCase
```

---

# 21. Có nhất thiết phải dùng CommandBus?

**Không.**

Nếu application có:

```text
5 use cases
```

thì:

```python
create_story.execute(command)
```

thường đơn giản hơn:

```python
command_bus.dispatch(command)
```

CQRS không yêu cầu CommandBus.

CommandBus chỉ hữu ích khi cần:

* central dispatch;
* middleware;
* logging;
* authorization;
* metrics;
* transaction behavior;
* retry;
* tracing.

---

# 22. Command Middleware

CommandBus có thể trở thành pipeline:

```text
Command
   ↓
Logging Middleware
   ↓
Authorization Middleware
   ↓
Transaction Middleware
   ↓
Handler
```

Ví dụ:

```text
AddChapterCommand
      ↓
log
      ↓
check permission
      ↓
BEGIN
      ↓
handler
      ↓
COMMIT
```

Đây là kiến trúc nâng cao.

---

# 23. Command Result

Command thường không nên trả Domain Entity trực tiếp.

Ví dụ:

```python
@dataclass(frozen=True)
class CreateStoryResult:

    story_id: str
```

Use Case:

```python
return CreateStoryResult(
    story_id=str(story.id)
)
```

CLI:

```python
result = use_case.execute(command)

print(result.story_id)
```

---

# 24. Vì sao không trả Entity?

Nếu trả:

```python
return story
```

thì presentation layer bắt đầu phụ thuộc Domain Entity.

Trong một số application nhỏ, điều này không nghiêm trọng.

Nhưng với architecture lớn:

```text
Domain
   ↓
Application DTO
   ↓
Interface
```

thường sạch hơn.

---

# 25. Command Error

Ví dụ:

```python
class StoryNotFoundError(Exception):
    pass


class DuplicateChapterError(Exception):
    pass


class InvalidCrawlerStateError(Exception):
    pass
```

Use Case không nên:

```python
except Exception:
    print("Something went wrong")
```

CLI mới quyết định cách hiển thị.

---

# 26. Domain Error vs Application Error

Ví dụ:

```text
StoryNotFoundError
```

có thể thuộc Application:

```text
repository không tìm thấy Aggregate
```

Trong khi:

```text
DuplicateChapterError
```

rất rõ là Domain rule.

Ví dụ:

```python
story.add_chapter(chapter)
```

raise:

```python
DuplicateChapterError
```

Đó là business rule.

---

# 27. Command Model và Transaction

Một Command thường tương ứng với một application transaction:

```text
Command
   ↓
Use Case
   ↓
BEGIN
   ↓
Domain changes
   ↓
Outbox
   ↓
COMMIT
```

Ví dụ:

```text
AddChapterCommand
```

không nên:

```text
commit chapter
commit story
commit event
```

thành ba transaction độc lập.

Thường muốn:

```text
ONE COMMAND
     ↓
ONE UNIT OF WORK
     ↓
ONE TRANSACTION
```

---

# 28. Nhưng "một Command = một Transaction" không phải luật tuyệt đối

Có những workflow dài:

```text
StartCrawler
    ↓
Crawler chạy 30 phút
    ↓
Download
    ↓
Parse
    ↓
Save
```

Không nên giữ một DB transaction trong 30 phút.

Ta chia thành nhiều Command:

```text
StartCrawler
     ↓
CrawlerStarted

CompleteCrawler
     ↓
CrawlerCompleted
```

Mỗi operation có transaction riêng.

---

# 29. Command và Aggregate Boundary

Command không nên thao tác tùy tiện:

```python
chapter_repository.update(...)
story_repository.update(...)
crawler_repository.update(...)
```

nếu các thay đổi đó thực sự thuộc cùng một Aggregate.

Ví dụ:

```python
story.add_chapter(...)
```

thay vì:

```python
chapter_repository.add(...)
```

vì Aggregate Root phải bảo vệ invariant.

---

# 30. Một Command có thể sử dụng nhiều Repository

Có thể.

Ví dụ:

```text
StartCrawler
```

có thể cần:

```text
CrawlerSourceRepository
CrawlerJobRepository
OutboxRepository
```

Use Case orchestration:

```python
source = sources.get(...)

job = CrawlerJob.start(source.id)

jobs.add(job)

events = job.collect_events()

for event in events:
    outbox.add(event)
```

Đó chính là Application Layer.

---

# 31. Command Model không phải Domain Model

Đây là điểm cần khắc sâu:

```text
Command Model
    ≠
Domain Model
```

Ví dụ:

```text
AddChapterCommand
```

có:

```text
story_id
number
title
content
```

Trong Domain:

```text
Chapter
 ├── ChapterId
 ├── ChapterNumber
 ├── Title
 └── Content
```

Command là input.

Domain là business model.

---

# 32. Command Model vs CRUD Service

CRUD:

```python
story_service.create_story(...)
story_service.update_story(...)
story_service.delete_story(...)
```

DDD/CQRS:

```text
CreateStory
RenameStory
PublishStory
ArchiveStory
```

Sự khác biệt rất quan trọng.

CRUD mô tả:

> dữ liệu được CRUD thế nào.

DDD mô tả:

> **business intention là gì.**

---

# 33. Ví dụ

Không nên:

```text
UpdateCrawlerJob(status="paused")
```

Nếu business thực sự có hành động:

```text
PauseCrawler
```

thì dùng:

```text
PauseCrawlerCommand
```

Domain:

```python
job.pause()
```

Điều này diễn đạt business tốt hơn:

```text
UPDATE status
```

---

# 34. Command có thể đại diện cho Business Intent

So sánh:

```text
UpdateStory(status="published")
```

với:

```text
PublishStory
```

Cái thứ hai tốt hơn nếu:

```text
PublishStory
```

có business rule:

```text
Draft → Published
```

và:

```text
Published → Draft
```

không hợp lệ.

---

# 35. Command Naming

Nên dùng **imperative verb**:

```text
CreateStory
AddChapter
PublishStory
StartCrawler
PauseCrawler
ResumeCrawler
CompleteCrawler
```

Tránh:

```text
StoryCreation
ChapterData
CrawlerStatusUpdate
```

Tên Command nên thể hiện:

> **Action / Intent**

---

# 36. Command Model của hệ thống đọc truyện

Ta có thể thiết kế:

```text
commands/

├── story/
│   ├── create_story.py
│   ├── rename_story.py
│   └── publish_story.py
│
├── chapter/
│   ├── add_chapter.py
│   └── update_chapter.py
│
├── crawler/
│   ├── start_crawler.py
│   ├── pause_crawler.py
│   ├── resume_crawler.py
│   └── complete_crawler.py
│
└── reading/
    └── update_reading_progress.py
```

---

# 37. Một Command Module hoàn chỉnh

Ví dụ:

```python
# application/commands/add_chapter.py

from dataclasses import dataclass


@dataclass(frozen=True)
class AddChapterCommand:

    story_id: str
    number: int
    title: str
    content: str


@dataclass(frozen=True)
class AddChapterResult:

    chapter_id: str
```

Use Case:

```python
class AddChapterUseCase:

    def __init__(self, uow):
        self.uow = uow

    def execute(
        self,
        command: AddChapterCommand,
    ) -> AddChapterResult:

        story = self.uow.stories.get(
            command.story_id
        )

        chapter = Chapter.create(
            number=command.number,
            title=command.title,
            content=command.content,
        )

        story.add_chapter(chapter)

        self.uow.stories.save(story)

        for event in story.collect_events():
            self.uow.outbox.add(event)

        self.uow.commit()

        return AddChapterResult(
            chapter_id=str(chapter.id)
        )
```

Đây đã khá gần production-style.

---

# 38. Toàn bộ kiến trúc

Sau Buổi 37, ta có:

```text
                        CLI
                         │
                         ▼
                  Command DTO
                         │
                         ▼
                 Command Handler
                  /   Use Case
                         │
                         ▼
                     Domain
                         │
                  ┌──────┴──────┐
                  ▼             ▼
              Aggregate     Domain Service
                  │
                  ▼
              Repository
                  │
                  ▼
              Unit of Work
                  │
             ┌────┴────┐
             ▼         ▼
          Write DB   Outbox
                       │
                     Worker
                       │
                       ▼
                  Domain Event
                       │
                       ▼
                  Read Model
```

Buổi 38 sẽ đi theo hướng ngược lại:

```text
Query
  ↓
Query Handler
  ↓
Read Model
  ↓
SQL
```

---

# 39. Bài tập Buổi 37

Hãy tự thiết kế 5 Command:

### 1. CreateStory

```text
CreateStoryCommand
    title
    source_id
```

### 2. AddChapter

```text
AddChapterCommand
    story_id
    number
    title
    content
```

### 3. StartCrawler

```text
StartCrawlerCommand
    source_id
```

### 4. PauseCrawler

```text
PauseCrawlerCommand
    job_id
```

### 5. ResumeCrawler

```text
ResumeCrawlerCommand
    job_id
```

Với mỗi Command, hãy viết flow:

```text
Command
 ↓
Use Case
 ↓
Aggregate
 ↓
Repository
 ↓
Domain Event
 ↓
Outbox
 ↓
Commit
```

---

# 40. Bài tập tư duy quan trọng

Phân loại các object sau:

```text
CreateStory
Story
CreateStoryUseCase
StoryRepository
StoryCreated
StoryListItem
GetStoryList
SQLiteStoryRepository
```

thành:

```text
Command
Domain
Application
Repository
Domain Event
Read Model
Query
Infrastructure
```

Nếu phân loại đúng, bạn đã nắm được **Command Model** khá chắc.

---

## Mental Model của Buổi 37

Chỉ cần nhớ chuỗi này:

```text
                 USER INTENT
                     │
                     ▼
                  COMMAND
                     │
                     ▼
                  USE CASE
                     │
              orchestration
                     │
                     ▼
                 AGGREGATE
                     │
              business rules
                     │
                     ▼
                REPOSITORY
                     │
                     ▼
                UNIT OF WORK
                     │
              ┌──────┴──────┐
              ▼             ▼
           DATABASE       OUTBOX
```

**Command không thực hiện business logic.**

**Use Case không chứa business rule.**

**Aggregate bảo vệ business invariant.**

**Repository lo persistence.**

**Unit of Work lo transaction.**

**Outbox đảm bảo Domain Event không bị mất sau commit.**

Đây chính là cách ghép **DDD + CQRS + Repository + Unit of Work + Outbox** thành một kiến trúc thống nhất.
