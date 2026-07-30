# Khóa học urllib Deep Dive

# Buổi 13: SSL/TLS và HTTPS Deep Dive với `urllib`

> Đây là một trong những chủ đề quan trọng nhất của toàn bộ khóa học.

Rất nhiều lập trình viên sử dụng HTTPS mỗi ngày nhưng chưa thực sự hiểu:

  * SSL là gì? 
  * TLS là gì? 
  * Chứng chỉ số (Certificate) hoạt động ra sao? 
  * Vì sao có lỗi **CERTIFICATE_VERIFY_FAILED**? 
  * `SSLContext` dùng để làm gì? 
  * Làm sao để dùng chứng chỉ client (mTLS)? 
  * Khi nào được phép bỏ qua kiểm tra chứng chỉ? 



Sau buổi này, bạn sẽ hiểu gần như toàn bộ cơ chế HTTPS của `urllib`.

* * *

# Mục tiêu

Sau buổi học này, bạn sẽ:

  * Hiểu SSL và TLS. 
  * Hiểu Certificate. 
  * Hiểu CA. 
  * Hiểu Handshake. 
  * Hiểu SSLContext. 
  * Tùy chỉnh HTTPSHandler. 
  * Dùng Client Certificate. 
  * Thiết kế SSLConfig cho HttpClient. 



* * *

# 1\. HTTP vs HTTPS

HTTP
    
    
    Client
    
    ↓
    
    Server

Mọi dữ liệu truyền dưới dạng rõ (plaintext).

* * *

HTTPS
    
    
    Client
    
    ↓
    
    TLS
    
    ↓
    
    Server

Dữ liệu được mã hóa trước khi truyền.

* * *

# 2\. SSL và TLS

Ngày nay, khi nói "SSL" thực tế thường là **TLS**.

Lịch sử:
    
    
    SSL 2.0
    
    ↓
    
    SSL 3.0
    
    ↓
    
    TLS 1.0
    
    ↓
    
    TLS 1.1
    
    ↓
    
    TLS 1.2
    
    ↓
    
    TLS 1.3

SSL 2.0 và SSL 3.0 đã lỗi thời và không còn được khuyến nghị sử dụng.

* * *

# 3\. HTTPS Handshake

Khi truy cập:
    
    
    https://example.com

Không gửi HTTP ngay.

Trình tự:
    
    
    TCP Connect
    
    ↓
    
    TLS Handshake
    
    ↓
    
    Verify Certificate
    
    ↓
    
    Sinh Session Key
    
    ↓
    
    HTTP Request

* * *

# 4\. Handshake đơn giản
    
    
    Client
    
    ↓
    
    Hello
    
    ↓
    
    Server
    
    ↓
    
    Certificate
    
    ↓
    
    Verify
    
    ↓
    
    Key Exchange
    
    ↓
    
    Encrypted HTTP

Sau khi hoàn tất bắt tay, các bản tin HTTP mới được mã hóa bằng khóa phiên.

* * *

# 5\. Certificate là gì?

Certificate giống như:
    
    
    CMND
    
    hoặc
    
    Hộ chiếu

của website.

Ví dụ:
    
    
    example.com

↓

Server chứng minh:
    
    
    "Tôi đúng là example.com"

* * *

# 6\. Certificate chứa gì?

Thông thường:
    
    
    Domain
    
    Issuer
    
    Serial Number
    
    Public Key
    
    Valid From
    
    Valid To

và các thông tin mở rộng khác như Subject Alternative Name (SAN).

* * *

# 7\. CA là gì?

CA:
    
    
    Certificate Authority

Ví dụ:

  * Let's Encrypt 
  * DigiCert 
  * GlobalSign 



CA xác nhận rằng chứng chỉ thuộc về đúng chủ thể.

* * *

# 8\. Chuỗi xác thực
    
    
    Website Certificate
    
    ↓
    
    Intermediate CA
    
    ↓
    
    Root CA

Máy khách kiểm tra chuỗi này trước khi tin tưởng kết nối.

* * *

# 9\. Python xác minh Certificate

Theo mặc định:
    
    
    urlopen(...)

↓

Kiểm tra:

  * Certificate hợp lệ. 
  * Chưa hết hạn. 
  * Đúng hostname. 
  * Chuỗi CA đáng tin cậy. 



Nếu không đạt, kết nối sẽ thất bại.

* * *

# 10\. SSLContext

Mọi cấu hình HTTPS đều xoay quanh:
    
    
    import ssl
    
    context = ssl.create_default_context()

