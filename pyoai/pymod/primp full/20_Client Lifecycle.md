# Buổi 20 — Client Lifecycle

Đây là **buổi cuối của Phần II — HTTP Client**.

Sau buổi này, bạn sẽ nắm được một nguyên tắc rất quan trọng khi xây `Fetcher`:

> **`Primp.Client` không phải thứ tạo ra cho từng request. Nó là một resource có lifecycle, thường được tạo cùng Fetcher và sống đủ lâu để phục vụ nhiều request.**

Một điểm cần cập nhật theo phiên bản hiện tại: tài liệu Rust của `primp` hiện ở **2.0.1**, và `Client` quản lý state như headers, cookies, proxy và connection/service stack. ([Docs.rs][1])

---

# 1. Client Lifecycle là gì?

Ta có vòng đời:

```text
Application start
       │
       ▼
Create Primp Client
       │
       ▼
Create Fetcher
       │
       ├──── GET
       ├──── GET
       ├──── POST
       ├──── GET
       ├──── GET
       │
       ▼
Application shutdown
       │
       ▼
Release Client resources
```

Không nên:

```text
GET /chapter/1
    ↓
create Client
    ↓
request
    ↓
destroy Client

GET /chapter/2
    ↓
create Client
    ↓
request
    ↓
destroy Client
```

Mà nên:

```text
Create Client
     │
     ├── chapter/1
     ├── chapter/2
     ├── chapter/3
     ├── chapter/4
     └── chapter/5
     
     ↓
Shutdown
```

Điều này đặc biệt quan trọng với crawler.

---

# 2. Vì sao không tạo Client mỗi request?

Ví dụ **không nên**:

```python
import primp


def get(url: str):
    client = primp.Client()
    return client.get(url)
```

Nếu crawler có:

```text
10.000 chapters
```

thì về mặt kiến trúc ta đang biến:

```text
10.000 requests
```

thành:

```text
10.000 Client instances
```

Trong khi mục tiêu là:

```text
1 Fetcher
    ↓
1 Client
    ↓
n requests
```

Client còn có thể giữ trạng thái HTTP như:

* cookies
* default headers
* proxy configuration
* connection/service state

Tài liệu `primp` hiện cũng mô tả `Client` có default headers, cookie support và proxy state. ([Docs.rs][2])

---

# 3. Lifecycle gồm những giai đoạn nào?

Ta chia thành 4 bước:

```text
1. Create
2. Use
3. Maintain
4. Shutdown
```

Ví dụ:

```python
client = primp.Client()

# Use
response = client.get("https://example.com")

# ...

# Shutdown
```

Trong ứng dụng lớn:

```text
Application
    │
    ▼
Fetcher creation
    │
    ▼
Primp Client
    │
    ├── request
    ├── request
    ├── request
    │
    ▼
Application shutdown
```

---

# 4. Client nên thuộc về ai?

Đây là phần rất quan trọng với kiến trúc Novel Crawler.

Không nên:

```text
Parser
   ↓
primp.Client
```

Không nên:

```text
UseCase
   ↓
primp.Client
```

Mà:

```text
Application
      ↓
Fetcher
      ↓
PrimpFetcher
      ↓
primp.Client
```

Ví dụ:

```python
class PrimpFetcher:
    def __init__(self):
        self.client = primp.Client()
```

`PrimpFetcher` sở hữu lifecycle của `primp.Client`.

---

# 5. Fetcher lifecycle

Ta xây lại `PrimpFetcher`:

```python
import primp


class PrimpFetcher:
    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)

    def post(self, url: str, **kwargs):
        return self.client.post(url, **kwargs)
```

Sử dụng:

```python
def main():
    fetcher = PrimpFetcher()

    response1 = fetcher.get(
        "https://httpbin.org/get"
    )

    response2 = fetcher.get(
        "https://httpbin.org/headers"
    )

    print(response1.status_code)
    print(response2.status_code)


if __name__ == "__main__":
    main()
```

Lifecycle:

```text
main()
 │
 ├── PrimpFetcher()
 │      │
 │      └── PrimpClient
 │
 ├── GET
 ├── GET
 │
 └── end
```

---

# 6. Client không nên nằm trong method

Không nên:

```python
class PrimpFetcher:

    def get(self, url: str):
        client = primp.Client()
        return client.get(url)
```

Bởi vì:

```text
Fetcher
  │
  ├── get()
  │     └── Client #1
  │
  ├── get()
  │     └── Client #2
  │
  └── get()
        └── Client #3
```

Đây là lifecycle sai.

Nên:

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)
```

Kết quả:

```text
Fetcher
   │
   └── Client
        │
        ├── GET
        ├── GET
        ├── GET
        └── GET
```

---

# 7. Client và Cookies

Ta đã học Cookies ở Buổi 9.

Lifecycle giải thích **tại sao cookies có thể được duy trì**.

Ví dụ:

```python
client = primp.Client()

client.get(
    "https://example.com/login"
)

client.get(
    "https://example.com/profile"
)
```

Hai request sử dụng cùng Client.

Về kiến trúc:

```text
Client
 │
 ├── Cookie state
 ├── Headers
 ├── Proxy
 └── Connection state
```

Nếu bạn liên tục tạo Client:

```python
primp.Client().get(...)
primp.Client().get(...)
primp.Client().get(...)
```

thì bạn không còn có một HTTP session/client lifecycle thống nhất.

---

# 8. Client và Connection Reuse

Buổi 16 chúng ta đã học:

> Connection reuse.

Lifecycle chính là nền tảng để thực hiện điều đó.

Ví dụ:

```text
PrimpFetcher
     │
     ▼
Primp Client
     │
     ▼
HTTP connection/service state
     │
     ├── Request 1
     ├── Request 2
     ├── Request 3
     └── Request 4
```

Không có nghĩa là:

> "Tất cả request chắc chắn sử dụng đúng một TCP connection."

Điều đó **không đúng**.

Connection có thể:

* được reuse
* bị server đóng
* bị proxy đóng
* timeout
* reset
* tạo connection mới khi cần

Ta nên hiểu chính xác là:

> **Client sống lâu tạo điều kiện cho HTTP transport quản lý và tái sử dụng connection state hiệu quả.**

---

# 9. Client Lifecycle và Default Headers

Buổi 17:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN,vi;q=0.9",
    }
)
```

Lifecycle:

```text
Create Client
      │
      └── default headers
             │
             ├── GET
             ├── GET
             └── POST
```

Không cần:

```python
client.get(
    url,
    headers={"Accept-Language": "vi-VN,vi;q=0.9"}
)
```

ở mọi request.

---

# 10. Client Lifecycle và RequestOptions

Buổi 19 chúng ta có:

```python
@dataclass
class RequestOptions:
    timeout: float | None = None
    headers: dict[str, str] = field(default_factory=dict)
    params: dict = field(default_factory=dict)
```

Ta có hai tầng:

```text
Client / Fetcher configuration
│
├── default headers
├── default timeout
├── proxy
├── TLS
└── browser profile

RequestOptions
│
├── request timeout
├── request headers
└── request params
```

Ví dụ:

```python
fetcher = PrimpFetcher(
    timeout=10,
)

options = RequestOptions(
    timeout=30,
    params={"page": 2},
)
```

Ý nghĩa:

```text
Fetcher
  │
  ├── stable configuration
  │
  └── Client lifecycle
           │
           ▼
       RequestOptions
           │
           ▼
        Request
```

---

# 11. Một lifecycle hoàn chỉnh

Bây giờ kết hợp những gì đã học từ Buổi 1 → 19.

