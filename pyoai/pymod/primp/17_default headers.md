# Buổi 17 — Default Headers

Ở Buổi 16 chúng ta đã xây được mô hình:

```text
PrimpFetcher
    │
    └── 1 long-lived Client
             │
             └── nhiều requests
```

Hôm nay chúng ta tiếp tục với một vấn đề rất thực tế:

> Nếu **mọi request** đều cần một số header giống nhau thì có cần truyền `headers=` ở từng request không?

Mục tiêu:

```text
PrimpFetcher
      │
      ▼
Primp Client
      │
      ├── Default Headers
      │
      ├── GET
      ├── POST
      ├── GET
      └── GET
```

---

# 1. Vấn đề lặp lại `headers=`

Ví dụ:

```python
import primp


client = primp.Client()

response = client.get(
    "https://example.com/a",
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Accept": "text/html",
    },
)

response = client.get(
    "https://example.com/b",
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Accept": "text/html",
    },
)

response = client.get(
    "https://example.com/c",
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Accept": "text/html",
    },
)
```

Có vấn đề:

```text
Accept-Language  → lặp
Accept            → lặp
```

Crawler có thể có hàng nghìn request.

Không nên viết như vậy.

---

# 2. Default Header là gì?

Ta muốn cấu hình một lần:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Accept": "text/html",
    }
)
```

Sau đó:

```python
client.get(url1)
client.get(url2)
client.get(url3)
```

cùng sử dụng cấu hình header mặc định.

Điểm quan trọng là **hãy kiểm tra API của phiên bản `primp` bạn đang cài**, vì tên/tham số constructor có thể thay đổi giữa các phiên bản. Trong các binding/SDK dựa trên primp hiện nay, khái niệm `Default Headers` cũng được hỗ trợ ở cấp client. ([GitHub][1])

Với Python `primp`, nếu môi trường của bạn chấp nhận `headers=` ở `Client`, đây là cách ta sử dụng trong bài học:

```python
import primp


client = primp.Client(
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Accept": "text/html",
    }
)
```

Nếu bản `primp` của bạn không nhận `headers` ở constructor, **đừng tự suy đoán API**; khi đó ta giữ header ở `PrimpFetcher` và truyền xuống từng request.

---

# 3. Default Header và Request Header

Có hai tầng:

```text
Client
 └── Default Headers
          │
          ▼
       Request
       └── Request Headers
```

Ví dụ:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN",
        "Accept": "text/html",
    }
)

response = client.get(
    "https://example.com",
    headers={
        "Referer": "https://google.com",
    },
)
```

Ý tưởng:

```text
Default:
    Accept-Language
    Accept

Request-specific:
    Referer
```

---

# 4. Tại sao cần hai tầng?

Trong Novel Crawler, một số header gần như cố định:

```text
Accept
Accept-Language
```

nhưng một số header phụ thuộc request:

```text
Referer
Authorization
Content-Type
```

Ví dụ:

```text
GET chapter 1
    Referer = novel page

GET chapter 2
    Referer = novel page

GET image
    Referer = chapter page
```

Do đó không nên biến mọi header thành default.

---

# 5. Header nào nên là Default?

Một cách phân loại thực tế:

### Có thể default

```text
Accept
Accept-Language
```

và các header ứng dụng thực sự muốn gửi nhất quán.

### Có thể cấu hình theo crawler/client

```text
User-Agent
```

nhưng cần đặc biệt chú ý khi dùng browser impersonation — ta sẽ học sâu hơn ở Phần III.

### Thường nên request-specific

```text
Referer
Authorization
Content-Type
Content-Length
Cookie
```

Một số header trong nhóm cuối còn được HTTP client tự sinh/quản lý, vì vậy **không nên tùy tiện tự đặt**.

---

# 6. `User-Agent` có phải Default Header không?

Có thể.

Ví dụ:

```python
client = primp.Client(
    headers={
        "User-Agent": "NovelCrawler/1.0",
    }
)
```

Nhưng cần nhớ:

```text
User-Agent
    ≠
Browser Fingerprint
```

Đây là kiến thức rất quan trọng cho các buổi:

```text
21. Vì sao cần impersonation
22. Chrome fingerprint
...
27. Headers + fingerprint
```

