# Buổi 10 — Retry

Hôm nay chúng ta thiết kế **Retry** cho Fetcher.

Đây là bước rất quan trọng vì từ đây Fetcher bắt đầu có hành vi gần với crawler thực tế:

```text
Request
   ↓
Proxy A
   ↓
Failure
   ↓
Retry / đổi Proxy
   ↓
Proxy B
   ↓
Success
```

Nhưng ta sẽ **không** viết một vòng `for` khổng lồ bên trong `Fetcher`.

Mục tiêu của buổi này:

```text
Retry Policy
Retry Decision
Retry Delay
Proxy Rotation
HTTP Error Classification
```

---

# 1. Retry là gì?

Retry nghĩa là:

> Thử lại một request sau khi request thất bại.

Ví dụ:

```text
GET chapter-10

Attempt 1 → timeout
Attempt 2 → success
```

Nhưng crawler của chúng ta còn có proxy:

```text
Attempt 1
Proxy A → timeout

Attempt 2
Proxy B → success
```

Do đó cần phân biệt:

```text
Retry
```

và:

```text
Proxy Rotation
```

---

# 2. Retry ≠ Proxy Rotation

Ví dụ:

```text
Proxy A
   ↓
timeout
   ↓
Retry
```

có thể vẫn dùng A.

Trong khi:

```text
Proxy A
   ↓
timeout
   ↓
Proxy B
```

là rotation.

Hai khái niệm này độc lập.

---

# 3. Các loại failure

Fetcher có thể gặp:

### Network failure

```text
Timeout
Connection refused
DNS failure
Network error
```

### HTTP failure

```text
429
500
502
503
504
```

### HTTP response không phải failure transport

```text
403
404
```

Đây là điểm quan trọng.

---

# 4. Không retry mọi thứ

Sai:

```python
while attempts < 3:
    try:
        return fetch()
    except Exception:
        retry()
```

Ví dụ:

```text
GET /chapter/abc
↓
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

Không có ích gì.

`404` thường có nghĩa:

> Resource không tồn tại.

Retry không làm resource xuất hiện.

---

# 5. Retry Policy

Ta tạo abstraction:

```python
from abc import ABC, abstractmethod


class RetryPolicy(ABC):
    @abstractmethod
    def should_retry(
        self,
        *,
        attempt: int,
        error: Exception | None = None,
        status_code: int | None = None,
    ) -> bool:
        raise NotImplementedError
```

Fetcher không cần biết rule cụ thể.

---

# 6. RetryConfig

Ta tạo config:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3

    retry_status_codes: frozenset[int] = frozenset(
        {
            429,
            500,
            502,
            503,
            504,
        }
    )
```

Ví dụ:

```text
max_attempts = 3
```

nghĩa là:

```text
Attempt 1
Attempt 2
Attempt 3
```

**Không phải 3 lần retry + 1 request đầu tiên.**

---

# 7. Basic RetryPolicy

```python
class DefaultRetryPolicy(RetryPolicy):
    def __init__(
        self,
        config: RetryConfig,
    ):
        self._config = config

    def should_retry(
        self,
        *,
        attempt: int,
        error: Exception | None = None,
        status_code: int | None = None,
    ) -> bool:

        if attempt >= self._config.max_attempts:
            return False

        if error is not None:
            return True

        if status_code in self._config.retry_status_codes:
            return True

        return False
```

Nhưng code trên còn hơi nguy hiểm:

```python
if error is not None:
    return True
```

Không phải exception nào cũng retry được.

---

# 8. Phân loại exception

Ta đã có:

```text
FetchError
├── FetchTimeoutError
├── FetchConnectionError
└── FetchNetworkError
```

Ta chỉ retry những lỗi transient.

Ví dụ:

```python
RETRYABLE_EXCEPTIONS = (
    FetchTimeoutError,
    FetchConnectionError,
    FetchNetworkError,
)
```

Policy:

```python
class DefaultRetryPolicy(RetryPolicy):
    def __init__(
        self,
        config: RetryConfig,
    ):
        self._config = config

    def should_retry(
        self,
        *,
        attempt: int,
        error: Exception | None = None,
        status_code: int | None = None,
    ) -> bool:

        if attempt >= self._config.max_attempts:
            return False

        if isinstance(
            error,
            RETRYABLE_EXCEPTIONS,
        ):
            return True

        if status_code in (self._config.retry_status_codes):
            return True

        return False
```

