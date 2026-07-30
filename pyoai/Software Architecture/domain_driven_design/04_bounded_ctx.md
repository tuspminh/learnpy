# Domain-Driven Design Deep Dive

# Buổi 4: Bounded Context (Trái tim của Domain-Driven Design)

> Nếu phải chọn **một khái niệm quan trọng nhất trong DDD** , tôi sẽ chọn **Bounded Context**.

Rất nhiều dự án thất bại không phải vì code kém, mà vì **mọi người đang nói cùng một từ nhưng hiểu theo những ý nghĩa khác nhau**.

Sau buổi này, bạn sẽ hiểu:

  * Tại sao cùng là `User` nhưng có thể có 5 kiểu User khác nhau. 
  * Tại sao không nên có một `models.py` chứa hàng trăm Entity. 
  * Vì sao Microservices chịu ảnh hưởng rất lớn từ DDD. 
  * Cách chia Bounded Context cho dự án App Cào Truyện của bạn. 



* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ Buổi 3: Domain & Subdomain

✅ **Buổi 4: Bounded Context**

⬜ Buổi 5: Context Mapping

...

* * *

# 1\. Bounded Context là gì?

Định nghĩa ngắn gọn:

> Một Bounded Context là **ranh giới mà trong đó Ubiquitous Language có một ý nghĩa duy nhất.**

Hay nói đơn giản hơn:

> Bên trong Context, mọi người đều hiểu một thuật ngữ giống nhau.

* * *

Ví dụ

Một công ty bán hàng.

Có từ
    
    
    Customer

Nhưng...

Phòng Marketing hiểu
    
    
    Customer
    
    ↓
    
    Người nhận quảng cáo

* * *

Phòng Sales hiểu
    
    
    Customer
    
    ↓
    
    Người mua hàng

* * *

Phòng Support hiểu
    
    
    Customer
    
    ↓
    
    Người đang mở ticket

* * *

Phòng Billing hiểu
    
    
    Customer
    
    ↓
    
    Người thanh toán hóa đơn

Đều gọi là

Customer

Nhưng

không giống nhau.

* * *

# 2\. Nếu không có Bounded Context

Developer thường viết
    
    
    class Customer:
        id: int
        email: str
        phone: str
        tickets: list
        invoices: list
        orders: list
        campaigns: list
        loyalty_points: int
        support_level: str
        ...

Một class

5000 dòng.

Mọi module đều sửa.

Cuối cùng

không ai dám động vào.

Đây gọi là

> God Object

* * *

# 3\. DDD giải quyết thế nào?

DDD nói

Đừng tạo

một Customer.

Hãy tạo

nhiều Customer.

Ví dụ

Marketing Context
    
    
    class Customer:
        email: str
        subscribed: bool

* * *

Support Context
    
    
    class Customer:
        tickets: list

* * *

Sales Context
    
    
    class Customer:
        orders: list

* * *

Billing Context
    
    
    class Customer:
        invoices: list

Tên giống nhau.

Ý nghĩa khác nhau.

Không sao cả.

Miễn là

không vượt khỏi Context.

* * *

# 4\. Một ví dụ khác

Shopee

Có từ
    
    
    Product

* * *

Trong Search
    
    
    class Product:
        name
        keywords
        score

* * *

Trong Inventory
    
    
    class Product:
        quantity
        warehouse

* * *

Trong Recommendation
    
    
    class Product:
        category
        similarity_vector

* * *

Trong Payment

Thậm chí

không cần Product.

Chỉ cần
    
    
    class OrderItem:
        price

Đó là sức mạnh của Bounded Context.

* * *

# 5\. App Cào Truyện

Đây là ví dụ sát với dự án của bạn.

Có từ
    
    
    Novel

Nếu không có Context

Developer viết
    
    
    class Novel:
    
        title
    
        author
    
        category
    
        description
    
        chapters
    
        bookmarks
    
        reading_history
    
        crawl_time
    
        parser_version
    
        rating
    
        comments
    
        download_url
    
        views
    
        favorites
    
        ...

Sau vài năm

class này

100 thuộc tính.

