# Buổi 19 — Rate Limiting

Ở Buổi 18 chúng ta đã có:

```text
Proxy
   ↓
Circuit Breaker
   ↓
OPEN / CLOSED / HALF_OPEN
```

Circuit Breaker trả lời:

> **Có nên cho request đi qua Proxy này hay không?**

Buổi 19 thêm một câu hỏi khác:

> **Nếu được phép đi qua, tốc độ request là bao nhiêu?**

Đó là **Rate Limiting**.

---

# 1. Vì sao Fetcher cần Rate Limiting?

Giả sử crawler có:

```text
1000 URLs
10 workers
```

Nếu mỗi worker gửi request liên tục:

```text
Worker 1 → request
Worker 2 → request
Worker 3 → request
...
Worker 10 → request
```

server có thể nhận:

```text
████████████████████████████
request request request ...
```

Hậu quả:

* server trả `429 Too Many Requests`;
* proxy bị giới hạn;
* IP bị rate-limit;
* crawler tạo tải không cần thiết;
* retry lại càng làm tình hình tệ hơn.

Ta muốn:

```text
Request
   ↓
Rate Limiter
   ↓
ALLOW / WAIT / REJECT
```

---

# 2. Rate Limiting khác Retry

Đây là điểm phải nhớ.

### Retry

```text
HTTP request
     ↓
   500
     ↓
retry
```

Retry xử lý:

> Request đã thất bại → có thử lại không?

### Rate Limiter

```text
request
   ↓
Rate Limiter
   ↓
chưa đến lượt
   ↓
wait
```

Rate Limiter xử lý:

> Request này có được phép gửi **ngay bây giờ** không?

---

# 3. Rate Limiting khác Circuit Breaker

Circuit Breaker:

```text
Proxy A
   ↓
fail
   ↓
fail
   ↓
fail
   ↓
OPEN
   ↓
BLOCK
```

Rate Limiter:

```text
Proxy A
   ↓
request 1
   ↓
wait
   ↓
request 2
   ↓
wait
   ↓
request 3
```

Một cái dựa trên **failure state**.

Một cái dựa trên **request frequency**.

---

# 4. Rate Limit theo cái gì?

Trong crawler của chúng ta có thể limit theo:

```text
Global
Proxy
Domain
Endpoint
```

Ví dụ:

### Global

```text
toàn crawler:
100 requests / second
```

### Proxy

```text
Proxy A:
2 requests / second

Proxy B:
2 requests / second
```

### Domain

```text
example.com:
1 request / second
```

### Endpoint

```text
example.com/api:
10 requests / second
```

Với crawler truyện, **domain-level rate limiting** rất hữu ích.

Ví dụ:

```text
truyen-a.com → 1 req/s
truyen-b.com → 2 req/s
truyen-c.com → 1 req/s
```

---

# 5. Thiết kế theo SOLID

Không để Fetcher tự viết:

```python
time.sleep(...)
```

vì như vậy Fetcher sẽ biết quá nhiều.

Ta tạo abstraction:

```python
class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, key: str) -> None: ...
```

Ý nghĩa:

```text
Fetcher
   ↓
RateLimiter
```

Fetcher không cần biết limiter dùng:

* sleep;
* token bucket;
* leaky bucket;
* Redis;
* distributed rate limit;
* database.

---

# 6. `RateLimiter`

```python
from abc import ABC, abstractmethod


class RateLimiter(ABC):
    @abstractmethod
    def acquire(self, key: str) -> None:
        """
        Block cho tới khi request được phép thực hiện.
        """
        raise NotImplementedError
```

---

# 7. Rate Limit Configuration

Ta cần một Value Object/config:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitConfig:
    requests: int
    period: float

    def __post_init__(self):
        if self.requests <= 0:
            raise ValueError("requests must be > 0")

        if self.period <= 0:
            raise ValueError("period must be > 0")
```

Ví dụ:

```python
RateLimitConfig(
    requests=2,
    period=1.0,
)
```

nghĩa là:

```text
2 requests / 1 second
```

---

# 8. Tại sao không gọi là `requests_per_second`?

Ta có thể viết:

```python
requests_per_second: float
```

nhưng:

```text
requests / period
```

tổng quát hơn.

Ví dụ:

```text
10 requests / 60 seconds
```

hoặc:

```text
100 requests / 1 hour
```

---

# 9. Fixed Window Rate Limiter

Đầu tiên học thuật toán đơn giản nhất:

**Fixed Window.**

Ví dụ:

```text
10:00:00 ───────── 10:00:01
       window 1
