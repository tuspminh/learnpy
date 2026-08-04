# Buổi 7 — Xây dựng Request Client Layer (HTTP Client)

> Sau buổi này, **mọi plugin trong framework đều bị cấm import `requests`**.

Plugin chỉ được phép gọi:

```python
response = context.http.get(url)
```

hoặc

```python
response = context.http.send(request)
```

Đây là nguyên tắc quan trọng của framework.

---

# Mục tiêu

Sau buổi này kiến trúc sẽ là

```text
                 Worker
                    │
                    ▼
               CrawlContext
                    │
                    ▼
               RequestClient
                    │
      ┌─────────────┴─────────────┐
      │                           │
RequestsHttpClient          MockHttpClient
      │                           │
      ▼                           ▼
  Internet                  Fake Response
```

Điều này giúp:

* đổi `requests` sang `httpx`
* test offline
* benchmark
* logging
* retry
* proxy
* cache

mà Plugin không cần sửa.

---

# Mục tiêu thiết kế

Framework phải đạt được:

```python
response = context.http.get(url)

response = context.http.post(url)

response = context.text(url)

response = context.download(url)
```

Plugin không biết đang dùng thư viện HTTP nào.

---

# 1. Kiến trúc

```text
crawler/

network/

    __init__.py

    request.py

    response.py

    client.py

    requests_client.py

    mock_client.py

    session.py

    retry.py

    middleware.py

    headers.py

    cookie.py

    proxy.py

    exceptions.py
```

---

# 2. Luồng Request

```text
Plugin

↓

HttpRequest

↓

Middleware

↓

Retry

↓

Session

↓

requests

↓

Internet

↓

HttpResponse

↓

Plugin
```

---

# 3. HttpRequest

```python
from dataclasses import dataclass, field

@dataclass(slots=True)
class HttpRequest:

    method: str

    url: str

    headers: dict[str, str] = field(default_factory=dict)

    params: dict = field(default_factory=dict)

    data: dict = field(default_factory=dict)

    json: dict | None = None

    timeout: int = 30

    allow_redirects: bool = True
```

Plugin không truyền tham số lung tung nữa.

---

Ví dụ

```python
request = HttpRequest(

    method="GET",

    url="https://..."
)
```

---

# 4. HttpResponse

```python
from dataclasses import dataclass

@dataclass(slots=True)
class HttpResponse:

    status_code: int

    url: str

    text: str

    headers: dict

    elapsed: float

    encoding: str

    content: bytes
```

---

Plugin sử dụng

```python
response.text

response.status_code

response.headers
```

---

# 5. HttpClient Interface

```python
from abc import ABC
from abc import abstractmethod

class HttpClient(ABC):

    @abstractmethod
    def send(
        self,
        request: HttpRequest
    ) -> HttpResponse:
        ...
```

---

Thêm helper

```python
client.get(url)

client.post(url)

client.head(url)
```

đều gọi về `send()`.

---

# 6. RequestsHttpClient

```python
import requests

class RequestsHttpClient(HttpClient):

    def __init__(self):

        self.session = requests.Session()
```

---

send()

```python
response = self.session.request(

    method=request.method,

    url=request.url,

    headers=request.headers,

    params=request.params,

    data=request.data,

    json=request.json,

    timeout=request.timeout,

    allow_redirects=request.allow_redirects
)
```

---

Convert

```python
return HttpResponse(

    status_code=response.status_code,

    url=response.url,

    text=response.text,

    headers=dict(response.headers),

    elapsed=response.elapsed.total_seconds(),

    encoding=response.encoding,

    content=response.content
)
```

---

# 7. Session Manager

Không nên

```python
requests.get()

requests.get()

requests.get()
```

Nên

```python
client = RequestsHttpClient()

client.get()

client.get()

client.get()
```

Một Session

↓

giữ Cookie

↓

Keep Alive

↓

Connection Pool

↓

nhanh hơn rất nhiều.

---

# 8. Retry Policy

```python
class RetryPolicy:

    retries = 3

    delay = 1
```

Flow

```text
GET

↓

Timeout

↓

sleep 1

↓

Retry

↓

sleep 2

↓

Retry

↓

sleep 4

↓

FAIL
```

Đây là **Exponential Backoff**.

---

# 9. Default Header

```python
DEFAULT_HEADERS = {

    "User-Agent":
    "NovelCrawler/1.0",

    "Accept-Language":
    "vi,en;q=0.9"
}
```

Mỗi request

```python
headers = DEFAULT_HEADERS | request.headers
```

---

# 10. Middleware

Kiến trúc

```text
Plugin

↓

Logging

↓

Retry

↓

Rate Limit

↓

HttpClient
```

