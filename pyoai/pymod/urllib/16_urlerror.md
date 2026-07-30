# Khóa học urllib Deep Dive

# Chuyên đề: `urllib.error` – Xử lý lỗi chuyên nghiệp

> Đây là một trong những module quan trọng nhất của `urllib`. Nếu bạn chỉ biết `try...except Exception`, bạn sẽ không thể xây dựng một HTTP Client hay Web Scraper ổn định.

`urllib.error` cung cấp hệ thống ngoại lệ (exception) chuyên biệt cho HTTP và URL.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu kiến trúc của `urllib.error`. 
  * Phân biệt `URLError` và `HTTPError`. 
  * Xử lý timeout, DNS, SSL và connection error. 
  * Hiểu khi nào `HTTPError` vẫn chứa dữ liệu. 
  * Thiết kế hệ thống Exception cho `HttpClient`. 



* * *

# 1\. Module urllib.error

Import:
    
    
    import urllib.error

hoặc
    
    
    from urllib.error import URLError, HTTPError

Module chỉ có vài class nhưng rất quan trọng.

* * *

# 2\. Kiến trúc Exception
    
    
    Exception
        │
        └── URLError
                │
                └── HTTPError

Điều này có nghĩa:
    
    
    except URLError:

sẽ bắt luôn:
    
    
    HTTPError

Nếu muốn xử lý riêng HTTP Error, hãy đặt `except HTTPError` trước `except URLError`.

* * *

# 3\. URLError

Đây là exception cơ bản.

Ví dụ:
    
    
    from urllib.request import urlopen
    from urllib.error import URLError
    
    try:
        urlopen("http://not_exist.example")
    except URLError as e:
        print(e)

* * *

# 4\. Khi nào xảy ra URLError?

Ví dụ:
    
    
    DNS Error
    
    Connection Refused
    
    Timeout
    
    SSL Error
    
    Invalid URL
    
    No Route

Điểm chung:

> **Request chưa nhận được HTTP Response hợp lệ.**

* * *

# 5\. HTTPError

Khác với URLError.

Ví dụ:
    
    
    404
    
    500
    
    401
    
    403

Server **đã trả Response**.

Chỉ là status báo lỗi.

* * *

# 6\. Ví dụ
    
    
    from urllib.request import urlopen
    from urllib.error import HTTPError
    
    try:
        urlopen("https://httpbin.org/status/404")
    except HTTPError as e:
        print(e.code)

↓
    
    
    404

* * *

# 7\. HTTPError có Response

Điều rất nhiều người không biết:

`HTTPError`

vừa là
    
    
    Exception

vừa là
    
    
    Response

Nó có thể đọc body.

* * *

# 8\. Ví dụ
    
    
    try:
        urlopen(url)
    except HTTPError as e:
    
        print(e.read())

Điều này rất hữu ích vì nhiều API trả JSON mô tả lỗi.

* * *

# 9\. HTTPError có gì?

Ví dụ:
    
    
    print(e.code)
    
    print(e.reason)
    
    print(e.headers)
    
    print(e.url)

Có gần như đầy đủ thông tin của một phản hồi HTTP.

* * *

# 10\. code

Ví dụ
    
    
    e.code

↓
    
    
    404

* * *

# 11\. reason
    
    
    e.reason

↓
    
    
    Not Found

Hoặc với `URLError`, `reason` có thể là một ngoại lệ hệ thống như `socket.timeout` hoặc `socket.gaierror`.

* * *

# 12\. headers
    
    
    e.headers

↓
    
    
    Server
    
    Content-Type
    
    Date
    ...

Bạn có thể kiểm tra các header để quyết định cách xử lý.

* * *

# 13\. url
    
    
    e.url

↓

URL cuối cùng gây lỗi.

* * *

# 14\. filename

`HTTPError` kế thừa từ:
    
    
    addinfourl

Nên:
    
    
    e.geturl()

vẫn hoạt động.

* * *

# 15\. HTTPError đọc nhiều lần?

Sai:
    
    
    print(e.read())
    
    print(e.read())

Lần hai:
    
    
    b''

Vì stream đã được đọc hết.

* * *

# 16\. Đúng
    
    
    body = e.read()
    
    print(body)
    
    print(body)

Đọc một lần rồi lưu lại.

* * *

# 17\. Ví dụ API

Server:
    
    
    400

Body:
    
    
    {
        "error":"invalid_token"
    }

Ta có thể:
    
    
    body = e.read()
    
    print(body)

↓
    
    
    {
        "error":"invalid_token"
    }

Sau đó giải mã JSON để lấy thông tin chi tiết.

* * *

# 18\. URLError.reason

Ví dụ:
    
    
    except URLError as e:
    
        print(e.reason)

Có thể là:
    
    
    timed out

hoặc
    
    
    Connection refused

* * *

# 19\. Timeout

Ví dụ:
    
    
    urlopen(url, timeout=1)

↓
    
    
    except URLError as e:

↓
    
    
    timed out

Bạn có thể kiểm tra kiểu của `e.reason` để phân biệt timeout với các lỗi khác.

* * *

# 20\. DNS Error

