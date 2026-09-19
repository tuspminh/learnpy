# Buổi 44 — `PrimpFetcher`

Hôm nay chúng ta biến toàn bộ phần đã học thành **Fetcher thực tế dùng `primp.AsyncClient`**, nhưng vẫn giữ đúng kiến trúc DDD/SOLID.

`primp` hiện tại là **2.0.1**, yêu cầu Python ≥ 3.10 và cung cấp `AsyncClient`, browser impersonation như `chrome_146`, `chrome_153`, Firefox, Safari, Edge... ([PyPI][1])

---

# 1. Mục tiêu Buổi 44

Sau bài này ta có:

```text
Application
     │
     ▼
 Fetcher Protocol
     │
     ▼
 PrimpFetcher
     │
     ├── RetryExecutor
     │
     ├── RateLimiter
     │
     ├── Semaphore
     │
     ▼
 PrimpTransport
     │
     ▼
 primp.AsyncClient
```

Và quan trọng:

> `PrimpFetcher` không biết chi tiết HTTP của `primp`.

Nó chỉ biết:

```python
FetchRequest
      ↓
FetchResponse
```

---

# 2. Cấu trúc project

Ta hoàn thiện cấu trúc:

```text
src/
└── crawler/
    │
    ├── application/
    │   ├── models/
    │   │   ├── request.py
    │   │   └── response.py
    │   │
    │   ├── ports/
    │   │   └── fetcher.py
    │   │
    │   └── use_cases/
    │       └── crawl_chapter.py
    │
    └── infrastructure/
        └── http/
            ├── primp_transport.py
            ├── primp_fetcher.py
            ├── retry.py
            └── rate_limit.py
```

---

# 3. `FetchRequest`

`application/models/request.py`

```python
from dataclasses import dataclass, field
from urllib.parse import urlparse


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

    def __post_init__(self):
        if not self.url:
            raise ValueError(
                "URL cannot be empty"
            )

        parsed = urlparse(self.url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError(
                "URL must use http or https"
            )

        if self.timeout is not None:
            if self.timeout <= 0:
                raise ValueError(
                    "timeout must be > 0"
                )
```

---

# 4. `FetchResponse`

`application/models/response.py`

```python
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

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600
```

---

# 5. Fetcher Port

`application/ports/fetcher.py`

```python
from typing import Protocol

from crawler.application.models.request import FetchRequest
from crawler.application.models.response import FetchResponse


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Đây chính là **Port**.

Application không cần biết:

```text
primp
httpx
aiohttp
requests
curl_cffi
```

---

# 6. PrimpTransport

Đây là lớp tiếp xúc trực tiếp với `primp`.

`infrastructure/http/primp_transport.py`

```python
import primp

from crawler.application.models.request import FetchRequest
from crawler.application.models.response import FetchResponse


class PrimpTransport:

    def __init__(
        self,
        client: primp.AsyncClient,
    ):
        self.client = client

    async def send(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        response = await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )

        return FetchResponse(
            status_code=response.status_code,
            url=response.url,
            headers=dict(response.headers),
            content=response.content,
        )
```

Theo API hiện tại của `primp`, `AsyncClient` được dùng với:

```python
async with primp.AsyncClient(...) as client:
    response = await client.get(...)
```

([PyPI][1])

---

# 7. Tại sao cần `PrimpTransport`?

Có thể bạn sẽ hỏi:

> Tại sao không cho `PrimpFetcher` gọi thẳng `primp.AsyncClient`?

Ví dụ **không nên**:

```python
class PrimpFetcher:

    def __init__(self):
        self.client = primp.AsyncClient(
            impersonate="chrome_146"
        )

    async def get(self, request):
        return await self.client.get(
            request.url
        )
```

Lúc này `PrimpFetcher` biết quá nhiều:

```text
PrimpFetcher
 ├── primp
 ├── AsyncClient
 ├── timeout
 ├── headers
 ├── response
 ├── retry
 ├── semaphore
 ├── rate limit
 └── ...
```

Dễ biến thành **God Object**.

Kiến trúc của chúng ta:

```text
PrimpFetcher
     │
     ▼
