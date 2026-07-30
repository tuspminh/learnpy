# hóa học urllib Deep Dive

# Buổi 15: `urllib.parse` Deep Dive – Làm chủ phân tích và xây dựng URL

> Đây là một trong những module được sử dụng nhiều nhất trong toàn bộ thư viện `urllib`. Dù bạn làm Web Scraping, REST API, Web Framework hay HTTP Client thì gần như ngày nào cũng sẽ dùng `urllib.parse`.

Trong các buổi trước chúng ta đã học:

  * ✅ urllib.request 
  * ✅ urllib.response 
  * ✅ urllib.error 
  * ✅ Cookie 
  * ✅ Redirect 
  * ✅ SSL 
  * ✅ Proxy 



Bắt đầu từ buổi này chúng ta sẽ học **urllib.parse**.

Đây là module chịu trách nhiệm:

  * Phân tích URL 
  * Ghép URL 
  * Encode URL 
  * Decode URL 
  * Query String 
  * Path 
  * Percent Encoding 



* * *

# Mục tiêu

Sau buổi học này bạn sẽ:

  * Hiểu cấu trúc URL. 
  * Hiểu URL Encoding. 
  * Thành thạo `urlparse()`. 
  * Thành thạo `urlsplit()`. 
  * Thành thạo `urlunparse()`. 
  * Thành thạo `urlunsplit()`. 
  * Biết khi nào dùng từng hàm. 



* * *

# 1\. URL gồm những phần nào?

Ví dụ:
    
    
    https://admin:123@example.com:8443/products/books?id=100&page=2#comment

Cấu trúc:
    
    
    ┌──────── Scheme
    │       ┌──── User
    │       │     ┌── Password
    │       │     │
    https://admin:123@example.com:8443/products/books?id=100&page=2#comment
            │         │           │              │               │
            │         │           │              │               └── Fragment
            │         │           │              └── Query
            │         │           └── Path
            │         └── Port
            └── Host

* * *

# 2\. import
    
    
    from urllib import parse

Hoặc
    
    
    import urllib.parse

* * *

# 3\. urlparse()

Đây là hàm quan trọng nhất.
    
    
    from urllib.parse import urlparse
    
    result = urlparse(
        "https://example.com/books?id=10"
    )
    
    print(result)

Kết quả:
    
    
    ParseResult(
        scheme='https',
        netloc='example.com',
        path='/books',
        params='',
        query='id=10',
        fragment=''
    )

* * *

# 4\. ParseResult

Đây **không phải tuple thông thường**.
    
    
    print(type(result))

Kết quả
    
    
    urllib.parse.ParseResult

Nó là một **namedtuple**.

* * *

# 5\. Truy cập thuộc tính
    
    
    print(result.scheme)
    
    print(result.netloc)
    
    print(result.path)
    
    print(result.query)
    
    print(result.fragment)

* * *

# 6\. netloc

Ví dụ
    
    
    admin:123@example.com:8080

Toàn bộ phần này gọi là:
    
    
    netloc

Sau đó có thể tách tiếp.

* * *

# 7\. hostname
    
    
    url = urlparse(
        "https://admin:123@example.com:8080"
    )
    
    print(url.hostname)

↓
    
    
    example.com

* * *

# 8\. port
    
    
    print(url.port)

↓
    
    
    8080

* * *

# 9\. username
    
    
    print(url.username)

↓
    
    
    admin

* * *

# 10\. password
    
    
    print(url.password)

↓
    
    
    123

* * *

# 11\. fragment
    
    
    https://example.com/page#chapter2

↓
    
    
    result.fragment

↓
    
    
    chapter2

Lưu ý: fragment **không được gửi lên server** , nó chỉ được trình duyệt hoặc ứng dụng phía client sử dụng.

* * *

# 12\. query
    
    
    ?page=1&id=100

↓
    
    
    result.query

↓
    
    
    page=1&id=100

Đây vẫn là chuỗi, chưa được tách thành các cặp khóa–giá trị.

* * *

# 13\. path
    
    
    /books/python

↓
    
    
    result.path

* * *

# 14\. scheme
    
    
    https

↓
    
    
    result.scheme

* * *

# 15\. urlsplit()
    
    
    from urllib.parse import urlsplit

Khác:
    
    
    urlparse()

ở chỗ:
    
    
    Không tách params

Kết quả là `SplitResult`.

* * *

# 16\. urlsplit()
    
    
    result = urlsplit(
        url
    )

↓
    
    
    SplitResult

Bao gồm:

  * scheme 
  * netloc 
  * path 
  * query 
  * fragment 



* * *

# 17\. urlparse vs urlsplit

urlparse| urlsplit  
---|---  
Có params| Không params  
6 trường| 5 trường  
Ít dùng params trong web hiện đại| Đơn giản hơn  
  
