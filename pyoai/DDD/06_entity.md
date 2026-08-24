# DDD Deep Dive — Buổi 6

# Subdomain — Chia Domain thành những phần có ý nghĩa

Theo roadmap bạn vừa xác định, từ **Buổi 6** chúng ta bước vào:

# Phần II — Strategic DDD

```text
Buổi 6 — Subdomain
Buổi 7 — Bounded Context
Buổi 8 — Context Mapping
Buổi 9 — Domain Architecture
Buổi 10 — DDD + Clean Architecture
```

Hôm nay tập trung hoàn toàn vào **Subdomain**.

---

# 1. Nhắc lại: Domain là gì?

Giả sử chúng ta xây:

> Hệ thống đọc và crawl truyện.

Toàn bộ bài toán business là:

```text
Story Reading Platform
```

Đây là **Domain**.

Nhưng Domain khá lớn:

```text
Story Reading Platform
│
├── Crawling
├── Catalog
├── Reading
├── User
├── Notification
├── Search
├── Recommendation
└── ...
```

Nếu chúng ta cố xây một model duy nhất cho toàn bộ Domain:

```text
                    Domain
                      │
                    Story
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
     Crawler        Reader         User
```

hệ thống sẽ nhanh chóng trở nên phức tạp.

DDD đưa ra một ý tưởng:

> **Chia Domain lớn thành các Subdomain.**

---

# 2. Subdomain là gì?

Có thể hiểu đơn giản:

> **Subdomain là một phần có phạm vi và mục đích nghiệp vụ riêng bên trong một Domain lớn.**

Ví dụ:

```text
Domain
"Story Reading Platform"
```

có thể gồm:

```text
Crawling
Catalog
Reading
User
Notification
```

Mỗi phần giải quyết một nhóm business problem riêng.

---

# 3. Subdomain không phải module Python

Đây là điều phải nhớ ngay từ đầu.

Subdomain là:

```text
Business concept
```

không phải:

```text
Python package
```

Ví dụ:

```text
domain/
├── crawler/
├── catalog/
├── reading/
└── user/
```

có thể phản ánh Subdomain.

Nhưng:

> Package `crawler` không tự động trở thành Subdomain chỉ vì chúng ta đặt folder tên `crawler`.

Phải xuất phát từ business.

---

# 4. Vì sao cần Subdomain?

Không phải tất cả phần của hệ thống đều có giá trị như nhau.

Ví dụ:

```text
Crawling
Catalog
Reading
User
Notification
```

Trong một ứng dụng đọc truyện, phần quan trọng nhất có thể là:

```text
Crawling + Reading
```

Trong khi:

```text
Notification
```

chỉ là chức năng hỗ trợ.

DDD cần chúng ta biết:

> **Nên đầu tư trí tuệ và thời gian vào đâu?**

Đây là lý do xuất hiện ba loại Subdomain:

```text
Core
Supporting
Generic
```

---

# 5. Ba loại Subdomain

DDD phân chia:

```text
                    Domain
                      │
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
      Core        Supporting      Generic
```

---

# 6. Core Subdomain

**Core Subdomain** là phần tạo ra lợi thế nghiệp vụ quan trọng nhất.

Nó trả lời:

> "Điều gì khiến hệ thống này khác biệt?"

Ví dụ ứng dụng của chúng ta có khả năng:

> Crawl truyện từ hàng trăm nguồn với plugin crawler riêng cho từng nguồn.

Nếu đây là năng lực cạnh tranh chính:

```text
Crawling
```

có thể là:

```text
Core Subdomain
```

---

# 7. Core không có nghĩa là "module quan trọng nhất về kỹ thuật"

Đây là một nhầm lẫn phổ biến.

Ví dụ:

```text
SQLite Repository
```

có thể rất quan trọng về kỹ thuật.

Nhưng nó không phải Core Subdomain.

Vì:

> SQLite không phải business capability tạo ra lợi thế cạnh tranh.

Core được xác định bằng:

```text
Business value
+
Differentiation
+
Complexity
```

chứ không phải:

```text
Code size
```

---

# 8. Supporting Subdomain

Supporting Subdomain là phần:

> Cần thiết cho business nhưng không phải lợi thế cạnh tranh chính.

Ví dụ:

```text
Catalog
```

Nếu hệ thống cần quản lý:

```text
Story
Chapter
Author
Genre
```

thì Catalog rất quan trọng.

