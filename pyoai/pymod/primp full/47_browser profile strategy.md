# Buổi 47 — Browser Profile Strategy

Ở Buổi 46, chúng ta đã có:

```text
FetchRequest
     ↓
PrimpFetcher
     ↓
ProxyStrategy
     ↓
ProxyContext
     ↓
PrimpTransport
     ↓
primp.AsyncClient
```

Hôm nay ta thêm **Browser Profile Strategy**.

Mục tiêu cuối cùng là không quản lý riêng lẻ:

```text
Proxy
Browser
OS
Client
```

mà gom chúng thành một **Browser Context ổn định**:

```text
BrowserProfile
      +
OS
      +
Proxy
      +
AsyncClient
      ↓
BrowserContext
```

---

# 1. Browser Profile là gì?

Trong `primp`, tham số:

```python
primp.AsyncClient(
    impersonate="chrome_146"
)
```

không chỉ đơn giản là đổi:

```http
User-Agent
```

Mà profile impersonation nhằm mô phỏng các đặc điểm HTTP/TLS/browser tương ứng. `primp` hiện hỗ trợ nhiều profile Chrome, Firefox, Safari, Edge, Opera và các OS profile.

Vì vậy ta không nên coi:

```python
impersonate="chrome_146"
```

là một User-Agent string.

Nó là:

```text
Browser Profile
```

---

# 2. Tại sao cần Browser Profile Strategy?

Giả sử chúng ta có:

```text
chrome_146
chrome_147
firefox_151
safari_26
```

Không nên:

```text
request 1 → Chrome
request 2 → Firefox
request 3 → Safari
request 4 → Chrome
```

một cách ngẫu nhiên.

Ta muốn:

```text
Context A
    Chrome 146
    Proxy A
    Client A

Context B
    Firefox 151
    Proxy B
    Client B

Context C
    Safari 26
    Proxy C
    Client C
```

Sau đó strategy chọn **context**.

---

# 3. BrowserProfile Model

Tạo:

```text id="xv7p1m"
infrastructure/http/browser_profile.py
```

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

Firefox:

```python
firefox = BrowserProfile(
    name="firefox_linux",
    impersonate="firefox_151",
    os="linux",
)
```

---

# 4. Tại sao có `name`?

Không nên dùng:

```python
profile.name == profile.impersonate
```

một cách bắt buộc.

Vì:

```text
name
```

là identity của application:

```text
chrome_windows
```

còn:

```text
impersonate
```

là configuration cho `primp`:

```text
chrome_146
```

Tách hai khái niệm này giúp Infrastructure dễ thay đổi hơn.

---

# 5. BrowserContext

Bây giờ kết hợp Browser + Proxy + Transport.

```python
from dataclasses import dataclass

from crawler.infrastructure.http.browser_profile import (
    BrowserProfile,
)

from crawler.infrastructure.http.proxy import (
    ProxyConfig,
)

from crawler.infrastructure.http.primp_transport import (
    PrimpTransport,
)


@dataclass(frozen=True)
class BrowserContext:

    profile: BrowserProfile

    proxy: ProxyConfig | None

    transport: PrimpTransport
```

Một context:

```text
BrowserContext
├── Chrome 146
├── Windows
├── Proxy A
└── AsyncClient A
```

---

# 6. Tại sao Context là abstraction quan trọng?

Thay vì:

```text
ProxyStrategy
BrowserStrategy
ClientStrategy
```

độc lập rồi phải đồng bộ:

```text
Chrome
   +
Proxy A
   +
Client ?
```

ta tạo:

```text
BrowserContext
```

để giữ các thành phần liên quan với nhau.

Ví dụ:

```text
Context A
    Browser = Chrome 146
    OS = Windows
    Proxy = A
    Client = A
```

Không xảy ra tình trạng:

```text
Chrome context
    ↓
nhưng lại dùng Client của Firefox
```

---

# 7. Context Pool

