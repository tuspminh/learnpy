# Buổi 48 — Error Classification

Đây là một trong những buổi **quan trọng nhất của Part V**.

Sau Buổi 47, chúng ta đã có:

```text id="f4y4m0"
FetchRequest
    ↓
PrimpFetcher
    ↓
RetryPolicy
    ↓
BrowserContext
    ↓
Proxy + Browser Profile + Transport
```

Nhưng hiện tại crawler vẫn chưa trả lời được câu hỏi:

> **Lỗi này thì phải retry, đổi proxy, bỏ request, hay dừng luôn?**

Ví dụ:

```text
404
```

không giống:

```text
503
```

và:

```text
Proxy connection failed
```

không giống:

```text
403 Forbidden
```

Vì vậy hôm nay ta xây:

```text id="9n0gq2"
Raw HTTP / Exception
        ↓
ErrorClassifier
        ↓
FetchError
        ↓
ErrorCategory
        ↓
Retry / Proxy / Stop
```

---

# 1. Tại sao Error Classification cần thiết?

Nếu viết:

```python id="6ob9i1"
except Exception:
    retry()
```

thì:

```text id="v3i9n5"
Invalid URL
     ↓
retry ❌

ProgrammingError
     ↓
retry ❌

Proxy failure
     ↓
retry ?

Timeout
     ↓
retry ✓

503
     ↓
retry ✓
```

Không thể dùng một hành động cho tất cả.

---

# 2. Ta phân loại lỗi thành 3 tầng

Đối với Novel Crawler, trước mắt ta chia:

```text id="c4d7h5"
                    Fetch Error
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Network         HTTP       Request
```

Chi tiết:

```text id="6wm1lk"
Network
├── Timeout
├── Connection Error
├── TLS Error
└── Proxy Error

HTTP
├── 403
├── 404
├── 408
├── 429
├── 5xx
└── Other 4xx

Request
├── Invalid URL
├── Invalid configuration
└── Programming/configuration error
```

---

# 3. ErrorCategory

Tạo:

```text id="6n3q2d"
infrastructure/http/errors.py
```

```python id="u9y5pl"
from enum import Enum


class ErrorCategory(str, Enum):

    TIMEOUT = "timeout"

    CONNECTION = "connection"

    TLS = "tls"

    PROXY = "proxy"

    HTTP_403 = "http_403"

    HTTP_404 = "http_404"

    HTTP_429 = "http_429"

    HTTP_5XX = "http_5xx"

    HTTP_OTHER = "http_other"

    INVALID_REQUEST = "invalid_request"

    UNKNOWN = "unknown"
```

---

# 4. Tại sao dùng Enum?

Không nên rải string khắp project:

```python id="wl0a6a"
if error.category == "proxy":
```

rồi chỗ khác:

```python id="wjsh7g"
if error.category == "Proxy":
```

hoặc:

```python id="k2g4ly"
if error.category == "proxy_error":
```

Enum cho chúng ta một vocabulary thống nhất:

```python id="8ksxbl"
ErrorCategory.PROXY
```

---

# 5. FetchError

Bây giờ tạo object đại diện cho lỗi của crawler:

```python id="fcr7g2"
from dataclasses import dataclass


@dataclass(frozen=True)
class FetchError:

    category: ErrorCategory

    message: str

    status_code: int | None = None

    retryable: bool = False

    proxy_related: bool = False
```

Ví dụ:

```python id="1e1sq9"
FetchError(
    category=ErrorCategory.PROXY,
    message="Proxy connection failed",
    retryable=True,
    proxy_related=True,
)
```

---

# 6. Tại sao không chỉ dùng Exception?

Ví dụ raw exception:

```python id="g1d8m4"
TimeoutError(...)
```

Application rất khó biết:

```text id="6pjq2g"
Có retry không?
Có đổi proxy không?
Có log warning hay error?
```

Với `FetchError`:

```text id="2gnr0q"
category = PROXY
retryable = True
proxy_related = True
```

Application có thông tin rõ ràng.

---

# 7. Error Classification không nên nằm trong Application

Đây là điểm kiến trúc rất quan trọng.

Không nên:

```text id="l9ef3u"
CrawlChapter
    ↓
if primp exception...
```

vì Application bắt đầu phụ thuộc `primp`.

Đúng:

```text id="m3ajd9"
primp exception
       ↓
Infrastructure
       ↓
ErrorClassifier
       ↓
FetchError
       ↓
Application
```

---

# 8. ErrorClassifier Protocol

```python id="v6a6c9"
from typing import Protocol


class ErrorClassifier(Protocol):

    def classify(
        self,
        exc: Exception,
    ) -> FetchError:
        ...
```