```python
from dataclasses import dataclass, field

import primp


@dataclass
class RequestOptions:
    timeout: float | None = None
    headers: dict[str, str] = field(default_factory=dict)
    params: dict = field(default_factory=dict)


class PrimpFetcher:

    def __init__(
        self,
        *,
        timeout: float = 10,
        default_headers: dict[str, str] | None = None,
        default_params: dict | None = None,
    ):
        self.client = primp.Client()

        self.default_timeout = timeout

        self.default_headers = (
            default_headers.copy()
            if default_headers
            else {}
        )

        self.default_params = (
            default_params.copy()
            if default_params
            else {}
        )

    def get(
        self,
        url: str,
        *,
        options: RequestOptions | None = None,
    ):
        options = options or RequestOptions()

        timeout = (
            options.timeout
            if options.timeout is not None
            else self.default_timeout
        )

        headers = self.default_headers.copy()
        headers.update(options.headers)

        params = self.default_params.copy()
        params.update(options.params)

        return self.client.get(
            url,
            timeout=timeout,
            headers=headers,
            params=params,
        )
```

Sử dụng:

```python
def main():
    fetcher = PrimpFetcher(
        timeout=10,
        default_headers={
            "Accept": "text/html",
            "Accept-Language": "vi-VN,vi;q=0.9",
        },
    )

    response = fetcher.get(
        "https://httpbin.org/get",
        options=RequestOptions(
            params={
                "page": 2,
            }
        ),
    )

    print(response.status_code)
    print(response.url)


if __name__ == "__main__":
    main()
```

---

# 12. Lifecycle của Novel Crawler

Đây mới là phần quan trọng nhất đối với project của bạn.

Giả sử crawler chạy:

```text
Novel
 ├── Chapter 1
 ├── Chapter 2
 ├── Chapter 3
 ├── ...
 └── Chapter 500
```

Không nên:

```text
Chapter 1 → Client
Chapter 2 → Client
Chapter 3 → Client
...
Chapter 500 → Client
```

Nên:

```text
Crawler Application
        │
        ▼
   PrimpFetcher
        │
        ▼
   Primp Client
        │
        ├── Chapter 1
        ├── Chapter 2
        ├── Chapter 3
        ├── ...
        └── Chapter 500
```

Đây chính là lý do lifecycle rất quan trọng.

---

# 13. Lifecycle ở tầng Application

Ta có thể tổ chức:

```text
main()
 │
 ├── create Fetcher
 │
 ├── create Use Cases
 │
 ├── crawl
 │
 └── shutdown
```

Ví dụ:

```python
class CrawlApplication:

    def __init__(self):
        self.fetcher = PrimpFetcher()

    def run(self):
        response = self.fetcher.get(
            "https://example.com"
        )

        print(response.status_code)


def main():
    app = CrawlApplication()
    app.run()


if __name__ == "__main__":
    main()
```

Architecture:

```text
main
 │
 ▼
Application
 │
 ▼
Use Case
 │
 ▼
Fetcher Interface
 │
 ▼
PrimpFetcher
 │
 ▼
Primp Client
```

Domain hoàn toàn không biết:

```python
import primp
```

Đây là điểm rất quan trọng với DDD/Clean Architecture.

---

# 14. Có cần `close()` không?

Đây là chỗ cần **cẩn thận với `primp` hiện tại**.

Tài liệu Rust hiện tại của `primp` mô tả `Client`, nhưng API lifecycle của Python binding không nên suy ra máy móc từ Rust API. Một số tài liệu bên ngoài còn ghi nhận rằng Python `primp.Client` không expose `close()` ở một số phiên bản. ([GitHub][3])

Vì vậy, **không nên tự viết**:

```python
self.client.close()
```

chỉ vì các HTTP client khác có API đó.

Đặc biệt:

```python
with primp.Client() as client:
    ...
```

cũng **không nên giả định** nếu chưa kiểm tra đúng Python version đang cài.

Đây là một bài học quan trọng:

> **Rust API ≠ Python binding API.**

---

# 15. Kiểm tra lifecycle API thực tế

Bạn có thể kiểm tra ngay trên máy:

```python
import primp


client = primp.Client()

print(type(client))

print("close:", hasattr(client, "close"))
print("__enter__:", hasattr(client, "__enter__"))
print("__exit__:", hasattr(client, "__exit__"))

print(dir(client))
```