```

Cho phép:

```text
2 requests
```

Trong window:

```text
R1 → ALLOW
R2 → ALLOW
R3 → WAIT
```

Sang window mới:

```text
10:00:01
```

counter reset.

---

# 10. Implement Fixed Window

```python
import time


class FixedWindowRateLimiter(RateLimiter):
    def __init__(
        self,
        config: RateLimitConfig,
    ):
        self._config = config

        self._window_start = time.monotonic()
        self._count = 0

    def acquire(self, key: str) -> None:

        while True:
            now = time.monotonic()

            elapsed = now - self._window_start

            if elapsed >= self._config.period:
                self._window_start = now
                self._count = 0

            if self._count < self._config.requests:
                self._count += 1
                return

            remaining = self._config.period - elapsed

            if remaining > 0:
                time.sleep(remaining)
```

---

# 11. Nhưng có một vấn đề

Implementation trên:

```text
Một limiter
     ↓
tất cả request
```

Nếu:

```text
example.com
other.com
another.com
```

thì tất cả cùng dùng một counter.

Không phù hợp với crawler nhiều domain.

Ta cần:

```text
key
 ↓
state riêng
```

---

# 12. Rate Limit theo key

Ta tạo:

```python
from dataclasses import dataclass


@dataclass
class WindowState:
    window_start: float
    count: int
```

Sau đó:

```python
self._states: dict[str, WindowState]
```

Ví dụ:

```text
states

example.com
    ↓
WindowState

google.com
    ↓
WindowState

site-a.com
    ↓
WindowState
```

---

# 13. Per-Key Fixed Window

```python
import time
from dataclasses import dataclass


@dataclass
class WindowState:
    window_start: float
    count: int


class FixedWindowRateLimiter(RateLimiter):
    def __init__(
        self,
        config: RateLimitConfig,
    ):
        self._config = config
        self._states: dict[str, WindowState] = {}

    def acquire(self, key: str) -> None:

        while True:
            now = time.monotonic()

            state = self._states.get(key)

            if state is None:
                state = WindowState(
                    window_start=now,
                    count=0,
                )
                self._states[key] = state

            elapsed = now - state.window_start

            if elapsed >= self._config.period:
                state.window_start = now
                state.count = 0

            if state.count < self._config.requests:
                state.count += 1
                return

            remaining = self._config.period - elapsed

            if remaining > 0:
                time.sleep(remaining)
```

---

# 14. Ví dụ

Config:

```python
RateLimitConfig(
    requests=2,
    period=1.0,
)
```

Requests:

```text
example.com
example.com
example.com
```

Kết quả:

```text
R1 → ALLOW
R2 → ALLOW
R3 → WAIT
```

Trong khi:

```text
other.com
```

vẫn có thể:

```text
other.com → ALLOW
```

vì có state riêng.

---

# 15. Nhưng Fixed Window có một nhược điểm lớn

Giả sử:

```text
limit = 2 req/s
```

Ta có:

```text
10:00:00.99
R1

10:00:00.99
R2
```

Sau đó window mới:

```text
10:00:01.00
R3

10:00:01.00
R4
```

Trong khoảng khoảng:

```text
0.01 second
```

server nhận:

```text
4 requests
```

Trong khi ta nói:

```text
2 req/s
```

Đây gọi là **boundary burst**.

Vì vậy production thường dùng thuật toán tốt hơn.

---

# 16. Token Bucket

Một thuật toán rất phổ biến là:

**Token Bucket.**

Ý tưởng:

```text
Bucket
capacity = 5

█████
```

Mỗi request lấy một token:

```text
request
   ↓
take token
   ↓
HTTP
```

Token được refill theo tốc độ:

```text
1 token / second
```

---

# 17. Ví dụ Token Bucket

Config:

```text
capacity = 5
rate = 1 token/s
```

Ban đầu:

```text
█████
```

Có 5 request:

```text
R1 → token
R2 → token
R3 → token
R4 → token
R5 → token

bucket = 0
```

Request thứ 6:

```text
R6
 ↓
không có token
 ↓
WAIT
```

Sau 1 giây:

```text
█
```

R6 được phép.

---

# 18. Token Bucket Model

```python
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: float
    refill_rate: float
    tokens: float
    updated_at: float
```

Trong đó:

```text
capacity
```

= số token tối đa.

```text
refill_rate
```

= token / second.

```text
tokens
```

= số token hiện tại.

---

# 19. Token Bucket Limiter

```python
import time


