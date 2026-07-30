# Domain-Driven Design Deep Dive

# Buổi 5: Context Mapping (Cách các Bounded Context giao tiếp với nhau)

> **Nếu Bounded Context là các quốc gia, thì Context Mapping chính là ngoại giao giữa các quốc gia đó.**

Đây là chương cực kỳ quan trọng trong DDD vì trong thực tế:

  * Không có hệ thống nào chỉ có **1 Bounded Context**. 
  * Không có Context nào sống hoàn toàn độc lập. 
  * Điều khó nhất không phải thiết kế Entity, mà là **thiết kế cách các Context giao tiếp**. 



* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ Buổi 4: Bounded Context

✅ **Buổi 5: Context Mapping**

⬜ Buổi 6: Entity

⬜ Buổi 7: Value Object

...

* * *

# 1\. Tại sao cần Context Mapping?

Giả sử hệ thống App Cào Truyện của chúng ta có:
    
    
    Crawler Context
    
    Reader Context
    
    Search Context
    
    Recommendation Context
    
    Library Context

Một ngày...

Crawler vừa crawl được truyện mới.

Làm sao

Reader biết?

Search biết?

Recommendation biết?

Library biết?

Nếu không thiết kế cẩn thận

hệ thống sẽ trở thành
    
    
    Crawler
    
    ↓
    
    Reader
    
    ↓
    
    Search
    
    ↓
    
    Recommendation
    
    ↓
    
    Library

Sau vài năm

mọi module gọi lẫn nhau.

Không thể bảo trì.

* * *

# 2\. Context Mapping là gì?

Context Mapping

là

> Bản đồ mô tả cách các Bounded Context giao tiếp với nhau.

Ví dụ
    
    
    Crawler
    
    ↓
    
    Library
    
    ↓
    
    Reader

hay
    
    
    Crawler
    
    ↓
    
    Search
    
    ↓
    
    Recommendation

DDD không chỉ hỏi

"Context là gì?"

mà còn hỏi

"Context nói chuyện với nhau như thế nào?"

* * *

# 3\. Ví dụ thực tế

Shopee
    
    
    Inventory
    
    ↓
    
    Order
    
    ↓
    
    Payment
    
    ↓
    
    Shipping

Order

không được

UPDATE trực tiếp

Inventory Database.

Thay vào đó

gửi yêu cầu.

Đó chính là

Context Mapping.

* * *

# 4\. Ví dụ App Cào Truyện

Crawler

crawl được

Novel mới.

Không nên
    
    
    reader.save(novel)
    
    search.save(novel)
    
    recommendation.save(novel)
    
    statistics.save(novel)

Crawler

đang biết

quá nhiều.

Coupling rất lớn.

* * *

# 5\. Nên làm gì?

Crawler

chỉ nên nói
    
    
    Novel Crawled

Thế thôi.

Ai quan tâm

thì nghe.

Ví dụ
    
    
    Crawler
    
    ↓
    
    NovelCrawled Event
    
    ↓
    
    Search
    
    ↓
    
    Recommendation
    
    ↓
    
    Library

Đây là mô hình Event-Driven rất phổ biến trong DDD.

* * *

# 6\. Quan hệ giữa Context

DDD định nghĩa nhiều kiểu quan hệ.

Chúng ta sẽ học lần lượt.
    
    
    Shared Kernel
    
    Customer/Supplier
    
    Conformist
    
    Anti-Corruption Layer
    
    Open Host Service
    
    Published Language
    
    Partnership

* * *

# 7\. Shared Kernel

Hai Context

chia sẻ

một phần nhỏ

Domain Model.

Ví dụ
    
    
    Reader
    
    ↓
    
    BookId
    
    NovelId
    
    ChapterId

và
    
    
    Bookmark

đều dùng
    
    
    @dataclass(frozen=True)
    class NovelId:
        value: str

Thì

NovelId

là

Shared Kernel.

* * *

Không nên chia sẻ

toàn bộ Entity.

Chỉ chia sẻ

những thứ thật sự ổn định.

* * *

Ví dụ
    
    
    shared/
    
        ids.py
    
        events.py
    
        exceptions.py

* * *

# 8\. Customer / Supplier

Ví dụ

Crawler

là

Supplier.

Reader

là

Customer.
    
    
    Crawler
    
    ↓
    
    Novel
    
    ↓
    
    Reader

Reader

phụ thuộc

Crawler.

Nếu

Crawler

đổi API

Reader

phải cập nhật.

* * *

Ví dụ Python

Crawler
    
    
    class CrawlService:
    
        def crawl(self) -> Novel:
            ...

