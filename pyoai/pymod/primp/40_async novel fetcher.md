# Buổi 40 — Xây dựng Async Novel Fetcher

Đây là **bài tổng kết Phần IV — Async + Crawler**.

Sau bài này, chúng ta không chỉ biết dùng `primp.AsyncClient`, mà có một `AsyncNovelFetcher` có kiến trúc đủ sạch để bước sang **Phần V — Novel Crawler**.

---

# 1. Mục tiêu

Fetcher cuối cùng cần xử lý:

```text
Novel URL
    ↓
FetchRequest
    ↓
Retry
    ↓
Rate Limiter
    ↓
Semaphore
    ↓
Proxy
    ↓
Browser Profile
    ↓
primp.AsyncClient
    ↓
FetchResponse
    ↓
Parser
```

Các concern:

```text
Timeout          → HTTP request
Retry            → RetryPolicy
Rate limiting    → RateLimiter
Concurrency      → Semaphore
Proxy            → ProxyPool
Browser identity → BrowserProfilePool
HTTP             → primp.AsyncClient
```

Không để tất cả vào một class.

---

# 2. Kiến trúc cuối cùng

```text
                    APPLICATION
                         │
                         ↓
                ┌─────────────────┐
                │ AsyncNovelFetch │
                └────────┬────────┘
                         │
                         ↓
                   FetchRequest
                         │
                         ↓
                  RetryExecutor
                         │
                         ↓
                   RateLimiter
                         │
                         ↓
                    Semaphore
                         │
                         ↓
                  Request Context
                  /             \
                 ↓               ↓
            ProxyPool      BrowserProfilePool
                 \               /
                  \             /
                   ↓           ↓
                    PrimpTransport
                         │
                         ↓
                  primp.AsyncClient
                         │
                         ↓
                        HTTP
                         │
                         ↓
                   FetchResponse
                         │
                         ↓
                      Parser
```

Đây là architecture chúng ta sẽ giữ làm nền tảng.

---

# 3. Trước tiên: Domain không biết HTTP

Ví dụ Entity:

```python
@dataclass
class Chapter:
    title: str
    content: str
```

Domain không được import:

```python
import primp
import asyncio
```

Domain chỉ biết:

```text
Novel
Chapter
CrawlTask
```

---

# 4. Application cần Fetcher

Application định nghĩa contract:

```python
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

# 5. Vì sao dùng `FetchRequest`?

Không muốn API thành:

```python
fetcher.get(
    url,
    headers,
    params,
    timeout,
    proxy,
    profile,
    retry,
    ...
)
```

Thay vào đó:

```python
request = FetchRequest(
    url=url,
    headers={
        "Accept": "text/html",
    },
    timeout=10,
)
```

Application chỉ mô tả:

> Tôi muốn lấy URL này.

---

# 6. Request không chứa Proxy

Không làm:

```python
@dataclass
class FetchRequest:
    url: str
    proxy: ProxyConfig
```

Vì Proxy là infrastructure concern.

Tương tự:

```text
FetchRequest
    ✗ Proxy
    ✗ BrowserProfile
    ✗ RetryPolicy
    ✗ RateLimiter
    ✗ primp.Client
```

---

# 7. `PrimpTransport`

Transport là lớp duy nhất trực tiếp nói chuyện với `primp`.

```python
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

`primp` hiện cung cấp `AsyncClient` và async request API; đây là lý do nó phù hợp nằm sau một transport adapter trong architecture này.

---

# 8. Response Adapter

Không đưa `primp.Response` ra Application.

```python
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

Flow:

```text
primp.Response
      ↓
adapt_response()
      ↓
FetchResponse
```

---

# 9. Browser Profile

Ta đã học Browser Profile ở Buổi 37.

Ví dụ:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:

    impersonate: str

    os: str | None = None
```

Ví dụ:

```python
chrome_windows = BrowserProfile(
    impersonate="chrome_146",
    os="windows",
)
```

---

# 10. Browser Profile Pool

Pool đơn giản:

```python
class BrowserProfilePool:

    def __init__(
        self,
        profiles: list[BrowserProfile],
    ):
        if not profiles:
            raise ValueError(
                "Profile pool cannot be empty"
            )

        self.profiles = profiles
        self.index = 0

    def next(self) -> BrowserProfile:

        profile = self.profiles[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % len(self.profiles)

        return profile
```

Ví dụ:

