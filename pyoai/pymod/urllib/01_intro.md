# Buổi 1 — Tổng quan urllib

* * *

# urllib là gì?

`urllib` là package chuẩn của Python dùng để:

  * gửi HTTP Request 
  * download dữ liệu 
  * upload dữ liệu 
  * encode/decode URL 
  * parse URL 
  * xử lý Cookie 
  * SSL 
  * Proxy 
  * Authentication 



Không cần cài đặt:
    
    
    import urllib

* * *

# urllib gồm những module nào?
    
    
    urllib
    │
    ├── request
    ├── parse
    ├── error
    ├── robotparser
    └── response

Đây là kiến trúc tổng thể:
    
    
    Application
    
    ↓
    
    urllib.request
    
    ↓
    
    HTTP Handler
    
    ↓
    
    socket
    
    ↓
    
    Internet

* * *

# 1\. urllib.request

Đây là module quan trọng nhất.

Dùng để:

  * GET 
  * POST 
  * Download 
  * Upload 
  * Headers 
  * Proxy 
  * Cookie 
  * SSL 



Ví dụ:
    
    
    from urllib.request import urlopen
    
    response = urlopen("https://httpbin.org/get")
    
    print(response.read())

* * *

# 2\. urllib.parse

Chuyên xử lý URL.

Ví dụ:
    
    
    https://example.com/search?q=python&page=2

Tách thành
    
    
    scheme
    host
    path
    query
    fragment

Ví dụ
    
    
    from urllib.parse import urlparse
    
    url = urlparse(
        "https://example.com/search?q=python"
    )
    
    print(url.scheme)
    print(url.netloc)
    print(url.path)
    print(url.query)

Kết quả
    
    
    https
    example.com
    /search
    q=python

* * *

# 3\. urllib.error

Chứa các Exception.

Ví dụ
    
    
    from urllib.request import urlopen
    from urllib.error import HTTPError
    
    try:
        urlopen("https://httpbin.org/status/404")
    except HTTPError as e:
        print(e.code)

Output
    
    
    404

* * *

# 4\. urllib.robotparser

Đọc file
    
    
    robots.txt

Ví dụ
    
    
    User-agent: *
    
    Disallow: /admin

Python có thể kiểm tra:
    
    
    Được phép crawl không?

* * *

# HTTP hoạt động thế nào?

Giả sử:
    
    
    https://example.com/index.html

Browser gửi
    
    
    GET /index.html HTTP/1.1
    
    Host: example.com
    
    User-Agent: Firefox

Server trả về
    
    
    HTTP/1.1 200 OK
    
    Content-Type: text/html
    
    <html>
    ...

`urllib.request` chính là thư viện giúp Python gửi request và nhận response theo cơ chế này.

* * *

# Luồng hoạt động
    
    
    urlopen()
    
    ↓
    
    Request
    
    ↓
    
    Internet
    
    ↓
    
    Server
    
    ↓
    
    Response
    
    ↓
    
    Python

* * *

# urlopen()

Đây là hàm được dùng nhiều nhất.
    
    
    from urllib.request import urlopen
    
    response = urlopen(
        "https://httpbin.org/get"
    )

`response` là đối tượng:
    
    
    http.client.HTTPResponse

* * *

# HTTPResponse

Có rất nhiều phương thức.
    
    
    read()
    
    readline()
    
    readlines()
    
    status
    
    headers
    
    reason
    
    geturl()
    
    info()

* * *

Ví dụ
    
    
    from urllib.request import urlopen
    
    r = urlopen("https://httpbin.org/get")
    
    print(type(r))

Output
    
    
    <class 'http.client.HTTPResponse'>

* * *

# Đọc dữ liệu
    
    
    data = r.read()
    
    print(type(data))

Output
    
    
    <class 'bytes'>

Lưu ý:

`urllib` luôn trả về **bytes** , không phải `str`.

* * *

# Decode
    
    
    text = data.decode("utf-8")

* * *

Ví dụ hoàn chỉnh
    
    
    from urllib.request import urlopen
    
    response = urlopen(
        "https://httpbin.org/get"
    )
    
    text = response.read().decode("utf-8")
    
    print(text)

* * *

# Kiểm tra Status
    
    
    print(response.status)

Ví dụ
    
    
    200

* * *

# Headers
    
    
    print(response.headers)

Ví dụ
    
    
    Content-Type
    
    Content-Length
    
    Server
    
    Date

* * *

# Lấy Header
    
    
    print(
        response.headers["Content-Type"]
    )

* * *

# URL cuối cùng

Nếu redirect:
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C

Thì
    
    
    response.geturl()

trả về
    
    
    C

* * *

# Đóng kết nối
    
    
    response.close()

Hoặc tốt hơn:
    
    
    from urllib.request import urlopen
    
    with urlopen(
        "https://httpbin.org/get"
    ) as response:
    
        text = response.read().decode()
    
    print(text)

* * *

# Context Manager

Đây là cách nên dùng.
    
    
    with
    
    ↓
    
    request
    
    ↓
    
    response
    
    ↓
    
    auto close

* * *

# Ví dụ thực tế 1 — Tải trang web
    
    
    from urllib.request import urlopen
    
    url = "https://www.python.org"
    
    with urlopen(url) as response:
        html = response.read().decode("utf-8")
    
    print(html[:500])

* * *

# Ví dụ thực tế 2 — Kiểm tra API
    
    
    from urllib.request import urlopen
    import json
    
    url = "https://httpbin.org/get"
    
    with urlopen(url) as response:
        data = json.loads(
            response.read()
        )
    
    print(data)

* * *

# So sánh urllib và requests

urllib| requests  
---|---  
Thư viện chuẩn| Cài thêm  
API chi tiết, mức thấp| API đơn giản  
Linh hoạt| Dễ dùng  
Phù hợp học bản chất HTTP| Phù hợp ứng dụng thông thường  
Cần xử lý bytes, Request, opener rõ ràng| Tự động hóa nhiều thao tác  
  
Một lập trình viên Python chuyên nghiệp nên nắm `urllib` trước, sau đó dùng `requests` hoặc `httpx` sẽ hiểu rõ hơn cách chúng hoạt động.

* * *

# Cấu trúc dự án sẽ xây trong khóa học

Trong suốt 20 buổi, chúng ta sẽ xây dựng một thư viện HTTP client có cấu trúc như sau:
    
    
    urllib_client/
    ├── client.py          # HTTP client
    ├── request.py         # Đóng gói request
    ├── response.py        # Xử lý response
    ├── auth.py            # Authentication
    ├── cookies.py         # CookieJar
    ├── proxy.py           # Proxy
    ├── retry.py           # Retry logic
    ├── downloader.py      # Download file
    ├── api.py             # REST API helpers
    ├── exceptions.py      # Exception tùy chỉnh
    └── examples/
        ├── get.py
        ├── post.py
        ├── upload.py
        ├── download.py
        └── github_api.py

Đến cuối khóa, bạn sẽ hiểu không chỉ cách sử dụng `urllib` mà còn cách thiết kế một HTTP client có kiến trúc rõ ràng, làm nền tảng để phát triển SDK hoặc công cụ crawler chuyên nghiệp.

