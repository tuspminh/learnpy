# Domain-Driven Design Deep Dive

# Buổi 3: Domain, Subdomain, Core Domain

Đây là một trong những buổi quan trọng nhất của DDD.

Sau buổi này bạn sẽ hiểu:

  * Tại sao hai công ty cùng bán hàng nhưng thiết kế phần mềm hoàn toàn khác nhau. 
  * Vì sao không nên dành quá nhiều thời gian viết module Login. 
  * Phần nào của hệ thống đáng để đầu tư kiến trúc DDD. 
  * Cách chia Domain cho một hệ thống lớn. 



* * *

# Roadmap

✅ Buổi 1: DDD là gì

✅ Buổi 2: Ubiquitous Language

✅ **Buổi 3: Domain & Subdomain**

⬜ Buổi 4: Bounded Context

⬜ Buổi 5: Context Mapping

...

* * *

# 1\. Domain là gì?

Buổi trước ta đã nói:

Domain là

> Lĩnh vực nghiệp vụ.

Ví dụ

Ngân hàng
    
    
    Banking

Shopee
    
    
    E-commerce

Bệnh viện
    
    
    Healthcare

Ứng dụng đọc truyện
    
    
    Novel Platform

* * *

Nhưng...

Một Domain rất lớn.

Ví dụ Shopee
    
    
    Shopee

không chỉ có
    
    
    Order

mà còn
    
    
    Payment
    
    Voucher
    
    Shipping
    
    Search
    
    Review
    
    Chat
    
    Recommendation
    
    Notification
    
    Inventory

Nếu tất cả nằm trong một module
    
    
    src/
    
        order.py
    
        payment.py
    
        shipping.py
    
        search.py
    
        review.py
    
        notification.py
    
        ....

thì vài năm sau

mọi thứ sẽ rối tung.

* * *

# 2\. DDD giải quyết như thế nào?

DDD chia Domain thành
    
    
    Domain
    
    ↓
    
    Subdomain
    
    ↓
    
    Model

Giống như
    
    
    Quốc gia
    
    ↓
    
    Tỉnh
    
    ↓
    
    Huyện

* * *

Ví dụ
    
    
    E-commerce

chia thành
    
    
    Order
    
    Payment
    
    Shipping
    
    Review
    
    Recommendation
    
    Inventory

Mỗi phần là một

Subdomain.

* * *

# 3\. Ví dụ App Cào Truyện

Giả sử chúng ta xây
    
    
    Novel Platform

Domain chính

Bên trong có
    
    
    Crawler
    
    Reader
    
    Bookmark
    
    Authentication
    
    Search
    
    Recommendation
    
    Statistics
    
    Notification
    
    Sync
    
    User
    
    Library

Đây là các

Subdomain.

* * *

# 4\. Ví dụ thư mục
    
    
    src/
    
        crawler/
    
        reader/
    
        bookmark/
    
        user/
    
        notification/
    
        search/
    
        statistics/
    
        recommendation/

Đây không phải chia theo

MVC.

Đây là chia theo

Business.

Đó chính là DDD.

* * *

# 5\. Vì sao phải chia?

Ví dụ

Có

100 lập trình viên.

Nếu mọi người cùng sửa
    
    
    models.py

thì

Git conflict mỗi ngày.

Nếu chia
    
    
    Crawler Team
    
    Search Team
    
    Reader Team
    
    Recommendation Team

thì

mọi người làm độc lập.

* * *

# 6\. Không phải Subdomain nào cũng quan trọng

Đây là điểm đặc biệt của DDD.

Eric Evans nói

Không phải mọi module đều đáng đầu tư như nhau.

DDD chia thành
    
    
    Core Domain
    
    Supporting Subdomain
    
    Generic Subdomain

* * *

# 7\. Core Domain

Đây là

**linh hồn của công ty.**

Nếu bỏ Core Domain

công ty mất lợi thế cạnh tranh.

* * *

Ví dụ Netflix

Core Domain là
    
    
    Recommendation

không phải
    
    
    Login

* * *

Google

Core Domain
    
    
    Search Ranking

