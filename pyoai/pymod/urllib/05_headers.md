# Khóa học urllib Deep Dive

# Buổi 5: HTTP Headers Deep Dive – User-Agent, Accept, Authorization và kiến trúc quản lý Header

> Đây là một trong những buổi quan trọng nhất của khóa học. Rất nhiều lập trình viên chỉ biết "thêm User-Agent", nhưng chưa thực sự hiểu **HTTP Header là gì** , **chúng hoạt động như thế nào** , và **cách thiết kế hệ thống quản lý Header** cho một HTTP Client chuyên nghiệp.

* * *

# Mục tiêu

Sau buổi học này bạn sẽ:

  * Hiểu bản chất của HTTP Header. 
  * Biết các Header phổ biến trong Request và Response. 
  * Quản lý Header bằng `urllib.request.Request`. 
  * Hiểu User-Agent, Accept, Authorization, Referer, Cookie... 
  * Xây dựng lớp `Headers` để quản lý header chuyên nghiệp. 
  * Nâng cấp `HttpClient` để có default headers. 



* * *

# 1\. HTTP Request gồm những gì?

Một HTTP Request thực tế:
    
    
    GET /search?q=python HTTP/1.1
    Host: example.com
    User-Agent: Mozilla/5.0
    Accept: application/json
    Accept-Language: vi-VN
    Connection: keep-alive
    
    <Body (nếu có)>

HTTP Request gồm 3 phần:
    
    
    Request Line
    
    ↓
    
    Headers
    
    ↓
    
    Body

* * *

# 2\. Header là gì?

Header là tập hợp các cặp:
    
    
    Key : Value

Ví dụ:
    
    
    Content-Type: application/json
    
    Accept: application/json
    
    User-Agent: Mozilla/5.0

Trong Python:
    
    
    headers = {
        "User-Agent": "MyClient",
        "Accept": "application/json"
    }

* * *

# 3\. Request Headers vs Response Headers

Request:
    
    
    Python
    
    ↓
    
    Server

Ví dụ:
    
    
    User-Agent
    
    Accept
    
    Authorization
    
    Cookie

* * *

Response:
    
    
    Server
    
    ↓
    
    Python

Ví dụ:
    
    
    Content-Type
    
    Content-Length
    
    Set-Cookie
    
    Server
    
    Date

* * *

# 4\. Header không phân biệt hoa thường

Các dòng sau tương đương:
    
    
    Content-Type
    
    
    content-type
    
    
    CONTENT-TYPE

Theo chuẩn HTTP, tên header **không phân biệt chữ hoa/chữ thường**.

* * *

# 5\. User-Agent

Đây là header quan trọng nhất.

Ví dụ trình duyệt Chrome:
    
    
    Mozilla/5.0 ...
    
    Chrome/140 ...

Firefox:
    
    
    Mozilla/5.0 ...
    
    Firefox/153 ...

Python:
    
    
    Python-urllib/3.x

* * *

# 6\. Tại sao nhiều website chặn urllib?

Vì server thấy:
    
    
    User-Agent
    
    ↓
    
    Python-urllib

Nhiều hệ thống chống bot sẽ:
    
    
    403 Forbidden

* * *

# 7\. Thêm User-Agent
    
    
    from urllib.request import Request
    
    req = Request(
        "https://httpbin.org/get",
        headers={
            "User-Agent": "GardenClient/1.0"
        }
    )

* * *

# 8\. Kiểm tra User-Agent
    
    
    import json
    
    from urllib.request import Request
    from urllib.request import urlopen
    
    req = Request(
        "https://httpbin.org/get",
        headers={
            "User-Agent": "GardenClient/1.0"
        }
    )
    
    with urlopen(req) as response:
        data = json.loads(
            response.read().decode()
        )
    
    print(data["headers"])

Kết quả sẽ hiển thị User-Agent mà server nhận được.

* * *

# 9\. Accept

Header này nói với server:

> Tôi muốn nhận kiểu dữ liệu gì.