* * *

DDD nói

chia ra.

* * *

# 6\. Crawler Context

Ở Context này

Novel chỉ cần
    
    
    from dataclasses import dataclass
    
    @dataclass
    class Novel:
        url: str
        title: str
        last_updated: str

Crawler

không cần biết

Bookmark là gì.

* * *

# 7\. Parser Context
    
    
    from dataclasses import dataclass
    
    @dataclass
    class Novel:
        raw_html: str
        metadata: dict

Parser

không cần biết

Reader.

* * *

# 8\. Reader Context
    
    
    from dataclasses import dataclass
    
    @dataclass
    class Novel:
        id: int
        title: str
        chapters: list

Reader

không cần biết

Crawler.

* * *

# 9\. Recommendation Context
    
    
    from dataclasses import dataclass
    
    @dataclass
    class Novel:
        id: int
        tags: list[str]
        score: float

Không cần

HTML.

Không cần

URL.

* * *

# 10\. Cùng tên

Nhưng khác Context
    
    
    Crawler Context
    
    Novel

↓
    
    
    Parser Context
    
    Novel

↓
    
    
    Reader Context
    
    Novel

↓
    
    
    Recommendation Context
    
    Novel

Đều tên

Novel

Nhưng

là

4 model khác nhau.

* * *

# 11\. Điều này có mâu thuẫn không?

Không.

Vì

Bounded Context

chính là

ranh giới.

Bên trong

được quyền định nghĩa

Novel

theo cách phù hợp nhất.

* * *

# 12\. Ví dụ thư mục
    
    
    src/
    
        crawler/
    
            domain/
    
                entities/
    
                    novel.py
    
        parser/
    
            domain/
    
                entities/
    
                    novel.py
    
        reader/
    
            domain/
    
                entities/
    
                    novel.py
    
        recommendation/
    
            domain/
    
                entities/
    
                    novel.py

Có

4 file

Novel.py

Hoàn toàn bình thường.

* * *

# 13\. Không chia Context sẽ xảy ra gì?

Ví dụ

Reader thêm
    
    
    novel.font_size

* * *

Crawler

không dùng.

* * *

Parser

không dùng.

* * *

Search

không dùng.

* * *

Nhưng

tất cả đều phải rebuild.

Đó là coupling.

* * *

# 14\. Một ví dụ khác

Ngân hàng

Có từ
    
    
    Account

* * *

Customer Context
    
    
    Account
    
    owner
    
    phone

* * *

Transaction Context
    
    
    Account
    
    balance
    
    currency

* * *

Security Context
    
    
    Account
    
    password_hash
    
    mfa

* * *

Audit Context
    
    
    Account
    
    created_at
    
    updated_at
    
    history

Không cần

gộp vào

một Account.

* * *

# 15\. Bounded Context và Database

Một sai lầm rất phổ biến.

Nhiều người nghĩ
    
    
    Một Entity
    
    ↓
    
    Một Table

DDD

không nói vậy.

Ví dụ

Reader Context
    
    
    Novel

có thể lấy dữ liệu từ
    
    
    novels
    
    chapters
    
    reading_progress

* * *

Trong khi

Crawler Context
    
    
    Novel

chỉ đọc
    
    
    crawl_jobs
    
    crawl_sources

Entity không nhất thiết ánh xạ 1-1 với bảng dữ liệu.

* * *

# 16\. Bounded Context và Clean Architecture

Bạn đã học
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain
    
    ↓
    
    Infrastructure

Nếu kết hợp DDD

sẽ thành
    
    
    Crawler Context
    
    Presentation
    
    Application
    
    Domain
    
    Infrastructure

và
    
    
    Reader Context
    
    Presentation
    
    Application
    
    Domain
    
    Infrastructure

Mỗi Context

gần như

một hệ thống nhỏ.

* * *

# 17\. Thiết kế cho App Cào Truyện

Tôi đề xuất chia thành các Bounded Context sau:

## Context 1 — Source Management

Chịu trách nhiệm:

  * Quản lý nguồn truyện 
  * Plugin 
  * Enable/Disable nguồn 
  * Kiểm tra trạng thái nguồn 



