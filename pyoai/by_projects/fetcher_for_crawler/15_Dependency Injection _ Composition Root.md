# Buổi 15 — Dependency Injection + Composition Root

Ở Buổi 13–14, chúng ta đã tách được **Domain Service** và **Application Service**. Bây giờ cần giải quyết một vấn đề rất quan trọng:

> **Ai tạo các object và nối chúng lại với nhau?**

Đây chính là **Dependency Injection (DI)** và **Composition Root**.

---

# 1. Vấn đề nếu không dùng DI

Ví dụ `Fetcher` tự tạo dependency:

```python
class Fetcher:
    def __init__(self):
        self._proxy_pool = ProxyPool(...)
        self._ua_pool = UserAgentPool(...)
        self._http_client = HttpxClient(...)
        self._health_checker = HttpxProxyHealthChecker(...)
```

Thoạt nhìn khá tiện.

Nhưng kiến trúc bắt đầu gặp vấn đề:

```text
Fetcher
 ├── ProxyPool
 ├── UserAgentPool
 ├── HttpxClient
 └── HealthChecker
```

`Fetcher` bị **coupling** với implementation cụ thể.

Muốn test:

```text
Fetcher
   ↓
HttpxClient
   ↓
Internet
```

Rất khó.

Ta muốn:

```text
Fetcher
   ↓
HttpClient
   ↓
FakeHttpClient
```

để test mà không cần Internet.

---

# 2. Dependency Injection là gì?

DI nghĩa đơn giản:

> **Object không tự tạo dependency của mình. Dependency được truyền từ bên ngoài vào.**

Ví dụ:

```python
class Fetcher:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
        health_service: ProxyHealthService,
        http_client: HttpClient,
        policy: FetchPolicy,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
        self._health_service = health_service
        self._http_client = http_client
        self._policy = policy
```

`Fetcher` không biết:

```python
ProxyPool(...)
HttpxClient(...)
```

nó chỉ biết:

```text
ProxyProvider
UserAgentProvider
ProxyHealthService
HttpClient
FetchPolicy
```

Đây chính là **Dependency Inversion Principle**.

---

# 3. Constructor Injection

Đây là kiểu DI mà chúng ta sẽ dùng chủ yếu.

```python
class Fetcher:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
```

Sau đó:

```python
http_client = HttpxClient(...)
fetcher = Fetcher(http_client)
```

Hoặc test:

```python
fake_client = FakeHttpClient(...)
fetcher = Fetcher(fake_client)
```

Cùng một `Fetcher`.

```text
                    ┌── HttpxClient
                    │
Fetcher ← HttpClient
                    │
                    └── FakeHttpClient
```

Đây là lợi ích cực lớn của DI.

---

# 4. DIP trong Fetcher

Nhắc lại SOLID:

> **High-level module should not depend on low-level modules. Both should depend on abstractions.**

Không nên:

```text
Fetcher
   ↓
HttpxClient
   ↓
httpx
```

Mà:

```text
Fetcher
   ↓
HttpClient
   ↑
HttpxClient
```

`Fetcher` phụ thuộc abstraction.

`HttpxClient` implement abstraction.

---

# 5. Dependency graph của Fetcher

Sau các bài 1–14, hệ thống đã có khá nhiều component.

Ta có:

```text
                         ┌──────────────────┐
                         │   ProxyPool      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ProxyProvider
                                  │
                                  ▼
                         HealthyProxySelector
                                  │
                                  ▼
                         ProxyHealthService
                                  │
                                  ▼
                         ProxyHealthChecker
                                  │
                                  ▼
                            HttpClient
                                  │
                                  ▼
                            HttpxClient


UserAgentPool
      │
      ▼
UserAgentProvider


ErrorClassifier
      │
      ▼
FetchPolicy
      │
      ▼
    Fetcher
      │
      ▼
Application Service
```

Nhưng chúng ta không muốn mỗi class tự xây graph này.

Cần một nơi chuyên trách.

Đó là:

# Composition Root

---

# 6. Composition Root là gì?

Composition Root là:

> **Nơi duy nhất trong application chịu trách nhiệm tạo object và nối dependency lại với nhau.**

