# Domain-Driven Design Deep Dive — Buổi 2

## Domain Discovery — Tìm và phân loại Subdomain

Buổi 1 chúng ta đã có một nguyên tắc:

> **DDD bắt đầu từ business, không bắt đầu từ database, framework hay class.**

Buổi 2 là bước đầu tiên để biến một hệ thống lớn thành **những vùng nghiệp vụ có ranh giới rõ ràng**.

Case study xuyên suốt vẫn là:

> **Ứng dụng cào truyện + lưu trữ + đọc truyện + crawler worker**

---

# 1. Domain Discovery là gì?

**Domain Discovery** là quá trình tìm hiểu:

```text
Business đang làm gì?
       ↓
Có những khái niệm nào?
       ↓
Có những hoạt động nào?
       ↓
Có những quy tắc nào?
       ↓
Có những vùng nghiệp vụ nào?
```

Kết quả cuối cùng là chúng ta tìm được:

```text
Domain
 ├── Subdomain A
 ├── Subdomain B
 ├── Subdomain C
 └── ...
```

Đây là bước thuộc **Strategic DDD**.

---

# 2. Tại sao không xây cả hệ thống thành một Domain duy nhất?

Giả sử app của bạn có:

```text
Story
Chapter
Crawler
User
Reading
Bookmark
Search
Notification
```

Nếu tất cả nằm trong một model lớn:

```text
Application
   |
   +-- Story
   +-- Chapter
   +-- Crawler
   +-- User
   +-- Reading
   +-- Search
   +-- Notification
```

sẽ rất nhanh trở nên khó quản lý.

Vấn đề là:

> Những khái niệm này không có cùng mức độ quan trọng và không phục vụ cùng một business purpose.

Ví dụ:

**Crawler** quan tâm:

```text
URL
HTTP
Parser
Pagination
Retry
Rate limit
```

Trong khi **Reading** quan tâm:

```text
Current chapter
Reading position
Bookmark
Reading history
```

Hai vùng này có logic hoàn toàn khác nhau.

---

# 3. Subdomain là gì?

**Subdomain** là một vùng chức năng/nghiệp vụ tương đối độc lập bên trong domain lớn.

Ví dụ domain:

```text
Online Book Platform
```

có thể có:

```text
Catalog
Reading
User
Search
Recommendation
Payment
```

Mỗi vùng có:

* terminology riêng
* business rules riêng
* model riêng
* mức độ quan trọng khác nhau

---

# 4. Ba loại Subdomain

DDD thường phân loại thành:

```text
Core Subdomain
Supporting Subdomain
Generic Subdomain
```

Đây là một trong những kiến thức quan trọng nhất của Strategic DDD.

---

# 5. Core Subdomain

**Core Domain/Subdomain** là phần tạo ra **lợi thế cạnh tranh chính** của hệ thống.

Nói đơn giản:

> Đây là thứ mà nếu bỏ đi thì sản phẩm mất phần quan trọng nhất.

Ví dụ:

### Netflix

Có thể Core Domain liên quan đến:

```text
Content recommendation
Personalization
Streaming experience
```

### Shopee

Có thể Core Domain liên quan đến:

```text
Marketplace
Matching buyer/seller
Commerce optimization
```

### Google Search

Core Domain:

```text
Search / Ranking
```

---

# 6. Core Domain của ứng dụng cào truyện là gì?

Đây là câu hỏi **không có một đáp án tuyệt đối**.

Nếu mục tiêu của app là:

> Cào truyện từ nhiều website và tự động cập nhật chapter.

thì Core Domain có thể là:

```text
Crawler Orchestration
```

hoặc:

```text
Content Acquisition
```

Nếu mục tiêu là:

> Xây ứng dụng đọc truyện có trải nghiệm đọc tốt.

Core Domain có thể là:

```text
Reading Experience
```

Nếu mục tiêu là:

> Xây hệ thống quản lý kho truyện.

Core Domain có thể là:

```text
Story Catalog
```