---

# 9. Retry matrix

Ta có thể hình dung:

| Failure          | Retry? |
| ---------------- | ------ |
| Timeout          | ✅      |
| Connection Error | ✅      |
| Network Error    | ✅      |
| 429              | ✅      |
| 500              | ✅      |
| 502              | ✅      |
| 503              | ✅      |
| 504              | ✅      |
| 403              | ❌      |
| 404              | ❌      |
| 401              | ❌      |
| 200              | ❌      |

Đây là **policy**, không phải logic của HttpClient.

---

# 10. Tại sao RetryPolicy không nằm trong HttpClient?

Không làm:

```python
class HttpxClient:

    def get(...):
        for _ in range(3):
            ...
```

Vì HttpClient không biết:

```text
crawler
proxy rotation
business policy
```

`HttpClient` chỉ nên làm:

```text
request
 ↓
HTTP
 ↓
response/error
```

Còn:

```text
có retry hay không?
```

là Application Policy.

---

# 11. Retry Delay

Nếu retry ngay:

```text
500
↓
retry
↓
500
↓
retry
↓
500
```

thì có thể tạo ra một burst request.

Ta cần delay:

```text
Attempt 1
   ↓
failure
   ↓
wait
   ↓
Attempt 2
```

---

# 12. Retry Backoff

Một công thức đơn giản:

```text
delay = base_delay × 2^(attempt - 1)
```

Ví dụ:

```text
base = 1

attempt 1 → 1s
attempt 2 → 2s
attempt 3 → 4s
```

Đây gọi là:

> Exponential Backoff.

---

# 13. RetryDelayStrategy

Ta tách abstraction:

```python
class RetryDelayStrategy(ABC):
    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        raise NotImplementedError
```

Implementation:

```python
class ExponentialBackoff:
    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
    ):
        self._base_delay = base_delay
        self._max_delay = max_delay

    def get_delay(
        self,
        attempt: int,
    ) -> float:

        delay = self._base_delay * (2 ** (attempt - 1))

        return min(
            delay,
            self._max_delay,
        )
```

---

# 14. Ví dụ

```python
backoff = ExponentialBackoff(
    base_delay=1,
    max_delay=30,
)
```

Ta có:

```text
attempt 1 → 1
attempt 2 → 2
attempt 3 → 4
attempt 4 → 8
attempt 5 → 16
attempt 6 → 30
```

---

# 15. Nhưng production nên có jitter

Nếu 100 worker cùng retry:

```text
Worker 1 → retry sau 2s
Worker 2 → retry sau 2s
Worker 3 → retry sau 2s
...
```

→ tất cả request quay lại cùng lúc.

Ta thêm:

> Jitter.

Ví dụ:

```text
2s + random nhỏ
```

hoặc Full Jitter:

```text
random(0, exponential_delay)
```

Ta sẽ chưa triển khai sâu ở đây; chỉ cần biết:

```text
Exponential Backoff
+
Jitter
```

là pattern thường dùng cho hệ thống phân tán.

---

# 16. Retry Engine

Thay vì để Fetcher tự tính delay, ta có thể tạo:

```python
class RetryEngine: ...
```

Nhưng hiện tại **chưa cần**.

Nếu tạo quá nhiều abstraction từ sớm:

```text
Fetcher
RetryEngine
RetryPolicy
RetryDelayStrategy
RetryContext
RetryDecision
```

thì project sẽ bị over-engineering.

Ở phiên bản v1:

```text
Fetcher
  ↓
RetryPolicy
  ↓
DelayStrategy
```

là đủ.

---

# 17. Retry và Proxy Rotation

Đây là phần quan trọng nhất của Buổi 10.

Giả sử:

```text
Proxy A
```

đã health check:

```text
ALIVE
```

Sau đó:

```text
GET
↓
Timeout
```

Có hai lựa chọn.

### Strategy A

```text
Retry cùng Proxy A
```

### Strategy B

```text
Proxy A failed
↓
Proxy B
```

Crawler thường muốn:

```text
transport failure
→ proxy có thể có vấn đề
→ rotate proxy
```

Nhưng không phải mọi lỗi đều như vậy.

---

# 18. Phân biệt failure

Ví dụ:

```text
Proxy A
   ↓
Health Check
   ↓
200
```

