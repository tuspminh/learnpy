# DDD Deep Dive — Buổi 8

# Context Mapping

Ở Buổi 7 chúng ta đã học:

```text
Domain
   ↓
Subdomain
   ↓
Bounded Context
```

Hôm nay chúng ta trả lời câu hỏi tiếp theo:

> **Các Bounded Context giao tiếp và phụ thuộc lẫn nhau như thế nào?**

Đó chính là **Context Mapping**.

---

# 1. Context Map là gì?

Giả sử hệ thống đọc truyện có:

```text
┌──────────────┐
│   Crawling   │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Catalog    │
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Reading    │
└──────────────┘
```

Sơ đồ này mới chỉ cho chúng ta biết:

> Có những Context nào.

Nhưng chưa biết:

* Ai phụ thuộc ai?
* Ai cung cấp dữ liệu?
* Ai kiểm soát contract?
* Model có được chia sẻ không?
* Có cần chuyển đổi model không?
* Context nào là upstream?
* Context nào là downstream?

**Context Map** mô tả những mối quan hệ đó.

---

# 2. Context Map không phải Architecture Diagram

Đây là điểm rất quan trọng.

Context Map tập trung vào:

```text
Business Model
Language
Dependency
Integration
Ownership
```

Không tập trung vào:

```text
Docker
Redis
SQLite
HTTP
FastAPI
PySide6
```

Ví dụ:

```text
Crawling
    │
    │ publishes ChapterDiscovered
    ↓
Catalog
```

đây là Context Mapping.

Còn:

```text
Crawler
    ↓
Redis
    ↓
RabbitMQ
    ↓
Catalog API
```

là technical architecture.

---

# 3. Context Map của hệ thống đọc truyện

Một phiên bản đơn giản:

```text
┌──────────────┐
│   Crawling   │
└──────┬───────┘
       │
       │ ChapterDiscovered
       ↓
┌──────────────┐
│   Catalog    │
└──────┬───────┘
       │
       │ Story/Chapter
       ↓
┌──────────────┐
│   Reading    │
└──────────────┘
```

Sau đó chúng ta phải xác định **relationship** giữa chúng.

---

# 4. Upstream và Downstream

Đây là hai khái niệm phải nắm chắc.

## Upstream

Context cung cấp model hoặc thông tin cho context khác.

```text
A
│
│ provides
↓
B
```

A là:

```text
Upstream
```

---

## Downstream

Context phụ thuộc vào upstream.

```text
A
│
↓
B
```

B là:

```text
Downstream
```

---

# 5. Ví dụ

```text
Crawling
    │
    │ ChapterDiscovered
    ↓
Catalog
```

Ta có:

```text
Crawling = Upstream
Catalog  = Downstream
```

Catalog cần thông tin từ Crawling.

---

# 6. Tại sao Upstream/Downstream quan trọng?

Bởi vì nó cho chúng ta biết:

> Nếu A thay đổi thì B có thể bị ảnh hưởng như thế nào?

Ví dụ:

```text
Crawling
   ↓
Catalog
```

Nếu Crawling thay đổi event:

```text
ChapterDiscovered
```

Catalog có thể bị ảnh hưởng.

Do đó relationship cần được thiết kế rõ ràng.

---

# 7. Relationship #1 — Partnership

**Partnership** xảy ra khi hai Context phụ thuộc lẫn nhau và cùng hợp tác để đạt business goal.

```text
┌────────────┐
│ Context A  │
└─────┬──────┘
      ↕
┌─────┴──────┐
│ Context B  │
└────────────┘
```

Hai bên:

```text
coordinate
negotiate
evolve together
```

---

# 8. Ví dụ Partnership

Giả sử hệ thống có:

```text
Recommendation Context
        ↕
Reading Context
```

Recommendation cần:

```text
Reading history
```

Reading lại cần:

```text
Recommendation result
```

Hai team cùng phát triển contract.

Đây có thể là:

```text
Partnership
```

---

# 9. Partnership có một đặc điểm

Hai bên phải:

> **cùng có khả năng thay đổi contract.**

Không phải:

```text
A quyết định
B phải chạy theo
```

mà là:

```text
A ←→ B
```

---

# 10. Relationship #2 — Shared Kernel

Shared Kernel nghĩa là:

> Hai Context chia sẻ một phần model/code/data được thống nhất.

Ví dụ:

```text
Context A
   │
   ├── Shared Kernel
   │
Context B
```

---

# 11. Ví dụ Shared Kernel

Giả sử:

```text
Catalog
Reading
```

cùng cần một Value Object:

```python
@dataclass(frozen=True)
class StoryId:
    value: int
```