class TokenBucketRateLimiter(RateLimiter):
    def __init__(
        self,
        capacity: float,
        refill_rate: float,
    ):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")

        if refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")

        self._capacity = capacity
        self._refill_rate = refill_rate

        self._buckets: dict[str, TokenBucket] = {}

    def acquire(self, key: str) -> None:

        while True:
            now = time.monotonic()

            bucket = self._buckets.get(key)

            if bucket is None:
                bucket = TokenBucket(
                    capacity=self._capacity,
                    refill_rate=self._refill_rate,
                    tokens=self._capacity,
                    updated_at=now,
                )

                self._buckets[key] = bucket

            elapsed = now - bucket.updated_at

            bucket.tokens = min(
                self._capacity,
                bucket.tokens + elapsed * self._refill_rate,
            )

            bucket.updated_at = now

            if bucket.tokens >= 1:
                bucket.tokens -= 1
                return

            missing = 1 - bucket.tokens

            wait_time = missing / self._refill_rate

            time.sleep(wait_time)
```

---

# 20. Ví dụ

```python
limiter = TokenBucketRateLimiter(
    capacity=2,
    refill_rate=1,
)
```

Ban đầu:

```text
tokens = 2
```

Request:

```text
R1 → token 1
R2 → token 2
R3 → wait
```

Sau khoảng 1 second:

```text
token refill
```

R3 được chạy.

---

# 21. Vì sao Token Bucket phù hợp crawler?

Nó cho phép **burst nhỏ**.

Ví dụ:

```text
capacity = 3
rate = 1 req/s
```

Crawler có thể gửi nhanh:

```text
R1
R2
R3
```

nhưng sau đó phải giảm tốc:

```text
R4 → wait
R5 → wait
```

Điều này thường thực tế hơn fixed window.

---

# 22. Nhưng có một vấn đề lớn: concurrency

Crawler của chúng ta sau này sẽ có:

```text
Worker 1
Worker 2
Worker 3
Worker 4
```

cùng gọi:

```python
limiter.acquire("example.com")
```

Nếu không lock:

```text
Worker 1 → tokens = 1
Worker 2 → tokens = 1
Worker 3 → tokens = 1
```

nhiều worker có thể cùng lấy một token.

Đây là **race condition**.

---

# 23. Thread-safe Rate Limiter

Nếu dùng threading, cần:

```python
threading.Lock
```

Ví dụ:

```python
import threading


class ThreadSafeTokenBucketRateLimiter:
    def __init__(
        self,
        capacity: float,
        refill_rate: float,
    ):
        self._capacity = capacity
        self._refill_rate = refill_rate

        self._buckets = {}

        self._lock = threading.Lock()
```

Điểm quan trọng:

> **State mutation phải được bảo vệ.**

---

# 24. Nhưng không nên giữ lock khi sleep

Sai:

```python
with self._lock:
    ...
    time.sleep(wait_time)
```

Nếu worker A sleep trong lock:

```text
Worker A
   ↓
LOCK
   ↓
sleep 1s
```

Worker B:

```text
LOCK
 ↓
BLOCK
```

Không tốt.

Thiết kế đúng:

```text
LOCK
 ↓
calculate
 ↓
unlock
 ↓
sleep
 ↓
retry
```

---

# 25. Đây là lý do RateLimiter nên là abstraction

Fetcher không nên biết:

```python
threading.Lock()
time.sleep()
TokenBucket
```

Fetcher chỉ biết:

```python
rate_limiter.acquire(key)
```

Đây chính là **DIP**.

---

# 26. Rate Limit key

Trong crawler truyện, ta có thể chọn:

```text
domain
```

Ví dụ:

```python
key = "truyenfull.vn"
```

Flow:

```text
URL
 ↓
parse domain
 ↓
rate_limiter.acquire(domain)
 ↓
HTTP
```

---

# 27. Domain Rate Limiter Service

Có thể tạo:

```python
from urllib.parse import urlparse


class DomainRateLimiter:
    def __init__(
        self,
        limiter: RateLimiter,
    ):
        self._limiter = limiter

    def acquire(self, url: str) -> None:

        parsed = urlparse(url)

        if not parsed.hostname:
            raise ValueError("URL hostname is required")

        self._limiter.acquire(parsed.hostname)
```

Đây là một lớp rất nhỏ nhưng hữu ích.

---

# 28. Fetcher lúc này

Fetcher trước đây:

```text
Fetcher
   ↓
