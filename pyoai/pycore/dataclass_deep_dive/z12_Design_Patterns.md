# Dataclass Deep Dive - Buổi 12

# Dataclass Design Patterns & Best Practices (Master Class)

> Chúc mừng bạn đã đến buổi cuối của khóa **Dataclass Deep Dive**.

Đây không còn là buổi học về cú pháp nữa.

Mục tiêu của buổi này là giúp bạn biết:

> **Một lập trình viên Python chuyên nghiệp sẽ thiết kế hệ thống bằng dataclass như thế nào?**

Đặc biệt, mình sẽ lấy ví dụ xuyên suốt bằng **hệ thống crawler truyện** mà bạn đang xây dựng.

---

# Mục lục

1. Dataclass trong kiến trúc phần mềm
2. DTO Pattern
3. Value Object Pattern
4. Entity Pattern
5. Configuration Pattern
6. Event Pattern
7. Request / Response Pattern
8. Aggregate Pattern
9. Domain Model
10. Anti-patterns
11. Dataclass vs các lựa chọn khác
12. Kiến trúc hoàn chỉnh cho hệ thống crawler

---

# 1. Dataclass dùng để làm gì?

Một nguyên tắc rất quan trọng:

> **Dataclass sinh ra để biểu diễn dữ liệu (Data), không phải hành vi (Behavior).**

Nó phù hợp với các đối tượng mà mục đích chính là **mang dữ liệu**.

Ví dụ:

```text-x-trilium-auto
Novel
Chapter
Author
Category
Image
UserInfo
ApiResponse
Config
Task
Event
DTO
```

---

Không phù hợp:

```text-x-trilium-auto
CrawlerEngine
DownloadManager
Scheduler
HttpClient
Repository
NovelService
Parser
```

Những lớp này chứa nhiều logic nghiệp vụ và thường nên là class thông thường.

---

# 2. DTO Pattern (Data Transfer Object)

DTO dùng để truyền dữ liệu giữa các tầng.

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(slots=True)
class ChapterDTO:
    id: int
    title: str
    url: str
```

Luồng:

```text-x-trilium-auto
Database
      │
Repository
      │
 ChapterDTO
      │
Service
      │
GUI
```

DTO không chứa logic.

---

# 3. Value Object Pattern

Ví dụ:

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(
    frozen=True,
    slots=True
)
class NovelID:
    source: str
    novel_id: str
```

Đặc điểm:

- Immutable
- Hashable
- Có thể làm key của dict
- So sánh theo giá trị

```text-x-trilium-auto
NovelID("truyenfull", "100")
```

đại diện cho một định danh.

---

# 4. Entity Pattern

Entity có identity.

Ví dụ:

```text-x-trilium-auto
@dataclass(slots=True)
class Chapter:
    id: int
    title: str
    content: str
```

Hai object

```text-x-trilium-auto
Chapter(1, ...)
```

và

```text-x-trilium-auto
Chapter(1, ...)
```

có thể đại diện cùng một thực thể trong cơ sở dữ liệu.

Trong nhiều hệ thống DDD (Domain-Driven Design), entity còn có hành vi nghiệp vụ riêng, nhưng nếu hành vi ngày càng nhiều, nên cân nhắc chuyển sang class thường.

---

# 5. Configuration Pattern

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass(
    slots=True,
    kw_only=True
)
class CrawlConfig:

    timeout:int=30

    retry:int=3

    verify_ssl:bool=True

    proxy:str|None=None
```

Khởi tạo

```text-x-trilium-auto
config = CrawlConfig(
    timeout=60,
    retry=5
)
```

Đây là cách thiết kế rất phổ biến.

---

# 6. Event Pattern

Ví dụ

```text-x-trilium-auto
@dataclass(
    frozen=True,
    slots=True
)
class CrawlFinished:

    novel_id:int

    total:int
```

Event

↓

không sửa.

↓

chỉ phát đi.

---

# 7. Request Pattern

Ví dụ

```text-x-trilium-auto
@dataclass(
    slots=True
)
class DownloadRequest:

    url:str

    save_to:str
```

---

Response

```text-x-trilium-auto
@dataclass(
    slots=True
)
class DownloadResponse:

    status:int

    html:str
```

Đây là pattern rất phổ biến trong API và hệ thống phân tầng.

---

# 8. Aggregate Pattern

Ví dụ

```text-x-trilium-auto
from dataclasses import dataclass

@dataclass class Chapter:
    title: str
```

```text-x-trilium-auto
@dataclass class Novel:

    title:str

    chapters:list[Chapter]
```

Đây là Aggregate.

```text-x-trilium-auto
Novel

↓

Chapter

↓

Chapter

↓

Chapter
```

`Novel` là đối tượng bao gồm nhiều `Chapter`.

---

# 9. Domain Model

Ví dụ

```text-x-trilium-auto
Novel
```

gồm

```text-x-trilium-auto
Title

Author

Category

Chapter

Image

Status
```

Không phải

↓

mọi thứ đều nằm trong một class.

Nên tách.

```text-x-trilium-auto
Novel

