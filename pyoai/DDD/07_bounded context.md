# DDD Deep Dive — Buổi 7

# Bounded Context

Hôm nay chúng ta đi vào một trong những khái niệm **quan trọng nhất của Strategic DDD**:

> **Bounded Context là ranh giới mà trong đó một Domain Model và Ubiquitous Language có một meaning thống nhất.**

Roadmap:

```text
Buổi 6 — Subdomain
        ↓
Buổi 7 — Bounded Context  ← hôm nay
        ↓
Buổi 8 — Context Mapping
        ↓
Buổi 9 — Domain Architecture
        ↓
Buổi 10 — DDD + Clean Architecture
```

---

# 1. Vấn đề mà Bounded Context giải quyết

Hãy quay lại hệ thống đọc truyện.

Chúng ta có một khái niệm:

```text
Story
```

Developer rất dễ nghĩ:

```python
class Story:
    ...
```

và sử dụng `Story` ở khắp hệ thống:

```text
Crawler
   ↓
Story

Catalog
   ↓
Story

Reading
   ↓
Story

User
   ↓
Story
```

Ban đầu nhìn rất đẹp.

Nhưng khi hệ thống lớn lên, vấn đề xuất hiện.

---

# 2. `Story` trong Crawling

Crawler cần biết:

```text
Story
├── source_url
├── source_id
├── crawler_plugin
├── external_story_id
└── last_crawled_at
```

Crawler quan tâm:

> Story này lấy từ đâu?

---

# 3. `Story` trong Catalog

Catalog lại quan tâm:

```text
Story
├── title
├── author
├── description
├── genres
├── status
└── cover
```

Catalog quan tâm:

> Story này được hiển thị như thế nào?

---

# 4. `Story` trong Reading

Reading lại quan tâm:

```text
Story
├── reading_order
├── chapters
└── available_content
```

Reading quan tâm:

> User đọc Story này như thế nào?

---

# 5. `Story` trong User

User có thể chỉ cần:

```text
Story
├── story_id
└── title
```

để:

```text
favorite
follow
bookmark
```

User không cần biết:

```text
crawler_plugin
```

---

# 6. Vấn đề

Chúng ta có:

```text
              Story
                │
      ┌─────────┼─────────┐
      ↓         ↓         ↓
   Crawling   Catalog   Reading
```

Nhưng mỗi nơi lại cần:

```text
Story ≠ Story ≠ Story
```

Vậy nên câu hỏi là:

> Có nên tạo **một `Story` class dùng chung toàn hệ thống** không?

Trong DDD:

> **Không nhất thiết. Thậm chí thường là không nên.**

Đây chính là nơi Bounded Context xuất hiện.

---

# 7. Bounded Context là gì?

Định nghĩa thực dụng:

> **Bounded Context là một ranh giới trong đó một model và ngôn ngữ domain có meaning nhất quán.**

Ba từ quan trọng:

```text
Boundary
Model
Language
```

---

# 8. "Bounded" nghĩa là gì?

`Bounded` = có ranh giới.

Ví dụ:

```text
┌─────────────────────────────┐
│      Crawling Context       │
│                             │
│  Story                      │
│  CrawlJob                   │
│  Source                     │
│  CrawlerPlugin              │
│                             │
└─────────────────────────────┘
```

và:

```text
┌─────────────────────────────┐
│       Reading Context       │
│                             │
│  Story                      │
│  ReadingSession             │
│  ReadingProgress            │
│  Bookmark                   │
│                             │
└─────────────────────────────┘
```

Hai context có thể cùng có class:

```text
Story
```

nhưng chúng **không nhất thiết là cùng một model**.

---

# 9. Context Boundary

Context Boundary nói:

> "Từ đây trở vào, những khái niệm này có meaning A."

Ví dụ:

```text
┌────────────────────────────────┐
│ Crawling Context               │
│                                │
│ Story = crawl target           │
│ Source = website               │
│ Chapter = discovered content   │
│                                │
└────────────────────────────────┘
```

Trong Reading:

