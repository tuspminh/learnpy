# Buổi 9 — User-Agent Rotation

Ở Buổi 8, chúng ta đã hoàn thành **Proxy Rotation**.

Bây giờ thêm **User-Agent Rotation** để mỗi request có thể sử dụng User-Agent khác nhau.

Mục tiêu:

```text
Request 1 → Proxy A + UA 1
Request 2 → Proxy B + UA 2
Request 3 → Proxy C + UA 3
Request 4 → Proxy A + UA 4
Request 5 → Proxy B + UA 1
```

Nhưng có một nguyên tắc rất quan trọng:

> **Proxy rotation và User-Agent rotation là hai cơ chế độc lập.**

---

# 1. Kiến trúc hiện tại

Ta đang có:

```text
                         Fetcher
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       ProxyProvider   UAProvider    HealthChecker
             │              │              │
             ▼              ▼              ▼
         ProxyPool        UAPool      HealthResult
             │              │
             └───────┬──────┘
                     ▼
                FetchContext
                     │
                     ▼
                 HttpClient
                     │
                     ▼
                  HttpxClient
```

`Fetcher` lấy:

```python
proxy = proxy_provider.get_proxy()
```

và:

```python
user_agent = user_agent_provider.get_user_agent()
```

sau đó tạo:

```python
FetchContext(
    proxy=proxy,
    user_agent=user_agent,
)
```

---

# 2. Tại sao không gắn UA vào Proxy?

Không nên thiết kế:

```python
class Proxy:
    url: ProxyUrl
    user_agent: str
```

vì quan hệ thực tế không phải:

```text
Proxy A → UA 1
```

mà là:

```text
Proxy Pool
     ↓
Proxy A

UA Pool
     ↓
UA 1
```

Hai resource này độc lập.

Ví dụ:

```text
Proxy A
Proxy B
Proxy C
```

và:

```text
UA 1
UA 2
UA 3
UA 4
```

Ta có thể tạo:

```text
A + 1
B + 2
C + 3
A + 4
B + 1
C + 2
```

---

# 3. `UserAgentProvider`

Ta đã có abstraction từ Buổi 4:

```python
from abc import ABC, abstractmethod


class UserAgentProvider(ABC):
    @abstractmethod
    def get_user_agent(self) -> str:
        raise NotImplementedError
```

Implementation:

```python
class UserAgentPool(UserAgentProvider):
    def __init__(self, user_agents: list[str]):
        cleaned = [ua.strip() for ua in user_agents if ua.strip()]

        if not cleaned:
            raise ValueError("User-Agent pool cannot be empty")

        self._user_agents = cleaned
        self._index = 0

    def get_user_agent(self) -> str:
        user_agent = self._user_agents[self._index]

        self._index = (self._index + 1) % len(self._user_agents)

        return user_agent
```

---

# 4. Round-Robin

Nếu có:

```text
UA1
UA2
UA3
```

thì:

```text
get_user_agent()
       ↓
      UA1

get_user_agent()
       ↓
      UA2

get_user_agent()
       ↓
      UA3

get_user_agent()
       ↓
      UA1
```

Đây là:

```text
Round Robin
```

---

# 5. Test UserAgentPool

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

Test này rất đơn giản nhưng quan trọng.

---

# 6. User-Agent phải được chọn khi nào?

Một câu hỏi quan trọng:

```text
Health Check
       ↓
User-Agent
       ↓
Actual Request
```

Hay:

```text
User-Agent
       ↓
Health Check
       ↓
Actual Request
```

Với thiết kế hiện tại, ta nên:

```text
Proxy
  ↓
Health Check
  ↓
ALIVE
  ↓
User-Agent
  ↓
Actual Request
```

Lý do:

**Health check nhằm kiểm tra proxy**, không phải mô phỏng hoàn chỉnh request tới target.

Do đó không cần lấy UA trước health check.

---

# 7. `FetchContext`

Đây là object rất quan trọng.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchContext:
    proxy: Proxy
    user_agent: str
```

Sau khi proxy đã khỏe:

```python
proxy = self._get_healthy_proxy()

user_agent = self._user_agent_provider.get_user_agent()

context = FetchContext(
    proxy=proxy,
    user_agent=user_agent,
)
```

Từ đây request được xác định bởi:

```text
FetchContext
├── Proxy
└── User-Agent
```

---

# 8. `FetchContext` nên immutable

Ta dùng:

```python
@dataclass(frozen=True)
class FetchContext:
```

Không dùng:

```python
@dataclass
class FetchContext:
```

Tại sao?

Một khi request đã được tạo:

```text
Request
    │
    ▼
Proxy A
UA 1
```

thì context không nên bị thay đổi giữa chừng thành:

```text
Proxy B
UA 2
```

Nếu cần proxy mới:

> tạo một context mới.

---

# 9. Fetcher hoàn chỉnh

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

    def fetch(
        self,
        request: FetchRequest,
    ) -> FetchResult:

        proxy = self._get_healthy_proxy()

        user_agent = self._user_agent_provider.get_user_agent()

        context = FetchContext(
            proxy=proxy,
            user_agent=user_agent,
        )

        response = self._http_client.get(
            request.url,
            headers={
                "User-Agent": context.user_agent,
            },
            proxy=context.proxy.url.value,
        )

        return FetchResult(
            url=response.url,
            status_code=response.status_code,
            headers=response.headers,
            content=response.content,
        )
```

