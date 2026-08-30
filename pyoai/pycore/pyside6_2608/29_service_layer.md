# Phần III — UI Architecture

# Buổi 29 — Service Layer

Ở các buổi trước, chúng ta đã đi qua:

```text
Buổi 25
UI ≠ Business Logic

Buổi 26
MVC

Buổi 27
MVVM

Buổi 28
Controller
```

Hôm nay chúng ta thêm một mảnh ghép cực kỳ quan trọng:

```text
                 Controller / ViewModel
                           │
                           ▼
                    ┌─────────────┐
                    │   Service   │
                    └──────┬──────┘
                           │
                           ▼
                        Domain
```

Mục tiêu của Buổi 29 là hiểu thật rõ:

* Service là gì?
* Tại sao cần Service?
* Service khác Controller thế nào?
* Service khác Domain Service thế nào?
* Application Service là gì?
* Khi nào Service trở thành **God Service**?
* Thiết kế `StoryService` cho project Story Reader.

---

# 1. Vấn đề: Business logic bắt đầu nằm trong Controller

Ví dụ:

```python
class StoryController:

    def create_story(self):
        title = self.view.get_title()

        if not title:
            self.view.show_error(
                "Title required"
            )
            return

        if len(title) > 200:
            self.view.show_error(
                "Title too long"
            )
            return

        if self.repository.exists(title):
            self.view.show_error(
                "Story already exists"
            )
            return

        story = Story(title)

        self.repository.save(story)

        self.view.refresh()
```

Controller đang làm:

```text
Controller
│
├── nhận input
├── validation
├── business logic
├── repository
├── persistence
└── UI
```

Đây là vấn đề.

---

# 2. Đưa Application Logic sang Service

Ta refactor:

```text
Controller
    │
    ▼
StoryService
    │
    ▼
Repository
```

Controller:

```python
class StoryController:

    def create_story(self):
        title = self.view.get_title()

        try:
            self.service.create_story(title)

        except ValueError as e:
            self.view.show_error(str(e))
            return

        self.view.clear_form()
        self.view.refresh()
```

Service:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository

    def create_story(self, title):
        story = Story(title)

        if self.repository.exists(title):
            raise ValueError(
                "Story already exists"
            )

        self.repository.save(story)

        return story
```

Bây giờ:

```text
Controller
    ↓
Service
    ↓
Domain
    ↓
Repository
```

rõ ràng hơn rất nhiều.

---

# 3. Service là gì?

Có thể hiểu đơn giản:

> **Service là nơi thực hiện một hoặc nhiều operation của application mà không thuộc về UI.**

Ví dụ:

```text
StoryService
```

có thể cung cấp:

```python
create_story()
update_story()
delete_story()
get_story()
list_stories()
```

Còn:

```text
CrawlerService
```

có:

```python
crawl_story()
crawl_chapter()
```

---

# 4. Controller vs Service

Đây là điểm quan trọng nhất của buổi hôm nay.

## Controller

Quan tâm:

> **User vừa làm gì?**

Ví dụ:

```text
User click Save
```

Controller:

```python
title = view.get_title()
service.create_story(title)
```

---

## Service

Quan tâm:

> **Ứng dụng cần làm gì?**

Ví dụ:

```python
def create_story(title):
    story = Story(title)

    if repository.exists(title):
        raise DuplicateStory()

    repository.save(story)
```

---

# 5. Mental Model

Hãy nhớ:

```text
View
 │
 │ "User click Save"
 ▼
Controller
 │
 │ "Create Story"
 ▼
Service
 │
 │ "Thực hiện use case"
 ▼
Domain
 │
 │ "Business rules"
 ▼
Repository
 │
 ▼
Database
```

Controller biết **user interaction**.

Service biết **application operation**.

Domain biết **business rules**.

Repository biết **persistence**.

---

# 6. Service không phải nơi chứa mọi logic

Đây là lỗi rất phổ biến.

Có người học Service Layer xong bắt đầu viết:

```python
class StoryService:

    def create(self):
        ...

    def validate(self):
        ...

    def parse_html(self):
        ...

    def crawl(self):
        ...

    def save_database(self):
        ...

    def download_image(self):
        ...

    def convert_epub(self):
        ...

    def send_notification(self):
        ...