Sau đó target:

```text
GET
   ↓
403
```

Proxy A vẫn có thể sống.

Không nên:

```python
proxy.mark_dead()
```

cho mọi HTTP error.

---

# 19. Mapping failure

Ta có thể thiết kế:

```text
Failure
│
├── Proxy failure
│      ├── Timeout
│      ├── Connection Error
│      └── Network Error
│
└── Target HTTP response
       ├── 403
       ├── 404
       ├── 429
       ├── 500
       └── ...
```

Sau này Fetch Policy sẽ quyết định:

```text
failure
   ↓
retry?
   ↓
rotate proxy?
   ↓
backoff?
```

---

# 20. Fetcher v1 với Retry

Ta có thể viết phiên bản đơn giản:

```python
def fetch(
    self,
    request: FetchRequest,
) -> FetchResult:

    for attempt in range(
        1,
        self._retry_policy.max_attempts + 1,
    ):
        proxy = self._get_healthy_proxy()

        user_agent = self._user_agent_provider.get_user_agent()

        try:
            response = self._http_client.get(
                request.url,
                headers={
                    "User-Agent": user_agent,
                },
                proxy=proxy.url.value,
            )

        except FetchError as exc:
            if not self._retry_policy.should_retry(
                attempt=attempt,
                error=exc,
            ):
                raise

            delay = self._delay_strategy.get_delay(attempt)

            time.sleep(delay)

            continue

        if self._retry_policy.should_retry(
            attempt=attempt,
            status_code=response.status_code,
        ):
            delay = self._delay_strategy.get_delay(attempt)

            time.sleep(delay)

            continue

        return FetchResult(
            url=response.url,
            status_code=response.status_code,
            headers=response.headers,
            content=response.content,
        )

    raise FetchError("Fetch failed")
```

Đây là **v1**, chưa phải architecture cuối cùng.

---

# 21. Có một bug tiềm ẩn

Nếu:

```text
A → timeout
```

thì vòng lặp quay lại:

```text
_get_healthy_proxy()
```

Proxy A có thể đã được:

```python
proxy.mark_dead()
```

và pool bỏ qua nó.

Kết quả:

```text
A → DEAD
B → ALIVE
```

Retry tiếp theo sẽ dùng:

```text
B
```

Đây chính là sự kết hợp:

```text
Retry
+
Proxy Rotation
```

mà chúng ta muốn.

---

# 22. Nhưng HTTP 500 thì sao?

Ví dụ:

```text
Proxy A
   ↓
GET
   ↓
500
```

Không nhất thiết proxy chết.

Retry có thể vẫn dùng:

```text
Proxy A
```

hoặc rotation sang B.

Vì vậy:

> **Retry policy và Proxy rotation policy không nên bị đồng nhất.**

Đây là lý do sau này chúng ta sẽ có **Fetch Policy**.

---

# 23. Test Retry

Fake client có thể trả sequence:

```python
class SequenceHttpClient(HttpClient):
    def __init__(
        self,
        responses: list[HttpResponse | Exception],
    ):
        self._responses = responses
        self._index = 0

    def get(
        self,
        url: str,
        *,
        headers=None,
        proxy=None,
    ):

        item = self._responses[self._index]

        self._index += 1

        if isinstance(item, Exception):
            raise item

        return item
```

---

# 24. Test timeout → success

```python
client = SequenceHttpClient(
    [
        FetchTimeoutError("timeout"),
        HttpResponse(
            status_code=200,
            headers={},
            content=b"hello",
            url="https://example.com",
        ),
    ]
)
```

Kỳ vọng:

```text
Attempt 1 → timeout
Attempt 2 → 200
```

và:

```python
assert result.status_code == 200
```

---

# 25. Test 404 không retry

```python
client = SequenceHttpClient(
    [
        HttpResponse(
            status_code=404,
            headers={},
            content=b"not found",
            url="https://example.com/missing",
        ),
    ]
)
```

Kỳ vọng:

```text
GET
 ↓
404
 ↓
return result
```

Không:

```text
404
 ↓
retry
 ↓
404
 ↓
retry
```

---

# 26. Test 500 retry

```python
client = SequenceHttpClient(
    [
        HttpResponse(
            status_code=500,
            headers={},
            content=b"server error",
            url="https://example.com",
        ),
        HttpResponse(
            status_code=200,
            headers={},
            content=b"ok",
            url="https://example.com",
        ),
    ]
)
```