```python
class BrowserContextPool:

    def __init__(
        self,
        contexts: list[BrowserContext],
    ):
        if not contexts:
            raise ValueError(
                "Browser context pool cannot be empty"
            )

        self._contexts = list(contexts)
```

Ta cần:

```python
def all(self) -> list[BrowserContext]:
    return list(self._contexts)
```

---

# 8. Browser Profile Strategy

Protocol:

```python
from typing import Protocol


class BrowserProfileStrategy(Protocol):

    def select(
        self,
    ) -> BrowserContext:
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

Ta đang quản lý **context**, không chỉ browser profile.

---

# 9. Round-Robin Strategy

```python
class RoundRobinBrowserStrategy:

    def __init__(
        self,
        pool: BrowserContextPool,
    ):
        self.pool = pool
        self.index = 0

    def select(
        self,
    ) -> BrowserContext:

        contexts = self.pool.all()

        context = contexts[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % len(contexts)

        return context

    def mark_success(
        self,
        context: BrowserContext,
    ) -> None:
        pass

    def mark_failure(
        self,
        context: BrowserContext,
    ) -> None:
        pass
```

Kết quả:

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

# 10. Nhưng Browser Profile cũng cần health

Ví dụ:

```text
Context A
Chrome 146
Proxy A

Context B
Firefox 151
Proxy B

Context C
Safari 26
Proxy C
```

Nếu:

```text
Context A
 ↓
503
 ↓
503
 ↓
503
```

ta không muốn tiếp tục dùng A.

Ta cần:

```text
ContextState
```

---

# 11. ContextState

```python
from dataclasses import dataclass


@dataclass
class ContextState:

    failures: int = 0

    successes: int = 0

    available: bool = True
```

---

# 12. Health-aware strategy

```python
class HealthAwareBrowserStrategy:

    def __init__(
        self,
        pool: BrowserContextPool,
        failure_threshold: int = 3,
    ):
        self.contexts = pool.all()

        self.failure_threshold = (
            failure_threshold
        )

        self.states = {
            id(context): ContextState()
            for context in self.contexts
        }

        self.index = 0
```

---

# 13. Select

```python
def select(
    self,
) -> BrowserContext:

    total = len(self.contexts)

    for _ in range(total):

        context = self.contexts[
            self.index
        ]

        self.index = (
            self.index + 1
        ) % total

        state = self.states[
            id(context)
        ]

        if state.available:
            return context

    raise RuntimeError(
        "No healthy browser context"
    )
```

---

# 14. Mark failure

```python
def mark_failure(
    self,
    context: BrowserContext,
) -> None:

    state = self.states[
        id(context)
    ]

    state.failures += 1

    if (
        state.failures
        >= self.failure_threshold
    ):
        state.available = False
```

---

# 15. Mark success

```python
def mark_success(
    self,
    context: BrowserContext,
) -> None:

    state = self.states[
        id(context)
    ]

    state.successes += 1

    state.failures = 0

    state.available = True
```

---

# 16. Nhưng có một vấn đề

Nếu:

```text
Context A
Proxy A
Chrome 146
```

bị lỗi:

```text
Proxy A chết
```

thì có nên đánh dấu:

```text
Chrome 146 = unhealthy
```

không?

**Không nhất thiết.**

Đây là lý do ta phải phân biệt:

```text
Browser health
```

và:

```text
Proxy health
```

Một lỗi proxy không đồng nghĩa Chrome profile có vấn đề.

---

# 17. Đây là lý do Buổi 46 và 47 phải tách abstraction

Ta có:

```text
ProxyStrategy
        │
        ▼
Proxy health

BrowserProfileStrategy
        │
        ▼
Browser health
```

Không nên:

```text
Proxy failure
    ↓
Chrome profile failure
```

một cách tự động.

Sau Buổi 48, Error Classification sẽ cho biết:

```text
ProxyError
Timeout
TLS error
HTTP 429
HTTP 403
HTTP 503
```

rồi quyết định component nào cần bị đánh dấu.

---

# 18. Context thực tế

Ví dụ:

```python
profile = BrowserProfile(
    name="chrome_windows",
    impersonate="chrome_146",
    os="windows",
)

proxy = ProxyConfig(
    url="http://127.0.0.1:8080"
)
```

Client được tạo với browser profile phù hợp:

```python
client = primp.AsyncClient(
    impersonate=profile.impersonate,
)
```

Sau đó:

```python
transport = PrimpTransport(
    client=client
)
```

và:

```python
context = BrowserContext(
    profile=profile,
    proxy=proxy,
    transport=transport,
)
```

**Lưu ý:** exact proxy configuration cần được nối vào cách khởi tạo client theo API `primp` version đang dùng; không nên giả định một `proxy=` request argument nếu API hiện tại không cung cấp nó.

---

# 19. Một Context nên có lifetime

Đây là nguyên tắc rất quan trọng.

Không nên:

```text
request 1
 ↓
create Client
 ↓
request
 ↓
close Client

request 2
 ↓
create Client
 ↓
request
 ↓
close Client
```

Thay vào đó:

```text
BrowserContext
      │
      ▼
AsyncClient
      │
      ├── request 1
      ├── request 2
      ├── request 3
      ├── request 4
      └── ...
```

Sau cùng:

```text
shutdown
   ↓
close AsyncClient
```

Điều này tận dụng connection reuse.

---

# 20. Browser Context = Session Identity

Ta có thể hình dung:

```text
Context A
─────────────────────
Browser: Chrome 146
OS: Windows
Proxy: A
Client: A
─────────────────────
request 1
request 2
request 3
request 4
```

Context B:

```text
Context B
─────────────────────
Browser: Firefox 151
OS: Linux
Proxy: B
Client: B
─────────────────────
request 5
request 6
request 7
```

Đây là cách tổ chức **ổn định** hơn so với random profile cho từng request.

---

# 21. `PrimpFetcher` lúc này thay đổi thế nào?

Ở Buổi 44:

```python
PrimpFetcher(
    transport,
    retry_executor,
    rate_limiter,
    semaphore,
)
```

Sau khi có nhiều context, ta có thể hướng tới:

```python
PrimpFetcher(
    context_strategy,
    retry_policy,
    rate_limiter,
    semaphore,
)
```

Ví dụ:

```python
class PrimpFetcher:

    def __init__(
        self,
        context_strategy,
        retry_policy,
        rate_limiter,
        semaphore,
    ):
        self.context_strategy = (
            context_strategy
        )

        self.retry_policy = retry_policy

        self.rate_limiter = rate_limiter

        self.semaphore = semaphore
```

---

# 22. Fetch flow

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
            self.context_strategy.select()
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

                self.context_strategy.mark_success(
                    context
                )

                return response

            if not self.retry_policy.should_retry(
                attempt=attempt,
                status_code=response.status_code,
            ):
                return response

            self.context_strategy.mark_failure(
                context
            )

            delay = (
                self.retry_policy.calculate_delay(
                    attempt
                )
            )

            await asyncio.sleep(delay)

        except RetryableError:

            self.context_strategy.mark_failure(
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

Đây là skeleton để hiểu kiến trúc; Buổi 48 sẽ làm error classification chính xác hơn.

---

# 23. Retry + Browser Context

Giả sử:

```text
3 contexts
```

Ta có:

```text
attempt 1
    ↓
Context A
    ↓
503
```

retry:

```text
attempt 2
    ↓
Context B
    ↓
503
```

retry:

```text
attempt 3
    ↓
Context C
    ↓
200
```

Như vậy:

```text
Retry
+
Context Strategy
```

hoạt động cùng nhau.

---

# 24. Nhưng đừng random vô hạn

Một anti-pattern:

```python
context = random.choice(contexts)
```

cho **mỗi request**.

Ví dụ:

```text
chapter 1 → Chrome
chapter 2 → Safari
chapter 3 → Firefox
chapter 4 → Chrome
chapter 5 → Safari
```

Điều này không tạo ra một "browser session" ổn định.

Tốt hơn:

```text
worker/session
      ↓
Context A
      ↓
nhiều requests
```

hoặc strategy có chính sách rotation rõ ràng.

---

# 25. Browser Profile Pool nên chứa profile ổn định

Ví dụ:

```python
profiles = [
    BrowserProfile(
        name="chrome_146_windows",
        impersonate="chrome_146",
        os="windows",
    ),
    BrowserProfile(
        name="firefox_151_linux",
        impersonate="firefox_151",
        os="linux",
    ),
]
```

Không nên:

```python
impersonate=random.choice(
    [
        "chrome_146",
        "firefox_151",
        "safari_26",
    ]
)
```

trước mỗi HTTP request.

---

# 26. OS cũng là một phần của persona

Ta không chỉ có:

```text
Chrome
```

mà:

```text
Chrome
+
OS
```

Ví dụ:

```text
Chrome 146
Windows
```

khác về persona so với:

```text
Chrome 146
Linux
```

`primp` hiện cung cấp các OS profile như Windows, Linux, macOS, Android, iOS và random profile theo tài liệu hiện tại.

---

# 27. Một nguyên tắc quan trọng

Đừng tạo persona kiểu:

```text
Browser = Chrome
OS = Linux
Proxy = US
```

rồi nói:

> "Đây chắc chắn là fingerprint hoàn chỉnh của Chrome Linux."

Browser impersonation là một mô phỏng network/browser characteristics, **không phải một trình duyệt thật hoàn chỉnh**.

Không có guarantee rằng mọi anti-bot system sẽ coi context đó giống hệt browser thật.

---

# 28. Test Browser Strategy

Không cần Internet.

```python
context_a = BrowserContext(
    profile=BrowserProfile(
        name="chrome",
        impersonate="chrome_146",
        os="windows",
    ),
    proxy=None,
    transport=fake_transport_a,
)

context_b = BrowserContext(
    profile=BrowserProfile(
        name="firefox",
        impersonate="firefox_151",
        os="linux",
    ),
    proxy=None,
    transport=fake_transport_b,
)
```

Pool:

```python
pool = BrowserContextPool([
    context_a,
    context_b,
])
```

Strategy:

```python
strategy = RoundRobinBrowserStrategy(
    pool
)
```

Test:

```python
print(
    strategy.select()
    .profile.name
)

print(
    strategy.select()
    .profile.name
)

print(
    strategy.select()
    .profile.name
)
```

Kết quả:

```text
chrome
firefox
chrome
```

---

# 29. Test health

```python
strategy = HealthAwareBrowserStrategy(
    pool,
    failure_threshold=2,
)
```

Chọn:

```text
A
```

Đánh dấu:

```python
strategy.mark_failure(
    context_a
)

strategy.mark_failure(
    context_a
)
```

Bây giờ:

```text
A
 ↓
2 failures
 ↓
unavailable
```

Lần tiếp theo:

```python
context = strategy.select()
```

sẽ chọn:

```text
B
```

---

# 30. Nhưng production cần cooldown

Hiện tại:

```text
A failed 3 lần
↓
A unavailable forever
```

không tốt.

Proxy/server có thể hồi phục.

Ta cần:

```text
A
 ↓
failure threshold
 ↓
cooldown
 ↓
health check
 ↓
healthy
 ↓
A trở lại pool
```

Ví dụ:

```text
A failed
↓
disabled 30s
↓
30s
↓
probe
↓
success
↓
available
```

Đây sẽ là một phần của thiết kế production sau Error Classification.

---

# 31. Browser Context và Proxy Context

Đây là điểm kiến trúc rất đẹp.

Buổi 46:

```text
ProxyContext
    Proxy
    Transport
```

Buổi 47:

```text
BrowserContext
    BrowserProfile
    Proxy
    Transport
```

Ta đã nâng cấp từ:

```text
Proxy
```

thành:

```text
Browser Persona
+
Network Identity
+
Client Session
```

---

# 32. Kiến trúc hiện tại

```text
                         Fetcher
                            │
                            ▼
                     PrimpFetcher
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        RetryPolicy    RateLimiter    Semaphore
              │
              ▼
      BrowserProfileStrategy
              │
              ▼
       BrowserContext
              │
       ┌──────┼─────────┐
       │      │         │
       ▼      ▼         ▼
    Browser  Proxy   Transport
    Profile           │
                      ▼
               AsyncClient
                      │
                      ▼
                     HTTP
```

---

# 33. Nhưng có một vấn đề chúng ta cố tình để lại

Hiện tại khi nhận:

```text
403
```

chúng ta chưa biết chính xác nên:

```text
retry?
đổi proxy?
đổi browser?
disable context?
```

Tương tự:

```text
Timeout
```

có thể là:

```text
Proxy chết
Server chậm
Network lỗi
```

Còn:

```text
TLS error
```

có thể liên quan đến:

```text
Proxy
TLS
Network
```

Do đó không nên tiếp tục nhồi logic vào `PrimpFetcher`.

---

# 34. Buổi 48 sẽ giải quyết chính xác vấn đề này

Ta sẽ xây:

```text
Error Classification
```

Flow:

```text
HTTP / Exception
       ↓
ErrorClassifier
       ↓
FetchError
       │
       ├── Retryable
       ├── NonRetryable
       ├── ProxyError
       ├── TimeoutError
       ├── TLSFailure
       ├── HTTP429
       ├── HTTP403
       └── HTTP5xx
```

Sau đó:

```text
ProxyError
    ↓
ProxyStrategy.mark_failure()

Timeout
    ↓
Retry

403
    ↓
policy quyết định

503
    ↓
Retry
```

Lúc đó kiến trúc mới thật sự production-grade.

---

# 35. Tổng kết Buổi 47

Bạn cần nhớ:

### ① BrowserProfile

```text
Browser configuration
```

Ví dụ:

```text
chrome_146
firefox_151
safari_26
```

### ② BrowserContext

```text
BrowserProfile
+
Proxy
+
Transport
+
Client
```

### ③ BrowserProfileStrategy

Quyết định:

```text
context nào được sử dụng
```

### ④ Stable identity

Không random browser/OS/proxy vô tội vạ cho từng request.

### ⑤ Health

Không nên đánh đồng:

```text
Proxy failure
```

với:

```text
Browser failure
```

---

# 36. Toàn bộ roadmap đến hiện tại

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
46 Proxy Strategy
       ↓
47 Browser Profile Strategy   ← HÔM NAY
       ↓
48 Error Classification
       ↓
49 Observability / Logging
       ↓
50 Production Fetcher
```

Và kiến trúc cuối Part V đang tiến đến:

```text
                    CrawlChapter
                         │
                         ▼
                      Fetcher
                         │
                         ▼
                   PrimpFetcher
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
     Retry          RateLimiter       Semaphore
        │
        ▼
 BrowserProfileStrategy
        │
        ▼
 BrowserContext
        │
   ┌────┼─────┐
   ▼    ▼     ▼
Browser Proxy Transport
Profile          │
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

**Điểm mấu chốt của Buổi 47:** từ đây ta không còn nghĩ theo kiểu **“mỗi request chọn một User-Agent”**, mà nghĩ theo **“một Fetch Context có browser profile + OS + proxy + client lifetime ổn định”**. Đây là nền tảng để Buổi 48 phân loại lỗi và quyết định **lỗi nào retry, lỗi nào đổi proxy, lỗi nào loại context**.