Ví dụ:

```text
close: False
__enter__: False
__exit__: False
```

hoặc tùy phiên bản có thể khác.

Đây là cách kiểm tra **API thực tế của package bạn đang chạy**, thay vì đoán.

---

# 16. Garbage Collection / Resource Release

Nếu Python object không còn được tham chiếu:

```python
client = primp.Client()

# ...

client = None
```

object cuối cùng có thể được giải phóng khi Python/Rust binding xử lý lifecycle của nó.

Nhưng ta **không nên thiết kế crawler dựa vào việc "Python sẽ tự dọn lúc nào đó"**.

Nguyên tắc tốt hơn:

```text
Application owns Fetcher
Fetcher owns Client
Application controls Fetcher lifetime
```

Ví dụ:

```text
start application
       ↓
create fetcher
       ↓
crawl
       ↓
stop application
       ↓
release fetcher/client
```

---

# 17. Không nên tạo Client trong vòng lặp

Ví dụ crawler sai:

```python
for chapter_url in chapter_urls:
    client = primp.Client()

    response = client.get(chapter_url)

    process(response)
```

Nếu:

```python
chapter_urls = [
    ".../chuong-1",
    ".../chuong-2",
    ".../chuong-3",
]
```

thì Client bị tạo liên tục.

Sửa:

```python
client = primp.Client()

for chapter_url in chapter_urls:
    response = client.get(chapter_url)

    process(response)
```

Tốt hơn nữa:

```python
fetcher = PrimpFetcher()

for chapter_url in chapter_urls:
    response = fetcher.get(chapter_url)

    process(response)
```

---

# 18. Lifecycle và Proxy

Đến Buổi 14 chúng ta học Proxy.

Proxy thường thuộc về Client/Fetcher configuration:

```text
PrimpFetcher
    │
    └── Client
         │
         └── Proxy
```

Không nên:

```python
parser.parse(...)
```

rồi Parser tự quyết định:

```python
proxy = ...
```

Parser không biết proxy.

---

# 19. Lifecycle và Browser Impersonation

Đây là cầu nối rất quan trọng sang **Phần III**.

Ta sẽ sớm có:

```python
primp.Client(
    impersonate="chrome_146"
)
```

Khi đó:

```text
Client
 │
 ├── Browser profile
 ├── TLS fingerprint
 ├── HTTP/2
 ├── Default headers
 └── Connection state
```

Browser impersonation trong `primp` hiện liên quan đến TLS, HTTP/2 và default headers; tài liệu hiện liệt kê nhiều profile Chrome/Firefox/Safari/Edge. ([Docs.rs][4])

Vì vậy lifecycle càng quan trọng:

```text
Create Browser Client
        │
        ▼
Multiple requests
        │
        ▼
Same browser profile
```

---

# 20. Một nguyên tắc kiến trúc rất quan trọng

Ta có:

```text
Domain
Application
Infrastructure
```

`primp` nằm ở:

```text
Infrastructure
```

Ví dụ:

```text
domain/
    novel.py
    chapter.py

application/
    crawl_novel.py

infrastructure/
    http/
        fetcher.py
        primp_fetcher.py
```

`PrimpFetcher`:

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url: str):
        return self.client.get(url)
```

Application:

```python
class CrawlChapter:

    def __init__(self, fetcher):
        self.fetcher = fetcher

    def execute(self, url: str):
        response = self.fetcher.get(url)

        return response.text
```

Application **không cần biết**:

```python
primp.Client
```

---

# 21. Dependency Injection

Đây chính là chỗ DDD/SOLID bắt đầu phát huy tác dụng.

Thay vì:

```python
class CrawlChapter:

    def __init__(self):
        self.client = primp.Client()
```

ta làm:

```python
class CrawlChapter:

    def __init__(self, fetcher):
        self.fetcher = fetcher
```

Sau đó:

```python
fetcher = PrimpFetcher()

