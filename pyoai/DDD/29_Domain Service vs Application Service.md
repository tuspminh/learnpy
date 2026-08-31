# DDD Deep Dive — Buổi 29

# Domain Service vs Application Service

Buổi 29 là buổi **phân biệt trách nhiệm**. Nếu nắm chắc bài này, khi thiết kế project DDD bạn sẽ ít rơi vào các lỗi như `GodService`, `Anemic Domain Model`, business logic nằm trong Repository hoặc SQL nằm trong Domain.

Ta sẽ so sánh trực tiếp 5 thành phần:

```text
Entity
Domain Service
Application Service
Repository
Infrastructure Service
```

---

# 1. Bức tranh tổng thể

Hãy bắt đầu bằng flow:

```text
CLI / PySide6 / API
        │
        ▼
Application Service
        │
        ├──────────────┐
        ▼              ▼
   Repository     Domain Service
        │              │
        │              ▼
        │           Entity
        │              │
        └──────────────┤
                       ▼
                  Unit of Work
                       │
                       ▼
                    SQLite
```

Nhưng sơ đồ này **không có nghĩa Application Service lúc nào cũng phải gọi Domain Service**.

Có Use Case chỉ cần:

```text
Application Service
        ↓
Aggregate
        ↓
Repository
```

---

# 2. Entity

Entity là object có:

```text
Identity
+
State
+
Behavior
+
Lifecycle
```

Ví dụ:

```python
class Story:
    def publish(self):
        ...
```

`Story` có identity:

```text
StoryId
```

Hai Story có title giống nhau vẫn có thể là hai Entity khác nhau.

```text
Story(id=1, title="ABC")
Story(id=2, title="ABC")
```

→ khác Entity.

---

# 3. Entity chịu trách nhiệm gì?

Entity chịu trách nhiệm bảo vệ **business behavior/invariant thuộc về chính nó**.

Ví dụ:

```python
class Story:

    def publish(self):

        if self.status == StoryStatus.PUBLISHED:
            raise StoryAlreadyPublished()

        self.status = StoryStatus.PUBLISHED
```

Đây là:

```text
Story
 ↓
publish()
```

Logic rất tự nhiên thuộc về `Story`.

---

# 4. Đừng lấy Entity làm data container

Không tốt:

```python
class Story:
    id: str
    title: str
    status: str
```

rồi toàn bộ behavior nằm ở:

```python
class StoryService:
    ...
```

Ví dụ:

```python
story.status = "published"
```

Thay vào đó:

```python
story.publish()
```

Domain Model trở nên có behavior.

---

# 5. Domain Service

Domain Service xuất hiện khi:

> **Business logic không tự nhiên thuộc về một Entity/Value Object duy nhất.**

Ví dụ:

```text
Story
User
CrawlerSource
```

Business rule:

> User có thể publish Story hay không dựa trên quyền của User và trạng thái Story.

Có thể có:

```python
class StoryPublicationPolicy:

    def can_publish(
        self,
        user: User,
        story: Story,
    ) -> bool:
        ...
```

Đây là Domain Service/Policy.

---

# 6. Domain Service tập trung vào business

Ví dụ:

```python
class ChapterNumberPolicy:

    def is_valid_next_number(
        self,
        current: ChapterNumber,
        previous: ChapterNumber,
    ) -> bool:

        return (
            current.value
            == previous.value + 1
        )
```

Nó trả lời:

> Business rule có hợp lệ không?

---

# 7. Domain Service không điều phối Use Case

Đây là điểm cần nhớ.

Không nên:

```python
class StoryPublishingService:

    def publish(self, story_id):

        story = repository.get(story_id)

        ...

        repository.save(story)

        connection.commit()
```

Service này đang làm:

```text
Load
 ↓
Business
 ↓
Save
 ↓
Commit
```

Đó là Application Service/UoW orchestration, không còn là Domain Service thuần túy.

---

# 8. Application Service

Application Service đại diện cho:

> **Một Use Case của hệ thống.**

Ví dụ:

```python
class PublishStoryUseCase:
    ...
```

Nó mô tả workflow:

```text
Load Story
    ↓
Check something
    ↓
Call Domain
    ↓
Save
    ↓
Commit
```

---

# 9. Application Service không sở hữu business rule

Ví dụ:

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

Nó không quyết định:

```text
"Story được publish khi nào?"
```

`Story` quyết định.

---

# 10. So sánh bằng một câu

