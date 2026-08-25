# DDD Deep Dive — Buổi 26

# Domain Service

Đây là bước rất quan trọng trong Tactical DDD, vì từ đây chúng ta bắt đầu trả lời một câu hỏi khó:

> **Nếu một business rule không thuộc về một Entity hoặc Aggregate cụ thể thì đặt nó ở đâu?**

Câu trả lời có thể là **Domain Service**.

---

# 1. Ôn lại những gì đã học

Đến Buổi 25, chúng ta có:

```text
Entity
   ↓
Aggregate
   ↓
Repository
   ↓
Unit of Work
```

Ví dụ:

```python
story.publish()
```

Business logic thuộc về `Story` thì để trong:

```python
class Story:
    def publish(self):
        ...
```

Nhưng không phải business rule nào cũng thuộc về một object duy nhất.

Ví dụ:

> Kiểm tra xem một Chapter có thể được xuất bản hay không dựa trên Story, Chapter và CrawlerSource.

Logic này có thể cần:

```text
Story
Chapter
CrawlerSource
```

Không object nào thực sự "sở hữu" toàn bộ logic.

Đây là lúc Domain Service xuất hiện.

---

# 2. Domain Service là gì?

Định nghĩa thực tế:

> **Domain Service là một stateless object chứa business logic thuộc Domain nhưng không tự nhiên thuộc về một Entity hoặc Value Object cụ thể.**

Có ba đặc điểm:

```text
Domain Service
    │
    ├── Business logic
    ├── Stateless
    └── Belongs to Domain
```

---

# 3. Ví dụ đơn giản

Giả sử hệ thống có:

```text
Story
User
```

Business rule:

> User chỉ được đọc Story nếu Story đã Published.

Có thể viết:

```python
class Story:

    def can_read(self, user):
        ...
```

Nhưng nếu rule thực tế là:

> User có quyền đọc Story dựa trên User + Story + Subscription + Permission.

Thì logic bắt đầu liên quan đến nhiều object.

```text
User
Story
Subscription
Permission
```

Đây có thể là Domain Service.

---

# 4. Domain Service không phải "service" chung chung

Đây là điểm cực kỳ quan trọng.

Không phải class nào tên:

```python
SomethingService
```

cũng là Domain Service.

Ví dụ:

```python
class EmailService:
    def send(...):
        ...
```

thường **không phải Domain Service**.

Nó là Infrastructure Service.

---

# 5. Domain Service phải chứa Domain Logic

Ví dụ:

```python
class ChapterPublishingService:

    def can_publish(
        self,
        story: Story,
        chapter: Chapter,
    ) -> bool:
        ...
```

Nếu logic này là business rule thực sự:

```text
Story
+
Chapter
→
quyết định business
```

thì đây có thể là Domain Service.

---

# 6. Stateless là gì?

Domain Service thường:

```text
không giữ state business
```

Ví dụ tốt:

```python
class ChapterPublishingService:

    def can_publish(
        self,
        story: Story,
        chapter: Chapter,
    ) -> bool:
        return (
            story.is_published
            and chapter.has_content
        )
```

Mỗi lần gọi:

```python
service.can_publish(...)
```

service không phụ thuộc vào kết quả lần gọi trước.

---

# 7. Không nên làm thế này

```python
class ChapterPublishingService:

    def __init__(self):
        self.current_story = None
        self.current_chapter = None
```

Sau đó:

```python
service.current_story = story
service.current_chapter = chapter
```

Đây là stateful service.

Không cần thiết trong đa số Domain Service.

---

# 8. Domain Service vs Entity

Đây là câu hỏi quan trọng nhất của Buổi 26:

> Khi nào logic nằm trong Entity, khi nào nằm trong Domain Service?

Hãy dùng nguyên tắc:

> **Nếu business rule tự nhiên thuộc về một Entity thì đặt trong Entity.**

Ví dụ:

```python
story.publish()
```

Rõ ràng:

```text
Story
 ↓
publish
```

→ Entity.

---

# 9. Ví dụ Entity tốt