Nhưng nếu Catalog không phải năng lực đặc biệt khiến hệ thống khác biệt:

```text
Catalog = Supporting
```

---

# 9. Generic Subdomain

Generic Subdomain là:

> Chức năng phổ biến, không tạo lợi thế cạnh tranh riêng.

Ví dụ:

```text
Notification
Authentication
Email
Logging
```

Những thứ này có thể mua, dùng thư viện hoặc sử dụng dịch vụ bên ngoài.

Ví dụ:

```text
Email
    ↓
SMTP
SendGrid
Amazon SES
```

Không cần tự xây một hệ thống email phức tạp.

---

# 10. Ví dụ hệ thống đọc truyện

Giả sử chúng ta xác định:

| Subdomain      | Loại       |
| -------------- | ---------- |
| Crawling       | Core       |
| Reading        | Core       |
| Catalog        | Supporting |
| User           | Supporting |
| Notification   | Generic    |
| Authentication | Generic    |

Có thể hình dung:

```text
                 Story Platform
                       │
       ┌───────────────┼───────────────┐
       │               │               │
      Core         Supporting        Generic
       │               │               │
 ┌─────┴─────┐    ┌────┴────┐     ┌────┴────┐
 │           │    │         │     │         │
Crawling   Reading Catalog  User Notification Auth
```

---

# 11. Core Subdomain phải được đầu tư nhiều nhất

Nếu:

```text
Crawling = Core
```

thì ta nên dành nhiều thời gian cho:

```text
Crawler architecture
Crawler plugin system
Crawler scheduling
Crawler state
Crawler failure handling
Crawler retry
Crawler source adaptation
```

Trong khi Notification:

```text
Notification = Generic
```

không cần tự phát minh:

```text
UltraAdvancedNotificationFramework
```

---

# 12. Core Complexity là "đáng giá"

Đây là một tư duy rất quan trọng.

Có những complexity:

```text
Good complexity
```

và:

```text
Bad complexity
```

Ví dụ:

```text
Crawler plugin architecture
```

phức tạp vì business thực sự phức tạp.

Đó có thể là **essential complexity**.

Nhưng:

```text
Tự viết email server
```

phức tạp vì chúng ta tự làm thứ generic.

Đó là complexity không cần thiết.

---

# 13. Một cách nhìn khác

```text
Core
  ↓
We must understand deeply.

Supporting
  ↓
We need to build adequately.

Generic
  ↓
We should reuse/buy if possible.
```

Đây là chiến lược rất quan trọng của DDD.

---

# 14. Cách xác định Subdomain

Đừng bắt đầu bằng database.

Hãy hỏi:

> Business của hệ thống có những capability nào?

Ví dụ:

```text
Hệ thống có thể:

1. Crawl nội dung
2. Quản lý truyện
3. Cho user đọc
4. Quản lý tài khoản
5. Gửi thông báo
```

Ta có:

```text
Crawling
Catalog
Reading
User
Notification
```

Sau đó mới phân loại:

```text
Core
Supporting
Generic
```

---

# 15. Business Capability

Đây là một khái niệm rất hữu ích.

Thay vì hỏi:

> "Hệ thống có những class nào?"

Hỏi:

> **"Business có khả năng làm những gì?"**

Ví dụ:

```text
Crawling
    ↓
Khả năng lấy nội dung từ nguồn bên ngoài.

Catalog
    ↓
Khả năng quản lý metadata truyện.

Reading
    ↓
Khả năng cung cấp trải nghiệm đọc.

User
    ↓
Khả năng quản lý người dùng.

Notification
    ↓
Khả năng thông báo.
```

Business capability thường giúp chúng ta tìm Subdomain.

---

# 16. Subdomain vs Feature

Hai thứ cũng dễ nhầm.

Ví dụ:

```text
Bookmark
```

có thể là một **feature**.

Nhưng:

```text
Reading
```

có thể là một **Subdomain**.

Một Subdomain có thể chứa nhiều feature:

```text
Reading
│
├── Start Reading
├── Continue Reading
├── Mark as Read
├── Bookmark
├── Reading Progress
└── Reading History
```

---

# 17. Subdomain vs Entity

Cũng đừng nhầm:

```text
Story
Chapter
User
```

là Entity.

Trong khi:

```text
Crawling
Reading
Catalog
```

là candidate Subdomain.

Ta có:

```text
Subdomain
    ↓
chứa nhiều Domain Concept
```

Ví dụ:

```text
Reading
├── ReadingSession
├── ReadingProgress
├── Bookmark
└── ReadingHistory
```

---

# 18. Một Subdomain có thể có nhiều Entity

Ví dụ:

```text
Crawling
│
├── Source
├── CrawlerJob
├── CrawlTarget
└── CrawlResult
```

Tất cả có thể thuộc cùng một Subdomain.

---

# 19. Một Entity có thể có meaning khác nhau ở các Subdomain

Ví dụ:

```text
Story
```

Trong Catalog:

```text
Story
├── title
├── author
├── genres
└── status
```

Trong Reading:

```text
Story
├── chapters
└── reading order
```

Trong Crawling:

```text
Story
├── source URL
└── crawl metadata
```

Điều này sẽ dẫn trực tiếp đến:

# Buổi 7 — Bounded Context.

---

# 20. Một Subdomain không nhất thiết = một Bounded Context

Đây là điểm nâng cao.

Ta có thể có:

```text
Subdomain
    ≠
Bounded Context
```

Subdomain là:

> **business boundary**

Bounded Context là:

> **model/language boundary**

Hai khái niệm liên quan nhưng không đồng nhất.

---

# 21. Ví dụ

Giả sử:

```text
Reading
```

là một Subdomain.

Bên trong có thể có một Bounded Context:

```text
Reading Context
```

Nhưng một Subdomain phức tạp có thể cần nhiều Context.

Ví dụ:

```text
Crawling Subdomain
│
├── Source Management Context
├── Crawl Execution Context
└── Crawl Monitoring Context
```

Tùy độ phức tạp.

---

# 22. Không chia Subdomain theo technical layer

Sai:

```text
Subdomain
├── Database
├── API
├── UI
└── Service
```

Đây là technical architecture.

DDD muốn:

```text
Subdomain
├── Crawling
├── Reading
├── Catalog
└── User
```

Đây là business architecture.

---

# 23. Không chia theo database table

Sai:

```text
Subdomain
├── stories
├── chapters
├── users
└── crawler_jobs
```

Database table không phải business boundary.

Ví dụ:

```text
stories
chapters
```

có thể cùng thuộc:

```text
Catalog
```

hoặc:

```text
Reading
```

tùy business model.

---

# 24. Core Subdomain trong hệ thống crawler của chúng ta

Hãy giả sử business differentiation là:

> Có thể crawl nhiều website truyện với kiến trúc plugin và xử lý các cấu trúc HTML khác nhau.

Khi đó:

```text
Crawling
```

có thể là Core.

Bên trong:

```text
Crawling
│
├── Source discovery
├── Crawl scheduling
├── Crawl execution
├── Plugin resolution
├── Chapter discovery
├── Content extraction
├── Retry
└── Failure handling
```

Đây là nơi cần DDD sâu.

---

# 25. Supporting: Catalog

Catalog:

```text
Story
Chapter
Author
Genre
```

cần thiết.

Nhưng nếu các quy tắc khá đơn giản:

```text
Story
    ↓
has chapters
```

thì không nhất thiết phải tạo một architecture quá phức tạp.

Đây là một nguyên tắc:

> **Đừng over-engineer Supporting Subdomain giống Core Subdomain.**

---

# 26. Generic: Notification

Ví dụ:

```text
CrawlerCompleted
       ↓
Notification
       ↓
Send notification
```

Notification có thể sử dụng:

```text
Email provider
Telegram
Web Push
Desktop notification
```

Không cần biến nó thành trọng tâm của Domain Model nếu business không cạnh tranh ở đây.

---

# 27. Generic không có nghĩa là không quan trọng

Ví dụ:

```text
Authentication
```

có thể cực kỳ quan trọng về security.

Nhưng nó vẫn có thể là Generic Subdomain.

Ta phân biệt:

```text
Important
```

với:

```text
Core competitive capability
```

Hai thứ không giống nhau.

---

# 28. Cách đầu tư khác nhau

### Core

```text
Custom design
Deep domain modeling
Rich domain model
Extensive tests
Strong architecture
```

### Supporting

```text
Good design
Moderate complexity
Enough testing
```

### Generic

```text
Reuse
Buy
Adopt existing solution
Keep simple
```

---

# 29. Ví dụ chiến lược

Giả sử team có 3 tháng.

Không nên:

```text
1 tháng → Notification framework
1 tháng → Authentication framework
1 tháng → Crawling
```

Nếu Crawling là Core.

Nên:

```text
Crawling
████████████████████

Reading
████████████

Catalog
███████

User
████

Notification
██
```

Đây chính là giá trị của Strategic DDD.

---

# 30. Một cách xác định Core rất thực tế

Hỏi 5 câu:

### 1.

> Nếu bỏ capability này, sản phẩm còn khác biệt không?

### 2.

> Competitor có dễ dàng copy nó không?

### 3.

> Business rule ở đây có phức tạp không?

### 4.

> Domain expert có nhiều knowledge đặc biệt không?

### 5.

> Đây có phải nơi công ty muốn đầu tư innovation không?

Nếu phần lớn câu trả lời là "Có":

```text
Core candidate
```

---

# 31. Ví dụ với hệ thống đọc truyện

### Crawling

```text
Có nhiều rule đặc thù?
→ Có

Khác biệt với app khác?
→ Có

Cần plugin?
→ Có

Nhiều domain knowledge?
→ Có
```

→ **Core**

---

### Catalog

```text
Quản lý title/chapter/author
→ Cần thiết

Nhưng có khác biệt lớn?
→ Không nhiều
```

→ **Supporting**

---

### Notification

```text
Gửi thông báo
→ Có

Đặc biệt?
→ Không

Có thể dùng dịch vụ ngoài?
→ Có
```

→ **Generic**

---

# 32. Một Domain có thể thay đổi classification

Điều này rất quan trọng.

Hôm nay:

```text
Reading = Supporting
```

Nhưng nếu sản phẩm phát triển thành:

> "Nền tảng đọc truyện với recommendation engine cá nhân hóa."

thì:

```text
Recommendation
```

có thể trở thành Core.

DDD không phải classification bất biến.

---

# 33. Core Subdomain có thể thay đổi theo chiến lược business

Ví dụ:

### Version 1

```text
Crawling = Core
```

### Version 2

```text
Crawling = Supporting
Recommendation = Core
```

### Version 3

```text
Reading Experience = Core
```

Do đó Strategic DDD phải gắn với:

```text
Business Strategy
```

chứ không chỉ architecture.

---

# 34. Một ví dụ khác: Amazon

Giả sử hệ thống bán hàng.

Các capability:

```text
Product Catalog
Order Management
Payment
Shipping
Recommendation
Authentication
Email
```

Không phải tất cả đều Core.

Có thể:

```text
Recommendation
Order Management
```

là Core.

Trong khi:

```text
Email
Authentication
```

có thể Generic.

Điều này giúp quyết định:

> Tự xây hay mua?

---

# 35. Core Domain ≠ Core Subdomain?

Trong tài liệu DDD, bạn có thể gặp thuật ngữ:

```text
Core Domain
```

và:

```text
Core Subdomain
```

Trong thực tế, chúng thường được dùng gần nhau khi nói về phần quan trọng nhất.

Nhưng nên hiểu rõ:

```text
Domain
    ↓
Subdomains
    ↓
Một hoặc vài Core Subdomains
```

Toàn bộ Domain không phải Core.

---

# 36. Một sai lầm lớn: "Everything is Core"

Team nói:

```text
Crawling = Core
Reading = Core
Catalog = Core
User = Core
Notification = Core
Search = Core
```

Kết quả:

> Nếu mọi thứ đều Core thì thực tế không có gì được ưu tiên.

Core phải mang tính tương đối.

Hãy hỏi:

> **Đâu là nơi tạo ra differentiation lớn nhất?**

---

# 37. Một sai lầm khác: "Generic = đơn giản"

Generic không nhất thiết dễ.

Ví dụ:

```text
Authentication
```

có thể cực kỳ phức tạp.

Nhưng nếu authentication không phải business differentiation:

```text
Generic
```

vẫn có thể đúng.

Classification nói về:

> **Business uniqueness**

không phải:

> **Technical complexity**

---

# 38. Subdomain và team

Trong hệ thống lớn, Subdomain có thể ảnh hưởng đến team boundary.

Ví dụ:

```text
Crawling Team
Catalog Team
Reading Team
User Team
```

Không phải lúc nào cũng 1:1.

Nhưng Subdomain giúp tổ chức team theo business capability thay vì:

```text
Frontend Team
Backend Team
Database Team
```

