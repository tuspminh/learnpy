# Buổi 50 — Production Fetcher

Đây là **buổi tổng kết Part V**.

Sau 49 buổi học `primp`, chúng ta không còn mục tiêu đơn giản là:

```python
response = client.get(url)
```

Mà mục tiêu là xây được một HTTP layer đủ sạch để Novel Crawler sử dụng:

```text
                    Novel Crawler
                         │
                         ▼
                    Fetcher Port
                         │
                         ▼
                  ProductionFetcher
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   RetryPolicy       RateLimiter      Semaphore
       │                                   │
       ▼                                   ▼
 ErrorClassifier                    BrowserContext
       │                              Strategy
       ▼                                  │
 FetchError                              ▼
                                  Browser + Proxy
                                         │
                                         ▼
                                  PrimpTransport
                                         │
                                         ▼
                                 primp.AsyncClient
```

Tính đến hiện tại, `primp` 2.0.1 là bản mới nhất trên PyPI, yêu cầu Python >=3.10 và cung cấp cả `Client`/`AsyncClient`, browser impersonation và các OS profile. Vì API của thư viện thay đổi tương đối nhanh, phần adapter bên dưới cố tình giữ API `primp` ở **Infrastructure**, không để lan vào Application. ([PyPI][1])

---

# 1. Production Fetcher cần giải quyết gì?

Một request production phải xử lý:

```text
1. Request validation
2. Browser context
3. Proxy
4. Rate limiting
5. Concurrency limiting
6. HTTP request
7. Timeout
8. Error classification
9. Retry
10. Context health
11. Logging
12. Response adaptation
```

Nhưng **không được** biến tất cả thành một class khổng lồ.

---

# 2. Kiến trúc cuối cùng

Ta hướng tới:

```text
                    ┌─────────────────────┐
                    │   CrawlChapter      │
                    │     Use Case        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Fetcher Protocol  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ ProductionFetcher   │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   RetryPolicy          RateLimiter          Semaphore
          │
          ▼
   ErrorClassifier
          │
          ▼
      FetchError
          │
          ▼
 BrowserContextStrategy
          │
          ▼
   BrowserContext
      │         │
      ▼         ▼
 Browser      Proxy
 Profile        │
      │         │
      └────┬────┘
           ▼
    PrimpTransport
           │
           ▼
   primp.AsyncClient
```

---

# 3. Project structure

Đây là structure tôi đề xuất chốt cho Part V:

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
        │
        ├── http/
        │   ├── primp_transport.py
        │   ├── production_fetcher.py
        │   ├── errors.py
        │   ├── error_classifier.py
        │   ├── retry.py
        │   ├── rate_limit.py
        │   ├── semaphore.py
        │   ├── proxy.py
        │   ├── proxy_strategy.py
        │   ├── browser_profile.py
        │   └── browser_strategy.py
        │
        └── logging/
            ├── config.py
            └── fetch_logger.py
```

Điểm quan trọng:

```text
Application
    ↓
không import primp
```

---

# 4. Request Model

Ta giữ model nhỏ:

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

        if parsed.scheme not in {
            "http",
            "https",
        }:
            raise ValueError(
                "URL must use http or https"
            )

        if (
            self.timeout is not None
            and self.timeout <= 0
        ):
            raise ValueError(
                "timeout must be > 0"
            )
```

---

# 5. Response Model

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

# 6. Fetcher Port

Application chỉ cần:

```python
from typing import Protocol


class Fetcher(Protocol):

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:
        ...
```

Đây là abstraction quan trọng nhất.

Application không biết:

```text
primp
proxy
TLS
HTTP/2
browser impersonation
retry
```

---

# 7. PrimpTransport

Đây là nơi duy nhất chúng ta chạm vào `primp`.

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
    ) -> FetchResponse:

        response = await self.client.get(
            request.url,
            headers=request.headers,
            params=request.params,
            timeout=request.timeout,
        )

        return FetchResponse(
            status_code=response.status_code,
            url=str(response.url),
            headers=dict(response.headers),
            content=response.content,
        )
```

`primp.AsyncClient` hiện được PyPI tài liệu hóa với API async như trên; browser impersonation được cấu hình khi tạo client. ([PyPI][1])

---

# 8. Một nguyên tắc cực kỳ quan trọng

Không viết:

```python
class ProductionFetcher:

    async def get(...):

        client = primp.AsyncClient(...)
```

mỗi request.

Sai architecture:

```text
request
 ↓
create client
 ↓
HTTP
 ↓
close client
```

Thay vào đó:

```text
Application startup
       ↓
create BrowserContext
       ↓
create AsyncClient
       ↓
reuse
       ↓