Đây là mental model quan trọng:

### Entity

> **Tôi biết cách thay đổi chính mình một cách hợp lệ.**

```python
story.publish()
```

### Domain Service

> **Tôi biết một business rule liên quan đến nhiều domain concept.**

```python
policy.can_publish(user, story)
```

### Application Service

> **Tôi biết phải phối hợp các bước nào để hoàn thành một Use Case.**

```text
load
→ domain
→ save
→ commit
```

### Repository

> **Tôi biết cách lấy/lưu Aggregate.**

```python
story_repo.get(story_id)
```

### Infrastructure Service

> **Tôi biết cách giao tiếp với hệ thống bên ngoài.**

```text
HTTP
SMTP
Filesystem
SQLite
Redis
```

---

# 11. Bảng so sánh

| Thành phần             | Trách nhiệm chính           |   Business logic |              DB |         Transaction |
| ---------------------- | --------------------------- | ---------------: | --------------: | ------------------: |
| Entity                 | Domain behavior             |                ✅ |               ❌ |                   ❌ |
| Domain Service         | Cross-entity business logic |                ✅ |               ❌ |                   ❌ |
| Application Service    | Use Case orchestration      | Không nên sở hữu | Qua abstraction |           Điều phối |
| Repository             | Persistence abstraction     |                ❌ |    Interface: ❌ | Thường phối hợp UoW |
| Infrastructure Service | Technical integration       |                ❌ |          Có thể |              Có thể |

---

# 12. Một ví dụ xuyên suốt

Ta có:

```text
Story
Chapter
User
CrawlerSource
```

Business requirement:

> User muốn publish Story.

Điều kiện:

```text
1. Story tồn tại
2. User có permission
3. Story có đủ chapter
4. Story chưa published
```

Chúng ta phân chia thế nào?

---

# 13. Entity — Story

Rule:

> Story không được publish hai lần.

```python
class Story:

    def publish(self):

        if self.status == StoryStatus.PUBLISHED:
            raise StoryAlreadyPublished()

        self.status = StoryStatus.PUBLISHED
```

---

# 14. Domain Service — Permission

Rule:

> User phải có quyền publish Story.

```python
class StoryPublicationPolicy:

    def can_publish(
        self,
        user: User,
        story: Story,
    ) -> bool:

        return (
            user.can_publish_stories
            and story.status != StoryStatus.PUBLISHED
        )
```

---

# 15. Application Service — Publish

```python
class PublishStoryUseCase:

    def __init__(
        self,
        uow: UnitOfWork,
        policy: StoryPublicationPolicy,
    ):
        self.uow = uow
        self.policy = policy

    def execute(
        self,
        user_id: str,
        story_id: str,
    ):

        with self.uow:

            user = self.uow.users.get(
                user_id
            )

            story = self.uow.stories.get(
                story_id
            )

            if user is None:
                raise UserNotFound()

            if story is None:
                raise StoryNotFound()

            if not self.policy.can_publish(
                user,
                story,
            ):
                raise PermissionDenied()

            story.publish()

            self.uow.stories.save(story)

            self.uow.commit()
```

Đây là Application Service.

---

# 16. Repository

`StoryRepository`:

```python
class StoryRepository(ABC):

    @abstractmethod
    def get(
        self,
        story_id: StoryId,
    ) -> Story | None:
        ...

    @abstractmethod
    def add(
        self,
        story: Story,
    ) -> None:
        ...

    @abstractmethod
    def save(
        self,
        story: Story,
    ) -> None:
        ...
```

Repository abstraction không cần biết caller là:

```text
CLI
PySide6
API
Worker
```

---

# 17. Infrastructure

Implementation:

```python
class SQLiteStoryRepository:

    def __init__(self, connection):
        self.connection = connection
```

Ở đây mới có:

```python
connection.execute(...)
```

Domain không nhìn thấy SQL.

---

# 18. Hãy nhìn dependency

```text
Domain
   ↑
Application
   ↑
Interface
```

Infrastructure implement abstraction:

```text
Domain/Application
        ↑
Repository interface

Infrastructure
        │
        └── implements Repository
```

Không phải:

```text
Domain
   ↓
SQLite
```

---

# 19. Domain Service vs Application Service

Đây là câu hỏi bạn phải trả lời được ngay.

### Domain Service

```python
policy.can_publish(
    user,
    story,
)
```

Nó trả lời:

> Có được phép không?

### Application Service

