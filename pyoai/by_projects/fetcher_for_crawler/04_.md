# Buổi 4 — User-Agent Pool + Request Context

Hôm nay ta xây phần **User-Agent rotation** và ghép nó với Proxy theo đúng hướng DDD + SOLID.

Mục tiêu cuối buổi:

```text
Fetcher
   │
   ├── ProxyProvider
   │       └── ProxyPool
   │
   └── UserAgentProvider
           └── UserAgentPool
```

Fetcher sẽ lấy được:

```text
Proxy
User-Agent
```

nhưng **chưa gọi `httpx`**.

---

# 1. Vì sao User-Agent cũng cần abstraction?

Không nên viết trực tiếp trong Fetcher:

```python
USER_AGENTS = [
    "...",
    "...",
    "...",
]
```

rồi:

```python
random.choice(USER_AGENTS)
```

Vì Fetcher đang phải biết cách chọn UA.

Ta muốn:

```text
Fetcher
   │
   ▼
UserAgentProvider
   │
   ▼
UserAgentPool
```

Fetcher chỉ hỏi:

```python
user_agent = provider.get_user_agent()
```

---

# 2. Tạo `UserAgentProvider`

Tạo:

```text
domain/
└── fetch/
    └── interfaces.py
```

```python
from abc import ABC, abstractmethod


class UserAgentProvider(ABC):

    @abstractmethod
    def get_user_agent(self) -> str:
        raise NotImplementedError
```

Đây là interface rất nhỏ.

Nó tuân thủ **ISP**:

> Interface chỉ yêu cầu đúng một hành vi mà client cần.

---

# 3. User-Agent có phải Entity không?

Không.

Một User-Agent string:

```text
Mozilla/5.0 ...
```

không có identity riêng trong domain của chúng ta.

Ta có thể coi nó là một **Value** đơn giản.

Do đó chưa cần:

```python
@dataclass
class UserAgent:
    ...
```

Chỉ cần:

```python
str
```

là đủ ở giai đoạn này.

---

# 4. UserAgentPool

Tạo:

```text
infrastructure/
└── user_agent/
    └── ua_pool.py
```

Code:

```python
from domain.fetch.interfaces import UserAgentProvider


class UserAgentPool(UserAgentProvider):

    def __init__(self, user_agents: list[str]):
        if not user_agents:
            raise ValueError(
                "User-Agent pool cannot be empty"
            )

        self._user_agents = user_agents
        self._index = 0

    def get_user_agent(self) -> str:

        user_agent = self._user_agents[self._index]

        self._index = (
            self._index + 1
        ) % len(self._user_agents)

        return user_agent
```

---

# 5. Hoạt động thế nào?

Giả sử:

```python
uas = [
    "UA-1",
    "UA-2",
    "UA-3",
]
```

Ta có:

```text
request 1 → UA-1
request 2 → UA-2
request 3 → UA-3
request 4 → UA-1
request 5 → UA-2
```

Đây cũng là Round-Robin.

---

# 6. Test

```python
def test_user_agent_round_robin():

    pool = UserAgentPool(
        [
            "UA-1",
            "UA-2",
            "UA-3",
        ]
    )

    assert pool.get_user_agent() == "UA-1"
    assert pool.get_user_agent() == "UA-2"
    assert pool.get_user_agent() == "UA-3"
    assert pool.get_user_agent() == "UA-1"
```

---

# 7. Không cho User-Agent rỗng

Ta nên bảo vệ invariant:

```python
UserAgentPool([
    "",
    "UA-2",
])
```

không nên tồn tại.

Ta có thể validate:

```python
class UserAgentPool(UserAgentProvider):

    def __init__(self, user_agents: list[str]):

        cleaned = [
            ua.strip()
            for ua in user_agents
            if ua.strip()
        ]

        if not cleaned:
            raise ValueError(
                "User-Agent pool cannot be empty"
            )

        self._user_agents = cleaned
        self._index = 0

    def get_user_agent(self) -> str:

        user_agent = self._user_agents[self._index]

        self._index = (
            self._index + 1
        ) % len(self._user_agents)

        return user_agent
```

Ví dụ:

```python
pool = UserAgentPool(
    [
        "",
        "  ",
        "UA-1",
    ]
)
```

kết quả chỉ còn:

```text
UA-1
```

---

# 8. Không nên random quá sớm

Ta có thể dùng:

```python
random.choice(...)
```

nhưng chưa cần.

Round-Robin có lợi thế:

```text
A → B → C → A
```

