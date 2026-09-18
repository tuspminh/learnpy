# Buổi 46 — Proxy Strategy

Hôm nay chúng ta đưa **Proxy Pool** đã học ở Buổi 36 vào kiến trúc `PrimpFetcher`.

Mục tiêu không phải chỉ là:

```text
Proxy A
Proxy B
Proxy C
```

mà là thiết kế:

```text
FetchRequest
     ↓
PrimpFetcher
     ↓
ProxyStrategy
     ↓
ProxyPool
     ↓
Proxy
     ↓
PrimpTransport
     ↓
primp.AsyncClient
```

và khi proxy lỗi:

```text
Proxy A
   ↓
request
   ↓
failure
   ↓
mark A failed
   ↓
Proxy B
   ↓
retry
```

---

# 1. Vấn đề của việc hard-code proxy

Không nên viết:

```python
class PrimpFetcher:

    async def get(self, request):

        proxy = random.choice(
            self.proxies
        )

        ...
```

Vì `PrimpFetcher` lúc này phải biết:

* proxy list
* random
* health
* failure count
* cooldown
* proxy rotation

Nó sẽ ngày càng phình to.

Ta tách:

```text
PrimpFetcher
     │
     ▼
ProxyStrategy
     │
     ▼
ProxyPool
```

---

# 2. Proxy Strategy là gì?

`ProxyPool` trả lời:

> Có những proxy nào?

`ProxyStrategy` trả lời:

> Request tiếp theo nên dùng proxy nào?

Đây là hai khái niệm khác nhau.

Ví dụ:

```text
ProxyPool

A
B
C
D
```

Strategy có thể chọn:

```text
RoundRobin
A → B → C → D → A
```

hoặc:

```text
Random
C → A → D → B → C
```

hoặc:

```text
HealthAware
A → B → D
```

---

# 3. Domain model cho Proxy

Tạo:

```text
infrastructure/http/proxy.py
```

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:
    url: str
```

Ví dụ:

```python
proxy = ProxyConfig(
    url="http://127.0.0.1:8080"
)
```

Không nên để:

```python
password
username
```

riêng rẽ trong mọi lớp nếu URL đã encapsulate credentials.

Quan trọng hơn:

> Không log nguyên proxy URL nếu URL chứa username/password.

---

# 4. ProxyPool

```python
from dataclasses import dataclass


class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self._proxies = list(proxies)
        self._index = 0

    def next(self) -> ProxyConfig:

        proxy = self._proxies[
            self._index
        ]

        self._index = (
            self._index + 1
        ) % len(self._proxies)

        return proxy
```

Đây là round-robin:

```text
A
↓
B
↓
C
↓
A
↓
B
```

---

# 5. Nhưng Async crawler có vấn đề

Ta có:

```text
Worker 1 → proxy A
Worker 2 → proxy B
Worker 3 → proxy C
Worker 4 → proxy A
```

Nếu Proxy A vừa chết:

```text
Worker 1 → A → fail
Worker 4 → A → fail
```

Vậy ProxyPool phải biết:

```text
A = unhealthy
```

Đây là lý do cần health state.

---

# 6. Proxy State

Ta tạo:

```python
from dataclasses import dataclass


@dataclass
class ProxyState:

    failures: int = 0

    successes: int = 0

    available: bool = True
```

Ví dụ:

```text
Proxy A

failures = 3
successes = 12
available = False
```

---

# 7. ProxyPool có state

```python
class ProxyPool:

    def __init__(
        self,
        proxies: list[ProxyConfig],
    ):
        if not proxies:
            raise ValueError(
                "Proxy pool cannot be empty"
            )

        self._proxies = list(proxies)

        self._states = {
            proxy.url: ProxyState()
            for proxy in proxies
        }

        self._index = 0
```

---

# 8. Chọn proxy khỏe

```python
def next(self) -> ProxyConfig:

    for _ in range(len(self._proxies)):

        proxy = self._proxies[
            self._index
        ]

        self._index = (
            self._index + 1
        ) % len(self._proxies)

        state = self._states[
            proxy.url
        ]

        if state.available:
            return proxy

    raise RuntimeError(
        "No healthy proxy available"
    )
```

---

# 9. Mark success

```python
def mark_success(
    self,
    proxy: ProxyConfig,
):
    state = self._states[
        proxy.url
    ]

    state.successes += 1
    state.failures = 0
    state.available = True
```

---

# 10. Mark failure

```python
def mark_failure(
    self,
    proxy: ProxyConfig,
):
    state = self._states[
        proxy.url
    ]

    state.failures += 1

    if state.failures >= 3:
        state.available = False
```

Bây giờ:

```text
A failure 1
A failure 2
A failure 3
     ↓