```python
class Story:

    def publish(self):

        if self._status == StoryStatus.PUBLISHED:
            raise StoryAlreadyPublished()

        self._status = StoryStatus.PUBLISHED
```

Logic này chỉ cần:

```text
Story
```

Không cần Service.

---

# 10. Khi nào cần Domain Service?

Giả sử:

> Hai Story không được có cùng `SourceId` + `slug`.

Ta cần:

```text
Story A
Story B
```

để kiểm tra.

Logic không tự nhiên thuộc về:

```text
Story A
```

hay:

```text
Story B
```

Ta có thể có:

```python
class StoryUniquenessService:

    def is_unique(
        self,
        stories: list[Story],
    ) -> bool:
        ...
```

Nhưng đây chỉ là ví dụ minh họa. Trong hệ thống thực tế, nếu phải query repository để kiểm tra uniqueness, ta cần cẩn thận về boundary và concurrency; phần đó sẽ quay lại ở các bài sau.

---

# 11. Một ví dụ gần với hệ thống đọc truyện

Giả sử crawler tải chapter.

Có:

```text
CrawlerChapter
Chapter
Story
```

Business rule:

> Chapter chỉ được chấp nhận nếu chapter thuộc đúng Story và chapter number chưa tồn tại.

Ta có:

```python
class ChapterAcceptanceService:

    def accept(
        self,
        story: Story,
        chapter: Chapter,
    ) -> None:

        if chapter.story_id != story.id:
            raise ValueError(
                "Chapter belongs to another story"
            )

        if story.has_chapter(
            chapter.number
        ):
            raise ValueError(
                "Chapter already exists"
            )
```

---

# 12. Nhưng hãy cẩn thận

Có thể bạn nhìn thấy:

```python
story.has_chapter(...)
```

và nhận ra:

> "Nếu Story đã có khả năng kiểm tra chapter, có lẽ phần lớn logic nên nằm trong Story."

Đúng.

Ta không nên vội tạo Domain Service.

Đây là nguyên tắc:

> **Domain Service không phải nơi để nhét business logic khi Entity đã có thể xử lý nó.**

---

# 13. "Anemic Domain Model"

Một lỗi rất phổ biến:

```python
class Story:

    pass
```

Sau đó:

```python
class StoryService:

    def publish(self, story):
        ...

    def add_chapter(self, story, chapter):
        ...

    def rename(self, story, title):
        ...

    def archive(self, story):
        ...
```

Kết quả:

```text
Story
  ↓
data only

StoryService
  ↓
all business logic
```

Đây dễ trở thành **Anemic Domain Model**.

---

# 14. So sánh

### Anemic

```python
story.status = "published"
```

và:

```python
story_service.publish(story)
```

### Rich Domain Model

```python
story.publish()
```

DDD thường ưu tiên mô hình thứ hai khi behavior thực sự thuộc về Entity.

---

# 15. Domain Service không phải nơi chứa mọi logic

Sai:

```python
class StoryDomainService:

    def create_story(...):
        ...

    def publish_story(...):
        ...

    def add_chapter(...):
        ...

    def delete_story(...):
        ...

    def send_email(...):
        ...
```

Đây rất dễ trở thành:

```text
God Service
```

Giống hệt vấn đề God Object mà bạn đã học trong SOLID.

---

# 16. Domain Service nên nhỏ

Ví dụ:

```python
class ChapterNumberPolicy:

    def is_valid(
        self,
        previous: ChapterNumber,
        current: ChapterNumber,
    ) -> bool:
        return current.value == previous.value + 1
```

Service này có một business responsibility rõ ràng.

---

# 17. Domain Service vs Utility

Hai thứ này rất dễ nhầm.

## Utility

Ví dụ:

```python
def slugify(text: str) -> str:
    ...
```

Đây thường là:

```text
technical helper
```

Không nhất thiết có business meaning.

---

# 18. Domain Service

Ví dụ:

```python
class StoryPublishingPolicy:

    def can_publish(
        self,
        story: Story,
    ) -> bool:
        return (
            story.chapter_count >= 1
            and story.has_cover
        )
```

Điều này thể hiện:

```text
business rule
```

chứ không đơn thuần là technical transformation.

---

# 19. Một cách phân biệt rất hữu ích

Hỏi:

> Nếu đổi business rule, class/function này có thay đổi không?

Nếu:

```text
business rule thay đổi
        ↓
code thay đổi
```

thì nó có khả năng thuộc Domain.

Nếu:

```text
business không đổi
nhưng framework/library đổi
        ↓
code thay đổi
```

thì nhiều khả năng là Infrastructure/technical utility.

---

# 20. Ví dụ `slugify`

```python
def slugify(title: str) -> str:
    return ...
```

Nếu chỉ:

```text
lowercase
replace spaces
remove symbols
```

thì thường là utility.

Nhưng nếu business nói:

> Story URL identifier phải tuân theo quy tắc X, Y, Z.

thì việc tạo canonical slug có thể trở thành:

```text
Value Object
```

hoặc Domain logic.

Đừng đánh đồng:

```text
function
```

với:

```text
Domain Service
```

---

# 21. Domain Service vs Application Service

Đây là phần quan trọng nhất.

### Domain Service

```text
Business decision
```

### Application Service

```text
Business operation orchestration
```

Ví dụ:

```text
Domain Service
    ↓
"Chapter này có được publish không?"
```

Application Service:

```text
"Publish Chapter"
    ↓
load Story
    ↓
load Chapter
    ↓
gọi Domain Service
    ↓
save
    ↓
commit
```

---

# 22. Ví dụ

Domain Service:

```python
class ChapterPublishingPolicy:

    def can_publish(
        self,
        story: Story,
        chapter: Chapter,
    ) -> bool:

        return (
            story.status
            == StoryStatus.PUBLISHED
            and bool(chapter.content.strip())
        )
```

---

# 23. Application Service

```python
class PublishChapterUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
        policy: ChapterPublishingPolicy,
    ):
        self.uow = uow
        self.policy = policy
```

Sau đó:

```python
def execute(
    self,
    story_id: StoryId,
    chapter_id: ChapterId,
):

    with self.uow:

        story = self.uow.stories.get(
            story_id
        )

        chapter = self.uow.chapters.get(
            chapter_id
        )

        if story is None:
            raise StoryNotFound()

        if chapter is None:
            raise ChapterNotFound()

        if not self.policy.can_publish(
            story,
            chapter,
        ):
            raise ChapterCannotBePublished()

        chapter.publish()

        self.uow.chapters.save(chapter)

        self.uow.commit()
```

---

# 24. Nhìn vào flow

```text
                 Use Case
                    │
                    ▼
             Load Aggregate(s)
                    │
                    ▼
             Domain Service
                    │
                    ▼
             Business Decision
                    │
                    ▼
                Entity
                    │
                    ▼
                Repository
                    │
                    ▼
                  Commit
```

Đây là một architecture rất quan trọng.

---

# 25. Domain Service không quản lý transaction

Không viết:

```python
class ChapterPublishingService:

    def publish(...):
        ...
        connection.commit()
```

❌

Domain Service không biết:

```text
SQLite
connection
transaction
repository implementation
```

Nó chỉ biết Domain.

---

# 26. Domain Service không gọi Repository?

Đây là một câu hỏi tinh tế.

Trong DDD thực tế có những thiết kế cho phép Domain Service phụ thuộc vào domain-facing repository abstraction.

Ví dụ:

```python
class StoryUniquenessService:

    def __init__(
        self,
        stories: StoryRepository,
    ):
        self.stories = stories
```

Nhưng bạn nên dùng cách này thận trọng.

Nếu business rule có thể giải quyết từ Aggregate hiện tại:

```text
đừng gọi repository
```

Nếu Domain Service bắt đầu:

```text
load Story
load User
load Chapter
load Source
load Permission
```

thì rất dễ biến thành một Application Service trá hình.

---

