# Khóa học urllib Deep Dive

# Buổi 12: Proxy Deep Dive – Xây dựng hệ thống Proxy chuyên nghiệp với urllib

> Đây là một trong những chủ đề quan trọng nhất khi xây dựng Web Crawler, Web Scraper, SEO Bot, Data Mining, Automation...

Rất nhiều lập trình viên chỉ biết:
    
    
    ProxyHandler(...)

nhưng không hiểu:

  * Proxy hoạt động như thế nào? 
  * HTTPS Proxy khác HTTP Proxy? 
  * Proxy Authentication? 
  * Proxy Rotation? 
  * Proxy Pool? 
  * Proxy Failover? 
  * Health Check? 



Trong buổi này chúng ta sẽ học theo góc nhìn của người thiết kế framework.

* * *

# Mục tiêu

Sau buổi học bạn sẽ:

  * Hiểu Proxy là gì. 
  * Hiểu Forward Proxy. 
  * Hiểu HTTP Proxy. 
  * Hiểu HTTPS Proxy. 
  * Sử dụng `ProxyHandler`. 
  * Thiết kế `ProxyManager`. 
  * Thiết kế Proxy Rotation. 
  * Chuẩn bị xây dựng crawler chuyên nghiệp. 



* * *

# 1\. Không dùng Proxy

Thông thường:
    
    
    Client
    
    ↓
    
    example.com

IP mà server nhìn thấy:
    
    
    Your IP

Ví dụ
    
    
    123.123.123.123

* * *

# 2\. Dùng Proxy
    
    
    Client
    
    ↓
    
    Proxy
    
    ↓
    
    example.com

Server nhìn thấy:
    
    
    Proxy IP

Không còn IP thật của bạn (ở góc nhìn của máy chủ đích).

* * *

# 3\. Forward Proxy

Đây là loại phổ biến nhất.
    
    
    Browser
    
    ↓
    
    Forward Proxy
    
    ↓
    
    Internet

`urllib` chủ yếu làm việc với kiểu proxy này.

* * *

# 4\. Reverse Proxy
    
    
    Internet
    
    ↓
    
    Nginx
    
    ↓
    
    Application

Reverse Proxy phục vụ **server** , không phải client.

Ví dụ:

  * Nginx 
  * HAProxy 
  * Traefik 
  * Caddy 



`urllib` không cấu hình reverse proxy vì đó là hạ tầng phía máy chủ.

* * *

# 5\. HTTP Proxy
    
    
    GET
    
    ↓
    
    Proxy
    
    ↓
    
    Server

Đơn giản nhất.

* * *

# 6\. HTTPS Proxy

HTTPS sử dụng kết nối TLS.

Thường sẽ diễn ra:
    
    
    CONNECT
    
    ↓
    
    Proxy
    
    ↓
    
    TLS
    
    ↓
    
    Server

Lệnh `CONNECT` yêu cầu proxy tạo đường hầm (tunnel) đến máy chủ đích.

* * *

# 7\. ProxyHandler

Ví dụ:
    
    
    from urllib.request import ProxyHandler
    
    proxy = ProxyHandler({
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080"
    })

* * *

# 8\. build_opener()
    
    
    from urllib.request import build_opener
    
    opener = build_opener(proxy)

Sau đó:
    
    
    response = opener.open(url)

* * *

# 9\. Không dùng urlopen()

Nếu cần Proxy:
    
    
    urlopen(...)

↓

Không linh hoạt.

Nên:
    
    
    opener.open(...)

Vì `OpenerDirector` cho phép kết hợp nhiều handler.

* * *

# 10\. Proxy Authentication

Một số Proxy yêu cầu:
    
    
    Username
    
    Password

Ví dụ:
    
    
    proxy.company.com
    
    user
    
    pass

* * *

# 11\. Proxy URL

Có thể viết:
    
    
    http://user:pass@proxy.example.com:8080

Ví dụ:
    
    
    proxy = {
        "http":
        "http://admin:123456@proxy.example.com:8080"
    }

**Lưu ý:** Cách này tiện nhưng không nên dùng trong sản phẩm vì thông tin xác thực xuất hiện ngay trong URL.

* * *

# 12\. ProxyBasicAuthHandler

`urllib` hỗ trợ:
    
    
    ProxyBasicAuthHandler

Cách dùng rất giống:
    
    
    HTTPBasicAuthHandler

Kết hợp với:

  * `HTTPPasswordMgrWithDefaultRealm`
  * `build_opener()`



* * *

# 13\. Password Manager
    
    
    from urllib.request import HTTPPasswordMgrWithDefaultRealm
    
    mgr = HTTPPasswordMgrWithDefaultRealm()
    
    mgr.add_password(
        realm=None,
        uri="http://proxy.example.com:8080",
        user="admin",
        passwd="123456"
    )