many requests
       ↓
Application shutdown
       ↓
close
```

Đây chính là lý do chúng ta học **Session / Connection Reuse** từ Buổi 16.

---

# 9. BrowserContext

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:

    name: str

    impersonate: str

    os: str | None = None
```

Ví dụ:

```python
chrome = BrowserProfile(
    name="chrome_windows",
    impersonate="chrome_146",
    os="windows",
)
```

`chrome_146` và các browser/OS profile tương ứng là các profile được PyPI hiện tại liệt kê. ([PyPI][1])

---

# 10. ProxyConfig

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ProxyConfig:

    name: str

    url: str
```

Ví dụ:

```python
proxy = ProxyConfig(
    name="proxy-01",
    url="http://user:password@proxy.example.com:8080",
)
```

---

# 11. BrowserContext

```python
@dataclass(frozen=True)
class BrowserContext:

    name: str

    profile: BrowserProfile

    proxy: ProxyConfig | None

    transport: PrimpTransport
```

Một context đại diện cho:

```text
Chrome 146
Windows
Proxy A
AsyncClient A
```

---

# 12. Tại sao context là đơn vị quan trọng?

Ta không muốn:

```text
request 1
Chrome + Proxy A

request 2
Firefox + Proxy B

request 3
Safari + Proxy C
```

một cách ngẫu nhiên.

Thay vào đó:

```text
Context A
Chrome + Windows + Proxy A
      ↓
client A

Context B
Firefox + Linux + Proxy B
      ↓
client B
```

và strategy chọn context.

---

# 13. RetryPolicy

Ta dùng phiên bản đã học:

```python
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class RetryDecision:

    retry: bool

    delay: float = 0.0

    reason: str = ""

    change_proxy: bool = False

    change_browser: bool = False


@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    jitter: bool = True

    retryable_statuses: frozenset[int] = (
        frozenset({
            408,
            429,
            500,
            502,
            503,
            504,
        })
    )

    def calculate_delay(
        self,
        attempt: int,
        retry_after: float | None = None,
    ) -> float:

        if retry_after is not None:
            return min(
                retry_after,
                self.max_delay,
            )

        delay = min(
            self.base_delay
            * (2 ** (attempt - 1)),
            self.max_delay,
        )

        if self.jitter:
            return random.uniform(
                0,
                delay,
            )

        return delay
```

---

# 14. Error Model

```python
from enum import Enum
from dataclasses import dataclass


class ErrorCategory(str, Enum):

    TIMEOUT = "timeout"

    CONNECTION = "connection"

    TLS = "tls"

    PROXY = "proxy"

    HTTP_403 = "http_403"

    HTTP_404 = "http_404"

    HTTP_429 = "http_429"

    HTTP_5XX = "http_5xx"

    INVALID_REQUEST = "invalid_request"

    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FetchError:

    category: ErrorCategory

    message: str

    status_code: int | None = None

    retryable: bool = False

    proxy_related: bool = False
```

---

# 15. ErrorClassifier

Interface:

```python
from typing import Protocol


class ErrorClassifier(Protocol):

    def classify(
        self,
        exc: Exception,
    ) -> FetchError:
        ...

    def classify_response(
        self,
        response: FetchResponse,
    ) -> FetchError | None:
        ...
```

Implementation:

```python
class BasicErrorClassifier:

    def classify(
        self,
        exc: Exception,
    ) -> FetchError:

        if isinstance(
            exc,
            TimeoutError,
        ):
            return FetchError(
                category=ErrorCategory.TIMEOUT,
                message=str(exc),
                retryable=True,
            )

        return FetchError(
            category=ErrorCategory.UNKNOWN,
            message=str(exc),
            retryable=False,
        )

    def classify_response(
        self,
        response: FetchResponse,
    ) -> FetchError | None:

        status = response.status_code

        if status == 403:
            return FetchError(
                category=ErrorCategory.HTTP_403,
                message="Forbidden",
                status_code=status,
                retryable=False,
            )

        if status == 404:
            return FetchError(
                category=ErrorCategory.HTTP_404,
                message="Not Found",
                status_code=status,
                retryable=False,
            )

        if status == 429:
            return FetchError(
                category=ErrorCategory.HTTP_429,
                message="Too Many Requests",
                status_code=status,
                retryable=True,
            )

        if 500 <= status <= 599:
            return FetchError(
                category=ErrorCategory.HTTP_5XX,
                message="Server error",
                status_code=status,
                retryable=True,
            )

        return None
```

---

# 16. Điểm cần lưu ý về primp exceptions

Không nên tự đoán các class exception nội bộ của phiên bản `primp` đang cài.

Ở production, ta sẽ làm:

```text
primp exception
      ↓