**DDD luôn phụ thuộc business goal.**

---

# 7. Supporting Subdomain

Supporting Subdomain là những phần:

> Quan trọng đối với hệ thống nhưng không phải lợi thế cạnh tranh chính.

Ví dụ app của chúng ta có thể có:

```text
Catalog Management
Crawler Management
Reading Progress
Bookmark
User Management
```

Giả sử Core Domain là crawler.

Khi đó:

```text
Crawler
   ↓
Core

Catalog
   ↓
Supporting

Reading
   ↓
Supporting

Bookmark
   ↓
Supporting
```

---

# 8. Generic Subdomain

Generic Subdomain là những thứ:

> Cần thiết nhưng không có giá trị cạnh tranh đặc biệt.

Ví dụ:

```text
Authentication
Authorization
Email
Logging
Monitoring
```

Bạn có thể:

* mua
* dùng thư viện
* dùng SaaS
* dùng framework

thay vì tự xây toàn bộ.

Ví dụ:

```text
JWT authentication
OAuth
Email service
```

Không nhất thiết phải tự phát minh.

---

# 9. Một sai lầm rất phổ biến

Nhiều developer nghĩ:

> "Phần nào code khó nhất thì là Core Domain."

Không đúng.

Core Domain không phải:

```text
Code khó nhất
```

mà là:

```text
Business value cao nhất
+
Competitive differentiation cao nhất
```

Ví dụ authentication có thể code rất phức tạp.

Nhưng:

> Authentication chưa chắc là Core Domain.

---

# 10. Phân tích ứng dụng cào truyện

Hãy tưởng tượng product requirement:

> Hệ thống tự động crawl hàng trăm website truyện, phát hiện chapter mới, chuẩn hóa dữ liệu, lưu trữ và cung cấp cho người dùng đọc.

Ta bắt đầu liệt kê:

```text
Story
Chapter
Author
Source
Crawler
CrawlerJob
Parser
User
ReadingProgress
Bookmark
Search
Notification
```

Nhưng chưa được phân loại ngay.

Ta hỏi:

> Chúng đang phục vụ business capability nào?

---

# 11. Nhóm thứ nhất — Content Acquisition

```text
Source
Crawler
CrawlerJob
Parser
Fetcher
ChapterDiscovery
```

Mục đích:

```text
Website
   ↓
Fetch
   ↓
Parse
   ↓
Discover
   ↓
Normalize
   ↓
Chapter
```

Đây là một vùng nghiệp vụ rõ ràng.

Ta gọi tạm:

```text
Content Acquisition
```

---

# 12. Nhóm thứ hai — Catalog

```text
Story
Chapter
Author
Genre
Metadata
```

Mục đích:

> Quản lý nội dung truyện đã được thu thập.

Ví dụ:

```text
Story
 ├── title
 ├── author
 ├── description
 ├── status
 └── chapters
```

Đây là:

```text
Catalog
```

---

# 13. Nhóm thứ ba — Reading

```text
ReadingProgress
ReadingSession
Bookmark
History
```

Mục đích:

> Cho phép user đọc và tiếp tục đọc.

Ví dụ:

```text
User
   ↓
Open Story
   ↓
Open Chapter
   ↓
Read
   ↓
Update Progress
```

Đây là:

```text
Reading
```

---

# 14. Nhóm thứ tư — User

```text
User
Account
Permission
Preference
```

Mục đích:

```text
Authentication
Authorization
Profile
```

Đây là một subdomain khác.

---

# 15. Nhóm thứ năm — Search

Ví dụ:

```text
SearchStory
SearchChapter
SearchAuthor
SearchGenre
```

Nếu hệ thống có search nâng cao:

```text
full-text search
ranking
relevance
filtering
```

thì Search có thể trở thành một subdomain riêng.

---

# 16. Ta bắt đầu có Domain Map

Một phiên bản đầu tiên:

```text
                    Story Platform
                          |
       +------------------+------------------+
       |                  |                  |
       ↓                  ↓                  ↓
   Acquisition         Catalog            Reading
       |                  |                  |
   Crawler              Story          ReadingProgress
   Parser               Chapter        Bookmark
   Source               Author         History
       |
       ↓
    Search

                    +
                   User
```

Đây **chưa phải Bounded Context**.

Rất quan trọng.

Hiện tại chúng ta mới đang phân tích **Subdomain**.

---

# 17. Subdomain và Bounded Context không giống nhau

Đây là một điểm rất nhiều người mới học DDD nhầm.

### Subdomain

Là:

> **business boundary**

### Bounded Context

Là:

> **model boundary**

Nói đơn giản:

```text
Subdomain
=
Business problem boundary
```

còn:

```text
Bounded Context
=
Model / language / implementation boundary
```

Chúng thường liên quan chặt chẽ nhưng không bắt buộc 1-1.

---

# 18. Ví dụ về sự khác biệt

Ta có:

```text
Catalog
```

Trong Catalog:

```text
Story
Chapter
```

Nhưng Reading cũng có:

```text
Story
Chapter
```

Có vẻ giống nhau.

Nhưng ý nghĩa khác nhau.

### Catalog

Quan tâm:

```text
Story metadata
Chapter metadata
Publication status
```

### Reading

Quan tâm:

```text
Current chapter
Reading position
Navigation
Progress
```

Cùng từ:

```text
Chapter
```

nhưng có thể có **hai model khác nhau**.

Đây chính là tiền đề cho Bounded Context.

---

# 19. Core Domain cần được bảo vệ

Giả sử:

```text
Crawler = Core
```

thì đội ngũ nên dành nhiều effort cho:

```text
Crawler Domain
```

Ví dụ:

```text
Crawler scheduling
Retry strategy
Source adaptation
Chapter discovery
Duplicate detection
Crawler state
```

Trong khi:

```text
Authentication
```

có thể dùng giải pháp có sẵn.

Điều này giúp tránh lãng phí nguồn lực.

---

# 20. DDD không có nghĩa "mọi Subdomain đều phải tự code"

Đây là nguyên tắc rất thực tế.

Giả sử:

```text
Authentication = Generic
```

Ta có thể dùng:

```text
OAuth
OIDC
JWT
Auth provider
```

Không cần xây:

```text
MyOwnAuthenticationFramework
```

Ngược lại nếu:

```text
Crawler = Core
```

thì không nên phụ thuộc hoàn toàn vào một crawler framework khiến business model bị khóa chặt vào framework đó.

---

# 21. Core Domain và "moat"

Một cách nghĩ rất hữu ích:

> Core Domain chính là phần bạn muốn công ty/sản phẩm giỏi hơn đối thủ.

Ví dụ nếu app của bạn có khả năng:

```text
phát hiện chapter mới cực nhanh
+
crawl ổn định
+
tự thích ứng website
+
retry thông minh
+
không duplicate
```

thì đó chính là giá trị.

Bạn nên đầu tư vào:

```text
Domain Model
Tests
Algorithms
Business Rules
Architecture
```

chứ không chỉ đầu tư vào UI.

---

# 22. Domain Discovery bằng Event Storming

Một kỹ thuật rất mạnh để tìm Subdomain là:

> **Event Storming**

Thay vì hỏi:

> "Database có những bảng nào?"

Ta hỏi:

> "Trong business đã xảy ra những sự kiện gì?"

Ví dụ crawler:

```text
SourceRegistered
CrawlerStarted
PageFetched
PageParsed
StoryDiscovered
ChapterDiscovered
ChapterDownloaded
ChapterSaved
CrawlerCompleted
CrawlerFailed
```

Nhìn vào các event này ta bắt đầu thấy:

```text
Crawler
Content Acquisition
Catalog
```

---

# 23. Từ Event tìm Command

Event:

```text
CrawlerStarted
```

Command có thể là:

```text
StartCrawler
```

Event:

```text
ChapterDiscovered
```

Command:

```text
DiscoverChapter
```

Event:

```text
ChapterSaved
```

Command:

```text
SaveChapter
```

Ta có:

```text
Command
   ↓
Business behavior
   ↓
Event
```

Phần này chúng ta sẽ học sâu ở các buổi sau.

---

# 24. Từ Event tìm Actor

Ví dụ:

```text
UserStartedReading
```

Actor:

```text
User
```

Nhưng:

```text
ChapterDiscovered
```

Actor có thể là:

```text
Crawler
```

hoặc:

```text
Crawler Worker
```

Còn:

```text
CrawlerPaused
```

có thể do:

```text
Admin
```

Như vậy Event Storming giúp chúng ta nhìn domain từ **behavior**, chứ không chỉ từ data.

---

# 25. Một ví dụ Event Storming nhỏ

```text
Admin
  |
  | StartCrawler
  ↓
CrawlerStarted
  |
  ↓
PageFetched
  |
  ↓
PageParsed
  |
  ↓
ChapterDiscovered
  |
  ↓
ChapterDownloaded
  |
  ↓
ChapterSaved
  |
  ↓
CrawlerCompleted
```

Từ flow này, ta bắt đầu nhìn thấy:

```text
Crawler
    ↓
Acquisition
    ↓
Catalog
```

---

# 26. Domain Discovery không phải một lần là xong

Đây là điều rất quan trọng.

Lúc đầu:

```text
Crawler
Catalog
Reading
User
```

Sau khi hiểu sâu hơn, có thể phát hiện:

```text
Crawler
 ├── Scheduling
 ├── Fetching
 ├── Parsing
 ├── Discovery
 └── Normalization
```

Lúc đó ta có thể quyết định:

> Có nên tách chúng thành subdomain riêng không?

Câu trả lời phụ thuộc business.

**Không tách chỉ vì code nhiều.**

---

# 27. Khi nào nên tách Subdomain?

Hãy xem xét các câu hỏi:

### 1. Có business purpose riêng không?

Nếu có → có khả năng là subdomain.

### 2. Có business rules riêng không?

Nếu có → dấu hiệu mạnh.

### 3. Có terminology riêng không?

Nếu có → dấu hiệu mạnh.

### 4. Có thể phát triển tương đối độc lập không?

Nếu có → càng đáng tách.

### 5. Có giá trị business riêng không?

Nếu có → rất đáng xem xét.

---

# 28. Đừng tách theo database table

Đây là anti-pattern.

Sai:

```text
stories table
    ↓
StorySubdomain

chapters table
    ↓
ChapterSubdomain

users table
    ↓
UserSubdomain
```

Database table không quyết định Subdomain.

Đúng hơn:

```text
Business capability
       ↓
Subdomain
       ↓
Domain model
       ↓
Persistence model
```

---

# 29. Ví dụ thực tế

Giả sử:

```text
Story
Chapter
```

cùng nằm trong một table relationship.

Không có nghĩa:

```text
Story = một Subdomain
Chapter = một Subdomain
```

Có thể cả hai thuộc:

```text
Catalog Subdomain
```

hoặc thậm chí:

```text
Catalog
```

và:

```text
Reading
```

cùng có concept `Chapter` nhưng với model khác nhau.

---

# 30. Strategic DDD bắt đầu từ Business Capability

Một cách tiếp cận rất tốt:

Thay vì:

```text
"Ứng dụng có những entity nào?"
```

hãy hỏi:

```text
"Hệ thống có những business capabilities nào?"
```

Ví dụ:

```text
Acquire content
Manage catalog
Provide reading
Manage users
Search content
Notify users
```

Sau đó mới tìm:

```text
Subdomain
```

---

# 31. Phân loại thử cho project của chúng ta

Giả sử business goal:

> Xây hệ thống tự động thu thập truyện từ nhiều nguồn và cung cấp nội dung ổn định cho người đọc.

Một cách phân loại **giả định**:

| Subdomain             | Loại       |
| --------------------- | ---------- |
| Content Acquisition   | **Core**   |
| Crawler Orchestration | **Core**   |
| Catalog               | Supporting |
| Reading               | Supporting |
| Search                | Supporting |
| User Management       | Generic    |
| Authentication        | Generic    |
| Notification          | Generic    |

Nhưng nếu business goal thay đổi:

> Xây app đọc truyện có trải nghiệm đọc tốt nhất.

thì:

| Subdomain          | Loại       |
| ------------------ | ---------- |
| Reading Experience | **Core**   |
| Catalog            | Supporting |
| Acquisition        | Supporting |
| Search             | Supporting |
| Authentication     | Generic    |

**Không có bảng phân loại cố định cho mọi sản phẩm.**

---

# 32. Đây là lý do DDD bắt đầu bằng business

Nếu bạn chỉ nhìn code:

```text
crawler/
story/
chapter/
user/
```

bạn không biết cái nào quan trọng nhất.

Nhưng nếu hiểu business:

```text
"Chúng ta kiếm giá trị bằng cách nào?"
```

thì mới xác định được:

```text
Core Domain
```

---

# 33. Một quy trình Domain Discovery thực tế

Khi bắt đầu project thật, bạn có thể làm:

```text
Bước 1
↓
Xác định business goal

Bước 2
↓
Liệt kê business capability

Bước 3
↓
Event Storming

Bước 4
↓
Tìm business rules

Bước 5
↓
Nhóm các capability

Bước 6
↓
Xác định Subdomain

Bước 7
↓
Phân loại Core / Supporting / Generic

Bước 8
↓
Tiếp tục tìm Bounded Context
```

---

# 34. Bài tập Buổi 2

Hãy làm bài tập trên chính project của bạn.

## Bài 1 — Business Goal

Viết 1 đoạn ngắn:

> Ứng dụng cào và đọc truyện này tồn tại để làm gì?

Đừng viết:

```text
Python app dùng SQLite.
```

Hãy viết theo business.

Ví dụ:

```text
Hệ thống tự động thu thập nội dung truyện từ nhiều nguồn,
chuẩn hóa nội dung và cung cấp trải nghiệm đọc liên tục.
```

---

## Bài 2 — Business Capabilities

Tìm khoảng **8–12 capabilities**.

Ví dụ:

```text
1. Register source
2. Crawl source
3. Discover story
4. Discover chapter
5. Normalize content
6. Manage catalog
7. Read story
8. Track reading progress
9. Search story
10. Bookmark story
```

---

## Bài 3 — Phân loại Subdomain

Tự phân loại:

```text
Core
Supporting
Generic
```

Ví dụ:

```text
Core:
    ...

Supporting:
    ...

Generic:
    ...
```

---

## Bài 4 — Event Storming

Hãy liệt kê khoảng **15 Domain Events** của crawler.

Ví dụ:

```text
SourceRegistered
CrawlerStarted
PageFetched
...
```

Không cần code.

---

## Bài 5 — Tìm business rule

Viết ít nhất 10 rule.

Ví dụ:

```text
- Không thể start crawler đang Running.
- Không thể resume crawler chưa Paused.
- Chapter number phải > 0.
- Không được duplicate chapter.
```

---

# 35. Kiến thức cần nhớ sau Buổi 2

```text
Domain
   ↓
Business capability
   ↓
Subdomain
   ↓
Core / Supporting / Generic
```

Và đặc biệt:

> **Core Domain không phải phần code khó nhất. Nó là phần tạo ra giá trị/lợi thế cạnh tranh quan trọng nhất của business.**

Buổi 3 chúng ta sẽ đi vào **Ubiquitous Language** — một trong những khái niệm nền tảng nhất của DDD: cách biến ngôn ngữ của business thành **ngôn ngữ thống nhất trong code**, và vì sao `Story`, `Chapter`, `Source`, `CrawlerJob` phải có **meaning rõ ràng**, thay vì chỉ là những class chứa dữ liệu.