không phải
    
    
    User Profile

* * *

Shopee

Core Domain
    
    
    Order Matching
    
    Recommendation
    
    Promotion

không phải
    
    
    Login

* * *

# 8\. App Cào Truyện

Core Domain là gì?

Có thể là
    
    
    Crawler

vì đây là nơi

thu thập dữ liệu.

Hoặc
    
    
    Recommendation

nếu mục tiêu là đề xuất truyện.

Hoặc
    
    
    Reading Experience

nếu muốn cạnh tranh bằng trải nghiệm đọc.

* * *

Ví dụ
    
    
    Novel Platform
    
    ↓
    
    Crawler

Crawler quyết định

  * Crawl nhanh 
  * Crawl đúng 
  * Không bị chặn 
  * Plugin dễ mở rộng 



Đây là lợi thế cạnh tranh.

=> Core Domain.

* * *

# 9\. Supporting Subdomain

Là phần

hỗ trợ

Core Domain.

Ví dụ
    
    
    Bookmark
    
    Reading History
    
    Favorite
    
    Library

Chúng quan trọng.

Nhưng

không tạo nên sự khác biệt lớn.

* * *

Ví dụ
    
    
    Reading History

Ai cũng làm được.

Không cần thuật toán quá phức tạp.

* * *

# 10\. Generic Subdomain

Là phần

ai cũng giống nhau.

Ví dụ
    
    
    Login
    
    Register
    
    Permission
    
    Role
    
    Email
    
    SMS
    
    Logging
    
    Configuration

Đây không phải

bí quyết kinh doanh.

Có thể dùng thư viện có sẵn.

* * *

Ví dụ
    
    
    JWT Login

Đừng mất

3 tháng

để tự viết.

* * *

# 11\. Ví dụ thực tế

Một website bán hàng
    
    
    Order
    
    Inventory
    
    Shipping
    
    Recommendation
    
    Payment
    
    Login
    
    Notification

Ta phân loại

Core
    
    
    Recommendation
    
    Promotion

Supporting
    
    
    Order
    
    Inventory
    
    Shipping

Generic
    
    
    Login
    
    Email
    
    Logging
    
    Cache

* * *

# 12\. Tại sao quan trọng?

Ví dụ

Có

1000 giờ phát triển.

DDD nói
    
    
    700 giờ
    
    ↓
    
    Core Domain
    
    
    200 giờ
    
    ↓
    
    Supporting
    
    
    100 giờ
    
    ↓
    
    Generic

Đừng dành phần lớn thời gian cho những thứ không tạo ra giá trị khác biệt.

* * *

# 13\. Ví dụ App Cào Truyện
    
    
    Novel Platform
    
    │
    
    ├── crawler
    
    ├── parser
    
    ├── search
    
    ├── recommendation
    
    ├── reader
    
    ├── bookmark
    
    ├── user
    
    ├── login
    
    ├── notification
    
    ├── statistics

Có thể phân loại

### Core
    
    
    crawler
    
    parser
    
    recommendation

* * *

Supporting
    
    
    reader
    
    bookmark
    
    statistics
    
    library

* * *

Generic
    
    
    login
    
    jwt
    
    email
    
    config
    
    logging
    
    cache

* * *

# 14\. Một sai lầm phổ biến

Nhiều người

đầu tư rất nhiều vào
    
    
    Permission
    
    User
    
    JWT
    
    Authentication

trong khi

Core Domain

lại viết rất sơ sài.

Kết quả
    
    
    Đăng nhập rất đẹp
    
    ↓
    
    Nhưng nghiệp vụ chính rất yếu.

DDD nhắc chúng ta rằng **công sức nên tập trung vào nơi tạo ra giá trị kinh doanh**.

* * *

# 15\. Kết hợp với Clean Architecture

Bạn đã học
    
    
    Presentation
    
    ↓
    
    Application
    
    ↓
    
    Domain
    
    ↓
    
    Infrastructure

DDD bổ sung thêm
    
    
    Domain
    
    ├── Crawler
    
    ├── Search
    
    ├── Reader
    
    ├── Recommendation
    
    ├── Bookmark

