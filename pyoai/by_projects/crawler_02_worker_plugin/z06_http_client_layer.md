# Buổi 6 — Xây dựng HTTP Client Layer

Đây là một trong những thành phần quan trọng nhất của framework.

> **Kể từ buổi này, plugin bị cấm gọi `requests.get()` hoặc `requests.Session()` trực tiếp.**

Mọi truy cập mạng phải đi qua **HttpClient**.

---

# Mục tiêu

Sau buổi này chúng ta sẽ có kiến trúc:

```text
                Worker
                   │
                   ▼
            NovelBinPlugin
                   │
                   ▼
             HttpClient
                   │
          ┌────────┴────────┐
          │                 │
      requests         MockClient
          │                 │
          ▼                 ▼
      Internet        Fake Response
```

Điều này giúp:

* đổi `requests` sang `httpx` mà không sửa plugin
* test offline
* logging tập trung
* retry tập trung
* cache tập trung

---

# 1. Cấu trúc thư mục

```text
crawler/
│
├── network/
│
├── client.py
├── request.py
├── response.py
├── middleware.py
├── session.py
├── exceptions.py
├── retry.py
├── headers.py
└── mock.py
```

---

# 2. Thiết kế Request Model

```python
from dataclasses import dataclass, field

@dataclass(slots=True)
class HttpRequest:

    method: str

    url: str

    headers: dict[str, str] = field(default_factory=dict)

    params: dict = field(default_factory=dict)

    data: dict = field(default_factory=dict)

    timeout: int = 30
```

Plugin sẽ không truyền trực tiếp vào `requests.get()` nữa.

Ví dụ:

```python
request = HttpRequest(
    method="GET",
    url="https://abc.com"
)
```

---

# 3. Thiết kế Response Model

```python
from dataclasses import dataclass

@dataclass(slots=True)
class HttpResponse:

    status_code: int

    url: str

    text: str

    headers: dict

    elapsed: float
```

Plugin chỉ làm việc với `HttpResponse`.

Không biết phía dưới dùng `requests`, `httpx` hay `aiohttp`.

---

# 4. HttpClient Interface

```python
from abc import ABC, abstractmethod

class HttpClient(ABC):

    @abstractmethod
    def send(self, request: HttpRequest) -> HttpResponse:
        ...
```

Tiện ích:

```python
def get(self, url):

    request = HttpRequest(
        method="GET",
        url=url
    )

    return self.send(request)
```

---

# 5. RequestsHttpClient

```python
import requests

class RequestsHttpClient(HttpClient):

    def __init__(self):

        self.session = requests.Session()
```

Phương thức `send()`:

```python
def send(self, request):

    response = self.session.request(
        method=request.method,
        url=request.url,
        headers=request.headers,
        params=request.params,
        data=request.data,
        timeout=request.timeout,
    )

    return HttpResponse(
        status_code=response.status_code,
        url=response.url,
        text=response.text,
        headers=dict(response.headers),
        elapsed=response.elapsed.total_seconds(),
    )
```

---

# 6. Session dùng chung

Sai:

```python
requests.get(...)

requests.get(...)

requests.get(...)
```

Đúng:

```python
client = RequestsHttpClient()

client.get(...)

client.get(...)
```

Một `Session` sẽ:

* giữ cookie
* tái sử dụng TCP connection
* nhanh hơn

---

# 7. Headers mặc định

```python
DEFAULT_HEADERS = {

    "User-Agent": "NovelCrawler/0.1",

    "Accept-Language": "vi,en;q=0.9"
}
```

Mỗi request:

```python
headers = DEFAULT_HEADERS | request.headers
```

---

# 8. Retry

Tạo lớp:

```python
class RetryPolicy:

    retries = 3

    delay = 1
```

Logic:

```text
GET

↓

Timeout

↓

retry

↓

retry

↓

retry

↓

Raise
```

Plugin không cần biết.

---

# 9. Middleware

Đây là phần mở rộng rất mạnh.

```text
Plugin

↓

LoggingMiddleware

↓

RetryMiddleware

↓

RateLimitMiddleware

↓

HttpClient
```

Interface:

```python
class Middleware:

    def before(self, request):

        ...

    def after(self, request, response):

        ...
```

Ví dụ:

Logging:

```text
GET https://abc.com

200

0.52 s
```

---

# 10. MockHttpClient

Đây là thứ giúp test offline.