Đây là cách khởi tạo `SSLContext` được khuyến nghị.

* * *

# 11\. HTTPSHandler
    
    
    from urllib.request import HTTPSHandler

Có thể truyền:
    
    
    HTTPSHandler(
        context=context
    )

để sử dụng `SSLContext` tùy chỉnh.

* * *

# 12\. build_opener()
    
    
    from urllib.request import build_opener
    
    opener = build_opener(
    
        HTTPSHandler(
            context=context
        )
    )

Sau đó:
    
    
    opener.open(url)

Mọi kết nối HTTPS sẽ sử dụng context này.

* * *

# 13\. Chứng chỉ tự ký (Self-Signed)

Ví dụ:
    
    
    My Server
    
    ↓
    
    Self Signed

Không được CA công khai xác nhận.

Python sẽ từ chối theo mặc định.

* * *

# 14\. Lỗi thường gặp
    
    
    CERTIFICATE_VERIFY_FAILED

Nghĩa là:

  * chứng chỉ không đáng tin, 
  * hoặc hostname không khớp, 
  * hoặc chuỗi CA không hợp lệ, 
  * hoặc chứng chỉ đã hết hạn. 



* * *

# 15\. Bỏ qua Verify (Chỉ để phát triển)
    
    
    import ssl
    
    context = ssl._create_unverified_context()

Sau đó:
    
    
    HTTPSHandler(
        context=context
    )

⚠️ **Không nên dùng trong môi trường production** , vì điều này vô hiệu hóa việc xác minh chứng chỉ.

* * *

# 16\. Verify CA riêng

Nếu công ty có CA nội bộ:
    
    
    context = ssl.create_default_context(
        cafile="company-ca.pem"
    )

Python sẽ tin tưởng CA đó ngoài các CA mặc định.

* * *

# 17\. Client Certificate (mTLS)

Thông thường:
    
    
    Server
    
    ↓
    
    Xác minh Client?

↓

Client gửi:
    
    
    Certificate

Đây gọi là:
    
    
    Mutual TLS

hoặc:
    
    
    mTLS

* * *

# 18\. Load Client Certificate
    
    
    context.load_cert_chain(
    
        certfile="client.crt",
    
        keyfile="client.key"
    )

Bây giờ client có thể chứng minh danh tính với server.

* * *

# 19\. Thiết kế SSLConfig

Thay vì:
    
    
    context = ...

khắp nơi.

Ta tạo:
    
    
    class SSLConfig:
        ...

* * *

# 20\. Thuộc tính
    
    
    class SSLConfig:
    
        verify = True
    
        cafile = None
    
        certfile = None
    
        keyfile = None

Có thể mở rộng thêm:

  * `cadata`
  * `check_hostname`
  * `minimum_tls_version`



* * *

# 21\. create_context()
    
    
    class SSLConfig:
    
        def create_context(
            self
        ):
    
            ...

↓

Trả về:
    
    
    SSLContext

Đây là nơi tập trung toàn bộ logic cấu hình TLS.

* * *

# 22\. Tích hợp HttpClient
    
    
    client = HttpClient(
    
        ssl_config=...
    )

Bên trong:
    
    
    SSLConfig
    
    ↓
    
    SSLContext
    
    ↓
    
    HTTPSHandler
    
    ↓
    
    build_opener()

* * *

# 23\. Chỉ định phiên bản TLS

Ví dụ:
    
    
    import ssl
    
    context = ssl.create_default_context()
    
    context.minimum_version = ssl.TLSVersion.TLSv1_2

Điều này giúp loại bỏ các phiên bản TLS cũ.

* * *

# 24\. Kiểm tra Hostname

Theo mặc định:
    
    
    context.check_hostname

↓
    
    
    True

Python sẽ xác minh:
    
    
    example.com

có khớp với chứng chỉ hay không.

* * *

# 25\. Cipher Suites

TLS sử dụng:
    
    
    Cipher

để mã hóa dữ liệu.

Ví dụ:
    
    
    AES
    
    ChaCha20

Thông thường không cần chỉnh sửa; hãy để hệ điều hành và Python chọn bộ mã mạnh mặc định.

* * *

# 26\. Kiến trúc HTTPS
    
    
    HttpClient
    
    ↓
    
    SSLConfig
    
    ↓
    
    SSLContext
    
    ↓
    
    HTTPSHandler
    
    ↓
    
    TLS
    
    ↓
    
    Server

* * *

# 27\. Certificate Pinning