PrimpTransport
      ↓
classifier
      ↓
FetchError
```

Thay vì để:

```text
primp.SomeException
```

lọt ra Application.

PyPI hiện có riêng phần documentation cho error handling, nhưng API cụ thể nên được khóa theo version mà project pin trong `pyproject.toml`. ([PyPI][1])

---

# 17. RateLimiter

Giữ component đã học:

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

                wait = (
                    self._next_allowed
                    - now
                )

                self._next_allowed += (
                    self.interval
                )

            else:

                wait = 0

                self._next_allowed = (
                    now + self.interval
                )

        if wait > 0:
            await asyncio.sleep(wait)
```

---

# 18. Semaphore

Semaphore rất đơn giản:

```python
semaphore = asyncio.Semaphore(10)
```

Trong request:

```python
async with semaphore:
    response = await transport.send(
        request
    )
```

Ý nghĩa:

```text
RateLimiter
    =
bao nhiêu request / giây

Semaphore
    =
bao nhiêu request đang chạy đồng thời
```

Hai thứ không thay thế nhau.

---

# 19. BrowserContextStrategy

```python
from typing import Protocol


class BrowserContextStrategy(Protocol):

    def select(self) -> BrowserContext:
        ...

    def mark_success(
        self,
        context: BrowserContext,
    ) -> None:
        ...

    def mark_failure(
        self,
        context: BrowserContext,
    ) -> None:
        ...
```

---

# 20. Round-robin strategy

```python
class RoundRobinBrowserStrategy:

    def __init__(
        self,
        contexts: list[BrowserContext],
    ):
        if not contexts:
            raise ValueError(
                "No browser contexts"
            )

        self.contexts = contexts
        self.index = 0

    def select(self) -> BrowserContext:

        context = self.contexts[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % len(self.contexts)

        return context

    def mark_success(
        self,
        context,
    ):
        pass

    def mark_failure(
        self,
        context,
    ):
        pass
```

Production version có thể thay bằng health-aware strategy.

---

# 21. Observability

Ta dùng logger:

```python
import logging


logger = logging.getLogger(
    "crawler.fetcher"
)
```

Một helper:

```python
def log_success(
    *,
    request_id: str,
    attempt: int,
    status: int,
    elapsed: float,
):
    logger.info(
        "event=fetch.success "
        "request_id=%s "
        "attempt=%d "
        "status=%d "
        "elapsed=%.3f",
        request_id,
        attempt,
        status,
        elapsed,
    )
```

---

# 22. Bây giờ mới đến ProductionFetcher

Đây là class quan trọng nhất.

Nhưng chú ý:

> Nó **orchestrate**, không tự implement tất cả logic.

```python
class ProductionFetcher:

    def __init__(
        self,
        *,
        context_strategy,
        retry_policy,
        error_classifier,
        rate_limiter,
        semaphore,
    ):
        self.context_strategy = (
            context_strategy
        )

        self.retry_policy = retry_policy

        self.error_classifier = (
            error_classifier
        )

        self.rate_limiter = (
            rate_limiter
        )

        self.semaphore = semaphore
```

---

# 23. get()

```python
async def get(
    self,
    request: FetchRequest,
) -> FetchResponse:

    request_id = uuid4().hex[:12]

    for attempt in range(
        1,
        self.retry_policy.max_attempts + 1,
    ):

        context = (
            self.context_strategy.select()
        )

        started = time.perf_counter()

        logger.info(
            "event=fetch.start "
            "request_id=%s "
            "attempt=%d "
            "url=%s "
            "context=%s",
            request_id,
            attempt,
            request.url,
            context.name,
        )

        try:

            await self.rate_limiter.acquire()

            async with self.semaphore:

                response = (
                    await context.transport.send(
                        request
                    )
                )

        except Exception as exc:

            error = (
                self.error_classifier.classify(
                    exc
                )
            )

            elapsed = (
                time.perf_counter()
                - started
            )

            if not error.retryable:

                logger.error(
                    "event=fetch.failed "
                    "request_id=%s "
                    "error=%s "
                    "elapsed=%.3f",
                    request_id,
                    error.category.value,
                    elapsed,
                )

                raise

            if error.proxy_related:

                self.context_strategy.mark_failure(
                    context
                )

            if (
                attempt
                >= self.retry_policy.max_attempts
            ):

                logger.error(
                    "event=fetch.failed "
                    "request_id=%s "
                    "error=%s",
                    request_id,
                    error.category.value,
                )

                raise

            delay = (
                self.retry_policy.calculate_delay(
                    attempt
                )
            )

            logger.warning(
                "event=fetch.retry "
                "request_id=%s "
                "attempt=%d "
                "error=%s "
                "delay=%.3f",
                request_id,
                attempt,
                error.category.value,
                delay,
            )

            await asyncio.sleep(delay)

            continue
```