```

Cuối cùng:

```text
StoryService
    ↓
God Service
```

Đây không phải kiến trúc tốt.

---

# 7. Application Service vs Domain Service

Đây là phần quan trọng nếu bạn đang học DDD.

Có hai khái niệm dễ nhầm:

```text
Application Service
Domain Service
```

Chúng không giống nhau.

---

# 8. Application Service

Application Service điều phối **use case**.

Ví dụ:

```python
class CreateStoryService:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, title):
        story = Story(title)

        self.repository.save(story)

        return story
```

Nó có thể:

```text
load entity
     ↓
gọi domain behavior
     ↓
save entity
```

Nó là orchestration.

---

# 9. Domain Service

Domain Service chứa **business logic không tự nhiên thuộc về một Entity hoặc Value Object**.

Ví dụ:

```text
Story
Chapter
Author
```

Giả sử rule:

> Một chapter không được trùng với chapter khác trong cùng story.

Logic này có thể liên quan đến:

```text
Story
Chapter
```

Nếu logic không hợp lý để đặt hoàn toàn vào một Entity, có thể tạo:

```python
class ChapterUniquenessService:

    def is_unique(
        self,
        story,
        chapter,
    ):
        ...
```

Đây là Domain Service.

---

# 10. So sánh

|                    | Application Service | Domain Service      |
| ------------------ | ------------------- | ------------------- |
| Tầng               | Application         | Domain              |
| Mục đích           | Điều phối use case  | Business rule       |
| Biết Repository    | Có thể              | Thường không        |
| Biết UI            | Không               | Không               |
| Business logic     | Điều phối           | Có                  |
| CRUD orchestration | Có                  | Không phải mục tiêu |
| PySide6            | Không               | Không               |

---

# 11. Một ví dụ rất rõ

Giả sử:

```text
User muốn publish Story
```

Application Service:

```python
class PublishStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, story_id):
        story = self.repository.get(story_id)

        story.publish()

        self.repository.save(story)
```

Domain:

```python
class Story:

    def publish(self):
        if not self.chapters:
            raise ValueError(
                "Cannot publish empty story"
            )

        self.status = "published"
```

Ở đây:

```text
PublishStory
```

điều phối use case.

Còn:

```text
Story.publish()
```

chứa business rule.

---

# 12. Service Layer không nên phụ thuộc PySide6

Sai:

```python
from PySide6.QtWidgets import QMessageBox


class StoryService:

    def create_story(self, title):
        if not title:
            QMessageBox.warning(
                None,
                "Error",
                "Title required",
            )
```

Service không nên biết:

```text
QMessageBox
QWidget
QLabel
QPushButton
```

Thay vào đó:

```python
class StoryService:

    def create_story(self, title):
        if not title:
            raise ValueError(
                "Title required"
            )
```

UI quyết định cách hiển thị lỗi.

---

# 13. Tại sao Service nên độc lập UI?

Vì sau này cùng một use case có thể được gọi từ:

```text
PySide6
   │
   ├── GUI
   │
   ├── CLI
   │
   └── Worker
```

Ví dụ:

```text
                 CreateStory
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       PySide6       CLI        Worker
```

Tất cả dùng cùng:

```python
service.create_story(...)
```

---

# 14. Service và CLI

Bạn từng học CLI architecture.

Ví dụ:

```text
CLI
 │
 ▼
CreateStoryUseCase
 │
 ▼
Repository
```

Không cần PySide6.

Trong GUI:

```text
PySide6
 │
 ▼
CreateStoryUseCase
 │
 ▼
Repository
```

Đây chính là lợi ích của việc tách Application Layer.

---

# 15. Service và Testing

Đây là một lợi ích lớn.

Ta có:

```python
class FakeRepository:

    def __init__(self):
        self.items = []

    def save(self, story):
        self.items.append(story)

    def exists(self, title):
        return any(
            s.title == title
            for s in self.items
        )
```

Test:

```python
def test_create_story():
    repository = FakeRepository()

    service = StoryService(
        repository
    )

    story = service.create_story(
        "Python"
    )

    assert story.title == "Python"
    assert len(repository.items) == 1
```

Không cần:

```text
QApplication
QMainWindow
QPushButton
```

---

# 16. Service và Dependency Injection

Service nên nhận dependency:

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository
```

