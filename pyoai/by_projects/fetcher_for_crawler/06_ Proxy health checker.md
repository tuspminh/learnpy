# Buổi 6 — Proxy Health Checker

Ở buổi này ta xây dựng **Proxy Health Checker** — thành phần chịu trách nhiệm kiểm tra proxy còn hoạt động hay không **trước khi Fetcher dùng proxy đó để crawl**.

Mục tiêu:

```text
Fetcher
   │
   ▼
ProxyProvider
   │
   ▼
Proxy A
   │
   ▼
HealthChecker
   │
   ├── DEAD ──────► ProxyPool chọn proxy khác
   │
   └── ALIVE
          │
          ▼
      HttpClient
          │
          ▼
       GET URL
```

Điểm quan trọng của kiến trúc:

> **HealthChecker kiểm tra proxy, còn HttpClient chỉ chịu trách nhiệm gửi HTTP request.**

---

# 1. Vì sao cần Health Checker?

Giả sử pool có:

```text
Proxy A → chết
Proxy B → sống
Proxy C → chết
```

Nếu Fetcher lấy ngẫu nhiên:

```text
Proxy A
   ↓
GET target.com
   ↓
Connection timeout
   ↓
Retry
   ↓
Proxy A
   ↓
Timeout
```

Ta đang lãng phí thời gian.

Thay vào đó:

```text
Proxy A
   ↓
Health Check
   ↓
DEAD
   ↓
bỏ qua

Proxy B
   ↓
Health Check
   ↓
ALIVE
   ↓
GET target.com
```

---

# 2. Nhưng có một vấn đề rất quan trọng

**HTTP request tới website bị lỗi không đồng nghĩa proxy chết.**

Ví dụ:

```text
Proxy A
   ↓
example.com
   ↓
403 Forbidden
```

Điều này có thể nghĩa là:

```text
Proxy vẫn sống
Website từ chối request
```

Không nên làm:

```python
if response.status_code == 403:
    proxy.mark_dead()
```

Ngược lại:

```text
Proxy A
   ↓
Health check
   ↓
Connection timeout
```

thì mới có cơ sở mạnh hơn để đánh dấu:

```python
proxy.mark_dead()
```

Đây là một distinction rất quan trọng trong crawler production.

---

# 3. Interface `ProxyHealthChecker`

Domain/Application không biết `httpx`.

Ta tạo abstraction:

```python
from abc import ABC, abstractmethod

from domain.entities.proxy import Proxy


class ProxyHealthChecker(ABC):
    @abstractmethod
    def check(self, proxy: Proxy) -> bool:
        raise NotImplementedError
```

Ý nghĩa:

```text
Application
     │
     ▼
ProxyHealthChecker
     ▲
     │
HttpxProxyHealthChecker
```

Sau này có thể có:

```text
HttpxProxyHealthChecker
FakeProxyHealthChecker
SeleniumProxyHealthChecker
RequestsProxyHealthChecker
```

mà Fetcher không cần thay đổi.

---

# 4. Health check URL

Không nên hard-code:

```python
https://example.com
```

Ta cấu hình:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyHealthCheckConfig:
    url: str = "https://httpbin.org/ip"
    timeout: float = 5.0
```

Nhưng trong production, URL nên là một endpoint phù hợp với hệ thống của bạn.

Ví dụ:

```text
https://your-health-check-server.com/ping
```

hoặc một endpoint rất nhẹ.

---

# 5. Tận dụng `HttpClient`

Ta đã có abstraction:

```python
class HttpClient(ABC):
    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        proxy: str | None = None,
    ) -> HttpResponse:
        raise NotImplementedError
```

HealthChecker không cần biết `httpx`.

Nó chỉ biết:

```text
HttpClient
```

---

# 6. Implementation

Tạo:

```text
infrastructure/
└── http/
    ├── httpx_client.py
    └── httpx_proxy_health_checker.py
```

Code:

```python
class HttpxProxyHealthChecker(ProxyHealthChecker):
    def __init__(
        self,
        http_client: HttpClient,
        config: ProxyHealthCheckConfig,
    ):
        self._http_client = http_client
        self._config = config

    def check(self, proxy: Proxy) -> bool:

        try:
            response = self._http_client.get(
                self._config.url,
                proxy=proxy.url.value,
            )

        except FetchError:
            proxy.mark_dead()
            return False

        if 200 <= response.status_code < 400:
            proxy.mark_alive()
            return True

        return False
```

Ta có:

```text
HttpxProxyHealthChecker
        │
        ▼
     HttpClient
        │
        ▼
    HttpxClient
        │
        ▼
      httpx
```

---

# 7. Một vấn đề: status code

Ta phải phân biệt:

### Proxy connection failure

```text
timeout
connection refused
DNS/network failure
```

→ proxy có khả năng chết.

### HTTP response

```text
200
301
403
404
429
500
```

→ proxy **đã truyền request tới server thành công**.

Do đó:

```text
403
```

không nên tự động:

```python
proxy.mark_dead()
```

Ví dụ:

```python
if 200 <= response.status_code < 400:
    proxy.mark_alive()
    return True

