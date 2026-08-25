# DDD Deep Dive — Buổi 27

# Application Service

Buổi 26 chúng ta học **Domain Service** — nơi chứa business logic không tự nhiên thuộc về một Entity/Value Object.

Hôm nay chúng ta chuyển sang một khái niệm khác:

> **Application Service không quyết định business rule. Nó điều phối một Use Case.**

Đây là ranh giới rất quan trọng trong DDD + Clean Architecture.

---

# 1. Application Service là gì?

Có thể hiểu đơn giản:

```text
Application Service
        =
Use Case Orchestrator
```

Nó chịu trách nhiệm:

```text
1. Nhận input
2. Load Aggregate
3. Gọi domain behavior
4. Gọi Domain Service nếu cần
5. Gọi Repository
6. Quản lý transaction
7. Trả kết quả
```

Ví dụ:

```text
AddChapterUseCase
```

không tự quyết định:

> Chapter có hợp lệ hay không?

Nó gọi:

```python
story.add_chapter(chapter)
```

để **Domain quyết định**.

---

# 2. Phân biệt Domain Service và Application Service

Đây là phần quan trọng nhất của buổi học.

## Domain Service

```text
"Business rule này đúng hay sai?"
```

## Application Service

```text
"Để thực hiện use case này, tôi cần gọi những gì?"
```

Ví dụ:

```text
Publish Story
```

Application Service:

```text
Load Story
    ↓
Check permission
    ↓
Domain logic
    ↓
Save Story
    ↓
Commit
```

Domain:

```text
Story.publish()
```

---

# 3. Ví dụ hệ thống đọc truyện

Chúng ta có các Use Case:

```text
CreateStory
AddChapter
PublishStory
StartCrawler
CompleteCrawlerJob
UpdateReadingProgress
```

Mỗi cái là một **application use case**.

```text
CLI / GUI / API
       ↓
Application Service
       ↓
Domain
       ↓
Repository
       ↓
Infrastructure
```

---

# 4. Application Service không phải Controller

Giả sử PySide6 có:

```python
def on_publish_clicked():
    ...
```

Đây là UI code.

Nó không nên chứa:

```python
story = ...
story.publish()
connection.execute(...)
connection.commit()
```

Thay vào đó:

```python
def on_publish_clicked():
    self.publish_story.execute(
        story_id
    )
```

UI chỉ gọi Use Case.

---

# 5. Application Service cũng không phải Repository

Repository:

```text
"Cho tôi Story"
```

Application Service:

```text
"Thực hiện nghiệp vụ Publish Story"
```

Ví dụ:

```python
story = story_repo.get(story_id)
```

Repository làm việc này.

Nhưng:

```python
story.publish()
```

là Domain.

Và:

```python
uow.commit()
```

là transaction orchestration của Application/UoW.

---

# 6. Một Use Case hoàn chỉnh

Ta xây:

```python
class PublishStoryUseCase:
    ...
```

Constructor:

```python
class PublishStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

Execute:

```python
def execute(
    self,
    story_id: StoryId,
) -> None:

    with self.uow:

        story = self.uow.stories.get(
            story_id
        )

        if story is None:
            raise StoryNotFound(
                story_id
            )

        story.publish()

        self.uow.stories.save(story)

        self.uow.commit()
```

---

# 7. Phân tích

## Load

```python
story = self.uow.stories.get(
    story_id
)
```

Application Service biết cần Story.

---

## Business behavior

```python
story.publish()
```

Application Service **không implement rule**.

Nó chỉ gọi Domain.

---

## Persistence

```python
self.uow.stories.save(story)
```

Application Service yêu cầu Repository lưu.

---

## Transaction

```python
self.uow.commit()
```

Application Service xác định khi nào Use Case hoàn thành transaction.

---

# 8. Application Service chính là "workflow"

Ví dụ:

```text
PublishStoryUseCase
```

workflow:

```text
BEGIN
 ↓
load Story
 ↓
validate existence
 ↓
Story.publish()
 ↓
save Story
 ↓
COMMIT
```

Nó không cần biết SQL cụ thể.

---

# 9. Application Service không nên chứa business rule

Sai:

```python
class PublishStoryUseCase:

    def execute(self, story_id):

        story = self.uow.stories.get(story_id)

        if story.status == "published":
            raise Exception()

        if len(story.chapters) < 3:
            raise Exception()

        story.status = "published"

        self.uow.commit()