PrimpTransport
     │
     ▼
primp.AsyncClient
```

Mỗi lớp một trách nhiệm.

---

# 8. RetryPolicy

`infrastructure/http/retry.py`

```python
from dataclasses import dataclass
import asyncio


@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 10.0

    retryable_statuses: frozenset[int] = frozenset({
        429,
        500,
        502,
        503,
        504,
    })

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
            self.base_delay * (2 ** (attempt - 1)),
            self.max_delay,
        )
```

---

# 9. RetryExecutor

Cũng trong `retry.py`:

```python
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
                    status_code=response.status_code,
                ):
                    return response

                if attempt < self.policy.max_attempts:

                    delay = self.policy.delay(attempt)

                    await asyncio.sleep(delay)

            except Exception as exc:

                last_exception = exc

                if not self.policy.should_retry(
                    attempt=attempt,
                    exception=exc,
                ):
                    raise

                if attempt < self.policy.max_attempts:

                    delay = self.policy.delay(attempt)

                    await asyncio.sleep(delay)

        if last_exception is not None:
            raise last_exception

        raise RuntimeError(
            "Retry attempts exhausted"
        )
```

### Luồng:

Ví dụ:

```text
GET
 ↓
503
 ↓
wait 1s
 ↓
GET
 ↓
503
 ↓
wait 2s
 ↓
GET
 ↓
200
 ↓
return
```

---

# 10. RateLimiter

`infrastructure/http/rate_limit.py`

```python
import asyncio


class RateLimiter:

    def __init__(
        self,
        requests_per_second: float,
    ):
        if requests_per_second <= 0:
            raise ValueError(
                "requests_per_second must be > 0"
            )

        self.interval = (
            1.0 / requests_per_second
        )

        self._lock = asyncio.Lock()

        self._next_allowed = 0.0

    async def acquire(self):

        loop = asyncio.get_running_loop()

        async with self._lock:

            now = loop.time()

            if now < self._next_allowed:

                wait_time = (
                    self._next_allowed - now
                )

                self._next_allowed += (
                    self.interval
                )

            else:

                wait_time = 0.0

                self._next_allowed = (
                    now + self.interval
                )

        if wait_time > 0:
            await asyncio.sleep(wait_time)
```

---

# 11. Bây giờ đến lớp quan trọng nhất

## `PrimpFetcher`

`infrastructure/http/primp_fetcher.py`

```python
import asyncio

from crawler.application.models.request import FetchRequest
from crawler.application.models.response import FetchResponse
from crawler.application.ports.fetcher import Fetcher

from crawler.infrastructure.http.primp_transport import (
    PrimpTransport,
)

from crawler.infrastructure.http.retry import (
    RetryExecutor,
)

from crawler.infrastructure.http.rate_limit import (
    RateLimiter,
)


class PrimpFetcher:

    def __init__(
        self,
        transport: PrimpTransport,
        retry_executor: RetryExecutor,
        rate_limiter: RateLimiter,
        semaphore: asyncio.Semaphore,
    ):
        self.transport = transport
        self.retry_executor = retry_executor
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        async def operation():

            # 1. Rate limiting
            await self.rate_limiter.acquire()

            # 2. Concurrency limiting
            async with self.semaphore:

                # 3. Actual HTTP request
                return await self.transport.send(
                    request
                )

        # 4. Retry
        return await self.retry_executor.execute(
            operation
        )
```

Đây chính là trung tâm của Buổi 44.

---

# 12. Hiểu thứ tự thực thi

Ta có:

```text
fetcher.get()
     │
     ▼
RetryExecutor
     │
     ▼
operation()
     │
     ├── RateLimiter
     │
     ▼
Semaphore
     │
     ▼
PrimpTransport
     │
     ▼
AsyncClient
     │
     ▼