```python
pool = BrowserProfilePool([
    BrowserProfile(
        "chrome_146",
        "windows",
    ),
    BrowserProfile(
        "firefox_146",
        "windows",
    ),
    BrowserProfile(
        "edge_146",
        "windows",
    ),
])
```

---

# 11. Nhưng có một vấn đề

Nếu mỗi request:

```text
Profile A
Profile B
Profile C
Profile A
```

mà vẫn dùng cùng một `AsyncClient`, thì concept identity có thể trở nên khó kiểm soát.

Ta muốn:

```text
Browser Profile
+
Proxy
+
Client
```

gắn với một execution identity ổn định.

Do đó trong crawler thật, thay vì random profile trên từng request, ta thường quản lý **client/session resources**.

---

# 12. Request Context

Ta có thể biểu diễn:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestContext:

    profile: BrowserProfile

    proxy: ProxyConfig | None = None
```

Nó nói:

```text
Request này được thực thi trong context nào?
```

Nhưng nó vẫn không phải Domain Model.

---

# 13. ProxyConfig

Từ Buổi 14:

```python
@dataclass(frozen=True)
class ProxyConfig:

    url: str

    username: str | None = None

    password: str | None = None
```

Không log:

```python
proxy.password
```

---

# 14. Proxy Pool

Ví dụ round-robin:

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

        self.proxies = proxies
        self.index = 0

    def next(self) -> ProxyConfig:

        proxy = self.proxies[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % len(self.proxies)

        return proxy
```

Ví dụ:

```text
A
B
C
A
B
C
...
```

Trong production, ProxyPool sau này có thể thông minh hơn:

```text
healthy
failure count
cooldown
latency
```

nhưng chưa cần nhồi vào `AsyncNovelFetcher`.

---

# 15. Một điểm quan trọng về primp + Proxy

Ở tầng architecture:

```text
ProxyPool
    ↓
ProxyConfig
    ↓
PrimpTransport / Client configuration
```

Còn **cách truyền proxy chính xác vào API `primp`** nên được cô lập trong Infrastructure.

Điều này rất có giá trị:

Nếu API thư viện thay đổi:

```text
PrimpTransport
```

thay đổi.

Application không cần sửa.

---

# 16. RateLimiter

Ta giữ implementation từ Buổi 38:

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
            await asyncio.sleep(
                wait_time
            )
```

---

# 17. Semaphore

Đơn giản:

```python
semaphore = asyncio.Semaphore(10)
```

Nó đảm bảo:

```text
MAX ACTIVE HTTP OPERATIONS = 10
```

Không phải:

```text
10 requests / second
```

RateLimiter mới đảm nhiệm tốc độ.

---

# 18. Retry Policy

```python
from dataclasses import dataclass


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

        return (
            status_code
            in self.retryable_statuses
        )

    def delay(
        self,
        attempt: int,
    ) -> float:

        return min(
            self.base_delay
            * 2 ** (attempt - 1),
            self.max_delay,
        )
```

---

# 19. RetryExecutor

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

                should_retry = (
                    self.policy.should_retry(
                        attempt=attempt,
                        status_code=(
                            response.status_code
                        ),
                    )
                )

                if not should_retry:
                    return response

                if attempt < (
                    self.policy.max_attempts
                ):

                    delay = (
                        self.policy.delay(
                            attempt
                        )
                    )

                    await asyncio.sleep(
                        delay
                    )

            except Exception as exc:

                last_exception = exc

                should_retry = (
                    self.policy.should_retry(
                        attempt=attempt,
                        exception=exc,
                    )
                )

                if not should_retry:
                    raise

                if attempt < (
                    self.policy.max_attempts
                ):

                    delay = (
                        self.policy.delay(
                            attempt
                        )
                    )

                    await asyncio.sleep(
                        delay
                    )

        if last_exception is not None:
            raise last_exception

        raise RuntimeError(
            "Retry attempts exhausted"
        )
```

---

# 20. Bây giờ xây `AsyncNovelFetcher`

Đây là phần trung tâm.

```python
class AsyncNovelFetcher:

    def __init__(
        self,
        transport,
        rate_limiter,
        semaphore,
        retry_executor,
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

                raw_response = (
                    await self.transport.send(
                        request
                    )
                )

                return adapt_response(
                    raw_response
                )

        return await self.retry_executor.execute(
            operation
        )
```

Đây là **orchestrator**.

Nó không biết chi tiết:

```text
TLS
HTTP/2
socket
connection pool
```

---

# 21. Flow thực tế

Một chapter:

```text
https://example.com/chapter-100
```

đi qua:

```text
AsyncNovelFetcher.get()
        ↓
RetryExecutor
        ↓
Attempt 1
        ↓
RateLimiter
        ↓
Semaphore
        ↓
Transport
        ↓
primp.AsyncClient
        ↓
HTTP
```

Nếu:

```text
500
```

thì:

```text
RetryExecutor
        ↓
backoff
        ↓
Attempt 2
        ↓
RateLimiter
        ↓
Semaphore
        ↓
HTTP
```

---

# 22. Parser nằm sau Fetcher

Đây là boundary cực kỳ quan trọng.

Không làm:

```python
class AsyncNovelFetcher:

    async def get_chapter(self, url):
        html = ...
        parser = ChapterParser()
        return parser.parse(html)
```

Fetcher chỉ fetch.

Đúng:

```text
Fetcher
   ↓
FetchResponse
   ↓
Parser
   ↓
Chapter
```

---

# 23. Use Case

Ví dụ:

```python
class CrawlChapter:

    def __init__(
        self,
        fetcher: Fetcher,
        parser,
    ):
        self.fetcher = fetcher
        self.parser = parser

    async def execute(
        self,
        url: str,
    ):

        response = await self.fetcher.get(
            FetchRequest(
                url=url,
                headers={
                    "Accept": "text/html",
                },
                timeout=10,
            )
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code}"
            )

        return self.parser.parse(
            response.text
        )
```

Flow:

```text
CrawlChapter
     ↓
Fetcher
     ↓
HTML
     ↓
ChapterParser
     ↓
Chapter
```

---

# 24. Đây chính là DDD boundary

```text
Domain
  │
  │ Chapter
  │ Novel
  │ CrawlTask
  ↓
Application
  │
  │ CrawlChapter
  │ Fetcher Port
  ↓
Infrastructure
  │
  │ PrimpFetcher
  │ PrimpTransport
  │ Proxy
  │ Browser Profile
  │ RateLimiter
  ↓
primp
```

---

# 25. Composition Root

Bây giờ tất cả dependency được lắp ở một nơi.

```python
import asyncio
import primp


async def main():

    client = primp.AsyncClient(
        impersonate="chrome_146",
        impersonate_os="windows",
    )

    transport = PrimpTransport(
        client
    )

    rate_limiter = RateLimiter(
        requests_per_second=2
    )

    semaphore = asyncio.Semaphore(10)

    retry_executor = RetryExecutor(
        RetryPolicy(
            max_attempts=3,
            base_delay=1,
        )
    )

    fetcher = AsyncNovelFetcher(
        transport=transport,
        rate_limiter=rate_limiter,
        semaphore=semaphore,
        retry_executor=retry_executor,
    )

    response = await fetcher.get(
        FetchRequest(
            url="https://httpbin.org/get",
            timeout=10,
        )
    )

    print(response.status_code)
    print(response.url)
    print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

Ở đây:

```text
main()
```

là **Composition Root**.

---

# 26. Vì sao Composition Root rất quan trọng?

Application không tự làm:

```python
primp.AsyncClient(...)
```

mà Composition Root làm.

Sau này muốn đổi:

```text
primp
```

thành:

```text
httpx
```

thì:

```text
Application
    ↓
Fetcher
```

không thay đổi.

Chỉ Infrastructure thay đổi.

---

# 27. FakeTransport

Đây là cách test cực tốt.

```python
class FakeResponse:

    def __init__(
        self,
        status_code: int,
        content: bytes = b"hello",
    ):
        self.status_code = status_code
        self.url = "https://example.com"
        self.headers = {}
        self.content = content


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

---

# 28. Test success

```python
async def test_success():

    transport = FakeTransport([
        FakeResponse(200, b"chapter html")
    ])

    fetcher = AsyncNovelFetcher(
        transport=transport,
        rate_limiter=RateLimiter(1000),
        semaphore=asyncio.Semaphore(10),
        retry_executor=RetryExecutor(
            RetryPolicy(
                max_attempts=3,
                base_delay=0.001,
            )
        ),
    )

    response = await fetcher.get(
        FetchRequest(
            url="https://example.com/chapter"
        )
    )

    assert response.status_code == 200

    assert response.text == (
        "chapter html"
    )

    assert transport.calls == 1
```

---

# 29. Test Retry

