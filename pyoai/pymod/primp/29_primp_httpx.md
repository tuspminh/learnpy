# Buổi 29 — So sánh `httpx` vs `primp`

Đây là một buổi rất quan trọng đối với **Novel Crawler**, vì mục tiêu không phải học thêm một thư viện rồi bỏ thư viện cũ, mà phải trả lời được:

> **Khi nào dùng `httpx`, khi nào dùng `primp`, và kiến trúc Fetcher nên thiết kế thế nào để có thể thay đổi implementation?**

Hiện tại `primp` 2.0.1 là HTTP client tập trung vào browser impersonation, còn `httpx` là HTTP client tổng quát với HTTP/1.1, HTTP/2, connection pooling, proxy, timeout, async... ([PyPI][1])

---

# 1. Nhìn tổng quan trước

```text
                    HTTP Client
                        │
            ┌───────────┴───────────┐
            │                       │
          httpx                   primp
            │                       │
     General-purpose          Browser impersonation
            │                       │
    ┌───────┼────────┐       ┌──────┼───────┐
    ↓       ↓        ↓       ↓      ↓       ↓
   HTTP    HTTP/2   Async    TLS   HTTP/2  Headers
   Proxy   Pool     Async    FP     FP      Profile
```

Nói ngắn gọn:

```text
httpx
    → HTTP client hiện đại, tổng quát

primp
    → HTTP client + browser impersonation
```

Nhưng đừng hiểu:

```text
primp > httpx
```

hoặc:

```text
httpx > primp
```

Đó không phải cách so sánh đúng.

Ta phải hỏi:

```text
Use case là gì?
```

---

# 2. So sánh kiến trúc

| Khía cạnh                  | `httpx`                                   | `primp` |
| -------------------------- | ----------------------------------------- | ------- |
| HTTP client                | ✅                                         | ✅       |
| Sync                       | ✅                                         | ✅       |
| Async                      | ✅                                         | ✅       |
| HTTP/1.1                   | ✅                                         | ✅       |
| HTTP/2                     | ✅                                         | ✅       |
| Connection pooling         | ✅                                         | ✅       |
| Cookies                    | ✅                                         | ✅       |
| Headers                    | ✅                                         | ✅       |
| Query params               | ✅                                         | ✅       |
| Timeout                    | ✅                                         | ✅       |
| Proxy                      | ✅                                         | ✅       |
| Authentication             | ✅                                         | ✅       |
| Browser impersonation      | ❌                                         | ✅       |
| TLS browser fingerprint    | Không tập trung vào browser impersonation | ✅       |
| HTTP/2 browser fingerprint | Không tập trung vào browser impersonation | ✅       |
| Browser profiles           | ❌                                         | ✅       |
| Browser OS profiles        | ❌                                         | ✅       |

`httpx` có HTTP/2 nhưng HTTP/2 không được bật mặc định; có thể bật bằng `http2=True`. ([Httpx][2])

`primp` hiện cung cấp các browser profile như Chrome, Firefox, Safari, Edge, Opera và OS profiles như Windows, macOS, Linux, Android, iOS. ([PyPI][1])

---

# 3. HTTP request cơ bản

Hai thư viện có cách sử dụng khá giống nhau.

## HTTPX

```python
import httpx

response = httpx.get(
    "https://httpbin.org/get"
)

print(response.status_code)
print(response.text)
```

## PRIMP

```python
import primp

client = primp.Client()

response = client.get(
    "https://httpbin.org/get"
)

print(response.status_code)
print(response.text)
```

Về abstraction:

```text
GET
POST
PUT
DELETE
headers
params
cookies
timeout
```

thì hai thư viện đều có mô hình khá gần nhau.

---

# 4. Client và connection pooling

Đây là điểm chúng ta đã học ở Buổi 16.

Không nên:

```python
for url in urls:
    client = ...
    client.get(url)
```

Mà nên:

```text
Application
    │
    ↓
Fetcher
    │
    ↓
Long-lived Client
    │
    ├── request 1
    ├── request 2
    ├── request 3
    └── request 4
```

HTTPX document nói rõ `Client` sử dụng connection pooling và có thể tái sử dụng TCP connection giữa các request. ([Httpx][3])

