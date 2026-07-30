# Clean Architecture Deep Dive

# Buổi 8: Domain Service - Nghiệp vụ không thuộc Entity thì để ở đâu?

Đây là buổi mà rất nhiều lập trình viên bắt đầu hiểu đúng về Domain-Driven Design.

Sau buổi trước, bạn có thể sẽ đặt câu hỏi:

> "Business Rule phải nằm trong Entity."

Điều này **đúng nhưng chưa đủ**.

Có những Business Rule:

  * Không thuộc Entity 
  * Không thuộc Repository 
  * Không thuộc UseCase 



Vậy nó thuộc đâu?

Đáp án là:

> **Domain Service**

Đây là khái niệm rất nhiều lập trình viên Python chưa từng sử dụng.

* * *

# Mục tiêu

Sau buổi này bạn sẽ hiểu:

  * Domain Service là gì 
  * Khi nào nên tạo Domain Service 
  * Phân biệt Entity, Value Object, Domain Service, Use Case 
  * Tránh God Entity 
  * Tránh God UseCase 
  * Ví dụ hoàn chỉnh với app cào truyện 



* * *

# Roadmap
    
    
    Entity
    
    ↓
    
    Value Object
    
    ↓
    
    Domain Service   ← Hôm nay
    
    ↓
    
    Aggregate
    
    ↓
    
    Domain Event

* * *

# Bài toán đầu tiên

Giả sử bạn có Entity.
    
    
    class Story:
    
        def publish(self):
            ...

Hoàn toàn đúng.

Nhưng bây giờ xuất hiện luật mới.

> Một Story chỉ được publish nếu:

  * Có ít nhất 5 chapter 
  * Có cover 
  * Có author 
  * Không bị khóa 
  * Không trùng slug trong toàn hệ thống 



Câu hỏi:

Có nên viết hết vào Entity?

* * *

# Cách 1
    
    
    class Story:
    
        def publish(self):
    
            if len(self.chapters) < 5:
                ...
    
            if self.cover is None:
                ...
    
            if repository.exists_slug(...):
                ...
    
            if cache.exists(...):
                ...

Sai.

Entity biết:

  * Repository 
  * Cache 



Vi phạm Clean Architecture.

* * *

# Cách 2

Nhét hết vào UseCase.
    
    
    class PublishStoryUseCase:
    
        def execute(self):
    
            if ...
    
            if ...
    
            if ...
    
            if ...
    
            if ...
    
            if ...

Sau vài năm.

UseCase:
    
    
    2500 dòng

Đây gọi là:

> God UseCase

* * *

# Vậy để đâu?

Domain Service.
    
    
    UseCase
    
    ↓
    
    Domain Service
    
    ↓
    
    Entity

* * *

# Domain Service là gì?

Định nghĩa.

> Domain Service là nơi chứa Business Rule không thuộc về một Entity cụ thể.

Đây là câu quan trọng nhất của buổi hôm nay.

* * *

# Khi nào dùng Domain Service?

Một nghiệp vụ nên là Domain Service nếu:

✅ Liên quan nhiều Entity

✅ Không có Identity

✅ Không phải Infrastructure

✅ Là Business Logic

* * *

Ví dụ.
    
    
    Story
    
    +
    
    Author
    
    ↓
    
    Kiểm tra có được publish không

Không thuộc Story.

Không thuộc Author.

Đó là Domain Service.

* * *

# Ví dụ đầu tiên
    
    
    class StoryPublishService:
    
        def can_publish(self, story):
    
            if len(story.chapters) < 5:
                return False
    
            if story.cover is None:
                return False
    
            return True

Entity không biết Service.

UseCase gọi Service.

* * *

# Luồng
    
    
    UI
    
    ↓
    
    UseCase
    
    ↓
    
    StoryPublishService
    
    ↓
    
    Story

Không có Repository trong Entity.

* * *

# Một ví dụ khác

Giả sử.
    
    
    Story
    
    +
    
    Category
    
    +
    
    Author

Muốn tính điểm đề xuất.
    
    
    Recommendation Score

Không thuộc Story.

Không thuộc Category.

Không thuộc Author.

Đó là Domain Service.

* * *

# App cào truyện

Ví dụ.

Muốn quyết định.
    
    
    Story
    
    ↓
    
    Đã tải đủ chưa?

Điều kiện.

  * đủ chapter 
  * cover 
  * metadata 
  * author 
  * category 



Đây không phải trách nhiệm của Story.

* * *

Service.
    
    
    class StoryCompletionService:
    
        def is_complete(self, story):
    
            ...