```python
async def test_retry():

    transport = FakeTransport([
        FakeResponse(500),
        FakeResponse(500),
        FakeResponse(
            200,
            b"success",
        ),
    ])

    fetcher = AsyncNovelFetcher(
        transport=transport,
        rate_limiter=RateLimiter(1000),
        semaphore=asyncio.Semaphore(10),
        retry_executor=RetryExecutor(
            RetryPolicy(
                max_attempts=3,
                base_delay=0.001,
            )
        ),
    )

    response = await fetcher.get(
        FetchRequest(
            url="https://example.com"
        )
    )

    assert response.status_code == 200

    assert transport.calls == 3
```

Không có:

```text
Internet
DNS
Proxy
TLS
primp
```

Test vẫn chạy.

Đây là giá trị lớn nhất của architecture này.

---

# 30. Test 404 không retry

```python
async def test_404():

    transport = FakeTransport([
        FakeResponse(404)
    ])

    fetcher = AsyncNovelFetcher(
        transport=transport,
        rate_limiter=RateLimiter(1000),
        semaphore=asyncio.Semaphore(10),
        retry_executor=RetryExecutor(
            RetryPolicy(
                max_attempts=3,
                base_delay=0.001,
            )
        ),
    )

    response = await fetcher.get(
        FetchRequest(
            url="https://example.com/missing"
        )
    )

    assert response.status_code == 404

    assert transport.calls == 1
```

Đây là behavior mong muốn của policy hiện tại.

---

# 31. Test concurrency

Ta có thể tạo transport giả:

```python
class SlowFakeTransport:

    def __init__(
        self,
        delay: float,
    ):
        self.delay = delay
        self.active = 0
        self.max_active = 0

    async def send(
        self,
        request,
    ):

        self.active += 1

        self.max_active = max(
            self.max_active,
            self.active,
        )

        try:

            await asyncio.sleep(
                self.delay
            )

            return FakeResponse(200)

        finally:

            self.active -= 1
```

---

# 32. Test Semaphore

```python
async def test_concurrency():

    transport = SlowFakeTransport(
        delay=0.1
    )

    fetcher = AsyncNovelFetcher(
        transport=transport,
        rate_limiter=RateLimiter(1000),
        semaphore=asyncio.Semaphore(3),
        retry_executor=RetryExecutor(
            RetryPolicy(
                max_attempts=1
            )
        ),
    )

    requests = [
        FetchRequest(
            url=f"https://example.com/{i}"
        )
        for i in range(10)
    ]

    await asyncio.gather(
        *(
            fetcher.get(request)
            for request in requests
        )
    )

    assert transport.max_active <= 3
```

Ta vừa kiểm tra được:

```text
10 requests
↓
Semaphore(3)
↓
MAX ACTIVE <= 3
```

---

# 33. Test RateLimiter

Không cần HTTP.

```python
async def test_rate_limiter():

    limiter = RateLimiter(
        requests_per_second=5
    )

    times = []

    async def worker():

        await limiter.acquire()

        times.append(
            asyncio.get_running_loop().time()
        )

    await asyncio.gather(
        *(worker() for _ in range(5))
    )

    times.sort()

    intervals = [
        b - a
        for a, b in zip(
            times,
            times[1:],
        )
    ]

    print(intervals)
```

Ta kỳ vọng các khoảng thời gian gần:

```text
0.2s
0.2s
0.2s
0.2s
```

---

# 34. Một vấn đề thực tế: RateLimiter + Retry

Ta thiết kế:

```text
RetryExecutor
    ↓
operation()
    ↓
RateLimiter
    ↓
HTTP
```

Đây là lựa chọn có chủ ý.

Mỗi attempt:

```text
Attempt 1 → RateLimiter → HTTP
Attempt 2 → RateLimiter → HTTP
Attempt 3 → RateLimiter → HTTP
```

Do đó retry cũng chịu rate limit.

---

# 35. Một vấn đề thực tế khác: Retry + 429

Nếu server:

```http
429 Too Many Requests
Retry-After: 5
```

thì production Fetcher nên xử lý:

```text
429
 ↓
Retry-After
 ↓
backoff
 ↓
RateLimiter
 ↓
retry
```

Ở architecture hiện tại, việc parse `Retry-After` nên được đưa vào **Retry/HTTP policy**, không đưa vào Parser truyện.

---

# 36. Proxy + Retry

Một behavior quan trọng:

```text
Proxy A
   ↓
timeout
   ↓
Proxy A failure
   ↓
Retry
```

Không nhất thiết:

```text
Proxy A
   ↓
retry
   ↓
Proxy A
```

Nếu A có dấu hiệu unhealthy, retry có thể chọn:

```text
Proxy B
```

Flow production:

```text
Attempt 1
    ↓
Proxy A
    ↓
timeout
    ↓
mark A unhealthy
    ↓
Attempt 2
    ↓
Proxy B
```

Đây là nơi **ProxyPool + RetryPolicy** bắt đầu tương tác.

Buổi 48 sẽ làm phần Error Classification sâu hơn.

---

# 37. Browser Profile + Proxy

Ta có:

```text
Profile A
Proxy A
```

và:

```text
Profile B
Proxy B
```

không nên hiểu rằng:

```text
mỗi request random mọi thứ
```

Ví dụ:

```text
request 1 → Chrome/Windows + Proxy A
request 2 → Firefox/Linux + Proxy B
request 3 → Safari/iOS + Proxy C
```

có thể tạo behavior rất không ổn định.

Tốt hơn là quản lý **identity/session ổn định**.

```text
Crawler Identity
 ├── Browser Profile
 ├── Proxy
 └── Client/Session
```

---

# 38. Đây là lý do Pool sau này nên tiến hóa

Hiện tại:

```text
ProxyPool
BrowserProfilePool
```

là hai pool riêng.

Sau này có thể có:

```text
ClientIdentityPool
```

mỗi identity:

```text
Identity
 ├── BrowserProfile
 ├── Proxy
 └── AsyncClient
```

Ví dụ:

```text
Identity #1
 ├── Chrome Windows
 ├── Proxy A
 └── Client A

Identity #2
 ├── Firefox Windows
 ├── Proxy B
 └── Client B
```

Nhưng **chưa cần triển khai abstraction này ở Buổi 40**.

---

# 39. Cấu trúc project hoàn chỉnh

Sau Phần IV, tôi đề xuất:

```text
src/
└── crawler/
    │
    ├── domain/
    │   ├── novel.py
    │   ├── chapter.py
    │   └── crawl_task.py
    │
    ├── application/
    │   │
    │   ├── ports/
    │   │   └── fetcher.py
    │   │
    │   └── use_cases/
    │       └── crawl_chapter.py
    │
    └── infrastructure/
        │
        └── http/
            │
            ├── primp_transport.py
            ├── async_fetcher.py
            ├── retry.py
            ├── rate_limit.py
            ├── proxy.py
            ├── proxy_pool.py
            ├── browser_profile.py
            └── browser_profile_pool.py
```

---

# 40. Luồng Crawl Chapter hoàn chỉnh

Đây chính là thứ chúng ta hướng tới.

```text
                 CrawlChapter
                      │
                      ↓
              FetchRequest(URL)
                      │
                      ↓
                AsyncFetcher
                      │
                      ↓
                RetryExecutor
                      │
                      ↓
                 RateLimiter
                      │
                      ↓
                  Semaphore
                      │
                      ↓
              Identity Selection
                 /          \
                ↓            ↓
             Proxy       BrowserProfile
                 \          /
                  \        /
                   ↓      ↓
                PrimpTransport
                      │
                      ↓
               AsyncClient
                      │
                      ↓
                    HTTP
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
                ChapterRepository
                      │
                      ↓
                   SQLite
```

Đây là pipeline gần với hệ thống Novel Crawler mà chúng ta đã thiết kế ở các buổi DDD trước.

---

# 41. Parser không được gọi HTTP

Ví dụ `ChapterParser`:

```python
class ChapterParser:

    def parse(
        self,
        html: str,
    ):
        ...
```

Nó nhận:

```text
HTML
```

chứ không nhận:

```text
URL
```

rồi tự gọi:

```python
httpx.get(...)
```

hoặc:

```python
primp.get(...)
```

Architecture:

```text
Fetcher
   ↓
HTML
   ↓
Parser
```

không phải:

```text
Parser
   ↓
HTTP
   ↓
HTML
```

---

# 42. Tại sao architecture này rất hợp với crawler?

Vì crawler có hai loại thay đổi.

### Thay đổi HTTP

Ví dụ:

```text
primp
↓
httpx
```

hoặc:

```text
proxy strategy
↓
new proxy strategy
```

Infrastructure thay đổi.

---

### Thay đổi nghiệp vụ

Ví dụ:

```text
Chapter
Novel
Chapter numbering
Duplicate detection
Save chapter
```

Domain/Application thay đổi.

Hai loại thay đổi không kéo nhau đi theo.

---

# 43. SOLID của toàn bộ Fetcher