```

Business rule đã bị kéo ra khỏi Domain.

---

# 10. Đúng

```python
class PublishStoryUseCase:

    def execute(self, story_id):

        with self.uow:

            story = self.uow.stories.get(
                story_id
            )

            if story is None:
                raise StoryNotFound()

            story.publish()

            self.uow.stories.save(story)

            self.uow.commit()
```

Domain:

```python
class Story:

    def publish(self):

        if len(self._chapters) < 3:
            raise StoryCannotBePublished()

        self._status = StoryStatus.PUBLISHED
```

---

# 11. Application Service có thể gọi Domain Service

Ví dụ:

```text
Publish Story
     │
     ├── Story
     │
     ├── Permission
     │
     └── PublicationPolicy
```

Application:

```python
class PublishStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
        publication_policy: StoryPublicationPolicy,
    ):
        self.uow = uow
        self.policy = publication_policy
```

Execute:

```python
def execute(self, story_id):

    with self.uow:

        story = self.uow.stories.get(
            story_id
        )

        if story is None:
            raise StoryNotFound()

        decision = self.policy.evaluate(
            story
        )

        if not decision.allowed:
            raise StoryCannotBePublished(
                decision.reason
            )

        story.publish()

        self.uow.stories.save(story)

        self.uow.commit()
```

Flow:

```text
Application Service
        │
        ├── Domain Service
        │
        └── Entity
```

---

# 12. Application Service có thể gọi nhiều Repository

Ví dụ:

```text
StartCrawler
```

cần:

```text
CrawlerSource
CrawlerJob
```

Application:

```python
class StartCrawlerUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

Execute:

```python
def execute(
    self,
    source_id: CrawlerSourceId,
):

    with self.uow:

        source = self.uow.sources.get(
            source_id
        )

        if source is None:
            raise SourceNotFound()

        job = CrawlerJob.start(
            source_id=source.id
        )

        self.uow.jobs.add(job)

        self.uow.commit()

        return job.id
```

---

# 13. Application Service có thể phối hợp nhiều Aggregate

Đây là một trong những vai trò quan trọng của Application Service.

Ví dụ:

```text
StartCrawler
```

có:

```text
CrawlerSource Aggregate
        +
CrawlerJob Aggregate
```

Không nên nhét logic điều phối hai Aggregate vào một Entity.

Application Service:

```text
load Source
    ↓
validate
    ↓
create Job
    ↓
save Job
    ↓
commit
```

---

# 14. Aggregate vẫn bảo vệ invariant

Điều này rất quan trọng.

Application Service:

```python
job = CrawlerJob.start(...)
```

Domain:

```python
class CrawlerJob:

    @classmethod
    def start(cls, source_id):
        ...
```

Nếu Job không thể bắt đầu trong trạng thái nào đó:

```python
raise InvalidCrawlerJobState()
```

Application Service không bypass rule.

---

# 15. Application Service không nên sửa private state

Không làm:

```python
story._status = StoryStatus.PUBLISHED
```

❌

Mà:

```python
story.publish()
```

Application Service chỉ orchestrate.

---

# 16. Command-style Application Service

Một pattern rất phổ biến:

```python
@dataclass(frozen=True)
class CreateStoryCommand:

    story_id: str
    title: str
    source_id: str
```

Use Case:

```python
class CreateStoryUseCase:

    def execute(
        self,
        command: CreateStoryCommand,
    ):
        ...
```

Flow:

```text
Command
   ↓
Use Case
   ↓
Domain
   ↓
Repository
```

Chúng ta sẽ đi sâu vào Command/Input DTO ở **Buổi 28**.

---

# 17. Application Service có nên trả Entity?

Thường không nên để UI/API trực tiếp phụ thuộc Entity Domain nếu không cần.

Ví dụ:

```python
return story
```

có thể được, nhưng thường tốt hơn:

```python
return StoryResult(...)
```

hoặc DTO.

Ví dụ:

```python
@dataclass(frozen=True)
class StoryResult:

    id: str
    title: str
    status: str
```

Buổi 28 sẽ đi sâu phần này.

---

# 18. Application Service và transaction

Một Use Case thường tương ứng với:

```text
Application Operation
        =
Transaction Boundary
```

Ví dụ:

```python
def execute(...):

    with self.uow:
        ...
        self.uow.commit()
```

Không nên:

```python
repository.save()
repository.commit()

another_repository.save()
another_repository.commit()
```

vì như vậy bạn có thể tạo:

```text
Transaction 1 → thành công
Transaction 2 → thất bại
```

và hệ thống rơi vào trạng thái không nhất quán.

---

# 19. Application Service + Unit of Work

Mô hình:

```text
Use Case
   │
   ▼
 Unit of Work
   │
   ├── StoryRepository
   ├── ChapterRepository
   ├── JobRepository
   └── UserRepository
```

Một Use Case có thể phối hợp nhiều repository nhưng commit một lần.

---

# 20. Ví dụ CompleteCrawlerJob

Giả sử crawler hoàn thành một Job.

Business operation:

```text
Complete Crawler Job
```

Có thể cần:

```text
CrawlerJob
Story
Chapter
```

Application Service:

```python
class CompleteCrawlerJobUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

---

# 21. Execute

```python
def execute(
    self,
    job_id: CrawlerJobId,
):

    with self.uow:

        job = self.uow.jobs.get(
            job_id
        )

        if job is None:
            raise CrawlerJobNotFound()

        job.complete()

        self.uow.jobs.save(job)

        self.uow.commit()
```

Logic:

```text
job.complete()
```

thuộc Domain.

Logic:

```text
load
save
commit
```

thuộc Application.

---

# 22. Một ví dụ phức tạp hơn

Giả sử:

> Khi crawler hoàn thành một chapter, hệ thống phải cập nhật CrawlerJob và lưu Chapter.

Flow:

```text
CompleteCrawlerChapter
        │
        ├── Load CrawlerJob
        │
        ├── Load Story
        │
        ├── Create Chapter
        │
        ├── Story.add_chapter()
        │
        ├── Job.record_success()
        │
        ├── Save Story
        │
        ├── Save Job
        │
        └── Commit
```

Đây chính là **Application Service orchestration**.

---

# 23. Nhưng có một vấn đề

Bạn không nên để Application Service trở thành:

```text
God Service
```

Ví dụ:

```python
class StoryService:

    def create_story(...):
        ...

    def update_story(...):
        ...

    def publish_story(...):
        ...

    def crawl_story(...):
        ...

    def notify_story(...):
        ...

    def update_progress(...):
        ...
```

Đây là dấu hiệu xấu.

---

# 24. Tốt hơn: một Use Case một responsibility

```text
CreateStoryUseCase
PublishStoryUseCase
AddChapterUseCase
StartCrawlerUseCase
CompleteCrawlerJobUseCase
UpdateReadingProgressUseCase
```

Mỗi class:

```text
một application operation
```

Ví dụ:

```python
class AddChapterUseCase:
    ...

class PublishStoryUseCase:
    ...

class StartCrawlerUseCase:
    ...
```

---

# 25. Đây cũng liên quan SRP

SOLID:

> A class should have one reason to change.

Nếu:

```text
StoryService
```

thay đổi khi:

```text
create logic
publish logic
crawler logic
notification logic
```

thì nó có quá nhiều responsibility.

Tách thành Use Case:

```text
CreateStory
PublishStory
StartCrawler
```

sẽ rõ hơn.

---

# 26. Application Service và Dependency Injection

Ví dụ:

```python
class AddChapterUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow
```

Composition Root:

```python
uow = SQLiteUnitOfWork(connection)

add_chapter = AddChapterUseCase(
    uow=uow
)
```

Production:

```text
SQLiteUnitOfWork
```

Testing:

```text
FakeUnitOfWork
```

Use Case không cần biết implementation.

---

# 27. Testing Application Service

Đây là một lợi ích cực lớn.

Ta có Fake UoW:

```python
class FakeUnitOfWork:

    def __init__(self):
        self.stories = FakeStoryRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
```

Test:

```python
def test_publish_story():

    uow = FakeUnitOfWork()

    story = make_story()

    uow.stories.add(story)

    use_case = PublishStoryUseCase(
        uow
    )

    use_case.execute(
        story.id
    )

    assert story.status == (
        StoryStatus.PUBLISHED
    )

    assert uow.committed is True