```python
class MockHttpClient(HttpClient):

    def send(self, request):

        return HttpResponse(

            status_code=200,

            url=request.url,

            text="<html>Hello</html>",

            headers={},

            elapsed=0.0
        )
```

Plugin không biết đây là giả.

---

# 11. Inject HttpClient vào Plugin

Không làm:

```python
class NovelPlugin:

    def __init__(self):

        self.session = requests.Session()
```

Mà:

```python
class NovelPlugin:

    def __init__(self, client):

        self.client = client
```

Sử dụng:

```python
response = self.client.get(url)
```

Plugin không phụ thuộc `requests`.

---

# 12. CLI kiểm thử

## Test GET

```bash
crawler dev http get https://example.com
```

Output:

```text
GET https://example.com

Status : 200

Elapsed : 0.13 s

Length : 1256 bytes
```

---

## Test HEAD

```bash
crawler dev http head https://example.com
```

---

## Test Header

```bash
crawler dev http headers https://example.com
```

Output:

```text
Content-Type

Server

Content-Length
```

---

## Test Benchmark

```bash
crawler dev http benchmark https://example.com
```

Ví dụ:

```text
Run 1 120 ms

Run 2 140 ms

Run 3 118 ms

Average

126 ms
```

---

## Test Mock

```bash
crawler dev http mock
```

Output:

```text
Status : 200

Body

<html>Hello</html>
```

Không cần Internet.

---

# 13. Unit Test

Kiểm tra `HttpRequest`:

```python
def test_request():

    request = HttpRequest(
        method="GET",
        url="https://example.com"
    )

    assert request.method == "GET"
```

Kiểm tra `MockHttpClient`:

```python
def test_mock():

    client = MockHttpClient()

    response = client.get("https://abc.com")

    assert response.status_code == 200
```

Kiểm tra `RetryPolicy` bằng cách tạo một `FakeHttpClient` luôn ném `TimeoutError` trong vài lần đầu rồi trả về thành công, để xác minh số lần retry đúng như mong đợi.

---

# 14. Kiến trúc sau Buổi 6

```text
network/
│
├── client.py
├── request.py
├── response.py
├── middleware.py
├── retry.py
├── session.py
├── headers.py
├── exceptions.py
└── mock.py
```

Luồng hoạt động:

```text
Plugin

↓

HttpRequest

↓

Middleware

↓

HttpClient

↓

requests.Session

↓

Internet

↓

HttpResponse

↓

Plugin
```

---

# Bài tập

1. Tạo `HttpRequest` và `HttpResponse`.
2. Xây dựng `HttpClient` interface.
3. Cài đặt `RequestsHttpClient`.
4. Cài đặt `MockHttpClient`.
5. Thêm `RetryPolicy` cơ bản.
6. Viết `LoggingMiddleware`.
7. Viết các lệnh CLI:

   * `crawler dev http get <url>`
   * `crawler dev http head <url>`
   * `crawler dev http headers <url>`
   * `crawler dev http benchmark <url>`
   * `crawler dev http mock`
8. Viết unit test cho `HttpRequest`, `HttpResponse`, `MockHttpClient` và `RetryPolicy`.

---

# Mở rộng: Thiết kế CLI theo hướng chuyên nghiệp

Để các lệnh CLI không chỉ in kết quả mà còn phục vụ debug và tự động hóa, tôi khuyến nghị mọi lệnh đều hỗ trợ các tùy chọn chung như:

```bash
crawler dev http get https://example.com \
    --timeout 10 \
    --header "User-Agent: TestBot" \
    --save response.html \
    --json \
    --verbose
```

Các tùy chọn này sẽ được tái sử dụng ở nhiều nhóm lệnh khác (`parser`, `plugin`, `worker`...), giúp CLI thống nhất và rất thuận tiện khi phát triển cũng như khi tích hợp vào các script CI/CD.

Ở **Buổi 7**, chúng ta sẽ xây dựng **Parser Engine** dựa trên `parsel`, tách hoàn toàn việc phân tích HTML khỏi plugin. Khi đó plugin chỉ còn nhiệm vụ điều phối, còn toàn bộ XPath/CSS selector sẽ được quản lý trong một parser engine có thể kiểm thử độc lập bằng CLI như:

```bash
crawler dev parser book saved_page.html
crawler dev parser chapter saved_page.html
crawler dev xpath saved_page.html "//h1/text()"
```

Đây sẽ là bước giúp việc bảo trì parser khi website thay đổi giao diện trở nên nhanh và an toàn hơn.