```text
┌────────────────────────────────┐
│ Reading Context                │
│                                │
│ Story = content collection     │
│ Chapter = readable unit        │
│                                │
└────────────────────────────────┘
```

---

# 10. Ubiquitous Language gắn với Context

Đây là nguyên tắc cực kỳ quan trọng:

> **Ubiquitous Language không nhất thiết tồn tại trên toàn hệ thống.**

Nó tồn tại **bên trong Bounded Context**.

Ví dụ:

### Crawling Context

```text
Source
Crawler
CrawlJob
Discovery
Extraction
```

### Reading Context

```text
Reader
Chapter
ReadingSession
Progress
Bookmark
```

### Catalog Context

```text
Story
Author
Genre
Series
Publication
```

Mỗi context có vocabulary riêng.

---

# 11. Một từ có thể có nhiều meaning

Đây là một trong những lý do Bounded Context tồn tại.

Ví dụ:

```text
"Chapter"
```

Trong Crawling:

> Chapter là nội dung được crawler phát hiện từ website.

Trong Catalog:

> Chapter là một phần của Story được catalog.

Trong Reading:

> Chapter là đơn vị nội dung mà user có thể đọc.

Cùng từ:

```text
Chapter
```

nhưng meaning khác nhau.

---

# 12. "Story" là ví dụ kinh điển

### Crawling

```python
@dataclass
class Story:
    source_id: str
    external_id: str
    url: str
```

### Catalog

```python
@dataclass
class Story:
    title: str
    author: str
    description: str
```

### Reading

```python
@dataclass
class Story:
    story_id: int
    chapters: list[int]
```

Không có gì sai khi có ba `Story`.

---

# 13. Tại sao không dùng một Shared `Story`?

Giả sử:

```python
class Story:
    id: int
    title: str
    author: str
    source_url: str
    crawler_plugin: str
    chapters: list
    reading_progress: float
    bookmarks: list
    ...
```

Sau một thời gian:

```text
Story
├── Crawling logic
├── Catalog logic
├── Reading logic
├── User logic
└── Notification logic
```

Kết quả:

> **God Entity**

và nó vi phạm rất nhiều nguyên tắc thiết kế.

---

# 14. Shared Model tạo coupling

Giả sử Reading muốn thay đổi:

```text
Story.chapters
```

thì:

```text
Catalog
Crawler
User
```

có thể bị ảnh hưởng.

Ta có:

```text
Reading
   ↓
Shared Story
   ↑
Catalog
   ↑
Crawler
   ↑
User
```

Một model trở thành trung tâm coupling.

---

# 15. Bounded Context giảm coupling

Thay vì:

```text
             Shared Story
            /     |      \
       Crawler Catalog Reading
```

ta có:

```text
Crawling Context
      Story

Catalog Context
      Story

Reading Context
      Story
```

Các model độc lập hơn.

---

# 16. Không có nghĩa các Context không giao tiếp

Đây là điểm cực kỳ quan trọng.

Bounded Context **không phải silo**.

Ta vẫn có:

```text
Crawling Context
       ↓
     Event
       ↓
Catalog Context
```

Ví dụ:

```text
ChapterDiscovered
```

Catalog có thể nhận thông tin và tạo model của chính nó.

---

# 17. Mỗi Context sở hữu Model của mình

Ví dụ:

```text
Crawling
    │
    └── CrawledStory

Catalog
    │
    └── CatalogStory

Reading
    │
    └── ReadingStory
```

Không nhất thiết phải đặt tên khác nhau trong code.

Có thể:

```text
crawling.domain.Story
catalog.domain.Story
reading.domain.Story
```

và namespace đã tạo boundary.

---

# 18. Context không nhất thiết là package

Có thể triển khai:

```text
src/
├── crawling/
├── catalog/
├── reading/
└── user/
```

Nhưng Bounded Context là **conceptual boundary trước**, package chỉ là implementation.

---

# 19. Context có thể là Monolith

DDD không yêu cầu microservices.

Ta hoàn toàn có:

```text
Single Application
│
├── Crawling Context
├── Catalog Context
├── Reading Context
├── User Context
└── Notification Context
```

Đây là:

> **Modular Monolith**