---

# 24. Xử lý HTTP response

Sau phần exception:

```python
        error = (
            self.error_classifier
            .classify_response(response)
        )
```

Nếu không có error:

```python
        if error is None:

            elapsed = (
                time.perf_counter()
                - started
            )

            self.context_strategy.mark_success(
                context
            )

            logger.info(
                "event=fetch.success "
                "request_id=%s "
                "attempt=%d "
                "status=%d "
                "elapsed=%.3f",
                request_id,
                attempt,
                response.status_code,
                elapsed,
            )

            return response
```

---

# 25. HTTP error

Nếu có error:

```python
        if (
            not error.retryable
            or attempt
            >= self.retry_policy.max_attempts
        ):

            logger.error(
                "event=fetch.failed "
                "request_id=%s "
                "attempt=%d "
                "status=%s "
                "error=%s",
                request_id,
                attempt,
                error.status_code,
                error.category.value,
            )

            return response
```

Đây là một điểm rất quan trọng:

### 404 không phải Exception

Ta không:

```python
raise Exception("404")
```

một cách máy móc.

Fetcher có thể trả:

```text
FetchResponse(status_code=404)
```

để Application quyết định 404 có ý nghĩa gì.

---

# 26. Retry HTTP error

```python
        delay = (
            self.retry_policy.calculate_delay(
                attempt
            )
        )

        if error.proxy_related:
            self.context_strategy.mark_failure(
                context
            )

        logger.warning(
            "event=fetch.retry "
            "request_id=%s "
            "attempt=%d "
            "status=%d "
            "error=%s "
            "delay=%.3f",
            request_id,
            attempt,
            response.status_code,
            error.category.value,
            delay,
        )

        await asyncio.sleep(delay)
```

Sau đó:

```python
        continue
```

---

# 27. Full ProductionFetcher

Ghép lại:

```python
import asyncio
import logging
import time
from uuid import uuid4


logger = logging.getLogger(
    "crawler.fetcher"
)


class ProductionFetcher:

    def __init__(
        self,
        *,
        context_strategy,
        retry_policy,
        error_classifier,
        rate_limiter,
        semaphore,
    ):
        self.context_strategy = (
            context_strategy
        )

        self.retry_policy = retry_policy

        self.error_classifier = (
            error_classifier
        )

        self.rate_limiter = (
            rate_limiter
        )

        self.semaphore = semaphore

    async def get(
        self,
        request: FetchRequest,
    ) -> FetchResponse:

        request_id = uuid4().hex[:12]

        for attempt in range(
            1,
            self.retry_policy.max_attempts + 1,
        ):

            context = (
                self.context_strategy.select()
            )

            started = time.perf_counter()

            logger.info(
                "event=fetch.start "
                "request_id=%s "
                "attempt=%d "
                "url=%s "
                "context=%s",
                request_id,
                attempt,
                request.url,
                context.name,
            )

            try:

                await (
                    self.rate_limiter.acquire()
                )

                async with self.semaphore:

                    response = (
                        await context.transport.send(
                            request
                        )
                    )

            except Exception as exc:

                error = (
                    self.error_classifier.classify(
                        exc
                    )
                )

                elapsed = (
                    time.perf_counter()
                    - started
                )

                if not error.retryable:

                    logger.error(
                        "event=fetch.failed "
                        "request_id=%s "
                        "error=%s "
                        "elapsed=%.3f",
                        request_id,
                        error.category.value,
                        elapsed,
                    )

                    raise

                self.context_strategy.mark_failure(
                    context
                )

                if (
                    attempt
                    >= self.retry_policy.max_attempts
                ):
                    raise

                delay = (
                    self.retry_policy.calculate_delay(
                        attempt
                    )
                )

                logger.warning(
                    "event=fetch.retry "
                    "request_id=%s "
                    "attempt=%d "
                    "error=%s "
                    "delay=%.3f",
                    request_id,
                    attempt,
                    error.category.value,
                    delay,
                )

                await asyncio.sleep(delay)

                continue

            error = (
                self.error_classifier
                .classify_response(response)
            )

            if error is None:

                elapsed = (
                    time.perf_counter()
                    - started
                )

                self.context_strategy.mark_success(
                    context
                )

                logger.info(
                    "event=fetch.success "
                    "request_id=%s "
                    "attempt=%d "
                    "status=%d "
                    "elapsed=%.3f",
                    request_id,
                    attempt,
                    response.status_code,
                    elapsed,
                )

                return response

            if (
                not error.retryable
                or attempt
                >= self.retry_policy.max_attempts
            ):

                logger.error(
                    "event=fetch.failed "
                    "request_id=%s "
                    "attempt=%d "
                    "status=%s "
                    "error=%s",
                    request_id,
                    attempt,
                    error.status_code,
                    error.category.value,
                )

                return response

            delay = (
                self.retry_policy.calculate_delay(
                    attempt
                )
            )

            logger.warning(
                "event=fetch.retry "
                "request_id=%s "
                "attempt=%d "
                "status=%d "
                "error=%s "
                "delay=%.3f",
                request_id,
                attempt,
                response.status_code,
                error.category.value,
                delay,
            )

            await asyncio.sleep(delay)

        raise RuntimeError(
            "Fetcher exhausted retry loop"
        )
```