Proxy
   ↓
Health Check
   ↓
HttpClient
```

Bây giờ:

```text
Fetcher
   ↓
Proxy Selection
   ↓
Circuit Breaker
   ↓
Rate Limiter
   ↓
Health Check
   ↓
HttpClient
```

Nhưng **thứ tự thực tế cần suy nghĩ kỹ**.

---

# 29. Rate Limit đặt trước hay sau Circuit Breaker?

Ví dụ Circuit đang:

```text
OPEN
```

Nếu:

```text
RateLimiter
   ↓
CircuitBreaker
```

ta có thể:

```text
consume rate token
     ↓
Circuit OPEN
     ↓
request bị block
```

Token đã bị tiêu tốn vô ích.

Do đó thường hợp lý hơn:

```text
Circuit Breaker
     ↓
Rate Limiter
```

Chỉ rate-limit request thực sự có khả năng được gửi.

---

# 30. Nhưng còn Health Check?

Nếu:

```text
Circuit CLOSED
```

ta có:

```text
Circuit
 ↓
Rate Limit
 ↓
Health Check
 ↓
HTTP
```

Health check cũng là HTTP request.

Có thể cần **rate limit health check riêng**.

Nếu không:

```text
health check
health check
health check
health check
```

cũng có thể gây tải.

---

# 31. Kiến trúc hợp lý hơn

```text
                    Fetcher
                       │
                       ▼
                Proxy Selector
                       │
                       ▼
                Circuit Breaker
                       │
                       ▼
                  Rate Limiter
                       │
                       ▼
                 Health Check
                       │
                       ▼
                   HttpClient
```

Nhưng nhớ:

```text
Health Check
```

và:

```text
Actual Fetch
```

là hai loại request khác nhau.

---

# 32. Rate Limit theo Proxy hay Domain?

Đây là câu hỏi kiến trúc rất quan trọng.

### Theo Proxy

```text
Proxy A → 2 req/s
Proxy B → 2 req/s
Proxy C → 2 req/s
```

### Theo Domain

```text
example.com → 1 req/s
```

### Kết hợp

Có thể:

```text
Proxy A + example.com
```

nhưng complexity tăng đáng kể.

Với crawler truyện ban đầu, tôi khuyên:

```text
Domain rate limit
```

trước.

Sau đó nếu cần:

```text
Proxy rate limit
+
Domain rate limit
```

---

# 33. Rate Limiter không nên biết Proxy

Ví dụ **không nên**:

```python
limiter.acquire(proxy)
```

nếu domain mới là policy.

Nên:

```python
limiter.acquire(domain)
```

RateLimiter chỉ biết:

```text
key
```

Nó không biết:

```text
Proxy
HTTP
Novel
Chapter
SQLite
```

Đây là ISP + SRP rất rõ.

---

# 34. Configuration cho crawler

Ví dụ:

```python
@dataclass(frozen=True)
class RateLimitConfig:
    requests_per_second: float = 1.0

    def __post_init__(self):

        if self.requests_per_second <= 0:
            raise ValueError("requests_per_second must be > 0")
```

Token bucket:

```python
limiter = TokenBucketRateLimiter(
    capacity=2,
    refill_rate=1,
)
```

Nghĩa:

```text
burst tối đa = 2
average = 1 req/s
```

---

# 35. Testing — không dùng `sleep()`

Đây là phần đặc biệt quan trọng.

Không nên test:

```python
time.sleep(1)
```

vì test:

* chậm;
* không deterministic;
* khó kiểm soát.

Giống Buổi 17, ta inject Clock.

---

# 36. Clock abstraction

```python
from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    @abstractmethod
    def now(self) -> datetime:
        raise NotImplementedError
```

Nhưng Rate Limiter cần **monotonic time**, không phải wall-clock.

Do đó tốt hơn tạo:

```python
class MonotonicClock(ABC):
    @abstractmethod
    def now(self) -> float:
        raise NotImplementedError
```

Production:

```python
import time


class SystemMonotonicClock(MonotonicClock):
    def now(self) -> float:
        return time.monotonic()
```

---

# 37. Fake Clock

```python
class FakeMonotonicClock(MonotonicClock):
    def __init__(self, value: float = 0.0):
        self._value = value

    def now(self) -> float:
        return self._value

    def advance(self, seconds: float) -> None:

        if seconds < 0:
            raise ValueError("seconds must be >= 0")

        self._value += seconds