Bây giờ Infrastructure có thể có:

```text id="6z0y3n"
PrimpErrorClassifier
HttpxErrorClassifier
FakeErrorClassifier
```

Application không cần biết implementation nào.

---

# 9. HTTP status classification

HTTP không nhất thiết là Exception.

Ví dụ:

```text id="n3fsqk"
503
```

vẫn là một response hợp lệ về mặt transport.

Do đó ta có thêm:

```python id="7p0tdl"
def classify_status(
    status_code: int,
) -> FetchError | None:

    if status_code == 403:

        return FetchError(
            category=ErrorCategory.HTTP_403,
            message="Forbidden",
            status_code=403,
            retryable=False,
        )

    if status_code == 404:

        return FetchError(
            category=ErrorCategory.HTTP_404,
            message="Not Found",
            status_code=404,
            retryable=False,
        )

    if status_code == 429:

        return FetchError(
            category=ErrorCategory.HTTP_429,
            message="Too Many Requests",
            status_code=429,
            retryable=True,
        )

    if 500 <= status_code <= 599:

        return FetchError(
            category=ErrorCategory.HTTP_5XX,
            message=f"Server error: {status_code}",
            status_code=status_code,
            retryable=True,
        )

    return None
```

---

# 10. 403 không tự động có nghĩa là retry

Ví dụ:

```text id="gj1gib"
403
```

Có thể là:

```text id="9c7s0u"
permission denied
```

hoặc:

```text id="v8g6j3"
access policy
```

hoặc:

```text id="s3zqk8"
WAF / bot protection
```

Ta **không nên tự động kết luận nguyên nhân**.

Vì vậy ở lớp generic:

```text id="57c6gz"
403
 ↓
HTTP_403
 ↓
retryable = False
```

Sau này source-specific policy có thể thay đổi hành vi nếu cần.

---

# 11. 429

```text id="7q11zw"
429 Too Many Requests
```

là trường hợp rõ ràng hơn:

```text id="g9j4bj"
429
 ↓
Retry
```

Nhưng phải chú ý:

```http id="hrrb5h"
Retry-After: 30
```

Nếu có header:

```text id="a6l4gm"
Retry-After
      ↓
RetryPolicy
```

để quyết định thời gian chờ.

---

# 12. 5xx

Các lỗi:

```text id="k3xj4f"
500
502
503
504
```

thường có tính chất transient hơn 4xx.

Ta có:

```text id="m5c4fp"
HTTP_5XX
retryable = True
```

Nhưng:

> retryable không có nghĩa retry vô hạn.

Retry vẫn phải chịu:

```text id="k5t0d5"
max_attempts
backoff
jitter
rate limit
```

---

# 13. 404

Đối với novel crawler:

```text id="xg0sde"
GET /chuong-999
     ↓
404
```

thường có nghĩa:

```text id="z8r8q4"
resource không tồn tại
```

Không retry:

```text id="74g5di"
404 → stop
```

Điều này tiết kiệm request rất nhiều.

---

# 14. Timeout

Timeout khác HTTP status.

Ví dụ:

```text id="78e0yh"
client
 ↓
server
 ↓
không response
 ↓
timeout
```

Không có:

```text id="z8w5h5"
status_code = 503
```

Đây là Exception.

Ta phân loại:

```text id="r2w5td"
Timeout
 ↓
ErrorCategory.TIMEOUT
 ↓
retryable = True
```

---

# 15. Connection Error

Ví dụ:

```text id="8o0p4c"
Connection refused
Connection reset
Connection failed
```

Thông thường:

```text id="ef0w58"
Connection
    ↓
retryable = True
```

Nhưng nếu connection failure được xác định là do proxy:

```text id="nj8i8c"
Proxy connection failed
    ↓
PROXY
```

thì cần thêm hành động:

```text id="6v0h6e"
retry
+
mark proxy unhealthy
```

Đây là lý do `proxy_related` rất hữu ích.

---

# 16. Proxy Error

Ta có:

```python id="b4j9cm"
FetchError(
    category=ErrorCategory.PROXY,
    message="Proxy unavailable",
    retryable=True,
    proxy_related=True,
)
```

`PrimpFetcher` có thể làm:

```text id="7tx3mm"
PROXY error
     │
     ├── mark_failure(context)
     │
     └── retry
```

---

# 17. TLS Error

TLS error:

```text id="n1d4fl"
TLS handshake failed
certificate error
connection TLS failure
```

Không nên mặc định:

```text id="w2y7tv"
TLS error
 ↓
retry same proxy forever
```

Nếu nguyên nhân là proxy:

```text id="axf9vb"
TLS
 ↓
proxy-related
 ↓
disable/change proxy
```

Nếu certificate configuration sai:

```text id="17x6d9"
TLS configuration
 ↓
non-retryable
```

Classification phải giữ đủ thông tin để policy quyết định.

---

# 18. ErrorClassifier

Ta có thể xây một classifier đơn giản:

```python id="r6s5fg"
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
```

Đây là skeleton.

Trong implementation thực tế, ta sẽ map exception types cụ thể của transport adapter.

---

# 19. Đừng để `PrimpFetcher` biết exception của primp

Sai:

```python id="4d2v7e"
class PrimpFetcher:

    except primp.SomeException:
        ...
```

Nếu Application-facing Fetcher phụ thuộc trực tiếp vào exception của `primp`, abstraction bị phá.

Tốt hơn:

```text id="h9q8lf"
PrimpTransport
       │
       ├── catches primp exception
       │
       ▼
ErrorClassifier
       │
       ▼
FetchError
       │
       ▼
PrimpFetcher
```

---

# 20. Error → Action

Bây giờ ta tạo tư duy quan trọng:

```text id="6q6n9e"
ErrorCategory
      ↓
Action
```

Ví dụ:

| Error           |    Retry | Proxy action         |
| --------------- | -------: | -------------------- |
| TIMEOUT         |        ✅ | có thể đổi           |
| CONNECTION      |        ✅ | có thể đổi           |
| PROXY           |        ✅ | mark failed          |
| TLS             |      tùy | tùy                  |
| 403             | thường ❌ | tùy policy           |
| 404             |        ❌ | không                |
| 429             |        ✅ | không nhất thiết đổi |
| 5xx             |        ✅ | không nhất thiết đổi |
| INVALID_REQUEST |        ❌ | không                |
| UNKNOWN         |    ❌/tùy | không                |

---

# 21. Đừng gộp Error Classification với Retry Policy

Đây là một lỗi thiết kế dễ mắc.

Không nên:

```python id="6n9g43"
class RetryPolicy:

    def classify_exception(...):
        ...

    def select_proxy(...):
        ...

    def calculate_delay(...):
        ...
```

Nó lại trở thành God Object.

Tách:

```text id="4e1a6c"
ErrorClassifier
       ↓
FetchError
       ↓
RetryPolicy
       ↓
RetryDecision
```

---

# 22. RetryDecision

Ta hoàn thiện object đã học ở Buổi 45:

```python id="q0qz7h"
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryDecision:

    retry: bool

    delay: float = 0.0

    reason: str = ""

    change_proxy: bool = False

    change_browser: bool = False
```

Ví dụ:

```text id="p6u1lq"
PROXY ERROR

retry = True
change_proxy = True
change_browser = False
```

---

# 23. Timeout

```text id="2s2zj8"
TIMEOUT

retry = True
change_proxy = True
change_browser = False
```

Một timeout không nhất thiết do proxy, nhưng trong crawler proxy pool, thử context khác có thể là một policy hợp lý.

---

# 24. 429

```text id="1o3yzo"
429

retry = True
change_proxy = False
change_browser = False
```

Tại sao?

Vì 429 chủ yếu nói:

> Request rate đang quá cao.

Đổi proxy ngay lập tức có thể không giải quyết nguyên nhân.

Ta nên ưu tiên:

```text id="z3qgzi"
Retry-After
+
RateLimiter
```

---

# 25. 503

```text id="7ivcx7"
503

retry = True
change_proxy = False
change_browser = False
```

Server đang lỗi không nhất thiết liên quan proxy.

---

# 26. Proxy failure

```text id="ap8fbd"
PROXY

retry = True
change_proxy = True
change_browser = False
```

Flow:

```text id="5k9f3j"
Proxy A
   ↓
Proxy error
   ↓
mark A failed
   ↓
select B
   ↓
retry
```

---

# 27. 403

Có thể:

```text id="3a7o3v"
403
 ↓
no retry
```

Nhưng source-specific policy có thể quyết định:

```text id="a1l1h7"
403
 ↓
stop this request
```

hoặc trong một hệ thống được cấu hình phù hợp:

```text id="sgm6tu"
403
 ↓
change context
 ↓
retry
```

Điểm quan trọng là:

> **Classifier cung cấp facts; Policy quyết định action.**

Đừng để classifier tự quyết định mọi thứ.

---

# 28. Đây là nguyên tắc thiết kế quan trọng nhất Buổi 48

```text id="b5qj3n"
Classifier
    ↓
"Đây là lỗi gì?"
```

Còn:

```text id="x3b3zw"
Policy
    ↓
"Ta phải làm gì?"
```

Hai câu hỏi khác nhau.

---

# 29. Flow hoàn chỉnh

```text id="lqzrrk"
primp.AsyncClient
       │
       ▼
PrimpTransport
       │
       ├───────────────┐
       │               │
       ▼               ▼
    Response         Exception
       │               │
       │               ▼
       │         ErrorClassifier
       │               │
       │               ▼
       │           FetchError
       │               │
       └───────┬───────┘
               ▼
          RetryPolicy
               │
               ▼
         RetryDecision
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
     Retry   Proxy    Stop
              change
```

---

# 30. Tích hợp vào PrimpFetcher

Skeleton:

```python id="6y9x4b"
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

        except Exception as exc:

            error = (
                self.error_classifier.classify(
                    exc
                )
            )

            decision = (
                self.retry_policy.decide(
                    attempt=attempt,
                    error=error,
                )
            )

            if error.proxy_related:
                self.context_strategy.mark_failure(
                    context
                )

            if not decision.retry:
                raise

            await asyncio.sleep(
                decision.delay
            )

            continue

        error = self.error_classifier.classify_response(
            response
        )

        if error is None:
            self.context_strategy.mark_success(
                context
            )
            return response

        decision = (
            self.retry_policy.decide(
                attempt=attempt,
                error=error,
            )
        )

        if error.proxy_related:
            self.context_strategy.mark_failure(
                context
            )

        if not decision.retry:
            return response

        await asyncio.sleep(
            decision.delay
        )

    raise RuntimeError(
        "Retry attempts exhausted"
    )
```

Đây là kiến trúc khái niệm; ta sẽ tiếp tục tinh chỉnh ở Buổi 49–50.

---

# 31. Một điểm cần sửa so với thiết kế cũ

Trước đây ta có:

```text id="6d0r7w"
response.is_success
     ↓
mark_success(proxy)
```

Nhưng bây giờ cần cẩn thận hơn.

Ví dụ:

```text id="w3bqkn"
200
```

không có nghĩa:

```text id="6m5p4k"
proxy hoàn toàn healthy
```

Nó chỉ chứng minh:

> Request này nhận được HTTP response thành công.

Trong production, health scoring nên có policy riêng.

---

# 32. HTTP 200 nhưng crawler vẫn thất bại

Đây là một case cực kỳ quan trọng với Novel Crawler:

```text id="n4ib3k"
HTTP 200
    ↓
HTML
    ↓
CAPTCHA / challenge page
```

hoặc:

```text id="u5x6n3"
HTTP 200
    ↓
"Access denied"
```

HTTP layer nói:

```text id="aqf7yn"
200 OK
```

nhưng Parser nói:

```text id="u1b5f4"
Không tìm thấy chapter content
```

Đó **không còn là HTTP error**.

Nó sẽ liên quan đến:

```text id="s6c3n0"
ParserError
ContentValidationError
ChallengeDetected
```

Chúng ta chưa trộn chúng vào `FetchError`.

Đây là một ranh giới kiến trúc rất quan trọng.

---

# 33. HTTP Success ≠ Crawl Success

```text id="x2b9yq"
HTTP
 ↓
200
 ↓
FetchResponse
 ↓
Parser
 ↓
?
```

Có thể:

```text id="tq8jcz"
200 → valid chapter
```

hoặc:

```text id="2k2jyo"
200 → challenge page
```

Vì vậy:

```text id="4k2spw"
Fetcher
```

chỉ chịu trách nhiệm HTTP.

Parser chịu trách nhiệm:

```text id="f5m2lh"
HTML → Domain
```

---

# 34. Test Error Classification

Ta có:

```python id="l4u7gm"
classifier = BasicErrorClassifier()
```

Test timeout:

```python id="o5b7ze"
error = classifier.classify(
    TimeoutError("request timeout")
)

print(error)
```

Kết quả kỳ vọng:

```text id="t1xjpn"
category=TIMEOUT
retryable=True
```

---

# 35. Test unknown error

```python id="xj0p8u"
error = classifier.classify(
    RuntimeError("something unexpected")
)

print(error)
```

Kết quả:

```text id="3d5z7w"
category=UNKNOWN
retryable=False
```

Đây là default an toàn.

---

# 36. Test HTTP

```python id="2j3y9e"
print(
    classify_status(404)
)

print(
    classify_status(429)
)

print(
    classify_status(503)
)
```

Ta mong muốn:

```text id="qz8o4m"
404 → HTTP_404 → no retry
429 → HTTP_429 → retry
503 → HTTP_5XX → retry
```

---

# 37. Test Proxy Failure