A unavailable
```

---

# 11. Nhưng `ProxyPool` chưa phải Strategy

Đây là điểm cần phân biệt.

```text
ProxyPool
    → quản lý proxy
```

Strategy:

```text
ProxyStrategy
    → quyết định cách sử dụng proxy
```

Ta tạo Protocol:

```python
from typing import Protocol


class ProxyStrategy(Protocol):

    def select(self) -> ProxyConfig:
        ...

    def mark_success(
        self,
        proxy: ProxyConfig,
    ) -> None:
        ...

    def mark_failure(
        self,
        proxy: ProxyConfig,
    ) -> None:
        ...
```

---

# 12. RoundRobinProxyStrategy

```python
class RoundRobinProxyStrategy:

    def __init__(
        self,
        pool: ProxyPool,
    ):
        self.pool = pool

    def select(self) -> ProxyConfig:
        return self.pool.next()

    def mark_success(
        self,
        proxy: ProxyConfig,
    ) -> None:

        self.pool.mark_success(
            proxy
        )

    def mark_failure(
        self,
        proxy: ProxyConfig,
    ) -> None:

        self.pool.mark_failure(
            proxy
        )
```

Hiện tại lớp này khá mỏng.

Nhưng abstraction này cho phép sau này:

```text
RoundRobinProxyStrategy
RandomProxyStrategy
HealthAwareProxyStrategy
```

---

# 13. Vấn đề lớn: `primp.AsyncClient` và proxy

Đây là điểm kiến trúc rất quan trọng.

Proxy thường thuộc **transport/client configuration**, không phải một argument tùy ý của Application.

Do đó không nên mặc định nghĩ:

```python
await client.get(
    url,
    proxy=proxy
)
```

nếu API/version cụ thể của `primp` chưa xác nhận hỗ trợ request-level proxy như vậy.

Thay vào đó, với browser/proxy persona ổn định, ta ưu tiên mô hình:

```text
Proxy
  ↓
Client
  ↓
Requests
```

tức là mỗi proxy context có một `AsyncClient` tương ứng.

---

# 14. Kiến trúc Proxy Context

Thay vì:

```text
PrimpFetcher
   ↓
AsyncClient
   ↓
random proxy
```

ta hướng tới:

```text
Proxy A
   ↓
AsyncClient A

Proxy B
   ↓
AsyncClient B

Proxy C
   ↓
AsyncClient C
```

Sau đó:

```text
ProxyStrategy
      ↓
Proxy A
      ↓
Transport A
      ↓
Client A
```

Đây cũng rất phù hợp với Browser Profile Strategy ở Buổi 47.

---

# 15. `PrimpTransport` cần mở rộng

Hiện tại:

```python
class PrimpTransport:

    def __init__(
        self,
        client,
    ):
        self.client = client
```

Ta giữ nguyên nguyên tắc:

> Một `PrimpTransport` đại diện cho một HTTP client context.

Ví dụ:

```text
PrimpTransport A
    ↓
AsyncClient A
    ↓
Proxy A
```

và:

```text
PrimpTransport B
    ↓
AsyncClient B
    ↓
Proxy B
```

---

# 16. Transport Pool

Ta tạo:

```python
class TransportPool:

    def __init__(
        self,
        transports: dict[
            str,
            PrimpTransport,
        ],
    ):
        self.transports = transports

    def get(
        self,
        proxy: ProxyConfig,
    ) -> PrimpTransport:

        return self.transports[
            proxy.url
        ]
```

Bây giờ:

```text
ProxyConfig
     ↓
TransportPool
     ↓
PrimpTransport
     ↓
AsyncClient
```

---

# 17. Nhưng có một vấn đề thiết kế

Ta đang có:

```text
ProxyPool
TransportPool
```

và:

```text
Proxy A ↔ Transport A
Proxy B ↔ Transport B
```

Không nên để `PrimpFetcher` tự quản lý mapping này.

Ta tạo:

```python
class ProxyContext:
    def __init__(
        self,
        proxy: ProxyConfig,
        transport: PrimpTransport,
    ):
        self.proxy = proxy
        self.transport = transport
```

---

# 18. ProxyContext

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyContext:

    proxy: ProxyConfig

    transport: PrimpTransport
```

Pool:

```python
class ProxyContextPool:

    def __init__(
        self,
        contexts: list[ProxyContext],
    ):
        if not contexts:
            raise ValueError(
                "No proxy contexts"
            )

        self.contexts = contexts
```

Strategy có thể chọn:

```python
context = strategy.select()
```

thay vì chỉ:

```python
proxy = strategy.select()
```

Điều này đơn giản hóa:

```text
Proxy
 +
Client
 +
Transport
```

thành một **runtime context**.

---

# 19. Strategy Protocol tốt hơn