HTTPX còn cho phép cấu hình giới hạn connection pool bằng `httpx.Limits`. ([Httpx][4])

Với `primp`, tư duy kiến trúc của chúng ta cũng giữ nguyên:

```python
class PrimpFetcher:
    def __init__(self):
        self.client = primp.Client(
            impersonate="chrome_146",
            impersonate_os="windows",
        )
```

Không tạo client cho từng chapter.

---

# 5. Async

Đây là điểm quan trọng vì roadmap của chúng ta sẽ đi tới:

```text
31. AsyncClient
32. async GET
33. Concurrent Requests
```

Cả hai đều có async client.

## HTTPX

```python
import httpx
import asyncio


async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://httpbin.org/get"
        )

        print(response.status_code)


asyncio.run(main())
```

HTTPX có `AsyncClient` và khuyến nghị không tạo nhiều client trong hot loop vì sẽ làm mất lợi ích connection pooling. ([Httpx][5])

---

## PRIMP

API hiện tại của `primp 2.0.1` cũng có:

```python
import asyncio
import primp


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146"
    ) as client:

        response = await client.get(
            "https://tls.peet.ws/api/all"
        )

        print(response.text)


asyncio.run(main())
```

Đây là ví dụ async chính thức trên PyPI của `primp`. ([PyPI][1])

---

# 6. HTTP/2

Đây là nơi dễ hiểu nhầm.

## HTTPX

HTTPX hỗ trợ HTTP/2 nhưng phải bật:

```python
client = httpx.Client(
    http2=True
)
```

hoặc:

```python
client = httpx.AsyncClient(
    http2=True
)
```

HTTPX cũng lưu ý rằng `http2=True` không đảm bảo request thực tế luôn chạy bằng HTTP/2; server cũng phải hỗ trợ HTTP/2. Có thể kiểm tra version qua `response.http_version`. ([Httpx][2])

---

## PRIMP

PRIMP đi xa hơn khái niệm:

```text
HTTP/2 enabled
```

Nó hướng tới:

```text
Browser HTTP/2 behavior
```

khi sử dụng browser impersonation.

Tức là:

```text
HTTPX:

HTTP/2
   ↓
Protocol support


PRIMP:

Browser Profile
      ↓
TLS
HTTP/2
Headers
      ↓
Browser-like network profile
```

PyPI của `primp` mô tả browser impersonation bao gồm TLS/HTTP2 fingerprinting và các browser profiles. ([PyPI][1])

---

# 7. TLS

Đây là khác biệt lớn.

HTTPX:

```python
client = httpx.Client(
    verify=True
)
```

chủ yếu quan tâm:

```text
TLS security
certificate verification
SSLContext
CA
```

HTTPX cho phép `verify=True`, `False` hoặc SSL context tùy cấu hình. ([Httpx][6])

PRIMP có thêm lớp:

```text
TLS browser fingerprint
```

khi dùng:

```python
primp.Client(
    impersonate="chrome_146"
)
```

Do đó:

```text
HTTPX
    TLS
    ↓
Security / transport

PRIMP
    TLS
    ↓
Security
    +
Browser impersonation
```

Đây chính là lý do chúng ta dành riêng Buổi 25 cho TLS fingerprint.

---

# 8. Headers

HTTPX:

```python
client = httpx.Client(
    headers={
        "Accept-Language": "vi-VN"
    }
)
```

PRIMP:

```python
client = primp.Client(
    headers={
        "Accept-Language": "vi-VN"
    }
)
```

Hai bên đều có custom headers.

Nhưng:

```python
headers={
    "User-Agent": "Chrome..."
}
```

không tương đương với:

```python
impersonate="chrome_146"
```

Trong PRIMP:

```text
impersonate
    ↓
Browser profile
    ├── Headers
    ├── TLS
    └── HTTP/2
```

PyPI của PRIMP mô tả trực tiếp đây là HTTP client có khả năng impersonate browser. ([PyPI][1])

---

# 9. Proxy

HTTPX hỗ trợ proxy trực tiếp qua `proxy=` và cả các cấu hình transport/mount phức tạp hơn. ([Httpx][7])