```python
publish_story.execute(...)
```

Nó trả lời:

> Để publish Story, hệ thống cần làm những bước nào?

---

# 20. Domain Service thường không có `execute()`

Không phải quy tắc tuyệt đối, nhưng tên method có thể giúp thể hiện intent.

Domain:

```python
policy.can_publish(...)
```

hoặc:

```python
pricing.calculate(...)
```

Application:

```python
use_case.execute(...)
```

Nhìn API đã thấy khác nhau.

---

# 21. Ví dụ Domain Service tính giá

Giả sử:

```text
Book
Customer
DiscountPolicy
```

Rule:

> Giá cuối cùng phụ thuộc vào Book + Customer + DiscountPolicy.

Có thể:

```python
class PricingService:

    def calculate_price(
        self,
        book: Book,
        customer: Customer,
    ) -> Money:
        ...
```

Đây là business calculation.

Không nên:

```python
book_service.calculate_price(book_id)
```

rồi bên trong:

```text
load book
load customer
query database
save
commit
```

---

# 22. Application Service dùng Domain Service

```python
class CalculateBookPriceUseCase:

    def execute(
        self,
        book_id: str,
        customer_id: str,
    ) -> PriceResult:

        with self.uow:

            book = self.uow.books.get(book_id)
            customer = self.uow.customers.get(
                customer_id
            )

            price = self.pricing.calculate_price(
                book,
                customer,
            )

            return PriceResult(
                amount=price.amount
            )
```

Flow:

```text
Use Case
   │
   ├── Repository
   │
   └── Domain Service
```

---

# 23. Repository khác Application Service như thế nào?

Repository:

```python
story_repo.get(story_id)
```

chỉ quan tâm:

> "Làm sao lấy Story?"

Application:

```python
publish_story.execute(story_id)
```

quan tâm:

> "Làm sao hoàn thành Publish Story?"

---

# 24. Repository không phải DAO

DAO thường thiên về:

```text
database operation
```

Ví dụ:

```python
find_by_id()
insert_row()
update_row()
```

Repository trong DDD hướng đến:

```text
Domain collection / Aggregate persistence
```

Ví dụ:

```python
story_repository.get(story_id)
```

nó trả:

```python
Story
```

chứ không nhất thiết trả:

```python
dict
```

hoặc:

```python
sqlite3.Row
```

---

# 25. Infrastructure Service

Ví dụ crawler:

```python
class HttpCrawlerClient:

    def fetch(self, url: str) -> str:
        ...
```

Nó dùng:

```text
httpx
requests
aiohttp
```

Đây không phải Domain Service.

---

# 26. Email cũng vậy

```python
class EmailSender:

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
    ):
        ...
```

Nó là Infrastructure Service.

Domain không cần biết:

```text
SMTP
Gmail
SendGrid
```

---

# 27. File system

```python
class FileStorage:

    def save(
        self,
        path: str,
        content: bytes,
    ):
        ...
```

Infrastructure.

---

# 28. Redis

```python
class RedisCache:
    ...
```

Infrastructure.

---

# 29. SQLite

Có một điểm cần phân biệt:

```text
SQLite Repository
```

là persistence infrastructure.

```text
SQLite connection
```

là infrastructure detail.

Domain không biết cả hai.

---

# 30. Ví dụ toàn bộ hệ thống đọc truyện

```text
                    CLI
                     │
                     ▼
             AddChapterUseCase
                     │
          ┌──────────┼───────────┐
          ▼          ▼           ▼
       StoryRepo   Chapter     Policy
          │          │           │
          │          │           │
          └──────────┼───────────┘
                     ▼
                  Domain
                     │
                     ▼
                   UoW
                     │
                     ▼
                   SQLite
```

---

# 31. Khi nào Entity đủ?

Ví dụ:

> Chapter title không được rỗng.

Ta có:

```python
class ChapterTitle:

    def __init__(self, value: str):

        if not value.strip():
            raise InvalidChapterTitle()

        self.value = value
```

Không cần:

```python
ChapterValidationService
```

---

# 32. Khi nào cần Domain Service?

Ví dụ:

> Giá chapter phụ thuộc vào `Chapter` + `UserSubscription` + `Promotion`.

Không một object nào sở hữu tự nhiên toàn bộ logic.

Có thể:

```python
class ChapterPricingService:
    ...
```

---

# 33. Khi nào cần Application Service?

Khi có một Use Case:

```text
PurchaseChapter
```

