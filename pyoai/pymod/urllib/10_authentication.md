# Khóa học urllib Deep Dive

# Buổi 10: Authentication Deep Dive – Thiết kế hệ thống xác thực chuyên nghiệp

> Đây là một trong những chủ đề quan trọng nhất khi làm việc với HTTP. Hầu như mọi REST API hiện đại đều yêu cầu xác thực (Authentication).

Ví dụ:

  * GitHub API 
  * Docker Registry 
  * OpenAI API 
  * Google Cloud API 
  * AWS API 
  * Azure API 
  * Kubernetes API 
  * Firebase API 



Nếu thiết kế phần Authentication không tốt, toàn bộ HTTP Client sẽ khó mở rộng.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu Authentication và Authorization khác nhau như thế nào. 
  * Hiểu các cơ chế xác thực phổ biến. 
  * Sử dụng các Auth Handler có sẵn của `urllib`. 
  * Thiết kế `AuthProvider` theo nguyên tắc OCP (Open/Closed Principle). 
  * Tích hợp Authentication vào `HttpClient`. 



* * *

# 1\. Authentication ≠ Authorization

Đây là hai khái niệm rất dễ nhầm.

Authentication (Xác thực):
    
    
    Bạn là ai?

Ví dụ:

  * Username + Password 
  * API Key 
  * Access Token 



* * *

Authorization (Phân quyền):
    
    
    Bạn được phép làm gì?

Ví dụ:

  * Đọc dữ liệu 
  * Ghi dữ liệu 
  * Xóa dữ liệu 
  * Quản trị hệ thống 



* * *

Ví dụ:
    
    
    Đăng nhập thành công
    
    ↓
    
    Authentication OK
    
    ↓
    
    Có quyền Admin?
    
    ↓
    
    Authorization

* * *

# 2\. Các kiểu Authentication phổ biến

Ngày nay thường gặp:
    
    
    Basic Auth
    
    Bearer Token
    
    API Key
    
    Digest Auth
    
    OAuth2
    
    JWT
    
    Session Cookie

* * *

# 3\. Basic Authentication

Đây là chuẩn lâu đời nhất.

HTTP Header:
    
    
    Authorization: Basic dXNlcjpwYXNz

Trong đó:
    
    
    user:pass

được mã hóa bằng Base64.

**Lưu ý quan trọng:** Base64 **không phải mã hóa bảo mật** , chỉ là biểu diễn dữ liệu dạng văn bản. Basic Auth luôn nên được sử dụng cùng HTTPS.

* * *

# 4\. Tạo Basic Auth bằng Python
    
    
    import base64
    
    username = "admin"
    password = "123456"
    
    token = f"{username}:{password}"
    
    encoded = base64.b64encode(
        token.encode("utf-8")
    ).decode("ascii")
    
    print(encoded)

Ví dụ:
    
    
    YWRtaW46MTIzNDU2

* * *

# 5\. Gửi Basic Auth
    
    
    headers = {
        "Authorization":
            f"Basic {encoded}"
    }

Sau đó truyền `headers` vào `Request`.

* * *

# 6\. HTTPBasicAuthHandler

`urllib` đã hỗ trợ sẵn Basic Authentication.
    
    
    from urllib.request import HTTPPasswordMgrWithDefaultRealm
    from urllib.request import HTTPBasicAuthHandler
    from urllib.request import build_opener

* * *

# 7\. Password Manager
    
    
    password_mgr = HTTPPasswordMgrWithDefaultRealm()
    
    password_mgr.add_password(
        realm=None,
        uri="https://example.com",
        user="admin",
        passwd="123456"
    )

* * *

# 8\. Tạo Opener
    
    
    auth_handler = HTTPBasicAuthHandler(
        password_mgr
    )
    
    opener = build_opener(auth_handler)

Sau đó:
    
    
    response = opener.open(url)

Thay vì:
    
    
    urlopen(url)

* * *

# 9\. Bearer Token

Đây là kiểu phổ biến nhất hiện nay.

Ví dụ:
    
    
    Authorization:
    Bearer eyJhbGc...

Python:
    
    
    headers = {
        "Authorization":
            f"Bearer {token}"
    }

Ví dụ:

  * GitHub Personal Access Token 
  * OpenAI API Key (trước đây dùng Bearer) 
  * Kubernetes 
  * Auth0 



* * *

# 10\. API Key

Có nhiều API dùng:
    
    
    X-API-Key:
    xxxxxxxx