---

# 10. `_get_healthy_proxy()`

Phần này giữ nguyên logic Buổi 8:

```python
def _get_healthy_proxy(self) -> Proxy:

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

Như vậy:

```text
_get_healthy_proxy()
```

chỉ lo:

> Proxy.

Còn:

```text
get_user_agent()
```

chỉ lo:

> User-Agent.

---

# 11. Proxy và UA rotation độc lập

Giả sử:

```text
ProxyPool:

A
B
C
```

và:

```text
UAPool:

UA1
UA2
UA3
UA4
```

Ta có sequence:

```text
Request 1:
A + UA1

Request 2:
B + UA2

Request 3:
C + UA3

Request 4:
A + UA4

Request 5:
B + UA1

Request 6:
C + UA2
```

Đây là điều chúng ta muốn.

---

# 12. Nhưng có một trường hợp thú vị

Giả sử:

```text
A → DEAD
B → ALIVE
```

Request 1:

```text
A
 ↓
DEAD
 ↓
B
 ↓
UA1
 ↓
GET
```

Request 2:

```text
B
 ↓
ALIVE
 ↓
UA2
 ↓
GET
```

User-Agent vẫn tiếp tục rotation độc lập.

Không nên làm:

```text
Proxy A → UA1
Proxy B → UA2
```

rồi coi đó là cặp cố định.

---

# 13. Không tạo `ProxyUserAgentPair`

Không cần:

```python
@dataclass
class ProxyUserAgentPair:
    proxy: Proxy
    user_agent: str
```

rồi xây:

```text
A + UA1
B + UA2
C + UA3
```

thành pool cố định.

Tại sao?

Vì nó làm giảm tính linh hoạt:

```text
3 proxy × 20 UA
```

có thể tạo ra rất nhiều combination.

Ta chỉ cần:

```text
ProxyProvider
+
UserAgentProvider
```

là đủ.

---

# 14. Test Fetcher với UA

Fake HTTP client:

```python
class FakeHttpClient(HttpClient):
    def __init__(
        self,
        response: HttpResponse,
    ):
        self.response = response
        self.last_headers = None
        self.last_proxy = None

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ) -> HttpResponse:

        self.last_headers = headers
        self.last_proxy = proxy

        return self.response
```

Sau request:

```python
assert client.last_headers == {"User-Agent": "UA-1"}
```

---

# 15. Test UA rotation

Ta có:

```python
ua_pool = UserAgentPool(
    [
        "UA-1",
        "UA-2",
        "UA-3",
    ]
)
```

Nếu gọi Fetcher 3 lần:

```python
fetcher.fetch(...)
fetcher.fetch(...)
fetcher.fetch(...)
```

thì HTTP client phải nhận:

```text
UA-1
UA-2
UA-3
```

---

# 16. Một cải tiến quan trọng: Header không chỉ có UA

Fetcher hiện tại:

```python
headers = {
    "User-Agent": user_agent,
}
```

Trong crawler thực tế có thể có:

```text
Accept
Accept-Language
Referer
Connection
```

Nhưng **không nên nhét toàn bộ logic header vào UserAgentPool**.

Không làm:

```python
class UserAgentPool:
    def get_headers(self): ...
```

vì:

> UserAgentProvider chỉ nên cung cấp User-Agent.

---

# 17. Tạo `RequestHeaders`

Nếu hệ thống lớn hơn, ta có thể có:

```python
@dataclass(frozen=True)
class RequestHeaders:
    user_agent: str

    def to_dict(self) -> dict[str, str]:
        return {
            "User-Agent": self.user_agent,
        }
```

Sau này mở rộng:

```python
@dataclass(frozen=True)
class RequestHeaders:
    user_agent: str
    accept: str | None = None
    referer: str | None = None

    def to_dict(self) -> dict[str, str]:

        headers = {
            "User-Agent": self.user_agent,
        }

        if self.accept:
            headers["Accept"] = self.accept

        if self.referer:
            headers["Referer"] = self.referer

        return headers
```

Nhưng **chưa cần triển khai ở Buổi 9**.

---

# 18. Một nguyên tắc bảo mật / tính đúng đắn

Không nên coi User-Agent rotation là cách "đánh lừa" hệ thống chống abuse.

Trong crawler hợp lệ, mục đích của rotation có thể là:

```text
phân phối request
test nhiều client profile
mô phỏng browser/client hợp lệ
tránh hard-code một header
```

Nhưng crawler vẫn phải:

```text
respect robots.txt khi phù hợp
respect rate limits
respect website terms
không gây quá tải
```

Sau này khi học **Rate Limiting** và **Fetch Policy**, các quy tắc này sẽ được đưa vào kiến trúc.

---

# 19. Test toàn bộ Proxy + UA

Ta muốn test:

```text
Request 1
Proxy A + UA1