# 27. Đây là dấu hiệu cảnh báo

Nếu Domain Service có:

```python
def execute(...):

    story = repository.get(...)
    user = repository.get(...)
    chapter = repository.get(...)
    progress = repository.get(...)
```

rồi:

```python
save(...)
save(...)
save(...)
commit()
```

thì gần như chắc chắn nó đang làm công việc của:

```text
Application Service
```

---

# 28. Domain Service nên nhận object

Tốt hơn:

```python
policy.can_publish(
    story,
    chapter,
)
```

thay vì:

```python
policy.can_publish(
    story_id,
    chapter_id,
)
```

Tại sao?

Vì:

```text
story_id
chapter_id
```

là application/persistence concern.

Còn:

```text
Story
Chapter
```

là Domain.

---

# 29. Domain Service có thể trả Value Object

Không nhất thiết chỉ:

```python
bool
```

Ví dụ:

```python
@dataclass(frozen=True)
class PublicationDecision:

    allowed: bool
    reason: str | None = None
```

Domain Service:

```python
class ChapterPublishingPolicy:

    def evaluate(
        self,
        story: Story,
        chapter: Chapter,
    ) -> PublicationDecision:

        if story.status != StoryStatus.PUBLISHED:
            return PublicationDecision(
                allowed=False,
                reason="Story is not published",
            )

        if not chapter.content.strip():
            return PublicationDecision(
                allowed=False,
                reason="Chapter has no content",
            )

        return PublicationDecision(
            allowed=True
        )
```

Đây là một thiết kế giàu domain hơn.

---

# 30. Domain Service có thể là Function không?

**Có.**

DDD không yêu cầu Domain Service bắt buộc phải là class.

Nếu logic:

```python
def calculate_x(...):
    ...
```

đủ rõ ràng và stateless, có thể dùng function.

Ví dụ:

```python
def calculate_next_chapter_number(
    chapters: list[Chapter],
) -> ChapterNumber:

    if not chapters:
        return ChapterNumber(1)

    maximum = max(
        chapter.number.value
        for chapter in chapters
    )

    return ChapterNumber(maximum + 1)
```

Nếu đây là business rule, function này hoàn toàn có thể thuộc Domain.

---

# 31. Khi nào dùng class?

Dùng class khi:

```text
business concept rõ ràng
```

hoặc:

```text
có nhiều related operations
```

Ví dụ:

```python
class ChapterOrderingPolicy:
    ...
```

thay vì:

```python
calculate_1()
calculate_2()
calculate_3()
```

Class làm concept rõ hơn.

---

# 32. Domain Service và SOLID

Bạn sẽ thấy mối liên hệ với SOLID.

### SRP

```text
Story
    → Story behavior

ChapterPublishingPolicy
    → Publishing policy
```

### OCP

Policy có thể thay thế:

```text
DefaultPublishingPolicy
PremiumPublishingPolicy
StrictPublishingPolicy
```

### DIP

Application phụ thuộc abstraction:

```text
ChapterPublishingPolicy
```

chứ không phụ thuộc implementation cụ thể.

---

# 33. Ví dụ hệ thống đọc truyện

Giả sử có rule:

> Một Story chỉ được publish khi có ít nhất 3 chapter và chapter cuối cùng phải có content.

Logic liên quan:

```text
Story
Chapter[]
```

Nếu `Story` aggregate sở hữu danh sách chapter:

```python
story.can_publish()
```

có thể là lựa chọn tốt.

Không cần Domain Service.

---

# 34. Nhưng nếu rule là

> Story chỉ được publish nếu Source đã được xác thực và User hiện tại có quyền publish.

Ta có:

```text
Story
Source
User
Permission
```

Lúc này có thể cân nhắc:

```python
class StoryPublicationPolicy:
    ...
```

---

# 35. Nhưng đừng đưa User vào Domain nếu không cần

Đây là một bẫy.

Có thể rule thực sự là:

```text
UserPermission
```

và:

```text
StoryPublicationPolicy
```

chỉ cần:

```python
permission: PublicationPermission
story: Story
```

Thay vì:

```python
user: User
```

Nguyên tắc:

> Domain Service nên nhận đúng những domain concept mà business rule cần.

---

# 36. Domain Service không phải "manager"

Tên như:

```text
StoryManager
CrawlerManager
ChapterManager
```

thường là dấu hiệu cần xem xét.

Một class:

```python
class StoryManager:
    ...
```

có thể đang làm:

```text
create
update
delete
publish
crawl
notify
save
```

Đây là God Object/God Service.

DDD giúp tách:

```text
Entity
Domain Service
Application Service
Infrastructure Service
```

---

# 37. So sánh toàn diện

| Thành phần             | Chứa gì?                |              Biết DB? |        Stateful? |
| ---------------------- | ----------------------- | --------------------: | ---------------: |
| Entity                 | Business behavior       |                     ❌ |  Có state domain |
| Value Object           | Value + invariant       |                     ❌ | Thường immutable |
| Domain Service         | Domain logic            |                     ❌ | Thường stateless |
| Application Service    | Orchestration           | Thông qua abstraction | Thường stateless |
| Repository             | Persistence abstraction |       Interface thì ❌ |           Có thể |
| Infrastructure Service | Technical operation     |                Có thể |              Tùy |
| Utility                | Generic helper          |                     ❌ | Thường stateless |

---

# 38. Một ví dụ đầy đủ

## Domain

```python
class StoryPublicationPolicy:

    def can_publish(
        self,
        story: Story,
        chapters: list[Chapter],
    ) -> bool:

        if not chapters:
            return False

        if len(chapters) < 3:
            return False

        return all(
            chapter.content.strip()
            for chapter in chapters
        )
```

---

# 39. Application

```python
class PublishStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
        policy: StoryPublicationPolicy,
    ):
        self.uow = uow
        self.policy = policy
```

Execute:

```python
def execute(
    self,
    story_id: StoryId,
):

    with self.uow:

        story = self.uow.stories.get(
            story_id
        )

        if story is None:
            raise StoryNotFound()

        chapters = (
            self.uow.stories
            .get_chapters(story.id)
        )

        if not self.policy.can_publish(
            story,
            chapters,
        ):
            raise StoryCannotBePublished()

        story.publish()

        self.uow.stories.save(story)

        self.uow.commit()
```

---

# 40. Nhưng có vấn đề

Nhìn code:

```python
self.uow.stories.get_chapters(...)
```

Ta đang thấy:

```text
StoryRepository
```

trở thành query service cho mọi thứ.

Đây là lúc phải quay lại Aggregate Design.

Nếu:

```text
Story
 └── Chapter[]
```

là một Aggregate thực sự, Repository có thể load toàn bộ Aggregate.

Nếu không:

```text
Chapter
```

có thể là Aggregate riêng.

Không có câu trả lời chung cho mọi hệ thống.

---

# 41. Đây chính là lý do DDD khó

DDD không phải:

```text
Entity
Repository
Service
```

rồi xong.

DDD là quá trình trả lời:

```text
Business invariant là gì?
        ↓
Object nào sở hữu invariant?
        ↓
Aggregate boundary ở đâu?
        ↓
Logic nào thuộc Entity?
        ↓
Logic nào cần Domain Service?
        ↓
Transaction boundary ở đâu?
```

---

# 42. Domain Service nên xuất hiện khi "conceptual ownership" không rõ

Ví dụ:

```text
A + B → business rule
```

mà:

```text
A không sở hữu tự nhiên
B không sở hữu tự nhiên
```

thì:

```text
Domain Service
```

là một ứng viên.

---

# 43. Nhưng ưu tiên Entity trước

Một quy tắc thực hành rất tốt:

```text
1. Có thể đặt vào Entity không?
       ↓ YES
    Đặt vào Entity

       ↓ NO

2. Có phải business logic không?
       ↓ NO
    Utility / Infrastructure

       ↓ YES

3. Logic liên quan nhiều Domain object?
       ↓ YES
    Domain Service
```

