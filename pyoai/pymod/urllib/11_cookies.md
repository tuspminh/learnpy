# Khóa học urllib Deep Dive

# Buổi 11 (phiên bản chuyên đề): Cookies Deep Dive với `urllib` và `http.cookiejar`

> Đây là một trong những chủ đề quan trọng nhất khi xây dựng crawler, web scraper, trình tự động đăng nhập hoặc HTTP Client chuyên nghiệp.

Rất nhiều người nghĩ Cookie chỉ là:
    
    
    Cookie: sessionid=abcdef

Nhưng thực tế, Cookie là **một hệ thống quản lý trạng thái (State Management)** của HTTP.

Sau buổi này, bạn sẽ hiểu gần như toàn bộ cách Cookie hoạt động.

* * *

# Mục tiêu

Sau buổi này bạn sẽ:

  * Hiểu Cookie hoạt động như thế nào. 
  * Hiểu Session Cookie. 
  * Hiểu Persistent Cookie. 
  * Hiểu CookieJar. 
  * Biết cách lưu Cookie ra file. 
  * Biết cách nạp Cookie. 
  * Thiết kế CookieManager. 
  * Hiểu kiến trúc Cookie của urllib. 



* * *

# 1\. HTTP là Stateless

HTTP không nhớ gì cả.

Ví dụ:

Request 1
    
    
    GET /login

↓

Server

↓

Response

* * *

Request 2
    
    
    GET /profile

Server không biết đây có phải cùng người dùng hay không.

* * *

# 2\. Cookie giải quyết vấn đề gì?

Server:
    
    
    Login OK

↓

Sinh:
    
    
    sessionid=ABC123

↓

Gửi về trình duyệt

↓

Lần sau trình duyệt gửi lại

↓

Server nhận ra
    
    
    À
    
    Đây là người vừa đăng nhập

* * *

# 3\. Cookie ở đâu?

Server Response
    
    
    HTTP/1.1 200 OK
    
    Set-Cookie:
    sessionid=ABC123

Client lưu lại.

Request tiếp theo
    
    
    GET /profile
    
    Cookie:
    sessionid=ABC123

* * *

# 4\. Set-Cookie

Ví dụ:
    
    
    Set-Cookie:
    
    sessionid=ABC123

Server chỉ gửi:
    
    
    Set-Cookie

Client tự lưu.

* * *

# 5\. Cookie Header

Sau này client gửi:
    
    
    Cookie:
    
    sessionid=ABC123

Không còn là:
    
    
    Set-Cookie

Đây là điểm nhiều người mới học hay nhầm.

* * *

# 6\. Một Cookie gồm những gì?

Ví dụ:
    
    
    Set-Cookie:
    
    sessionid=ABC123;
    
    Path=/;
    
    Domain=example.com;
    
    Expires=...
    
    HttpOnly;
    
    Secure

Cookie thực tế có rất nhiều thuộc tính.

* * *

# 7\. Các thuộc tính quan trọng
    
    
    Name
    
    Value
    
    Domain
    
    Path
    
    Expires
    
    Max-Age
    
    Secure
    
    HttpOnly
    
    SameSite

* * *

# 8\. Name & Value

Ví dụ
    
    
    theme=dark

Tên:
    
    
    theme

Giá trị:
    
    
    dark

* * *

# 9\. Domain

Ví dụ
    
    
    example.com

Cookie chỉ gửi tới:
    
    
    example.com

Không gửi sang:
    
    
    google.com

* * *

# 10\. Path

Ví dụ
    
    
    Path=/admin

Cookie chỉ gửi khi truy cập:
    
    
    /admin

Không gửi:
    
    
    /images

* * *

# 11\. Secure
    
    
    Secure

↓

Chỉ gửi qua
    
    
    HTTPS

Không gửi HTTP.

* * *

# 12\. HttpOnly

Cookie:
    
    
    HttpOnly

↓

JavaScript
    
    
    Không đọc được

Giảm nguy cơ đánh cắp cookie qua XSS.

* * *

# 13\. Session Cookie

Không có:
    
    
    Expires

hoặc
    
    
    Max-Age

↓

Đóng trình duyệt

↓

Cookie biến mất.

* * *

# 14\. Persistent Cookie

Có:
    
    
    Expires

↓

Lưu trên ổ cứng

↓

Mở trình duyệt vẫn còn.

* * *

# 15\. CookieJar

Python có module:
    
    
    import http.cookiejar

Đây là nơi lưu Cookie.

* * *