Đây là một lợi ích rất lớn khi hệ thống lớn.

---

# 39. Subdomain và Microservices

Một hiểu lầm phổ biến:

> "DDD = mỗi Subdomain một microservice."

Không đúng.

Bạn hoàn toàn có thể có:

```text
Monolith
│
├── Crawling
├── Catalog
├── Reading
└── User
```

Đây có thể là một:

> **Modular Monolith**

và vẫn là DDD.

---

# 40. Đừng tách service quá sớm

Ví dụ:

```text
Crawling Service
Catalog Service
Reading Service
User Service
Notification Service
```

nghe rất "microservice".

Nhưng nếu chúng ta chưa hiểu:

```text
Business boundary
Consistency boundary
Context boundary
```

thì việc tách service có thể tạo ra:

```text
Distributed Monolith
```

DDD phải giúp chúng ta **hiểu boundary trước**, rồi mới quyết định deployment.

---

# 41. Strategic DDD hiện tại

Sau Buổi 6:

```text
Domain
  │
  └── Subdomains
        │
        ├── Core
        ├── Supporting
        └── Generic
```

Buổi 7 sẽ thêm:

```text
Subdomain
    ↓
Bounded Context
```

Buổi 8:

```text
Bounded Context
    ↓
Context Map
    ↓
Relationships
```

Sau đó:

```text
Context Map
    ↓
Architecture
```

---

# 42. Bài tập thực hành — hệ thống đọc truyện

Hãy coi Domain là:

> **Nền tảng crawl và đọc truyện.**

Hãy xác định các Subdomain.

Gợi ý:

```text
Crawling
Catalog
Reading
User
Notification
Search
Recommendation
```

Sau đó phân loại:

```text
Core
Supporting
Generic
```

---

# 43. Bài tập nâng cao

Giả sử business nói:

> "Điểm khác biệt lớn nhất của sản phẩm là khả năng tự động phát hiện chapter mới từ nhiều nguồn truyện khác nhau."

Hãy trả lời:

### Core Subdomain là gì?

```text
?
```

### Supporting Subdomain?

```text
?
```

### Generic Subdomain?

```text
?
```

### Vì sao?

Đừng trả lời dựa trên số lượng code.

Hãy trả lời dựa trên:

```text
Business Value
Differentiation
Domain Complexity
Business Knowledge
```

---

# 44. Bài tập rất quan trọng: Context Boundary Preview

Hãy lấy `Story` và thử đặt vào:

```text
Crawling
Catalog
Reading
User
```

Sau đó viết:

### Crawling Story

```text
Story:
?
```

### Catalog Story

```text
Story:
?
```

### Reading Story

```text
Story:
?
```

### User Story

```text
Story:
?
```

Bạn sẽ bắt đầu nhận ra:

> Một từ `Story` không nhất thiết đại diện cho cùng một model.

Đây chính là bước chuẩn bị cho **Bounded Context**.

---

# 45. Tổng kết Buổi 6

Điều quan trọng nhất hôm nay:

### Domain

```text
Toàn bộ bài toán business
```

### Subdomain

```text
Một phần business capability
```

### Core

```text
Năng lực tạo lợi thế cạnh tranh
```

### Supporting

```text
Cần thiết nhưng không phải lợi thế chính
```

### Generic

```text
Phổ biến, có thể reuse/buy/adopt
```

---

## Chuỗi tư duy cần nhớ

```text
Business Problem
       ↓
Domain
       ↓
Business Capabilities
       ↓
Subdomains
       ↓
Core / Supporting / Generic
       ↓
Bounded Context
       ↓
Context Mapping
```

### Một câu cần nhớ

> **Strategic DDD không bắt đầu bằng việc hỏi "Class nào cần tạo?", mà bắt đầu bằng câu hỏi "Business của chúng ta thực sự có những năng lực nào, và năng lực nào tạo ra giá trị khác biệt?"**

**Buổi 7 — Bounded Context** sẽ đi sâu vào một trong những khái niệm quan trọng nhất của DDD:

```text
Crawling Context
        │
        ├── Story
        │
Catalog Context
        │
        ├── Story
        │
Reading Context
        │
        ├── Story
        │
User Context
        │
        └── ...
```

và chúng ta sẽ giải quyết câu hỏi: **Tại sao `Story` trong Crawling có thể hoàn toàn khác `Story` trong Reading, dù cùng mang một cái tên?**