Hoặc:
    
    
    Api-Key:
    xxxxxxxx

Hoặc:
    
    
    Authorization:
    ApiKey xxxx

Không có chuẩn duy nhất.

* * *

# 11\. Query API Key

Một số API cũ:
    
    
    GET
    
    /users
    
    ?apikey=123

Không nên dùng nếu API hỗ trợ Header, vì khóa có thể xuất hiện trong log hoặc lịch sử URL.

* * *

# 12\. Digest Authentication

Khác Basic.

Server gửi:
    
    
    Challenge

Client tính toán:
    
    
    Hash

và gửi lại.

Ưu điểm:

  * Không gửi password trực tiếp. 



`urllib` hỗ trợ:
    
    
    HTTPDigestAuthHandler

Cách dùng tương tự `HTTPBasicAuthHandler`.

* * *

# 13\. OAuth2

OAuth2 rất rộng.

Thông thường:
    
    
    Login
    
    ↓
    
    Authorization Server
    
    ↓
    
    Access Token
    
    ↓
    
    REST API

Trong `urllib`, sau khi có Access Token, bạn chỉ cần gửi:
    
    
    Authorization:
    Bearer TOKEN

Việc lấy token thường cần triển khai theo tài liệu của từng nhà cung cấp.

* * *

# 14\. JWT

JWT là:
    
    
    Header
    
    .
    
    Payload
    
    .
    
    Signature

Ví dụ:
    
    
    eyJhbGc...
    
    .
    
    eyJuYW1l...
    
    .
    
    xxxxx

Thông thường JWT được gửi dưới dạng:
    
    
    Authorization:
    Bearer JWT

* * *

# 15\. Thiết kế AuthProvider

Không nên viết:
    
    
    headers = {
        "Authorization":
            ...
    }

ở khắp nơi.

Thay vào đó:
    
    
    class AuthProvider:
        def apply(self, headers):
            raise NotImplementedError

* * *

# 16\. BearerAuth
    
    
    class BearerAuth(AuthProvider):
    
        def __init__(self, token):
            self.token = token
    
        def apply(self, headers):
            headers["Authorization"] = (
                f"Bearer {self.token}"
            )

* * *

# 17\. BasicAuth
    
    
    import base64
    
    class BasicAuth(AuthProvider):
    
        def __init__(
            self,
            username,
            password
        ):
            self.username = username
            self.password = password
    
        def apply(self, headers):
    
            raw = (
                f"{self.username}:{self.password}"
            )
    
            encoded = (
                base64.b64encode(
                    raw.encode()
                )
                .decode("ascii")
            )
    
            headers["Authorization"] = (
                f"Basic {encoded}"
            )

* * *

# 18\. ApiKeyAuth
    
    
    class ApiKeyAuth(AuthProvider):
    
        def __init__(
            self,
            api_key
        ):
            self.api_key = api_key
    
        def apply(self, headers):
    
            headers["X-API-Key"] = (
                self.api_key
            )

Bạn có thể mở rộng để hỗ trợ tên header khác nhau.

* * *

# 19\. HttpClient tích hợp Auth
    
    
    class HttpClient:
    
        def __init__(
            self,
            auth=None
        ):
            self.auth = auth

Trước khi gửi request:
    
    
    headers = dict(
        self.default_headers
    )
    
    if self.auth:
        self.auth.apply(headers)

Điều này giúp `HttpClient` không cần biết chi tiết về từng cơ chế xác thực.

* * *

# 20\. Đổi Authentication rất dễ
    
    
    client = HttpClient(
        auth=BearerAuth(token)
    )

Hoặc:
    
    
    client = HttpClient(
        auth=BasicAuth(
            "admin",
            "123456"
        )
    )

Hoặc:
    
    
    client = HttpClient(
        auth=ApiKeyAuth(key)
    )

Không cần sửa `HttpClient`.

Đây là ví dụ điển hình của **Strategy Pattern**.

* * *

# 21\. Cấu trúc thư mục
    
    
    httpclient/
    │
    ├── auth.py
    ├── client.py
    ├── api.py
    ├── downloader.py
    ├── multipart.py
    ├── retry.py
    ├── headers.py
    ├── response.py
    ├── exceptions.py
    └── examples/

Trong `auth.py`:
    
    
    AuthProvider
    
    BasicAuth
    
    BearerAuth
    
    ApiKeyAuth

Sau này có thể thêm:
    
    
    OAuth2Auth
    
    DigestAuth
    
    SessionAuth