Request 2
Proxy B + UA2

Request 3
Proxy C + UA3
```

Fake client lưu history:

```python
class FakeHttpClient(HttpClient):
    def __init__(
        self,
        response: HttpResponse,
    ):
        self.response = response
        self.requests = []

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ) -> HttpResponse:

        self.requests.append(
            {
                "url": url,
                "headers": headers,
                "proxy": proxy,
            }
        )

        return self.response
```

Sau đó:

```python
fetcher.fetch(FetchRequest("https://example.com/1"))

fetcher.fetch(FetchRequest("https://example.com/2"))

fetcher.fetch(FetchRequest("https://example.com/3"))
```

Ta có thể kiểm tra:

```python
assert client.requests[0]["proxy"] == ("http://proxy-a:8080")

assert client.requests[0]["headers"]["User-Agent"] == "UA-1"
```

v.v.

---

# 20. Một vấn đề sẽ xuất hiện ở Buổi 10

Hiện tại nếu:

```text
Proxy A
 ↓
ALIVE
 ↓
GET
 ↓
Timeout
```

Fetcher chưa biết phải làm gì.

Có thể:

```text
Retry A
```

hoặc:

```text
Retry B
```

hoặc:

```text
mark A DEAD
↓
B
```

Đây chính là **Retry**.

Nhưng trước khi làm Retry, cần phân biệt:

```text
Health Check failure
```

và:

```text
Fetch failure
```

Ví dụ:

```text
Health Check:
Proxy A → timeout
```

→ khả năng proxy chết.

Trong khi:

```text
Health Check:
Proxy A → 200

Actual fetch:
Proxy A → 403
```

→ proxy vẫn hoạt động.

Không được đánh đồng hai loại lỗi.

---

# 21. Kiến trúc sau Buổi 9

```text
                         Fetcher
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
      ProxyProvider   UserAgentProvider   HealthChecker
            │               │                │
            ▼               ▼                ▼
        ProxyPool         UAPool         HealthResult
            │               │
            └───────┬───────┘
                    ▼
              FetchContext
             ┌─────────────┐
             │ Proxy       │
             │ User-Agent  │
             └──────┬──────┘
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

# 22. SOLID của Buổi 9

### SRP

```text
ProxyPool
→ Proxy rotation

UserAgentPool
→ UA rotation

HealthChecker
→ Proxy health

HttpClient
→ HTTP transport

Fetcher
→ Orchestration
```

Mỗi component có một lý do để thay đổi.

---

### OCP

Sau này có thể thay:

```text
RoundRobinUserAgentPool
```

bằng:

```text
RandomUserAgentPool
```

mà Fetcher không đổi.

---

### DIP

Fetcher chỉ biết:

```python
UserAgentProvider
```

không biết:

```python
UserAgentPool
```

---

# 23. Code skeleton cuối Buổi 9

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

    def fetch(
        self,
        request: FetchRequest,
    ) -> FetchResult:

        proxy = self._get_healthy_proxy()

        user_agent = self._user_agent_provider.get_user_agent()

        context = FetchContext(
            proxy=proxy,
            user_agent=user_agent,
        )

        response = self._http_client.get(
            request.url,
            headers={
                "User-Agent": context.user_agent,
            },
            proxy=context.proxy.url.value,
        )

        return FetchResult(
            url=response.url,
            status_code=response.status_code,
            headers=response.headers,
            content=response.content,
        )
```

Fetcher hiện tại đã có:

```text
✅ Proxy selection
✅ Proxy health check
✅ Proxy rotation
✅ User-Agent selection
✅ User-Agent rotation
✅ Request Context
✅ HTTP abstraction
✅ Dependency Injection
✅ Testable bằng Fake
```

---

# Roadmap

```text
01 Architecture                 ✅
02 Proxy Domain Model            ✅
03 ProxyPool                     ✅
04 User-Agent Pool               ✅
05 HttpClient + httpx             ✅
06 Proxy Health Checker           ✅
07 Fetcher cơ bản                 ✅
08 Proxy Rotation                 ✅
09 User-Agent Rotation            ✅
10 Retry                          ⬅️ tiếp theo
11 Error Handling
12 Fetch Policy
13 Domain Service
14 Application Service
15 Dependency Injection
...
```

## Buổi 10 — Retry

Ta sẽ không đơn giản làm:

```python
for _ in range(3):
    try:
        fetch()
    except:
        retry()
```

mà sẽ thiết kế **Retry Policy** phân biệt:

```text
Timeout              → retry
Connection error     → retry
429                  → retry sau delay
500                  → có thể retry
502/503/504          → có thể retry
403                  → không retry mù quáng
404                  → không retry
```

và quan trọng nhất:

```text
Retry
  +
Proxy Rotation
```

sẽ được thiết kế thành hai trách nhiệm riêng, thay vì biến `Fetcher` thành một vòng lặp khổng lồ.