use_case = CrawlChapter(
    fetcher=fetcher
)
```

Architecture:

```text
             ┌───────────────┐
             │ CrawlChapter  │
             └───────┬───────┘
                     │
                     ▼
              Fetcher Interface
                     ▲
                     │
              PrimpFetcher
                     │
                     ▼
                primp.Client
```

Đây là **Dependency Inversion Principle**.

---

# 22. Test cũng dễ hơn

Vì Application không phụ thuộc trực tiếp vào `primp`, ta có thể tạo fake:

```python
class FakeFetcher:

    def get(self, url: str):
        return type(
            "Response",
            (),
            {
                "text": "<html>Hello</html>",
                "status_code": 200,
            },
        )()
```

Test:

```python
def test_crawl_chapter():
    fetcher = FakeFetcher()

    use_case = CrawlChapter(
        fetcher=fetcher
    )

    result = use_case.execute(
        "https://example.com/chapter-1"
    )

    assert "Hello" in result
```

Không cần Internet.

Không cần `primp`.

Không cần proxy.

Không cần server.

Đây là một trong những lợi ích lớn nhất của việc đặt lifecycle đúng tầng.

---

# 23. Threading sau này thì sao?

Ở Phần IV chúng ta sẽ học:

```text
AsyncClient
Concurrent Requests
Semaphore
Proxy Pool
Browser Profile Pool
```

Khi đó lifecycle sẽ phức tạp hơn.

Ví dụ:

```text
Crawler
 │
 ├── Fetcher #1
 │      └── Client #1
 │
 ├── Fetcher #2
 │      └── Client #2
 │
 └── Fetcher #3
        └── Client #3
```

Hoặc một kiến trúc pool:

```text
Fetcher Pool
 │
 ├── Client/Profile A
 ├── Client/Profile B
 ├── Client/Profile C
 └── Client/Profile D
```

Nhưng **chưa cần thiết kế pool bây giờ**.

Buổi 20 chỉ cần nắm:

> **Client lifetime phải có chủ sở hữu rõ ràng.**

---

# 24. Bài thực hành

## Bài 1 — Kiểm tra Client

Tạo:

```text
lesson_20_1.py
```

```python
import primp


def main():
    client = primp.Client()

    print("Client type:")
    print(type(client))

    print()

    print("Has close:")
    print(hasattr(client, "close"))

    print()

    print("Has context manager:")
    print(hasattr(client, "__enter__"))
    print(hasattr(client, "__exit__"))


if __name__ == "__main__":
    main()
```

Mục tiêu:

> Không đoán API. Hãy kiểm tra package thực tế.

---

# 25. Bài 2 — Một Client, nhiều request

```python
import primp


def main():
    client = primp.Client()

    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/headers",
        "https://httpbin.org/ip",
    ]

    for url in urls:
        response = client.get(url)

        print("=" * 60)
        print("URL:", response.url)
        print("STATUS:", response.status_code)


if __name__ == "__main__":
    main()
```

Mục tiêu:

```text
1 Client
   ↓
3 requests
```

---

# 26. Bài 3 — Sai và đúng

### Sai

```python
import primp


def fetch(url):
    client = primp.Client()
    return client.get(url)


def main():
    for i in range(10):
        response = fetch(
            "https://httpbin.org/get"
        )

        print(response.status_code)


if __name__ == "__main__":
    main()
```

### Đúng

```python
import primp


class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client()

    def get(self, url):
        return self.client.get(url)


def main():
    fetcher = PrimpFetcher()

    for i in range(10):
        response = fetcher.get(
            "https://httpbin.org/get"
        )

        print(response.status_code)


if __name__ == "__main__":
    main()
```

Hãy nhìn sự khác biệt:

```text
BAD

request
  ↓
new Client
  ↓
request
  ↓
destroy


GOOD

Fetcher
  ↓
Client
  ├── request
  ├── request
  ├── request
  └── request
```

---

# 27. Bài 4 — Lifecycle của Novel Crawler

Viết:

```python
class NovelFetcher:

    def __init__(self):
        self.client = primp.Client()

    def fetch_chapter(self, url: str):
        return self.client.get(url)
