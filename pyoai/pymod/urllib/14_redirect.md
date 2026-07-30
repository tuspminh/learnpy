# Khóa học urllib Deep Dive

# Chuyên đề: Redirect Deep Dive với `urllib`

> Redirect (chuyển hướng) là một trong những cơ chế quan trọng nhất của HTTP. Mặc dù `urllib` tự động xử lý redirect, nhưng để xây dựng HTTP Client, Web Scraper hoặc API Client chuyên nghiệp, bạn cần hiểu rõ cách nó hoạt động.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu Redirect là gì. 
  * Hiểu các mã trạng thái 301, 302, 303, 307, 308. 
  * Hiểu `HTTPRedirectHandler`. 
  * Tùy chỉnh hành vi redirect. 
  * Giới hạn số lần redirect. 
  * Phát hiện vòng lặp redirect. 
  * Thiết kế `RedirectPolicy`. 



* * *

# 1\. Redirect là gì?

Ví dụ:

Người dùng truy cập:
    
    
    http://example.com

Server trả về:
    
    
    HTTP/1.1 301 Moved Permanently
    Location: https://example.com

Client sẽ tự động gửi request mới đến:
    
    
    https://example.com

* * *

# 2\. Luồng Redirect
    
    
    Client
       │
       ▼
    GET /old-page
       │
       ▼
    301 Moved Permanently
    Location: /new-page
       │
       ▼
    GET /new-page
       │
       ▼
    200 OK

* * *

# 3\. Header `Location`

Redirect luôn đi kèm header:
    
    
    Location: https://new.example.com/page

Hoặc:
    
    
    Location: /login

`Location` có thể là:

  * URL tuyệt đối 
  * URL tương đối 



`urllib` sẽ tự chuyển URL tương đối thành URL đầy đủ.

* * *

# 4\. Các mã Redirect

Status| Ý nghĩa  
---|---  
301| Moved Permanently  
302| Found  
303| See Other  
307| Temporary Redirect  
308| Permanent Redirect  
  
Đây là những mã phổ biến nhất.

* * *

# 5\. 301
    
    
    Old URL
    
    ↓
    
    New URL
    
    ↓
    
    Luôn dùng URL mới

Ví dụ:
    
    
    http://example.com
    
    ↓
    
    https://example.com

Search Engine cũng cập nhật URL mới.

* * *

# 6\. 302
    
    
    Old URL
    
    ↓
    
    Temporary
    
    ↓
    
    Sau này có thể quay lại

Ví dụ:

Website bảo trì.

* * *

# 7\. 303

Sau khi:
    
    
    POST
    
    ↓
    
    Server
    
    ↓
    
    303
    
    ↓
    
    GET

Rất phổ biến sau khi submit form.

Ví dụ:
    
    
    Đăng nhập
    
    ↓
    
    Redirect
    
    ↓
    
    Trang chủ

* * *

# 8\. 307

307 yêu cầu:
    
    
    POST
    
    ↓
    
    POST

Không được đổi thành GET.

Điều này khác với 302/303.

* * *

# 9\. 308

Giống:
    
    
    301

Nhưng:
    
    
    POST
    
    ↓
    
    POST

Method vẫn được giữ nguyên.

* * *

# 10\. urllib tự Redirect

Ví dụ:
    
    
    from urllib.request import urlopen
    
    response = urlopen(url)

Nếu server trả:
    
    
    301

↓

`urllib`

↓

Request mới

↓

200

Người dùng gần như không nhận thấy quá trình chuyển hướng.

* * *

# 11\. HTTPRedirectHandler

Đây là handler chịu trách nhiệm Redirect.
    
    
    from urllib.request import HTTPRedirectHandler

Nó được `build_opener()` thêm vào mặc định.

* * *

# 12\. Kiến trúc
    
    
    Request
    
    ↓
    
    HTTPHandler
    
    ↓
    
    301
    
    ↓
    
    HTTPRedirectHandler
    
    ↓
    
    Request mới
    
    ↓
    
    HTTPHandler
    
    ↓
    
    200

* * *

# 13\. Kiểm tra Redirect

Ví dụ:
    
    
    response = urlopen(url)
    
    print(response.geturl())