```

Bây giờ test cực kỳ nhanh.

---

# 38. Sleep cũng nên inject

Tạo:

```python
class Sleeper(ABC):
    @abstractmethod
    def sleep(self, seconds: float) -> None:
        raise NotImplementedError
```

Production:

```python
import time


class SystemSleeper(Sleeper):
    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)
```

Test:

```python
class FakeSleeper(Sleeper):
    def __init__(self):
        self.calls = []

    def sleep(self, seconds: float) -> None:
        self.calls.append(seconds)
```

Như vậy test không thực sự sleep.

---

# 39. Nhưng Token Bucket test còn tốt hơn

Ta có thể thiết kế limiter:

```text
Clock
Sleeper
```

được inject:

```python
class TokenBucketRateLimiter:
    def __init__(
        self,
        capacity,
        refill_rate,
        clock,
        sleeper,
    ): ...
```

Production:

```text
SystemMonotonicClock
SystemSleeper
```

Test:

```text
FakeMonotonicClock
FakeSleeper
```

Đây chính là **Dependency Injection** từ Buổi 15 được áp dụng lại.

---

# 40. Test cases

### Test 1

```text
capacity = 2
```

```text
R1 → allow
R2 → allow
```

---

### Test 2

```text
R3
```

không có token:

```text
wait
```

---

### Test 3

Sau:

```text
1 second
```

có:

```text
1 token
```

---

### Test 4

Không vượt quá capacity:

```text
capacity = 2
```

dù 10 giây không có request:

```text
tokens <= 2
```

Không được:

```text
tokens = 10
```

---

# 41. Rate Limit + Retry

Đây là chỗ rất dễ thiết kế sai.

Giả sử:

```text
Request
 ↓
Rate Limiter
 ↓
HTTP
 ↓
500
 ↓
Retry
```

Retry request **cũng phải chịu Rate Limiter**.

Không được:

```text
request
 ↓
rate limit
 ↓
500
 ↓
retry
 ↓
retry
 ↓
retry
```

mà bỏ qua limiter.

Flow đúng:

```text
Request
   ↓
RateLimiter
   ↓
HTTP
   ↓
500
   ↓
Backoff
   ↓
Retry
   ↓
RateLimiter
   ↓
HTTP
```

---

# 42. Rate Limit + 429

Ví dụ server trả:

```text
429 Too Many Requests
```

Ta có:

```text
429
 ↓
Retry Policy
 ↓
Backoff
 ↓
Rate Limiter
 ↓
Retry
```

Không nên chỉ:

```text
429 → retry immediately
```

vì như vậy có thể tạo:

```text
429
429
429
429
429
```

và càng bị rate-limit mạnh hơn.

---

# 43. `Retry-After`

Một server có thể trả:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 5
```

Ý nghĩa:

```text
hãy đợi 5 giây
```

Đây sẽ là một enhancement rất hữu ích sau này.

Rate Limiter và Retry Policy có thể phối hợp:

```text
429
 │
 ├── Retry-After = 5s
 │
 ▼
Backoff / server hint
 │
 ▼
RateLimiter
 │
 ▼
retry
```

Nhưng **Buổi 19 chưa cần implement `Retry-After`**. Ta giữ scope rõ ràng.

---

# 44. Rate Limiting và async

Hiện tại Fetcher của roadmap đang dùng HTTP client abstraction và chưa chuyển sang async orchestration.

Với synchronous code:

```python
time.sleep()
```

có thể chấp nhận.

Nhưng sau này khi dùng:

```text
asyncio
```

không được:

```python
time.sleep()
```

trong coroutine.

Phải:

```python
await asyncio.sleep(...)
```

Do đó về sau abstraction có thể thành:

```python
class AsyncRateLimiter(ABC):
    @abstractmethod
    async def acquire(self, key: str) -> None: ...
```

Đây là lý do **không nhúng sleep trực tiếp vào Fetcher**.

---

# 45. Rate Limiting và Distributed Crawler

Hiện tại:

```text
Process
 ├── Worker 1
 ├── Worker 2
 └── Worker 3
```

mỗi process có:

```text
RateLimiter memory
```

Nếu có:

```text
Process A → 1 req/s
Process B → 1 req/s
```

thì domain thực tế có thể nhận:

```text
2 req/s
```

chứ không phải:

```text
1 req/s
```

Nếu cần rate limit **toàn hệ thống**, phải dùng shared state:

```text
Worker A ─┐
Worker B ─┼──> Redis Rate Limiter
Worker C ─┘
```