workflow:

```text
Load User
   ↓
Load Chapter
   ↓
Calculate price
   ↓
Charge
   ↓
Update ReadingAccess
   ↓
Commit
```

Đây là Application Service.

---

# 34. Một điểm rất quan trọng: Infrastructure Service có thể được gọi từ Application

Ví dụ:

```text
StartCrawlerUseCase
        │
        ├── CrawlerJob
        │
        └── CrawlerClient
```

Application Service điều phối:

```python
content = crawler.fetch(url)
```

Nhưng interface nên được thiết kế để Application không phụ thuộc trực tiếp implementation:

```python
class CrawlerClient(Protocol):

    def fetch(self, url: str) -> str:
        ...
```

Infrastructure:

```python
class HttpxCrawlerClient:
    ...
```

---

# 35. Đây là Dependency Inversion

```text
Application
     ↓
CrawlerClient
     ↑
HttpxCrawlerClient
```

Không:

```text
Application
     ↓
httpx
```

---

# 36. Một lỗi cực kỳ phổ biến

Tạo:

```python
class StoryService:
```

rồi nhét tất cả:

```python
def create_story()
def add_chapter()
def publish_story()
def delete_story()
def crawl_story()
def update_progress()
```

Đây là:

```text
God Service
```

Thay bằng:

```text
CreateStoryUseCase
AddChapterUseCase
PublishStoryUseCase
DeleteStoryUseCase
StartCrawlerUseCase
UpdateReadingProgressUseCase
```

---

# 37. Một lỗi khác

Repository chứa business logic:

```python
class SQLiteStoryRepository:

    def save(self, story):

        if len(story.chapters) < 3:
            raise ...

        ...
```

❌

Repository không nên quyết định:

> Story có được publish hay không?

Domain quyết định.

Repository chỉ persistence.

---

# 38. Một lỗi khác

Application Service tự sửa state:

```python
story.status = "published"
```

❌ nếu đây là business state transition.

Nên:

```python
story.publish()
```

---

# 39. Một lỗi khác

Domain Service truy cập SQLite:

```python
class StoryPolicy:

    def can_publish(self, story_id):

        row = sqlite.execute(...)
```

❌

Domain Service không nên biết SQLite.

---

# 40. Một lỗi khác

Entity gửi HTTP:

```python
class Story:

    def publish(self):

        requests.post(...)
```

❌

Entity không biết network.

---

# 41. Quy tắc "Who owns the decision?"

Khi gặp một đoạn code, hãy hỏi:

> **Ai sở hữu quyết định này?**

Ví dụ:

```text
Story có được publish?
```

→ Story/Domain.

```text
User có permission publish?
```

→ Domain model/policy.

```text
Cần load Story ở đâu?
```

→ Application orchestration + Repository.

```text
SQL query viết thế nào?
```

→ Infrastructure.

```text
Khi nào commit?
```

→ Unit of Work/Application orchestration.

---

# 42. Decision Tree

```text
                 Logic này là gì?
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Business      Workflow     Technical
          │            │            │
          ▼            ▼            ▼
      Domain       Application   Infrastructure
          │
      ┌───┴────┐
      ▼        ▼
   Entity    Domain
             Service
```

Persistence:

```text
Repository
```

là abstraction dành cho việc lưu Aggregate.

---

# 43. Ví dụ thực tế với `AddChapter`

Requirement:

> Thêm chapter vào Story.

Application:

```python
class AddChapterUseCase:

    def execute(self, command):

        with self.uow:

            story = self.uow.stories.get(
                StoryId(command.story_id)
            )

            if story is None:
                raise StoryNotFound()

            chapter = Chapter.create(
                ...
            )

            story.add_chapter(chapter)

            self.uow.stories.save(story)

            self.uow.commit()
```

---

# 44. Ai làm gì?

```text
AddChapterUseCase
→ orchestration

StoryRepository
→ load/save Story

Chapter
→ chapter invariants

Story
→ add_chapter business behavior

ChapterNumber
→ chapter number invariant

UnitOfWork
→ transaction

SQLiteStoryRepository
→ SQL
```

Đây chính là DDD decomposition.

---

# 45. Một nguyên tắc cực hay

Nếu bạn thấy:

```python
if ...
```

đừng lập tức nghĩ:

> "Business logic!"

Hỏi tiếp:

> **Điều kiện này thuộc về ai?**

Ví dụ:

```python
if chapter.number <= 0:
```