↓

Author

↓

Category

↓

Chapter
```

Giúp mô hình rõ ràng và dễ bảo trì hơn.

---

# 10. Không nhồi logic vào Dataclass

Sai

```text-x-trilium-auto
@dataclass class Novel:

    title:str

    def crawl(self):
        ...

    def save_db(self):
        ...

    def download_image(self):
        ...

    def login(self):
        ...

    def upload(self):
        ...
```

Dataclass trở thành "God Object".

---

Đúng

```text-x-trilium-auto
Novel

↓

Data

----------------

NovelService

↓

Logic
```

Phân tách rõ:

- Data
- Behavior

---

# 11. Không biến dataclass thành ORM

Sai

```text-x-trilium-auto
@dataclass class User:

    id:int

    def save(self):
        ...

    def delete(self):
        ...

    def update(self):
        ...
```

Đúng

```text-x-trilium-auto
User

↓

UserRepository
```

Repository chịu trách nhiệm lưu trữ và truy xuất dữ liệu.

---

# 12. Không truyền dependency

Sai

```text-x-trilium-auto
@dataclass class Chapter:

    http:HttpClient

    db:SQLite

    logger:Logger
```

Đúng

```text-x-trilium-auto
@dataclass class Chapter:

    title:str

    content:str
```

Nếu cần dependency để khởi tạo, cân nhắc `InitVar` như đã học ở buổi 9.

---

# 13. Dùng slots

Nếu object được tạo nhiều

↓

```text-x-trilium-auto
@dataclass(
slots=True
)
```

Gần như luôn nên dùng.

Ví dụ

```text-x-trilium-auto
Chapter

Novel

Image

Author
```

---

# 14. Dùng Frozen

Nếu object không đổi

↓

```text-x-trilium-auto
@dataclass(
frozen=True
)
```

Ví dụ

```text-x-trilium-auto
NovelID

AuthorID

URL

ISBN

Email
```

---

# 15. Dùng kw_only

Nếu nhiều config

↓

```text-x-trilium-auto
CrawlerOptions(

timeout=60,

retry=3,

proxy=...
)
```

Dễ đọc hơn nhiều so với truyền theo vị trí.

---

# 16. Metadata

Ví dụ

```text-x-trilium-auto
price = field(
    metadata={
        "unit": "USD"
    }
)
```

Framework có thể đọc metadata để:

- validate,
- serialize,
- sinh biểu mẫu,
- tạo SQL.

---

# 17. Kiến trúc crawler

```text-x-trilium-auto
story_crawler/

│

├── models/

│     novel.py

│     chapter.py

│     author.py

│     category.py

│     image.py

│

├── dto/

│     novel_dto.py

│     chapter_dto.py

│

├── config/

│     crawl_config.py

│

├── events/

│     crawl_started.py

│     crawl_finished.py

│

├── requests/

│     download_request.py

│

├── responses/

│     download_response.py

│

├── repository/

│

├── services/

│

├── plugins/

│

└── parser/
```

Đây là cách nhiều dự án Python lớn tổ chức mã nguồn.

---

# 18. Dataclass vs Class

## Dataclass

```text-x-trilium-auto
@dataclass class User:
    id: int
    name: str
```

↓

Data.

---

Class

```text-x-trilium-auto
class UserService:

    def save(self):
        ...

    def login(self):
        ...
```

↓

Behavior.

---

# 19. Dataclass vs NamedTuple

```text-x-trilium-auto
from typing import NamedTuple

class Point(NamedTuple):
    x:int
    y:int
```

Ưu điểm:

- Immutable
- Nhẹ

Nhược:

- Khó mở rộng.
- Ít tùy biến hơn dataclass.

---

# 20. Dataclass vs TypedDict

```text-x-trilium-auto
class UserDict(TypedDict):

    id:int

    name:str
```

TypedDict:

↓

chỉ hỗ trợ type checker.

Không tạo object thật.

Dataclass:

↓

là object thực.

---

# 21. Dataclass vs attrs

`attrs` là thư viện bên thứ ba, ra đời trước `dataclasses`.

Ưu điểm:

- Có nhiều tính năng nâng cao hơn.
- Validator, converter tích hợp sẵn.
- Hỗ trợ Python cũ.

`dataclasses`:

- Có sẵn trong thư viện chuẩn.
- Đủ mạnh cho phần lớn ứng dụng.
- Phù hợp khi không cần phụ thuộc thêm.

---

# 22. Checklist khi thiết kế Dataclass

Trước khi tạo một dataclass, hãy tự hỏi:

- Đối tượng này chủ yếu mang dữ liệu hay chứa nhiều hành vi?
- Có cần bất biến (`frozen=True`) không?
- Có tạo nhiều instance để nên dùng `slots=True` không?
- Có nhiều tham số cấu hình để nên dùng `kw_only=True` không?
- Có dữ liệu chỉ dùng khi khởi tạo để dùng `InitVar` không?
- Có cần metadata cho serialization hoặc validation không?

Nếu trả lời được các câu hỏi này, bạn sẽ thiết kế dataclass hợp lý hơn.

---

# 23. Mẫu thiết kế hoàn chỉnh cho dự án crawler

```text-x-trilium-auto
BaseModel (slots=True)
│
├── BaseAuditModel
│       ├── created_at
│       └── updated_at
│
├──────────────┐
│              │
│              │
Novel      Chapter
│              │
│              │
Author      Image
│
Category