Đây là phiên bản **học tập/production-oriented skeleton**. Trong hệ thống thật, ta còn có thể tách `RetryExecutor` riêng để giảm trách nhiệm của `ProductionFetcher`.

---

# 28. Nhưng có một vấn đề kiến trúc

Class trên đã bắt đầu hơi lớn:

```text
ProductionFetcher
├── retry
├── classification
├── logging
├── rate limit
├── semaphore
└── context strategy
```

Đây là lúc phải nhớ nguyên tắc:

> **Production code không có nghĩa là một class phải chứa mọi tính năng.**

Ta có thể giữ `ProductionFetcher` là orchestrator và đưa retry execution ra ngoài.

---

# 29. Phiên bản sạch hơn

```text
ProductionFetcher
      │
      ├── AttemptExecutor
      │       ├── RateLimiter
      │       ├── Semaphore
      │       └── Transport
      │
      ├── RetryPolicy
      ├── ErrorClassifier
      └── ContextStrategy
```

Khi đó:

```text
ProductionFetcher
```

chỉ điều phối.

---

# 30. AttemptExecutor

```python
class AttemptExecutor:

    def __init__(
        self,
        rate_limiter,
        semaphore,
    ):
        self.rate_limiter = rate_limiter
        self.semaphore = semaphore

    async def execute(
        self,
        transport,
        request,
    ):

        await self.rate_limiter.acquire()

        async with self.semaphore:

            return await transport.send(
                request
            )
```

Rất dễ test.

---

# 31. ProductionFetcher lúc này

```python
class ProductionFetcher:

    def __init__(
        self,
        context_strategy,
        attempt_executor,
        retry_policy,
        error_classifier,
    ):
        self.context_strategy = (
            context_strategy
        )

        self.attempt_executor = (
            attempt_executor
        )

        self.retry_policy = retry_policy

        self.error_classifier = (
            error_classifier
        )
```

Nó trở thành orchestrator thực sự.

---

# 32. Composition Root

Đây là nơi tất cả dependency được lắp ráp.

Ví dụ:

```python
import asyncio
import primp


async def build_fetcher():

    client = primp.AsyncClient(
        impersonate="chrome_146",
    )

    transport = PrimpTransport(
        client
    )

    context = BrowserContext(
        name="chrome_windows",
        profile=BrowserProfile(
            name="chrome_windows",
            impersonate="chrome_146",
            os="windows",
        ),
        proxy=None,
        transport=transport,
    )

    strategy = (
        RoundRobinBrowserStrategy(
            [context]
        )
    )

    retry_policy = RetryPolicy(
        max_attempts=3,
        base_delay=1.0,
        max_delay=20.0,
    )

    classifier = (
        BasicErrorClassifier()
    )

    limiter = RateLimiter(
        requests_per_second=2
    )

    semaphore = asyncio.Semaphore(
        5
    )

    attempt_executor = (
        AttemptExecutor(
            rate_limiter=limiter,
            semaphore=semaphore,
        )
    )

    return ProductionFetcher(
        context_strategy=strategy,
        attempt_executor=attempt_executor,
        retry_policy=retry_policy,
        error_classifier=classifier,
    )
```

---

# 33. Client lifecycle

Đây là chỗ cần đặc biệt chú ý.

Nếu `build_fetcher()` tạo:

```python
client = primp.AsyncClient(...)
```

thì application phải đảm bảo client được đóng khi shutdown.

Ví dụ conceptual:

```python
async with primp.AsyncClient(
    impersonate="chrome_146"
) as client:

    ...
```

PyPI chính thức cũng minh họa `AsyncClient` bằng `async with`. ([PyPI][1])

---

# 34. Application lifecycle

Ta muốn:

```text
Application startup
        ↓
Composition Root
        ↓
Create AsyncClient(s)
        ↓
Create Fetcher
        ↓
Crawler runs
        ↓
Crawler stops
        ↓
Close clients
```