dễ test:

```python
assert ...
```

và dễ debug.

Sau này nếu cần, ta có thể thiết kế:

```text
UserAgentSelectionStrategy
       │
       ├── RoundRobin
       ├── Random
       └── Weighted
```

---

# 9. Bây giờ ghép Proxy + User-Agent

Một HTTP request thực tế có:

```text
RequestContext
 ├── URL
 ├── Proxy
 └── User-Agent
```

Ta có thể tạo một object biểu diễn thông tin cần thiết cho fetch.

Ví dụ:

```python
from dataclasses import dataclass

from domain.proxy.entities import Proxy


@dataclass(frozen=True)
class FetchContext:

    proxy: Proxy
    user_agent: str
```

Nhưng ở đây có một vấn đề.

`FetchContext` thuộc Domain nào?

Nó không phải Proxy.

Nó cũng không phải HTTP implementation.

Nó là **input/value của Fetch use case**.

Do đó đặt:

```text
domain/
└── fetch/
    ├── entities.py
    ├── interfaces.py
    └── value_objects.py
```

---

# 10. `FetchContext`

```python
from dataclasses import dataclass

from domain.proxy.entities import Proxy


@dataclass(frozen=True)
class FetchContext:

    proxy: Proxy
    user_agent: str
```

Dùng:

```python
context = FetchContext(
    proxy=proxy,
    user_agent="UA-1",
)
```

---

# 11. Nhưng có nên đưa Proxy Entity vào HTTP Context?

Đây là câu hỏi kiến trúc thú vị.

Có hai hướng.

### Cách 1

```text
FetchContext
 ├── Proxy
 └── UserAgent
```

Ưu điểm:

* Domain rõ ràng
* giữ được thông tin proxy
* dễ update state

### Cách 2

Chỉ truyền:

```text
proxy_url
user_agent
```

Ví dụ:

```python
@dataclass(frozen=True)
class RequestOptions:

    proxy: str | None
    user_agent: str
```

Cách này gần Infrastructure hơn.

Ở giai đoạn hiện tại ta chọn **Cách 1**, vì Proxy Entity còn cần được cập nhật:

```text
request success
      ↓
proxy.mark_success()

request failure
      ↓
proxy.mark_failure()
```

---

# 12. `FetchContext` không gọi HTTP

Đây là nguyên tắc quan trọng.

Không làm:

```python
@dataclass
class FetchContext:

    def execute(self):
        httpx.get(...)
```

Sai boundary.

`FetchContext` chỉ là data:

```text
Proxy
User-Agent
```

---

# 13. Tạo `RequestHeaders`

Ta cũng có thể tạo:

```python
@dataclass(frozen=True)
class RequestHeaders:

    user_agent: str
```

nhưng hiện tại hơi over-engineering.

Ta giữ đơn giản:

```python
user_agent: str
```

Khi có thêm:

```text
Accept
Accept-Language
Referer
Connection
Cookie
```

ta sẽ cân nhắc tạo `RequestHeaders`.

---

# 14. Fetcher bắt đầu có hình dạng

Hiện tại:

```python
class Fetcher:

    def __init__(
        self,
        proxy_provider: ProxyProvider,
        user_agent_provider: UserAgentProvider,
    ):
        self._proxy_provider = proxy_provider
        self._user_agent_provider = user_agent_provider
```

Sau đó:

```python
def build_context(self) -> FetchContext:

    proxy = self._proxy_provider.get_proxy()

    user_agent = (
        self._user_agent_provider
        .get_user_agent()
    )

    return FetchContext(
        proxy=proxy,
        user_agent=user_agent,
    )
```

Fetcher lúc này chưa fetch.

Nó chỉ tạo context.

---

# 15. Flow hiện tại

```text
                 Fetcher
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
  ProxyProvider       UserAgentProvider
          │                   │
          ▼                   ▼
     ProxyPool           UserAgentPool
          │                   │
          ▼                   ▼
       Proxy                 UA
          └─────────┬─────────┘
                    ▼
              FetchContext
```

Đây là một bước tiến quan trọng.

---

# 16. Một request cụ thể

Ví dụ pool:

```text
Proxy:
A
B
C
```

UA:

```text
UA-1
UA-2
UA-3
```

Lần request:

```text
Request 1
Proxy A
UA-1

Request 2
Proxy B
UA-2

Request 3
Proxy C
UA-3

Request 4
Proxy A
UA-1
```

Đây là hành vi deterministic.

---