Một chuỗi:

```text
User-Agent: Chrome/...
```

không biến HTTP client thành Chrome.

Browser impersonation còn liên quan tới TLS/HTTP behavior và nhiều đặc điểm khác.

---

# 7. Default Headers trong `PrimpFetcher`

Thay vì để Application biết `primp`:

```python
class PrimpFetcher:

    def __init__(self):

        self.client = primp.Client(
            headers={
                "Accept-Language": "vi-VN",
            }
        )
```

Application chỉ biết:

```text
Fetcher
```

Điều này phù hợp architecture của chúng ta.

---

# 8. Xây `PrimpFetcher`

Ví dụ:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
    ):
        self.client = primp.Client(
            headers={
                "Accept": "text/html",
                "Accept-Language": "vi-VN,vi;q=0.9",
            }
        )

        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        timeout: float | None = None,
        headers: dict[str, str] | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            timeout=timeout,
            headers=headers,
        )
```

Bây giờ:

```python
fetcher = PrimpFetcher()

response = fetcher.get(
    "https://httpbin.org/headers"
)
```

---

# 9. Test với httpbin

Tạo:

```text
lesson_17.py
```

```python
import primp


def main():

    client = primp.Client(
        headers={
            "Accept": "text/html",
            "Accept-Language": "vi-VN,vi;q=0.9",
        }
    )

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.text)


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python lesson_17.py
```

`httpbin` sẽ trả lại các request headers mà server nhìn thấy.

Đây là cách tốt để **kiểm tra thực tế** thay vì chỉ đoán.

---

# 10. Default + Request-specific

Ví dụ:

```python
import primp


client = primp.Client(
    headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    }
)


response = client.get(
    "https://httpbin.org/headers",
    headers={
        "X-Crawler-Request": "chapter",
    },
)

print(response.text)
```

Conceptually:

```text
Client defaults
├── Accept
└── Accept-Language

        +

Request headers
└── X-Crawler-Request

        ↓

Final request
├── Accept
├── Accept-Language
└── X-Crawler-Request
```

Cách merge cụ thể và ưu tiên khi trùng tên header phụ thuộc API của client/version, nên với những header quan trọng ta nên test bằng `httpbin` thay vì giả định.

---

# 11. Nếu trùng header thì sao?

Ví dụ:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN",
    }
)

response = client.get(
    url,
    headers={
        "Accept-Language": "en-US",
    },
)
```

Ta có:

```text
Default:
Accept-Language = vi-VN

Request:
Accept-Language = en-US
```

Thông thường request-level configuration được thiết kế để override cấu hình mặc định cùng tên; đây cũng là pattern phổ biến trong HTTP client/SDK. ([GitHub][2])

Nhưng với `primp` cụ thể, hãy test trên version đang cài nếu logic này ảnh hưởng crawler production.

---

# 12. Đừng tự tạo `Content-Length`

Ví dụ **không nên**:

```python
headers = {
    "Content-Length": "123",
}
```

Khi gửi body, HTTP client thường có thể tự tính.

Tương tự với:

```text
Host
Content-Length
Transfer-Encoding
multipart boundary
```

Không nên tùy tiện hard-code.

Python HTTP stack cũng có cơ chế tự xử lý `Content-Length`/`Transfer-Encoding` dựa trên body trong các trường hợp thích hợp. ([GitHub][3])

---

# 13. `Content-Type` thì sao?

`Content-Type` phụ thuộc body.

Ví dụ JSON:

```python
client.post(
    url,
    json={
        "title": "Hello",
    }
)
```

Client có thể xác định body là JSON và thiết lập content type phù hợp.

Form:

```python
client.post(
    url,
    data={
        "username": "alice",
    }
)
```

lại là một loại encoding khác.

Do đó:

```text
Content-Type
```

thường **không nên đưa vào default headers chung** cho tất cả request.

Nếu bạn đặt:

```python
"Content-Type": "application/json"
```

làm default rồi sau đó gửi form:

```python
data={...}
```

thì bạn có thể tạo ra cấu hình sai.

---

# 14. Sai lầm rất phổ biến

Ví dụ:

```python
client = primp.Client(
    headers={
        "Content-Type": "application/json",
    }
)
```