Ví dụ:

```python
import httpx

client = httpx.Client(
    proxy="http://localhost:8080"
)
```

PRIMP cũng có proxy support.

Nhưng kiến trúc của crawler không nên:

```python
class PrimpFetcher:
    def __init__(
        self,
        proxy: str,
        browser: str,
        retry: int,
        rate_limit: float,
        ...
    ):
        ...
```

Đây là God Object.

Chúng ta đã học cách tách:

```text
BrowserProfile
ProxyConfig
RequestOptions
RetryPolicy
RateLimiter
```

---

# 10. Timeout

HTTPX có timeout khá mạnh:

```python
timeout = httpx.Timeout(
    10.0,
    connect=30.0,
)

client = httpx.Client(
    timeout=timeout
)
```

HTTPX phân biệt:

```text
connect
read
write
pool
```

timeout. ([Httpx][8])

Đây là một điểm HTTPX rất thuận tiện khi xây crawler production.

Với architecture:

```text
Fetcher
    ↓
TimeoutPolicy
    ↓
HTTP Client
```

ta không cần để Domain biết `httpx.Timeout`.

---

# 11. Exception

HTTPX có hierarchy khá rõ:

```text
HTTPError
    │
    └── RequestError
          │
          └── TransportError
                ├── TimeoutException
                │     ├── ConnectTimeout
                │     ├── ReadTimeout
                │     ├── WriteTimeout
                │     └── PoolTimeout
                │
                └── NetworkError
```

Đây là một ưu điểm khi xây `ErrorClassifier`. ([Httpx][9])

Ví dụ:

```python
try:
    response = client.get(url)

except httpx.ConnectTimeout:
    ...

except httpx.ReadTimeout:
    ...

except httpx.NetworkError:
    ...
```

Sau này chúng ta sẽ biến thành:

```text
HTTP Exception
      ↓
ErrorClassifier
      ↓
Retryable?
      │
 ┌────┴────┐
 YES       NO
 ↓          ↓
Retry      Fail
```

---

# 12. Redirect

HTTPX có:

```python
client.get(
    url,
    follow_redirects=True,
)
```

và có:

```python
response.history
```

để xem redirect chain. ([Httpx][10])

Đây là kiểu API rất thuận tiện cho crawler.

Với Novel Crawler:

```text
chapter URL
      ↓
301
      ↓
new URL
      ↓
200
```

ta có thể lưu:

```text
requested_url
final_url
redirect_history
```

---

# 13. Resource management

HTTPX có API lifecycle rất rõ:

```python
with httpx.Client() as client:
    ...
```

hoặc:

```python
client = httpx.Client()

try:
    ...
finally:
    client.close()
```

Tài liệu HTTPX khuyến nghị context manager để đảm bảo connection được cleanup. ([Httpx][3])

Async:

```python
async with httpx.AsyncClient() as client:
    ...
```

hoặc:

```python
await client.aclose()
```

([Httpx][5])

Với `primp`, API hiện tại cũng cung cấp `AsyncClient` dưới context manager như ví dụ chính thức. ([PyPI][1])

---

# 14. Điểm mạnh của HTTPX

Nếu project cần:

```text
API Client
Microservice Client
Internal service
REST API
Generic crawler
Async crawler
HTTP/2
Proxy
Connection Pool
Fine-grained Timeout
Transport customization
```

thì HTTPX có một hệ sinh thái API rất phù hợp.

Đặc biệt:

```text
httpx.Client
httpx.AsyncClient
httpx.Limits
httpx.Timeout
HTTPTransport
exceptions
mounts
```

cho phép kiểm soát khá sâu transport layer. ([Httpx][8])

---

# 15. Điểm mạnh của PRIMP

Nếu yêu cầu chính là:

```text
Website
   ↓
Browser-like HTTP behavior
```

thì:

```python
primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

cho chúng ta browser profile ngay ở client layer.

Hiện tại PRIMP 2.0.1 có nhiều profile Chrome/Firefox/Safari/Edge/Opera và OS profiles. ([PyPI][1])

Đây chính là điểm khác biệt lớn nhất.

---

# 16. Một ví dụ rất thực tế

Giả sử Novel Crawler của bạn có:

```text
100 website
```

Trong đó:

```text
Site A
Site B
Site C
...
```

không phải tất cả đều có cùng yêu cầu.

Ta có thể có:

```text
Fetcher
│
├── HttpxFetcher
│
└── PrimpFetcher
```

Application chỉ biết:

```python
class Fetcher(Protocol):

    def get(
        self,
        url: str,
        ...
    ):
        ...
```

Nó **không biết** implementation bên dưới là gì.

---

# 17. Đây mới là kiến trúc chúng ta muốn

```text
                 Application
                      │
                      ↓
                Fetcher Protocol
                      │
             ┌────────┴────────┐
             ↓                 ↓
       HttpxFetcher       PrimpFetcher
             │                 │
             ↓                 ↓
           httpx             primp
                               │
                    ┌──────────┼──────────┐
                    ↓          ↓          ↓
                   TLS       HTTP/2    Headers
                    │          │          │
                    └──────────┼──────────┘
                               ↓
                      Browser Impersonation
```

Đây là lý do học `primp` **sau khi đã học `httpx` rất có giá trị**.

---

# 18. Xây Fetcher Interface

Đây là phiên bản đơn giản:

```python
from typing import Protocol


class Fetcher(Protocol):

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict | None = None,
        timeout: float | None = None,
    ):
        ...
```

Sau đó:

```python
class HttpxFetcher:

    def __init__(self):
        self.client = httpx.Client()

    def get(
        self,
        url: str,
        *,
        headers=None,
        params=None,
        timeout=None,
    ):
        return self.client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
```

và:

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.Client(
            impersonate="chrome_146",
            impersonate_os="windows",
        )

    def get(
        self,
        url: str,
        *,
        headers=None,
        params=None,
        timeout=None,
    ):
        return self.client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )
```

---

# 19. Application không cần biết

Ví dụ:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher

    def execute(
        self,
        url: str,
    ):
        response = self.fetcher.get(url)

        return response.text
```

Có thể inject:

```python
use_case = CrawlChapter(
    fetcher=HttpxFetcher()
)
```

hoặc:

```python
use_case = CrawlChapter(
    fetcher=PrimpFetcher()
)
```

Use Case không đổi.

Đây chính là:

```text
Dependency Inversion
```

và:

```text
Dependency Injection
```

mà bạn đã học trong DDD/SOLID.

---

# 20. Nhưng có một vấn đề

Bạn có thể hỏi:

> Response của `httpx` và `primp` có hoàn toàn giống nhau không?

**Không nên giả định như vậy.**

Ví dụ application không nên phụ thuộc quá sâu vào:

```python
response._internal_something
```

hoặc API đặc thù của một library.

Thay vào đó, chúng ta nên có:

```text
HTTP library response
        ↓
Adapter
        ↓
Application Response Model
```

Ví dụ:

```python
from dataclasses import dataclass


@dataclass
class FetchResponse:
    status_code: int
    url: str
    headers: dict[str, str]
    content: bytes

    @property
    def text(self) -> str:
        return self.content.decode(
            "utf-8",
            errors="replace",
        )
```

---

# 21. Adapter Pattern

Kiến trúc:

```text
httpx.Response
      ↓
HttpxResponseAdapter
      ↓
FetchResponse
      ↑
PrimpResponseAdapter
      ↑
primp.Response
```

Application chỉ nhìn:

```python
FetchResponse
```

chứ không nhìn:

```python
httpx.Response
```

hay:

```python
primp.Response
```

Đây là thiết kế rất phù hợp với crawler lớn.

---

# 22. So sánh theo Novel Crawler

Bây giờ đặt vào project thật:

| Nhu cầu                  |    HTTPX |   PRIMP |
| ------------------------ | -------: | ------: |
| Website bình thường      |        ✅ |       ✅ |
| REST API                 |        ✅ |       ✅ |
| SQLite crawler           |        ✅ |       ✅ |
| Cookie session           |        ✅ |       ✅ |
| Timeout                  |        ✅ |       ✅ |
| Retry layer              |        ✅ |       ✅ |
| Proxy                    |        ✅ |       ✅ |
| Async crawler            |        ✅ |       ✅ |
| HTTP/2                   |        ✅ |       ✅ |
| Browser impersonation    |        — |       ✅ |
| Browser profile          |        — |       ✅ |
| TLS/browser fingerprint  |        — |       ✅ |
| Architecture abstraction |        ✅ |       ✅ |
| Transport customization  | Rất mạnh |      Có |
| Generic ecosystem/docs   | Rất rộng | Nhỏ hơn |

---

# 23. Vậy Novel Crawler nên dùng gì?

Thay vì hard-code:

```text
Novel Crawler = PRIMP
```

chúng ta nên thiết kế:

```text
Novel Crawler
      │
      ↓