---

# 44. Decision Tree

```text
                 Business Logic?
                       │
                 ┌─────┴─────┐
                 │           │
                NO          YES
                 │           │
              Utility       │
                             ▼
                     Belongs naturally
                       to one Entity?
                             │
                       ┌─────┴─────┐
                       │           │
                      YES          NO
                       │           │
                    Entity         ▼
                              Domain Service
```

Đây là mental model rất hữu ích.

---

# 45. Bài tập 1

Cho:

```python
class Story:
    title
    status
```

Business rule:

> Story không được publish nếu title rỗng.

Hỏi:

> Entity hay Domain Service?

Đáp án:

```python
Story.publish()
```

**Entity**.

---

# 46. Bài tập 2

Business rule:

> Một Story chỉ được publish nếu có ít nhất 3 Chapter.

Nếu `Story` sở hữu Chapters và có đủ thông tin:

```python
story.publish()
```

có thể là **Entity**.

Không cần Service chỉ vì có nhiều object.

---

# 47. Bài tập 3

Business rule:

> Story chỉ được publish nếu Story + Source + PublicationPolicy đều thỏa mãn.

Đây là ứng viên tốt cho:

```python
StoryPublicationPolicy
```

hoặc:

```python
StoryPublishingService
```

---

# 48. Bài tập 4

Code:

```python
class EmailService:

    def send(
        self,
        email: str,
        message: str,
    ):
        smtp.send(...)
```

Đây là:

```text
Infrastructure Service
```

Không phải Domain Service.

---

# 49. Bài tập 5

Code:

```python
def slugify(text: str) -> str:
    ...
```

Nếu chỉ biến đổi chuỗi:

```text
Utility
```

Nếu business định nghĩa:

```text
StorySlug
```

với invariant riêng:

```text
Value Object
```

Đây là ví dụ rất hay về việc **context quyết định abstraction**.

---

# 50. Bài tập 6 — hệ thống đọc truyện

Cho các rule:

### A

```text
Chapter.number > 0
```

→ ?

### B

```text
Story.publish()
```

chỉ khi Story hợp lệ.

→ ?

### C

```text
Story + Source + Policy
```

quyết định có publish được không.

→ ?

### D

```text
SQLite connection
```

thực hiện query.

→ ?

### E

```text
Load Story
→ call domain logic
→ save
→ commit
```

→ ?

Đáp án:

```text
A → Value Object
B → Entity
C → Domain Service
D → Infrastructure
E → Application Service
```

---

# 51. Bài tập code

Hãy tự viết:

```python
class StoryPublicationPolicy:
    ...
```

với rule:

```text
Story phải có title
Story phải có ít nhất 3 chapters
Mọi chapter phải có content
```

API:

```python
decision = policy.evaluate(
    story,
    chapters,
)
```

Sau đó tạo:

```python
@dataclass(frozen=True)
class PublicationDecision:
    allowed: bool
    reason: str | None = None
```

---

# 52. Mục tiêu cuối Buổi 26

Bạn cần phân biệt được:

```text
Entity
   ↓
"tôi sở hữu behavior này"

Domain Service
   ↓
"business logic này cần nhiều domain object
 và không thuộc tự nhiên về một object"

Application Service
   ↓
"tôi điều phối use case"

Infrastructure Service
   ↓
"tôi giao tiếp với hệ thống bên ngoài"

Utility
   ↓
"tôi chỉ là technical helper"
```

---

# 53. Mental Model quan trọng nhất

Đừng bắt đầu bằng câu:

> "Tôi cần tạo một Service."

Hãy bắt đầu bằng:

> **"Business rule này thuộc về ai?"**

Sau đó:

```text
Một Entity?
    ↓
Entity

Nhiều Domain object?
    ↓
Domain Service

Điều phối workflow?
    ↓
Application Service

Database / HTTP / filesystem?
    ↓
Infrastructure Service
```

Đây chính là tư duy DDD mà bạn cần hình thành trước khi sang **Buổi 27 — Application Service**.
