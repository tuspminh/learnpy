# Buổi 39 — Fetcher Architecture

Đây là buổi **rất quan trọng** của phần Async + Crawler.

Từ Buổi 31–38, chúng ta đã xây từng mảnh:

```text id="h7k3p1"
AsyncClient
Concurrent Requests
Semaphore
Timeout
Retry
ProxyPool
BrowserProfilePool
RateLimiter
```

Nhưng hiện tại nếu nhét tất cả vào một class:

```python id="n4c8s2"
class AsyncFetcher:
    ...
```

thì rất nhanh sẽ thành **God Object**.

Hôm nay chúng ta thiết kế lại toàn bộ Fetcher theo:

* DDD
* SOLID
* Dependency Injection
* Ports & Adapters
* testable
* chuẩn bị trực tiếp cho **Buổi 40 — Async Novel Fetcher**

`primp` hiện tại là 2.0.1, hỗ trợ `Client`, `AsyncClient`, browser impersonation và các profile browser/OS; vì vậy trong architecture của chúng ta, `primp` sẽ nằm ở **Infrastructure**, không lan vào Domain/Application. ([PyPI][1])

---

# 1. Vấn đề của Fetcher hiện tại

Nếu viết nhanh:

```python
class AsyncFetcher:

    def __init__(
        self,
        client,
        proxy_pool,
        profile_pool,
        retry_policy,
        rate_limiter,
        semaphore,
    ):
        ...
```

rồi:

```python
async def get(self, url):
    ...
```

thì `get()` cuối cùng có thể thành:

```text id="w2p8k1"
get()
 │
 ├── chọn proxy
 ├── chọn browser profile
 ├── rate limit
 ├── semaphore
 ├── timeout
 ├── request
 ├── classify error
 ├── retry
 ├── proxy failure
 ├── logging
 ├── metrics
 └── response conversion
```

Đây là dấu hiệu architecture bắt đầu xấu.

---

# 2. Mục tiêu của Buổi 39

Ta muốn:

```text id="a8j5q2"
Application
     ↓
Fetcher Interface
     ↓
AsyncFetcher
     ↓
Infrastructure components
     │
     ├── PrimpClient
     ├── ProxyPool
     ├── BrowserProfilePool
     ├── RateLimiter
     ├── RetryPolicy
     └── Semaphore
```

Quan trọng:

```text id="k9m4x1"
Domain
    ✗ không biết primp
    ✗ không biết asyncio
    ✗ không biết proxy
    ✗ không biết HTTP
```

---

# 3. Layering

Architecture chúng ta sẽ dùng:

```text id="q3f8z7"
┌────────────────────────────────────┐
│           Application              │
│                                    │
│       AsyncNovelFetcher            │
│              │                     │
│              ↓                     │
│          Fetcher Port              │
└──────────────┬─────────────────────┘
               │
               ↓
┌────────────────────────────────────┐
│          Infrastructure            │
│                                    │
│   PrimpFetcher                     │
│      │                             │
│      ├── ProxyPool                 │
│      ├── BrowserProfilePool        │
│      ├── RateLimiter               │
│      ├── Semaphore                 │
│      └── RetryPolicy               │
│                                    │
│          ↓                         │
│      primp.AsyncClient             │
└────────────────────────────────────┘
```

---

# 4. Fetcher Interface

Đầu tiên phải định nghĩa:

> Application cần Fetcher làm gì?

Không cần biết `primp` là gì.

Ví dụ:

```python id="q4d7s9"
from typing import Protocol


class Fetcher(Protocol):

    async def get(
        self,
        url: str,
    ):
        ...
```

Application chỉ cần:

```python id="m2k7v5"
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher

    async def execute(
        self,
        url: str,
    ):
        response = await self.fetcher.get(url)

        return response
```

`CrawlChapter` không biết:

```text id="f6a1c8"
primp
proxy
TLS
HTTP/2
rate limit
retry
```

---

# 5. Đây là Dependency Inversion