Fetcher Interface
      │
      ├───────────────┐
      ↓               ↓
 HttpxFetcher     PrimpFetcher
```

Sau đó từng website/plugin có thể chọn:

```text
Plugin A
   ↓
HttpxFetcher


Plugin B
   ↓
PrimpFetcher
```

Hoặc application config:

```yaml
fetcher:
  type: primp
  profile: chrome_146
  os: windows
```

Sau này:

```yaml
fetcher:
  type: httpx
```

không cần sửa Domain.

---

# 24. Đừng tạo abstraction quá sớm

Một lỗi khác:

```python
class UniversalHTTPClient:
    ...
```

rồi:

```text
UniversalHTTPClient
    ↓
Httpx
Primp
Requests
Aiohttp
Curl
...
```

trong khi crawler chỉ dùng 1–2 implementation.

Không cần.

Ở giai đoạn hiện tại:

```text
Fetcher Protocol
      │
      ├── HttpxFetcher
      └── PrimpFetcher
```

là đủ.

Đây là abstraction vừa đủ.

---

# 25. Một lab rất quan trọng

Tạo:

```text
lesson29/
└── compare_clients.py
```

```python
import httpx
import primp


URL = "https://httpbin.org/get"


def test_httpx():
    print("=" * 60)
    print("HTTPX")
    print("=" * 60)

    with httpx.Client(
        timeout=10.0,
        follow_redirects=True,
    ) as client:

        response = client.get(URL)

        print("Status:", response.status_code)
        print("URL:", response.url)
        print("HTTP version:", response.http_version)


def test_primp():
    print("=" * 60)
    print("PRIMP")
    print("=" * 60)

    client = primp.Client(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    response = client.get(
        URL,
        timeout=10,
    )

    print("Status:", response.status_code)
    print("URL:", response.url)


def main():
    test_httpx()
    print()

    test_primp()


if __name__ == "__main__":
    main()
```

Chạy:

```bash
python compare_clients.py
```

---

# 26. Lab thứ hai — HTTP/2

HTTPX:

```python
import httpx


with httpx.Client(http2=True) as client:
    response = client.get(
        "https://tls.peet.ws/api/all"
    )

    print(
        response.http_version
    )
```

HTTPX sẽ thương lượng với server; `http2=True` chỉ bật khả năng HTTP/2, không ép server phải dùng HTTP/2. ([Httpx][2])

PRIMP:

```python
import primp


client = primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)

response = client.get(
    "https://tls.peet.ws/api/all"
)

print(response.text)
```

Sau đó quan sát network information từ endpoint.

---

# 27. Một điểm rất đáng nhớ

Đừng so sánh:

```text
HTTPX vs PRIMP
```

theo kiểu:

```text
Ai nhanh hơn?
```

rồi kết luận.

Crawler production cần xem:

```text
                   Fetcher
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
  Correctness     Stability      Behavior
       │              │              │
    parsing         retry       fingerprint
    redirect        timeout       headers
    cookies         proxy         HTTP/2