Có thể chia sẻ:

```text
shared/
└── story_id.py
```

Nhưng cần cực kỳ cẩn thận.

---

# 12. Shared Kernel nguy hiểm ở đâu?

Nếu:

```text
Catalog
   ↓
Shared Kernel
   ↑
Reading
```

thì:

```text
Catalog
```

và:

```text
Reading
```

đều phụ thuộc vào Shared Kernel.

Thay đổi:

```text
StoryId
```

có thể ảnh hưởng cả hai.

Vì vậy:

> **Shared Kernel làm giảm duplication nhưng tăng coupling.**

---

# 13. Shared Kernel nên nhỏ

Tốt:

```text
shared/
└── story_id.py
```

Nguy hiểm:

```text
shared/
├── story.py
├── chapter.py
├── author.py
├── repository.py
├── service.py
├── mapper.py
├── ...
```

Đến lúc đó:

> Shared Kernel đã trở thành **God Model**.

---

# 14. Quy tắc thực tế

Nếu bạn chưa có lý do rõ ràng:

```text
Prefer separate models
```

thay vì:

```text
Share everything
```

DDD thường ưu tiên:

```text
Duplication
```

hơn:

```text
Accidental Coupling
```

---

# 15. Relationship #3 — Customer/Supplier

Đây là relationship rất quan trọng.

```text
Supplier
    │
    │ provides
    ↓
Customer
```

Supplier cung cấp service/model.

Customer sử dụng nó.

Ví dụ:

```text
Crawling
    │
    │
    ↓
Catalog
```

Catalog là Customer.

Crawling là Supplier.

---

# 16. Customer/Supplier có nghĩa là gì?

Điểm quan trọng:

> **Downstream Customer có thể đưa ra yêu cầu đối với Upstream Supplier.**

Ví dụ Catalog nói:

> "Tôi cần event chứa `source_id`, `external_story_id`, `title` và `chapter_url`."

Crawling cung cấp contract đáp ứng nhu cầu đó.

---

# 17. Customer/Supplier khác Partnership

### Partnership

```text
A ↔ B
```

Hai bên cùng thương lượng.

### Customer/Supplier

```text
Supplier → Customer
```

Supplier cung cấp.

Customer tiêu thụ.

Có thể có negotiation, nhưng relationship vẫn có hướng rõ ràng.

---

# 18. Relationship #4 — Conformist

Đây là một relationship rất thực tế.

Conformist nghĩa là:

> Downstream chấp nhận model của Upstream mà không cố thay đổi nó.

```text
Upstream
   ↓
Downstream
```

Downstream:

> "API của anh như thế nào thì tôi dùng như thế."

---

# 19. Ví dụ Conformist

Giả sử chúng ta dùng một dịch vụ:

```text
External Book Metadata API
```

API trả:

```json
{
    "book_id": 123,
    "name": "...",
    "author_name": "..."
}
```

Chúng ta có thể conform với model của họ.

Thay vì cố bắt external service thay đổi:

```text
Book
Title
Author
```

ta chấp nhận contract.

---

# 20. Khi nào Conformist phù hợp?

Khi:

```text
Upstream rất mạnh
```

và:

```text
Downstream không có khả năng thương lượng
```

hoặc:

```text
Chi phí tạo abstraction không đáng.
```

Ví dụ:

```text
Google API
Stripe API
GitHub API
```

Bạn không thể yêu cầu họ đổi domain model cho mình.

---

# 21. Vấn đề của Conformist

Model của external system có thể "nhiễm" vào domain.

Ví dụ:

```python
class StripeCustomer:
    ...
```

rồi domain của bạn sử dụng trực tiếp:

```python
StripeCustomer
```

Nếu business model của bạn khác:

> architecture bắt đầu phụ thuộc external model.

Đây là lúc cần:

# Anti-Corruption Layer

---

# 22. Relationship #5 — Anti-Corruption Layer

Đây là một trong những pattern quan trọng nhất của DDD.

Viết tắt:

```text
ACL
```

Anti-Corruption Layer nghĩa là:

> Tạo một lớp bảo vệ Domain Model của mình khỏi model của context khác.

---

# 23. Hình dung

Không tốt:

```text
External Context
      ↓
Our Domain
```

Model external đi thẳng vào domain.

Tốt hơn:

```text
External Context
      ↓
   Adapter
      ↓
    Mapper
      ↓
Our Domain Model
```

---

# 24. Ví dụ với crawler

Website A trả:

```json
{
    "novel_name": "ABC",
    "author_name": "XYZ",
    "chapters": [...]
}
```

Domain Catalog của chúng ta muốn:

```python
@dataclass
class Story:
    title: str
    author: str
```

Không nên:

```python
class Story:
    novel_name: str
    author_name: str
```

chỉ vì external website dùng tên đó.

---

# 25. ACL

Ta tạo:

```text
External API
      ↓
ExternalStoryDTO
      ↓
StoryMapper
      ↓
CatalogStory
```

Ví dụ:

```python
@dataclass
class ExternalStoryDTO:
    novel_name: str
    author_name: str
```

Mapper:

```python
def to_catalog_story(dto: ExternalStoryDTO) -> Story:
    return Story(
        title=dto.novel_name,
        author=dto.author_name,
    )
```

Domain không biết:

```text
novel_name
author_name
```

Domain chỉ biết:

```text
title
author
```

Đó chính là bảo vệ model.

---

# 26. Tại sao gọi là "Anti-Corruption"?

Không phải security.

"Corruption" ở đây nghĩa là:

> Domain Model của chúng ta bị "nhiễm" bởi model bên ngoài.

ACL ngăn:

```text
External Language
       ↓
Our Domain Language
```

---

# 27. Ví dụ cực kỳ rõ

External:

```text
novel_name
chapter_title
chapter_url
```

Our domain:

```text
Story.title
Chapter.title
Chapter.url
```

ACL:

```text
novel_name
      ↓
Story.title

chapter_title
      ↓
Chapter.title
```

---

# 28. ACL trong Python

Một cấu trúc đơn giản:

```text
catalog/
├── domain/
│   ├── story.py
│   └── chapter.py
│
├── application/
│   └── commands.py
│
└── infrastructure/
    └── crawler_acl/
        ├── dto.py
        ├── mapper.py
        └── adapter.py
```

Điểm quan trọng:

```text
domain/
```

không import:

```text
crawler_acl/
```

---

# 29. Relationship #6 — Open Host Service

Open Host Service:

> Context cung cấp một protocol/service chính thức để các context khác sử dụng.

Ví dụ:

```text
Catalog Context
      │
      │ API
      ↓
Reading Context
```

Catalog cung cấp:

```text
GET /stories/{id}
GET /stories/{id}/chapters
```

Đó là một **Open Host Service**.

---

# 30. Tại sao gọi là Open Host Service?

Context:

```text
Catalog
```

đóng vai trò như một "host".

Nó công khai một:

```text
well-defined protocol
```

cho nhiều consumer.

Ví dụ:

```text
Catalog API
     ↑
     ├── Reading
     ├── Search
     ├── Recommendation
     └── Mobile App
```

---

# 31. Open Host Service và API

Không nhất thiết phải là REST.

Có thể là:

```text
REST
gRPC
GraphQL
Message Bus
Event Stream
```

Miễn là có một protocol chính thức để context khác tích hợp.

---

# 32. Relationship #7 — Published Language

Published Language:

> Một ngôn ngữ/format được công khai và chuẩn hóa để các Context giao tiếp.

Ví dụ:

```json
{
    "event": "ChapterDiscovered",
    "story_id": "123",
    "chapter_id": "456",
    "title": "Chapter 10"
}
```

Đây có thể là Published Language.

---

# 33. Published Language thường đi cùng Open Host Service

Ví dụ:

```text
Catalog
   │
   ├── Open Host Service
   │       ↓
   │      API
   │
   └── Published Language
           ↓
        JSON schema
```

Open Host Service:

> Cách truy cập.

Published Language:

> Ngôn ngữ/format được sử dụng để trao đổi.

---

# 34. Event-driven example

Crawling phát:

```python
@dataclass(frozen=True)
class ChapterDiscovered:
    source_id: str
    external_story_id: str
    external_chapter_id: str
    title: str
    url: str
```

Đây là contract.

Catalog nhận:

```text
ChapterDiscovered
       ↓
Mapper
       ↓
CatalogChapter
```

Catalog không cần biết crawler implementation.

---

# 35. Tổng hợp 7 relationship

Bạn nên nhớ bảng này:

| Relationship       | Ý nghĩa                              |
| ------------------ | ------------------------------------ |
| Partnership        | Hai bên hợp tác                      |
| Shared Kernel      | Chia sẻ một phần model               |
| Customer/Supplier  | Supplier cung cấp cho Customer       |
| Conformist         | Downstream chấp nhận model upstream  |
| ACL                | Bảo vệ model khỏi context khác       |
| Open Host Service  | Cung cấp protocol chính thức         |
| Published Language | Ngôn ngữ/format chung được công khai |

---

# 36. Context Map của hệ thống đọc truyện

Một thiết kế khá hợp lý:

```text
                   ┌─────────────────┐
                   │    Crawling     │
                   │    Context      │
                   └────────┬────────┘
                            │
                            │ Published Language
                            │ ChapterDiscovered
                            ↓
                   ┌─────────────────┐
                   │     Catalog     │
                   │    Context      │
                   └────────┬────────┘
                            │
                            │ Open Host Service
                            ↓
                   ┌─────────────────┐
                   │     Reading     │
                   │    Context      │
                   └─────────────────┘
```

---

# 37. Crawling → Catalog

Quan hệ:

```text
Crawling
    ↓
Catalog
```

Có thể thiết kế:

```text
Upstream = Crawling
Downstream = Catalog
```

và dùng:

```text
Published Language
```

Ví dụ:

```text
ChapterDiscovered
StoryDiscovered
```

---

# 38. Catalog → Reading

Có thể:

```text
Catalog
    ↓
Reading
```

Catalog cung cấp:

```text
Story metadata
Chapter metadata
```

Reading tiêu thụ.

Nếu Catalog có API chính thức:

```text
Open Host Service
```

---

# 39. Reading → User

Không nhất thiết phải là:

```text
Reading
   ↓
User
```

Có thể User Context sở hữu:

```text
Favorite
Bookmark
Follow
```

Reading chỉ phát:

```text
ReadingProgressChanged
```

User có thể consume event.

Ví dụ:

```text
Reading
   │
   │ ReadingProgressChanged
   ↓
User
```

---

# 40. Notification

Notification thường là downstream:

```text
Crawling
    │
    │ ChapterDiscovered
    ↓
Notification
```

hoặc:

```text
Catalog
    │
    │ NewChapterPublished
    ↓
Notification
```

Notification không cần biết toàn bộ Catalog model.

Nó chỉ cần event contract.

---

# 41. Tư duy quan trọng: "Data ownership"

Ví dụ:

```text
CatalogStory
```

do:

```text
Catalog Context
```

sở hữu.

Reading không được tự ý sửa:

```text
CatalogStory
```

Reading có:

```text
ReadingStory
```

hoặc:

```text
StoryReference
```

Đây là một cách giữ boundary.

---

# 42. Context Map không chỉ là mũi tên

Một Context Map tốt cần mô tả:

```text
A
 │
 │ relationship
 │
 ↓
B
```

và biết:

```text
Who owns the model?
Who controls the contract?
Who depends on whom?
How is translation done?
How does change propagate?
```

---

# 43. Ví dụ Context Map hoàn chỉnh hơn

```text
                   ┌─────────────────┐
                   │    Crawling     │
                   │     Context     │
                   └────────┬────────┘
                            │
                            │ Published Language
                            │
                            ↓
                   ┌─────────────────┐
                   │     Catalog     │
                   │     Context     │
                   └───────┬─┬───────┘
                           │ │
             Open Host     │ │ Event
             Service       │ │
                           ↓ ↓
                  ┌────────┐ ┌──────────────┐
                  │Reading │ │Notification  │
                  │Context │ │Context       │
                  └────────┘ └──────────────┘
```

---

# 44. Một ví dụ về ACL trong hệ thống của chúng ta

Giả sử crawler plugin trả:

```python
@dataclass
class CrawlerStory:
    novel_name: str
    novel_author: str
    novel_url: str
```

Catalog không dùng trực tiếp.

Ta có:

```text
Crawler
   │
   ↓
CrawlerStory
   │
   ↓
ACL / Mapper
   │
   ↓
CatalogStory
```

Mapper:

```python
def map_story(source: CrawlerStory) -> CatalogStory:
    return CatalogStory(
        title=source.novel_name,
        author=source.novel_author,
    )
```

---

# 45. Lợi ích

Website crawler đổi:

```text
novel_name
```

thành:

```text
book_title
```

thì:

```text
Crawler Adapter
```

thay đổi.

Catalog vẫn giữ:

```python
story.title
```

Domain không bị ảnh hưởng.

Đây chính là giá trị của ACL.

---

# 46. Khi nào nên dùng ACL?

Dùng ACL khi:

```text
External model rất khác
```

hoặc:

```text
External model không đáng tin
```

hoặc:

```text
External system thay đổi thường xuyên
```

hoặc:

```text
Domain của mình có language rất khác
```

---

# 47. Khi nào không cần ACL?

Nếu integration cực kỳ đơn giản:

```text
External API
    ↓
Simple DTO
```

và model hoàn toàn phù hợp, không cần tạo một lớp abstraction quá lớn.

DDD không phải:

> "Pattern nào cũng phải dùng."

Mà là:

> **Dùng pattern khi relationship thực sự cần nó.**

---

# 48. Sai lầm: ACL cho mọi thứ

Nếu có:

```text
Context A
    ↓
Context B
```

và mỗi field đều giống nhau:

```text
id
title
```

mà tạo:

```text
Mapper
Translator
Adapter
Facade
AntiCorruptionLayer
TranslatorFactory
```

thì có thể đang over-engineering.

---

# 49. Sai lầm: Shared Kernel cho tiện

Developer thường nghĩ:

> "Hai context dùng chung class này, tạo common package đi."

Sau vài tháng:

```text
common/
├── Story
├── Chapter
├── User
├── Repository
├── Service
├── DTO
└── Utils
```

Rồi tất cả Context:

```text
Crawling
Catalog
Reading
User
```

đều import `common`.

Kết quả:

> Bounded Context gần như biến mất.

---

# 50. Một nguyên tắc rất đáng nhớ

> **Bounded Context tồn tại để bảo vệ model khỏi sự thay đổi bên ngoài.**

Context Map giúp chúng ta hiểu:

> **Context nào đang đe dọa model của context nào?**

Từ đó chọn:

```text
Partnership
Shared Kernel
Customer/Supplier
Conformist
ACL
Open Host Service
Published Language
```

---

# 51. Bài tập thực hành 1

Cho:

```text
Crawling
Catalog
Reading
Notification
```

Hãy xác định relationship:

```text
Crawling → Catalog
Catalog → Reading
Catalog → Notification
Reading → Notification
```

Bạn chọn relationship nào?

Gợi ý:

```text
Published Language
Open Host Service
Customer/Supplier
ACL
```

Không nhất thiết chỉ có một đáp án.

Điều quan trọng là **giải thích lý do**.

---

# 52. Bài tập thực hành 2

Cho external API:

```json
{
    "novel_name": "One Piece",
    "novel_author": "Eiichiro Oda",
    "chapter_list": []
}
```

Domain của Catalog:

```python
@dataclass
class Story:
    title: str
    author: str
```

Hãy thiết kế:

```text
External DTO
       ↓
     Mapper
       ↓
Catalog Story
```

và viết Python code.

---

# 53. Bài tập thực hành 3

Phân biệt:

```text
A. Hai context dùng chung Story class

B. Hai context có Story riêng

C. Hai context có Story riêng nhưng chia sẻ StoryId

D. Một context gọi API của context kia

E. Một context nhận event từ context kia
```

Với mỗi trường hợp, hãy trả lời:

> Coupling tăng hay giảm?

---

# 54. Bài tập thực hành 4 — thiết kế Context Map

Hãy vẽ Context Map cho:

```text
Crawling
Catalog
Reading
User
Notification
```

và đánh dấu:

```text
↑ Upstream
↓ Downstream
↔ Partnership
ACL
OHS
Published Language
```

---

# 55. Tóm tắt Buổi 8

Toàn bộ bài hôm nay có thể thu gọn thành:

```text
Bounded Context
       │
       ↓
Context Map
       │
       ├── Partnership
       ├── Shared Kernel
       ├── Customer/Supplier
       ├── Conformist
       ├── Anti-Corruption Layer
       ├── Open Host Service
       └── Published Language
```

Và hệ thống đọc truyện:

```text
┌──────────────┐
│   Crawling   │
└──────┬───────┘
       │
       │ Published Language
       │ ChapterDiscovered
       ↓
┌──────────────┐
│   Catalog    │
└──────┬───────┘
       │
       │ Open Host Service
       ↓
┌──────────────┐
│   Reading    │
└──────────────┘
```

Điểm quan trọng nhất cần nhớ:

> **Bounded Context nói "model nào thuộc về boundary nào"; Context Mapping nói "những boundary đó quan hệ với nhau như thế nào".**

---

## Chuỗi Strategic DDD

```text
Buổi 6
Subdomain
   ↓
Core / Supporting / Generic

Buổi 7
Bounded Context
   ↓
Model + Language Boundary

Buổi 8
Context Mapping
   ↓
Relationship giữa các Context

Buổi 9
Domain Architecture
   ↓
Domain
Application
Infrastructure
Interface

Buổi 10
DDD + Clean Architecture
   ↓
Ports & Adapters
Dependency Rule
Project Python
```

**Buổi 9** chúng ta sẽ chuyển từ Strategic DDD sang **Domain Architecture**: làm thế nào tổ chức `Domain Layer`, `Application Layer`, `Infrastructure Layer`, `Interface Layer`, và đặc biệt là **Dependency Direction + Dependency Inversion** trong Python.