Thay vì:

```text id="g8z4q2"
CrawlChapter
     ↓
primp.AsyncClient
```

ta có:

```text id="x1c9m5"
CrawlChapter
     ↓
Fetcher Protocol
     ↑
PrimpFetcher
```

Application phụ thuộc vào abstraction.

Infrastructure implement abstraction.

Đây chính là **Dependency Inversion Principle**.

---

# 6. Response cũng nên có abstraction

Nếu Application nhận trực tiếp:

```python id="p6d2k8"
primp.Response
```

thì `primp` đã lọt vào Application.

Không tốt.

Ta tạo:

```python id="z9v3r1"
from dataclasses import dataclass


@dataclass(frozen=True)
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

Bây giờ:

```text id="v5n8q3"
primp.Response
      ↓
adapter
      ↓
FetchResponse
      ↓
Application
```

---

# 7. Tại sao không dùng `response.text` luôn?

Vì Application không nên biết response đến từ:

```text id="j2r7c4"
primp
httpx
aiohttp
requests
```

Ta có thể thay:

```text id="b5x1v8"
PrimpFetcher
```

bằng:

```text id="n7k3q6"
HttpxFetcher
```

mà Application không đổi.

Đây chính là lợi ích của Adapter.

---

# 8. Primp Response Adapter

```python id="e4s9p2"
def to_fetch_response(
    response,
) -> FetchResponse:

    return FetchResponse(
        status_code=response.status_code,
        url=response.url,
        headers=dict(response.headers),
        content=response.content,
    )
```

Infrastructure chịu trách nhiệm chuyển đổi.

---

# 9. Request Model

Đến đây ta cũng không nên để Application truyền quá nhiều primitive:

```python id="x8m2q4"
fetcher.get(
    url,
    headers=...,
    params=...,
    timeout=...,
)
```

Ta đã học `RequestOptions` trước đó.

Có thể nâng cấp thành:

```python id="u5r7n1"
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None
```

---

# 10. Fetcher Port

Bây giờ:

```python id="c3v8p6"
from typing import Protocol


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Application:

```python id="n9k4t2"
response = await self.fetcher.get(
    FetchRequest(url=url)
)
```

---

# 11. Nhưng có cần Request Model không?

Có hai mức abstraction:

### Đơn giản

```python id="g7m2c8"
await fetcher.get(url)
```

### Linh hoạt

```python id="z4p8n1"
await fetcher.get(
    FetchRequest(
        url=url,
        headers=...,
        params=...,
        timeout=...,
    )
)
```

Đối với **Novel Crawler production architecture**, tôi chọn `FetchRequest`.

Vì sau này request có thể cần:

```text id="k2d7v5"
method
headers
params
body
timeout
referer
```

nhưng không muốn API Fetcher phình thành:

```python
get(
    url,
    headers,
    params,
    timeout,
    proxy,
    retry,
    profile,
    rate_limit,
    ...
)
```

---

# 12. FetchRequest không chứa Infrastructure

Không làm:

```python id="b6m1x9"
@dataclass
class FetchRequest:

    url: str
    proxy: ProxyConfig
    browser_profile: BrowserProfile
    retry_policy: RetryPolicy
```

Vì:

```text id="r3k8v2"
FetchRequest
```

sẽ bị phụ thuộc infrastructure.

Request chỉ mô tả:

> Application muốn request HTTP gì?

Infrastructure quyết định:

> Request đó được gửi bằng proxy/client/profile nào.

---

# 13. Thiết kế lại

Bây giờ:

```text id="w8q4m1"
FetchRequest
     ↓
Fetcher
     ↓
FetchResponse
```

Đây là **Port**.

Còn:

```text id="p7n2c5"
PrimpFetcher
```

là **Adapter**.

---

# 14. PrimpTransport

Ta tách tiếp một lớp:

```python id="k3v9s6"
class PrimpTransport:

    def __init__(self, client):
        self.client = client

    async def send(
        self,
        request: FetchRequest,
    ):
        return await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )
```