* * *

# 22\. Token Refresh

Một vấn đề thực tế:
    
    
    Bearer Token
    
    ↓
    
    Hết hạn
    
    ↓
    
    401 Unauthorized

Thay vì bắt người dùng tạo lại client, có thể thiết kế:
    
    
    class AuthProvider:
        def refresh(self):
            ...

`HttpClient` có thể:

  1. Nhận `401`. 
  2. Gọi `refresh()`. 
  3. Thử lại request (một lần). 



Đây là nền tảng của các SDK chuyên nghiệp.

* * *

# 23\. Những nguyên tắc bảo mật

## Không hard-code token

Sai:
    
    
    token = "abc123"

Nên:
    
    
    import os
    
    token = os.getenv("API_TOKEN")

Hoặc đọc từ file cấu hình được bảo vệ.

* * *

## Không ghi log Authorization

Sai:
    
    
    print(headers)

Có thể làm lộ:
    
    
    Authorization:
    Bearer xxxxxxxxx

Nên che giá trị nhạy cảm trước khi log.

* * *

## Luôn dùng HTTPS

Basic Auth, Bearer Token và API Key đều nên truyền qua HTTPS để tránh bị nghe lén trên đường truyền.

* * *

# Bài tập thực hành

## Bài 1

Viết:
    
    
    class AuthProvider:

Có phương thức:
    
    
    apply(headers)

* * *

## Bài 2

Viết ba lớp:

  * `BasicAuth`
  * `BearerAuth`
  * `ApiKeyAuth`



Đều kế thừa `AuthProvider`.

* * *

## Bài 3

Nâng cấp `HttpClient`

Cho phép:
    
    
    client = HttpClient(
        auth=BearerAuth("TOKEN")
    )

và tự động thêm header xác thực vào mọi request.

* * *

## Bài 4

Tạo thêm:
    
    
    class HeaderApiKeyAuth:

Cho phép:
    
    
    HeaderApiKeyAuth(
        header_name="Api-Key",
        api_key="123456"
    )

để hỗ trợ nhiều API khác nhau.

* * *

# Thiết kế hướng Framework

Sau 10 buổi, dự án của chúng ta đã có kiến trúc khá rõ ràng:
    
    
    httpclient/
    │
    ├── client.py
    ├── api.py
    ├── auth.py
    ├── retry.py
    ├── downloader.py
    ├── multipart.py
    ├── headers.py
    ├── response.py
    ├── exceptions.py
    └── examples/

Các thành phần đã tách biệt trách nhiệm:

  * `HttpClient`: gửi request. 
  * `ApiClient`: làm việc với JSON. 
  * `AuthProvider`: xác thực. 
  * `RetryPolicy`: retry. 
  * `MultipartEncoder`: upload. 
  * `Downloader`: tải file. 



Đây là nền tảng của một thư viện HTTP có khả năng mở rộng và bảo trì tốt.

# Tổng kết

Trong buổi 10, bạn đã học:

  * Phân biệt Authentication và Authorization. 
  * Basic Auth, Bearer Token, API Key, Digest Auth, OAuth2 và JWT ở mức kiến trúc. 
  * Sử dụng `HTTPBasicAuthHandler` của `urllib`. 
  * Thiết kế hệ thống xác thực theo **Strategy Pattern** với `AuthProvider`. 
  * Tích hợp Authentication vào `HttpClient`. 
  * Các nguyên tắc bảo mật khi làm việc với thông tin xác thực. 



* * *

## Chuẩn bị cho buổi 11

Ở **buổi 11** , chúng ta sẽ đi vào một phần rất đặc trưng của `urllib` mà nhiều lập trình viên bỏ qua:

**Opener, Handler và Processor Architecture**.

Bạn sẽ học:

  * `build_opener()`
  * `OpenerDirector`
  * `BaseHandler`
  * `HTTPHandler`
  * `HTTPSHandler`
  * `ProxyHandler`
  * `HTTPRedirectHandler`
  * `HTTPCookieProcessor`
  * Cơ chế Chain of Responsibility bên trong `urllib`
  * Cách viết **Custom Handler** để mở rộng `urllib` giống như cách framework hoạt động. 



Sau buổi 11, bạn sẽ hiểu **kiến trúc nội bộ của`urllib.request`**, thay vì chỉ biết cách sử dụng các hàm API. Đây là bước chuyển từ **người dùng thư viện** sang **người thiết kế thư viện**.