* * *

# 14\. ProxyBasicAuthHandler
    
    
    from urllib.request import ProxyBasicAuthHandler
    
    handler = ProxyBasicAuthHandler(mgr)

* * *

# 15\. build_opener()
    
    
    opener = build_opener(
        proxy_handler,
        handler
    )

Bây giờ opener có thể vừa dùng proxy vừa tự động xác thực với proxy.

* * *

# 16\. Proxy Rotation

Crawler lớn:
    
    
    Request 1
    
    ↓
    
    IP1
    
    
    Request 2
    
    ↓
    
    IP2
    
    
    Request 3
    
    ↓
    
    IP3

↓

Giảm khả năng bị chặn.

* * *

# 17\. Proxy Pool

Ví dụ:
    
    
    proxies = [
    
        "...1",
    
        "...2",
    
        "...3",
    
        "...4"
    ]

Thay vì chỉ có một Proxy.

* * *

# 18\. ProxyManager

Thiết kế:
    
    
    class ProxyManager:
    
        ...

Thay vì:
    
    
    proxy = ...

rải rác trong code.

* * *

# 19\. Thuộc tính
    
    
    class ProxyManager:
    
        def __init__(self):
    
            self.proxies = []
    
            self.index = 0

* * *

# 20\. add()
    
    
    manager.add(
        proxy_url
    )

Ví dụ:
    
    
    manager.add(
        "http://1.1.1.1:8080"
    )

* * *

# 21\. next_proxy()
    
    
    proxy = manager.next_proxy()

Ví dụ:
    
    
    1
    
    ↓
    
    2
    
    ↓
    
    3
    
    ↓
    
    1
    
    ↓
    
    2

Đây là chiến lược **Round Robin**.

* * *

# 22\. Round Robin
    
    
    Proxy1
    
    ↓
    
    Proxy2
    
    ↓
    
    Proxy3
    
    ↓
    
    Proxy1

Ưu điểm:

  * đơn giản 
  * phân phối đều 



Nhược điểm:

  * không biết proxy nào đang hỏng. 



* * *

# 23\. Random Rotation
    
    
    import random
    
    proxy = random.choice(
        proxies
    )

Không theo thứ tự.

* * *

# 24\. Weighted Rotation

Ví dụ:
    
    
    Proxy A
    
    90%
    
    
    Proxy B
    
    10%

Áp dụng khi có proxy nhanh/chậm khác nhau.

* * *

# 25\. Health Check

Ví dụ:
    
    
    Proxy1
    
    ×
    
    Timeout

↓

Đánh dấu:
    
    
    Dead

↓

Không dùng nữa.

* * *

# 26\. Retry với Proxy khác

Ví dụ:
    
    
    Proxy1
    
    ↓
    
    Timeout

↓

Retry

↓

Proxy2

↓

OK
    
    
    Đây là kỹ thuật rất phổ biến trong crawler.
    
    ---
    
    # 27. Thiết kế Proxy Object
    
    Thay vì:
    
    ```python
    proxy = "http://..."

Ta có:
    
    
    from dataclasses import dataclass
    
    @dataclass
    class Proxy:
    
        url: str
    
        alive: bool = True
    
        fail_count: int = 0
    
        success_count: int = 0

Có thể mở rộng thêm:

  * thời gian phản hồi, 
  * thời điểm kiểm tra cuối, 
  * quốc gia, 
  * loại proxy,... 



* * *

# 28\. ProxyManager
    
    
    ProxyManager
    │
    ├── add()
    ├── remove()
    ├── next()
    ├── mark_dead()
    ├── health_check()
    └── reset()

Đây là thiết kế phù hợp cho một framework.

* * *

# 29\. Tích hợp HttpClient
    
    
    client = HttpClient(
        proxy_manager=...
    )

Trước mỗi request:
    
    
    next_proxy()
    
    ↓
    
    build_opener()
    
    ↓
    
    request

Bạn có thể tái sử dụng opener nếu proxy không thay đổi; nếu đổi proxy thường xuyên, có thể cần tạo opener tương ứng.

* * *

# 30\. Proxy + Retry
    
    
    Request
    
    ↓
    
    Proxy1
    
    ↓
    
    Timeout
    
    ↓
    
    Retry
    
    ↓
    
    Proxy2
    
    ↓
    
    OK

Proxy và Retry nên phối hợp với nhau.

* * *

# 31\. Proxy + Cookie

Thông thường:
    
    
    Cookie
    
    ↓
    
    Proxy1

↓

OK

↓

Proxy2

↓

Server nghi ngờ
    
    
    Một số website liên kết phiên đăng nhập với địa chỉ IP, nên thay đổi proxy giữa chừng có thể làm phiên bị vô hiệu.
    
    ---
    
    # 32. Proxy + Session
    
    Crawler lớn thường quản lý:
    
    ```text
    Session
    
    ↓
    
    Cookie
    
    ↓
    
    Proxy
    
    ↓
    
    User-Agent