Đây là lớp rất gần `primp`.

---

# 15. Vì sao tách Transport?

Ta có:

```text id="e2m7p4"
PrimpFetcher
      ↓
PrimpTransport
      ↓
primp.AsyncClient
```

`PrimpFetcher` xử lý:

```text id="q8v1n3"
retry
rate limit
proxy
profile
concurrency
```

`PrimpTransport` chỉ xử lý:

```text id="z5c9m2"
"gửi HTTP request bằng primp"
```

Đây là Separation of Concerns.

---

# 16. Transport Interface

Ta còn có thể định nghĩa:

```python id="s7p3k1"
class AsyncTransport(Protocol):

    async def send(
        self,
        request: FetchRequest,
    ):
        ...
```

Sau đó:

```text id="d1n6q8"
AsyncTransport
      ↑
      │
 ┌────┴──────────┐
 │               │
PrimpTransport  FakeTransport
```

Production:

```text id="x9c2m5"
PrimpTransport
```

Test:

```text id="v4k7n1"
FakeTransport
```

---

# 17. FakeTransport

Đây là thứ cực kỳ hữu ích.

```python id="b8m3q6"
class FakeTransport:

    def __init__(
        self,
        responses: list[FetchResponse],
    ):
        self.responses = responses
        self.calls = []

    async def send(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        self.calls.append(request)

        if not self.responses:
            raise RuntimeError(
                "No fake response left"
            )

        return self.responses.pop(0)
```

Không cần Internet.

---

# 18. Retry không nên nằm trong Transport

Đây là một quyết định architecture quan trọng.

Không làm:

```text id="f3m8q2"
PrimpTransport
    ├── HTTP
    ├── Retry
    ├── Proxy
    ├── RateLimit
    └── Semaphore
```

Transport chỉ nên:

```text id="r7n2k5"
Request
   ↓
HTTP
   ↓
Response / Exception
```

Retry là policy bên ngoài.

---

# 19. Retry Policy

Ta đã có:

```python id="q6m1v8"
@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    retryable_statuses: frozenset[int] = (
        frozenset({
            429,
            500,
            502,
            503,
            504,
        })
    )
```

Nhưng hôm nay ta nên tách:

```text id="h8c3p5"
RetryPolicy
```

và:

```text id="j4n7m2"
RetryExecutor
```

---

# 20. RetryPolicy là quyết định

`RetryPolicy` trả lời:

> Có nên retry không?

Ví dụ:

```python id="p2v6k9"
class RetryPolicy:

    def should_retry(
        self,
        *,
        attempt: int,
        status_code: int | None = None,
        exception: Exception | None = None,
    ) -> bool:

        if attempt >= self.max_attempts:
            return False

        if status_code in self.retryable_statuses:
            return True

        if exception is not None:
            return True

        return False
```

Đây là **policy**.

---

# 21. RetryExecutor là thực thi

Nó làm:

```text id="q8c4m1"
attempt
 ↓
send
 ↓
policy
 ↓
retry?
 ↓
backoff
```

Ví dụ:

```python id="s5n9k2"
class RetryExecutor:

    def __init__(
        self,
        policy: RetryPolicy,
    ):
        self.policy = policy

    async def execute(
        self,
        operation,
    ):
        ...
```

`operation` là một async callable.

---

# 22. Tại sao truyền `operation`?

Vì RetryExecutor không cần biết:

```text id="v2m7q9"
primp
proxy
URL
chapter
novel
```

Nó chỉ biết:

```text id="c5k1p8"
"Thực hiện operation này."
```

Ví dụ:

```python id="j3r8n6"
async def operation():
    return await transport.send(request)
```

Sau đó:

```python id="e7q2m4"
response = await retry_executor.execute(
    operation
)
```

Đây là một abstraction rất sạch.

---

# 23. RateLimiter cũng là một dependency

```text id="w1k6p3"
RateLimiter
    ↓
acquire()
```

Fetcher orchestration:

```text id="m8c4r2"
attempt
 ↓
rate limiter
 ↓
semaphore
 ↓
transport
```

---

# 24. Semaphore cũng vậy

Không cần class:

```python id="g9p2v6"
ConcurrencyManager
```

Chỉ cần:

```python id="z4m7c1"
asyncio.Semaphore
```

vì `Semaphore` đã là một abstraction tốt.

---

# 25. Browser Profile và Proxy

Fetcher cần một **execution context**.

Ví dụ:

```text id="j5n8q2"
Request
   ↓
Execution Context
   ├── Proxy
   ├── Browser Profile
   └── Client
```

Nhưng chúng ta không cần biến context thành một class khổng lồ ngay.

Có thể để:

```text id="c3r7m9"
BrowserClient
```

đã gắn:

```text id="u6k2p5"
BrowserProfile
+
AsyncClient
```

và ProxyPool chọn client/resource tương ứng.

---

# 26. Một architecture tốt hơn

Thay vì:

```text id="y8n3q1"
Fetcher
 ├── profile pool
 ├── proxy pool
 └── primp client
```

ta có:

```text id="r5m9c2"
Fetcher
   ↓
ClientPool
   ↓
BrowserClient
   ├── BrowserProfile
   ├── Proxy
   └── primp.AsyncClient
```

Tuy nhiên, ở Buổi 39 chúng ta **chưa cần ép ProxyPool và BrowserProfilePool thành một ClientPool**.

Ta chỉ cần thiết kế boundary để sau này thay đổi được.

---

# 27. Fetcher Architecture mục tiêu

```text id="w7k2p4"
                    Fetcher
                       │
                       ↓
                FetchRequest
                       │
                       ↓
              ┌────────────────┐
              │ RetryExecutor  │
              └───────┬────────┘
                      ↓
                RateLimiter
                      ↓
                 Semaphore
                      ↓
                Transport
                      ↓
              PrimpTransport
                      ↓
             primp.AsyncClient
                      ↓
                   HTTP
                      ↓
              FetchResponse
```

Proxy/Profile nằm trong client/transport infrastructure.

---

# 28. Implement `PrimpTransport`

Bây giờ viết code thật.

```python id="q1v6m8"
import primp


class PrimpTransport:

    def __init__(
        self,
        client: primp.AsyncClient,
    ):
        self.client = client

    async def send(
        self,
        request: FetchRequest,
    ):

        return await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )
```

Lưu ý: API hiện tại của `primp` 2.0.1 xác nhận `AsyncClient` và `client.get(...)` theo async quick-start chính thức. ([PyPI][1])

---

# 29. Response Adapter

```python id="a9k3r7"
def adapt_response(
    response,
) -> FetchResponse:

    return FetchResponse(
        status_code=response.status_code,
        url=response.url,
        headers=dict(response.headers),
        content=response.content,
    )
```

---

# 30. Fetcher

Bây giờ:

```python id="m4c8q1"
class PrimpFetcher:

    def __init__(
        self,
        transport: AsyncTransport,
        rate_limiter: RateLimiter,
        semaphore: asyncio.Semaphore,
        retry_executor: RetryExecutor,
    ):
        self.transport = transport
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore
        self.retry_executor = retry_executor
```

Điểm hay:

`PrimpFetcher` **không cần import `primp`**.

---

# 31. `get()`

```python id="v7n2c5"
class PrimpFetcher:

    def __init__(
        self,
        transport: AsyncTransport,
        rate_limiter: RateLimiter,
        semaphore: asyncio.Semaphore,
        retry_executor: RetryExecutor,
    ):
        self.transport = transport
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore
        self.retry_executor = retry_executor

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        async def operation():

            await self.rate_limiter.acquire()

            async with self.semaphore:

                response = await self.transport.send(
                    request
                )

                return adapt_response(
                    response
                )

        return await self.retry_executor.execute(
            operation
        )
```

Đây là bước tiến rất lớn.