Interface

```python
class HttpMiddleware:

    def before(
        self,
        request
    ):
        ...

    def after(

        self,

        request,

        response
    ):
        ...
```

---

Logging Middleware

```text
GET

https://abc.com

↓

200

↓

0.33 s
```

---

# 11. Mock Client

Đây là thứ giúp test plugin.

```python
class MockHttpClient(HttpClient):

    def send(
        self,
        request
    ):

        return HttpResponse(

            status_code=200,

            url=request.url,

            text="<html>Hello</html>",

            headers={},

            elapsed=0,

            encoding="utf-8",

            content=b""
        )
```

Không cần Internet.

---

# 12. Context sử dụng

Ở Buổi 6 chúng ta đã có

```python
context.http
```

Bây giờ

```python
response = context.http.get(url)
```

Plugin không cần import

```python
import requests
```

nữa.

---

# 13. CLI Test

Đây là điểm khác biệt của framework.

---

## Test GET

```bash
crawler dev http get https://example.com
```

Output

```text
GET https://example.com

Status : 200

Elapsed : 130 ms

Encoding : utf-8

Length : 124 KB
```

---

## Test HEAD

```bash
crawler dev http head https://example.com
```

Output

```text
Status : 200

Server : nginx

Content-Length : 124512
```

---

## Test Download

```bash
crawler dev http download \
    https://.../cover.jpg
```

Output

```text
Downloading...

OK

Saved

cover.jpg
```

---

## Test Benchmark

```bash
crawler dev http benchmark \
    https://example.com
```

Output

```text
Run 1

140 ms

Run 2

130 ms

Run 3

126 ms

Average

132 ms
```

---

## Test Retry

```bash
crawler dev http retry \
    https://timeout.com
```

Output

```text
Attempt 1

Timeout

Attempt 2

Timeout

Attempt 3

200 OK
```

---

## Test Mock

```bash
crawler dev http mock
```

Output

```text
Using Mock Client

Status

200
```

---

# 14. Unit Test

```python
def test_request():

    request = HttpRequest(

        method="GET",

        url="https://..."
    )

    assert request.method == "GET"
```

---

```python
def test_mock():

    client = MockHttpClient()

    response = client.get(
        "https://abc.com"
    )

    assert response.status_code == 200
```

---

```python
def test_retry():

    retry = RetryPolicy()

    assert retry.retries == 3
```

---

# 15. Cấu trúc sau Buổi 7

```text
network/

    request.py

    response.py

    client.py

    requests_client.py

    mock_client.py

    retry.py

    middleware.py

    session.py

    headers.py

    cookie.py

    proxy.py

    exceptions.py
```

---

# Luồng hoạt động

```text
Plugin

↓

Context

↓

HttpClient

↓

Middleware

↓

Retry

↓

Session

↓

requests

↓

Internet

↓

HttpResponse

↓

Plugin
```

---

# Bài tập

Hoàn thành các thành phần sau:

* `HttpRequest`
* `HttpResponse`
* `HttpClient`
* `RequestsHttpClient`
* `MockHttpClient`
* `RetryPolicy`
* `LoggingMiddleware`

Viết các lệnh CLI:

```bash
crawler dev http get URL
crawler dev http head URL
crawler dev http download URL
crawler dev http benchmark URL
crawler dev http retry URL
crawler dev http mock
```

Viết unit test cho:

* `HttpRequest`
* `HttpResponse`
* `RequestsHttpClient` (có thể mock `requests.Session`)
* `MockHttpClient`
* `RetryPolicy`
* `LoggingMiddleware`

---

# Cải tiến kiến trúc (khuyến nghị)

Thay vì để `RequestsHttpClient` tự xử lý mọi thứ trong một lớp lớn, hãy chia nhỏ theo **pipeline**:

```text
HttpClient
    │
    ▼
RequestBuilder
    │
    ▼
MiddlewarePipeline
    │
    ▼
Transport (requests/httpx)
    │
    ▼
ResponseBuilder
```

Khi đó:

* **RequestBuilder**: hợp nhất URL, query, header mặc định, cookie.
* **MiddlewarePipeline**: logging, retry, rate limit, cache, auth.
* **Transport**: chỉ chịu trách nhiệm gửi request qua `requests` hoặc `httpx`.
* **ResponseBuilder**: chuyển `requests.Response` thành `HttpResponse`.

Thiết kế này giúp mỗi lớp có một trách nhiệm rõ ràng, dễ kiểm thử bằng CLI và mở đường cho việc hỗ trợ cả HTTP đồng bộ (`requests`) và bất đồng bộ (`httpx`/`aiohttp`) trong các giai đoạn tiếp theo của framework.