```python id="r0i7e4"
error = FetchError(
    category=ErrorCategory.PROXY,
    message="proxy unavailable",
    retryable=True,
    proxy_related=True,
)

print(error.category)
print(error.retryable)
print(error.proxy_related)
```

Kết quả:

```text id="4u6i1g"
ErrorCategory.PROXY
True
True
```

---

# 38. Tại sao `proxy_related` là boolean?

Hiện tại:

```python id="4u4n2j"
proxy_related: bool
```

đơn giản và đủ để học.

Sau này có thể nâng cấp thành:

```text id="6ydx7w"
FailureScope
├── REQUEST
├── PROXY
├── BROWSER
├── SERVER
└── CONFIGURATION
```

Khi đó policy có thể chính xác hơn:

```text id="uh1c6n"
PROXY
   ↓
change proxy

BROWSER
   ↓
change browser

SERVER
   ↓
wait

CONFIGURATION
   ↓
stop
```

Đây có thể là một cải tiến ở Buổi 50.

---

# 39. Error Classification + Proxy Strategy

Bây giờ hai buổi 46 và 48 kết nối:

```text id="4w6j3f"
Request
   ↓
Context A
   ↓
Proxy A
   ↓
Timeout
   ↓
ErrorClassifier
   ↓
TIMEOUT
   ↓
RetryPolicy
   ↓
Retry
   ↓
ProxyStrategy
   ↓
Context B
   ↓
Proxy B
```

---

# 40. Error Classification + Browser Strategy

Tương tự:

```text id="p6i8lr"
Context A
Chrome 146
Proxy A
       ↓
failure
       ↓
classification
       ↓
policy
       ↓
Context B
Firefox 151
Proxy B
```

Nhưng **không phải lỗi nào cũng đổi browser**.

Đây chính là lý do:

```text id="ErrorClassifier"
```

và:

```text id="RetryPolicy"
```

phải tách nhau.

---

# 41. Kiến trúc sau Buổi 48

```text id="6p6f0m"
                         PrimpFetcher
                              │
              ┌───────────────┼────────────────┐
              │               │                │
              ▼               ▼                ▼
        RetryPolicy      RateLimiter       Semaphore
              │
              ▼
       ErrorClassifier
              │
              ▼
         FetchError
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    Retry   Proxy   Stop
       │      │
       │      ▼
       │ ProxyStrategy
       │      │
       │      ▼
       │ BrowserContext
       │      │
       └──────┤
              ▼
        PrimpTransport
              │
              ▼
       primp.AsyncClient
```

---

# 42. Toàn bộ Part V hiện tại

```text id="2q3w4e"
41. Request Model
        ↓
42. Response Model
        ↓
43. Fetcher Interface
        ↓
44. PrimpFetcher
        ↓
45. Retry Policy
        ↓
46. Proxy Strategy
        ↓
47. Browser Profile Strategy
        ↓
48. Error Classification      ← HÔM NAY
        ↓
49. Observability / Logging
        ↓
50. Production Fetcher
```

---

# 43. Điều quan trọng nhất cần nhớ

Đừng nghĩ:

```text id="r8r2m6"
Exception
   ↓
Retry
```

Hãy nghĩ:

```text id="5d4f4n"
Exception / HTTP
       ↓
Classification
       ↓
FetchError
       ↓
Policy
       ↓
Decision
       ↓
Action
```

Trong đó:

```text id="0u4h5g"
Classifier
= "Chuyện gì đã xảy ra?"

Policy
= "Ta nên làm gì?"

Strategy
= "Dùng context nào?"

Executor
= "Thực hiện retry thế nào?"
```

Đây là cách chia trách nhiệm rất phù hợp với kiến trúc DDD/SOLID của Novel Crawler.

---

## Bài tập thực hành

Hãy tự tạo bảng:

```text
Timeout
ConnectionError
ProxyError
TLS error
403
404
408
429
500
502
503
504
Invalid URL
Unknown Exception
```

và với mỗi lỗi xác định:

```text
Category
Retry?
Change Proxy?
Change Browser?
Backoff?
```

Sau đó **Buổi 49 — Observability / Logging** sẽ dùng chính `FetchError`, `RetryDecision`, `BrowserContext`, `Proxy` để tạo log có cấu trúc:

```text
2026-09-18 17:30:12
GET /chapter-123
context=chrome_146_windows
proxy=proxy-03
attempt=2
status=503
error=http_5xx
retry=true
delay=2.37
```

từ đó chúng ta có thể biết **crawler đang chậm vì server, proxy, retry hay rate limit**, thay vì chỉ thấy một đống `Exception`.