Không nên:

```python
class StoryService:

    def __init__(self):
        self.repository = SQLiteStoryRepository(
            "stories.db"
        )
```

Tại sao?

Vì sau này:

```text
Production
    ↓
SQLiteRepository

Test
    ↓
FakeRepository

Development
    ↓
MemoryRepository
```

Cùng dùng:

```text
StoryService
```

Đây là bước chuẩn bị cho:

# Buổi 31 — Dependency Injection

---

# 17. Service Interface

Ta có thể định nghĩa abstraction:

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def save(self, story):
        ...

    @abstractmethod
    def get(self, story_id):
        ...

    @abstractmethod
    def delete(self, story_id):
        ...
```

Service:

```python
class StoryService:

    def __init__(
        self,
        repository: StoryRepository,
    ):
        self.repository = repository
```

Service không cần biết:

```text
SQLite
PostgreSQL
Memory
Remote API
```

---

# 18. Service có nên chứa CRUD không?

Có thể.

Ví dụ application đơn giản:

```python
class StoryService:

    def create(self, title):
        ...

    def get(self, story_id):
        ...

    def update(self, story):
        ...

    def delete(self, story_id):
        ...
```

Điều này hoàn toàn hợp lý nếu application nhỏ.

Nhưng với application lớn:

```text
CreateStory
DeleteStory
PublishStory
AddChapter
RemoveChapter
```

có thể tách thành **Use Case**.

---

# 19. Service vs Use Case

Đừng quá cứng nhắc.

Có hai cách phổ biến.

### Cách 1

```text
StoryService
 ├── create()
 ├── update()
 ├── delete()
 └── publish()
```

### Cách 2

```text
CreateStory
DeleteStory
UpdateStory
PublishStory
```

Cách 2 thường phù hợp với Clean Architecture hơn khi application lớn.

---

# 20. Một Use Case

Ví dụ:

```python
class CreateStory:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, title):
        story = Story(title)

        if self.repository.exists(title):
            raise ValueError(
                "Story already exists"
            )

        self.repository.save(story)

        return story
```

Controller:

```python
story = self.create_story.execute(title)
```

---

# 21. Service Layer trong project của chúng ta

Ta có thể bắt đầu đơn giản:

```text
application/
│
├── story_service.py
├── chapter_service.py
└── crawl_service.py
```

Ví dụ:

```python
class StoryService:
    ...
```

Sau này khi project lớn:

```text
application/
│
├── stories/
│   ├── create_story.py
│   ├── delete_story.py
│   ├── update_story.py
│   └── publish_story.py
│
├── chapters/
│   ├── add_chapter.py
│   └── delete_chapter.py
│
└── crawling/
    ├── start_crawl.py
    └── stop_crawl.py
```

Không cần làm phức tạp ngay từ đầu.

---

# 22. Service và Transaction

Service rất phù hợp để xác định **ranh giới transaction**.

Ví dụ:

```text
CreateStory
    │
    ├── INSERT story
    ├── INSERT metadata
    └── INSERT initial chapter
```

Ta muốn:

```text
Tất cả thành công
       ↓
COMMIT
```

hoặc:

```text
Một bước thất bại
       ↓
ROLLBACK
```

Service/Application layer là nơi thích hợp để điều phối use case.

Buổi 54 trong phần SQLite sau này chúng ta sẽ đi sâu vào transaction.

---

# 23. Service và nhiều Repository

Một use case có thể cần nhiều repository:

```python
class PublishStory:

    def __init__(
        self,
        story_repository,
        chapter_repository,
    ):
        self.story_repository = story_repository
        self.chapter_repository = chapter_repository
```

Sau đó:

```python
def execute(self, story_id):

    story = self.story_repository.get(
        story_id
    )

    chapters = self.chapter_repository.list_by_story(
        story_id
    )

    story.publish(chapters)

    self.story_repository.save(story)
```

Đây là **orchestration**.

---

# 24. Service và Domain

Một nguyên tắc rất quan trọng:

> **Service không nên thay thế Domain Model.**

Sai:

```python
class StoryService:

    def publish(self, story):
        if not story.chapters:
            raise ValueError(...)

        story.status = "published"