```text
PrimpTransport
    → Single Responsibility

RetryPolicy
    → Single Responsibility

RateLimiter
    → Single Responsibility

ProxyPool
    → Single Responsibility

BrowserProfilePool
    → Single Responsibility
```

Fetcher:

```text
AsyncNovelFetcher
    → orchestration
```

Fetcher Protocol:

```text
Fetcher
    → abstraction
```

FakeTransport:

```text
FakeTransport
    → testing adapter
```

Đây là SOLID theo hướng thực dụng, không phải tạo class chỉ để "đủ SOLID".

---

# 44. Điều chúng ta không làm

Không tạo:

```text
RetryManager
RetryFactory
RateLimiterFactory
SemaphoreManager
ProxyManagerFactory
BrowserProfileFactory
TransportFactory
FetcherBuilder
FetcherFactoryFactory
```

😄

Abstraction chỉ xuất hiện khi nó giải quyết một vấn đề thật.

---

# 45. Một `AsyncNovelFetcher` tốt cần làm gì?

Chỉ cần orchestration:

```text
1. nhận FetchRequest
2. thực hiện attempt
3. rate limit
4. concurrency limit
5. gửi transport
6. retry nếu cần
7. trả FetchResponse
```

Không:

```text
parse HTML
save SQLite
construct Novel
construct Chapter
```

---

# 46. Production flow

Một request production có thể trở thành:

```text
FetchRequest
    │
    ↓
RetryExecutor
    │
    ├── Attempt 1
    │      ↓
    │  RateLimiter
    │      ↓
    │  Semaphore
    │      ↓
    │  Identity
    │      ↓
    │  HTTP
    │      ↓
    │  503
    │
    ├── Backoff
    │
    ├── Attempt 2
    │      ↓
    │  RateLimiter
    │      ↓
    │  Semaphore
    │      ↓
    │  Identity
    │      ↓
    │  HTTP
    │      ↓
    │  200
    │
    ↓
FetchResponse
```

Đây là một Fetcher thực sự có khả năng phục vụ crawler.

---

# 47. Phần IV đã hoàn thành

```text
PHẦN IV — ASYNC + CRAWLER

31. AsyncClient
        ↓
32. async GET
        ↓
33. Concurrent Requests
        ↓
34. Semaphore
        ↓
35. Timeout + Retry
        ↓
36. Proxy Pool
        ↓
37. Browser Profile Pool
        ↓
38. Rate Limiting
        ↓
39. Fetcher Architecture
        ↓
40. Async Novel Fetcher        ✅
```

Toàn bộ phần này đã đi từ:

```text
await client.get(url)
```

đến:

```text
Async Novel Fetcher
```

theo architecture.

---

# 48. Và đây là điểm kết thúc quan trọng

Chúng ta đã xây xong **HTTP Infrastructure**.

Từ đây không nên tiếp tục đào sâu `primp` một cách rời rạc nữa.

Phần V sẽ đưa nó vào **Novel Crawler thật**:

```text
PHẦN V — NOVEL CRAWLER

41. Request Model
42. Response Model
43. Fetcher Interface
44. PrimpFetcher
45. Retry Policy
46. Proxy Strategy
47. Browser Profile Strategy
48. Error Classification
49. Observability / Logging
50. Production Fetcher
```

Điểm thú vị là nhiều thành phần của 41–47 chúng ta **đã làm prototype ở Phần IV**. Vì vậy Phần V sẽ không học lại; chúng ta sẽ **refactor chúng thành kiến trúc production**, gắn trực tiếp với `CrawlTask`, `Novel`, `Chapter`, Repository và Clean Architecture của Novel Crawler.

### Architecture đích

```text
                    ┌──────────────────────┐
                    │      CrawlTask       │
                    └──────────┬───────────┘
                               ↓
                         Application
                               ↓
                    ┌──────────────────────┐
                    │   AsyncNovelFetcher  │
                    └──────────┬───────────┘
                               ↓
                  ┌────────────┼────────────┐
                  ↓            ↓            ↓
             RetryPolicy  RateLimiter  ProxyStrategy
                  │            │            │
                  └────────────┼────────────┘
                               ↓
                    BrowserProfileStrategy
                               ↓
                        PrimpFetcher
                               ↓
                     primp.AsyncClient
                               ↓
                         FetchResponse
                               ↓
                          Novel Parser
                               ↓
                         Domain Model
                               ↓
                          Repository
                               ↓
                            SQLite
```

**Đây là nền móng HTTP hoàn chỉnh của Novel Crawler.**