Đây là lý do Redis/RQ mà bạn đã học sau này sẽ rất hữu ích cho crawler production.

---

# 46. Nhưng chưa cần Redis

Ở giai đoạn hiện tại:

```text
Fetcher
 ↓
In-memory RateLimiter
```

là đúng.

Không nên nhảy ngay sang:

```text
Redis
Lua
Distributed Lock
```

vì sẽ làm architecture learning bị lan man.

Sau khi local version hoàn chỉnh, ta mới nâng cấp.

---

# 47. Architecture sau Buổi 19

Hiện tại hệ thống đã tiến tới:

```text
                         Crawler
                            │
                            ▼
                   Application Service
                            │
                            ▼
                         Fetcher
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
      Proxy Selector   Circuit Breaker  UA Provider
             │              │
             └───────┬──────┘
                     ▼
                Rate Limiter
                     │
                     ▼
                Health Check
                     │
                     ▼
                 HttpClient
                     │
                     ▼
                  HttpxClient
```

---

# 48. Mapping DDD

Ta đang có:

```text
Domain
├── Proxy
├── ProxyUrl
├── ProxyStatus
├── CircuitBreaker
├── CircuitState
└── RateLimit rules
```

Infrastructure:

```text
Infrastructure
├── HttpxClient
├── SQLiteProxyRepository
├── SystemClock
└── SystemSleeper
```

Application:

```text
Application
├── Fetcher
├── FetchPolicy
├── ErrorClassifier
└── Application Services
```

---

# 49. Mapping SOLID

### SRP

```text
CircuitBreaker
```

chỉ xử lý circuit state.

```text
RateLimiter
```

chỉ xử lý request frequency.

```text
Fetcher
```

orchestrate.

---

### OCP

Có thể thay:

```text
FixedWindowRateLimiter
```

bằng:

```text
TokenBucketRateLimiter
```

mà Fetcher không đổi.

---

### LSP

```text
RateLimiter
   ↑
   ├── FixedWindowRateLimiter
   └── TokenBucketRateLimiter
```

cùng có thể thay thế abstraction.

---

### ISP

Fetcher chỉ cần:

```python
acquire(key)
```

không cần biết hàng loạt method khác.

---

### DIP

```text
Fetcher
   ↓
RateLimiter
```

không:

```text
Fetcher
   ↓
TokenBucketRateLimiter
```

---

# 50. Một điểm kiến trúc quan trọng

Đừng biến RateLimiter thành:

```python
class RateLimiter:

    def check_proxy(...)
    def check_url(...)
    def check_domain(...)
    def check_retry(...)
    def check_circuit(...)
    def sleep(...)
    def send_request(...)
```

Đây sẽ trở thành:

> **God RateLimiter**

Thiết kế tốt:

```text
RateLimiter
    ↓
acquire(key)
```

đơn giản.

Các policy khác nằm ở component riêng.

---

# 51. Roadmap đã đi đến đâu?

```text
13 Domain Service                 ✅
14 Application Service            ✅
15 Dependency Injection           ✅
16 Repository cho Proxy           ✅
17 Proxy State + Persistence      ✅
18 Circuit Breaker                ✅
19 Rate Limiting                  ← HIỆN TẠI
20 Fetch Orchestration
```

Sau Buổi 19, ta đã có:

```text
                 Request
                    │
                    ▼
              Proxy Selector
                    │
                    ▼
             Circuit Breaker
                    │
             ┌──────┴──────┐
             │             │
            OPEN         CLOSED
             │             │
            STOP           ▼
                      Rate Limiter
                           │
                           ▼
                      Health Check
                           │
                           ▼
                       HTTP
                           │
                    ┌──────┴──────┐
                    │             │
                  success       error
                    │             │
                    ▼             ▼
                 result      FetchPolicy
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                       retry            rotate
                         │                 │
                         └────────┬────────┘
                                  ▼
                             Rate Limiter
```

### Ba khái niệm cần thuộc sau Buổi 19

```text
Circuit Breaker
→ Có cho request đi tới Proxy không?

Rate Limiter
→ Nếu được phép, có được gửi ngay không?

Retry
→ Nếu request thất bại, có thử lại không?
```

Và với crawler truyện của chúng ta, **Token Bucket + per-domain key** là hướng triển khai thực tế tốt để tiếp tục sang **Buổi 20 — Fetch Orchestration**, nơi toàn bộ Proxy Rotation + Circuit Breaker + Rate Limiting + Retry + Error Policy sẽ được ghép thành một Fetcher hoàn chỉnh.