```

Nếu đây là invariant của Story, tốt hơn:

```python
class Story:

    def publish(self):
        if not self.chapters:
            raise ValueError(...)

        self.status = "published"
```

Service:

```python
class PublishStory:

    def execute(self, story_id):
        story = self.repository.get(story_id)

        story.publish()

        self.repository.save(story)
```

Đây là sự phân chia rất đẹp:

```text
Service
    = orchestration

Domain
    = business behavior
```

---

# 25. Service và Domain Service

Ví dụ Domain Service:

```python
class StoryRatingService:

    def calculate_rating(
        self,
        reviews,
    ):
        ...
```

Nếu calculation là business concept nhưng không thuộc riêng:

```text
Story
Review
User
```

thì Domain Service có thể phù hợp.

Application Service có thể gọi Domain Service:

```text
Application Service
        │
        ▼
Domain Service
        │
        ▼
Domain
```

---

# 26. Một nguyên tắc DDD

Domain Service:

> **Không phải nơi nhét những thứ "không biết bỏ đâu".**

Nếu logic thuộc về Entity:

```python
story.publish()
```

thì để trong Entity.

Chỉ khi business operation:

```text
liên quan nhiều domain objects
+
không tự nhiên thuộc một object
```

mới cân nhắc Domain Service.

---

# 27. Service và HTTP

Ví dụ Story Reader cần crawl.

Không nên:

```python
class StoryService:

    def crawl(self):
        requests.get(...)
        BeautifulSoup(...)
        ...
```

Nếu crawler là infrastructure/application component riêng:

```text
StoryService
    ↓
Crawler Interface
    ↓
Crawler Implementation
```

hoặc:

```text
CrawlStoryUseCase
    ↓
Crawler
```

Sau này chúng ta sẽ kết hợp với:

```text
httpx
selectolax
asyncio
```

mà bạn đang học.

---

# 28. Kiến trúc Story Reader

Đến đây ta có:

```text
                     PySide6
                        │
                        ▼
                 Controller /
                 ViewModel
                        │
                        ▼
              ┌─────────────────┐
              │     Service     │
              └────────┬────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
          Domain             Repository
                                 │
                                 ▼
                               SQLite
```

Đây là nền móng rất tốt.

---

# 29. Ví dụ hoàn chỉnh

## Domain

```python
class Story:

    def __init__(self, title):
        title = title.strip()

        if not title:
            raise ValueError(
                "Title is required"
            )

        if len(title) > 200:
            raise ValueError(
                "Title too long"
            )

        self.title = title
```

---

## Repository abstraction

```python
from abc import ABC, abstractmethod


class StoryRepository(ABC):

    @abstractmethod
    def exists(self, title):
        ...

    @abstractmethod
    def save(self, story):
        ...
```

---

## Service

```python
class StoryService:

    def __init__(self, repository):
        self.repository = repository

    def create_story(self, title):
        story = Story(title)

        if self.repository.exists(
            story.title
        ):
            raise ValueError(
                "Story already exists"
            )

        self.repository.save(story)

        return story
```

---

## Controller

```python
class StoryController:

    def __init__(
        self,
        view,
        service,
    ):
        self.view = view
        self.service = service

        self.view.save_clicked.connect(
            self.create_story
        )

    def create_story(self):
        title = self.view.get_title()

        try:
            self.service.create_story(
                title
            )

        except ValueError as e:
            self.view.show_error(str(e))
            return

        self.view.clear_form()
        self.view.show_success()
```

---

# 30. Nhìn toàn bộ luồng

```text
User
 │
 │ click Save
 ▼
QPushButton
 │
 │ Signal
 ▼
Controller
 │
 │ create_story(title)
 ▼
StoryService
 │
 │ Story(title)
 ▼
Domain
 │
 │ valid?
 ▼
Repository
 │
 ▼
SQLite
```

Khi thành công:

```text
SQLite
  ↓
Service
  ↓
Controller
  ↓
View
  ↓
User
```

---

# 31. Một nguyên tắc cực kỳ đáng nhớ

Hãy hỏi:

### Controller:

> "User muốn làm gì?"

### Service:

> "Use case này phải làm những bước nào?"

### Domain:

> "Điều gì được phép xảy ra?"

### Repository:

> "Lưu/lấy dữ liệu thế nào?"

### View:

> "Hiển thị kết quả thế nào?"

Nếu mỗi thành phần trả lời đúng câu hỏi của mình, architecture thường sẽ rất sạch.

---

# 32. Bài tập 1 — Phân loại

Cho:

```text
A. title = title.strip()