→ `ChapterNumber`.

```python
if story.status == PUBLISHED:
```

→ có thể là `Story`.

```python
if user.can_publish and story.is_ready:
```

→ có thể là Domain Policy/Service.

```python
if row is None:
```

→ Repository/Application concern tùy ngữ cảnh.

---

# 46. Bảng nhận diện nhanh

| Bạn đang viết...          | Khả năng thuộc      |
| ------------------------- | ------------------- |
| `story.publish()`         | Entity              |
| `story.add_chapter()`     | Aggregate Root      |
| `ChapterNumber(...)`      | Value Object        |
| `pricing.calculate(...)`  | Domain Service      |
| `policy.can_publish(...)` | Domain Service      |
| `use_case.execute(...)`   | Application Service |
| `repo.get(...)`           | Repository          |
| `repo.save(...)`          | Repository          |
| `uow.commit()`            | Unit of Work        |
| `httpx.get(...)`          | Infrastructure      |
| `sqlite.execute(...)`     | Infrastructure      |
| `QMessageBox(...)`        | Interface           |

---

# 47. Architecture cuối cùng

Với project đọc truyện của bạn, tôi khuyên mental model:

```text
┌───────────────────────────────────────┐
│              Interface                │
│                                       │
│       CLI / PySide6 / API             │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│            Application                │
│                                       │
│ CreateStoryUseCase                    │
│ AddChapterUseCase                     │
│ PublishStoryUseCase                   │
│ StartCrawlerUseCase                   │
│ UpdateReadingProgressUseCase          │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│               Domain                 │
│                                       │
│ Entity                                │
│ Value Object                          │
│ Aggregate                             │
│ Domain Service                        │
│ Domain Event                          │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│          Ports / Abstractions         │
│                                       │
│ Repository                            │
│ UnitOfWork                            │
│ CrawlerClient                         │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│            Infrastructure             │
│                                       │
│ SQLite                                │
│ httpx                                 │
│ filesystem                            │
│ Redis                                 │
└───────────────────────────────────────┘
```

---

# 48. Công thức ghi nhớ

Bạn có thể nhớ bằng 5 câu:

```text
Entity
→ Tôi bảo vệ state của chính tôi.

Domain Service
→ Tôi thực hiện business logic không thuộc tự nhiên một Entity.

Application Service
→ Tôi điều phối một Use Case.

Repository
→ Tôi lưu và lấy Aggregate.

Infrastructure Service
→ Tôi giao tiếp với thế giới bên ngoài.
```

Và một câu cực kỳ quan trọng:

> **Application Service nói "làm theo trình tự nào"; Domain nói "được phép làm hay không".**

---

# 49. Bài tập Buổi 29

Cho requirement:

> Người dùng muốn bắt đầu một CrawlerJob cho một CrawlerSource.

Các rule:

```text
1. Source phải tồn tại.
2. Source phải active.
3. Source không được có Job đang chạy.
4. Tạo CrawlerJob.
5. Lưu Job.
6. Commit.
```

Hãy phân loại:

```text
Source tồn tại
Source active
Không có Job đang chạy
Tạo Job
Save Job
Commit
```

thành:

```text
Entity
Domain Service
Application Service
Repository
UnitOfWork
```

---

# 50. Bài tập nâng cao

Thiết kế:

```text
StartCrawlerUseCase
```

với flow:

```text
CLI
 ↓
StartCrawlerCommand
 ↓
StartCrawlerUseCase
 ↓
CrawlerSourceRepository
 ↓
CrawlerSource
 ↓
CrawlerJob.start()
 ↓
CrawlerJobRepository
 ↓
UnitOfWork
 ↓
SQLite
```

Sau đó thử trả lời:

> **Nếu kiểm tra "Source đang có Job chạy hay không" cần `CrawlerSource + CrawlerJob`, bạn sẽ đặt logic đó ở Entity, Domain Service hay Application Service? Vì sao?**

Đây là bài tập rất tốt để chuẩn bị cho **Buổi 30 — Use Case Architecture**, nơi chúng ta sẽ ghép tất cả lại thành kiến trúc hoàn chỉnh:

```text
CLI
 ↓
Command
 ↓
Use Case
 ↓
Aggregate / Domain Service
 ↓
Repository
 ↓
Unit of Work
 ↓
SQLite
```

và cuối cùng xây một project Python DDD có cấu trúc thực tế, thay vì chỉ học từng pattern riêng lẻ.