HTTP
```

Nếu server trả:

```text
503
```

thì:

```text
RetryExecutor
      │
      ├── attempt 1
      │      ↓
      │   RateLimiter
      │      ↓
      │   Semaphore
      │      ↓
      │   HTTP
      │      ↓
      │     503
      │
      ├── wait
      │
      ├── attempt 2
      │      ↓
      │   RateLimiter
      │      ↓
      │   Semaphore
      │      ↓
      │   HTTP
      │      ↓
      │     200
      │
      └── return
```

Điểm rất quan trọng:

> **Retry attempt thứ 2 cũng phải đi qua RateLimiter.**

Không được viết:

```python
for attempt:
    await transport.send()
```

rồi mới rate-limit bên ngoài.

---

# 13. Composition Root

Bây giờ chúng ta cần lắp các dependency lại.

Ví dụ:

```python
import asyncio
import primp

from crawler.infrastructure.http.primp_transport import (
    PrimpTransport,
)

from crawler.infrastructure.http.primp_fetcher import (
    PrimpFetcher,
)

from crawler.infrastructure.http.retry import (
    RetryPolicy,
    RetryExecutor,
)

from crawler.infrastructure.http.rate_limit import (
    RateLimiter,
)


async def main():

    async with primp.AsyncClient(
        impersonate="chrome_146",
    ) as client:

        transport = PrimpTransport(
            client=client
        )

        retry_policy = RetryPolicy(
            max_attempts=3,
            base_delay=1,
            max_delay=10,
        )

        retry_executor = RetryExecutor(
            policy=retry_policy
        )

        rate_limiter = RateLimiter(
            requests_per_second=2
        )

        semaphore = asyncio.Semaphore(
            5
        )

        fetcher = PrimpFetcher(
            transport=transport,
            retry_executor=retry_executor,
            rate_limiter=rate_limiter,
            semaphore=semaphore,
        )

        # sử dụng fetcher...


if __name__ == "__main__":
    asyncio.run(main())
```

`primp` hiện yêu cầu Python ≥ 3.10; ví dụ async chính thức cũng sử dụng `AsyncClient` trong `async with`. ([PyPI][1])

---

# 14. Gọi Fetcher

```python
from crawler.application.models.request import FetchRequest


request = FetchRequest(
    url="https://example.com",
)

response = await fetcher.get(request)

print(response.status_code)
print(response.url)
print(response.text)
```

Application hoàn toàn không cần:

```python
import primp
```

Đây chính là Dependency Inversion.

---

# 15. Đưa vào Use Case

`application/use_cases/crawl_chapter.py`

```python
from crawler.application.models.request import (
    FetchRequest,
)

from crawler.application.ports.fetcher import (
    Fetcher,
)


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

        request = FetchRequest(
            url=url
        )

        response = await self.fetcher.get(
            request
        )

        if not response.is_success:

            raise RuntimeError(
                f"HTTP {response.status_code}"
            )

        return response.text
```

Use Case:

```text
CrawlChapter
      │
      ▼
Fetcher
      │
      ▼
FetchResponse
```

Không hề biết:

```text
Primp
Proxy
Semaphore
RateLimiter
Retry
TLS
HTTP/2
```

---

# 16. Test mà không cần Internet

Đây là phần rất quan trọng.

Ta tạo:

```python
class FakeTransport:

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    async def send(self, request):

        self.calls += 1

        if not self.responses:
            raise RuntimeError(
                "No response"
            )

        return self.responses.pop(0)
```

Fake response:

```python
class FakeResponse:

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

# 17. Test Retry

```python
import asyncio

from crawler.infrastructure.http.primp_fetcher import (
    PrimpFetcher,
)

from crawler.infrastructure.http.retry import (
    RetryPolicy,
    RetryExecutor,
)

from crawler.infrastructure.http.rate_limit import (
    RateLimiter,
)

from crawler.application.models.request import (
    FetchRequest,
)


async def main():

    transport = FakeTransport([
        FakeResponse(503),
        FakeResponse(503),
        FakeResponse(200),
    ])

    retry_executor = RetryExecutor(
        RetryPolicy(
            max_attempts=3,
            base_delay=0.1,
        )
    )

    fetcher = PrimpFetcher(
        transport=transport,
        retry_executor=retry_executor,
        rate_limiter=RateLimiter(100),
        semaphore=asyncio.Semaphore(5),
    )

    response = await fetcher.get(
        FetchRequest(
            url="https://example.com"
        )
    )

    print(
        "status:",
        response.status_code
    )

    print(
        "calls:",
        transport.calls
    )


asyncio.run(main())
```