Reader
    
    
    novel = crawl_service.crawl()

Reader

đang phụ thuộc.

* * *

# 9\. Conformist

Conformist nghĩa là

"Tôi chấp nhận theo luật của anh."

Ví dụ

Bạn dùng

Stripe.

Stripe trả về
    
    
    {
        "payment_intent": {}
    }

Bạn không thể bảo

Stripe

đổi thành
    
    
    {
        "payment": {}
    }

Bạn phải

conform.

* * *

Trong Python
    
    
    payment_intent = stripe.payment_intent.retrieve(...)

Không nên

đổi tên

API của Stripe.

* * *

# 10\. Anti-Corruption Layer (ACL)

Đây là pattern nổi tiếng nhất.

Giả sử

Website A

trả
    
    
    {
        "story_name": "...",
        "story_author": "...",
        "story_cover": "..."
    }

Website B
    
    
    {
        "title": "...",
        "author": "...",
        "cover": "..."
    }

Website C
    
    
    {
        "book_title": "...",
        "writer": "..."
    }

Nếu

Reader

phải hiểu

tất cả

format này

thì rất khổ.

* * *

ACL nói rằng

tạo

Translator.
    
    
    Website
    
    ↓
    
    Translator
    
    ↓
    
    Novel

* * *

Python
    
    
    from dataclasses import dataclass
    
    
    @dataclass
    class Novel:
        title: str
        author: str
    
    
    class NovelTranslator:
    
        def from_site_a(self, data):
    
            return Novel(
                title=data["story_name"],
                author=data["story_author"]
            )
    
        def from_site_b(self, data):
    
            return Novel(
                title=data["title"],
                author=data["author"]
            )

Reader

không biết

Website A.

Không biết

Website B.

Reader chỉ biết

Novel.

Đó là ACL.

* * *

# 11\. Đây chính là Plugin Parser của dự án bạn

Bạn đã học Plugin Architecture.

Mỗi website
    
    
    truyenfull
    
    metruyen
    
    truyenyy
    
    bachngocsach
    
    ...

trả

HTML khác nhau.

Parser

chuyển thành
    
    
    Novel
    Chapter
    Author
    Category

Parser

chính là

Anti-Corruption Layer.

Đây là lý do kiến trúc plugin parser của bạn rất phù hợp với DDD.

* * *

# 12\. Published Language

Các Context

đồng ý

dùng

một ngôn ngữ chung.

Ví dụ

Event
    
    
    NovelCreated
    
    NovelUpdated
    
    NovelDeleted

Mọi Context

đều hiểu.

* * *

Python
    
    
    @dataclass(frozen=True)
    class NovelCreated:
    
        novel_id: str
    
        title: str

Không cần

chia sẻ Entity.

Chỉ chia sẻ

Event.

* * *

# 13\. Open Host Service

Một Context

công bố

API chuẩn.

Ví dụ

Search
    
    
    GET /search?q=...

Reader

Recommendation

Admin

đều gọi.

Không truy cập trực tiếp

Database.

* * *

# 14\. Partnership

Hai Context

phát triển cùng nhau.

Ví dụ

Crawler

và

Parser

luôn thay đổi đồng thời.

Team

thường họp chung.

Release cùng.

Đó là Partnership.

* * *

# 15\. Context Mapping của App Cào Truyện
    
    
                   +----------------+
                   | Source Manager |
                   +----------------+
                            |
                            |
                            v
                   +----------------+
                   |    Crawler     |
                   +----------------+
                            |
                     NovelCrawled
                            |
            +---------------+----------------+
            |               |                |
            v               v                v
     +--------------+ +--------------+ +--------------+
     |    Search    | | Recommendation| |   Library    |
     +--------------+ +--------------+ +--------------+
                                           |
                                           |
                                           v
                                   +---------------+
                                   |    Reader     |
                                   +---------------+

Đây là

Event Driven Context Mapping.

* * *

# 16\. Mapping bằng Event

Crawler
    
    
    class CrawlNovelUseCase:
    
        def execute(self):
    
            novel = ...
    
            event = NovelCreated(
                novel.id,
                novel.title
            )
    
            event_bus.publish(event)

Search
    
    
    class SearchUpdater:
    
        def handle(self, event):
    
            ...

Recommendation
    
    
    class RecommendationUpdater:
    
        def handle(self, event):
    
            ...

Crawler

không biết

Search.

Không biết

Recommendation.

Coupling rất thấp.

* * *

# 17\. Mapping bằng Repository (Không nên lạm dụng)