Fetcher chỉ **orchestrate**.

---

# 32. Ai chịu trách nhiệm gì?

```text id="u6c9r3"
PrimpFetcher
    =
orchestration

RetryExecutor
    =
retry execution

RetryPolicy
    =
retry decision

RateLimiter
    =
request pacing

Semaphore
    =
concurrency

PrimpTransport
    =
HTTP transport

primp.AsyncClient
    =
actual HTTP implementation
```

Đây là Separation of Concerns.

---

# 33. RetryExecutor hoàn chỉnh

Ta viết phiên bản đơn giản trước:

```python id="e5m8q2"
import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 10.0

    retryable_statuses: frozenset[int] = (
        frozenset({
            429,
            500,
            502,
            503,
            504,
        })
    )

    def should_retry(
        self,
        *,
        attempt: int,
        status_code: int | None = None,
        exception: Exception | None = None,
    ) -> bool:

        if attempt >= self.max_attempts:
            return False

        if exception is not None:
            return True

        if (
            status_code is not None
            and status_code in self.retryable_statuses
        ):
            return True

        return False

    def delay(
        self,
        attempt: int,
    ) -> float:

        return min(
            self.base_delay
            * (2 ** (attempt - 1)),
            self.max_delay,
        )


class RetryExecutor:

    def __init__(
        self,
        policy: RetryPolicy,
    ):
        self.policy = policy

    async def execute(
        self,
        operation,
    ):

        last_exception = None

        for attempt in range(
            1,
            self.policy.max_attempts + 1,
        ):

            try:

                response = await operation()

                if not self.policy.should_retry(
                    attempt=attempt,
                    status_code=(
                        response.status_code
                    ),
                ):
                    return response

                if attempt < (
                    self.policy.max_attempts
                ):

                    await asyncio.sleep(
                        self.policy.delay(
                            attempt
                        )
                    )

            except Exception as exc:

                last_exception = exc

                if not self.policy.should_retry(
                    attempt=attempt,
                    exception=exc,
                ):
                    raise

                await asyncio.sleep(
                    self.policy.delay(
                        attempt
                    )
                )

        if last_exception is not None:
            raise last_exception

        raise RuntimeError(
            "Retry attempts exhausted"
        )
```

---

# 34. Một điểm cần sửa so với Buổi 35

Ở Buổi 35 ta từng có:

```python
except Exception:
    retry
```

Hôm nay chúng ta đưa nó vào `RetryPolicy`.

Đây là bước tiến architecture.

Nhưng về production, vẫn chưa đủ tốt:

```text id="x5m8q2"
mọi Exception
    ↓
retry
```

không nên là policy cuối cùng.

Buổi 48:

```text id="p8n3v6"
Error Classification
```

sẽ giải quyết vấn đề này.

---

# 35. FakeTransport test

Đây là lúc architecture mới phát huy tác dụng.

```python id="k7q2m4"
class FakeTransport:

    def __init__(
        self,
        responses,
    ):
        self.responses = list(responses)
        self.calls = 0

    async def send(
        self,
        request,
    ):

        self.calls += 1

        if not self.responses:
            raise RuntimeError(
                "No response"
            )

        return self.responses.pop(0)
```

Fake response:

```python id="z4m8p1"
class FakePrimpResponse:

    def __init__(
        self,
        status_code: int,
        url: str = "https://example.com",
    ):
        self.status_code = status_code
        self.url = url
        self.headers = {}
        self.content = b"hello"
```

---

# 36. Test Retry

