# Khóa học urllib Deep Dive

# Buổi 11: Kiến trúc `OpenerDirector` và `Handler` – Trái tim của `urllib`

> **Đây là buổi học quan trọng nhất của toàn bộ khóa học.**

Cho đến buổi 10, chúng ta chỉ mới **sử dụng** `urllib`.

Từ buổi này trở đi, chúng ta sẽ học **urllib được thiết kế như thế nào**.

Sau buổi học này, bạn sẽ hiểu vì sao `urllib` có thể hỗ trợ:

  * HTTP 
  * HTTPS 
  * FTP 
  * Proxy 
  * Redirect 
  * Cookie 
  * Authentication 
  * Compression 



mà **không cần sửa`urlopen()`**.

Đây là một ví dụ kinh điển của **Design Pattern** trong thư viện chuẩn Python.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ:

  * Hiểu `urlopen()` thực sự làm gì. 
  * Hiểu `OpenerDirector`. 
  * Hiểu `Handler`. 
  * Hiểu Chain of Responsibility. 
  * Hiểu Strategy Pattern trong `urllib`. 
  * Tự viết Custom Handler. 



* * *

# 1\. urlopen() có thật sự mở URL không?

Hầu hết mọi người nghĩ:
    
    
    urlopen(url)

↓
    
    
    Socket
    
    ↓
    
    HTTP
    
    ↓
    
    Done

Thực tế không phải vậy.

* * *

`urlopen()` chỉ là một shortcut.

Nó làm gần giống:
    
    
    opener = build_opener()
    
    response = opener.open(url)

Hay nói cách khác:
    
    
    urlopen()
    
    ↓
    
    build_opener()
    
    ↓
    
    OpenerDirector
    
    ↓
    
    Handlers
    
    ↓
    
    Socket

* * *

# 2\. OpenerDirector

Đây là class trung tâm.
    
    
                    OpenerDirector
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    HTTPHandler      HTTPSHandler     FTPHandler
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    Network

OpenerDirector **không tự xử lý HTTP**.

Nó chỉ:

  * quản lý handler 
  * quyết định handler nào xử lý request 



* * *

# 3\. build_opener()

Ví dụ:
    
    
    from urllib.request import build_opener
    
    opener = build_opener()
    
    print(opener)

Kết quả sẽ là một đối tượng:
    
    
    OpenerDirector

* * *

# 4\. Handler là gì?

Handler là một object chuyên xử lý một nhiệm vụ.

Ví dụ:
    
    
    HTTPHandler

↓

HTTP

* * *
    
    
    HTTPSHandler

↓

HTTPS

* * *
    
    
    ProxyHandler

↓

Proxy

* * *
    
    
    HTTPCookieProcessor

↓

Cookie

* * *

Mỗi Handler chỉ làm **một việc**.

Đây là nguyên tắc **Single Responsibility Principle (SRP)**.

* * *

# 5\. Kiến trúc Handler
    
    
    Request
    
    ↓
    
    Handler A
    
    ↓
    
    Handler B
    
    ↓
    
    Handler C
    
    ↓
    
    Server
    
    ↓
    
    Handler C
    
    ↓
    
    Handler B
    
    ↓
    
    Handler A
    
    ↓
    
    Response

Giống như một dây chuyền xử lý.

* * *

# 6\. Chain of Responsibility

Đây chính là Design Pattern nổi tiếng.
    
    
    Request
    
    ↓
    
    AuthHandler
    
    ↓
    
    CookieHandler
    
    ↓
    
    RedirectHandler
    
    ↓
    
    HTTPHandler

Mỗi handler:

  * xử lý một phần 
  * chuyển tiếp cho handler tiếp theo 



Không handler nào biết toàn bộ hệ thống.

* * *

# 7\. Các Handler mặc định

`build_opener()` thường tạo nhiều handler mặc định như:
    
    
    ProxyHandler
    
    UnknownHandler
    
    HTTPHandler
    
    HTTPSHandler
    
    HTTPDefaultErrorHandler
    
    HTTPRedirectHandler
    
    FTPHandler
    
    FileHandler
    
    HTTPErrorProcessor

Danh sách cụ thể có thể thay đổi theo phiên bản Python.

* * *

# 8\. Xem danh sách Handler
    
    
    from urllib.request import build_opener
    
    opener = build_opener()
    
    for handler in opener.handlers:
        print(type(handler).__name__)