return False
```

Ở phiên bản đơn giản, `False` có thể nghĩa:

> Health check không đạt.

Nhưng **không nhất thiết phải đánh dấu proxy DEAD**.

---

# 8. Tách `reachable` và `healthy`

Đây là thiết kế tốt hơn.

Thay vì:

```python
check() -> bool
```

ta có:

```python
@dataclass(frozen=True)
class ProxyHealthResult:
    reachable: bool
    status_code: int | None = None
```

Ví dụ:

```text
timeout:

reachable = False
status_code = None
```

Trong khi:

```text
403:

reachable = True
status_code = 403
```

Điều này rất hữu ích.

---

# 9. Thiết kế `ProxyHealthResult`

```python
@dataclass(frozen=True)
class ProxyHealthResult:
    reachable: bool
    status_code: int | None = None
```

Có thể thêm:

```python
@dataclass(frozen=True)
class ProxyHealthResult:
    reachable: bool
    status_code: int | None = None
    latency: float | None = None
```

Sau này metrics có thể dùng:

```text
Proxy A
reachable = True
latency = 0.82s
```

---

# 10. Health Checker tốt hơn

Ta thiết kế:

```python
class ProxyHealthChecker(ABC):
    @abstractmethod
    def check(self, proxy: Proxy) -> ProxyHealthResult:
        raise NotImplementedError
```

Implementation:

```python
class HttpxProxyHealthChecker(ProxyHealthChecker):
    def __init__(
        self,
        http_client: HttpClient,
        config: ProxyHealthCheckConfig,
    ):
        self._http_client = http_client
        self._config = config

    def check(self, proxy: Proxy) -> ProxyHealthResult:

        try:
            response = self._http_client.get(
                self._config.url,
                proxy=proxy.url.value,
            )

        except FetchError:
            return ProxyHealthResult(
                reachable=False,
            )

        return ProxyHealthResult(
            reachable=True,
            status_code=response.status_code,
        )
```

Bây giờ HealthChecker **không tự ý thay đổi domain state**.

Đây là một lựa chọn kiến trúc rất đáng chú ý.

---

# 11. Ai cập nhật Proxy?

Có hai cách.

### Cách 1 — HealthChecker cập nhật Entity

```text
HealthChecker
      ↓
Proxy.mark_alive()
Proxy.mark_dead()
```

Đơn giản.

### Cách 2 — Application Service cập nhật Entity

```text
HealthChecker
      ↓
ProxyHealthResult
      ↓
Application Service
      ↓
Proxy.mark_alive()
Proxy.mark_dead()
```

Với hệ thống DDD lớn, ta ưu tiên **Cách 2** vì HealthChecker tập trung vào:

> kiểm tra.

Còn Application Service chịu trách nhiệm:

> điều phối và thay đổi state.

---

# 12. Application logic

Ví dụ:

```python
result = health_checker.check(proxy)

if result.reachable:
    proxy.mark_alive()
else:
    proxy.mark_dead()
```

Flow:

```text
Proxy
  │
  ▼
HealthChecker
  │
  ▼
ProxyHealthResult
  │
  ▼
Application Service
  │
  ├── reachable=True
  │       ↓
  │   mark_alive()
  │
  └── reachable=False
          ↓
      mark_dead()
```

Đây là thiết kế sạch hơn.

---

# 13. Proxy Health Check Service

Ta có thể tạo domain/application service:

```python
class ProxyHealthService:
    def __init__(
        self,
        checker: ProxyHealthChecker,
    ):
        self._checker = checker

    def ensure_healthy(self, proxy: Proxy) -> bool:

        result = self._checker.check(proxy)

        if result.reachable:
            proxy.mark_alive()
            return True

        proxy.mark_dead()
        return False
```

Tên:

```text
ProxyHealthService
```

chịu trách nhiệm điều phối health checking.

---

# 14. Fetcher bắt đầu có logic thực tế

Sau buổi 6, Fetcher có thể hoạt động như:

```python
class Fetcher:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
        health_checker: ProxyHealthChecker,
        http_client: HttpClient,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
        self._health_checker = health_checker
        self._http_client = http_client
```

Khi fetch:

```python
proxy = self._proxy_provider.get_proxy()

health = self._health_checker.check(proxy)

if not health.reachable:
    proxy.mark_dead()
    # chọn proxy khác

proxy.mark_alive()

user_agent = self._user_agent_provider.get_user_agent()
```

Đây chính là nền móng cho **Buổi 7 — Fetcher cơ bản**.

---

# 15. Test bằng Fake

Đây là chỗ kiến trúc DI phát huy tác dụng.

Không cần Internet.

```python
class FakeProxyHealthChecker(ProxyHealthChecker):
    def __init__(self, result: ProxyHealthResult):
        self.result = result
        self.checked_proxies = []

    def check(self, proxy: Proxy) -> ProxyHealthResult:
        self.checked_proxies.append(proxy)
        return self.result