Thông thường:

```text
main.py
```

hoặc:

```text
bootstrap.py
```

hoặc:

```text
container.py
```

Ví dụ:

```text
main.py

ProxyPool
    ↓
ProxyProvider

UserAgentPool
    ↓
UserAgentProvider

HttpxClient
    ↓
HttpClient

HealthChecker
    ↓
ProxyHealthService
    ↓
HealthyProxySelector
    ↓
Fetcher
    ↓
FetchUrlService
```

---

# 7. Một nguyên tắc cực kỳ quan trọng

Các class bên trong application **không nên biết Composition Root tồn tại**.

Ví dụ `Fetcher` không được làm:

```python
class Fetcher:
    def __init__(self):
        self._http_client = HttpxClient()
```

Không.

Phải là:

```python
class Fetcher:
    def __init__(self, http_client: HttpClient):
        self._http_client = http_client
```

Sau đó `main.py`:

```python
http_client = HttpxClient()

fetcher = Fetcher(
    http_client=http_client,
)
```

---

# 8. Xây Composition Root từng bước

Giả sử project:

```text
fetcher/
├── domain/
│   ├── models/
│   │   ├── proxy.py
│   │   └── fetch.py
│   ├── services/
│   │   ├── proxy_health.py
│   │   └── proxy_selection.py
│   ├── errors.py
│   └── enums.py
│
├── application/
│   ├── services/
│   │   └── fetch_url.py
│   ├── fetcher.py
│   ├── error_classifier.py
│   └── fetch_policy.py
│
├── infrastructure/
│   └── http/
│       └── httpx_client.py
│
└── main.py
```

---

# 9. Tạo ProxyPool

```python
proxies = [
    Proxy(url=ProxyUrl("http://127.0.0.1:8080")),
    Proxy(url=ProxyUrl("http://127.0.0.1:8081")),
]
```

Sau đó:

```python
proxy_pool = ProxyPool(proxies)
```

Ta inject nó dưới dạng abstraction:

```python
proxy_provider: ProxyProvider = proxy_pool
```

Không bắt buộc phải ghi annotation như vậy trong code, nhưng về tư duy kiến trúc:

```text
ProxyPool
    implements
ProxyProvider
```

---

# 10. User-Agent Pool

```python
user_agents = [
    "Mozilla/5.0 Chrome",
    "Mozilla/5.0 Firefox",
    "Mozilla/5.0 Safari",
]

ua_pool = UserAgentPool(user_agents)
```

Fetcher chỉ cần:

```python
UserAgentProvider
```

không cần biết `UserAgentPool`.

---

# 11. HttpClient

Infrastructure tạo implementation:

```python
http_client = HttpxClient(
    config=HttpClientConfig(
        connect_timeout=10.0,
        read_timeout=20.0,
        write_timeout=10.0,
        pool_timeout=10.0,
    )
)
```

Sau đó inject:

```text
HttpxClient
    ↓ implements
HttpClient
```

---

# 12. Health Checker

Ta có:

```python
health_checker = HttpxProxyHealthChecker(
    http_client=http_client,
    health_url="https://httpbin.org/ip",
)
```

Lưu ý rất quan trọng:

`HttpxProxyHealthChecker` **không cần tự tạo `HttpxClient`**.

Sai:

```python
class HttpxProxyHealthChecker:
    def __init__(self):
        self._client = HttpxClient()
```

Đúng:

```python
class HttpxProxyHealthChecker:
    def __init__(
        self,
        http_client: HttpClient,
    ):
        self._http_client = http_client
```

---

# 13. ProxyHealthService

```python
health_service = ProxyHealthService(
    health_checker=health_checker,
)
```

Graph:

```text
HttpxClient
     ↑
HttpClient
     ↑
HealthChecker
     ↑
ProxyHealthService
```

---

# 14. HealthyProxySelector

```python
proxy_selector = HealthyProxySelector(
    proxy_provider=proxy_pool,
    health_service=health_service,
)
```

Đây là một điểm rất đẹp của DI.

`HealthyProxySelector` không cần biết:

```python
ProxyPool
```

Nó chỉ cần:

```python
ProxyProvider
ProxyHealthService
```

---

# 15. FetchPolicy

```python
policy = DefaultFetchPolicy(
    config=RetryConfig(
        max_attempts=3,
    )
)
```

---

# 16. ErrorClassifier

```python
error_classifier = DefaultErrorClassifier()
```

Sau đó Fetcher nhận nó:

```python
fetcher = Fetcher(
    proxy_selector=proxy_selector,
    user_agent_provider=ua_pool,
    http_client=http_client,
    error_classifier=error_classifier,
    policy=policy,
)
```

---

# 17. Application Service

Cuối cùng:

```python
fetch_url_service = FetchUrlService(
    fetcher=fetcher,
)
```

Bây giờ toàn bộ dependency graph đã hoàn chỉnh.

---

# 18. Composition Root hoàn chỉnh

Ví dụ:

```python
def build_application() -> FetchUrlService:

    # -------------------------
    # 1. Proxy
    # -------------------------

    proxies = [
        Proxy(url=ProxyUrl("http://127.0.0.1:8080")),
        Proxy(url=ProxyUrl("http://127.0.0.1:8081")),
    ]

    proxy_pool = ProxyPool(proxies)

    # -------------------------
    # 2. User Agent
    # -------------------------

    user_agents = [
        "Mozilla/5.0 Chrome",
        "Mozilla/5.0 Firefox",
        "Mozilla/5.0 Safari",
    ]

    user_agent_pool = UserAgentPool(user_agents)

    # -------------------------
    # 3. HTTP
    # -------------------------

    http_client = HttpxClient(
        config=HttpClientConfig(
            connect_timeout=10.0,
            read_timeout=20.0,
            write_timeout=10.0,
            pool_timeout=10.0,
        )
    )

    # -------------------------
    # 4. Health Checker
    # -------------------------

    health_checker = HttpxProxyHealthChecker(
        http_client=http_client,
        health_url="https://httpbin.org/ip",
    )

    # -------------------------
    # 5. Domain Services
    # -------------------------

    health_service = ProxyHealthService(
        health_checker=health_checker,
    )

    proxy_selector = HealthyProxySelector(
        proxy_provider=proxy_pool,
        health_service=health_service,
    )

    # -------------------------
    # 6. Policy
    # -------------------------

    error_classifier = DefaultErrorClassifier()

    policy = DefaultFetchPolicy(
        config=RetryConfig(
            max_attempts=3,
        )
    )

    # -------------------------
    # 7. Fetcher
    # -------------------------

    fetcher = Fetcher(
        proxy_selector=proxy_selector,
        user_agent_provider=user_agent_pool,
        http_client=http_client,
        error_classifier=error_classifier,
        policy=policy,
    )

    # -------------------------
    # 8. Application Service
    # -------------------------

    return FetchUrlService(
        fetcher=fetcher,
    )
```

Đây chính là **Composition Root**.

---

# 19. main.py

Sau đó `main.py` rất sạch:

```python
def main():

    service = build_application()

    command = FetchUrlCommand(url="https://example.com")

    result = service.execute(command)

    print("Status:", result.status_code)
    print(result.text)


if __name__ == "__main__":
    main()
```

Điều quan trọng là:

```text
main.py
   │
   ▼
build_application()
   │
   ├── ProxyPool
   ├── UserAgentPool
   ├── HttpxClient
   ├── HealthChecker
   ├── HealthService
   ├── ProxySelector
   ├── ErrorClassifier
   ├── FetchPolicy
   ├── Fetcher
   └── ApplicationService
```

Sau khi build xong:

```text
main
  ↓
Application Service
  ↓
Fetcher
```

---

# 20. DI giúp Testing như thế nào?

Đây mới là lợi ích lớn nhất.

Production:

```text
Fetcher
   ↓
HttpxClient
   ↓
Internet
```

Test:

```text
Fetcher
   ↓
FakeHttpClient
   ↓
Không có Internet
```

Ví dụ:

```python
class FakeHttpClient(HttpClient):
    def __init__(self, response: HttpResponse):
        self.response = response
        self.calls = []

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ) -> HttpResponse:

        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "proxy": proxy,
            }
        )

        return self.response
```

Test:

```python
fake_client = FakeHttpClient(
    HttpResponse(
        status_code=200,
        headers={},
        content=b"Hello",
        url="https://example.com",
    )
)
```

Sau đó:

```python
fetcher = Fetcher(
    proxy_selector=fake_proxy_selector,
    user_agent_provider=fake_ua_provider,
    http_client=fake_client,
    error_classifier=error_classifier,
    policy=policy,
)
```

Không Internet.

Không `httpx.Client`.

Không proxy thật.

---

# 21. DI cho toàn bộ hệ thống

Kiến trúc production-style hiện tại:

```text
                    Composition Root
                         main.py
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
     ProxyPool       UserAgentPool      HttpxClient
          │                │                 │
          ▼                ▼                 ▼
   ProxyProvider    UA Provider       HttpClient
          │                                  │
          ▼                                  ▼
 HealthyProxySelector              ProxyHealthChecker
          │                                  │
          ▼                                  ▼
  ProxyHealthService ────────────────────────┘
          │
          ▼
       Fetcher
          │
          ▼
 FetchUrlService
          │
          ▼
       CLI / GUI
```

Có thể hình dung:

```text
             ┌───────────────────────┐
             │    Composition Root   │
             │       main.py         │
             └───────────┬───────────┘
                         │
                creates + connects
                         │
                         ▼
┌───────────────────────────────────────────────────┐
│                    Application                    │
│                                                   │
│  FetchUrlService                                  │
│       ↓                                           │
│    Fetcher                                        │
│       ↓                                           │
│  ProxySelector ─── UserAgentProvider              │
│       ↓                                           │
│  ProxyHealthService                               │
│       ↓                                           │
│  HttpClient                                       │
└───────────────────────────────────────────────────┘
                         ▲
                         │
                 implementations
                         │
              ┌──────────┴──────────┐
              │                     │
         HttpxClient           FakeHttpClient
```

---

# 22. Một quy tắc rất đáng nhớ

## ❌ Không làm Dependency Injection như thế này

```python
class Fetcher:
    def __init__(
        self,
        http_client=None,
    ):
        self._http_client = http_client or HttpxClient()
```

Có vẻ tiện nhưng thực tế vẫn làm `Fetcher` biết implementation.

---

## ✅ Làm như thế này

```python
class Fetcher:
    def __init__(
        self,
        http_client: HttpClient,
    ):
        self._http_client = http_client
```

Composition Root quyết định implementation:

```python
http_client = HttpxClient()

fetcher = Fetcher(http_client=http_client)
```

---

# 23. DI không có nghĩa là phải dùng DI Framework

Python có rất nhiều DI library.

Nhưng **chưa cần**.

Đối với project Fetcher hiện tại:

```python
def build_application(): ...
```

đã là một DI container rất đơn giản.

Thậm chí nhiều Python project production vẫn dùng **manual dependency injection**.

Ưu điểm:

* dễ đọc
* dễ debug
* ít magic
* IDE hiểu tốt
* dependency graph nhìn thấy trực tiếp
* dễ test

---

# 24. Composition Root và Clean Architecture

Đây là một điểm rất quan trọng.

Ta muốn:

```text
                 Infrastructure
                       │
                       ▼
               ┌───────────────┐
               │ Composition   │
               │     Root      │
               └───────┬───────┘
                       │
                       ▼
                Application
                       │
                       ▼
                   Domain
```

Dependency trong business code:

```text
Application → Domain
```

Infrastructure implementation:

```text
Infrastructure → Domain/Application abstractions
```

Composition Root có quyền biết **tất cả**.

Ví dụ `main.py` được phép biết:

```python
ProxyPool
HttpxClient
HttpxProxyHealthChecker
Fetcher
FetchUrlService
```

Nhưng:

```python
Fetcher
```

không được biết:

```python
HttpxClient
```

---

# 25. Một nguyên tắc cực mạnh

> **Dependencies flow inward; object construction happens at the edge.**

Nói dễ hiểu:

```text
         OUTER
┌───────────────────────┐
│ HTTPX                 │
│ SQLite                │
│ Redis                 │
│ File                  │
│ CLI                   │
│ PySide6               │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Application           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Domain                │
└───────────────────────┘
         INNER
```

Domain không đi ngược ra:

```text
Domain → httpx       ❌
Domain → sqlite3     ❌
Domain → PySide6     ❌
Domain → Redis       ❌
```

---

# 26. Liên hệ trực tiếp với project Novel Crawler

Đây chính là lý do chúng ta học DI ở đây.

Sau này hệ thống của bạn sẽ có:

```text
Novel Crawler
│
├── CLI
├── PySide6
│
├── Application
│   ├── CrawlNovel
│   ├── CrawlBook
│   ├── CrawlChapter
│   └── RetryChapter
│
├── Domain
│   ├── Novel
│   ├── Book
│   ├── Chapter
│   ├── Proxy
│   └── CrawlSession
│
└── Infrastructure
    ├── HTTPX
    ├── SQLite
    ├── Redis
    └── File
```

Composition Root sẽ quyết định:

```text
Production:
HTTPX + SQLite + Redis

Test:
FakeHTTP + FakeRepository + FakeQueue
```

Không cần sửa Domain/Application.

---

# 27. Bài tập Buổi 15

### Bài 1

Vẽ dependency graph:

```text
ProxyPool
UserAgentPool
HttpxClient
HealthChecker
HealthService
ProxySelector
Fetcher
FetchUrlService
```

theo đúng thứ tự dependency.

### Bài 2

Viết:

```python
build_application()
```

sao cho **không class nào tự tạo dependency**.

### Bài 3

Thay:

```python
HttpxClient
```

bằng:

```python
FakeHttpClient
```

mà không sửa `Fetcher`.

### Bài 4 — rất quan trọng

Tạo:

```text
main.py
bootstrap.py
```

và chuyển toàn bộ object construction vào:

```python
bootstrap.py
```

Sau đó:

```python
# main.py

from bootstrap import build_application


def main():
    app = build_application()

    result = app.execute(FetchUrlCommand(url="https://example.com"))

    print(result.status_code)


if __name__ == "__main__":
    main()
```

Mục tiêu cuối buổi:

```text
main.py
   │
   ▼
bootstrap.py
   │
   ├── create dependencies
   ├── connect dependencies
   └── return Application Service
```

---

# 28. Tóm tắt Buổi 15

| Khái niệm             | Vai trò                                      |
| --------------------- | -------------------------------------------- |
| Dependency Injection  | Truyền dependency từ bên ngoài               |
| Constructor Injection | Kiểu DI chính chúng ta dùng                  |
| DIP                   | Phụ thuộc abstraction thay vì implementation |
| Composition Root      | Nơi tạo + nối toàn bộ object                 |
| `main.py`             | Entry point                                  |
| `bootstrap.py`        | Có thể chứa Composition Root                 |
| `HttpClient`          | Abstraction                                  |
| `HttpxClient`         | Production implementation                    |
| `FakeHttpClient`      | Test implementation                          |

Mental model cần nhớ:

```text
CLASS
không tự tạo dependency
        ↓
dependency được inject
        ↓
Composition Root tạo object
        ↓
Composition Root nối object
        ↓
Application chạy
```

Và đây là kiến trúc chúng ta đang hướng tới:

```text
CLI / PySide6
      │
      ▼
Application Service
      │
      ▼
    Fetcher
      │
      ├───────────────┐
      ▼               ▼
Proxy Selector    UserAgentProvider
      │
      ▼
ProxyHealthService
      │
      ▼
HttpClient
      │
      ▼
HttpxClient
```

**Buổi 16 tiếp theo: Repository cho Proxy** — lúc này chúng ta sẽ bắt đầu nối Fetcher với **persistence**, tức lưu/load Proxy từ database thay vì ProxyPool chỉ giữ dữ liệu trong memory. Đây sẽ là bước rất quan trọng để nối kiến trúc Fetcher với phần **SQLite + Repository + UoW** mà bạn đã học.
