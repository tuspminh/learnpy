# Khóa học urllib Deep Dive

# Buổi 15: Authentication Deep Dive – Xác thực HTTP với `urllib`

> Đây là một trong những chuyên đề quan trọng nhất nếu bạn làm việc với API, Web Scraper, hệ thống nội bộ doanh nghiệp hoặc các dịch vụ yêu cầu đăng nhập.

Đến buổi này, chúng ta đã học:

  * ✅ Request 
  * ✅ Response 
  * ✅ Headers 
  * ✅ Cookies 
  * ✅ Redirect 
  * ✅ Proxy 
  * ✅ SSL/TLS 



Bây giờ chúng ta sẽ học **Authentication (Auth)**.

Authentication là chủ đề rất rộng. Chúng ta sẽ bắt đầu với những cơ chế mà `urllib` hỗ trợ trực tiếp, sau đó mở rộng sang các phương pháp hiện đại như Bearer Token và API Key.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ:

  * Hiểu Authentication là gì. 
  * Phân biệt Authentication và Authorization. 
  * Hiểu Basic Authentication. 
  * Hiểu Digest Authentication. 
  * Hiểu Bearer Token. 
  * Hiểu API Key. 
  * Hiểu Password Manager của `urllib`. 
  * Thiết kế `AuthProvider` cho `HttpClient`. 



* * *

# 1\. Authentication là gì?

Authentication trả lời câu hỏi:
    
    
    Bạn là ai?

Ví dụ:
    
    
    Username
    
    ↓
    
    Password
    
    ↓
    
    Server
    
    ↓
    
    OK

* * *

# 2\. Authorization là gì?

Sau khi xác thực thành công.

Server hỏi:
    
    
    Bạn được phép làm gì?

Ví dụ:
    
    
    Admin
    
    ↓
    
    Delete User
    
    ✓
    
    
    Guest
    
    ↓
    
    Delete User
    
    ✗

Đây là **Authorization** , không phải Authentication.

* * *

# 3\. Các kiểu Authentication

Trong HTTP phổ biến có:
    
    
    Basic Auth
    
    Digest Auth
    
    Bearer Token
    
    API Key
    
    Cookie Session
    
    OAuth2
    
    mTLS

`urllib` hỗ trợ trực tiếp Basic và Digest thông qua các handler chuyên dụng.

* * *

# 4\. HTTP Header Authorization

Hầu hết Authentication sử dụng:
    
    
    Authorization: ...

Ví dụ:
    
    
    Authorization:
    Basic xxxxxxxxx

Hoặc:
    
    
    Authorization:
    Bearer abc123

* * *

# 5\. Basic Authentication

Thông tin:
    
    
    username
    
    password

↓

Ghép:
    
    
    username:password

↓

Base64

↓
    
    
    Authorization:
    Basic dXNlcjpwYXNz

⚠️ **Base64 không phải là mã hóa** , chỉ là một cách biểu diễn dữ liệu.

* * *

# 6\. urllib hỗ trợ Basic Auth
    
    
    from urllib.request import HTTPBasicAuthHandler

Đây là handler dành cho Basic Authentication.

* * *

# 7\. Password Manager

Trước tiên tạo:
    
    
    from urllib.request import HTTPPasswordMgrWithDefaultRealm
    
    mgr = HTTPPasswordMgrWithDefaultRealm()

Đây là nơi lưu thông tin đăng nhập.

* * *

# 8\. add_password()
    
    
    mgr.add_password(
    
        realm=None,
    
        uri="https://example.com",
    
        user="admin",
    
        passwd="123456"
    )

Từ đó, handler có thể lấy đúng thông tin khi cần.

* * *

# 9\. Tạo Handler
    
    
    from urllib.request import HTTPBasicAuthHandler
    
    handler = HTTPBasicAuthHandler(mgr)

* * *

# 10\. build_opener()
    
    
    from urllib.request import build_opener
    
    opener = build_opener(handler)

↓
    
    
    response = opener.open(url)

Khi server yêu cầu Basic Auth, `urllib` sẽ tự động phản hồi bằng thông tin đã lưu.

