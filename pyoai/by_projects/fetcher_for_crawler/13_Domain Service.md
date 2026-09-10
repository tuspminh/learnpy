# 📘 Buổi 13 — Domain Service

Chúng ta tiếp tục đúng roadmap:

```text
01 Architecture
02 Proxy Domain Model
03 ProxyPool
04 User-Agent Pool
05 HttpClient
06 Proxy Health Checker
07 Basic Fetcher
08 Proxy Rotation
09 User-Agent Rotation
10 Retry
11 Error Handling
12 Fetch Policy
👉 13 Domain Service
14 Application Service
15 Dependency Injection
16 Repository cho Proxy
...
```

Buổi này rất quan trọng vì từ đây chúng ta bắt đầu **tách Fetcher thành kiến trúc DDD rõ ràng**, thay vì cứ thêm logic vào một class `Fetcher`.

---

# 1. Vấn đề hiện tại

Fetcher của chúng ta đang làm khá nhiều việc:

```text
Fetcher
 ├── chọn Proxy
 ├── health check Proxy
 ├── cập nhật Proxy state
 ├── chọn User-Agent
 ├── tạo headers
 ├── gọi HTTP
 ├── classify error
 ├── fetch policy
 ├── retry
 ├── rotate proxy
 └── tạo FetchResult
```

Nếu tiếp tục:

```text
Buổi 14
Buổi 15
Buổi 16
...
```

thì `Fetcher` sẽ ngày càng phình to.

Đây chính là lúc cần:

> **Domain Service**

---

# 2. Domain Service là gì?

Trong DDD:

> Domain Service chứa **business/domain logic** không tự nhiên thuộc về một Entity hoặc Value Object cụ thể.

Ví dụ:

```text
Proxy
```

biết:

```python
proxy.mark_alive()
proxy.mark_dead()
proxy.mark_success()
proxy.mark_failure()
```

Nhưng `Proxy` không nên biết:

```text
Proxy nào nên được chọn?
Proxy nào cần health check?
Nếu A chết thì chọn B?
Có cần kiểm tra lại không?
```

Đó là logic liên quan đến **nhiều Proxy**.

Vì vậy có thể đưa vào:

```text
ProxySelectionService
ProxyHealthService
```

---

# 3. Entity vs Domain Service

Đây là phần cần hiểu thật chắc.

### Entity

```python
proxy.mark_dead()
```

Proxy tự thay đổi **trạng thái của chính nó**.

---

### Domain Service

```python
selection_service.select(...)
```

Service quyết định **giữa nhiều Proxy**.

---

### Application Service

```python
fetch_service.fetch(...)
```

Application Service điều phối toàn bộ use case.

---

# 4. Ví dụ dễ hiểu

Giả sử:

```text
Proxy A
Proxy B
Proxy C
```

A:

```text
DEAD
```

B:

```text
ALIVE
```

C:

```text
UNKNOWN
```

Logic:

```text
chọn proxy
↓
health check
↓
nếu chết → proxy tiếp theo
↓
nếu sống → trả proxy
```

Không hợp lý nếu nhét tất cả vào Entity `Proxy`.

Vì một `Proxy` không thể tự biết:

```text
"hãy lấy Proxy B"
```

Do đó:

```text
ProxySelectionService
```

phù hợp hơn.

---

# 5. Kiến trúc mới

Sau Buổi 13:

```text
                    Application
                        │
                        ▼
                     Fetcher
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
 ProxySelectionService       UserAgentProvider
            │
            ├───────────────┐
            │               │
            ▼               ▼
      ProxyProvider   ProxyHealthChecker
            │               │
            ▼               ▼
         Proxy          HealthResult
```

Sau đó:

```text
Fetcher
   ↓
HttpClient
```

vẫn nằm riêng.

---

# 6. `ProxySelectionService`

Ta bắt đầu bằng interface:

```python
from abc import ABC, abstractmethod


class ProxySelectionService(ABC):
    @abstractmethod
    def select(self) -> Proxy:
        raise NotImplementedError
```

Nhưng tên này hơi gây nhầm.

Nếu service vừa:

```text
select
+
health check
+
mark state
```

thì nên đặt rõ hơn:

```python
class HealthyProxySelector(ABC):
    @abstractmethod
    def select(self) -> Proxy:
        raise NotImplementedError
```

Tên thể hiện đúng business intent:

> **Chọn một proxy khỏe.**

---

# 7. `HealthyProxySelector`

Implementation:

```python
class HealthyProxySelector:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        health_checker: ProxyHealthChecker,
    ):
        self._proxy_provider = proxy_provider
        self._health_checker = health_checker

    def select(self) -> Proxy:
        max_attempts = self._proxy_provider.get_rotation_limit()

        for _ in range(max_attempts):
            proxy = self._proxy_provider.get_proxy()

            result = self._health_checker.check(proxy)

            if result.reachable:
                proxy.mark_alive()
                return proxy

            proxy.mark_dead()

        raise NoHealthyProxyError("No healthy proxy available")
```

---

# 8. Đây có phải Domain Service không?

Có một vấn đề kiến trúc rất thú vị.

Class trên sử dụng:

```python
ProxyProvider
ProxyHealthChecker
```

Đây là abstraction/application-level dependencies.

Vì vậy trong hệ thống thực tế, ta có thể xem nó là:

```text
Domain Service
```

nếu logic lựa chọn proxy là **business rule của domain**.

Nhưng cũng có thể đặt nó ở:

```text
Application Service
```

nếu logic chủ yếu là orchestration.

Đây là điểm DDD không nên học máy móc.

---

# 9. Quy tắc phân biệt

Một cách thực dụng:

### Domain Service

Nếu logic trả lời:

> **"Business rule của hệ thống là gì?"**

Ví dụ:

```text
Không được sử dụng proxy DEAD.
Proxy phải được health check trước khi dùng.
Proxy thất bại liên tiếp phải bị loại.
```

→ Domain.

---

### Application Service

Nếu logic trả lời:

> **"Use case này được thực hiện theo trình tự nào?"**

Ví dụ:

```text
nhận URL
↓
chọn proxy
↓
chọn UA
↓
gọi HTTP
↓
classify lỗi
↓
policy
↓
retry
```

→ Application.

---

# 10. Đây là điểm rất quan trọng

Đừng biến mọi class có chữ `Service` thành Domain Service.

Ví dụ:

```python
class FetchService:
    def fetch(): ...
```

không tự động là Domain Service.

Nếu nó đang:

```text
HTTP
retry
logging
proxy
UA
```

thì phần lớn đó là **Application orchestration**.

---

# 11. Domain Service đầu tiên: Proxy Health

Ta có thể tách riêng:

```python
class ProxyHealthService:
    def __init__(
        self,
        health_checker: ProxyHealthChecker,
    ):
        self._health_checker = health_checker

    def verify(self, proxy: Proxy) -> bool:
        result = self._health_checker.check(proxy)

        if result.reachable:
            proxy.mark_alive()
            return True

        proxy.mark_dead()
        return False
```

Logic:

```text
verify(proxy)
     │
     ▼
health check
     │
 ┌───┴────┐
 │        │
alive    dead
 │        │
 ▼        ▼
mark     mark
alive    dead
```

---

# 12. Tại sao tách Health Service?

Nếu Fetcher tự viết:

```python
result = checker.check(proxy)

if result.reachable:
    proxy.mark_alive()
else:
    proxy.mark_dead()
```

thì Fetcher đang biết quá nhiều về:

```text
health check
proxy state transition
```

Tách ra:

```text
ProxyHealthService
```

Fetcher chỉ cần:

```python
if health_service.verify(proxy):
    ...
```

---

# 13. Nhưng Entity vẫn chịu trách nhiệm state

Đây là điểm cực kỳ quan trọng.

Không nên:

```python
proxy.status = ProxyStatus.DEAD
```

trong service.

Nên:

```python
proxy.mark_dead()
```

Tức là:

```text
Service
   ↓
quyết định
   ↓
Entity
   ↓
thực hiện state transition
```

Service:

> "Proxy này không healthy."

Entity:

> "Vậy tôi chuyển state của tôi sang DEAD."

Đây là cách giữ invariant trong Entity.

---

# 14. Ghép hai Service

Ta có:

```text
ProxyHealthService
```

và:

```text
HealthyProxySelector
```

Selector:

```python
class HealthyProxySelector:
    def __init__(
        self,
        proxy_provider: ProxyProvider,
        health_service: ProxyHealthService,
    ):
        self._proxy_provider = proxy_provider
        self._health_service = health_service

    def select(self) -> Proxy:
        max_attempts = self._proxy_provider.get_rotation_limit()

        for _ in range(max_attempts):
            proxy = self._proxy_provider.get_proxy()

            if self._health_service.verify(proxy):
                return proxy

        raise NoHealthyProxyError("No healthy proxy available")
```

Đẹp hơn version trước.

---

# 15. Flow mới

```text
Fetcher
   │
   ▼
HealthyProxySelector
   │
   ▼
ProxyProvider
   │
   ▼
Proxy A
   │
   ▼
ProxyHealthService
   │
   ▼
HealthChecker
   │
   ├── healthy → Proxy.mark_alive()
   │
   └── dead    → Proxy.mark_dead()
```

Nếu A chết:

```text
Selector
   ↓
Proxy B
   ↓
HealthService
   ↓
healthy
   ↓
return B
```

---

# 16. Fetcher trở nên đơn giản

Trước:

```python
proxy = self._proxy_provider.get_proxy()

result = self._health_checker.check(proxy)

if result.reachable:
    proxy.mark_alive()
else:
    proxy.mark_dead()

...
```

Sau:

```python
proxy = self._proxy_selector.select()
```

Đây là sự khác biệt rất lớn.

Fetcher không cần biết chi tiết:

```text
rotation
health check
mark_alive
mark_dead
```

---

# 17. Fetcher lúc này làm gì?

Fetcher tập trung vào:

```text
id="qf1p8a"
1. nhận FetchRequest
2. lấy healthy proxy
3. lấy User-Agent
4. tạo request context
5. gọi HttpClient
6. classify error
7. hỏi FetchPolicy
8. thực hiện decision
9. trả FetchResult
```

Đó chính là **Application orchestration**.

---

# 18. Domain Service không nên gọi HttpClient

Ví dụ này **không nên**:

```python
class ProxySelectionService:
    def select(self, url):
        response = httpx.get(url)
        ...
```

Sai vì Domain Service biết:

```text
httpx
HTTP
network
```

Domain logic bị dính Infrastructure.

Đúng:

```text
ProxySelectionService
        ↓
ProxyHealthChecker
        ↓
abstraction
```

Implementation:

```text
HttpxProxyHealthChecker
        ↓
HttpClient
        ↓
HttpxClient
```

---

# 19. Dependency graph

Kiến trúc đầy đủ:

```text
                 ┌─────────────────────┐
                 │      Fetcher        │
                 │   Application       │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
     HealthyProxy      UserAgent       FetchPolicy
       Selector         Provider
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
```

---

# 20. Domain Layer

Có thể tổ chức:

```text
fetcher/
│
├── domain/
│   │
│   ├── models/
│   │   ├── proxy.py
│   │   └── fetch.py
│   │
│   ├── services/
│   │   ├── proxy_health.py
│   │   └── proxy_selection.py
│   │
│   ├── errors.py
│   └── enums.py
│
├── application/
│   ├── fetcher.py
│   ├── error_classifier.py
│   └── fetch_policy.py
│
└── infrastructure/
    └── http/
        └── httpx_client.py
```

---

# 21. Có nên đưa `ProxyProvider` vào Domain?

Đây là một câu hỏi DDD quan trọng.

`ProxyProvider` hiện tại:

```python
class ProxyProvider(ABC):
    def get_proxy(self) -> Proxy: ...
```

Nếu nó đại diện cho nguồn cung cấp Proxy:

```text
memory
database
Redis
remote service
```

thì có thể xem nó là một **Domain abstraction**.

Implementation:

```text
ProxyPool
SQLiteProxyRepository
RedisProxyProvider
```

nằm ngoài Domain.

---

# 22. ProxyPool và Repository khác nhau

Đừng nhầm:

```text
ProxyPool
```

với:

```text
ProxyRepository
```

### ProxyPool

Runtime:

```text
"Proxy nào sẽ được dùng tiếp?"
```

### ProxyRepository

Persistence:

```text
"Proxy được lưu ở đâu?"
```

Ví dụ:

```text
ProxyRepository
       ↓
SQLite
```

và:

```text
ProxyPool
       ↓
runtime selection
```

Buổi 16 chúng ta sẽ quay lại phần Repository.

---

# 23. Một vấn đề mới: Health check mỗi request

Hiện tại:

```text
mỗi lần fetch
    ↓
health check
    ↓
request
```

Ví dụ 1000 chapter:

```text
1000 health checks
+
1000 actual requests
```

Không tối ưu.

Nhưng **chưa giải quyết ở Buổi 13**.

Sau này:

```text
last_checked_at
health TTL
cooldown
circuit breaker
```

sẽ giải quyết.

Đừng vội nhét vào hôm nay.

---

# 24. Test `ProxyHealthService`

Fake checker:

```python
class FakeProxyHealthChecker:
    def __init__(self, reachable: bool):
        self.reachable = reachable

    def check(self, proxy):
        return ProxyHealthResult(reachable=self.reachable)
```

Test alive:

```python
def test_health_service_marks_proxy_alive():
    proxy = make_proxy()

    checker = FakeProxyHealthChecker(reachable=True)

    service = ProxyHealthService(checker)

    result = service.verify(proxy)

    assert result is True
    assert proxy.status == ProxyStatus.ALIVE
```

---

# 25. Test dead

```python
def test_health_service_marks_proxy_dead():
    proxy = make_proxy()

    checker = FakeProxyHealthChecker(reachable=False)

    service = ProxyHealthService(checker)

    result = service.verify(proxy)

    assert result is False
    assert proxy.status == ProxyStatus.DEAD
```

---

# 26. Test HealthyProxySelector

Giả sử:

```text
A → DEAD
B → ALIVE
```

Fake provider:

```python
class FakeProxyProvider:
    def __init__(self, proxies):
        self._proxies = list(proxies)
        self._index = 0

    def get_proxy(self):
        proxy = self._proxies[self._index]
        self._index += 1
        return proxy

    def get_rotation_limit(self):
        return len(self._proxies)
```

Health checker:

```python
class FakeProxyHealthChecker:
    def __init__(self, results):
        self._results = iter(results)

    def check(self, proxy):
        return next(self._results)
```

Test:

```python
def test_selector_skips_dead_proxy():
    proxy_a = make_proxy("http://a:8080")
    proxy_b = make_proxy("http://b:8080")

    provider = FakeProxyProvider([proxy_a, proxy_b])

    checker = FakeProxyHealthChecker(
        [
            ProxyHealthResult(reachable=False),
            ProxyHealthResult(reachable=True),
        ]
    )

    health_service = ProxyHealthService(checker)

    selector = HealthyProxySelector(
        provider,
        health_service,
    )

    selected = selector.select()

    assert selected is proxy_b
    assert proxy_a.status == ProxyStatus.DEAD
    assert proxy_b.status == ProxyStatus.ALIVE
```

Đây là test có giá trị rất cao vì nó kiểm tra đúng business flow.

---

# 27. Test tất cả Proxy chết

```python
def test_selector_raises_when_all_proxies_dead():
    proxies = [
        make_proxy("http://a:8080"),
        make_proxy("http://b:8080"),
    ]

    provider = FakeProxyProvider(proxies)

    checker = FakeProxyHealthChecker(
        [
            ProxyHealthResult(reachable=False),
            ProxyHealthResult(reachable=False),
        ]
    )

    health_service = ProxyHealthService(checker)

    selector = HealthyProxySelector(
        provider,
        health_service,
    )

    with pytest.raises(NoHealthyProxyError):
        selector.select()
```

---

# 28. Một nguyên tắc DDD rất quan trọng

Không phải cứ:

```text
"logic phức tạp"
```

là đưa vào Domain Service.

Ví dụ:

```python
time.sleep(2)
```

không phải Domain Service.

```python
httpx.get(...)
```

không phải Domain Service.

```python
logger.info(...)
```

không phải Domain Service.

Domain Service nên chứa **domain rules**, không phải technical plumbing.

---

# 29. Phân loại trách nhiệm

Hãy nhớ bảng này:

| Component              | Trách nhiệm                            |
| ---------------------- | -------------------------------------- |
| `Proxy`                | State + invariant của một proxy        |
| `ProxyUrl`             | Validate proxy URL                     |
| `ProxyPool`            | Runtime rotation                       |
| `ProxyHealthChecker`   | Kiểm tra khả năng kết nối              |
| `ProxyHealthService`   | Áp dụng health result vào domain state |
| `HealthyProxySelector` | Tìm proxy phù hợp                      |
| `UserAgentPool`        | Rotation UA                            |
| `HttpClient`           | HTTP abstraction                       |
| `HttpxClient`          | HTTP implementation                    |
| `ErrorClassifier`      | Phân loại lỗi                          |
| `FetchPolicy`          | Quyết định xử lý lỗi                   |
| `Fetcher`              | Orchestrate use case                   |

Đây chính là kiến trúc mà chúng ta đang hướng tới.

---

# 30. Có một điều cần đặc biệt tránh

Đừng tạo:

```text
ProxyService
```

rồi nhét tất cả:

```text
ProxyService
 ├── add_proxy()
 ├── remove_proxy()
 ├── save_proxy()
 ├── health_check()
 ├── select_proxy()
 ├── rotate_proxy()
 ├── mark_dead()
 ├── retry()
 └── fetch()
```

Đó chỉ là một **God Service** thay cho God Object.

DDD không có nghĩa:

```text
mọi thứ → Service
```

Mà là:

```text
Entity
Value Object
Domain Service
Repository
Application Service
Infrastructure
```

mỗi thành phần có ranh giới rõ ràng.

---

# 31. Kiến trúc sau Buổi 13

```text
                         Crawler
                            │
                            ▼
                    Application Service
                            │
                            ▼
                         Fetcher
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
 HealthyProxy         UserAgentProvider   FetchPolicy
   Selector
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
```

Trong đó:

```text
Domain
 ├── Proxy
 ├── ProxyUrl
 ├── ProxyHealthService
 └── HealthyProxySelector

Application
 ├── Fetcher
 ├── ErrorClassifier
 └── FetchPolicy

Infrastructure
 └── HttpxClient
```

---

# 32. 🎯 Bài tập Buổi 13

Bạn nên tự code theo thứ tự này:

### Bài 1

Tạo:

```text
domain/services/proxy_health.py
```

implement:

```python
ProxyHealthService
```

---

### Bài 2

Tạo:

```text
domain/services/proxy_selection.py
```

implement:

```python
HealthyProxySelector
```

---

### Bài 3

Viết test:

```text
A alive → chọn A

A dead, B alive → chọn B

A dead, B dead, C alive → chọn C

A dead, B dead → NoHealthyProxyError
```

---

### Bài 4 — quan trọng

Hãy đảm bảo:

```text
ProxyHealthService
```

**không import `httpx`.**

Và:

```text
HealthyProxySelector
```

**không import `httpx`.**

Nếu thấy:

```python
import httpx
```

trong:

```text
domain/
```

thì gần như chắc chắn chúng ta đã phá boundary.

---

# 🧠 Tóm tắt Buổi 13

Điểm cốt lõi hôm nay:

```text
Proxy Entity
    ↓
quản lý state của chính nó

Domain Service
    ↓
xử lý business rule liên quan nhiều Entity

Application Service
    ↓
điều phối use case

Infrastructure
    ↓
thực hiện kỹ thuật
```

Với Fetcher:

```text
Proxy
  ↓
ProxyHealthService
  ↓
HealthyProxySelector
  ↓
Fetcher
  ↓
HttpClient
```

Và nguyên tắc quan trọng nhất:

> **Domain Service quyết định business rule; Entity bảo vệ state/invariant; Application Service điều phối; Infrastructure thực hiện kỹ thuật.**

---

## 🔜 Buổi 14 — Application Service

Buổi kế tiếp chúng ta sẽ lấy toàn bộ những gì đã xây dựng và thiết kế:

```text
FetchApplicationService
```

theo flow:

```text
CLI / Crawler
      ↓
FetchApplicationService
      ↓
Fetcher
      ↓
Domain Services
      ↓
Infrastructure
```

Đồng thời chúng ta sẽ phân biệt thật rõ **`Fetcher` khác `Application Service` ở đâu**, vì đây là chỗ rất dễ lẫn khi áp dụng DDD/Clean Architecture.