Trong thực tế, `urlsplit()` thường được ưu tiên nếu bạn không cần xử lý trường `params`.

* * *

# 18\. urlunparse()

Ghép URL.
    
    
    from urllib.parse import urlunparse

Ví dụ:
    
    
    url = urlunparse((
        "https",
        "example.com",
        "/books",
        "",
        "id=1",
        ""
    ))
    
    print(url)

↓
    
    
    https://example.com/books?id=1

* * *

# 19\. urlunsplit()

Tương tự:
    
    
    urlunsplit()

Nhưng làm việc với 5 thành phần tương ứng `urlsplit()`.

* * *

# 20\. _replace()

`ParseResult` là immutable.

Muốn sửa:
    
    
    new_url = result._replace(
        scheme="http"
    )

↓
    
    
    print(new_url.geturl())

↓
    
    
    http://...

`_replace()` trả về một đối tượng mới, không thay đổi đối tượng cũ.

* * *

# 21\. geturl()
    
    
    url = result.geturl()

Ghép toàn bộ URL từ các thành phần hiện có.

* * *

# 22\. Ví dụ thực tế
    
    
    u = urlparse(
        "https://example.com/api/users?page=2"
    )
    
    print(u.path)

↓
    
    
    /api/users

↓

Dùng Router.

* * *

# 23\. Kiểm tra HTTPS
    
    
    if result.scheme == "https":
        print("Secure")

* * *

# 24\. Lấy Host
    
    
    host = result.hostname

↓
    
    
    example.com

Rất hữu ích khi kiểm tra whitelist hoặc phân loại domain.

* * *

# 25\. Kiểm tra Port
    
    
    if result.port == 443:
        ...

Nếu URL không ghi rõ cổng, `result.port` sẽ là `None`, dù `https` thường ngầm hiểu là 443.

* * *

# 26\. Ví dụ Router
    
    
    url = urlparse(url)
    
    if url.path.startswith("/api"):
        ...

* * *

# 27\. Thiết kế Url Object
    
    
    class Url:
    
        def __init__(self, url):
    
            self.result = urlparse(url)

Sau này:
    
    
    url.host
    
    url.scheme
    
    url.query

Thay vì gọi trực tiếp `ParseResult` ở nhiều nơi.

* * *

# 28\. Kiến trúc
    
    
    URL
    
    ↓
    
    urlparse()
    
    ↓
    
    ParseResult
    
    ↓
    
    Business Logic

* * *

# 29\. Framework
    
    
    HttpClient
    
    ↓
    
    Url
    
    ↓
    
    Request
    
    ↓
    
    urllib

Tách việc xử lý URL khỏi lớp `Request` giúp mã nguồn rõ ràng hơn.

* * *

# 30\. Những lỗi thường gặp

## Sai
    
    
    url.split("?")

Đây chỉ là tách chuỗi.

Không phải parser URL.

* * *

## Đúng
    
    
    urlparse(url)

* * *

## Sai
    
    
    url.split("/")

Không xử lý:

  * username 
  * password 
  * port 
  * fragment 
  * IPv6 
  * percent encoding 



* * *

## Đúng

Dùng:
    
    
    urllib.parse

* * *

# Bài tập

## Bài 1

Viết chương trình:

In:

  * scheme 
  * host 
  * port 
  * path 
  * query 



của:
    
    
    https://admin:123@example.com:8080/books?id=10&page=2

* * *

## Bài 2

Đổi:
    
    
    https

↓
    
    
    http

bằng:
    
    
    _replace()

* * *

## Bài 3

Viết lớp:
    
    
    class Url:

Có:

  * host 
  * scheme 
  * path 
  * query 
  * geturl() 



* * *

## Bài 4

Viết hàm:
    
    
    is_secure(url)

Trả về:
    
    
    True

nếu dùng HTTPS.

* * *

# Tổng kết

Trong buổi 15, bạn đã học:

  * Cấu trúc đầy đủ của một URL. 
  * `urlparse()`. 
  * `urlsplit()`. 
  * `urlunparse()`. 
  * `urlunsplit()`. 
  * `ParseResult` và `SplitResult`. 
  * `_replace()`. 
  * `geturl()`. 
  * Thiết kế lớp `Url` để đóng gói việc xử lý URL. 



* * *

# Chuẩn bị cho buổi 16

Ở **buổi 16** , chúng ta sẽ đi sâu vào **URL Encoding và Query String** , bao gồm:

  * `quote()`
  * `quote_plus()`
  * `unquote()`
  * `unquote_plus()`
  * `urlencode()`
  * `parse_qs()`
  * `parse_qsl()`
  * Percent Encoding 
  * UTF-8 trong URL 
  * Thiết kế `QueryParams` tương tự như `requests` và `httpx`. 



Đây là phần được sử dụng cực kỳ thường xuyên khi xây dựng REST API Client, Web Scraper và các ứng dụng web hiện đại.