# 17. Proxy và UA độc lập

Một điểm rất quan trọng:

Không làm:

```text
Proxy A → UA A
Proxy B → UA B
Proxy C → UA C
```

bắt buộc.

Hai pool độc lập:

```text
ProxyPool
A B C

UAPool
1 2 3 4 5
```

Nên có thể:

```text
A + UA1
B + UA2
C + UA3
A + UA4
B + UA5
C + UA1
```

Điều này giúp các component có tính độc lập cao hơn.

---

# 18. Test FetchContext

```python
def test_build_fetch_context():

    proxy = Proxy(
        ProxyUrl("http://proxy-a:8080")
    )

    proxy_pool = ProxyPool([proxy])

    ua_pool = UserAgentPool(
        ["UA-1"]
    )

    fetcher = Fetcher(
        proxy_provider=proxy_pool,
        user_agent_provider=ua_pool,
    )

    context = fetcher.build_context()

    assert context.proxy is proxy
    assert context.user_agent == "UA-1"
```

Chưa cần Internet.

Chưa cần `httpx`.

Đây chính là lợi ích của kiến trúc.

---

# 19. SOLID nhìn từ Buổi 4

### SRP

`UserAgentPool` chỉ:

```text
quản lý User-Agent + rotation
```

Không:

```text
❌ HTTP
❌ Proxy
❌ Retry
```

### DIP

Fetcher phụ thuộc:

```text
UserAgentProvider
```

không phụ thuộc:

```text
UserAgentPool
```

### OCP

Sau này:

```text
UserAgentProvider
       ▲
       │
       ├── StaticUserAgentProvider
       ├── RoundRobinUserAgentPool
       ├── RandomUserAgentPool
       └── DatabaseUserAgentProvider
```

Fetcher không đổi.

---

# 20. Cấu trúc project sau Buổi 4

```text
crawler/
│
├── domain/
│   │
│   ├── proxy/
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   └── interfaces.py
│   │
│   └── fetch/
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
    ├── proxy/
    │   └── proxy_pool.py
    │
    └── user_agent/
        └── ua_pool.py
```

---

# 21. Một điểm cần sửa so với các buổi trước

Ta đang dùng:

```text
ProxyPool
```

trong `infrastructure`.

Nếu `ProxyPool` chỉ là **runtime selection algorithm**, điều này hợp lý.

Nhưng nếu sau này ta quyết định:

```text
ProxyPool = Domain concept
```

thì có thể chuyển nó vào:

```text
domain/proxy/services.py
```

Không cần quyết định cứng ngay hôm nay.

Đây chính là tư duy DDD:

> Package boundary nên phản ánh business responsibility, không phải chỉ phản ánh loại class.

---

# 22. Kiến trúc chúng ta đang hướng tới

```text
                         Application
                              │
                              ▼
                          Fetcher
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
       ProxyProvider    UAProvider       HttpClient
             │                │                │
             ▼                ▼                ▼
        ProxyPool          UAPool          HttpxClient
             │                                 │
             ▼                                 ▼
          Proxy                              httpx
```

Và health check sẽ chen vào:

```text
Fetcher
   │
   ▼
ProxyProvider
   │
   ▼
Proxy
   │
   ▼
ProxyHealthChecker
   │
   ▼
HttpxProxyHealthChecker
   │
   ▼
httpx
```

---

# 23. Điều quan trọng nhất của Buổi 4

Ta đã tách được:

```text
Proxy selection
       ≠
User-Agent selection
       ≠
HTTP transport
```

Ba trách nhiệm độc lập:

```text
ProxyProvider
UserAgentProvider
HttpClient
```

Đây là nền móng để sau này Fetcher không biến thành một "God Class".

---

## Bài tập

Hãy tự viết 3 thành phần:

```text
1. UserAgentProvider
2. UserAgentPool
3. FetchContext
```

và test:

```text
UA-1 → UA-2 → UA-3 → UA-1
```

sau đó:

```text
Proxy A + UA-1
Proxy B + UA-2
Proxy C + UA-3
```

---

### Buổi 5

Ta sẽ bắt đầu **`HttpClient` abstraction + `HttpxClient`**, tức là lần đầu tiên đưa `httpx sync` vào kiến trúc.

Ta sẽ xử lý:

```text
HttpClient
    ↑
HttpxClient
    │
    ├── timeout
    ├── headers
    ├── proxy
    ├── response
    └── exception mapping
```

Quan trọng nhất: **Domain/Application vẫn không import `httpx`**.