* * *

# 11\. Luồng hoạt động
    
    
    Request
    
    ↓
    
    401 Unauthorized
    
    ↓
    
    WWW-Authenticate
    
    ↓
    
    BasicAuthHandler
    
    ↓
    
    Authorization
    
    ↓
    
    200 OK

* * *

# 12\. WWW-Authenticate

Server trả:
    
    
    HTTP/1.1 401 Unauthorized
    
    WWW-Authenticate:
    Basic realm="Admin Area"

Client biết cần dùng Basic Authentication.

* * *

# 13\. Digest Authentication

An toàn hơn Basic.

`urllib` hỗ trợ:
    
    
    from urllib.request import HTTPDigestAuthHandler

* * *

# 14\. Digest hoạt động

Không gửi trực tiếp:
    
    
    username:password

Mà tính toán giá trị băm (hash) từ nhiều thành phần như:

  * username 
  * password 
  * realm 
  * nonce 
  * method 
  * URI 



Điều này giúp tránh gửi thông tin xác thực ở dạng dễ suy luận.

* * *

# 15\. Bearer Token

Rất phổ biến với REST API.
    
    
    Authorization:
    Bearer eyJhbGci...

`urllib` **không có BearerAuthHandler**.

Ta chỉ cần thêm header:
    
    
    request.add_header(
    
        "Authorization",
    
        f"Bearer {token}"
    )

* * *

# 16\. API Key

Ví dụ:
    
    
    X-API-Key:
    abcdef123456

Hoặc:
    
    
    Authorization:
    ApiKey abcdef123456

Hoặc:
    
    
    ?api_key=...

Tùy từng API.

* * *

# 17\. Thiết kế AuthProvider

Thay vì:
    
    
    request.add_header(...)

ở khắp nơi.

Ta tạo:
    
    
    class AuthProvider:
        ...

* * *

# 18\. Interface
    
    
    from abc import ABC, abstractmethod
    
    class AuthProvider(ABC):
    
        @abstractmethod
        def apply(self, request):
            ...

Mỗi loại xác thực chỉ cần cài đặt `apply()`.

* * *

# 19\. BearerAuth
    
    
    class BearerAuth(
    
        AuthProvider
    
    ):
        ...

Bên trong:
    
    
    request.add_header(
    
        "Authorization",
    
        f"Bearer {token}"
    )

* * *

# 20\. ApiKeyAuth
    
    
    class ApiKeyAuth(
    
        AuthProvider
    
    ):
        ...

Ví dụ:
    
    
    request.add_header(
    
        "X-API-Key",
    
        key
    )

* * *

# 21\. BasicAuthProvider

Có thể viết wrapper:
    
    
    class BasicAuthProvider(
        AuthProvider
    ):
        ...

để thống nhất giao diện với các loại xác thực khác.

* * *

# 22\. HttpClient
    
    
    client = HttpClient(
    
        auth=BearerAuth(...)
    )

Hoặc:
    
    
    client = HttpClient(
    
        auth=ApiKeyAuth(...)
    )

Hoặc:
    
    
    client = HttpClient(
    
        auth=BasicAuthProvider(...)
    )

* * *

# 23\. Kiến trúc
    
    
    HttpClient
    
    ↓
    
    AuthProvider
    
    ↓
    
    Request
    
    ↓
    
    urllib

Nhờ đó `HttpClient` không cần biết đang dùng kiểu xác thực nào.

* * *

# 24\. Token Refresh

Nhiều API:
    
    
    Bearer
    
    ↓
    
    Expired
    
    ↓
    
    401
    
    ↓
    
    Refresh Token
    
    ↓
    
    Bearer mới

Đây là tính năng nâng cao mà `urllib` không tự hỗ trợ.

Ta sẽ tự xây dựng sau.

* * *

# 25\. Auth Chain
    
    
    Request
    
    ↓
    
    AuthProvider
    
    ↓
    
    Cookie
    
    ↓
    
    Redirect
    
    ↓
    
    HTTP

Authentication chỉ là một middleware trong toàn bộ pipeline.