Nếu bị Redirect:
    
    
    https://new-site.com

`geturl()` trả về URL cuối cùng.

* * *

# 14\. URL ban đầu
    
    
    request = Request(url)

↓
    
    
    request.full_url

Ví dụ:
    
    
    http://example.com

Sau redirect:
    
    
    response.geturl()

↓
    
    
    https://example.com

* * *

# 15\. Phát hiện Redirect
    
    
    if response.geturl() != url:
        print("Redirected")

Đây là cách đơn giản để biết request đã bị chuyển hướng.

* * *

# 16\. Custom RedirectHandler
    
    
    from urllib.request import HTTPRedirectHandler
    
    class MyRedirectHandler(
        HTTPRedirectHandler
    ):
        pass

* * *

# 17\. redirect_request()

Quan trọng nhất:
    
    
    class MyRedirectHandler(
        HTTPRedirectHandler
    ):
    
        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            ...

Đây là nơi quyết định có tạo request mới hay không.

* * *

# 18\. Log Redirect
    
    
    class LoggingRedirectHandler(
        HTTPRedirectHandler
    ):
    
        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
    
            print(
                f"{code}: "
                f"{req.full_url}"
                f" -> "
                f"{newurl}"
            )
    
            return super().redirect_request(
                req,
                fp,
                code,
                msg,
                headers,
                newurl
            )

* * *

# 19\. Chặn Redirect
    
    
    class NoRedirectHandler(
        HTTPRedirectHandler
    ):
    
        def redirect_request(
            self,
            req,
            fp,
            code,
            msg,
            headers,
            newurl
        ):
            return None

Khi trả về `None`, `urllib` sẽ không tự tạo request mới. Khi đó bạn có thể nhận được phản hồi redirect dưới dạng lỗi hoặc tự xử lý tùy thiết kế.

* * *

# 20\. build_opener()
    
    
    opener = build_opener(
        NoRedirectHandler()
    )

↓
    
    
    opener.open(...)

Bây giờ Redirect không còn tự động.

* * *

# 21\. Theo dõi Redirect Chain

Ví dụ:
    
    
    A
    
    ↓
    
    301
    
    ↓
    
    B
    
    ↓
    
    302
    
    ↓
    
    C
    
    ↓
    
    200

Ta có thể lưu:
    
    
    history = [
        "A",
        "B",
        "C"
    ]

Điều này hữu ích khi debug hoặc phân tích website.

* * *

# 22\. Redirect Loop

Ví dụ:
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    C
    
    ↓
    
    A

↓

Lặp vô hạn.

* * *

# 23\. urllib xử lý thế nào?

`urllib` có giới hạn số lần Redirect.

Nếu vượt quá:

↓
    
    
    HTTPError

để tránh vòng lặp vô hạn.

* * *

# 24\. RedirectPolicy

Thiết kế:
    
    
    class RedirectPolicy:
    
        max_redirects = 10
    
        allow_https = True
    
        allow_http = True

Có thể mở rộng thêm:

  * danh sách domain được phép, 
  * cho phép hay cấm redirect giữa các giao thức. 



* * *

# 25\. HttpClient
    
    
    client = HttpClient(
    
        redirect_policy=...
    )

↓

`RedirectHandler`

↓

Request

* * *

# 26\. Chỉ cho phép HTTPS

Ví dụ:
    
    
    https://api.example.com
    
    ↓
    
    https://cdn.example.com
    
    ✓

* * *

Không cho phép:
    
    
    https://example.com
    
    ↓
    
    http://example.com
    
    ✗

Điều này giúp tránh việc giảm mức độ bảo mật.

* * *

# 27\. Redirect và Cookie

Ví dụ:
    
    
    Login
    
    ↓
    
    302
    
    ↓
    
    Home

Cookie thường được đặt:
    
    
    302 Response
    
    ↓
    
    Set-Cookie

↓

Request tiếp theo

↓

Cookie

Nếu dùng `HTTPCookieProcessor`, cookie sẽ được lưu trước khi thực hiện request tiếp theo.

* * *

# 28\. Redirect và POST

Ví dụ:
    
    
    POST Login
    
    ↓
    
    302
    
    ↓
    
    GET Home