Không:

```text
every request
 ↓
create client
 ↓
close client
```

---

# 35. Crawler Use Case

Application cuối cùng cực kỳ đơn giản:

```python
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

Notice:

**Không có `primp` ở đây.**

---

# 36. Đây mới là Dependency Inversion

```text
Sai:

CrawlChapter
     ↓
PrimpFetcher
     ↓
primp
```

Đúng:

```text
CrawlChapter
     ↓
Fetcher Protocol
     ↑
PrimpFetcher
     ↓
primp
```

Application phụ thuộc abstraction.

Infrastructure phụ thuộc implementation.

---

# 37. FakeFetcher

Nhờ vậy test rất dễ:

```python
class FakeFetcher:

    def __init__(
        self,
        response: FetchResponse,
    ):
        self.response = response

    async def get(
        self,
        request: FetchRequest,
    ):
        return self.response
```

Test:

```python
async def test_crawl_chapter():

    fetcher = FakeFetcher(
        FetchResponse(
            status_code=200,
            url="https://example.com/ch1",
            headers={},
            content=b"Hello",
        )
    )

    use_case = CrawlChapter(
        fetcher
    )

    result = await use_case.execute(
        "https://example.com/ch1"
    )

    assert result == "Hello"
```

Không cần:

```text
Internet
primp
proxy
TLS
browser
```

---

# 38. FakeTransport test retry

Đây mới là test Infrastructure:

```python
class FakeTransport:

    def __init__(
        self,
        responses,
    ):
        self.responses = list(
            responses
        )

        self.calls = 0

    async def send(
        self,
        request,
    ):

        self.calls += 1

        response = self.responses.pop(
            0
        )

        return response
```

Test:

```python
transport = FakeTransport([
    FakePrimpResponse(503),
    FakePrimpResponse(503),
    FakePrimpResponse(200),
])
```

Kỳ vọng:

```text
call 1 → 503
call 2 → 503
call 3 → 200
```

---

# 39. Test retry count

```python
assert transport.calls == 3
```

Đây là test cực kỳ quan trọng.

Nó chứng minh:

```text
RetryPolicy
+
Fetcher
```

đang phối hợp đúng.

---

# 40. Test 404

```python
transport = FakeTransport([
    FakePrimpResponse(404),
])
```

Kỳ vọng:

```python
assert transport.calls == 1
```

Không được:

```text
404
 ↓
retry
 ↓
retry
```

---

# 41. Test 503

```python
transport = FakeTransport([
    FakePrimpResponse(503),
    FakePrimpResponse(200),
])
```

Kỳ vọng:

```python
assert transport.calls == 2
```

---

# 42. Test timeout

Fake transport:

```python
class TimeoutTransport:

    async def send(
        self,
        request,
    ):
        raise TimeoutError(
            "request timeout"
        )
```

Kỳ vọng:

```text
attempt 1
 ↓
timeout
 ↓
retry
 ↓
attempt 2
```

---

# 43. Test proxy failure

Nếu:

```text
Context A
Proxy A
```

thất bại:

```text
Proxy A
 ↓
mark_failure
 ↓
Context B
 ↓
retry
```

Ta có thể assert:

```python
assert strategy.failed_contexts == [
    "context-a"
]
```

Đây là test quan trọng hơn test HTTP đơn thuần.

---

# 44. Test concurrency

Giả sử:

```python
semaphore = asyncio.Semaphore(2)
```

10 URL:

```python
await asyncio.gather(
    *(fetcher.get(request)
      for request in requests)
)
```

Không được có quá:

```text
2 active requests
```

Test bằng counter:

```python
active = 0
maximum = 0
```

Mỗi request:

```python
active += 1

maximum = max(
    maximum,
    active,
)
```

sau request:

```python
active -= 1
```

Kỳ vọng:

```python
assert maximum <= 2
```

---

# 45. Test RateLimiter

Ví dụ:

```python
RateLimiter(
    requests_per_second=2
)
```

thì khoảng cách giữa các request được pacing.

Lưu ý:

> RateLimiter không phải một cơ chế đảm bảo chính xác tuyệt đối về throughput trong mọi scheduler/cluster.

Nó là client-side pacing.

Production distributed crawler có thể cần rate limit theo:

```text
source
host
domain
proxy
worker
```

---

# 46. Retry + RateLimiter

Đây là lỗi rất dễ mắc.

Sai:

```text
request
 ↓
rate limiter
 ↓
retry 1
retry 2
retry 3
```

RateLimiter chỉ áp dụng lần đầu.

Đúng:

```text
attempt 1
 ↓
RateLimiter
 ↓
HTTP
 ↓