* * *

# 26\. Nhiều Auth cùng lúc

Ví dụ:
    
    
    Cookie
    
    +
    
    API Key
    
    +
    
    Bearer

Điều này hoàn toàn có thể xảy ra với một số hệ thống nội bộ.

* * *

# 27\. Không lưu Password trong code

Sai:
    
    
    password = "123456"

Đúng:

  * biến môi trường, 
  * file cấu hình, 
  * secret manager, 
  * keyring. 



* * *

# 28\. Auth Factory
    
    
    AuthFactory
    
    ↓
    
    Bearer
    
    ↓
    
    Basic
    
    ↓
    
    ApiKey

Có thể tạo đối tượng xác thực dựa trên file cấu hình.

* * *

# 29\. Cấu trúc Framework
    
    
    httpclient/
    
    ├── auth/
    
    │   ├── base.py
    
    │   ├── basic.py
    
    │   ├── bearer.py
    
    │   ├── apikey.py
    
    │   ├── digest.py
    
    │   └── factory.py

Thiết kế này giúp dễ mở rộng.

* * *

# 30\. Kiến trúc hoàn chỉnh
    
    
    HttpClient
    │
    ├── AuthProvider
    ├── CookieManager
    ├── ProxyManager
    ├── RedirectPolicy
    ├── RetryPolicy
    ├── SSLConfig
    ├── MultipartEncoder
    ├── Downloader
    └── Response

* * *

# Những lỗi thường gặp

## 1\. Nhầm Authentication và Authorization

Authentication:
    
    
    Bạn là ai?

Authorization:
    
    
    Bạn được phép làm gì?

* * *

## 2\. Gửi Password không dùng HTTPS

Sai:
    
    
    HTTP
    
    ↓
    
    Basic Auth

Thông tin có thể bị đọc nếu kết nối không được bảo vệ.

Hãy luôn dùng HTTPS khi gửi thông tin xác thực.

* * *

## 3\. Hard-code Token

Sai:
    
    
    TOKEN = "..."

Đúng:
    
    
    Environment
    
    ↓
    
    Config
    
    ↓
    
    Secret Manager

* * *

## 4\. Quên Refresh Token
    
    
    401
    
    ↓
    
    Token hết hạn
    
    ↓
    
    Lỗi

Nên có cơ chế làm mới token khi cần.

* * *

# Bài tập

## Bài 1

Viết:
    
    
    class AuthProvider

bằng `abc.ABC`.

* * *

## Bài 2

Viết:
    
    
    class BearerAuth

Thêm:
    
    
    Authorization:
    Bearer ...

* * *

## Bài 3

Viết:
    
    
    class ApiKeyAuth

Hỗ trợ:
    
    
    X-API-Key

* * *

## Bài 4

Tích hợp:
    
    
    HttpClient(
    
        auth=...
    )

để mọi request đều được áp dụng cơ chế xác thực phù hợp.

* * *

# Tổng kết

Sau buổi 15, bạn đã hiểu:

  * Authentication và Authorization. 
  * Basic Authentication. 
  * Digest Authentication. 
  * Bearer Token. 
  * API Key. 
  * `HTTPBasicAuthHandler`. 
  * `HTTPDigestAuthHandler`. 
  * `HTTPPasswordMgrWithDefaultRealm`. 
  * Thiết kế `AuthProvider` theo hướng mở rộng. 



* * *

# Chuẩn bị cho buổi 16

Ở **buổi 16** , chúng ta sẽ học **HTTP Cache và Caching Strategy** , bao gồm:

  * `Cache-Control`
  * `ETag`
  * `If-None-Match`
  * `Last-Modified`
  * `If-Modified-Since`
  * `304 Not Modified`
  * Thiết kế `CacheManager`
  * Tích hợp bộ nhớ đệm vào `HttpClient`



Đây là một chủ đề rất quan trọng để xây dựng HTTP client hiệu quả, giảm băng thông và tăng tốc độ phản hồi, đặc biệt khi làm việc với API hoặc crawler quy mô lớn.