Kết quả mong đợi:

```text
status: 200
calls: 3
```

Ta vừa chứng minh:

```text
503
 ↓
retry
 ↓
503
 ↓
retry
 ↓
200
```

---

# 18. Test không retry

```python
transport = FakeTransport([
    FakeResponse(404),
])
```

Sau đó:

```python
response = await fetcher.get(
    FetchRequest(
        url="https://example.com"
    )
)
```

Kết quả:

```text
status = 404
calls = 1
```

Không retry.

Điều này rất quan trọng đối với crawler.

Ví dụ:

```text
404 → chapter không tồn tại
```

không nên biến thành:

```text
404
 ↓
retry
 ↓
404
 ↓
retry
 ↓
404
```

---

# 19. Test concurrency

Giả sử:

```python
semaphore = asyncio.Semaphore(3)
```

và chúng ta có:

```text
100 URLs
```

Không có nghĩa:

```text
100 requests cùng lúc
```

Mà tối đa:

```text
request 1 ─┐
request 2  ├── 3 concurrent
request 3 ─┘

request 4 ─┐
request 5  ├── chờ
request 6 ─┘
```

Khi một request hoàn thành:

```text
request 1 DONE
      ↓
request 4 chạy
```

---

# 20. Test Rate Limit

Nếu:

```python
RateLimiter(
    requests_per_second=2
)
```

thì khoảng cách pacing mục tiêu là:

```text
1 / 2 = 0.5 giây
```

Ví dụ:

```text
request 1
    ↓
~0.5s
    ↓
request 2
    ↓
~0.5s
    ↓
request 3
```

Nhưng:

> RateLimiter không giới hạn số request đang chạy.

Đó là nhiệm vụ của:

```python
Semaphore
```

---

# 21. Ba thành phần rất dễ nhầm

| Thành phần      | Nhiệm vụ                      |
| --------------- | ----------------------------- |
| `Semaphore`     | Giới hạn concurrent requests  |
| `RateLimiter`   | Giới hạn tốc độ request       |
| `RetryExecutor` | Quyết định và thực hiện retry |

Ví dụ:

```text
100 URLs
   │
   ▼
RateLimiter
2 req/s
   │
   ▼
Semaphore
5 concurrent
   │
   ▼
HTTP
   │
   ▼
503
   │
   ▼
RetryExecutor
```

Ba abstraction này **không nên gộp thành một class**.

---

# 22. PrimpFetcher có phải God Object không?

Hiện tại:

```python
class PrimpFetcher:
    def __init__(
        self,
        transport,
        retry_executor,
        rate_limiter,
        semaphore,
    ):
```

Có vẻ nhiều dependency.

Nhưng trách nhiệm của nó chỉ là:

> **Orchestrate quá trình fetch.**

Nó không thực hiện:

```text
❌ retry algorithm
❌ rate limiting algorithm
❌ HTTP implementation
❌ browser fingerprint
❌ proxy selection
```

Nó chỉ phối hợp:

```text
PrimpFetcher
     │
     ├── RetryExecutor
     ├── RateLimiter
     ├── Semaphore
     └── Transport
```

Đây là khác biệt rất quan trọng.

---

# 23. `PrimpFetcher` và `PrimpTransport` khác nhau thế nào?

### `PrimpTransport`

```text
"HOW do I talk to primp?"
```

Nó biết:

```python
primp.AsyncClient
client.get()
response.status_code
response.content
```

---

### `PrimpFetcher`

```text
"HOW do I fetch safely?"
```

Nó biết:

```text
retry
rate limit
concurrency
transport
```

---

### `Fetcher`

```text
"WHAT capability does Application need?"
```

Nó chỉ biết:

```python
async def get(
    request: FetchRequest
) -> FetchResponse:
    ...
```