# 16\. Tạo CookieJar
    
    
    from http.cookiejar import CookieJar
    
    jar = CookieJar()

Lúc này:
    
    
    jar

↓

là kho Cookie.

* * *

# 17\. HTTPCookieProcessor

CookieJar chưa làm gì cả.

Cần:
    
    
    from urllib.request import HTTPCookieProcessor
    
    processor = HTTPCookieProcessor(jar)

* * *

# 18\. build_opener
    
    
    from urllib.request import build_opener
    
    opener = build_opener(
        processor
    )

Giờ đây:
    
    
    Response
    
    ↓
    
    Set-Cookie
    
    ↓
    
    CookieJar
    
    ↓
    
    Request sau
    
    ↓
    
    Cookie

Mọi thứ diễn ra tự động.

* * *

# 19\. opener.open()
    
    
    response = opener.open(url)

Không cần tự thêm:
    
    
    Cookie:

`HTTPCookieProcessor` sẽ làm việc đó.

* * *

# 20\. Xem Cookie
    
    
    for cookie in jar:
        print(cookie.name)
        print(cookie.value)

Ví dụ:
    
    
    sessionid
    
    ABC123

* * *

# 21\. Xem đầy đủ
    
    
    for cookie in jar:
    
        print(cookie.domain)
    
        print(cookie.path)
    
        print(cookie.expires)
    
        print(cookie.secure)

Một đối tượng `Cookie` chứa rất nhiều thông tin hữu ích.

* * *

# 22\. Cookie Object
    
    
    Cookie
    │
    ├── name
    ├── value
    ├── domain
    ├── path
    ├── expires
    ├── secure
    ├── version
    └── ...

* * *

# 23\. MozillaCookieJar
    
    
    from http.cookiejar import MozillaCookieJar
    
    jar = MozillaCookieJar("cookies.txt")

Có thể:
    
    
    jar.save()

↓

Lưu file.

* * *

# 24\. Load Cookie
    
    
    jar.load()

↓

Cookie quay lại.

Điều này rất hữu ích để giữ phiên đăng nhập giữa các lần chạy chương trình.

* * *

# 25\. LWP CookieJar
    
    
    from http.cookiejar import LWPCookieJar

Khác:
    
    
    Mozilla
    
    ↓
    
    cookies.txt

LWP dùng định dạng riêng, phổ biến trong một số công cụ dòng lệnh.

* * *

# 26\. Lưu Cookie
    
    
    jar.save(
        ignore_discard=True,
        ignore_expires=True
    )

Giải thích:

  * `ignore_discard=True`: lưu cả Session Cookie. 
  * `ignore_expires=True`: lưu cả Cookie đã hết hạn (chỉ nên dùng khi thực sự cần, ví dụ để phân tích hoặc debug). 



* * *

# 27\. Load Cookie
    
    
    jar.load(
        ignore_discard=True,
        ignore_expires=True
    )

* * *

# 28\. Kiến trúc Cookie
    
    
    Response
    
    ↓
    
    HTTPCookieProcessor
    
    ↓
    
    CookieJar
    
    ↓
    
    File
    
    ↓
    
    Lần chạy sau
    
    ↓
    
    CookieJar
    
    ↓
    
    Request

Đây là vòng đời đầy đủ của Cookie.

* * *

# 29\. Thiết kế CookieManager

Không nên để mọi nơi gọi trực tiếp `CookieJar`.

Ta tạo lớp bao bọc:
    
    
    class CookieManager:
    
        def __init__(self):
            self.jar = MozillaCookieJar()

* * *

# 30\. save()
    
    
    class CookieManager:
    
        ...
    
        def save(self, filename):
    
            self.jar.filename = filename
    
            self.jar.save(
                ignore_discard=True
            )

* * *

# 31\. load()
    
    
    class CookieManager:
    
        ...
    
        def load(self, filename):
    
            self.jar.filename = filename
    
            self.jar.load(
                ignore_discard=True
            )

Bạn có thể kiểm tra file có tồn tại hay không trước khi gọi `load()` để tránh ngoại lệ.

* * *

# 32\. Tích hợp HttpClient
    
    
    client = HttpClient(
        cookie_manager=...
    )

Bên trong:
    
    
    CookieManager
    
    ↓
    
    CookieJar
    
    ↓
    
    HTTPCookieProcessor
    
    ↓
    
    build_opener()
    
    ↓
    
    open()

* * *