```

Performance chỉ là **một yếu tố**.

---

# 28. Khi nào tôi sẽ chọn HTTPX?

Ví dụ:

```text
Novel API
REST API
Internal API
JSON service
Download service
Database service
Generic HTTP crawler
```

thì:

```python
httpx.AsyncClient()
```

là một lựa chọn rất tự nhiên.

HTTPX có async, HTTP/2, proxy, timeout, connection pool và transport abstractions phong phú. ([Httpx][3])

---

# 29. Khi nào tôi sẽ chọn PRIMP?

Nếu bài toán cần:

```text
HTTP request
+
Browser impersonation
+
Browser profile
+
TLS/HTTP2 fingerprint
```

thì:

```python
primp.Client(
    impersonate="chrome_146",
    impersonate_os="windows",
)
```

có abstraction trực tiếp cho nhu cầu đó. ([PyPI][1])

---

# 30. Và Novel Crawler của chúng ta?

Kiến trúc mục tiêu:

```text
                         Novel Crawler
                              │
                              ↓
                         Application
                              │
                              ↓
                       Fetcher Interface
                              │
                  ┌───────────┴───────────┐
                  │                       │
                  ↓                       ↓
            HttpxFetcher             PrimpFetcher
                  │                       │
                  ↓                       ↓
                httpx                   primp
                                          │
                                Browser Profile
                                          │
                             ┌────────────┼────────────┐
                             ↓            ↓            ↓
                            TLS         HTTP/2       Headers
```

Sau đó chúng ta tiếp tục thêm:

```text
Fetcher
   │
   ├── Timeout
   ├── Proxy
   ├── Browser Profile
   ├── Retry
   ├── Rate Limiting
   └── Error Classification
```

**Fetcher interface không thay đổi.**

Đó là điều quan trọng nhất của buổi này.

---

# 31. Kết luận Buổi 29

Hãy ghi nhớ bảng tư duy này:

```text
HTTPX
│
├── General-purpose HTTP client
├── Sync / Async
├── HTTP/1.1
├── HTTP/2
├── Connection Pool
├── Timeout
├── Proxy
├── Transport
└── Rich HTTP infrastructure


PRIMP
│
├── HTTP client
├── Sync / Async
├── Connection reuse
├── HTTP/1.1 / HTTP/2
├── Proxy / Timeout
└── Browser Impersonation
       │
       ├── Browser
       ├── Version
       ├── OS
       ├── Headers
       ├── TLS
       └── HTTP/2 fingerprint
```

Và với project của chúng ta:

```text
                 Application
                     │
                     ↓
               Fetcher Protocol
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
     HttpxFetcher          PrimpFetcher
          │                     │
        httpx                 primp
```

**Đây là điểm kết thúc của phần so sánh.**

### Roadmap tiếp theo

```text
21. Vì sao cần impersonation       ✅
22. Chrome fingerprint             ✅
23. Firefox / Safari / Edge        ✅
24. impersonate_os                 ✅
25. TLS fingerprint                ✅
26. HTTP/2                         ✅
27. Headers + fingerprint          ✅
28. Fingerprint thực tế            ✅
29. So sánh httpx vs primp         ✅
30. Xây BrowserClient              ← tiếp theo
```

Ở **Buổi 30**, chúng ta sẽ gom toàn bộ kiến thức 21–29 để xây một `BrowserClient` có cấu trúc sạch: **BrowserProfile → Client Factory → session lifecycle → request options → response adapter**, làm nền trực tiếp cho phần Async + Crawler từ Buổi 31.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
[2]: https://www.python-httpx.org/http2/?utm_source=chatgpt.com "HTTP/2 Support - HTTPX"
[3]: https://www.python-httpx.org/advanced/clients/?utm_source=chatgpt.com "Clients - HTTPX"
[4]: https://www.python-httpx.org/advanced/resource-limits/?utm_source=chatgpt.com "Resource Limits - HTTPX"
[5]: https://www.python-httpx.org/async/?utm_source=chatgpt.com "Async Support - HTTPX"
[6]: https://www.python-httpx.org/api/?utm_source=chatgpt.com "Developer Interface - HTTPX"
[7]: https://www.python-httpx.org/advanced/proxies/?utm_source=chatgpt.com "Proxies - HTTPX"
[8]: https://www.python-httpx.org/advanced/timeouts/?utm_source=chatgpt.com "Timeouts - HTTPX"
[9]: https://www.python-httpx.org/exceptions/?utm_source=chatgpt.com "Exceptions - HTTPX"
[10]: https://www.python-httpx.org/quickstart/?utm_source=chatgpt.com "QuickStart - HTTPX"