Ví dụ:
    
    
    ProxyHandler
    UnknownHandler
    HTTPHandler
    HTTPSHandler
    HTTPRedirectHandler
    HTTPErrorProcessor
    ...

Đây là cách rất tốt để khám phá nội bộ của `urllib`.

* * *

# 9\. HTTPHandler

Nhiệm vụ:
    
    
    Request
    
    ↓
    
    Socket
    
    ↓
    
    HTTP
    
    ↓
    
    Response

Nó là handler thật sự gửi request.

* * *

# 10\. HTTPSHandler

Khác:
    
    
    HTTP

↓
    
    
    HTTPS

Nó thêm SSL/TLS.

* * *

# 11\. ProxyHandler

Ví dụ:
    
    
    proxy = {
        "http": "http://proxy.example:8080",
        "https": "http://proxy.example:8080"
    }
    
    
    from urllib.request import ProxyHandler
    
    handler = ProxyHandler(proxy)

Sau này:
    
    
    opener = build_opener(handler)

* * *

# 12\. RedirectHandler

Ví dụ:

Server trả:
    
    
    301

↓
    
    
    Location:
    /new-page

Handler sẽ:
    
    
    Request mới
    
    ↓
    
    URL mới

Người dùng không cần tự xử lý redirect.

* * *

# 13\. CookieProcessor

Không có CookieProcessor:
    
    
    Login
    
    ↓
    
    Cookie
    
    ↓
    
    Mất

Có CookieProcessor:
    
    
    Login
    
    ↓
    
    CookieJar
    
    ↓
    
    Request tiếp theo

↓

Đăng nhập vẫn còn hiệu lực.

* * *

# 14\. ErrorProcessor

Server:
    
    
    404

↓

Không trả Response ngay.

↓

Handler quyết định:
    
    
    Raise HTTPError

Hay:
    
    
    Return Response

* * *

# 15\. Handler kế thừa BaseHandler
    
    
    from urllib.request import BaseHandler
    
    class MyHandler(BaseHandler):
        pass

Đây là nền tảng để mở rộng `urllib`.

* * *

# 16\. Custom Handler

Ví dụ:
    
    
    from urllib.request import BaseHandler
    
    class LoggingHandler(BaseHandler):
    
        def http_request(self, request):
    
            print(request.full_url)
    
            return request

* * *

# 17\. build_opener với Custom Handler
    
    
    opener = build_opener(
        LoggingHandler()
    )

Bây giờ:
    
    
    opener.open(url)

Sẽ in URL trước khi gửi request.

* * *

# 18\. Logging Request
    
    
    class LoggingHandler(BaseHandler):
    
        def http_request(self, request):
    
            print("=" * 40)
    
            print(request.get_method())
    
            print(request.full_url)
    
            print(request.header_items())
    
            return request

Rất hữu ích khi debug.

* * *

# 19\. Logging Response

Ngoài:
    
    
    http_request()

còn có:
    
    
    http_response()

Ví dụ:
    
    
    class LoggingHandler(BaseHandler):
    
        def http_response(
            self,
            request,
            response
        ):
    
            print(response.status)
    
            return response

Lưu ý: **bạn phải trả về`response`** để chuỗi xử lý tiếp tục hoạt động.

* * *

# 20\. Handler có thể sửa Request

Ví dụ:
    
    
    request.add_header(
        "User-Agent",
        "GardenClient"
    )

Trước khi gửi.

Điều này rất giống với **Middleware** trong:

  * Django 
  * Flask 
  * FastAPI 
  * ASP.NET Core 



* * *

# 21\. Handler có thể sửa Response

Ví dụ:
    
    
    Response
    
    ↓
    
    Giải nén
    
    ↓
    
    Decode
    
    ↓
    
    Log
    
    ↓
    
    User

Mỗi handler có thể biến đổi response trước khi trả về.

* * *

# 22\. Kiến trúc tổng thể
    
    
                        OpenerDirector
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
     LoggingHandler      AuthHandler      RetryHandler
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                      HTTPRedirectHandler
                               │
                      HTTPCookieProcessor
                               │
                         HTTPHandler
                               │
                             Socket

Đây chính là kiến trúc dạng **Pipeline**.

* * *

# 23\. So sánh với Middleware