Sau đó:

```python
client.post(
    login_url,
    data={
        "username": "alice",
        "password": "123",
    },
)
```

Bạn đã tạo conflict về mặt semantics:

```text
Body:
form data

Header:
application/json
```

Đừng làm vậy.

---

# 15. Default Headers ≠ Cookies

Chúng ta đã học Cookies ở Buổi 9.

Không nên nghĩ:

```python
headers={
    "Cookie": "session=abc123"
}
```

là cách quản lý session tốt nhất.

Nếu client có cookie store/jar:

```text
Client
 ├── Default Headers
 │
 └── Cookie State
```

Cookies là **state của session**, còn default headers là **cấu hình request**.

Hai khái niệm khác nhau.

---

# 16. Default Headers ≠ Authentication

Buổi 13 chúng ta học:

```text
Authorization
```

Ví dụ:

```python
headers={
    "Authorization": "Bearer ..."
}
```

Có thể cấu hình ở client-level trong một số thiết kế.

Nhưng với crawler, hãy cẩn thận.

Nếu:

```text
Client
    Authorization = Token A
```

rồi client được dùng để truy cập:

```text
site A
site B
site C
```

thì có nguy cơ gửi credential sai domain/context.

Vì vậy authentication nên được thiết kế có chủ đích, không phải cứ thấy header lặp lại là đưa vào global default.

---

# 17. Default Headers và Novel Crawler

Một cấu hình đơn giản:

```python
DEFAULT_HEADERS = {
    "Accept": "text/html",
    "Accept-Language": "vi-VN,vi;q=0.9",
}
```

Fetcher:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        timeout: float = 10,
    ):
        self.client = primp.Client(
            headers=DEFAULT_HEADERS,
        )

        self.default_timeout = timeout

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ):

        if timeout is None:
            timeout = self.default_timeout

        return self.client.get(
            url,
            headers=headers,
            timeout=timeout,
        )
```

---

# 18. Nhưng Plugin Crawler thì sao?

Đây mới là vấn đề quan trọng với project của bạn.

Ta có:

```text
Novel Source A
Novel Source B
Novel Source C
```

Các site có thể cần header khác nhau.

Không nên:

```text
Global Client
    ↓
mọi site
    ↓
cùng headers
```

Có thể thiết kế:

```text
Crawler
 │
 ├── Source A Fetcher
 │      └── Client A
 │
 ├── Source B Fetcher
 │      └── Client B
 │
 └── Source C Fetcher
        └── Client C
```

hoặc:

```text
Crawler
    ↓
PrimpFetcher
    ↓
RequestOptions
```

Ta chưa quyết định architecture cuối cùng ở bài này.

Đến Phần V, khi xây:

```text
44 PrimpFetcher
47 Browser Profile Strategy
```

chúng ta sẽ làm rõ hơn.

---

# 19. Default Headers và Browser Impersonation

Đây là điểm nối tới Phần III.

Ví dụ:

```python
client = primp.Client(
    impersonate="chrome_146",
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
    },
)
```

Conceptually:

```text
impersonate
    ↓
Browser behavior / fingerprint

headers
    ↓
HTTP header configuration
```

Hai thứ bổ sung cho nhau:

```text
Browser Impersonation
        +
Application Headers
```

nhưng:

```text
headers ≠ fingerprint
```

Đây sẽ là chủ đề rất quan trọng từ Buổi 21 trở đi.

---

# 20. Thiết kế tốt hơn một chút

Ta có thể tạo cấu hình:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetcherConfig:

    timeout: float = 10

    headers: dict[str, str] | None = None
```

Sau đó:

```python
import primp


class PrimpFetcher:

    def __init__(
        self,
        config: FetcherConfig,
    ):

        headers = config.headers or {}

        self.client = primp.Client(
            headers=headers,
        )

        self.default_timeout = config.timeout
```

Sử dụng:

```python
config = FetcherConfig(
    timeout=15,
    headers={
        "Accept": "text/html",
        "Accept-Language": "vi-VN",
    },
)

fetcher = PrimpFetcher(config)
```

Nhưng **chưa cần** đưa abstraction này vào production architecture ngay.

Ở giai đoạn học hiện tại,:

```python
PrimpFetcher(...)
```

vẫn đủ.

---

# 21. Header configuration nên nằm ở đâu?

Architecture:

```text
                    Application
                         │
                         ▼
                      Fetcher
                         │
                         ▼
                   PrimpFetcher
                         │
              ┌──────────┴──────────┐
              │                     │
       Client Config          Request Config
              │                     │
        Default Headers       Per-request Headers
              │                     │
              └──────────┬──────────┘
                         ▼
                       primp
```

Parser:

```text
Parser
  │
  └── KHÔNG quản lý headers
```

Parser chỉ:

```text
HTML
 ↓
Parse
 ↓
Novel / Chapter
```

Fetcher mới quản lý HTTP.

---

# 22. Một nguyên tắc rất quan trọng

Đừng biến:

```python
headers={
    ...
}
```

thành một "sọt rác" chứa mọi thứ.

Ví dụ xấu:

```python
DEFAULT_HEADERS = {
    "Accept": "...",
    "User-Agent": "...",
    "Cookie": "...",
    "Authorization": "...",
    "Content-Type": "...",
    "Content-Length": "...",
    "Referer": "...",
}
```

Tất cả đều global.

Đây sẽ tạo coupling rất mạnh.

Thay vào đó:

```text
Default
├── stable request headers
│
Request-specific
├── Referer
├── Content-Type
└── special headers

State
└── Cookies

Authentication
└── Auth strategy
```

---

# 23. Bài tập thực hành

### Bài 1

Viết:

```python
client = primp.Client(...)
```

với:

```text
Accept
Accept-Language
User-Agent
```

Sau đó gọi:

```text
https://httpbin.org/headers
```

và xem server nhận được gì.

---

### Bài 2

Tạo:

```python
class PrimpFetcher:
    ...
```

với:

```python
fetcher.get(url)
```

không cần truyền lại:

```python
Accept
Accept-Language
```

mỗi lần.

---

### Bài 3

Thử:

```python
default_headers = {
    "X-Test": "default",
}
```

và request:

```python
headers = {
    "X-Test": "request",
}
```

Gửi tới:

```text
https://httpbin.org/headers
```

quan sát kết quả trên **phiên bản `primp` bạn đang cài**.

---

# 24. Tổng kết Buổi 17

Nhớ sơ đồ này:

```text
                 PrimpFetcher
                      │
                      ▼
                Primp Client
                      │
          ┌───────────┴───────────┐
          │                       │
   Default Headers         Request Headers
          │                       │
          └───────────┬───────────┘
                      ▼
                   HTTP
```

Và phân biệt:

```text
Default Headers
    ↓
Cấu hình HTTP chung

Request Headers
    ↓
Cấu hình riêng request

Cookies
    ↓
Session state

Authentication
    ↓
Credential mechanism

User-Agent
    ↓
Một HTTP header

Browser Fingerprint
    ↓
Một khái niệm rộng hơn User-Agent
```

### Roadmap hiện tại

```text
13 Authentication       ✅
14 Proxy                 ✅
15 SSL / Verify          ✅
16 Session / Connection  ✅
17 Default Headers       ← hôm nay
18 Default Params
19 Request Options
20 Client Lifecycle
```

**Buổi 18 — Default Params** sẽ tiếp tục đúng pattern này, nhưng chuyển từ **Headers** sang **Query Parameters**: cấu hình `params` mặc định ở client/fetcher, cách kết hợp default params với params của từng request, và ứng dụng vào pagination của Novel Crawler.

[1]: https://github.com/Knaackee/primp.net?utm_source=chatgpt.com "GitHub - Knaackee/primp.net: .NET bridge for the primp HTTP client — browser-grade TLS fingerprinting via Rust native interop · GitHub"
[2]: https://github.com/anthropics/anthropic-sdk-python/blob/main/MIGRATION.md?utm_source=chatgpt.com "anthropic-sdk-python/MIGRATION.md at main · anthropics/anthropic-sdk-python · GitHub"
[3]: https://github.com/python/cpython/blob/main/Doc/library/http.client.rst?plain=1&utm_source=chatgpt.com "cpython/Doc/library/http.client.rst at main · python/cpython · GitHub"