* * *

# Ví dụ thực tế

Story.
    
    
    story.publish()

Publish chỉ đổi trạng thái.
    
    
    self.status = PUBLISHED

Không kiểm tra.

Service.
    
    
    publish_service.can_publish(story)

Kiểm tra.

UseCase.
    
    
    if service.can_publish(story):
    
        story.publish()

Đẹp.

* * *

# Domain Service không lưu Database

Sai.
    
    
    class StoryPublishService:
    
        def publish(self):
    
            sqlite.save(...)

Sai.

Không biết Database.

* * *

# Domain Service không HTTP

Sai.
    
    
    requests.get(...)

Sai.

* * *

# Domain Service không GUI

Sai.
    
    
    QMessageBox(...)

Sai.

* * *

# Domain Service chỉ Business

Ví dụ.
    
    
    class SlugGenerator:
    
        def generate(title):
    
            ...

Business.

Không Infrastructure.

* * *

# Ví dụ hay

Giả sử.
    
    
    Story
    
    ↓
    
    Slug

Slug tạo từ.
    
    
    Đấu Phá Thương Khung

↓
    
    
    dau-pha-thuong-khung

Đây là Business.

Không phải Entity.

* * *
    
    
    class SlugService:
    
        def generate(title):
    
            ...

* * *

# Một ví dụ lớn

Giả sử.
    
    
    Story
    
    ↓
    
    Chapter
    
    ↓
    
    Download Progress

Luật.
    
    
    Nếu đã tải 100%
    
    ↓
    
    Completed

Service.
    
    
    class DownloadProgressService:
    
        def calculate(story):
    
            ...

Entity không nên tự tính.

* * *

# Domain Service và nhiều Entity

Ví dụ.
    
    
    Story
    
    Author
    
    Publisher

Muốn kiểm tra.
    
    
    Có thể ký hợp đồng không?

Đó là luật giữa nhiều Entity.

* * *

# So sánh

Entity.
    
    
    story.rename()

* * *

Value Object.
    
    
    StoryTitle(...)

* * *

Domain Service.
    
    
    publish_service.can_publish(story)

* * *

UseCase.
    
    
    execute()

* * *

# Trách nhiệm

Entity.
    
    
    Tự quản lý trạng thái.

* * *

Value Object.
    
    
    Biểu diễn giá trị.

* * *

Domain Service.
    
    
    Business giữa nhiều object.

* * *

UseCase.
    
    
    Điều phối.

* * *

# Sai lầm phổ biến

## Sai 1

Nhét tất cả vào Entity.
    
    
    Story
    
    ↓
    
    200 method

God Entity.

* * *

## Sai 2

Nhét tất cả vào UseCase.
    
    
    PublishStoryUseCase
    
    ↓
    
    5000 dòng

God UseCase.

* * *

## Sai 3

Domain Service biết SQLite.

Sai.

* * *

## Sai 4

Domain Service biết Requests.

Sai.

* * *

# Một ví dụ hoàn chỉnh

Entity.
    
    
    class Story:
    
        def publish(self):
    
            self.is_published = True

Service.
    
    
    class StoryPublishService:
    
        MIN_CHAPTER = 5
    
        def can_publish(self, story):
    
            if len(story.chapters) < self.MIN_CHAPTER:
    
                return False
    
            if story.cover is None:
    
                return False
    
            return True

UseCase.
    
    
    class PublishStoryUseCase:
    
        def execute(self, story):
    
            if not self.service.can_publish(story):
    
                raise Exception()
    
            story.publish()
    
            self.repo.save(story)

Đây là Clean Architecture.

* * *

# Nhưng có một vấn đề...

Ví dụ.
    
    
    class StoryPublishService:
    
        def can_publish(self, story):
    
            return not repository.exists_slug(...)

Repository xuất hiện.

Có sai không?

**Không hẳn.**

Đây là điểm mà nhiều tài liệu đơn giản hóa quá mức.

Trong DDD, Domain Service **có thể phụ thuộc vào abstraction của Domain** , ví dụ:
    
    
    from abc import ABC, abstractmethod
    
    class StoryRepository(ABC):
    
        @abstractmethod
        def exists_slug(self, slug) -> bool:
            ...

Khi đó:
    
    
    class StoryPublishService:
    
        def __init__(self, repository: StoryRepository):
            self._repository = repository
    
        def ensure_slug_available(self, slug):
            if self._repository.exists_slug(slug):
                raise ValueError("Slug already exists")

Service chỉ biết **interface** , không biết SQLite hay PostgreSQL.