```python
class ProxyStrategy(Protocol):

    def select(
        self,
    ) -> ProxyContext:
        ...

    def mark_success(
        self,
        context: ProxyContext,
    ) -> None:
        ...

    def mark_failure(
        self,
        context: ProxyContext,
    ) -> None:
        ...
```

---

# 20. Health-aware Strategy

Ta có thể xây:

```python
class HealthAwareProxyStrategy:

    def __init__(
        self,
        contexts: list[ProxyContext],
    ):
        self.contexts = contexts

        self.failures = {
            context.proxy.url: 0
            for context in contexts
        }

        self.index = 0
```

Chọn proxy:

```python
def select(self) -> ProxyContext:

    for _ in range(len(self.contexts)):

        context = self.contexts[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % len(self.contexts)

        if self.failures[
            context.proxy.url
        ] < 3:
            return context

    raise RuntimeError(
        "No healthy proxy"
    )
```

---

# 21. Mark failure

```python
def mark_failure(
    self,
    context: ProxyContext,
) -> None:

    key = context.proxy.url

    self.failures[key] += 1
```

Mark success:

```python
def mark_success(
    self,
    context: ProxyContext,
) -> None:

    self.failures[
        context.proxy.url
    ] = 0
```

Đây mới chỉ là phiên bản cơ bản.

Production sẽ cần:

```text
failure count
cooldown
last failure
half-open
health check
```

---

# 22. Proxy Rotation trong Retry

Bây giờ ta đến phần quan trọng nhất.

Không muốn:

```text
attempt 1
  Proxy A
  ↓
  fail

attempt 2
  Proxy A
  ↓
  fail
```

Ta muốn:

```text
attempt 1
  Proxy A
  ↓
  fail
  ↓
mark A failure

attempt 2
  Proxy B
  ↓
  success
```

Do đó proxy selection phải nằm trong **attempt**, không phải bên ngoài toàn bộ retry operation.

---

# 23. Sai

```python
context = proxy_strategy.select()

async def operation():

    return await context.transport.send(
        request
    )

await retry_executor.execute(
    operation
)
```

Kết quả:

```text
Retry
  ↓
same Proxy A
  ↓
same Proxy A
  ↓
same Proxy A
```

---

# 24. Đúng về mặt ý tưởng

Mỗi attempt:

```text
Retry attempt
      ↓
select proxy
      ↓
send
      ↓
success/failure
      ↓
mark proxy
```

Tức:

```text
attempt 1 → A → fail
attempt 2 → B → fail
attempt 3 → C → success
```

---

# 25. Vì vậy RetryExecutor và ProxyStrategy phải phối hợp

Nhưng đừng làm:

```python
RetryExecutor(
    proxy_strategy=...
)
```

vì RetryExecutor lúc này biết proxy.

Đây là vi phạm SRP.

Thay vào đó `PrimpFetcher` làm orchestration:

```text
PrimpFetcher
      │
      ├── Retry Policy
      ├── Proxy Strategy
      ├── Rate Limiter
      └── Semaphore
```

---

# 26. Một phiên bản Fetcher phù hợp

Ta có thể viết:

```python
class PrimpFetcher:

    def __init__(
        self,
        proxy_strategy,
        retry_policy,
        rate_limiter,
        semaphore,
    ):
        self.proxy_strategy = proxy_strategy
        self.retry_policy = retry_policy
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore
```

Và:

```python
async def get(
    self,
    request: FetchRequest,
) -> FetchResponse:

    for attempt in range(
        1,
        self.retry_policy.max_attempts + 1,
    ):

        context = (
            self.proxy_strategy.select()
        )

        try:

            await self.rate_limiter.acquire()

            async with self.semaphore:

                response = (
                    await context.transport.send(
                        request
                    )
                )

            if response.is_success:

                self.proxy_strategy.mark_success(
                    context
                )

                return response

            if not self.retry_policy.should_retry(
                attempt=attempt,
                status_code=response.status_code,
            ):

                return response

            self.proxy_strategy.mark_failure(
                context
            )

            delay = (
                self.retry_policy.calculate_delay(
                    attempt
                )
            )

            await asyncio.sleep(delay)

        except RetryableError:

            self.proxy_strategy.mark_failure(
                context
            )

            if attempt >= (
                self.retry_policy.max_attempts
            ):
                raise

            delay = (
                self.retry_policy.calculate_delay(
                    attempt
                )
            )

            await asyncio.sleep(delay)

    raise RuntimeError(
        "Retry attempts exhausted"
    )
```

Đây là một ví dụ để hiểu orchestration; ở Buổi 48 chúng ta sẽ tách phần error classification sạch hơn.

---

# 27. Flow lúc này

Ví dụ:

```text
Chapter 100
     │
     ▼
PrimpFetcher
     │
     ▼
attempt 1
     │
     ▼
Proxy A
     │
     ▼
HTTP
     │
     ▼
503
     │
     ├── mark A failed
     │
     ▼
backoff
     │
     ▼
attempt 2
     │
     ▼
Proxy B
     │
     ▼
HTTP
     │
     ▼
200
     │
     ├── mark B success
     │
     ▼
FetchResponse
```

Đây chính là mục tiêu của Buổi 46.

---

# 28. Proxy không nên đổi mỗi request một cách vô tội vạ

Một lỗi thiết kế khác:

```text
chapter 1 → Proxy A
chapter 2 → Proxy B
chapter 3 → Proxy C
chapter 4 → Proxy A
```

Việc này không nhất thiết tốt hơn.

Nếu browser profile là:

```text
Chrome 146 / Windows
```

nhưng proxy liên tục đổi:

```text
Vietnam
Singapore
US
Germany
```

thì network identity có thể thay đổi rất mạnh.

Vì vậy sau Buổi 47 ta sẽ kết hợp:

```text
Browser Profile
       +
Proxy
       +
Client
```

thành một **Browser Session / Fetch Context** ổn định.

---

# 29. Proxy và Browser Profile

Cuối cùng ta hướng đến:

```text
Context A

Chrome 146
Windows
Proxy A
AsyncClient A
```

```text
Context B

Firefox 151
Linux
Proxy B
AsyncClient B
```

```text
Context C

Safari 26
macOS
Proxy C
AsyncClient C
```

Và:

```text
Strategy
   ↓
Context A
   ↓
Client A
```

Thay vì random riêng từng thành phần:

```text
random browser
+
random OS
+
random proxy
```

---

# 30. DDD/SOLID

### Single Responsibility

```text
ProxyPool
    → quản lý proxy

ProxyStrategy
    → chọn proxy

PrimpTransport
    → HTTP

PrimpFetcher
    → orchestration
```

---

### Open/Closed

Có thể thêm:

```text
RoundRobinProxyStrategy
RandomProxyStrategy
HealthAwareProxyStrategy
LeastFailureProxyStrategy
```

mà không thay đổi `Fetcher` Port.

---

### Dependency Inversion

Application vẫn chỉ:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher
```

Không biết:

```text
ProxyPool
ProxyStrategy
primp
AsyncClient
```

---

# 31. Một điều cực kỳ quan trọng

Proxy rotation **không phải anti-bot bypass**.

Nó chỉ giải quyết:

```text
network routing
availability
failure isolation
load distribution
```

Không đảm bảo:

```text
❌ không bị block
❌ không bị CAPTCHA
❌ không bị WAF phát hiện
❌ không bị rate-limit
```

Crawler production vẫn phải tuân thủ giới hạn truy cập và chính sách của website.

---

# 32. Kiến trúc sau Buổi 46

```text
                    Fetcher
                       │
                       ▼
                 PrimpFetcher
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 RetryPolicy      RateLimiter     Semaphore
        │
        │
        ▼
 ProxyStrategy
        │
        ▼
 ProxyContext
        │
    ┌───┴────┐
    ▼        ▼
 Proxy     Transport
              │
              ▼
       primp.AsyncClient
```

Retry:

```text
attempt 1
    ↓
Proxy A
    ↓
failure
    ↓
mark A
    ↓
backoff
    ↓
attempt 2
    ↓
Proxy B
    ↓
success
```

---

# 33. Vị trí của Buổi 46

```text
41 Request Model
        ↓
42 Response Model
        ↓
43 Fetcher Interface
        ↓
44 PrimpFetcher
        ↓
45 Retry Policy
        ↓
46 Proxy Strategy        ← HÔM NAY
        ↓
47 Browser Profile Strategy
        ↓
48 Error Classification
        ↓
49 Observability / Logging
        ↓
50 Production Fetcher
```

## Kiến thức cần nhớ

Buổi 46 có 4 ý cốt lõi:

```text
1. ProxyPool
   = quản lý proxy

2. ProxyStrategy
   = quyết định proxy nào được chọn

3. ProxyContext
   = Proxy + HTTP Client/Transport context

4. Retry
   = mỗi attempt có thể chọn context khác
```

Kiến trúc mục tiêu:

```text
FetchRequest
    ↓
PrimpFetcher
    ↓
Retry
    ↓
ProxyStrategy
    ↓
ProxyContext
    ↓
RateLimiter
    ↓
Semaphore
    ↓
PrimpTransport
    ↓
primp.AsyncClient
    ↓
FetchResponse
```

**Buổi 47 — Browser Profile Strategy** sẽ làm nốt nửa còn lại: quản lý `chrome_146`, `firefox_151`, `safari_26`..., gắn **Browser Profile + OS + Proxy + AsyncClient** thành các context ổn định thay vì random từng request.