Mỗi Subdomain

có
    
    
    Entity
    
    Repository
    
    Service
    
    Value Object
    
    Event

riêng.

Ví dụ
    
    
    crawler/
    
        entities/
    
        repositories/
    
        services/
    
        events/

và
    
    
    reader/
    
        entities/
    
        repositories/
    
        services/

Điều này giúp mỗi Subdomain có mô hình riêng, tránh phụ thuộc lẫn nhau.

* * *

# 16\. Thiết kế cho dự án App Cào Truyện

Dựa trên các cuộc trao đổi trước đây về dự án của bạn (ứng dụng cào, quản lý và đọc truyện với plugin nguồn, SQLite và giao diện PySide6), một cách phân chia hợp lý có thể là:
    
    
    Core Domain

  * Source Management 
  * Crawling Engine 
  * Parser 
  * Novel Synchronization 


    
    
    Supporting Subdomain

  * Reader 
  * Bookmark 
  * Reading History 
  * Library 
  * Search 


    
    
    Generic Subdomain

  * Authentication 
  * Logging 
  * Configuration 
  * Scheduler 
  * Cache 



Lưu ý rằng đây là một gợi ý. Nếu sau này sản phẩm của bạn cạnh tranh bằng công cụ tìm kiếm hoặc hệ thống gợi ý truyện, thì `Search` hoặc `Recommendation` hoàn toàn có thể trở thành **Core Domain**.

* * *

# 17\. Best Practices

✅ Hỏi trước:

> "Điều gì tạo nên lợi thế cạnh tranh của sản phẩm?"

Đó thường là Core Domain.

* * *

✅ Đừng tự viết lại Generic Subdomain nếu đã có giải pháp tốt.

Ví dụ:

  * JWT 
  * OAuth 
  * Logging 
  * SMTP 
  * Redis Cache 



* * *

✅ Tổ chức mã nguồn theo Subdomain thay vì theo công nghệ khi dự án đủ lớn.

Thay vì:
    
    
    models/
    repositories/
    services/

hãy cân nhắc:
    
    
    crawler/
    reader/
    search/
    bookmark/

Trong mỗi Subdomain mới chia tiếp thành Entity, Repository, Service,...

* * *

# Bài tập

## Bài 1

Với ứng dụng cào truyện, hãy liệt kê khoảng **15 Subdomain** mà bạn nghĩ cần có.

* * *

## Bài 2

Phân loại từng Subdomain vào một trong ba nhóm:

  * Core Domain 
  * Supporting Subdomain 
  * Generic Subdomain 



và giải thích ngắn gọn vì sao.

* * *

## Bài 3

Thiết kế cây thư mục cho dự án theo Subdomain, ví dụ:
    
    
    src/
        crawler/
        parser/
        reader/
        bookmark/
        search/
        ...

Sau đó, với **mỗi Subdomain** , hãy thử xác định:

  * Entity 
  * Repository 
  * Domain Service 
  * Domain Event 



* * *

# Tổng kết

Đến cuối buổi này, bạn nên nắm được:

  * **Domain** là toàn bộ lĩnh vực nghiệp vụ của hệ thống. 
  * **Subdomain** là cách chia nhỏ Domain thành các khu vực nghiệp vụ độc lập. 
  * Không phải Subdomain nào cũng quan trọng như nhau. 
  * **Core Domain** là nơi tạo ra lợi thế cạnh tranh và xứng đáng nhận phần lớn công sức thiết kế. 
  * **Supporting Subdomain** hỗ trợ Core Domain nhưng không phải yếu tố khác biệt. 
  * **Generic Subdomain** là những phần phổ biến, nên ưu tiên tái sử dụng thư viện hoặc giải pháp có sẵn. 



Ở **Buổi 4** , chúng ta sẽ học **Bounded Context** — khái niệm được nhiều người xem là "trái tim" của kiến trúc DDD, nơi bạn sẽ hiểu vì sao cùng một khái niệm như `User`, `Novel` hay `Order` có thể mang ý nghĩa khác nhau ở các phần khác nhau của cùng một hệ thống.