Một kiến trúc rất phù hợp khi bắt đầu.

---

# 20. Bounded Context vs Subdomain

Đây là câu hỏi chắc chắn bạn phải phân biệt.

## Subdomain

Trả lời:

> Business có những phần nào?

Ví dụ:

```text
Crawling
Catalog
Reading
User
Notification
```

## Bounded Context

Trả lời:

> Model và language nào được sử dụng trong boundary nào?

Ví dụ:

```text
Crawling Context
Catalog Context
Reading Context
```

---

# 21. Có thể hình dung

```text
Business Domain
       │
       ↓
   Subdomains
       │
       ↓
Bounded Contexts
       │
       ↓
 Domain Models
```

Nhưng mapping không phải lúc nào cũng 1:1.

---

# 22. Trường hợp 1 — Một Subdomain, một Context

Đơn giản:

```text
Crawling Subdomain
        │
        ↓
Crawling Context
```

---

# 23. Trường hợp 2 — Một Subdomain, nhiều Context

Nếu Crawling rất lớn:

```text
Crawling Subdomain
       │
       ├── Source Management Context
       ├── Crawl Execution Context
       └── Crawl Monitoring Context
```

Một business area có thể cần nhiều model boundary.

---

# 24. Trường hợp 3 — Một Context phục vụ nhiều capability nhỏ

Ví dụ:

```text
User Context
│
├── Registration
├── Profile
├── Preferences
└── Authentication
```

Tùy business complexity, có thể cùng một Context.

---

# 25. Context Boundary không phải Database Boundary

Ví dụ một hệ thống có:

```text
SQLite
```

và:

```text
Crawling Context
Catalog Context
Reading Context
```

Chúng có thể dùng cùng một database.

Vẫn có thể là ba Bounded Context.

Điều quan trọng là:

```text
Model boundary
Language boundary
Ownership boundary
```

chứ không phải số database.

---

# 26. Context Boundary cũng không nhất thiết là process boundary

Có thể:

```text
Process
│
├── Crawling Context
├── Catalog Context
└── Reading Context
```

hoặc:

```text
Process A
└── Crawling Context

Process B
└── Catalog Context
```

Deployment là quyết định khác.

---

# 27. Ví dụ project Python

Một modular monolith có thể:

```text
src/
└── app/
    ├── crawling/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    │
    ├── catalog/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    │
    ├── reading/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    │
    └── user/
        ├── domain/
        ├── application/
        └── infrastructure/
```

Chúng ta sẽ đi sâu cấu trúc này ở **Buổi 9–10**.

---

# 28. Crawling Context

Hãy thiết kế thử.

```text
Crawling Context
```

Domain concepts:

```text
Source
CrawlerJob
CrawlerPlugin
CrawlTarget
CrawlResult
```

`Story` ở đây có thể chỉ là:

```python
@dataclass(frozen=True)
class Story:
    external_id: str
    source_url: str
```

Crawler không cần:

```text
author
reading_progress
bookmark
```

---

# 29. Catalog Context

Catalog:

```text
Catalog Context
```

có:

```text
Story
Chapter
Author
Genre
```

Story:

```python
@dataclass
class Story:
    id: int
    title: str
    author: str
    description: str
```

Không cần:

```text
crawler_plugin
reading_progress
```

---

# 30. Reading Context

Reading:

```text
Reading Context
```

có:

```text
ReadingSession
ReadingProgress
Bookmark
Chapter
Story
```

Ở đây `Story` có thể chỉ cần:

```python
@dataclass(frozen=True)
class Story:
    story_id: int
    title: str
```

Reading không cần biết:

```text
source_url
crawler_plugin
```

---

# 31. User Context

User:

```text
User
├── UserAccount
├── UserPreference
├── Favorite
└── Follow
```

User Context có thể chỉ giữ:

```python
@dataclass(frozen=True)
class StoryReference:
    story_id: int
```

Không cần copy toàn bộ Story.

---

# 32. Đây là một insight quan trọng

Không phải context nào cũng cần Entity `Story`.

Có context chỉ cần:

```text
StoryId
```

hoặc:

```text
StoryReference
```

Ví dụ User:

```text
Favorite
├── user_id
└── story_id
```

Thế là đủ.

Không cần:

```text
Favorite
└── Story
    ├── author
    ├── chapters
    ├── crawler
    └── ...
```

---

# 33. Context quyết định mức độ model

Đây là tư duy rất mạnh:

> **Model chỉ nên chứa những gì context cần.**

Ví dụ:

### Crawling

```text
Story
→ crawl identity
```

### Catalog

```text
Story
→ metadata
```

### Reading

```text
Story
→ reading structure
```

### User

```text
Story
→ reference
```

---

# 34. Context giúp tránh "Universal Domain Model"

Anti-pattern:

```text
UniversalStory
UniversalUser
UniversalChapter
UniversalOrder
```

Mỗi object chứa mọi thứ mà toàn hệ thống có thể cần.

Kết quả:

```text
Massive coupling
```

DDD khuyến khích:

```text
Context-specific model
```

---

# 35. Context Boundary và Language

Giả sử từ:

```text
"Source"
```

Trong Crawling:

> Website mà crawler lấy dữ liệu.

Trong Catalog:

> Có thể không tồn tại khái niệm Source.

Trong Reading:

> Hoàn toàn không cần Source.

Điều này cho thấy:

> Không phải domain concept nào cũng phải xuất hiện trong mọi context.

---

# 36. Context Boundary và invariant

Đây là điểm nâng cao.

Một invariant trong Crawling:

> Một CrawlJob chỉ được chạy một lần tại một thời điểm.

Trong Reading:

> ReadingProgress không được vượt quá chapter length.

Hai invariant hoàn toàn khác nhau.

Do đó:

```text
Crawling Context
    ↓
Crawling invariants

Reading Context
    ↓
Reading invariants
```

Mỗi context có rules riêng.

---

# 37. Context Boundary và transaction

Ví dụ:

```text
Crawler
   ↓
ChapterDiscovered
```

Catalog cập nhật:

```text
CatalogStory
CatalogChapter
```

Không nhất thiết transaction phải bao trùm:

```text
Crawling DB
+
Catalog DB
```

Đây là một trong những lý do Context Boundary cực kỳ quan trọng.

Sau này khi học Context Mapping và architecture, vấn đề này sẽ rõ hơn.

---

# 38. Context Boundary và ownership

Một nguyên tắc tốt:

> Mỗi Context nên có quyền sở hữu model của chính nó.

Ví dụ:

```text
Catalog Context
    owns
    CatalogStory
```

Reading không được trực tiếp sửa:

```text
CatalogStory
```

Reading phải thông qua contract/interface/event.

---

# 39. Một ví dụ về coupling xấu

```python
from catalog.domain.story import Story
```

rồi:

```python
class ReadingService:

    def read(self, story: Story):
        ...
```

Reading đang phụ thuộc trực tiếp vào Catalog model.

Nếu Catalog thay đổi:

```text
Story
```

Reading bị ảnh hưởng.

---

# 40. Cách tốt hơn

Reading định nghĩa model của mình:

```python
@dataclass(frozen=True)
class ReadingStory:
    story_id: int
    title: str
```

và nhận dữ liệu cần thiết từ application boundary.

Ta có:

```text
Catalog
   │
   │ contract
   ↓
Reading
```

không phải:

```text
Reading
   ↓
Catalog internal model
```

---

# 41. Context không có nghĩa là "copy tất cả dữ liệu"

Ví dụ Catalog có:

```text
Story
├── title
├── author
├── genres
├── description
├── cover
└── chapters
```

Reading chỉ cần:

```text
story_id
title
```

Không cần copy:

```text
description
genres
cover
```

nếu business không dùng.

---

# 42. Khi nào Context nên có riêng Model?

Hãy hỏi:

> Context này có business rules khác không?

> Có vocabulary khác không?

> Có lifecycle khác không?

> Có ownership khác không?

> Có invariant khác không?

Nếu có nhiều câu trả lời "Có":

```text
Separate Model
```

thường là lựa chọn tốt.

---