* * *

# Domain Service hay UseCase?

Đây là câu hỏi quan trọng nhất.

Ví dụ:
    
    
    Người dùng nhấn Publish

Có hai phần:

### Điều phối (Application)

  * Đọc Story từ Repository 
  * Gọi Service 
  * Gọi `story.publish()`
  * Lưu Repository 
  * Gửi Event 



→ Đây là **UseCase**.

### Quy tắc nghiệp vụ

  * Ít nhất 5 chapter 
  * Có cover 
  * Slug phải duy nhất 
  * Không bị khóa 



→ Đây là **Domain Service**.

Một mẹo nhớ:

> **UseCase hỏi "làm gì tiếp theo?"**  
>  **Domain Service trả lời "điều đó có hợp lệ theo nghiệp vụ không?"**

* * *

# Áp dụng vào dự án cào truyện

Tôi đề xuất Domain Layer của bạn như sau:
    
    
    domain/
    
    ├── entities/
    │   ├── story.py
    │   ├── chapter.py
    │   └── author.py
    │
    ├── value_objects/
    │   ├── story_title.py
    │   ├── story_url.py
    │   └── chapter_number.py
    │
    ├── repositories/
    │   └── story_repository.py
    │
    └── services/
        ├── story_publish_service.py
        ├── story_completion_service.py
        ├── slug_service.py
        └── chapter_order_service.py

Ví dụ:

  * `StoryCompletionService`: kiểm tra truyện đã đầy đủ metadata và chapter chưa. 
  * `ChapterOrderService`: kiểm tra thứ tự chapter có liên tục hay bị thiếu. 
  * `SlugService`: chuẩn hóa và kiểm tra slug. 
  * `StoryPublishService`: quyết định truyện có đủ điều kiện publish không. 



Các service này đều là **business** , không chứa SQL, HTTP hay GUI.

* * *

# Checklist

Một class nên là Domain Service nếu:

  * Không có Identity. 
  * Không biểu diễn dữ liệu như Value Object. 
  * Không điều phối toàn bộ luồng như UseCase. 
  * Chứa quy tắc nghiệp vụ. 
  * Thường làm việc với nhiều Entity hoặc cần abstraction của Domain. 
  * Không phụ thuộc vào SQLite, Redis, Requests, PySide6... 



* * *

# Bài tập

## Bài 1

Thiết kế `StoryCompletionService` với các quy tắc:

  * Có tiêu đề hợp lệ. 
  * Có tác giả. 
  * Có ít nhất 10 chapter. 
  * Có ảnh bìa. 
  * Có mô tả. 



Service chỉ trả về `True/False`, không lưu database.

* * *

## Bài 2

Thiết kế `ChapterOrderService`:

Đầu vào:
    
    
    [
        Chapter(1),
        Chapter(2),
        Chapter(4),
    ]

Kết quả:

  * Phát hiện thiếu chapter 3. 
  * Trả về danh sách chapter bị thiếu. 



Service chỉ sử dụng Entity và Value Object.

* * *

## Bài 3

Xem lại dự án cào truyện của bạn và lập bảng:

Nghiệp vụ| Entity| Domain Service| UseCase  
---|---|---|---  
Đổi tên truyện| ✅| ❌| ❌  
Kiểm tra đủ điều kiện publish| ❌| ✅| ❌  
Tải HTML| ❌| ❌| ❌ (Infrastructure)  
Lưu SQLite| ❌| ❌| ❌ (Infrastructure Repository)  
Điều phối quy trình publish| ❌| ❌| ✅  
  
Nếu bạn phân loại được rõ ba cột này, bạn đã bắt đầu có tư duy thiết kế Domain theo đúng DDD và Clean Architecture.

* * *

### Chuẩn bị cho Buổi 9

Buổi tiếp theo chúng ta sẽ học **Aggregate và Aggregate Root** — một trong những khái niệm khó nhất của DDD nhưng cũng là chìa khóa để quản lý tính nhất quán (consistency) của dữ liệu. Sau buổi này, bạn sẽ biết:

  * Vì sao không nên cho mọi Entity truy cập lẫn nhau. 
  * Khi nào `Story` nên là Aggregate Root. 
  * Vì sao `Chapter` không nên được Repository quản lý trực tiếp trong nhiều trường hợp. 
  * Cách bảo vệ invariant của cả một cụm Entity thay vì từng Entity riêng lẻ. 



Đây là bước đưa Domain Model của bạn lên mức thiết kế dành cho các hệ thống lớn và phức tạp.

