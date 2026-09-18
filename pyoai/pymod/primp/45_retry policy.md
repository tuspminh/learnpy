# Buổi 45 — Retry Policy Production-Grade

Ở Buổi 44, ta đã có:

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
```

Nhưng `RetryPolicy` hiện tại còn đơn giản:

```python
if exception:
    return True
```

Production crawler **không thể retry mọi exception**.

Hôm nay ta thiết kế retry bài bản hơn.

---

# 1. Retry thực sự phải quyết định 4 thứ

Một hệ thống retry tốt phải trả lời:

```text
1. Có retry không?
2. Retry bao nhiêu lần?
3. Chờ bao lâu?
4. Có nên retry loại lỗi này không?
```

Ví dụ:

```text
503
 ↓
Retry
 ↓
wait 1.2s
 ↓
503
 ↓
Retry
 ↓
wait 2.7s
 ↓
200
```

Nhưng:

```text
404
 ↓
NO RETRY
```

và:

```text
Invalid URL
 ↓
NO RETRY
```

---

# 2. Retry không phải là "thử lại mọi thứ"

Crawler có rất nhiều loại lỗi:

```text
HTTP
├── 2xx
├── 3xx
├── 4xx
└── 5xx

Network
├── Timeout
├── Connection error
├── TLS error
└── Proxy error

Application
├── Invalid URL
├── Invalid configuration
└── Programming error
```

Không phải tất cả đều retry.

Một nguyên tắc ban đầu:

| Lỗi               | Retry    |
| ----------------- | -------- |
| 200               | ❌        |
| 301               | ❌        |
| 404               | ❌        |
| 401               | ❌        |
| 403               | thường ❌ |
| 408               | ✅        |
| 429               | ✅        |
| 500               | ✅        |
| 502               | ✅        |
| 503               | ✅        |
| 504               | ✅        |
| Timeout           | thường ✅ |
| Connection error  | thường ✅ |
| Invalid URL       | ❌        |
| Programming error | ❌        |

**"thường"** ở đây rất quan trọng: quyết định thực tế còn phụ thuộc transport, source, proxy và chính sách crawler.

---

# 3. Vấn đề lớn nhất của Retry

Giả sử:

```text
100 chapter
```

và server trả:

```text
503
```

Nếu 100 worker lập tức retry:

```text
100 requests
 ↓
100 × 503
 ↓
100 retry
 ↓
100 × 503
 ↓
100 retry
```

Server càng quá tải.

Đây là lý do cần:

```text
Exponential Backoff
+
Jitter
+
Rate Limiter
```

---

# 4. Exponential Backoff

Công thức cơ bản:

```text
delay = base_delay × 2^(attempt - 1)
```

Nếu:

```python
base_delay = 1
```

thì:

```text
attempt 1 → 1s
attempt 2 → 2s
attempt 3 → 4s
attempt 4 → 8s
attempt 5 → 16s
```

Có giới hạn:

```python
max_delay = 30
```

thì:

```text
1
2
4
8
16
30
30
30
```

---

# 5. Vì sao cần Jitter?

Giả sử 100 request cùng nhận:

```text
503
```

và tất cả đều:

```text
sleep(2)
```

Sau đúng 2 giây:

```text
100 requests
     ↓
cùng retry
     ↓
server lại nhận burst
```

Đó gọi là **thundering herd**.

Jitter thêm một khoảng ngẫu nhiên:

```text
2.1s
2.4s
2.7s
1.8s
2.3s
...
```

Các request được phân tán.

---

# 6. Full Jitter

Một cách đơn giản:

```text
delay = random(0, exponential_delay)
```

Ví dụ exponential delay:

```text
4s
```

thì jitter có thể:

```text
0.8s
2.3s
3.7s
1.1s
...
```

Đây là chiến lược rất phù hợp cho crawler.

---

# 7. Thiết kế lại `RetryPolicy`

Ta tạo:

```python
from dataclasses import dataclass
import random
```

```python
@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    retryable_statuses: frozenset[int] = frozenset({
        408,
        429,
        500,
        502,
        503,
        504,
    })

    jitter: bool = True

    def should_retry_status(
        self,
        status_code: int,
    ) -> bool:

        return status_code in self.retryable_statuses
```

---

# 8. Tính exponential delay

```python
def exponential_delay(
    self,
    attempt: int,
) -> float:

    delay = self.base_delay * (
        2 ** (attempt - 1)
    )

    return min(
        delay,
        self.max_delay,
    )