B. self.view.get_title()

C. repository.save(story)

D. story.publish()

E. QMessageBox.warning(...)

F. repository.get(story_id)

G. self.service.create_story(title)
```

Hãy phân loại:

```text
View
Controller
Service
Domain
Repository
```

---

# 33. Bài tập 2 — Refactor

Code hiện tại:

```python
class StoryController:

    def save(self):
        title = self.view.title_input.text()

        if not title:
            return

        conn = sqlite3.connect("story.db")

        cursor = conn.execute(
            "SELECT id FROM stories WHERE title=?",
            (title,),
        )

        if cursor.fetchone():
            return

        conn.execute(
            "INSERT INTO stories(title)"
            " VALUES(?)",
            (title,),
        )

        conn.commit()

        self.view.refresh()
```

Hãy refactor thành:

```text
StoryController
       ↓
StoryService
       ↓
StoryRepository
       ↓
SQLite
```

và:

```text
Story
```

chứa business rule.

---

# 34. Bài tập 3 — Application Service

Thiết kế:

```python
class PublishStory:
    ...
```

Use case:

```text
1. Load Story
2. Kiểm tra Story tồn tại
3. Publish Story
4. Save Story
5. Trả kết quả
```

Câu hỏi:

> Bước nào thuộc Service?

> Bước nào thuộc Domain?

---

# 35. Bài tập 4 — God Service

Cho:

```python
class StoryService:

    def create_story(self):
        ...

    def delete_story(self):
        ...

    def crawl_story(self):
        ...

    def parse_html(self):
        ...

    def download_images(self):
        ...

    def convert_to_markdown(self):
        ...

    def convert_to_epub(self):
        ...

    def backup_database(self):
        ...

    def send_notification(self):
        ...
```

Hãy tìm các responsibility khác nhau và đề xuất:

```text
StoryService
CrawlerService
Parser
DownloadService
MarkdownExporter
EpubExporter
BackupService
NotificationService
```

---

# 36. Bài tập 5 — Architecture Challenge

Thiết kế use case:

> **"Download một chapter."**

Ứng dụng cần:

```text
1. Tìm Chapter
2. Kiểm tra Chapter tồn tại
3. Download HTML
4. Parse HTML
5. Lưu nội dung
6. Cập nhật trạng thái
```

Hãy suy nghĩ kiến trúc:

```text
Controller
    ↓
DownloadChapter
    ↓
ChapterRepository
    ↓
Crawler
    ↓
Parser
    ↓
ChapterRepository
```

Câu hỏi khó:

> `Crawler` có phải Service không?

> `Parser` có phải Domain Service không?

> `DownloadChapter` nên nằm ở Application hay Domain?

Đây là bài tập rất tốt để kết nối **PySide6 + Clean Architecture + DDD + crawler architecture**.

---

# 37. Tổng kết Buổi 29

Ba tầng quan trọng:

```text
Controller
    ↓
Service
    ↓
Domain
```

Controller:

```text
User interaction
```

Service:

```text
Application orchestration
```

Domain:

```text
Business rules
```

Repository:

```text
Persistence
```

View:

```text
Presentation
```

Mental Model:

```text
┌──────────────────┐
│       View       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Controller / VM  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Application      │
│ Service / UseCase│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│      Domain      │
│ Entity / Rules   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Repository    │
└────────┬─────────┘
         │
         ▼
       SQLite
```

### Một câu cần nhớ

> **Controller điều phối UI, Service điều phối use case, Domain quyết định business rule, Repository xử lý persistence.**

Và trong buổi tiếp theo, **Buổi 30 — Repository Pattern**, chúng ta sẽ tách hẳn:

```text
Service
   ↓
Repository Interface
   ↓
SQLite Repository
```

Sau đó bạn sẽ thấy tại sao `StoryService` **không nên biết SQL**, tại sao Repository không nên trở thành "God Repository", và cách thiết kế Repository để sau này có thể thay **SQLite bằng PostgreSQL hoặc Fake Repository để test** mà không phải sửa Application Layer.