Ví dụ:
    
    
    Accept: application/json

hoặc
    
    
    Accept: text/html

* * *

Ví dụ:
    
    
    headers = {
        "Accept": "application/json"
    }

* * *

# 10\. Accept-Language
    
    
    Accept-Language
    
    ↓
    
    vi-VN

hoặc
    
    
    en-US

Ví dụ:
    
    
    headers = {
        "Accept-Language": "vi-VN"
    }

Một số website sẽ trả về nội dung theo ngôn ngữ này.

* * *

# 11\. Referer

Ví dụ:
    
    
    Referer:
    
    https://google.com

Server biết người dùng đến từ đâu.

Python:
    
    
    headers = {
        "Referer":
        "https://google.com"
    }

* * *

# 12\. Authorization

Dùng để xác thực.

Ví dụ Bearer Token:
    
    
    Authorization:
    
    Bearer abcdef123456

Python:
    
    
    headers = {
        "Authorization":
        "Bearer my_token"
    }

Chúng ta sẽ học chi tiết hơn ở buổi Authentication.

* * *

# 13\. Connection
    
    
    Connection:
    
    keep-alive

hoặc
    
    
    close

`urllib` xử lý phần lớn việc này cho bạn.

* * *

# 14\. Cache-Control
    
    
    Cache-Control:
    
    no-cache

Hoặc:
    
    
    max-age=3600

Giúp kiểm soát việc lưu cache.

* * *

# 15\. Content-Type

Đã học ở buổi trước.

Ví dụ:
    
    
    application/json
    
    
    application/x-www-form-urlencoded
    
    
    multipart/form-data

* * *

# 16\. Content-Length

Response:
    
    
    Content-Length:
    
    3489

Trong Python:
    
    
    length = response.headers.get(
        "Content-Length"
    )
    
    print(length)

* * *

# 17\. Xây dựng lớp Headers

Không nên truyền `dict` trực tiếp khắp nơi.

Ta tạo lớp:
    
    
    class Headers:
    
        def __init__(self):
            self._headers = {}
    
        def set(self, key, value):
            self._headers[key] = value
    
        def get(self, key, default=None):
            return self._headers.get(key, default)
    
        def remove(self, key):
            self._headers.pop(key, None)
    
        def to_dict(self):
            return dict(self._headers)

* * *

Sử dụng:
    
    
    headers = Headers()
    
    headers.set(
        "User-Agent",
        "GardenClient"
    )
    
    headers.set(
        "Accept",
        "application/json"
    )

* * *

# 18\. Default Headers

Trong HttpClient:
    
    
    class HttpClient:
    
        def __init__(self):
    
            self.default_headers = {
                "User-Agent":
                "GardenClient/1.0",
    
                "Accept":
                "application/json"
            }

* * *

# 19\. Gộp Header

Ví dụ:
    
    
    client.default_headers
    
    ↓
    
    {
    
    User-Agent
    
    Accept
    
    }

Người dùng truyền:
    
    
    {
    
    Authorization
    
    }

Ta gộp:
    
    
    merged = dict(self.default_headers)
    
    merged.update(headers or {})

Đây là kỹ thuật rất phổ biến.

* * *

# 20\. Nâng cấp HttpClient
    
    
    from urllib.request import Request, urlopen
    
    class HttpClient:
    
        def __init__(self):
            self.default_headers = {
                "User-Agent": "GardenClient/1.0",
                "Accept": "application/json",
            }
    
        def get(self, url, headers=None):
    
            merged = dict(self.default_headers)
    
            if headers:
                merged.update(headers)
    
            request = Request(
                url,
                headers=merged
            )
    
            with urlopen(request) as response:
                return response.read().decode()

* * *

Sử dụng:
    
    
    client = HttpClient()
    
    print(
        client.get(
            "https://httpbin.org/get"
        )
    )

* * *

Ghi đè:
    
    
    client.get(
        url,
        headers={
            "User-Agent":
            "Crawler 2.0"
        }
    )

