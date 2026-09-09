
# Buổi 1 — Thiết kế kiến trúc Fetcher

Mục tiêu hôm nay **chưa code nhiều**.

Ta phải hiểu:

> Fetcher không phải là `httpx.get(url)`.

Trong crawler thực tế:

```text
Crawler
   │
   ▼
Application Service
   │
   ▼
Fetcher
   │
   ├── UserAgentProvider
   │
   ├── ProxyProvider
   │
   ├── ProxyHealthChecker
   │
   └── HttpClient
             │
             ▼
           httpx
             │
             ▼
          Internet
```

Điểm quan trọng nhất:

```text
Domain
   ↑
Application
   ↑
Infrastructure
```

`httpx` thuộc **Infrastructure**, không được rò rỉ vào Domain.

---

# 1. Sai lầm phổ biến

Một người mới thường viết:

```python
import httpx


class Fetcher:

    def fetch(self, url):
        proxy = self.get_proxy()

        headers = {
            "User-Agent": self.get_user_agent()
        }

        response = httpx.get(
            url,
            headers=headers,
            proxy=proxy,
            timeout=10,
        )

        return response.text
```

Nhìn rất đơn giản.

Nhưng class này đang làm quá nhiều việc:

```text
Fetcher
 ├── lấy proxy
 ├── kiểm tra proxy
 ├── chọn User-Agent
 ├── tạo HTTP request
 ├── retry
 ├── xử lý exception
 ├── đánh dấu proxy chết
 └── trả response
```

Đây là dấu hiệu vi phạm **SRP**.

---

# 2. Ta chia trách nhiệm

Thiết kế đầu tiên:

```text
                    ┌───────────────────┐
                    │      Fetcher      │
                    │  orchestration    │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      ProxyProvider    UserAgentProvider   HttpClient
             │
             ▼
        ProxyPool
             │
             ▼
     ProxyHealthChecker
```

Fetcher chỉ điều phối:

```python
proxy = proxy_provider.get()

if not health_checker.is_alive(proxy):
    ...

ua = user_agent_provider.get()

response = http_client.get(
    url,
    proxy=proxy,
    user_agent=ua,
)
```

Nó **không biết `httpx` hoạt động thế nào**.

---

# 3. Domain Layer

Ta bắt đầu từ Domain.

Cấu trúc project:

```text
crawler/
│
├── domain/
│   │
│   ├── fetch/
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   ├── interfaces.py
│   │   └── exceptions.py
│   │
│   └── proxy/
│       ├── entities.py
│       ├── value_objects.py
│       └── interfaces.py
│
├── application/
│   └── fetch/
│       └── fetcher.py
│
└── infrastructure/
    │
    ├── http/
    │   └── httpx_client.py
    │
    ├── proxy/
    │   ├── proxy_pool.py
    │   └── proxy_checker.py
    │
    └── user_agent/
        └── ua_pool.py
```

Sau này có thể mở rộng:

```text
infrastructure/
├── sqlite/
├── logging/
├── metrics/
└── config/
```

---

# 4. Proxy là Domain Concept

Proxy không nên chỉ là:

```python
proxy = "http://127.0.0.1:8080"
```

Ta muốn Domain hiểu:

```text
Proxy
 ├── url
 ├── status
 ├── failure_count
 └── last_checked
```

Ví dụ:

```python
from dataclasses import dataclass
from enum import Enum


class ProxyStatus(Enum):
    UNKNOWN = "unknown"
    ALIVE = "alive"
    DEAD = "dead"


@dataclass
class Proxy:
    url: str
    status: ProxyStatus = ProxyStatus.UNKNOWN
    failure_count: int = 0
```

Đây là **Domain Entity**.

Fetcher không cần biết proxy được lấy từ đâu.

Có thể từ:

```text
SQLite
Redis
file
API
memory
```

---

# 5. ProxyProvider

Fetcher cần proxy.

Nhưng Fetcher không nên biết:

```python
proxy_list = [...]
```

hoặc:

```python
sqlite.execute(...)
```

Ta tạo abstraction:

```python
from abc import ABC, abstractmethod


class ProxyProvider(ABC):

    @abstractmethod
    def get_proxy(self) -> Proxy:
        ...
```

Bây giờ:

```text
Fetcher
   │
   ▼
ProxyProvider
   │
   ├── InMemoryProxyProvider
   ├── SQLiteProxyProvider
   ├── RedisProxyProvider
   └── RotatingProxyProvider
```

Đây chính là **DIP**.

Fetcher phụ thuộc abstraction:

```text
Fetcher → ProxyProvider
```

không phải:

```text
Fetcher → SQLite
```

---

# 6. User-Agent cũng là abstraction

Tương tự:

```python
class UserAgentProvider(ABC):

    @abstractmethod
    def get_user_agent(self) -> str:
        ...
```

Implementation:

```python
class UserAgentPool:

    def __init__(self, user_agents: list[str]):
        self._user_agents = user_agents

    def get_user_agent(self) -> str:
        ...
```

Fetcher chỉ biết:

```python
ua_provider.get_user_agent()
```

Không quan tâm UA nằm ở đâu.

---

# 7. HTTP Client abstraction

Đây là phần cực kỳ quan trọng.

**Không viết:**

```python
class Fetcher:

    def fetch(self, url):
        httpx.get(...)
```

Thay vào đó:

```python
class HttpClient(ABC):

    @abstractmethod
    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        proxy: str | None = None,
    ):
        ...
```

Infrastructure:

```text
HttpClient
    ▲
    │
HttpxClient
```

Vậy:

```text
Application
     │
     ▼
 HttpClient
     ▲
     │
 HttpxClient
     │
     ▼
   httpx
```

`httpx` bị nhốt trong Infrastructure.

---

# 8. Proxy Health Checker

Một abstraction khác:

```python
class ProxyHealthChecker(ABC):

    @abstractmethod
    def is_alive(self, proxy: Proxy) -> bool:
        ...
```

Implementation sau này:

```python
class HttpxProxyHealthChecker:
    ...
```

Nó có thể thực hiện:

```text
Proxy
 │
 ▼
GET health-check URL
 │
 ├── 200 → ALIVE
 │
 ├── timeout → DEAD
 │
 ├── connection error → DEAD
 │
 └── invalid response → DEAD
```

Fetcher không cần biết cách kiểm tra.

---

# 9. Fetcher lúc này trở nên rất nhỏ

Về mặt ý tưởng:

```python
class Fetcher:

    def __init__(
        self,
        proxy_provider,
        user_agent_provider,
        proxy_health_checker,
        http_client,
    ):
        self.proxy_provider = proxy_provider
        self.user_agent_provider = user_agent_provider
        self.proxy_health_checker = proxy_health_checker
        self.http_client = http_client

    def fetch(self, url):
        proxy = self.proxy_provider.get_proxy()

        if not self.proxy_health_checker.is_alive(proxy):
            ...

        user_agent = self.user_agent_provider.get_user_agent()

        return self.http_client.get(
            url,
            headers={
                "User-Agent": user_agent,
            },
            proxy=proxy.url,
        )
```

Đây mới chỉ là **skeleton**.

Chúng ta chưa xử lý:

```text
retry
rotation
dead proxy
timeout
status code
redirect
cookies
robots
rate limit
```

Những phần đó sẽ xây dần.

---

# 10. Dòng chảy hoàn chỉnh

Khi fetch:

```text
                    fetch(url)
                         │
                         ▼
                  ┌─────────────┐
                  │   Fetcher   │
                  └──────┬──────┘
                         │
                         ▼
                  get_proxy()
                         │
                         ▼
                    ProxyPool
                         │
                         ▼
                     Proxy A
                         │
                         ▼
                  is_alive(A)?
                    /         \
                  NO           YES
                  │             │
                  ▼             ▼
             Proxy B       get_user_agent()
                                │
                                ▼
                              UA #3
                                │
                                ▼
                          HttpxClient
                                │
                                ▼
                             httpx
                                │
                                ▼
                              URL
```