Ví dụ:
    
    
    abc.xyz.invalid

↓
    
    
    Name or service not known

↓

`URLError`

* * *

# 21\. SSL Error

Ví dụ:
    
    
    CERTIFICATE_VERIFY_FAILED

↓

`URLError`

↓

`reason`

↓
    
    
    SSLError

* * *

# 22\. Connection Refused

Ví dụ
    
    
    127.0.0.1:9999

Không có server.

↓
    
    
    Connection Refused

↓

`URLError`

* * *

# 23\. Invalid URL

Ví dụ
    
    
    urlopen("abc")

↓
    
    
    ValueError

Lưu ý: Không phải mọi URL sai đều tạo `URLError`; một số trường hợp sẽ phát sinh `ValueError` ngay khi tạo request.

* * *

# 24\. Retry

Không nên Retry:
    
    
    404

Nên Retry:
    
    
    Timeout
    
    Connection Reset
    
    503
    
    502

Đây là nền tảng để xây dựng `RetryPolicy`.

* * *

# 25\. RetryPolicy
    
    
    class RetryPolicy:
    
        ...

↓
    
    
    HTTPError
    
    ↓
    
    Retry?

↓
    
    
    Yes / No

Ví dụ: retry với 502, 503, 504 nhưng không retry với 404.

* * *

# 26\. Exception Mapping

Thiết kế:
    
    
    URLError
    
    ↓
    
    HttpClientTimeout
    
    
    HTTPError
    
    ↓
    
    NotFound
    
    
    HTTPError
    
    ↓
    
    Unauthorized

Thay vì để code bên ngoài phải hiểu trực tiếp `urllib`.

* * *

# 27\. Custom Exception
    
    
    class HttpClientError(Exception):
        pass

↓
    
    
    class TimeoutError(
        HttpClientError
    ):
        pass

↓
    
    
    class NotFound(
        HttpClientError
    ):
        pass

Giúp API của thư viện rõ ràng hơn.

* * *

# 28\. Kiến trúc
    
    
    urllib.error
    
    ↓
    
    Mapper
    
    ↓
    
    Framework Exception
    
    ↓
    
    Business Logic

Business Logic không cần phụ thuộc trực tiếp vào `urllib`.

* * *

# 29\. HttpClient
    
    
    HttpClient
    
    ↓
    
    urllib
    
    ↓
    
    Exception Mapper
    
    ↓
    
    Application

Đây là cách nhiều thư viện HTTP được thiết kế.

* * *

# 30\. Những lỗi thường gặp

## Sai
    
    
    except Exception:

↓

Không biết lỗi gì.

* * *

## Đúng
    
    
    except HTTPError:
    
    
    except URLError:
    
    
    except ValueError:

Xử lý theo từng nhóm lỗi.

* * *

## Sai
    
    
    except URLError:

↓

Retry mọi lỗi.

Ví dụ:
    
    
    404

Không nên retry.

* * *

## Đúng

Kiểm tra:
    
    
    e.code

hoặc loại của `e.reason`.

* * *

## Sai
    
    
    print(e.read())
    
    print(e.read())

↓

Lần hai rỗng.

* * *

## Đúng
    
    
    body = e.read()

* * *

# Bài tập

## Bài 1

Viết chương trình:
    
    
    try:
        ...
    except HTTPError:

In:

  * code 
  * reason 
  * headers 
  * body 



* * *

## Bài 2

Tạo:
    
    
    ExceptionMapper

Chuyển:
    
    
    404
    
    ↓
    
    NotFound
    
    
    401
    
    ↓
    
    Unauthorized
    
    
    403
    
    ↓
    
    Forbidden

* * *

## Bài 3

Viết:
    
    
    RetryPolicy

Retry khi:
    
    
    502
    
    503
    
    504
    
    Timeout

Không retry:
    
    
    404
    
    401
    
    400

* * *

## Bài 4

Thiết kế:
    
    
    exceptions/
    
    ├── base.py
    ├── timeout.py
    ├── notfound.py
    ├── forbidden.py
    ├── unauthorized.py
    └── servererror.py

* * *

# Tổng kết

Trong buổi học này, bạn đã nắm được:

  * Kiến trúc `urllib.error`. 
  * Sự khác nhau giữa `URLError` và `HTTPError`. 
  * Cách đọc `code`, `reason`, `headers`, `body`. 
  * Phân biệt lỗi mạng và lỗi HTTP. 
  * Thiết kế `ExceptionMapper`. 
  * Xây dựng hệ thống ngoại lệ cho `HttpClient`. 



* * *

# Chuẩn bị cho buổi tiếp theo

Ở **buổi tiếp theo** , chúng ta sẽ học **`urllib.robotparser`** , bao gồm:

  * Robots.txt là gì? 
  * Quy tắc `User-agent`
  * `Disallow`
  * `Allow`
  * `Crawl-delay`
  * `Request-rate`
  * `Sitemap`
  * Sử dụng `RobotFileParser`
  * Tích hợp kiểm tra robots.txt vào Web Scraper 



Đây là chủ đề quan trọng nếu bạn muốn xây dựng crawler hoặc scraper tuân thủ quy tắc của website.