Một kỹ thuật nâng cao:
    
    
    Server
    
    ↓
    
    Certificate
    
    ↓
    
    SHA256 Fingerprint
    
    ↓
    
    Compare

Nếu fingerprint thay đổi bất ngờ:
    
    
    Reject

Điều này giúp giảm nguy cơ tấn công nếu CA bị xâm phạm, nhưng cũng làm tăng chi phí bảo trì khi chứng chỉ được thay mới.

* * *

# 28\. Thiết kế Framework
    
    
    httpclient/
    
    ├── sslconfig.py
    
    ├── auth.py
    
    ├── retry.py
    
    ├── cookies.py
    
    ├── proxy.py
    
    ├── multipart.py
    
    ├── client.py
    
    └── response.py

* * *

# 29\. Không nên Disable SSL

Sai:
    
    
    ssl._create_unverified_context()

cho:
    
    
    Production

Đúng:
    
    
    create_default_context()

Hoặc cấu hình CA phù hợp.

* * *

# 30\. Những lỗi thường gặp

## 1\. Dùng Self-Signed nhưng không thêm CA

↓
    
    
    CERTIFICATE_VERIFY_FAILED

* * *

## 2\. Disable Verify trong Production

↓

Nguy cơ:
    
    
    MITM Attack

(Machine-in-the-Middle)

* * *

## 3\. Hard-code đường dẫn chứng chỉ

Sai:
    
    
    certfile = "/home/user/..."

Nên:

  * đọc từ file cấu hình, 
  * biến môi trường, 
  * hoặc tham số khởi tạo. 



* * *

## 4\. Quên nạp Client Certificate

Nếu server yêu cầu mTLS:

↓
    
    
    Handshake Failed

* * *

# Bài tập

## Bài 1

Viết:
    
    
    SSLConfig

Hỗ trợ:

  * verify 
  * cafile 
  * certfile 
  * keyfile 
  * create_context() 



* * *

## Bài 2

Tạo:
    
    
    HTTPSHandler(
        context=...
    )

sử dụng `SSLConfig`.

* * *

## Bài 3

Tích hợp:
    
    
    HttpClient(
    
        ssl_config=...
    )

để mọi kết nối HTTPS đều dùng chung cấu hình.

* * *

## Bài 4

Viết ví dụ:
    
    
    SSLConfig(
    
        verify=False
    )

và ghi chú rõ:
    
    
    Development Only

Không sử dụng trong production.

* * *

# Góc nhìn kiến trúc

Sau 13 buổi, framework của chúng ta đã có cấu trúc như sau:
    
    
    HttpClient
    │
    ├── RetryPolicy
    ├── AuthProvider
    ├── CookieManager
    ├── ProxyManager
    ├── SSLConfig
    ├── MultipartEncoder
    ├── Downloader
    └── Response

Mỗi thành phần quản lý một khía cạnh của giao thức HTTP/HTTPS:

  * **RetryPolicy** : tăng khả năng chịu lỗi. 
  * **AuthProvider** : xác thực. 
  * **CookieManager** : duy trì trạng thái phiên. 
  * **ProxyManager** : định tuyến qua proxy. 
  * **SSLConfig** : bảo mật kết nối. 
  * **MultipartEncoder** : upload dữ liệu. 
  * **Downloader** : tải tệp. 



Đây là kiến trúc gần với nhiều HTTP client hiện đại.

* * *

# Tổng kết

Trong buổi 13, bạn đã học:

  * Phân biệt HTTP và HTTPS. 
  * SSL, TLS và quá trình Handshake. 
  * Chứng chỉ số (Certificate) và CA. 
  * `ssl.SSLContext` và `HTTPSHandler`. 
  * Chứng chỉ tự ký (Self-Signed). 
  * Mutual TLS (mTLS). 
  * Thiết kế `SSLConfig`. 
  * Các lưu ý bảo mật khi làm việc với HTTPS. 



* * *

# Chuẩn bị cho buổi 14

Ở **buổi 14** , chúng ta sẽ đi sâu vào **HTTP Compression và Content Encoding** , bao gồm:

  * `Accept-Encoding`
  * `Content-Encoding`
  * Gzip 
  * Deflate 
  * Brotli (thông qua thư viện ngoài) 
  * Giải nén dữ liệu trong `urllib`
  * Streaming Decompression 
  * Thiết kế `CompressionHandler`



Sau buổi này, bạn sẽ hiểu cách các website hiện đại giảm băng thông và cách xây dựng `HttpClient` tự động xử lý dữ liệu nén một cách hiệu quả.