FastAPI:
    
    
    Request
    
    ↓
    
    Middleware
    
    ↓
    
    Route
    
    ↓
    
    Middleware
    
    ↓
    
    Response

urllib:
    
    
    Request
    
    ↓
    
    Handler
    
    ↓
    
    HTTP
    
    ↓
    
    Handler
    
    ↓
    
    Response

Ý tưởng gần như giống nhau.

* * *

# 24\. Vì sao urllib dùng Handler?

Nếu không có Handler:
    
    
    urlopen()
    
    ↓
    
    2000 dòng code
    
    ↓
    
    if
    
    ↓
    
    else
    
    ↓
    
    if
    
    ↓
    
    else

Rất khó bảo trì.

Có Handler:
    
    
    Logging
    
    ↓
    
    Auth
    
    ↓
    
    Retry
    
    ↓
    
    Cookie
    
    ↓
    
    Redirect

Mỗi phần độc lập.

* * *

# 25\. Áp dụng vào HttpClient của chúng ta

Đến buổi 10 chúng ta có:
    
    
    HttpClient
    
    ↓
    
    Retry
    
    ↓
    
    Auth
    
    ↓
    
    Headers

Ta có thể nâng cấp:
    
    
    HttpClient
    
    ↓
    
    Middleware
    
    ↓
    
    Logging
    
    ↓
    
    Retry
    
    ↓
    
    Auth
    
    ↓
    
    HTTP

Tức là thiết kế giống `urllib`.

* * *

# 26\. Bài tập thực hành

## Bài 1

In danh sách tất cả handler của:
    
    
    build_opener()

và ghi chú vai trò của từng handler.

* * *

## Bài 2

Viết:
    
    
    LoggingHandler

Hiển thị:

  * Method 
  * URL 
  * Headers 



trước khi gửi request.

* * *

## Bài 3

Viết:
    
    
    TimingHandler

Đo thời gian xử lý request.

Gợi ý:

  * Lưu thời điểm bắt đầu trong `http_request()`. 
  * Tính thời gian trong `http_response()`. 



* * *

## Bài 4

Viết:
    
    
    HeaderHandler

Tự động thêm:
    
    
    X-App-Name:
    GardenClient

vào mọi request.

* * *

# Những lỗi thường gặp

## 1\. Quên trả về Request

Sai:
    
    
    def http_request(self, request):
        print(request.full_url)

Kết quả:
    
    
    None

Các handler phía sau sẽ không nhận được request.

Đúng:
    
    
    return request

* * *

## 2\. Quên trả về Response

Sai:
    
    
    def http_response(self, request, response):
        print(response.status)

Đúng:
    
    
    return response

* * *

## 3\. Handler làm quá nhiều việc

Sai:
    
    
    Logging
    
    Retry
    
    Auth
    
    Cookie
    
    ↓
    
    1 class

Đúng:
    
    
    LoggingHandler
    
    RetryHandler
    
    CookieHandler
    
    AuthHandler

Mỗi lớp một trách nhiệm.

* * *

# Tổng kết

Buổi 11 là bước ngoặt của khóa học.

Bạn đã hiểu:

  * `urlopen()` chỉ là lớp bọc của `OpenerDirector`. 
  * Vai trò của `build_opener()`. 
  * Kiến trúc `Handler` và `BaseHandler`. 
  * Cách hoạt động của **Chain of Responsibility** trong `urllib`. 
  * Cách viết `Custom Handler`. 
  * Mối liên hệ giữa Handler của `urllib` và Middleware trong các framework hiện đại. 



Đây là nền tảng để hiểu cách nhiều thư viện HTTP và web framework được thiết kế.

* * *

# Chuẩn bị cho buổi 12

Ở **buổi 12** , chúng ta sẽ đi sâu vào **Cookie Management** , bao gồm:

  * `http.cookiejar`
  * `CookieJar`
  * `MozillaCookieJar`
  * `LWPCookieJar`
  * Cookie phiên (Session Cookie) và Cookie lâu dài (Persistent Cookie) 
  * Lưu và tải cookie từ file 
  * Tự động đăng nhập và duy trì phiên làm việc 
  * Thiết kế `CookieManager` tích hợp với `HttpClient`



Đây là kiến thức rất quan trọng khi xây dựng crawler, web scraper hoặc client cần đăng nhập và duy trì trạng thái làm việc.