503
 ↓
backoff

attempt 2
 ↓
RateLimiter
 ↓
HTTP
```

Mỗi retry là **một request mới**.

---

# 47. Retry + Semaphore

Cũng tương tự.

Sai:

```text
acquire semaphore
   ↓
request
   ↓
sleep retry
   ↓
request
   ↓
release
```

Như vậy semaphore bị giữ trong lúc ngủ.

Đúng:

```text
acquire
 ↓
HTTP
 ↓
release
 ↓
backoff
 ↓
acquire
 ↓
HTTP
 ↓
release
```

Semaphore chỉ bảo vệ **active HTTP operation**.

---

# 48. Retry + Proxy

Sai:

```text
select Proxy A
     ↓
retry
     ↓
Proxy A
     ↓
retry
     ↓
Proxy A
```

Nếu Proxy A chết thì vô nghĩa.

Tốt hơn:

```text
attempt 1
 ↓
Context A
 ↓
failure
 ↓
mark A
 ↓
backoff

attempt 2
 ↓
Context B
```

Đây chính là lý do strategy phải nằm ngoài RetryPolicy.

---

# 49. Retry + Browser Profile

Không nên mặc định:

```text
mọi lỗi
 ↓
đổi browser
```

Ví dụ:

```text
500
```

chỉ đơn giản là server error.

Không cần đổi:

```text
Chrome → Firefox
```

Trong khi:

```text
Proxy connection failure
```

có thể cần:

```text
Proxy A → Proxy B
```

Cho nên:

```text
ErrorClassifier
      ↓
ErrorCategory
      ↓
RetryPolicy
      ↓
RetryDecision
```

mới quyết định action.

---

# 50. Production Fetcher hoàn chỉnh về mặt kiến trúc

Ta có:

```text
                     FetchRequest
                          │
                          ▼
                  ProductionFetcher
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
 ContextStrategy    RetryPolicy      Observability
          │               │
          ▼               ▼
 BrowserContext      RetryDecision
          │
    ┌─────┴──────┐
    ▼            ▼
 Browser       Proxy
 Profile
    │            │
    └─────┬──────┘
          ▼
    PrimpTransport
          │
          ▼
   AsyncClient
          │
          ▼
       HTTP
          │
          ▼
   FetchResponse
```

---

# 51. Clean Architecture cuối cùng

Toàn bộ Novel Crawler:

```text
┌──────────────────────────────────────────┐
│              Presentation                │
│          CLI / PySide6 / Flet            │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│              Application                 │
│                                          │
│ CrawlNovel                               │
│ CrawlChapter                             │
│ Fetcher Protocol                         │
└────────────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────┐
│                 Domain                  │
│                                          │
│ Novel                                    │
│ Chapter                                  │
│ CrawlTask                                │
│ Value Objects                            │
└──────────────────────────────────────────┘


┌──────────────────────────────────────────┐
│             Infrastructure               │
│                                          │
│ PrimpFetcher                             │
│ PrimpTransport                           │
│ ProxyStrategy                            │
│ BrowserStrategy                          │
│ RetryPolicy                              │
│ RateLimiter                              │
│ ErrorClassifier                          │
│ Logging                                  │
│ SQLite Repository                        │
└──────────────────────────────────────────┘
```

Dependency direction:

```text
Presentation
      ↓
Application
      ↓
Domain

Infrastructure
      ↑
implements Application ports
```

---

# 52. Dòng dữ liệu của Novel Crawler

Đây là flow cuối cùng chúng ta đã xây suốt Part V:

```text
Chapter URL
     │
     ▼
FetchRequest
     │
     ▼
Fetcher Port
     │
     ▼
ProductionFetcher
     │
     ├── Request ID
     │
     ├── BrowserContextStrategy
     │
     ├── RateLimiter
     │
     ├── Semaphore
     │
     └── RetryPolicy
             │
             ▼
       BrowserContext
             │
       ┌─────┴─────┐
       ▼           ▼
    Browser      Proxy
    Profile
       │           │
       └─────┬─────┘
             ▼
       PrimpTransport
             │
             ▼
      primp.AsyncClient
             │
             ▼
           HTTP
             │
      ┌──────┴──────┐
      ▼             ▼
   Response       Exception
      │             │
      │             ▼
      │       ErrorClassifier
      │             │
      └──────► FetchError
                    │
                    ▼
               RetryPolicy
                    │
             ┌──────┴──────┐
             ▼             ▼
           Retry          Stop
             │
             ▼
          Response
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

---

# 53. Một thay đổi rất quan trọng cho Production

Ở các buổi trước ta dùng:

```python
response.text
```

và fallback UTF-8.