```

Không cần SQLite.

---

# 28. Application Service không nên biết PySide6

Sai:

```python
class PublishStoryUseCase:

    def execute(self, story_id):

        QMessageBox.information(...)
```

❌

Application Layer không nên biết UI framework.

---

# 29. Không biết CLI

Sai:

```python
class PublishStoryUseCase:

    def execute(...):

        print("Publishing...")
```

❌

CLI là Interface Layer.

---

# 30. Không biết HTTP

Sai:

```python
class PublishStoryUseCase:

    def execute(...):

        requests.post(...)
```

Nếu đây là external technical operation, hãy dùng abstraction/Infrastructure Service phù hợp.

Application có thể **điều phối** một port, nhưng không nên tự gắn với HTTP library.

---

# 31. Kiến trúc đầy đủ

```text
                    ┌───────────┐
                    │   CLI     │
                    └─────┬─────┘
                          │
                    ┌─────▼─────┐
                    │  PySide6  │
                    └─────┬─────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Application      │
                │                  │
                │ CreateStory      │
                │ AddChapter       │
                │ PublishStory     │
                │ StartCrawler     │
                └────────┬─────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     Domain      │
                │                 │
                │ Entity          │
                │ Value Object    │
                │ Aggregate       │
                │ Domain Service  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Repository Port │
                │ UoW Port        │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Infrastructure  │
                │ SQLite          │
                └─────────────────┘
```

---

# 32. Một nguyên tắc cực kỳ quan trọng

Application Service:

> **Không phải nơi để business logic "bởi vì nó tiện".**

Nó là nơi để:

```text
ORCHESTRATE
```

Ví dụ:

```python
story = repo.get(...)
chapter = repo.get(...)

story.add_chapter(chapter)

repo.save(story)

uow.commit()
```

Đây là orchestration.

Nhưng:

```python
if chapter.number <= 0:
    ...
```

nên thuộc:

```text
ChapterNumber
```

hoặc Domain.

---

# 33. Một Use Case có thể rất mỏng

Đừng nghĩ:

> Application Service phải chứa nhiều code.

Một Use Case tốt đôi khi chỉ:

```python
class PublishStoryUseCase:

    def execute(self, story_id):

        with self.uow:

            story = self.uow.stories.get(
                story_id
            )

            story.publish()

            self.uow.stories.save(story)

            self.uow.commit()
```

Đó là hoàn toàn bình thường.

**Thin Application Layer không phải là vấn đề.**

Ngược lại, nếu business logic nằm đúng trong Domain thì Application Service càng mỏng càng tốt.

---

# 34. Application Service và Domain Service

Hãy nhìn ví dụ:

```text
PublishStoryUseCase
        │
        ├── StoryRepository.get()
        │
        ├── StoryPublicationPolicy.evaluate()
        │
        ├── story.publish()
        │
        ├── StoryRepository.save()
        │
        └── UoW.commit()
```

Phân chia:

```text
Use Case
→ workflow

PublicationPolicy
→ business decision

Story
→ state transition

Repository
→ persistence

UoW
→ transaction
```

Đây là kiến trúc rất sạch.

---

# 35. Application Service vs Domain Service

|               | Domain Service                  | Application Service    |
| ------------- | ------------------------------- | ---------------------- |
| Layer         | Domain                          | Application            |
| Mục đích      | Business logic                  | Use Case orchestration |
| Business rule | Có                              | Không nên sở hữu       |
| Repository    | Hạn chế/qua abstraction nếu cần | Thường xuyên           |
| Transaction   | Không                           | Có thể điều phối       |
| SQLite        | ❌                               | ❌                      |
| HTTP          | ❌                               | ❌                      |
| Stateless     | Thường có                       | Thường có              |

---

# 36. Ví dụ với hệ thống của bạn

Ta có:

```text
Story
Chapter
CrawlerJob
CrawlerSource
ReadingProgress
User
```

Application layer có thể:

```text
CreateStoryUseCase
AddChapterUseCase
PublishStoryUseCase

StartCrawlerJobUseCase
CompleteCrawlerJobUseCase
FailCrawlerJobUseCase