Entity
    
    
    Source
    
    Plugin
    
    Capability

* * *

## Context 2 — Crawling

Entity
    
    
    Crawler
    
    Novel
    
    Chapter
    
    CrawlJob

* * *

## Context 3 — Parsing

Entity
    
    
    RawPage
    
    Parser
    
    Novel
    
    Chapter

* * *

## Context 4 — Library

Entity
    
    
    Novel
    
    Shelf
    
    Category

* * *

## Context 5 — Reader

Entity
    
    
    Novel
    
    ReadingProgress
    
    Bookmark
    
    ReadingHistory

* * *

## Context 6 — Recommendation

Entity
    
    
    Novel
    
    Tag
    
    RecommendationModel

* * *

## Context 7 — Search

Entity
    
    
    NovelIndex
    
    Keyword
    
    SearchQuery

Lưu ý rằng `Novel` trong **Library** , **Reader** , **Crawler** và **Recommendation** không nhất thiết có cùng thuộc tính hoặc hành vi.

* * *

# 18\. Khi nào cần tạo Context mới?

Đây là một câu hỏi rất quan trọng.

Một dấu hiệu tốt là:

> Hai nhóm người trong nghiệp vụ bắt đầu dùng cùng một từ nhưng với ý nghĩa khác nhau.

Hoặc:

> Một Entity ngày càng phình to vì phải phục vụ nhiều mục đích khác nhau.

Ví dụ:
    
    
    class Novel:
        ...
        crawl_url
        ...
        bookmark_count
        ...
        search_keywords
        ...
        embedding_vector
        ...
        parser_version

Đây thường là dấu hiệu bạn đang cố nhồi nhiều Context vào cùng một Entity.

* * *

# 19\. Best Practices

✅ Chia Context theo nghiệp vụ, **không phải theo công nghệ**.

Không nên:
    
    
    controllers/
    models/
    services/
    repositories/

Đối với hệ thống lớn, nên nghĩ theo:
    
    
    crawler/
    reader/
    search/
    recommendation/

* * *

✅ Chấp nhận việc cùng một khái niệm có nhiều mô hình.

Ví dụ:

  * `Novel` của Reader. 
  * `Novel` của Crawler. 
  * `Novel` của Search. 



Đừng cố ép chúng thành một lớp duy nhất.

* * *

✅ Giảm phụ thuộc giữa các Context.

Mỗi Context nên có thể phát triển tương đối độc lập.

* * *

# 20\. Bài tập

## Bài 1

Trong dự án App Cào Truyện, hãy xác định ít nhất **6 Bounded Context**.

* * *

## Bài 2

Đối với mỗi Context, hãy trả lời:

  * Ubiquitous Language là gì? 
  * Entity chính là gì? 
  * Context này chịu trách nhiệm điều gì? 



* * *

## Bài 3

Hãy thiết kế cây thư mục theo Bounded Context, ví dụ:
    
    
    src/
        crawler/
            application/
            domain/
            infrastructure/
        reader/
            application/
            domain/
            infrastructure/
        search/
            application/
            domain/
            infrastructure/

* * *

# Tổng kết

Sau buổi này, bạn nên nắm vững:

  * **Bounded Context** là ranh giới mà trong đó một mô hình và Ubiquitous Language có ý nghĩa nhất quán. 
  * Cùng một thuật ngữ (`Novel`, `Customer`, `Product`...) có thể được mô hình hóa khác nhau ở các Context khác nhau. 
  * Không nên tạo một "God Entity" phục vụ mọi nghiệp vụ. 
  * Mỗi Context nên có Domain Model, Use Case và Infrastructure riêng để giảm coupling và tăng khả năng mở rộng. 



Ở **Buổi 5** , chúng ta sẽ học **Context Mapping** — cách các Bounded Context giao tiếp với nhau, chia sẻ dữ liệu và bảo vệ mô hình nghiệp vụ mà không làm hệ thống trở nên phụ thuộc chặt chẽ. Đây là bước kết nối các Context thành một hệ thống DDD hoàn chỉnh.