Trong production crawler, nên ưu tiên giữ:

```python
content: bytes
```

ở Fetcher.

Parser hoặc response adapter có thể xử lý encoding phù hợp.

Điều này tránh việc HTTP layer tự ý biến dữ liệu thành text quá sớm.

---

# 54. Fetcher không phải Parser

Đây là boundary phải giữ rất rõ:

```text
Fetcher
    ↓
"HTTP request thành công chưa?"
```

Parser:

```text
HTML
 ↓
"Đây có phải chapter hợp lệ không?"
```

Ví dụ:

```text
HTTP 200
 ↓
FetchResponse
 ↓
Parser
 ↓
No chapter-content
```

Không nên để Fetcher biến thành:

```text
if "captcha" in response.text:
    ...
```

đó là content validation/domain/source concern.

---

# 55. Fetcher không phải Repository

Fetcher:

```text
URL
 ↓
HTTP
 ↓
Response
```

Repository:

```text
Chapter
 ↓
SQLite
```

Không:

```python
class ProductionFetcher:

    async def get(...):
        ...
        await chapter_repository.save(...)
```

Nếu làm vậy:

```text
Fetcher
 ↓
HTTP
 ↓
Parser
 ↓
Domain
 ↓
SQLite
```

tất cả thành một God Object.

---

# 56. Fetcher không phải Crawler

Fetcher:

```text
GET URL
```

Crawler:

```text
Listing
 ↓
Novel
 ↓
Chapter URLs
 ↓
Fetch
 ↓
Parse
 ↓
Save
```

Fetcher chỉ là **hạ tầng HTTP**.

---

# 57. Production checklist

Trước khi gọi Fetcher là production-ready, kiểm tra:

```text
[✓] Request validation
[✓] Response model
[✓] Fetcher interface
[✓] Long-lived AsyncClient
[✓] Browser impersonation
[✓] Browser context
[✓] Proxy strategy
[✓] Retry policy
[✓] Error classification
[✓] Exponential backoff
[✓] Jitter
[✓] Rate limiting
[✓] Semaphore
[✓] Structured logging
[✓] Request ID
[✓] Timeout
[✓] Fake transport
[✓] Retry tests
[✓] 404 tests
[✓] 503 tests
[✓] Timeout tests
[✓] Concurrency tests
[✓] Graceful client shutdown
```

---

# 58. Những thứ **chưa** nên nhét vào Fetcher

Không vì gọi là "Production" mà thêm tất cả:

```text
❌ EventBus
❌ Kafka
❌ Redis
❌ Celery
❌ Circuit Breaker
❌ Distributed tracing
❌ Prometheus
❌ CAPTCHA solver
❌ Parser
❌ SQLite
❌ Domain Event
```

Các thứ này có thể xuất hiện trong **toàn hệ thống**, nhưng không thuộc trách nhiệm trực tiếp của Fetcher.

---

# 59. Part V — hoàn thành

Ta đã đi hết:

```text
PHẦN V — NOVEL CRAWLER

41. Request Model              ✅
42. Response Model             ✅
43. Fetcher Interface          ✅
44. PrimpFetcher               ✅
45. Retry Policy               ✅
46. Proxy Strategy             ✅
47. Browser Profile Strategy   ✅
48. Error Classification       ✅
49. Observability / Logging    ✅
50. Production Fetcher        ✅
```

Và kiến trúc cuối cùng là:

```text
                    Novel Crawler
                          │
                          ▼
                     Fetcher Port
                          │
                          ▼
                  ProductionFetcher
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   RetryPolicy       RateLimiter       Semaphore
        │
        ▼
 ErrorClassifier
        │
        ▼
    FetchError
        │
        ▼
 BrowserContextStrategy
        │
        ▼
 BrowserContext
    ┌───┴────┐
    ▼        ▼
 Browser   Proxy
 Profile
    │        │
    └───┬────┘
        ▼
 PrimpTransport
        │
        ▼
primp.AsyncClient
        │
        ▼
      HTTP
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

**Đây là điểm kết thúc hợp lý của khóa `primp` hiện tại:** từ việc học API HTTP ban đầu, chúng ta đã đi đến một **Infrastructure HTTP layer độc lập với Application**, có retry/proxy/browser context/rate-limit/concurrency/error classification/observability và có thể thay `primp` bằng implementation khác mà không phải sửa Use Case.

Bản `primp` hiện tại là **2.0.1**, phát hành ngày 13/09/2026; vì vậy khi bạn triển khai project thật, nên pin version thay vì để dependency trôi tự do. ([PyPI][1])

[1]: https://pypi.org/project/primp/2.0.1/?utm_source=chatgpt.com "primp · PyPI"