```python id="r6n2c8"
async def main():

    transport = FakeTransport([
        FakePrimpResponse(500),
        FakePrimpResponse(500),
        FakePrimpResponse(200),
    ])

    policy = RetryPolicy(
        max_attempts=3,
        base_delay=0.01,
    )

    retry_executor = RetryExecutor(
        policy
    )

    async def operation():

        response = await transport.send(
            FetchRequest(
                url="https://example.com"
            )
        )

        return adapt_response(response)

    result = await retry_executor.execute(
        operation
    )

    print(
        "Status:",
        result.status_code,
    )

    print(
        "Calls:",
        transport.calls,
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Kỳ vọng:

```text id="c1v8m5"
Status: 200
Calls: 3
```

Không cần Internet.

---

# 37. Test Fetcher không cần primp

Đây mới là điểm quan trọng.

Ta có thể:

```python id="w2k7p4"
fake_transport = FakeTransport([
    FakePrimpResponse(200)
])
```

và:

```python id="m9c3q6"
fetcher = PrimpFetcher(
    transport=fake_transport,
    rate_limiter=...,
    semaphore=...,
    retry_executor=...,
)
```

Application test được mà không:

```text id="a7n2v5"
DNS
HTTP
proxy
TLS
Internet
```

Đây là **testability**.

---

# 38. Application không biết Infrastructure

Ví dụ Use Case:

```python id="h4m8q2"
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        self.fetcher = fetcher

    async def execute(
        self,
        url: str,
    ):

        response = await self.fetcher.get(
            FetchRequest(url=url)
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code}"
            )

        return response.text
```

Không có:

```python
import primp
```

Không có:

```python
asyncio.Semaphore
```

Không có:

```python
ProxyPool
```

---

# 39. Đây chính là Clean Architecture

```text id="u7c3m9"
                  DOMAIN
                     ↑
                     │
                APPLICATION
                     ↑
                     │
              Fetcher Protocol
                     ↑
                     │
             INFRASTRUCTURE
                     │
                     ├── PrimpFetcher
                     ├── PrimpTransport
                     ├── ProxyPool
                     ├── BrowserProfilePool
                     ├── RateLimiter
                     └── primp
```

Dependency hướng vào trong.

---

# 40. Cấu trúc project

Đến đây tôi đề xuất:

```text id="f2m8q5"
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   └── crawl_task.py
    │
    ├── application/
    │   ├── ports/
    │   │   └── fetcher.py
    │   │
    │   └── use_cases/
    │       └── crawl_chapter.py
    │
    └── infrastructure/
        │
        └── http/
            ├── request.py
            ├── response.py
            ├── fetcher.py
            ├── transport.py
            ├── retry.py
            ├── rate_limit.py
            ├── proxy.py
            ├── proxy_pool.py
            ├── browser_profile.py
            └── browser_profile_pool.py
```

---

# 41. Một vấn đề: `FetchRequest` nằm đâu?

Có hai lựa chọn.

### Infrastructure

```text id="z8m3k1"
infrastructure/http/request.py
```

### Application

```text id="p4c7n9"
application/ports/fetcher.py
```

Tôi chọn **Application**, bởi vì:

```text id="q5n8v2"
FetchRequest
FetchResponse
Fetcher
```

là contract giữa Application và Infrastructure.

Ví dụ:

```text id="x2k6m4"
application/
└── ports/
    └── fetcher.py
```

---

# 42. `fetcher.py`

Có thể chứa:

```python id="b7m1q8"
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class FetchRequest:

    url: str

    headers: dict[str, str] = field(
        default_factory=dict
    )

    params: dict[str, object] = field(
        default_factory=dict
    )

    timeout: float | None = None


@dataclass(frozen=True)
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


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Đây là **Port**.

---

# 43. Infrastructure

```text id="m8q2c6"
infrastructure/http/
    ├── primp_transport.py
    ├── primp_fetcher.py
    ├── retry.py
    ├── rate_limit.py
    ├── proxy.py
    ├── proxy_pool.py
    ├── browser_profile.py
    └── browser_profile_pool.py
```

Application không cần biết chúng tồn tại như thế nào.

---

# 44. Dependency Injection

Composition Root sẽ tạo tất cả:

```text id="c9m3v7"
Composition Root
      │
      ├── AsyncClient
      ├── Transport
      ├── RateLimiter
      ├── Semaphore
      ├── RetryPolicy
      └── Fetcher
```

Sau đó:

```text id="q4n8k2"
Fetcher
    ↓
Use Case
```

Ví dụ concept:

```python id="t7m2p5"
client = primp.AsyncClient(
    impersonate="chrome_146",
    impersonate_os="windows",
)

transport = PrimpTransport(client)

limiter = RateLimiter(
    RateLimitConfig(
        requests_per_second=2
    )
)

semaphore = asyncio.Semaphore(10)

retry_executor = RetryExecutor(
    RetryPolicy(
        max_attempts=3
    )
)

fetcher = PrimpFetcher(
    transport=transport,
    rate_limiter=limiter,
    semaphore=semaphore,
    retry_executor=retry_executor,
)
```

Đây là **Composition Root**.

---

# 45. Tại sao Composition Root quan trọng?

Nếu tự tạo dependency bên trong:

```python id="x1m6q9"
class PrimpFetcher:

    def __init__(self):

        self.client = primp.AsyncClient()

        self.rate_limiter = RateLimiter(...)

        self.retry = RetryExecutor(...)

        self.semaphore = asyncio.Semaphore(10)
```

thì:

```text id="j8p3c5"
PrimpFetcher
```

vừa:

```text id="f5m9q2"
create dependency
```

vừa:

```text id="k2n7v4"
use dependency
```

khó test và khó cấu hình.

Dependency Injection giải quyết:

```text id="w6c1m8"
create outside
     ↓
inject
     ↓
use inside
```

---

# 46. SOLID nhìn vào architecture

### S — Single Responsibility

```text id="z3n7p5"
RetryExecutor → retry
RateLimiter   → rate
Transport     → HTTP
Fetcher       → orchestration
```

---

### O — Open/Closed

Có thể thêm:

```text id="q8m2c4"
HttpxTransport
```

mà không sửa Fetcher contract.

---

### L — Liskov

```text id="u5n9k1"
PrimpFetcher
FakeFetcher
```

đều có thể được dùng qua:

```text id="a4m7c2"
Fetcher
```

---

### I — Interface Segregation

Không tạo:

```text id="e8k3p6"
MegaFetcherInterface
```

với 30 method.

Chỉ cần:

```python id="s2v7m4"
async def get(...)
```

ở giai đoạn hiện tại.

---

### D — Dependency Inversion

```text id="n6c1q8"
Application
    ↓
Fetcher Protocol
    ↑
PrimpFetcher
```

---

# 47. Điều gì chưa nên làm ở Buổi 39?

Chưa cần:

```text id="w4m8k2"
EventBus
Middleware Framework
Plugin Registry
Circuit Breaker
Metrics Collector
Tracing System
Connection Manager abstraction
```

Chúng ta đang xây crawler, không xây framework HTTP tổng quát.

---

# 48. Fetcher Architecture cuối buổi

Đây là sơ đồ quan trọng nhất:

```text id="p7c2m9"
                         USE CASE
                            │
                            ↓
                       Fetcher Port
                            │
                            ↓
                     ┌──────────────┐
                     │ PrimpFetcher │
                     └──────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
        RetryExecutor   RateLimiter   Semaphore
              │             │             │
              └─────────────┼─────────────┘
                            ↓
                    PrimpTransport
                            │
                            ↓
                    primp.AsyncClient
                            │
                    ┌───────┴────────┐
                    ↓                ↓
               BrowserProfile      Proxy
                    │                │
                    └───────┬────────┘
                            ↓
                           HTTP
                            │
                            ↓
                     FetchResponse
                            │
                            ↓
                         Parser
```

---

# 49. Và đây là architecture đặc biệt phù hợp với Novel Crawler

```text id="k8m3q1"
CrawlChapter
     │
     ↓
Fetcher
     │
     ↓
FetchResponse
     │
     ↓
ChapterParser
     │
     ↓
Chapter
     │
     ↓
Repository
     │
     ↓
SQLite
```

HTTP hoàn toàn nằm ngoài Domain.

---

# 50. Test Pyramid