```

Test proxy sống:

```python
def test_proxy_is_alive():

    proxy = Proxy(url=ProxyUrl("http://127.0.0.1:8080"))

    checker = FakeProxyHealthChecker(
        ProxyHealthResult(
            reachable=True,
            status_code=200,
        )
    )

    result = checker.check(proxy)

    assert result.reachable is True
    assert result.status_code == 200
```

Test proxy chết:

```python
def test_proxy_is_dead():

    proxy = Proxy(url=ProxyUrl("http://127.0.0.1:8080"))

    checker = FakeProxyHealthChecker(
        ProxyHealthResult(
            reachable=False,
        )
    )

    result = checker.check(proxy)

    assert result.reachable is False
```

---

# 16. Test quan trọng hơn

Ta muốn đảm bảo **403 không bị coi là proxy chết**:

```python
def test_403_means_proxy_is_reachable():

    checker = FakeProxyHealthChecker(
        ProxyHealthResult(
            reachable=True,
            status_code=403,
        )
    )

    result = checker.check(proxy)

    assert result.reachable is True
    assert result.status_code == 403
```

Đây là test rất quan trọng đối với crawler.

---

# 17. Kiến trúc sau Buổi 6

```text
                    APPLICATION
                         │
                         ▼
                      Fetcher
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ProxyProvider    UAProvider    HealthChecker
          │              │              │
          ▼              ▼              ▼
      ProxyPool        UAPool      ProxyHealthService
                                       │
                                       ▼
                                   HttpClient
                                       │
                                       ▼
                                  HttpxClient
                                       │
                                       ▼
                                     httpx
```

Điểm quan trọng:

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

và **không được để**:

```text
Domain → httpx
Application → httpx
```

---

# 18. SOLID trong Buổi 6

### SRP

`HttpxProxyHealthChecker`:

> chỉ kiểm tra proxy.

Không:

* chọn proxy
* xoay User-Agent
* crawl chapter
* parse HTML
* lưu database.

---

### OCP

Có thể thêm:

```text
HttpxProxyHealthChecker
SocksProxyHealthChecker
CloudProxyHealthChecker
FakeProxyHealthChecker
```

mà không sửa Fetcher.

---

### LSP

```python
ProxyHealthChecker
```

có thể được thay bằng:

```python
HttpxProxyHealthChecker
FakeProxyHealthChecker
```

---

### ISP

Interface rất nhỏ:

```python
check(proxy)
```

Không ép implementation phải implement hàng loạt method không cần thiết.

---

### DIP

Fetcher phụ thuộc:

```python
ProxyHealthChecker
```

không phụ thuộc:

```python
HttpxProxyHealthChecker
```

và càng không phụ thuộc:

```python
httpx
```

---

# 19. Một cải tiến rất quan trọng cho production

Không nên health-check **mọi request** mãi mãi.

Nếu có:

```text
1000 chapter
100 proxy
```

mỗi chapter lại:

```text
health check
+
actual request
```

thì số request tăng rất nhiều.

Sau này ta sẽ cần:

```text
Proxy
 ├── last_checked_at
 ├── failure_count
 ├── success_count
 └── status
```

và chính Entity `Proxy` của chúng ta đã có:

```python
last_checked_at
```

Nó sẽ cho phép thiết kế:

```text
Proxy chưa check quá 60 giây
        ↓
     Health Check

Proxy vừa check 10 giây trước
        ↓
     dùng luôn
```

Đây sẽ liên quan trực tiếp tới **Proxy State + Circuit Breaker** ở các buổi sau.

---

# 20. Kết quả sau Buổi 6

Đến đây ta đã xây được:

```text
                    Fetcher
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  ProxyProvider   UAProvider     HealthChecker
       │               │               │
       ▼               ▼               ▼
   ProxyPool         UAPool      ProxyHealthResult
                                       │
                                       ▼
                                  HttpClient
                                       │
                                       ▼
                                  HttpxClient
                                       │
                                       ▼
                                     httpx
```

Và nguyên tắc quan trọng nhất của buổi này là:

> **Proxy health ≠ target-site success.**

Ví dụ:

```text
Proxy → target
       │
       ├── timeout       → proxy có thể DEAD
       ├── connection error → proxy có thể DEAD
       ├── 200           → proxy reachable
       ├── 403           → proxy reachable, target từ chối
       ├── 429           → proxy reachable, bị rate-limit
       └── 500           → proxy reachable, server lỗi
```

**Buổi 7 tiếp theo:** chúng ta sẽ ghép toàn bộ những thành phần đã học thành **Fetcher cơ bản hoàn chỉnh**:

```text
Fetcher
  ↓
chọn Proxy
  ↓
Health Check
  ↓
chọn User-Agent
  ↓
build request
  ↓
HttpClient
  ↓
GET URL
  ↓
FetchResult
```

và bắt đầu thiết kế `FetchResult`, `FetchRequest`, exception boundary và vòng đời một request.