UpdateReadingProgressUseCase
GetReadingChapterUseCase
```

---

# 37. Crawler Use Case

Ví dụ:

```python
class StartCrawlerUseCase:

    def execute(
        self,
        source_id: CrawlerSourceId,
    ) -> CrawlerJobId:

        with self.uow:

            source = self.uow.sources.get(
                source_id
            )

            if source is None:
                raise SourceNotFound()

            job = CrawlerJob.start(
                source.id
            )

            self.uow.jobs.add(job)

            self.uow.commit()

            return job.id
```

Notice:

Use Case **không crawl web**.

Nó chỉ tạo Job.

Crawler worker sẽ xử lý Job sau.

---

# 38. Đây là một thiết kế rất tốt

Thay vì:

```text
StartCrawlerUseCase
    ↓
requests.get()
    ↓
BeautifulSoup
    ↓
parse
    ↓
SQLite
```

ta có:

```text
StartCrawlerUseCase
    ↓
Create CrawlerJob
    ↓
Commit
```

và:

```text
Crawler Worker
    ↓
Crawler Port
    ↓
Crawler Plugin
```

Hai trách nhiệm được tách ra.

---

# 39. Điều này cực kỳ hữu ích cho project đọc truyện

Kiến trúc:

```text
PySide6
   ↓
StartCrawlerUseCase
   ↓
CrawlerJob
   ↓
SQLite
```

Sau đó worker:

```text
Crawler Worker
   ↓
CrawlerJob
   ↓
Crawler Interface
   ↓
Website Plugin
```

GUI không cần biết crawler implementation.

Đây là sự kết hợp rất đẹp giữa:

```text
DDD
+
Clean Architecture
+
SOLID
+
Plugin Architecture
```

---

# 40. Bài tập Buổi 27

Hãy tự thiết kế 4 Use Case:

### 1. CreateStoryUseCase

```text
Input:
    title
    source_id

Output:
    StoryId
```

Flow:

```text
create Story
    ↓
repository.add()
    ↓
commit()
```

---

### 2. AddChapterUseCase

```text
Input:
    story_id
    chapter_number
    title
    content
```

Flow:

```text
load Story
    ↓
create Chapter
    ↓
story.add_chapter()
    ↓
save
    ↓
commit
```

---

### 3. StartCrawlerUseCase

```text
Input:
    source_id

Output:
    job_id
```

Flow:

```text
load Source
    ↓
CrawlerJob.start()
    ↓
save
    ↓
commit
```

---

### 4. CompleteCrawlerJobUseCase

```text
Input:
    job_id
```

Flow:

```text
load Job
    ↓
job.complete()
    ↓
save
    ↓
commit
```

---

# 41. Bài tập nâng cao

Viết:

```python
class AddChapterUseCase:
    ...
```

với:

```text
UnitOfWork
StoryRepository
ChapterRepository
```

Sau đó cố tình tạo một lỗi:

```python
raise RuntimeError()
```

sau:

```python
story.add_chapter(chapter)
```

nhưng trước:

```python
uow.commit()
```

Kiểm tra transaction rollback.

---

# 42. Checklist Buổi 27

Sau bài này bạn nên trả lời được:

* Application Service là gì?
* Use Case là gì?
* Application Service khác Domain Service thế nào?
* Application Service có chứa business rule không?
* Application Service có thể gọi nhiều Repository không?
* Application Service có thể phối hợp nhiều Aggregate không?
* Transaction boundary nằm ở đâu?
* Vì sao UI không nên chứa Use Case logic?
* Vì sao Application Service không nên biết SQLite?
* Vì sao một Use Case một class thường dễ maintain hơn God Service?

---

# 43. Mental Model cuối buổi

Hãy nhớ:

```text
               APPLICATION
                    │
             "What happens?"
                    │
                    ▼
                Use Case
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      Repository  Domain   Domain
                   Entity   Service
          │
          ▼
         UoW
          │
          ▼
       Database
```

Còn Domain trả lời:

```text
"What is allowed?"
```

Application trả lời:

```text
"What steps do I execute?"
```

Đây là sự khác biệt cốt lõi giữa **Domain Service** và **Application Service**.

**Buổi 28** sẽ đi sâu vào **Use Case Design**: `Input DTO`, `Output DTO`, `Command`, `Result`, error handling và cách thiết kế API của Use Case sao cho CLI, PySide6 và crawler worker đều có thể dùng chung.