Kỳ vọng:

```text
Attempt 1 → 500
Attempt 2 → 200
```

---

# 27. Test max attempts

```text
Attempt 1 → 500
Attempt 2 → 500
Attempt 3 → 500
```

Sau đó:

```python
assert client.call_count == 3
```

Không được:

```text
Attempt 4
Attempt 5
...
```

---

# 28. Test Delay

Đừng test bằng:

```python
time.sleep(10)
```

Test sẽ chậm.

Thay `DelayStrategy` bằng Fake:

```python
class FakeDelayStrategy:
    def __init__(self):
        self.calls = []

    def get_delay(self, attempt: int) -> float:
        self.calls.append(attempt)
        return 0
```

Sau đó:

```python
assert delay_strategy.calls == [1]
```

Unit test không phải chờ thật.

---

# 29. Một nguyên tắc testing rất quan trọng

Ta muốn:

```text
Real implementation
        ↓
ExponentialBackoff
```

nhưng test:

```text
FakeDelayStrategy
```

Điều này cho phép:

```text
Production
→ sleep thật

Test
→ delay = 0
```

Không cần thay đổi Fetcher.

Đây chính là:

> Dependency Injection.

---

# 30. Architecture sau Buổi 10

```text
                         Fetcher
                            │
        ┌───────────────────┼──────────────────┐
        │                   │                  │
        ▼                   ▼                  ▼
 ProxyProvider       UserAgentProvider    HealthChecker
        │                   │                  │
        ▼                   ▼                  │
    ProxyPool             UAPool               │
        │                                      │
        └──────────────┬───────────────────────┘
                       ▼
                 FetchContext
                       │
                       ▼
                  HttpClient
                       │
                       ▼
                  HttpxClient
                       │
                       ▼
                     httpx


                 RetryPolicy
                     │
                     ▼
               DelayStrategy
```

Fetcher hiện đã có:

```text
✅ Proxy selection
✅ Proxy health check
✅ Proxy rotation
✅ User-Agent rotation
✅ Retry decision
✅ Retry delay
✅ HTTP status classification
```

---

# 31. Nhưng Fetcher bắt đầu phình ra

Ta đang có:

```python
fetch()
```

phải biết:

```text
proxy
health
UA
HTTP
retry
delay
status code
exception
```

Nếu tiếp tục thêm:

```text
rate limit
circuit breaker
metrics
logging
cache
robots.txt
request policy
```

Fetcher sẽ trở thành:

```text
              Fetcher
                 │
       ┌─────────┼─────────┐
       │         │         │
     Retry     Proxy      Rate
     Logic     Logic     Limit
       │         │         │
    Logging   Health    Metrics
       │         │         │
       ...
```

Đó là dấu hiệu cần một abstraction quan trọng hơn.

---

# 32. Bài học kiến trúc của Buổi 10

Chúng ta **chưa cần** tách ngay tất cả thành 20 class.

Nhưng cần nhận ra:

```text
Fetcher
```

đang chuyển từ:

```text
simple service
```

sang:

```text
orchestrator
```

Ở các buổi tiếp theo, chúng ta sẽ giải quyết việc này từng bước.

---

# 33. Roadmap hiện tại

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
10 Retry                          ✅
11 Error Handling                 ⬅️
12 Fetch Policy
13 Domain Service
14 Application Service
15 Dependency Injection
16 Repository cho Proxy
17 Proxy State
18 Circuit Breaker
19 Rate Limiting
20 Fetch Orchestration
```

## Buổi 11 — Error Handling

Chúng ta sẽ **không chỉ `try/except`**, mà thiết kế một hierarchy rõ ràng:

```text
FetchError
├── FetchTimeoutError
├── FetchConnectionError
├── FetchNetworkError
├── FetchHttpError
│   ├── TooManyRequestsError
│   ├── ServerError
│   └── ...
└── NoHealthyProxyError
```

Sau đó xây **Error Classification**:

```text
Exception
    ↓
ErrorClassifier
    ↓
Retryable?
Proxy failure?
Target failure?
Fatal?
    ↓
FetchPolicy
```

Đây sẽ là bước nối trực tiếp giữa **Retry** của Buổi 10 và **Fetch Policy** của Buổi 12.
