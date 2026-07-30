# Khóa học urllib Deep Dive

# Buổi 16: `urllib.robotparser` Deep Dive – Xây dựng Web Scraper lịch sự và chuyên nghiệp

> Nếu bạn định viết Web Scraper, Search Engine hoặc Crawler thì **`urllib.robotparser`** là module không thể bỏ qua.

Nhiều người chỉ biết dùng:
    
    
    urlopen(...)

để tải HTML.

Nhưng crawler chuyên nghiệp luôn làm thêm một bước:
    
    
    robots.txt
    
    ↓
    
    Được phép crawl?
    
    ↓
    
    YES
    
    ↓
    
    Download

Đó chính là nhiệm vụ của `urllib.robotparser`.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu robots.txt là gì. 
  * Hiểu Robot Exclusion Protocol. 
  * Biết cách sử dụng `RobotFileParser`. 
  * Kiểm tra URL có được crawl hay không. 
  * Đọc Crawl-delay. 
  * Đọc Request-rate. 
  * Đọc Sitemap. 
  * Thiết kế `RobotsPolicy` cho Scraper Framework. 



* * *

# 1\. robots.txt là gì?

Một website thường có:
    
    
    https://example.com/robots.txt

Ví dụ:
    
    
    User-agent: *
    
    Disallow: /admin/
    
    Disallow: /private/
    
    Allow: /

Crawler sẽ đọc file này trước khi thu thập dữ liệu.

* * *

# 2\. robots.txt nằm ở đâu?

Luôn ở:
    
    
    https://domain.com/robots.txt

Ví dụ:
    
    
    https://python.org/robots.txt

Không phải:
    
    
    /blog/robots.txt

* * *

# 3\. Robot Exclusion Protocol

Là giao thức quy ước giữa:
    
    
    Website
    
    ↓
    
    Crawler

Website **không bắt buộc** crawler phải tuân theo, nhưng các crawler "lịch sự" sẽ làm vậy.

* * *

# 4\. User-agent

Ví dụ:
    
    
    User-agent: Googlebot

Hoặc
    
    
    User-agent: Bingbot

Hoặc
    
    
    User-agent: *

Dấu `*` nghĩa là áp dụng cho mọi crawler.

* * *

# 5\. Disallow

Ví dụ:
    
    
    Disallow: /admin

↓

Crawler:
    
    
    Không được crawl

* * *

# 6\. Allow

Ví dụ:
    
    
    Disallow: /images
    
    Allow: /images/public

↓
    
    
    /images
    
    ✗

↓
    
    
    /images/public
    
    ✓

* * *

# 7\. Crawl-delay

Ví dụ:
    
    
    Crawl-delay: 5

↓

Crawler:
    
    
    Mỗi request cách nhau
    
    5 giây

Không phải mọi website đều khai báo chỉ thị này.

* * *

# 8\. Request-rate

Ví dụ:
    
    
    Request-rate: 10/60

↓
    
    
    10 request
    
    ↓
    
    60 giây

Đây là chỉ thị ít phổ biến hơn `Crawl-delay`.

* * *

# 9\. Sitemap

Ví dụ:
    
    
    Sitemap:
    https://example.com/sitemap.xml

Crawler có thể lấy toàn bộ URL từ đây thay vì phải tự khám phá.

* * *

# 10\. Import
    
    
    from urllib.robotparser import RobotFileParser

* * *

# 11\. Tạo RobotFileParser
    
    
    from urllib.robotparser import RobotFileParser
    
    rp = RobotFileParser()

* * *

# 12\. set_url()
    
    
    rp.set_url(
        "https://example.com/robots.txt"
    )

* * *

# 13\. read()
    
    
    rp.read()

`RobotFileParser` sẽ tải và phân tích nội dung `robots.txt`.

* * *

# 14\. can_fetch()

Quan trọng nhất.
    
    
    rp.can_fetch(
        "*",
        "https://example.com/admin"
    )

↓
    
    
    False

* * *

# 15\. Ví dụ
    
    
    from urllib.robotparser import RobotFileParser
    
    rp = RobotFileParser()
    
    rp.set_url(
        "https://example.com/robots.txt"
    )
    
    rp.read()
    
    print(
        rp.can_fetch(
            "*",
            "https://example.com/"
        )
    )

* * *

# 16\. User-agent cụ thể
    
    
    rp.can_fetch(
    
        "Googlebot",
    
        url
    )

↓

Kiểm tra rule dành riêng cho Googlebot.

* * *

# 17\. Crawl Delay
    
    
    delay = rp.crawl_delay("*")

Ví dụ:
    
    
    print(delay)

↓
    
    
    5

Nếu không có chỉ thị, kết quả thường là `None`.

* * *

# 18\. Request Rate
    
    
    rate = rp.request_rate("*")

↓

Ví dụ:
    
    
    RequestRate(
        requests=10,
    
        seconds=60
    )

Có thể truy cập:
    
    
    print(rate.requests)
    print(rate.seconds)

* * *

# 19\. SiteMap
    
    
    rp.site_maps()

↓
    
    
    [
        "https://..."
    ]

Nếu robots.txt không khai báo sitemap, kết quả là `None`.

* * *

# 20\. modified()
    
    
    rp.modified()

Thông báo parser rằng robots.txt vừa được cập nhật.

Thường dùng khi bạn tự tải nội dung robots.txt thay vì gọi `read()`.

* * *

# 21\. mtime()
    
    
    rp.mtime()

↓
    
    
    Unix Timestamp

Cho biết thời điểm robots.txt được đọc lần cuối.