Architecture này cho phép:

```text id="r3n7m5"
             E2E
              ▲
             / \
            /   \
           /     \
          / Integration
         /           \
        /_____________\
        Unit Tests
```

Ví dụ Unit:

```text id="z5c8p2"
RetryPolicy
RateLimiter
ProxyPool
BrowserProfilePool
```

Integration:

```text id="m1q7v4"
PrimpTransport
```

E2E:

```text id="a8n3k6"
NovelFetcher
    ↓
real HTTP
    ↓
real parser
```

Đây chính là lý do chúng ta không nhét tất cả vào một class.

---

# 51. Bài tập thực hành

## Bài 1 — Fetcher Protocol

Tạo:

```python id="g5m8q2"
Fetcher
FetchRequest
FetchResponse
```

và một:

```python id="p7c1n4"
FakeFetcher
```

---

## Bài 2 — FakeTransport

Test:

```text id="r8m3k6"
500
500
200
```

và đảm bảo:

```text id="w2q7p1"
3 attempts
→ 200
```

---

## Bài 3 — RateLimiter

Test:

```text id="m4n8c2"
5 req/s
```

với 20 tasks.

---

## Bài 4 — Full Fetcher

Ghép:

```text id="j6p2v9"
Fetcher
 ├── RetryExecutor
 ├── RateLimiter
 ├── Semaphore
 └── Transport
```

nhưng **không dùng Internet**.

Dùng `FakeTransport`.

---

# 52. Bài tập chính

Hãy tạo project nhỏ:

```text id="v9c3m7"
lesson39/
│
├── application/
│   └── fetcher.py
│
├── infrastructure/
│   └── http/
│       ├── transport.py
│       ├── retry.py
│       ├── rate_limit.py
│       └── fetcher.py
│
└── tests/
    └── test_fetcher.py
```

Test các case:

```text id="f6k2p8"
1. 200 ngay lần đầu
2. 500 → 200
3. 500 → 500 → 200
4. 500 → 500 → 500
5. Rate limiting
6. Semaphore
7. FakeTransport
8. FetchResponse
```

---

# 53. Tổng kết Buổi 39

Trước Buổi 39:

```text id="e7m2q5"
Fetcher
=
một class gọi HTTP
+
rất nhiều logic
```

Sau Buổi 39:

```text id="u4n8c1"
Fetcher
=
orchestrator
```

với các component:

```text id="s9p3k6"
Fetcher
 │
 ├── FetchRequest
 ├── FetchResponse
 ├── RetryExecutor
 ├── RateLimiter
 ├── Semaphore
 └── Transport
        ↓
   PrimpTransport
        ↓
   primp.AsyncClient
```

Đây là bước chuyển từ:

```text id="j2m7q4"
"biết dùng primp"
```

sang:

```text id="q8c1n5"
"biết thiết kế HTTP infrastructure cho một crawler"
```

`primp` chỉ là **implementation detail** ở Infrastructure; API chính thức hiện vẫn cung cấp `AsyncClient` và browser impersonation profiles, nên adapter này là ranh giới phù hợp để giữ Application độc lập với thư viện. ([PyPI][1])

### Roadmap

```text id="x5n9k2"
31. AsyncClient              ✅
32. async GET                ✅
33. Concurrent Requests      ✅
34. Semaphore                ✅
35. Timeout + Retry          ✅
36. Proxy Pool               ✅
37. Browser Profile Pool     ✅
38. Rate Limiting            ✅
39. Fetcher Architecture     ✅
40. Async Novel Fetcher      ← tiếp theo
```

**Buổi 40** sẽ là bài tổng hợp thực chiến: chúng ta lấy toàn bộ architecture này và xây `AsyncNovelFetcher` hoàn chỉnh cho Novel Crawler — từ `URL → FetchRequest → RateLimiter → Semaphore → Retry → Proxy/Profile → primp.AsyncClient → FetchResponse → Parser`, có cấu trúc project và testable bằng Fake Transport.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