```

Ví dụ:

```python
policy = RetryPolicy(
    base_delay=1,
    max_delay=10,
)
```

```text
attempt 1 → 1
attempt 2 → 2
attempt 3 → 4
attempt 4 → 8
attempt 5 → 10
```

---

# 9. Thêm Full Jitter

```python
def delay(
    self,
    attempt: int,
) -> float:

    exponential = self.exponential_delay(
        attempt
    )

    if not self.jitter:
        return exponential

    return random.uniform(
        0,
        exponential,
    )
```

Ví dụ:

```text
attempt 1
exponential = 1
jitter = 0.73

attempt 2
exponential = 2
jitter = 1.42

attempt 3
exponential = 4
jitter = 3.17
```

---

# 10. Nhưng còn `Retry-After`?

Đây là phần rất quan trọng.

Server có thể trả:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 10
```

Điều đó có nghĩa server yêu cầu client đợi khoảng:

```text
10 seconds
```

Trường hợp này không nên đơn giản bỏ qua header rồi dùng:

```python
random.uniform(0, 4)
```

---

# 11. Retry-After có thể có hai dạng

### Dạng số giây

```http
Retry-After: 10
```

Nghĩa là:

```text
wait 10 seconds
```

### Dạng HTTP date

Ví dụ:

```http
Retry-After: Wed, 21 Oct 2026 07:28:00 GMT
```

Nghĩa là server chỉ định thời điểm retry.

Trong crawler thực tế, ta nên hỗ trợ ít nhất dạng số trước.

---

# 12. Retry Decision

Một thiết kế sạch hơn là không để `RetryExecutor` tự suy đoán tất cả.

Ta tạo:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:

    retry: bool

    delay: float = 0.0

    reason: str = ""
```

Ví dụ:

```python
RetryDecision(
    retry=True,
    delay=2.5,
    reason="HTTP 503",
)
```

hoặc:

```python
RetryDecision(
    retry=False,
    reason="HTTP 404",
)
```

---

# 13. RetryPolicy chịu trách nhiệm quyết định

```python
@dataclass(frozen=True)
class RetryPolicy:

    max_attempts: int = 3

    base_delay: float = 1.0

    max_delay: float = 30.0

    retryable_statuses: frozenset[int] = frozenset({
        408,
        429,
        500,
        502,
        503,
        504,
    })

    jitter: bool = True

    def should_retry(
        self,
        *,
        attempt: int,
        status_code: int | None = None,
    ) -> bool:

        if attempt >= self.max_attempts:
            return False

        if status_code is None:
            return False

        return (
            status_code
            in self.retryable_statuses
        )

    def calculate_delay(
        self,
        attempt: int,
    ) -> float:

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

# 14. Nhưng Exception thì sao?

Đây là vấn đề Buổi 48 chúng ta sẽ xử lý sâu hơn.

Hiện tại có thể định nghĩa một abstraction:

```python
class RetryableError(Exception):
    pass
```

Các exception được phân loại thành:

```text
RetryableError
NonRetryableError
```

Ví dụ:

```python
class NetworkError(RetryableError):
    pass
```

```python
class InvalidRequestError(
    Exception
):
    pass
```

Nhưng **không nên tùy tiện bắt mọi `Exception` rồi coi là `RetryableError`**.

---

# 15. RetryExecutor production hơn

Ta viết:

```python
import asyncio


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

                delay = (
                    self.policy.calculate_delay(
                        attempt
                    )
                )

                if attempt < self.policy.max_attempts:
                    await asyncio.sleep(delay)

            except RetryableError as exc:

                last_exception = exc

                if attempt >= self.policy.max_attempts:
                    raise

                delay = (
                    self.policy.calculate_delay(
                        attempt
                    )
                )

                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception

        raise RuntimeError(
            "Retry attempts exhausted"
        )
```

Điểm khác biệt rất quan trọng:

```python
except RetryableError
```

thay vì:

```python
except Exception
```

---

# 16. Nhưng `primp` exception cụ thể là gì?

Đây là chỗ cần cẩn thận.

Không nên tự đoán:

```python
except primp.SomeException:
```

nếu chưa kiểm tra API/version hiện tại.

Ở tầng kiến trúc của chúng ta, tốt hơn là:

```text
primp exception
       ↓
PrimpTransport
       ↓
Infrastructure error mapping
       ↓
RetryableError / NonRetryableError
       ↓
RetryExecutor
```

Tức là Application không phụ thuộc exception cụ thể của `primp`.

---

# 17. Retry-After

Ta viết helper riêng:

```python
def parse_retry_after(
    headers: dict[str, str],
) -> float | None:

    value = headers.get(
        "Retry-After"
    )

    if value is None:
        return None

    try:
        seconds = float(value)

    except ValueError:
        return None

    if seconds < 0:
        return None

    return seconds
```

---

# 18. Ưu tiên Retry-After

Nếu server nói:

```text
Retry-After: 15
```

thì:

```text
server instruction
       ↓
15 seconds
```

thay vì:

```text
client exponential backoff
       ↓
4 seconds
```

Ta có thể viết:

```python
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

# 19. Ví dụ

Server:

```http
429 Too Many Requests
Retry-After: 10
```

Ta có:

```python
delay = policy.calculate_delay(
    attempt=1,
    retry_after=10,
)
```

Kết quả:

```text
10 seconds
```

Nếu không có:

```http
Retry-After
```

thì:

```text
Exponential Backoff
+
Jitter
```

được sử dụng.

---

# 20. Idempotency

Một vấn đề rất quan trọng.

GET:

```http
GET /chapter/123
```

thường có thể retry tương đối an toàn.

Nhưng POST:

```http
POST /payment
```

retry có thể tạo:

```text
payment 1
payment 2
```

Do đó Retry Policy nên quan tâm đến HTTP method.

Hiện tại Fetcher của chúng ta mới có:

```python
get()
```

nên chưa cần đưa complexity này vào `FetchRequest`.

Sau này khi mở rộng:

```text
GET
POST
PUT
PATCH
DELETE
```

ta sẽ có:

```text
RetryPolicy
      ↓
method
      ↓
idempotency
      ↓
retry?
```

---

# 21. Đừng retry 403 một cách máy móc

Đặc biệt trong crawler:

```text
403
```

có thể có nghĩa:

```text
Access denied
WAF
bot protection
permission
```

Nếu cứ:

```text
403
 ↓
retry
 ↓
403
 ↓
retry
```

thường chỉ làm tình hình tệ hơn.

Đây là lý do sau này chúng ta có:

```text
Buổi 46 Proxy Strategy
Buổi 47 Browser Profile Strategy
Buổi 48 Error Classification
```

Không nên giải quyết tất cả bằng Retry.

---

# 22. Retry + Proxy

Đây là kiến trúc chúng ta hướng tới:

```text
Request
   ↓
Retry
   ↓
Proxy A
   ↓
503
   ↓
Retry
   ↓
Proxy B
   ↓
200
```

Nhưng để làm được điều đó đúng cách, RetryExecutor không nên tự biết:

```text
ProxyPool
```

Thay vào đó:

```text
RetryExecutor
       ↓
Retry decision
       ↓
PrimpFetcher
       ↓
Proxy Strategy
```

Phần này sẽ được xây dựng ở **Buổi 46**.

---

# 23. Retry + RateLimiter

Một điểm cực kỳ quan trọng:

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
 ↓
attempt 2
 ↓
RateLimiter
 ↓
HTTP
```

Không được:

```text
attempt 1
 ↓
RateLimiter
 ↓
HTTP
 ↓
503
 ↓
attempt 2
 ↓
HTTP   ← bỏ qua RateLimiter
```

Nếu không:

```text
Retry
```

có thể phá vỡ:

```text
RateLimit
```

---

# 24. Retry + Semaphore

Tương tự:

```text
attempt
 ↓
Semaphore
 ↓
HTTP
 ↓
release
```

Retry attempt mới lại:

```text
Semaphore
 ↓
HTTP
```

Không giữ semaphore trong lúc:

```python
await asyncio.sleep(...)
```

Sai:

```python
async with semaphore:

    response = await operation()

    await asyncio.sleep(5)
```

Nếu có nhiều worker:

```text
Semaphore = 5

5 workers
 ↓
503
 ↓
sleep 5s
```

thì cả 5 slot bị giữ vô ích.

Thiết kế của Buổi 44 tốt hơn:

```python
async def operation():

    await rate_limiter.acquire()

    async with semaphore:
        return await transport.send(
            request
        )
```

Sau khi request xong:

```text
Semaphore released
       ↓
Retry sleep
       ↓
attempt tiếp theo
```

---

# 25. Test Retry Policy

Không cần Internet.

```python
policy = RetryPolicy(
    max_attempts=4,
    base_delay=1,
    max_delay=10,
    jitter=False,
)
```

Test:

```python
print(
    policy.should_retry(
        attempt=1,
        status_code=503,
    )
)
```

Kết quả:

```text
True
```

Test 404:

```python
print(
    policy.should_retry(
        attempt=1,
        status_code=404,
    )
)
```

```text
False
```

---

# 26. Test exponential backoff

```python
for attempt in range(1, 6):

    print(
        attempt,
        policy.calculate_delay(
            attempt
        )
    )
```

Với:

```python
base_delay=1
max_delay=10
jitter=False
```

kết quả:

```text
1 1
2 2
3 4
4 8
5 10
```

---

# 27. Test Jitter

```python
policy = RetryPolicy(
    base_delay=4,
    max_delay=30,
    jitter=True,
)

for _ in range(5):

    print(
        policy.calculate_delay(3)
    )
```

Có thể nhận:

```text
0.83
2.14
3.72
1.55
3.91
```

Không cố định.

---

# 28. Test Retry-After

```python
headers = {
    "Retry-After": "15"
}

retry_after = parse_retry_after(
    headers
)

print(retry_after)
```

Kết quả:

```text
15.0
```

---

# 29. Một lỗi tinh tế: `Retry-After` quá lớn

Server có thể trả:

```http
Retry-After: 86400
```

Không nên để crawler:

```python
await asyncio.sleep(86400)
```

trong một worker.

Do đó:

```python
max_delay=30
```

hoặc một giá trị phù hợp với hệ thống.

Ta có:

```python
min(
    retry_after,
    max_delay,
)
```

Tuy nhiên production crawler có thể cần một chính sách riêng cho server-mandated delay, thay vì luôn cắt xuống; đây là quyết định hệ thống cần cấu hình.

---

# 30. Kiến trúc Retry cuối Buổi 45

```text
                 PrimpFetcher
                       │
                       ▼
                 RetryExecutor
                       │
                       ▼
                  RetryPolicy
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       Status       Exception    Attempt
          │            │            │
          └────────────┼────────────┘
                       ▼
                RetryDecision
                       │
              ┌────────┴────────┐
              │                 │
           retry             no retry
              │                 │
              ▼                 ▼
       calculate delay        return
              │
       ┌──────┴───────┐
       │              │
 Retry-After    Exponential
                    Backoff
                       │
                    Jitter
                       │
                       ▼
                  asyncio.sleep()
```

---

# 31. Những gì chúng ta **chưa** làm

Đừng vội nhét tất cả vào `RetryPolicy`.

Chưa xử lý sâu:

```text
❌ Proxy failure classification
❌ Browser profile switching
❌ Circuit breaker
❌ Retry budget
❌ Distributed retry
❌ Persistent retry queue
❌ HTTP-date Retry-After
❌ Per-domain retry policy
```

Các phần đó sẽ xuất hiện khi crawler trưởng thành hơn.

---

# 32. Vị trí của Buổi 45 trong toàn bộ Part V

```text
41 Request Model
       ↓
42 Response Model
       ↓
43 Fetcher Interface
       ↓
44 PrimpFetcher
       ↓
45 Retry Policy       ← HÔM NAY
       ↓
46 Proxy Strategy
       ↓
47 Browser Profile Strategy
       ↓
48 Error Classification
       ↓
49 Observability / Logging
       ↓
50 Production Fetcher
```

Điều quan trọng nhất hôm nay là chúng ta đã chuyển từ:

```python
except Exception:
    retry()
```

sang tư duy:

```text
Exception / HTTP result
        ↓
Classification
        ↓
Retry Policy
        ↓
Retry Decision
        ↓
Backoff + Jitter
        ↓
Retry
```

Và kiến trúc vẫn giữ nguyên:

```text
Application
    ↓
Fetcher
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
```

**Buổi 46 — Proxy Strategy** sẽ nối `ProxyPool` mà chúng ta đã học ở Phần IV vào `PrimpFetcher`, đặc biệt là bài toán: **request qua Proxy A lỗi → đánh dấu A → chọn Proxy B → retry**, nhưng vẫn giữ `PrimpFetcher` không trở thành God Object.