* * *

# 22\. Kiến trúc
    
    
    Crawler
    
    ↓
    
    robots.txt
    
    ↓
    
    RobotFileParser
    
    ↓
    
    Allowed?
    
    ↓
    
    Download

* * *

# 23\. RobotsPolicy

Thay vì:
    
    
    rp.can_fetch(...)

khắp nơi.

Ta tạo:
    
    
    class RobotsPolicy:
        ...

* * *

# 24\. Interface
    
    
    class RobotsPolicy:
    
        def allowed(
            self,
            url
        ):
            ...

Bên trong sử dụng:
    
    
    RobotFileParser

* * *

# 25\. Tích hợp Scraper
    
    
    Scraper
    
    ↓
    
    RobotsPolicy
    
    ↓
    
    HttpClient
    
    ↓
    
    urllib

Điều này giúp Scraper không phụ thuộc trực tiếp vào `RobotFileParser`.

* * *

# 26\. Cache robots.txt

Sai:
    
    
    Mỗi URL
    
    ↓
    
    Download robots.txt

Đúng:
    
    
    Domain
    
    ↓
    
    Download robots.txt
    
    ↓
    
    Cache

Ví dụ:
    
    
    python.org
    
    ↓
    
    robots.txt
    
    ↓
    
    Memory Cache

Một lần tải có thể dùng cho hàng nghìn URL.

* * *

# 27\. Multi Domain
    
    
    python.org
    
    ↓
    
    RobotFileParser
    
    
    github.com
    
    ↓
    
    RobotFileParser

↓
    
    
    dict

Ví dụ:
    
    
    robots_cache = {
        "python.org": parser1,
        "github.com": parser2,
    }

* * *

# 28\. Framework
    
    
    crawler/
    
    ├── robotspolicy.py
    
    ├── downloader.py
    
    ├── scheduler.py
    
    ├── parser.py
    
    └── pipeline.py

* * *

# 29\. Luồng Scraper
    
    
    Scheduler
    
    ↓
    
    RobotsPolicy
    
    ↓
    
    Downloader
    
    ↓
    
    HTML
    
    ↓
    
    Parser

RobotsPolicy luôn là một bước trước khi tải trang.

* * *

# 30\. Những lỗi thường gặp

## Sai

Không kiểm tra:
    
    
    robots.txt

↓

Crawler vẫn chạy.

Điều này có thể vi phạm chính sách của website.

* * *

## Sai

Download:
    
    
    robots.txt

1000 lần.

↓

Lãng phí.

Nên cache theo domain.

* * *

## Sai

Bỏ qua:
    
    
    Crawl-delay

↓

Spam server.

* * *

## Sai

Không dùng:
    
    
    User-agent

phù hợp.

Một số website có quy tắc khác nhau cho từng crawler.

* * *

# Bài tập

## Bài 1

Viết chương trình:

Đọc:
    
    
    robots.txt

↓

In:
    
    
    can_fetch(...)

* * *

## Bài 2

In:
    
    
    crawl_delay()

* * *

## Bài 3

In:
    
    
    site_maps()

* * *

## Bài 4

Viết:
    
    
    class RobotsPolicy

Có:

  * cache parser theo domain 
  * `allowed(url)`
  * `crawl_delay(url)`



* * *

## Bài 5 (Nâng cao)

Thiết kế:
    
    
    crawler/
    
    ├── robots.py
    ├── downloader.py
    ├── scheduler.py
    ├── urlqueue.py
    └── spider.py

Trong đó:

  * `robots.py` quản lý toàn bộ `RobotFileParser`. 
  * `downloader.py` chỉ tải URL khi `RobotsPolicy.allowed(url)` trả về `True`. 
  * `scheduler.py` kết hợp `crawl_delay()` để điều phối tốc độ crawl. 



Đây là kiến trúc được nhiều crawler chuyên nghiệp áp dụng.

* * *

# Những hạn chế của `urllib.robotparser`

Mặc dù hữu ích, `urllib.robotparser` có một số giới hạn:

  * Không hỗ trợ đầy đủ mọi mở rộng không chuẩn của robots.txt. 
  * Không tự động tải lại robots.txt khi hết hạn cache. 
  * Không có cơ chế lưu cache ra đĩa. 
  * Không tích hợp sẵn với hàng đợi (queue) hay rate limiter. 
  * Không xử lý song song (concurrent) cho nhiều domain. 



Vì vậy, trong các framework crawler lớn, `RobotFileParser` thường chỉ là **thành phần nền tảng** , được bao bọc bởi một lớp quản lý cấp cao hơn.

* * *

# Tổng kết

Trong buổi học này, bạn đã nắm được:

  * Robot Exclusion Protocol. 
  * Cấu trúc của `robots.txt`. 
  * `User-agent`, `Allow`, `Disallow`. 
  * `Crawl-delay`. 
  * `Request-rate`. 
  * `Sitemap`. 
  * `RobotFileParser`. 
  * `can_fetch()`. 
  * `crawl_delay()`. 
  * `request_rate()`. 
  * `site_maps()`. 
  * Thiết kế `RobotsPolicy` để tích hợp vào Web Scraper. 



Đến thời điểm này, bạn đã học gần như đầy đủ các module cốt lõi của `urllib` dùng trong việc xây dựng một **HTTP Client** và **Web Scraper** chuyên nghiệp. Các buổi tiếp theo có thể tập trung vào việc **kết hợp tất cả các thành phần** (Request, Cookie, Proxy, SSL, Redirect, Parse, Error, Robots...) để xây dựng một framework hoàn chỉnh.