thành một **Identity** thống nhất.

* * *

# 33\. SOCKS Proxy

`urllib` **không hỗ trợ SOCKS Proxy trực tiếp**.

Nếu cần:
    
    
    SOCKS5

thường dùng:

  * PySocks 
  * requests + requests[socks] 



hoặc cấu hình socket ở mức thấp hơn.

* * *

# 34\. Proxy Environment

`urllib` có thể tự đọc:
    
    
    HTTP_PROXY
    
    HTTPS_PROXY
    
    NO_PROXY

từ biến môi trường.

Ví dụ trên Linux:
    
    
    export HTTP_PROXY=http://proxy.example.com:8080

Nếu không muốn dùng proxy từ môi trường, bạn cần cấu hình opener hoặc handler phù hợp.

* * *

# 35\. Cấu trúc Framework
    
    
    httpclient/
    │
    ├── client.py
    ├── retry.py
    ├── auth.py
    ├── cookies.py
    ├── proxy.py
    ├── downloader.py
    ├── multipart.py
    ├── response.py
    ├── exceptions.py
    └── examples/

* * *

# Những lỗi thường gặp

## 1\. Một Proxy duy nhất

Sai:
    
    
    100000 requests
    
    ↓
    
    1 Proxy

Rất dễ bị chặn hoặc quá tải.

* * *

## 2\. Không kiểm tra Proxy chết
    
    
    Timeout
    
    ↓
    
    Retry
    
    ↓
    
    Timeout
    
    ↓
    
    Retry
    
    ↓
    
    Timeout

Nếu luôn dùng cùng proxy lỗi, retry sẽ không hiệu quả.

* * *

## 3\. Hard-code User/Password

Sai:
    
    
    proxy = (
        "http://admin:123@..."
    )

Nên đọc từ:

  * biến môi trường, 
  * file cấu hình, 
  * hệ thống quản lý bí mật (secret manager). 



* * *

## 4\. Dùng Session với nhiều Proxy

Cookie:
    
    
    ABC123

↓

IP đổi liên tục.

↓

Website có thể yêu cầu đăng nhập lại hoặc chặn truy cập.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    ProxyManager

Hỗ trợ:

  * add() 
  * remove() 
  * next_proxy() 



* * *

## Bài 2

Tạo:
    
    
    Proxy

bằng `@dataclass`.

Thêm các thuộc tính:

  * url 
  * alive 
  * fail_count 
  * success_count 



* * *

## Bài 3

Viết:
    
    
    mark_dead(proxy)

Nếu số lần lỗi vượt quá ngưỡng, đánh dấu proxy không còn khả dụng.

* * *

## Bài 4

Tích hợp `ProxyManager` vào `HttpClient`.

Mỗi request:

  * lấy proxy tiếp theo, 
  * tạo `ProxyHandler`, 
  * gửi request. 



* * *

# Góc nhìn kiến trúc

Đến buổi 12, các thành phần của framework đã khá đầy đủ:
    
    
    HttpClient
    │
    ├── AuthProvider
    ├── RetryPolicy
    ├── CookieManager
    ├── ProxyManager
    ├── MultipartEncoder
    ├── Downloader
    └── Response

Mỗi thành phần đều có một trách nhiệm rõ ràng:

  * **AuthProvider** : xác thực. 
  * **RetryPolicy** : xử lý lỗi tạm thời. 
  * **CookieManager** : quản lý trạng thái phiên. 
  * **ProxyManager** : quản lý định tuyến mạng. 
  * **MultipartEncoder** : xây dựng dữ liệu upload. 
  * **Downloader** : tải tệp. 



Đây là một thiết kế hướng đối tượng giúp dễ mở rộng và kiểm thử.

* * *

# Chuẩn bị cho buổi 13

Ở **buổi 13** , chúng ta sẽ học **SSL/TLS và HTTPS Deep Dive** , bao gồm:

  * `ssl.SSLContext`
  * Chứng chỉ số (Certificate) 
  * CA (Certificate Authority) 
  * Kiểm tra chứng chỉ (Certificate Verification) 
  * Client Certificate (Mutual TLS) 
  * Tùy chỉnh `HTTPSHandler`
  * Bỏ qua kiểm tra chứng chỉ (chỉ dùng trong môi trường phát triển) 
  * Thiết kế `SSLConfig` để tích hợp vào `HttpClient`



Sau buổi này, bạn sẽ hiểu rõ cách `urllib` làm việc với HTTPS và biết cách cấu hình kết nối an toàn cho các ứng dụng thực tế.