Ba tầng:

```text
Fetcher
  ↑
PrimpFetcher
  ↓
PrimpTransport
  ↓
primp.AsyncClient
```

---

# 24. SOLID trong Buổi 44

### Single Responsibility

```text
PrimpTransport
    → HTTP

RetryExecutor
    → retry

RateLimiter
    → rate

Semaphore
    → concurrency

PrimpFetcher
    → orchestration
```

---

### Open/Closed

Sau này muốn dùng `httpx`:

```python
class HttpxTransport:
    ...
```

Không cần sửa:

```python
CrawlChapter
```

và gần như không cần sửa:

```python
PrimpFetcher
```

---

### Liskov Substitution

Application:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
    ):
        ...
```

Có thể truyền:

```text
PrimpFetcher
FakeFetcher
HttpxFetcher
```

---

### Dependency Inversion

Không phải:

```text
CrawlChapter
    ↓
primp
```

mà là:

```text
CrawlChapter
    ↓
Fetcher Protocol
    ↑
PrimpFetcher
```

---

# 25. Toàn bộ kiến trúc hiện tại

Sau Buổi 44:

```text
                    APPLICATION
                         │
                         ▼
                 ┌──────────────┐
                 │   Fetcher    │
                 │   Protocol   │
                 └──────┬───────┘
                        ▲
                        │
                 ┌──────┴───────┐
                 │ PrimpFetcher │
                 └──────┬───────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
       RetryExecutor RateLimiter Semaphore
            │           │           │
            └───────────┼───────────┘
                        ▼
                 PrimpTransport
                        │
                        ▼
                primp.AsyncClient
                        │
                        ▼
                      HTTP
```

---

# 26. Và toàn bộ Novel Crawler

Bây giờ hệ thống bắt đầu hình thành rất rõ:

```text
                  CrawlChapter
                       │
                       ▼
                    Fetcher
                       │
                       ▼
                 PrimpFetcher
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      Retry         RateLimit      Semaphore
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                PrimpTransport
                       │
                       ▼
                primp.AsyncClient
                       │
                       ▼
                  FetchResponse
                       │
                       ▼
                 ChapterParser
                       │
                       ▼
                    Chapter
                       │
                       ▼
                  Repository
                       │
                       ▼
                    SQLite
```

Đây chính là kiến trúc chúng ta sẽ tiếp tục mở rộng ở **Buổi 45 — Retry Policy**.

---

# 27. Một lưu ý quan trọng trước Buổi 45

Hiện tại:

```python
except Exception:
    retry
```

là **quá rộng cho production**.

Ví dụ một số lỗi có thể không nên retry:

```text
Invalid URL
Authentication configuration error
Programming error
Invalid request
...
```

Do đó ở:

**Buổi 48 — Error Classification**

chúng ta sẽ chuyển từ:

```text
Exception
   ↓
retry
```

sang:

```text
Exception
    ↓
Error Classification
    ├── Retryable
    ├── NonRetryable
    ├── Proxy Error
    ├── Timeout
    ├── HTTP Error
    └── Configuration Error
```

Đó mới là phiên bản production-grade.

---

## Tóm tắt Buổi 44

Bạn cần nắm chắc 5 điểm:

```text
1. Fetcher
   = Port

2. PrimpFetcher
   = orchestrator

3. PrimpTransport
   = adapter cho primp

4. RetryExecutor
   = retry

5. RateLimiter + Semaphore
   = kiểm soát tốc độ + concurrency
```

Và flow chuẩn:

```text
FetchRequest
     ↓
PrimpFetcher
     ↓
RetryExecutor
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

`primp` 2.0.1 hiện là bản phát hành mới nhất trên PyPI và tài liệu chính thức xác nhận API `AsyncClient` cùng các browser profile hiện hành. ([PyPI][1])

**Buổi 45** sẽ đi sâu vào **Retry Policy production-grade**: `Retry-After`, exponential backoff + jitter, retry theo exception/status, idempotency và cách thiết kế `RetryDecision` để không biến `PrimpFetcher` thành God Object.

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