* * *

# 21\. Builder Pattern cho Header

Ta có thể xây dựng API đẹp hơn:
    
    
    headers = (
        Headers()
    )
    
    headers.set(
        "User-Agent",
        "GardenClient"
    )
    
    headers.set(
        "Accept",
        "application/json"
    )
    
    headers.set(
        "Authorization",
        "Bearer TOKEN"
    )

Hoặc hỗ trợ fluent interface:
    
    
    class Headers:
        def __init__(self):
            self._headers = {}
    
        def add(self, key, value):
            self._headers[key] = value
            return self
    
        def to_dict(self):
            return dict(self._headers)

Sử dụng:
    
    
    headers = (
        Headers()
        .add("User-Agent", "GardenClient/1.0")
        .add("Accept", "application/json")
        .add("Authorization", "Bearer TOKEN")
    )

Đây là phong cách thường thấy trong các thư viện hiện đại.

* * *

# Những lỗi thường gặp

## 1\. Ghi đè toàn bộ header

Sai:
    
    
    merged = headers

Nếu `headers` không chứa `User-Agent`, bạn sẽ mất giá trị mặc định.

Đúng:
    
    
    merged = dict(self.default_headers)
    merged.update(headers or {})

* * *

## 2\. Dùng sai Content-Type

Ví dụ:
    
    
    Content-Type:
    
    application/json

nhưng Body lại là:
    
    
    name=Alice&age=20

Server sẽ hiểu sai dữ liệu.

* * *

## 3\. Hard-code token

Sai:
    
    
    headers = {
        "Authorization":
        "Bearer abc123"
    }

Trong dự án thật, token nên lấy từ:

  * biến môi trường (`os.environ`) 
  * file cấu hình 
  * hệ thống quản lý bí mật (secret manager) 



* * *

# Bài tập thực hành

### Bài 1

Viết lớp:
    
    
    class Headers:

Hỗ trợ:

  * `set()`
  * `get()`
  * `remove()`
  * `clear()`
  * `to_dict()`



* * *

### Bài 2

Viết phiên bản fluent:
    
    
    headers = (
        Headers()
        .add("User-Agent", "GardenClient")
        .add("Accept", "application/json")
        .add("Accept-Language", "vi-VN")
    )

* * *

### Bài 3

Nâng cấp `HttpClient`:

  * có `default_headers`
  * hỗ trợ ghi đè header theo từng request 
  * luôn giữ lại các header mặc định nếu không bị ghi đè 



* * *

### Bài 4

Gửi request đến `https://httpbin.org/get` với:
    
    
    headers = {
        "User-Agent": "GardenClient/2.0",
        "Accept": "application/json",
        "Accept-Language": "vi-VN",
        "Referer": "https://example.com"
    }

Đọc JSON phản hồi và in ra:

  * User-Agent 
  * Accept 
  * Accept-Language 
  * Referer 



Để kiểm tra server đã nhận đúng các header hay chưa.

* * *

# Tổng kết

Trong buổi 5, bạn đã nắm được:

  * Cấu trúc và vai trò của HTTP Header. 
  * Các header quan trọng: `User-Agent`, `Accept`, `Accept-Language`, `Referer`, `Authorization`, `Content-Type`. 
  * Cách thêm và quản lý header trong `urllib.request.Request`. 
  * Thiết kế lớp `Headers` để đóng gói logic quản lý header. 
  * Nâng cấp `HttpClient` với `default_headers` và cơ chế hợp nhất (merge) header. 



Ở **buổi 6** , chúng ta sẽ học **làm việc với JSON API chuyên sâu** , bao gồm:

  * thiết kế `ApiClient` kế thừa từ `HttpClient`, 
  * tự động chuyển đổi giữa `dict` và JSON, 
  * xử lý phản hồi JSON, 
  * chuẩn hóa lỗi API, 
  * xây dựng nền tảng cho một REST SDK chuyên nghiệp bằng `urllib`.