DTO
│
├── NovelDTO
├── ChapterDTO

Config
│
└── CrawlConfig

Request
│
└── DownloadRequest

Response
│
└── DownloadResponse

Event
│
├── CrawlStarted
└── CrawlFinished
```

Điểm quan trọng:

- **Model** biểu diễn dữ liệu nghiệp vụ.
- **DTO** truyền dữ liệu giữa các tầng.
- **Config** chứa cấu hình.
- **Request/Response** mô tả giao tiếp giữa các module.
- **Event** mô tả sự kiện trong hệ thống.

---

# 24. Những Anti-pattern phổ biến

❌ Dataclass có hàng chục phương thức nghiệp vụ.

❌ Dataclass trực tiếp truy cập database.

❌ Dataclass trực tiếp gọi HTTP.

❌ Dataclass trực tiếp đọc/ghi file.

❌ Một dataclass có quá nhiều trách nhiệm.

Hãy để dataclass tập trung vào **dữ liệu**, còn các service, repository và client đảm nhiệm hành vi.

---

# Bảng tổng kết toàn bộ khóa học

| Chủ đề | Nội dung |
| --- | --- |
| `@dataclass` | Tự sinh `__init__`, `__repr__`, `__eq__` |
| `field()` | Tùy biến từng field |
| `default_factory` | Giá trị mặc định động |
| `__post_init__()` | Xử lý sau khởi tạo |
| `frozen=True` | Immutable |
| `order=True` | So sánh, sắp xếp |
| `slots=True` | Tiết kiệm bộ nhớ |
| `kw_only=True` | API rõ ràng |
| `InitVar` | Dữ liệu chỉ dùng khi khởi tạo |
| Inheritance | Kế thừa dataclass |
| Utility API | `fields()`, `asdict()`, `replace()`... |
| Design Patterns | DTO, Value Object, Entity, Config, Event |

---

# Lộ trình tiếp theo

Sau khi đã làm chủ `dataclass`, mình khuyến nghị học theo thứ tự sau để phục vụ trực tiếp dự án crawler của bạn:

1. `**Enum**` **Deep Dive** – mô hình hóa trạng thái (`NovelStatus`, `CrawlStatus`, `TaskPriority`...).
2. `**pathlib**` **Deep Dive** – quản lý file và thư mục.
3. `**datetime**` **Deep Dive** – xử lý thời gian, timezone, lịch chạy.
4. `**logging**` **Deep Dive** – xây dựng hệ thống log chuyên nghiệp.
5. `**sqlite3**` **+ Repository Pattern** – lưu trữ dữ liệu.
6. `**SQLAlchemy 2.0**` – ORM hiện đại.
7. `**asyncio**` **+** `**aiohttp**` – crawler bất đồng bộ hiệu năng cao.
8. **Dependency Injection** – tổ chức hệ thống lớn.
9. **Plugin Architecture** – mở rộng nhiều nguồn truyện.
10. **Clean Architecture / DDD với Python** – hoàn thiện kiến trúc toàn bộ dự án.

---

# Bài tập tổng hợp (Capstone)

Thiết kế mô hình dữ liệu cho hệ thống crawler:

```text-x-trilium-auto
BaseEntity
│
├── id
├── created_at
├── updated_at
│
├── Novel
├── Chapter
├── Author
├── Category
├── Image
│
├── DTO
│      ├── NovelDTO
│      ├── ChapterDTO
│
├── Config
│      └── CrawlConfig
│
├── Request
│      └── DownloadRequest
│
├── Response
│      └── DownloadResponse
│
└── Event
       ├── CrawlStarted
       └── CrawlFinished
```

Yêu cầu:

- Sử dụng `slots=True` cho các model tạo nhiều instance.
- Dùng `frozen=True` cho các Value Object.
- Dùng `kw_only=True` cho các lớp cấu hình.
- Dùng `InitVar` nếu có dependency chỉ phục vụ khởi tạo.
- Thêm `metadata` cho các field cần phục vụ validation hoặc serialization.
- Viết các hàm `to_dict()`, `to_json()`, `copy_with()` (dựa trên `replace()`).

---

## Kết luận

Sau 12 buổi, bạn đã đi từ kiến thức cơ bản đến các chủ đề nâng cao nhất của `dataclasses`. Với nền tảng này, bạn có thể thiết kế các mô hình dữ liệu rõ ràng, hiệu quả và dễ bảo trì cho những dự án Python lớn như hệ thống crawler truyện, ứng dụng PySide6 hay dịch vụ web backend. Đây là một trong những kỹ năng quan trọng giúp mã nguồn Python trở nên chuyên nghiệp hơn.