# 43. Ví dụ Story lifecycle

### Crawling

```text
Discovered
    ↓
Crawled
    ↓
Failed
```

### Catalog

```text
Draft
    ↓
Published
    ↓
Archived
```

### Reading

Có thể không có lifecycle của Story.

Reading chỉ:

```text
Available
```

và quản lý:

```text
ReadingProgress
```

Cùng `Story`, nhưng lifecycle khác.

Đây là dấu hiệu rất mạnh của Bounded Context.

---

# 44. Bounded Context là nơi model "được phép không đồng nhất"

Một tư duy rất quan trọng:

> **DDD không cố làm mọi model giống nhau.**

Ngược lại:

> DDD chấp nhận sự khác biệt giữa các model để giảm coupling.

Ví dụ:

```text
Catalog:
Story(title, author, description)

Reading:
Story(id, chapters)

Crawling:
Story(external_id, source_url)
```

Không cần ép thành:

```text
UniversalStory(...)
```

---

# 45. Context Map preview

Ở Buổi 8 chúng ta sẽ nối các context:

```text
┌────────────┐
│  Crawling  │
└─────┬──────┘
      │
      │ ChapterDiscovered
      ↓
┌────────────┐
│  Catalog   │
└─────┬──────┘
      │
      │ Catalog data
      ↓
┌────────────┐
│  Reading   │
└────────────┘
```

Nhưng câu hỏi:

> Context nào là upstream?

> Context nào là downstream?

> Ai kiểm soát contract?

> Có cần Anti-Corruption Layer không?

Đó là nội dung **Context Mapping**.

---

# 46. Một Context có thể có nhiều integration points

Ví dụ:

```text
Crawling Context
│
├── → Catalog
├── → Notification
└── → Monitoring
```

Nhưng không có nghĩa Crawling phải biết implementation của tất cả.

Ví dụ:

```text
Crawler
   ↓
ChapterDiscovered
```

Các context khác có thể subscribe/react.

---

# 47. Domain Event và Bounded Context

Event có thể trở thành boundary-crossing message:

```text
Crawling Context
      │
      │ ChapterDiscovered
      ↓
Catalog Context
```

Catalog không cần biết:

```text
CrawlerPlugin
CrawlerJob
HTML parser
```

Nó chỉ cần dữ liệu contract cần thiết.

---

# 48. Một quy tắc rất hữu ích

Khi một context nói:

> "Tôi cần biết toàn bộ object của context kia."

Hãy cảnh giác.

Ví dụ:

```text
Reading needs entire CatalogStory
```

Có thể đang có coupling quá mạnh.

Hỏi lại:

> Reading thực sự cần những field nào?

Có thể chỉ:

```text
story_id
title
chapter_ids
```

---

# 49. Context Boundary trong code

Một cách tổ chức:

```text
src/
└── app/
    ├── crawling/
    │   └── domain/
    │       └── story.py
    │
    ├── catalog/
    │   └── domain/
    │       └── story.py
    │
    └── reading/
        └── domain/
            └── story.py
```

Ba file:

```text
crawling/domain/story.py
catalog/domain/story.py
reading/domain/story.py
```

hoàn toàn có thể có ba class `Story`.

---

# 50. Đừng vội tạo Shared Kernel

Bạn có thể nghĩ:

> "Sao không tạo `common.domain.Story`?"

Đây thường là con đường dẫn đến:

```text
Shared Kernel
```

Shared Kernel tồn tại và có trường hợp hữu ích, nhưng:

> **Không nên dùng nó chỉ vì muốn tránh duplication.**

Duplication đôi khi tốt hơn coupling.

---

# 51. Duplication vs Coupling

Ví dụ:

```text
Catalog Story
title
author

Reading Story
title
```

Có duplication:

```text
title
```

Nhưng coupling thấp.

Nếu ép dùng chung:

```text
SharedStory
```

thì coupling tăng.

Trong DDD:

> **Một chút duplication có thể tốt hơn một abstraction sai.**

---

# 52. Dấu hiệu Bounded Context bị sai

### Dấu hiệu 1

Một model được import khắp nơi:

```python
from shared.domain.story import Story
```

### Dấu hiệu 2

Thay đổi một field làm nhiều module sửa.

### Dấu hiệu 3

Một class có quá nhiều business rule.

### Dấu hiệu 4

Mỗi team dùng từ `Story` nhưng hiểu khác nhau.

### Dấu hiệu 5

Context phải biết implementation nội bộ của context khác.

---

# 53. Một bài tập quan trọng

Hãy thiết kế `Story` ở 4 Context.

## Crawling

```python
class Story:
    ...
```

Hãy xác định 3–5 thuộc tính cần thiết.

## Catalog

```python
class Story:
    ...
```

Xác định 3–5 thuộc tính.

## Reading

```python
class Story:
    ...
```

Xác định 2–4 thuộc tính.

## User

Có cần `Story` Entity không?

Hay chỉ:

```python
class Favorite:
    user_id: int
    story_id: int
```

---

# 54. Bài tập 2 — tìm boundary

Cho các concept:

```text
Crawler
CrawlerJob
Source
Story
Chapter
Author
Genre
ReadingSession
ReadingProgress
Bookmark
User
Notification
```

Hãy chia vào:

```text
Crawling Context
Catalog Context
Reading Context
User Context
Notification Context
```

Không cần mọi concept xuất hiện ở mọi context.

---

# 55. Bài tập 3 — tìm meaning khác nhau

Giải thích `Chapter` có meaning gì trong:

```text
Crawling
Catalog
Reading
```

Ví dụ:

```text
Crawling:
?

Catalog:
?

Reading:
?
```

Đây là bài tập rất quan trọng để bạn thực sự hiểu Bounded Context.

---

# 56. Bài tập 4 — phát hiện coupling

Code:

```python
from catalog.domain.story import Story


class ReadingService:

    def start(self, story: Story):
        ...
```

Hãy trả lời:

1. Vấn đề ở đâu?
2. Reading đang phụ thuộc vào gì?
3. Có nên dùng `catalog.domain.Story` không?
4. Thiết kế lại thế nào?

---

# 57. Bài tập 5 — Context Map Preview

Hãy vẽ:

```text
Crawling
   ↓
?
   ↓
Catalog
   ↓
?
   ↓
Reading
```

và xác định:

```text
Event nào?
Data nào?
Context nào sở hữu model?
```

Đây sẽ là nền tảng trực tiếp cho **Buổi 8 — Context Mapping**.

---

# 58. Tổng kết Buổi 7

Bạn cần nắm thật chắc 6 ý:

### 1. Bounded Context

```text
Boundary của Model + Language
```

### 2. Một từ có thể có nhiều meaning

```text
Story
Chapter
Source
```

### 3. Mỗi Context có model riêng

```text
Crawling.Story
Catalog.Story
Reading.Story
```

### 4. Không dùng Universal Domain Model

```text
❌ UniversalStory
```

### 5. Subdomain ≠ Bounded Context

```text
Subdomain → business boundary
Context   → model/language boundary
```

### 6. Context vẫn cần giao tiếp

```text
Context A
   ↓
Contract / Event
   ↓
Context B
```

---

# Bức tranh Strategic DDD đến hiện tại

```text
                    DOMAIN
                       │
             ┌─────────┴─────────┐
             │                   │
        SUBDOMAINS          Business Capability
             │
     ┌───────┼────────┐
     ↓       ↓        ↓
   CORE  SUPPORTING  GENERIC
     │
     ↓
BOUNDED CONTEXTS
     │
     ├── Crawling Context
     ├── Catalog Context
     ├── Reading Context
     ├── User Context
     └── Notification Context
```

Và bước tiếp theo là **Buổi 8 — Context Mapping**:

```text
Crawling Context
       │
       │ ?
       ↓
Catalog Context
       │
       │ ?
       ↓
Reading Context
```

Chúng ta sẽ học cách xác định **Upstream/Downstream, Partnership, Shared Kernel, Customer/Supplier, Conformist, ACL, Open Host Service và Published Language**, rồi áp dụng trực tiếp vào hệ thống **Crawler → Catalog → Reading**.