Nhiều người làm
    
    
    crawler.reader_repository.save()
    
    crawler.search_repository.save()
    
    crawler.bookmark_repository.save()

Crawler

đang biết

mọi Context.

Đây là kiến trúc khó mở rộng.

* * *

# 18\. Best Practices

### Không chia sẻ Entity giữa Context

Sai
    
    
    reader.Novel
    
    ↓
    
    crawler.Novel

Đúng
    
    
    Crawler Novel
    
    ↓
    
    DTO / Event
    
    ↓
    
    Reader Novel

* * *

### Dùng Event thay vì gọi trực tiếp

Sai
    
    
    crawler.update_search()

Đúng
    
    
    event_bus.publish(
        NovelCreated(...)
    )

* * *

### ACL ở ranh giới hệ thống

Không để

HTML

đi vào

Domain.

Không để

JSON

đi vào

Entity.

Chuyển đổi ở Infrastructure hoặc ACL trước.

* * *

### Chỉ chia sẻ những gì thật sự ổn định

Ví dụ
    
    
    NovelId
    
    ChapterId
    
    Domain Events

Không chia sẻ

toàn bộ Entity.

* * *

# 19\. Liên hệ với Clean Architecture

Khi kết hợp với kiến trúc bạn đã học, một luồng hoàn chỉnh sẽ là:
    
    
    Website
          │
          ▼
    Infrastructure
          │
          ▼
    Anti-Corruption Layer
          │
          ▼
    Application
          │
          ▼
    Domain
          │
          ▼
    Domain Event
          │
          ▼
    Event Bus
          │
          ▼
    Search / Reader / Recommendation

Bạn có thể thấy rất nhiều chủ đề chúng ta đã học trước đây bắt đầu ghép lại:

  * **Plugin Architecture** → Plugin Parser. 
  * **Clean Architecture** → chia tầng. 
  * **Repository Pattern** → lưu trữ. 
  * **Domain Events** → giao tiếp giữa Context. 
  * **DDD** → xác định ranh giới và mô hình. 



* * *

# 20\. Thiết kế cho dự án của bạn

Nếu xây dựng App Cào Truyện theo DDD, tôi khuyến nghị:
    
    
    Source Context
          │
          ▼
    Crawler Context
          │
          ▼
    Parser Context (ACL)
          │
          ▼
    NovelCreated Event
          │
     ┌────┼───────────────┐
     ▼    ▼               ▼
    Library Search Recommendation
          │
          ▼
    Reader Context

Trong đó:

  * **Parser Context** đóng vai trò **Anti-Corruption Layer** giữa website bên ngoài và Domain nội bộ. 
  * **NovelCreated** , **ChapterUpdated** ,... là **Published Language**. 
  * **Event Bus** là cơ chế chính để giao tiếp giữa các Context. 



* * *

# Bài tập

## Bài 1

Vẽ Context Mapping cho App Cào Truyện gồm:

  * Source 
  * Crawler 
  * Parser 
  * Search 
  * Recommendation 
  * Library 
  * Reader 



và chỉ rõ mũi tên giao tiếp.

* * *

## Bài 2

Hãy xác định:

  * Context nào là Supplier? 
  * Context nào là Customer? 
  * Context nào nên dùng Partnership? 



* * *

## Bài 3

Thiết kế một **Anti-Corruption Layer** cho ba website truyện có JSON khác nhau nhưng đều được chuyển thành cùng một `Novel` Domain Entity.

* * *

# Tổng kết

Sau buổi học này, bạn cần ghi nhớ:

  * **Context Mapping** mô tả cách các **Bounded Context** giao tiếp với nhau. 
  * Không nên để các Context gọi trực tiếp hoặc phụ thuộc sâu vào mô hình của nhau. 
  * **Anti-Corruption Layer (ACL)** bảo vệ Domain khỏi mô hình bên ngoài và đặc biệt phù hợp với hệ thống plugin parser của ứng dụng cào truyện. 
  * **Published Language** (thường là Domain Events hoặc DTO) là cách an toàn để các Context trao đổi thông tin. 
  * Với hệ thống lớn, **Event-Driven** thường giúp giảm coupling và tăng khả năng mở rộng hơn so với việc các Context gọi trực tiếp nhau. 



Ở **Buổi 6** , chúng ta sẽ bắt đầu phần **Tactical Design** với **Entity**. Đây là lúc đi từ kiến trúc tổng thể sang cách viết các Domain Model "chuẩn DDD", bao gồm identity, vòng đời (lifecycle), business behavior và cách Entity khác với Model thông thường trong các framework CRUD.