Đây là hành vi phổ biến của nhiều website.

Nhưng:
    
    
    307
    
    ↓
    
    POST
    
    ↓
    
    POST

Method được giữ nguyên.

* * *

# 29\. Redirect và Auth

Một số website:
    
    
    Unauthorized
    
    ↓
    
    302
    
    ↓
    
    Login Page

Nếu scraper chỉ kiểm tra mã trạng thái cuối cùng là `200`, có thể nhầm rằng đã truy cập thành công, trong khi thực tế đã bị chuyển đến trang đăng nhập.

* * *

# 30\. Kiến trúc Framework
    
    
    HttpClient
    
    │
    
    ├── RetryPolicy
    
    ├── AuthProvider
    
    ├── CookieManager
    
    ├── ProxyManager
    
    ├── RedirectPolicy
    
    ├── SSLConfig
    
    └── MultipartEncoder

Redirect trở thành một module độc lập.

* * *

# Những lỗi thường gặp

## 1\. Không kiểm tra URL cuối
    
    
    response.status

↓

200

↓

Tưởng thành công.

Nhưng thực tế:
    
    
    302
    
    ↓
    
    Login

↓

200

Luôn kiểm tra thêm:
    
    
    response.geturl()

* * *

## 2\. Redirect Loop
    
    
    A
    
    ↓
    
    B
    
    ↓
    
    A
    
    ↓
    
    B

Nếu tự viết HTTP Client, hãy luôn có giới hạn số lần redirect.

* * *

## 3\. Mất Header Authorization

Một số server yêu cầu xác thực.
    
    
    Redirect
    
    ↓
    
    Request mới
    
    ↓
    
    Authorization mất

Trong thực tế, nhiều HTTP client sẽ **không** chuyển tiếp `Authorization` khi redirect sang **host khác** để tránh rò rỉ thông tin xác thực.

* * *

## 4\. POST bị đổi thành GET
    
    
    302
    
    ↓
    
    GET

Không phải lúc nào cũng đúng.

Hãy phân biệt:

  * 302 
  * 303 
  * 307 
  * 308 



* * *

# Bài tập

## Bài 1

Viết:
    
    
    LoggingRedirectHandler

In:
    
    
    301
    
    old_url
    
    ↓
    
    new_url

* * *

## Bài 2

Viết:
    
    
    NoRedirectHandler

Không cho phép Redirect.

* * *

## Bài 3

Viết:
    
    
    RedirectPolicy

Có:

  * `max_redirects`
  * `allow_https`
  * `allow_http`



* * *

## Bài 4

Tích hợp:
    
    
    HttpClient(
    
        redirect_policy=...
    )

để kiểm soát redirect tập trung.

* * *

# Góc nhìn thiết kế

Nếu xem toàn bộ `urllib`, bạn sẽ thấy Redirect không hoạt động độc lập mà phối hợp với nhiều thành phần khác:
    
    
    Request
        │
        ▼
    AuthHandler
        │
        ▼
    CookieHandler
        │
        ▼
    RedirectHandler
        │
        ▼
    HTTPHandler
        │
        ▼
    Response

Một redirect có thể:

  * nhận `Set-Cookie`, 
  * yêu cầu xác thực lại, 
  * kích hoạt retry nếu lỗi, 
  * thay đổi URL đích. 



Đó là lý do các HTTP client hiện đại thường thiết kế Redirect thành một **chính sách (Policy)** thay vì chỉ là một đoạn mã xử lý trạng thái HTTP.

* * *

# Tổng kết

Trong chuyên đề này, bạn đã học:

  * Cơ chế Redirect của HTTP. 
  * Ý nghĩa và sự khác nhau giữa 301, 302, 303, 307 và 308. 
  * Vai trò của `HTTPRedirectHandler`. 
  * Cách tạo `Custom RedirectHandler`. 
  * Cách phát hiện và ghi lại chuỗi redirect. 
  * Cách chặn redirect và tự xử lý. 
  * Thiết kế `RedirectPolicy` để tích hợp vào `HttpClient`. 



Đây là một mảnh ghép quan trọng để hoàn thiện một HTTP client hoặc web crawler chuyên nghiệp dựa trên `urllib`.