Nếu Proxy A chết:

```text
Proxy A
   ↓
health check
   ↓
DEAD
   ↓
ProxyPool loại A
   ↓
Proxy B
   ↓
health check
   ↓
ALIVE
   ↓
fetch
```

---

# 11. SOLID map

Kiến trúc này tương ứng khá rõ:

| Principle   | Áp dụng                                                               |
| ----------- | --------------------------------------------------------------------- |
| **S — SRP** | ProxyPool, UA Pool, HealthChecker, HttpClient mỗi cái một trách nhiệm |
| **O — OCP** | Có thể thêm `RedisProxyProvider` mà không sửa Fetcher                 |
| **L — LSP** | `HttpxClient` thay thế `HttpClient`                                   |
| **I — ISP** | Interface nhỏ: ProxyProvider, UAProvider, HealthChecker               |
| **D — DIP** | Fetcher phụ thuộc abstraction                                         |

Đặc biệt:

```text
Fetcher
   ↓
abstraction
   ↓
Infrastructure
```

chứ không phải:

```text
Fetcher
   ↓
httpx
   ↓
SQLite
```

---

# 12. DDD map

Ta cũng có:

### Entity

```python
Proxy
```

### Value Object

Sau này có thể tạo:

```python
ProxyUrl
```

thay vì dùng raw `str`.

### Domain Service

Ví dụ:

```text
ProxySelectionService
```

để quyết định proxy nào được sử dụng.

### Application Service

```text
Fetcher
```

điều phối use case:

```text
Fetch URL
```

### Infrastructure

```text
HttpxClient
SQLiteProxyRepository
HttpxProxyHealthChecker
```

---

# 13. Một nguyên tắc rất quan trọng

Ta **không nên để Domain biết HTTP**.

Ví dụ đây là thiết kế không tốt:

```python
@dataclass
class Proxy:

    url: str

    def check(self):
        response = httpx.get(self.url)
```

Sai boundary:

```text
Domain
  ↓
httpx
```

Đúng phải là:

```text
Domain
  ↑
ProxyHealthChecker
  ↑
HttpxProxyHealthChecker
  ↑
httpx
```

---

# 14. Dependency Graph

Toàn bộ dependency cuối cùng sẽ giống:

```text
                 APPLICATION
                     │
                     ▼
                  Fetcher
                  /  |  \
                 /   |   \
                ▼    ▼    ▼
        ProxyProvider UAProvider HttpClient
                │              │
                │              │
                ▼              ▼
          ProxyPool       HttpxClient
                │              │
                ▼              ▼
       ProxyHealthChecker     httpx
                │
                ▼
        HttpxProxyHealthChecker
```

Infrastructure nằm bên ngoài.

---

# 15. Bài tập Buổi 1

Trước khi sang Buổi 2, hãy tự thiết kế 4 interface:

```text
ProxyProvider
UserAgentProvider
ProxyHealthChecker
HttpClient
```

và trả lời 4 câu:

### Câu 1

Tại sao không viết:

```python
Fetcher → httpx
```

mà viết:

```python
Fetcher → HttpClient
             ↑
         HttpxClient
```

### Câu 2

Nếu ngày mai ta muốn đổi:

```text
httpx
```

sang:

```text
requests
```

thì phần nào phải thay đổi?

### Câu 3

Nếu proxy được lưu trong:

```text
SQLite
```

sau đó chuyển sang:

```text
Redis
```

Fetcher có cần sửa không?

### Câu 4

Tại sao `Proxy` nên là Domain Entity thay vì chỉ:

```python
proxy: str
```

---

**Buổi 2 chúng ta sẽ đi sâu vào `Proxy` Domain Model:** `Proxy`, `ProxyStatus`, `ProxyUrl`, failure count, health state và các invariant — sau đó tự xây **ProxyPool + rotation** mà chưa đụng tới `httpx`.
