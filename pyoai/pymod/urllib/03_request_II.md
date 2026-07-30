# Khóa học urllib Deep Dive

# Buổi 3: HTTP GET nâng cao – `Request`, Query Parameters và Header

Đến buổi này, chúng ta sẽ chuyển từ cách gọi đơn giản:
    
    
    urlopen(url)

sang cách chuyên nghiệp hơn:
    
    
    Request(...)

Đây là cách mà hầu hết các ứng dụng thực tế, crawler, REST client và SDK đều sử dụng.

* * *

# Mục tiêu buổi học

Sau buổi này, bạn sẽ:

  * Hiểu tại sao cần `Request`. 
  * Biết cách tạo HTTP GET request chuyên nghiệp. 
  * Thêm Query Parameters đúng chuẩn. 
  * Quản lý Header. 
  * Hiểu User-Agent. 
  * Hiểu URL Encoding. 
  * Xây dựng helper cho GET request. 



* * *

# 1\. Tại sao cần `Request`?

Ở buổi trước:
    
    
    from urllib.request import urlopen
    
    response = urlopen(
        "https://httpbin.org/get"
    )

Python tự tạo một Request ngầm.

Thực tế là:
    
    
    urlopen(url)
    
    ↓
    
    Request(url)
    
    ↓
    
    HTTP Request
    
    ↓
    
    Response

Muốn kiểm soát request, ta phải tạo `Request` thủ công.

* * *

# 2\. Đối tượng Request
    
    
    from urllib.request import Request
    
    req = Request(
        url="https://httpbin.org/get"
    )

Sau đó:
    
    
    from urllib.request import urlopen
    
    with urlopen(req) as response:
        print(response.status)

* * *

# 3\. Request có gì?
    
    
    Request
    │
    ├── full_url
    ├── headers
    ├── method
    ├── data
    └── host

Request đại diện cho toàn bộ HTTP Request sẽ gửi đến server.

* * *

# 4\. So sánh

### Cách đơn giản
    
    
    urlopen("https://httpbin.org/get")

### Cách chuyên nghiệp
    
    
    req = Request("https://httpbin.org/get")
    
    urlopen(req)

Hãy tập sử dụng `Request` từ bây giờ.

* * *

# 5\. Query Parameters

Giả sử API:
    
    
    https://example.com/search

Muốn tìm:
    
    
    python

URL sẽ là:
    
    
    https://example.com/search?q=python

Có nhiều tham số:
    
    
    https://example.com/search?q=python&page=2

* * *

# 6\. Không nên nối chuỗi

Sai:
    
    
    url = (
        "https://example.com/search?"
        "q=python&page=2"
    )

Hoặc:
    
    
    url = base + "?q=" + keyword

Dễ lỗi khi dữ liệu chứa khoảng trắng, ký tự đặc biệt hoặc Unicode.

* * *

# 7\. `urlencode()`

Đúng:
    
    
    from urllib.parse import urlencode
    
    params = {
        "q": "python",
        "page": 2,
    }
    
    query = urlencode(params)
    
    print(query)

Kết quả:
    
    
    q=python&page=2

* * *

# 8\. URL đầy đủ
    
    
    from urllib.parse import urlencode
    
    base = "https://httpbin.org/get"
    
    params = {
        "name": "Alice",
        "age": 20,
    }
    
    url = base + "?" + urlencode(params)
    
    print(url)

Kết quả:
    
    
    https://httpbin.org/get?name=Alice&age=20

* * *

# 9\. Ký tự đặc biệt

Ví dụ:
    
    
    params = {
        "keyword": "machine learning"
    }

Nếu nối chuỗi:
    
    
    machine learning

sẽ sai.

`urlencode()`:
    
    
    from urllib.parse import urlencode
    
    print(
        urlencode(params)
    )

Kết quả:
    
    
    keyword=machine+learning

* * *

# 10\. Unicode
    
    
    params = {
        "name": "Nguyễn Văn A"
    }
    
    print(
        urlencode(params)
    )

Kết quả:
    
    
    name=Nguy%E1%BB%85n+V%C4%83n+A

Đây là **URL Encoding**.

* * *

# 11\. Gửi GET Request
    
    
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.parse import urlencode
    
    params = {
        "name": "Alice",
        "age": 30,
    }
    
    url = (
        "https://httpbin.org/get?"
        + urlencode(params)
    )
    
    req = Request(url)
    
    with urlopen(req) as response:
        print(response.read().decode())

`httpbin` sẽ trả về JSON chứa các tham số bạn gửi.

* * *

# 12\. Header là gì?

HTTP Request gồm:
    
    
    GET / HTTP/1.1
    
    Host: example.com
    
    User-Agent: ...
    
    Accept: ...
    
    Connection: keep-alive

Phần dưới chính là **Header**.

* * *

# 13\. Thêm Header
    
    
    from urllib.request import Request
    
    req = Request(
        "https://httpbin.org/get",
        headers={
            "User-Agent": "Python Demo"
        }
    )

* * *

# 14\. Kiểm tra Header đã gửi
    
    
    from urllib.request import Request
    
    req = Request(
        "https://example.com",
        headers={
            "User-Agent": "Demo"
        }
    )
    
    print(req.header_items())

Kết quả:
    
    
    [
        ('User-agent', 'Demo')
    ]

Lưu ý: Python có thể chuẩn hóa cách viết tên header (ví dụ `User-Agent` thành `User-agent`), nhưng giá trị vẫn được gửi đúng.