# 33\. Kiến trúc Framework
    
    
    HttpClient
    │
    ├── AuthProvider
    ├── RetryPolicy
    ├── CookieManager
    ├── Downloader
    ├── MultipartEncoder
    └── ApiClient

Cookie trở thành một thành phần độc lập.

* * *

# 34\. Kiểm tra Cookie
    
    
    for cookie in jar:
    
        print(
            f"{cookie.name}={cookie.value}"
        )

Ví dụ:
    
    
    sessionid=ABC123
    
    csrftoken=xyz
    
    theme=dark

* * *

# 35\. Xóa Cookie
    
    
    jar.clear()

Hoặc:
    
    
    jar.clear(
        domain="example.com"
    )

Bạn cũng có thể xóa theo `domain`, `path` và `name` nếu muốn loại bỏ một cookie cụ thể.

* * *

# 36\. Session mô phỏng
    
    
    Login
    
    ↓
    
    CookieJar
    
    ↓
    
    Request 1
    
    ↓
    
    Request 2
    
    ↓
    
    Request 3
    
    ↓
    
    Logout
    
    ↓
    
    clear()

Đây là cách các crawler duy trì trạng thái đăng nhập.

* * *

# 37\. Cookie và Redirect

Server:
    
    
    302

↓
    
    
    Set-Cookie

↓
    
    
    Location

↓

Trang mới

Nếu dùng `HTTPCookieProcessor` kết hợp `HTTPRedirectHandler`, cookie sẽ được lưu trước và tự động gửi ở request tiếp theo nếu phù hợp với domain/path.

* * *

# Những lỗi thường gặp

## 1\. Tự thêm Header Cookie

Sai:
    
    
    headers = {
        "Cookie":
            "sessionid=..."
    }

Nếu đã dùng `CookieJar`, hãy để `HTTPCookieProcessor` quản lý. Chỉ tự thêm `Cookie` trong những trường hợp rất đặc biệt.

* * *

## 2\. Quên HTTPCookieProcessor
    
    
    jar = CookieJar()

↓

Không dùng.

↓

Cookie không hoạt động.

* * *

## 3\. Quên save()

Chương trình kết thúc.

↓

Cookie mất.

Nếu muốn tái sử dụng ở lần chạy sau, hãy lưu Cookie ra file.

* * *

## 4\. Lưu Session Cookie nhưng không bật `ignore_discard`

Session Cookie sẽ không được ghi ra file.

* * *

# Bài tập

## Bài 1

Tạo:
    
    
    CookieJar()

Sau đó:

  * mở một website có đặt cookie, 
  * in tất cả cookie trong `jar`. 



* * *

## Bài 2

Đổi sang:
    
    
    MozillaCookieJar

Lưu:
    
    
    cookies.txt

Đóng chương trình.

Mở lại.

Load cookie.

Kiểm tra còn dữ liệu hay không.

* * *

## Bài 3

Viết:
    
    
    CookieManager

Có:

  * load() 
  * save() 
  * clear() 
  * print_all() 



* * *

## Bài 4

Tích hợp `CookieManager` vào `HttpClient`.

Mục tiêu:
    
    
    client = HttpClient()
    
    client.login()
    
    client.save_cookie()
    
    client.load_cookie()

Không cần người dùng tự thao tác với `CookieJar`.

* * *

# Tổng kết

Trong buổi 11, bạn đã học được:

  * Bản chất của Cookie trong giao thức HTTP. 
  * Phân biệt `Set-Cookie` và `Cookie`. 
  * Session Cookie và Persistent Cookie. 
  * `CookieJar`, `MozillaCookieJar`, `LWPCookieJar`. 
  * `HTTPCookieProcessor` và cách tích hợp với `OpenerDirector`. 
  * Thiết kế `CookieManager` để quản lý cookie theo hướng đối tượng. 
  * Cách lưu, nạp và tái sử dụng cookie giữa các lần chạy chương trình. 



* * *

# Chuẩn bị cho buổi 12

Ở **buổi 12** , chúng ta sẽ học **Proxy Deep Dive** , bao gồm:

  * `ProxyHandler`
  * HTTP Proxy và HTTPS Proxy 
  * SOCKS Proxy (thông qua thư viện bổ sung) 
  * Proxy Authentication 
  * Proxy Pool 
  * Proxy Rotation 
  * Thiết kế `ProxyManager`
  * Tích hợp Proxy vào `HttpClient`



Đây là kiến thức rất quan trọng khi xây dựng crawler quy mô lớn hoặc hệ thống thu thập dữ liệu cần phân phối lưu lượng qua nhiều proxy khác nhau.