```

Sau đó:

```python
def main():
    fetcher = NovelFetcher()

    chapters = [
        "https://httpbin.org/get?chapter=1",
        "https://httpbin.org/get?chapter=2",
        "https://httpbin.org/get?chapter=3",
    ]

    for url in chapters:
        response = fetcher.fetch_chapter(url)

        print(
            response.status_code,
            response.url,
        )


if __name__ == "__main__":
    main()
```

Mục tiêu kiến trúc:

```text
NovelFetcher
      │
      ▼
    Client
      │
      ├── Chapter 1
      ├── Chapter 2
      └── Chapter 3
```

---

# 28. Tổng kết Phần II

Chúng ta đã đi:

```text
11 Timeout
12 Exception
13 Authentication
14 Proxy
15 SSL / Verify
16 Session / Connection Reuse
17 Default Headers
18 Default Params
19 Request Options
20 Client Lifecycle
```

Có thể gom thành:

```text
                    HTTP CLIENT
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Request           State          Transport
        │                │                │
   ┌────┼────┐       Cookies         Timeout
   │    │    │       Headers         Proxy
 GET   POST Params    Auth            SSL
   │    │    │                         │
   └────┴────┘                    Connection
                                      │
                                 Client Lifecycle
```

---

# 29. Kiến trúc hiện tại của `PrimpFetcher`

Sau 20 buổi, ta đã có nền tảng:

```text
Application
     │
     ▼
Fetcher Interface
     │
     ▼
PrimpFetcher
     │
     └───────────────┐
                     ▼
                primp.Client
                     │
        ┌────────────┼─────────────┐
        │            │             │
     Headers       Cookies       Proxy
        │            │             │
     Params        Auth           SSL
        │            │             │
     Timeout     RequestOptions   ...
```

Điểm quan trọng:

> **Chưa cần Retry, ProxyPool, BrowserProfilePool hay RateLimiter ở đây.**

Chúng ta sẽ xây từng abstraction khi đến đúng phần của roadmap.

---

# 30. Chuẩn bị sang Phần III

Phần II kết thúc ở đây.

Phần III sẽ thay đổi câu hỏi từ:

```text
"Làm thế nào gửi HTTP request?"
```

sang:

```text
"Làm thế nào để request có
đặc điểm giống một browser thật?"
```

Roadmap:

```text
21. Vì sao cần impersonation
22. Chrome fingerprint
23. Firefox / Safari / Edge
24. impersonate_os
25. TLS fingerprint
26. HTTP/2
27. Headers + fingerprint
28. Fingerprint thực tế
29. So sánh httpx vs primp
30. Xây BrowserClient
```

Đặc biệt, `primp` hiện mô tả browser impersonation ở mức **TLS + HTTP/2 + default headers**, chứ không đơn giản chỉ là đổi `User-Agent`. ([Docs.rs][4])

**Mốc kiến thức sau Buổi 20:**

```text
HTTP fundamentals
       ↓
primp basics
       ↓
HTTP Client
       ↓
Client lifecycle
       ↓
────────────────────
PHẦN III
Browser Impersonation
```

Và đây là nền tảng rất phù hợp để sau này ghép vào `PrimpFetcher` của **Novel Crawler** mà không làm Domain/Application phụ thuộc trực tiếp vào `primp`.

[1]: https://docs.rs/crate/primp/latest?utm_source=chatgpt.com "primp 2.0.1 - Docs.rs"
[2]: https://docs.rs/primp/latest/primp/struct.Client.html?utm_source=chatgpt.com "Client in primp - Rust"
[3]: https://github.com/zinzied/TLS-Chameleon/blob/main/docs/NATIVE_BACKEND_RESEARCH.md?utm_source=chatgpt.com "TLS-Chameleon/docs/NATIVE_BACKEND_RESEARCH.md at main · zinzied/TLS-Chameleon · GitHub"
[4]: https://docs.rs/primp/latest/primp/imp/index.html?utm_source=chatgpt.com "primp::imp - Rust"