* * *

# 15\. User-Agent

Đây là header quan trọng.

Ví dụ:
    
    
    Mozilla/5.0 ...
    
    Chrome/140 ...
    
    Firefox/153 ...
    
    curl/8.0
    
    Python-urllib/3.13

Nhiều website sẽ chặn User-Agent mặc định của Python.

* * *

# 16\. Xem User-Agent
    
    
    from urllib.request import Request
    from urllib.request import urlopen
    
    req = Request(
        "https://httpbin.org/get",
        headers={
            "User-Agent": "MyCrawler/1.0"
        }
    )
    
    with urlopen(req) as r:
        print(r.read().decode())

Trong JSON trả về sẽ có:
    
    
    {
        "headers": {
            "User-Agent": "MyCrawler/1.0"
        }
    }

* * *

# 17\. Thêm nhiều Header
    
    
    headers = {
        "User-Agent": "MyApp/1.0",
        "Accept": "application/json",
        "Accept-Language": "vi-VN",
    }
    
    
    req = Request(
        url,
        headers=headers
    )

* * *

# 18\. Thêm Header sau khi tạo
    
    
    req = Request(url)
    
    req.add_header(
        "User-Agent",
        "Crawler"
    )

Có thể gọi nhiều lần:
    
    
    req.add_header(
        "Accept",
        "application/json"
    )

* * *

# 19\. Hàm tiện ích GET

Thay vì lặp lại nhiều đoạn mã:
    
    
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    
    def http_get(url, params=None, headers=None):
        if params:
            url += "?" + urlencode(params)
    
        request = Request(
            url,
            headers=headers or {}
        )
    
        with urlopen(request) as response:
            return response.read().decode()

Sử dụng:
    
    
    text = http_get(
        "https://httpbin.org/get",
        params={
            "name": "Bob"
        },
        headers={
            "User-Agent": "Demo"
        }
    )
    
    print(text)

* * *

# 20\. Thiết kế hướng đối tượng

Một lớp đơn giản:
    
    
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
    
    
    class HttpClient:
        def get(self, url, params=None, headers=None):
            if params:
                url += "?" + urlencode(params)
    
            request = Request(
                url,
                headers=headers or {}
            )
    
            with urlopen(request) as response:
                return response.read().decode()

Sử dụng:
    
    
    client = HttpClient()
    
    html = client.get(
        "https://httpbin.org/get",
        params={"page": 1},
        headers={"User-Agent": "Demo"}
    )
    
    print(html)

Đây sẽ là nền tảng để chúng ta mở rộng thành một HTTP client hoàn chỉnh ở các buổi sau.

* * *

# Những lỗi thường gặp

### 1\. Tự nối chuỗi URL
    
    
    url = base + "?q=" + keyword

❌ Sai khi `keyword` chứa khoảng trắng hoặc ký tự đặc biệt.

✔ Luôn dùng:
    
    
    url = base + "?" + urlencode(params)

* * *

### 2\. Ghi đè dấu `?`
    
    
    url += "?" + urlencode(params)

Nếu URL đã có query (`?page=1`), cách này sẽ tạo URL không hợp lệ.

Ở các buổi sau, chúng ta sẽ học cách dùng `urlparse()` và `urlunparse()` để xử lý an toàn.

* * *

### 3\. Quên User-Agent

Nhiều website sẽ trả về:
    
    
    403 Forbidden

Nếu bạn để User-Agent mặc định của Python.

* * *

# Bài tập thực hành

## Bài 1

Viết hàm:
    
    
    def build_url(base, params):
        ...

Ví dụ:
    
    
    build_url(
        "https://httpbin.org/get",
        {
            "name": "Alice",
            "page": 2,
        }
    )

Kết quả:
    
    
    https://httpbin.org/get?name=Alice&page=2

* * *

## Bài 2

Viết hàm:
    
    
    def get(url, params=None):
        ...

Yêu cầu:

  * tự động encode query 
  * trả về chuỗi văn bản 



* * *

## Bài 3

Viết lớp:
    
    
    class HttpClient:

Có phương thức:
    
    
    get(
        url,
        params=None,
        headers=None
    )

* * *

## Bài 4

Gọi `https://httpbin.org/get` với:
    
    
    params = {
        "keyword": "Python urllib",
        "page": 5
    }

và header:
    
    
    {
        "User-Agent": "GardenDau/1.0",
        "Accept": "application/json"
    }

Sau đó in ra:

  * URL đã gửi 
  * User-Agent mà server nhận được 
  * Các tham số `args` trong JSON phản hồi 



* * *

# Tổng kết

Trong buổi 3, bạn đã học cách xây dựng HTTP GET một cách bài bản:

  * Hiểu vai trò của `Request`. 
  * Tạo và tùy biến HTTP request. 
  * Sử dụng `urlencode()` để xây dựng query string an toàn. 
  * Thêm và quản lý HTTP header, đặc biệt là `User-Agent`. 
  * Viết các hàm và lớp `HttpClient` cơ bản để tái sử dụng mã nguồn. 



Ở **buổi 4** , chúng ta sẽ học **HTTP POST, PUT và DELETE** , bao gồm cách gửi dữ liệu biểu mẫu (`application/x-www-form-urlencoded`), gửi JSON (`application/json`), và làm việc với các phương thức HTTP khác trong `urllib.request`. Đây là bước quan trọng để tương tác với các REST API hiện đại.

